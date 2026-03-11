#!/usr/bin/env python3
"""
趋势分析与预测模块

基于日志分析模块扩展时间序列趋势分析、任务执行成功率预测、行为模式发现
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

PROJECT_ROOT = Path(__file__).parent.parent
RUNTIME_STATE = PROJECT_ROOT / "runtime" / "state"
RUNTIME_LOGS = PROJECT_ROOT / "runtime" / "logs"


def load_execution_analysis():
    """加载执行分析数据"""
    analysis_file = RUNTIME_STATE / "execution_analysis.json"
    if analysis_file.exists():
        with open(analysis_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def load_behavior_logs(days=30):
    """加载最近 N 天的行为日志"""
    logs = []
    today = datetime.now()

    for i in range(days):
        date = (today - timedelta(days=i)).strftime("%Y-%m-%d")
        log_file = RUNTIME_LOGS / f"behavior_{date}.log"
        if log_file.exists():
            try:
                with open(log_file, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            # 解析 TSV 格式: time\tphase\tdesc\tmission=...\ttask_id=...\tresult=...
                            parts = line.split("\t")
                            if len(parts) >= 3:
                                log_entry = {
                                    "time": parts[0],
                                    "phase": parts[1],
                                    "desc": parts[2]
                                }
                                # 解析额外字段
                                for part in parts[3:]:
                                    if part.startswith("mission="):
                                        log_entry["mission"] = part.replace("mission=", "")
                                    elif part.startswith("result="):
                                        log_entry["result"] = part.replace("result=", "")
                                    elif part.startswith("task_id="):
                                        log_entry["task_id"] = part.replace("task_id=", "")
                                logs.append(log_entry)
            except Exception as e:
                print(f"Warning: Failed to read {log_file}: {e}")

    return logs


def analyze_time_series(logs):
    """分析时间序列趋势"""
    # 按日期分组
    daily_stats = defaultdict(lambda: {"total": 0, "phase_counts": defaultdict(int)})

    for log in logs:
        if "time" in log:
            try:
                log_time = datetime.fromisoformat(log["time"].replace("Z", "+00:00"))
                date = log_time.strftime("%Y-%m-%d")
                daily_stats[date]["total"] += 1

                phase = log.get("phase", "unknown")
                daily_stats[date]["phase_counts"][phase] += 1
            except:
                pass

    # 计算趋势
    dates = sorted(daily_stats.keys())
    if len(dates) < 2:
        return {"trend": "insufficient_data", "daily_stats": daily_stats}

    # 计算环比变化
    recent = sum(daily_stats[d]["total"] for d in dates[-7:] if d in daily_stats)
    previous = sum(daily_stats[d]["total"] for d in dates[-14:-7] if d in daily_stats)

    if previous > 0:
        change_rate = (recent - previous) / previous * 100
    else:
        change_rate = 0

    # 判断趋势方向
    if change_rate > 10:
        trend = "increasing"
    elif change_rate < -10:
        trend = "decreasing"
    else:
        trend = "stable"

    return {
        "trend": trend,
        "change_rate": round(change_rate, 2),
        "recent_week_total": recent,
        "previous_week_total": previous,
        "daily_stats": dict(daily_stats)
    }


def analyze_phase_distribution(logs):
    """分析阶段分布趋势"""
    phase_counts = defaultdict(int)

    for log in logs:
        phase = log.get("phase", "unknown")
        phase_counts[phase] += 1

    total = len(logs)
    if total == 0:
        return {}

    phase_distribution = {
        phase: {
            "count": count,
            "percentage": round(count / total * 100, 2)
        }
        for phase, count in phase_counts.items()
    }

    return phase_distribution


def analyze_task_success_trend(logs):
    """分析任务执行成功率趋势"""
    # 统计 verify 阶段的结果
    verify_logs = [log for log in logs if log.get("phase") == "verify"]

    results = {"pass": 0, "fail": 0, "unknown": 0}
    for log in verify_logs:
        result = log.get("result", "unknown")
        if result == "pass":
            results["pass"] += 1
        elif result == "fail":
            results["fail"] += 1
        else:
            results["unknown"] += 1

    total = results["pass"] + results["fail"]
    if total > 0:
        success_rate = results["pass"] / total * 100
    else:
        success_rate = 0

    return {
        "success_rate": round(success_rate, 2),
        "total_verified": total,
        "passed": results["pass"],
        "failed": results["fail"],
        "unknown": results["unknown"]
    }


def analyze_behavior_patterns(logs):
    """分析行为模式"""
    patterns = {
        "most_common_phases": [],
        "common_missions": defaultdict(int),
        "step_types": defaultdict(int)
    }

    for log in logs:
        # 记录 mission
        mission = log.get("mission", "unknown")
        patterns["common_missions"][mission] += 1

        # 记录 phase
        phase = log.get("phase", "unknown")
        patterns["step_types"][phase] += 1

    # 排序并取前 5
    patterns["most_common_phases"] = sorted(
        patterns["step_types"].items(),
        key=lambda x: x[1],
        reverse=True
    )[:5]

    # 取最常见的 mission
    patterns["top_missions"] = sorted(
        patterns["common_missions"].items(),
        key=lambda x: x[1],
        reverse=True
    )[:5]

    # 转换为可序列化格式
    patterns["most_common_phases"] = [
        {"phase": p[0], "count": p[1]} for p in patterns["most_common_phases"]
    ]
    patterns["top_missions"] = [
        {"mission": m[0], "count": m[1]} for m in patterns["top_missions"]
    ]

    return patterns


def predict_execution_trend(time_series, success_trend):
    """预测执行趋势"""
    predictions = []

    # 基于时间序列趋势预测
    if time_series.get("trend") == "increasing":
        predictions.append({
            "type": "activity",
            "prediction": "系统活跃度正在上升",
            "confidence": "high",
            "detail": f"最近7天执行次数比上周增长 {time_series.get('change_rate', 0)}%"
        })
    elif time_series.get("trend") == "decreasing":
        predictions.append({
            "type": "activity",
            "prediction": "系统活跃度正在下降",
            "confidence": "medium",
            "detail": f"最近7天执行次数比上周下降 {abs(time_series.get('change_rate', 0))}%"
        })
    else:
        predictions.append({
            "type": "activity",
            "prediction": "系统活跃度保持稳定",
            "confidence": "high",
            "detail": "执行次数变化在正常范围内"
        })

    # 基于成功率趋势预测
    success_rate = success_trend.get("success_rate", 0)
    if success_rate >= 90:
        predictions.append({
            "type": "success_rate",
            "prediction": "执行成功率很高",
            "confidence": "high",
            "detail": f"当前成功率 {success_rate}%，系统运行良好"
        })
    elif success_rate >= 70:
        predictions.append({
            "type": "success_rate",
            "prediction": "执行成功率一般",
            "confidence": "medium",
            "detail": f"当前成功率 {success_rate}%，建议关注失败案例"
        })
    else:
        predictions.append({
            "type": "success_rate",
            "prediction": "执行成功率较低",
            "confidence": "high",
            "detail": f"当前成功率仅 {success_rate}%，需要检查问题原因"
        })

    return predictions


def generate_trend_report():
    """生成趋势分析报告"""
    # 加载数据
    execution_analysis = load_execution_analysis()
    logs = load_behavior_logs(30)

    if not logs:
        return {
            "error": "No logs available for analysis",
            "timestamp": datetime.now().isoformat()
        }

    # 分析
    time_series = analyze_time_series(logs)
    phase_dist = analyze_phase_distribution(logs)
    success_trend = analyze_task_success_trend(logs)
    behavior_patterns = analyze_behavior_patterns(logs)

    # 预测
    predictions = predict_execution_trend(time_series, success_trend)

    # 构建报告
    report = {
        "timestamp": datetime.now().isoformat(),
        "analysis_period_days": 30,
        "total_logs": len(logs),
        "time_series": time_series,
        "phase_distribution": phase_dist,
        "success_trend": success_trend,
        "behavior_patterns": behavior_patterns,
        "predictions": predictions,
        "execution_analysis_summary": execution_analysis.get("summary", {}) if execution_analysis else {}
    }

    # 保存报告
    output_file = RUNTIME_STATE / "trend_predictions.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    return report


def main():
    """主函数"""
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("""
趋势分析与预测模块

用法: python trend_predictor.py

基于日志分析模块扩展时间序列趋势分析、任务执行成功率预测、行为模式发现

输出文件: runtime/state/trend_predictions.json
        """)
        return

    report = generate_trend_report()

    if "error" in report:
        print(f"Error: {report['error']}")
        sys.exit(1)

    print(f"趋势分析报告生成完成")
    print(f"分析日志数: {report['total_logs']}")
    print(f"活跃度趋势: {report['time_series'].get('trend', 'unknown')}")
    print(f"成功率: {report['success_trend'].get('success_rate', 0)}%")
    print(f"预测数: {len(report['predictions'])}")
    print(f"详细报告: {RUNTIME_STATE / 'trend_predictions.json'}")


if __name__ == "__main__":
    main()