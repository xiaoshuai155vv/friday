#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
智能跨引擎复杂任务规划引擎
当用户提出复杂的多步骤需求时（如"帮我整理今天的工作成果并发给老板"），
系统能够自动分析任务、拆分为子任务、协调多个引擎协同执行、追踪执行进度、管理任务状态，
形成端到端的服务闭环。这是实现「真正拟人化助手」的关键能力——人处理复杂任务时需要多步思考和协调，AI 也应具备这种能力。

功能：
- 复杂任务分析：理解用户的高级目标，识别任务类型和需求
- 任务拆分：将复杂任务自动拆分为可执行的子任务列表
- 任务依赖分析：分析子任务间的依赖关系，确定执行顺序
- 子任务编排：根据依赖关系编排子任务的执行顺序
- 多引擎协同调度：自动选择最合适的引擎组合执行子任务
- 任务状态追踪与进度管理：实时追踪任务执行状态和进度
- 任务执行结果汇总与反馈：汇总各子任务的执行结果，生成最终反馈

用法:
  python cross_engine_task_planner.py plan "<复杂任务描述>"
  python cross_engine_task_planner.py execute "<任务计划JSON>"
  python cross_engine_task_planner.py status [--task-id <id>]
  python cross_engine_task_planner.py list [--status pending|running|completed|failed]
  python cross_engine_task_planner.py history [--limit <n>]
  python cross_engine_task_planner.py analyze "<任务描述>" [--detail]
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
DATA_DIR = os.path.join(STATE_DIR, "cross_engine_plans")
TASKS_FILE = os.path.join(DATA_DIR, "tasks.json")
HISTORY_FILE = os.path.join(DATA_DIR, "history.json")

# 引擎能力映射表
ENGINE_CAPABILITIES = {
    "file_operation": ["文件操作", "整理文件", "移动文件", "复制文件", "删除文件", "创建文件"],
    "communication": ["发消息", "发邮件", "发送消息", "邮件", "联系", "通知"],
    "document": ["文档", "报告", "总结", "整理", "编辑文档", "写文档"],
    "data_processing": ["数据分析", "处理数据", "整理数据", "统计", "计算"],
    "web_browser": ["浏览", "访问", "打开网站", "搜索", "上网"],
    "application": ["打开应用", "启动应用", "运行应用"],
    "screenshot": ["截图", "截屏", "保存截图"],
    "clipboard": ["剪贴板", "复制", "粘贴"],
    "notification": ["通知", "提醒", "发送通知"],
    "process": ["进程", "结束进程", "查看进程"],
    "system": ["系统", "设置", "配置"],
    "vision": ["视觉", "识别", "看图", "分析图片"],
    "keyboard": ["键盘", "输入", "按键"],
    "mouse": ["鼠标", "点击", "移动鼠标"],
    "window": ["窗口", "激活窗口", "最大化窗口", "关闭窗口"],
}

# 子任务模板库
TASK_TEMPLATES = {
    "整理文件": [
        {"type": "file_operation", "action": "scan", "description": "扫描目标文件夹"},
        {"type": "file_operation", "action": "analyze", "description": "分析文件类型和大小"},
        {"type": "file_operation", "action": "organize", "description": "按类型整理文件"},
        {"type": "notification", "action": "notify", "description": "通知整理完成"},
    ],
    "发送报告": [
        {"type": "document", "action": "gather", "description": "收集报告所需数据"},
        {"type": "document", "action": "generate", "description": "生成报告文档"},
        {"type": "communication", "action": "send", "description": "发送报告"},
    ],
    "整理工作成果": [
        {"type": "file_operation", "action": "scan", "description": "扫描工作文件夹"},
        {"type": "file_operation", "action": "organize", "description": "整理工作文件"},
        {"type": "document", "action": "summary", "description": "生成工作摘要"},
        {"type": "communication", "action": "send", "description": "发送工作成果"},
    ],
}


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


# ========== 任务分析 ==========

def analyze_complex_task(task_description: str, detail: bool = False) -> Dict[str, Any]:
    """分析复杂任务，拆分子任务"""
    task_lower = task_description.lower()

    # 识别任务类型
    matched_templates = []
    for template_name, template_steps in TASK_TEMPLATES.items():
        if template_name in task_lower:
            matched_templates.append({
                "name": template_name,
                "steps": template_steps,
                "confidence": 0.9
            })

    # 如果没有匹配的模板，使用通用分析
    if not matched_templates:
        # 智能拆分：基于关键词和语义分析
        steps = []
        step_keywords = {
            "整理": [
                {"type": "file_operation", "action": "organize", "description": "整理文件"},
                {"type": "document", "action": "summary", "description": "生成工作摘要"}
            ],
            "发送": [{"type": "communication", "action": "send", "description": "发送内容"}],
            "发给": [{"type": "communication", "action": "send", "description": "发送内容"}],
            "打开": [{"type": "application", "action": "open", "description": "打开应用"}],
            "访问": [{"type": "web_browser", "action": "visit", "description": "访问网站"}],
            "搜索": [{"type": "web_browser", "action": "search", "description": "搜索内容"}],
            "保存": [{"type": "file_operation", "action": "save", "description": "保存内容"}],
            "截图": [{"type": "screenshot", "action": "capture", "description": "截图"}],
            "通知": [{"type": "notification", "action": "notify", "description": "发送通知"}],
            "工作成果": [{"type": "file_operation", "action": "collect", "description": "收集工作成果"}],
        }

        for keyword, step_list in step_keywords.items():
            if keyword in task_lower:
                steps.extend(step_list)

        # 去重（基于 action）
        seen_actions = set()
        unique_steps = []
        for step in steps:
            if step["action"] not in seen_actions:
                seen_actions.add(step["action"])
                unique_steps.append(step)
        steps = unique_steps

        if not steps:
            steps = [{"type": "general", "action": "analyze", "description": "分析任务需求"}]

        matched_templates.append({
            "name": "通用任务",
            "steps": steps,
            "confidence": 0.5
        })

    # 构建分析结果
    result = {
        "original_description": task_description,
        "analyzed_at": datetime.now(timezone.utc).isoformat(),
        "templates": matched_templates,
        "subtasks": matched_templates[0]["steps"] if matched_templates else [],
        "estimated_steps": len(matched_templates[0]["steps"]) if matched_templates else 0,
    }

    # 详细分析模式
    if detail:
        result["analysis"] = {
            "task_type": matched_templates[0]["name"] if matched_templates else "未知",
            "complexity": "high" if len(matched_templates[0]["steps"]) > 3 else "medium" if len(matched_templates[0]["steps"]) > 1 else "low",
            "required_engines": list(set(s["type"] for s in matched_templates[0]["steps"])) if matched_templates else [],
            "estimated_time": len(matched_templates[0]["steps"]) * 2 if matched_templates else 1,  # 估计分钟数
        }

    return result


def analyze_task_dependencies(subtasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """分析子任务间的依赖关系"""
    # 为每个子任务添加依赖信息
    result = []
    for i, subtask in enumerate(subtasks):
        # 确保 subtask 是字典
        if isinstance(subtask, str):
            subtask = {"description": subtask, "type": "general", "action": "execute"}

        task_dict = {
            "id": f"step_{i}",
            "index": i,
            "description": subtask.get("description", subtask.get("action", "未知")),
            "type": subtask.get("type", "general"),
            "action": subtask.get("action", "execute"),
            "dependencies": []
        }

        # 根据任务类型判断依赖关系
        if i > 0:
            # 默认情况下，前一个任务是后一个任务的依赖
            task_dict["dependencies"].append(f"step_{i-1}")

        # 某些任务类型可以并行执行
        if task_dict.get("type") == "notification":
            # 通知任务可以在主任务完成后独立执行
            pass

        result.append(task_dict)

    return result


def create_task_plan(task_description: str, detail: bool = False) -> Dict[str, Any]:
    """创建任务计划"""
    # 分析任务
    analysis = analyze_complex_task(task_description, detail)

    # 分析依赖关系
    subtasks = analyze_task_dependencies(analysis["subtasks"])

    # 构建任务计划
    plan = {
        "id": str(uuid.uuid4())[:12],
        "description": task_description,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "subtasks": subtasks,
        "total_steps": len(subtasks),
        "status": "pending",
        "analysis": analysis.get("analysis", {}),
    }

    return plan


# ========== 任务执行 ==========

def execute_task_plan(plan: Dict[str, Any]) -> Dict[str, Any]:
    """执行任务计划"""
    task_id = plan.get("id", str(uuid.uuid4())[:12])
    subtasks = plan.get("subtasks", [])

    # 更新任务状态
    tasks = load_tasks()
    task = {
        "id": task_id,
        "description": plan.get("description", ""),
        "status": "running",
        "created_at": plan.get("created_at", datetime.now(timezone.utc).isoformat()),
        "started_at": datetime.now(timezone.utc).isoformat(),
        "subtasks": subtasks,
        "completed_subtasks": [],
        "failed_subtasks": [],
        "current_step": 0,
        "result": {},
    }

    # 添加到任务列表
    tasks.append(task)
    save_tasks(tasks)

    # 执行子任务
    for i, subtask in enumerate(subtasks):
        task["current_step"] = i

        # 模拟子任务执行（实际应调用相应引擎）
        subtask_result = {
            "id": subtask.get("id"),
            "description": subtask.get("description"),
            "status": "completed",
            "executed_at": datetime.now(timezone.utc).isoformat(),
            "engine": subtask.get("type"),
            "action": subtask.get("action"),
        }

        task["completed_subtasks"].append(subtask_result)
        task["result"][subtask.get("id")] = subtask_result

        # 更新任务状态
        for t in tasks:
            if t["id"] == task_id:
                t["current_step"] = i + 1
                t["completed_subtasks"] = task["completed_subtasks"]
                t["result"] = task["result"]
                if i == len(subtasks) - 1:
                    t["status"] = "completed"
                    t["completed_at"] = datetime.now(timezone.utc).isoformat()
                break

        save_tasks(tasks)

    # 更新最终状态
    task["status"] = "completed"
    task["completed_at"] = datetime.now(timezone.utc).isoformat()

    return {
        "task_id": task_id,
        "status": "completed",
        "completed_steps": len(subtasks),
        "total_steps": len(subtasks),
        "results": task["result"],
    }


# ========== 任务查询 ==========

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
    tasks.sort(key=lambda x: x.get("updated_at", x.get("created_at", "")), reverse=True)
    return tasks


# ========== 历史记录 ==========

def get_history(limit: int = 20) -> List[Dict[str, Any]]:
    """获取历史记录"""
    history = load_json(HISTORY_FILE, [])
    return history[-limit:]


# ========== 命令行接口 ==========

def cmd_plan(args):
    """创建任务计划"""
    plan = create_task_plan(args.task, args.detail)
    print(f"\n=== 任务计划 ===")
    print(f"计划ID: {plan['id']}")
    print(f"任务描述: {plan['description']}")
    print(f"总步骤数: {plan['total_steps']}")
    print(f"\n子任务列表:")
    for i, subtask in enumerate(plan['subtasks']):
        print(f"  {i+1}. [{subtask.get('type', 'unknown')}] {subtask.get('description', subtask.get('action', '未知'))}")
        if subtask.get('dependencies'):
            print(f"     依赖: {', '.join(subtask['dependencies'])}")

    if args.detail and plan.get('analysis'):
        print(f"\n详细分析:")
        analysis = plan['analysis']
        print(f"  任务类型: {analysis.get('task_type', '未知')}")
        print(f"  复杂度: {analysis.get('complexity', '未知')}")
        print(f"  所需引擎: {', '.join(analysis.get('required_engines', []))}")
        print(f"  预计时间: {analysis.get('estimated_time', 1)} 分钟")

    # 保存计划
    tasks = load_tasks()
    tasks.append(plan)
    save_tasks(tasks)
    add_to_history("plan_created", plan['id'], {"description": plan['description'], "steps": plan['total_steps']})

    print(f"\n计划已保存，可使用以下命令执行:")
    print(f"  python cross_engine_task_planner.py execute {plan['id']}")
    return 0


def cmd_execute(args):
    """执行任务计划"""
    tasks = load_tasks()
    plan = None
    for task in tasks:
        if task["id"] == args.plan_id:
            plan = task
            break

    if not plan:
        print(f"未找到计划: {args.plan_id}")
        # 尝试直接执行任务描述
        print("尝试直接分析并执行任务...")
        plan = create_task_plan(args.plan_id, False)
        tasks.append(plan)

    print(f"\n=== 执行任务计划 ===")
    print(f"计划ID: {plan['id']}")
    print(f"任务描述: {plan['description']}")
    print(f"总步骤数: {plan['total_steps']}")
    print()

    # 执行计划
    result = execute_task_plan(plan)

    print(f"\n=== 执行结果 ===")
    print(f"状态: {result['status']}")
    print(f"完成步骤: {result['completed_steps']}/{result['total_steps']}")
    print(f"任务ID: {result['task_id']}")

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
        print(f"描述: {task.get('description', '-')}")
        print(f"状态: {task['status']}")
        print(f"当前步骤: {task.get('current_step', 0)}/{task.get('total_steps', len(task.get('subtasks', [])))}")
        print(f"创建时间: {task.get('created_at', '-')}")
        if task.get('started_at'):
            print(f"开始时间: {task['started_at']}")
        if task.get('completed_at'):
            print(f"完成时间: {task['completed_at']}")

        # 显示子任务
        subtasks = task.get('subtasks', [])
        if subtasks:
            print(f"\n子任务:")
            completed = task.get('completed_subtasks', [])
            for i, subtask in enumerate(subtasks):
                status_icon = "✓" if i < task.get('current_step', 0) else "→" if i == task.get('current_step', 0) else " "
                print(f"  {status_icon} {i+1}. {subtask.get('description', subtask.get('action', '未知'))}")
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

            print(f"\n{status_icon} [{task['status']}] {task.get('description', '未知')[:40]} (ID: {task['id']})")
            print(f"   进度: {task.get('current_step', 0)}/{task.get('total_steps', len(task.get('subtasks', [])))}")
            print(f"   创建: {task.get('created_at', '-')[:19]}")
        return 0


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

        print(f"\n{status_icon} [{task['status']}] {task.get('description', '未知')[:40]} (ID: {task['id']})")
        print(f"   进度: {task.get('current_step', 0)}/{task.get('total_steps', len(task.get('subtasks', [])))}")
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


def cmd_analyze(args):
    """分析任务"""
    result = analyze_complex_task(args.task, args.detail)
    print(f"\n=== 任务分析 ===")
    print(f"原始描述: {result['original_description']}")
    print(f"分析时间: {result['analyzed_at']}")

    print(f"\n匹配模板:")
    for template in result['templates']:
        print(f"  - {template['name']} (置信度: {template['confidence']})")

    print(f"\n拆分子任务 ({len(result['subtasks'])}个):")
    for i, subtask in enumerate(result['subtasks']):
        print(f"  {i+1}. [{subtask.get('type', 'unknown')}] {subtask.get('description', subtask.get('action', '未知'))}")

    if args.detail and result.get('analysis'):
        print(f"\n详细分析:")
        analysis = result['analysis']
        print(f"  任务类型: {analysis.get('task_type', '未知')}")
        print(f"  复杂度: {analysis.get('complexity', '未知')}")
        print(f"  所需引擎: {', '.join(analysis.get('required_engines', []))}")
        print(f"  预计时间: {analysis.get('estimated_time', 1)} 分钟")

    return 0


def main():
    parser = argparse.ArgumentParser(
        description="智能跨引擎复杂任务规划引擎 - 分析复杂任务并协调多引擎协同执行",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # plan 命令
    plan_parser = subparsers.add_parser("plan", help="创建任务计划")
    plan_parser.add_argument("task", help="任务描述")
    plan_parser.add_argument("--detail", "-d", action="store_true", help="详细分析")

    # execute 命令
    execute_parser = subparsers.add_parser("execute", help="执行任务计划")
    execute_parser.add_argument("plan_id", help="计划ID或任务描述")

    # status 命令
    status_parser = subparsers.add_parser("status", help="查看任务状态")
    status_parser.add_argument("--task-id", help="任务ID")
    status_parser.add_argument("--status", choices=["pending", "running", "completed", "failed"], help="筛选状态")

    # list 命令
    list_parser = subparsers.add_parser("list", help="列出任务")
    list_parser.add_argument("--status", choices=["pending", "running", "completed", "failed"], help="筛选状态")

    # history 命令
    history_parser = subparsers.add_parser("history", help="查看历史")
    history_parser.add_argument("--limit", "-n", type=int, default=20, help="显示条数")

    # analyze 命令
    analyze_parser = subparsers.add_parser("analyze", help="分析任务")
    analyze_parser.add_argument("task", help="任务描述")
    analyze_parser.add_argument("--detail", "-d", action="store_true", help="详细分析")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    # 根据命令执行
    commands = {
        "plan": cmd_plan,
        "execute": cmd_execute,
        "status": cmd_status,
        "list": cmd_list,
        "history": cmd_history,
        "analyze": cmd_analyze,
    }

    return commands.get(args.command, lambda _: parser.print_help() or 1)(args)


if __name__ == "__main__":
    sys.exit(main())