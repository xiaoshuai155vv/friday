#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能进化闭环学习增强引擎（Evolution Loop Learning Enhancer）
让系统从进化执行结果中自动学习最优策略，实现真正的"学会如何进化"

功能：
1. 进化结果自动分析 - 分析进化成功率、效率、模式
2. 进化策略自动优化 - 根据分析结果调整策略
3. 闭环学习机制 - 学习→优化→验证→再学习
4. 进化效果预测 - 预测进化方向的成功率

集成：支持"进化学习"、"闭环学习"、"智能优化"等关键词触发
"""

import os
import json
import glob
from datetime import datetime, timedelta
from collections import defaultdict

SCRIPTS = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(SCRIPTS)
RUNTIME_STATE = os.path.join(PROJECT, "runtime", "state")


class EvolutionLoopLearningEnhancer:
    """智能进化闭环学习增强引擎"""

    def __init__(self):
        self.name = "EvolutionLoopLearningEnhancer"
        self.version = "1.0.0"
        self.learning_data_path = os.path.join(RUNTIME_STATE, "evolution_loop_learning_data.json")
        self.optimization_config_path = os.path.join(RUNTIME_STATE, "evolution_loop_optimization_config.json")
        self.learning_data = self._load_learning_data()
        self.optimization_config = self._load_optimization_config()

    def _load_learning_data(self):
        """加载学习数据"""
        if os.path.exists(self.learning_data_path):
            try:
                with open(self.learning_data_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "evolution_history": [],
            "pattern_success_rates": {},
            "strategy_effectiveness": {},
            "learning_insights": []
        }

    def _save_learning_data(self):
        """保存学习数据"""
        try:
            with open(self.learning_data_path, "w", encoding="utf-8") as f:
                json.dump(self.learning_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存学习数据失败: {e}")

    def _load_optimization_config(self):
        """加载优化配置"""
        if os.path.exists(self.optimization_config_path):
            try:
                with open(self.optimization_config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "strategy_weights": {
                "innovation": 0.25,
                "user_need": 0.30,
                "system_health": 0.20,
                "feasibility": 0.15,
                "efficiency": 0.10
            },
            "learning_rate": 0.1,
            "exploration_rate": 0.2,
            "last_optimization": None
        }

    def _save_optimization_config(self):
        """保存优化配置"""
        try:
            with open(self.optimization_config_path, "w", encoding="utf-8") as f:
                json.dump(self.optimization_config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存优化配置失败: {e}")

    def analyze_evolution_results(self):
        """分析进化执行结果"""
        # 读取进化历史
        evolution_files = glob.glob(os.path.join(RUNTIME_STATE, "evolution_completed_ev_*.json"))

        total = len(evolution_files)
        if total == 0:
            return {
                "total_evolution_rounds": 0,
                "message": "暂无进化历史数据"
            }

        completed = 0
        failed = 0
        success_rate_by_goal = defaultdict(lambda: {"success": 0, "total": 0})

        for f in evolution_files:
            try:
                with open(f, "r", encoding="utf-8") as fp:
                    data = json.load(fp)
                    status = data.get("result", {}).get("status", "unknown")
                    goal = data.get("current_goal", "unknown")

                    if status == "completed":
                        completed += 1
                        success_by_goal[goal]["success"] += 1
                    else:
                        failed += 1
                    success_by_goal[goal]["total"] += 1
            except Exception:
                pass

        success_rate = (completed / total * 100) if total > 0 else 0

        return {
            "total_evolution_rounds": total,
            "completed": completed,
            "failed": failed,
            "success_rate": round(success_rate, 2),
            "success_by_goal": dict(success_rate_by_goal)
        }

    def detect_patterns(self):
        """检测进化模式"""
        evolution_files = glob.glob(os.path.join(RUNTIME_STATE, "evolution_completed_ev_*.json"))

        patterns = {
            "round_intervals": [],
            "goal_categories": defaultdict(int),
            "execution_patterns": []
        }

        prev_time = None
        for f in sorted(evolution_files):
            try:
                with open(f, "r", encoding="utf-8") as fp:
                    data = json.load(fp)
                    completed_at = data.get("completed_at", "")

                    if completed_at:
                        try:
                            current_time = datetime.fromisoformat(completed_at.replace("+00:00", ""))
                            if prev_time:
                                interval = (current_time - prev_time).total_seconds() / 60
                                patterns["round_intervals"].append(interval)
                            prev_time = current_time
                        except Exception:
                            pass

                    goal = data.get("current_goal", "")
                    if "智能" in goal and "引擎" in goal:
                        category = goal.split("智能")[1].split("引擎")[0] if "智能" in goal and "引擎" in goal else "other"
                        patterns["goal_categories"][category] += 1
            except Exception:
                pass

        avg_interval = sum(patterns["round_intervals"]) / len(patterns["round_intervals"]) if patterns["round_intervals"] else 0

        return {
            "patterns_detected": len(patterns["goal_categories"]),
            "most_common_categories": dict(sorted(patterns["goal_categories"].items(), key=lambda x: x[1], reverse=True)[:5]),
            "average_round_interval_minutes": round(avg_interval, 2),
            "total_intervals": len(patterns["round_intervals"])
        }

    def optimize_strategy(self):
        """自动优化进化策略"""
        analysis = self.analyze_evolution_results()
        patterns = self.detect_patterns()

        # 基于分析结果优化策略权重
        current_weights = self.optimization_config["strategy_weights"]

        # 如果成功率低，增加可行性权重
        success_rate = analysis.get("success_rate", 50)
        if success_rate < 50:
            current_weights["feasibility"] = min(0.30, current_weights["feasibility"] + 0.05)
            current_weights["efficiency"] = min(0.20, current_weights["efficiency"] + 0.05)
            current_weights["innovation"] = max(0.15, current_weights["innovation"] - 0.05)
        # 如果成功率高，增加创新权重
        elif success_rate > 80:
            current_weights["innovation"] = min(0.35, current_weights["innovation"] + 0.05)
            current_weights["user_need"] = min(0.35, current_weights["user_need"] + 0.05)

        # 根据模式调整
        avg_interval = patterns.get("average_round_interval_minutes", 60)
        if avg_interval < 30:
            # 进化太快，增加效率关注
            current_weights["efficiency"] = min(0.20, current_weights["efficiency"] + 0.03)
        elif avg_interval > 120:
            # 进化太慢，增加创新
            current_weights["innovation"] = min(0.35, current_weights["innovation"] + 0.03)

        self.optimization_config["strategy_weights"] = current_weights
        self.optimization_config["last_optimization"] = datetime.now().isoformat()
        self._save_optimization_config()

        return {
            "optimized_weights": current_weights,
            "optimization_basis": {
                "success_rate": success_rate,
                "avg_interval": avg_interval
            },
            "message": "策略优化完成"
        }

    def predict_evolution_success(self, evolution_goal):
        """预测进化方向的成功率"""
        # 简单预测：基于历史相似目标
        evolution_files = glob.glob(os.path.join(RUNTIME_STATE, "evolution_completed_ev_*.json"))

        similar_goals = []
        for f in evolution_files:
            try:
                with open(f, "r", encoding="utf-8") as fp:
                    data = json.load(fp)
                    goal = data.get("current_goal", "")
                    # 简单相似度：检查关键词重叠
                    goal_keywords = set(goal.split())
                    target_keywords = set(evolution_goal.split())
                    overlap = len(goal_keywords & target_keywords)
                    if overlap > 0:
                        status = data.get("result", {}).get("status", "unknown")
                        similar_goals.append({
                            "goal": goal,
                            "overlap": overlap,
                            "status": status
                        })
            except Exception:
                pass

        if similar_goals:
            # 计算相似目标的历史成功率
            similar_goals.sort(key=lambda x: x["overlap"], reverse=True)
            top_similar = similar_goals[:5]
            success_count = sum(1 for g in top_similar if g["status"] == "completed")
            predicted_success_rate = (success_count / len(top_similar) * 100) if top_similar else 50
        else:
            predicted_success_rate = 50

        return {
            "evolution_goal": evolution_goal,
            "predicted_success_rate": round(predicted_success_rate, 2),
            "similar_goals_analyzed": len(similar_goals),
            "confidence": "high" if len(similar_goals) >= 5 else "medium" if len(similar_goals) >= 2 else "low"
        }

    def generate_learning_insight(self):
        """生成学习洞察"""
        analysis = self.analyze_evolution_results()
        patterns = self.detect_patterns()

        insights = []

        # 基于成功率洞察
        success_rate = analysis.get("success_rate", 0)
        if success_rate < 50:
            insights.append("进化成功率偏低，建议增加可行性评估，降低过于激进的创新")
        elif success_rate > 80:
            insights.append("进化成功率很高，可以尝试更激进的创新方向")

        # 基于模式洞察
        most_common = patterns.get("most_common_categories", {})
        if most_common:
            top_category = max(most_common.items(), key=lambda x: x[1])
            insights.append(f"最常见的进化方向是「{top_category[0]}」，共 {top_category[1]} 轮")

        # 基于时间间隔洞察
        avg_interval = patterns.get("average_round_interval_minutes", 0)
        if avg_interval < 30:
            insights.append("进化节奏很快，可能需要更多质量保证措施")
        elif avg_interval > 120:
            insights.append("进化节奏较慢，考虑增加自动化程度")

        return {
            "insights": insights,
            "analysis_summary": analysis,
            "pattern_summary": patterns,
            "generated_at": datetime.now().isoformat()
        }

    def status(self):
        """获取状态"""
        return {
            "name": self.name,
            "version": self.version,
            "total_learning_rounds": len(self.learning_data.get("evolution_history", [])),
            "strategy_weights": self.optimization_config.get("strategy_weights", {}),
            "last_optimization": self.optimization_config.get("last_optimization"),
            "learning_data_exists": os.path.exists(self.learning_data_path)
        }


def main():
    """主入口"""
    import argparse

    parser = argparse.ArgumentParser(description="智能进化闭环学习增强引擎")
    parser.add_argument("command", nargs="?", default="status",
                        help="命令: status/analyze/patterns/optimize/predict/insights")
    parser.add_argument("--goal", type=str, help="进化目标（用于预测）")

    args = parser.parse_args()

    enhancer = EvolutionLoopLearningEnhancer()

    if args.command == "status":
        result = enhancer.status()
        print(f"\n=== 智能进化闭环学习增强引擎 ===")
        print(f"版本: {result['version']}")
        print(f"学习轮次: {result['total_learning_rounds']}")
        print(f"策略权重: {result['strategy_weights']}")
        print(f"上次优化: {result['last_optimization']}")
        print(f"学习数据: {'已存在' if result['learning_data_exists'] else '不存在'}")

    elif args.command == "analyze":
        result = enhancer.analyze_evolution_results()
        print(f"\n=== 进化结果分析 ===")
        print(f"总进化轮次: {result['total_evolution_rounds']}")
        print(f"已完成: {result['completed']}")
        print(f"失败: {result['failed']}")
        print(f"成功率: {result['success_rate']}%")

    elif args.command == "patterns":
        result = enhancer.detect_patterns()
        print(f"\n=== 进化模式检测 ===")
        print(f"检测到的模式类别: {result['patterns_detected']}")
        print(f"最常见类别: {result['most_common_categories']}")
        print(f"平均轮次间隔: {result['average_round_interval_minutes']} 分钟")

    elif args.command == "optimize":
        result = enhancer.optimize_strategy()
        print(f"\n=== 策略优化结果 ===")
        print(f"优化后的权重: {result['optimized_weights']}")
        print(f"优化依据: {result['optimization_basis']}")
        print(result['message'])

    elif args.command == "predict":
        goal = args.goal or "智能进化引擎"
        result = enhancer.predict_evolution_success(goal)
        print(f"\n=== 进化成功率预测 ===")
        print(f"目标: {result['evolution_goal']}")
        print(f"预测成功率: {result['predicted_success_rate']}%")
        print(f"置信度: {result['confidence']}")
        print(f"分析的相似目标: {result['similar_goals_analyzed']}")

    elif args.command == "insights":
        result = enhancer.generate_learning_insight()
        print(f"\n=== 学习洞察 ===")
        for i, insight in enumerate(result['insights'], 1):
            print(f"{i}. {insight}")
        print(f"\n生成时间: {result['generated_at']}")

    else:
        print(f"未知命令: {args.command}")
        print("可用命令: status, analyze, patterns, optimize, predict, insights")


if __name__ == "__main__":
    main()