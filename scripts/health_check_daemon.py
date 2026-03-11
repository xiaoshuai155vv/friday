#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动健康检查守护进程
支持定时自动执行系统健康检查并更新状态
"""

import json
import os
import sys
import time
import signal
import argparse
import threading
from datetime import datetime
from pathlib import Path

# 添加项目根目录到路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, PROJECT_ROOT)

# 状态和日志目录
RUNTIME_DIR = os.path.join(PROJECT_ROOT, "runtime")
STATE_DIR = os.path.join(RUNTIME_DIR, "state")
LOGS_DIR = os.path.join(RUNTIME_DIR, "logs")

# 历史健康记录文件
HEALTH_HISTORY_FILE = os.path.join(STATE_DIR, "health_check_history.json")
DAEMON_STATUS_FILE = os.path.join(STATE_DIR, "health_daemon_status.json")


class HealthCheckDaemon:
    """健康检查守护进程"""

    def __init__(self, interval=300, daemon_mode=False):
        """
        初始化守护进程

        Args:
            interval: 检查间隔（秒），默认 5 分钟
            daemon_mode: 是否作为守护进程运行
        """
        self.interval = interval
        self.daemon_mode = daemon_mode
        self.running = False
        self.check_count = 0

    def load_health_check_module(self):
        """动态加载健康检查模块"""
        health_check_path = os.path.join(SCRIPT_DIR, "system_health_check.py")
        if not os.path.exists(health_check_path):
            return None

        spec = __import__("importlib.util").util.spec_from_file_location(
            "system_health_check", health_check_path
        )
        module = __import__("importlib.util").util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def run_single_check(self):
        """执行一次健康检查"""
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Running health check...")

        # 导入并运行健康检查
        health_module = self.load_health_check_module()
        if health_module and hasattr(health_module, 'run_health_check'):
            report = health_module.run_health_check()
        else:
            # 如果无法导入模块，执行基本检查
            report = self._basic_check()

        self.check_count += 1
        report["check_number"] = self.check_count

        # 保存到历史记录
        self._save_to_history(report)

        # 更新守护进程状态
        self._update_daemon_status(report)

        # 输出检查结果
        status_icon = "[OK]" if report["status"] == "healthy" else "[FAIL]"
        print(f"{status_icon} Health check #{self.check_count}: {report['status']}")

        return report

    def _basic_check(self):
        """基本健康检查（当无法导入模块时）"""
        report = {
            "check_time": datetime.now().isoformat(),
            "status": "healthy",
            "components": [],
            "check_number": self.check_count
        }

        # 检查核心脚本是否存在
        core_scripts = [
            "screenshot_tool.py",
            "mouse_tool.py",
            "keyboard_tool.py",
            "vision_proxy.py",
            "clipboard_tool.py",
            "run_plan.py"
        ]

        for script in core_scripts:
            script_path = os.path.join(SCRIPT_DIR, script)
            exists = os.path.exists(script_path)
            report["components"].append({
                "component": script,
                "status": "healthy" if exists else "missing",
                "message": "存在" if exists else "不存在"
            })
            if not exists:
                report["status"] = "degraded"

        return report

    def _save_to_history(self, report):
        """保存检查结果到历史记录"""
        os.makedirs(STATE_DIR, exist_ok=True)

        # 读取现有历史
        history = []
        if os.path.exists(HEALTH_HISTORY_FILE):
            try:
                with open(HEALTH_HISTORY_FILE, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            except Exception:
                pass

        # 添加新记录（保留最近 100 条）
        history.append(report)
        history = history[-100:]

        # 保存
        try:
            with open(HEALTH_HISTORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Failed to save health history: {e}")

    def _update_daemon_status(self, latest_report):
        """更新守护进程状态"""
        os.makedirs(STATE_DIR, exist_ok=True)

        status = {
            "daemon_running": self.running,
            "last_check_time": latest_report["check_time"],
            "last_status": latest_report["status"],
            "check_count": self.check_count,
            "interval_seconds": self.interval,
            "updated_at": datetime.now().isoformat()
        }

        try:
            with open(DAEMON_STATUS_FILE, 'w', encoding='utf-8') as f:
                json.dump(status, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Failed to update daemon status: {e}")

    def run(self):
        """运行守护进程"""
        self.running = True

        # 初始检查
        self.run_single_check()

        print(f"Health check daemon started. Interval: {self.interval} seconds")
        print("Press Ctrl+C to stop")

        # 守护循环
        while self.running:
            time.sleep(self.interval)
            if self.running:
                self.run_single_check()

    def stop(self):
        """停止守护进程"""
        print("\nStopping health check daemon...")
        self.running = False
        self._update_daemon_status({
            "check_time": datetime.now().isoformat(),
            "status": "stopped",
            "check_number": self.check_count
        })


def get_daemon_status():
    """获取守护进程状态"""
    if os.path.exists(DAEMON_STATUS_FILE):
        try:
            with open(DAEMON_STATUS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass

    return {
        "daemon_running": False,
        "last_check_time": None,
        "last_status": "never_run",
        "check_count": 0
    }


def get_health_history(limit=10):
    """获取健康检查历史"""
    if os.path.exists(HEALTH_HISTORY_FILE):
        try:
            with open(HEALTH_HISTORY_FILE, 'r', encoding='utf-8') as f:
                history = json.load(f)
                return history[-limit:] if len(history) > limit else history
        except Exception:
            pass

    return []


def main():
    """主函数"""
    # 设置输出编码
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')

    parser = argparse.ArgumentParser(description="自动健康检查守护进程")
    parser.add_argument("--start", action="store_true", help="启动守护进程")
    parser.add_argument("--stop", action="store_true", help="停止守护进程")
    parser.add_argument("--once", action="store_true", help="执行一次健康检查")
    parser.add_argument("--status", action="store_true", help="查看守护进程状态")
    parser.add_argument("--history", action="store_true", help="查看健康检查历史")
    parser.add_argument("--interval", type=int, default=300, help="检查间隔（秒），默认 300")
    parser.add_argument("--daemon", "-d", action="store_true", help="以后台守护进程模式运行")

    args = parser.parse_args()

    # 显示状态
    if args.status:
        status = get_daemon_status()
        print(json.dumps(status, indent=2, ensure_ascii=False))
        return 0

    # 显示历史
    if args.history:
        history = get_health_history(20)
        print(json.dumps(history, indent=2, ensure_ascii=False))
        return 0

    # 执行一次检查
    if args.once:
        daemon = HealthCheckDaemon(interval=args.interval)
        report = daemon.run_single_check()
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return 0 if report["status"] == "healthy" else 1

    # 启动守护进程
    if args.start or args.daemon:
        daemon = HealthCheckDaemon(interval=args.interval, daemon_mode=True)

        # 设置信号处理
        def signal_handler(sig, frame):
            daemon.stop()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        daemon.run()
        return 0

    # 默认显示状态
    status = get_daemon_status()
    print("Health Check Daemon Status:")
    print(json.dumps(status, indent=2, ensure_ascii=False))
    print("\nUsage:")
    print("  python health_check_daemon.py --start          # 启动守护进程")
    print("  python health_check_daemon.py --once          # 执行一次检查")
    print("  python health_check_daemon.py --status         # 查看状态")
    print("  python health_check_daemon.py --history        # 查看历史")
    print("  python health_check_daemon.py --start --interval 600  # 每 10 分钟检查一次")

    return 0


if __name__ == "__main__":
    sys.exit(main())