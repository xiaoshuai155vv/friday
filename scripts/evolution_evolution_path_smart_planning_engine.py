#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环进化路径智能规划与自适应演进引擎
(Evolution Evolution Path Smart Planning and Adaptive Evolution Engine)

在 round 478 完成的动态阈值自适应优化引擎基础上，
进一步增强进化路径的智能规划能力，实现基于数据驱动的自适应演进。

让系统能够主动规划最优进化方向、预测进化路径效果、动态调整进化策略，
形成「路径规划→效果预测→策略调整→执行验证→持续优化」的完整闭环。

让进化环能够"看到"未来进化方向，选择最优路径前进。

Version: 1.0.0
"""

import json
import os
import sys
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from collections import deque, defaultdict
import statistics

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
STATE_DIR = PROJECT_ROOT / "runtime" / "state"
DATA_DIR = PROJECT_ROOT / "runtime" / "data"
LOGS_DIR = PROJECT_ROOT / "runtime" / "logs"

# 添加 scripts 目录到路径以便导入
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

# 尝试导入相关引擎
try:
    from evolution_dynamic_threshold_adaptive_optimization_engine import (
        AdaptiveThresholdOptimizer,
        get_adaptive_threshold_optimizer
    )
    THRESHOLD_OPTIMIZER_AVAILABLE = True
except ImportError:
    THRESHOLD_OPTIMIZER_AVAILABLE = False
    AdaptiveThresholdOptimizer = None

try:
    from evolution_cross_engine_collaboration_prediction_engine import (
        CrossEngineCollaborationPredictionEngine
    )
    COLLABORATION_PREDICTION_AVAILABLE = True
except ImportError:
    COLLABORATION_PREDICTION_AVAILABLE = False
    CrossEngineCollaborationPredictionEngine = None

try:
    from evolution_effectiveness_prediction_prevention_engine import (
        EvolutionEffectivenessPredictor
    )
    EFFECTIVENESS_PREDICTOR_AVAILABLE = True
except ImportError:
    EFFECTIVENESS_PREDICTOR_AVAILABLE = False
    EvolutionEffectivenessPredictor = None


class EvolutionPathPlanner:
    """进化路径规划器"""

    def __init__(self):
        self.planning_history: List[Dict[str, Any]] = []
        self.path_performance: Dict[str, List[float]] = defaultdict(list)
        self._load_planning_history()

    def _load_planning_history(self):
        """加载规划历史"""
        history_file = DATA_DIR / "evolution_path_planning_history.json"
        if history_file.exists():
            try:
                with open(history_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.planning_history = data.get("history", [])
                    self.path_performance = defaultdict(
                        list,
                        data.get("performance", {})
                    )
            except Exception:
                pass

    def _save_planning_history(self):
        """保存规划历史"""
        history_file = DATA_DIR / "evolution_path_planning_history.json"
        os.makedirs(DATA_DIR, exist_ok=True)
        try:
            with open(history_file, "w", encoding="utf-8") as f:
                json.dump({
                    "history": self.planning_history[-100:],
                    "performance": dict(self.path_performance)
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存规划历史失败: {e}")

    def analyze_evolution_patterns(self) -> Dict[str, Any]:
        """分析进化模式

        Returns:
            进化模式分析结果
        """
        # 读取进化历史
        evolution_files = list(STATE_DIR.glob("evolution_completed_*.json"))

        patterns = {
            "total_rounds": len(evolution_files),
            "successful_rounds": 0,
            "failed_rounds": 0,
            "common_directions": defaultdict(int),
            "average_efficiency": 0.0,
            "trend": "stable"
        }

        efficiency_scores = []

        for ef in evolution_files[-50:]:  # 分析最近50轮
            try:
                with open(ef, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if data.get("status") in ["completed", "已完成"]:
                        patterns["successful_rounds"] += 1
                    else:
                        patterns["failed_rounds"] += 1

                    # 提取进化方向
                    goal = data.get("current_goal", "")
                    if goal:
                        # 提取关键词
                        keywords = ["优化", "引擎", "增强", "集成", "预测", "自适应", "智能", "自动化"]
                        for kw in keywords:
                            if kw in goal:
                                patterns["common_directions"][kw] += 1

                    # 效率评分
                    efficiency = data.get("efficiency_score", 0)
                    if efficiency:
                        efficiency_scores.append(efficiency)
            except Exception:
                pass

        # 计算平均效率
        if efficiency_scores:
            patterns["average_efficiency"] = statistics.mean(efficiency_scores)

            # 趋势分析
            if len(efficiency_scores) >= 5:
                recent_avg = statistics.mean(efficiency_scores[-5:])
                older_avg = statistics.mean(efficiency_scores[:-5])
                if recent_avg > older_avg + 5:
                    patterns["trend"] = "improving"
                elif recent_avg < older_avg - 5:
                    patterns["trend"] = "declining"

        return patterns

    def predict_path_effectiveness(
        self,
        path_name: str,
        path_features: Dict[str, Any]
    ) -> Dict[str, Any]:
        """预测路径效果

        Args:
            path_name: 路径名称
            path_features: 路径特征

        Returns:
            预测结果
        """
        # 基于历史模式预测
        prediction = {
            "path_name": path_name,
            "predicted_success_rate": 0.75,  # 默认75%成功率
            "predicted_efficiency": 0.70,
            "predicted_value": 0.65,
            "risk_level": "low",
            "confidence": 0.60,
            "factors": []
        }

        # 分析特征对成功率的影响
        if "complexity" in path_features:
            complexity = path_features["complexity"]
            if complexity > 8:
                prediction["predicted_success_rate"] *= 0.8
                prediction["risk_level"] = "high"
                prediction["factors"].append("高复杂度降低成功率")
            elif complexity > 5:
                prediction["predicted_success_rate"] *= 0.9
                prediction["risk_level"] = "medium"

        if "integration" in path_features:
            prediction["predicted_success_rate"] *= 0.95
            prediction["predicted_efficiency"] *= 1.1
            prediction["factors"].append("集成现有引擎提升效率")

        if "innovation" in path_features:
            prediction["predicted_success_rate"] *= 0.85
            prediction["predicted_value"] *= 1.2
            prediction["factors"].append("创新性强但风险较高")

        # 计算综合置信度
        base_confidence = 0.6
        if patterns := self.analyze_evolution_patterns():
            if patterns.get("trend") == "improving":
                base_confidence += 0.1
            elif patterns.get("trend") == "declining":
                base_confidence -= 0.1

        prediction["confidence"] = min(0.9, max(0.3, base_confidence))

        return prediction

    def generate_evolution_paths(
        self,
        system_state: Dict[str, Any],
        num_paths: int = 3
    ) -> List[Dict[str, Any]]:
        """生成进化路径

        Args:
            system_state: 系统状态
            num_paths: 生成路径数量

        Returns:
            进化路径列表
        """
        paths = []

        # 分析当前进化模式
        patterns = self.analyze_evolution_patterns()

        # 基于模式生成路径
        # 路径1: 效能优化方向
        path1 = {
            "name": "效能优化路径",
            "description": "基于历史效能分析，优化进化效率",
            "features": {
                "complexity": 4,
                "integration": True,
                "innovation": False
            },
            "expected_outcomes": [
                "提升进化执行效率15%",
                "减少资源浪费",
                "优化引擎协同"
            ],
            "priority": 1
        }
        path1["prediction"] = self.predict_path_effectiveness(
            path1["name"], path1["features"]
        )
        paths.append(path1)

        # 路径2: 智能预测方向
        path2 = {
            "name": "智能预测路径",
            "description": "增强预测能力，主动预防问题",
            "features": {
                "complexity": 6,
                "integration": True,
                "innovation": True
            },
            "expected_outcomes": [
                "提升问题预测准确率",
                "实现主动预防",
                "减少紧急干预"
            ],
            "priority": 2
        }
        path2["prediction"] = self.predict_path_effectiveness(
            path2["name"], path2["features"]
        )
        paths.append(path2)

        # 路径3: 创新探索方向
        path3 = {
            "name": "创新探索路径",
            "description": "探索新的进化方向和能力组合",
            "features": {
                "complexity": 8,
                "integration": False,
                "innovation": True
            },
            "expected_outcomes": [
                "发现新的能力组合",
                "探索前沿方向",
                "创造独特价值"
            ],
            "priority": 3
        }
        path3["prediction"] = self.predict_path_effectiveness(
            path3["name"], path3["features"]
        )
        paths.append(path3)

        # 按预测效果排序
        paths.sort(
            key=lambda x: x.get("prediction", {}).get("predicted_success_rate", 0),
            reverse=True
        )

        return paths[:num_paths]

    def record_path_execution(
        self,
        path_name: str,
        actual_result: Dict[str, Any]
    ):
        """记录路径执行结果

        Args:
            path_name: 路径名称
            actual_result: 实际执行结果
        """
        record = {
            "path_name": path_name,
            "timestamp": datetime.now().isoformat(),
            "result": actual_result
        }

        self.planning_history.append(record)

        # 记录性能数据
        success = actual_result.get("success", False)
        efficiency = actual_result.get("efficiency_score", 0)

        self.path_performance[path_name].append(efficiency if success else 0)

        self._save_planning_history()


class AdaptiveEvolutionEngine:
    """自适应演进引擎"""

    def __init__(self):
        self.planner = EvolutionPathPlanner()
        self.current_strategy: Dict[str, Any] = {}
        self.adaptation_history: List[Dict[str, Any]] = []
        self._load_current_strategy()

    def _load_current_strategy(self):
        """加载当前策略"""
        strategy_file = DATA_DIR / "evolution_path_current_strategy.json"
        if strategy_file.exists():
            try:
                with open(strategy_file, "r", encoding="utf-8") as f:
                    self.current_strategy = json.load(f)
            except Exception:
                pass

    def _save_current_strategy(self):
        """保存当前策略"""
        strategy_file = DATA_DIR / "evolution_path_current_strategy.json"
        os.makedirs(DATA_DIR, exist_ok=True)
        try:
            with open(strategy_file, "w", encoding="utf-8") as f:
                json.dump(self.current_strategy, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存策略失败: {e}")

    def analyze_system_state(self) -> Dict[str, Any]:
        """分析系统状态

        Returns:
            系统状态分析
        """
        state = {
            "timestamp": datetime.now().isoformat(),
            "health_score": 80,
            "evolution_round": 479,
            "active_engines": 0,
            "recent_performance": 0.75,
            "recommendations": []
        }

        # 统计活跃引擎
        try:
            engine_count = len(list(STATE_DIR.glob("evolution_*.py")))
            state["active_engines"] = engine_count
        except Exception:
            pass

        # 分析进化模式
        patterns = self.planner.analyze_evolution_patterns()
        state["patterns"] = patterns

        # 生成建议
        if patterns.get("trend") == "declining":
            state["recommendations"].append("检测到效率下降趋势，建议调整进化策略")

        if patterns.get("average_efficiency", 0) < 60:
            state["recommendations"].append("平均效率偏低，建议优化基础能力")

        return state

    def recommend_next_evolution(
        self,
        system_state: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """推荐下一轮进化

        Args:
            system_state: 系统状态（可选）

        Returns:
            推荐结果
        """
        if system_state is None:
            system_state = self.analyze_system_state()

        # 生成进化路径
        paths = self.planner.generate_evolution_paths(system_state)

        # 选择最佳路径
        best_path = paths[0] if paths else {}

        recommendation = {
            "recommended_path": best_path.get("name"),
            "description": best_path.get("description"),
            "expected_outcomes": best_path.get("expected_outcomes", []),
            "prediction": best_path.get("prediction", {}),
            "all_paths": paths,
            "system_state_summary": {
                "health": system_state.get("health_score"),
                "trend": system_state.get("patterns", {}).get("trend")
            },
            "rationale": self._generate_rationale(best_path, system_state)
        }

        return recommendation

    def _generate_rationale(
        self,
        path: Dict[str, Any],
        system_state: Dict[str, Any]
    ) -> str:
        """生成推荐理由

        Args:
            path: 选择的路径
            system_state: 系统状态

        Returns:
            推荐理由
        """
        prediction = path.get("prediction", {})
        success_rate = prediction.get("predicted_success_rate", 0)

        rationale = f"选择「{path.get('name')}」的原因："

        # 基于成功率
        rationale += f"预测成功率为 {success_rate:.1%}，"

        # 基于系统趋势
        trend = system_state.get("patterns", {}).get("trend", "stable")
        if trend == "improving":
            rationale += "系统处于上升趋势，适合执行新进化；"
        elif trend == "declining":
            rationale += "系统效率有下降趋势，需要优化策略；"
        else:
            rationale += "系统状态稳定，可稳步推进；"

        # 基于风险
        risk = prediction.get("risk_level", "low")
        rationale += f"风险等级为 {risk}。"

        return rationale

    def adapt_strategy(
        self,
        execution_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """自适应调整策略

        Args:
            execution_result: 执行结果

        Returns:
            调整后的策略
        """
        adaptation = {
            "timestamp": datetime.now().isoformat(),
            "execution_result": execution_result,
            "adjustments": [],
            "new_strategy": {}
        }

        # 分析执行结果
        success = execution_result.get("success", False)
        efficiency = execution_result.get("efficiency_score", 0)

        # 根据结果调整
        if not success:
            adaptation["adjustments"].append("执行失败，降低复杂度")
            adaptation["new_strategy"]["complexity"] = "reduced"
        elif efficiency < 0.6:
            adaptation["adjustments"].append("效率偏低，增加集成")
            adaptation["new_strategy"]["integration"] = True
        else:
            adaptation["adjustments"].append("执行成功，保持策略")

        # 更新当前策略
        self.current_strategy.update(adaptation["new_strategy"])
        self._save_current_strategy()

        self.adaptation_history.append(adaptation)

        return adaptation


def get_evolution_path_planner() -> EvolutionPathPlanner:
    """获取进化路径规划器实例"""
    return EvolutionPathPlanner()


def get_adaptive_evolution_engine() -> AdaptiveEvolutionEngine:
    """获取自适应演进引擎实例"""
    return AdaptiveEvolutionEngine()


# 主函数
def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="智能全场景进化环进化路径智能规划与自适应演进引擎"
    )
    parser.add_argument("--status", action="store_true", help="查看引擎状态")
    parser.add_argument("--analyze-patterns", action="store_true", help="分析进化模式")
    parser.add_argument(
        "--generate-paths",
        action="store_true",
        help="生成进化路径"
    )
    parser.add_argument(
        "--recommend",
        action="store_true",
        help="推荐下一轮进化"
    )
    parser.add_argument(
        "--adapt",
        action="store_true",
        help="自适应策略调整"
    )
    parser.add_argument(
        "--cockpit-data",
        action="store_true",
        help="获取驾驶舱数据"
    )

    args = parser.parse_args()

    engine = get_adaptive_evolution_engine()
    planner = get_evolution_path_planner()

    if args.status:
        print("=== 进化路径智能规划引擎状态 ===")
        state = engine.analyze_system_state()
        print(f"系统健康分: {state.get('health_score')}")
        print(f"活跃引擎数: {state.get('active_engines')}")
        print(f"进化轮次: {state.get('evolution_round')}")
        print(f"性能趋势: {state.get('patterns', {}).get('trend', 'unknown')}")
        print()

    if args.analyze_patterns:
        print("=== 进化模式分析 ===")
        patterns = planner.analyze_evolution_patterns()
        print(f"总进化轮次: {patterns.get('total_rounds')}")
        print(f"成功轮次: {patterns.get('successful_rounds')}")
        print(f"失败轮次: {patterns.get('failed_rounds')}")
        print(f"平均效率: {patterns.get('average_efficiency', 0):.1%}")
        print(f"趋势: {patterns.get('trend')}")
        print("常见方向:")
        for direction, count in sorted(
            patterns.get("common_directions", {}).items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]:
            print(f"  - {direction}: {count}次")
        print()

    if args.generate_paths:
        print("=== 生成进化路径 ===")
        system_state = engine.analyze_system_state()
        paths = planner.generate_evolution_paths(system_state)
        for i, path in enumerate(paths, 1):
            print(f"\n路径 {i}: {path.get('name')}")
            print(f"  描述: {path.get('description')}")
            prediction = path.get("prediction", {})
            print(f"  预测成功率: {prediction.get('predicted_success_rate', 0):.1%}")
            print(f"  预测效率: {prediction.get('predicted_efficiency', 0):.1%}")
            print(f"  风险等级: {prediction.get('risk_level')}")
            print(f"  预期成果: {', '.join(path.get('expected_outcomes', []))}")
        print()

    if args.recommend:
        print("=== 推荐下一轮进化 ===")
        recommendation = engine.recommend_next_evolution()
        print(f"推荐路径: {recommendation.get('recommended_path')}")
        print(f"描述: {recommendation.get('description')}")
        print(f"理由: {recommendation.get('rationale')}")
        print(f"\n预测效果:")
        pred = recommendation.get("prediction", {})
        print(f"  成功率: {pred.get('predicted_success_rate', 0):.1%}")
        print(f"  效率: {pred.get('predicted_efficiency', 0):.1%}")
        print(f"  价值: {pred.get('predicted_value', 0):.1%}")
        print(f"  风险: {pred.get('risk_level')}")
        print()

    if args.adapt:
        print("=== 自适应策略调整 ===")
        # 模拟执行结果
        test_result = {
            "success": True,
            "efficiency_score": 0.75
        }
        adaptation = engine.adapt_strategy(test_result)
        print(f"调整时间: {adaptation.get('timestamp')}")
        print("调整内容:")
        for adj in adaptation.get("adjustments", []):
            print(f"  - {adj}")
        print()

    if args.cockpit_data:
        print("=== 驾驶舱数据 ===")
        state = engine.analyze_system_state()
        recommendation = engine.recommend_next_evolution()

        cockpit_data = {
            "engine_name": "Evolution Path Smart Planning Engine",
            "version": "1.0.0",
            "system_state": state,
            "recommendation": recommendation,
            "timestamp": datetime.now().isoformat()
        }

        # 保存到文件
        output_file = DATA_DIR / "evolution_path_cockpit_data.json"
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(cockpit_data, f, ensure_ascii=False, indent=2)

        print(f"驾驶舱数据已保存到: {output_file}")
        print()


if __name__ == "__main__":
    main()