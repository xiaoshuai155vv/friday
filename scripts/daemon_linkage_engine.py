#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
智能守护进程间联动引擎 (Daemon Linkage Engine)
实现跨守护进程的任务传递和自动触发，形成多守护进程协同的主动服务体系。

支持的功能：
- 守护进程状态共享
- 条件触发联动（守护进程A检测到X条件时自动触发守护进程B执行Y操作）
- 任务队列和消息传递
- 与 daemon_manager.py 集成支持联动触发配置
- do.py 集成支持关键词触发

使用方法：
    python daemon_linkage_engine.py list                    # 查看所有联动配置
    python daemon_linkage_engine.py status                  # 查看联动引擎状态
    python daemon_linkage_engine.py add <source> <target>   # 添加联动规则
    python daemon_linkage_engine.py remove <link_id>         # 删除联动规则
    python daemon_linkage_engine.py enable <link_id>         # 启用联动规则
    python daemon_linkage_engine.py disable <link_id>       # 禁用联动规则
    python daemon_linkage_engine.py trigger <daemon> <event> # 手动触发事件
    python daemon_linkage_engine.py run                      # 启动联动引擎（守护进程模式）
"""

import os
import sys
import json
import time
import threading
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

# 配置日志
SCRIPT_DIR = Path(__file__).parent
LOG_DIR = SCRIPT_DIR.parent / "runtime" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "daemon_linkage.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("daemon_linkage")

# 配置文件路径
LINKAGE_CONFIG_FILE = SCRIPT_DIR.parent / "runtime" / "state" / "daemon_linkage_config.json"
LINKAGE_STATE_FILE = SCRIPT_DIR.parent / "runtime" / "state" / "daemon_linkage_state.json"
LINKAGE_HISTORY_FILE = SCRIPT_DIR.parent / "runtime" / "state" / "daemon_linkage_history.json"


class LinkageType(Enum):
    """联动类型"""
    CONDITION_TRIGGER = "condition_trigger"   # 条件触发
    STATE_CHANGE = "state_change"             # 状态变化触发
    MANUAL = "manual"                          # 手动触发
    SCHEDULED = "scheduled"                    # 定时触发


class LinkageStatus(Enum):
    """联动状态"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    DISABLED = "disabled"


@dataclass
class LinkageRule:
    """联动规则"""
    id: str
    name: str
    source_daemon: str           # 源守护进程
    source_event: str            # 源事件（如 "high_cpu", "low_memory", "error"）
    target_daemon: str           # 目标守护进程
    target_action: str            # 目标动作（如 "start", "optimize", "notify"）
    condition: str               # 触发条件（如 "cpu > 80"）
    enabled: bool = True
    cooldown_seconds: int = 60   # 冷却时间（秒）
    last_triggered: Optional[str] = None
    trigger_count: int = 0


@dataclass
class DaemonStatus:
    """守护进程状态"""
    name: str
    status: str                  # running, stopped, error
    health_score: float = 100.0  # 健康分数 0-100
    metrics: Dict[str, Any] = field(default_factory=dict)
    last_updated: Optional[str] = None


@dataclass
class LinkageEvent:
    """联动事件"""
    id: str
    rule_id: str
    source_daemon: str
    source_event: str
    target_daemon: str
    target_action: str
    timestamp: str
    status: str
    result: Optional[str] = None


class DaemonLinkageEngine:
    """智能守护进程间联动引擎"""

    def __init__(self):
        self.rules: Dict[str, LinkageRule] = {}
        self.daemon_status: Dict[str, DaemonStatus] = {}
        self.event_queue: List[Dict[str, Any]] = []
        self.running = False
        self._lock = threading.Lock()
        self._load_config()
        self._load_state()

    def _load_config(self):
        """加载联动配置"""
        if LINKAGE_CONFIG_FILE.exists():
            try:
                with open(LINKAGE_CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    rules_data = config.get('rules', [])
                    for rule_data in rules_data:
                        rule = LinkageRule(**rule_data)
                        self.rules[rule.id] = rule
                    logger.info(f"已加载 {len(self.rules)} 条联动规则")
            except Exception as e:
                logger.error(f"加载联动配置失败: {e}")

    def _save_config(self):
        """保存联动配置"""
        try:
            LINKAGE_CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
            rules_data = [vars(rule) for rule in self.rules.values()]
            config = {
                'rules': rules_data,
                'updated_at': datetime.now().isoformat(),
            }
            with open(LINKAGE_CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存联动配置失败: {e}")

    def _load_state(self):
        """加载状态"""
        if LINKAGE_STATE_FILE.exists():
            try:
                with open(LINKAGE_STATE_FILE, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                    daemon_status_data = state.get('daemon_status', {})
                    for name, data in daemon_status_data.items():
                        self.daemon_status[name] = DaemonStatus(**data)
            except Exception as e:
                logger.error(f"加载状态失败: {e}")

        # 如果没有守护进程状态，初始化默认状态
        if not self.daemon_status:
            self.daemon_status = {
                'health_check': DaemonStatus(name='health_check', status='stopped', last_updated=datetime.now().isoformat()),
                'evolution_loop': DaemonStatus(name='evolution_loop', status='stopped', last_updated=datetime.now().isoformat()),
                'health_assurance': DaemonStatus(name='health_assurance', status='stopped', last_updated=datetime.now().isoformat()),
            }
            self._save_state()

    def _save_state(self):
        """保存状态"""
        try:
            LINKAGE_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
            daemon_status_data = {name: vars(status) for name, status in self.daemon_status.items()}
            state = {
                'daemon_status': daemon_status_data,
                'event_queue_length': len(self.event_queue),
                'updated_at': datetime.now().isoformat(),
            }
            with open(LINKAGE_STATE_FILE, 'w', encoding='utf-8') as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存状态失败: {e}")

    def add_rule(self, name: str, source_daemon: str, source_event: str,
                 target_daemon: str, target_action: str, condition: str = "",
                 cooldown_seconds: int = 60) -> str:
        """添加联动规则"""
        rule_id = f"link_{int(time.time() * 1000)}"
        rule = LinkageRule(
            id=rule_id,
            name=name,
            source_daemon=source_daemon,
            source_event=source_event,
            target_daemon=target_daemon,
            target_action=target_action,
            condition=condition,
            cooldown_seconds=cooldown_seconds,
        )
        with self._lock:
            self.rules[rule_id] = rule
            self._save_config()
        logger.info(f"添加联动规则: {rule_id} - {name}")
        return rule_id

    def remove_rule(self, rule_id: str) -> bool:
        """删除联动规则"""
        with self._lock:
            if rule_id in self.rules:
                del self.rules[rule_id]
                self._save_config()
                logger.info(f"删除联动规则: {rule_id}")
                return True
        return False

    def enable_rule(self, rule_id: str) -> bool:
        """启用联动规则"""
        with self._lock:
            if rule_id in self.rules:
                self.rules[rule_id].enabled = True
                self._save_config()
                logger.info(f"启用联动规则: {rule_id}")
                return True
        return False

    def disable_rule(self, rule_id: str) -> bool:
        """禁用联动规则"""
        with self._lock:
            if rule_id in self.rules:
                self.rules[rule_id].enabled = False
                self._save_config()
                logger.info(f"禁用联动规则: {rule_id}")
                return True
        return False

    def list_rules(self) -> List[Dict[str, Any]]:
        """列出所有联动规则"""
        result = []
        for rule in self.rules.values():
            result.append({
                'id': rule.id,
                'name': rule.name,
                'source_daemon': rule.source_daemon,
                'source_event': rule.source_event,
                'target_daemon': rule.target_daemon,
                'target_action': rule.target_action,
                'condition': rule.condition,
                'enabled': rule.enabled,
                'cooldown_seconds': rule.cooldown_seconds,
                'last_triggered': rule.last_triggered,
                'trigger_count': rule.trigger_count,
            })
        return result

    def update_daemon_status(self, name: str, status: str, health_score: float = 100.0, metrics: Dict = None):
        """更新守护进程状态"""
        with self._lock:
            if name not in self.daemon_status:
                self.daemon_status[name] = DaemonStatus(name=name, status=status)

            self.daemon_status[name].status = status
            self.daemon_status[name].health_score = health_score
            self.daemon_status[name].metrics = metrics or {}
            self.daemon_status[name].last_updated = datetime.now().isoformat()
            self._save_state()

    def get_daemon_status(self, name: str = None) -> Dict:
        """获取守护进程状态"""
        if name:
            status = self.daemon_status.get(name)
            if status:
                return vars(status)
            return {}

        return {name: vars(status) for name, status in self.daemon_status.items()}

    def trigger_event(self, source_daemon: str, source_event: str, event_data: Dict = None) -> List[Dict]:
        """触发事件，检查并执行匹配的联动规则"""
        triggered_rules = []
        now = datetime.now()

        logger.info(f"事件触发: {source_daemon} - {source_event}")

        with self._lock:
            for rule in self.rules.values():
                # 检查规则是否匹配
                if rule.source_daemon != source_daemon:
                    continue
                if rule.source_event != source_event:
                    continue
                if not rule.enabled:
                    continue

                # 检查冷却时间
                if rule.last_triggered:
                    last_time = datetime.fromisoformat(rule.last_triggered)
                    if (now - last_time).total_seconds() < rule.cooldown_seconds:
                        logger.debug(f"规则 {rule.id} 在冷却期内，跳过")
                        continue

                # 触发联动
                rule.last_triggered = now.isoformat()
                rule.trigger_count += 1

                result = self._execute_linkage(rule, event_data or {})
                triggered_rules.append({
                    'rule_id': rule.id,
                    'name': rule.name,
                    'target_daemon': rule.target_daemon,
                    'target_action': rule.target_action,
                    'result': result,
                })

                self._save_config()
                self._save_state()

        # 记录历史
        self._record_history(source_daemon, source_event, triggered_rules)

        return triggered_rules

    def _execute_linkage(self, rule: LinkageRule, event_data: Dict) -> str:
        """执行联动操作"""
        logger.info(f"执行联动: {rule.name} -> {rule.target_daemon}.{rule.target_action}")

        try:
            # 导入 daemon_manager 执行实际操作
            sys.path.insert(0, str(SCRIPT_DIR))
            from daemon_manager import DaemonManager

            manager = DaemonManager()

            if rule.target_action == "start":
                success = manager.start_daemon(rule.target_daemon)
                return "success" if success else "failed"
            elif rule.target_action == "restart":
                success = manager.restart_daemon(rule.target_daemon)
                return "success" if success else "failed"
            elif rule.target_action == "stop":
                success = manager.stop_daemon(rule.target_daemon)
                return "success" if success else "failed"
            elif rule.target_action == "notify":
                # 发送通知
                return "notification_sent"
            elif rule.target_action == "optimize":
                # 执行优化（需要具体实现）
                logger.info(f"执行优化操作: {rule.target_daemon}")
                return "optimize_triggered"
            else:
                logger.warning(f"未知目标动作: {rule.target_action}")
                return "unknown_action"

        except Exception as e:
            logger.error(f"执行联动失败: {e}")
            return f"error: {str(e)}"

    def _record_history(self, source_daemon: str, source_event: str, triggered_rules: List[Dict]):
        """记录联动历史"""
        try:
            history = []
            if LINKAGE_HISTORY_FILE.exists():
                with open(LINKAGE_HISTORY_FILE, 'r', encoding='utf-8') as f:
                    history = json.load(f)

            # 添加新记录
            record = {
                'id': f"evt_{int(time.time() * 1000)}",
                'timestamp': datetime.now().isoformat(),
                'source_daemon': source_daemon,
                'source_event': source_event,
                'triggered_rules': triggered_rules,
            }
            history.append(record)

            # 只保留最近100条
            history = history[-100:]

            with open(LINKAGE_HISTORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)

        except Exception as e:
            logger.error(f"记录历史失败: {e}")

    def get_history(self, limit: int = 20) -> List[Dict]:
        """获取联动历史"""
        try:
            if LINKAGE_HISTORY_FILE.exists():
                with open(LINKAGE_HISTORY_FILE, 'r', encoding='utf-8') as f:
                    history = json.load(f)
                    return history[-limit:]
        except Exception as e:
            logger.error(f"读取历史失败: {e}")
        return []

    def monitor_and_link(self):
        """监控守护进程状态并触发联动（守护进程模式）"""
        logger.info("启动守护进程监控与联动")

        while self.running:
            try:
                # 检查各守护进程状态
                sys.path.insert(0, str(SCRIPT_DIR))
                from daemon_manager import DaemonManager

                manager = DaemonManager()
                for daemon_name in ['health_check', 'evolution_loop', 'health_assurance']:
                    status = manager.get_daemon_status(daemon_name)
                    if status:
                        running = status.get('process_running', False)
                        self.update_daemon_status(
                            daemon_name,
                            'running' if running else 'stopped',
                            health_score=90.0 if running else 0.0
                        )

                        # 检查状态变化触发联动
                        if not running and self.daemon_status.get(daemon_name):
                            old_status = self.daemon_status[daemon_name].status
                            if old_status == 'running':
                                self.trigger_event(daemon_name, 'stopped')

            except Exception as e:
                logger.error(f"监控联动时出错: {e}")

            time.sleep(30)  # 每30秒检查一次

        logger.info("守护进程监控与联动已停止")

    def start(self):
        """启动联动引擎（守护进程模式）"""
        if not self.running:
            self.running = True
            self.monitor_thread = threading.Thread(target=self.monitor_and_link, daemon=True)
            self.monitor_thread.start()
            logger.info("智能守护进程间联动引擎已启动")

    def stop(self):
        """停止联动引擎"""
        self.running = False
        logger.info("智能守护进程间联动引擎已停止")


def main():
    """主函数 - 命令行入口"""
    engine = DaemonLinkageEngine()

    if len(sys.argv) < 2:
        # 无参数时显示状态
        print("\n=== 智能守护进程间联动引擎 ===")
        print("\n联动规则列表:")
        rules = engine.list_rules()
        if not rules:
            print("  暂无联动规则")
        else:
            for rule in rules:
                status_icon = "●" if rule['enabled'] else "○"
                print(f"  {status_icon} {rule['id'][:16]}... {rule['name']}")
                print(f"      {rule['source_daemon']}:{rule['source_event']} -> {rule['target_daemon']}:{rule['target_action']}")
                print(f"      触发次数: {rule['trigger_count']}, 冷却: {rule['cooldown_seconds']}s")
                print()

        print("守护进程状态:")
        daemon_status = engine.get_daemon_status()
        for name, status in daemon_status.items():
            status_icon = "●" if status['status'] == 'running' else "○"
            print(f"  {status_icon} {name:20s} [{status['status']:10s}] 健康: {status['health_score']:.0f}%")
        print()
        return

    command = sys.argv[1].lower()

    if command == "list":
        print("\n=== 联动规则列表 ===")
        rules = engine.list_rules()
        if not rules:
            print("  暂无联动规则")
        else:
            for rule in rules:
                status_icon = "●" if rule['enabled'] else "○"
                print(f"\n{status_icon} {rule['name']}")
                print(f"  ID: {rule['id']}")
                print(f"  源: {rule['source_daemon']}:{rule['source_event']}")
                print(f"  目标: {rule['target_daemon']}:{rule['target_action']}")
                print(f"  条件: {rule['condition'] or '无'}")
                print(f"  启用: {'是' if rule['enabled'] else '否'}")
                print(f"  触发次数: {rule['trigger_count']}")
                print(f"  最后触发: {rule['last_triggered'] or '从未'}")
        print()

    elif command == "status":
        print("\n=== 联动引擎状态 ===")
        print(f"运行中: {'是' if engine.running else '否'}")
        print(f"联动规则数: {len(engine.rules)}")
        print(f"事件队列长度: {len(engine.event_queue)}")

        print("\n守护进程状态:")
        daemon_status = engine.get_daemon_status()
        for name, status in daemon_status.items():
            status_icon = "●" if status['status'] == 'running' else "○"
            print(f"  {status_icon} {name:20s} [{status['status']:10s}] 健康: {status['health_score']:.0f}%")

        print("\n最近联动历史:")
        history = engine.get_history(5)
        for record in history:
            print(f"  {record['timestamp'][:19]} {record['source_daemon']}:{record['source_event']}")
            for rule in record.get('triggered_rules', []):
                print(f"    -> {rule['target_daemon']}:{rule['target_action']} [{rule['result']}]")
        print()

    elif command == "add":
        if len(sys.argv) < 6:
            print("用法: python daemon_linkage_engine.py add <源守护进程> <源事件> <目标守护进程> <目标动作>")
        else:
            source_daemon = sys.argv[2]
            source_event = sys.argv[3]
            target_daemon = sys.argv[4]
            target_action = sys.argv[5]
            rule_id = engine.add_rule(
                f"{source_daemon}_{source_event}_to_{target_daemon}",
                source_daemon, source_event,
                target_daemon, target_action
            )
            print(f"联动规则已添加: {rule_id}")

    elif command == "remove":
        if len(sys.argv) < 3:
            print("用法: python daemon_linkage_engine.py remove <rule_id>")
        else:
            rule_id = sys.argv[2]
            if engine.remove_rule(rule_id):
                print(f"联动规则已删除: {rule_id}")
            else:
                print(f"联动规则不存在: {rule_id}")

    elif command == "enable":
        if len(sys.argv) < 3:
            print("用法: python daemon_linkage_engine.py enable <rule_id>")
        else:
            rule_id = sys.argv[2]
            if engine.enable_rule(rule_id):
                print(f"联动规则已启用: {rule_id}")
            else:
                print(f"联动规则不存在: {rule_id}")

    elif command == "disable":
        if len(sys.argv) < 3:
            print("用法: python daemon_linkage_engine.py disable <rule_id>")
        else:
            rule_id = sys.argv[2]
            if engine.disable_rule(rule_id):
                print(f"联动规则已禁用: {rule_id}")
            else:
                print(f"联动规则不存在: {rule_id}")

    elif command == "trigger":
        if len(sys.argv) < 4:
            print("用法: python daemon_linkage_engine.py trigger <守护进程> <事件>")
        else:
            source_daemon = sys.argv[2]
            source_event = sys.argv[3]
            triggered = engine.trigger_event(source_daemon, source_event)
            print(f"触发事件: {source_daemon}:{source_event}")
            print(f"匹配规则数: {len(triggered)}")
            for rule in triggered:
                print(f"  -> {rule['target_daemon']}:{rule['target_action']} [{rule['result']}]")

    elif command == "run":
        print("启动智能守护进程间联动引擎...")
        engine.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n正在停止...")
            engine.stop()

    else:
        print(f"未知命令: {command}")
        print("可用命令: list, status, add, remove, enable, disable, trigger, run")


if __name__ == "__main__":
    main()