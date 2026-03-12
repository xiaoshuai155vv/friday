#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能定时任务调度器 - 根据时间或条件自动执行场景计划

功能：
1. 定时执行场景计划（单次/周期）
2. 条件触发执行（系统状态、时间段等）
3. 任务历史记录
4. 与其他模块协同工作

用法:
  python task_scheduler.py --add --plan <plan_name> --trigger time --cron "09:00" [--days Mon,Tue]
  python task_scheduler.py --add --plan <plan_name> --trigger condition --condition "健康检查"
  python task_scheduler.py --list
  python task_scheduler.py --run <task_id>
  python task_scheduler.py --delete <task_id>
  python task_scheduler.py --daemon [--interval 60]
"""

import argparse
import json
import os
import sys
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path

# 路径配置
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
SCHEDULER_DIR = os.path.join(PROJECT_ROOT, "runtime", "state", "scheduler")
TASKS_FILE = os.path.join(SCHEDULER_DIR, "tasks.json")
HISTORY_FILE = os.path.join(SCHEDULER_DIR, "history.json")

# 导入项目模块
sys.path.insert(0, SCRIPT_DIR)


def ensure_dir():
    """确保目录存在"""
    os.makedirs(SCHEDULER_DIR, exist_ok=True)


def load_tasks():
    """加载任务列表"""
    ensure_dir()
    if not os.path.exists(TASKS_FILE):
        return []
    try:
        with open(TASKS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_tasks(tasks):
    """保存任务列表"""
    ensure_dir()
    with open(TASKS_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)


def load_history():
    """加载执行历史"""
    ensure_dir()
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_history(history):
    """保存执行历史"""
    ensure_dir()
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def parse_cron(cron_str, days=None):
    """
    解析 cron 表达式
    支持格式：HH:MM（每天）、HH:MM on Mon,Tue,Wed（特定日期）
    """
    try:
        hour, minute = map(int, cron_str.split(":"))
        return {
            "hour": hour,
            "minute": minute,
            "days": days.split(",") if days else None
        }
    except Exception:
        return None


def should_run(schedule):
    """判断是否应该执行"""
    now = datetime.now()

    # 检查时间
    if now.hour != schedule.get("hour") or now.minute != schedule.get("minute"):
        return False

    # 检查星期
    days = schedule.get("days")
    if days:
        weekday = now.strftime("%a")  # Mon, Tue, etc.
        if weekday not in days:
            return False

    return True


def run_plan(plan_name):
    """执行场景计划"""
    plan_path = os.path.join(PROJECT_ROOT, "assets", "plans", f"{plan_name}.json")
    if not os.path.exists(plan_path):
        return {"success": False, "error": f"Plan not found: {plan_name}"}

    import subprocess
    try:
        result = subprocess.run(
            [sys.executable, os.path.join(SCRIPT_DIR, "run_plan.py"), plan_path],
            capture_output=True,
            text=True,
            timeout=300,
            cwd=PROJECT_ROOT
        )
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr if result.returncode != 0 else None
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def add_task(plan_name, trigger, schedule=None, condition=None):
    """添加任务"""
    tasks = load_tasks()

    task_id = f"task_{len(tasks) + 1}_{int(time.time())}"

    task = {
        "id": task_id,
        "plan": plan_name,
        "trigger": trigger,
        "schedule": schedule,
        "condition": condition,
        "enabled": True,
        "created_at": datetime.now().isoformat(),
        "last_run": None,
        "run_count": 0
    }

    tasks.append(task)
    save_tasks(tasks)

    print(f"Task added: {task_id}")
    print(f"  Plan: {plan_name}")
    print(f"  Trigger: {trigger}")
    if schedule:
        print(f"  Schedule: {schedule}")
    if condition:
        print(f"  Condition: {condition}")

    return task_id


def list_tasks():
    """列出所有任务"""
    tasks = load_tasks()
    if not tasks:
        print("No scheduled tasks.")
        return

    print(f"\n{'ID':<30} {'Plan':<25} {'Trigger':<12} {'Enabled':<8} {'Last Run':<20}")
    print("-" * 100)

    for task in tasks:
        print(f"{task['id']:<30} {task['plan']:<25} {task['trigger']:<12} {'Yes' if task['enabled'] else 'No':<8} {task.get('last_run') or 'Never':<20}")


def run_task(task_id):
    """手动执行任务"""
    tasks = load_tasks()
    task = None

    for t in tasks:
        if t["id"] == task_id:
            task = t
            break

    if not task:
        print(f"Task not found: {task_id}")
        return

    print(f"Running task: {task['plan']}")

    result = run_plan(task["plan"])

    # 记录历史
    history = load_history()
    history.append({
        "task_id": task_id,
        "plan": task["plan"],
        "run_at": datetime.now().isoformat(),
        "result": result
    })
    save_history(history[-100:])  # 保留最近100条

    # 更新任务
    task["last_run"] = datetime.now().isoformat()
    task["run_count"] = task.get("run_count", 0) + 1
    save_tasks(tasks)

    if result.get("success"):
        print("Task completed successfully.")
    else:
        print(f"Task failed: {result.get('error')}")


def delete_task(task_id):
    """删除任务"""
    tasks = load_tasks()
    tasks = [t for t in tasks if t["id"] != task_id]
    save_tasks(tasks)
    print(f"Task deleted: {task_id}")


def daemon_mode(interval=60):
    """守护进程模式"""
    print(f"Scheduler daemon started (interval: {interval}s)")

    while True:
        tasks = load_tasks()

        for task in tasks:
            if not task.get("enabled", True):
                continue

            if task["trigger"] == "time" and task.get("schedule"):
                if should_run(task["schedule"]):
                    # 检查是否刚执行过（避免重复执行）
                    last_run = task.get("last_run")
                    if last_run:
                        last_dt = datetime.fromisoformat(last_run)
                        if (datetime.now() - last_dt).total_seconds() < 120:
                            continue

                    print(f"\n[Scheduler] Running task: {task['plan']}")
                    result = run_plan(task["plan"])

                    # 更新任务状态
                    task["last_run"] = datetime.now().isoformat()
                    task["run_count"] = task.get("run_count", 0) + 1
                    save_tasks(tasks)

                    # 记录历史
                    history = load_history()
                    history.append({
                        "task_id": task["id"],
                        "plan": task["plan"],
                        "run_at": datetime.now().isoformat(),
                        "result": result
                    })
                    save_history(history[-100:])

        time.sleep(interval)


def main():
    parser = argparse.ArgumentParser(description="智能定时任务调度器")
    parser.add_argument("--add", action="store_true", help="添加任务")
    parser.add_argument("--plan", help="场景计划名称")
    parser.add_argument("--trigger", choices=["time", "condition", "manual"], help="触发类型")
    parser.add_argument("--cron", help="时间计划 (HH:MM)")
    parser.add_argument("--days", help="星期几 (Mon,Tue,...)")
    parser.add_argument("--condition", help="触发条件")
    parser.add_argument("--list", action="store_true", help="列出所有任务")
    parser.add_argument("--run", metavar="TASK_ID", help="手动执行任务")
    parser.add_argument("--delete", metavar="TASK_ID", help="删除任务")
    parser.add_argument("--daemon", action="store_true", help="守护进程模式")
    parser.add_argument("--interval", type=int, default=60, help="守护进程检查间隔(秒)")

    args = parser.parse_args()

    if args.add:
        if not args.plan or not args.trigger:
            print("Error: --plan and --trigger are required for --add")
            sys.exit(1)

        schedule = None
        if args.trigger == "time":
            if not args.cron:
                print("Error: --cron is required for time trigger")
                sys.exit(1)
            schedule = parse_cron(args.cron, args.days)
            if not schedule:
                print("Error: Invalid cron format. Use HH:MM")
                sys.exit(1)

        add_task(args.plan, args.trigger, schedule, args.condition)

    elif args.list:
        list_tasks()

    elif args.run:
        run_task(args.run)

    elif args.delete:
        delete_task(args.delete)

    elif args.daemon:
        daemon_mode(args.interval)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()