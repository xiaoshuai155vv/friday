#!/usr/bin/env python3
"""
主动任务执行器
根据当前上下文（时间段、活动窗口、历史行为）主动生成和执行任务
"""

import json
import os
import time
import datetime
from pathlib import Path

# 导入必要的工具
import sys
sys.path.append(str(Path(__file__).parent.parent))

from scripts.autonomous_decision_maker import (
    get_time_context,
    get_environment_context,
    check_system_health,
    check_idle_time,
    get_active_suggestions,
    make_autonomous_decision
)

def load_task_history():
    """加载任务历史记录"""
    task_history_file = Path("runtime/state/task_history.json")
    if task_history_file.exists():
        with open(task_history_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_task_history(task_record):
    """保存任务历史记录"""
    task_history_file = Path("runtime/state/task_history.json")
    task_history = load_task_history()
    task_history.append(task_record)

    # 只保留最近100条记录
    if len(task_history) > 100:
        task_history = task_history[-100:]

    with open(task_history_file, 'w', encoding='utf-8') as f:
        json.dump(task_history, f, ensure_ascii=False, indent=2)

def check_idle_time():
    """检查用户空闲时间（简化版本，实际实现可能需要调用系统API）"""
    # 这里可以集成更复杂的空闲检测逻辑
    # 暂时返回一个固定值表示空闲状态
    return True  # 简化处理

def get_proactive_tasks():
    """
    生成主动任务列表
    根据当前上下文判断应该执行哪些主动任务
    """
    tasks = []

    # 获取系统健康状态
    health_ok = check_system_health()

    # 获取环境上下文（包含活动窗口和时间）
    env_context = get_environment_context()
    time_context = env_context.get("time", {})
    time_period = time_context.get("period", "")
    active_window = env_context.get("active_window", "")

    # 检查是否空闲
    is_idle = check_idle_time()

    # 根据时间段推荐任务
    if time_period == "morning":
        # 上午推荐任务
        if not health_ok:
            tasks.append({
                "type": "system_health_check",
                "description": "系统健康检查",
                "action": "建议运行系统健康检查"
            })
        elif active_window and "办公平台" not in active_window:
            tasks.append({
                "type": "check_ihaier",
                "description": "检查iHaier消息",
                "action": "打开iHaier查看是否有新消息"
            })

    elif time_period == "afternoon":
        # 下午推荐任务
        if active_window and "办公平台" not in active_window and "浏览器" not in active_window:
            tasks.append({
                "type": "check_ihaier",
                "description": "检查iHaier消息",
                "action": "打开iHaier查看是否有新消息"
            })
            tasks.append({
                "type": "browse_news",
                "description": "查看新闻",
                "action": "浏览新闻网站"
            })

    elif time_period == "evening":
        # 晚上推荐任务
        if active_window and "办公平台" not in active_window:
            tasks.append({
                "type": "check_ihaier",
                "description": "检查iHaier消息",
                "action": "打开iHaier查看是否有新消息"
            })

    # 如果用户空闲时间较长，推荐一些任务
    if is_idle:
        idle_tasks = [
            {
                "type": "browse_news",
                "description": "查看新闻",
                "action": "浏览新闻网站"
            },
            {
                "type": "watch_movie",
                "description": "观看电影",
                "action": "打开视频播放器"
            }
        ]
        tasks.extend(idle_tasks)

    return tasks

def execute_proactive_task(task):
    """
    执行一个主动任务（生成建议并保存）

    Args:
        task (dict): 任务信息

    Returns:
        bool: 是否成功生成建议
    """
    try:
        print(f"主动任务建议: {task['description']}")
        print(f"建议动作: {task.get('action', '无')}")

        # 记录任务
        task_record = {
            "timestamp": datetime.datetime.now().isoformat(),
            "task_type": task["type"],
            "description": task["description"],
            "action": task.get("action", ""),
            "status": "suggested"
        }

        # 保存任务历史
        save_task_history(task_record)

        return True

    except Exception as e:
        print(f"生成主动任务建议失败: {str(e)}")
        return False

def run_proactive_tasks():
    """
    运行所有主动任务，生成建议并保存
    """
    print("=== 主动任务执行器 ===")
    print("开始生成主动任务建议...")

    # 获取主动任务列表
    tasks = get_proactive_tasks()

    if not tasks:
        print("没有需要执行的主动任务")
        return False

    # 对每个任务生成建议
    success_count = 0
    for task in tasks:
        if execute_proactive_task(task):
            success_count += 1

    print(f"\n主动任务建议生成完成，建议数: {success_count}/{len(tasks)}")

    # 保存主动建议到文件供 do.py 使用
    proactive_suggestions_file = Path("runtime/state/proactive_suggestions.json")
    try:
        with open(proactive_suggestions_file, 'w', encoding='utf-8') as f:
            json.dump({
                "timestamp": datetime.datetime.now().isoformat(),
                "tasks": tasks,
                "count": success_count
            }, f, ensure_ascii=False, indent=2)
        print(f"主动建议已保存到 {proactive_suggestions_file}")
    except Exception as e:
        print(f"保存主动建议时出错: {e}")

    return success_count > 0

if __name__ == "__main__":
    run_proactive_tasks()