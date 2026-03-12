#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
用户行为自动学习与适应模块

功能：
- 记录用户高频任务、时间段偏好、常用场景
- 分析用户行为模式并自动应用到任务推荐中
- 支持增量学习，更新用户偏好
- 输出用户行为分析结果到 runtime/state/user_behavior.json
"""

import os
import sys
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from collections import Counter, defaultdict
import random

# 确保 scripts 目录在路径中
SCRIPT_DIR = Path(__file__).parent
RUNTIME_DIR = SCRIPT_DIR.parent / "runtime"
STATE_DIR = RUNTIME_DIR / "state"

# 用户行为数据文件路径
BEHAVIOR_FILE = STATE_DIR / "user_behavior.json"

# 时间段定义
TIME_PERIODS = {
    "凌晨": (0, 6),
    "早晨": (6, 9),
    "上午": (9, 12),
    "中午": (12, 14),
    "下午": (14, 18),
    "傍晚": (18, 20),
    "晚上": (20, 24)
}

# 默认用户行为数据结构
DEFAULT_BEHAVIOR = {
    "created_at": None,
    "updated_at": None,
    "task_history": [],  # 任务执行历史
    "task_counts": {},  # 任务执行次数统计
    "time_preferences": {},  # 时间段偏好
    "scene_preferences": {},  # 场景偏好
    "pattern_scores": {},  # 行为模式得分
    "recent_tasks": [],  # 最近任务（用于短期偏好）
    "learning_enabled": True  # 学习开关
}


def get_time_period():
    """获取当前时间段名称"""
    hour = datetime.now().hour
    for period, (start, end) in TIME_PERIODS.items():
        if start <= hour < end:
            return period
    return "晚上"


def load_behavior_data():
    """加载用户行为数据"""
    if BEHAVIOR_FILE.exists():
        try:
            with open(BEHAVIOR_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data
        except Exception as e:
            print(f"加载用户行为数据失败: {e}")

    # 返回默认数据结构
    data = DEFAULT_BEHAVIOR.copy()
    data["created_at"] = datetime.now().isoformat()
    return data


def save_behavior_data(data):
    """保存用户行为数据"""
    data["updated_at"] = datetime.now().isoformat()
    try:
        with open(BEHAVIOR_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"保存用户行为数据失败: {e}")
        return False


def normalize_task_name(task_name):
    """标准化任务名称"""
    # 移除常见的后缀和前缀
    task_name = task_name.lower().strip()

    # 标准化同义词
    synonyms = {
        "听音乐": ["放歌", "播放音乐", "听歌", "音乐"],
        "看新闻": ["新闻", "浏览新闻", "看新闻"],
        "发消息": ["发个消息", "发消息给", "发送消息"],
        "申报绩效": ["绩效申报", "绩效达成", "绩效"],
    }

    for standard, variants in synonyms.items():
        for variant in variants:
            if variant in task_name:
                return standard

    return task_name


def record_task(task_name, success=True, context=None):
    """
    记录任务执行

    Args:
        task_name: 任务名称
        success: 是否成功
        context: 额外上下文信息（如场景名、时间段等）

    Returns:
        bool: 是否记录成功
    """
    data = load_behavior_data()

    if not data.get("learning_enabled", True):
        return False

    # 标准化任务名称
    normalized_task = normalize_task_name(task_name)

    # 获取时间段
    time_period = get_time_period()

    # 创建任务记录
    task_record = {
        "task": normalized_task,
        "original_task": task_name,
        "timestamp": datetime.now().isoformat(),
        "time_period": time_period,
        "success": success,
        "context": context or {}
    }

    # 添加到历史记录
    data["task_history"].append(task_record)

    # 限制历史记录长度（保留最近1000条）
    if len(data["task_history"]) > 1000:
        data["task_history"] = data["task_history"][-1000:]

    # 更新任务计数
    if normalized_task not in data["task_counts"]:
        data["task_counts"][normalized_task] = 0
    data["task_counts"][normalized_task] += 1

    # 更新最近任务
    data["recent_tasks"].append(normalized_task)
    if len(data["recent_tasks"]) > 50:
        data["recent_tasks"] = data["recent_tasks"][-50:]

    # 更新时间段偏好
    if time_period not in data["time_preferences"]:
        data["time_preferences"][time_period] = {}
    if normalized_task not in data["time_preferences"][time_period]:
        data["time_preferences"][time_period][normalized_task] = 0
    data["time_preferences"][time_period][normalized_task] += 1

    # 更新场景偏好
    if context and "scene" in context:
        scene = context["scene"]
        if scene not in data["scene_preferences"]:
            data["scene_preferences"][scene] = 0
        data["scene_preferences"][scene] += 1

    # 重新计算行为模式得分
    calculate_pattern_scores(data)

    # 保存数据
    return save_behavior_data(data)


def calculate_pattern_scores(data):
    """计算行为模式得分"""
    if not data["task_history"]:
        return

    # 计算任务频率得分
    task_counts = data.get("task_counts", {})
    total_tasks = sum(task_counts.values()) if task_counts else 1

    for task, count in task_counts.items():
        score = count / total_tasks
        data["pattern_scores"][task] = score


def get_frequent_tasks(limit=5):
    """获取最频繁的任务"""
    data = load_behavior_data()
    task_counts = data.get("task_counts", {})

    if not task_counts:
        return []

    # 按频率排序
    sorted_tasks = sorted(task_counts.items(), key=lambda x: x[1], reverse=True)
    return [{"task": t[0], "count": t[1]} for t in sorted_tasks[:limit]]


def get_time_preference(time_period=None):
    """
    获取时间段偏好

    Args:
        time_period: 指定时间段，None表示当前时间段

    Returns:
        list: 该时间段偏好的任务列表（按频率排序）
    """
    data = load_behavior_data()
    time_period = time_period or get_time_period()

    time_prefs = data.get("time_preferences", {}).get(time_period, {})

    if not time_prefs:
        return []

    sorted_tasks = sorted(time_prefs.items(), key=lambda x: x[1], reverse=True)
    return [{"task": t[0], "count": t[1]} for t in sorted_tasks[:5]]


def get_recent_tasks(limit=5):
    """获取最近执行的任务"""
    data = load_behavior_data()
    recent = data.get("recent_tasks", [])

    # 去重并保持顺序
    seen = set()
    unique_recent = []
    for task in reversed(recent):
        if task not in seen:
            seen.add(task)
            unique_recent.append(task)

    return unique_recent[:limit]


def get_recommendations(context=None, limit=3):
    """
    根据用户行为模式获取推荐

    Args:
        context: 上下文信息
        limit: 返回推荐数量

    Returns:
        list: 推荐任务列表
    """
    data = load_behavior_data()
    recommendations = []

    # 获取当前时间段的偏好任务
    current_period = get_time_period()
    time_prefs = get_time_preference(current_period)

    # 获取高频任务
    frequent = get_frequent_tasks(limit=5)

    # 获取最近任务
    recent = get_recent_tasks(limit=5)

    # 综合计算得分
    task_scores = defaultdict(float)

    # 时间段偏好权重
    for task_data in time_prefs:
        task_scores[task_data["task"]] += task_data["count"] * 2.0

    # 频率权重
    for task_data in frequent:
        task_scores[task_data["task"]] += task_data["count"] * 1.5

    # 最近任务权重
    for i, task in enumerate(recent):
        weight = (len(recent) - i) / len(recent)
        task_scores[task] += weight * 1.0

    # 按得分排序
    sorted_tasks = sorted(task_scores.items(), key=lambda x: x[1], reverse=True)

    # 去重并返回前limit个
    seen = set()
    for task, score in sorted_tasks:
        if task not in seen:
            seen.add(task)
            recommendations.append({"task": task, "score": round(score, 2)})
            if len(recommendations) >= limit:
                break

    return recommendations


def get_behavior_summary():
    """获取用户行为摘要"""
    data = load_behavior_data()

    summary = {
        "total_tasks": len(data.get("task_history", [])),
        "unique_tasks": len(data.get("task_counts", {})),
        "frequent_tasks": get_frequent_tasks(5),
        "current_time_period": get_time_period(),
        "time_period_preferences": {},
        "recent_tasks": get_recent_tasks(5),
        "recommendations": get_recommendations(limit=3),
        "learning_enabled": data.get("learning_enabled", True),
        "last_updated": data.get("updated_at")
    }

    # 添加各时间段的偏好
    for period in TIME_PERIODS.keys():
        prefs = get_time_preference(period)
        if prefs:
            summary["time_period_preferences"][period] = prefs[:3]

    return summary


def clear_history():
    """清除用户行为历史（重置）"""
    data = DEFAULT_BEHAVIOR.copy()
    data["created_at"] = datetime.now().isoformat()
    data["updated_at"] = datetime.now().isoformat()
    return save_behavior_data(data)


def set_learning_enabled(enabled):
    """设置学习开关"""
    data = load_behavior_data()
    data["learning_enabled"] = enabled
    return save_behavior_data(data)


def analyze_task_success_rate():
    """分析任务成功率"""
    data = load_behavior_data()
    history = data.get("task_history", [])

    if not history:
        return {"total": 0, "success": 0, "fail": 0, "rate": 0}

    success = sum(1 for h in history if h.get("success", True))
    fail = len(history) - success
    rate = success / len(history) if history else 0

    return {
        "total": len(history),
        "success": success,
        "fail": fail,
        "rate": round(rate * 100, 1)
    }


def main():
    """主函数：处理命令行参数"""
    if len(sys.argv) < 2:
        # 默认输出行为摘要
        summary = get_behavior_summary()
        print("=== 用户行为摘要 ===")
        print(f"总任务数: {summary['total_tasks']}")
        print(f"独立任务: {summary['unique_tasks']}")
        print(f"当前时段: {summary['current_time_period']}")
        print(f"学习状态: {'开启' if summary['learning_enabled'] else '关闭'}")
        print(f"\n高频任务:")
        for task in summary["frequent_tasks"]:
            print(f"  - {task['task']}: {task['count']}次")
        print(f"\n推荐任务:")
        for rec in summary["recommendations"]:
            print(f"  - {rec['task']} (得分: {rec['score']})")
        print(f"\n最近任务: {', '.join(summary['recent_tasks'])}")
        print(f"\n最后更新: {summary['last_updated']}")
        sys.exit(0)

    command = sys.argv[1]

    if command == "record":
        # 记录任务: python user_behavior_learner.py record <task_name> [success] [scene]
        if len(sys.argv) < 3:
            print("用法: python user_behavior_learner.py record <task_name> [success] [scene]")
            sys.exit(1)

        task_name = sys.argv[2]
        success = sys.argv[3].lower() == "true" if len(sys.argv) > 3 else True
        context = {}
        if len(sys.argv) > 4:
            context["scene"] = sys.argv[4]

        if record_task(task_name, success, context):
            print(f"已记录任务: {task_name}")
        else:
            print(f"记录失败或学习已关闭")

    elif command == "frequent":
        # 获取高频任务
        tasks = get_frequent_tasks()
        print("=== 高频任务 ===")
        for task in tasks:
            print(f"  {task['task']}: {task['count']}次")

    elif command == "preference":
        # 获取时间段偏好
        period = sys.argv[2] if len(sys.argv) > 2 else None
        prefs = get_time_preference(period)
        print(f"=== {period or get_time_period()} 偏好 ===")
        for pref in prefs:
            print(f"  {pref['task']}: {pref['count']}次")

    elif command == "recent":
        # 获取最近任务
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        tasks = get_recent_tasks(limit)
        print("=== 最近任务 ===")
        for task in tasks:
            print(f"  - {task}")

    elif command == "recommend":
        # 获取推荐
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 3
        recs = get_recommendations(limit=limit)
        print("=== 推荐任务 ===")
        for rec in recs:
            print(f"  {rec['task']} (得分: {rec['score']})")

    elif command == "summary":
        # 完整摘要
        summary = get_behavior_summary()
        print(json.dumps(summary, ensure_ascii=False, indent=2))

    elif command == "stats":
        # 成功率统计
        stats = analyze_task_success_rate()
        print(f"=== 任务成功率 ===")
        print(f"总计: {stats['total']}")
        print(f"成功: {stats['success']}")
        print(f"失败: {stats['fail']}")
        print(f"成功率: {stats['rate']}%")

    elif command == "clear":
        # 清除历史
        if clear_history():
            print("已清除用户行为历史")

    elif command == "enable":
        # 开启学习
        if set_learning_enabled(True):
            print("已开启学习功能")

    elif command == "disable":
        # 关闭学习
        if set_learning_enabled(False):
            print("已关闭学习功能")

    else:
        print(f"未知命令: {command}")
        print("可用命令: record, frequent, preference, recent, recommend, summary, stats, clear, enable, disable")
        sys.exit(1)


if __name__ == "__main__":
    main()