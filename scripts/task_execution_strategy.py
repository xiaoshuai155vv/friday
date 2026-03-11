#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
任务执行策略自适应模块
根据任务类型、历史执行情况、当前环境自动选择最佳执行策略
"""

import os
import sys
import json
import time
import subprocess
from datetime import datetime
from typing import Dict, Any, Optional, Tuple

# 项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE_DIR = os.path.join(PROJECT_ROOT, "runtime", "state")
STRATEGY_HISTORY_FILE = os.path.join(STATE_DIR, "task_strategy_history.json")

def get_current_environment() -> Dict[str, Any]:
    """
    获取当前系统环境信息（不依赖 psutil）
    """
    now = datetime.now()

    # 基础信息
    env = {
        "hour": now.hour,
        "day_of_week": now.weekday(),
        "timestamp": now.isoformat(),
        "is_work_hours": False,
        "is_weekend": False
    }

    # 判断是否为工作时间（周一到周五，8:00-18:00）
    env["is_work_hours"] = 0 <= env["day_of_week"] <= 4 and 8 <= env["hour"] <= 18

    # 判断是否为周末
    env["is_weekend"] = env["day_of_week"] >= 5

    # 尝试获取 CPU 使用情况（Windows）
    try:
        if sys.platform == "win32":
            result = subprocess.run(
                ["wmic", "cpu", "get", "loadpercentage"],
                capture_output=True,
                text=True,
                timeout=5
            )
            lines = result.stdout.strip().split("\n")
            if len(lines) > 1:
                cpu_val = lines[1].strip()
                if cpu_val.isdigit():
                    env["cpu_percent"] = int(cpu_val)
    except Exception:
        env["cpu_percent"] = 0

    return env

def get_task_history(task_name: str) -> Dict[str, Any]:
    """
    获取任务的历史执行记录
    """
    try:
        if os.path.exists(STRATEGY_HISTORY_FILE):
            with open(STRATEGY_HISTORY_FILE, 'r', encoding='utf-8') as f:
                history = json.load(f)
                return history.get(task_name, {})
        return {}
    except Exception:
        return {}

def save_task_history(task_name: str, strategy_used: str, execution_time: float, success: bool, environment: Dict[str, Any]):
    """
    保存任务执行历史
    """
    try:
        # 读取现有历史
        history = {}
        if os.path.exists(STRATEGY_HISTORY_FILE):
            with open(STRATEGY_HISTORY_FILE, 'r', encoding='utf-8') as f:
                try:
                    history = json.load(f)
                except json.JSONDecodeError:
                    history = {}

        # 更新任务历史
        if task_name not in history:
            history[task_name] = {
                "strategy_history": [],
                "execution_stats": {
                    "total_executions": 0,
                    "successful_executions": 0,
                    "average_execution_time": 0.0,
                    "strategy_distribution": {}
                }
            }

        task_history = history[task_name]

        # 记录本次执行
        task_history["strategy_history"].append({
            "strategy_used": strategy_used,
            "execution_time": execution_time,
            "success": success,
            "environment": environment,
            "timestamp": datetime.now().isoformat()
        })

        # 只保留最近 50 条记录
        task_history["strategy_history"] = task_history["strategy_history"][-50:]

        # 更新统计信息
        stats = task_history["execution_stats"]
        stats["total_executions"] += 1
        if success:
            stats["successful_executions"] += 1

        # 更新平均执行时间
        times = [h["execution_time"] for h in task_history["strategy_history"]]
        if times:
            stats["average_execution_time"] = sum(times) / len(times)

        # 更新策略分布
        strategy_count = stats["strategy_distribution"]
        strategy_count[strategy_used] = strategy_count.get(strategy_used, 0) + 1

        # 保存到文件
        os.makedirs(STATE_DIR, exist_ok=True)
        with open(STRATEGY_HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

    except Exception as e:
        # 记录错误但不影响主流程
        print(f"Warning: Failed to save task history: {e}", file=sys.stderr)

def get_adaptive_strategy(step_type: str, task_name: str = "", **kwargs) -> Dict[str, Any]:
    """
    根据任务类型和环境信息，自适应选择执行策略

    Args:
        step_type: 步骤类型 (vision, click, type, screenshot, etc.)
        task_name: 任务名称
        **kwargs: 其他参数

    Returns:
        Dict 包含策略配置的字典
    """

    # 获取当前环境
    environment = get_current_environment()

    # 默认策略
    strategy = {
        "strategy": "standard",  # standard, retry, wait
        "max_retries": 0,
        "retry_delay": 2.0,
        "wait_before": 0.0,
        "wait_after": 0.0,
        "priority": "normal",  # normal, high, low
        "use_enhanced_coords": False  # 对 vision 坐标使用增强处理
    }

    # 根据任务类型调整策略
    if step_type == "vision":
        # vision 通常需要更多重试，因为模型输出不稳定
        strategy.update({
            "strategy": "retry",
            "max_retries": 3,
            "retry_delay": 3.0,
            "priority": "high",
            "use_enhanced_coords": True
        })

    elif step_type in ["vision_coords"]:
        # vision_coords 是获取坐标的关键操作，需要更高的准确性
        strategy.update({
            "strategy": "retry",
            "max_retries": 5,  # 多轮取中位数
            "retry_delay": 2.0,
            "priority": "high",
            "use_enhanced_coords": True
        })

    elif step_type in ["click", "right_click", "middle_click", "drag"]:
        # 点击操作通常比较稳定，但需要考虑环境因素
        strategy.update({
            "strategy": "standard",
            "max_retries": 2,
            "retry_delay": 1.5,
            "priority": "normal"
        })

    elif step_type in ["type", "key", "paste"]:
        # 输入操作需要考虑系统响应速度
        strategy.update({
            "strategy": "standard",
            "max_retries": 1,
            "retry_delay": 1.0,
            "priority": "normal"
        })

    elif step_type == "screenshot":
        # 截图操作通常很快
        strategy.update({
            "strategy": "standard",
            "max_retries": 1,
            "retry_delay": 0.5,
            "priority": "low"
        })

    elif step_type == "scroll":
        # 滚动操作需要考虑速度和稳定性
        strategy.update({
            "strategy": "standard",
            "max_retries": 2,
            "retry_delay": 1.0,
            "priority": "normal"
        })

    elif step_type == "wait":
        # 等待操作
        strategy.update({
            "strategy": "standard",
            "max_retries": 0,
            "priority": "low"
        })

    # 根据环境调整策略
    cpu_load = environment.get("cpu_percent", 0)

    # 高 CPU 负载时降低重试次数，增加等待时间
    if cpu_load > 70:
        strategy["max_retries"] = max(0, strategy["max_retries"] - 1)
        strategy["wait_before"] = max(0.5, strategy["wait_before"])
        strategy["priority"] = "low"

    # 非工作时间系统负载通常更低，可以更激进地执行
    if environment.get("is_work_hours", False) == False:
        strategy["wait_before"] = max(0.2, strategy["wait_before"] * 0.7)

    # 根据历史执行情况调整策略
    if task_name:
        task_history = get_task_history(task_name)
        if task_history:
            stats = task_history.get("execution_stats", {})
            total = stats.get("total_executions", 0)
            if total > 0:
                success_rate = stats.get("successful_executions", 0) / total

                # 如果成功率低，增加重试次数
                if success_rate < 0.7:
                    strategy["max_retries"] = min(5, strategy["max_retries"] + 1)
                    strategy["retry_delay"] = min(5.0, strategy["retry_delay"] * 1.2)

                # 如果平均执行时间长，增加等待时间
                avg_time = stats.get("average_execution_time", 0)
                if avg_time > 5.0:
                    strategy["wait_before"] = max(0.5, strategy["wait_before"] + 0.5)

    # 工作时间增加等待时间
    if environment.get("is_work_hours", False):
        strategy["wait_before"] = max(1.0, strategy["wait_before"] + 0.5)

    return strategy

def apply_strategy(strategy: Dict[str, Any], step_type: str, step_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    应用策略到具体的步骤执行

    Args:
        strategy: 策略配置
        step_type: 步骤类型
        step_data: 步骤数据

    Returns:
        处理后的步骤数据
    """
    processed_data = step_data.copy()

    # 如果需要等待，添加等待时间
    if strategy.get("wait_before", 0) > 0:
        processed_data["wait_before"] = strategy["wait_before"]

    if strategy.get("wait_after", 0) > 0:
        processed_data["wait_after"] = strategy["wait_after"]

    # 如果需要使用增强坐标处理
    if strategy.get("use_enhanced_coords", False):
        processed_data["enhanced_mode"] = True

    return processed_data

def record_execution(task_name: str, step_type: str, strategy: Dict[str, Any], execution_time: float, success: bool):
    """
    记录单次执行结果
    """
    environment = get_current_environment()
    save_task_history(
        task_name,
        strategy.get("strategy", "standard"),
        execution_time,
        success,
        environment
    )

# 测试函数
if __name__ == "__main__":
    # 测试策略获取
    print("Testing adaptive strategy...")

    # 测试不同类型的步骤
    test_steps = ["vision", "click", "type", "screenshot", "scroll", "vision_coords"]

    for step_type in test_steps:
        strategy = get_adaptive_strategy(step_type, "test_task")
        print(f"\nStep type '{step_type}':")
        for k, v in strategy.items():
            print(f"  {k}: {v}")

    # 测试环境信息获取
    env = get_current_environment()
    print(f"\nEnvironment info:")
    for k, v in env.items():
        print(f"  {k}: {v}")