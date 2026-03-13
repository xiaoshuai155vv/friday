#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全自动化服务引擎

让系统能够实现真正的 24/7 自动化服务——基于时间、事件、用户行为模式，
自动触发并执行任务，无需用户每次都下指令。

这是「拟人化助手」的终极形态：不需要用户说「帮我做某事」，
系统自己知道什么时候该做什么。

功能：
1. 条件触发引擎 - 时间触发、事件触发、行为模式触发
2. 自动任务调度器 - 智能调度和执行自动化任务
3. 守护进程模式 - 持续监听并响应条件
4. 效果评估与学习 - 评估自动执行效果并优化
5. 与其他引擎深度集成

区别于现有模块：
- automation_execution_engine：执行自动化任务（被动执行）
- full_auto_service_engine：自动触发执行（主动服务）
- proactive_service_trigger：单一触发器，本模块是完整的自动化服务层
"""

import os
import sys
import json
import time
import threading
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Callable, Any, Tuple
from enum import Enum
import signal
import atexit

# 项目根目录
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
RUNTIME_DIR = PROJECT_ROOT / "runtime"
STATE_DIR = RUNTIME_DIR / "state"
LOGS_DIR = RUNTIME_DIR / "logs"
PLANS_DIR = PROJECT_ROOT / "assets" / "plans"

# 添加 scripts 目录到路径
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))


class TriggerType(Enum):
    """触发类型"""
    TIME = "time"           # 定时触发
    EVENT = "event"         # 事件触发
    BEHAVIOR = "behavior"   # 行为模式触发
    CONDITION = "condition" # 条件触发


class ExecutionMode(Enum):
    """执行模式"""
    AUTO = "auto"           # 完全自动执行
    CONFIRM = "confirm"     # 确认后执行
    DRY_RUN = "dry_run"     # 模拟执行


class AutoTask:
    """自动任务定义"""

    def __init__(self, task_id: str, name: str, trigger_config: Dict, action_config: Dict):
        self.task_id = task_id
        self.name = name
        self.trigger_type = TriggerType(trigger_config.get("type", "time"))
        self.trigger_config = trigger_config
        self.action_config = action_config
        self.enabled = trigger_config.get("enabled", True)
        self.last_triggered: Optional[datetime] = None
        self.trigger_count = 0
        self.success_count = 0
        self.last_result: Optional[Dict] = None

    def to_dict(self) -> Dict:
        return {
            "task_id": self.task_id,
            "name": self.name,
            "trigger_type": self.trigger_type.value,
            "trigger_config": self.trigger_config,
            "action_config": self.action_config,
            "enabled": self.enabled,
            "last_triggered": self.last_triggered.isoformat() if self.last_triggered else None,
            "trigger_count": self.trigger_count,
            "success_count": self.success_count,
            "last_result": self.last_result
        }


class FullAutoServiceEngine:
    """智能全自动化服务引擎"""

    def __init__(self):
        self.tasks: Dict[str, AutoTask] = {}
        self.is_running = False
        self.daemon_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        self.execution_mode = ExecutionMode.CONFIRM

        # 加载配置
        self.config = self._load_config()

        # 加载任务
        self._load_tasks()

        # 初始化集成引擎
        self._init_engines()

        # 注册退出清理
        atexit.register(self._cleanup)

    def _load_config(self) -> Dict:
        """加载配置"""
        config_file = STATE_DIR / "full_auto_service_config.json"
        default_config = {
            "execution_mode": "confirm",
            "daemon_interval_seconds": 60,
            "max_tasks_per_hour": 20,
            "enable_time_trigger": True,
            "enable_event_trigger": True,
            "enable_behavior_trigger": True,
            "require_confirmation": True,
            "notification_on_execute": True,
            "learning_enabled": True
        }

        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    return {**default_config, **json.load(f)}
            except Exception:
                pass

        return default_config

    def _save_config(self):
        """保存配置"""
        config_file = STATE_DIR / "full_auto_service_config.json"
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存配置失败: {e}")

    def _load_tasks(self):
        """加载自动任务"""
        tasks_file = STATE_DIR / "auto_tasks.json"
        if tasks_file.exists():
            try:
                with open(tasks_file, 'r', encoding='utf-8') as f:
                    tasks_data = json.load(f)
                    for task_data in tasks_data:
                        task = AutoTask(
                            task_data["task_id"],
                            task_data["name"],
                            task_data["trigger_config"],
                            task_data["action_config"]
                        )
                        task.enabled = task_data.get("enabled", True)
                        task.trigger_count = task_data.get("trigger_count", 0)
                        task.success_count = task_data.get("success_count", 0)
                        if task_data.get("last_triggered"):
                            task.last_triggered = datetime.fromisoformat(task_data["last_triggered"])
                        self.tasks[task.task_id] = task
            except Exception as e:
                print(f"加载任务失败: {e}")

    def _save_tasks(self):
        """保存自动任务"""
        tasks_file = STATE_DIR / "auto_tasks.json"
        try:
            tasks_data = [task.to_dict() for task in self.tasks.values()]
            with open(tasks_file, 'w', encoding='utf-8') as f:
                json.dump(tasks_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存任务失败: {e}")

    def _init_engines(self):
        """初始化集成引擎"""
        # 尝试导入自动化执行引擎
        try:
            from automation_execution_engine import AutomationExecutionEngine
            self.automation_engine = AutomationExecutionEngine()
        except ImportError:
            self.automation_engine = None

        # 尝试导入模式发现引擎
        try:
            from automation_pattern_discovery import AutomationPatternDiscovery
            self.pattern_discovery = AutomationPatternDiscovery()
        except ImportError:
            self.pattern_discovery = None

        # 尝试导入执行增强引擎
        try:
            from execution_enhancement_engine import ExecutionEnhancementEngine
            self.execution_enhancement = ExecutionEnhancementEngine()
        except ImportError:
            self.execution_enhancement = None

        # 尝试导入任务偏好引擎
        try:
            from task_preference_engine import TaskPreferenceEngine
            self.preference_engine = TaskPreferenceEngine()
        except ImportError:
            self.preference_engine = None

    def add_task(self, task: AutoTask):
        """添加自动任务"""
        self.tasks[task.task_id] = task
        self._save_tasks()

    def remove_task(self, task_id: str) -> bool:
        """移除自动任务"""
        if task_id in self.tasks:
            del self.tasks[task_id]
            self._save_tasks()
            return True
        return False

    def enable_task(self, task_id: str) -> bool:
        """启用任务"""
        if task_id in self.tasks:
            self.tasks[task_id].enabled = True
            self._save_tasks()
            return True
        return False

    def disable_task(self, task_id: str) -> bool:
        """禁用任务"""
        if task_id in self.tasks:
            self.tasks[task_id].enabled = False
            self._save_tasks()
            return True
        return False

    def _check_time_triggers(self) -> List[AutoTask]:
        """检查时间触发条件"""
        triggered = []
        now = datetime.now()

        for task in self.tasks.values():
            if not task.enabled or task.trigger_type != TriggerType.TIME:
                continue

            trigger_cfg = task.trigger_config
            schedule_str = trigger_cfg.get("schedule")

            # 解析调度表达式
            if schedule_str:
                # 简单调度：每 N 分钟/小时
                if schedule_str.startswith("every "):
                    if task.last_triggered:
                        interval = trigger_cfg.get("interval_minutes", 60)
                        if (now - task.last_triggered).total_seconds() >= interval * 60:
                            triggered.append(task)
                    elif not task.last_triggered:
                        # 首次触发
                        triggered.append(task)

                # 定时：每天/每周的某个时间
                elif " at " in schedule_str:
                    time_str = schedule_str.split(" at ")[-1]
                    try:
                        target_time = datetime.strptime(time_str, "%H:%M").time()
                        if now.time().hour == target_time.hour and now.time().minute == target_time.minute:
                            # 检查是否今天已经触发过
                            if not task.last_triggered or task.last_triggered.date() != now.date():
                                triggered.append(task)
                    except ValueError:
                        pass

        return triggered

    def _check_behavior_triggers(self) -> List[AutoTask]:
        """检查行为模式触发条件"""
        triggered = []

        # 读取最近的用户行为
        recent_logs = self._get_recent_behavior_logs()

        for task in self.tasks.values():
            if not task.enabled or task.trigger_type != TriggerType.BEHHAVIOR:
                continue

            trigger_cfg = task.trigger_config
            pattern = trigger_cfg.get("pattern")

            if pattern and self._match_behavior_pattern(recent_logs, pattern):
                # 检查冷却时间
                if task.last_triggered:
                    cooldown_minutes = trigger_cfg.get("cooldown_minutes", 60)
                    if (datetime.now() - task.last_triggered).total_seconds() >= cooldown_minutes * 60:
                        triggered.append(task)
                else:
                    triggered.append(task)

        return triggered

    def _get_recent_behavior_logs(self, minutes: int = 60) -> List[Dict]:
        """获取最近的用户行为日志"""
        logs = []
        cutoff = datetime.now() - timedelta(minutes=minutes)

        # 尝试从 recent_logs.json 读取
        recent_logs_file = STATE_DIR / "recent_logs.json"
        if recent_logs_file.exists():
            try:
                with open(recent_logs_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        for entry in data:
                            if isinstance(entry, dict):
                                ts = entry.get("timestamp", "")
                                if ts:
                                    try:
                                        log_time = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                                        if log_time.replace(tzinfo=None) >= cutoff:
                                            logs.append(entry)
                                    except:
                                        pass
            except Exception:
                pass

        return logs

    def _match_behavior_pattern(self, logs: List[Dict], pattern: Dict) -> bool:
        """匹配行为模式"""
        # 简单实现：检查最近是否有匹配的操作
        pattern_type = pattern.get("type")
        pattern_value = pattern.get("value", "")

        for log in logs:
            action = log.get("action", "")
            content = log.get("content", "")

            if pattern_type == "action" and action == pattern_value:
                return True
            if pattern_type == "contains" and pattern_value.lower() in content.lower():
                return True

        return False

    def _execute_task(self, task: AutoTask) -> Dict:
        """执行自动任务"""
        result = {
            "task_id": task.task_id,
            "task_name": task.name,
            "timestamp": datetime.now().isoformat(),
            "success": False,
            "message": "",
            "details": {}
        }

        action_cfg = task.action_config
        action_type = action_cfg.get("type")

        try:
            if action_type == "run_plan":
                # 执行场景计划
                plan_path = action_cfg.get("plan_path")
                if plan_path:
                    plan_file = PLANS_DIR / plan_path
                    if plan_file.exists():
                        cmd = [sys.executable, str(SCRIPT_DIR / "run_plan.py"), str(plan_file)]
                        if self.execution_mode == ExecutionMode.DRY_RUN:
                            result["message"] = f"[DRY RUN] Would execute: {' '.join(cmd)}"
                            result["success"] = True
                        elif self.execution_mode == ExecutionMode.CONFIRM:
                            # 确认模式，返回任务信息等待确认
                            result["message"] = f"需要确认执行: {task.name}"
                            result["details"]["confirmation_needed"] = True
                            result["details"]["task"] = task.to_dict()
                        else:
                            # 自动执行
                            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                            result["success"] = proc.returncode == 0
                            result["message"] = proc.stdout if result["success"] else proc.stderr
                            result["details"]["output"] = proc.stdout
                            result["details"]["error"] = proc.stderr

            elif action_type == "run_script":
                # 执行脚本
                script_name = action_cfg.get("script_name")
                script_args = action_cfg.get("args", [])
                if script_name:
                    script_path = SCRIPT_DIR / script_name
                    if script_path.exists():
                        cmd = [sys.executable, str(script_path)] + script_args
                        if self.execution_mode == ExecutionMode.DRY_RUN:
                            result["message"] = f"[DRY RUN] Would execute: {' '.join(cmd)}"
                            result["success"] = True
                        else:
                            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                            result["success"] = proc.returncode == 0
                            result["message"] = proc.stdout if result["success"] else proc.stderr

            elif action_type == "do_command":
                # 执行 do 命令
                command = action_cfg.get("command")
                if command:
                    cmd = [sys.executable, str(SCRIPT_DIR / "do.py")] + command.split()
                    if self.execution_mode == ExecutionMode.DRY_RUN:
                        result["message"] = f"[DRY RUN] Would execute: {' '.join(cmd)}"
                        result["success"] = True
                    else:
                        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                        result["success"] = proc.returncode == 0
                        result["message"] = proc.stdout if result["success"] else proc.stderr

            elif action_type == "engine_action":
                # 执行引擎动作
                engine_name = action_cfg.get("engine_name")
                action_name = action_cfg.get("action_name")
                params = action_cfg.get("params", {})

                if engine_name and action_name:
                    if self.execution_mode == ExecutionMode.DRY_RUN:
                        result["message"] = f"[DRY RUN] Would execute engine: {engine_name}.{action_name}"
                        result["success"] = True
                    else:
                        result["success"], result["message"] = self._execute_engine_action(
                            engine_name, action_name, params
                        )

            else:
                result["message"] = f"未知动作类型: {action_type}"

        except Exception as e:
            result["message"] = f"执行失败: {str(e)}"

        # 更新任务状态
        task.last_triggered = datetime.now()
        task.trigger_count += 1
        if result["success"]:
            task.success_count += 1
        task.last_result = result
        self._save_tasks()

        # 记录执行日志
        self._log_execution(task, result)

        return result

    def _execute_engine_action(self, engine_name: str, action_name: str, params: Dict) -> Tuple[bool, str]:
        """执行引擎动作"""
        try:
            if engine_name == "automation" and self.automation_engine:
                if hasattr(self.automation_engine, action_name):
                    method = getattr(self.automation_engine, action_name)
                    result = method(**params)
                    return True, str(result)

            elif engine_name == "pattern_discovery" and self.pattern_discovery:
                if hasattr(self.pattern_discovery, action_name):
                    method = getattr(self.pattern_discovery, action_name)
                    result = method(**params)
                    return True, str(result)

            return False, f"引擎 {engine_name} 或动作 {action_name} 不存在"

        except Exception as e:
            return False, str(e)

    def _log_execution(self, task: AutoTask, result: Dict):
        """记录执行日志"""
        log_file = LOGS_DIR / "auto_service_execution.log"
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"[{result['timestamp']}] {task.task_id}: {task.name} - "
                       f"{'SUCCESS' if result['success'] else 'FAILED'} - {result['message']}\n")
        except Exception:
            pass

    def check_and_execute(self) -> List[Dict]:
        """检查所有触发条件并执行"""
        results = []

        # 检查时间触发
        time_triggered = self._check_time_triggers()
        for task in time_triggered:
            result = self._execute_task(task)
            results.append(result)

        # 检查行为触发
        behavior_triggered = self._check_behavior_triggers()
        for task in behavior_triggered:
            result = self._execute_task(task)
            results.append(result)

        return results

    def start_daemon(self, interval_seconds: int = None):
        """启动守护进程模式"""
        if self.is_running:
            return {"success": False, "message": "守护进程已在运行中"}

        if interval_seconds is None:
            interval_seconds = self.config.get("daemon_interval_seconds", 60)

        self.is_running = True
        self.stop_event.clear()

        def daemon_loop():
            while not self.stop_event.is_set():
                try:
                    self.check_and_execute()
                except Exception as e:
                    print(f"守护进程执行错误: {e}")
                self.stop_event.wait(interval_seconds)

        self.daemon_thread = threading.Thread(target=daemon_loop, daemon=True)
        self.daemon_thread.start()

        return {"success": True, "message": f"守护进程已启动，间隔 {interval_seconds} 秒"}

    def stop_daemon(self):
        """停止守护进程"""
        if not self.is_running:
            return {"success": False, "message": "守护进程未运行"}

        self.stop_event.set()
        if self.daemon_thread:
            self.daemon_thread.join(timeout=5)

        self.is_running = False
        return {"success": True, "message": "守护进程已停止"}

    def get_status(self) -> Dict:
        """获取服务状态"""
        return {
            "is_running": self.is_running,
            "total_tasks": len(self.tasks),
            "enabled_tasks": sum(1 for t in self.tasks.values() if t.enabled),
            "execution_mode": self.execution_mode.value,
            "config": self.config,
            "tasks": [task.to_dict() for task in self.tasks.values()]
        }

    def add_default_tasks(self):
        """添加默认的自动任务示例"""
        # 示例1：每天早上自动检查待办事项
        task1 = AutoTask(
            task_id="morning_check",
            name="早上自动检查",
            trigger_config={
                "type": "time",
                "enabled": False,  # 默认禁用
                "schedule": "every 60 minutes",
                "interval_minutes": 60
            },
            action_config={
                "type": "engine_action",
                "engine_name": "long_term_memory",
                "action_name": "get_pending_tasks",
                "params": {}
            }
        )

        # 示例2：检测到重复行为时自动建议自动化
        task2 = AutoTask(
            task_id="auto_automation_suggest",
            name="自动建议自动化",
            trigger_config={
                "type": "behavior",
                "enabled": False,
                "pattern": {"type": "action", "value": "run_plan"},
                "cooldown_minutes": 120
            },
            action_config={
                "type": "engine_action",
                "engine_name": "automation",
                "action_name": "analyze_automation_opportunities",
                "params": {}
            }
        )

        # 示例3：定期系统健康检查
        task3 = AutoTask(
            task_id="system_health_check",
            name="定期系统健康检查",
            trigger_config={
                "type": "time",
                "enabled": False,
                "schedule": "every 60 minutes",
                "interval_minutes": 60
            },
            action_config={
                "type": "engine_action",
                "engine_name": "health",
                "action_name": "check_system_health",
                "params": {}
            }
        )

        self.add_task(task1)
        self.add_task(task2)
        self.add_task(task3)

    def _cleanup(self):
        """清理资源"""
        if self.is_running:
            self.stop_daemon()


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="智能全自动化服务引擎")
    parser.add_argument("command", nargs="?", help="命令: status, start, stop, add-task, list-tasks, enable, disable, check")
    parser.add_argument("--task-id", help="任务ID")
    parser.add_argument("--task-name", help="任务名称")
    parser.add_argument("--trigger-type", default="time", choices=["time", "event", "behavior"], help="触发类型")
    parser.add_argument("--schedule", help="调度表达式")
    parser.add_argument("--action-type", default="do_command", choices=["run_plan", "run_script", "do_command", "engine_action"], help="动作类型")
    parser.add_argument("--action", help="动作内容")
    parser.add_argument("--interval", type=int, default=60, help="守护进程间隔(秒)")

    args = parser.parse_args()
    engine = FullAutoServiceEngine()

    if args.command == "status":
        status = engine.get_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))

    elif args.command == "start":
        result = engine.start_daemon(args.interval)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "stop":
        result = engine.stop_daemon()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "check":
        results = engine.check_and_execute()
        print(json.dumps(results, ensure_ascii=False, indent=2))

    elif args.command == "add-default-tasks":
        engine.add_default_tasks()
        print(json.dumps({"success": True, "message": "已添加默认任务"}, ensure_ascii=False, indent=2))

    elif args.command == "list-tasks":
        tasks = [task.to_dict() for task in engine.tasks.values()]
        print(json.dumps(tasks, ensure_ascii=False, indent=2))

    elif args.command == "enable":
        if args.task_id:
            result = engine.enable_task(args.task_id)
            print(json.dumps({"success": result, "message": "任务已启用" if result else "任务未找到"}, ensure_ascii=False, indent=2))
        else:
            print("请指定 --task-id")

    elif args.command == "disable":
        if args.task_id:
            result = engine.disable_task(args.task_id)
            print(json.dumps({"success": result, "message": "任务已禁用" if result else "任务未找到"}, ensure_ascii=False, indent=2))
        else:
            print("请指定 --task-id")

    elif args.command == "add-task":
        if args.task_name:
            task = AutoTask(
                task_id=args.task_id or f"task_{int(time.time())}",
                name=args.task_name,
                trigger_config={
                    "type": args.trigger_type,
                    "enabled": True,
                    "schedule": args.schedule or "every 60 minutes",
                    "interval_minutes": 60
                },
                action_config={
                    "type": args.action_type,
                    "command": args.action or ""
                }
            )
            engine.add_task(task)
            print(json.dumps({"success": True, "message": f"任务 {args.task_name} 已添加"}, ensure_ascii=False, indent=2))
        else:
            print("请指定 --task-name")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()