#!/usr/bin/env python3
"""
进化环定时触发器
实现定时/间隔自动运行进化环的能力，让系统能够周期性自动执行进化
支持配置触发间隔，后台守护进程模式，与现有 evolution_loop_automation.py 集成
"""

import os
import sys
import json
import time
import signal
import threading
import subprocess
import argparse
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from pathlib import Path

# 添加 scripts 目录到路径
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPTS_DIR)

# 配置文件路径
CONFIG_FILE = os.path.join(SCRIPTS_DIR, "runtime/state/evolution_scheduler_config.json")
STATE_FILE = os.path.join(SCRIPTS_DIR, "runtime/state/evolution_scheduler_state.json")
LOG_FILE = os.path.join(SCRIPTS_DIR, "runtime/logs/evolution_scheduler.log")

# 默认配置
DEFAULT_CONFIG = {
    "enabled": True,
    "interval_hours": 24,  # 默认每24小时运行一次
    "interval_minutes": 0,
    "max_runs_per_day": 10,
    "run_on_startup": False,
    "daemon_mode": False,
    "last_run": None,
    "next_run": None,
    "total_runs": 0,
    "failed_runs": 0
}


def load_config() -> Dict[str, Any]:
    """加载配置文件"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # 合并默认配置
                merged = DEFAULT_CONFIG.copy()
                merged.update(config)
                return merged
        except Exception as e:
            print(f"加载配置文件失败: {e}")
    return DEFAULT_CONFIG.copy()


def save_config(config: Dict[str, Any]):
    """保存配置文件"""
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def load_state() -> Dict[str, Any]:
    """加载状态文件"""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载状态文件失败: {e}")
    return {
        "running": False,
        "daemon_pid": None,
        "start_time": None
    }


def save_state(state: Dict[str, Any]):
    """保存状态文件"""
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def log(message: str, level: str = "INFO"):
    """记录日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [{level}] {message}"
    print(log_entry)

    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_entry + "\n")


def run_evolution_loop() -> bool:
    """运行进化闭环"""
    try:
        log("启动进化闭环自动化引擎...")
        result = subprocess.run(
            [sys.executable, os.path.join(SCRIPTS_DIR, "evolution_loop_automation.py")],
            capture_output=True,
            text=True,
            timeout=300,
            cwd=SCRIPTS_DIR
        )

        if result.returncode == 0:
            log("进化闭环自动化引擎执行成功")
            return True
        else:
            log(f"进化闭环自动化引擎执行失败: {result.stderr}", "ERROR")
            return False
    except subprocess.TimeoutExpired:
        log("进化闭环执行超时", "ERROR")
        return False
    except Exception as e:
        log(f"运行进化闭环时发生错误: {e}", "ERROR")
        return False


def calculate_next_run(config: Dict[str, Any]) -> datetime:
    """计算下次运行时间"""
    now = datetime.now()
    interval = timedelta(hours=config.get("interval_hours", 24), minutes=config.get("interval_minutes", 0))
    return now + interval


def should_run(config: Dict[str, Any]) -> bool:
    """检查是否应该运行"""
    if not config.get("enabled", True):
        return False

    last_run = config.get("last_run")
    if last_run:
        try:
            last_run_time = datetime.fromisoformat(last_run)
            next_run = calculate_next_run(config)
            if datetime.now() < next_run:
                return False
        except Exception:
            pass

    # 检查每日运行次数限制
    today = datetime.now().strftime("%Y-%m-%d")
    runs_today = config.get(f"runs_{today}", 0)
    max_runs = config.get("max_runs_per_day", 10)

    if runs_today >= max_runs:
        log(f"已达到每日运行次数上限 ({max_runs})", "WARNING")
        return False

    return True


def update_run_stats(success: bool):
    """更新运行统计"""
    config = load_config()
    today = datetime.now().strftime("%Y-%m-%d")

    config["last_run"] = datetime.now().isoformat()
    config["next_run"] = calculate_next_run(config).isoformat()
    config["total_runs"] = config.get("total_runs", 0) + 1
    config[f"runs_{today}"] = config.get(f"runs_{today}", 0) + 1

    if not success:
        config["failed_runs"] = config.get("failed_runs", 0) + 1

    save_config(config)


def scheduler_loop(interval_check: int = 60):
    """调度主循环"""
    log("进化环定时触发器开始运行...")

    config = load_config()

    if config.get("run_on_startup", False):
        log("配置为启动时运行，执行进化闭环...")
        success = run_evolution_loop()
        update_run_stats(success)

    while True:
        try:
            if should_run(config):
                log("触发进化闭环执行...")
                success = run_evolution_loop()
                update_run_stats(success)

            # 等待下一次检查
            time.sleep(interval_check)

            # 重新加载配置（支持热更新）
            config = load_config()

        except KeyboardInterrupt:
            log("接收到中断信号，退出调度器")
            break
        except Exception as e:
            log(f"调度器发生错误: {e}", "ERROR")
            time.sleep(interval_check)


def start_daemon():
    """启动守护进程模式"""
    pid = os.fork()
    if pid > 0:
        # 父进程退出
        sys.exit(0)

    # 子进程成为新的会话领导者
    os.setsid()

    # 再次 fork，确保进程不会成为会话领导者
    pid = os.fork()
    if pid > 0:
        sys.exit(0)

    # 重定向标准文件描述符
    sys.stdout.flush()
    sys.stderr.flush()

    with open('/dev/null', 'r') as f:
        os.dup2(f.fileno(), sys.stdin.fileno())
    with open('/dev/null', 'a+') as f:
        os.dup2(f.fileno(), sys.stdout.fileno())
        os.dup2(f.fileno(), sys.stderr.fileno())

    # 保存守护进程 PID
    state = load_state()
    state["running"] = True
    state["daemon_pid"] = os.getpid()
    state["start_time"] = datetime.now().isoformat()
    save_state(state)

    log("守护进程模式启动成功", "INFO")

    # 运行调度主循环
    scheduler_loop()


def stop_daemon():
    """停止守护进程"""
    state = load_state()
    daemon_pid = state.get("daemon_pid")

    if daemon_pid:
        try:
            os.kill(daemon_pid, signal.SIGTERM)
            log(f"已发送终止信号到守护进程 (PID: {daemon_pid})")
            state["running"] = False
            state["daemon_pid"] = None
            save_state(state)
            return True
        except ProcessLookupError:
            log("守护进程不存在", "WARNING")
        except Exception as e:
            log(f"停止守护进程失败: {e}", "ERROR")

    return False


def status():
    """查看调度器状态"""
    config = load_config()
    state = load_state()

    print("=== 进化环定时触发器状态 ===")
    print(f"启用状态: {'已启用' if config.get('enabled') else '已禁用'}")
    print(f"运行间隔: {config.get('interval_hours')} 小时 {config.get('interval_minutes')} 分钟")
    print(f"每日最大运行次数: {config.get('max_runs_per_day')}")
    print(f"启动时运行: {'是' if config.get('run_on_startup') else '否'}")
    print(f"守护进程运行: {'是' if state.get('running') else '否'}")
    print(f"守护进程PID: {state.get('daemon_pid')}")
    print(f"上次运行: {config.get('last_run')}")
    print(f"下次运行: {config.get('next_run')}")
    print(f"总运行次数: {config.get('total_runs')}")
    print(f"失败次数: {config.get('failed_runs')}")
    print(f"启动时间: {state.get('start_time')}")
    print("================================")


def set_config(key: str, value: Any):
    """设置配置项"""
    config = load_config()

    if key == "interval":
        # 支持格式: 24h, 30m, 1h30m
        if isinstance(value, str):
            hours = 0
            minutes = 0
            value = value.lower()
            if 'h' in value:
                parts = value.split('h')
                hours = int(parts[0])
                value = parts[1] if parts[1] else '0'
            if 'm' in value:
                minutes = int(value.replace('m', ''))
            config["interval_hours"] = hours
            config["interval_minutes"] = minutes
    elif key == "enabled":
        config["enabled"] = value in [True, "true", "1", "yes"]
    elif key in ["interval_hours", "interval_minutes", "max_runs_per_day", "run_on_startup", "daemon_mode"]:
        config[key] = value
    else:
        print(f"未知配置项: {key}")
        return False

    save_config(config)
    print(f"已设置 {key} = {value}")
    return True


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="进化环定时触发器")
    parser.add_argument("command", nargs="?", choices=["start", "stop", "restart", "status", "run", "enable", "disable"], help="命令")
    parser.add_argument("--interval", help="设置运行间隔 (如 24h, 30m, 1h30m)")
    parser.add_argument("--max-runs", type=int, help="设置每日最大运行次数")
    parser.add_argument("--on-startup", action="store_true", help="启动时运行")
    parser.add_argument("--daemon", action="store_true", help="守护进程模式")

    args = parser.parse_args()

    if args.command == "status":
        status()
    elif args.command == "start":
        if args.daemon or load_config().get("daemon_mode"):
            log("以守护进程模式启动...")
            start_daemon()
        else:
            log("以交互模式启动...")
            scheduler_loop()
    elif args.command == "stop":
        stop_daemon()
    elif args.command == "restart":
        stop_daemon()
        time.sleep(2)
        start_daemon()
    elif args.command == "run":
        # 立即运行一次
        log("手动触发进化闭环执行...")
        success = run_evolution_loop()
        update_run_stats(success)
        if success:
            print("进化闭环执行成功")
            sys.exit(0)
        else:
            print("进化闭环执行失败")
            sys.exit(1)
    elif args.command == "enable":
        set_config("enabled", True)
    elif args.command == "disable":
        set_config("enabled", False)
    else:
        # 设置配置
        if args.interval:
            set_config("interval", args.interval)
        if args.max_runs:
            set_config("max_runs_per_day", args.max_runs)
        if args.on_startup:
            set_config("run_on_startup", True)

        if not args.command:
            status()
        else:
            parser.print_help()


if __name__ == "__main__":
    main()