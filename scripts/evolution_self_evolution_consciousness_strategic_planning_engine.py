#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环自我进化意识与战略规划引擎
version 1.0.0

让系统能够基于500+轮进化历史进行自我反思、评估当前进化状态与目标差距、
智能规划下一阶段进化战略，形成「自我认知→状态评估→战略规划→执行验证」的完整闭环。
让进化环具备真正的「自主进化意识」，知道自己从哪里来、现在在哪里、应该往哪里去。

这是 LLM 特有的大规模历史分析优势的应用，让系统能够像战略家一样规划自己的进化方向。

功能：
1. 进化历史深度分析 - 分析500+轮进化的模式、效果、趋势
2. 自我状态评估 - 当前能力、健康度、进化效率的多维度评估
3. 战略规划 - 基于自我认知智能规划进化方向和优先级
4. 目标差距分析 - 当前状态与理想状态的差距识别
5. 驾驶舱集成 - 可视化自我认知和战略规划过程

依赖：
- evolution_knowledge_driven_emergence_execution_engine.py (round 530)
- evolution_effectiveness_deep_analysis_optimizer_engine.py (round 524)
- evolution_meta_evolution_enhancement_engine.py (round 442)
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


class EvolutionState:
    """进化状态评估"""

    def __init__(self, total_rounds: int, completed_rounds: int, failed_rounds: int,
                 avg_completion_time: float, success_rate: float, health_score: float,
                 capability_count: int, engine_count: int):
        self.total_rounds = total_rounds
        self.completed_rounds = completed_rounds
        self.failed_rounds = failed_rounds
        self.avg_completion_time = avg_completion_time
        self.success_rate = success_rate
        self.health_score = health_score
        self.capability_count = capability_count
        self.engine_count = engine_count
        self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict:
        return {
            "total_rounds": self.total_rounds,
            "completed_rounds": self.completed_rounds,
            "failed_rounds": self.failed_rounds,
            "avg_completion_time": self.avg_completion_time,
            "success_rate": self.success_rate,
            "health_score": self.health_score,
            "capability_count": self.capability_count,
            "engine_count": self.engine_count,
            "timestamp": self.timestamp
        }


class StrategicDirection:
    """战略方向"""

    def __init__(self, direction_id: str, title: str, description: str,
                 priority: float, estimated_impact: float, risk_level: float,
                 dependencies: List[str], expected_outcome: str):
        self.id = direction_id
        self.title = title
        self.description = description
        self.priority = priority  # 0-1
        self.estimated_impact = estimated_impact  # 0-1
        self.risk_level = risk_level  # 0-1 (lower is better)
        self.dependencies = dependencies
        self.expected_outcome = expected_outcome
        self.timestamp = datetime.now().isoformat()

        # 计算综合评分
        self.score = self._calculate_score()

    def _calculate_score(self) -> float:
        """计算综合评分"""
        # 综合评分 = 优先级 * 影响力 * (1 - 风险)
        return self.priority * self.estimated_impact * (1 - self.risk_level * 0.5)

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "estimated_impact": self.estimated_impact,
            "risk_level": self.risk_level,
            "score": self.score,
            "dependencies": self.dependencies,
            "expected_outcome": self.expected_outcome,
            "timestamp": self.timestamp
        }


class GoalGap:
    """目标差距"""

    def __init__(self, gap_id: str, category: str, current_state: str,
                 ideal_state: str, gap_severity: float, suggested_actions: List[str]):
        self.id = gap_id
        self.category = category
        self.current_state = current_state
        self.ideal_state = ideal_state
        self.gap_severity = gap_severity  # 0-1 (higher is worse)
        self.suggested_actions = suggested_actions
        self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "category": self.category,
            "current_state": self.current_state,
            "ideal_state": self.ideal_state,
            "gap_severity": self.gap_severity,
            "suggested_actions": self.suggested_actions,
            "timestamp": self.timestamp
        }


class SelfEvolutionConsciousnessEngine:
    """自我进化意识与战略规划引擎"""

    VERSION = "1.0.0"

    def __init__(self, runtime_dir: str = None):
        if runtime_dir is None:
            # 默认使用项目根目录
            self.runtime_dir = Path(__file__).parent.parent / "runtime"
        else:
            self.runtime_dir = Path(runtime_dir)

        self.state_dir = self.runtime_dir / "state"
        self.logs_dir = self.runtime_dir / "logs"
        self.scripts_dir = Path(__file__).parent

        # 确保目录存在
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)

    def get_status(self) -> Dict:
        """获取引擎状态"""
        # 分析进化历史
        history_analysis = self.analyze_evolution_history()

        # 评估当前状态
        state_assessment = self.assess_current_state()

        # 识别目标差距
        gaps = self.identify_goal_gaps()

        # 生成战略方向
        strategic_directions = self.generate_strategic_directions()

        return {
            "engine": "SelfEvolutionConsciousnessStrategicPlanning",
            "version": self.VERSION,
            "status": "active",
            "history_analysis": history_analysis,
            "state_assessment": state_assessment.to_dict(),
            "goal_gaps": [g.to_dict() for g in gaps],
            "strategic_directions": [d.to_dict() for d in strategic_directions],
            "timestamp": datetime.now().isoformat()
        }

    def analyze_evolution_history(self, lookback_rounds: int = None) -> Dict:
        """分析进化历史，识别模式和趋势"""
        completed_files = sorted(self.state_dir.glob("evolution_completed_*.json"))

        if not completed_files:
            return {
                "total_rounds": 0,
                "message": "No evolution history found"
            }

        # 如果没有指定回看轮次，默认分析全部历史
        if lookback_rounds is None:
            lookback_rounds = len(completed_files)

        recent_files = completed_files[-lookback_rounds:] if len(completed_files) > lookback_rounds else completed_files

        # 统计信息
        total_rounds = len(completed_files)
        completed_count = 0
        failed_count = 0
        round_details = []

        for f in recent_files:
            try:
                with open(f, 'r', encoding='utf-8') as fp:
                    data = json.load(fp)
                    status = data.get("是否完成", "未知")
                    if "完成" in str(status):
                        completed_count += 1
                    elif "未完成" in str(status):
                        failed_count += 1
                    round_details.append({
                        "round": data.get("loop_round", "unknown"),
                        "goal": data.get("current_goal", "unknown"),
                        "status": status,
                        "timestamp": data.get("updated_at", "")
                    })
            except Exception as e:
                print(f"Warning: Failed to read {f}: {e}")

        # 分析模式
        patterns = self._identify_patterns(round_details)

        # 分析趋势
        trends = self._analyze_trends(round_details)

        return {
            "total_rounds": total_rounds,
            "analyzed_rounds": len(recent_files),
            "completed_count": completed_count,
            "failed_count": failed_count,
            "success_rate": completed_count / len(recent_files) if recent_files else 0,
            "patterns": patterns,
            "trends": trends,
            "recent_details": round_details[-10:] if len(round_details) > 10 else round_details
        }

    def _identify_patterns(self, round_details: List[Dict]) -> Dict:
        """识别进化模式"""
        patterns = {
            "frequent_categories": [],
            "success_patterns": [],
            "common_dependencies": []
        }

        if not round_details:
            return patterns

        # 统计目标类型
        goal_counts = defaultdict(int)
        for detail in round_details:
            goal = str(detail.get("goal", ""))
            # 简单分类
            if "引擎" in goal or "engine" in goal.lower():
                goal_counts["engine"] += 1
            elif "优化" in goal or "optimization" in goal.lower():
                goal_counts["optimization"] += 1
            elif "增强" in goal or "enhancement" in goal.lower():
                goal_counts["enhancement"] += 1
            elif "集成" in goal or "integration" in goal.lower():
                goal_counts["integration"] += 1
            elif "分析" in goal or "analysis" in goal.lower():
                goal_counts["analysis"] += 1
            else:
                goal_counts["other"] += 1

        # 排序
        sorted_goals = sorted(goal_counts.items(), key=lambda x: x[1], reverse=True)
        patterns["frequent_categories"] = [{"category": k, "count": v} for k, v in sorted_goals[:5]]

        # 识别成功模式（连续完成的轮次）
        success_streak = 0
        max_streak = 0
        for detail in round_details:
            if "完成" in str(detail.get("status", "")):
                success_streak += 1
                max_streak = max(max_streak, success_streak)
            else:
                success_streak = 0

        patterns["success_patterns"] = {
            "current_streak": success_streak,
            "max_streak": max_streak
        }

        return patterns

    def _analyze_trends(self, round_details: List[Dict]) -> Dict:
        """分析进化趋势"""
        if len(round_details) < 2:
            return {"trend": "insufficient_data"}

        # 简单趋势分析：计算近期的成功率变化
        recent_half = round_details[len(round_details)//2:]
        early_half = round_details[:len(round_details)//2]

        def calc_success_rate(details):
            completed = sum(1 for d in details if "完成" in str(d.get("status", "")))
            return completed / len(details) if details else 0

        recent_rate = calc_success_rate(recent_half)
        early_rate = calc_success_rate(early_half)

        if recent_rate > early_rate + 0.1:
            trend = "improving"
        elif recent_rate < early_rate - 0.1:
            trend = "declining"
        else:
            trend = "stable"

        return {
            "trend": trend,
            "recent_success_rate": recent_rate,
            "early_success_rate": early_rate,
            "change": recent_rate - early_rate
        }

    def assess_current_state(self) -> EvolutionState:
        """评估当前进化状态"""
        # 统计进化历史
        completed_files = list(self.state_dir.glob("evolution_completed_*.json"))

        total_rounds = len(completed_files)
        completed_rounds = 0
        failed_rounds = 0

        for f in completed_files:
            try:
                with open(f, 'r', encoding='utf-8') as fp:
                    data = json.load(fp)
                    status = str(data.get("是否完成", ""))
                    if "完成" in status:
                        completed_rounds += 1
                    elif "未完成" in status:
                        failed_rounds += 1
            except Exception:
                pass

        # 计算成功率
        success_rate = completed_rounds / total_rounds if total_rounds > 0 else 0

        # 评估健康分数（基于成功率和完成度）
        health_score = success_rate * 0.7 + (completed_rounds / 500) * 0.3 if total_rounds > 0 else 0.5

        # 统计能力和引擎数量
        capability_count = self._count_capabilities()
        engine_count = self._count_engines()

        return EvolutionState(
            total_rounds=total_rounds,
            completed_rounds=completed_rounds,
            failed_rounds=failed_rounds,
            avg_completion_time=0,  # 简化处理
            success_rate=success_rate,
            health_score=health_score,
            capability_count=capability_count,
            engine_count=engine_count
        )

    def _count_capabilities(self) -> int:
        """统计能力数量"""
        capabilities_file = self.runtime_dir.parent / "references" / "capabilities.md"
        if not capabilities_file.exists():
            return 0

        try:
            content = capabilities_file.read_text(encoding='utf-8')
            # 简单统计 "| 已覆盖" 出现次数
            return content.count("| 已覆盖")
        except Exception:
            return 0

    def _count_engines(self) -> int:
        """统计引擎数量"""
        scripts_dir = Path(__file__).parent
        engine_files = list(scripts_dir.glob("evolution_*.py"))
        return len(engine_files)

    def identify_goal_gaps(self) -> List[GoalGap]:
        """识别目标差距"""
        gaps = []
        state = self.assess_current_state()

        # 能力覆盖差距
        if state.capability_count < 50:
            gaps.append(GoalGap(
                gap_id="gap_capability",
                category="capability",
                current_state=f"已覆盖 {state.capability_count} 项能力",
                ideal_state="覆盖主要电脑操作能力（50+项）",
                gap_severity=1 - (state.capability_count / 50),
                suggested_actions=["增强能力覆盖", "扩展应用场景", "增加多模态能力"]
            ))

        # 健康度差距
        if state.health_score < 0.8:
            gaps.append(GoalGap(
                gap_id="gap_health",
                category="health",
                current_state=f"健康分数 {state.health_score:.2f}",
                ideal_state="健康分数 0.8+",
                gap_severity=1 - state.health_score,
                suggested_actions=["提升进化成功率", "增强自愈能力", "优化执行效率"]
            ))

        # 自主性差距
        if state.success_rate < 0.9:
            gaps.append(GoalGap(
                gap_id="gap_autonomy",
                category="autonomy",
                current_state=f"成功率 {state.success_rate:.2f}",
                ideal_state="成功率 0.9+",
                gap_severity=1 - state.success_rate,
                suggested_actions=["增强决策质量", "优化执行策略", "增加预防性维护"]
            ))

        # 添加一些基于分析的建议
        history_analysis = self.analyze_evolution_history()
        if history_analysis.get("trends", {}).get("trend") == "declining":
            gaps.append(GoalGap(
                gap_id="gap_trend",
                category="trend",
                current_state="进化成功率下降趋势",
                ideal_state="稳定或上升趋势",
                gap_severity=0.7,
                suggested_actions=["分析下降原因", "增强预防性干预", "优化进化策略"]
            ))

        return gaps

    def generate_strategic_directions(self) -> List[StrategicDirection]:
        """生成战略方向"""
        directions = []
        gaps = self.identify_goal_gaps()
        history = self.analyze_evolution_history()

        # 基于差距生成方向
        for gap in gaps:
            if gap.category == "capability":
                directions.append(StrategicDirection(
                    direction_id="strat_capability",
                    title="能力扩展战略",
                    description=f"扩展能力覆盖，缩小与目标的差距。当前{gap.current_state}。",
                    priority=0.8,
                    estimated_impact=0.7,
                    risk_level=0.3,
                    dependencies=["evolution_knowledge_driven_emergence_execution_engine.py"],
                    expected_outcome="能力覆盖达到50+项"
                ))
            elif gap.category == "health":
                directions.append(StrategicDirection(
                    direction_id="strat_health",
                    title="健康提升战略",
                    description=f"提升系统健康度。当前{gap.current_state}。",
                    priority=0.9,
                    estimated_impact=0.8,
                    risk_level=0.2,
                    dependencies=["evolution_meta_evolution_internal_health_diagnosis_self_healing_engine.py"],
                    expected_outcome="健康分数达到0.8+"
                ))
            elif gap.category == "autonomy":
                directions.append(StrategicDirection(
                    direction_id="strat_autonomy",
                    title="自主性增强战略",
                    description=f"提升进化成功率。当前{gap.current_state}。",
                    priority=0.85,
                    estimated_impact=0.75,
                    risk_level=0.25,
                    dependencies=["evolution_decision_execution_learning_integration_engine.py"],
                    expected_outcome="成功率提升到0.9+"
                ))

        # 基于趋势生成方向
        trends = history.get("trends", {})
        if trends.get("trend") == "declining":
            directions.append(StrategicDirection(
                direction_id="strat_trend",
                title="趋势逆转战略",
                description="逆转当前下降趋势，恢复到稳定或上升状态。",
                priority=0.95,
                estimated_impact=0.9,
                risk_level=0.15,
                dependencies=["evolution_preventive_intervention_evaluation_optimizer_engine.py"],
                expected_outcome="趋势转为稳定或上升"
            ))

        # 通用战略：持续创新
        directions.append(StrategicDirection(
            direction_id="strat_innovation",
            title="持续创新战略",
            description="保持创新动力，持续发现新的优化机会和进化方向。",
            priority=0.7,
            estimated_impact=0.6,
            risk_level=0.4,
            dependencies=["evolution_emergence_discovery_innovation_engine.py"],
            expected_outcome="持续产生高价值创新"
        ))

        # 按分数排序
        directions.sort(key=lambda x: x.score, reverse=True)

        return directions

    def plan_evolution_direction(self, focus_areas: List[str] = None) -> Dict:
        """规划进化方向"""
        if focus_areas is None:
            focus_areas = []

        strategic = self.generate_strategic_directions()

        # 如果指定了关注领域，过滤
        if focus_areas:
            strategic = [s for s in strategic if any(f.lower() in s.title.lower() for f in focus_areas)]

        # 选择最佳方向
        best_direction = strategic[0] if strategic else None

        return {
            "recommended_direction": best_direction.to_dict() if best_direction else None,
            "alternatives": [s.to_dict() for s in strategic[1:5]] if len(strategic) > 1 else [],
            "focus_areas": focus_areas,
            "timestamp": datetime.now().isoformat()
        }

    def get_cockpit_data(self) -> Dict:
        """获取驾驶舱数据"""
        status = self.get_status()

        return {
            "self_awareness": {
                "total_evolution_rounds": status["history_analysis"]["total_rounds"],
                "success_rate": status["state_assessment"].success_rate,
                "health_score": status["state_assessment"].health_score,
                "capability_count": status["state_assessment"].capability_count,
                "engine_count": status["state_assessment"].engine_count
            },
            "strategic_planning": {
                "top_priority": status["strategic_directions"][0].to_dict() if status["strategic_directions"] else None,
                "total_directions": len(status["strategic_directions"])
            },
            "goal_gaps": {
                "total_gaps": len(status["goal_gaps"]),
                "critical_gaps": [g for g in status["goal_gaps"] if g["gap_severity"] > 0.5]
            },
            "patterns": status["history_analysis"]["patterns"],
            "trends": status["history_analysis"]["trends"],
            "timestamp": status["timestamp"]
        }


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(
        description="智能全场景进化环自我进化意识与战略规划引擎"
    )
    parser.add_argument("--status", action="store_true", help="获取引擎状态")
    parser.add_argument("--analyze-history", action="store_true", help="分析进化历史")
    parser.add_argument("--assess-state", action="store_true", help="评估当前状态")
    parser.add_argument("--identify-gaps", action="store_true", help="识别目标差距")
    parser.add_argument("--plan-direction", action="store_true", help="规划进化方向")
    parser.add_argument("--focus-areas", nargs="*", help="关注领域列表")
    parser.add_argument("--cockpit-data", action="store_true", help="获取驾驶舱数据")
    parser.add_argument("--runtime-dir", type=str, help="运行时目录路径")

    args = parser.parse_args()

    # 初始化引擎
    engine = SelfEvolutionConsciousnessEngine(
        runtime_dir=args.runtime_dir if args.runtime_dir else None
    )

    # 执行命令
    if args.status:
        result = engine.get_status()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.analyze_history:
        result = engine.analyze_evolution_history()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.assess_state:
        state = engine.assess_current_state()
        print(json.dumps(state.to_dict(), ensure_ascii=False, indent=2))
    elif args.identify_gaps:
        gaps = engine.identify_goal_gaps()
        print(json.dumps([g.to_dict() for g in gaps], ensure_ascii=False, indent=2))
    elif args.plan_direction:
        result = engine.plan_evolution_direction(args.focus_areas)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.cockpit_data:
        result = engine.get_cockpit_data()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        # 默认显示状态
        result = engine.get_status()
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()