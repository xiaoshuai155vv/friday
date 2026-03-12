#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""智能情境感知引擎 - 让系统主动感知当前环境、用户状态、时间上下文，主动预测并推荐场景计划

功能：
1. 时间感知：识别当前时间段（早晨/上午/下午/晚上/深夜）、工作日/周末、特殊日期
2. 系统状态感知：当前运行的进程、活跃窗口、CPU/内存使用情况
3. 用户活动感知：基于近期用户交互历史推断当前状态
4. 场景推荐：基于感知结果主动推荐合适的场景计划

用法：
    python context_awareness_engine.py [status|perceive|recommend|full]
"""

import os
import sys
import json
import time
import datetime
import subprocess
from pathlib import Path

PROJECT = os.path.dirname(os.path.abspath(__file__))
RUNTIME_STATE = os.path.join(PROJECT, "runtime", "state")


def get_time_context():
    """获取时间上下文"""
    now = datetime.datetime.now()
    hour = now.hour

    # 时间段识别
    if 5 <= hour < 9:
        period = "morning"
        period_cn = "早晨"
    elif 9 <= hour < 12:
        period = "forenoon"
        period_cn = "上午"
    elif 12 <= hour < 14:
        period = "noon"
        period_cn = "中午"
    elif 14 <= hour < 18:
        period = "afternoon"
        period_cn = "下午"
    elif 18 <= hour < 22:
        period = "evening"
        period_cn = "晚上"
    else:
        period = "night"
        period_cn = "深夜"

    # 星期几
    weekday = now.weekday()
    is_weekend = weekday >= 5
    week_cn = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][weekday]

    return {
        "hour": hour,
        "minute": now.minute,
        "period": period,
        "period_cn": period_cn,
        "weekday": weekday,
        "week_cn": week_cn,
        "is_weekend": is_weekend,
        "date": now.strftime("%Y-%m-%d"),
        "time_str": now.strftime("%H:%M")
    }


def get_system_state():
    """获取系统状态"""
    state = {
        "running_processes": [],
        "active_windows": [],
        "cpu_usage": 0,
        "memory_usage": 0
    }

    # 获取运行进程（取前20个）
    try:
        result = subprocess.run(
            [sys.executable, os.path.join(PROJECT, "scripts", "process_tool.py"), "list"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0 and result.stdout:
            processes = result.stdout.strip().split('\n')[:20]
            state["running_processes"] = processes
    except Exception:
        pass

    # 尝试获取窗口列表
    try:
        result = subprocess.run(
            [sys.executable, os.path.join(PROJECT, "scripts", "window_tool.py"), "list"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0 and result.stdout:
            windows = result.stdout.strip().split('\n')[:10]
            state["active_windows"] = [w for w in windows if w.strip()]
    except Exception:
        pass

    return state


def get_user_activity_context():
    """获取用户活动上下文（基于近期交互历史）"""
    context = {
        "recent_intents": [],
        "last_intent": None,
        "last_task": None,
        "interaction_count_today": 0
    }

    # 读取最近的日志
    recent_logs_path = os.path.join(RUNTIME_STATE, "recent_logs.json")
    if os.path.exists(recent_logs_path):
        try:
            with open(recent_logs_path, "r", encoding="utf-8") as f:
                logs = json.load(f)
                entries = logs.get("entries", [])

                # 统计今日交互次数
                today = datetime.datetime.now().strftime("%Y-%m-%d")
                today_entries = [e for e in entries if e.get("time", "").startswith(today)]
                context["interaction_count_today"] = len(today_entries)

                # 获取最近意图
                recent = entries[-5:] if len(entries) > 5 else entries
                for entry in reversed(recent):
                    if entry.get("phase") == "track" and entry.get("desc"):
                        context["recent_intents"].append(entry["desc"])
                if context["recent_intents"]:
                    context["last_intent"] = context["recent_intents"][-1]
        except Exception:
            pass

    # 读取会话上下文
    session_ctx_path = os.path.join(RUNTIME_STATE, "session_context.json")
    if os.path.exists(session_ctx_path):
        try:
            with open(session_ctx_path, "r", encoding="utf-8") as f:
                session_ctx = json.load(f)
                context["last_task"] = session_ctx.get("last_task")
        except Exception:
            pass

    return context


def perceive_current_context():
    """感知当前完整上下文"""
    context = {
        "time": get_time_context(),
        "system": get_system_state(),
        "user_activity": get_user_activity_context(),
        "timestamp": datetime.datetime.now().isoformat()
    }
    return context


def generate_recommendations(context):
    """基于上下文生成推荐"""
    recommendations = []
    time_ctx = context["time"]
    user_ctx = context["user_activity"]
    sys_ctx = context["system"]

    period = time_ctx["period"]
    is_weekend = time_ctx["is_weekend"]

    # 基于时间段的推荐
    time_recommendations = {
        "morning": ["查看日程安排", "查看今日待办", "制定今日计划"],
        "forenoon": ["开始工作", "查看邮件", "处理工单"],
        "noon": ["休息放松", "查看午餐安排"],
        "afternoon": ["继续工作", "查看进度", "安排会议"],
        "evening": ["查看今日总结", "安排明日计划", "放松娱乐"],
        "night": ["查看消息", "准备休息", "设置明日闹钟"]
    }

    if period in time_recommendations:
        for rec in time_recommendations[period]:
            recommendations.append({
                "type": "time_based",
                "recommendation": rec,
                "reason": f"当前是{time_ctx['period_cn']}{time_ctx['time_str']}"
            })

    # 周末特殊推荐
    if is_weekend:
        recommendations.append({
            "type": "weekend",
            "recommendation": "周末适合处理个人事务",
            "reason": "今天是周末"
        })

    # 基于系统状态的推荐
    active_windows = sys_ctx.get("active_windows", [])
    if active_windows:
        # 检查是否有特定应用在运行
        window_str = " ".join(active_windows).lower()
        if "code" in window_str or "visual studio" in window_str:
            recommendations.append({
                "type": "system_state",
                "recommendation": "检测到您正在编程，是否需要创建代码相关计划？",
                "reason": "检测到开发工具运行中"
            })
        elif "chrome" in window_str or "edge" in window_str:
            recommendations.append({
                "type": "system_state",
                "recommendation": "检测到浏览器运行中，是否需要访问特定网站？",
                "reason": "检测到浏览器运行中"
            })

    # 基于用户活动的推荐
    if user_ctx.get("interaction_count_today", 0) == 0:
        recommendations.append({
            "type": "user_activity",
            "recommendation": "今天还没有交互记录，是新的一天开始！",
            "reason": "今日交互次数为0"
        })

    if user_ctx.get("last_task"):
        recommendations.append({
            "type": "user_activity",
            "recommendation": f"上次任务是：{user_ctx['last_task']}，是否继续？",
            "reason": "基于上次任务"
        })

    return recommendations


def get_context_status():
    """获取情境感知系统状态"""
    context = perceive_current_context()

    status = {
        "engine": "Context Awareness Engine",
        "status": "active",
        "current_context": {
            "time": context["time"]["period_cn"] + " " + context["time"]["time_str"],
            "date": f"{context['time']['week_cn']} {context['time']['date']}",
            "period": context["time"]["period"],
            "is_weekend": context["time"]["is_weekend"]
        },
        "system_state": {
            "process_count": len(context["system"]["running_processes"]),
            "window_count": len(context["system"]["active_windows"])
        },
        "user_activity": {
            "interactions_today": context["user_activity"]["interaction_count_today"],
            "last_intent": context["user_activity"]["last_intent"]
        },
        "timestamp": context["timestamp"]
    }

    return status


def main():
    """主函数"""
    if len(sys.argv) < 2 or sys.argv[1] in ["--help", "-h", "help"]:
        print(__doc__)
        print("\n可用命令:")
        print("  status     - 查看情境感知系统状态")
        print("  perceive   - 感知当前完整上下文")
        print("  recommend  - 基于当前上下文生成推荐")
        print("  full       - 完整报告（状态+上下文+推荐）")
        return 0

    command = sys.argv[1].lower()

    if command == "status":
        status = get_context_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))
        return 0

    elif command == "perceive":
        context = perceive_current_context()
        print(json.dumps(context, ensure_ascii=False, indent=2))
        return 0

    elif command == "recommend":
        context = perceive_current_context()
        recommendations = generate_recommendations(context)
        result = {
            "context_summary": f"当前是{context['time']['period_cn']} {context['time']['time_str']}，{context['time']['week_cn']}",
            "recommendations": recommendations,
            "count": len(recommendations)
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    elif command == "full":
        context = perceive_current_context()
        recommendations = generate_recommendations(context)
        result = {
            "status": get_context_status(),
            "full_context": context,
            "recommendations": recommendations
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    else:
        print(f"未知命令: {command}")
        print(__doc__)
        return 1


if __name__ == "__main__":
    sys.exit(main())