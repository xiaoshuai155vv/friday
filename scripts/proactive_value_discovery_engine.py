#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能主动价值发现与即时服务引擎（Proactive Value Discovery Engine）

让系统能够主动分析用户当前情境（行为、环境、时间、任务状态），识别用户可能需要但
尚未提出的高价值服务，即时提供并执行，实现从「被动响应」到「主动发现+即时服务」的范式升级。

功能：
1. 多维度情境分析 - 分析用户行为、环境、时间、任务状态、情绪
2. 价值机会识别 - 发现高价值但用户未说的需求
3. 即时服务生成与推荐 - 生成服务方案并主动询问或自动执行
4. 服务效果追踪与学习 - 追踪服务效果并从中学习

版本：1.0.0
"""

import json
import os
from datetime import datetime, timedelta
from collections import defaultdict
from pathlib import Path
import argparse

# 基础路径
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
STATE_DIR = PROJECT_ROOT / "runtime" / "state"
LOGS_DIR = PROJECT_ROOT / "runtime" / "logs"

# 数据文件路径
CONTEXT_DATA_FILE = STATE_DIR / "current_context.json"
USER_BEHAVIOR_FILE = STATE_DIR / "user_behavior_patterns.json"
VALUE_OPPORTUNITIES_FILE = STATE_DIR / "value_opportunities.json"
SERVICE_RECOMMENDATIONS_FILE = STATE_DIR / "service_recommendations.json"
SERVICE_FEEDBACK_FILE = STATE_DIR / "value_discovery_feedback.json"

# 版本
VERSION = "1.0.0"


def load_json_safe(filepath, default=None):
    """安全加载JSON文件"""
    if default is None:
        default = {}
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"加载文件失败 {filepath}: {e}")
    return default


def save_json_safe(filepath, data):
    """安全保存JSON文件"""
    try:
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"保存文件失败 {filepath}: {e}")
        return False


def get_current_context():
    """获取当前系统上下文"""
    context = {
        "timestamp": datetime.now().isoformat(),
        "hour": datetime.now().hour,
        "weekday": datetime.now().weekday(),
        "time_period": get_time_period(),
        "recent_behaviors": get_recent_behaviors(),
        "active_applications": get_active_applications(),
        "system_state": get_system_state()
    }
    return context


def get_time_period():
    """获取时间段"""
    hour = datetime.now().hour
    if 6 <= hour < 9:
        return "早晨"
    elif 9 <= hour < 12:
        return "上午"
    elif 12 <= hour < 14:
        return "午间"
    elif 14 <= hour < 18:
        return "下午"
    elif 18 <= hour < 22:
        return "傍晚"
    else:
        return "夜间"


def get_recent_behaviors():
    """获取最近的用户行为"""
    behavior_data = load_json_safe(USER_BEHAVIOR_FILE, {"behaviors": []})
    behaviors = behavior_data.get("behaviors", [])
    # 返回最近10条
    return behaviors[-10:] if behaviors else []


def get_active_applications():
    """获取当前活跃的应用（如果有）"""
    # 尝试从状态文件中获取
    recent_logs = STATE_DIR / "recent_logs.json"
    logs_data = load_json_safe(recent_logs, {"logs": []})
    apps = set()
    for log in logs_data.get("logs", []):
        if "打开应用" in str(log.get("action", "")):
            apps.add(log.get("action", ""))
    return list(apps)[:5]


def get_system_state():
    """获取系统状态"""
    return {
        "focus_mode": False,  # 简化，实际可以从相关引擎获取
        "is_busy": False,
        "last_interaction": datetime.now().isoformat()
    }


def analyze_context():
    """分析当前情境"""
    context = get_current_context()

    # 基于时间和行为分析情境
    situational_analysis = {
        "time_context": context["time_period"],
        "behavior_pattern": analyze_behavior_pattern(context["recent_behaviors"]),
        "suggested_need": infer_needs_from_context(context),
        "opportunity_score": calculate_opportunity_score(context)
    }

    return situational_analysis


def analyze_behavior_pattern(behaviors):
    """分析行为模式"""
    if not behaviors:
        return "无行为数据"

    action_types = defaultdict(int)
    for b in behaviors:
        action = b.get("action", "")
        if action:
            action_types[action] += 1

    if not action_types:
        return "无明确模式"

    top_action = max(action_types.items(), key=lambda x: x[1])[0]

    # 判断用户状态
    work_keywords = ["工作", "办公", "代码", "文档", "会议"]
    entertainment_keywords = ["视频", "音乐", "游戏", "娱乐"]

    for kw in work_keywords:
        if any(kw in str(a) for a in action_types.keys()):
            return "工作中"
    for kw in entertainment_keywords:
        if any(kw in str(a) for a in action_types.keys()):
            return "娱乐中"

    return f"执行中: {top_action}"


def infer_needs_from_context(context):
    """从情境推断用户可能的需求"""
    needs = []
    hour = context["hour"]
    weekday = context["weekday"]
    time_period = context["time_period"]

    # 基于时间推断
    if 9 <= hour < 12 and weekday < 5:
        needs.append({"type": "工作准备", "priority": 8, "suggestion": "检查今日工作计划"})
    elif 14 <= hour < 17 and weekday < 5:
        needs.append({"type": "下午工作", "priority": 7, "suggestion": "建议短暂休息或切换任务"})
    elif 18 <= hour < 20:
        needs.append({"type": "下班准备", "priority": 8, "suggestion": "总结今日工作或安排明日任务"})
    elif time_period == "夜间":
        needs.append({"type": "放松", "priority": 6, "suggestion": "可播放音乐或观看视频放松"})

    # 基于行为推断
    recent = context.get("recent_behaviors", [])
    if recent:
        last_action = recent[-1].get("action", "") if recent else ""
        if "搜索" in last_action:
            needs.append({"type": "信息探索", "priority": 7, "suggestion": "可能需要整理或保存搜索结果"})
        if "文档" in last_action:
            needs.append({"type": "文档处理", "priority": 8, "suggestion": "检查文档保存状态或格式"})

    return needs


def calculate_opportunity_score(context):
    """计算价值发现机会分数"""
    score = 50  # 基础分数

    # 时间因素
    if context["time_period"] in ["早晨", "下午"]:
        score += 10  # 工作黄金时段
    elif context["time_period"] == "夜间":
        score += 5  # 放松时段

    # 行为因素
    if len(context.get("recent_behaviors", [])) > 5:
        score += 15  # 活跃用户

    # 系统状态
    if not context.get("system_state", {}).get("is_busy", False):
        score += 10  # 用户不忙

    return min(score, 100)


def discover_value_opportunities():
    """发现价值机会"""
    context = analyze_context()
    opportunities = []

    # 从情境分析推断需求
    inferred_needs = context.get("suggested_need", [])

    for need in inferred_needs:
        opportunity = {
            "type": need.get("type", "未知"),
            "priority": need.get("priority", 5),
            "suggestion": need.get("suggestion", ""),
            "context": context.get("time_context", ""),
            "timestamp": datetime.now().isoformat(),
            "value_score": calculate_value_score(need)
        }
        opportunities.append(opportunity)

    # 按价值分数排序
    opportunities.sort(key=lambda x: x.get("value_score", 0), reverse=True)

    # 保存发现的机会
    save_json_safe(VALUE_OPPORTUNITIES_FILE, {
        "opportunities": opportunities,
        "timestamp": datetime.now().isoformat()
    })

    return opportunities


def calculate_value_score(need):
    """计算需求价值分数"""
    priority = need.get("priority", 5)
    # 基础分数 = 优先级 * 10
    base_score = priority * 10
    # 加上一些随机因素模拟真实场景
    return min(base_score, 100)


def generate_service_recommendations(opportunities):
    """生成服务推荐"""
    recommendations = []

    for opp in opportunities[:3]:  # 最多推荐3个
        service_type = opp.get("type", "")

        # 根据机会类型生成对应的服务推荐
        if "工作" in service_type:
            recommendations.append({
                "service": "工作准备检查",
                "description": "检查今日任务列表和工作进度",
                "action": "查询任务状态或显示工作摘要",
                "priority": opp.get("priority", 5),
                "value_score": opp.get("value_score", 0)
            })
        elif "休息" in service_type or "放松" in service_type:
            recommendations.append({
                "service": "放松服务",
                "description": "播放轻松音乐或推荐视频",
                "action": "打开音乐播放器或显示娱乐建议",
                "priority": opp.get("priority", 5),
                "value_score": opp.get("value_score", 0)
            })
        elif "信息" in service_type:
            recommendations.append({
                "service": "信息整理服务",
                "description": "整理和保存搜索结果",
                "action": "提供笔记或收藏功能",
                "priority": opp.get("priority", 5),
                "value_score": opp.get("value_score", 0)
            })
        else:
            recommendations.append({
                "service": "通用助手",
                "description": "询问是否需要帮助",
                "action": "主动询问用户需求",
                "priority": opp.get("priority", 5),
                "value_score": opp.get("value_score", 0)
            })

    # 保存推荐
    save_json_safe(SERVICE_RECOMMENDATIONS_FILE, {
        "recommendations": recommendations,
        "timestamp": datetime.now().isoformat()
    })

    return recommendations


def track_service_feedback(service_name, user_accepted, feedback_text=""):
    """追踪服务反馈"""
    feedback_data = load_json_safe(SERVICE_FEEDBACK_FILE, {"feedbacks": []})

    feedback = {
        "service": service_name,
        "accepted": user_accepted,
        "feedback_text": feedback_text,
        "timestamp": datetime.now().isoformat()
    }

    feedback_data["feedbacks"].append(feedback)

    # 只保留最近100条
    if len(feedback_data["feedbacks"]) > 100:
        feedback_data["feedbacks"] = feedback_data["feedbacks"][-100:]

    save_json_safe(SERVICE_FEEDBACK_FILE, feedback_data)
    return True


def analyze_service_effectiveness():
    """分析服务效果"""
    feedback_data = load_json_safe(SERVICE_FEEDBACK_FILE, {"feedbacks": []})
    feedbacks = feedback_data.get("feedbacks", [])

    if not feedbacks:
        return {
            "total_services": 0,
            "acceptance_rate": 0,
            "top_services": []
        }

    # 统计接受率
    accepted = sum(1 for f in feedbacks if f.get("accepted", False))
    total = len(feedbacks)
    acceptance_rate = (accepted / total * 100) if total > 0 else 0

    # 统计最受欢迎的服务
    service_stats = defaultdict(lambda: {"total": 0, "accepted": 0})
    for f in feedbacks:
        service = f.get("service", "unknown")
        service_stats[service]["total"] += 1
        if f.get("accepted", False):
            service_stats[service]["accepted"] += 1

    top_services = []
    for service, stats in sorted(service_stats.items(), key=lambda x: x[1]["total"], reverse=True):
        top_services.append({
            "service": service,
            "total": stats["total"],
            "accepted": stats["accepted"],
            "acceptance_rate": (stats["accepted"] / stats["total"] * 100) if stats["total"] > 0 else 0
        })

    return {
        "total_services": total,
        "acceptance_rate": acceptance_rate,
        "top_services": top_services[:10]
    }


def auto_discover_and_suggest():
    """自动发现并建议服务"""
    # 1. 发现价值机会
    opportunities = discover_value_opportunities()

    if not opportunities:
        return {
            "status": "no_opportunities",
            "message": "当前未发现明确的主动服务机会",
            "opportunities": [],
            "recommendations": []
        }

    # 2. 生成服务推荐
    recommendations = generate_service_recommendations(opportunities)

    # 3. 构建响应
    return {
        "status": "success",
        "context_analysis": analyze_context(),
        "opportunities": opportunities,
        "recommendations": recommendations,
        "effectiveness": analyze_service_effectiveness()
    }


def interactive_discovery():
    """交互式价值发现"""
    print("=" * 60)
    print("智能主动价值发现与即时服务引擎")
    print("=" * 60)

    # 自动发现
    result = auto_discover_and_suggest()

    print(f"\n状态: {result.get('status', 'unknown')}")

    # 显示机会
    opportunities = result.get("opportunities", [])
    if opportunities:
        print(f"\n发现 {len(opportunities)} 个价值机会:")
        for i, opp in enumerate(opportunities, 1):
            print(f"  {i}. {opp.get('type', '未知')} (价值分: {opp.get('value_score', 0)})")
            print(f"     建议: {opp.get('suggestion', '')}")

    # 显示推荐
    recommendations = result.get("recommendations", [])
    if recommendations:
        print(f"\n推荐服务:")
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec.get('service', '')}")
            print(f"     描述: {rec.get('description', '')}")
            print(f"     操作: {rec.get('action', '')}")

    # 显示效果分析
    effectiveness = result.get("effectiveness", {})
    if effectiveness.get("total_services", 0) > 0:
        print(f"\n服务效果统计:")
        print(f"  总服务次数: {effectiveness.get('total_services', 0)}")
        print(f"  接受率: {effectiveness.get('acceptance_rate', 0):.1f}%")

    print("\n" + "=" * 60)

    return result


def main():
    """主入口"""
    parser = argparse.ArgumentParser(description="智能主动价值发现与即时服务引擎")
    parser.add_argument("args", nargs="*", help="位置参数")
    parser.add_argument("--discover", action="store_true", help="自动发现价值机会并推荐服务")
    parser.add_argument("--analyze", action="store_true", help="分析当前情境")
    parser.add_argument("--feedback", nargs=3, metavar=("SERVICE", "ACCEPTED", "FEEDBACK"),
                        help="提交服务反馈 (服务名 是否接受(yes/no) 反馈内容)")
    parser.add_argument("--effectiveness", action="store_true", help="分析服务效果")
    parser.add_argument("--version", action="store_true", help="显示版本")

    args = parser.parse_args()

    if args.version:
        print(f"Proactive Value Discovery Engine v{VERSION}")
        return

    # 处理位置参数（支持从 do.py 传递的参数）
    if args.args:
        first_arg = args.args[0].lower()
        if "发现" in first_arg or "discover" in first_arg or "机会" in first_arg:
            interactive_discovery()
            return
        elif "分析" in first_arg or "analyze" in first_arg:
            context = analyze_context()
            print("当前情境分析:")
            print(json.dumps(context, ensure_ascii=False, indent=2))
            return
        elif "效果" in first_arg or "effectiveness" in first_arg:
            effectiveness = analyze_service_effectiveness()
            print("服务效果分析:")
            print(json.dumps(effectiveness, ensure_ascii=False, indent=2))
            return

    if args.discover:
        interactive_discovery()
    elif args.analyze:
        context = analyze_context()
        print("当前情境分析:")
        print(json.dumps(context, ensure_ascii=False, indent=2))
    elif args.effectiveness:
        effectiveness = analyze_service_effectiveness()
        print("服务效果分析:")
        print(json.dumps(effectiveness, ensure_ascii=False, indent=2))
    else:
        # 默认显示状态
        interactive_discovery()


if __name__ == "__main__":
    main()