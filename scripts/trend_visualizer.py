#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
趋势数据可视化模块 - 将趋势预测数据以文本图表形式展示

功能：
- 生成 ASCII 趋势图表
- 展示活跃度趋势、成功率和行为模式
- 支持不同类型的可视化输出

触发方式：
  python scripts/trend_visualizer.py [--type activity|success|pattern]
  do 趋势可视化 / 可视化趋势 / 查看趋势图表
"""

import json
import os
import sys
from datetime import datetime, timedelta

# 添加项目根目录到路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, PROJECT_ROOT)

STATE_DIR = os.path.join(PROJECT_ROOT, "runtime", "state")

TREND_FILE = os.path.join(STATE_DIR, "trend_predictions.json")


def load_trend_data():
    """加载趋势预测数据"""
    if not os.path.exists(TREND_FILE):
        return None
    try:
        with open(TREND_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def create_bar_chart(data_dict, max_width=40, title=""):
    """创建水平条形图（ASCII）"""
    if not data_dict:
        return "No data"

    # 过滤并排序
    items = [(k, v) for k, v in data_dict.items() if isinstance(v, (int, float))]
    if not items:
        return "No valid data"
    items.sort(key=lambda x: x[1], reverse=True)
    items = items[:10]  # 最多显示10项

    max_val = max(v for _, v in items) if items else 1

    lines = []
    if title:
        lines.append("=" * 50)
        lines.append(title)
        lines.append("=" * 50)

    for label, value in items:
        bar_len = int((value / max_val) * max_width) if max_val > 0 else 0
        bar = "#" * bar_len
        lines.append(f"{label:30s} |{bar} {value}")

    return "\n".join(lines)


def visualize_activity_trend(data):
    """可视化活跃度趋势"""
    ts = data.get("time_series", {})
    trend = ts.get("trend", "unknown")
    change_rate = ts.get("change_rate", 0)

    lines = []
    lines.append("\n" + "=" * 50)
    lines.append("ACTIVITY TREND ANALYSIS")
    lines.append("=" * 50)

    # 趋势指示器
    trend_symbol = {
        "up": ">",
        "down": "<",
        "stable": "-"
    }
    symbol = trend_symbol.get(trend, "?")

    lines.append(f"\nCurrent trend: {symbol} {trend.upper()}")
    lines.append(f"Change rate: {change_rate:+.1f}%")

    # 每日统计图表
    daily_stats = ts.get("daily_stats", {})
    if daily_stats:
        # 取最近7天
        sorted_days = sorted(daily_stats.keys(), reverse=True)[:7]
        day_data = {day: daily_stats[day].get("total", 0) for day in sorted_days}

        lines.append("\nActivity in last 7 days:")
        max_val = max(day_data.values()) if day_data else 1
        chart_width = 30

        for day in sorted_days:
            count = day_data[day]
            bar_len = int((count / max_val) * chart_width) if max_val > 0 else 0
            bar = "*" * bar_len
            lines.append(f"  {day[-5:]} |{bar} {count}")

    return "\n".join(lines)


def visualize_success_rate(data):
    """可视化成功率趋势"""
    st = data.get("success_trend", {})

    lines = []
    lines.append("\n" + "=" * 50)
    lines.append("TASK SUCCESS RATE")
    lines.append("=" * 50)

    success_rate = st.get("success_rate", 0)
    total = st.get("total_verified", 0)
    passed = st.get("passed", 0)
    failed = st.get("failed", 0)

    # 成功率仪表盘
    lines.append(f"\nSuccess Rate: {success_rate:.1f}%")
    gauge_len = 30
    filled = int((success_rate / 100) * gauge_len)
    gauge = "#" * filled + "." * (gauge_len - filled)
    lines.append(f"  [{gauge}]")

    # 详细统计
    lines.append(f"\nTotal verifications: {total}")
    lines.append(f"  Passed: {passed}  |  Failed: {failed}")

    # 预测信息
    predictions = data.get("predictions", [])
    for pred in predictions:
        if pred.get("type") == "success_rate":
            lines.append(f"\nPrediction: {pred.get('prediction', '')}")
            lines.append(f"Confidence: {pred.get('confidence', '')}")

    return "\n".join(lines)


def visualize_behavior_patterns(data):
    """可视化行为模式"""
    bp = data.get("behavior_patterns", {})

    lines = []
    lines.append("\n" + "=" * 50)
    lines.append("BEHAVIOR PATTERNS")
    lines.append("=" * 50)

    # 最常见阶段
    phases = bp.get("most_common_phases", [])
    if phases:
        lines.append("\nMost Common Phases (Top 5):")
        for i, p in enumerate(phases[:5], 1):
            lines.append(f"  {i}. {p.get('phase', '')}: {p.get('count', 0)} times")

    # 步骤类型分布
    step_types = bp.get("step_types", {})
    # 过滤掉非步骤类型
    step_items = {k: v for k, v in step_types.items()
                  if not k.startswith("step ") and k not in ["assume", "plan", "track", "verify", "decide"]}
    if step_items:
        lines.append(create_bar_chart(step_items, title="Step Type Distribution"))

    # 高频任务
    top_missions = bp.get("top_missions", [])
    if top_missions:
        lines.append("\nHigh Frequency Missions (Top 5):")
        for i, m in enumerate(top_missions[:5], 1):
            lines.append(f"  {i}. {m.get('mission', '')}: {m.get('count', 0)} times")

    return "\n".join(lines)


def visualize_all():
    """完整可视化"""
    data = load_trend_data()
    if not data:
        return "No trend data. Please run 'trend analysis' first."

    lines = []
    lines.append("\n" + "=" * 60)
    lines.append("FRI DAY - TRENDS VISUALIZATION REPORT")
    lines.append(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("=" * 60)

    lines.append(visualize_activity_trend(data))
    lines.append(visualize_success_rate(data))
    lines.append(visualize_behavior_patterns(data))

    lines.append("\n" + "=" * 60)
    lines.append("TIP: Use 'do set alert' to configure anomaly thresholds")
    lines.append("=" * 60)

    return "\n".join(lines)


def main():
    import argparse
    ap = argparse.ArgumentParser(description="Trend Data Visualization")
    ap.add_argument("--type", choices=["activity", "success", "pattern", "all"],
                    default="all", help="Visualization type")
    args = ap.parse_args()

    data = load_trend_data()
    if not data:
        print("No trend data. Please run 'trend analysis' first.")
        return

    if args.type == "activity":
        print(visualize_activity_trend(data))
    elif args.type == "success":
        print(visualize_success_rate(data))
    elif args.type == "pattern":
        print(visualize_behavior_patterns(data))
    else:
        print(visualize_all())


if __name__ == "__main__":
    main()