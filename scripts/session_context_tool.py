#!/usr/bin/env python3
"""
会话上下文管理工具 - 增强跨会话任务上下文保持能力

功能：
- 保存当前会话的任务摘要到 previous_session_summary
- 加载上一会话的任务上下文
- 管理会话间的任务状态传递
"""

import json
import os
import sys
from datetime import datetime

# 路径配置
STATE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "runtime", "state")
SESSION_CONTEXT_PATH = os.path.join(STATE_DIR, "session_context.json")


def load_session_context():
    """加载会话上下文"""
    if os.path.exists(SESSION_CONTEXT_PATH):
        with open(SESSION_CONTEXT_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "last_intent": None,
        "last_args": [],
        "history": [],
        "last_task": None,
        "last_task_detail": None,
        "task_progress": {},
        "pending_tasks": [],
        "completed_tasks": [],
        "session_id": None,
        "previous_session_summary": None,
        "user_preferences": {}
    }


def save_session_context(context):
    """保存会话上下文"""
    os.makedirs(STATE_DIR, exist_ok=True)
    with open(SESSION_CONTEXT_PATH, "w", encoding="utf-8") as f:
        json.dump(context, f, ensure_ascii=False, indent=2)


def save_session_summary(pending_tasks=None, completed_tasks=None, task_progress=None):
    """
    保存当前会话的任务摘要，供下一会话使用

    Args:
        pending_tasks: 未完成的任务列表
        completed_tasks: 已完成的任务列表
        task_progress: 任务进度字典
    """
    context = load_session_context()

    summary = {
        "timestamp": datetime.now().isoformat(),
        "pending_tasks": pending_tasks or context.get("pending_tasks", []),
        "completed_tasks": completed_tasks or context.get("completed_tasks", []),
        "task_progress": task_progress or context.get("task_progress", {}),
        "last_task": context.get("last_task"),
        "last_task_detail": context.get("last_task_detail"),
        "session_id": context.get("session_id")
    }

    context["previous_session_summary"] = summary
    save_session_context(context)
    print(f"会话摘要已保存: {len(summary.get('completed_tasks', []))} 个已完成任务")
    return summary


def load_previous_summary():
    """加载上一会话的任务摘要"""
    context = load_session_context()
    summary = context.get("previous_session_summary")
    if summary:
        print(f"上一会话摘要加载成功: {len(summary.get('completed_tasks', []))} 个已完成任务")
    else:
        print("无上一会话摘要")
    return summary


def start_new_session():
    """开始新会话，加载上一会话上下文"""
    context = load_session_context()

    # 生成新 session_id
    import uuid
    new_session_id = str(uuid.uuid4())

    # 保存上一会话摘要
    previous_summary = context.get("previous_session_summary")
    if previous_summary:
        print(f"继承上一会话: {len(previous_summary.get('completed_tasks', []))} 个已完成任务")

    # 创建新会话
    new_context = {
        "last_intent": context.get("last_intent"),
        "last_args": context.get("last_args"),
        "history": context.get("history", [])[-10:],  # 保留最近10条历史
        "last_task": None,
        "last_task_detail": None,
        "task_progress": {},
        "pending_tasks": [],
        "completed_tasks": [],
        "session_id": new_session_id,
        "previous_session_summary": previous_summary,
        "user_preferences": context.get("user_preferences", {})
    }

    save_session_context(new_context)
    print(f"新会话开始: {new_session_id}")
    return new_context


def update_task_status(task_id, status, detail=None):
    """更新任务状态"""
    context = load_session_context()

    if status == "pending":
        if task_id not in context["pending_tasks"]:
            context["pending_tasks"].append(task_id)
        if task_id in context["completed_tasks"]:
            context["completed_tasks"].remove(task_id)
    elif status == "completed":
        if task_id in context["pending_tasks"]:
            context["pending_tasks"].remove(task_id)
        if task_id not in context["completed_tasks"]:
            context["completed_tasks"].append(task_id)
        context["task_progress"][task_id] = "done"

    if detail:
        context["task_progress"][task_id] = detail

    context["last_task"] = task_id
    context["last_task_detail"] = detail or status

    save_session_context(context)
    print(f"任务状态更新: {task_id} -> {status}")


def main():
    if len(sys.argv) < 2:
        print("用法:")
        print("  session_context_tool.py save_summary [pending_tasks...]  - 保存会话摘要")
        print("  session_context_tool.py load_summary                     - 加载上一会话摘要")
        print("  session_context_tool.py new_session                     - 开始新会话")
        print("  session_context_tool.py update <task_id> <status> [detail] - 更新任务状态")
        print("  session_context_tool.py show                            - 显示当前上下文")
        sys.exit(1)

    command = sys.argv[1]

    if command == "save_summary":
        pending = sys.argv[2] if len(sys.argv) > 2 else None
        completed = sys.argv[3] if len(sys.argv) > 3 else None
        save_session_summary(pending, completed)
    elif command == "load_summary":
        load_previous_summary()
    elif command == "new_session":
        start_new_session()
    elif command == "update":
        if len(sys.argv) < 4:
            print("用法: session_context_tool.py update <task_id> <status> [detail]")
            sys.exit(1)
        task_id = sys.argv[2]
        status = sys.argv[3]
        detail = sys.argv[4] if len(sys.argv) > 4 else None
        update_task_status(task_id, status, detail)
    elif command == "show":
        context = load_session_context()
        print(json.dumps(context, ensure_ascii=False, indent=2))
    else:
        print(f"未知命令: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()