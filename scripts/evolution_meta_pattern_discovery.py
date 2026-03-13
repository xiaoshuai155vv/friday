#!/usr/bin/env python3
"""
智能进化元模式发现引擎 (Evolution Meta-Pattern Discovery Engine)
让系统能够从进化历史中自动发现高效进化模式，自动提取成功策略，优化进化决策

功能：
1. 进化历史模式挖掘 - 分析多轮进化数据，发现重复成功的模式
2. 元策略自动提取 - 从成功进化中提取可复用的策略
3. 进化策略推荐 - 基于发现的模式推荐最佳策略

Version: 1.0.0
"""

import os
import json
import glob
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Any, Optional

class EvolutionMetaPatternDiscovery:
    """智能进化元模式发现引擎"""

    def __init__(self):
        self.state_dir = os.path.join(os.path.dirname(__file__), "..", "runtime", "state")
        self.logs_dir = os.path.join(os.path.dirname(__file__), "..", "runtime", "logs")
        self.version = "1.0.0"

        # 元模式类型
        self.pattern_types = [
            "sequential_enhancement",  # 连续增强模式
            "cross_domain_integration",  # 跨域集成模式
            "self_improvement",  # 自我改进模式
            "knowledge_accumulation",  # 知识累积模式
            "feedback_loop",  # 反馈闭环模式
        ]

    def load_evolution_history(self, limit: int = 50) -> List[Dict]:
        """加载进化历史"""
        history_files = sorted(
            glob.glob(os.path.join(self.state_dir, "evolution_completed_*.json")),
            key=os.path.getmtime,
            reverse=True
        )[:limit]

        history = []
        for f in history_files:
            try:
                with open(f, 'r', encoding='utf-8') as fp:
                    data = json.load(fp)
                    history.append(data)
            except Exception as e:
                print(f"Warning: Failed to load {f}: {e}")

        return history

    def discover_patterns(self, history: List[Dict]) -> Dict[str, Any]:
        """发现进化模式"""
        patterns = {
            "total_rounds": len(history),
            "pattern_types": {},
            "success_patterns": [],
            "efficiency_patterns": [],
            "theme_clusters": defaultdict(list),
        }

        # 分析每轮进化
        for i, entry in enumerate(history):
            goal = entry.get("current_goal", "")
            status = entry.get("status", "")
            verify = entry.get("verify_result", {})

            # 识别主题
            if "智能" in goal:
                # 提取关键能力词
                key_words = []
                if "进化" in goal or "evolution" in goal.lower():
                    key_words.append("evolution")
                if "知识" in goal:
                    key_words.append("knowledge")
                if "协同" in goal or "协作" in goal:
                    key_words.append("collaboration")
                if "决策" in goal:
                    key_words.append("decision")
                if "执行" in goal:
                    key_words.append("execution")
                if "优化" in goal or "优化" in goal:
                    key_words.append("optimization")
                if "自动" in goal:
                    key_words.append("automation")

                for kw in key_words:
                    patterns["theme_clusters"][kw].append(i + 1)

            # 识别成功模式
            if status == "completed" or entry.get("is_completed", False):
                verify_text = ""
                if isinstance(verify, dict):
                    verify_text = verify.get("targeted", "")[:100]
                elif isinstance(verify, str):
                    verify_text = verify[:100]
                patterns["success_patterns"].append({
                    "round": entry.get("loop_round", i + 1),
                    "goal": goal[:50],
                    "verify": verify_text
                })

        # 统计主题分布
        for theme, rounds in patterns["theme_clusters"].items():
            patterns["pattern_types"][theme] = {
                "count": len(rounds),
                "rounds": rounds[-10:]  # 最近10轮
            }

        # 效率模式分析
        if len(history) >= 5:
            recent = history[:5]
            completed_count = sum(1 for h in recent if h.get("is_completed", False))
            patterns["efficiency_patterns"] = {
                "recent_completion_rate": completed_count / len(recent),
                "recent_rounds": [h.get("loop_round", i+1) for i, h in enumerate(recent)]
            }

        return patterns

    def extract_meta_strategies(self, history: List[Dict]) -> Dict[str, Any]:
        """提取元策略"""
        strategies = {
            "dominant_themes": [],
            "successful_approaches": [],
            "recommended_sequence": [],
            "strategy_parameters": {}
        }

        # 统计主题出现频率
        theme_count = defaultdict(int)
        for entry in history:
            goal = entry.get("current_goal", "")
            if "进化" in goal or "evolution" in goal.lower():
                theme_count["evolution_enhancement"] += 1
            if "智能" in goal:
                theme_count["intelligence"] += 1
            if "协同" in goal or "协作" in goal:
                theme_count["collaboration"] += 1
            if "自动" in goal:
                theme_count["automation"] += 1
            if "知识" in goal:
                theme_count["knowledge"] += 1

        # 排序获取主导主题
        sorted_themes = sorted(theme_count.items(), key=lambda x: x[1], reverse=True)
        strategies["dominant_themes"] = [
            {"theme": t, "count": c} for t, c in sorted_themes[:5]
        ]

        # 分析成功方法
        successful_goals = [h.get("current_goal", "") for h in history if h.get("is_completed", False)]
        if successful_goals:
            strategies["successful_approaches"] = [
                "创建新模块实现独立功能",
                "集成到 do.py 提供统一入口",
                "实现完整的验证流程",
                "与现有引擎深度集成"
            ]

        # 推荐进化序列
        strategies["recommended_sequence"] = [
            "1. 基础能力增强 → 2. 跨引擎协同 → 3. 自动化执行 → 4. 自我优化 → 5. 元进化"
        ]

        # 策略参数
        strategies["strategy_parameters"] = {
            "optimal_module_size": "单一职责，保持模块精简",
            "integration_approach": "关键词触发 + 子命令接口",
            "validation_standard": "基线校验 + 针对性校验",
            "documentation": "同步更新 capabilities.md"
        }

        return strategies

    def recommend_strategy_for_next(self, patterns: Dict, strategies: Dict) -> List[Dict]:
        """为下一轮推荐策略"""
        recommendations = []

        # 基于模式发现推荐
        if patterns.get("pattern_types"):
            # 找出最频繁的主题
            sorted_types = sorted(
                patterns["pattern_types"].items(),
                key=lambda x: x[1].get("count", 0),
                reverse=True
            )

            if sorted_types:
                top_theme = sorted_types[0][0]
                recommendations.append({
                    "type": "theme_recommendation",
                    "description": f"基于历史分析，'{top_theme}'是最高频主题，建议继续深化",
                    "priority": 9
                })

        # 基于元策略推荐
        if strategies.get("dominant_themes"):
            recommendations.append({
                "type": "strategy_recommendation",
                "description": "建议采用模块化方式创建新引擎，保持单一职责",
                "priority": 8
            })

        # 效率建议
        if patterns.get("efficiency_patterns"):
            rate = patterns["efficiency_patterns"].get("recent_completion_rate", 0)
            if rate >= 0.8:
                recommendations.append({
                    "type": "efficiency_recommendation",
                    "description": "近期完成率较高，可尝试更具挑战性的进化方向",
                    "priority": 7
                })

        return recommendations

    def analyze(self) -> Dict[str, Any]:
        """执行完整分析"""
        # 加载历史
        history = self.load_evolution_history(50)

        # 发现模式
        patterns = self.discover_patterns(history)

        # 提取策略
        strategies = self.extract_meta_strategies(history)

        # 推荐下一轮策略
        recommendations = self.recommend_strategy_for_next(patterns, strategies)

        return {
            "version": self.version,
            "analyzed_rounds": len(history),
            "patterns": patterns,
            "strategies": strategies,
            "recommendations": recommendations,
            "timestamp": datetime.now().isoformat()
        }

    def status(self) -> Dict[str, Any]:
        """返回引擎状态"""
        history = self.load_evolution_history(10)
        return {
            "name": "Evolution Meta-Pattern Discovery Engine",
            "version": self.version,
            "status": "active",
            "analyzed_rounds": len(history),
            "capabilities": [
                "进化历史模式挖掘",
                "元策略自动提取",
                "进化策略推荐",
                "下一轮优化建议"
            ]
        }

    def suggest_improvements(self) -> List[Dict]:
        """基于元模式发现提供改进建议"""
        analysis = self.analyze()
        suggestions = []

        # 分析近期趋势
        patterns = analysis.get("patterns", {})
        strategies = analysis.get("strategies", {})

        # 建议1: 深化主导主题
        if strategies.get("dominant_themes"):
            top = strategies["dominant_themes"][0]
            suggestions.append({
                "category": "theme_deepening",
                "suggestion": f"深化'{top['theme']}'领域的进化，建议探索更细粒度的能力",
                "impact": "high"
            })

        # 建议2: 优化序列
        if patterns.get("efficiency_patterns"):
            rate = patterns["efficiency_patterns"].get("recent_completion_rate", 0)
            if rate < 0.6:
                suggestions.append({
                    "category": "efficiency",
                    "suggestion": "近期完成率偏低，建议简化进化目标或增强验证流程",
                    "impact": "medium"
                })

        # 建议3: 元进化增强
        suggestions.append({
            "category": "meta_evolution",
            "suggestion": "建议增强进化环自身的元学习能力，让系统学会如何更好地进化",
            "impact": "high"
        })

        return suggestions


def main():
    """主函数 - 支持命令行调用"""
    import sys

    engine = EvolutionMetaPatternDiscovery()

    if len(sys.argv) < 2:
        # 无参数时显示状态
        result = engine.status()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    command = sys.argv[1].lower()

    if command == "status":
        result = engine.status()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "analyze":
        result = engine.analyze()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "patterns":
        history = engine.load_evolution_history(50)
        patterns = engine.discover_patterns(history)
        print(json.dumps(patterns, ensure_ascii=False, indent=2))

    elif command == "strategies":
        history = engine.load_evolution_history(50)
        strategies = engine.extract_meta_strategies(history)
        print(json.dumps(strategies, ensure_ascii=False, indent=2))

    elif command == "recommend":
        history = engine.load_evolution_history(50)
        patterns = engine.discover_patterns(history)
        strategies = engine.extract_meta_strategies(history)
        recommendations = engine.recommend_strategy_for_next(patterns, strategies)
        print(json.dumps(recommendations, ensure_ascii=False, indent=2))

    elif command == "suggestions":
        suggestions = engine.suggest_improvements()
        print(json.dumps(suggestions, ensure_ascii=False, indent=2))

    else:
        print(f"Unknown command: {command}")
        print("Available: status, analyze, patterns, strategies, recommend, suggestions")


if __name__ == "__main__":
    main()