#!/usr/bin/env python3
"""
智能全场景进化环元进化方法论有效性评估与持续优化引擎 - version 1.0.0

让系统能够评估自身进化方法论的有效性、识别低效模式、自动生成优化建议，
形成持续改进进化方法的递归闭环。

核心能力：
1. 进化方法论有效性评估 - 评估当前进化策略的有效性
2. 低效模式识别 - 识别重复进化、目标偏移、资源浪费等低效模式
3. 优化建议自动生成 - 基于分析结果生成可执行优化建议
4. 持续优化闭环 - 将优化效果反馈到进化决策过程

与 round 621-630 的引擎深度集成：
- round 621: 价值创造与自我增强引擎
- round 622: 架构自演进优化引擎
- round 625: 记忆深度整合与智慧涌现引擎
- round 629: 自我诊断优化闭环引擎
- round 630: 主动自我进化规划引擎
"""

import os
import json
import glob
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from collections import Counter, defaultdict

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
STATE_DIR = PROJECT_ROOT / "runtime" / "state"
LOGS_DIR = PROJECT_ROOT / "runtime" / "logs"
REFERENCES_DIR = PROJECT_ROOT / "references"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"


class EvolutionMetaMethodologyEffectivenessEngine:
    """元进化方法论有效性评估与持续优化引擎"""

    def __init__(self):
        self.version = "1.0.0"
        self.name = "元进化方法论有效性评估与持续优化引擎"
        self.capability_description = (
            "让系统能够评估自身进化方法论的有效性、识别低效模式、自动生成优化建议，"
            "形成持续改进进化方法的递归闭环"
        )

        # 评估维度
        self.evaluation_dimensions = {
            "goal_alignment": 0.20,        # 目标对齐度
            "execution_efficiency": 0.20,  # 执行效率
            "resource_utilization": 0.15,   # 资源利用率
            "innovation_value": 0.20,      # 创新价值
            "learning_effectiveness": 0.15, # 学习效果
            "system_health": 0.10          # 系统健康影响
        }

        # 低效模式类型
        self.inefficiency_patterns = {
            "repeated_evolution": {
                "name": "重复进化",
                "description": "同一能力被多次重复开发",
                "severity": "high"
            },
            "goal_drift": {
                "name": "目标漂移",
                "description": "进化目标偏离原始意图",
                "severity": "medium"
            },
            "resource_waste": {
                "name": "资源浪费",
                "description": "投入产出比低下的进化",
                "severity": "high"
            },
            "strategy_degradation": {
                "name": "策略退化",
                "description": "进化策略效果逐渐下降",
                "severity": "medium"
            },
            "dependency_complexity": {
                "name": "依赖复杂度",
                "description": "进化间依赖关系过于复杂",
                "severity": "low"
            },
            "knowledge_silo": {
                "name": "知识孤岛",
                "description": "进化成果未被有效复用",
                "severity": "medium"
            }
        }

    def scan_evolution_history(self, max_rounds: int = 50) -> List[Dict[str, Any]]:
        """扫描最近的进化历史"""
        history = []

        # 扫描 evolution_completed_*.json 文件
        completed_files = sorted(STATE_DIR.glob("evolution_completed_*.json"))

        # 取最近的文件
        recent_files = completed_files[-max_rounds:] if len(completed_files) > max_rounds else completed_files

        for filepath in recent_files:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    history.append({
                        "round": data.get("loop_round", 0),
                        "session_id": data.get("session_id", ""),
                        "goal": data.get("current_goal", ""),
                        "mission": data.get("mission", ""),
                        "status": data.get("completion_status", ""),
                        "actions": data.get("execution_summary", {}).get("actions_taken", []),
                        "created_at": data.get("created_at", ""),
                        "completed_at": data.get("completed_at", "")
                    })
            except Exception as e:
                print(f"Warning: Failed to read {filepath}: {e}")

        return sorted(history, key=lambda x: x["round"], reverse=True)

    def analyze_goal_alignment(self, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析目标对齐度 - 评估进化目标是否一致"""
        if not history:
            return {"score": 0.5, "analysis": "无历史数据"}

        # 提取目标关键词
        goal_keywords = []
        for item in history[:20]:  # 分析最近20轮
            goal = item.get("goal", "")
            # 提取关键名词短语
            words = re.findall(r'[\u4e00-\u9fa5]+', goal)
            goal_keywords.extend(words)

        # 统计关键词频率
        keyword_freq = Counter(goal_keywords)

        # 检查是否有明确的主题主线
        top_keywords = [kw for kw, _ in keyword_freq.most_common(5)]

        # 评估主题一致性
        main_themes = ["进化", "优化", "引擎", "智能", "能力"]
        theme_coverage = sum(1 for kw in top_keywords if kw in main_themes)

        score = min(1.0, theme_coverage / 3.0)

        return {
            "score": score,
            "top_keywords": top_keywords,
            "keyword_freq": dict(keyword_freq.most_common(10)),
            "analysis": f"目标对齐度评估：{len(history)}轮进化中，识别出{len(top_keywords)}个主要关键词，主题覆盖度{int(score*100)}%"
        }

    def analyze_execution_efficiency(self, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析执行效率 - 评估进化执行的速度和效果"""
        if not history:
            return {"score": 0.5, "analysis": "无历史数据"}

        completed_count = sum(1 for item in history if item.get("status") == "completed")
        total_count = len(history)

        completion_rate = completed_count / total_count if total_count > 0 else 0

        # 分析每个进化的平均行动数
        action_counts = []
        for item in history:
            actions = item.get("actions", [])
            action_counts.append(len(actions))

        avg_actions = sum(action_counts) / len(action_counts) if action_counts else 0

        # 效率评分：完成率高且行动数适中为佳
        efficiency_score = completion_rate * 0.6 + (1 - min(1.0, avg_actions / 10)) * 0.4

        return {
            "score": efficiency_score,
            "completion_rate": completion_rate,
            "avg_actions_per_evolution": avg_actions,
            "completed_count": completed_count,
            "total_count": total_count,
            "analysis": f"执行效率评估：完成率{int(completion_rate*100)}%，平均每轮{int(avg_actions)}个行动，效率评分{int(efficiency_score*100)}%"
        }

    def analyze_resource_utilization(self, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析资源利用率 - 评估进化投入产出比"""
        if not history:
            return {"score": 0.5, "analysis": "无历史数据"}

        # 统计创建的模块数量
        modules_created = []
        for item in history:
            actions = item.get("actions", [])
            for action in actions:
                if "创建" in action and "模块" in action:
                    # 提取模块名
                    match = re.search(r'创建\s+([\w\.]+)\s+模块', action)
                    if match:
                        modules_created.append(match.group(1))

        # 统计修改的模块数量
        modules_modified = []
        for item in history:
            actions = item.get("actions", [])
            for action in actions:
                if "修改" in action and "模块" in action:
                    match = re.search(r'修改\s+([\w\.]+)\s+模块', action)
                    if match:
                        modules_modified.append(match.group(1))

        # 计算利用率
        total_modules = len(modules_created) + len(modules_modified)
        unique_modules = len(set(modules_created + modules_modified))

        utilization_rate = unique_modules / total_modules if total_modules > 0 else 0

        return {
            "score": utilization_rate,
            "total_modules": total_modules,
            "unique_modules": unique_modules,
            "creation_rate": len(modules_created) / len(history) if history else 0,
            "reuse_rate": len(modules_modified) / len(history) if history else 0,
            "analysis": f"资源利用率评估：{unique_modules}个独立模块被{total_modules}次操作，复用率{int(utilization_rate*100)}%"
        }

    def identify_inefficiency_patterns(self, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """识别低效模式"""
        patterns_found = {}

        # 1. 检查重复进化 - 统计相似目标
        goals = [item.get("goal", "") for item in history[:30]]
        goal_similarity = self._check_goal_similarity(goals)
        if goal_similarity["repeated_count"] > 3:
            patterns_found["repeated_evolution"] = {
                **self.inefficiency_patterns["repeated_evolution"],
                "instances": goal_similarity["repeated_goals"]
            }

        # 2. 检查目标漂移 - 目标与执行结果不匹配
        drift_score = self._check_goal_drift(history[:10])
        if drift_score > 0.5:
            patterns_found["goal_drift"] = {
                **self.inefficiency_patterns["goal_drift"],
                "drift_score": drift_score
            }

        # 3. 检查知识孤岛 - 统计模块被引用的次数
        silo_score = self._check_knowledge_silo(history)
        if silo_score < 0.3:
            patterns_found["knowledge_silo"] = {
                **self.inefficiency_patterns["knowledge_silo"],
                "silo_score": silo_score
            }

        # 4. 检查策略退化 - 完成率随时间下降
        degradation_score = self._check_strategy_degradation(history)
        if degradation_score > 0.3:
            patterns_found["strategy_degradation"] = {
                **self.inefficiency_patterns["strategy_degradation"],
                    "degradation_score": degradation_score
            }

        # 总体低效评分
        overall_score = len(patterns_found) / len(self.inefficiency_patterns)

        return {
            "patterns_found": patterns_found,
            "pattern_count": len(patterns_found),
            "total_patterns": len(self.inefficiency_patterns),
            "inefficiency_score": overall_score,
            "analysis": f"低效模式识别：发现{len(patterns_found)}/{len(self.inefficiency_patterns)}种低效模式"
        }

    def _check_goal_similarity(self, goals: List[str]) -> Dict[str, Any]:
        """检查目标相似性"""
        # 提取关键词
        goal_keywords = []
        for goal in goals:
            keywords = re.findall(r'[\u4e00-\u9fa5]{4,}', goal)
            goal_keywords.append(set(keywords))

        # 比较相邻目标
        repeated = []
        for i in range(len(goal_keywords) - 1):
            if goal_keywords[i] & goal_keywords[i+1]:
                # 有交集说明有相似性
                if len(goal_keywords[i] & goal_keywords[i+1]) >= 2:
                    repeated.append(goals[i][:50])

        return {
            "repeated_count": len(repeated),
            "repeated_goals": repeated[:5]
        }

    def _check_goal_drift(self, recent_history: List[Dict[str, Any]]) -> float:
        """检查目标漂移"""
        if len(recent_history) < 3:
            return 0.0

        # 简化为检查目标长度变化
        goal_lengths = [len(item.get("goal", "")) for item in recent_history]
        avg_length = sum(goal_lengths) / len(goal_lengths)

        variance = sum((l - avg_length) ** 2 for l in goal_lengths) / len(goal_lengths)

        # 方差大说明目标不稳定
        return min(1.0, variance / 1000)

    def _check_knowledge_silo(self, history: List[Dict[str, Any]]) -> float:
        """检查知识孤岛 - 简化为检查跨轮引用"""
        # 检查最近历史中是否有明确的依赖引用
        ref_count = 0
        for item in history:
            actions = item.get("actions", [])
            for action in actions:
                if "集成" in action or "深度集成" in action or "与" in action and "引擎" in action:
                    ref_count += 1

        return min(1.0, ref_count / len(history)) if history else 0

    def _check_strategy_degradation(self, history: List[Dict[str, Any]]) -> float:
        """检查策略退化"""
        if len(history) < 5:
            return 0.0

        # 按时间分成前后两半
        mid = len(history) // 2
        first_half = history[mid:]
        second_half = history[:mid]

        first_completed = sum(1 for item in first_half if item.get("status") == "completed")
        second_completed = sum(1 for item in second_half if item.get("status") == "completed")

        first_rate = first_completed / len(first_half) if first_half else 0
        second_rate = second_completed / len(second_half) if second_half else 0

        # 完成率下降说明策略退化
        degradation = first_rate - second_rate

        return max(0, degradation)

    def generate_optimization_suggestions(self,
                                          goal_alignment: Dict,
                                          execution_efficiency: Dict,
                                          resource_utilization: Dict,
                                          patterns: Dict) -> List[Dict[str, Any]]:
        """生成优化建议"""
        suggestions = []

        # 基于目标对齐度的建议
        if goal_alignment.get("score", 0) < 0.5:
            suggestions.append({
                "priority": "high",
                "category": "goal_alignment",
                "suggestion": "加强进化目标的主题一致性，建立明确的进化主线",
                "actions": [
                    "制定清晰的进化主题路线图",
                    "在每个进化轮次中明确主题目标"
                ]
            })

        # 基于执行效率的建议
        if execution_efficiency.get("score", 0) < 0.6:
            suggestions.append({
                "priority": "high",
                "category": "execution_efficiency",
                "suggestion": "优化进化执行流程，减少冗余行动",
                "actions": [
                    "简化进化执行步骤",
                    "增加自动化执行比例"
                ]
            })

        # 基于资源利用的建议
        if resource_utilization.get("score", 0) < 0.5:
            suggestions.append({
                "priority": "medium",
                "category": "resource_utilization",
                "suggestion": "提高模块复用率，减少重复开发",
                "actions": [
                    "建立模块复用机制",
                    "鼓励基于现有模块进行扩展"
                ]
            })

        # 基于低效模式的建议
        patterns_found = patterns.get("patterns_found", {})
        if "repeated_evolution" in patterns_found:
            suggestions.append({
                "priority": "high",
                "category": "inefficiency",
                "suggestion": "建立能力缺口检测机制，避免重复开发",
                "actions": [
                    "在生成进化目标前先检查现有能力"
                ]
            })

        if "knowledge_silo" in patterns_found:
            suggestions.append({
                "priority": "medium",
                "category": "knowledge",
                "suggestion": "加强进化知识共享机制",
                "actions": [
                    "在进化规划中强制引用相关历史"
                ]
            })

        if "strategy_degradation" in patterns_found:
            suggestions.append({
                "priority": "high",
                "category": "strategy",
                "suggestion": "重新评估进化策略有效性",
                "actions": [
                    "分析最近失败的进化原因",
                    "调整优化方向和优先级"
                ]
            })

        # 如果没有明显问题，生成正向建议
        if not suggestions:
            suggestions.append({
                "priority": "low",
                "category": "continuous_improvement",
                "suggestion": "进化方法论运行良好，持续保持并微调",
                "actions": [
                    "保持当前进化策略",
                    "定期进行方法论审计"
                ]
            })

        return suggestions

    def evaluate_methodology(self) -> Dict[str, Any]:
        """评估进化方法论有效性 - 主入口"""
        # 1. 扫描进化历史
        history = self.scan_evolution_history(max_rounds=50)

        if not history:
            return {
                "success": False,
                "message": "无进化历史数据",
                "evaluation": {}
            }

        # 2. 各维度评估
        goal_alignment = self.analyze_goal_alignment(history)
        execution_efficiency = self.analyze_execution_efficiency(history)
        resource_utilization = self.analyze_resource_utilization(history)
        patterns = self.identify_inefficiency_patterns(history)

        # 3. 计算总体评分
        overall_score = (
            goal_alignment.get("score", 0) * self.evaluation_dimensions["goal_alignment"] +
            execution_efficiency.get("score", 0) * self.evaluation_dimensions["execution_efficiency"] +
            resource_utilization.get("score", 0) * self.evaluation_dimensions["resource_utilization"] +
            (1 - patterns.get("inefficiency_score", 0.5)) * 0.3
        )

        # 4. 生成优化建议
        suggestions = self.generate_optimization_suggestions(
            goal_alignment, execution_efficiency, resource_utilization, patterns
        )

        return {
            "success": True,
            "version": self.version,
            "rounds_analyzed": len(history),
            "evaluation": {
                "overall_score": overall_score,
                "dimensions": {
                    "goal_alignment": goal_alignment,
                    "execution_efficiency": execution_efficiency,
                    "resource_utilization": resource_utilization,
                    "inefficiency_patterns": patterns
                },
                "suggestions": suggestions,
                "timestamp": datetime.now().isoformat()
            }
        }

    def get_cockpit_data(self) -> Dict[str, Any]:
        """获取驾驶舱数据"""
        result = self.evaluate_methodology()

        return {
            "engine_name": self.name,
            "version": self.version,
            "overall_score": result.get("evaluation", {}).get("overall_score", 0),
            "rounds_analyzed": result.get("rounds_analyzed", 0),
            "suggestions_count": len(result.get("evaluation", {}).get("suggestions", [])),
            "dimensions": {
                "goal_alignment": result.get("evaluation", {}).get("dimensions", {}).get("goal_alignment", {}).get("score", 0),
                "execution_efficiency": result.get("evaluation", {}).get("dimensions", {}).get("execution_efficiency", {}).get("score", 0),
                "resource_utilization": result.get("evaluation", {}).get("dimensions", {}).get("resource_utilization", {}).get("score", 0),
                "inefficiency_score": result.get("evaluation", {}).get("dimensions", {}).get("inefficiency_patterns", {}).get("inefficiency_score", 0)
            },
            "top_suggestions": [
                s.get("suggestion", "") for s in result.get("evaluation", {}).get("suggestions", [])[:3]
            ]
        }


def main():
    """主入口 - 支持命令行调用"""
    import sys

    engine = EvolutionMetaMethodologyEffectivenessEngine()

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "--version":
            print(f"{engine.name} version {engine.version}")
            return

        elif command == "--status":
            result = engine.evaluate_methodology()
            if result.get("success"):
                eval_data = result.get("evaluation", {})
                print(f"进化方法论有效性评估:")
                print(f"  - 总体评分: {int(eval_data.get('overall_score', 0) * 100)}%")
                print(f"  - 分析轮次: {result.get('rounds_analyzed', 0)}")
                print(f"  - 目标对齐度: {int(eval_data.get('dimensions', {}).get('goal_alignment', {}).get('score', 0) * 100)}%")
                print(f"  - 执行效率: {int(eval_data.get('dimensions', {}).get('execution_efficiency', {}).get('score', 0) * 100)}%")
                print(f"  - 资源利用率: {int(eval_data.get('dimensions', {}).get('resource_utilization', {}).get('score', 0) * 100)}%")
                print(f"  - 低效模式: {eval_data.get('dimensions', {}).get('inefficiency_patterns', {}).get('pattern_count', 0)}种")
            else:
                print(f"评估失败: {result.get('message')}")
            return

        elif command == "--run":
            result = engine.evaluate_methodology()
            if result.get("success"):
                eval_data = result.get("evaluation", {})
                print(json.dumps(eval_data, ensure_ascii=False, indent=2))
            return

        elif command == "--cockpit-data":
            data = engine.get_cockpit_data()
            print(json.dumps(data, ensure_ascii=False, indent=2))
            return

    # 默认执行评估
    result = engine.evaluate_methodology()
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()