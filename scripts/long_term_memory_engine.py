#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
智能长期记忆与主动规划引擎
让系统能够记住用户的长期目标、跨会话习惯和偏好，主动分析用户意图并提前准备可能需要的内容，
实现真正的主动式智能助手。

功能：
- 长期记忆存储：跨会话持久化存储用户重要信息和偏好
- 用户目标跟踪：记录用户声明的目标、进度和截止日期
- 主动规划功能：基于用户习惯和时间主动推荐待办/计划
- 跨会话上下文恢复：重新打开对话时恢复之前的上下文

用法:
  python long_term_memory_engine.py goals [--add "目标内容" --deadline "YYYY-MM-DD"]
  python long_term_memory_engine.py goals --list
  python long_term_memory_engine.py goals --progress <goal_id> <进度百分比>
  python long_term_memory_engine.py plan [--add "待办内容" --due "YYYY-MM-DD"]
  python long_term_memory_engine.py plan --list
  python long_term_memory_engine.py plan --complete <plan_id>
  python long_term_memory_engine.py recommend
  python long_term_memory_engine.py context --save <session_id> "<上下文内容>"
  python long_term_memory_engine.py context --restore <session_id>
  python long_term_memory_engine.py habits [--analyze]
  python long_term_memory_engine.py memory --store "<类型>" "<内容>"
  python long_term_memory_engine.py memory --search "<关键词>"
  python long_term_memory_engine.py status
"""

import argparse
import json
import os
import uuid
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional
from collections import defaultdict

# 路径配置
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
STATE_DIR = os.path.join(PROJECT_ROOT, "runtime", "state")
DATA_DIR = os.path.join(STATE_DIR, "long_term_memory")
GOALS_FILE = os.path.join(DATA_DIR, "goals.json")
PLANS_FILE = os.path.join(DATA_DIR, "plans.json")
CONTEXTS_FILE = os.path.join(DATA_DIR, "contexts.json")
HABITS_FILE = os.path.join(DATA_DIR, "habits.json")
MEMORY_FILE = os.path.join(DATA_DIR, "memory.json")


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


# ========== 目标管理功能 ==========

def add_goal(content: str, deadline: str = None) -> Dict[str, Any]:
    """添加新目标"""
    goals = load_json(GOALS_FILE, [])

    goal_id = str(uuid.uuid4())[:8]
    goal = {
        "id": goal_id,
        "content": content,
        "progress": 0,
        "deadline": deadline,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "status": "active"
    }

    goals.append(goal)
    save_json(GOALS_FILE, goals)

    return goal


def list_goals() -> List[Dict[str, Any]]:
    """列出所有目标"""
    goals = load_json(GOALS_FILE, [])
    # 按创建时间倒序
    goals.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return goals


def update_progress(goal_id: str, progress: int) -> Dict[str, Any]:
    """更新目标进度"""
    goals = load_json(GOALS_FILE, [])

    for goal in goals:
        if goal["id"] == goal_id:
            goal["progress"] = min(100, max(0, progress))
            goal["updated_at"] = datetime.now(timezone.utc).isoformat()

            if goal["progress"] >= 100:
                goal["status"] = "completed"

            save_json(GOALS_FILE, goals)
            return goal

    return {"status": "not_found", "message": f"未找到目标 {goal_id}"}


def get_goals_by_status(status: str = "active") -> List[Dict[str, Any]]:
    """按状态获取目标"""
    goals = load_json(GOALS_FILE, [])
    return [g for g in goals if g.get("status") == status]


# ========== 计划/待办管理功能 ==========

def add_plan(content: str, due: str = None, priority: str = "normal") -> Dict[str, Any]:
    """添加新计划/待办"""
    plans = load_json(PLANS_FILE, [])

    plan_id = str(uuid.uuid4())[:8]
    plan = {
        "id": plan_id,
        "content": content,
        "due": due,
        "priority": priority,
        "completed": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "completed_at": None
    }

    plans.append(plan)
    save_json(PLANS_FILE, plans)

    return plan


def list_plans(include_completed: bool = False) -> List[Dict[str, Any]]:
    """列出所有计划"""
    plans = load_json(PLANS_FILE, [])

    if not include_completed:
        plans = [p for p in plans if not p.get("completed", False)]

    # 按截止日期和优先级排序
    plans.sort(key=lambda x: (x.get("completed", False), -{"high": 2, "normal": 1, "low": 0}.get(x.get("priority", "normal"), 0), x.get("due", "9999-99-99")))
    return plans


def complete_plan(plan_id: str) -> Dict[str, Any]:
    """标记计划完成"""
    plans = load_json(PLANS_FILE, [])

    for plan in plans:
        if plan["id"] == plan_id:
            plan["completed"] = True
            plan["completed_at"] = datetime.now(timezone.utc).isoformat()
            save_json(PLANS_FILE, plans)
            return plan

    return {"status": "not_found", "message": f"未找到计划 {plan_id}"}


def get_upcoming_plans(days: int = 7) -> List[Dict[str, Any]]:
    """获取即将到期的计划"""
    plans = load_json(PLANS_FILE, [])
    result = []

    now = datetime.now(timezone.utc)
    deadline = now + timedelta(days=days)

    for plan in plans:
        if plan.get("completed", False):
            continue

        if plan.get("due"):
            try:
                due_date = datetime.fromisoformat(plan["due"].replace("Z", "+00:00"))
                if now <= due_date <= deadline:
                    result.append(plan)
            except Exception:
                pass
        else:
            result.append(plan)

    return result


# ========== 主动推荐功能 ==========

def get_recommendations() -> Dict[str, Any]:
    """获取主动推荐"""
    recommendations = []

    # 1. 检查即将到期的计划
    upcoming = get_upcoming_plans(3)
    if upcoming:
        recommendations.append({
            "type": "upcoming_deadline",
            "title": "即将到期的待办",
            "items": [{"id": p["id"], "content": p["content"], "due": p.get("due")} for p in upcoming[:3]]
        })

    # 2. 检查超时的目标
    now = datetime.now(timezone.utc)
    goals = load_json(GOALS_FILE, [])

    overdue_goals = []
    for goal in goals:
        if goal.get("status") == "active" and goal.get("deadline"):
            try:
                deadline = datetime.fromisoformat(goal["deadline"].replace("Z", "+00:00"))
                if deadline < now:
                    overdue_goals.append(goal)
            except Exception:
                pass

    if overdue_goals:
        recommendations.append({
            "type": "overdue_goals",
            "title": "已超时的目标",
            "items": [{"id": g["id"], "content": g["content"], "deadline": g.get("deadline")} for g in overdue_goals]
        })

    # 3. 检查长期未完成的计划
    plans = load_json(PLANS_FILE, [])
    stale_plans = []
    for plan in plans:
        if not plan.get("completed", False):
            try:
                created = datetime.fromisoformat(plan["created_at"].replace("Z", "+00:00"))
                days_old = (now - created).days
                if days_old >= 7:
                    stale_plans.append(plan)
            except Exception:
                pass

    if stale_plans:
        recommendations.append({
            "type": "stale_plans",
            "title": "长期未完成的待办",
            "items": [{"id": p["id"], "content": p["content"], "days_old": (now - datetime.fromisoformat(p["created_at"].replace("Z", "+00:00"))).days} for p in stale_plans[:3]]
        })

    # 4. 基于习惯的推荐（分析最近的交互时间）
    habits = load_json(HABITS_FILE, {})

    if "time_patterns" in habits:
        current_hour = now.hour
        time_patterns = habits["time_patterns"]

        # 根据时间段推荐
        hour_patterns = {}
        for pattern in time_patterns:
            hour = pattern.get("hour", 0)
            count = pattern.get("count", 0)
            hour_patterns[hour] = hour_patterns.get(hour, 0) + count

        # 找到用户最活跃的时间段
        if hour_patterns:
            most_active_hour = max(hour_patterns.items(), key=lambda x: x[1])[0]

            if current_hour == most_active_hour:
                recommendations.append({
                    "type": "time_pattern",
                    "title": f"现在是您最活跃的时间段（{most_active_hour}:00）",
                    "items": [{"content": "建议处理重要任务或待办"}]
                })

    return {
        "recommendations": recommendations,
        "generated_at": now.isoformat()
    }


# ========== 跨会话上下文功能 ==========

def save_context(session_id: str, content: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
    """保存会话上下文"""
    contexts = load_json(CONTEXTS_FILE, {})

    contexts[session_id] = {
        "content": content,
        "metadata": metadata or {},
        "saved_at": datetime.now(timezone.utc).isoformat()
    }

    save_json(CONTEXTS_FILE, contexts)

    return {"status": "saved", "session_id": session_id}


def restore_context(session_id: str) -> Optional[Dict[str, Any]]:
    """恢复会话上下文"""
    contexts = load_json(CONTEXTS_FILE, {})

    if session_id in contexts:
        return contexts[session_id]

    return None


def list_recent_sessions(limit: int = 10) -> List[Dict[str, Any]]:
    """列出最近的会话"""
    contexts = load_json(CONTEXTS_FILE, {})

    sessions = []
    for session_id, data in contexts.items():
        sessions.append({
            "session_id": session_id,
            "saved_at": data.get("saved_at"),
            "preview": data.get("content", "")[:100]
        })

    sessions.sort(key=lambda x: x.get("saved_at", ""), reverse=True)
    return sessions[:limit]


# ========== 习惯分析功能 ==========

def record_interaction(interaction_type: str):
    """记录用户交互用于习惯分析"""
    habits = load_json(HABITS_FILE, {"interactions": [], "time_patterns": []})

    now = datetime.now(timezone.utc)

    # 记录交互
    habits["interactions"].append({
        "type": interaction_type,
        "timestamp": now.isoformat()
    })

    # 保持最近1000条
    habits["interactions"] = habits["interactions"][-1000:]

    # 分析时间模式
    hour_counts = defaultdict(int)
    for inter in habits["interactions"]:
        try:
            ts = datetime.fromisoformat(inter["timestamp"].replace("Z", "+00:00"))
            hour_counts[ts.hour] += 1
        except Exception:
            pass

    habits["time_patterns"] = [{"hour": h, "count": c} for h, c in hour_counts.items()]
    habits["time_patterns"].sort(key=lambda x: x["count"], reverse=True)

    save_json(HABITS_FILE, habits)


def analyze_habits() -> Dict[str, Any]:
    """分析用户习惯"""
    habits = load_json(HABITS_FILE, {"interactions": [], "time_patterns": []})

    time_patterns = habits.get("time_patterns", [])

    analysis = {
        "total_interactions": len(habits.get("interactions", [])),
        "time_patterns": time_patterns[:5],  # 前5个最活跃时段
        "most_active_hour": time_patterns[0]["hour"] if time_patterns else None,
        "analysis_time": datetime.now(timezone.utc).isoformat()
    }

    return analysis


# ========== 长期记忆功能 ==========

def store_long_term_memory(memory_type: str, content: str, tags: List[str] = None) -> Dict[str, Any]:
    """存储长期记忆"""
    memory_list = load_json(MEMORY_FILE, [])

    memory = {
        "id": str(uuid.uuid4())[:8],
        "type": memory_type,
        "content": content,
        "tags": tags or [],
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    memory_list.append(memory)
    save_json(MEMORY_FILE, memory_list)

    return memory


def search_long_term_memory(keyword: str, memory_type: str = None) -> List[Dict[str, Any]]:
    """搜索长期记忆"""
    memory_list = load_json(MEMORY_FILE, [])

    results = []
    for mem in memory_list:
        # 类型过滤
        if memory_type and mem.get("type") != memory_type:
            continue

        # 关键词搜索
        if keyword.lower() in mem.get("content", "").lower() or \
           any(keyword.lower() in tag.lower() for tag in mem.get("tags", [])):
            results.append(mem)

    return results


# ========== 状态概览 ==========

def get_status() -> Dict[str, Any]:
    """获取整体状态"""
    goals = load_json(GOALS_FILE, [])
    plans = load_json(PLANS_FILE, [])
    contexts = load_json(CONTEXTS_FILE, {})
    habits = load_json(HABITS_FILE, {})
    memory = load_json(MEMORY_FILE, [])

    active_goals = [g for g in goals if g.get("status") == "active"]
    overdue_goals = []
    now = datetime.now(timezone.utc)
    for g in active_goals:
        if g.get("deadline"):
            try:
                deadline = datetime.fromisoformat(g["deadline"].replace("Z", "+00:00"))
                if deadline < now:
                    overdue_goals.append(g)
            except Exception:
                pass

    active_plans = [p for p in plans if not p.get("completed", False)]
    completed_plans = [p for p in plans if p.get("completed", False)]

    return {
        "goals": {
            "total": len(goals),
            "active": len(active_goals),
            "completed": len([g for g in goals if g.get("status") == "completed"]),
            "overdue": len(overdue_goals)
        },
        "plans": {
            "total": len(plans),
            "active": len(active_plans),
            "completed": len(completed_plans)
        },
        "contexts": {
            "total": len(contexts)
        },
        "habits": {
            "total_interactions": len(habits.get("interactions", []))
        },
        "memory": {
            "total": len(memory)
        },
        "updated_at": now.isoformat()
    }


def main():
    parser = argparse.ArgumentParser(description="智能长期记忆与主动规划引擎")
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # goals 命令
    goals_parser = subparsers.add_parser("goals", help="目标管理")
    goals_parser.add_argument("--add", help="添加新目标")
    goals_parser.add_argument("--deadline", help="目标截止日期 (YYYY-MM-DD)")
    goals_parser.add_argument("--list", action="store_true", help="列出所有目标")
    goals_parser.add_argument("--progress", nargs=2, metavar=("GOAL_ID", "PROGRESS"), help="更新目标进度 (0-100)")
    goals_parser.add_argument("--status", choices=["active", "completed"], help="按状态筛选")

    # plan 命令
    plan_parser = subparsers.add_parser("plan", help="计划/待办管理")
    plan_parser.add_argument("--add", help="添加新计划")
    plan_parser.add_argument("--due", help="计划截止日期 (YYYY-MM-DD)")
    plan_parser.add_argument("--priority", choices=["high", "normal", "low"], default="normal", help="优先级")
    plan_parser.add_argument("--list", action="store_true", help="列出所有计划")
    plan_parser.add_argument("--complete", help="标记计划完成")

    # recommend 命令
    subparsers.add_parser("recommend", help="获取主动推荐")

    # context 命令
    context_parser = subparsers.add_parser("context", help="跨会话上下文管理")
    context_parser.add_argument("--save", nargs=2, metavar=("SESSION_ID", "CONTENT"), help="保存会话上下文")
    context_parser.add_argument("--restore", help="恢复会话上下文")
    context_parser.add_argument("--list", action="store_true", help="列出最近会话")

    # habits 命令
    habits_parser = subparsers.add_parser("habits", help="习惯分析")
    habits_parser.add_argument("--analyze", action="store_true", help="分析用户习惯")
    habits_parser.add_argument("--record", help="记录交互类型")

    # memory 命令
    memory_parser = subparsers.add_parser("memory", help="长期记忆管理")
    memory_parser.add_argument("--store", nargs=2, metavar=("TYPE", "CONTENT"), help="存储长期记忆")
    memory_parser.add_argument("--search", help="搜索长期记忆")
    memory_parser.add_argument("--type", help="搜索时指定类型")

    # status 命令
    subparsers.add_parser("status", help="获取整体状态")

    args = parser.parse_args()

    # goals 命令处理
    if args.command == "goals":
        if args.add:
            result = add_goal(args.add, args.deadline)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        elif args.list:
            if args.status:
                result = get_goals_by_status(args.status)
            else:
                result = list_goals()
            print(json.dumps(result, ensure_ascii=False, indent=2))
        elif args.progress:
            goal_id, progress = args.progress
            result = update_progress(goal_id, int(progress))
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            # 默认列出
            result = list_goals()
            print(json.dumps(result, ensure_ascii=False, indent=2))

    # plan 命令处理
    elif args.command == "plan":
        if args.add:
            result = add_plan(args.add, args.due, args.priority)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        elif args.list:
            result = list_plans()
            print(json.dumps(result, ensure_ascii=False, indent=2))
        elif args.complete:
            result = complete_plan(args.complete)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            result = list_plans()
            print(json.dumps(result, ensure_ascii=False, indent=2))

    # recommend 命令处理
    elif args.command == "recommend":
        result = get_recommendations()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    # context 命令处理
    elif args.command == "context":
        if args.save:
            session_id, content = args.save
            result = save_context(session_id, content)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        elif args.restore:
            result = restore_context(args.restore)
            if result:
                print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                print(json.dumps({"status": "not_found"}, ensure_ascii=False))
        elif args.list:
            result = list_recent_sessions()
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            parser.print_help()

    # habits 命令处理
    elif args.command == "habits":
        if args.analyze:
            result = analyze_habits()
            print(json.dumps(result, ensure_ascii=False, indent=2))
        elif args.record:
            record_interaction(args.record)
            print(json.dumps({"status": "recorded"}, ensure_ascii=False))
        else:
            result = analyze_habits()
            print(json.dumps(result, ensure_ascii=False, indent=2))

    # memory 命令处理
    elif args.command == "memory":
        if args.store:
            memory_type, content = args.store
            result = store_long_term_memory(memory_type, content)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        elif args.search:
            result = search_long_term_memory(args.search, args.type)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            parser.print_help()

    # status 命令处理
    elif args.command == "status":
        result = get_status()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()