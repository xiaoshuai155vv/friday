#!/usr/bin/env python3
"""
进化环元学习引擎
实现一个能够分析进化历史、识别进化模式并自动调整进化策略的引擎

功能：
1. 分析历史进化数据，识别进化模式
2. 建立进化策略优化模型
3. 实现自适应进化方向推荐
4. 集成到 do.py 支持关键词触发
"""

import os
import json
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional
from collections import defaultdict

# 添加 scripts 目录到路径
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPTS_DIR)

# 状态和日志目录
PROJECT_DIR = os.path.dirname(SCRIPTS_DIR)  # 项目根目录
RUNTIME_DIR = os.path.join(PROJECT_DIR, "runtime")
STATE_DIR = os.path.join(RUNTIME_DIR, "state")
LOGS_DIR = os.path.join(RUNTIME_DIR, "logs")


def load_evolution_history() -> List[Dict[str, Any]]:
    """加载进化历史数据"""
    history_file = os.path.join(STATE_DIR, "evolution_history.json")
    if os.path.exists(history_file):
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict) and 'history' in data:
                    return data['history']
        except Exception as e:
            print(f"加载进化历史失败: {e}")

    # 尝试从其他文件加载历史
    completed_files = []
    if os.path.exists(STATE_DIR):
        for f in os.listdir(STATE_DIR):
            if f.startswith("evolution_completed_") and f.endswith(".json"):
                completed_files.append(os.path.join(STATE_DIR, f))

    history = []
    for file_path in sorted(completed_files, reverse=True)[:50]:  # 最多加载50条
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if 'loop_round' in data:
                    history.append(data)
        except Exception:
            pass

    return sorted(history, key=lambda x: x.get('loop_round', 0), reverse=True)


def analyze_evolution_patterns(history: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    分析进化模式

    识别：
    - 进化频率（每轮完成多少任务）
    - 进化类型分布（哪些类型的进化任务更常见）
    - 进化成功率（完成/未完成的比例）
    - 进化周期特征（早晨/下午/晚上进化的效果差异）
    """
    if not history:
        return {
            "patterns": [],
            "summary": "无足够历史数据进行分析"
        }

    patterns = {
        "total_evolution_rounds": len(history),
        "completed_rounds": sum(1 for h in history if h.get("是否完成") == "完成"),
        "failed_rounds": sum(1 for h in history if h.get("是否完成") == "未完成"),
    }

    # 分析进化类型分布
    evolution_types = defaultdict(int)
    for h in history:
        goal = h.get("current_goal", "")
        if "智能" in goal or "引擎" in goal:
            evolution_types["engine_creation"] += 1
        elif "增强" in goal or "优化" in goal:
            evolution_types["enhancement"] += 1
        elif "自动化" in goal or "自动" in goal:
            evolution_types["automation"] += 1
        elif "可解释" in goal or "透明" in goal:
            evolution_types["transparency"] += 1
        else:
            evolution_types["other"] += 1

    patterns["evolution_types"] = dict(evolution_types)

    # 分析成功模式
    if patterns["completed_rounds"] > 0:
        patterns["success_rate"] = patterns["completed_rounds"] / patterns["total_evolution_rounds"]

    # 识别最近的进化趋势
    recent_rounds = history[:10]  # 最近10轮
    recent_goals = [h.get("current_goal", "") for h in recent_rounds]
    patterns["recent_trends"] = recent_goals

    return patterns


def analyze_evolution_effectiveness(history: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    分析进化效果

    评估每个进化方向的效果，找出最有效的进化策略
    """
    effectiveness = {
        "by_type": defaultdict(lambda: {"total": 0, "completed": 0, "avg_round_time": 0}),
        "overall_score": 0,
        "recommendations": []
    }

    type_stats = defaultdict(lambda: {"total": 0, "completed": 0})

    for h in history:
        goal = h.get("current_goal", "")
        if "智能" in goal or "引擎" in goal:
            ev_type = "engine_creation"
        elif "增强" in goal or "优化" in goal:
            ev_type = "enhancement"
        elif "自动化" in goal or "自动" in goal:
            ev_type = "automation"
        else:
            ev_type = "other"

        type_stats[ev_type]["total"] += 1
        if h.get("是否完成") == "完成":
            type_stats[ev_type]["completed"] += 1

    # 计算各类型成功率
    for ev_type, stats in type_stats.items():
        if stats["total"] > 0:
            success_rate = stats["completed"] / stats["total"]
            effectiveness["by_type"][ev_type] = {
                "total": stats["total"],
                "completed": stats["completed"],
                "success_rate": success_rate
            }

    # 生成推荐
    if type_stats:
        best_type = max(type_stats.items(), key=lambda x: x[1]["completed"] / max(x[1]["total"], 1))
        effectiveness["recommendations"].append(
            f"最有效的进化类型是 {best_type[0]}，成功率为 {best_type[1]['completed'] / max(best_type[1]['total'], 1):.1%}"
        )
    else:
        effectiveness["recommendations"].append("暂无进化数据，无法分析进化效果")

    return effectiveness


def identify_evolution_gaps(history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    识别进化缺口

    基于历史分析，找出尚未充分探索的进化方向
    """
    # 已完成的进化类型统计
    completed_types = set()
    for h in history:
        if h.get("是否完成") == "完成":
            goal = h.get("current_goal", "")
            if "可解释" in goal:
                completed_types.add("explainability")
            if "自动化" in goal:
                completed_types.add("automation")
            if "元学习" in goal or "学习" in goal:
                completed_types.add("meta_learning")
            if "预测" in goal:
                completed_types.add("prediction")
            if "协同" in goal or "联动" in goal:
                completed_types.add("collaboration")
            if "健康" in goal or "监控" in goal:
                completed_types.add("monitoring")
            if "情感" in goal:
                completed_types.add("emotion")
            if "对话" in goal:
                completed_types.add("conversation")
            if "语音" in goal:
                completed_types.add("voice")
            if "文件" in goal:
                completed_types.add("file_management")
            if "工作流" in goal:
                completed_types.add("workflow")

    # 潜在的进化方向
    potential_directions = [
        {"direction": "多模态融合", "description": "将视觉、语音、文本等多种模态融合，提供更丰富的交互体验", "status": "未探索" if "voice" not in completed_types else "部分完成"},
        {"direction": "主动感知与预测", "description": "基于当前环境主动感知并预测用户需求", "status": "部分完成"},
        {"direction": "自我进化优化", "description": "让进化环能够自我优化进化策略，提高进化效率", "status": "未探索" if "meta_learning" not in completed_types else "部分完成"},
        {"direction": "跨场景适应", "description": "让系统能够适应不同用户场景，实现更智能的场景切换", "status": "未探索"},
    ]

    return potential_directions


def generate_meta_learning_recommendations(history: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    生成元学习推荐

    基于历史分析，生成下一轮进化建议
    """
    patterns = analyze_evolution_patterns(history)
    effectiveness = analyze_evolution_effectiveness(history)
    gaps = identify_evolution_gaps(history)

    recommendations = {
        "timestamp": datetime.now().isoformat(),
        "patterns_summary": patterns,
        "effectiveness_summary": effectiveness,
        "identified_gaps": gaps,
        "next_evolution_suggestions": []
    }

    # 基于分析生成具体建议
    if effectiveness.get("recommendations"):
        recommendations["next_evolution_suggestions"].extend(effectiveness["recommendations"])

    # 添加缺口相关的建议
    for gap in gaps[:3]:
        if gap["status"] in ["未探索", "部分完成"]:
            recommendations["next_evolution_suggestions"].append(
                f"建议探索方向：{gap['direction']} - {gap['description']}"
            )

    # 基于模式分析给出优化建议
    if patterns.get("success_rate", 0) < 0.7:
        recommendations["next_evolution_suggestions"].append(
            "进化成功率偏低，建议：1) 简化进化目标；2) 增加自校验环节；3) 降低单轮任务复杂度"
        )
    else:
        recommendations["next_evolution_suggestions"].append(
            f"进化成功率较高({patterns.get('success_rate', 0):.1%})，可以尝试更复杂的进化目标"
        )

    return recommendations


def optimize_evolution_strategy(recommendations: Dict[str, Any]) -> Dict[str, Any]:
    """
    基于元学习结果优化进化策略
    """
    optimized = {
        "strategy_version": "1.0",
        "last_updated": datetime.now().isoformat(),
        "optimizations": [],
        "applied_recommendations": []
    }

    # 分析建议并生成优化项
    suggestions = recommendations.get("next_evolution_suggestions", [])

    for suggestion in suggestions:
        if "成功率偏低" in suggestion:
            optimized["optimizations"].append({
                "type": "complexity_reduction",
                "description": "降低单轮进化复杂度，拆分大任务为小任务",
                "priority": "high"
            })
            optimized["applied_recommendations"].append(suggestion)
        elif "成功率较高" in suggestion:
            optimized["optimizations"].append({
                "type": "ambition_increase",
                "description": "可以尝试更复杂的进化目标",
                "priority": "low"
            })
            optimized["applied_recommendations"].append(suggestion)

    # 基于缺口添加优化
    gaps = recommendations.get("identified_gaps", [])
    for gap in gaps[:2]:
        if gap["status"] == "未探索":
            optimized["optimizations"].append({
                "type": "exploration",
                "direction": gap["direction"],
                "description": gap["description"],
                "priority": "medium"
            })

    return optimized


def run_meta_learning_analysis() -> Dict[str, Any]:
    """运行元学习分析"""
    print("=" * 60)
    print("进化环元学习引擎")
    print("=" * 60)

    # 加载历史数据
    print("\n[1/4] 加载进化历史数据...")
    history = load_evolution_history()
    print(f"    加载了 {len(history)} 条进化记录")

    # 分析进化模式
    print("\n[2/4] 分析进化模式...")
    patterns = analyze_evolution_patterns(history)
    print(f"    总进化轮次: {patterns.get('total_evolution_rounds', 0)}")
    print(f"    完成轮次: {patterns.get('completed_rounds', 0)}")
    print(f"    成功率: {patterns.get('success_rate', 0):.1%}")

    # 分析进化效果
    print("\n[3/4] 分析进化效果...")
    effectiveness = analyze_evolution_effectiveness(history)
    print("    各类进化成功率:")
    for ev_type, stats in effectiveness.get("by_type", {}).items():
        print(f"      - {ev_type}: {stats.get('success_rate', 0):.1%}")

    # 生成推荐
    print("\n[3/4] 生成元学习推荐...")
    recommendations = generate_meta_learning_recommendations(history)

    print("\n[4/4] 优化进化策略...")
    optimized = optimize_evolution_strategy(recommendations)

    # 保存结果
    result = {
        "timestamp": datetime.now().isoformat(),
        "history_count": len(history),
        "patterns": patterns,
        "effectiveness": effectiveness,
        "recommendations": recommendations,
        "optimized_strategy": optimized
    }

    result_file = os.path.join(STATE_DIR, "evolution_meta_learning_result.json")
    os.makedirs(STATE_DIR, exist_ok=True)
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n结果已保存到: {result_file}")

    # 打印摘要
    print("\n" + "=" * 60)
    print("元学习分析摘要")
    print("=" * 60)
    print(f"\n进化模式:")
    print(f"  - 总轮次: {patterns.get('total_evolution_rounds', 0)}")
    print(f"  - 完成率: {patterns.get('completed_rounds', 0)}/{patterns.get('total_evolution_rounds', 0)}")
    if patterns.get("success_rate"):
        print(f"  - 成功率: {patterns.get('success_rate', 0):.1%}")

    print(f"\n优化建议:")
    for opt in optimized.get("optimizations", [])[:3]:
        print(f"  - [{opt.get('priority', 'N/A').upper()}] {opt.get('description', '')}")

    return result


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="进化环元学习引擎")
    parser.add_argument("--analyze", action="store_true", help="运行元学习分析")
    parser.add_argument("--recommend", action="store_true", help="生成进化推荐")
    parser.add_argument("--optimize", action="store_true", help="优化进化策略")
    parser.add_argument("--format", choices=["json", "text"], default="text", help="输出格式")

    args = parser.parse_args()

    # 如果没有指定参数，默认运行分析
    if not any([args.analyze, args.recommend, args.optimize]):
        args.analyze = True

    if args.analyze:
        result = run_meta_learning_analysis()
    elif args.recommend:
        history = load_evolution_history()
        recommendations = generate_meta_learning_recommendations(history)
        if args.format == "json":
            print(json.dumps(recommendations, ensure_ascii=False, indent=2))
        else:
            print("\n元学习推荐:")
            for rec in recommendations.get("next_evolution_suggestions", []):
                print(f"  - {rec}")
    elif args.optimize:
        history = load_evolution_history()
        recommendations = generate_meta_learning_recommendations(history)
        optimized = optimize_evolution_strategy(recommendations)
        if args.format == "json":
            print(json.dumps(optimized, ensure_ascii=False, indent=2))
        else:
            print("\n优化后的进化策略:")
            for opt in optimized.get("optimizations", []):
                print(f"  - [{opt.get('priority', 'N/A').upper()}] {opt.get('description', '')}")


if __name__ == "__main__":
    main()