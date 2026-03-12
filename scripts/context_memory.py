#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
上下文记忆与意图预测系统

实现跨会话的上下文记忆和意图预测功能，让系统能够记住之前的交互
并在适当时机主动提供帮助。

功能：
- 上下文记忆：记录跨会话的关键交互信息
- 意图预测：根据用户历史行为预测可能的下一个意图
- 上下文检索：根据当前上下文检索相关的历史信息

用法:
  python context_memory.py add "<内容>" [--type <类型>]
  python context_memory.py predict [--current "<当前意图>"]
  python context_memory.py recent [--count <数量>]
  python context_memory.py search "<关键词>"
  python context_memory.py clear
  python context_memory.py stats
"""

import argparse
import json
import os
from datetime import datetime, timezone
from collections import Counter

# 路径配置
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
STATE_DIR = os.path.join(PROJECT_ROOT, "runtime", "state")
CONTEXT_FILE = os.path.join(STATE_DIR, "context_memory.json")

# 意图关键词映射
INTENT_PATTERNS = {
    "iHaier消息": ["发消息", "给某人发消息", "消息", "联系人", "办公平台"],
    "iHaier绩效": ["绩效", "绩效申报", "绩效达成", "填写绩效"],
    "音乐": ["放歌", "听歌", "播放音乐", "音乐"],
    "摄像头": ["摄像头", "自拍", "相机", "拍照"],
    "浏览器": ["浏览器", "上网", "访问", "网站"],
    "文件操作": ["文件", "文件夹", "打开文件", "保存"],
    "系统设置": ["设置", "配置", "调整"],
    "健康检查": ["健康", "检查", "系统状态"],
    "工作流": ["工作流", "编排", "任务计划"],
    "定时任务": ["定时", "计划任务", "调度"],
}


def ensure_dir():
    """确保目录存在"""
    os.makedirs(STATE_DIR, exist_ok=True)


def load_context():
    """加载上下文记忆"""
    ensure_dir()
    if not os.path.exists(CONTEXT_FILE):
        return {"contexts": [], "intent_history": [], "last_updated": None}
    try:
        with open(CONTEXT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"contexts": [], "intent_history": [], "last_updated": None}


def save_context(data):
    """保存上下文记忆"""
    ensure_dir()
    data["last_updated"] = datetime.now(timezone.utc).isoformat()
    with open(CONTEXT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def add_context(content, context_type="general"):
    """添加新的上下文记录"""
    data = load_context()

    context_entry = {
        "content": content,
        "type": context_type,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    data["contexts"].append(context_entry)

    # 识别意图并记录
    intent = recognize_intent(content)
    if intent:
        data["intent_history"].append({
            "intent": intent,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    # 只保留最近 100 条上下文和 200 条意图历史
    data["contexts"] = data["contexts"][-100:]
    data["intent_history"] = data["intent_history"][-200:]

    save_context(data)
    return context_entry


def recognize_intent(text):
    """识别文本中的意图"""
    text_lower = text.lower()
    for intent, patterns in INTENT_PATTERNS.items():
        for pattern in patterns:
            if pattern in text_lower:
                return intent
    return None


def predict_intent(current_intent=None):
    """预测用户可能的下一个意图"""
    data = load_context()

    if not data["intent_history"]:
        return {
            "prediction": None,
            "reason": "没有足够的历史数据",
            "suggestions": list(INTENT_PATTERNS.keys())[:3],
        }

    # 统计最近意图
    recent_intents = [h["intent"] for h in data["intent_history"][-20:] if h["intent"]]
    if not recent_intents:
        return {
            "prediction": None,
            "reason": "最近没有识别的意图",
            "suggestions": list(INTENT_PATTERNS.keys())[:3],
        }

    intent_counts = Counter(recent_intents)
    most_common = intent_counts.most_common(1)[0]

    # 预测下一个意图（考虑时间模式和序列）
    prediction = most_common[0]
    confidence = most_common[1] / len(recent_intents)

    # 获取其他可能的意图
    suggestions = [intent for intent, _ in intent_counts.most_common(4) if intent != prediction]
    if current_intent and current_intent not in suggestions:
        suggestions.append(current_intent)
    suggestions = suggestions[:3]

    return {
        "prediction": prediction,
        "confidence": round(confidence, 2),
        "reason": f"基于最近 {len(recent_intents)} 次交互统计",
        "recent_intents": recent_intents[-5:],
        "suggestions": suggestions,
    }


def get_recent_contexts(count=10):
    """获取最近的上下文"""
    data = load_context()
    return data["contexts"][-count:]


def search_context(keyword):
    """搜索相关上下文"""
    data = load_context()
    keyword_lower = keyword.lower()
    results = []

    for ctx in data["contexts"]:
        if keyword_lower in ctx["content"].lower():
            results.append(ctx)

    return results


def get_stats():
    """获取统计信息"""
    data = load_context()

    # 意图统计
    intent_counts = Counter(h["intent"] for h in data["intent_history"] if h["intent"])

    return {
        "total_contexts": len(data["contexts"]),
        "total_intent_records": len(data["intent_history"]),
        "intent_distribution": dict(intent_counts.most_common(10)),
        "last_updated": data["last_updated"],
    }


def clear_context():
    """清空上下文记忆"""
    ensure_dir()
    data = {"contexts": [], "intent_history": [], "last_updated": None}
    save_context(data)
    return {"status": "cleared", "message": "上下文记忆已清空"}


def main():
    parser = argparse.ArgumentParser(description="上下文记忆与意图预测系统")
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # add 命令
    add_parser = subparsers.add_parser("add", help="添加新的上下文")
    add_parser.add_argument("content", help="上下文内容")
    add_parser.add_argument("--type", default="general", help="上下文类型")

    # predict 命令
    predict_parser = subparsers.add_parser("predict", help="预测下一个意图")
    predict_parser.add_argument("--current", help="当前意图")

    # recent 命令
    recent_parser = subparsers.add_parser("recent", help="获取最近上下文")
    recent_parser.add_argument("--count", type=int, default=10, help="获取数量")

    # search 命令
    search_parser = subparsers.add_parser("search", help="搜索上下文")
    search_parser.add_argument("keyword", help="搜索关键词")

    # clear 命令
    subparsers.add_parser("clear", help="清空上下文记忆")

    # stats 命令
    subparsers.add_parser("stats", help="获取统计信息")

    args = parser.parse_args()

    if args.command == "add":
        result = add_context(args.content, args.type)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "predict":
        result = predict_intent(args.current)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "recent":
        result = get_recent_contexts(args.count)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "search":
        result = search_context(args.keyword)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "clear":
        result = clear_context()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "stats":
        result = get_stats()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()