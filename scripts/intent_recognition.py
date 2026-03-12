#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
意图智能识别与推荐系统

功能：
- 识别用户的模糊意图（如「有啥好玩的」「推荐个东西」「不知道干啥」）
- 分析当前系统状态（时间、健康状态、番茄钟状态等）
- 结合场景计划库智能推荐合适的行动
- 输出推荐结果到 runtime/state/intent_recommendations.json
"""

import os
import sys
import json
import glob
import re
from datetime import datetime
from pathlib import Path

# 确保 scripts 目录在路径中
SCRIPT_DIR = Path(__file__).parent
RUNTIME_DIR = SCRIPT_DIR.parent / "runtime"
STATE_DIR = RUNTIME_DIR / "state"
LOGS_DIR = RUNTIME_DIR / "logs"

# 意图模式定义：模糊意图 -> 关键词 + 推荐方向
INTENT_PATTERNS = {
    "找事做": {
        "keywords": ["有啥好玩的", "有啥干的", "不知道干啥", "推荐个东西", "无聊", "没什么事", "干嘛", "干什么"],
        "category": "entertainment",
        "score_boost": {"music": 1.2, "movie": 1.1, "zhihu": 1.0, "news": 0.9}
    },
    "工作": {
        "keywords": ["工作", "干活", "办公", "忙", "处理", "申报", "绩效"],
        "category": "work",
        "score_boost": {"ihaier": 1.5, "performance": 1.3, "messages": 1.0}
    },
    "休息": {
        "keywords": ["休息", "放松", "休息一下", "累了", "困", "想躺"],
        "category": "rest",
        "score_boost": {"music": 1.5, "movie": 1.3, "zhihu": 0.8}
    },
    "学习": {
        "keywords": ["学习", "看看", "了解", "查一下", "看看新闻", "刷知乎"],
        "category": "learning",
        "score_boost": {"news": 1.5, "zhihu": 1.3, "website": 1.0}
    },
    "社交": {
        "keywords": ["聊天", "消息", "发消息", "联系人", "谁找我", "看看有人没"],
        "category": "social",
        "score_boost": {"ihaier": 1.5, "messages": 1.3}
    },
    "娱乐": {
        "keywords": ["听歌", "听音乐", "看电影", "看视频", "娱乐", "玩"],
        "category": "entertainment",
        "score_boost": {"music": 1.5, "movie": 1.5, "video": 1.2}
    }
}

# 场景计划文件映射
SCENARIO_PLANS = {
    "music": {
        "name": "听音乐",
        "plan": "play_music.json",
        "keywords": ["听歌", "听音乐", "放歌", "音乐", "歌"]
    },
    "movie": {
        "name": "看电影",
        "plan": "watch_movie.json",
        "keywords": ["电影", "看片", "视频"]
    },
    "zhihu": {
        "name": "刷知乎",
        "plan": "browse_zhihu.json",
        "keywords": ["知乎", "刷知乎"]
    },
    "news": {
        "name": "看新闻",
        "plan": "read_news.json",
        "keywords": ["新闻", "资讯"]
    },
    "ihaier": {
        "name": "iHaier 办公",
        "plan": "ihaier_contact_latest_message.json",
        "keywords": ["办公", "消息", "联系人", "谁找我", "ihaier"]
    },
    "performance": {
        "name": "绩效申报",
        "plan": "ihaier_performance_declaration.json",
        "keywords": ["绩效", "申报"]
    },
    "messages": {
        "name": "发送消息",
        "plan": "send_to_zhouxiaoshuai.json",
        "keywords": ["发消息", "联系"]
    },
    "website": {
        "name": "访问网站",
        "plan": "example_visit_website.json",
        "keywords": ["网站", "浏览器", "访问"]
    },
    "video": {
        "name": "视频会议",
        "plan": "video_conference.json",
        "keywords": ["会议", "视频会议"]
    }
}


def get_system_state():
    """获取当前系统状态"""
    state = {
        "time": datetime.now().strftime("%H:%M"),
        "hour": datetime.now().hour,
        "weekday": datetime.now().weekday(),
        "is_workday": datetime.now().weekday() < 5,
        "health_status": "unknown",
        "pomodoro_status": "idle",
        "recent_tasks": []
    }

    # 检查健康状态
    health_file = STATE_DIR / "health_report.json"
    if health_file.exists():
        try:
            with open(health_file, "r", encoding="utf-8") as f:
                health = json.load(f)
                state["health_status"] = health.get("overall_status", "unknown")
        except:
            pass

    # 检查番茄钟状态
    pomodoro_file = STATE_DIR / "pomodoro_status.json"
    if pomodoro_file.exists():
        try:
            with open(pomodoro_file, "r", encoding="utf-8") as f:
                pomodoro = json.load(f)
                state["pomodoro_status"] = pomodoro.get("status", "idle")
        except:
            pass

    # 检查最近任务
    recent_logs = list(LOGS_DIR.glob("behavior_*.log"))
    if recent_logs:
        latest_log = max(recent_logs, key=lambda p: p.stat().st_mtime)
        try:
            with open(latest_log, "r", encoding="utf-8") as f:
                lines = f.readlines()
                state["recent_tasks"] = [line.strip() for line in lines[-10:] if line.strip()]
        except:
            pass

    return state


def recognize_intent(user_input):
    """识别用户意图"""
    user_input = user_input.lower().strip()

    matched_intent = None
    matched_keywords = []

    for intent_name, intent_info in INTENT_PATTERNS.items():
        for keyword in intent_info["keywords"]:
            if keyword in user_input:
                matched_intent = intent_name
                matched_keywords.append(keyword)
                break
        if matched_intent:
            break

    # 如果没有匹配到明确意图，根据上下文猜测
    if not matched_intent:
        # 根据时间猜测意图
        hour = datetime.now().hour
        if 9 <= hour < 12 or 14 <= hour < 18:
            matched_intent = "工作"
        elif 12 <= hour < 14:
            matched_intent = "休息"
        elif 18 <= hour < 22:
            matched_intent = "娱乐"
        else:
            matched_intent = "休息"

    return matched_intent, matched_keywords


def get_time_based_boost():
    """获取基于时间的推荐权重"""
    hour = datetime.now().hour

    if 9 <= hour < 12:
        return {"work": 1.3, "music": 0.7, "movie": 0.5, "zhihu": 0.6}
    elif 12 <= hour < 14:
        return {"work": 0.5, "music": 1.2, "movie": 1.0, "zhihu": 0.8, "news": 1.2}
    elif 14 <= hour < 18:
        return {"work": 1.3, "music": 0.7, "movie": 0.5, "zhihu": 0.6}
    elif 18 <= hour < 22:
        return {"work": 0.3, "music": 1.5, "movie": 1.5, "zhihu": 1.2, "news": 0.5}
    else:  # 22-24 或 6-9
        return {"work": 0.2, "music": 1.0, "movie": 1.2, "zhihu": 0.8}


def generate_recommendations(user_input, max_results=3):
    """生成智能推荐"""
    system_state = get_system_state()
    intent, matched_keywords = recognize_intent(user_input)

    intent_info = INTENT_PATTERNS.get(intent, INTENT_PATTERNS["找事做"])
    category = intent_info.get("category", "general")

    # 获取时间权重
    time_boost = get_time_based_boost()

    # 计算每个场景的得分
    scores = {}
    for key, plan_info in SCENARIO_PLANS.items():
        score = 50  # 基础分

        # 意图匹配加分
        intent_boost = intent_info.get("score_boost", {}).get(key, 1.0)
        score *= intent_boost

        # 时间权重加分
        time_b = time_boost.get(key, 1.0)
        score *= time_b

        # 系统状态调整
        if system_state["pomodoro_status"] == "working" and key == "work":
            score *= 0.5  # 番茄钟工作时减少工作推荐
        elif system_state["pomodoro_status"] == "break" and key in ["music", "movie"]:
            score *= 1.3  # 休息时增加娱乐推荐

        scores[key] = score

    # 按得分排序
    sorted_scenarios = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    # 生成推荐结果
    recommendations = []
    for key, score in sorted_scenarios[:max_results]:
        plan_info = SCENARIO_PLANS[key]
        recommendations.append({
            "scenario": key,
            "name": plan_info["name"],
            "plan_file": plan_info["plan"],
            "score": round(score, 2),
            "reason": _generate_reason(key, intent, system_state)
        })

    return {
        "user_input": user_input,
        "recognized_intent": intent,
        "matched_keywords": matched_keywords,
        "system_state": {
            "time": system_state["time"],
            "health": system_state["health_status"],
            "pomodoro": system_state["pomodoro_status"]
        },
        "recommendations": recommendations,
        "timestamp": datetime.now().isoformat()
    }


def _generate_reason(scenario_key, intent, system_state):
    """生成推荐理由"""
    reasons = {
        "music": "适合放松身心，听歌可以缓解疲劳",
        "movie": "看电影是休闲娱乐的好选择",
        "zhihu": "刷知乎可以了解最新资讯和热门话题",
        "news": "看看新闻了解国内外大事",
        "ihaier": "处理工作消息和联系同事",
        "performance": "完成绩效申报工作",
        "messages": "与同事朋友保持联系",
        "website": "访问网站获取信息",
        "video": "参加或安排视频会议"
    }

    base_reason = reasons.get(scenario_key, "推荐")

    # 添加上下文
    if system_state["pomodoro_status"] == "working":
        return f"{base_reason}（番茄钟工作中，建议专注）"
    elif system_state["pomodoro_status"] == "break":
        return f"{base_reason}（休息时间到了，适当放松）"

    return base_reason


def save_recommendations(result):
    """保存推荐结果到文件"""
    output_file = STATE_DIR / "intent_recommendations.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    return output_file


def main():
    """主函数"""
    if len(sys.argv) < 2:
        # 无参数时输出简短推荐
        result = generate_recommendations("有啥好玩的")
    else:
        # 有参数时识别用户输入
        user_input = " ".join(sys.argv[1:])
        result = generate_recommendations(user_input)

    # 保存结果
    output_file = save_recommendations(result)

    # 输出推荐
    print(f"\n🎯 识别意图: {result['recognized_intent']}")
    if result['matched_keywords']:
        print(f"📌 匹配关键词: {', '.join(result['matched_keywords'])}")
    print(f"⏰ 当前时间: {result['system_state']['time']}")
    print(f"🍅 番茄钟: {result['system_state']['pomodoro']}")
    print(f"\n💡 为您推荐:")
    for i, rec in enumerate(result['recommendations'], 1):
        print(f"  {i}. {rec['name']} (得分: {rec['score']})")
        print(f"     理由: {rec['reason']}")
        print(f"     执行: run_plan assets/plans/{rec['plan_file']}")

    print(f"\n📁 推荐结果已保存到: {output_file}")

    return result


if __name__ == "__main__":
    main()