#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
任务状态管理模块
用于保存和恢复中断的任务状态
"""

import os
import json
import sys
from datetime import datetime

SCRIPTS = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(SCRIPTS)
STATE_DIR = os.path.join(PROJECT, "runtime", "state")
INTERRUPTED_TASKS_FILE = os.path.join(STATE_DIR, "interrupted_tasks.json")


def save_task_state(plan_path, step_index, step_name, step_result, total_steps, plan_data):
    """
    保存任务状态

    Args:
        plan_path (str): 计划文件路径
        step_index (int): 当前步骤索引
        step_name (str): 当前步骤名称
        step_result (str): 当前步骤结果
        total_steps (int): 总步骤数
        plan_data (list): 计划数据
    """
    # 创建状态目录
    os.makedirs(STATE_DIR, exist_ok=True)

    # 构建任务状态
    task_state = {
        "plan_path": plan_path,
        "step_index": step_index,
        "step_name": step_name,
        "step_result": step_result,
        "total_steps": total_steps,
        "plan_data": plan_data,
        "saved_at": datetime.now().isoformat(),
        "status": "interrupted"
    }

    # 读取现有的中断任务列表
    interrupted_tasks = []
    if os.path.exists(INTERRUPTED_TASKS_FILE):
        try:
            with open(INTERRUPTED_TASKS_FILE, "r", encoding="utf-8") as f:
                interrupted_tasks = json.load(f)
        except (OSError, json.JSONDecodeError):
            interrupted_tasks = []

    # 添加新的任务状态到列表
    interrupted_tasks.append(task_state)

    # 保存更新后的列表
    try:
        with open(INTERRUPTED_TASKS_FILE, "w", encoding="utf-8") as f:
            json.dump(interrupted_tasks, f, ensure_ascii=False, indent=2)
        return True
    except OSError:
        return False


def get_interrupted_tasks():
    """
    获取所有中断的任务列表

    Returns:
        list: 中断任务列表
    """
    if not os.path.exists(INTERRUPTED_TASKS_FILE):
        return []

    try:
        with open(INTERRUPTED_TASKS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return []


def clear_interrupted_task(plan_path):
    """
    清除指定计划的中断任务状态

    Args:
        plan_path (str): 计划文件路径
    """
    if not os.path.exists(INTERRUPTED_TASKS_FILE):
        return

    try:
        with open(INTERRUPTED_TASKS_FILE, "r", encoding="utf-8") as f:
            interrupted_tasks = json.load(f)

        # 过滤掉已完成的任务
        filtered_tasks = [task for task in interrupted_tasks if task.get("plan_path") != plan_path]

        # 保存更新后的列表
        with open(INTERRUPTED_TASKS_FILE, "w", encoding="utf-8") as f:
            json.dump(filtered_tasks, f, ensure_ascii=False, indent=2)
    except (OSError, json.JSONDecodeError):
        pass


def clear_all_interrupted_tasks():
    """
    清除所有中断的任务状态
    """
    if os.path.exists(INTERRUPTED_TASKS_FILE):
        try:
            os.remove(INTERRUPTED_TASKS_FILE)
        except OSError:
            pass


def get_interrupted_task_by_plan(plan_path):
    """
    获取指定计划的中断任务状态

    Args:
        plan_path (str): 计划文件路径

    Returns:
        dict or None: 中断任务状态，如果不存在则返回None
    """
    interrupted_tasks = get_interrupted_tasks()
    for task in interrupted_tasks:
        if task.get("plan_path") == plan_path and task.get("status") == "interrupted":
            return task
    return None


def resume_task(plan_path):
    """
    恢复指定计划的中断任务

    Args:
        plan_path (str): 计划文件路径

    Returns:
        dict or None: 中断任务状态，如果不存在则返回None
    """
    task = get_interrupted_task_by_plan(plan_path)
    if task:
        # 从中断点开始执行
        return task
    return None


if __name__ == "__main__":
    # 测试函数
    print("任务状态管理模块已加载")