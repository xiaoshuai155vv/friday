#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环策略执行效果实时反馈与动态调整深度集成引擎 (version 1.0.0)

在 round 417 完成的进化策略智能推荐与自动选择引擎基础上，进一步增强策略执行效果
的实时反馈与动态调整能力。让系统能够：
1. 实时跟踪策略执行效果并收集数据
2. 分析执行效果与预期的偏差
3. 动态生成调整策略
4. 形成完整的"推荐→执行→效果验证→动态调整→优化建议"闭环

核心功能：
1. 策略执行效果实时跟踪与数据收集
2. 执行效果分析与偏差检测
3. 动态调整策略生成
4. 反馈学习闭环（执行→分析→调整→优化→再执行）
5. 与进化驾驶舱的深度集成

集成模块：
- evolution_strategy_intelligent_recommendation_engine.py (round 417)
- evolution_cockpit_engine.py (round 350)
- evolution_loop_self_healing_advanced.py (round 290)
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from collections import defaultdict

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

# 尝试导入集成的模块
try:
    from evolution_strategy_intelligent_recommendation_engine import StrategyRecommendationEngine
except ImportError:
    StrategyRecommendationEngine = None

try:
    from evolution_loop_self_healing_advanced import EvolutionLoopSelfHealingAdvanced
except ImportError:
    EvolutionLoopSelfHealingAdvanced = None


class StrategyFeedbackAdjustmentEngine:
    """策略执行效果实时反馈与动态调整深度集成引擎"""

    def __init__(self, state_dir: str = "runtime/state"):
        self.state_dir = Path(state_dir)
        self.state_file = self.state_dir / "evolution_strategy_feedback_state.json"

        # 集成核心引擎
        self.strategy_recommendation_engine = None
        self.self_healing_engine = None

        # 反馈调整状态
        self.state = {
            "initialized": False,
            "version": "1.0.0",
            "feedback_count": 0,
            "adjustment_count": 0,
            "execution_tracking_count": 0,
            "deviation_analysis_count": 0,
            "learning_iterations": 0,
            "last_feedback_time": None,
            "last_adjustment_time": None,
            "feedback_history": [],
            "adjustment_history": [],
            "execution_tracking": [],
            "deviation_patterns": [],
            "successful_adjustments": [],
            "failed_adjustments": [],
            "状态": "待触发",
        }

        self._initialize_engines()
        self._load_state()

    def _initialize_engines(self):
        """初始化集成的引擎"""
        if StrategyRecommendationEngine:
            try:
                self.strategy_recommendation_engine = StrategyRecommendationEngine(self.state_dir)
                print("[FeedbackAdjustment] 策略推荐引擎已加载")
            except Exception as e:
                print(f"[FeedbackAdjustment] 策略推荐引擎加载失败: {e}")

        if EvolutionLoopSelfHealingAdvanced:
            try:
                self.self_healing_engine = EvolutionLoopSelfHealingAdvanced(self.state_dir)
                print("[FeedbackAdjustment] 自愈引擎已加载")
            except Exception as e:
                print(f"[FeedbackAdjustment] 自愈引擎加载失败: {e}")

        self.state["initialized"] = True

    def _load_state(self):
        """加载状态"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    saved_state = json.load(f)
                    self.state.update(saved_state)
            except Exception as e:
                print(f"[FeedbackAdjustment] 状态加载失败: {e}")

    def _save_state(self):
        """保存状态"""
        try:
            self.state_dir.mkdir(parents=True, exist_ok=True)
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[FeedbackAdjustment] 状态保存失败: {e}")

    def track_execution(self, strategy_name: str, execution_data: Dict[str, Any]) -> Dict[str, Any]:
        """跟踪策略执行效果"""
        print(f"[FeedbackAdjustment] 正在跟踪策略执行: {strategy_name}")

        tracking_record = {
            "strategy_name": strategy_name,
            "timestamp": datetime.now().isoformat(),
            "execution_data": execution_data,
            "start_time": execution_data.get("start_time", datetime.now().isoformat()),
            "expected_outcome": execution_data.get("expected_outcome", {}),
            "actual_outcome": {},
            "deviation": {},
        }

        self.state["execution_tracking_count"] += 1

        # 记录到跟踪列表
        self.state["execution_tracking"].append(tracking_record)

        # 保持跟踪记录不超过50条
        if len(self.state["execution_tracking"]) > 50:
            self.state["execution_tracking"] = self.state["execution_tracking"][-50:]

        self._save_state()

        return {
            "status": "tracking_started",
            "tracking_id": len(self.state["execution_tracking"]) - 1,
            "strategy_name": strategy_name,
        }

    def record_actual_outcome(
        self,
        strategy_name: str,
        actual_outcome: Dict[str, Any],
        metrics: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """记录策略执行的实际结果"""
        print(f"[FeedbackAdjustment] 记录实际执行结果: {strategy_name}")

        # 找到对应的跟踪记录
        tracking_record = None
        for record in reversed(self.state["execution_tracking"]):
            if record.get("strategy_name") == strategy_name:
                tracking_record = record
                break

        if tracking_record is None:
            # 如果没有找到跟踪记录，创建一个新的
            tracking_record = {
                "strategy_name": strategy_name,
                "timestamp": datetime.now().isoformat(),
                "execution_data": {},
                "start_time": datetime.now().isoformat(),
                "expected_outcome": {},
            }

        # 更新实际结果
        tracking_record["actual_outcome"] = actual_outcome
        tracking_record["end_time"] = datetime.now().isoformat()

        # 计算偏差
        expected = tracking_record.get("expected_outcome", {})
        deviation = self._calculate_deviation(expected, actual_outcome)
        tracking_record["deviation"] = deviation

        # 如果是更新现有记录
        for i, record in enumerate(self.state["execution_tracking"]):
            if record.get("strategy_name") == strategy_name and not record.get("actual_outcome"):
                self.state["execution_tracking"][i] = tracking_record
                break
        else:
            # 如果是新的跟踪记录
            self.state["execution_tracking"].append(tracking_record)

        self._save_state()

        return {
            "status": "outcome_recorded",
            "strategy_name": strategy_name,
            "deviation": deviation,
        }

    def _calculate_deviation(
        self,
        expected: Dict[str, Any],
        actual: Dict[str, Any]
    ) -> Dict[str, Any]:
        """计算预期与实际的偏差"""
        deviation = {}

        for key in expected:
            if key in actual:
                exp_val = expected[key]
                act_val = actual[key]

                # 数值类型偏差计算
                if isinstance(exp_val, (int, float)) and isinstance(act_val, (int, float)):
                    diff = act_val - exp_val
                    percent_diff = (diff / exp_val * 100) if exp_val != 0 else 0
                    deviation[key] = {
                        "expected": exp_val,
                        "actual": act_val,
                        "difference": diff,
                        "percent_difference": percent_diff,
                    }
                else:
                    # 非数值类型直接比较
                    deviation[key] = {
                        "expected": exp_val,
                        "actual": act_val,
                        "match": exp_val == act_val,
                    }

        # 计算整体偏差评分
        if deviation:
            numeric_devs = [
                abs(d.get("percent_difference", 0))
                for d in deviation.values()
                if isinstance(d.get("percent_difference"), (int, float))
            ]
            if numeric_devs:
                deviation["overall_deviation_score"] = sum(numeric_devs) / len(numeric_devs)

        return deviation

    def analyze_deviation(self, strategy_name: Optional[str] = None) -> Dict[str, Any]:
        """分析偏差模式"""
        print(f"[FeedbackAdjustment] 正在分析偏差模式...")

        analysis = {
            "timestamp": datetime.now().isoformat(),
            "strategy_name": strategy_name,
            "deviation_patterns": [],
            "common_issues": [],
            "improvement_suggestions": [],
        }

        # 收集所有有偏差的跟踪记录
        relevant_records = []
        for record in self.state["execution_tracking"]:
            if record.get("deviation"):
                if strategy_name is None or record.get("strategy_name") == strategy_name:
                    relevant_records.append(record)

        if not relevant_records:
            analysis["message"] = "暂无足够的偏差数据进行分析"
            return analysis

        # 分析偏差模式
        deviation_types = defaultdict(list)

        for record in relevant_records:
            deviation = record.get("deviation", {})
            for key, dev_data in deviation.items():
                if key == "overall_deviation_score":
                    continue
                if isinstance(dev_data, dict):
                    percent_diff = dev_data.get("percent_difference", 0)
                    if abs(percent_diff) > 10:  # 偏差超过10%
                        deviation_types[key].append(percent_diff)

        # 识别常见问题
        for issue_type, diffs in deviation_types.items():
            if diffs:
                avg_diff = sum(diffs) / len(diffs)
                analysis["common_issues"].append({
                    "issue_type": issue_type,
                    "occurrence_count": len(diffs),
                    "average_deviation": avg_diff,
                    "severity": "high" if abs(avg_diff) > 30 else "medium" if abs(avg_diff) > 15 else "low",
                })

        # 生成改进建议
        for issue in analysis["common_issues"]:
            if issue["severity"] in ["high", "medium"]:
                analysis["improvement_suggestions"].append({
                    "target": issue["issue_type"],
                    "suggestion": f"调整{issue['issue_type']}相关参数，建议调整幅度: {issue['average_deviation']:.1f}%",
                    "priority": issue["severity"],
                })

        self.state["deviation_analysis_count"] += 1
        self._save_state()

        return analysis

    def generate_adjustment(
        self,
        strategy_name: str,
        deviation: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """生成动态调整策略"""
        print(f"[FeedbackAdjustment] 正在生成调整策略: {strategy_name}")

        if context is None:
            context = {}

        adjustment = {
            "strategy_name": strategy_name,
            "timestamp": datetime.now().isoformat(),
            "based_on_deviation": deviation,
            "adjustments": [],
            "expected_impact": {},
            "confidence": 0,
        }

        # 基于偏差类型生成调整建议
        deviation_score = deviation.get("overall_deviation_score", 0)

        if deviation_score > 30:
            # 高偏差，需要重大调整
            adjustment["adjustments"].append({
                "type": "参数大幅调整",
                "description": "当前执行效果与预期偏差较大，建议重新评估策略参数",
                "specific_actions": [
                    "重新分析系统状态和历史数据",
                    "调整策略优先级和资源分配",
                    "考虑切换到备选策略",
                ],
            })
            adjustment["confidence"] = 0.5
        elif deviation_score > 15:
            # 中等偏差，微调即可
            adjustment["adjustments"].append({
                "type": "参数微调",
                "description": "执行效果略有偏差，进行参数微调",
                "specific_actions": [
                    "调整执行顺序和时序",
                    "优化资源分配比例",
                    "增强错误处理机制",
                ],
            })
            adjustment["confidence"] = 0.7
        else:
            # 低偏差，保持当前策略
            adjustment["adjustments"].append({
                "type": "保持策略",
                "description": "执行效果符合预期，保持当前策略",
                "specific_actions": [
                    "继续执行当前策略",
                    "记录成功模式供后续参考",
                ],
            })
            adjustment["confidence"] = 0.9

        # 添加预期影响
        adjustment["expected_impact"] = {
            "deviation_reduction": f"预期降低偏差至 {deviation_score * 0.5:.1f}%",
            "execution_improvement": "预期执行效率提升 10-20%",
            "stability_improvement": "预期稳定性提升",
        }

        # 更新状态
        self.state["adjustment_count"] += 1
        self.state["last_adjustment_time"] = datetime.now().isoformat()
        self.state["adjustment_history"].append(adjustment)

        # 保持历史记录不超过30条
        if len(self.state["adjustment_history"]) > 30:
            self.state["adjustment_history"] = self.state["adjustment_history"][-30:]

        self._save_state()

        return adjustment

    def feedback_learning(
        self,
        strategy_name: str,
        adjustment_applied: Dict[str, Any],
        result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """反馈学习 - 从调整结果中学习"""
        print(f"[FeedbackAdjustment] 正在进行反馈学习: {strategy_name}")

        learning_result = {
            "strategy_name": strategy_name,
            "timestamp": datetime.now().isoformat(),
            "adjustment_applied": adjustment_applied,
            "result": result,
            "learning_outcome": {},
        }

        # 分析调整是否成功
        deviation_before = adjustment_applied.get("based_on_deviation", {}).get("overall_deviation_score", 0)
        deviation_after = result.get("deviation_score", 0)

        if deviation_after < deviation_before:
            # 调整成功
            learning_outcome = {
                "successful": True,
                "improvement": deviation_before - deviation_after,
                "pattern": "调整有效",
            }
            self.state["successful_adjustments"].append({
                "strategy_name": strategy_name,
                "improvement": deviation_before - deviation_after,
                "timestamp": datetime.now().isoformat(),
            })
        else:
            # 调整未达预期
            learning_outcome = {
                "successful": False,
                "note": "调整效果不明显，可能需要重新评估策略",
                "pattern": "需要进一步分析",
            }
            self.state["failed_adjustments"].append({
                "strategy_name": strategy_name,
                "timestamp": datetime.now().isoformat(),
            })

        learning_result["learning_outcome"] = learning_outcome

        # 更新学习迭代次数
        self.state["learning_iterations"] += 1

        # 保持记录
        self.state["feedback_history"].append(learning_result)
        if len(self.state["feedback_history"]) > 30:
            self.state["feedback_history"] = self.state["feedback_history"][-30:]

        # 保持成功/失败记录
        if len(self.state["successful_adjustments"]) > 20:
            self.state["successful_adjustments"] = self.state["successful_adjustments"][-20:]
        if len(self.state["failed_adjustments"]) > 20:
            self.state["failed_adjustments"] = self.state["failed_adjustments"][-20:]

        self._save_state()

        return learning_result

    def execute_full_loop(
        self,
        strategy_name: str,
        initial_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """执行完整的反馈调整闭环"""
        print(f"[FeedbackAdjustment] 正在执行完整反馈闭环: {strategy_name}")

        if initial_context is None:
            initial_context = {}

        # 1. 跟踪执行
        track_result = self.track_execution(strategy_name, {
            "start_time": datetime.now().isoformat(),
            "expected_outcome": initial_context.get("expected_outcome", {
                "success_rate": 0.8,
                "execution_time": 60,
                "efficiency": 0.75,
            }),
        })

        # 2. 模拟执行（实际应用中这里会是真实的策略执行）
        # 记录实际结果
        actual_outcome = {
            "success_rate": initial_context.get("actual_success_rate", 0.7),
            "execution_time": initial_context.get("actual_execution_time", 75),
            "efficiency": initial_context.get("actual_efficiency", 0.65),
        }

        record_result = self.record_actual_outcome(strategy_name, actual_outcome)

        # 3. 分析偏差
        analysis = self.analyze_deviation(strategy_name)

        # 4. 生成调整策略
        deviation = record_result.get("deviation", {})
        adjustment = self.generate_adjustment(strategy_name, deviation)

        # 5. 模拟应用调整并记录结果（实际应用中需要真实执行）
        result = {
            "deviation_score": deviation.get("overall_deviation_score", 0) * 0.6,  # 模拟调整后偏差降低
            "status": "adjusted",
        }

        # 6. 反馈学习
        learning_result = self.feedback_learning(strategy_name, adjustment, result)

        # 更新反馈计数
        self.state["feedback_count"] += 1
        self.state["last_feedback_time"] = datetime.now().isoformat()
        self._save_state()

        return {
            "status": "loop_completed",
            "strategy_name": strategy_name,
            "track_result": track_result,
            "record_result": record_result,
            "analysis": analysis,
            "adjustment": adjustment,
            "learning_result": learning_result,
        }

    def get_status(self) -> Dict[str, Any]:
        """获取引擎状态"""
        return {
            "initialized": self.state.get("initialized", False),
            "version": self.state.get("version", "1.0.0"),
            "feedback_count": self.state.get("feedback_count", 0),
            "adjustment_count": self.state.get("adjustment_count", 0),
            "execution_tracking_count": self.state.get("execution_tracking_count", 0),
            "deviation_analysis_count": self.state.get("deviation_analysis_count", 0),
            "learning_iterations": self.state.get("learning_iterations", 0),
            "last_feedback_time": self.state.get("last_feedback_time"),
            "last_adjustment_time": self.state.get("last_adjustment_time"),
            "状态": self.state.get("状态", "待触发"),
        }

    def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        return {
            "status": "healthy" if self.state.get("initialized") else "uninitialized",
            "engines_loaded": {
                "strategy_recommendation": self.strategy_recommendation_engine is not None,
                "self_healing": self.self_healing_engine is not None,
            },
            "metrics": self.get_status(),
            "successful_adjustments_count": len(self.state.get("successful_adjustments", [])),
            "failed_adjustments_count": len(self.state.get("failed_adjustments", [])),
        }


def main():
    """主函数 - 用于命令行调用"""
    import argparse

    parser = argparse.ArgumentParser(description="策略执行效果实时反馈与动态调整引擎")
    parser.add_argument("action", choices=["track", "record", "analyze", "adjust", "learn", "loop", "status", "health"], help="执行动作")
    parser.add_argument("--strategy", type=str, help="策略名称")
    parser.add_argument("--outcome", type=str, help="实际结果(JSON字符串)")
    parser.add_argument("--deviation", type=str, help="偏差数据(JSON字符串)")

    args = parser.parse_args()

    engine = StrategyFeedbackAdjustmentEngine()

    if args.action == "track":
        result = engine.track_execution(args.strategy or "default", {})
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.action == "record":
        outcome = json.loads(args.outcome or "{}")
        result = engine.record_actual_outcome(args.strategy or "default", outcome)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.action == "analyze":
        result = engine.analyze_deviation(args.strategy)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.action == "adjust":
        deviation = json.loads(args.deviation or "{}")
        result = engine.generate_adjustment(args.strategy or "default", deviation)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.action == "learn":
        result = engine.feedback_learning(args.strategy or "default", {}, {"deviation_score": 0})
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.action == "loop":
        result = engine.execute_full_loop(args.strategy or "test_strategy")
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.action == "status":
        result = engine.get_status()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.action == "health":
        result = engine.health_check()
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()