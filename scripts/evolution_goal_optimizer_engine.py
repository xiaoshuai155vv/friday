#!/usr/bin/env python3
"""
智能全场景进化环目标自优化引擎 (Evolution Goal Self-Optimizer Engine)

让系统能够自动评估进化目标的价值、检验目标设定的合理性、发现目标遗漏、
自动优化目标体系，形成"目标→执行→评估→优化目标"的元进化闭环。

这是进化环的"目标层面"优化器，与执行层面的优化器（evolution_loop_self_optimizer.py）
形成互补——一个优化"如何执行"，一个优化"设定什么目标"。

Version: 1.0.0
Author: AI Evolution System
"""

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
STATE_DIR = PROJECT_ROOT / "runtime" / "state"
LOGS_DIR = PROJECT_ROOT / "runtime" / "logs"
REFERENCES_DIR = PROJECT_ROOT / "references"


class EvolutionGoalOptimizer:
    """进化目标自优化引擎核心类"""

    def __init__(self):
        self.version = "1.0.0"
        self.name = "Evolution Goal Self-Optimizer Engine"
        self.capabilities = [
            "目标价值评估",
            "目标合理性检验",
            "目标遗漏发现",
            "目标体系优化",
            "目标依赖分析",
            "目标优先级排序",
            "元目标反思"
        ]

    def evaluate_goal_value(self, goal: str, context: Dict = None) -> Dict:
        """
        评估进化目标的价值

        Args:
            goal: 进化目标描述
            context: 额外的上下文信息

        Returns:
            价值评估结果
        """
        # 分析目标与系统现有能力的匹配度
        capabilities_file = REFERENCES_DIR / "capabilities.md"
        existing_goals_file = REFERENCES_DIR / "evolution_self_proposed.md"

        value_score = 0.7  # 基础分数
        match_reasons = []

        # 检查与现有能力的关系
        if capabilities_file.exists():
            with open(capabilities_file, 'r', encoding='utf-8') as f:
                capabilities = f.read()
                # 简单的关键词匹配
                keywords = ['引擎', '能力', '自动化', '智能', '自主', '协同']
                for kw in keywords:
                    if kw in goal and kw in capabilities:
                        value_score += 0.05
                        match_reasons.append(f"与现有{kw}能力相关")

        # 检查是否与已有进化目标重复
        if existing_goals_file.exists():
            with open(existing_goals_file, 'r', encoding='utf-8') as f:
                existing_content = f.read()
                if goal in existing_content:
                    value_score -= 0.2
                    match_reasons.append("可能与已有目标重复")

        # 计算最终得分
        value_score = min(1.0, max(0.0, value_score))

        return {
            "goal": goal,
            "value_score": round(value_score, 2),
            "match_reasons": match_reasons,
            "evaluation_time": datetime.now().isoformat()
        }

    def validate_goal_reasonableness(self, goal: str) -> Dict:
        """
        检验目标设定的合理性

        Args:
            goal: 进化目标描述

        Returns:
            合理性检验结果
        """
        issues = []
        score = 1.0

        # 检查目标是否过于模糊
        vague_patterns = ['增强', '优化', '改进', '提升']
        has_vague = any(p in goal for p in vague_patterns)
        if has_vague:
            score -= 0.1
            issues.append("目标描述较模糊，建议添加具体指标")

        # 检查目标是否过于宽泛
        if len(goal) > 50:
            score -= 0.15
            issues.append("目标描述过于宽泛，建议拆分为多个子目标")

        # 检查是否缺少可执行性
        action_words = ['创建', '实现', '集成', '构建', '开发', '生成']
        has_action = any(a in goal for a in action_words)
        if not has_action:
            score -= 0.2
            issues.append("缺少明确的行动词，建议添加'创建'、'实现'等")

        # 检查目标是否与其他目标冲突
        if "自省" in goal and "元认知" in goal:
            issues.append("与元认知能力可能存在功能重叠")

        score = max(0.0, score)

        return {
            "goal": goal,
            "reasonableness_score": round(score, 2),
            "issues": issues,
            "suggestions": self._generate_suggestions(issues),
            "validation_time": datetime.now().isoformat()
        }

    def discover_goal_gaps(self) -> Dict:
        """
        发现目标遗漏 - 分析当前目标体系的空白

        Returns:
            目标遗漏发现结果
        """
        gaps = []

        # 读取当前的进化目标
        current_mission_file = STATE_DIR / "current_mission.json"
        if current_mission_file.exists():
            with open(current_mission_file, 'r', encoding='utf-8') as f:
                mission = json.load(f)
                current_goal = mission.get("current_goal", "")

                # 分析当前目标覆盖的维度
                dimensions = {
                    "执行优化": "执行" in current_goal or "优化" in current_goal,
                    "目标优化": "目标" in current_goal or "元" in current_goal,
                    "知识管理": "知识" in current_goal,
                    "健康监控": "健康" in current_goal or "监控" in current_goal,
                    "创新驱动": "创新" in current_goal or "创造" in current_goal,
                }

                # 检查遗漏的维度
                for dim, covered in dimensions.items():
                    if not covered:
                        gaps.append({
                            "dimension": dim,
                            "description": f"当前目标体系缺少{dim}维度的优化",
                            "priority": "high" if dim in ["目标优化", "创新驱动"] else "medium"
                        })

        # 基于能力缺口检查遗漏
        gaps_file = REFERENCES_DIR / "capability_gaps.md"
        if gaps_file.exists():
            with open(gaps_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if "已覆盖" in content:
                    # 能力缺口基本覆盖
                    pass
                else:
                    gaps.append({
                        "dimension": "能力扩展",
                        "description": "发现新的能力缺口",
                        "priority": "medium"
                    })

        return {
            "gaps": gaps,
            "total_gaps": len(gaps),
            "discovery_time": datetime.now().isoformat()
        }

    def optimize_goal_system(self, goals: List[str] = None) -> Dict:
        """
        优化目标体系 - 对多个目标进行整体优化

        Args:
            goals: 目标列表，如果为None则从当前状态获取

        Returns:
            优化后的目标体系
        """
        if goals is None:
            # 从历史中获取目标
            goals = self._get_recent_goals()

        # 分析目标间的依赖关系
        dependencies = self._analyze_dependencies(goals)

        # 优先级排序
        priorities = self._calculate_priorities(goals)

        # 生成优化建议
        optimizations = []
        for i, goal in enumerate(goals):
            opt = {
                "original_goal": goal,
                "optimized_goal": self._optimize_single_goal(goal),
                "priority": priorities[i],
                "dependencies": dependencies.get(goal, [])
            }
            optimizations.append(opt)

        return {
            "original_goals": goals,
            "optimizations": optimizations,
            "dependency_graph": dependencies,
            "total_goals": len(goals),
            "optimization_time": datetime.now().isoformat()
        }

    def analyze_goal_dependencies(self, goal: str) -> Dict:
        """
        分析目标间的依赖关系

        Args:
            goal: 目标描述

        Returns:
            依赖分析结果
        """
        dependencies = []
        required_by = []

        # 分析元认知相关目标
        if "元认知" in goal or "认知" in goal:
            dependencies.append("自我意识")
            required_by.append("智慧觉醒")

        # 分析执行相关目标
        if "执行" in goal:
            dependencies.append("决策引擎")

        # 分析健康相关目标
        if "健康" in goal or "自愈" in goal:
            dependencies.append("监控系统")

        return {
            "goal": goal,
            "dependencies": dependencies,
            "required_by": required_by,
            "dependency_score": len(dependencies) / 10.0 if dependencies else 0.0,
            "analysis_time": datetime.now().isoformat()
        }

    def reflect_on_goals(self) -> Dict:
        """
        元目标反思 - 对当前目标设定框架本身的反思

        Returns:
            反思结果
        """
        # 获取当前目标
        current_mission_file = STATE_DIR / "current_mission.json"
        current_goal = ""
        if current_mission_file.exists():
            with open(current_mission_file, 'r', encoding='utf-8') as f:
                mission = json.load(f)
                current_goal = mission.get("current_goal", "")

        # 分析目标设定模式
        patterns = self._analyze_goal_patterns()

        # 识别盲点
        blind_spots = self._identify_blind_spots(patterns)

        # 生成反思洞察
        insights = []
        if patterns.get("avg_length", 0) > 40:
            insights.append("目标描述平均长度较高，可能过于复杂")

        if patterns.get("vague_ratio", 0) > 0.5:
            insights.append("模糊词汇使用率较高，目标需要更具体")

        if blind_spots:
            insights.append(f"识别到{len(blind_spots)}个目标设定盲点")

        return {
            "current_goal": current_goal,
            "patterns": patterns,
            "blind_spots": blind_spots,
            "insights": insights,
            "reflection_score": 1.0 - len(blind_spots) * 0.1,
            "reflection_time": datetime.now().isoformat()
        }

    def _get_recent_goals(self) -> List[str]:
        """获取最近的进化目标"""
        goals = []

        # 从 current_mission 获取当前目标
        current_mission_file = STATE_DIR / "current_mission.json"
        if current_mission_file.exists():
            with open(current_mission_file, 'r', encoding='utf-8') as f:
                mission = json.load(f)
                goal = mission.get("current_goal", "")
                if goal:
                    goals.append(goal)

        # 从 evolution_self_proposed 获取待执行目标
        proposed_file = REFERENCES_DIR / "evolution_self_proposed.md"
        if proposed_file.exists():
            with open(proposed_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # 提取待执行的目标
                import re
                matches = re.findall(r'\| ([^|]+) \|.*?\| 待执行 \|', content)
                goals.extend(matches[:5])

        return goals[:10]

    def _analyze_dependencies(self, goals: List[str]) -> Dict:
        """分析目标间的依赖关系"""
        dependencies = {}

        for goal in goals:
            deps = []
            if "元" in goal:
                deps.append("基础能力")
            if "优化" in goal or "增强" in goal:
                deps.append("基础功能")
            if "自动化" in goal:
                deps.append("手动执行能力")
            dependencies[goal] = deps

        return dependencies

    def _calculate_priorities(self, goals: List[str]) -> List[float]:
        """计算目标优先级"""
        priorities = []

        for goal in goals:
            priority = 0.5  # 基础优先级

            # 基于关键词调整优先级
            if "自" in goal or "自主" in goal:
                priority += 0.2
            if "闭环" in goal:
                priority += 0.15
            if "深度" in goal:
                priority += 0.1
            if "自动" in goal:
                priority += 0.1

            priorities.append(min(1.0, priority))

        return priorities

    def _optimize_single_goal(self, goal: str) -> str:
        """优化单个目标"""
        # 去除冗余词汇
        optimized = goal

        # 添加更具体的描述
        if "引擎" in goal and "实现" not in goal:
            optimized = goal.replace("引擎", "引擎 - 实现")

        return optimized

    def _analyze_goal_patterns(self) -> Dict:
        """分析目标设定模式"""
        goals = self._get_recent_goals()

        if not goals:
            return {"avg_length": 0, "vague_ratio": 0}

        avg_length = sum(len(g) for g in goals) / len(goals)

        vague_words = ['增强', '优化', '提升', '改进', '完善']
        vague_count = sum(1 for g in goals for w in vague_words if w in g)
        vague_ratio = vague_count / len(goals) if goals else 0

        return {
            "avg_length": round(avg_length, 2),
            "vague_ratio": round(vague_ratio, 2),
            "total_goals": len(goals)
        }

    def _identify_blind_spots(self, patterns: Dict) -> List[str]:
        """识别目标设定盲点"""
        blind_spots = []

        # 检查是否缺少特定类型的目标
        if patterns.get("vague_ratio", 0) > 0.5:
            blind_spots.append("过于依赖模糊词汇")

        if patterns.get("avg_length", 0) > 45:
            blind_spots.append("目标描述过于冗长")

        # 检查是否缺少执行层面的目标
        goals = self._get_recent_goals()
        has_execution = any("执行" in g for g in goals)
        if not has_execution:
            blind_spots.append("缺少执行层面的优化目标")

        return blind_spots

    def _generate_suggestions(self, issues: List[str]) -> List[str]:
        """生成改进建议"""
        suggestions = []

        for issue in issues:
            if "模糊" in issue:
                suggestions.append("将目标拆分为具体可衡量的子目标")
            if "宽泛" in issue:
                suggestions.append("缩小目标范围，聚焦于单一能力点")
            if "缺少" in issue and "行动词" in issue:
                suggestions.append("添加明确的行动词如'创建'、'实现'、'集成'")
            if "重叠" in issue:
                suggestions.append("重新定义目标边界，避免功能重叠")

        return suggestions


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(
        description="智能全场景进化环目标自优化引擎"
    )
    parser.add_argument(
        "--evaluate",
        type=str,
        help="评估指定目标的价值"
    )
    parser.add_argument(
        "--validate",
        type=str,
        help="检验目标设定的合理性"
    )
    parser.add_argument(
        "--discover-gaps",
        action="store_true",
        help="发现目标遗漏"
    )
    parser.add_argument(
        "--optimize",
        action="store_true",
        help="优化目标体系"
    )
    parser.add_argument(
        "--analyze-deps",
        type=str,
        help="分析目标依赖"
    )
    parser.add_argument(
        "--reflect",
        action="store_true",
        help="元目标反思"
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="显示引擎状态"
    )

    args = parser.parse_args()

    engine = EvolutionGoalOptimizer()

    if args.status:
        print(f"\n=== {engine.name} ===")
        print(f"Version: {engine.version}")
        print(f"Capabilities:")
        for cap in engine.capabilities:
            print(f"  - {cap}")
        return

    if args.evaluate:
        result = engine.evaluate_goal_value(args.evaluate)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if args.validate:
        result = engine.validate_goal_reasonableness(args.validate)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if args.discover_gaps:
        result = engine.discover_goal_gaps()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if args.optimize:
        result = engine.optimize_goal_system()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if args.analyze_deps:
        result = engine.analyze_goal_dependencies(args.analyze_deps)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if args.reflect:
        result = engine.reflect_on_goals()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    # 默认显示帮助
    parser.print_help()


if __name__ == "__main__":
    main()