#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环元进化系统自省与智能决策增强引擎

在 round 595 完成的跨维度智能自主闭环驱动能力基础上，构建更深层次的自省能力与智能决策增强。
让系统能够主动反思跨维度融合决策的有效性，评估融合效果，生成智能优化建议，
形成「自省→决策→执行→验证」的完整闭环。系统不仅能执行融合，还能思考融合决策的质量、
识别决策中的偏差、优化决策过程，实现真正的元进化自省能力。

Version: 1.0.0
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
import subprocess

# 项目根目录
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
RUNTIME_DIR = PROJECT_ROOT / "runtime"
STATE_DIR = RUNTIME_DIR / "state"
LOGS_DIR = RUNTIME_DIR / "logs"


class MetaSelfReflectionIntelligentDecisionEngine:
    """元进化系统自省与智能决策增强引擎"""

    def __init__(self):
        self.name = "元进化系统自省与智能决策增强引擎"
        self.version = "1.0.0"
        self.state_dir = STATE_DIR
        self.logs_dir = LOGS_DIR
        self.data_file = self.state_dir / "meta_self_reflection_decision_data.json"

    def reflect_on_fusion_decisions(self):
        """
        跨维度融合决策自省
        分析跨维度融合决策的有效性，识别低效决策模式
        """
        reflection = {
            "timestamp": datetime.now().isoformat(),
            "decision_analysis": {},
            "inefficiency_patterns": [],
            "insights": []
        }

        try:
            # 1. 读取跨维度智能自主闭环驱动引擎的执行数据
            fusion_loop_data = self._load_fusion_loop_data()
            reflection["fusion_data"] = fusion_loop_data

            # 2. 分析决策有效性
            decision_analysis = self._analyze_decision_effectiveness(fusion_loop_data)
            reflection["decision_analysis"] = decision_analysis

            # 3. 识别低效决策模式
            inefficiency_patterns = self._identify_inefficiency_patterns(decision_analysis)
            reflection["inefficiency_patterns"] = inefficiency_patterns

            # 4. 生成自省洞察
            reflection["insights"] = self._generate_reflection_insights(
                decision_analysis,
                inefficiency_patterns
            )

        except Exception as e:
            print(f"[ERROR] 跨维度融合决策自省失败: {e}")
            reflection["error"] = str(e)

        return reflection

    def _load_fusion_loop_data(self):
        """加载跨维度融合循环数据"""
        data = {}

        # 尝试读取跨维度智能自主闭环驱动引擎的数据
        fusion_data_file = self.state_dir / "cross_dimension_autonomous_loop_data.json"
        if fusion_data_file.exists():
            try:
                with open(fusion_data_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception as e:
                print(f"[WARN] 读取融合数据失败: {e}")

        return data

    def _analyze_decision_effectiveness(self, fusion_data):
        """分析决策有效性"""
        analysis = {
            "total_decisions": 0,
            "effective_decisions": 0,
            "ineffective_decisions": 0,
            "decision_quality_score": 0.0,
            "analysis_details": []
        }

        try:
            # 检查融合循环历史
            evolution_history = fusion_data.get("evolution_history", [])

            if not evolution_history:
                # 如果没有历史数据，基于当前状态生成默认分析
                analysis["analysis_details"].append({
                    "type": "default",
                    "description": "暂无融合循环历史数据，使用默认评估",
                    "recommendation": "建议先运行跨维度智能自主闭环驱动引擎"
                })
                analysis["decision_quality_score"] = 0.6
            else:
                analysis["total_decisions"] = len(evolution_history)

                # 分析每个决策
                for item in evolution_history:
                    if item.get("learning_results"):
                        analysis["effective_decisions"] += len(item["learning_results"])

                # 评估整体决策质量
                if analysis["total_decisions"] > 0:
                    quality_ratio = analysis["effective_decisions"] / analysis["total_decisions"]
                    analysis["decision_quality_score"] = min(quality_ratio * 1.2, 1.0)

                    analysis["analysis_details"].append({
                        "type": "quality_assessment",
                        "description": f"基于 {analysis['total_decisions']} 个决策的分析",
                        "effective_count": analysis["effective_decisions"],
                        "quality_ratio": quality_ratio
                    })

        except Exception as e:
            print(f"[WARN] 分析决策有效性失败: {e}")

        return analysis

    def _identify_inefficiency_patterns(self, decision_analysis):
        """识别低效决策模式"""
        patterns = []

        try:
            quality_score = decision_analysis.get("decision_quality_score", 0.6)

            # 根据决策质量识别模式
            if quality_score < 0.5:
                patterns.append({
                    "type": "low_quality_decisions",
                    "description": "决策质量偏低",
                    "severity": "high",
                    "root_cause": "可能是融合策略不当或评估标准不准确",
                    "recommendation": "需要重新审视融合决策的评估标准"
                })

            if quality_score < 0.7:
                patterns.append({
                    "type": "inefficient_optimization",
                    "description": "优化效率有待提升",
                    "severity": "medium",
                    "root_cause": "优化行动的针对性不足",
                    "recommendation": "增强优化策略的精准性"
                })

            # 检查历史数据
            total = decision_analysis.get("total_decisions", 0)
            if total < 5:
                patterns.append({
                    "type": "insufficient_history",
                    "description": "决策历史数据不足",
                    "severity": "low",
                    "root_cause": "跨维度融合执行次数较少",
                    "recommendation": "积累更多执行数据以供分析"
                })

            # 检查有效决策比例
            effective = decision_analysis.get("effective_decisions", 0)
            if total > 0 and effective / total < 0.6:
                patterns.append({
                    "type": "low_success_rate",
                    "description": "决策成功率偏低",
                    "severity": "medium",
                    "root_cause": "可能是决策标准过于宽松或执行不当",
                    "recommendation": "加强决策验证和执行监控"
                })

        except Exception as e:
            print(f"[WARN] 识别低效模式失败: {e}")

        return patterns

    def _generate_reflection_insights(self, decision_analysis, inefficiency_patterns):
        """生成自省洞察"""
        insights = []

        try:
            # 基于决策质量生成洞察
            quality_score = decision_analysis.get("decision_quality_score", 0.6)

            if quality_score >= 0.8:
                insights.append({
                    "category": "positive",
                    "title": "决策质量优秀",
                    "description": "跨维度融合决策整体质量较高，系统运行稳定"
                })
            elif quality_score >= 0.6:
                insights.append({
                    "category": "neutral",
                    "title": "决策质量良好",
                    "description": "跨维度融合决策整体良好，存在小幅改进空间"
                })
            else:
                insights.append({
                    "category": "improvement",
                    "title": "决策质量需提升",
                    "description": "建议重点关注决策标准和执行过程"
                })

            # 基于低效模式生成洞察
            high_severity = [p for p in inefficiency_patterns if p.get("severity") == "high"]
            if high_severity:
                insights.append({
                    "category": "attention",
                    "title": "发现高优先级问题",
                    "description": f"发现 {len(high_severity)} 个高优先级低效模式需要立即处理"
                })

            # 生成综合建议
            if inefficiency_patterns:
                recommendations = [p.get("recommendation", "") for p in inefficiency_patterns[:3]]
                insights.append({
                    "category": "recommendation",
                    "title": "优化建议",
                    "description": "; ".join(recommendations)
                })

        except Exception as e:
            print(f"[WARN] 生成自省洞察失败: {e}")

        return insights

    def evaluate_fusion_effectiveness(self):
        """
        融合效果自动评估
        评估融合后系统的整体表现和能力提升
        """
        evaluation = {
            "timestamp": datetime.now().isoformat(),
            "overall_performance": 0.0,
            "capability_improvements": [],
            "detailed_metrics": {},
            "evaluation_summary": ""
        }

        try:
            # 1. 加载跨维度融合数据
            fusion_data = self._load_fusion_loop_data()

            # 2. 评估各维度能力提升
            capability_assessment = self._assess_capability_improvements(fusion_data)
            evaluation["capability_improvements"] = capability_assessment

            # 3. 计算整体性能得分
            evaluation["overall_performance"] = self._calculate_overall_performance(
                capability_assessment
            )

            # 4. 生成详细指标
            evaluation["detailed_metrics"] = self._generate_detailed_metrics(
                capability_assessment,
                evaluation["overall_performance"]
            )

            # 5. 生成评估总结
            evaluation["evaluation_summary"] = self._generate_evaluation_summary(
                evaluation["overall_performance"],
                capability_assessment
            )

        except Exception as e:
            print(f"[ERROR] 融合效果评估失败: {e}")
            evaluation["error"] = str(e)

        return evaluation

    def _assess_capability_improvements(self, fusion_data):
        """评估能力提升"""
        improvements = []

        # 定义评估维度
        dimensions = [
            {"name": "value_driven", "description": "价值驱动能力"},
            {"name": "innovation", "description": "创新涌现能力"},
            {"name": "knowledge_graph", "description": "知识图谱能力"},
            {"name": "self_awareness", "description": "自我意识能力"},
            {"name": "meta_evolution", "description": "元进化决策能力"}
        ]

        for dim in dimensions:
            # 检查该维度的历史数据
            dim_data = fusion_data.get(dim["name"], {})
            score = dim_data.get("score", 0.5) if dim_data else 0.5

            improvements.append({
                "dimension": dim["name"],
                "description": dim["description"],
                "score": score,
                "status": "good" if score >= 0.6 else "needs_improvement"
            })

        return improvements

    def _calculate_overall_performance(self, capability_improvements):
        """计算整体性能得分"""
        if not capability_improvements:
            return 0.5

        total = sum(item.get("score", 0) for item in capability_improvements)
        return total / len(capability_improvements) if capability_improvements else 0.5

    def _generate_detailed_metrics(self, capability_assessment, overall_performance):
        """生成详细指标"""
        metrics = {
            "total_dimensions": len(capability_assessment),
            "good_dimensions": sum(1 for item in capability_assessment if item.get("status") == "good"),
            "needs_improvement_dimensions": sum(
                1 for item in capability_assessment if item.get("status") == "needs_improvement"
            ),
            "overall_performance": overall_performance,
            "performance_grade": self._get_performance_grade(overall_performance)
        }

        return metrics

    def _get_performance_grade(self, performance):
        """获取性能等级"""
        if performance >= 0.9:
            return "A+"
        elif performance >= 0.8:
            return "A"
        elif performance >= 0.7:
            return "B+"
        elif performance >= 0.6:
            return "B"
        elif performance >= 0.5:
            return "C"
        else:
            return "D"

    def _generate_evaluation_summary(self, overall_performance, capability_assessment):
        """生成评估总结"""
        grade = self._get_performance_grade(overall_performance)

        good_count = sum(
            1 for item in capability_assessment if item.get("status") == "good"
        )
        total_count = len(capability_assessment)

        summary = f"整体性能得分: {overall_performance:.2f} (等级: {grade})。 "
        summary += f"维度评估: {good_count}/{total_count} 个维度表现良好。 "

        if overall_performance >= 0.8:
            summary += "跨维度融合效果优秀，系统运行稳定高效。"
        elif overall_performance >= 0.6:
            summary += "跨维度融合效果良好，存在小幅改进空间。"
        elif overall_performance >= 0.4:
            summary += "跨维度融合效果一般，建议重点优化。"
        else:
            summary += "跨维度融合效果较差，需要立即优化改进。"

        return summary

    def generate_intelligent_suggestions(self, reflection, evaluation):
        """
        智能优化建议生成
        基于自省和评估结果生成可执行的优化方案
        """
        suggestions = {
            "timestamp": datetime.now().isoformat(),
            "suggestions": [],
            "priority_suggestions": [],
            "implementation_plan": []
        }

        try:
            # 1. 基于自省结果生成建议
            reflection_suggestions = self._generate_from_reflection(reflection)
            suggestions["suggestions"].extend(reflection_suggestions)

            # 2. 基于评估结果生成建议
            evaluation_suggestions = self._generate_from_evaluation(evaluation)
            suggestions["suggestions"].extend(evaluation_suggestions)

            # 3. 优先级排序
            suggestions["priority_suggestions"] = self._prioritize_suggestions(
                suggestions["suggestions"]
            )

            # 4. 生成实施计划
            suggestions["implementation_plan"] = self._create_implementation_plan(
                suggestions["priority_suggestions"]
            )

        except Exception as e:
            print(f"[ERROR] 生成智能建议失败: {e}")

        return suggestions

    def _generate_from_reflection(self, reflection):
        """基于自省结果生成建议"""
        suggestions = []

        # 基于低效模式生成建议
        patterns = reflection.get("inefficiency_patterns", [])
        for pattern in patterns:
            severity = pattern.get("severity", "low")

            suggestion = {
                "type": "reflection_based",
                "title": pattern.get("description", ""),
                "description": pattern.get("recommendation", ""),
                "severity": severity,
                "category": "self_improvement"
            }
            suggestions.append(suggestion)

        return suggestions

    def _generate_from_evaluation(self, evaluation):
        """基于评估结果生成建议"""
        suggestions = []

        # 基于能力提升评估生成建议
        improvements = evaluation.get("capability_improvements", [])

        for item in improvements:
            if item.get("status") == "needs_improvement":
                suggestion = {
                    "type": "evaluation_based",
                    "title": f"提升 {item.get('description', '能力')}",
                    "description": f"当前 {item.get('description')} 得分偏低({item.get('score', 0):.2f})，建议重点优化",
                    "severity": "medium",
                    "category": "capability_enhancement"
                }
                suggestions.append(suggestion)

        return suggestions

    def _prioritize_suggestions(self, suggestions):
        """对建议进行优先级排序"""
        if not suggestions:
            return []

        # 优先级权重
        severity_weight = {
            "high": 3,
            "medium": 2,
            "low": 1
        }

        # 排序
        prioritized = sorted(
            suggestions,
            key=lambda x: severity_weight.get(x.get("severity", "low"), 1),
            reverse=True
        )

        # 取前5条
        return prioritized[:5]

    def _create_implementation_plan(self, priority_suggestions):
        """创建实施计划"""
        plan = []

        for i, suggestion in enumerate(priority_suggestions, 1):
            plan.append({
                "step": i,
                "action": suggestion.get("title", ""),
                "description": suggestion.get("description", ""),
                "suggestion_type": suggestion.get("type", ""),
                "estimated_impact": "high" if suggestion.get("severity") == "high" else "medium"
            })

        return plan

    def run_self_reflection_loop(self):
        """
        运行完整的自省与决策增强流程
        「自省→评估→建议→优化」的完整闭环
        """
        loop_result = {
            "timestamp": datetime.now().isoformat(),
            "loop_round": self._get_loop_round(),
            "steps": {}
        }

        print("=" * 60)
        print("元进化系统自省与智能决策增强 - 开始运行")
        print("=" * 60)

        # 步骤1: 跨维度融合决策自省
        print("\n[步骤1] 跨维度融合决策自省...")
        reflection = self.reflect_on_fusion_decisions()
        loop_result["steps"]["reflection"] = reflection
        print(f"  识别到 {len(reflection.get('inefficiency_patterns', []))} 个低效模式")
        print(f"  生成 {len(reflection.get('insights', []))} 条自省洞察")

        # 步骤2: 融合效果自动评估
        print("\n[步骤2] 融合效果自动评估...")
        evaluation = self.evaluate_fusion_effectiveness()
        loop_result["steps"]["evaluation"] = evaluation
        print(f"  整体性能得分: {evaluation.get('overall_performance', 0):.2f}")
        print(f"  评估总结: {evaluation.get('evaluation_summary', 'N/A')[:50]}...")

        # 步骤3: 智能优化建议生成
        print("\n[步骤3] 智能优化建议生成...")
        suggestions = self.generate_intelligent_suggestions(reflection, evaluation)
        loop_result["steps"]["suggestions"] = suggestions
        print(f"  生成 {len(suggestions.get('suggestions', []))} 条优化建议")
        print(f"  优先建议: {len(suggestions.get('priority_suggestions', []))} 条")

        # 保存结果
        self._save_loop_result(loop_result)

        print("\n" + "=" * 60)
        print("元进化系统自省与智能决策增强 - 运行完成")
        print("=" * 60)

        return loop_result

    def _get_loop_round(self):
        """获取当前循环轮次"""
        try:
            mission_file = self.state_dir / "current_mission.json"
            if mission_file.exists():
                with open(mission_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get("loop_round", 596)
        except:
            pass
        return 596

    def _save_loop_result(self, result):
        """保存循环结果"""
        try:
            # 保存到数据文件
            existing_data = {}
            if self.data_file.exists():
                with open(self.data_file, "r", encoding="utf-8") as f:
                    existing_data = json.load(f)

            if "loop_history" not in existing_data:
                existing_data["loop_history"] = []

            existing_data["loop_history"].append(result)

            # 保留最近20条记录
            existing_data["loop_history"] = existing_data["loop_history"][-20:]

            # 更新最新结果
            existing_data["latest"] = result

            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(existing_data, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"[WARN] 保存循环结果失败: {e}")

    def get_cockpit_data(self):
        """获取驾驶舱数据"""
        try:
            # 运行自省循环获取最新数据
            reflection = self.reflect_on_fusion_decisions()
            evaluation = self.evaluate_fusion_effectiveness()
            suggestions = self.generate_intelligent_suggestions(reflection, evaluation)

            return {
                "engine_name": self.name,
                "version": self.version,
                "decision_quality_score": reflection.get("decision_analysis", {}).get(
                    "decision_quality_score", 0
                ),
                "overall_performance": evaluation.get("overall_performance", 0),
                "inefficiency_patterns_count": len(reflection.get("inefficiency_patterns", [])),
                "suggestions_count": len(suggestions.get("priority_suggestions", [])),
                "evaluation_summary": evaluation.get("evaluation_summary", ""),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "engine_name": self.name,
                "version": self.version,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(
        description="智能全场景进化环元进化系统自省与智能决策增强引擎"
    )
    parser.add_argument("--version", action="store_true", help="显示版本信息")
    parser.add_argument("--status", action="store_true", help="显示引擎状态")
    parser.add_argument("--reflect", action="store_true", help="执行跨维度融合决策自省")
    parser.add_argument("--evaluate", action="store_true", help="执行融合效果自动评估")
    parser.add_argument("--suggest", action="store_true", help="生成智能优化建议")
    parser.add_argument("--run", action="store_true", help="运行完整自省与决策增强流程")
    parser.add_argument("--cockpit-data", action="store_true", help="获取驾驶舱数据")

    args = parser.parse_args()

    engine = MetaSelfReflectionIntelligentDecisionEngine()

    if args.version:
        print(f"{engine.name} v{engine.version}")

    elif args.status:
        data = engine.get_cockpit_data()
        print(json.dumps(data, ensure_ascii=False, indent=2))

    elif args.reflect:
        result = engine.reflect_on_fusion_decisions()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.evaluate:
        result = engine.evaluate_fusion_effectiveness()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.suggest:
        reflection = engine.reflect_on_fusion_decisions()
        evaluation = engine.evaluate_fusion_effectiveness()
        result = engine.generate_intelligent_suggestions(reflection, evaluation)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.run:
        result = engine.run_self_reflection_loop()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.cockpit_data:
        data = engine.get_cockpit_data()
        print(json.dumps(data, ensure_ascii=False, indent=2))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()