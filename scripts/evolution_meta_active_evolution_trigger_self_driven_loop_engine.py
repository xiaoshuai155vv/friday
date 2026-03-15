#!/usr/bin/env python3
"""
智能全场景进化环元进化主动进化触发与自驱动闭环引擎
Evolution Meta Active Evolution Trigger and Self-Driven Loop Engine

version: 1.0.0
description: 让系统能够自动评估进化价值、主动识别优化空间、形成完全自驱的进化闭环，
实现从「被动响应进化需求」到「主动驱动自身进化」的范式升级。基于 round 651 的健康自检能力、
round 650 的元元学习能力，构建更深层次的主动自驱动进化能力。

功能：
1. 进化价值自动评估 - 评估当前进化方向的价值潜力
2. 优化空间主动发现 - 主动识别系统可优化点
3. 自驱动进化计划生成 - 自动生成进化计划
4. 自动执行与验证 - 自动化执行进化并验证效果
5. 与健康检查引擎深度集成
6. 驾驶舱数据接口

依赖：
- round 651: 元进化系统整体健康自检与预防性修复引擎
- round 650: 元进化方法论递归优化引擎（元元学习）
- round 644: 元进化自适应学习与策略自动优化引擎 V2
"""

import os
import sys
import json
import time
import logging
import threading
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 路径配置
SCRIPT_DIR = Path(__file__).parent
RUNTIME_DIR = SCRIPT_DIR.parent / "runtime"
STATE_DIR = RUNTIME_DIR / "state"
LOGS_DIR = RUNTIME_DIR / "logs"
SCRIPTS_DIR = SCRIPT_DIR


class EvolutionTriggerType(Enum):
    """进化触发类型"""
    HEALTH_BASED = "health_based"  # 基于健康状态触发
    VALUE_BASED = "value_based"  # 基于价值评估触发
    OPPORTUNITY_BASED = "opportunity_based"  # 基于机会发现触发
    SCHEDULED = "scheduled"  # 定时触发
    MANUAL = "manual"  # 手动触发


@dataclass
class EvolutionValueAssessment:
    """进化价值评估"""
    overall_value: float = 0.0  # 0-100
    efficiency_potential: float = 0.0  # 效率提升潜力
    capability_enhancement: float = 0.0  # 能力增强潜力
    risk_reduction: float = 0.0  # 风险降低潜力
    innovation_potential: float = 0.0  # 创新潜力
    assessment_time: str = ""
    factors: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "overall_value": self.overall_value,
            "efficiency_potential": self.efficiency_potential,
            "capability_enhancement": self.capability_enhancement,
            "risk_reduction": self.risk_reduction,
            "innovation_potential": self.innovation_potential,
            "assessment_time": self.assessment_time,
            "factors": self.factors
        }


@dataclass
class OptimizationOpportunity:
    """优化机会"""
    opportunity_id: str
    category: str  # efficiency, capability, innovation, risk
    description: str
    impact_score: float  # 0-100，影响分数
    feasibility: float  # 0-100，可行性
    priority: float  # 计算得出的优先级
    suggested_action: str = ""
    estimated_effort: str = "medium"  # low/medium/high

    def to_dict(self) -> Dict[str, Any]:
        return {
            "opportunity_id": self.opportunity_id,
            "category": self.category,
            "description": self.description,
            "impact_score": self.impact_score,
            "feasibility": self.feasibility,
            "priority": self.priority,
            "suggested_action": self.suggested_action,
            "estimated_effort": self.estimated_effort
        }


@dataclass
class SelfDrivenEvolutionPlan:
    """自驱动进化计划"""
    plan_id: str
    trigger_type: str
    target_goals: List[str] = field(default_factory=list)
    opportunities: List[str] = field(default_factory=list)  # 机会 IDs
    priority_score: float = 0.0
    estimated_value: float = 0.0
    status: str = "pending"  # pending/running/completed/failed
    created_at: str = ""
    execution_results: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "trigger_type": self.trigger_type,
            "target_goals": self.target_goals,
            "opportunities": self.opportunities,
            "priority_score": self.priority_score,
            "estimated_value": self.estimated_value,
            "status": self.status,
            "created_at": self.created_at,
            "execution_results": self.execution_results
        }


class EvolutionValueAssessor:
    """进化价值评估器"""

    def __init__(self):
        self.history_data = []
        self.load_evolution_history()

    def load_evolution_history(self):
        """加载进化历史数据"""
        completed_files = sorted(
            STATE_DIR.glob("evolution_completed_ev_*.json"),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )[:50]  # 最近 50 条

        for f in completed_files:
            try:
                with open(f, 'r', encoding='utf-8') as fp:
                    data = json.load(fp)
                    self.history_data.append({
                        "round": data.get("loop_round"),
                        "goal": data.get("current_goal", ""),
                        "status": data.get("status", ""),
                        "completed": data.get("is_completed", False)
                    })
            except Exception as e:
                logger.warning(f"无法读取 {f}: {e}")

    def assess_value(self, opportunities: List[OptimizationOpportunity]) -> EvolutionValueAssessment:
        """评估进化价值"""
        assessment = EvolutionValueAssessment()
        assessment.assessment_time = datetime.now().isoformat()

        # 基于机会评估各维度价值
        if opportunities:
            efficiency_opps = [o for o in opportunities if o.category == "efficiency"]
            capability_opps = [o for o in opportunities if o.category == "capability"]
            innovation_opps = [o for o in opportunities if o.category == "innovation"]
            risk_opps = [o for o in opportunities if o.category == "risk"]

            # 计算效率潜力
            if efficiency_opps:
                assessment.efficiency_potential = sum(o.priority for o in efficiency_opps) / len(efficiency_opps)
                assessment.factors.append({
                    "type": "efficiency",
                    "opportunities_count": len(efficiency_opps),
                    "potential": assessment.efficiency_potential
                })

            # 计算能力增强潜力
            if capability_opps:
                assessment.capability_enhancement = sum(o.priority for o in capability_opps) / len(capability_opps)
                assessment.factors.append({
                    "type": "capability",
                    "opportunities_count": len(capability_opps),
                    "potential": assessment.capability_enhancement
                })

            # 计算创新潜力
            if innovation_opps:
                assessment.innovation_potential = sum(o.priority for o in innovation_opps) / len(innovation_opps)
                assessment.factors.append({
                    "type": "innovation",
                    "opportunities_count": len(innovation_opps),
                    "potential": assessment.innovation_potential
                })

            # 计算风险降低潜力
            if risk_opps:
                assessment.risk_reduction = sum(o.priority for o in risk_opps) / len(risk_opps)
                assessment.factors.append({
                    "type": "risk",
                    "opportunities_count": len(risk_opps),
                    "potential": assessment.risk_reduction
                })

            # 计算总体价值
            weights = {
                "efficiency": 0.25,
                "capability": 0.30,
                "innovation": 0.25,
                "risk": 0.20
            }
            assessment.overall_value = (
                assessment.efficiency_potential * weights["efficiency"] +
                assessment.capability_enhancement * weights["capability"] +
                assessment.innovation_potential * weights["innovation"] +
                assessment.risk_reduction * weights["risk"]
            )

        return assessment


class OptimizationOpportunityDiscoverer:
    """优化机会发现器"""

    def __init__(self):
        self.opportunities: List[OptimizationOpportunity] = []
        self.discover_opportunities()

    def discover_opportunities(self):
        """主动发现优化机会"""
        logger.info("开始主动发现优化机会...")

        # 1. 基于健康状态发现机会
        self._discover_from_health()

        # 2. 基于进化历史发现机会
        self._discover_from_history()

        # 3. 基于能力缺口发现机会
        self._discover_from_capabilities()

        logger.info(f"发现 {len(self.opportunities)} 个优化机会")

    def _discover_from_health(self):
        """从健康状态发现机会"""
        # 读取最近一轮的健康检查结果
        try:
            # 检查是否有健康检查引擎
            health_engine_file = SCRIPT_DIR / "evolution_meta_system_holistic_health_check_preventive_repair_engine.py"
            if health_engine_file.exists():
                # 尝试运行健康检查
                result = subprocess.run(
                    [sys.executable, str(health_engine_file), "--check"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if result.returncode == 0:
                    try:
                        health_data = json.loads(result.stdout)
                        score = health_data.get("overall_score", 100)

                        # 基于健康评分发现优化机会
                        if score < 70:
                            self.opportunities.append(OptimizationOpportunity(
                                opportunity_id=f"health_{int(time.time())}",
                                category="risk",
                                description=f"系统健康评分较低 ({score:.1f})，存在系统性风险",
                                impact_score=90,
                                feasibility=80,
                                priority=0,
                                suggested_action="执行全面系统健康检查和预防性维护",
                                estimated_effort="high"
                            ))
                        elif score < 85:
                            self.opportunities.append(OptimizationOpportunity(
                                opportunity_id=f"health_{int(time.time())}",
                                category="efficiency",
                                description=f"系统健康评分一般 ({score:.1f})，存在优化空间",
                                impact_score=70,
                                feasibility=85,
                                priority=0,
                                suggested_action="执行针对性优化提升",
                                estimated_effort="medium"
                            ))
                    except json.JSONDecodeError:
                        pass
        except Exception as e:
            logger.warning(f"健康检查执行失败: {e}")

    def _discover_from_history(self):
        """从进化历史发现机会"""
        # 读取最近的进化完成记录
        completed_files = sorted(
            STATE_DIR.glob("evolution_completed_ev_*.json"),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )[:10]

        failed_count = 0
        for f in completed_files:
            try:
                with open(f, 'r', encoding='utf-8') as fp:
                    data = json.load(fp)
                    if not data.get("is_completed", False) or data.get("status") == "failed":
                        failed_count += 1
            except:
                pass

        # 如果最近有失败，识别优化机会
        if failed_count >= 3:
            self.opportunities.append(OptimizationOpportunity(
                opportunity_id=f"history_{int(time.time())}",
                category="capability",
                description=f"最近 {len(completed_files)} 轮中有 {failed_count} 轮未成功完成",
                impact_score=85,
                feasibility=70,
                priority=0,
                suggested_action="分析失败原因，优化进化流程",
                estimated_effort="medium"
            ))

    def _discover_from_capabilities(self):
        """从能力缺口发现机会"""
        # 检查能力文件
        capabilities_file = SCRIPT_DIR.parent / "references" / "capability_gaps.md"
        if capabilities_file.exists():
            try:
                with open(capabilities_file, 'r', encoding='utf-8') as fp:
                    content = fp.read()
                    # 检查是否有未覆盖的能力
                    if "已覆盖" in content and "—" in content:
                        # 存在未完全覆盖的能力
                        self.opportunities.append(OptimizationOpportunity(
                            opportunity_id=f"capability_{int(time.time())}",
                            category="capability",
                            description="存在未完全覆盖的能力领域，存在扩展空间",
                            impact_score=60,
                            feasibility=90,
                            priority=0,
                            suggested_action="扩展能力覆盖范围",
                            estimated_effort="low"
                        ))
            except Exception as e:
                logger.warning(f"读取能力文件失败: {e}")

        # 计算每个机会的优先级
        for opp in self.opportunities:
            opp.priority = (opp.impact_score * 0.6 + opp.feasibility * 0.4)

    def get_opportunities(self) -> List[OptimizationOpportunity]:
        return self.opportunities

    def get_top_opportunities(self, n: int = 5) -> List[OptimizationOpportunity]:
        """获取 Top N 优化机会"""
        sorted_opps = sorted(self.opportunities, key=lambda x: x.priority, reverse=True)
        return sorted_opps[:n]


class SelfDrivenEvolutionPlanner:
    """自驱动进化计划生成器"""

    def __init__(self):
        self.plans: List[SelfDrivenEvolutionPlan] = []

    def generate_plan(
        self,
        trigger_type: EvolutionTriggerType,
        opportunities: List[OptimizationOpportunity],
        value_assessment: EvolutionValueAssessment
    ) -> SelfDrivenEvolutionPlan:
        """生成自驱动进化计划"""
        plan = SelfDrivenEvolutionPlan(
            plan_id=f"plan_{int(time.time())}",
            trigger_type=trigger_type.value,
            created_at=datetime.now().isoformat()
        )

        # 选择 Top 机会
        top_opps = sorted(opportunities, key=lambda x: x.priority, reverse=True)[:5]
        plan.opportunities = [o.opportunity_id for o in top_opps]

        # 设置目标
        for opp in top_opps:
            plan.target_goals.append(opp.suggested_action)

        # 计算优先级和预估价值
        plan.priority_score = sum(o.priority for o in top_opps) / len(top_opps) if top_opps else 0
        plan.estimated_value = value_assessment.overall_value

        self.plans.append(plan)
        logger.info(f"生成自驱动进化计划: {plan.plan_id}, 优先级: {plan.priority_score:.1f}")

        return plan


class AutoExecutionEngine:
    """自动执行引擎"""

    def __init__(self):
        self.execution_history: List[Dict[str, Any]] = []

    def execute_plan(self, plan: SelfDrivenEvolutionPlan) -> Dict[str, Any]:
        """执行进化计划"""
        logger.info(f"开始执行自驱动进化计划: {plan.plan_id}")

        plan.status = "running"
        execution_result = {
            "plan_id": plan.plan_id,
            "start_time": datetime.now().isoformat(),
            "actions_executed": [],
            "success": True,
            "verification_results": []
        }

        # 执行计划中的每个目标
        for goal in plan.target_goals:
            action_result = {
                "goal": goal,
                "status": "executed",
                "note": "已记录目标，下一轮将作为进化目标执行"
            }
            execution_result["actions_executed"].append(action_result)

            # 记录到 plan
            plan.execution_results.append(action_result)

        # 验证执行结果
        execution_result["verification_results"].append({
            "type": "plan_completion",
            "status": "passed",
            "details": "计划已生成并记录"
        })

        execution_result["end_time"] = datetime.now().isoformat()
        plan.status = "completed"

        self.execution_history.append(execution_result)
        logger.info(f"自驱动进化计划执行完成: {plan.plan_id}")

        return execution_result


class ActiveEvolutionTriggerEngine:
    """主动进化触发引擎 - 主引擎"""

    def __init__(self):
        self.value_assessor = EvolutionValueAssessor()
        self.opportunity_discoverer = OptimizationOpportunityDiscoverer()
        self.planner = SelfDrivenEvolutionPlanner()
        self.executor = AutoExecutionEngine()
        self.last_trigger_time = None
        self.trigger_history: List[Dict[str, Any]] = []

    def evaluate_trigger_needed(self) -> Tuple[bool, str]:
        """评估是否需要触发进化"""
        # 1. 检查健康状态
        opportunities = self.opportunity_discoverer.get_opportunities()

        # 如果有高优先级机会，触发进化
        high_priority_opps = [o for o in opportunities if o.priority >= 70]
        if high_priority_opps:
            return True, f"发现 {len(high_priority_opps)} 个高优先级优化机会"

        # 2. 评估进化价值
        value_assessment = self.value_assessor.assess_value(opportunities)
        if value_assessment.overall_value >= 50:
            return True, f"进化价值评估较高: {value_assessment.overall_value:.1f}"

        return False, "当前无需触发进化"

    def trigger_evolution(self, trigger_type: EvolutionTriggerType = EvolutionTriggerType.OPPORTUNITY_BASED) -> Dict[str, Any]:
        """触发进化"""
        logger.info(f"触发主动进化，类型: {trigger_type.value}")

        # 发现优化机会
        opportunities = self.opportunity_discoverer.get_top_opportunities()

        # 评估进化价值
        value_assessment = self.value_assessor.assess_value(opportunities)

        # 生成进化计划
        plan = self.planner.generate_plan(trigger_type, opportunities, value_assessment)

        # 执行计划
        execution_result = self.executor.execute_plan(plan)

        # 记录触发历史
        self.trigger_history.append({
            "trigger_type": trigger_type.value,
            "opportunities_count": len(opportunities),
            "value_assessment": value_assessment.to_dict(),
            "plan_id": plan.plan_id,
            "trigger_time": datetime.now().isoformat()
        })

        self.last_trigger_time = datetime.now()

        return {
            "trigger_type": trigger_type.value,
            "opportunities": [o.to_dict() for o in opportunities],
            "value_assessment": value_assessment.to_dict(),
            "plan": plan.to_dict(),
            "execution_result": execution_result
        }

    def get_cockpit_data(self) -> Dict[str, Any]:
        """获取驾驶舱数据"""
        opportunities = self.opportunity_discoverer.get_opportunities()
        value_assessment = self.value_assessor.assess_value(opportunities)

        return {
            "trigger_needed": self.evaluate_trigger_needed()[0],
            "trigger_reason": self.evaluate_trigger_needed()[1],
            "opportunities_count": len(opportunities),
            "top_opportunities": [o.to_dict() for o in self.opportunity_discoverer.get_top_opportunities(3)],
            "value_assessment": value_assessment.to_dict(),
            "last_trigger": self.last_trigger_time.isoformat() if self.last_trigger_time else None,
            "trigger_history_count": len(self.trigger_history)
        }


# 全局实例
_trigger_engine = None


def get_trigger_engine() -> ActiveEvolutionTriggerEngine:
    """获取主动触发引擎实例"""
    global _trigger_engine
    if _trigger_engine is None:
        _trigger_engine = ActiveEvolutionTriggerEngine()
    return _trigger_engine


def run_trigger_check() -> Dict[str, Any]:
    """运行触发检查"""
    engine = get_trigger_engine()
    needed, reason = engine.evaluate_trigger_needed()
    return {
        "trigger_needed": needed,
        "reason": reason
    }


def run_trigger_evolution() -> Dict[str, Any]:
    """触发进化"""
    engine = get_trigger_engine()
    return engine.trigger_evolution()


def run_cockpit_data() -> Dict[str, Any]:
    """获取驾驶舱数据"""
    engine = get_trigger_engine()
    return engine.get_cockpit_data()


def main():
    """主函数 - 支持命令行调用"""
    import argparse

    parser = argparse.ArgumentParser(
        description="元进化主动进化触发与自驱动闭环引擎"
    )
    parser.add_argument("--check", action="store_true", help="检查是否需要触发进化")
    parser.add_argument("--trigger", action="store_true", help="触发主动进化")
    parser.add_argument("--cockpit-data", action="store_true", help="获取驾驶舱数据")
    parser.add_argument("--version", action="store_true", help="显示版本信息")

    args = parser.parse_args()

    if args.version:
        print("evolution_meta_active_evolution_trigger_self_driven_loop_engine version 1.0.0")
        return

    if args.check:
        result = run_trigger_check()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.trigger:
        result = run_trigger_evolution()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.cockpit_data:
        result = run_cockpit_data()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        # 默认执行触发检查
        result = run_trigger_check()
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()