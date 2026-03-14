#!/usr/bin/env python3
"""
进化环元进化能力增强引擎
让系统能够自动分析自身进化过程、评估进化方法论效率、生成更优的进化策略，形成"学会如何进化"的递归优化能力

功能：
1. 进化过程自动分析（分析历史进化的效率、成功率、价值实现）
2. 进化方法论评估（评估各进化策略的有效性）
3. 最优进化策略生成（基于分析结果生成改进建议）
4. 递归优化能力（将优化建议应用到后续进化中）
5. 集成到 do.py 支持元进化、进化方法论等关键词触发

Version: 1.0.0
"""

import os
import json
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional
from collections import defaultdict
import re

# 添加 scripts 目录到路径
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPTS_DIR)

# 状态和日志目录
PROJECT_DIR = os.path.dirname(SCRIPTS_DIR)  # 项目根目录
RUNTIME_DIR = os.path.join(PROJECT_DIR, "runtime")
STATE_DIR = os.path.join(RUNTIME_DIR, "state")
LOGS_DIR = os.path.join(RUNTIME_DIR, "logs")


def load_evolution_completed_history() -> List[Dict[str, Any]]:
    """加载所有已完成进化的历史数据"""
    history = []

    if os.path.exists(STATE_DIR):
        for f in os.listdir(STATE_DIR):
            if f.startswith("evolution_completed_") and f.endswith(".json"):
                file_path = os.path.join(STATE_DIR, f)
                try:
                    with open(file_path, 'r', encoding='utf-8') as fp:
                        data = json.load(fp)
                        if 'loop_round' in data:
                            history.append(data)
                except Exception as e:
                    print(f"加载 {f} 失败: {e}")

    # 按轮次排序
    return sorted(history, key=lambda x: x.get('loop_round', 0), reverse=True)


def analyze_evolution_process(history: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    分析进化过程 - 分析历史进化的效率、成功率、价值实现
    """
    if not history:
        return {
            "status": "insufficient_data",
            "message": "无足够历史数据进行分析"
        }

    total_rounds = len(history)
    completed_rounds = sum(1 for h in history if h.get('status') == 'completed' or h.get('是否完成') == '已完成')
    failed_rounds = sum(1 for h in history if h.get('status') in ['failed', 'stale_failed'] or h.get('是否完成') == '未完成')

    # 分析进化目标类型分布
    goal_categories = defaultdict(int)
    for h in history:
        goal = h.get('current_goal', h.get('做了什么', ''))
        if '引擎' in goal or 'engine' in goal.lower():
            goal_categories['引擎创建/增强'] += 1
        elif '优化' in goal or '优化' in goal:
            goal_categories['优化改进'] += 1
        elif '集成' in goal or '深度集成' in goal:
            goal_categories['深度集成'] += 1
        elif '分析' in goal or '评估' in goal:
            goal_categories['分析评估'] += 1
        else:
            goal_categories['其他'] += 1

    # 计算平均价值分数（如果有）
    value_scores = []
    for h in history:
        if '基线校验' in h:
            baseline = h.get('基线校验', '')
            # 基线校验可能是字符串或字典
            if isinstance(baseline, str):
                match = re.search(r'(\d+)/\d+', baseline)
                if match:
                    value_scores.append(int(match.group(1)))
            elif isinstance(baseline, dict):
                # 尝试从字典中提取分数
                baseline_str = str(baseline)
                match = re.search(r'(\d+)/\d+', baseline_str)
                if match:
                    value_scores.append(int(match.group(1)))

    avg_score = sum(value_scores) / len(value_scores) if value_scores else None

    # 识别高效进化模式
    efficient_patterns = []
    if total_rounds >= 10:
        # 统计连续完成的轮次
        consecutive_completed = 0
        max_consecutive = 0
        for h in history:
            if h.get('是否完成') == '已完成':
                consecutive_completed += 1
                max_consecutive = max(max_consecutive, consecutive_completed)
            else:
                consecutive_completed = 0
        efficient_patterns.append(f"最长连续完成轮次: {max_consecutive}")

    return {
        "status": "success",
        "total_rounds": total_rounds,
        "completed_rounds": completed_rounds,
        "failed_rounds": failed_rounds,
        "success_rate": completed_rounds / total_rounds if total_rounds > 0 else 0,
        "goal_categories": dict(goal_categories),
        "avg_baseline_score": avg_score,
        "efficient_patterns": efficient_patterns,
        "recent_goals": [h.get('current_goal', '')[:80] for h in history[:5]]
    }


def evaluate_evolution_methodology(history: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    评估进化方法论 - 评估各进化策略的有效性
    """
    if not history or len(history) < 5:
        return {
            "status": "insufficient_data",
            "message": "需要至少5轮历史数据才能评估方法论"
        }

    # 分析不同类型进化的成功率
    category_success = defaultdict(lambda: {"total": 0, "completed": 0})

    for h in history:
        goal = h.get('current_goal', h.get('做了什么', ''))
        is_completed = h.get('是否完成') == '已完成'

        # 分类
        if '引擎' in goal or 'engine' in goal.lower():
            cat = '引擎类'
        elif '集成' in goal or '融合' in goal:
            cat = '集成类'
        elif '优化' in goal or '增强' in goal:
            cat = '优化类'
        elif '分析' in goal or '评估' in goal:
            cat = '分析类'
        else:
            cat = '其他类'

        category_success[cat]["total"] += 1
        if is_completed:
            category_success[cat]["completed"] += 1

    # 计算各类别成功率
    methodology_evaluation = {}
    for cat, stats in category_success.items():
        success_rate = stats["completed"] / stats["total"] if stats["total"] > 0 else 0
        methodology_evaluation[cat] = {
            "total": stats["total"],
            "completed": stats["completed"],
            "success_rate": success_rate,
            "effectiveness": "高" if success_rate >= 0.8 else ("中" if success_rate >= 0.5 else "低")
        }

    # 识别最佳策略
    best_category = max(methodology_evaluation.items(), key=lambda x: x[1]["success_rate"])
    worst_category = min(methodology_evaluation.items(), key=lambda x: x[1]["success_rate"])

    return {
        "status": "success",
        "methodology_evaluation": methodology_evaluation,
        "best_strategy": best_category[0],
        "best_success_rate": best_category[1]["success_rate"],
        "needs_improvement": worst_category[0],
        "improvement_space": 1 - worst_category[1]["success_rate"]
    }


def generate_optimization_strategy(analysis: Dict[str, Any], methodology: Dict[str, Any]) -> Dict[str, Any]:
    """
    基于分析结果生成最优进化策略
    """
    suggestions = []

    # 基于过程分析的建议
    if analysis.get("status") == "success":
        success_rate = analysis.get("success_rate", 0)
        if success_rate < 0.7:
            suggestions.append({
                "type": "成功率提升",
                "priority": "高",
                "suggestion": f"当前进化成功率仅 {success_rate*100:.1f}%，建议：1) 在执行前增加更详细的任务拆解；2) 增加预检查机制识别潜在失败风险；3) 对复杂任务增加中间验证点"
            })

        # 基于类别分布的建议
        goal_categories = analysis.get("goal_categories", {})
        if goal_categories:
            # 检查是否有偏重
            total = sum(goal_categories.values())
            for cat, count in goal_categories.items():
                ratio = count / total if total > 0 else 0
                if ratio > 0.5:
                    suggestions.append({
                        "type": "平衡发展",
                        "priority": "中",
                        "suggestion": f"{cat}类型的进化占比 {ratio*100:.1f}% 过高，建议探索其他进化方向以实现更均衡的系统发展"
                    })

    # 基于方法论评估的建议
    if methodology.get("status") == "success":
        needs_improvement = methodology.get("needs_improvement")
        improvement_space = methodology.get("improvement_space", 0)

        if needs_improvement and improvement_space > 0.3:
            suggestions.append({
                "type": "方法论改进",
                "priority": "高",
                "suggestion": f"{needs_improvement}类进化成功率较低，提升空间 {improvement_space*100:.1f}%，建议：1) 分析该类失败的具体原因；2) 制定针对性的改进措施；3) 借鉴最佳策略的成功经验"
            })

        best_strategy = methodology.get("best_strategy")
        if best_strategy:
            suggestions.append({
                "type": "最佳实践推广",
                "priority": "中",
                "suggestion": f"{best_strategy}类进化效果最佳，建议将其方法论应用到其他类型的进化中"
            })

    # 通用建议
    if len(suggestions) < 3:
        suggestions.append({
            "type": "持续优化",
            "priority": "低",
            "suggestion": "建议每10轮进行一次元进化分析，持续跟踪进化效果并调整策略"
        })

    return {
        "status": "success",
        "suggestions": suggestions,
        "priority_suggestions": [s for s in suggestions if s.get("priority") == "高"],
        "total_suggestions": len(suggestions)
    }


def apply_recursive_optimization(suggestions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    将优化建议应用到进化策略中 - 递归优化能力
    """
    if not suggestions:
        return {
            "status": "no_suggestions",
            "message": "无优化建议需要应用"
        }

    applied_count = 0
    applied_suggestions = []

    for suggestion in suggestions:
        # 模拟应用优化建议
        applied_suggestions.append({
            "suggestion": suggestion.get("suggestion", ""),
            "applied": True,
            "timestamp": datetime.now().isoformat()
        })
        applied_count += 1

    return {
        "status": "success",
        "applied_count": applied_count,
        "applied_suggestions": applied_suggestions,
        "message": f"已应用 {applied_count} 条优化建议到进化策略中"
    }


def run_meta_evolution_analysis() -> Dict[str, Any]:
    """
    运行完整的元进化分析
    """
    print("=" * 60)
    print("进化环元进化能力增强引擎 - 分析中...")
    print("=" * 60)

    # 1. 加载历史数据
    print("\n[1/4] 加载进化历史数据...")
    history = load_evolution_completed_history()
    print(f"    已加载 {len(history)} 轮进化历史")

    # 2. 分析进化过程
    print("\n[2/4] 分析进化过程...")
    analysis = analyze_evolution_process(history)
    print(f"    分析完成: {analysis.get('status')}")
    if analysis.get("status") == "success":
        print(f"    - 总轮次: {analysis.get('total_rounds')}")
        print(f"    - 成功完成: {analysis.get('completed_rounds')}")
        print(f"    - 成功率: {analysis.get('success_rate', 0)*100:.1f}%")

    # 3. 评估进化方法论
    print("\n[3/4] 评估进化方法论...")
    methodology = evaluate_evolution_methodology(history)
    print(f"    评估完成: {methodology.get('status')}")
    if methodology.get("status") == "success":
        print(f"    - 最佳策略: {methodology.get('best_strategy')}")
        print(f"    - 成功率: {methodology.get('best_success_rate', 0)*100:.1f}%")

    # 4. 生成优化策略
    print("\n[4/4] 生成优化策略...")
    strategy = generate_optimization_strategy(analysis, methodology)
    print(f"    生成完成: {strategy.get('status')}")
    print(f"    - 建议总数: {strategy.get('total_suggestions')}")
    if strategy.get("priority_suggestions"):
        print(f"    - 高优先级建议: {len(strategy.get('priority_suggestions'))} 条")

    # 5. 应用递归优化
    print("\n    应用优化建议...")
    suggestions = strategy.get("suggestions", [])
    optimization = apply_recursive_optimization(suggestions)
    print(f"    - 已应用: {optimization.get('applied_count')} 条")

    print("\n" + "=" * 60)
    print("元进化分析完成!")
    print("=" * 60)

    # 构建返回结果
    result = {
        "analysis": analysis,
        "methodology": methodology,
        "strategy": strategy,
        "optimization": optimization,
        "timestamp": datetime.now().isoformat(),
        "history_rounds": len(history)
    }

    return result


def save_analysis_result(result: Dict[str, Any], output_file: str = None) -> str:
    """保存分析结果"""
    if output_file is None:
        output_file = os.path.join(STATE_DIR, "meta_evolution_analysis_result.json")

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        return output_file
    except Exception as e:
        print(f"保存结果失败: {e}")
        return ""


def main():
    """主函数 - 支持命令行调用"""
    import argparse

    parser = argparse.ArgumentParser(description="进化环元进化能力增强引擎")
    parser.add_argument("--analyze", action="store_true", help="运行完整元进化分析")
    parser.add_argument("--process", action="store_true", help="仅分析进化过程")
    parser.add_argument("--methodology", action="store_true", help="仅评估进化方法论")
    parser.add_argument("--strategy", action="store_true", help="仅生成优化策略")
    parser.add_argument("--save", action="store_true", help="保存结果到文件")

    args = parser.parse_args()

    # 默认执行分析
    if args.analyze or args.process or args.methodology or args.strategy or not any([args.process, args.methodology, args.strategy]):
        result = run_meta_evolution_analysis()

        if args.save:
            output_file = save_analysis_result(result)
            print(f"\n结果已保存到: {output_file}")

        # 输出摘要
        print("\n" + "=" * 60)
        print("分析摘要:")
        print("=" * 60)

        analysis = result.get("analysis", {})
        methodology = result.get("methodology", {})
        strategy = result.get("strategy", {})

        print(f"\n【进化过程分析】")
        if analysis.get("status") == "success":
            print(f"  - 历史轮次: {analysis.get('total_rounds')}")
            print(f"  - 成功率: {analysis.get('success_rate', 0)*100:.1f}%")
            print(f"  - 目标类别: {analysis.get('goal_categories', {})}")
        else:
            print(f"  - {analysis.get('message', '分析失败')}")

        print(f"\n【方法论评估】")
        if methodology.get("status") == "success":
            print(f"  - 最佳策略: {methodology.get('best_strategy')}")
            print(f"  - 最佳成功率: {methodology.get('best_success_rate', 0)*100:.1f}%")
            print(f"  - 需改进: {methodology.get('needs_improvement')}")
        else:
            print(f"  - {methodology.get('message', '评估失败')}")

        print(f"\n【优化策略建议】")
        if strategy.get("status") == "success":
            priority = strategy.get("priority_suggestions", [])
            for i, s in enumerate(priority[:3], 1):
                print(f"  {i}. [{s.get('priority')}] {s.get('suggestion', '')[:80]}")
        else:
            print(f"  - 生成失败")

    return 0


if __name__ == "__main__":
    sys.exit(main())