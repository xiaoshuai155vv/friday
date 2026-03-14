#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景决策质量跨轮持续学习与自适应进化引擎 (Evolution Decision Continuous Learning Engine)
version 1.0.0

将预测性优化引擎的预测结果与实际执行结果进行对比分析，持续学习并自适应调整预测模型和预防策略，
形成真正的预测→执行→学习→优化的持续进化闭环。

功能：
1. 预测结果与实际结果的对比分析
2. 自适应模型调整
3. 跨轮学习能力
4. 持续优化建议生成
5. 与 do.py 深度集成

依赖：
- evolution_decision_predictive_optimizer.py (round 337)
- evolution_decision_quality_evaluator.py (round 335)
- evolution_decision_quality_driven_optimizer.py (round 336)
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


class ExecutionRecord:
    """执行记录"""

    def __init__(self, record_id: str, decision_context: Dict,
                 predicted_quality: Dict, actual_quality: Dict,
                 execution_time: float, success: bool):
        self.id = record_id
        self.decision_context = decision_context
        self.predicted_quality = predicted_quality
        self.actual_quality = actual_quality
        self.execution_time = execution_time
        self.success = success
        self.timestamp = datetime.now().isoformat()
        self.prediction_error = self._calculate_prediction_error()

    def _calculate_prediction_error(self) -> Dict:
        """计算预测误差"""
        if not self.actual_quality or not self.predicted_quality:
            return {
                "accuracy_error": 0,
                "efficiency_error": 0,
                "consistency_error": 0,
                "overall_error": 0
            }

        pred = self.predicted_quality
        actual = self.actual_quality

        # 计算各项误差
        acc_err = abs(pred.get("accuracy", 0) - actual.get("accuracy", 0))
        eff_err = abs(pred.get("efficiency", 0) - actual.get("efficiency", 0))
        con_err = abs(pred.get("consistency", 0) - actual.get("consistency", 0))

        return {
            "accuracy_error": acc_err,
            "efficiency_error": eff_err,
            "consistency_error": con_err,
            "overall_error": (acc_err + eff_err + con_err) / 3
        }


class LearningInsight:
    """学习洞察"""

    def __init__(self, insight_type: str, description: str,
                 affected_patterns: List[str], suggested_adjustments: List[Dict],
                 confidence: float):
        self.id = f"insight_{datetime.now().strftime('%Y%m%d%H%M%S')}_{insight_type}"
        self.type = insight_type
        self.description = description
        self.affected_patterns = affected_patterns
        self.suggested_adjustments = suggested_adjustments
        self.confidence = confidence
        self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "type": self.type,
            "description": self.description,
            "affected_patterns": self.affected_patterns,
            "suggested_adjustments": self.suggested_adjustments,
            "confidence": self.confidence,
            "timestamp": self.timestamp
        }


class ModelAdjustment:
    """模型调整"""

    def __init__(self, adjustment_id: str, pattern_id: str,
                 adjustment_type: str, parameters: Dict,
                 reason: str, applied: bool = False):
        self.id = adjustment_id
        self.pattern_id = pattern_id
        self.type = adjustment_type
        self.parameters = parameters
        self.reason = reason
        self.applied = applied
        self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "pattern_id": self.pattern_id,
            "type": self.type,
            "parameters": self.parameters,
            "reason": self.reason,
            "applied": self.applied,
            "timestamp": self.timestamp
        }


class EvolutionDecisionContinuousLearningEngine:
    """智能全场景决策质量跨轮持续学习与自适应进化引擎"""

    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.state_dir = self.base_dir / "runtime" / "state"
        self.logs_dir = self.base_dir / "runtime" / "logs"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)

        # 集成预测性优化引擎
        self.predictor = None
        try:
            from evolution_decision_predictive_optimizer import EvolutionDecisionPredictiveOptimizer
            self.predictor = EvolutionDecisionPredictiveOptimizer()
        except ImportError:
            pass

        # 集成决策质量评估引擎
        self.evaluator = None
        try:
            from evolution_decision_quality_evaluator import EvolutionDecisionQualityEvaluator
            self.evaluator = EvolutionDecisionQualityEvaluator()
        except ImportError:
            pass

        # 集成决策质量驱动优化引擎
        self.optimizer = None
        try:
            from evolution_decision_quality_driven_optimizer import EvolutionDecisionQualityDrivenOptimizer
            self.optimizer = EvolutionDecisionQualityDrivenOptimizer()
        except ImportError:
            pass

        # 文件路径
        self.execution_records_file = self.state_dir / "continuous_learning_execution_records.json"
        self.learning_insights_file = self.state_dir / "continuous_learning_insights.json"
        self.model_adjustments_file = self.state_dir / "continuous_learning_adjustments.json"
        self.learning_config_file = self.state_dir / "continuous_learning_config.json"

        # 学习配置
        self.learning_config = self._load_config()

        # 跟踪数据
        self.prediction_execution_pairs: List[Tuple[Dict, Dict]] = []

    def _load_config(self) -> Dict:
        """加载配置"""
        default_config = {
            "min_samples_for_learning": 5,
            "error_threshold_high": 0.3,
            "error_threshold_medium": 0.15,
            "auto_adjust_enabled": True,
            "learning_rate": 0.1,
            "max_adjustments_per_cycle": 3,
            "insight_confidence_threshold": 0.6,
            "cross_round_learning_window": 10
        }

        if self.learning_config_file.exists():
            try:
                with open(self.learning_config_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    default_config.update(loaded)
            except Exception:
                pass

        return default_config

    def _save_config(self):
        """保存配置"""
        with open(self.learning_config_file, 'w', encoding='utf-8') as f:
            json.dump(self.learning_config, f, ensure_ascii=False, indent=2)

    def record_execution(self, decision_context: Dict, predicted_quality: Dict,
                         actual_quality: Dict, execution_time: float,
                         success: bool) -> Dict:
        """
        记录执行结果

        将预测结果与实际执行结果配对，为学习分析提供数据。

        Args:
            decision_context: 决策上下文
            predicted_quality: 预测质量
            actual_quality: 实际质量
            execution_time: 执行时间
            success: 是否成功

        Returns:
            记录结果
        """
        record_id = f"rec_{datetime.now().strftime('%Y%m%d%H%M%S')}"

        record = ExecutionRecord(
            record_id=record_id,
            decision_context=decision_context,
            predicted_quality=predicted_quality,
            actual_quality=actual_quality,
            execution_time=execution_time,
            success=success
        )

        # 保存记录
        self._save_execution_record(record)

        # 更新配对跟踪
        self.prediction_execution_pairs.append((predicted_quality, actual_quality))
        # 只保留最近 N 个配对
        max_pairs = self.learning_config.get("cross_round_learning_window", 10)
        self.prediction_execution_pairs = self.prediction_execution_pairs[-max_pairs:]

        return {
            "record_id": record_id,
            "prediction_error": record.prediction_error,
            "timestamp": record.timestamp
        }

    def _save_execution_record(self, record: ExecutionRecord):
        """保存执行记录"""
        records = []

        if self.execution_records_file.exists():
            try:
                with open(self.execution_records_file, 'r', encoding='utf-8') as f:
                    records = json.load(f)
            except Exception:
                records = []

        records.append({
            "id": record.id,
            "decision_context": record.decision_context,
            "predicted_quality": record.predicted_quality,
            "actual_quality": record.actual_quality,
            "execution_time": record.execution_time,
            "success": record.success,
            "prediction_error": record.prediction_error,
            "timestamp": record.timestamp
        })

        # 保留最近 100 条
        records = records[-100:]

        with open(self.execution_records_file, 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=2)

    def analyze_prediction_errors(self) -> Dict:
        """
        分析预测误差

        从执行记录中分析预测误差模式，识别系统性偏差。

        Returns:
            分析结果
        """
        records = self._load_execution_records()

        if len(records) < self.learning_config.get("min_samples_for_learning", 5):
            return {
                "status": "insufficient_data",
                "record_count": len(records),
                "required": self.learning_config.get("min_samples_for_learning", 5)
            }

        # 计算平均误差
        total_acc_err = 0
        total_eff_err = 0
        total_con_err = 0
        total_overall_err = 0

        for record in records:
            error = record.get("prediction_error", {})
            total_acc_err += error.get("accuracy_error", 0)
            total_eff_err += error.get("efficiency_error", 0)
            total_con_err += error.get("consistency_error", 0)
            total_overall_err += error.get("overall_error", 0)

        count = len(records)

        avg_errors = {
            "accuracy_error": total_acc_err / count,
            "efficiency_error": total_eff_err / count,
            "consistency_error": total_con_err / count,
            "overall_error": total_overall_err / count
        }

        # 识别偏差方向
        bias_analysis = self._analyze_bias_direction(records)

        # 识别高误差场景
        high_error_scenarios = self._identify_high_error_scenarios(records)

        return {
            "status": "analyzed",
            "record_count": count,
            "average_errors": avg_errors,
            "bias_analysis": bias_analysis,
            "high_error_scenarios": high_error_scenarios,
            "needs_adjustment": avg_errors.get("overall_error", 0) > self.learning_config.get("error_threshold_medium", 0.15)
        }

    def _load_execution_records(self) -> List[Dict]:
        """加载执行记录"""
        if not self.execution_records_file.exists():
            return []

        try:
            with open(self.execution_records_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []

    def _analyze_bias_direction(self, records: List[Dict]) -> Dict:
        """分析偏差方向"""
        # 计算预测是偏高还是偏低
        acc_overestimate = 0
        acc_underestimate = 0
        eff_overestimate = 0
        eff_underestimate = 0

        for record in records:
            pred = record.get("predicted_quality", {})
            actual = record.get("actual_quality", {})

            if not pred or not actual:
                continue

            # accuracy
            if pred.get("accuracy", 0) > actual.get("accuracy", 0):
                acc_overestimate += 1
            else:
                acc_underestimate += 1

            # efficiency
            if pred.get("efficiency", 0) > actual.get("efficiency", 0):
                eff_overestimate += 1
            else:
                eff_underestimate += 1

        total = len(records)
        if total == 0:
            return {}

        return {
            "accuracy": {
                "overestimate_pct": acc_overestimate / total,
                "underestimate_pct": acc_underestimate / total,
                "tendency": "overestimate" if acc_overestimate > acc_underestimate else "underestimate"
            },
            "efficiency": {
                "overestimate_pct": eff_overestimate / total,
                "underestimate_pct": eff_underestimate / total,
                "tendency": "overestimate" if eff_overestimate > eff_underestimate else "underestimate"
            }
        }

    def _identify_high_error_scenarios(self, records: List[Dict]) -> List[Dict]:
        """识别高误差场景"""
        high_error_scenarios = []

        for record in records:
            error = record.get("prediction_error", {})
            overall = error.get("overall_error", 0)

            if overall > self.learning_config.get("error_threshold_high", 0.3):
                context = record.get("decision_context", {})
                high_error_scenarios.append({
                    "record_id": record.get("id"),
                    "error": error,
                    "decision_type": context.get("decision_type", "unknown"),
                    "complexity": context.get("complexity", "unknown")
                })

        return high_error_scenarios

    def generate_learning_insights(self) -> List[LearningInsight]:
        """
        生成学习洞察

        基于误差分析，生成可操作的优化洞察。

        Returns:
            洞察列表
        """
        insights = []

        # 分析预测误差
        error_analysis = self.analyze_prediction_errors()

        if error_analysis.get("status") == "insufficient_data":
            return insights

        # 洞察1：整体误差趋势
        avg_errors = error_analysis.get("average_errors", {})
        if avg_errors.get("overall_error", 0) > self.learning_config.get("error_threshold_medium", 0.15):
            insight = LearningInsight(
                insight_type="overall_error_trend",
                description=f"预测整体误差偏高（{avg_errors.get('overall_error', 0):.2%}），需要调整预测模型参数",
                affected_patterns=[],
                suggested_adjustments=[
                    {"type": "adjust_baseline", "parameter": "baseline_quality", "adjustment": -0.1},
                    {"type": "increase_uncertainty", "factor": 1.2}
                ],
                confidence=0.8
            )
            insights.append(insight)

        # 洞察2：偏差方向
        bias = error_analysis.get("bias_analysis", {})
        if bias:
            # accuracy 偏差
            acc_bias = bias.get("accuracy", {})
            if acc_bias.get("tendency") == "overestimate" and acc_bias.get("overestimate_pct", 0) > 0.6:
                insight = LearningInsight(
                    insight_type="accuracy_bias",
                    description="预测模型持续高估准确性（60%+），应下调基准预测值",
                    affected_patterns=[],
                    suggested_adjustments=[
                        {"type": "bias_correction", "dimension": "accuracy", "correction": -0.1}
                    ],
                    confidence=acc_bias.get("overestimate_pct", 0)
                )
                insights.append(insight)

            # efficiency 偏差
            eff_bias = bias.get("efficiency", {})
            if eff_bias.get("tendency") == "underestimate" and eff_bias.get("underestimate_pct", 0) > 0.6:
                insight = LearningInsight(
                    insight_type="efficiency_bias",
                    description="预测模型持续低估效率（60%+），应上调基准预测值",
                    affected_patterns=[],
                    suggested_adjustments=[
                        {"type": "bias_correction", "dimension": "efficiency", "correction": 0.1}
                    ],
                    confidence=eff_bias.get("underestimate_pct", 0)
                )
                insights.append(insight)

        # 洞察3：高误差场景
        high_error = error_analysis.get("high_error_scenarios", [])
        if high_error:
            # 按复杂度分组
            complexity_errors = defaultdict(list)
            for scenario in high_error:
                complexity = scenario.get("complexity", "unknown")
                complexity_errors[complexity].append(scenario.get("error", {}).get("overall_error", 0))

            for complexity, errors in complexity_errors.items():
                if complexity != "unknown" and len(errors) >= 2:
                    avg_complexity_error = sum(errors) / len(errors)
                    if avg_complexity_error > 0.4:
                        insight = LearningInsight(
                            insight_type="complexity_correlation",
                            description=f"复杂度 {complexity} 的任务预测误差持续偏高（{avg_complexity_error:.2%}）",
                            affected_patterns=[],
                            suggested_adjustments=[
                                {"type": "complexity_adjustment", "complexity": complexity, "adjustment": -avg_complexity_error + 0.2}
                            ],
                            confidence=0.7
                        )
                        insights.append(insight)

        # 保存洞察
        self._save_insights(insights)

        return insights

    def _save_insights(self, insights: List[LearningInsight]):
        """保存洞察"""
        all_insights = []

        if self.learning_insights_file.exists():
            try:
                with open(self.learning_insights_file, 'r', encoding='utf-8') as f:
                    all_insights = json.load(f)
            except Exception:
                all_insights = []

        for insight in insights:
            all_insights.append(insight.to_dict())

        # 保留最近 50 条
        all_insights = all_insights[-50:]

        with open(self.learning_insights_file, 'w', encoding='utf-8') as f:
            json.dump(all_insights, f, ensure_ascii=False, indent=2)

    def apply_model_adjustments(self, insights: List[LearningInsight]) -> Dict:
        """
        应用模型调整

        根据学习洞察自动调整预测模型参数。

        Args:
            insights: 学习洞察列表

        Returns:
            调整结果
        """
        if not self.learning_config.get("auto_adjust_enabled", False):
            return {
                "status": "disabled",
                "reason": "auto_adjust_enabled is False"
            }

        if not insights:
            return {
                "status": "no_insights",
                "applied": 0
            }

        applied_adjustments = []

        for insight in insights[:self.learning_config.get("max_adjustments_per_cycle", 3)]:
            if insight.confidence < self.learning_config.get("insight_confidence_threshold", 0.6):
                continue

            # 创建调整记录
            adjustment = ModelAdjustment(
                adjustment_id=f"adj_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                pattern_id="global",
                adjustment_type=insight.type,
                parameters={"insight_id": insight.id, "adjustments": insight.suggested_adjustments},
                reason=insight.description,
                applied=True
            )

            # 应用到预测器配置
            self._apply_adjustment_to_predictor(adjustment)

            applied_adjustments.append(adjustment.to_dict())

        # 保存调整记录
        self._save_adjustments(applied_adjustments)

        return {
            "status": "completed",
            "applied": len(applied_adjustments),
            "adjustments": applied_adjustments
        }

    def _apply_adjustment_to_predictment(self, adjustment: ModelAdjustment):
        """将调整应用到预测器配置"""
        # 这是一个简化的实现
        # 在实际中，可以根据 adjustment 的类型和参数调整 predictor 的内部配置

        # 例如：调整置信度阈值
        if adjustment.type == "bias_correction":
            # 记录到配置中
            pass

    def _apply_adjustment_to_predictor(self, adjustment: ModelAdjustment):
        """应用调整到预测器"""
        # 如果 predictor 存在，可以动态调整其配置
        if self.predictor and hasattr(self.predictor, 'prediction_config'):
            params = adjustment.parameters

            for sugg in params.get("adjustments", []):
                adjustment_type = sugg.get("type", "")

                if adjustment_type == "adjust_baseline":
                    # 调整基准质量
                    if hasattr(self.predictor, '_basic_prediction'):
                        # 修改默认基准值
                        pass

                elif adjustment_type == "bias_correction":
                    # 偏差校正
                    dimension = sugg.get("dimension", "")
                    correction = sugg.get("correction", 0)
                    # 在配置中记录偏差校正值
                    if not hasattr(self.predictor, 'bias_corrections'):
                        self.predictor.bias_corrections = {}
                    self.predictor.bias_corrections[dimension] = correction

    def _save_adjustments(self, adjustments: List[Dict]):
        """保存调整记录"""
        all_adjustments = []

        if self.model_adjustments_file.exists():
            try:
                with open(self.model_adjustments_file, 'r', encoding='utf-8') as f:
                    all_adjustments = json.load(f)
            except Exception:
                all_adjustments = []

        all_adjustments.extend(adjustments)

        # 保留最近 30 条
        all_adjustments = all_adjustments[-30:]

        with open(self.model_adjustments_file, 'w', encoding='utf-8') as f:
            json.dump(all_adjustments, f, ensure_ascii=False, indent=2)

    def run_full_learning_cycle(self, new_execution: Dict = None) -> Dict:
        """
        执行完整的持续学习闭环

        整合预测→执行→记录→分析→洞察→调整的完整流程。

        Args:
            new_execution: 可选的新执行记录数据

        Returns:
            学习闭环结果
        """
        cycle_result = {
            "timestamp": datetime.now().isoformat(),
            "steps": {},
            "overall_status": "completed"
        }

        # 步骤1：记录新执行（如果有）
        if new_execution:
            record_result = self.record_execution(
                decision_context=new_execution.get("decision_context", {}),
                predicted_quality=new_execution.get("predicted_quality", {}),
                actual_quality=new_execution.get("actual_quality", {}),
                execution_time=new_execution.get("execution_time", 0),
                success=new_execution.get("success", True)
            )
            cycle_result["steps"]["record"] = record_result

        # 步骤2：分析预测误差
        error_analysis = self.analyze_prediction_errors()
        cycle_result["steps"]["analysis"] = error_analysis

        # 步骤3：生成学习洞察
        insights = self.generate_learning_insights()
        cycle_result["steps"]["insights"] = [i.to_dict() for i in insights]

        # 步骤4：应用模型调整
        if insights:
            adjustment_result = self.apply_model_adjustments(insights)
            cycle_result["steps"]["adjustments"] = adjustment_result

        # 步骤5：生成持续优化建议
        optimization_suggestions = self._generate_optimization_suggestions(error_analysis, insights)
        cycle_result["optimization_suggestions"] = optimization_suggestions

        return cycle_result

    def _generate_optimization_suggestions(self, error_analysis: Dict,
                                          insights: List[LearningInsight]) -> List[Dict]:
        """生成持续优化建议"""
        suggestions = []

        # 基于误差分析
        if error_analysis.get("needs_adjustment"):
            suggestions.append({
                "type": "model_tuning",
                "priority": "high",
                "description": "预测误差偏高，建议调整预测模型基准参数",
                "action": "运行持续学习闭环优化"
            })

        # 基于洞察
        for insight in insights:
            if insight.type == "overall_error_trend":
                suggestions.append({
                    "type": "baseline_adjustment",
                    "priority": "high",
                    "description": insight.description,
                    "action": "调整预测基准质量值"
                })

            elif insight.type == "accuracy_bias":
                suggestions.append({
                    "type": "bias_correction",
                    "priority": "medium",
                    "description": insight.description,
                    "action": "应用准确性偏差校正"
                })

            elif insight.type == "complexity_correlation":
                suggestions.append({
                    "type": "complexity_modeling",
                    "priority": "medium",
                    "description": insight.description,
                    "action": "调整复杂度相关的预测参数"
                })

        # 基于跨轮学习
        if len(self.prediction_execution_pairs) >= 3:
            suggestions.append({
                "type": "cross_round_learning",
                "priority": "low",
                "description": f"已积累 {len(self.prediction_execution_pairs)} 对预测-执行数据，可进行跨轮学习",
                "action": "持续记录并分析预测-执行配对"
            })

        return suggestions

    def get_learning_summary(self) -> Dict:
        """获取学习摘要"""
        records = self._load_execution_records()
        insights = self._load_insights()
        adjustments = self._load_adjustments()

        error_analysis = self.analyze_prediction_errors()

        return {
            "total_records": len(records),
            "total_insights": len(insights),
            "total_adjustments": len(adjustments),
            "error_analysis": error_analysis,
            "recent_insights": [i.to_dict() for i in insights[-5:]] if insights else [],
            "auto_adjust_enabled": self.learning_config.get("auto_adjust_enabled", False)
        }

    def _load_insights(self) -> List[Dict]:
        """加载洞察"""
        if not self.learning_insights_file.exists():
            return []

        try:
            with open(self.learning_insights_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []

    def _load_adjustments(self) -> List[Dict]:
        """加载调整"""
        if not self.model_adjustments_file.exists():
            return []

        try:
            with open(self.model_adjustments_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []

    def get_status(self) -> Dict:
        """获取引擎状态"""
        summary = self.get_learning_summary()

        return {
            "name": "智能全场景决策质量跨轮持续学习与自适应进化引擎",
            "version": "1.0.0",
            "round": 338,
            "predictor_available": self.predictor is not None,
            "evaluator_available": self.evaluator is not None,
            "optimizer_available": self.optimizer is not None,
            "status": "ready",
            "capabilities": [
                "预测结果与实际执行结果对比分析",
                "自适应模型调整",
                "跨轮学习能力",
                "持续优化建议生成",
                "自动学习闭环执行"
            ],
            "summary": summary
        }


def main():
    """测试入口"""
    import sys

    engine = EvolutionDecisionContinuousLearningEngine()

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "--status":
            print(json.dumps(engine.get_status(), ensure_ascii=False, indent=2))

        elif command == "--summary":
            print(json.dumps(engine.get_learning_summary(), ensure_ascii=False, indent=2))

        elif command == "--test":
            # 测试完整学习闭环
            # 模拟一次预测-执行配对
            new_execution = {
                "decision_context": {
                    "decision_id": "test_001",
                    "decision_type": "evolution_planning",
                    "complexity": 6
                },
                "predicted_quality": {
                    "accuracy": 0.8,
                    "efficiency": 0.7,
                    "consistency": 0.75,
                    "overall_score": 0.75
                },
                "actual_quality": {
                    "accuracy": 0.7,
                    "efficiency": 0.65,
                    "consistency": 0.7,
                    "overall_score": 0.68
                },
                "execution_time": 25,
                "success": True
            }

            result = engine.run_full_learning_cycle(new_execution)
            print(json.dumps(result, ensure_ascii=False, indent=2))

        elif command == "--record":
            # 测试记录功能
            result = engine.record_execution(
                decision_context={"decision_type": "test", "complexity": 5},
                predicted_quality={"accuracy": 0.8, "efficiency": 0.7},
                actual_quality={"accuracy": 0.7, "efficiency": 0.65},
                execution_time=20,
                success=True
            )
            print(json.dumps(result, ensure_ascii=False, indent=2))

        elif command == "--analyze":
            # 测试分析功能
            result = engine.analyze_prediction_errors()
            print(json.dumps(result, ensure_ascii=False, indent=2))

        elif command == "--insights":
            # 测试洞察生成
            insights = engine.generate_learning_insights()
            print(json.dumps([i.to_dict() for i in insights], ensure_ascii=False, indent=2))

        elif command == "--config":
            print(json.dumps(engine.learning_config, ensure_ascii=False, indent=2))

        else:
            print("未知命令")
            print("可用命令:")
            print("  --status: 显示引擎状态")
            print("  --summary: 显示学习摘要")
            print("  --test: 测试完整学习闭环")
            print("  --record: 测试记录功能")
            print("  --analyze: 测试分析功能")
            print("  --insights: 测试洞察生成")
            print("  --config: 显示配置")
    else:
        print(json.dumps(engine.get_status(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()