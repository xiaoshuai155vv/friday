"""
智能全场景进化环目标自优化引擎 (Evolution Goal Self-Optimizer Engine)
版本: 1.0.0

让系统能够自动评估进化目标的价值、检验目标设定的合理性、发现目标遗漏、
自动优化目标体系，形成「目标→执行→评估→优化目标」的元进化闭环。

核心能力:
1. 目标价值评估 - 评估每个进化目标的多维度价值
2. 目标合理性检验 - 验证目标设定的合理性、可行性和完整性
3. 目标遗漏发现 - 自动发现被忽视但有价值的进化方向
4. 目标体系优化 - 基于评估结果动态优化目标优先级和组合
5. 元目标闭环 - 让目标本身也能不断进化和优化
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

class EvolutionGoalSelfOptimizer:
    """进化目标自优化引擎"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.runtime_state_dir = self.project_root / "runtime" / "state"
        self.references_dir = self.project_root / "references"

        # 目标评估维度权重
        self.evaluation_weights = {
            "value": 0.3,        # 价值贡献度
            "feasibility": 0.2,  # 可行性
            "completeness": 0.15, # 完整性
            "innovation": 0.2,  # 创新性
            "urgency": 0.15     # 紧迫度
        }

    def evaluate_goal(self, goal: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        评估单个进化目标的多维度价值

        Args:
            goal: 进化目标描述
            context: 上下文信息（当前系统状态、进化历史等）

        Returns:
            评估结果字典
        """
        context = context or {}

        # 多维度评估
        evaluation = {
            "goal": goal,
            "timestamp": datetime.now().isoformat(),
            "scores": {},
            "total_score": 0.0,
            "level": "",
            "suggestions": []
        }

        # 1. 价值贡献度评估
        value_score = self._evaluate_value(goal, context)
        evaluation["scores"]["value"] = value_score

        # 2. 可行性评估
        feasibility_score = self._evaluate_feasibility(goal, context)
        evaluation["scores"]["feasibility"] = feasibility_score

        # 3. 完整性评估
        completeness_score = self._evaluate_completeness(goal, context)
        evaluation["scores"]["completeness"] = completeness_score

        # 4. 创新性评估
        innovation_score = self._evaluate_innovation(goal, context)
        evaluation["scores"]["innovation"] = innovation_score

        # 5. 紧迫度评估
        urgency_score = self._evaluate_urgency(goal, context)
        evaluation["scores"]["urgency"] = urgency_score

        # 计算总分
        total = sum(
            score * self.evaluation_weights[dim]
            for dim, score in evaluation["scores"].items()
        )
        evaluation["total_score"] = round(total, 3)

        # 评级
        if total >= 0.8:
            evaluation["level"] = "优秀"
        elif total >= 0.6:
            evaluation["level"] = "良好"
        elif total >= 0.4:
            evaluation["level"] = "一般"
        else:
            evaluation["level"] = "待改进"

        # 生成优化建议
        evaluation["suggestions"] = self._generate_suggestions(evaluation)

        return evaluation

    def _evaluate_value(self, goal: str, context: Dict) -> float:
        """评估目标的价值贡献度"""
        # 基于关键词分析价值维度
        high_value_keywords = {
            "自主": 0.9, "自我": 0.85, "自动": 0.8, "智能": 0.75,
            "闭环": 0.8, "进化": 0.7, "协同": 0.7, "集成": 0.65
        }

        score = 0.5  # 基础分
        for keyword, weight in high_value_keywords.items():
            if keyword in goal:
                score = max(score, weight)

        return min(score, 1.0)

    def _evaluate_feasibility(self, goal: str, context: Dict) -> float:
        """评估目标的可行性"""
        # 检查是否有明确的动作词和可执行性
        executable_keywords = ["创建", "实现", "集成", "增强", "优化", "生成", "构建"]

        has_action = any(kw in goal for kw in executable_keywords)

        # 复杂度评估 - 太长或太复杂的可能难以实现
        complexity_penalty = 0.0
        if len(goal) > 80:
            complexity_penalty = 0.2

        score = 0.8 if has_action else 0.5
        return max(score - complexity_penalty, 0.3)

    def _evaluate_completeness(self, goal: str, context: Dict) -> float:
        """评估目标的完整性"""
        # 检查是否包含「让系统能够」「形成」等完整性表述
        completeness_indicators = ["让系统", "形成", "实现", "具备", "提供", "支持"]

        has_completeness = any(indicator in goal for indicator in completeness_indicators)

        # 检查是否包含多个能力点（用顿号、分号分隔）
        separators = ["、", "；", ","]
        has_multiple = any(sep in goal for sep in separators)

        score = 0.7
        if has_completeness:
            score += 0.15
        if has_multiple:
            score += 0.15

        return min(score, 1.0)

    def _evaluate_innovation(self, goal: str, context: Dict) -> float:
        """评估目标的创新性"""
        # 创新关键词
        innovation_keywords = {
            "新": 0.8, "原创": 0.9, "首次": 0.85, "独创": 0.9,
            "突破": 0.85, "范式升级": 0.9, "深度": 0.7, "增强": 0.6
        }

        score = 0.5
        for keyword, weight in innovation_keywords.items():
            if keyword in goal:
                score = max(score, weight)

        return min(score, 1.0)

    def _evaluate_urgency(self, goal: str, context: Dict) -> float:
        """评估目标的紧迫度"""
        # 基于当前系统状态和历史
        urgency_keywords = {
            "紧急": 0.9, "优先": 0.8, "关键": 0.75, "核心": 0.7,
            "基础": 0.7, "必须": 0.8, "亟待": 0.85
        }

        score = 0.5
        for keyword, weight in urgency_keywords.items():
            if keyword in goal:
                score = max(score, weight)

        return min(score, 1.0)

    def _generate_suggestions(self, evaluation: Dict) -> List[str]:
        """基于评估结果生成优化建议"""
        suggestions = []

        scores = evaluation["scores"]

        if scores.get("value", 0) < 0.6:
            suggestions.append("建议：增强目标的价值贡献度，明确对系统的具体提升")

        if scores.get("feasibility", 0) < 0.6:
            suggestions.append("建议：简化目标描述，使其更易于执行和实现")

        if scores.get("completeness", 0) < 0.6:
            suggestions.append("建议：完善目标描述，包含完整的能力闭环")

        if scores.get("innovation", 0) < 0.6:
            suggestions.append("建议：增加创新元素，考虑突破性的实现方式")

        if scores.get("urgency", 0) < 0.6:
            suggestions.append("建议：明确目标的紧迫性和优先级")

        if not suggestions:
            suggestions.append("目标设定优秀，保持当前方向")

        return suggestions

    def validate_goal_system(self, goals: List[str], context: Dict = None) -> Dict[str, Any]:
        """
        验证目标体系的完整性和一致性

        Args:
            goals: 目标列表
            context: 上下文信息

        Returns:
            验证结果
        """
        context = context or {}

        validation = {
            "timestamp": datetime.now().isoformat(),
            "total_goals": len(goals),
            "individual_evaluations": [],
            "system_score": 0.0,
            "issues": [],
            "optimizations": []
        }

        # 评估每个目标
        for goal in goals:
            eval_result = self.evaluate_goal(goal, context)
            validation["individual_evaluations"].append(eval_result)

        # 整体评分 - 平均分
        if validation["individual_evaluations"]:
            avg_scores = [
                e["total_score"]
                for e in validation["individual_evaluations"]
            ]
            validation["system_score"] = round(sum(avg_scores) / len(avg_scores), 3)

        # 检查问题
        validation["issues"] = self._check_system_issues(validation)

        # 生成优化建议
        validation["optimizations"] = self._generate_system_optimizations(validation)

        return validation

    def _check_system_issues(self, validation: Dict) -> List[str]:
        """检查目标体系的问题"""
        issues = []

        # 检查目标数量
        if validation["total_goals"] < 3:
            issues.append("目标数量过少，建议至少3个以保证多样性")

        if validation["total_goals"] > 10:
            issues.append("目标数量过多，可能导致资源分散")

        # 检查分数分布
        scores = [e["total_score"] for e in validation["individual_evaluations"]]
        if scores:
            low_score_count = sum(1 for s in scores if s < 0.5)
            if low_score_count > validation["total_goals"] * 0.3:
                issues.append("超过30%的目标评分较低，建议重新评估这些目标的价值")

        return issues

    def _generate_system_optimizations(self, validation: Dict) -> List[str]:
        """生成目标体系优化建议"""
        optimizations = []

        # 基于系统评分
        if validation["system_score"] < 0.6:
            optimizations.append("整体目标体系评分较低，建议重新梳理进化方向")

        # 基于问题
        issues = validation.get("issues", [])
        if "目标数量过少" in str(issues):
            optimizations.append("增加目标多样性，覆盖更多进化维度")

        # 找出最需要改进的目标
        if validation["individual_evaluations"]:
            sorted_goals = sorted(
                validation["individual_evaluations"],
                key=lambda x: x["total_score"]
            )
            if sorted_goals:
                lowest = sorted_goals[0]
                optimizations.append(
                    f"优先改进目标「{lowest['goal'][:30]}...」评分最低({lowest['total_score']})"
                )

        return optimizations

    def discover_missing_goals(self, context: Dict = None) -> List[Dict[str, Any]]:
        """
        自动发现被遗漏但有价值的进化方向

        Args:
            context: 上下文信息

        Returns:
            发现的遗漏目标列表
        """
        context = context or {}

        discovered = []

        # 分析现有能力缺口
        gaps_file = self.references_dir / "capability_gaps.md"
        if gaps_file.exists():
            with open(gaps_file, "r", encoding="utf-8") as f:
                content = f.read()
                # 简单分析未覆盖领域
                if "待扩展" in content or "可行方向" in content:
                    discovered.append({
                        "type": "capability_gap",
                        "description": "基于能力缺口分析发现的进化方向",
                        "priority": 0.7
                    })

        # 分析失败教训
        failures_file = self.references_dir / "failures.md"
        if failures_file.exists():
            with open(failures_file, "r", encoding="utf-8") as f:
                content = f.read()
                # 提取失败的模式
                if "下次" in content:
                    discovered.append({
                        "type": "failure_learn",
                        "description": "基于历史失败教训发现的改进方向",
                        "priority": 0.8
                    })

        # 分析进化历史趋势
        auto_last = self.references_dir / "evolution_auto_last.md"
        if auto_last.exists():
            with open(auto_last, "r", encoding="utf-8") as f:
                content = f.read()
                # 检查最近的进化方向
                if "round" in content:
                    discovered.append({
                        "type": "evolution_trend",
                        "description": "基于进化趋势分析发现的新方向",
                        "priority": 0.6
                    })

        # 添加一些通用的遗漏领域
        discovered.extend([
            {
                "type": "system_health",
                "description": "系统长期健康监控与预防性维护",
                "priority": 0.75
            },
            {
                "type": "user_experience",
                "description": "用户体验持续优化与反馈闭环",
                "priority": 0.7
            },
            {
                "type": "performance",
                "description": "系统性能自动化优化与资源管理",
                "priority": 0.8
            }
        ])

        return discovered

    def optimize_goal_hierarchy(self, goals: List[str], context: Dict = None) -> Dict[str, Any]:
        """
        优化目标层级结构

        Args:
            goals: 原始目标列表
            context: 上下文信息

        Returns:
            优化后的目标层级
        """
        context = context or {}

        # 评估所有目标
        evaluations = [self.evaluate_goal(g, context) for g in goals]

        # 按优先级排序
        sorted_evaluations = sorted(
            evaluations,
            key=lambda x: (x["total_score"], x["scores"].get("urgency", 0)),
            reverse=True
        )

        # 分层
        optimization = {
            "timestamp": datetime.now().isoformat(),
            "original_count": len(goals),
            "layers": {
                "critical": [],    # 紧急且重要
                "important": [],  # 重要但非紧急
                "improving": [],  # 需要改进
                "optional": []    # 可选
            },
            "recommended_execution_order": []
        }

        for eval_item in sorted_evaluations:
            goal = eval_item["goal"]
            score = eval_item["total_score"]
            urgency = eval_item["scores"].get("urgency", 0)

            if score >= 0.8 and urgency >= 0.7:
                optimization["layers"]["critical"].append(goal)
                optimization["recommended_execution_order"].append(goal)
            elif score >= 0.6:
                optimization["layers"]["important"].append(goal)
                optimization["recommended_execution_order"].append(goal)
            elif score >= 0.4:
                optimization["layers"]["improving"].append(goal)
            else:
                optimization["layers"]["optional"].append(goal)

        return optimization

    def get_status(self) -> Dict[str, Any]:
        """获取引擎状态"""
        return {
            "engine": "evolution_goal_self_optimizer",
            "version": "1.0.0",
            "status": "active",
            "capabilities": [
                "目标价值评估",
                "目标合理性检验",
                "目标遗漏发现",
                "目标体系优化",
                "目标层级优化"
            ],
            "evaluation_weights": self.evaluation_weights,
            "timestamp": datetime.now().isoformat()
        }

    def analyze(self, mode: str = "status") -> Dict[str, Any]:
        """
        分析入口

        Args:
            mode: 分析模式
                - status: 获取引擎状态
                - discover: 发现遗漏目标
                - validate: 验证目标体系

        Returns:
            分析结果
        """
        if mode == "status":
            return self.get_status()
        elif mode == "discover":
            return {
                "discovered_goals": self.discover_missing_goals()
            }
        elif mode == "validate":
            # 默认验证几个示例目标
            sample_goals = [
                "智能全场景进化环目标自优化引擎",
                "让系统能够自动评估进化目标的价值",
                "形成元进化闭环"
            ]
            return self.validate_goal_system(sample_goals)
        else:
            return {"error": f"未知模式: {mode}"}

    def think(self, question: str = "") -> str:
        """
        思考入口

        Args:
            question: 问题

        Returns:
            思考结果
        """
        if not question:
            return "进化目标自优化引擎：帮助系统评估和优化进化目标，实现目标的自我进化。"

        # 基于问题生成回答
        if "目标" in question or "goal" in question.lower():
            return (
                "进化目标自优化引擎的核心职责：\n"
                "1. 评估每个进化目标的价值、可行性、创新性\n"
                "2. 验证目标体系的完整性和一致性\n"
                "3. 发现被遗漏但有价值的进化方向\n"
                "4. 动态优化目标优先级和执行顺序\n"
                "5. 形成目标→执行→评估→优化目标的闭环"
            )
        elif "优化" in question or "optimize" in question.lower():
            return (
                "目标优化策略：\n"
                "- 评估维度：价值(30%)、可行性(20%)、完整性(15%)、创新性(20%)、紧迫度(15%)\n"
                "- 优化方法：分层处理，优先执行高价值高紧迫目标\n"
                "- 持续迭代：每次进化后重新评估目标体系"
            )
        else:
            return "请提出关于进化目标的具体问题。"


def main():
    """主入口"""
    import sys

    engine = EvolutionGoalSelfOptimizer()

    if len(sys.argv) < 2:
        # 默认显示状态
        print(json.dumps(engine.get_status(), ensure_ascii=False, indent=2))
        return

    command = sys.argv[1]

    if command == "status":
        print(json.dumps(engine.get_status(), ensure_ascii=False, indent=2))

    elif command == "analyze":
        mode = sys.argv[2] if len(sys.argv) > 2 else "status"
        result = engine.analyze(mode)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "evaluate":
        # 评估指定目标
        if len(sys.argv) > 2:
            goal = " ".join(sys.argv[2:])
            result = engine.evaluate_goal(goal)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print("用法: python evolution_goal_self_optimizer.py evaluate <目标>")

    elif command == "discover":
        result = engine.discover_missing_goals()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "validate":
        # 示例目标验证
        sample_goals = [
            "智能全场景进化环目标自优化引擎",
            "让系统能够自动评估进化目标的价值",
            "形成元进化闭环"
        ]
        result = engine.validate_goal_system(sample_goals)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "think":
        question = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""
        print(engine.think(question))

    else:
        print(f"未知命令: {command}")
        print("可用命令: status, analyze, evaluate, discover, validate, think")


if __name__ == "__main__":
    main()