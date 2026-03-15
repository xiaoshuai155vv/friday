#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环元进化结果预测与自适应策略深度优化引擎

让系统能够基于历史进化结果训练预测模型、预测不同进化方向的预期效果、
主动选择最优进化路径，形成「学习历史→预测未来→主动选择→优化执行」的完整闭环。

本模块在 round 636 创建，构建更智能的进化决策能力。

功能：
1. 历史进化结果分析 - 分析 600+ 轮进化的结果数据
2. 预测模型训练 - 基于历史数据训练效果预测模型
3. 进化方向效果预测 - 预测不同进化方向的预期效果
4. 最优路径主动选择 - 基于预测结果主动选择最优进化路径
5. 策略自适应调整 - 根据执行反馈动态调整进化策略
6. 驾驶舱数据接口 - 提供可视化数据

依赖：
- round 635 创新执行迭代引擎
- round 634 价值验证排序引擎
- round 633 知识图谱引擎

版本: 1.0.0
"""

import os
import sys
import json
import glob
import re
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Tuple, Optional, Any

# 项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUNTIME_STATE_DIR = os.path.join(PROJECT_ROOT, "runtime", "state")
RUNTIME_LOGS_DIR = os.path.join(PROJECT_ROOT, "runtime", "logs")


class EvolutionResultPredictionEngine:
    """元进化结果预测与自适应策略优化引擎"""

    def __init__(self):
        self.history_data = []
        self.prediction_model = {}
        self.strategy_effectiveness = defaultdict(list)
        self.evolution_patterns = defaultdict(list)
        self.version = "1.0.0"

    def load_evolution_history(self) -> int:
        """加载历史进化数据"""
        history_files = glob.glob(
            os.path.join(RUNTIME_STATE_DIR, "evolution_completed_ev_*.json")
        )

        loaded_count = 0
        for f in history_files:
            try:
                with open(f, 'r', encoding='utf-8') as fp:
                    data = json.load(fp)
                    self.history_data.append(data)
                    loaded_count += 1
            except Exception as e:
                print(f"Warning: Failed to load {f}: {e}")

        # 按 round 排序
        self.history_data.sort(key=lambda x: x.get('loop_round', 0), reverse=True)
        return loaded_count

    def analyze_evolution_results(self) -> Dict[str, Any]:
        """分析进化结果，提取模式和趋势"""
        if not self.history_data:
            self.load_evolution_history()

        analysis = {
            "total_rounds": len(self.history_data),
            "completed_rounds": 0,
            "failed_rounds": 0,
            "categories": defaultdict(int),
            "effectiveness_scores": [],
            "round_durations": [],
            "success_patterns": [],
            "failure_patterns": []
        }

        for ev in self.history_data:
            goal = ev.get('current_goal', '')
            # 统计完成状态
            status = ev.get('completion_status', '')
            if status == 'completed':
                analysis["completed_rounds"] += 1

                # 提取有效性评分
                if 'learning_results' in ev:
                    lr = ev['learning_results']
                    if 'avg_effectiveness' in lr:
                        analysis["effectiveness_scores"].append(lr['avg_effectiveness'])
                elif 'verification' in ev:
                    v = ev['verification']
                    if v.get('targeted_passed'):
                        analysis["effectiveness_scores"].append(0.8)

                # 提取类别
                for keyword in ['价值', '创新', '效能', '健康', '知识', '决策', '执行', '优化', '自']:
                    if keyword in goal:
                        analysis["categories"][keyword] += 1
            else:
                analysis["failed_rounds"] += 1
                analysis["failure_patterns"].append(goal[:100] if goal else "Unknown")

        # 计算平均有效性
        if analysis["effectiveness_scores"]:
            analysis["avg_effectiveness"] = sum(analysis["effectiveness_scores"]) / len(
                analysis["effectiveness_scores"]
            )
        else:
            analysis["avg_effectiveness"] = 0.5

        # 提取成功模式
        for ev in self.history_data[:50]:  # 分析最近50轮
            goal = ev.get('current_goal', '')
            if ev.get('completion_status') == 'completed' and goal:
                # 提取关键特征
                features = []
                if "引擎" in goal:
                    features.append("engine_creation")
                if "优化" in goal:
                    features.append("optimization")
                if "智能" in goal:
                    features.append("intelligent")
                if "深度" in goal or "增强" in goal:
                    features.append("enhancement")
                if "自动" in goal:
                    features.append("automation")

                analysis["success_patterns"].extend(features)

        return analysis

    def train_prediction_model(self) -> Dict[str, Any]:
        """训练预测模型 - 基于历史数据建立预测能力"""
        analysis = self.analyze_evolution_results()

        # 构建预测模型
        self.prediction_model = {
            "version": self.version,
            "trained_at": datetime.now().isoformat(),
            "features": [
                "engine_creation",
                "optimization",
                "intelligent",
                "enhancement",
                "automation",
                "cross_engine",
                "self_evolution",
                "value_driven",
                "knowledge_based"
            ],
            "category_weights": dict(analysis["categories"]),
            "baseline_effectiveness": analysis.get("avg_effectiveness", 0.5),
            "success_rate": analysis["completed_rounds"] / max(1, analysis["total_rounds"]),
            "sample_size": analysis["total_rounds"]
        }

        # 计算每个特征的预测权重
        feature_scores = defaultdict(lambda: {"success": 0, "total": 0})
        for ev in self.history_data[:100]:
            goal = ev.get('current_goal', '')
            success = ev.get('completion_status') == 'completed'

            for feature in self.prediction_model["features"]:
                if feature.replace("_", "") in goal or feature in goal:
                    feature_scores[feature]["total"] += 1
                    if success:
                        feature_scores[feature]["success"] += 1

        # 计算每个特征的成功率
        for feature, scores in feature_scores.items():
            if scores["total"] > 0:
                self.prediction_model[f"{feature}_score"] = scores["success"] / scores["total"]

        return self.prediction_model

    def predict_evolution_outcome(self, evolution_goal: str) -> Dict[str, Any]:
        """预测特定进化目标的效果"""
        if not self.prediction_model:
            self.train_prediction_model()

        # 提取目标特征
        features = []
        feature_keywords = {
            "engine_creation": ["引擎", "创建", "模块"],
            "optimization": ["优化", "提升", "增强"],
            "intelligent": ["智能", "AI", "自适应"],
            "enhancement": ["深度", "增强", "强化"],
            "automation": ["自动", "自动化"],
            "cross_engine": ["跨引擎", "协同", "集成"],
            "self_evolution": ["自进化", "自省", "自愈"],
            "value_driven": ["价值", "ROI", "效果"],
            "knowledge_based": ["知识", "图谱", "推理"]
        }

        for feature, keywords in feature_keywords.items():
            for kw in keywords:
                if kw in evolution_goal:
                    features.append(feature)
                    break

        # 预测效果
        base_effectiveness = self.prediction_model.get("baseline_effectiveness", 0.5)
        feature_bonus = 0

        for feature in features:
            score_key = f"{feature}_score"
            if score_key in self.prediction_model:
                feature_bonus += (self.prediction_model[score_key] - 0.5) * 0.1

        predicted_effectiveness = min(0.95, max(0.1, base_effectiveness + feature_bonus))

        # 预测风险
        risk_factors = []
        if len(evolution_goal) > 100:
            risk_factors.append("目标过于复杂")
        if len(features) > 5:
            risk_factors.append("涉及多个维度，可能需要更多轮次")
        if "跨" in evolution_goal or "集成" in evolution_goal:
            risk_factors.append("跨组件集成存在不确定性")

        return {
            "goal": evolution_goal[:100] + "..." if len(evolution_goal) > 100 else evolution_goal,
            "detected_features": features,
            "predicted_effectiveness": round(predicted_effectiveness, 3),
            "confidence": min(0.9, 0.3 + 0.1 * len(features)),
            "risk_factors": risk_factors,
            "recommended_approach": self._get_recommended_approach(features, predicted_effectiveness)
        }

    def _get_recommended_approach(self, features: List[str], effectiveness: float) -> str:
        """基于特征和预测效果推荐执行策略"""
        if effectiveness > 0.8:
            return "直接执行，成功概率高"
        elif effectiveness > 0.6:
            return "分阶段执行，先验证核心功能"
        elif effectiveness > 0.4:
            return "需要更多准备，建议先做小规模验证"
        else:
            return "风险较高，建议重新设计目标或分解任务"

    def select_optimal_evolution_path(self, candidates: List[str]) -> Dict[str, Any]:
        """从多个候选进化方向中选择最优路径"""
        if not self.prediction_model:
            self.train_prediction_model()

        predictions = []
        for candidate in candidates:
            pred = self.predict_evolution_outcome(candidate)
            predictions.append(pred)

        # 按预测效果排序
        predictions.sort(key=lambda x: x["predicted_effectiveness"], reverse=True)

        return {
            "candidates_analyzed": len(candidates),
            "rankings": predictions,
            "recommended": predictions[0] if predictions else None,
            "reasoning": f"基于 {len(self.history_data)} 轮历史数据的预测模型分析"
        }

    def adapt_strategy(self, execution_result: Dict[str, Any]) -> Dict[str, Any]:
        """根据执行结果自适应调整策略"""
        goal = execution_result.get("goal", "")
        success = execution_result.get("success", False)
        effectiveness = execution_result.get("effectiveness", 0.5)

        # 更新策略有效性记录
        if goal:
            self.strategy_effectiveness[goal[:50]].append(effectiveness)

        # 生成调整建议
        adjustments = []

        if not success:
            adjustments.append({
                "type": "目标调整",
                "suggestion": "将复杂目标分解为多个简单子目标分步执行"
            })
            adjustments.append({
                "type": "策略调整",
                "suggestion": "增加基线验证，确保每步可验证后再推进"
            })

        if effectiveness < 0.5:
            adjustments.append({
                "type": "资源调整",
                "suggestion": "考虑增加验证轮次或引入更多历史参考"
            })

        # 计算调整后的预测
        new_prediction = self.predict_evolution_outcome(goal) if goal else {}

        return {
            "original_goal": goal[:50] + "..." if len(goal) > 50 else goal,
            "execution_result": {
                "success": success,
                "effectiveness": effectiveness
            },
            "adjustments_made": adjustments,
            "updated_prediction": new_prediction.get("predicted_effectiveness", effectiveness),
            "learning_applied": len(self.strategy_effectiveness)
        }

    def get_cockpit_data(self) -> Dict[str, Any]:
        """获取驾驶舱展示数据"""
        analysis = self.analyze_evolution_results()
        model = self.train_prediction_model()

        return {
            "engine_name": "元进化结果预测与自适应策略优化引擎",
            "version": self.version,
            "round": 636,
            "statistics": {
                "history_rounds": analysis["total_rounds"],
                "completed_rounds": analysis["completed_rounds"],
                "success_rate": round(analysis["completed_rounds"] / max(1, analysis["total_rounds"]), 3),
                "avg_effectiveness": round(analysis.get("avg_effectiveness", 0), 3)
            },
            "prediction_model": {
                "features_count": len(model.get("features", [])),
                "baseline_effectiveness": model.get("baseline_effectiveness", 0),
                "sample_size": model.get("sample_size", 0)
            },
            "strategy_adaptations": len(self.strategy_effectiveness),
            "top_categories": dict(sorted(
                analysis["categories"].items(),
                key=lambda x: x[1],
                reverse=True
            )[:5])
        }


def main():
    """主函数 - 支持命令行调用"""
    import argparse

    parser = argparse.ArgumentParser(
        description="元进化结果预测与自适应策略深度优化引擎"
    )
    parser.add_argument("--version", action="store_true", help="显示版本信息")
    parser.add_argument("--status", action="store_true", help="显示引擎状态")
    parser.add_argument("--run", action="store_true", help="运行完整分析")
    parser.add_argument("--predict", type=str, help="预测特定进化目标的效果")
    parser.add_argument("--select", nargs="+", help="从多个候选中选择最优路径")
    parser.add_argument("--adapt", type=str, help="根据执行结果调整策略 (JSON字符串)")
    parser.add_argument("--cockpit-data", action="store_true", help="获取驾驶舱数据")

    args = parser.parse_args()

    engine = EvolutionResultPredictionEngine()

    if args.version:
        print(f"evolution_meta_evolution_result_prediction_adaptive_strategy_optimizer_engine.py v{engine.version}")
        print("智能全场景进化环元进化结果预测与自适应策略深度优化引擎")
        return

    if args.status:
        engine.load_evolution_history()
        analysis = engine.analyze_evolution_results()
        print(f"状态: 已加载 {analysis['total_rounds']} 轮历史进化数据")
        print(f"完成率: {analysis['completed_rounds']}/{analysis['total_rounds']} ({analysis['completed_rounds']*100/max(1,analysis['total_rounds']):.1f}%)")
        print(f"平均有效性: {analysis.get('avg_effectiveness', 0):.2f}")
        return

    if args.run:
        print("=== 运行完整分析 ===")
        engine.load_evolution_history()
        analysis = engine.analyze_evolution_results()
        print(f"历史轮次: {analysis['total_rounds']}")
        print(f"完成轮次: {analysis['completed_rounds']}")
        print(f"平均有效性: {analysis.get('avg_effectiveness', 0):.2f}")

        model = engine.train_prediction_model()
        print(f"\n预测模型已训练")
        print(f"特征数: {len(model.get('features', []))}")
        print(f"基线有效性: {model.get('baseline_effectiveness', 0):.2f}")

        # 示例预测
        sample_goals = [
            "智能全场景进化环元进化自我意识深度增强引擎",
            "智能全场景进化环跨引擎协同优化引擎",
            "智能全场景进化环价值预测与预防性优化引擎"
        ]
        print("\n=== 示例预测 ===")
        for goal in sample_goals:
            pred = engine.predict_evolution_outcome(goal)
            print(f"\n目标: {goal[:40]}...")
            print(f"预测有效性: {pred['predicted_effectiveness']:.2f}")
            print(f"置信度: {pred['confidence']:.2f}")
            print(f"推荐方式: {pred['recommended_approach']}")
        return

    if args.predict:
        engine.load_evolution_history()
        engine.train_prediction_model()
        pred = engine.predict_evolution_outcome(args.predict)
        print(json.dumps(pred, ensure_ascii=False, indent=2))
        return

    if args.select:
        engine.load_evolution_history()
        engine.train_prediction_model()
        result = engine.select_optimal_evolution_path(args.select)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if args.adapt:
        try:
            exec_result = json.loads(args.adapt)
            result = engine.adapt_strategy(exec_result)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        except json.JSONDecodeError:
            print("错误: 请提供有效的 JSON 字符串")
        return

    if args.cockpit_data:
        data = engine.get_cockpit_data()
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return

    parser.print_help()


if __name__ == "__main__":
    main()