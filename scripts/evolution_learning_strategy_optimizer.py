#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能进化学习策略自动优化引擎 (Evolution Learning Strategy Optimizer)
让系统能够自动从历史进化决策和执行结果中学习最优策略，
并将学习到的知识主动应用到每轮进化决策中，实现真正的"学会如何进化"。

功能：
1. 历史进化决策分析 - 分析每轮的决策模式、执行策略、结果
2. 最优策略学习 - 从成功进化中提取最优策略模式
3. 策略模式识别 - 识别不同场景下的最佳策略
4. 自动策略应用 - 将学习到的策略自动应用到新进化决策中
5. 策略效果追踪 - 追踪策略应用效果并持续优化

集成：支持"进化学习策略"、"策略优化"、"学习如何进化"、"自动策略应用"等关键词触发
"""

import os
import sys
import json
import glob
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict

SCRIPTS = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(SCRIPTS)
RUNTIME_STATE = os.path.join(PROJECT, "runtime", "state")
RUNTIME_LOGS = os.path.join(PROJECT, "runtime", "logs")
REFERENCES = os.path.join(PROJECT, "references")


class EvolutionLearningStrategyOptimizer:
    """智能进化学习策略自动优化引擎"""

    def __init__(self):
        self.name = "EvolutionLearningStrategyOptimizer"
        self.version = "1.0.0"
        self.strategy_db_path = os.path.join(RUNTIME_STATE, "evolution_strategy_db.json")
        self.learning_history_path = os.path.join(RUNTIME_STATE, "evolution_learning_history.json")
        self.strategy_patterns_path = os.path.join(RUNTIME_STATE, "evolution_strategy_patterns.json")

        self.strategy_db = self._load_strategy_db()
        self.learning_history = self._load_learning_history()
        self.strategy_patterns = self._load_strategy_patterns()

    def _load_strategy_db(self) -> Dict:
        """加载策略数据库"""
        if os.path.exists(self.strategy_db_path):
            try:
                with open(self.strategy_db_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass

        return {
            "version": "1.0.0",
            "last_updated": datetime.now().isoformat(),
            "strategies": {},
            "best_practices": []
        }

    def _save_strategy_db(self):
        """保存策略数据库"""
        self.strategy_db["last_updated"] = datetime.now().isoformat()
        try:
            with open(self.strategy_db_path, "w", encoding="utf-8") as f:
                json.dump(self.strategy_db, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存策略数据库失败: {e}")

    def _load_learning_history(self) -> Dict:
        """加载学习历史"""
        if os.path.exists(self.learning_history_path):
            try:
                with open(self.learning_history_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass

        return {
            "version": "1.0.0",
            "learning_sessions": [],
            "insights": []
        }

    def _save_learning_history(self):
        """保存学习历史"""
        try:
            with open(self.learning_history_path, "w", encoding="utf-8") as f:
                json.dump(self.learning_history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存学习历史失败: {e}")

    def _load_strategy_patterns(self) -> Dict:
        """加载策略模式库"""
        if os.path.exists(self.strategy_patterns_path):
            try:
                with open(self.strategy_patterns_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass

        return {
            "version": "1.0.0",
            "patterns": {},
            "context_strategies": {}
        }

    def _save_strategy_patterns(self):
        """保存策略模式库"""
        try:
            with open(self.strategy_patterns_path, "w", encoding="utf-8") as f:
                json.dump(self.strategy_patterns, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存策略模式库失败: {e}")

    def _load_completed_evolutions(self, limit: int = 50) -> List[Dict]:
        """加载已完成的进化记录"""
        evolutions = []
        state_dir = Path(RUNTIME_STATE)

        # 查找所有 evolution_completed_*.json 文件
        for f in state_dir.glob("evolution_completed_*.json"):
            try:
                with open(f, "r", encoding="utf-8") as fp:
                    data = json.load(fp)
                    evolutions.append(data)
            except Exception:
                pass

        # 按时间排序
        evolutions.sort(key=lambda x: x.get("completed_at", ""), reverse=True)
        return evolutions[:limit]

    def analyze_historical_decisions(self) -> Dict[str, Any]:
        """分析历史进化决策"""
        evolutions = self._load_completed_evolutions(50)

        analysis = {
            "total_rounds": len(evolutions),
            "successful_rounds": sum(1 for e in evolutions if e.get("status") == "completed"),
            "failed_rounds": sum(1 for e in evolutions if e.get("status") in ["failed", "stale_failed"]),
            "decision_patterns": {},
            "execution_patterns": {},
            "phase_durations": defaultdict(list),
            "strategy_effectiveness": defaultdict(list)
        }

        for evo in evolutions:
            # 分析决策模式
            goal = evo.get("current_goal", "")
            if goal:
                # 提取关键词作为策略类型
                strategy_type = self._extract_strategy_type(goal)
                analysis["decision_patterns"][strategy_type] = \
                    analysis["decision_patterns"].get(strategy_type, 0) + 1

                # 记录策略效果
                status = evo.get("status", "unknown")
                analysis["strategy_effectiveness"][strategy_type].append(
                    1 if status == "completed" else 0
                )

            # 分析执行时长
            for phase in ["assume", "plan", "track", "verify", "decide"]:
                duration = evo.get(f"{phase}_duration_seconds", 0)
                if duration > 0:
                    analysis["phase_durations"][phase].append(duration)

        # 计算各策略类型的成功率
        success_rates = {}
        for strategy, results in analysis["strategy_effectiveness"].items():
            if results:
                success_rates[strategy] = sum(results) / len(results)

        analysis["success_rates"] = success_rates

        # 计算平均阶段时长
        avg_durations = {}
        for phase, durations in analysis["phase_durations"].items():
            if durations:
                avg_durations[phase] = sum(durations) / len(durations)
        analysis["avg_phase_durations"] = avg_durations

        return analysis

    def _extract_strategy_type(self, goal: str) -> str:
        """从目标中提取策略类型"""
        goal_lower = goal.lower()

        # 简单关键词匹配
        if any(kw in goal_lower for kw in ["优化", "增强", "提升", "改进"]):
            return "optimization"
        elif any(kw in goal_lower for kw in ["自动", "自主", "闭环"]):
            return "automation"
        elif any(kw in goal_lower for kw in ["智能", "学习", "推理"]):
            return "intelligent"
        elif any(kw in goal_lower for kw in ["协同", "协作", "多引擎"]):
            return "collaboration"
        elif any(kw in goal_lower for kw in ["服务", "场景", "用户"]):
            return "service"
        elif any(kw in goal_lower for kw in ["健康", "监控", "自愈"]):
            return "health"
        elif any(kw in goal_lower for kw in ["意识", "自我", "自主"]):
            return "self_awareness"
        else:
            return "other"

    def learn_best_practices(self) -> Dict[str, Any]:
        """学习最佳实践"""
        evolutions = self._load_completed_evolutions(50)
        analysis = self.analyze_historical_decisions()

        best_practices = []
        insights = []

        # 从成功的进化中提取最佳实践
        successful = [e for e in evolutions if e.get("status") == "completed"]

        if successful:
            # 统计最成功的策略类型
            if analysis["success_rates"]:
                best_strategy = max(analysis["success_rates"].items(), key=lambda x: x[1])
                best_practices.append({
                    "type": "most_effective_strategy",
                    "strategy": best_strategy[0],
                    "success_rate": best_strategy[1],
                    "description": f"策略类型 '{best_strategy[0]}' 成功率最高，达到 {best_strategy[1]:.1%}"
                })
                insights.append(f"发现最有效的策略类型: {best_strategy[0]}")

            # 分析最佳实践：短周期进化
            if successful:
                avg_completion_time = sum(
                    e.get("total_duration_seconds", 0) for e in successful
                ) / len(successful)
                best_practices.append({
                    "type": "efficient_execution",
                    "metric": "avg_completion_time",
                    "value": avg_completion_time,
                    "description": f"成功进化平均完成时间: {avg_completion_time:.1f}秒"
                })

            # 分析最佳实践：连续成功
            consecutive = self._find_consecutive_successes(evolutions)
            if consecutive > 3:
                best_practices.append({
                    "type": "sustained_success",
                    "consecutive_rounds": consecutive,
                    "description": f"发现连续{consecutive}轮成功进化的模式"
                })
                insights.append(f"发现连续{consecutive}轮成功进化的模式")

        # 添加策略到数据库
        self.strategy_db["best_practices"] = best_practices
        self._save_strategy_db()

        # 添加洞察到学习历史
        self.learning_history["insights"] = insights
        self.learning_history["learning_sessions"].append({
            "timestamp": datetime.now().isoformat(),
            "best_practices_count": len(best_practices),
            "insights": insights
        })
        self._save_learning_history()

        return {
            "best_practices": best_practices,
            "insights": insights,
            "total_successful": len(successful)
        }

    def _find_consecutive_successes(self, evolutions: List[Dict]) -> int:
        """查找连续成功次数"""
        max_consecutive = 0
        current_consecutive = 0

        for evo in evolutions:
            if evo.get("status") == "completed":
                current_consecutive += 1
                max_consecutive = max(max_consecutive, current_consecutive)
            else:
                current_consecutive = 0

        return max_consecutive

    def identify_strategy_patterns(self) -> Dict[str, Any]:
        """识别策略模式"""
        evolutions = self._load_completed_evolutions(30)
        analysis = self.analyze_historical_decisions()

        patterns = {}
        context_strategies = {}

        # 按时间分析策略演变
        if len(evolutions) >= 5:
            # 早期策略
            early = evolutions[15:] if len(evolutions) > 15 else evolutions[:len(evolutions)//2]
            # 近期策略
            recent = evolutions[:15] if len(evolutions) > 15 else evolutions[len(evolutions)//2:]

            early_types = [self._extract_strategy_type(e.get("current_goal", "")) for e in early]
            recent_types = [self._extract_strategy_type(e.get("current_goal", "")) for e in recent]

            # 早期和近期的策略偏好变化
            early_counts = defaultdict(int)
            for t in early_types:
                early_counts[t] += 1

            recent_counts = defaultdict(int)
            for t in recent_types:
                recent_counts[t] += 1

            patterns["evolution_trend"] = {
                "early_preference": dict(early_counts),
                "recent_preference": dict(recent_counts),
                "trend": "从" + str(dict(early_counts)) + "演变到" + str(dict(recent_counts))
            }

        # 识别不同场景的策略
        # 例如：高效进化、快速修复、深度优化等场景
        if analysis.get("avg_phase_durations"):
            fast_rounds = [e for e in evolutions if e.get("total_duration_seconds", 999) < 120]
            slow_rounds = [e for e in evolutions if e.get("total_duration_seconds", 0) >= 120]

            if fast_rounds:
                fast_types = [self._extract_strategy_type(e.get("current_goal", "")) for e in fast_rounds]
                context_strategies["fast_execution"] = {
                    "context": "快速完成（<2分钟）",
                    "recommended_strategies": list(set(fast_types)),
                    "description": "适用于需要快速执行的场景"
                }

            if slow_rounds:
                slow_types = [self._extract_strategy_type(e.get("current_goal", "")) for e in slow_rounds]
                context_strategies["deep_optimization"] = {
                    "context": "深度优化（>=2分钟）",
                    "recommended_strategies": list(set(slow_types)),
                    "description": "适用于需要深入分析和优化的场景"
                }

        # 保存策略模式
        self.strategy_patterns["patterns"] = patterns
        self.strategy_patterns["context_strategies"] = context_strategies
        self._save_strategy_patterns()

        return {
            "patterns": patterns,
            "context_strategies": context_strategies
        }

    def apply_learned_strategy(self, context: Dict = None) -> Dict[str, Any]:
        """应用学习到的策略"""
        if context is None:
            context = {}

        # 获取最佳实践
        best_practices = self.strategy_db.get("best_practices", [])

        # 获取策略模式
        context_strategies = self.strategy_patterns.get("context_strategies", {})

        # 根据上下文选择策略
        recommended_strategies = []

        # 检查是否需要快速执行
        if context.get("priority") == "fast":
            if "fast_execution" in context_strategies:
                recommended_strategies.append(context_strategies["fast_execution"])

        # 检查是否需要深度优化
        if context.get("priority") == "deep":
            if "deep_optimization" in context_strategies:
                recommended_strategies.append(context_strategies["deep_optimization"])

        # 添加通用的最佳实践
        for practice in best_practices[:3]:
            recommended_strategies.append(practice)

        # 生成策略建议
        suggestions = {
            "recommended_approach": recommended_strategies[0]["type"] if recommended_strategies else "standard",
            "alternative_approaches": [s["type"] for s in recommended_strategies[1:4]],
            "reasoning": self._generate_strategy_reasoning(recommended_strategies, context),
            "confidence": 0.8 if len(best_practices) >= 3 else 0.5
        }

        return suggestions

    def _generate_strategy_reasoning(self, strategies: List[Dict], context: Dict) -> str:
        """生成策略推理说明"""
        if not strategies:
            return "基于历史分析，当前没有足够的最佳实践数据，建议使用标准进化流程"

        reasons = []
        for s in strategies[:2]:
            reason = s.get("description", "")
            if reason:
                reasons.append(reason)

        return "；".join(reasons) if reasons else "基于历史进化数据的分析结果"

    def get_optimization_recommendations(self) -> Dict[str, Any]:
        """获取优化建议"""
        analysis = self.analyze_historical_decisions()
        best_practices = self.strategy_db.get("best_practices", [])
        patterns = self.strategy_patterns.get("patterns", {})

        recommendations = []

        # 基于分析结果生成建议
        if analysis.get("avg_phase_durations"):
            durations = analysis["avg_phase_durations"]

            # 找出最耗时的阶段
            if durations:
                slowest_phase = max(durations.items(), key=lambda x: x[1])
                if slowest_phase[1] > 60:  # 超过60秒
                    recommendations.append({
                        "type": "optimization",
                        "target": f"{slowest_phase[0]}_phase",
                        "current_value": slowest_phase[1],
                        "suggestion": f"优化{slowest_phase[0]}阶段执行效率，当前耗时{slowest_phase[1]:.1f}秒",
                        "priority": "high"
                    })

        # 基于策略效果生成建议
        if analysis.get("success_rates"):
            success_rates = analysis["success_rates"]
            lowest_rate = min(success_rates.items(), key=lambda x: x[1])
            if lowest_rate[1] < 0.7:
                recommendations.append({
                    "type": "strategy_improvement",
                    "target": f"strategy_{lowest_rate[0]}",
                    "current_value": lowest_rate[1],
                    "suggestion": f"改进策略类型'{lowest_rate[0]}'的执行方式，当前成功率仅{lowest_rate[1]:.1%}",
                    "priority": "medium"
                })

        # 基于最佳实践生成建议
        for practice in best_practices[:2]:
            recommendations.append({
                "type": "best_practice",
                "target": practice.get("type"),
                "suggestion": practice.get("description", ""),
                "priority": "low"
            })

        return {
            "recommendations": recommendations,
            "total_count": len(recommendations)
        }

    def auto_learn_and_optimize(self) -> Dict[str, Any]:
        """自动学习并优化"""
        # 分析历史决策
        analysis = self.analyze_historical_decisions()

        # 学习最佳实践
        best_practices = self.learn_best_practices()

        # 识别策略模式
        patterns = self.identify_strategy_patterns()

        # 生成优化建议
        recommendations = self.get_optimization_recommendations()

        return {
            "analysis": {
                "total_rounds": analysis["total_rounds"],
                "success_rate": analysis["successful_rounds"] / max(analysis["total_rounds"], 1)
            },
            "best_practices_count": len(best_practices.get("best_practices", [])),
            "patterns_identified": len(patterns.get("patterns", {})),
            "recommendations_count": len(recommendations.get("recommendations", [])),
            "status": "completed"
        }

    def get_status(self) -> Dict[str, Any]:
        """获取引擎状态"""
        return {
            "name": self.name,
            "version": self.version,
            "status": "active",
            "strategies_learned": len(self.strategy_db.get("strategies", {})),
            "best_practices_count": len(self.strategy_db.get("best_practices", [])),
            "patterns_identified": len(self.strategy_patterns.get("patterns", {})),
            "learning_sessions": len(self.learning_history.get("learning_sessions", [])),
            "last_updated": self.strategy_db.get("last_updated", "unknown")
        }


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="智能进化学习策略自动优化引擎")
    parser.add_argument("command", nargs="?", default="status",
                        help="命令: status, analyze, learn, patterns, apply, optimize, auto")
    parser.add_argument("--context", type=str, default="{}",
                        help="上下文 JSON 字符串")

    args = parser.parse_args()
    optimizer = EvolutionLearningStrategyOptimizer()

    result = {}

    if args.command == "status":
        result = optimizer.get_status()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == "analyze":
        result = optimizer.analyze_historical_decisions()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == "learn":
        result = optimizer.learn_best_practices()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == "patterns":
        result = optimizer.identify_strategy_patterns()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == "apply":
        try:
            context = json.loads(args.context) if args.context != "{}" else {}
        except:
            context = {}
        result = optimizer.apply_learned_strategy(context)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == "optimize":
        result = optimizer.get_optimization_recommendations()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == "auto":
        result = optimizer.auto_learn_and_optimize()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"未知命令: {args.command}")
        print("可用命令: status, analyze, learn, patterns, apply, optimize, auto")
        sys.exit(1)


if __name__ == "__main__":
    main()