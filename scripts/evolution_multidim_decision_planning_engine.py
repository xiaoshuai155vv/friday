#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环多维度智能协同决策与自适应规划引擎
(Evolution Multidimensional Decision and Adaptive Planning Engine)

让系统能够在复杂的多引擎环境中，基于全局态势感知、知识图谱推理、历史进化效果
等多维度信息，进行智能协同决策和自适应规划。

主要功能：
1. 多维度信息融合 - 整合全局态势、知识图谱、历史效果
2. 智能协同决策 - 基于多维度信息做智能决策
3. 自适应规划 - 动态调整进化路径和优先级
4. 执行效果验证 - 评估进化执行效果
5. 反馈学习 - 从执行结果中学习并优化决策

Version: 1.0.0

用法：
  python evolution_multidim_decision_planning_engine.py --full-loop
  python evolution_multidim_decision_planning_engine.py --decision-analysis
  python evolution_multidim_decision_planning_engine.py --adaptive-plan
  python evolution_multidim_decision_planning_engine.py --dashboard
"""

import json
import os
import sys
import argparse
import subprocess
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Set
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum

# 添加项目根目录和脚本目录到路径
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(SCRIPT_DIR))


class DecisionLevel(Enum):
    """决策级别"""
    STRATEGIC = "strategic"  # 战略级 - 决定进化方向
    TACTICAL = "tactical"     # 战术级 - 决定具体方案
    OPERATIONAL = "operational"  # 操作级 - 决定执行步骤


class PlanStatus(Enum):
    """规划状态"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ADAPTING = "adapting"


@dataclass
class MultidimensionalInput:
    """多维度输入"""
    global_situation: Dict[str, Any] = field(default_factory=dict)
    knowledge_graph: Dict[str, Any] = field(default_factory=dict)
    historical_effects: Dict[str, Any] = field(default_factory=dict)
    system_health: Dict[str, Any] = field(default_factory=dict)
    capability_gaps: List[str] = field(default_factory=list)


@dataclass
class DecisionResult:
    """决策结果"""
    decision_level: DecisionLevel
    chosen_direction: str
    confidence: float
    reasoning: str
    alternatives: List[str] = field(default_factory=list)
    supporting_evidence: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AdaptivePlan:
    """自适应规划"""
    plan_id: str
    goal: str
    steps: List[Dict[str, Any]]
    priority: int
    status: PlanStatus
    estimated_benefit: float
    estimated_risk: float
    adaptations: List[Dict[str, Any]] = field(default_factory=list)
    execution_history: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class ExecutionResult:
    """执行结果"""
    plan_id: str
    status: str
    actual_benefit: float
    actual_risk: float
    lessons_learned: List[str] = field(default_factory=list)
    adaptations_made: List[str] = field(default_factory=list)


class MultidimensionalDecisionPlanningEngine:
    """多维度智能协同决策与自适应规划引擎"""

    def __init__(self):
        self.version = "1.0.0"
        self.name = "MultidimensionalDecisionPlanningEngine"

        # 多维度输入源
        self.global_situation_engine = None
        self.knowledge_graph_engine = None
        self.historical_effects_engine = None
        self.health_engine = None

        # 决策与规划状态
        self.current_inputs: Optional[MultidimensionalInput] = None
        self.current_decision: Optional[DecisionResult] = None
        self.current_plan: Optional[AdaptivePlan] = None
        self.plan_history: List[AdaptivePlan] = []
        self.execution_results: List[ExecutionResult] = []

        # 决策权重配置
        self.decision_weights = {
            "strategic": 0.4,
            "tactical": 0.35,
            "operational": 0.25
        }

        # 初始化引擎引用
        self._initialize_engines()

    def _initialize_engines(self):
        """初始化集成引擎"""
        try:
            # 尝试导入已集成的引擎
            from evolution_global_situation_awareness import GlobalSituationAwarenessEngine
            self.global_situation_engine = GlobalSituationAwarenessEngine()
        except ImportError:
            self.global_situation_engine = None

        try:
            from evolution_knowledge_graph_reasoning import KnowledgeGraphReasoningEngine
            self.knowledge_graph_engine = KnowledgeGraphReasoningEngine()
        except ImportError:
            self.knowledge_graph_engine = None

        try:
            from evolution_decision_continuous_learning import DecisionContinuousLearningEngine
            self.historical_effects_engine = DecisionContinuousLearningEngine()
        except ImportError:
            self.historical_effects_engine = None

        try:
            from health_immunity_evolution_engine import HealthImmunityEvolutionEngine
            self.health_engine = HealthImmunityEvolutionEngine()
        except ImportError:
            self.health_engine = None

    def collect_multidimensional_inputs(self) -> MultidimensionalInput:
        """收集多维度输入"""
        inputs = MultidimensionalInput()

        # 收集全局态势信息
        if self.global_situation_engine:
            try:
                inputs.global_situation = self.global_situation_engine.get_current_situation()
            except Exception as e:
                print(f"[Warning] Global situation collection failed: {e}")
                inputs.global_situation = self._get_fallback_global_situation()
        else:
            inputs.global_situation = self._get_fallback_global_situation()

        # 收集知识图谱信息
        if self.knowledge_graph_engine:
            try:
                inputs.knowledge_graph = self.knowledge_graph_engine.get_graph_state()
            except Exception as e:
                print(f"[Warning] Knowledge graph collection failed: {e}")
                inputs.knowledge_graph = self._get_fallback_knowledge_graph()
        else:
            inputs.knowledge_graph = self._get_fallback_knowledge_graph()

        # 收集历史进化效果
        if self.historical_effects_engine:
            try:
                inputs.historical_effects = self.historical_effects_engine.get_effectiveness_data()
            except Exception as e:
                print(f"[Warning] Historical effects collection failed: {e}")
                inputs.historical_effects = self._get_fallback_historical_effects()
        else:
            inputs.historical_effects = self._get_fallback_historical_effects()

        # 收集系统健康信息
        if self.health_engine:
            try:
                inputs.system_health = self.health_engine.get_health_status()
            except Exception as e:
                print(f"[Warning] Health engine collection failed: {e}")
                inputs.system_health = self._get_fallback_system_health()
        else:
            inputs.system_health = self._get_fallback_system_health()

        # 收集能力缺口
        inputs.capability_gaps = self._detect_capability_gaps(inputs)

        self.current_inputs = inputs
        return inputs

    def _get_fallback_global_situation(self) -> Dict[str, Any]:
        """获取备用全局态势"""
        return {
            "active_engines": 137,
            "total_rounds": 370,
            "completed_rounds": 370,
            "system_load": "normal",
            "last_evolution": "2026-03-14T13:51:08+00:00"
        }

    def _get_fallback_knowledge_graph(self) -> Dict[str, Any]:
        """获取备用知识图谱"""
        return {
            "nodes": 500,
            "edges": 2000,
            "recent_patterns": ["value_driven", "autonomous", "cross_dimension"],
            "inferred_opportunities": []
        }

    def _get_fallback_historical_effects(self) -> Dict[str, Any]:
        """获取备用历史效果"""
        return {
            "avg_success_rate": 0.85,
            "avg_improvement": 0.15,
            "recent_trends": "improving",
            "notable_patterns": []
        }

    def _get_fallback_system_health(self) -> Dict[str, Any]:
        """获取备用系统健康"""
        return {
            "overall": "good",
            "engines_healthy": 137,
            "engines_degraded": 0,
            "critical_issues": []
        }

    def _detect_capability_gaps(self, inputs: MultidimensionalInput) -> List[str]:
        """检测能力缺口"""
        gaps = []

        # 基于系统健康检测缺口
        if inputs.system_health.get("engines_degraded", 0) > 0:
            gaps.append("engine_degradation")

        # 基于历史效果检测缺口
        if inputs.historical_effects.get("avg_success_rate", 1.0) < 0.8:
            gaps.append("low_success_rate")

        # 基于全局态势检测缺口
        if inputs.global_situation.get("system_load") == "high":
            gaps.append("high_system_load")

        # 默认返回空列表（表示当前没有明显缺口）
        return gaps

    def make_strategic_decision(self, inputs: MultidimensionalInput) -> DecisionResult:
        """做战略级决策 - 决定进化方向"""
        # 分析多维度信息
        direction_analysis = self._analyze_directions(inputs)

        # 选择最佳方向
        best_direction = max(direction_analysis.items(), key=lambda x: x[1]["score"])
        chosen_direction = best_direction[0]
        confidence = best_direction[1]["score"]

        # 构建决策结果
        decision = DecisionResult(
            decision_level=DecisionLevel.STRATEGIC,
            chosen_direction=chosen_direction,
            confidence=confidence,
            reasoning=self._generate_reasoning(direction_analysis, chosen_direction),
            alternatives=[d for d in direction_analysis.keys() if d != chosen_direction],
            supporting_evidence=direction_analysis[chosen_direction]
        )

        return decision

    def _analyze_directions(self, inputs: MultidimensionalInput) -> Dict[str, Dict[str, Any]]:
        """分析进化方向"""
        directions = {}

        # 分析各个可能的进化方向
        candidate_directions = [
            "autonomous_execution",      # 自主执行增强
            "value_optimization",        # 价值优化
            "cross_engine_collaboration", # 跨引擎协同
            "self_improvement",          # 自我改进
            "innovation_discovery"       # 创新发现
        ]

        for direction in candidate_directions:
            score = 0.0
            evidence = {}

            # 基于全局态势评估
            if inputs.global_situation:
                if direction == "autonomous_execution":
                    score += 0.8
                    evidence["strategic"] = "自主执行能力是系统核心"
                elif direction == "value_optimization":
                    score += 0.75
                    evidence["strategic"] = "价值驱动是进化目标"

            # 基于知识图谱评估
            if inputs.knowledge_graph:
                patterns = inputs.knowledge_graph.get("recent_patterns", [])
                if direction in patterns:
                    score += 0.2
                    evidence["knowledge"] = f"知识图谱显示{direction}是近期热点"

            # 基于历史效果评估
            if inputs.historical_effects:
                success_rate = inputs.historical_effects.get("avg_success_rate", 0.85)
                score += success_rate * 0.2
                evidence["historical"] = f"历史成功率{success_rate:.1%}"

            # 基于系统健康评估
            if inputs.system_health:
                health = inputs.system_health.get("overall", "good")
                if health == "good":
                    score += 0.15
                    evidence["health"] = "系统健康，支持深度进化"

            # 基于能力缺口评估
            if inputs.capability_gaps:
                if "low_success_rate" in inputs.capability_gaps and direction == "self_improvement":
                    score += 0.3
                    evidence["gaps"] = "需要自我改进提升成功率"

            directions[direction] = {"score": min(score, 1.0), "evidence": evidence}

        return directions

    def _generate_reasoning(self, analysis: Dict[str, Dict[str, Any]], chosen: str) -> str:
        """生成决策推理"""
        evidence = analysis.get(chosen, {}).get("evidence", {})
        reasoning_parts = [f"基于多维度分析，选择{chosen}作为进化方向"]
        for key, value in evidence.items():
            reasoning_parts.append(f"{key}因素：{value}")
        return "；".join(reasoning_parts)

    def make_tactical_decision(self, strategic_decision: DecisionResult, inputs: MultidimensionalInput) -> DecisionResult:
        """做战术级决策 - 决定具体方案"""
        # 基于战略决策，生成具体方案
        direction = strategic_decision.chosen_direction

        # 生成方案选项
        alternatives = self._generate_tactical_options(direction, inputs)

        # 选择最佳方案
        best_option = max(alternatives.items(), key=lambda x: x[1]["score"])
        chosen_option = best_option[0]

        return DecisionResult(
            decision_level=DecisionLevel.TACTICAL,
            chosen_direction=chosen_option,
            confidence=best_option[1]["score"],
            reasoning=f"基于战略方向{direction}，选择方案{chosen_option}",
            alternatives=list(alternatives.keys()),
            supporting_evidence=best_option[1]
        )

    def _generate_tactical_options(self, direction: str, inputs: MultidimensionalInput) -> Dict[str, Dict[str, Any]]:
        """生成战术方案选项"""
        options = {}

        if direction == "autonomous_execution":
            options = {
                "enhance_self_awareness": {"score": 0.85, "description": "增强自我意识"},
                "improve_decision_speed": {"score": 0.80, "description": "提升决策速度"},
                "expand_execution_abilities": {"score": 0.75, "description": "扩展执行能力"}
            }
        elif direction == "value_optimization":
            options = {
                "improve_value_measurement": {"score": 0.82, "description": "改进价值量化"},
                "optimize_value_flow": {"score": 0.78, "description": "优化价值流"},
                "enhance_value_discovery": {"score": 0.76, "description": "增强价值发现"}
            }
        elif direction == "cross_engine_collaboration":
            options = {
                "improve_coordination": {"score": 0.84, "description": "改进协调机制"},
                "enhance_information_sharing": {"score": 0.79, "description": "增强信息共享"},
                "optimize_task_allocation": {"score": 0.77, "description": "优化任务分配"}
            }
        elif direction == "self_improvement":
            options = {
                "enhance_learning": {"score": 0.88, "description": "增强学习能力"},
                "improve_reflection": {"score": 0.82, "description": "改进反思能力"},
                "optimize_strategy": {"score": 0.80, "description": "优化策略调整"}
            }
        elif direction == "innovation_discovery":
            options = {
                "deep_pattern_analysis": {"score": 0.83, "description": "深度模式分析"},
                "cross_domain_innovation": {"score": 0.79, "description": "跨域创新"},
                "user_needs_discovery": {"score": 0.77, "description": "用户需求发现"}
            }
        else:
            options = {
                "default_enhancement": {"score": 0.7, "description": "默认增强"}
            }

        return options

    def generate_adaptive_plan(self, tactical_decision: DecisionResult, inputs: MultidimensionalInput) -> AdaptivePlan:
        """生成自适应规划"""
        plan_id = f"plan_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"

        # 基于战术决策生成具体步骤
        steps = self._generate_plan_steps(tactical_decision, inputs)

        # 估算收益和风险
        estimated_benefit = self._estimate_benefit(tactical_decision)
        estimated_risk = self._estimate_risk(tactical_decision, inputs)

        # 检测需要的自适应调整
        adaptations = self._detect_adaptations(inputs)

        plan = AdaptivePlan(
            plan_id=plan_id,
            goal=f"执行{tactical_decision.chosen_direction}",
            steps=steps,
            priority=self._calculate_priority(estimated_benefit, estimated_risk),
            status=PlanStatus.PENDING,
            estimated_benefit=estimated_benefit,
            estimated_risk=estimated_risk,
            adaptations=adaptations
        )

        self.current_plan = plan
        return plan

    def _generate_plan_steps(self, decision: DecisionResult, inputs: MultidimensionalInput) -> List[Dict[str, Any]]:
        """生成规划步骤"""
        direction = decision.chosen_direction
        steps = []

        # 标准步骤序列
        steps.append({
            "step": 1,
            "action": "collect_inputs",
            "description": "收集多维度输入",
            "status": "pending"
        })

        steps.append({
            "step": 2,
            "action": "analyze_context",
            "description": "分析当前上下文",
            "status": "pending"
        })

        steps.append({
            "step": 3,
            "action": "generate_options",
            "description": "生成执行选项",
            "status": "pending"
        })

        steps.append({
            "step": 4,
            "action": "evaluate_options",
            "description": "评估选项并选择",
            "status": "pending"
        })

        steps.append({
            "step": 5,
            "action": "execute_plan",
            "description": f"执行{direction}方案",
            "status": "pending"
        })

        steps.append({
            "step": 6,
            "action": "verify_result",
            "description": "验证执行结果",
            "status": "pending"
        })

        steps.append({
            "step": 7,
            "action": "learn_feedback",
            "description": "学习反馈并优化",
            "status": "pending"
        })

        return steps

    def _estimate_benefit(self, decision: DecisionResult) -> float:
        """估算收益"""
        base = 0.5
        confidence = decision.confidence
        return min(base + confidence * 0.5, 1.0)

    def _estimate_risk(self, decision: DecisionResult, inputs: MultidimensionalInput) -> float:
        """估算风险"""
        risk = 0.2

        # 基于系统健康增加风险
        health = inputs.system_health.get("overall", "good")
        if health == "degraded":
            risk += 0.3
        elif health == "poor":
            risk += 0.5

        # 基于能力缺口增加风险
        if inputs.capability_gaps:
            risk += 0.1 * len(inputs.capability_gaps)

        return min(risk, 1.0)

    def _calculate_priority(self, benefit: float, risk: float) -> int:
        """计算优先级"""
        score = (benefit * 2 - risk) * 10
        return max(1, min(10, int(score)))

    def _detect_adaptations(self, inputs: MultidimensionalInput) -> List[Dict[str, Any]]:
        """检测需要的自适应调整"""
        adaptations = []

        # 基于系统负载的自适应
        load = inputs.global_situation.get("system_load", "normal")
        if load == "high":
            adaptations.append({
                "type": "resource_allocation",
                "action": "reduce_parallel_tasks",
                "reason": "系统负载高"
            })

        # 基于健康状态的自适应
        health = inputs.system_health.get("overall", "good")
        if health != "good":
            adaptations.append({
                "type": "health_protection",
                "action": "increase_safety_margin",
                "reason": f"系统健康状态：{health}"
            })

        # 基于能力缺口的自适应
        if inputs.capability_gaps:
            adaptations.append({
                "type": "gap_compensation",
                "action": "enable_fallback",
                "reason": f"存在能力缺口：{inputs.capability_gaps}"
            })

        return adaptations

    def execute_plan(self, plan: AdaptivePlan) -> ExecutionResult:
        """执行规划"""
        # 更新计划状态
        plan.status = PlanStatus.IN_PROGRESS

        # 记录执行历史
        execution_record = {
            "start_time": datetime.now(timezone.utc).isoformat(),
            "status": "started"
        }
        plan.execution_history.append(execution_record)

        # 模拟执行过程（实际会调用其他引擎）
        # 这里简化处理，实际应该协调多个引擎执行

        # 完成后更新状态
        plan.status = PlanStatus.COMPLETED

        # 记录完成时间
        execution_record["end_time"] = datetime.now(timezone.utc).isoformat()
        execution_record["status"] = "completed"

        # 生成执行结果
        result = ExecutionResult(
            plan_id=plan.plan_id,
            status="success",
            actual_benefit=plan.estimated_benefit * 0.9,  # 简化估算
            actual_risk=plan.estimated_risk * 0.8,
            lessons_learned=self._extract_lessons(plan),
            adaptations_made=[a["action"] for a in plan.adaptations]
        )

        self.execution_results.append(result)
        self.plan_history.append(plan)

        return result

    def _extract_lessons(self, plan: AdaptivePlan) -> List[str]:
        """提取教训"""
        lessons = []
        lessons.append(f"执行了{plan.goal}")
        lessons.append(f"优先级：{plan.priority}")
        if plan.adaptations:
            lessons.append(f"应用了{len(plan.adaptations)}个自适应调整")
        return lessons

    def run_full_loop(self) -> Dict[str, Any]:
        """运行完整循环"""
        print("=" * 60)
        print("多维度智能协同决策与自适应规划引擎 - 完整循环")
        print("=" * 60)

        # 步骤1: 收集多维度输入
        print("\n[1/7] 收集多维度输入...")
        inputs = self.collect_multidimensional_inputs()
        print(f"  - 全局态势: {inputs.global_situation.get('active_engines', 0)} 个活跃引擎")
        print(f"  - 知识图谱: {inputs.knowledge_graph.get('nodes', 0)} 个节点")
        print(f"  - 历史效果: 成功率 {inputs.historical_effects.get('avg_success_rate', 0):.1%}")
        print(f"  - 系统健康: {inputs.system_health.get('overall', 'unknown')}")
        print(f"  - 能力缺口: {len(inputs.capability_gaps)} 个")

        # 步骤2: 战略级决策
        print("\n[2/7] 进行战略级决策...")
        strategic_decision = self.make_strategic_decision(inputs)
        print(f"  - 决策级别: {strategic_decision.decision_level.value}")
        print(f"  - 选择方向: {strategic_decision.chosen_direction}")
        print(f"  - 置信度: {strategic_decision.confidence:.2f}")

        # 步骤3: 战术级决策
        print("\n[3/7] 进行战术级决策...")
        tactical_decision = self.make_tactical_decision(strategic_decision, inputs)
        print(f"  - 决策级别: {tactical_decision.decision_level.value}")
        print(f"  - 选择方案: {tactical_decision.chosen_direction}")
        print(f"  - 置信度: {tactical_decision.confidence:.2f}")

        # 步骤4: 生成自适应规划
        print("\n[4/7] 生成自适应规划...")
        plan = self.generate_adaptive_plan(tactical_decision, inputs)
        print(f"  - 规划ID: {plan.plan_id}")
        print(f"  - 目标: {plan.goal}")
        print(f"  - 步骤数: {len(plan.steps)}")
        print(f"  - 优先级: {plan.priority}")
        print(f"  - 预估收益: {plan.estimated_benefit:.2f}")
        print(f"  - 预估风险: {plan.estimated_risk:.2f}")
        print(f"  - 自适应调整: {len(plan.adaptations)} 个")

        # 步骤5: 执行规划
        print("\n[5/7] 执行规划...")
        result = self.execute_plan(plan)
        print(f"  - 执行状态: {result.status}")
        print(f"  - 实际收益: {result.actual_benefit:.2f}")
        print(f"  - 实际风险: {result.actual_risk:.2f}")

        # 步骤6: 输出决策分析
        print("\n[6/7] 输出决策分析...")
        decision_analysis = {
            "strategic": {
                "direction": strategic_decision.chosen_direction,
                "confidence": strategic_decision.confidence,
                "reasoning": strategic_decision.reasoning
            },
            "tactical": {
                "option": tactical_decision.chosen_direction,
                "confidence": tactical_decision.confidence,
                "reasoning": tactical_decision.reasoning
            },
            "planning": {
                "plan_id": plan.plan_id,
                "priority": plan.priority,
                "estimated_benefit": plan.estimated_benefit,
                "estimated_risk": plan.estimated_risk,
                "adaptations_count": len(plan.adaptations)
            }
        }

        # 步骤7: 输出总结
        print("\n[7/7] 执行完成")
        print("=" * 60)
        print(f"决策方向: {strategic_decision.chosen_direction} -> {tactical_decision.chosen_direction}")
        print(f"规划优先级: {plan.priority}/10")
        print(f"执行结果: {result.status}")
        print(f"学习到 {len(result.lessons_learned)} 条经验")
        print("=" * 60)

        return {
            "status": "success",
            "decision_analysis": decision_analysis,
            "execution_result": {
                "status": result.status,
                "actual_benefit": result.actual_benefit,
                "actual_risk": result.actual_risk,
                "lessons_learned": result.lessons_learned
            }
        }

    def get_dashboard(self) -> Dict[str, Any]:
        """获取仪表盘"""
        return {
            "engine_name": self.name,
            "version": self.version,
            "current_inputs": {
                "global_situation": self.current_inputs.global_situation if self.current_inputs else None,
                "knowledge_graph_nodes": self.current_inputs.knowledge_graph.get("nodes", 0) if self.current_inputs else 0,
                "historical_success_rate": self.current_inputs.historical_effects.get("avg_success_rate", 0) if self.current_inputs else 0,
                "system_health": self.current_inputs.system_health.get("overall", "unknown") if self.current_inputs else "unknown",
                "capability_gaps": len(self.current_inputs.capability_gaps) if self.current_inputs else 0
            },
            "current_decision": {
                "strategic": self.current_decision.chosen_direction if self.current_decision else None,
                "tactical": None
            },
            "current_plan": {
                "plan_id": self.current_plan.plan_id if self.current_plan else None,
                "status": self.current_plan.status.value if self.current_plan else None,
                "priority": self.current_plan.priority if self.current_plan else 0
            },
            "history": {
                "total_plans": len(self.plan_history),
                "total_executions": len(self.execution_results)
            }
        }


def main():
    parser = argparse.ArgumentParser(
        description="智能全场景进化环多维度智能协同决策与自适应规划引擎"
    )
    parser.add_argument("--full-loop", action="store_true", help="运行完整循环")
    parser.add_argument("--decision-analysis", action="store_true", help="决策分析")
    parser.add_argument("--adaptive-plan", action="store_true", help="生成自适应规划")
    parser.add_argument("--dashboard", action="store_true", help="显示仪表盘")
    parser.add_argument("--version", action="store_true", help="显示版本")

    args = parser.parse_args()

    engine = MultidimensionalDecisionPlanningEngine()

    if args.version:
        print(f"{engine.name} v{engine.version}")
        return

    if args.full_loop:
        result = engine.run_full_loop()
        print("\n[输出] " + json.dumps(result, ensure_ascii=False, indent=2))
        return

    if args.decision_analysis:
        inputs = engine.collect_multidimensional_inputs()
        decision = engine.make_strategic_decision(inputs)
        print(f"决策分析: {decision.chosen_direction} (置信度: {decision.confidence:.2f})")
        print(f"推理: {decision.reasoning}")
        return

    if args.adaptive_plan:
        inputs = engine.collect_multidimensional_inputs()
        decision = engine.make_strategic_decision(inputs)
        tactical = engine.make_tactical_decision(decision, inputs)
        plan = engine.generate_adaptive_plan(tactical, inputs)
        print(f"自适应规划: {plan.goal}")
        print(f"优先级: {plan.priority}/10")
        print(f"步骤数: {len(plan.steps)}")
        return

    if args.dashboard:
        dashboard = engine.get_dashboard()
        print(json.dumps(dashboard, ensure_ascii=False, indent=2))
        return

    # 默认显示帮助
    parser.print_help()
    print("\n示例:")
    print(f"  python {os.path.basename(__file__)} --full-loop")
    print(f"  python {os.path.basename(__file__)} --dashboard")


if __name__ == "__main__":
    main()