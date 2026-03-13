#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
智能守护进程管理器 (Daemon Manager)
统一管理系统中所有守护进程的启动、停止、监控和自动恢复，
实现系统级持续自动服务能力。

支持的功能：
- 守护进程注册与管理
- 启动/停止/重启守护进程
- 运行状态监控
- 故障自动恢复
- 与 do.py 集成支持关键词触发

使用方法：
    python daemon_manager.py start <daemon_name>     # 启动指定守护进程
    python daemon_manager.py stop <daemon_name>      # 停止指定守护进程
    python daemon_manager.py restart <daemon_name>   # 重启指定守护进程
    python daemon_manager.py status [daemon_name]    # 查看守护进程状态
    python daemon_manager.py list                     # 列出所有守护进程
    python daemon_manager.py enable <daemon_name>    # 启用守护进程自动启动
    python daemon_manager.py disable <daemon_name>   # 禁用守护进程自动启动
"""

import os
import sys
import json
import time
import signal
import threading
import subprocess
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

# 配置日志
SCRIPT_DIR = Path(__file__).parent
LOG_DIR = SCRIPT_DIR.parent / "runtime" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "daemon_manager.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("daemon_manager")

# 守护进程状态文件
DAEMON_STATE_FILE = SCRIPT_DIR.parent / "runtime" / "state" / "daemon_manager_state.json"

# 守护进程配置
DAEMON_REGISTRY = {
    "health_check": {
        "name": "health_check",
        "description": "系统健康检查守护进程 - 定期监控系统状态并报告健康状况",
        "script": "health_check_daemon.py",
        "auto_start": False,
        "restart_on_failure": True,
        "check_interval": 60,  # 秒
    },
    "evolution_loop": {
        "name": "evolution_loop",
        "description": "进化环守护进程 - 自动执行进化任务",
        "script": "evolution_loop_daemon.py",
        "auto_start": False,
        "restart_on_failure": True,
        "check_interval": 300,  # 5分钟
    },
    "health_assurance": {
        "name": "health_assurance",
        "description": "健康保障守护进程 - 在后台持续运行系统健康保障闭环（监控→预测→运维→自愈→反馈），自动执行优化和修复",
        "script": "health_assurance_daemon.py",
        "auto_start": False,
        "restart_on_failure": True,
        "check_interval": 300,  # 5分钟检查一次
    },
    "daemon_linkage": {
        "name": "daemon_linkage",
        "description": "守护进程间联动引擎 - 实现跨守护进程的任务传递和自动触发，形成多守护进程协同的主动服务体系",
        "script": "daemon_linkage_engine.py",
        "auto_start": False,
        "restart_on_failure": True,
        "check_interval": 30,  # 30秒检查一次
    },
}


class DaemonManager:
    """守护进程管理器类"""

    def __init__(self):
        self.daemons: Dict[str, Dict[str, Any]] = {}
        self.daemon_processes: Dict[str, subprocess.Popen] = {}
        self.daemon_threads: Dict[str, threading.Thread] = {}
        self.running = False
        self._lock = threading.Lock()
        self._load_state()

    def _load_state(self):
        """加载守护进程状态"""
        if DAEMON_STATE_FILE.exists():
            try:
                with open(DAEMON_STATE_FILE, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                    self.daemons = state.get('daemons', {})
                    logger.info(f"已加载 {len(self.daemons)} 个守护进程配置")
            except Exception as e:
                logger.error(f"加载守护进程状态失败: {e}")
                self.daemons = {}
        else:
            # 初始化默认状态
            self.daemons = {
                name: {
                    'status': 'stopped',
                    'enabled': config.get('auto_start', False),
                    'start_time': None,
                    'restart_count': 0,
                    'last_error': None,
                }
                for name, config in DAEMON_REGISTRY.items()
            }
            self._save_state()

    def _save_state(self):
        """保存守护进程状态"""
        try:
            DAEMON_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(DAEMON_STATE_FILE, 'w', encoding='utf-8') as f:
                json.dump({
                    'daemons': self.daemons,
                    'updated_at': datetime.now().isoformat(),
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存守护进程状态失败: {e}")

    def list_daemons(self) -> List[Dict[str, Any]]:
        """列出所有守护进程"""
        result = []
        for name, config in DAEMON_REGISTRY.items():
            status = self.daemons.get(name, {}).get('status', 'stopped')
            enabled = self.daemons.get(name, {}).get('enabled', False)
            result.append({
                'name': name,
                'description': config.get('description', ''),
                'status': status,
                'enabled': enabled,
                'auto_start': config.get('auto_start', False),
                'restart_on_failure': config.get('restart_on_failure', True),
            })
        return result

    def get_daemon_status(self, name: str) -> Optional[Dict[str, Any]]:
        """获取指定守护进程状态"""
        if name not in DAEMON_REGISTRY:
            return None

        config = DAEMON_REGISTRY[name]
        state = self.daemons.get(name, {})

        # 检查进程是否还在运行
        process_running = False
        if name in self.daemon_processes:
            proc = self.daemon_processes[name]
            if proc.poll() is None:
                process_running = True

        return {
            'name': name,
            'description': config.get('description', ''),
            'status': state.get('status', 'stopped'),
            'enabled': state.get('enabled', False),
            'process_running': process_running,
            'start_time': state.get('start_time'),
            'restart_count': state.get('restart_count', 0),
            'last_error': state.get('last_error'),
        }

    def start_daemon(self, name: str) -> bool:
        """启动守护进程"""
        if name not in DAEMON_REGISTRY:
            logger.error(f"未知守护进程: {name}")
            return False

        with self._lock:
            # 检查是否已经在运行
            if name in self.daemon_processes:
                proc = self.daemon_processes[name]
                if proc.poll() is None:
                    logger.info(f"守护进程 {name} 已在运行")
                    return True

            config = DAEMON_REGISTRY[name]
            script_path = SCRIPT_DIR / config['script']

            if not script_path.exists():
                logger.error(f"守护进程脚本不存在: {script_path}")
                return False

            try:
                # 启动进程
                proc = subprocess.Popen(
                    [sys.executable, str(script_path)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=str(SCRIPT_DIR),
                )
                self.daemon_processes[name] = proc

                # 更新状态
                self.daemons[name] = {
                    'status': 'running',
                    'enabled': self.daemons.get(name, {}).get('enabled', False),
                    'start_time': datetime.now().isoformat(),
                    'restart_count': self.daemons.get(name, {}).get('restart_count', 0),
                    'last_error': None,
                }
                self._save_state()

                logger.info(f"守护进程 {name} 已启动 (PID: {proc.pid})")
                return True

            except Exception as e:
                logger.error(f"启动守护进程 {name} 失败: {e}")
                self.daemons[name] = {
                    'status': 'error',
                    'enabled': self.daemons.get(name, {}).get('enabled', False),
                    'start_time': None,
                    'restart_count': 0,
                    'last_error': str(e),
                }
                self._save_state()
                return False

    def stop_daemon(self, name: str) -> bool:
        """停止守护进程"""
        if name not in DAEMON_REGISTRY:
            logger.error(f"未知守护进程: {name}")
            return False

        with self._lock:
            if name not in self.daemon_processes:
                logger.info(f"守护进程 {name} 未运行")
                return True

            proc = self.daemon_processes[name]

            try:
                # 尝试正常终止
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    # 强制终止
                    proc.kill()
                    proc.wait()

                del self.daemon_processes[name]

                # 更新状态
                self.daemons[name] = {
                    'status': 'stopped',
                    'enabled': self.daemons.get(name, {}).get('enabled', False),
                    'start_time': None,
                    'restart_count': 0,
                    'last_error': None,
                }
                self._save_state()

                logger.info(f"守护进程 {name} 已停止")
                return True

            except Exception as e:
                logger.error(f"停止守护进程 {name} 失败: {e}")
                return False

    def restart_daemon(self, name: str) -> bool:
        """重启守护进程"""
        logger.info(f"重启守护进程 {name}")
        self.stop_daemon(name)
        time.sleep(1)
        return self.start_daemon(name)

    def enable_daemon(self, name: str) -> bool:
        """启用守护进程自动启动"""
        if name not in DAEMON_REGISTRY:
            logger.error(f"未知守护进程: {name}")
            return False

        with self._lock:
            if name not in self.daemons:
                self.daemons[name] = {}

            self.daemons[name]['enabled'] = True
            self._save_state()
            logger.info(f"守护进程 {name} 已启用自动启动")
            return True

    def disable_daemon(self, name: str) -> bool:
        """禁用守护进程自动启动"""
        if name not in DAEMON_REGISTRY:
            logger.error(f"未知守护进程: {name}")
            return False

        with self._lock:
            if name not in self.daemons:
                self.daemons[name] = {}

            self.daemons[name]['enabled'] = False
            self._save_state()
            logger.info(f"守护进程 {name} 已禁用自动启动")
            return True

    def monitor_daemons(self):
        """监控守护进程状态，自动重启失败的进程"""
        logger.info("开始守护进程监控")

        while self.running:
            try:
                with self._lock:
                    for name in list(self.daemon_processes.keys()):
                        proc = self.daemon_processes[name]

                        # 检查进程是否还在运行
                        if proc.poll() is not None:
                            # 进程已退出
                            config = DAEMON_REGISTRY.get(name, {})

                            if config.get('restart_on_failure', True):
                                logger.warning(f"守护进程 {name} 已退出，尝试重启")

                                # 增加重启计数
                                if name in self.daemons:
                                    self.daemons[name]['restart_count'] = \
                                        self.daemons[name].get('restart_count', 0) + 1

                                # 重新启动
                                self.start_daemon(name)
                            else:
                                logger.warning(f"守护进程 {name} 已退出，不自动重启")
                                del self.daemon_processes[name]

                                # 更新状态
                                self.daemons[name]['status'] = 'stopped'
                                self._save_state()

            except Exception as e:
                logger.error(f"监控守护进程时出错: {e}")

            time.sleep(10)  # 每10秒检查一次

        logger.info("守护进程监控已停止")

    def start_monitoring(self):
        """启动守护进程监控线程"""
        if not self.running:
            self.running = True
            self.monitor_thread = threading.Thread(target=self.monitor_daemons, daemon=True)
            self.monitor_thread.start()
            logger.info("守护进程监控已启动")

    def stop_monitoring(self):
        """停止守护进程监控"""
        self.running = False
        logger.info("守护进程监控已停止")


def main():
    """主函数 - 命令行入口"""
    if len(sys.argv) < 2:
        # 无参数时启动交互式状态查看
        manager = DaemonManager()
        daemons = manager.list_daemons()
        print("\n=== 守护进程列表 ===")
        for d in daemons:
            status_icon = "●" if d['status'] == 'running' else "○"
            auto_icon = "✓" if d['auto_start'] else " "
            print(f"{status_icon} {d['name']:20s} [{d['status']:10s}] {auto_icon} {d['description']}")
        print()
        return

    command = sys.argv[1].lower()
    manager = DaemonManager()

    if command == "list":
        daemons = manager.list_daemons()
        print("\n=== 守护进程列表 ===")
        for d in daemons:
            status_icon = "●" if d['status'] == 'running' else "○"
            auto_icon = "✓" if d['auto_start'] else " "
            print(f"{status_icon} {d['name']:20s} [{d['status']:10s}] {auto_icon} {d['description']}")
        print()

    elif command == "status":
        if len(sys.argv) > 2:
            name = sys.argv[2]
            status = manager.get_daemon_status(name)
            if status:
                print(f"\n=== 守护进程 {name} 状态 ===")
                print(f"描述: {status['description']}")
                print(f"状态: {status['status']}")
                print(f"启用: {'是' if status['enabled'] else '否'}")
                print(f"进程运行: {'是' if status['process_running'] else '否'}")
                print(f"启动时间: {status['start_time'] or 'N/A'}")
                print(f"重启次数: {status['restart_count']}")
                print(f"最后错误: {status['last_error'] or '无'}")
                print()
            else:
                print(f"错误: 未知守护进程 {name}")

        else:
            # 显示所有守护进程状态
            daemons = manager.list_daemons()
            print("\n=== 守护进程状态 ===")
            for d in daemons:
                status = manager.get_daemon_status(d['name'])
                status_icon = "●" if status['process_running'] else "○"
                print(f"{status_icon} {d['name']:20s} {status['status']:10s} 重启:{status['restart_count']}")
            print()

    elif command == "start":
        if len(sys.argv) > 2:
            name = sys.argv[2]
            if manager.start_daemon(name):
                print(f"守护进程 {name} 已启动")
            else:
                print(f"守护进程 {name} 启动失败")
        else:
            print("用法: python daemon_manager.py start <daemon_name>")

    elif command == "stop":
        if len(sys.argv) > 2:
            name = sys.argv[2]
            if manager.stop_daemon(name):
                print(f"守护进程 {name} 已停止")
            else:
                print(f"守护进程 {name} 停止失败")
        else:
            print("用法: python daemon_manager.py stop <daemon_name>")

    elif command == "restart":
        if len(sys.argv) > 2:
            name = sys.argv[2]
            if manager.restart_daemon(name):
                print(f"守护进程 {name} 已重启")
            else:
                print(f"守护进程 {name} 重启失败")
        else:
            print("用法: python daemon_manager.py restart <daemon_name>")

    elif command == "enable":
        if len(sys.argv) > 2:
            name = sys.argv[2]
            if manager.enable_daemon(name):
                print(f"守护进程 {name} 已启用自动启动")
            else:
                print(f"守护进程 {name} 启用失败")
        else:
            print("用法: python daemon_manager.py enable <daemon_name>")

    elif command == "disable":
        if len(sys.argv) > 2:
            name = sys.argv[2]
            if manager.disable_daemon(name):
                print(f"守护进程 {name} 已禁用自动启动")
            else:
                print(f"守护进程 {name} 禁用失败")
        else:
            print("用法: python daemon_manager.py disable <daemon_name>")

    else:
        print(f"未知命令: {command}")
        print("可用命令: list, status, start, stop, restart, enable, disable")


if __name__ == "__main__":
    main()