#!/usr/bin/env python3
"""
进化日志分析模块
用于分析进化环的日志，生成进化过程图表和报告
"""

import os
import json
import re
from datetime import datetime
from collections import defaultdict, Counter
from typing import Dict, List, Any

def analyze_evolution_logs(log_dir: str = "runtime/logs") -> Dict[str, Any]:
    """
    分析进化日志文件，生成进化过程分析报告

    Args:
        log_dir: 日志目录路径

    Returns:
        分析结果字典
    """
    # 存储分析结果
    analysis = {
        "summary": {},
        "by_round": {},
        "by_phase": {},
        "by_action": {},
        "timeline": [],
        "trends": {}
    }

    # 统计各个阶段和动作的数量
    phase_counts = Counter()
    action_counts = Counter()
    round_goals = {}

    # 读取所有日志文件
    log_files = []
    for filename in os.listdir(log_dir):
        if filename.startswith("behavior_") and filename.endswith(".log"):
            log_files.append(os.path.join(log_dir, filename))

    # 按时间排序
    log_files.sort()

    # 分析每个日志文件
    for log_file in log_files:
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # 解析每行日志
        for line in lines:
            if not line.strip():
                continue

            # 解析日志行格式：timestamp\taction\tmessage\tmission=xxx\t...
            parts = line.strip().split('\t')
            if len(parts) >= 4:
                timestamp_str = parts[0]
                action = parts[1]
                message = parts[2]
                mission = None
                task_id = None

                # 提取mission和task_id信息
                for part in parts[3:]:
                    if part.startswith('mission='):
                        mission = part.split('=', 1)[1]
                    elif part.startswith('task_id='):
                        task_id = part.split('=', 1)[1]

                # 提取轮次编号
                round_num = None
                if mission and "Round" in mission:
                    match = re.search(r'Round (\d+)', mission)
                    if match:
                        round_num = int(match.group(1))

                # 如果有轮次信息，记录该轮次的活动
                if round_num is not None:
                    if round_num not in analysis["by_round"]:
                        analysis["by_round"][round_num] = {
                            "actions": [],
                            "phases": [],
                            "goals": [],
                            "timestamp": timestamp_str
                        }

                    analysis["by_round"][round_num]["actions"].append(action)
                    analysis["by_round"][round_num]["phases"].append(action)
                    analysis["by_round"][round_num]["timestamp"] = timestamp_str

                    # 记录目标
                    if "plan" in action and message:
                        analysis["by_round"][round_num]["goals"].append(message)
                        round_goals[round_num] = message

                    # 更新全局统计
                    phase_counts[action] += 1
                    action_counts[action] += 1

                    # 添加时间线数据
                    analysis["timeline"].append({
                        "round": round_num,
                        "action": action,
                        "message": message,
                        "timestamp": timestamp_str,
                        "mission": mission
                    })

    # 计算摘要信息
    total_rounds = len(analysis["by_round"])
    analysis["summary"] = {
        "total_rounds": total_rounds,
        "total_actions": len(analysis["timeline"]),
        "phases": dict(phase_counts),
        "actions": dict(action_counts),
        "first_round": min(analysis["by_round"].keys()) if analysis["by_round"] else None,
        "last_round": max(analysis["by_round"].keys()) if analysis["by_round"] else None,
        "rounds_with_goals": len([r for r, data in analysis["by_round"].items() if data["goals"]])
    }

    # 生成趋势分析
    if analysis["timeline"]:
        # 按轮次分组统计
        rounds_data = defaultdict(list)
        for item in analysis["timeline"]:
            rounds_data[item["round"]].append(item["action"])

        # 计算每轮的行动数量
        round_counts = [(round_num, len(actions)) for round_num, actions in rounds_data.items()]
        round_counts.sort()

        analysis["trends"] = {
            "round_action_counts": round_counts,
            "average_actions_per_round": len(analysis["timeline"]) / total_rounds if total_rounds > 0 else 0
        }

    return analysis

def generate_visualization(analysis: Dict[str, Any], output_dir: str = "runtime/state"):
    """
    生成进化过程可视化图表（如果可用）

    Args:
        analysis: 分析结果
        output_dir: 输出目录
    """
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)

    # 如果没有matplotlib，跳过图像生成
    try:
        import matplotlib.pyplot as plt
        # 如果有趋势数据，绘制图表
        if "trends" in analysis and analysis["trends"]["round_action_counts"]:
            rounds, action_counts = zip(*analysis["trends"]["round_action_counts"])

            # 创建图表
            plt.figure(figsize=(12, 6))
            plt.plot(rounds, action_counts, marker='o', linestyle='-', linewidth=2, markersize=6)
            plt.xlabel('进化轮次')
            plt.ylabel('每轮行动数量')
            plt.title('进化过程行动趋势')
            plt.grid(True, alpha=0.3)

            # 保存图表
            output_path = os.path.join(output_dir, "evolution_trend.png")
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()

            return output_path
    except ImportError:
        # 如果没有matplotlib，返回None表示跳过图像生成
        return None

    return None

def save_analysis_to_json(analysis: Dict[str, Any], output_path: str = "runtime/state/evolution_analysis.json"):
    """
    将分析结果保存到JSON文件

    Args:
        analysis: 分析结果
        output_path: 输出文件路径
    """
    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # 添加分析时间戳
    analysis["analysis_timestamp"] = datetime.now().isoformat()

    # 写入JSON文件
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)

def main():
    """主函数"""
    try:
        # 分析进化日志
        print("正在分析进化日志...")
        analysis = analyze_evolution_logs()

        # 保存分析结果
        print("保存分析结果...")
        save_analysis_to_json(analysis)

        # 生成可视化图表
        print("生成可视化图表...")
        chart_path = generate_visualization(analysis)

        # 输出结果摘要
        print("\n=== 进化日志分析摘要 ===")
        print(f"总轮次: {analysis['summary']['total_rounds']}")
        print(f"总行动数: {analysis['summary']['total_actions']}")
        print(f"首次轮次: {analysis['summary']['first_round']}")
        print(f"最后轮次: {analysis['summary']['last_round']}")
        print(f"有目标的轮次: {analysis['summary']['rounds_with_goals']}")

        if chart_path:
            print(f"图表已保存到: {chart_path}")
        else:
            print("未生成图表（数据不足或缺少依赖）")

        print("分析完成!")

    except Exception as e:
        print(f"分析过程中发生错误: {str(e)}")
        raise

if __name__ == "__main__":
    main()