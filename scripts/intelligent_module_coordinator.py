#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
智能模块协同调度中心

功能：根据任务需求自动编排多个智能模块协同工作，形成更智能的任务处理流水线
支持模块注册、自动分析调用顺序、结果整合、协同历史记录

使用方式：
    python intelligent_module_coordinator.py <command> [options]

Commands:
    register <module_name> <description>    注册智能模块
    unregister <module_name>                注销智能模块
    list                                    列出已注册模块
    analyze <task_description>              分析任务需要的模块
    execute <task_description>              执行任务（自动编排模块）
    history [limit]                         查看协同历史
    help                                    显示帮助信息
"""

import json
import os
import sys
import importlib
import re
from datetime import datetime
from pathlib import Path

# 模块注册表和协同历史存储路径
MODULE_REGISTRY_PATH = "runtime/state/module_coordinator_registry.json"
COORDINATION_HISTORY_PATH = "runtime/state/module_coordination_history.json"

# 已注册的智能模块及其中英文关键词
DEFAULT_MODULES = {
    "intent_recognition": {
        "name": "意图智能识别",
        "description": "理解用户的模糊意图并智能推荐",
        "keywords": ["推荐", "有啥", "好玩", "无聊", "意图", "想做", "模糊"]
    },
    "knowledge_graph": {
        "name": "知识图谱",
        "description": "用户-场景-行为-知识的关联网络",
        "keywords": ["知识", "图谱", "关联", "推理", "关系"]
    },
    "user_behavior_learner": {
        "name": "用户行为学习",
        "description": "学习用户习惯并自动应用",
        "keywords": ["习惯", "偏好", "学习", "行为", "用户"]
    },
    "active_suggestion": {
        "name": "主动建议引擎",
        "description": "根据系统状态、时间主动推送建议",
        "keywords": ["建议", "推送", "主动", "提醒"]
    },
    "scenario_followup": {
        "name": "场景后续建议",
        "description": "场景执行后的智能后续建议",
        "keywords": ["后续", "完成后", "然后", "接下来"]
    },
    "emotional_interaction": {
        "name": "情感交互",
        "description": "识别情感并给予情感化回应",
        "keywords": ["情感", "心情", "开心", "难过", "疲惫", "无聊"]
    },
    "workflow_orchestrator": {
        "name": "工作流编排",
        "description": "复杂任务的智能拆分与自动规划",
        "keywords": ["工作流", "编排", "复杂任务", "规划", "拆分"]
    },
    "context_memory": {
        "name": "上下文记忆",
        "description": "跨会话记忆和意图预测",
        "keywords": ["记忆", "上下文", "历史", "之前"]
    },
    "error_diagnosis": {
        "name": "错误诊断引擎",
        "description": "跨模块错误聚合与根因分析",
        "keywords": ["错误", "诊断", "问题", "故障", "修复"]
    },
    "task_memory": {
        "name": "任务记忆中心",
        "description": "跨模块任务追踪与意图预测",
        "keywords": ["任务", "记忆", "追踪", "待办"]
    },
    "coordinator": {
        "name": "任务协调中心",
        "description": "多模块协同工作",
        "keywords": ["协调", "协同", "中心"]
    },
    "context_bus": {
        "name": "上下文总线",
        "description": "跨模块上下文共享与状态同步",
        "keywords": ["上下文", "共享", "同步", "总线", "状态"]
    }
}


def load_module_registry():
    """加载模块注册表"""
    if os.path.exists(MODULE_REGISTRY_PATH):
        try:
            with open(MODULE_REGISTRY_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {"modules": DEFAULT_MODULES.copy(), "updated_at": datetime.now().isoformat()}


def save_module_registry(registry):
    """保存模块注册表"""
    os.makedirs(os.path.dirname(MODULE_REGISTRY_PATH), exist_ok=True)
    with open(MODULE_REGISTRY_PATH, 'w', encoding='utf-8') as f:
        json.dump(registry, f, ensure_ascii=False, indent=2)


def load_coordination_history():
    """加载协同历史"""
    if os.path.exists(COORDINATION_HISTORY_PATH):
        try:
            with open(COORDINATION_HISTORY_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {"history": [], "updated_at": datetime.now().isoformat()}


def save_coordination_history(history):
    """保存协同历史"""
    os.makedirs(os.path.dirname(COORDINATION_HISTORY_PATH), exist_ok=True)
    with open(COORDINATION_HISTORY_PATH, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def register_module(module_name, description, keywords=None):
    """注册智能模块"""
    registry = load_module_registry()

    if keywords is None:
        keywords = []

    registry["modules"][module_name] = {
        "name": module_name,
        "description": description,
        "keywords": keywords,
        "registered_at": datetime.now().isoformat()
    }
    registry["updated_at"] = datetime.now().isoformat()

    save_module_registry(registry)
    return f"Module {module_name} registered successfully"


def unregister_module(module_name):
    """注销智能模块"""
    registry = load_module_registry()

    if module_name in registry["modules"]:
        del registry["modules"][module_name]
        registry["updated_at"] = datetime.now().isoformat()
        save_module_registry(registry)
        return f"Module {module_name} unregistered"
    else:
        return f"Module {module_name} does not exist"


def list_modules():
    """列出已注册模块"""
    registry = load_module_registry()
    modules = registry.get("modules", {})

    if not modules:
        return "No registered modules"

    result = [f"Registered modules: {len(modules)}", ""]
    for name, info in modules.items():
        keywords = ", ".join(info.get("keywords", [])[:5])
        result.append(f"* {info.get('name', name)} ({name})")
        result.append(f"  Description: {info.get('description', 'N/A')}")
        result.append(f"  Keywords: {keywords if keywords else 'N/A'}")
        result.append("")

    return "\n".join(result)


def analyze_task(task_description):
    """分析任务需要的模块"""
    registry = load_module_registry()
    modules = registry.get("modules", {})

    if not task_description:
        return "Please provide task description"

    # 统计匹配的关键词
    matched_modules = []
    task_lower = task_description.lower()

    for module_name, module_info in modules.items():
        keywords = module_info.get("keywords", [])
        match_count = sum(1 for kw in keywords if kw.lower() in task_lower)

        if match_count > 0:
            matched_modules.append({
                "module_name": module_name,
                "name": module_info.get("name", module_name),
                "match_count": match_count,
                "description": module_info.get("description", ""),
                "keywords": [kw for kw in keywords if kw.lower() in task_lower]
            })

    # 按匹配数量排序
    matched_modules.sort(key=lambda x: x["match_count"], reverse=True)

    if not matched_modules:
        return "No modules identified for this task. Suggest using do.py directly."

    result = [f"Task analysis: {task_description}", ""]
    result.append(f"Suggested modules (sorted by priority):")
    result.append("")

    for i, m in enumerate(matched_modules, 1):
        result.append(f"{i}. {m['name']} ({m['module_name']})")
        result.append(f"   Description: {m['description']}")
        result.append(f"   Matched keywords: {', '.join(m['keywords'])}")
        result.append("")

    # 返回调用顺序建议
    return "\n".join(result)


def execute_task(task_description):
    """执行任务（自动编排模块）"""
    registry = load_module_registry()
    modules = registry.get("modules", {})
    history = load_coordination_history()

    if not task_description:
        return "Please provide task description"

    # 分析需要的模块
    matched_modules = []
    task_lower = task_description.lower()

    for module_name, module_info in modules.items():
        keywords = module_info.get("keywords", [])
        match_count = sum(1 for kw in keywords if kw.lower() in task_lower)

        if match_count > 0:
            matched_modules.append({
                "module_name": module_name,
                "name": module_info.get("name", module_name),
                "match_count": match_count,
                "priority": match_count
            })

    # 按优先级排序
    matched_modules.sort(key=lambda x: x["priority"], reverse=True)

    if not matched_modules:
        return "No modules identified for this task"

    # 记录协同历史
    coordination_record = {
        "task": task_description,
        "modules": [m["module_name"] for m in matched_modules],
        "timestamp": datetime.now().isoformat()
    }

    history["history"].insert(0, coordination_record)
    # 只保留最近50条
    history["history"] = history["history"][:50]
    history["updated_at"] = datetime.now().isoformat()
    save_coordination_history(history)

    # 输出协同计划
    result = [f"Task: {task_description}", ""]
    result.append("Auto-coordinated module execution order:")
    result.append("")

    for i, m in enumerate(matched_modules, 1):
        result.append(f"{i}. {m['name']} ({m['module_name']})")

    result.append("")
    result.append("Use do.py + module_name to trigger specific module execution")

    return "\n".join(result)


def show_history(limit=10):
    """查看协同历史"""
    history = load_coordination_history()
    records = history.get("history", [])

    if not records:
        return "No coordination history"

    result = [f"Recent {min(limit, len(records))} coordination records:", ""]

    for i, record in enumerate(records[:limit], 1):
        modules = ", ".join(record.get("modules", []))
        timestamp = record.get("timestamp", "")
        result.append(f"{i}. Task: {record.get('task', 'N/A')}")
        result.append(f"   Modules: {modules}")
        result.append(f"   Time: {timestamp}")
        result.append("")

    return "\n".join(result)


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print(__doc__)
        return

    command = sys.argv[1].lower()

    if command == "register":
        if len(sys.argv) < 4:
            print("Usage: intelligent_module_coordinator.py register <module_name> <description>")
            return
        module_name = sys.argv[2]
        description = sys.argv[3]
        keywords = sys.argv[4:] if len(sys.argv) > 4 else []
        print(register_module(module_name, description, keywords))

    elif command == "unregister":
        if len(sys.argv) < 3:
            print("Usage: intelligent_module_coordinator.py unregister <module_name>")
            return
        module_name = sys.argv[2]
        print(unregister_module(module_name))

    elif command == "list":
        print(list_modules())

    elif command == "analyze":
        task_description = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""
        print(analyze_task(task_description))

    elif command == "execute":
        task_description = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""
        print(execute_task(task_description))

    elif command == "history":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        print(show_history(limit))

    elif command in ["help", "-h", "--help"]:
        print(__doc__)

    else:
        print(f"Unknown command: {command}")
        print(__doc__)


if __name__ == "__main__":
    main()