#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
任务状态推送模块
用于将 run_plan 的执行状态推送到文件，供外部轮询或悬浮窗显示
"""

import os
import json
import time
from datetime import datetime

STATE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "runtime", "state")
TASK_STATUS_FILE = os.path.join(STATE_DIR, "task_status.json")

def update_task_status(task_id, status, message="", progress=0):
    """
    更新任务状态

    Args:
        task_id (str): 任务唯一标识
        status (str): 任务状态 ('running', 'success', 'failed')
        message (str): 状态消息
        progress (int): 进度百分比 (0-100)
    """
    # 确保状态目录存在
    os.makedirs(STATE_DIR, exist_ok=True)

    # 读取现有状态
    status_data = {}
    if os.path.exists(TASK_STATUS_FILE):
        try:
            with open(TASK_STATUS_FILE, 'r', encoding='utf-8') as f:
                status_data = json.load(f)
        except Exception:
            pass

    # 更新状态
    status_data[task_id] = {
        'status': status,
        'message': message,
        'progress': progress,
        'updated_at': datetime.now().isoformat()
    }

    # 写入文件
    with open(TASK_STATUS_FILE, 'w', encoding='utf-8') as f:
        json.dump(status_data, f, ensure_ascii=False, indent=2)

def clear_task_status(task_id):
    """
    清除指定任务的状态

    Args:
        task_id (str): 任务唯一标识
    """
    # 确保状态目录存在
    os.makedirs(STATE_DIR, exist_ok=True)

    # 读取现有状态
    status_data = {}
    if os.path.exists(TASK_STATUS_FILE):
        try:
            with open(TASK_STATUS_FILE, 'r', encoding='utf-8') as f:
                status_data = json.load(f)
        except Exception:
            pass

    # 删除指定任务状态
    if task_id in status_data:
        del status_data[task_id]

    # 写入文件
    with open(TASK_STATUS_FILE, 'w', encoding='utf-8') as f:
        json.dump(status_data, f, ensure_ascii=False, indent=2)

def get_task_status(task_id):
    """
    获取指定任务的状态

    Args:
        task_id (str): 任务唯一标识

    Returns:
        dict: 任务状态信息，如果不存在返回 None
    """
    if not os.path.exists(TASK_STATUS_FILE):
        return None

    try:
        with open(TASK_STATUS_FILE, 'r', encoding='utf-8') as f:
            status_data = json.load(f)
        return status_data.get(task_id)
    except Exception:
        return None

if __name__ == "__main__":
    # 测试代码
    update_task_status("test_task_001", "running", "正在执行第一步", 10)
    print("Test status updated")
    print(get_task_status("test_task_001"))