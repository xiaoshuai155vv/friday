#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
情感交互模块

功能：
- 识别用户输入中的情感状态（如疲惫、无聊、开心、焦虑等）
- 根据情感状态生成情感化的回应
- 支持多种情感类型的关心、鼓励、安慰等回应
- 输出情感分析结果到 runtime/state/emotional_analysis.json
"""

import os
import sys
import json
import re
from datetime import datetime
from pathlib import Path

# 确保 scripts 目录在路径中
SCRIPT_DIR = Path(__file__).parent
RUNTIME_DIR = SCRIPT_DIR.parent / "runtime"
STATE_DIR = RUNTIME_DIR / "state"

# 情感模式定义：情感类型 -> 关键词 + 回应模板
EMOTION_PATTERNS = {
    "疲惫": {
        "keywords": ["累", "好累", "太累了", "疲惫", "疲倦", "困", "想睡", "好困", "没精神", "疲惫不堪", "好困啊", "累了"],
        "responses": [
            "辛苦了！先休息一下吧，我帮你看着时间",
            "听起来你很累了，要注意身体哦",
            "工作一天了，先放松一下吧",
            "你已经很努力了，适当休息一下"
        ],
        "suggestions": ["番茄钟", "休息提醒", "听音乐"]
    },
    "无聊": {
        "keywords": ["无聊", "没事干", "不知道干嘛", "没啥事", "闲得慌", "好无聊", "没事做", "无聊啊"],
        "responses": [
            "要不要听首歌放松一下？",
            "我帮你找点有意思的事做？",
            "想不想看个电影或者刷刷知乎？",
            "有什么想让我帮忙的吗？"
        ],
        "suggestions": ["听音乐", "看电影", "推荐"]
    },
    "开心": {
        "keywords": ["开心", "高兴", "快乐", "棒", "太好了", "不错", "满意", "舒服", "爽", "开心啊", "心情好"],
        "responses": [
            "听到你开心我也开心！",
            "太好了！有什么好事吗？",
            "继续保持！",
            "真替你高兴！"
        ],
        "suggestions": ["继续当前"]
    },
    "焦虑": {
        "keywords": ["焦虑", "着急", "烦躁", "烦", "不安", "紧张", "压力大", "焦虑啊", "急"],
        "responses": [
            "别着急，慢慢来",
            "先深呼吸一下，我在呢",
            "有什么我能帮你的吗？",
            "先把事情一件一件理清楚"
        ],
        "suggestions": ["番茄钟", "健康检查"]
    },
    "难过": {
        "keywords": ["难过", "伤心", "郁闷", "不爽", "烦心", "失落", "沮丧", "难受", "心情不好"],
        "responses": [
            "我在这里陪你",
            "一切都会好起来的",
            "想聊聊吗？我听着",
            "别太难过了"
        ],
        "suggestions": ["听音乐", "休息"]
    },
    "迷茫": {
        "keywords": ["迷茫", "困惑", "不知道", "怎么办", "纠结", "不知道该", "如何是好", "没方向"],
        "responses": [
            "想想目标是什么，我来帮你",
            "先把问题写下来，一件一件解决",
            "我可以帮你分析分析",
            "别着急，静下来想想"
        ],
        "suggestions": ["建议"]
    },
    "期待": {
        "keywords": ["期待", "盼望", "想要", "希望", "希望可以", "好想", "想要做"],
        "responses": [
            "加油！祝你实现",
            "有目标是好事！",
            "需要我帮忙准备什么吗？",
            "期待你的好消息！"
        ],
        "suggestions": ["待命"]
    },
    "感谢": {
        "keywords": ["谢谢", "感谢", "多亏", "太好了", "帮大忙", "感恩", "感谢你"],
        "responses": [
            "不客气！很高兴能帮到你",
            "应该的！有问题随时叫我",
            "不用谢！",
            "能帮到你我也很开心"
        ],
        "suggestions": ["待命"]
    }
}

# 情感强度修饰词
INTENSITY_MODIFIERS = {
    "非常": 1.5,
    "特别": 1.5,
    "极其": 1.8,
    "十分": 1.4,
    "有点": 0.7,
    "稍微": 0.6,
    "略微": 0.5
}


def detect_emotion(text):
    """
    检测输入文本中的情感

    Args:
        text: 用户输入文本

    Returns:
        dict: 包含情感类型、置信度和回应的字典
    """
    if not text:
        return None

    text = text.lower()
    detected_emotions = []

    for emotion_type, emotion_data in EMOTION_PATTERNS.items():
        matches = []
        for keyword in emotion_data["keywords"]:
            if keyword in text:
                matches.append(keyword)

        if matches:
            # 计算置信度
            base_confidence = 0.6
            match_bonus = len(matches) * 0.15
            confidence = min(base_confidence + match_bonus, 0.95)

            # 检查情感强度修饰词
            for modifier, multiplier in INTENSITY_MODIFIERS.items():
                if modifier in text:
                    confidence = min(confidence * multiplier, 0.98)
                    break

            detected_emotions.append({
                "type": emotion_type,
                "confidence": round(confidence, 2),
                "matches": matches,
                "responses": emotion_data["responses"],
                "suggestions": emotion_data["suggestions"]
            })

    if not detected_emotions:
        return None

    # 按置信度排序，返回最匹配的
    detected_emotions.sort(key=lambda x: x["confidence"], reverse=True)
    return detected_emotions[0]


def generate_response(emotion_data):
    """
    根据情感数据生成回应

    Args:
        emotion_data: detect_emotion 返回的情感数据

    Returns:
        str: 生成的回应文本
    """
    if not emotion_data:
        return None

    responses = emotion_data.get("responses", [])
    if not responses:
        return None

    # 根据时间和情感类型选择回应
    hour = datetime.now().hour

    # 疲惫时如果是工作时间之外，优先推荐休息
    if emotion_data["type"] == "疲惫" and (hour < 9 or hour > 18):
        # 优先选择关于休息的回应
        rest_responses = [r for r in responses if "休息" in r or "放松" in r]
        if rest_responses:
            return rest_responses[0 % len(rest_responses)]

    # 开心时工作时间优先选择简洁的回应
    if emotion_data["type"] == "开心" and 9 <= hour <= 18:
        return responses[1] if len(responses) > 1 else responses[0]

    # 随机选择一个回应
    import random
    return random.choice(responses)


def analyze_emotion(text):
    """
    完整的情感分析函数

    Args:
        text: 用户输入文本

    Returns:
        dict: 完整的情感分析结果
    """
    result = {
        "input": text,
        "timestamp": datetime.now().isoformat(),
        "detected": False,
        "emotion_type": None,
        "confidence": 0,
        "response": None,
        "suggestions": []
    }

    emotion_data = detect_emotion(text)
    if emotion_data:
        result["detected"] = True
        result["emotion_type"] = emotion_data["type"]
        result["confidence"] = emotion_data["confidence"]
        result["response"] = generate_response(emotion_data)
        result["suggestions"] = emotion_data.get("suggestions", [])

    return result


def save_result(result, filepath=None):
    """
    保存情感分析结果到文件

    Args:
        result: 情感分析结果
        filepath: 保存路径
    """
    if filepath is None:
        filepath = STATE_DIR / "emotional_analysis.json"

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)


def main():
    """主函数：处理命令行参数"""
    if len(sys.argv) < 2:
        print("用法: python emotional_interaction.py <文本>")
        print("示例: python emotional_interaction.py \"我好累啊\"")
        sys.exit(1)

    text = " ".join(sys.argv[1:])
    result = analyze_emotion(text)

    # 打印结果
    if result["detected"]:
        print(f"检测到情感: {result['emotion_type']} (置信度: {result['confidence']})")
        print(f"回应: {result['response']}")
        if result["suggestions"]:
            print(f"建议: {', '.join(result['suggestions'])}")
    else:
        print("未检测到明显情感")

    # 保存结果
    save_result(result)
    print(f"\n结果已保存到: {STATE_DIR / 'emotional_analysis.json'}")


if __name__ == "__main__":
    main()