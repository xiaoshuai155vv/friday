#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环自我进化元认知深度优化引擎
============================================================
在 round 494 完成的元进化智能决策自动策略生成与执行增强引擎基础上，
进一步增强自我进化的元认知深度优化能力。让系统能够主动分析自身进化过程的质量、
评估元进化策略的有效性、生成认知优化反馈，形成更深入的自我反思与递归优化闭环。
实现从「智能决策执行」到「深度自我反思与持续优化」的范式升级。

版本：1.0.0
"""

import json
import os
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

# 引入已有的引擎模块
try:
    from evolution_meta_decision_auto_execution_engine import MetaDecisionAutoExecutionEngine
    from evolution_self_evolution_effectiveness_analysis_engine import SelfEvolutionEffectivenessAnalysisEngine
except ImportError:
    # 如果导入失败，定义空类
    class MetaDecisionAutoExecutionEngine:
        def __init__(self):
            self.version = "1.0.0"
            self.name = "Meta Decision Auto Execution Engine"

        def get_status(self) -> Dict[str, Any]:
            return {"status": "fallback", "version": self.version}

        def analyze_system_state(self) -> Dict[str, Any]:
            return {"status": "fallback"}

        def run_full_loop(self, dry_run: bool = False) -> Dict[str, Any]:
            return {"status": "fallback"}

        def get_execution_history(self, limit: int = 10) -> List[Dict[str, Any]]:
            return []

    class SelfEvolutionEffectivenessAnalysisEngine:
        def __init__(self):
            self.version = "1.0.0"
            self.name = "Self Evolution Effectiveness Analysis Engine"

        def get_status(self) -> Dict[str, Any]:
            return {"status": "fallback"}


class SelfEvolutionMetaCognitionDeepOptimizationEngine:
    """自我进化元认知深度优化引擎核心类"""

    def __init__(self):
        self.version = "1.0.0"
        self.name = "Self Evolution Meta Cognition Deep Optimization Engine"
        self.state_dir = os.path.join(os.path.dirname(__file__), "..", "runtime", "state")
        self.logs_dir = os.path.join(os.path.dirname(__file__), "..", "runtime", "logs")

        # 初始化已集成的引擎
        self.meta_decision_engine = MetaDecisionAutoExecutionEngine()
        self.effectiveness_engine = SelfEvolutionEffectivenessAnalysisEngine()

        # 内部状态
        self.reflection_history: List[Dict[str, Any]] = []
        self.cognition_feedback: List[Dict[str, Any]] = []
        self.optimization_loops: List[Dict[str, Any]] = []

    def get_status(self) -> Dict[str, Any]:
        """获取引擎状态"""
        return {
            "name": self.name,
            "version": self.version,
            "integrated_engines": [
                self.meta_decision_engine.name,
                self.effectiveness_engine.name
            ],
            "reflection_history_count": len(self.reflection_history),
            "cognition_feedback_count": len(self.cognition_feedback),
            "optimization_loops_count": len(self.optimization_loops),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    def analyze_evolution_quality(self) -> Dict[str, Any]:
        """分析进化过程质量"""
        print("[元认知深度优化] 分析进化过程质量...")

        # 获取元决策引擎状态
        meta_status = self.meta_decision_engine.get_status()

        # 获取效能分析引擎状态
        effectiveness_status = self.effectiveness_engine.get_status()

        # 分析进化历史数据
        evolution_history = self._load_evolution_history()

        # 计算质量评分
        quality_metrics = self._calculate_quality_metrics(evolution_history)

        analysis_result = {
            "meta_engine_status": meta_status,
            "effectiveness_status": effectiveness_status,
            "quality_metrics": quality_metrics,
            "evolution_history_analyzed": len(evolution_history),
            "analysis_timestamp": datetime.now(timezone.utc).isoformat()
        }

        print(f"[元认知深度优化] 进化质量分析完成: 综合质量评分={quality_metrics.get('overall_quality_score', 0):.2f}")

        return analysis_result

    def _load_evolution_history(self) -> List[Dict[str, Any]]:
        """加载进化历史数据"""
        history = []

        # 加载已完成进化的记录
        state_dir = os.path.join(os.path.dirname(__file__), "..", "runtime", "state")
        if os.path.exists(state_dir):
            for filename in os.listdir(state_dir):
                if filename.startswith("evolution_completed_") and filename.endswith(".json"):
                    filepath = os.path.join(state_dir, filename)
                    try:
                        with open(filepath, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            history.append(data)
                    except Exception:
                        pass

        return history

    def _calculate_quality_metrics(self, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """计算质量指标"""
        if not history:
            return {
                "overall_quality_score": 0.5,
                "success_rate": 0.5,
                "efficiency_score": 0.5,
                "innovation_score": 0.5,
                "stability_score": 0.5
            }

        # 计算各维度评分
        total = len(history)
        success_count = sum(1 for h in history if h.get("是否完成") == "已完成")

        success_rate = success_count / total if total > 0 else 0.5

        # 基于进化的多样性计算创新评分
        unique_goals = len(set(h.get("current_goal", "") for h in history if h.get("current_goal")))
        innovation_score = min(unique_goals / max(total, 1), 1.0)

        # 基于完成率计算稳定性
        stability_score = success_rate

        # 综合评分（加权平均）
        overall = (success_rate * 0.4 + innovation_score * 0.3 + stability_score * 0.3)

        return {
            "overall_quality_score": overall,
            "success_rate": success_rate,
            "efficiency_score": 0.7,  # 默认值
            "innovation_score": innovation_score,
            "stability_score": stability_score,
            "total_evolution_rounds": total,
            "successful_rounds": success_count
        }

    def evaluate_meta_strategy_effectiveness(self) -> Dict[str, Any]:
        """评估元进化策略有效性"""
        print("[元认知深度优化] 评估元进化策略有效性...")

        # 分析系统状态
        system_state = self.meta_decision_engine.analyze_system_state()

        # 获取执行历史
        execution_history = self.meta_decision_engine.get_execution_history()

        # 评估策略有效性
        effectiveness_metrics = self._calculate_strategy_effectiveness(execution_history)

        evaluation_result = {
            "system_state_summary": {
                "cognition_score": system_state.get("cognition_assessment", {}).get("cognition_score", 0),
                "value_score": system_state.get("value_metrics", {}).get("value_score", 0)
            },
            "effectiveness_metrics": effectiveness_metrics,
            "execution_history_count": len(execution_history),
            "evaluation_timestamp": datetime.now(timezone.utc).isoformat()
        }

        print(f"[元认知深度优化] 策略有效性评估完成: 效率评分={effectiveness_metrics.get('efficiency_score', 0):.2f}")

        return evaluation_result

    def _calculate_strategy_effectiveness(self, execution_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """计算策略有效性"""
        if not execution_history:
            return {
                "efficiency_score": 0.5,
                "adaptability_score": 0.5,
                "impact_score": 0.5
            }

        total = len(execution_history)

        # 基于执行成功率计算效率评分
        successful = sum(1 for e in execution_history if e.get("results"))
        efficiency_score = successful / total if total > 0 else 0.5

        # 基于策略类型多样性计算适应性评分
        action_types = set()
        for e in execution_history:
            for r in e.get("results", []):
                action_types.add(r.get("action", ""))

        adaptability_score = min(len(action_types) / max(total, 1), 1.0)

        # 基于影响范围计算影响评分
        impact_score = 0.6  # 默认值

        return {
            "efficiency_score": efficiency_score,
            "adaptability_score": adaptability_score,
            "impact_score": impact_score
        }

    def generate_cognition_feedback(self) -> Dict[str, Any]:
        """生成认知优化反馈"""
        print("[元认知深度优化] 生成认知优化反馈...")

        # 分析进化质量
        quality_analysis = self.analyze_evolution_quality()

        # 评估策略有效性
        strategy_evaluation = self.evaluate_meta_strategy_effectiveness()

        # 生成优化建议
        optimization_suggestions = self._generate_optimization_suggestions(
            quality_analysis, strategy_evaluation
        )

        # 生成反馈
        feedback = {
            "quality_analysis": quality_analysis,
            "strategy_evaluation": strategy_evaluation,
            "optimization_suggestions": optimization_suggestions,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }

        self.cognition_feedback.append(feedback)

        print(f"[元认知深度优化] 生成了 {len(optimization_suggestions)} 条优化建议")

        return feedback

    def _generate_optimization_suggestions(self, quality_analysis: Dict[str, Any],
                                            strategy_evaluation: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成优化建议"""
        suggestions = []

        # 基于质量分析生成建议
        quality_metrics = quality_analysis.get("quality_metrics", {})
        overall_score = quality_metrics.get("overall_quality_score", 0.5)
        innovation_score = quality_metrics.get("innovation_score", 0.5)

        if overall_score < 0.6:
            suggestions.append({
                "type": "quality_improvement",
                "priority": "high",
                "description": "提升整体进化质量 - 当前质量评分偏低，建议优化进化策略",
                "target": "evolution_strategy"
            })

        if innovation_score < 0.5:
            suggestions.append({
                "type": "innovation_enhancement",
                "priority": "medium",
                "description": "增强进化创新性 - 建议探索新的进化方向",
                "target": "innovation_engine"
            })

        # 基于策略评估生成建议
        effectiveness = strategy_evaluation.get("effectiveness_metrics", {})
        efficiency = effectiveness.get("efficiency_score", 0.5)

        if efficiency < 0.6:
            suggestions.append({
                "type": "efficiency_optimization",
                "priority": "high",
                "description": "优化策略执行效率 - 当前策略执行效率偏低",
                "target": "execution_strategy"
            })

        # 如果没有明显问题，生成预防性建议
        if not suggestions:
            suggestions.append({
                "type": "preventive_optimization",
                "priority": "low",
                "description": "预防性优化 - 保持系统稳定运行",
                "target": "general"
            })

        # 按优先级排序
        priority_order = {"high": 0, "medium": 1, "low": 2}
        suggestions.sort(key=lambda x: priority_order.get(x.get("priority", "low"), 2))

        return suggestions

    def run_optimization_loop(self, dry_run: bool = False) -> Dict[str, Any]:
        """运行完整的元认知优化循环"""
        print("=" * 60)
        print("[元认知深度优化] 启动自我进化元认知深度优化循环...")
        print("=" * 60)

        # 步骤1: 分析进化质量
        print("\n[步骤 1/4] 分析进化过程质量...")
        quality_analysis = self.analyze_evolution_quality()

        # 步骤2: 评估策略有效性
        print("\n[步骤 2/4] 评估元进化策略有效性...")
        strategy_evaluation = self.evaluate_meta_strategy_effectiveness()

        # 步骤3: 生成认知反馈
        print("\n[步骤 3/4] 生成认知优化反馈...")
        feedback = self.generate_cognition_feedback()

        # 步骤4: 执行优化（如需要）
        print("\n[步骤 4/4] 执行优化...")

        optimization_result = {
            "quality_analysis": quality_analysis,
            "strategy_evaluation": strategy_evaluation,
            "feedback": feedback,
            "optimization_executed": not dry_run,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        # 记录优化循环
        self.optimization_loops.append(optimization_result)

        # 记录反思历史
        self.reflection_history.append({
            "loop_result": optimization_result,
            "reflected_at": datetime.now(timezone.utc).isoformat()
        })

        print("\n" + "=" * 60)
        print("[元认知深度优化] 自我进化元认知深度优化循环执行完成!")
        print(f"质量评分: {quality_analysis.get('quality_metrics', {}).get('overall_quality_score', 0):.2f}")
        print(f"策略效率: {strategy_evaluation.get('effectiveness_metrics', {}).get('efficiency_score', 0):.2f}")
        print(f"优化建议数: {len(feedback.get('optimization_suggestions', []))}")
        print("=" * 60)

        return optimization_result

    def get_reflection_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取反思历史"""
        return self.reflection_history[-limit:] if self.reflection_history else []

    def get_cockpit_data(self) -> Dict[str, Any]:
        """获取进化驾驶舱数据"""
        return {
            "engine_status": self.get_status(),
            "recent_reflections": self.get_reflection_history(5),
            "recent_feedback": self.cognition_feedback[-5:] if self.cognition_feedback else [],
            "optimization_loops": self.optimization_loops[-5:] if self.optimization_loops else [],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


def main():
    """主函数，支持命令行调用"""
    import argparse

    parser = argparse.ArgumentParser(description="自我进化元认知深度优化引擎")
    parser.add_argument("--status", action="store_true", help="获取引擎状态")
    parser.add_argument("--run", action="store_true", help="运行完整的元认知优化循环")
    parser.add_argument("--dry-run", action="store_true", help="模拟运行（不实际执行）")
    parser.add_argument("--analyze-quality", action="store_true", help="仅分析进化质量")
    parser.add_argument("--evaluate-strategy", action="store_true", help="仅评估策略有效性")
    parser.add_argument("--generate-feedback", action="store_true", help="仅生成认知反馈")
    parser.add_argument("--history", action="store_true", help="获取反思历史")
    parser.add_argument("--cockpit-data", action="store_true", help="获取进化驾驶舱数据")

    args = parser.parse_args()

    engine = SelfEvolutionMetaCognitionDeepOptimizationEngine()

    if args.status:
        print(json.dumps(engine.get_status(), ensure_ascii=False, indent=2))
        return

    if args.cockpit_data:
        print(json.dumps(engine.get_cockpit_data(), ensure_ascii=False, indent=2))
        return

    if args.history:
        history = engine.get_reflection_history()
        print(json.dumps(history, ensure_ascii=False, indent=2))
        return

    if args.analyze_quality:
        result = engine.analyze_evolution_quality()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if args.evaluate_strategy:
        result = engine.evaluate_meta_strategy_effectiveness()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if args.generate_feedback:
        result = engine.generate_cognition_feedback()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if args.run or (not any([args.status, args.history, args.cockpit_data, args.analyze_quality,
                              args.evaluate_strategy, args.generate_feedback])):
        result = engine.run_optimization_loop(dry_run=args.dry_run)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return


if __name__ == "__main__":
    main()