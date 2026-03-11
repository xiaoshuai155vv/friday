#!/usr/bin/env python3
"""
任务执行日志分析器
分析行为日志，生成执行统计和可视化报告，帮助理解系统行为模式并发现潜在改进点
"""

import json
import os
import sys
from datetime import datetime, timedelta
from collections import Counter, defaultdict
import glob

# 添加项目根目录到路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, PROJECT_ROOT)


def get_log_files(days=7):
    """获取最近N天的日志文件"""
    log_dir = os.path.join(PROJECT_ROOT, "runtime", "logs")
    pattern = os.path.join(log_dir, "behavior_*.log")
    files = sorted(glob.glob(pattern), reverse=True)
    return files[:days]


def parse_log_line(line):
    """解析单行日志"""
    parts = line.strip().split('\t')
    if len(parts) < 3:
        return None

    log_entry = {
        "timestamp": parts[0],
        "type": parts[1],
        "content": parts[2] if len(parts) > 2 else "",
    }

    # 解析 mission
    for part in parts[3:]:
        if part.startswith("mission="):
            log_entry["mission"] = part.replace("mission=", "")

    return log_entry


def analyze_log_files(files):
    """分析日志文件"""
    all_entries = []

    for filepath in files:
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    entry = parse_log_line(line)
                    if entry:
                        all_entries.append(entry)
        except Exception as e:
            print(f"Error reading {filepath}: {e}")

    return all_entries


def calculate_statistics(entries):
    """计算统计数据"""
    stats = {
        "total_entries": len(entries),
        "by_type": Counter(),
        "by_mission": Counter(),
        "success_count": 0,
        "fail_count": 0,
        "steps_by_type": Counter(),
        "missions": defaultdict(lambda: {"steps": 0, "success": 0, "fail": 0})
    }

    for entry in entries:
        log_type = entry.get("type", "unknown")
        stats["by_type"][log_type] += 1

        # 统计 mission
        mission = entry.get("mission", "unknown")
        stats["by_mission"][mission] += 1

        # 统计成功/失败
        if log_type == "verify":
            content = entry.get("content", "").lower()
            if "pass" in content or "ok" in content:
                stats["success_count"] += 1
                stats["missions"][mission]["success"] += 1
            else:
                stats["fail_count"] += 1
                stats["missions"][mission]["fail"] += 1

        # 统计步骤类型
        if log_type.startswith("step ") and ":" in log_type:
            step_type = log_type.split(":")[-1].strip()
            stats["steps_by_type"][step_type] += 1
            stats["missions"][mission]["steps"] += 1

    return stats


def generate_summary(stats):
    """生成摘要报告"""
    summary = {
        "report_time": datetime.now().isoformat(),
        "overview": {
            "total_entries": stats["total_entries"],
            "total_verifications": stats["success_count"] + stats["fail_count"],
            "success_rate": round(stats["success_count"] / (stats["success_count"] + stats["fail_count"]) * 100, 1)
                if (stats["success_count"] + stats["fail_count"]) > 0 else 0
        },
        "log_type_distribution": dict(stats["by_type"].most_common(10)),
        "top_missions": dict(stats["by_mission"].most_common(10)),
        "step_type_distribution": dict(stats["steps_by_type"].most_common(10)),
        "mission_performance": {}
    }

    # 添加每个任务的性能统计
    for mission, data in stats["missions"].items():
        if data["steps"] > 0:
            total = data["success"] + data["fail"]
            summary["mission_performance"][mission] = {
                "steps": data["steps"],
                "success": data["success"],
                "fail": data["fail"],
                "success_rate": round(data["success"] / total * 100, 1) if total > 0 else 0
            }

    return summary


def generate_insights(stats, summary):
    """生成分析洞察"""
    insights = []

    # 分析成功率
    if summary["overview"]["success_rate"] > 90:
        insights.append({
            "type": "positive",
            "message": f"系统整体成功率较高 ({summary['overview']['success_rate']}%)，运行稳定"
        })
    elif summary["overview"]["success_rate"] < 70:
        insights.append({
            "type": "warning",
            "message": f"系统成功率偏低 ({summary['overview']['success_rate']}%)，需关注失败原因"
        })

    # 分析高频步骤类型
    if stats["steps_by_type"]:
        top_step = stats["steps_by_type"].most_common(1)[0]
        insights.append({
            "type": "info",
            "message": f"最常用的步骤类型: {top_step[0]} ({top_step[1]} 次)"
        })

    # 分析高频任务
    if stats["by_mission"]:
        top_mission = stats["by_mission"].most_common(1)[0]
        insights.append({
            "type": "info",
            "message": f"最常见的任务: {top_mission[0]} ({top_mission[1]} 次)"
        })

    # 查找失败率高的任务
    for mission, perf in summary["mission_performance"].items():
        if perf["fail"] > 0 and perf["success_rate"] < 50:
            insights.append({
                "type": "warning",
                "message": f"任务 '{mission}' 失败率较高 ({perf['success_rate']}% 成功率, {perf['fail']} 次失败)"
            })

    return insights


def main():
    """主函数"""
    # 设置输出编码
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')

    print("=" * 60)
    print("任务执行日志分析器")
    print("=" * 60)

    # 获取最近7天的日志
    log_files = get_log_files(days=7)
    print(f"\n分析最近 {len(log_files)} 个日志文件...")

    if not log_files:
        print("未找到日志文件")
        return 1

    # 分析日志
    entries = analyze_log_files(log_files)
    print(f"共解析 {len(entries)} 条日志记录")

    # 计算统计
    stats = calculate_statistics(entries)

    # 生成摘要
    summary = generate_summary(stats)

    # 生成洞察
    insights = generate_insights(stats, summary)

    # 输出报告
    print("\n" + "=" * 60)
    print("概览")
    print("=" * 60)
    print(f"总日志条数: {summary['overview']['total_entries']}")
    print(f"总验证次数: {summary['overview']['total_verifications']}")
    print(f"成功率: {summary['overview']['success_rate']}%")

    print("\n" + "-" * 40)
    print("日志类型分布")
    print("-" * 40)
    for log_type, count in summary["log_type_distribution"].items():
        print(f"  {log_type}: {count}")

    print("\n" + "-" * 40)
    print("步骤类型分布")
    print("-" * 40)
    for step_type, count in summary["step_type_distribution"].items():
        print(f"  {step_type}: {count}")

    print("\n" + "-" * 40)
    print("分析洞察")
    print("-" * 40)
    for insight in insights:
        icon = {
            "positive": "[OK]",
            "warning": "[WARN]",
            "info": "[INFO]"
        }.get(insight["type"], "[--]")
        print(f"  {icon} {insight['message']}")

    # 保存报告
    report_path = os.path.join(PROJECT_ROOT, "runtime", "state", "execution_analysis.json")
    os.makedirs(os.path.dirname(report_path), exist_ok=True)

    report = {
        "summary": summary,
        "insights": insights,
        "generated_at": datetime.now().isoformat()
    }

    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\n报告已保存到: {report_path}")
    print("\n" + "=" * 60)
    print("分析完成")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())