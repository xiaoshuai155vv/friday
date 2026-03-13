#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
智能跨会话任务接续引擎
让系统能够追踪长时间运行的任务状态，实现跨会话的任务接续能力。
当用户开启复杂任务后关闭对话，再次打开时能够恢复任务状态，继续执行未完成的工作。
这是「超越用户」的体现：人关闭电脑后会丢失任务上下文，但 AI 可以自动保存和恢复。

功能：
- 任务状态持久化：保存任务ID、当前步骤、已完成/待执行、环境快照
- 任务恢复功能：根据保存的状态恢复执行
- 任务历史查询：查看之前的任务进度
- 长时间任务追踪：追踪需要多会话完成的任务

用法:
  python task_continuation_engine.py start "<任务名称>" --steps "步骤1|步骤2|步骤3"
  python task_continuation_engine.py status [--task-id <id>]
  python task_continuation_engine.py resume <task_id>
  python task_continuation_engine.py complete <task_id> --step <step_index>
  python task_continuation_engine.py fail <task_id> --reason "<失败原因>"
  python task_continuation_engine.py list [--status pending|running|completed|failed]
  python task_continuation_engine.py history [--limit <n>]
  python task_continuation_engine.py snapshot <task_id> --data "<环境数据>"
  python task_continuation_engine.py delete <task_id>
  python task_continuation_engine.py env --save <task_id>
  python task_continuation_engine.py env --restore <task_id>
"""

import argparse
import json
import os
import sys
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

# 路径配置
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
STATE_DIR = os.path.join(PROJECT_ROOT, "runtime", "state")
DATA_DIR = os.path.join(STATE_DIR, "task_continuation")
TASKS_FILE = os.path.join(DATA_DIR, "tasks.json")
SNAPSHOTS_DIR = os.path.join(DATA_DIR, "snapshots")
HISTORY_FILE = os.path.join(DATA_DIR, "history.json")


def ensure_dir():
    """确保目录存在"""
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(SNAPSHOTS_DIR, exist_ok=True)


def load_json(file_path: str, default: Any = None) -> Any:
    """加载 JSON 文件"""
    ensure_dir()
    if not os.path.exists(file_path):
        return default if default is not None else []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default if default is not None else []


def save_json(file_path: str, data: Any):
    """保存 JSON 文件"""
    ensure_dir()
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_tasks() -> List[Dict[str, Any]]:
    """加载所有任务"""
    return load_json(TASKS_FILE, [])


def save_tasks(tasks: List[Dict[str, Any]]):
    """保存所有任务"""
    save_json(TASKS_FILE, tasks)


def add_to_history(action: str, task_id: str, details: Dict[str, Any]):
    """添加到历史记录"""
    history = load_json(HISTORY_FILE, [])
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "task_id": task_id,
        "details": details
    }
    history.append(entry)
    # 只保留最近100条
    if len(history) > 100:
        history = history[-100:]
    save_json(HISTORY_FILE, history)


# ========== 任务创建 ==========

def start_task(name: str, steps: List[str] = None, description: str = "") -> Dict[str, Any]:
    """开始一个新任务"""
    tasks = load_tasks()

    task_id = str(uuid.uuid4())[:8]
    task = {
        "id": task_id,
        "name": name,
        "description": description,
        "steps": steps or [],
        "current_step": 0,
        "status": "running",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "completed_steps": [],
        "failed_step": None,
        "last_error": None,
        "env_snapshot": None,
        "metadata": {}
    }

    tasks.append(task)
    save_tasks(tasks)
    add_to_history("start", task_id, {"name": name, "steps_count": len(steps) if steps else 0})

    return task


# ========== 任务状态查询 ==========

def get_task(task_id: str) -> Optional[Dict[str, Any]]:
    """获取指定任务"""
    tasks = load_tasks()
    for task in tasks:
        if task["id"] == task_id:
            return task
    return None


def list_tasks(status: str = None) -> List[Dict[str, Any]]:
    """列出任务"""
    tasks = load_tasks()
    if status:
        tasks = [t for t in tasks if t.get("status") == status]
    # 按更新时间倒序
    tasks.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
    return tasks


# ========== 任务操作 ==========

def update_task_status(task_id: str, status: str, error: str = None, failed_step: int = None) -> bool:
    """更新任务状态"""
    tasks = load_tasks()
    for task in tasks:
        if task["id"] == task_id:
            task["status"] = status
            task["updated_at"] = datetime.now(timezone.utc).isoformat()
            if error:
                task["last_error"] = error
            if failed_step is not None:
                task["failed_step"] = failed_step
            save_tasks(tasks)
            add_to_history("status_update", task_id, {"status": status, "error": error})
            return True
    return False


def complete_step(task_id: str, step_index: int, result: str = "") -> bool:
    """标记步骤完成"""
    tasks = load_tasks()
    for task in tasks:
        if task["id"] == task_id:
            task["current_step"] = step_index + 1
            task["completed_steps"].append({
                "step_index": step_index,
                "completed_at": datetime.now(timezone.utc).isoformat(),
                "result": result
            })
            task["updated_at"] = datetime.now(timezone.utc).isoformat()

            # 检查是否所有步骤都完成
            if task["current_step"] >= len(task.get("steps", [])):
                task["status"] = "completed"
                add_to_history("task_completed", task_id, {"step": step_index})
            else:
                add_to_history("step_completed", task_id, {"step": step_index})

            save_tasks(tasks)
            return True
    return False


def resume_task(task_id: str) -> Optional[Dict[str, Any]]:
    """恢复任务"""
    task = get_task(task_id)
    if not task:
        return None

    if task["status"] in ["completed", "failed"]:
        return None

    # 更新状态为 running
    task["status"] = "running"
    task["updated_at"] = datetime.now(timezone.utc).isoformat()

    tasks = load_tasks()
    for i, t in enumerate(tasks):
        if t["id"] == task_id:
            tasks[i] = task
            break

    save_tasks(tasks)
    add_to_history("resume", task_id, {"current_step": task["current_step"]})
    return task


def fail_task(task_id: str, reason: str, failed_step: int = None) -> bool:
    """标记任务失败"""
    tasks = load_tasks()
    for task in tasks:
        if task["id"] == task_id:
            task["status"] = "failed"
            task["last_error"] = reason
            task["failed_step"] = failed_step if failed_step is not None else task.get("current_step")
            task["updated_at"] = datetime.now(timezone.utc).isoformat()
            save_tasks(tasks)
            add_to_history("task_failed", task_id, {"reason": reason, "step": failed_step})
            return True
    return False


def delete_task(task_id: str) -> bool:
    """删除任务"""
    tasks = load_tasks()
    original_len = len(tasks)
    tasks = [t for t in tasks if t["id"] != task_id]

    if len(tasks) < original_len:
        save_tasks(tasks)
        add_to_history("delete", task_id, {})
        return True
    return False


# ========== 环境快照 ==========

def save_snapshot(task_id: str, data: Dict[str, Any]) -> str:
    """保存环境快照"""
    snapshot_id = str(uuid.uuid4())[:12]
    snapshot = {
        "id": snapshot_id,
        "task_id": task_id,
        "data": data,
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    snapshot_file = os.path.join(SNAPSHOTS_DIR, f"{task_id}_{snapshot_id}.json")
    with open(snapshot_file, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, ensure_ascii=False, indent=2)

    # 更新任务的最新快照引用
    tasks = load_tasks()
    for task in tasks:
        if task["id"] == task_id:
            task["env_snapshot"] = snapshot_id
            task["updated_at"] = datetime.now(timezone.utc).isoformat()
            save_tasks(tasks)
            break

    add_to_history("snapshot_saved", task_id, {"snapshot_id": snapshot_id})
    return snapshot_id


def load_snapshot(task_id: str, snapshot_id: str = None) -> Optional[Dict[str, Any]]:
    """加载环境快照"""
    if not snapshot_id:
        # 加载最新的快照
        task = get_task(task_id)
        if not task or not task.get("env_snapshot"):
            return None
        snapshot_id = task["env_snapshot"]

    snapshot_file = os.path.join(SNAPSHOTS_DIR, f"{task_id}_{snapshot_id}.json")
    if os.path.exists(snapshot_file):
        with open(snapshot_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def save_current_env(task_id: str) -> bool:
    """保存当前环境快照（自动捕获系统状态）"""
    import subprocess

    env_data = {
        "window_title": "",
        "active_process": "",
        "clipboard": "",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    # 尝试获取活动窗口标题
    try:
        result = subprocess.run(
            ["powershell", "-Command",
             "(Get-Process | Where-Object {$_.MainWindowTitle -ne ''} | Select-Object -First 1).MainWindowTitle"],
            capture_output=True, text=True, timeout=5
        )
        if result.stdout.strip():
            env_data["window_title"] = result.stdout.strip()
    except:
        pass

    # 尝试获取活动进程
    try:
        result = subprocess.run(
            ["powershell", "-Command",
             "(Get-Process | Where-Object {$_.MainWindowTitle -ne ''} | Select-Object -First 1).ProcessName"],
            capture_output=True, text=True, timeout=5
        )
        if result.stdout.strip():
            env_data["active_process"] = result.stdout.strip()
    except:
        pass

    save_snapshot(task_id, env_data)
    add_to_history("env_saved", task_id, env_data)
    return True


# ========== 历史记录 ==========

def get_history(limit: int = 20) -> List[Dict[str, Any]]:
    """获取历史记录"""
    history = load_json(HISTORY_FILE, [])
    return history[-limit:]


# ========== 命令行接口 ==========

def cmd_start(args):
    """开始任务"""
    steps = args.steps.split("|") if args.steps else []
    task = start_task(args.name, steps, args.description or "")
    print(f"任务已创建: {task['id']}")
    print(f"名称: {task['name']}")
    print(f"步骤数: {len(task['steps'])}")
    if steps:
        print("步骤列表:")
        for i, step in enumerate(steps):
            print(f"  {i}. {step}")
    return 0


def cmd_status(args):
    """查看任务状态"""
    if args.task_id:
        task = get_task(args.task_id)
        if not task:
            print(f"未找到任务: {args.task_id}")
            return 1
        print(f"\n=== 任务状态 ===")
        print(f"ID: {task['id']}")
        print(f"名称: {task['name']}")
        print(f"描述: {task.get('description', '-')}")
        print(f"状态: {task['status']}")
        print(f"当前步骤: {task['current_step']}/{len(task.get('steps', []))}")
        print(f"创建时间: {task['created_at']}")
        print(f"更新时间: {task['updated_at']}")
        if task.get('steps'):
            print("\n步骤详情:")
            for i, step in enumerate(task['steps']):
                status_icon = "✓" if i < task['current_step'] else "→" if i == task['current_step'] else " "
                print(f"  {status_icon} {i}. {step}")
        if task.get('last_error'):
            print(f"\n错误: {task['last_error']}")
        if task.get('env_snapshot'):
            print(f"\n环境快照: {task['env_snapshot']}")
        return 0
    else:
        # 列出所有任务
        tasks = list_tasks(args.status)
        if not tasks:
            print("没有任务")
            return 0

        print(f"\n=== 任务列表 ({len(tasks)}个) ===")
        for task in tasks:
            status_icon = {
                "running": "→",
                "completed": "✓",
                "failed": "✗",
                "pending": "○"
            }.get(task['status'], " ")

            print(f"\n{status_icon} [{task['status']}] {task['name']} (ID: {task['id']})")
            print(f"   进度: {task['current_step']}/{len(task.get('steps', []))}")
            print(f"   更新: {task['updated_at']}")
        return 0


def cmd_resume(args):
    """恢复任务"""
    task = resume_task(args.task_id)
    if not task:
        print(f"无法恢复任务: {task_id} (可能已完成或不存在)")
        return 1

    print(f"任务已恢复: {task['id']}")
    print(f"名称: {task['name']}")
    print(f"当前步骤: {task['current_step']}/{len(task.get('steps', []))}")
    if task.get('steps') and task['current_step'] < len(task['steps']):
        print(f"下一步: {task['steps'][task['current_step']]}")
    return 0


def cmd_complete(args):
    """标记步骤完成"""
    if complete_step(args.task_id, args.step, args.result or ""):
        task = get_task(args.task_id)
        if task:
            print(f"步骤 {args.step} 已完成")
            print(f"当前进度: {task['current_step']}/{len(task.get('steps', []))}")
            if task['status'] == 'completed':
                print("任务已完成!")
        return 0
    print(f"未找到任务: {args.task_id}")
    return 1


def cmd_fail(args):
    """标记任务失败"""
    if fail_task(args.task_id, args.reason, args.step):
        print(f"任务已标记为失败: {args.task_id}")
        print(f"原因: {args.reason}")
        return 0
    print(f"未找到任务: {args.task_id}")
    return 1


def cmd_list(args):
    """列出任务"""
    status = getattr(args, 'status', None)
    tasks = list_tasks(status)
    if not tasks:
        print("没有任务")
        return 0

    print(f"\n=== 任务列表 ({len(tasks)}个) ===")
    for task in tasks:
        status_icon = {
            "running": "→",
            "completed": "✓",
            "failed": "✗",
            "pending": "○"
        }.get(task['status'], " ")

        print(f"\n{status_icon} [{task['status']}] {task['name']} (ID: {task['id']})")
        print(f"   进度: {task['current_step']}/{len(task.get('steps', []))}")
        print(f"   更新: {task['updated_at']}")
    return 0


def cmd_history(args):
    """查看历史"""
    entries = get_history(args.limit)
    if not entries:
        print("没有历史记录")
        return 0

    print(f"\n=== 最近历史 ({len(entries)}条) ===")
    for entry in entries:
        print(f"\n{entry['timestamp'][:19]} [{entry['action']}] 任务: {entry['task_id']}")
        details = entry.get('details', {})
        for k, v in details.items():
            print(f"  {k}: {v}")
    return 0


def cmd_snapshot(args):
    """保存快照"""
    if args.data:
        data = json.loads(args.data)
    else:
        data = {}
    snapshot_id = save_snapshot(args.task_id, data)
    print(f"快照已保存: {snapshot_id}")
    return 0


def cmd_delete(args):
    """删除任务"""
    if delete_task(args.task_id):
        print(f"任务已删除: {args.task_id}")
        return 0
    print(f"未找到任务: {args.task_id}")
    return 1


def cmd_env(args):
    """环境快照操作"""
    if args.save:
        save_current_env(args.save)
        print(f"环境快照已保存到任务: {args.save}")
        return 0
    elif args.restore:
        snapshot = load_snapshot(args.restore)
        if snapshot:
            print(f"\n=== 环境快照 ===")
            print(f"快照ID: {snapshot['id']}")
            print(f"保存时间: {snapshot['created_at']}")
            print(f"数据: {json.dumps(snapshot['data'], ensure_ascii=False, indent=2)}")
            return 0
        print(f"未找到快照")
        return 1
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="智能跨会话任务接续引擎 - 追踪长时间运行的任务状态，实现跨会话的任务接续能力",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # start 命令
    start_parser = subparsers.add_parser("start", help="开始新任务")
    start_parser.add_argument("name", help="任务名称")
    start_parser.add_argument("--steps", help="步骤列表，用|分隔，如 '步骤1|步骤2|步骤3'")
    start_parser.add_argument("--description", "-d", help="任务描述")

    # status 命令
    status_parser = subparsers.add_parser("status", help="查看任务状态")
    status_parser.add_argument("--task-id", help="任务ID")
    status_parser.add_argument("--status", choices=["pending", "running", "completed", "failed"], help="筛选状态")

    # resume 命令
    resume_parser = subparsers.add_parser("resume", help="恢复任务")
    resume_parser.add_argument("task_id", help="任务ID")

    # complete 命令
    complete_parser = subparsers.add_parser("complete", help="标记步骤完成")
    complete_parser.add_argument("task_id", help="任务ID")
    complete_parser.add_argument("--step", "-s", type=int, help="步骤索引")
    complete_parser.add_argument("--result", "-r", help="步骤结果")

    # fail 命令
    fail_parser = subparsers.add_parser("fail", help="标记任务失败")
    fail_parser.add_argument("task_id", help="任务ID")
    fail_parser.add_argument("--reason", "-r", required=True, help="失败原因")
    fail_parser.add_argument("--step", "-s", type=int, help="失败步骤索引")

    # list 命令
    list_parser = subparsers.add_parser("list", help="列出任务")
    list_parser.add_argument("--status", choices=["pending", "running", "completed", "failed"], help="筛选状态")

    # history 命令
    history_parser = subparsers.add_parser("history", help="查看历史")
    history_parser.add_argument("--limit", "-n", type=int, default=20, help="显示条数")

    # snapshot 命令
    snapshot_parser = subparsers.add_parser("snapshot", help="保存快照")
    snapshot_parser.add_argument("task_id", help="任务ID")
    snapshot_parser.add_argument("--data", "-d", help="快照数据(JSON)")

    # delete 命令
    delete_parser = subparsers.add_parser("delete", help="删除任务")
    delete_parser.add_argument("task_id", help="任务ID")

    # env 命令
    env_parser = subparsers.add_parser("env", help="环境快照操作")
    env_parser.add_argument("--save", help="保存当前环境到任务")
    env_parser.add_argument("--restore", help="恢复环境快照")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    # 根据命令执行
    commands = {
        "start": cmd_start,
        "status": cmd_status,
        "resume": cmd_resume,
        "complete": cmd_complete,
        "fail": cmd_fail,
        "list": cmd_list,
        "history": cmd_history,
        "snapshot": cmd_snapshot,
        "delete": cmd_delete,
        "env": cmd_env,
    }

    return commands.get(args.command, lambda _: parser.print_help() or 1)(args)


if __name__ == "__main__":
    sys.exit(main())