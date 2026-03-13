#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
智能会议助手引擎
让系统能够管理会议、记录会议纪要、生成待办事项、主动提醒会议时间，
实现会议全流程智能化管理。

功能：
- 会议管理：创建、列出、查看、删除会议
- 会议纪要：记录和生成会议纪要
- 待办提取：从会议内容中提取待办事项
- 会议提醒：定时检查即将到来的会议并提醒

用法:
  python meeting_assistant_engine.py create --title "会议标题" --time "YYYY-MM-DD HH:MM" --duration 60 --participants "张三,李四"
  python meeting_assistant_engine.py list
  python meeting_assistant_engine.py show <meeting_id>
  python meeting_assistant_engine.py minutes --id <meeting_id> --content "会议讨论内容"
  python meeting_assistant_engine.py extract-todos --content "会议内容..."
  python meeting_assistant_engine.py remind
  python meeting_assistant_engine.py status
"""

import argparse
import json
import os
import uuid
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional

# 路径配置
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
STATE_DIR = os.path.join(PROJECT_ROOT, "runtime", "state")
DATA_DIR = os.path.join(STATE_DIR, "meeting_assistant")
MEETINGS_FILE = os.path.join(DATA_DIR, "meetings.json")
MINUTES_FILE = os.path.join(DATA_DIR, "minutes.json")
TODOS_FILE = os.path.join(DATA_DIR, "meeting_todos.json")


def ensure_dir():
    """确保目录存在"""
    os.makedirs(DATA_DIR, exist_ok=True)


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


# ========== 会议管理功能 ==========

def create_meeting(title: str, meeting_time: str = None, duration: int = 60,
                   participants: str = None, description: str = None) -> Dict[str, Any]:
    """创建新会议"""
    meetings = load_json(MEETINGS_FILE, [])

    meeting_id = str(uuid.uuid4())[:8]

    # 解析会议时间
    scheduled_dt = None
    if meeting_time:
        try:
            scheduled_dt = datetime.strptime(meeting_time, "%Y-%m-%d %H:%M")
            scheduled_dt = scheduled_dt.replace(tzinfo=timezone.utc)
        except ValueError:
            try:
                scheduled_dt = datetime.fromisoformat(meeting_time.replace("Z", "+00:00"))
            except:
                scheduled_dt = datetime.now(timezone.utc) + timedelta(hours=1)

    meeting = {
        "id": meeting_id,
        "title": title,
        "scheduled_time": scheduled_dt.isoformat() if scheduled_dt else None,
        "duration": duration,  # 分钟
        "participants": [p.strip() for p in participants.split(",")] if participants else [],
        "description": description or "",
        "status": "scheduled",  # scheduled, in_progress, completed, cancelled
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }

    meetings.append(meeting)
    save_json(MEETINGS_FILE, meetings)

    return meeting


def list_meetings(status: str = None, days_ahead: int = 7) -> List[Dict[str, Any]]:
    """列出会议"""
    meetings = load_json(MEETINGS_FILE, [])

    now = datetime.now(timezone.utc)

    # 过滤和排序
    result = []
    for m in meetings:
        # 状态过滤
        if status and m.get("status") != status:
            continue

        # 时间过滤（只显示未来7天）
        if m.get("scheduled_time"):
            try:
                scheduled = datetime.fromisoformat(m["scheduled_time"].replace("Z", "+00:00"))
                if scheduled > now + timedelta(days=days_ahead):
                    continue
            except:
                pass

        result.append(m)

    # 按时间排序
    result.sort(key=lambda x: x.get("scheduled_time", ""))
    return result


def get_meeting(meeting_id: str) -> Optional[Dict[str, Any]]:
    """获取会议详情"""
    meetings = load_json(MEETINGS_FILE, [])

    for m in meetings:
        if m["id"] == meeting_id:
            return m

    return None


def update_meeting_status(meeting_id: str, status: str) -> Dict[str, Any]:
    """更新会议状态"""
    meetings = load_json(MEETINGS_FILE, [])

    for m in meetings:
        if m["id"] == meeting_id:
            m["status"] = status
            m["updated_at"] = datetime.now(timezone.utc).isoformat()
            save_json(MEETINGS_FILE, meetings)
            return m

    return {"status": "not_found", "message": f"未找到会议 {meeting_id}"}


def delete_meeting(meeting_id: str) -> Dict[str, Any]:
    """删除会议"""
    meetings = load_json(MEETINGS_FILE, [])

    original_count = len(meetings)
    meetings = [m for m in meetings if m["id"] != meeting_id]

    if len(meetings) < original_count:
        save_json(MEETINGS_FILE, meetings)
        return {"status": "deleted", "meeting_id": meeting_id}

    return {"status": "not_found", "message": f"未找到会议 {meeting_id}"}


# ========== 会议纪要功能 ==========

def save_minutes(meeting_id: str, content: str, summary: str = None,
                 decisions: List[str] = None) -> Dict[str, Any]:
    """保存会议纪要"""
    minutes_list = load_json(MINUTES_FILE, [])

    minutes = {
        "id": str(uuid.uuid4())[:8],
        "meeting_id": meeting_id,
        "content": content,
        "summary": summary or "",
        "decisions": decisions or [],
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    minutes_list.append(minutes)
    save_json(MINUTES_FILE, minutes_list)

    # 更新会议状态为已完成
    update_meeting_status(meeting_id, "completed")

    return minutes


def get_minutes(meeting_id: str) -> Optional[Dict[str, Any]]:
    """获取会议纪要"""
    minutes_list = load_json(MINUTES_FILE, [])

    for m in minutes_list:
        if m["meeting_id"] == meeting_id:
            return m

    return None


def generate_minutes_template(meeting_title: str, participants: List[str]) -> str:
    """生成会议纪要模板"""
    template = f"""# {meeting_title}

## 会议信息
- 时间：
- 地点：
- 主持人：
- 参会人：{', '.join(participants)}

## 议程

## 讨论内容

## 决议

## 待办事项

## 备注
"""
    return template


# ========== 待办提取功能 ==========

def extract_todos_from_content(content: str) -> List[Dict[str, Any]]:
    """从会议内容中提取待办事项"""
    # 基于关键词识别待办
    todo_keywords = ["待办", "todo", "待处理", "需要做", "需要完成", "action item", "跟进", "负责人"]
    lines = content.split("\n")

    todos = []
    for line in lines:
        line_lower = line.lower()
        if any(kw in line_lower for kw in todo_keywords):
            # 尝试提取待办内容
            todo_text = line
            for kw in todo_keywords:
                todo_text = todo_text.replace(kw, "").strip("：:、 -")

            if todo_text and len(todo_text) > 2:
                todos.append({
                    "id": str(uuid.uuid4())[:8],
                    "content": todo_text,
                    "source": "extracted",
                    "created_at": datetime.now(timezone.utc).isoformat()
                })

    # 如果没有识别到，提供智能建议
    if not todos:
        # 分析内容中可能的任务
        task_indicators = ["将", "要", "需要", "应该", "会"]
        for line in lines:
            if any(ind in line for ind in task_indicators) and len(line) > 5:
                todo_text = line.strip()
                if todo_text not in [t["content"] for t in todos]:
                    todos.append({
                        "id": str(uuid.uuid4())[:8],
                        "content": f"建议事项：{todo_text}",
                        "source": "suggested",
                        "created_at": datetime.now(timezone.utc).isoformat()
                    })

    # 保存到待办文件
    if todos:
        todos_store = load_json(TODOS_FILE, [])
        todos_store.extend(todos)
        save_json(TODOS_FILE, todos_store)

    return todos


def add_todo_from_meeting(meeting_id: str, content: str, assignee: str = None,
                            due: str = None, priority: str = "normal") -> Dict[str, Any]:
    """从会议添加待办"""
    todos = load_json(TODOS_FILE, [])

    todo = {
        "id": str(uuid.uuid4())[:8],
        "meeting_id": meeting_id,
        "content": content,
        "assignee": assignee,
        "due": due,
        "priority": priority,
        "completed": False,
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    todos.append(todo)
    save_json(TODOS_FILE, todos)

    return todo


def list_meeting_todos(meeting_id: str = None, include_completed: bool = False) -> List[Dict[str, Any]]:
    """列出会议待办"""
    todos = load_json(TODOS_FILE, [])

    result = []
    for t in todos:
        if meeting_id and t.get("meeting_id") != meeting_id:
            continue
        if not include_completed and t.get("completed", False):
            continue
        result.append(t)

    return result


def complete_todo(todo_id: str) -> Dict[str, Any]:
    """标记待办完成"""
    todos = load_json(TODOS_FILE, [])

    for t in todos:
        if t["id"] == todo_id:
            t["completed"] = True
            t["completed_at"] = datetime.now(timezone.utc).isoformat()
            save_json(TODOS_FILE, todos)
            return t

    return {"status": "not_found", "message": f"未找到待办 {todo_id}"}


# ========== 会议提醒功能 ==========

def check_upcoming_meetings(minutes_before: int = 15) -> List[Dict[str, Any]]:
    """检查即将开始的会议"""
    meetings = load_json(MEETINGS_FILE, [])
    now = datetime.now(timezone.utc)

    upcoming = []
    for m in meetings:
        if m.get("status") != "scheduled":
            continue

        if m.get("scheduled_time"):
            try:
                scheduled = datetime.fromisoformat(m["scheduled_time"].replace("Z", "+00:00"))
                time_diff = (scheduled - now).total_seconds() / 60  # 分钟

                if 0 <= time_diff <= minutes_before:
                    m["minutes_until_start"] = int(time_diff)
                    upcoming.append(m)
            except:
                pass

    return upcoming


def get_reminders() -> Dict[str, Any]:
    """获取提醒信息"""
    # 检查即将开始的会议
    upcoming_meetings = check_upcoming_meetings(15)

    # 检查未完成的会议待办
    todos = load_json(TODOS_FILE, [])
    pending_todos = [t for t in todos if not t.get("completed", False)]
    overdue_todos = []

    now = datetime.now(timezone.utc)
    for t in pending_todos:
        if t.get("due"):
            try:
                due = datetime.fromisoformat(t["due"].replace("Z", "+00:00"))
                if due < now:
                    overdue_todos.append(t)
            except:
                pass

    reminders = []

    if upcoming_meetings:
        reminders.append({
            "type": "upcoming_meetings",
            "title": "即将开始的会议",
            "items": [{"id": m["id"], "title": m["title"], "time": m.get("scheduled_time"),
                       "minutes_until": m.get("minutes_until_start")} for m in upcoming_meetings]
        })

    if overdue_todos:
        reminders.append({
            "type": "overdue_todos",
            "title": "已过期的待办",
            "items": [{"id": t["id"], "content": t["content"], "due": t.get("due")} for t in overdue_todos[:5]]
        })

    return {
        "reminders": reminders,
        "checked_at": now.isoformat()
    }


# ========== 状态概览 ==========

def get_status() -> Dict[str, Any]:
    """获取整体状态"""
    meetings = load_json(MEETINGS_FILE, [])
    minutes = load_json(MINUTES_FILE, [])
    todos = load_json(TODOS_FILE, [])

    now = datetime.now(timezone.utc)

    # 统计会议
    scheduled = [m for m in meetings if m.get("status") == "scheduled"]
    in_progress = [m for m in meetings if m.get("status") == "in_progress"]
    completed = [m for m in meetings if m.get("status") == "completed"]

    # 即将到来的会议
    upcoming = check_upcoming_meetings(60)

    # 待办统计
    pending_todos = [t for t in todos if not t.get("completed", False)]
    completed_todos = [t for t in todos if t.get("completed", False)]

    return {
        "meetings": {
            "total": len(meetings),
            "scheduled": len(scheduled),
            "in_progress": len(in_progress),
            "completed": len(completed),
            "upcoming_next_hour": len(upcoming)
        },
        "minutes": {
            "total": len(minutes)
        },
        "todos": {
            "total": len(todos),
            "pending": len(pending_todos),
            "completed": len(completed_todos)
        },
        "updated_at": now.isoformat()
    }


def main():
    parser = argparse.ArgumentParser(description="智能会议助手引擎")
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # create 命令
    create_parser = subparsers.add_parser("create", help="创建会议")
    create_parser.add_argument("--title", required=True, help="会议标题")
    create_parser.add_argument("--time", help="会议时间 (YYYY-MM-DD HH:MM)")
    create_parser.add_argument("--duration", type=int, default=60, help="会议时长（分钟）")
    create_parser.add_argument("--participants", help="参会人（逗号分隔）")
    create_parser.add_argument("--description", help="会议描述")

    # list 命令
    list_parser = subparsers.add_parser("list", help="列出会议")
    list_parser.add_argument("--status", choices=["scheduled", "in_progress", "completed", "cancelled"],
                             help="按状态筛选")
    list_parser.add_argument("--days", type=int, default=7, help="显示未来几天的会议")

    # show 命令
    subparsers.add_parser("show", help="查看会议详情").add_argument("meeting_id", help="会议ID")

    # update-status 命令
    status_parser = subparsers.add_parser("update-status", help="更新会议状态")
    status_parser.add_argument("meeting_id", help="会议ID")
    status_parser.add_argument("status", choices=["scheduled", "in_progress", "completed", "cancelled"])

    # delete 命令
    subparsers.add_parser("delete", help="删除会议").add_argument("meeting_id", help="会议ID")

    # minutes 命令
    minutes_parser = subparsers.add_parser("minutes", help="会议纪要管理")
    minutes_parser.add_argument("--id", help="会议ID")
    minutes_parser.add_argument("--content", help="会议内容")
    minutes_parser.add_argument("--summary", help="会议总结")
    minutes_parser.add_argument("--decisions", nargs="*", help="决议列表")
    minutes_parser.add_argument("--template", action="store_true", help="生成纪要模板")

    # extract-todos 命令
    extract_parser = subparsers.add_parser("extract-todos", help="从内容提取待办")
    extract_parser.add_argument("--content", required=True, help="会议内容")

    # add-todo 命令
    todo_parser = subparsers.add_parser("add-todo", help="添加会议待办")
    todo_parser.add_argument("--meeting-id", required=True, help="会议ID")
    todo_parser.add_argument("--content", required=True, help="待办内容")
    todo_parser.add_argument("--assignee", help="负责人")
    todo_parser.add_argument("--due", help="截止日期 (YYYY-MM-DD)")
    todo_parser.add_argument("--priority", choices=["high", "normal", "low"], default="normal")

    # list-todos 命令
    todos_parser = subparsers.add_parser("list-todos", help="列出会议待办")
    todos_parser.add_argument("--meeting-id", help="会议ID")
    todos_parser.add_argument("--include-completed", action="store_true", help="包含已完成的")

    # complete-todo 命令
    subparsers.add_parser("complete-todo", help="标记待办完成").add_argument("todo_id", help="待办ID")

    # remind 命令
    subparsers.add_parser("remind", help="获取会议提醒")

    # status 命令
    subparsers.add_parser("status", help="获取整体状态")

    args = parser.parse_args()

    # create 命令处理
    if args.command == "create":
        result = create_meeting(args.title, args.time, args.duration, args.participants, args.description)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    # list 命令处理
    elif args.command == "list":
        result = list_meetings(args.status, args.days)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    # show 命令处理
    elif args.command == "show":
        result = get_meeting(args.meeting_id)
        if result:
            # 获取关联的纪要和待办
            minutes = get_minutes(args.meeting_id)
            todos = list_meeting_todos(args.meeting_id)
            result["minutes"] = minutes
            result["todos"] = todos
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(json.dumps({"status": "not_found"}, ensure_ascii=False))

    # update-status 命令处理
    elif args.command == "update-status":
        result = update_meeting_status(args.meeting_id, args.status)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    # delete 命令处理
    elif args.command == "delete":
        result = delete_meeting(args.meeting_id)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    # minutes 命令处理
    elif args.command == "minutes":
        if args.template:
            result = generate_minutes_template("会议标题", ["参会人1", "参会人2"])
            print(result)
        elif args.id and args.content:
            result = save_minutes(args.id, args.content, args.summary, args.decisions)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            parser.print_help()

    # extract-todos 命令处理
    elif args.command == "extract_todos" or args.command == "extract-todos":
        result = extract_todos_from_content(args.content)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    # add-todo 命令处理
    elif args.command == "add-todo":
        result = add_todo_from_meeting(args.meeting_id, args.content, args.assignee, args.due, args.priority)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    # list-todos 命令处理
    elif args.command == "list-todos":
        result = list_meeting_todos(args.meeting_id, args.include_completed)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    # complete-todo 命令处理
    elif args.command == "complete-todo":
        result = complete_todo(args.todo_id)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    # remind 命令处理
    elif args.command == "remind":
        result = get_reminders()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    # status 命令处理
    elif args.command == "status":
        result = get_status()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()