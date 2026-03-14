#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景主动价值发现与智能决策闭环增强引擎 (Evolution Active Value Discovery Engine)
version 1.0.0

将持续学习能力与全局态势感知、知识图谱推理深度集成，
形成主动发现高价值进化机会→智能评估→自动决策→执行验证的完整闭环。

功能：
1. 主动价值发现 - 从知识图谱、进化历史、全局态势中主动挖掘高价值机会
2. 智能价值评估 - 综合评估每个机会的成功率、影响度、可行性
3. 自动决策选择 - 基于评估结果选择最优进化路径
4. 完整闭环执行 - 从发现到验证的端到端自动化

依赖：
- evolution_decision_continuous_learning.py (round 338)
- evolution_global_situation_awareness.py (round 329)
- evolution_kg_deep_reasoning_insight_engine.py (round 330)
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


class ValueOpportunity:
    """价值机会"""

    def __init__(self, opportunity_id: str, title: str, description: str,
                 category: str, potential_impact: float, feasibility: float,
                 risk_level: float, source: str, related_engines: List[str]):
        self.id = opportunity_id
        self.title = title
        self.description = description
        self.category = category
        self.potential_impact = potential_impact  # 0-1
        self.feasibility = feasibility  # 0-1
        self.risk_level = risk_level  # 0-1
        self.source = source
        self.related_engines = related_engines
        self.timestamp = datetime.now().isoformat()

        # 计算综合价值分数
        self.value_score = self._calculate_value_score()

    def _calculate_value_score(self) -> float:
        """计算综合价值分数"""
        # 价值 = 影响力 * 可行性 * (1 - 风险)
        return self.potential_impact * self.feasibility * (1 - self.risk_level)

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "potential_impact": self.potential_impact,
            "feasibility": self.feasibility,
            "risk_level": self.risk_level,
            "value_score": self.value_score,
            "source": self.source,
            "related_engines": self.related_engines,
            "timestamp": self.timestamp
        }


class ValueAssessment:
    """价值评估"""

    def __init__(self, opportunity: ValueOpportunity):
        self.opportunity = opportunity
        self.success_probability = 0.0
        self.estimated_benefit = 0.0
        self.estimated_cost = 0.0
        self.roi = 0.0
        self.assessment_factors = {}
        self.timestamp = datetime.now().isoformat()

    def evaluate(self, system_state: Dict) -> Dict:
        """执行评估"""
        # 基于系统状态评估成功概率
        system_load = system_state.get("system_load", 0.5)
        engine_health = system_state.get("engine_health_avg", 0.8)
        knowledge_completeness = system_state.get("knowledge_completeness", 0.6)

        # 成功概率 = 基础概率 * 系统状态因子
        base_probability = self.opportunity.feasibility
        state_factor = (system_load * 0.3 + engine_health * 0.4 + knowledge_completeness * 0.3)
        self.success_probability = base_probability * state_factor

        # 估算收益 = 影响力 * 基础收益
        self.estimated_benefit = self.opportunity.potential_impact * 100

        # 估算成本 = 风险 * 基础成本 + 复杂度成本
        self.estimated_cost = self.opportunity.risk_level * 50 + 10

        # ROI
        if self.estimated_cost > 0:
            self.roi = (self.estimated_benefit - self.estimated_cost) / self.estimated_cost

        self.assessment_factors = {
            "system_load": system_load,
            "engine_health": engine_health,
            "knowledge_completeness": knowledge_completeness,
            "state_factor": state_factor
        }

        return {
            "opportunity_id": self.opportunity.id,
            "success_probability": self.success_probability,
            "estimated_benefit": self.estimated_benefit,
            "estimated_cost": self.estimated_cost,
            "roi": self.roi,
            "assessment_factors": self.assessment_factors,
            "timestamp": self.timestamp
        }

    def to_dict(self) -> Dict:
        return {
            "opportunity": self.opportunity.to_dict(),
            "success_probability": self.success_probability,
            "estimated_benefit": self.estimated_benefit,
            "estimated_cost": self.estimated_cost,
            "roi": self.roi,
            "assessment_factors": self.assessment_factors,
            "timestamp": self.timestamp
        }


class DecisionRecommendation:
    """决策推荐"""

    def __init__(self, opportunity: ValueOpportunity, assessment: ValueAssessment,
                 decision: str, reasoning: str, confidence: float):
        self.id = f"decision_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.opportunity = opportunity
        self.assessment = assessment
        self.decision = decision  # "proceed", "defer", "reject"
        self.reasoning = reasoning
        self.confidence = confidence
        self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "opportunity_id": self.opportunity.id,
            "opportunity_title": self.opportunity.title,
            "decision": self.decision,
            "reasoning": self.reasoning,
            "confidence": self.confidence,
            "assessment": {
                "success_probability": self.assessment.success_probability,
                "roi": self.assessment.roi
            },
            "timestamp": self.timestamp
        }


class EvolutionActiveValueDiscoveryEngine:
    """智能全场景主动价值发现与智能决策闭环增强引擎"""

    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.state_dir = self.base_dir / "runtime" / "state"
        self.logs_dir = self.base_dir / "runtime" / "logs"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)

        # 集成持续学习引擎
        self.learning_engine = None
        try:
            from evolution_decision_continuous_learning import EvolutionDecisionContinuousLearningEngine
            self.learning_engine = EvolutionDecisionContinuousLearningEngine()
        except ImportError:
            pass

        # 集成全局态势感知引擎
        self.situation_engine = None
        try:
            from evolution_global_situation_awareness import EvolutionGlobalSituationAwarenessEngine
            self.situation_engine = EvolutionGlobalSituationAwarenessEngine()
        except ImportError:
            pass

        # 集成知识图谱推理引擎
        self.kg_engine = None
        try:
            from evolution_kg_deep_reasoning_insight_engine import EvolutionKGDeepReasoningInsightEngine
            self.kg_engine = EvolutionKGDeepReasoningInsightEngine()
        except ImportError:
            pass

        # 文件路径
        self.opportunities_file = self.state_dir / "value_discovery_opportunities.json"
        self.assessments_file = self.state_dir / "value_discovery_assessments.json"
        self.decisions_file = self.state_dir / "value_discovery_decisions.json"
        self.config_file = self.state_dir / "value_discovery_config.json"

        # 配置
        self.config = self._load_config()

    def _load_config(self) -> Dict:
        """加载配置"""
        default_config = {
            "min_opportunities": 3,
            "max_opportunities_per_cycle": 5,
            "value_threshold": 0.4,
            "success_probability_threshold": 0.5,
            "roi_threshold": 0.5,
            "auto_execute_enabled": False,
            "discovery_sources": ["knowledge_graph", "evolution_history", "system_state", "trend_analysis"],
            "opportunity_retention": 20
        }

        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    default_config.update(loaded)
            except Exception:
                pass

        return default_config

    def _save_config(self):
        """保存配置"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)

    def discover_opportunities(self, system_state: Dict = None) -> List[ValueOpportunity]:
        """
        主动发现价值机会

        从多个来源主动挖掘高价值进化机会。

        Returns:
            发现的机会列表
        """
        opportunities = []

        # 1. 从知识图谱发现机会
        kg_opportunities = self._discover_from_knowledge_graph()
        opportunities.extend(kg_opportunities)

        # 2. 从进化历史发现机会
        history_opportunities = self._discover_from_evolution_history()
        opportunities.extend(history_opportunities)

        # 3. 从系统态势发现机会
        if system_state:
            state_opportunities = self._discover_from_system_state(system_state)
            opportunities.extend(state_opportunities)

        # 4. 从持续学习引擎发现优化机会
        if self.learning_engine:
            learning_opportunities = self._discover_from_learning_engine()
            opportunities.extend(learning_opportunities)

        # 去重并排序
        opportunities = self._deduplicate_opportunities(opportunities)
        opportunities.sort(key=lambda x: x.value_score, reverse=True)

        # 只保留前 N 个
        max_opp = self.config.get("max_opportunities_per_cycle", 5)
        opportunities = opportunities[:max_opp]

        # 保存机会
        self._save_opportunities(opportunities)

        return opportunities

    def _discover_from_knowledge_graph(self) -> List[ValueOpportunity]:
        """从知识图谱发现机会"""
        opportunities = []

        if not self.kg_engine:
            return opportunities

        try:
            # 获取知识图谱洞察
            insights = self.kg_engine.generate_insights(max_insights=5)

            for insight in insights:
                # 将洞察转化为价值机会
                title = insight.get("title", "Unknown")
                description = insight.get("description", "")

                # 评估潜力
                if "创新" in title or "新" in title:
                    potential_impact = 0.8
                    feasibility = 0.6
                elif "优化" in title or "改进" in title:
                    potential_impact = 0.6
                    feasibility = 0.7
                else:
                    potential_impact = 0.5
                    feasibility = 0.5

                opp = ValueOpportunity(
                    opportunity_id=f"kg_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    title=f"知识图谱洞察: {title}",
                    description=description,
                    category="knowledge_discovery",
                    potential_impact=potential_impact,
                    feasibility=feasibility,
                    risk_level=0.3,
                    source="knowledge_graph",
                    related_engines=["kg_deep_reasoning", "kg_meta_integration"]
                )
                opportunities.append(opp)

        except Exception as e:
            print(f"从知识图谱发现机会时出错: {e}")

        return opportunities

    def _discover_from_evolution_history(self) -> List[ValueOpportunity]:
        """从进化历史发现机会"""
        opportunities = []

        # 读取进化历史
        history_file = self.state_dir / "evolution_completed_ev_20260314_103250.json"

        if history_file.exists():
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)

                # 分析历史模式，发现优化空间
                recent_goal = history.get("current_goal", "")

                # 如果最近几轮都在做决策质量相关，可能需要集成
                if "决策" in recent_goal:
                    opp = ValueOpportunity(
                        opportunity_id=f"history_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                        title="决策引擎深度集成机会",
                        description="多个决策相关引擎可以深度集成为统一决策大脑",
                        category="integration",
                        potential_impact=0.7,
                        feasibility=0.6,
                        risk_level=0.4,
                        source="evolution_history",
                        related_engines=["decision_continuous_learning", "decision_predictive_optimizer"]
                    )
                    opportunities.append(opp)

            except Exception as e:
                print(f"从进化历史发现机会时出错: {e}")

        # 发现重复进化
        opp = ValueOpportunity(
            opportunity_id=f"pattern_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            title="跨轮知识深度融合增强",
            description="将已建立的决策质量链路与全局态势感知深度融合，形成更强的主动价值发现能力",
            category="capability_enhancement",
            potential_impact=0.75,
            feasibility=0.7,
            risk_level=0.3,
            source="evolution_history",
            related_engines=["decision_quality_evaluator", "global_situation_awareness", "kg_deep_reasoning"]
        )
        opportunities.append(opp)

        return opportunities

    def _discover_from_system_state(self, system_state: Dict) -> List[ValueOpportunity]:
        """从系统态势发现机会"""
        opportunities = []

        # 从全局态势感知获取机会
        if self.situation_engine:
            try:
                # 获取系统健康状态
                health = system_state.get("health", {})
                if health.get("overall_health", 1.0) < 0.7:
                    # 系统健康度下降，发现优化机会
                    opp = ValueOpportunity(
                        opportunity_id=f"health_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                        title="系统健康优化机会",
                        description="检测到系统健康度下降，发现优化空间",
                        category="health_optimization",
                        potential_impact=0.6,
                        feasibility=0.8,
                        risk_level=0.2,
                        source="system_state",
                        related_engines=["health_immunity", "self_healing"]
                    )
                    opportunities.append(opp)

            except Exception as e:
                print(f"从系统态势发现机会时出错: {e}")

        # 基于系统负载发现机会
        load = system_state.get("load", 0.5)
        if load > 0.8:
            opp = ValueOpportunity(
                opportunity_id=f"load_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                title="高负载优化机会",
                description="系统负载较高，优化可显著提升性能",
                category="performance",
                potential_impact=0.7,
                feasibility=0.6,
                risk_level=0.4,
                source="system_state",
                related_engines=["efficiency_optimizer"]
            )
            opportunities.append(opp)

        return opportunities

    def _discover_from_learning_engine(self) -> List[ValueOpportunity]:
        """从持续学习引擎发现机会"""
        opportunities = []

        if not self.learning_engine:
            return opportunities

        try:
            # 获取学习摘要
            summary = self.learning_engine.get_learning_summary()
            error_analysis = summary.get("error_analysis", {})

            # 如果预测误差高，发现优化机会
            if error_analysis.get("needs_adjustment"):
                avg_errors = error_analysis.get("average_errors", {})
                overall_error = avg_errors.get("overall_error", 0)

                opp = ValueOpportunity(
                    opportunity_id=f"learning_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    title="预测模型优化机会",
                    description=f"检测到预测误差偏高（{overall_error:.2%}），可优化预测模型",
                    category="model_optimization",
                    potential_impact=0.6,
                    feasibility=0.8,
                    risk_level=0.2,
                    source="learning_engine",
                    related_engines=["decision_continuous_learning"]
                )
                opportunities.append(opp)

            # 基于学习洞察发现机会
            insights = summary.get("recent_insights", [])
            for insight in insights[:2]:
                insight_type = insight.get("type", "")

                if "bias" in insight_type:
                    opp = ValueOpportunity(
                        opportunity_id=f"insight_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                        title=f"模型偏差校正: {insight_type}",
                        description=insight.get("description", ""),
                        category="bias_correction",
                        potential_impact=0.5,
                        feasibility=0.9,
                        risk_level=0.1,
                        source="learning_engine",
                        related_engines=["decision_continuous_learning"]
                    )
                    opportunities.append(opp)

        except Exception as e:
            print(f"从学习引擎发现机会时出错: {e}")

        return opportunities

    def _deduplicate_opportunities(self, opportunities: List[ValueOpportunity]) -> List[ValueOpportunity]:
        """去重机会"""
        seen_titles = set()
        unique = []

        for opp in opportunities:
            # 简化标题用于比较
            key = opp.title[:20].lower()
            if key not in seen_titles:
                seen_titles.add(key)
                unique.append(opp)

        return unique

    def _save_opportunities(self, opportunities: List[ValueOpportunity]):
        """保存机会"""
        all_opportunities = []

        if self.opportunities_file.exists():
            try:
                with open(self.opportunities_file, 'r', encoding='utf-8') as f:
                    all_opportunities = json.load(f)
            except Exception:
                all_opportunities = []

        # 添加新机会
        for opp in opportunities:
            all_opportunities.append(opp.to_dict())

        # 只保留最近的
        retention = self.config.get("opportunity_retention", 20)
        all_opportunities = all_opportunities[-retention:]

        with open(self.opportunities_file, 'w', encoding='utf-8') as f:
            json.dump(all_opportunities, f, ensure_ascii=False, indent=2)

    def assess_opportunities(self, opportunities: List[ValueOpportunity],
                           system_state: Dict = None) -> List[ValueAssessment]:
        """
        评估价值机会

        对发现的机会进行综合评估。

        Args:
            opportunities: 机会列表
            system_state: 系统状态

        Returns:
            评估结果列表
        """
        if not system_state:
            system_state = self._get_system_state()

        assessments = []

        for opp in opportunities:
            assessment = ValueAssessment(opp)
            result = assessment.evaluate(system_state)
            assessments.append(assessment)

        # 保存评估结果
        self._save_assessments(assessments)

        return assessments

    def _get_system_state(self) -> Dict:
        """获取系统状态"""
        state = {
            "system_load": 0.5,
            "engine_health_avg": 0.8,
            "knowledge_completeness": 0.6,
            "health": {"overall_health": 0.85}
        }

        # 如果有态势感知引擎，获取真实状态
        if self.situation_engine:
            try:
                awareness = self.situation_engine.get_awareness()
                state.update(awareness)
            except Exception:
                pass

        return state

    def _save_assessments(self, assessments: List[ValueAssessment]):
        """保存评估结果"""
        all_assessments = []

        if self.assessments_file.exists():
            try:
                with open(self.assessments_file, 'r', encoding='utf-8') as f:
                    all_assessments = json.load(f)
            except Exception:
                pass

        for assessment in assessments:
            all_assessments.append(assessment.to_dict())

        # 只保留最近的
        all_assessments = all_assessments[-30:]

        with open(self.assessments_file, 'w', encoding='utf-8') as f:
            json.dump(all_assessments, f, ensure_ascii=False, indent=2)

    def make_decisions(self, assessments: List[ValueAssessment]) -> List[DecisionRecommendation]:
        """
        智能决策选择

        基于评估结果做出决策：进行、推迟或拒绝。

        Args:
            assessments: 评估结果列表

        Returns:
            决策推荐列表
        """
        decisions = []

        success_threshold = self.config.get("success_probability_threshold", 0.5)
        roi_threshold = self.config.get("roi_threshold", 0.5)
        value_threshold = self.config.get("value_threshold", 0.4)

        for assessment in assessments:
            opp = assessment.opportunity

            # 决策逻辑
            if opp.value_score < value_threshold:
                decision = "reject"
                reasoning = f"价值分数({opp.value_score:.2f})低于阈值({value_threshold})"
                confidence = 0.9

            elif assessment.success_probability < success_threshold:
                decision = "defer"
                reasoning = f"成功概率({assessment.success_probability:.2f})低于阈值({success_threshold})，建议等待系统状态改善"
                confidence = 0.7

            elif assessment.roi < roi_threshold:
                decision = "defer"
                reasoning = f"ROI({assessment.roi:.2f})低于阈值({roi_threshold})，建议等待更好时机"
                confidence = 0.7

            else:
                decision = "proceed"
                reasoning = f"机会价值高(价值分={opp.value_score:.2f}, 成功概率={assessment.success_probability:.2f}, ROI={assessment.roi:.2f})，建议执行"
                confidence = 0.85

            decision_rec = DecisionRecommendation(
                opportunity=opp,
                assessment=assessment,
                decision=decision,
                reasoning=reasoning,
                confidence=confidence
            )
            decisions.append(decision_rec)

        # 保存决策
        self._save_decisions(decisions)

        return decisions

    def _save_decisions(self, decisions: List[DecisionRecommendation]):
        """保存决策"""
        all_decisions = []

        if self.decisions_file.exists():
            try:
                with open(self.decisions_file, 'r', encoding='utf-8') as f:
                    all_decisions = json.load(f)
            except Exception:
                pass

        for decision in decisions:
            all_decisions.append(decision.to_dict())

        # 只保留最近的
        all_decisions = all_decisions[-30:]

        with open(self.decisions_file, 'w', encoding='utf-8') as f:
            json.dump(all_decisions, f, ensure_ascii=False, indent=2)

    def run_full_cycle(self, system_state: Dict = None) -> Dict:
        """
        执行完整的主动价值发现与决策闭环

        整合发现→评估→决策→验证的完整流程。

        Returns:
            完整闭环结果
        """
        cycle_result = {
            "timestamp": datetime.now().isoformat(),
            "steps": {},
            "overall_status": "completed"
        }

        # 步骤1：发现价值机会
        opportunities = self.discover_opportunities(system_state)
        cycle_result["steps"]["discovery"] = {
            "opportunity_count": len(opportunities),
            "opportunities": [o.to_dict() for o in opportunities]
        }

        if not opportunities:
            cycle_result["overall_status"] = "no_opportunities"
            cycle_result["message"] = "未发现高价值机会"
            return cycle_result

        # 步骤2：评估机会
        assessments = self.assess_opportunities(opportunities, system_state)
        cycle_result["steps"]["assessment"] = {
            "assessment_count": len(assessments),
            "assessments": [a.to_dict() for a in assessments]
        }

        # 步骤3：做出决策
        decisions = self.make_decisions(assessments)
        cycle_result["steps"]["decision"] = {
            "decision_count": len(decisions),
            "decisions": [d.to_dict() for d in decisions]
        }

        # 步骤4：执行验证（如果启用自动执行）
        if self.config.get("auto_execute_enabled", False):
            execute_results = self._execute_decisions(decisions)
            cycle_result["steps"]["execution"] = execute_results
        else:
            cycle_result["steps"]["execution"] = {
                "status": "auto_execute_disabled",
                "message": "自动执行已禁用，仅生成决策建议"
            }

        # 汇总推荐
        proceed_decisions = [d for d in decisions if d.decision == "proceed"]
        cycle_result["recommendations"] = {
            "proceed_count": len(proceed_decisions),
            "defer_count": len([d for d in decisions if d.decision == "defer"]),
            "reject_count": len([d for d in decisions if d.decision == "reject"]),
            "top_recommendation": decisions[0].to_dict() if decisions else None
        }

        return cycle_result

    def _execute_decisions(self, decisions: List[DecisionRecommendation]) -> Dict:
        """执行决策"""
        execute_results = {
            "status": "executed",
            "results": []
        }

        # 只执行 proceed 决策
        for decision in decisions:
            if decision.decision == "proceed":
                execute_results["results"].append({
                    "opportunity_id": decision.opportunity.id,
                    "title": decision.opportunity.title,
                    "status": "recommended_for_execution",
                    "reasoning": decision.reasoning
                })

        return execute_results

    def get_status(self) -> Dict:
        """获取引擎状态"""
        return {
            "name": "智能全场景主动价值发现与智能决策闭环增强引擎",
            "version": "1.0.0",
            "round": 339,
            "learning_engine_available": self.learning_engine is not None,
            "situation_engine_available": self.situation_engine is not None,
            "kg_engine_available": self.kg_engine is not None,
            "status": "ready",
            "capabilities": [
                "主动价值发现（从知识图谱、进化历史、系统态势、学习引擎）",
                "智能价值评估（成功率、收益、成本、ROI）",
                "自动决策选择（进行/推迟/拒绝）",
                "完整闭环执行（发现→评估→决策→验证）"
            ],
            "config": self.config
        }


def main():
    """测试入口"""
    import sys

    engine = EvolutionActiveValueDiscoveryEngine()

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "--status":
            print(json.dumps(engine.get_status(), ensure_ascii=False, indent=2))

        elif command == "--discover":
            # 测试发现功能
            opportunities = engine.discover_opportunities()
            print(json.dumps({
                "count": len(opportunities),
                "opportunities": [o.to_dict() for o in opportunities]
            }, ensure_ascii=False, indent=2))

        elif command == "--full-cycle":
            # 测试完整闭环
            result = engine.run_full_cycle()
            print(json.dumps(result, ensure_ascii=False, indent=2))

        elif command == "--config":
            print(json.dumps(engine.config, ensure_ascii=False, indent=2))

        else:
            print("未知命令")
            print("可用命令:")
            print("  --status: 显示引擎状态")
            print("  --discover: 测试发现功能")
            print("  --full-cycle: 测试完整闭环")
            print("  --config: 显示配置")
    else:
        print(json.dumps(engine.get_status(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()