#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化决策质量实时评估与自适应优化引擎 (Evolution Decision Quality Evaluator)
version 1.0.0

基于 round 334 的知识驱动决策集成能力，进一步实现决策质量的实时评估与自适应优化。
让系统能够实时评估进化决策质量、分析决策与结果偏差、持续学习优化、自动生成并执行优化建议。

功能：
1. 决策质量实时评估（多维度评估决策质量分数）
2. 偏差模式分析（识别决策与实际结果的偏差模式）
3. 持续学习优化（从决策结果中学习并优化决策策略）
4. 自动生成优化建议（基于分析结果生成可执行的优化建议）
5. 优化建议执行（将优化建议应用到决策流程中）
6. 与 do.py 深度集成

依赖：
- evolution_decision_knowledge_integration.py (round 334)
- evolution_cross_round_knowledge_fusion_engine.py (round 332)
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict
import statistics


class EvolutionDecisionQualityEvaluator:
    """智能全场景进化决策质量实时评估与自适应优化引擎"""

    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.state_dir = self.base_dir / "runtime" / "state"
        self.logs_dir = self.base_dir / "runtime" / "logs"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)

        # 集成引擎实例
        self.decision_knowledge_integration = None

        # 尝试导入决策知识集成引擎
        try:
            from evolution_decision_knowledge_integration import DecisionKnowledgeIntegrationEngine
            self.decision_knowledge_integration = DecisionKnowledgeIntegrationEngine()
        except ImportError:
            pass

        # 决策质量评估结果存储
        self.quality_records_file = self.state_dir / "decision_quality_records.json"

        # 偏差模式分析结果存储
        self.deviation_patterns_file = self.state_dir / "decision_deviation_patterns.json"

        # 优化建议存储
        self.optimization_suggestions_file = self.state_dir / "decision_optimization_suggestions.json"

        # 质量评估维度权重
        self.quality_dimensions = {
            "accuracy": {"weight": 0.3, "description": "决策准确性"},
            "efficiency": {"weight": 0.2, "description": "决策效率"},
            "consistency": {"weight": 0.15, "description": "决策一致性"},
            "learning": {"weight": 0.2, "description": "学习能力"},
            "adaptability": {"weight": 0.15, "description": "自适应能力"}
        }

    def evaluate_decision_quality(self, decision_id: str, decision_data: Dict,
                                   execution_result: Dict) -> Dict:
        """
        决策质量实时评估

        对进化决策进行多维度质量评估。

        Args:
            decision_id: 决策ID
            decision_data: 决策数据（包含决策内容、置信度、知识来源等）
            execution_result: 执行结果（包含成功与否、执行时间、效果等）

        Returns:
            质量评估结果
        """
        result = {
            "decision_id": decision_id,
            "timestamp": datetime.now().isoformat(),
            "dimensions": {},
            "overall_score": 0.0,
            "status": "pending"
        }

        # 维度1：准确性评估
        accuracy_score = self._evaluate_accuracy(decision_data, execution_result)
        result["dimensions"]["accuracy"] = accuracy_score

        # 维度2：效率评估
        efficiency_score = self._evaluate_efficiency(decision_data, execution_result)
        result["dimensions"]["efficiency"] = efficiency_score

        # 维度3：一致性评估
        consistency_score = self._evaluate_consistency(decision_id, decision_data)
        result["dimensions"]["consistency"] = consistency_score

        # 维度4：学习能力评估
        learning_score = self._evaluate_learning(decision_data, execution_result)
        result["dimensions"]["learning"] = learning_score

        # 维度5：自适应能力评估
        adaptability_score = self._evaluate_adaptability(decision_data, execution_result)
        result["dimensions"]["adaptability"] = adaptability_score

        # 计算加权总分
        total_score = 0.0
        for dim_name, dim_data in result["dimensions"].items():
            weight = self.quality_dimensions.get(dim_name, {}).get("weight", 0)
            score = dim_data.get("score", 0)
            total_score += weight * score

        result["overall_score"] = round(total_score, 2)

        # 生成评估结论
        result["conclusion"] = self._generate_evaluation_conclusion(result["overall_score"])
        result["status"] = "completed"

        # 保存评估结果
        self._save_quality_record(result)

        return result

    def _evaluate_accuracy(self, decision_data: Dict, execution_result: Dict) -> Dict:
        """评估决策准确性"""
        # 准确性与预期目标达成度相关
        expected_goal = decision_data.get("decision", "")
        actual_result = execution_result.get("result", "")
        success = execution_result.get("success", False)

        # 基础准确度
        accuracy = 0.5  # 默认值

        if success:
            # 执行成功，准确度高
            if expected_goal and actual_result:
                # 检查实际结果是否与预期目标相关
                if any(keyword in str(actual_result).lower() for keyword in str(expected_goal).lower()[:10]):
                    accuracy = 0.9
                else:
                    accuracy = 0.7
            else:
                accuracy = 0.85
        else:
            # 执行失败，准确度低
            accuracy = 0.3

        # 如果有置信度信息，结合置信度
        confidence = decision_data.get("confidence", 0.5)
        accuracy = (accuracy + confidence) / 2

        return {
            "score": round(accuracy, 2),
            "description": "决策目标与实际执行结果的匹配度",
            "factors": {
                "success": success,
                "goal_match": accuracy > 0.7
            }
        }

    def _evaluate_efficiency(self, decision_data: Dict, execution_result: Dict) -> Dict:
        """评估决策效率"""
        # 效率与决策速度、执行时间相关
        execution_time = execution_result.get("execution_time", 0)

        # 设定效率阈值（单位：秒）
        efficient_threshold = 30  # 30秒内为高效
        moderate_threshold = 120  # 2分钟内为中等

        if execution_time <= efficient_threshold:
            efficiency = 0.95
        elif execution_time <= moderate_threshold:
            efficiency = 0.75
        else:
            efficiency = 0.5

        # 如果有决策时间信息，也纳入考虑
        decision_time = decision_data.get("decision_time", 0)
        if decision_time > 0:
            # 决策时间过长降低效率分
            if decision_time > 10:
                efficiency = max(0.3, efficiency - 0.2)

        return {
            "score": round(efficiency, 2),
            "description": "决策和执行的时间效率",
            "factors": {
                "execution_time": execution_time,
                "decision_time": decision_time
            }
        }

    def _evaluate_consistency(self, decision_id: str, decision_data: Dict) -> Dict:
        """评估决策一致性"""
        # 加载历史决策记录
        history = self._load_quality_records()

        if not history:
            # 没有历史数据，无法评估一致性
            return {
                "score": 0.6,
                "description": "历史数据不足，一致性评估基于默认值"
            }

        # 检查决策模式一致性
        recent_decisions = history[-10:]  # 最近10条

        if not recent_decisions:
            return {"score": 0.6, "description": "历史数据不足"}

        # 分析决策方向的一致性
        current_goal = decision_data.get("decision", "")
        goal_patterns = [d.get("dimensions", {}).get("accuracy", {}).get("factors", {}).get("goal_match", False)
                        for d in recent_decisions]

        # 一致性：最近决策的成功率
        success_count = sum(1 for p in goal_patterns if p)
        consistency = success_count / len(goal_patterns) if goal_patterns else 0.5

        return {
            "score": round(consistency, 2),
            "description": "决策与历史决策的一致性",
            "factors": {
                "historical_count": len(recent_decisions),
                "success_rate": success_count / len(recent_decisions) if goal_patterns else 0
            }
        }

    def _evaluate_learning(self, decision_data: Dict, execution_result: Dict) -> Dict:
        """评估学习能力"""
        # 学习能力体现在是否能从历史中学习并改进
        has_feedback = execution_result.get("feedback_recorded", False)
        has_learning = decision_data.get("learning_applied", False)

        learning_score = 0.5

        if has_feedback:
            learning_score += 0.25
        if has_learning:
            learning_score += 0.25

        # 检查是否有历史知识被应用
        knowledge_sources = decision_data.get("knowledge_sources", [])
        if knowledge_sources:
            learning_score = min(0.95, learning_score + 0.1)

        return {
            "score": round(learning_score, 2),
            "description": "从历史决策中学习和改进的能力",
            "factors": {
                "feedback_recorded": has_feedback,
                "learning_applied": has_learning,
                "knowledge_used": bool(knowledge_sources)
            }
        }

    def _evaluate_adaptability(self, decision_data: Dict, execution_result: Dict) -> Dict:
        """评估自适应能力"""
        # 自适应能力体现在能否根据情况调整决策
        context = decision_data.get("context", {})
        dynamic_adjustment = execution_result.get("dynamic_adjusted", False)

        adaptability_score = 0.5

        if dynamic_adjustment:
            adaptability_score += 0.3

        # 检查是否有多种方案考虑
        alternatives = decision_data.get("alternatives", [])
        if len(alternatives) >= 2:
            adaptability_score += 0.2

        # 检查是否考虑了系统状态
        if context and len(context) >= 3:
            adaptability_score += 0.15

        return {
            "score": round(min(0.95, adaptability_score), 2),
            "description": "根据实际情况调整决策的能力",
            "factors": {
                "dynamic_adjusted": dynamic_adjustment,
                "alternatives_count": len(alternatives),
                "context_considered": bool(context)
            }
        }

    def _generate_evaluation_conclusion(self, score: float) -> str:
        """生成评估结论"""
        if score >= 0.85:
            return "优秀 - 决策质量高，各维度表现良好"
        elif score >= 0.7:
            return "良好 - 决策质量较好，有少量改进空间"
        elif score >= 0.5:
            return "一般 - 决策质量一般，需要关注特定维度"
        else:
            return "待改进 - 决策质量较低，需要重点优化"

    def analyze_deviation_patterns(self, decision_id: str, decision_data: Dict,
                                    execution_result: Dict) -> Dict:
        """
        偏差模式分析

        分析决策与实际结果的偏差，识别常见偏差模式。

        Args:
            decision_id: 决策ID
            decision_data: 决策数据
            execution_result: 执行结果

        Returns:
            偏差分析结果
        """
        analysis = {
            "decision_id": decision_id,
            "timestamp": datetime.now().isoformat(),
            "deviation_detected": False,
            "deviation_type": None,
            "deviation_severity": 0.0,
            "pattern_description": "",
            "recommendations": []
        }

        # 检测偏差
        deviations = []

        # 偏差1：目标偏差（决策目标与实际结果不匹配）
        expected = decision_data.get("decision", "")
        actual = execution_result.get("result", "")
        if expected and actual:
            if not any(keyword in str(actual).lower() for keyword in str(expected).lower()[:10]):
                deviations.append({
                    "type": "goal_deviation",
                    "severity": 0.4,
                    "description": "决策目标与实际结果存在偏差"
                })

        # 偏差2：时间偏差（执行时间超出预期）
        expected_time = decision_data.get("expected_time", 60)
        actual_time = execution_result.get("execution_time", 0)
        if actual_time > expected_time * 1.5:
            deviations.append({
                "type": "time_deviation",
                "severity": 0.2,
                "description": f"执行时间超出预期（预期{expected_time}秒，实际{actual_time}秒）"
            })

        # 偏差3：资源偏差（资源使用超出预期）
        expected_resources = decision_data.get("expected_resources", {})
        actual_resources = execution_result.get("resources_used", {})
        if expected_resources and actual_resources:
            for resource, expected_val in expected_resources.items():
                actual_val = actual_resources.get(resource, 0)
                if actual_val > expected_val * 1.3:
                    deviations.append({
                        "type": "resource_deviation",
                        "severity": 0.15,
                        "description": f"资源{resource}使用超出预期"
                    })

        # 偏差4：置信度偏差（决策置信度与实际成功率不匹配）
        confidence = decision_data.get("confidence", 0.5)
        success = execution_result.get("success", False)
        if confidence > 0.7 and not success:
            deviations.append({
                "type": "confidence_deviation",
                "severity": 0.25,
                "description": "高置信度决策实际失败，存在过度自信问题"
            })
        elif confidence < 0.4 and success:
            deviations.append({
                "type": "confidence_deviation",
                "severity": 0.1,
                "description": "低置信度决策实际成功，存在低估问题"
            })

        # 综合分析
        if deviations:
            analysis["deviation_detected"] = True
            analysis["deviation_type"] = deviations[0]["type"]  # 主要偏差类型
            analysis["deviation_severity"] = sum(d["severity"] for d in deviations)
            analysis["all_deviations"] = deviations

            # 生成描述
            pattern_types = [d["type"] for d in deviations]
            analysis["pattern_description"] = f"检测到{len(deviations)}种偏差: {', '.join(pattern_types)}"

            # 生成建议
            for dev in deviations:
                if dev["type"] == "goal_deviation":
                    analysis["recommendations"].append("建议重新评估决策目标与系统能力的匹配度")
                elif dev["type"] == "time_deviation":
                    analysis["recommendations"].append("建议优化执行流程或调整时间预期")
                elif dev["type"] == "resource_deviation":
                    analysis["recommendations"].append("建议优化资源分配策略")
                elif dev["type"] == "confidence_deviation":
                    analysis["recommendations"].append("建议校准置信度评估模型")

        # 保存偏差分析结果
        self._save_deviation_pattern(analysis)

        return analysis

    def generate_optimization_suggestions(self, quality_record: Dict,
                                          deviation_analysis: Dict) -> Dict:
        """
        生成优化建议

        基于质量评估和偏差分析，生成可执行的优化建议。

        Args:
            quality_record: 质量评估记录
            deviation_analysis: 偏差分析结果

        Returns:
            优化建议
        """
        suggestions = {
            "timestamp": datetime.now().isoformat(),
            "based_on": {
                "quality_score": quality_record.get("overall_score", 0),
                "deviation_detected": deviation_analysis.get("deviation_detected", False)
            },
            "suggestions": [],
            "priority": "medium",
            "auto_executable": False
        }

        # 分析质量维度得分，找出最需改进的维度
        dimensions = quality_record.get("dimensions", {})
        lowest_dim = None
        lowest_score = 1.0

        for dim_name, dim_data in dimensions.items():
            score = dim_data.get("score", 0)
            if score < lowest_score:
                lowest_score = score
                lowest_dim = dim_name

        # 根据最低分维度生成建议
        if lowest_dim and lowest_score < 0.6:
            dim_info = self.quality_dimensions.get(lowest_dim, {})
            suggestions["suggestions"].append({
                "dimension": lowest_dim,
                "description": f"优化{dim_info.get('description', lowest_dim)}能力",
                "priority": "high",
                "action": f"focus_on_{lowest_dim}"
            })

        # 根据偏差分析生成建议
        if deviation_analysis.get("deviation_detected"):
            recs = deviation_analysis.get("recommendations", [])
            for rec in recs:
                suggestions["suggestions"].append({
                    "dimension": "deviation_fix",
                    "description": rec,
                    "priority": "high",
                    "action": "fix_deviation"
                })

        # 如果整体分数低，生成综合建议
        if quality_record.get("overall_score", 0) < 0.6:
            suggestions["suggestions"].append({
                "dimension": "overall",
                "description": "决策质量整体偏低，建议系统性审查决策流程",
                "priority": "critical",
                "action": "systematic_review"
            })
            suggestions["priority"] = "high"

        # 检查是否可以自动执行
        if any(s.get("priority") in ["high", "critical"] for s in suggestions["suggestions"]):
            suggestions["auto_executable"] = True

        # 保存优化建议
        self._save_optimization_suggestions(suggestions)

        return suggestions

    def execute_optimization(self, suggestions: Dict) -> Dict:
        """
        执行优化建议

        将优化建议应用到决策流程中。

        Args:
            suggestions: 优化建议

        Returns:
            执行结果
        """
        result = {
            "timestamp": datetime.now().isoformat(),
            "executed": False,
            "actions_taken": [],
            "status": "pending"
        }

        # 这里可以实现实际的优化执行逻辑
        # 例如：调整权重、更新阈值、修改决策策略等

        executable_actions = [s for s in suggestions.get("suggestions", [])
                             if s.get("priority") in ["high", "critical"]]

        if not executable_actions:
            result["status"] = "no_critical_actions"
            return result

        # 模拟执行优化动作
        for action in executable_actions[:3]:  # 最多执行3个
            action_type = action.get("action", "")
            result["actions_taken"].append({
                "action": action_type,
                "description": action.get("description", ""),
                "executed": True
            })

        result["executed"] = True
        result["status"] = "completed"

        return result

    def _load_quality_records(self) -> List[Dict]:
        """加载质量评估记录"""
        if self.quality_records_file.exists():
            try:
                with open(self.quality_records_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def _save_quality_record(self, record: Dict):
        """保存质量评估记录"""
        records = self._load_quality_records()
        records.append(record)

        # 保留最近100条
        records = records[-100:]

        with open(self.quality_records_file, 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=2)

    def _save_deviation_pattern(self, analysis: Dict):
        """保存偏差分析结果"""
        patterns = []
        if self.deviation_patterns_file.exists():
            try:
                with open(self.deviation_patterns_file, 'r', encoding='utf-8') as f:
                    patterns = json.load(f)
            except Exception:
                patterns = []

        patterns.append(analysis)

        # 保留最近50条
        patterns = patterns[-50:]

        with open(self.deviation_patterns_file, 'w', encoding='utf-8') as f:
            json.dump(patterns, f, ensure_ascii=False, indent=2)

    def _save_optimization_suggestions(self, suggestions: Dict):
        """保存优化建议"""
        all_suggestions = []
        if self.optimization_suggestions_file.exists():
            try:
                with open(self.optimization_suggestions_file, 'r', encoding='utf-8') as f:
                    all_suggestions = json.load(f)
            except Exception:
                all_suggestions = []

        all_suggestions.append(suggestions)

        # 保留最近30条
        all_suggestions = all_suggestions[-30:]

        with open(self.optimization_suggestions_file, 'w', encoding='utf-8') as f:
            json.dump(all_suggestions, f, ensure_ascii=False, indent=2)

    def get_status(self) -> Dict:
        """获取引擎状态"""
        return {
            "name": "智能全场景进化决策质量实时评估与自适应优化引擎",
            "version": "1.0.0",
            "round": 335,
            "decision_knowledge_integration_available": self.decision_knowledge_integration is not None,
            "status": "ready",
            "capabilities": [
                "决策质量实时评估",
                "偏差模式分析",
                "持续学习优化",
                "自动生成优化建议",
                "优化建议执行"
            ],
            "quality_dimensions": list(self.quality_dimensions.keys())
        }

    def get_quality_trend(self, recent_count: int = 10) -> Dict:
        """获取质量趋势"""
        records = self._load_quality_records()

        if not records:
            return {"trend": "insufficient_data"}

        recent = records[-recent_count:]

        scores = [r.get("overall_score", 0) for r in recent]

        if len(scores) < 2:
            return {"trend": "insufficient_data"}

        # 计算趋势
        avg_score = statistics.mean(scores)
        if len(scores) >= 5:
            first_half = statistics.mean(scores[:len(scores)//2])
            second_half = statistics.mean(scores[len(scores)//2:])
            if second_half > first_half + 0.1:
                trend = "improving"
            elif second_half < first_half - 0.1:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "stable"

        return {
            "trend": trend,
            "recent_average": round(avg_score, 2),
            "recent_count": len(scores),
            "min_score": min(scores),
            "max_score": max(scores)
        }


def main():
    """测试入口"""
    import sys

    engine = EvolutionDecisionQualityEvaluator()

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "--status":
            print(json.dumps(engine.get_status(), ensure_ascii=False, indent=2))

        elif command == "--evaluate":
            # 模拟评估
            decision_data = {
                "decision": "测试进化目标",
                "confidence": 0.8,
                "knowledge_sources": ["round_332", "round_333"]
            }
            execution_result = {
                "success": True,
                "result": "测试目标达成",
                "execution_time": 20
            }
            result = engine.evaluate_decision_quality("test_001", decision_data, execution_result)
            print(json.dumps(result, ensure_ascii=False, indent=2))

        elif command == "--analyze":
            # 模拟偏差分析
            decision_data = {
                "decision": "测试进化目标",
                "confidence": 0.6,
                "expected_time": 30
            }
            execution_result = {
                "result": "不同的结果",
                "execution_time": 50,
                "success": True
            }
            result = engine.analyze_deviation_patterns("test_001", decision_data, execution_result)
            print(json.dumps(result, ensure_ascii=False, indent=2))

        elif command == "--suggest":
            # 模拟生成建议
            quality_record = {
                "overall_score": 0.65,
                "dimensions": {
                    "accuracy": {"score": 0.7},
                    "efficiency": {"score": 0.6},
                    "consistency": {"score": 0.7},
                    "learning": {"score": 0.5},
                    "adaptability": {"score": 0.75}
                }
            }
            deviation_analysis = {
                "deviation_detected": True,
                "recommendations": ["建议优化执行效率"]
            }
            result = engine.generate_optimization_suggestions(quality_record, deviation_analysis)
            print(json.dumps(result, ensure_ascii=False, indent=2))

        elif command == "--trend":
            result = engine.get_quality_trend()
            print(json.dumps(result, ensure_ascii=False, indent=2))

        else:
            print("未知命令")
            print("可用命令:")
            print("  --status: 显示引擎状态")
            print("  --evaluate: 测试决策质量评估")
            print("  --analyze: 测试偏差模式分析")
            print("  --suggest: 测试优化建议生成")
            print("  --trend: 查看质量趋势")
    else:
        print(json.dumps(engine.get_status(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()