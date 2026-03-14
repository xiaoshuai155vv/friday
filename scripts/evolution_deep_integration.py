"""
智能进化环深度集成引擎 (Evolution Deep Integration Engine)

Round 252: 将 round 251 的深度集成引擎与进化环进一步集成，
让进化环能够利用深度集成引擎的智能决策能力，实现自动进化优化。

核心功能：
1. 深度引擎集成 - 将 engine_deep_integration 与进化环融合
2. 进化环智能决策增强 - 利用引擎组合推荐能力辅助进化决策
3. 自动进化优化建议生成 - 基于系统状态和历史生成优化建议
4. 进化效果预测 - 预测进化方向的效果

Version: 1.0.0
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))


class EvolutionDeepIntegrationEngine:
    """智能进化环深度集成引擎"""

    def __init__(self):
        self.name = "Evolution Deep Integration Engine"
        self.version = "1.0.0"
        self.project_root = PROJECT_ROOT
        self.scripts_dir = SCRIPTS_DIR
        self.state_dir = self.project_root / "runtime" / "state"
        self.logs_dir = self.project_root / "runtime" / "logs"

        # 进化历史分析缓存
        self.evolution_history_cache = {}
        self.recent_suggestions = []

        # 导入并初始化深度集成引擎
        try:
            from engine_deep_integration import EngineDeepIntegrationCoordinator
            self.deep_integration = EngineDeepIntegrationCoordinator()
            self.deep_integration_loaded = True
        except ImportError as e:
            print(f"Warning: Failed to import engine deep integration: {e}")
            self.deep_integration = None
            self.deep_integration_loaded = False

    def status(self) -> Dict[str, Any]:
        """返回引擎状态"""
        return {
            "name": self.name,
            "version": self.version,
            "deep_integration_loaded": self.deep_integration_loaded,
            "evolution_history_cached": len(self.evolution_history_cache),
            "recent_suggestions": len(self.recent_suggestions),
            "integrated_capabilities": [
                "智能进化决策增强",
                "自动进化优化建议",
                "进化效果预测",
                "进化方向分析"
            ]
        }

    def analyze_evolution_needs(self, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        分析进化需求，利用深度集成引擎的智能决策能力

        Args:
            context: 可选的上下文信息

        Returns:
            包含进化需求分析的字典
        """
        if not self.deep_integration_loaded:
            return {"error": "Deep integration engine not loaded properly"}

        # 1. 读取进化历史
        evolution_history = self._load_evolution_history()

        # 2. 使用深度集成引擎分析当前系统状态
        system_state_prompt = f"分析当前进化环状态：已完成 {len(evolution_history)} 轮进化，历史记录显示系统持续在增强智能决策能力。请给出下一轮进化建议。"

        deep_analysis = self.deep_integration.analyze(
            system_state_prompt,
            context or {}
        )

        # 3. 生成进化优化建议
        optimization_suggestions = self._generate_optimization_suggestions(
            evolution_history,
            deep_analysis
        )

        # 4. 预测进化效果
        effect_predictions = self._predict_evolution_effect(
            optimization_suggestions
        )

        result = {
            "timestamp": datetime.now().isoformat(),
            "evolution_history_size": len(evolution_history),
            "deep_analysis": deep_analysis,
            "optimization_suggestions": optimization_suggestions,
            "effect_predictions": effect_predictions,
            "recommended_focus": self._determine_recommended_focus(
                optimization_suggestions,
                effect_predictions
            )
        }

        # 记录建议
        self.recent_suggestions.append({
            "timestamp": datetime.now().isoformat(),
            "suggestions": optimization_suggestions,
            "predictions": effect_predictions
        })

        # 保持建议历史在合理范围内
        if len(self.recent_suggestions) > 20:
            self.recent_suggestions = self.recent_suggestions[-20:]

        return result

    def _load_evolution_history(self) -> List[Dict]:
        """加载进化历史"""
        history = []

        # 读取 state 目录下的进化完成记录
        if self.state_dir.exists():
            for file in self.state_dir.glob("evolution_completed_*.json"):
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        history.append(data)
                except Exception as e:
                    print(f"Warning: Failed to read {file}: {e}")

        # 按时间排序
        history.sort(key=lambda x: x.get("created_at", ""), reverse=True)

        return history

    def _generate_optimization_suggestions(
        self,
        evolution_history: List[Dict],
        deep_analysis: Dict
    ) -> List[Dict]:
        """生成进化优化建议"""
        suggestions = []

        # 分析历史进化效率
        if evolution_history:
            # 计算完成率
            completed = sum(1 for h in evolution_history if h.get("status") in ["completed", "已完成"])
            total = len(evolution_history)
            completion_rate = completed / total if total > 0 else 0

            if completion_rate < 0.8:
                suggestions.append({
                    "type": "efficiency",
                    "priority": "high",
                    "description": "进化完成率偏低，建议优化执行策略",
                    "action": "增强执行跟踪和失败恢复机制"
                })

            # 检查是否有重复的进化方向
            recent_goals = [h.get("current_goal", "") for h in evolution_history[:10]]
            if len(set(recent_goals)) < len(recent_goals) * 0.5:
                suggestions.append({
                    "type": "diversity",
                    "priority": "high",
                    "description": "检测到重复的进化方向，需要更多样化",
                    "action": "引入更多创新性进化方向"
                })

        # 基于深度分析生成建议
        if deep_analysis.get("recommended_engines"):
            suggestions.append({
                "type": "integration",
                "priority": "medium",
                "description": f"建议集成新引擎组合: {deep_analysis['recommended_engines'][:3]}",
                "action": "将推荐的引擎组合集成到系统中"
            })

        # 通用优化建议
        if len(evolution_history) > 50:
            suggestions.append({
                "type": "knowledge",
                "priority": "medium",
                "description": "积累了大量进化知识，建议增强知识传承",
                "action": "完善进化知识图谱和跨代传承机制"
            })

        return suggestions

    def _predict_evolution_effect(
        self,
        suggestions: List[Dict]
    ) -> Dict[str, Any]:
        """预测进化效果"""
        if not suggestions:
            return {"predicted_impact": "low", "confidence": 0.5}

        # 基于建议类型预测效果
        high_priority = [s for s in suggestions if s.get("priority") == "high"]

        if len(high_priority) >= 2:
            return {
                "predicted_impact": "high",
                "confidence": 0.85,
                "reason": f"有 {len(high_priority)} 个高优先级优化点"
            }
        elif len(high_priority) == 1:
            return {
                "predicted_impact": "medium",
                "confidence": 0.7,
                "reason": "有 1 个高优先级优化点"
            }
        else:
            return {
                "predicted_impact": "low",
                "confidence": 0.5,
                "reason": "优化点较少或优先级较低"
            }

    def _determine_recommended_focus(
        self,
        suggestions: List[Dict],
        predictions: Dict
    ) -> str:
        """确定推荐的进化焦点"""
        if not suggestions:
            return "系统已处于良好状态，可探索创新方向"

        # 优先处理高优先级建议
        high_priority = [s for s in suggestions if s.get("priority") == "high"]

        if high_priority:
            return f"建议优先处理: {high_priority[0].get('description', '未知')}"

        # 按类型排序
        type_priority = {"integration": 1, "efficiency": 2, "diversity": 3, "knowledge": 4}
        sorted_suggestions = sorted(
            suggestions,
            key=lambda x: type_priority.get(x.get("type", ""), 99)
        )

        if sorted_suggestions:
            return f"建议关注: {sorted_suggestions[0].get('description', '未知')}"

        return "继续当前进化方向"

    def get_evolution_insights(self) -> Dict[str, Any]:
        """获取进化洞察"""
        history = self._load_evolution_history()

        insights = {
            "total_evolution_rounds": len(history),
            "recent_rounds_summary": [],
            "trend_analysis": {}
        }

        # 总结最近10轮
        for h in history[:10]:
            insights["recent_rounds_summary"].append({
                "round": h.get("loop_round", h.get("mission", "")),
                "goal": h.get("current_goal", "")[:50],
                "status": h.get("status", "")
            })

        # 趋势分析
        if len(history) >= 5:
            completed = sum(1 for h in history[:5] if h.get("status") in ["completed", "已完成"])
            insights["trend_analysis"] = {
                "recent_completion_rate": completed / 5,
                "trend": "improving" if completed >= 4 else "stable"
            }

        return insights

    def suggest_next_evolution(self) -> Dict[str, Any]:
        """建议下一轮进化方向"""
        # 分析进化需求
        analysis = self.analyze_evolution_needs()

        # 获取洞察
        insights = self.get_evolution_insights()

        # 综合判断
        recommended_focus = analysis.get("recommended_focus", "")
        predictions = analysis.get("effect_predictions", {})

        suggestion = {
            "timestamp": datetime.now().isoformat(),
            "recommended_evolution": recommended_focus,
            "predicted_impact": predictions.get("predicted_impact", "unknown"),
            "confidence": predictions.get("confidence", 0),
            "reason": predictions.get("reason", ""),
            "insights": insights,
            "based_on_history": len(insights.get("recent_rounds_summary", []))
        }

        return suggestion


def main():
    """主函数 - 支持命令行调用"""
    import argparse

    parser = argparse.ArgumentParser(
        description="智能进化环深度集成引擎"
    )
    parser.add_argument(
        "command",
        choices=["status", "analyze", "insights", "suggest"],
        help="要执行的命令"
    )
    parser.add_argument(
        "--context", "-c",
        help="上下文 JSON 字符串"
    )

    args = parser.parse_args()

    engine = EvolutionDeepIntegrationEngine()

    if args.command == "status":
        result = engine.status()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "analyze":
        context = json.loads(args.context) if args.context else None
        result = engine.analyze_evolution_needs(context)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "insights":
        result = engine.get_evolution_insights()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "suggest":
        result = engine.suggest_next_evolution()
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()