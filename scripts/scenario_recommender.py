#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
智能场景推荐引擎

功能：
- 根据用户行为习惯、时间段、系统状态主动推荐合适的场景计划
- 分析用户高频任务、时间段偏好
- 结合当前时间、系统状态生成个性化推荐
- 输出推荐结果到 runtime/state/scenario_recommendations.json
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path
from collections import Counter

# 确保 scripts 目录在路径中
SCRIPT_DIR = Path(__file__).parent
RUNTIME_DIR = SCRIPT_DIR.parent / "runtime"
STATE_DIR = RUNTIME_DIR / "state"

# 用户行为数据文件路径
BEHAVIOR_FILE = STATE_DIR / "user_behavior.json"
RECOMMENDATIONS_FILE = STATE_DIR / "scenario_recommendations.json"
FOCUS_STATE_FILE = STATE_DIR / "focus_reminder_state.json"

# 时间段定义
TIME_PERIODS = {
    "凌晨": (0, 6, ["听音乐", "看电影", "休息"]),
    "早晨": (6, 9, ["看新闻", "工作相关", "检查消息"]),
    "上午": (9, 12, ["工作相关", "处理邮件", "检查消息"]),
    "中午": (12, 14, ["休息", "听音乐", "看新闻"]),
    "下午": (14, 18, ["工作相关", "处理邮件", "检查消息"]),
    "傍晚": (18, 20, ["看新闻", "看电影", "听音乐"]),
    "晚上": (20, 24, ["看电影", "听音乐", "刷知乎", "休息"])
}

# 场景与标签映射
SCENE_TAGS = {
    "play_music.json": ["听音乐", "放松", "娱乐"],
    "listen_to_music.json": ["听音乐", "放松", "娱乐"],
    "read_news.json": ["看新闻", "资讯", "学习"],
    "news_reader.json": ["看新闻", "资讯", "学习"],
    "browse_zhihu.json": ["刷知乎", "社交", "学习"],
    "watch_movie.json": ["看电影", "放松", "娱乐"],
    "video_conference.json": ["会议", "工作"],
    "ihaier_performance_declaration.json": ["工作", "绩效申报"],
    "example_visit_website.json": ["浏览网站", "工作"],
    "example_ihaier_check_messages.json": ["工作", "检查消息", "办公"],
    "example_ihaier_my_latest_message.json": ["工作", "检查消息", "办公"],
    "send_to_zhouxiaoshuai.json": ["工作", "发消息", "办公"],
    "example_ihaier_send_message.json": ["工作", "发消息", "办公"]
}


def get_time_period():
    """获取当前时间段名称和推荐类型"""
    hour = datetime.now().hour
    for period, value in TIME_PERIODS.items():
        start, end, recommended_types = value
        if start <= hour < end:
            return period, recommended_types
    return "晚上", ["听音乐", "看电影", "放松"]


def load_user_behavior():
    """加载用户行为数据"""
    if BEHAVIOR_FILE.exists():
        try:
            with open(BEHAVIOR_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"加载用户行为数据失败: {e}")
    return None


def get_focus_state():
    """获取番茄钟/专注状态"""
    if FOCUS_STATE_FILE.exists():
        try:
            with open(FOCUS_STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"active": False}


def analyze_user_preferences(behavior_data):
    """分析用户偏好"""
    preferences = {
        "favorite_scenes": [],
        "time_preference": "晚上",
        "recent_focus": []
    }

    if not behavior_data:
        return preferences

    # 获取用户高频任务
    task_counts = behavior_data.get("task_counts", {})
    if task_counts:
        sorted_tasks = sorted(task_counts.items(), key=lambda x: x[1], reverse=True)
        preferences["favorite_scenes"] = [t[0] for t in sorted_tasks[:5]]

    # 获取时间段偏好
    time_prefs = behavior_data.get("time_preferences", {})
    if time_prefs:
        sorted_time = sorted(time_prefs.items(), key=lambda x: x[1], reverse=True)
        if sorted_time:
            preferences["time_preference"] = sorted_time[0][0]

    # 获取最近任务
    preferences["recent_focus"] = behavior_data.get("recent_tasks", [])[-5:]

    return preferences


def generate_recommendations(user_prefs, time_period, focus_state):
    """生成场景推荐"""
    recommendations = {
        "generated_at": datetime.now().isoformat(),
        "time_period": time_period,
        "focus_state": focus_state.get("active", False),
        "recommendations": []
    }

    # 如果用户处于专注模式，只推荐工作相关场景
    if focus_state.get("active", False):
        work_scenes = [s for s, tags in SCENE_TAGS.items() if "工作" in tags]
        for scene in work_scenes[:3]:
            recommendations["recommendations"].append({
                "scene": scene,
                "reason": "您当前处于专注模式",
                "priority": "high"
            })
        recommendations["focus_mode"] = True
        return recommendations

    # 基础推荐：根据时间段
    period, recommended_types = get_time_period()
    time_based_scenes = []
    for scene, tags in SCENE_TAGS.items():
        for tag in tags:
            if tag in recommended_types and scene not in [r["scene"] for r in time_based_scenes]:
                time_based_scenes.append({
                    "scene": scene,
                    "reason": f"当前是{period}，适合{tag}",
                    "priority": "medium"
                })
                break

    # 个性化推荐：根据用户历史行为
    personalized_scenes = []
    user_favorites = user_prefs.get("favorite_scenes", [])
    for task in user_favorites:
        for scene, tags in SCENE_TAGS.items():
            if task in tags and scene not in [r["scene"] for r in personalized_scenes]:
                personalized_scenes.append({
                    "scene": scene,
                    "reason": f"您经常{task}",
                    "priority": "high"
                })
                break

    # 合并推荐（去重）
    seen_scenes = set()
    final_recommendations = []

    # 优先添加个性化推荐
    for rec in personalized_scenes:
        if rec["scene"] not in seen_scenes:
            seen_scenes.add(rec["scene"])
            final_recommendations.append(rec)

    # 然后添时间基础推荐
    for rec in time_based_scenes:
        if rec["scene"] not in seen_scenes:
            seen_scenes.add(rec["scene"])
            final_recommendations.append(rec)

    recommendations["recommendations"] = final_recommendations[:5]
    return recommendations


def get_recommendations():
    """获取场景推荐（主入口）"""
    # 加载用户行为数据
    behavior_data = load_user_behavior()

    # 分析用户偏好
    user_prefs = analyze_user_preferences(behavior_data)

    # 获取当前时间段
    time_period, _ = get_time_period()

    # 获取专注状态
    focus_state = get_focus_state()

    # 生成推荐
    recommendations = generate_recommendations(user_prefs, time_period, focus_state)

    # 添加用户偏好信息
    recommendations["user_preferences"] = user_prefs

    # 保存推荐结果
    try:
        with open(RECOMMENDATIONS_FILE, "w", encoding="utf-8") as f:
            json.dump(recommendations, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"保存推荐结果失败: {e}")

    return recommendations


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="智能场景推荐引擎")
    parser.add_argument("action", nargs="?", default="get", choices=["get", "list-scenes"],
                        help="动作: get 获取推荐, list-scenes 列出可用场景")
    args = parser.parse_args()

    if args.action == "get":
        result = get_recommendations()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.action == "list-scenes":
        print("可用场景:")
        for scene, tags in SCENE_TAGS.items():
            print(f"  - {scene}: {', '.join(tags)}")


if __name__ == "__main__":
    main()