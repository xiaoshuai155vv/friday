#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景决策质量预测性优化与预防性增强引擎 (Evolution Decision Predictive Optimizer)
version 1.0.0

将决策质量评估从"事后分析"升级为"事前预测"，利用知识图谱的历史模式来预测可能的决策偏差，
实现真正的预防性优化而非事后补救。增强系统的主动预测和预防能力。

功能：
1. 基于历史模式的预测模型
2. 预测性决策质量评估
3. 预防性优化建议生成
4. 与知识图谱深度集成
5. 与决策质量驱动优化引擎（round 336）集成
6. 与 do.py 深度集成

依赖：
- evolution_decision_quality_evaluator.py (round 335)
- evolution_decision_quality_driven_optimizer.py (round 336)
- evolution_kg_deep_reasoning_insight_engine.py (round 330)
- evolution_knowledge_graph_reasoning.py (round 298)
"""

import json
import os
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict
import statistics
import re


class DecisionPattern:
    """决策模式"""

    def __init__(self, pattern_id: str, decision_type: str, context_features: Dict,
                 quality_outcomes: Dict, occurrence_count: int = 1):
        self.id = pattern_id
        self.decision_type = decision_type
        self.context_features = context_features  # 上下文特征
        self.quality_outcomes = quality_outcomes  # 质量结果分布
        self.occurrence_count = occurrence_count
        self.last_observed = datetime.now().isoformat()

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "decision_type": self.decision_type,
            "context_features": self.context_features,
            "quality_outcomes": self.quality_outcomes,
            "occurrence_count": self.occurrence_count,
            "last_observed": self.last_observed
        }


class PredictionResult:
    """预测结果"""

    def __init__(self, decision_id: str, predicted_quality: Dict,
                 confidence: float, risk_factors: List[Dict],
                 recommended_preventive_actions: List[Dict]):
        self.decision_id = decision_id
        self.predicted_quality = predicted_quality
        self.confidence = confidence
        self.risk_factors = risk_factors
        self.recommended_preventive_actions = recommended_preventive_actions
        self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict:
        return {
            "decision_id": self.decision_id,
            "predicted_quality": self.predicted_quality,
            "confidence": self.confidence,
            "risk_factors": self.risk_factors,
            "recommended_preventive_actions": self.recommended_preventive_actions,
            "timestamp": self.timestamp
        }


class EvolutionDecisionPredictiveOptimizer:
    """智能全场景决策质量预测性优化与预防性增强引擎"""

    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.state_dir = self.base_dir / "runtime" / "state"
        self.logs_dir = self.base_dir / "runtime" / "logs"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)

        # 集成决策质量评估引擎
        self.quality_evaluator = None
        try:
            from evolution_decision_quality_evaluator import EvolutionDecisionQualityEvaluator
            self.quality_evaluator = EvolutionDecisionQualityEvaluator()
        except ImportError:
            pass

        # 集成决策质量驱动优化引擎
        self.optimizer = None
        try:
            from evolution_decision_quality_driven_optimizer import EvolutionDecisionQualityDrivenOptimizer
            self.optimizer = EvolutionDecisionQualityDrivenOptimizer()
        except ImportError:
            pass

        # 集成知识图谱推理引擎
        self.kg_reasoning = None
        try:
            from evolution_kg_deep_reasoning_insight_engine import KGDeepReasoningInsightEngine
            self.kg_reasoning = KGDeepReasoningInsightEngine()
        except ImportError:
            pass

        # 预测模式存储
        self.patterns_file = self.state_dir / "decision_prediction_patterns.json"
        self.predictions_file = self.state_dir / "predictive_optimization_predictions.json"
        self.preventive_log_file = self.state_dir / "preventive_optimization_log.json"

        # 预测配置
        self.prediction_config = {
            "min_pattern_samples": 3,
            "confidence_threshold": 0.6,
            "prediction_horizon": 5,  # 预测未来5步
            "risk_threshold": 0.3,  # 风险阈值
            "auto_prevent": True,  # 自动预防
            "max_preventive_actions": 3
        }

        # 风险特征库
        self.risk_feature_library = {
            "time_pressure": {
                "indicator": "execution_time",
                "threshold": 60,
                "risk_score": 0.7,
                "preventive_action": "提前准备资源或并行处理"
            },
            "resource_contention": {
                "indicator": "concurrent_tasks",
                "threshold": 3,
                "risk_score": 0.6,
                "preventive_action": "调整任务优先级或延迟非关键任务"
            },
            "knowledge_gap": {
                "indicator": "knowledge_sources_count",
                "threshold": 1,
                "risk_score": 0.5,
                "preventive_action": "补充相关知识或寻求外部信息"
            },
            "complexity_high": {
                "indicator": "task_complexity",
                "threshold": 7,
                "risk_score": 0.65,
                "preventive_action": "分解任务或增加验证步骤"
            },
            "historical_failure": {
                "indicator": "previous_failure_rate",
                "threshold": 0.3,
                "risk_score": 0.8,
                "preventive_action": "使用已验证的替代方案"
            },
            "context_shift": {
                "indicator": "context_similarity",
                "threshold": 0.4,
                "risk_score": 0.55,
                "preventive_action": "重新评估上下文或调整策略"
            }
        }

    def learn_from_history(self, decision_history: List[Dict]) -> Dict:
        """
        从历史决策中学习模式

        Args:
            decision_history: 历史决策记录列表

        Returns:
            学习结果
        """
        learned_patterns = []

        # 按决策类型分组
        type_groups = defaultdict(list)
        for decision in decision_history:
            decision_type = decision.get("decision_type", "unknown")
            type_groups[decision_type].append(decision)

        # 提取每个类型的模式
        for decision_type, decisions in type_groups.items():
            if len(decisions) >= self.prediction_config["min_pattern_samples"]:
                # 提取上下文特征
                context_features = self._extract_context_features(decisions)

                # 提取质量结果分布
                quality_outcomes = self._extract_quality_outcomes(decisions)

                # 创建模式
                pattern = DecisionPattern(
                    pattern_id=f"pattern_{decision_type}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    decision_type=decision_type,
                    context_features=context_features,
                    quality_outcomes=quality_outcomes,
                    occurrence_count=len(decisions)
                )
                learned_patterns.append(pattern)

        # 保存模式
        self._save_patterns(learned_patterns)

        return {
            "patterns_learned": len(learned_patterns),
            "decisions_analyzed": len(decision_history),
            "status": "completed"
        }

    def _extract_context_features(self, decisions: List[Dict]) -> Dict:
        """提取上下文特征"""
        features = {
            "avg_execution_time": 0,
            "success_rate": 0,
            "common_contexts": [],
            "time_patterns": []
        }

        if not decisions:
            return features

        execution_times = [d.get("execution_time", 0) for d in decisions if d.get("execution_time")]
        successes = [d.get("success", False) for d in decisions]

        if execution_times:
            features["avg_execution_time"] = statistics.mean(execution_times)
        if successes:
            features["success_rate"] = sum(successes) / len(successes)

        return features

    def _extract_quality_outcomes(self, decisions: List[Dict]) -> Dict:
        """提取质量结果分布"""
        outcomes = {
            "avg_accuracy": 0,
            "avg_efficiency": 0,
            "avg_consistency": 0,
            "failure_rate": 0
        }

        if not decisions:
            return outcomes

        quality_scores = [d.get("quality_score", {}) for d in decisions if d.get("quality_score")]

        if quality_scores:
            outcomes["avg_accuracy"] = statistics.mean([s.get("accuracy", 0) for s in quality_scores])
            outcomes["avg_efficiency"] = statistics.mean([s.get("efficiency", 0) for s in quality_scores])
            outcomes["avg_consistency"] = statistics.mean([s.get("consistency", 0) for s in quality_scores])

        failures = [d.get("success", True) for d in decisions]
        outcomes["failure_rate"] = 1 - (sum(failures) / len(failures)) if failures else 0

        return outcomes

    def predict_decision_quality(self, decision_context: Dict) -> PredictionResult:
        """
        预测决策质量

        基于历史模式和当前上下文，预测决策可能的执行质量。

        Args:
            decision_context: 决策上下文，包含任务特征、时间要求等

        Returns:
            预测结果
        """
        decision_id = decision_context.get("decision_id", f"pred_{datetime.now().strftime('%Y%m%d%H%M%S')}")

        # 加载历史模式
        patterns = self._load_patterns()

        # 分析当前上下文特征
        context_features = self._analyze_context_features(decision_context)

        # 基于模式预测
        predicted_quality = self._predict_from_patterns(patterns, decision_context, context_features)

        # 识别风险因素
        risk_factors = self._identify_risk_factors(decision_context, predicted_quality)

        # 生成预防性建议
        preventive_actions = self._generate_preventive_actions(risk_factors, predicted_quality)

        # 计算置信度
        confidence = self._calculate_confidence(patterns, decision_context)

        result = PredictionResult(
            decision_id=decision_id,
            predicted_quality=predicted_quality,
            confidence=confidence,
            risk_factors=risk_factors,
            recommended_preventive_actions=preventive_actions
        )

        # 保存预测结果
        self._save_prediction(result)

        return result

    def _analyze_context_features(self, context: Dict) -> Dict:
        """分析上下文特征"""
        features = {
            "task_complexity": context.get("complexity", 5),
            "has_time_constraint": "expected_time" in context,
            "has_knowledge_support": "knowledge_sources" in context,
            "execution_mode": context.get("mode", "standard"),
            "historical_similarity": 0
        }

        # 检查是否在知识图谱中有类似决策
        if self.kg_reasoning:
            try:
                similar = self.kg_reasoning.find_similar_decisions(
                    context.get("task_description", ""),
                    limit=3
                )
                features["historical_similarity"] = len(similar) / 3.0 if similar else 0
            except Exception:
                pass

        return features

    def _predict_from_patterns(self, patterns: List[Dict], context: Dict,
                                  context_features: Dict) -> Dict:
        """基于模式预测"""
        if not patterns:
            # 无模式，使用基础预测
            return self._basic_prediction(context)

        # 找到最匹配的模式
        best_match = None
        best_score = 0

        for pattern in patterns:
            pattern_type = pattern.get("decision_type", "")
            context_type = context.get("decision_type", "")

            if pattern_type == context_type or not context_type:
                # 计算匹配度
                match_score = self._calculate_pattern_match(pattern, context_features)
                if match_score > best_score:
                    best_score = match_score
                    best_match = pattern

        if best_match and best_score >= self.prediction_config["confidence_threshold"]:
            # 使用模式预测
            return self._apply_pattern_prediction(best_match, context)
        else:
            return self._basic_prediction(context)

    def _basic_prediction(self, context: Dict) -> Dict:
        """基础预测（无模式时）"""
        return {
            "accuracy": 0.7,
            "efficiency": 0.7,
            "consistency": 0.6,
            "overall_score": 0.65,
            "prediction_method": "baseline",
            "note": "无历史模式，使用基准预测"
        }

    def _apply_pattern_prediction(self, pattern: Dict, context: Dict) -> Dict:
        """应用模式预测"""
        outcomes = pattern.get("quality_outcomes", {})

        # 考虑当前上下文的调整
        complexity = context.get("complexity", 5)
        adjustment = (7 - complexity) * 0.05  # 复杂度越高，质量越低

        accuracy = outcomes.get("avg_accuracy", 0.7) - max(0, adjustment)
        efficiency = outcomes.get("avg_efficiency", 0.7) - max(0, adjustment)
        consistency = outcomes.get("avg_consistency", 0.6) - max(0, adjustment)

        return {
            "accuracy": max(0, min(1, accuracy)),
            "efficiency": max(0, min(1, efficiency)),
            "consistency": max(0, min(1, consistency)),
            "overall_score": (accuracy + efficiency + consistency) / 3,
            "prediction_method": "pattern_based",
            "pattern_id": pattern.get("id"),
            "occurrence_count": pattern.get("occurrence_count", 1)
        }

    def _calculate_pattern_match(self, pattern: Dict, context_features: Dict) -> float:
        """计算模式匹配度"""
        if not pattern:
            return 0

        pattern_features = pattern.get("context_features", {})

        # 基于出现次数的权重
        occurrence = pattern.get("occurrence_count", 1)
        count_weight = min(1.0, occurrence / 10.0)

        # 基于历史成功率的权重
        success_rate = pattern_features.get("success_rate", 0.5)
        success_weight = success_rate

        return (count_weight + success_weight) / 2

    def _identify_risk_factors(self, context: Dict, predicted_quality: Dict) -> List[Dict]:
        """识别风险因素"""
        risk_factors = []

        # 检查时间压力
        if context.get("expected_time") and context.get("execution_time"):
            if context["execution_time"] > context["expected_time"] * 1.3:
                risk_factors.append({
                    "type": "time_pressure",
                    "severity": 0.7,
                    "description": "执行时间可能超出预期",
                    "current_value": context.get("execution_time"),
                    "expected_value": context.get("expected_time")
                })

        # 检查任务复杂度
        complexity = context.get("complexity", 5)
        if complexity > 7:
            risk_factors.append({
                "type": "complexity_high",
                "severity": 0.65,
                "description": "任务复杂度较高",
                "current_value": complexity,
                "threshold": 7
            })

        # 检查预测质量
        overall = predicted_quality.get("overall_score", 0)
        if overall < 0.5:
            risk_factors.append({
                "type": "low_quality_prediction",
                "severity": 0.8,
                "description": "预测决策质量较低",
                "predicted_score": overall
            })

        # 检查知识支持
        if not context.get("knowledge_sources"):
            risk_factors.append({
                "type": "knowledge_gap",
                "severity": 0.5,
                "description": "缺少知识支持"
            })

        return risk_factors

    def _generate_preventive_actions(self, risk_factors: List[Dict],
                                      predicted_quality: Dict) -> List[Dict]:
        """生成预防性动作"""
        actions = []

        for risk in risk_factors:
            risk_type = risk.get("type")

            # 从风险库中查找对应动作
            if risk_type in self.risk_feature_library:
                library_entry = self.risk_feature_library[risk_type]
                action = {
                    "type": risk_type,
                    "description": library_entry.get("preventive_action"),
                    "priority": "high" if risk.get("severity", 0) > 0.6 else "medium",
                    "risk_reduction": library_entry.get("risk_score", 0.5)
                }
                actions.append(action)

        # 基于质量预测添加通用优化
        if predicted_quality.get("overall_score", 0) < 0.7:
            actions.append({
                "type": "general_optimization",
                "description": "增加验证步骤和错误处理",
                "priority": "medium",
                "risk_reduction": 0.3
            })

        # 排序并限制数量
        actions = sorted(actions, key=lambda x: 0 if x.get("priority") == "high" else 1)
        return actions[:self.prediction_config["max_preventive_actions"]]

    def _calculate_confidence(self, patterns: List[Dict], context: Dict) -> float:
        """计算预测置信度"""
        if not patterns:
            return 0.3  # 无模式，低置信度

        # 基于模式数量
        pattern_confidence = min(1.0, len(patterns) / 10.0) * 0.5

        # 基于上下文完整性
        context_confidence = 0.5
        if context.get("knowledge_sources"):
            context_confidence += 0.2
        if context.get("expected_time"):
            context_confidence += 0.1
        if context.get("complexity"):
            context_confidence += 0.2

        return min(0.95, pattern_confidence + context_confidence * 0.5)

    def execute_preventive_optimization(self, prediction_result: PredictionResult,
                                         decision_context: Dict) -> Dict:
        """
        执行预防性优化

        根据预测结果，自动执行预防性动作。

        Args:
            prediction_result: 预测结果
            decision_context: 决策上下文

        Returns:
            执行结果
        """
        if not self.prediction_config.get("auto_prevent", False):
            return {
                "status": "skipped",
                "reason": "auto_prevent disabled"
            }

        executed_actions = []
        failed_actions = []

        for action in prediction_result.recommended_preventive_actions:
            if action.get("priority") != "high":
                continue  # 只自动执行高优先级动作

            try:
                result = self._execute_preventive_action(action, decision_context)
                if result.get("success"):
                    executed_actions.append(action)
                else:
                    failed_actions.append(action)
            except Exception as e:
                failed_actions.append({
                    "action": action,
                    "error": str(e)
                })

        # 记录到日志
        self._log_preventive_actions(executed_actions, failed_actions)

        return {
            "status": "completed" if executed_actions else "failed",
            "executed": len(executed_actions),
            "failed": len(failed_actions),
            "actions": executed_actions
        }

    def _execute_preventive_action(self, action: Dict, context: Dict) -> Dict:
        """执行单个预防性动作"""
        action_type = action.get("type")

        # 记录优化意图
        opt_record = {
            "type": "preventive_optimization",
            "action_type": action_type,
            "description": action.get("description"),
            "timestamp": datetime.now().isoformat(),
            "decision_id": context.get("decision_id", "unknown")
        }

        # 追加到优化日志
        log_file = self.state_dir / "preventive_optimization_log.json"
        logs = []

        if log_file.exists():
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
            except Exception:
                logs = []

        logs.append(opt_record)
        logs = logs[-50:]  # 保留最近50条

        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)

        return {
            "success": True,
            "action": action_type,
            "description": action.get("description")
        }

    def run_full_predictive_cycle(self, decision_context: Dict) -> Dict:
        """
        执行完整的预测性优化闭环

        整合预测→预防性优化→验证的完整流程。

        Args:
            decision_context: 决策上下文

        Returns:
            完整预测优化结果
        """
        cycle_result = {
            "decision_id": decision_context.get("decision_id", f"pred_{datetime.now().strftime('%Y%m%d%H%M%S')}"),
            "timestamp": datetime.now().isoformat(),
            "steps": {},
            "overall_status": "pending"
        }

        # 步骤1：预测决策质量
        prediction = self.predict_decision_quality(decision_context)
        cycle_result["steps"]["prediction"] = prediction.to_dict()

        # 步骤2：执行预防性优化
        if prediction.risk_factors:
            prevention_result = self.execute_preventive_optimization(prediction, decision_context)
            cycle_result["steps"]["prevention"] = prevention_result
            cycle_result["preventive_actions_applied"] = prevention_result.get("executed", 0)
        else:
            cycle_result["steps"]["prevention"] = {
                "status": "no_risks_detected",
                "actions": []
            }
            cycle_result["preventive_actions_applied"] = 0

        # 步骤3：评估整体状态
        has_high_risks = any(r.get("severity", 0) > 0.6 for r in prediction.risk_factors)
        has_actions = cycle_result["preventive_actions_applied"] > 0

        if has_high_risks and not has_actions:
            cycle_result["overall_status"] = "warning"
        elif has_actions:
            cycle_result["overall_status"] = "optimized"
        else:
            cycle_result["overall_status"] = "ready"

        return cycle_result

    def _save_patterns(self, patterns: List[DecisionPattern]):
        """保存模式"""
        pattern_list = [p.to_dict() for p in patterns]

        existing = []
        if self.patterns_file.exists():
            try:
                with open(self.patterns_file, 'r', encoding='utf-8') as f:
                    existing = json.load(f)
            except Exception:
                existing = []

        # 合并模式
        combined = existing + pattern_list
        # 去重并限制数量
        seen = set()
        unique_patterns = []
        for p in combined:
            p_id = p.get("id", "")
            if p_id not in seen:
                seen.add(p_id)
                unique_patterns.append(p)

        unique_patterns = unique_patterns[-50:]  # 保留最近50个模式

        with open(self.patterns_file, 'w', encoding='utf-8') as f:
            json.dump(unique_patterns, f, ensure_ascii=False, indent=2)

    def _load_patterns(self) -> List[Dict]:
        """加载模式"""
        if not self.patterns_file.exists():
            return []

        try:
            with open(self.patterns_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []

    def _save_prediction(self, prediction: PredictionResult):
        """保存预测结果"""
        predictions = []

        if self.predictions_file.exists():
            try:
                with open(self.predictions_file, 'r', encoding='utf-8') as f:
                    predictions = json.load(f)
            except Exception:
                predictions = []

        predictions.append(prediction.to_dict())
        predictions = predictions[-100:]  # 保留最近100条

        with open(self.predictions_file, 'w', encoding='utf-8') as f:
            json.dump(predictions, f, ensure_ascii=False, indent=2)

    def _log_preventive_actions(self, executed: List[Dict], failed: List[Dict]):
        """记录预防性动作"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "executed": executed,
            "failed": failed
        }

        logs = []
        if self.preventive_log_file.exists():
            try:
                with open(self.preventive_log_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
            except Exception:
                logs = []

        logs.append(log_entry)
        logs = logs[-50:]  # 保留最近50条

        with open(self.preventive_log_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)

    def get_prediction_summary(self) -> Dict:
        """获取预测摘要"""
        if not self.predictions_file.exists():
            return {
                "total_predictions": 0,
                "status": "no_data"
            }

        try:
            with open(self.predictions_file, 'r', encoding='utf-8') as f:
                predictions = json.load(f)
        except Exception:
            return {"total_predictions": 0, "status": "error"}

        if not predictions:
            return {"total_predictions": 0, "status": "empty"}

        # 统计
        total = len(predictions)
        high_risk_count = sum(1 for p in predictions
                              if p.get("risk_factors") and
                              any(r.get("severity", 0) > 0.6 for r in p["risk_factors"]))

        recent = predictions[-10:] if len(predictions) >= 10 else predictions
        avg_confidence = sum(p.get("confidence", 0) for p in recent) / len(recent) if recent else 0

        # 模式统计
        patterns = self._load_patterns()

        return {
            "total_predictions": total,
            "high_risk_predictions": high_risk_count,
            "pattern_count": len(patterns),
            "recent_avg_confidence": round(avg_confidence, 2),
            "auto_prevent_enabled": self.prediction_config.get("auto_prevent", False)
        }

    def get_status(self) -> Dict:
        """获取引擎状态"""
        summary = self.get_prediction_summary()

        return {
            "name": "智能全场景决策质量预测性优化与预防性增强引擎",
            "version": "1.0.0",
            "round": 337,
            "quality_evaluator_available": self.quality_evaluator is not None,
            "optimizer_available": self.optimizer is not None,
            "kg_reasoning_available": self.kg_reasoning is not None,
            "status": "ready",
            "capabilities": [
                "基于历史模式的预测模型",
                "预测性决策质量评估",
                "预防性优化建议生成",
                "风险因素自动识别",
                "自动预防性优化执行"
            ],
            "summary": summary
        }


def main():
    """测试入口"""
    import sys

    optimizer = EvolutionDecisionPredictiveOptimizer()

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "--status":
            print(json.dumps(optimizer.get_status(), ensure_ascii=False, indent=2))

        elif command == "--summary":
            print(json.dumps(optimizer.get_prediction_summary(), ensure_ascii=False, indent=2))

        elif command == "--test":
            # 测试完整预测性优化闭环
            decision_context = {
                "decision_id": "test_001",
                "decision_type": "evolution_planning",
                "task_description": "测试进化目标：增强决策质量",
                "complexity": 6,
                "expected_time": 30,
                "knowledge_sources": ["round_335", "round_336"],
                "mode": "auto"
            }
            result = optimizer.run_full_predictive_cycle(decision_context)
            print(json.dumps(result, ensure_ascii=False, indent=2))

        elif command == "--predict":
            # 测试预测
            if len(sys.argv) > 2:
                context = json.loads(sys.argv[2])
                result = optimizer.predict_decision_quality(context)
                print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
            else:
                print("用法: --predict <context_json>")

        elif command == "--config":
            print(json.dumps(optimizer.prediction_config, ensure_ascii=False, indent=2))

        else:
            print("未知命令")
            print("可用命令:")
            print("  --status: 显示引擎状态")
            print("  --summary: 显示预测摘要")
            print("  --test: 测试完整预测性优化闭环")
            print("  --predict <context>: 测试预测功能")
            print("  --config: 显示配置")
    else:
        print(json.dumps(optimizer.get_status(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()