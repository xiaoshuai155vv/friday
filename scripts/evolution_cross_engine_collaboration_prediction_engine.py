#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环跨引擎协同效能预测增强引擎
(Evolution Cross-Engine Collaboration Prediction Enhancement Engine)

在 round 476 完成的进化效能预测与预防性优化引擎基础上，
进一步构建跨引擎协同效能的预测增强能力。

让系统能够预测多个引擎协同工作时的效能，提前发现协同问题，
实现从「单引擎效能预测」到「跨引擎协同效能预测」的范式升级。

让进化环能够预测引擎之间的协作效果，提前发现协作瓶颈，
并提供优化建议。

Version: 1.0.0
"""

import json
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from collections import defaultdict
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
    from evolution_effectiveness_prediction_prevention_engine import (
        EvolutionEffectivenessPredictionPreventionEngine
    )
    EFFECTIVENESS_PREDICTION_AVAILABLE = True
except ImportError:
    EFFECTIVENESS_PREDICTION_AVAILABLE = False


class CrossEngineCollaborationPredictionEngine:
    """跨引擎协同效能预测增强引擎核心类"""

    def __init__(self):
        self.version = "1.0.0"
        self.name = "Evolution Cross-Engine Collaboration Prediction Enhancement Engine"
        self.runtime_dir = PROJECT_ROOT / "runtime"
        self.state_dir = self.runtime_dir / "state"
        self.data_dir = self.runtime_dir / "data"

        # 数据文件路径
        self.config_file = self.data_dir / "cross_engine_collaboration_prediction_config.json"
        self.collaboration_history_file = self.data_dir / "cross_engine_collaboration_history.json"
        self.prediction_results_file = self.data_dir / "cross_engine_prediction_results.json"
        self.early_warning_file = self.data_dir / "cross_engine_early_warning.json"

        self._ensure_directories()
        self._initialize_data()

    def _ensure_directories(self):
        """确保必要的目录存在"""
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def _initialize_data(self):
        """初始化数据文件"""
        if not self.config_file.exists():
            default_config = {
                "prediction_enabled": True,
                "collaboration_analysis": {
                    "enabled": True,
                    "history_window": 20,  # 分析窗口大小
                    "min_samples": 5,  # 最少样本数
                    "correlation_threshold": 0.3  # 协同相关性阈值
                },
                "prediction": {
                    "enabled": True,
                    "horizon_rounds": 5,
                    "confidence_threshold": 0.6,
                    "metrics": [
                        "collaboration_success_rate",
                        "coordination_efficiency",
                        "resource_contention",
                        "execution_overhead"
                    ]
                },
                "early_warning": {
                    "enabled": True,
                    "risk_threshold": 0.35,
                    "auto_notify": False,
                    "warning_levels": ["low", "medium", "high", "critical"]
                },
                "prediction_history": [],
                "warning_history": []
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, ensure_ascii=False, indent=2)

        if not self.collaboration_history_file.exists():
            with open(self.collaboration_history_file, 'w', encoding='utf-8') as f:
                json.dump({"collaborations": [], "last_analysis": None}, f, ensure_ascii=False, indent=2)

        if not self.prediction_results_file.exists():
            with open(self.prediction_results_file, 'w', encoding='utf-8') as f:
                json.dump({"predictions": [], "last_prediction": None}, f, ensure_ascii=False, indent=2)

    def _load_config(self) -> Dict:
        """加载配置"""
        with open(self.config_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def analyze_cross_engine_collaboration(self) -> Dict[str, Any]:
        """分析跨引擎协同效能"""
        print("[跨引擎协同预测] 分析跨引擎协同效能...")

        config = self._load_config()
        history_window = config.get("collaboration_analysis", {}).get("history_window", 20)

        # 收集历史进化记录
        completed_files = list(self.state_dir.glob("evolution_completed_*.json"))
        completed_files = sorted(completed_files, key=lambda x: x.name)[-history_window:]

        collaboration_data = []
        for file in completed_files:
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                round_num = data.get("loop_round", 0)
                goal = data.get("current_goal", "")
                status = data.get("status", "")
                baseline_pass = data.get("baseline_passed", False)
                targeted_pass = data.get("targeted_passed", False)

                # 提取涉及的引擎类型
                engines_involved = self._extract_engines_from_goal(goal)

                collaboration_entry = {
                    "round": round_num,
                    "goal": goal,
                    "status": status,
                    "baseline_passed": baseline_pass,
                    "targeted_passed": targeted_pass,
                    "engines_involved": engines_involved,
                    "success": status == "completed" and baseline_pass and targeted_pass
                }
                collaboration_data.append(collaboration_entry)
            except Exception as e:
                print(f"  警告：读取 {file.name} 失败: {e}")

        # 分析引擎协同模式
        engine_pairs = defaultdict(lambda: {"total": 0, "success": 0, "rounds": []})
        for entry in collaboration_data:
            engines = entry.get("engines_involved", [])
            for i, engine1 in enumerate(engines):
                for engine2 in engines[i+1:]:
                    pair_key = tuple(sorted([engine1, engine2]))
                    engine_pairs[pair_key]["total"] += 1
                    if entry["success"]:
                        engine_pairs[pair_key]["success"] += 1
                    engine_pairs[pair_key]["rounds"].append(entry["round"])

        # 计算协同成功率
        collaboration_stats = {}
        for pair, stats in engine_pairs.items():
            success_rate = stats["success"] / stats["total"] if stats["total"] > 0 else 0
            collaboration_stats[f"{pair[0]}+{pair[1]}"] = {
                "total_collaborations": stats["total"],
                "successful_collaborations": stats["success"],
                "success_rate": round(success_rate, 3),
                "rounds": stats["rounds"]
            }

        # 统计整体协同效能
        overall_stats = {
            "total_rounds": len(collaboration_data),
            "successful_rounds": sum(1 for e in collaboration_data if e["success"]),
            "overall_success_rate": round(
                sum(1 for e in collaboration_data if e["success"]) / len(collaboration_data)
                if collaboration_data else 0, 3
            ),
            "engine_pairs": collaboration_stats
        }

        # 保存分析结果
        with open(self.collaboration_history_file, 'w', encoding='utf-8') as f:
            json.dump({
                "collaborations": collaboration_data,
                "stats": overall_stats,
                "last_analysis": datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)

        print(f"  分析完成：共 {len(collaboration_data)} 轮进化记录")
        print(f"  整体协同成功率：{overall_stats['overall_success_rate']:.1%}")
        print(f"  发现 {len(collaboration_stats)} 对引擎协同模式")

        return overall_stats

    def _extract_engines_from_goal(self, goal: str) -> List[str]:
        """从目标描述中提取涉及的引擎类型"""
        goal_lower = goal.lower()

        # 引擎关键词映射
        engine_keywords = {
            "元进化": ["meta", "元进化", "元认知"],
            "知识": ["knowledge", "知识", "知识图谱"],
            "价值": ["value", "价值", "价值实现"],
            "认知": ["cognition", "认知", "意识"],
            "协同": ["collaboration", "协同", "协作"],
            "预测": ["prediction", "预测", "预防"],
            "效能": ["effectiveness", "效能", "效率"],
            "决策": ["decision", "决策"],
            "执行": ["execution", "执行"],
            "优化": ["optimization", "优化", "自优化"]
        }

        involved_engines = []
        for engine_name, keywords in engine_keywords.items():
            if any(kw in goal_lower for kw in keywords):
                involved_engines.append(engine_name)

        # 如果没有匹配到，返回默认值
        if not involved_engines:
            involved_engines = ["综合"]

        return involved_engines

    def predict_collaboration_effectiveness(self) -> Dict[str, Any]:
        """预测跨引擎协同效能趋势"""
        print("[跨引擎协同预测] 预测跨引擎协同效能趋势...")

        config = self._load_config()
        horizon = config.get("prediction", {}).get("horizon_rounds", 5)

        # 首先分析当前协同效能
        current_stats = self.analyze_cross_engine_collaboration()

        # 基于历史数据预测未来趋势
        predictions = {
            "prediction_time": datetime.now().isoformat(),
            "horizon_rounds": horizon,
            "current_status": current_stats,
            "trends": [],
            "risk_assessment": {}
        }

        # 分析各引擎对的协同趋势
        engine_pairs = current_stats.get("engine_pairs", {})
        for pair_key, stats in engine_pairs.items():
            total = stats.get("total_collaborations", 0)
            success_rate = stats.get("success_rate", 0)

            # 简单趋势预测：如果历史成功率低于 0.7，预测可能下降
            trend = "stable"
            risk_level = "low"

            if success_rate < 0.5:
                trend = "declining"
                risk_level = "high"
            elif success_rate < 0.7:
                trend = "slightly_declining"
                risk_level = "medium"

            predictions["trends"].append({
                "engine_pair": pair_key,
                "current_success_rate": success_rate,
                "predicted_trend": trend,
                "risk_level": risk_level,
                "confidence": min(total / 10, 1.0)  # 基于样本数的置信度
            })

        # 计算整体风险评估
        high_risk_pairs = [t for t in predictions["trends"] if t["risk_level"] == "high"]
        medium_risk_pairs = [t for t in predictions["trends"] if t["risk_level"] == "medium"]

        overall_risk = len(high_risk_pairs) * 0.4 + len(medium_risk_pairs) * 0.2
        predictions["risk_assessment"] = {
            "overall_risk_score": round(min(overall_risk, 1.0), 2),
            "risk_level": "critical" if overall_risk > 0.6 else "high" if overall_risk > 0.4 else "medium" if overall_risk > 0.2 else "low",
            "high_risk_pairs": high_risk_pairs,
            "medium_risk_pairs": medium_risk_pairs,
            "recommendation": self._generate_recommendation(high_risk_pairs, medium_risk_pairs)
        }

        # 保存预测结果
        with open(self.prediction_results_file, 'w', encoding='utf-8') as f:
            json.dump(predictions, f, ensure_ascii=False, indent=2)

        print(f"  预测完成：未来 {horizon} 轮")
        print(f"  整体风险评估：{predictions['risk_assessment']['risk_level']} ({predictions['risk_assessment']['overall_risk_score']:.2f})")

        return predictions

    def _generate_recommendation(self, high_risk: List, medium_risk: List) -> str:
        """生成优化建议"""
        if not high_risk and not medium_risk:
            return "跨引擎协同效能良好，无需特别优化。建议保持当前策略。"

        recommendations = []
        if high_risk:
            recommendations.append(f"发现 {len(high_risk)} 对高风险引擎协同，需要重点关注。")
        if medium_risk:
            recommendations.append(f"发现 {len(medium_risk)} 对中等风险引擎协同，建议适时优化。")

        recommendations.append("建议：1) 降低高风险引擎对的同时调用频率；2) 增加协同执行的前置检查；3) 考虑拆分为串行执行。")

        return " ".join(recommendations)

    def generate_early_warning(self) -> Dict[str, Any]:
        """生成跨引擎协同早期预警"""
        print("[跨引擎协同预测] 生成早期预警...")

        config = self._load_config()
        risk_threshold = config.get("early_warning", {}).get("risk_threshold", 0.35)

        # 获取预测结果
        predictions = self.predict_collaboration_effectiveness()
        risk_assessment = predictions.get("risk_assessment", {})
        overall_risk = risk_assessment.get("overall_risk_score", 0)
        risk_level = risk_assessment.get("risk_level", "low")

        # 生成预警
        warning = {
            "warning_time": datetime.now().isoformat(),
            "triggered": overall_risk > risk_threshold,
            "risk_level": risk_level,
            "risk_score": overall_risk,
            "threshold": risk_threshold,
            "details": {
                "high_risk_pairs": risk_assessment.get("high_risk_pairs", []),
                "medium_risk_pairs": risk_assessment.get("medium_risk_pairs", []),
                "recommendation": risk_assessment.get("recommendation", "")
            }
        }

        # 保存预警
        with open(self.prediction_results_file.parent / "cross_engine_early_warning.json", 'w', encoding='utf-8') as f:
            json.dump(warning, f, ensure_ascii=False, indent=2)

        if warning["triggered"]:
            print(f"  预警触发！风险等级：{risk_level}，风险分数：{overall_risk:.2f}")
            print(f"  建议：{risk_assessment.get('recommendation', '')}")
        else:
            print(f"  未触发预警。风险等级：{risk_level}，风险分数：{overall_risk:.2f}")

        return warning

    def get_cockpit_data(self) -> Dict[str, Any]:
        """获取驾驶舱展示数据"""
        predictions = self.predict_collaboration_effectiveness()

        return {
            "title": "跨引擎协同效能预测",
            "timestamp": datetime.now().isoformat(),
            "current_status": predictions.get("current_status", {}),
            "trends": predictions.get("trends", []),
            "risk_assessment": predictions.get("risk_assessment", {}),
            "visualization": {
                "type": "collaboration_matrix",
                "data": predictions.get("trends", [])
            }
        }

    def run_analysis(self) -> Dict[str, Any]:
        """运行完整分析"""
        result = {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "analysis": self.analyze_cross_engine_collaboration(),
            "predictions": self.predict_collaboration_effectiveness(),
            "warnings": self.generate_early_warning()
        }
        return result


def main():
    """主入口"""
    import argparse

    parser = argparse.ArgumentParser(description="跨引擎协同效能预测增强引擎")
    parser.add_argument("--status", action="store_true", help="查看当前状态")
    parser.add_argument("--analyze", action="store_true", help="分析跨引擎协同效能")
    parser.add_argument("--predict", action="store_true", help="预测协同效能趋势")
    parser.add_argument("--warning", action="store_true", help="生成早期预警")
    parser.add_argument("--cockpit-data", action="store_true", help="获取驾驶舱数据")
    parser.add_argument("--run", action="store_true", help="运行完整分析")

    args = parser.parse_args()

    engine = CrossEngineCollaborationPredictionEngine()

    if args.status:
        result = engine.analyze_cross_engine_collaboration()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.analyze:
        result = engine.analyze_cross_engine_collaboration()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.predict:
        result = engine.predict_collaboration_effectiveness()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.warning:
        result = engine.generate_early_warning()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.cockpit_data:
        result = engine.get_cockpit_data()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.run:
        result = engine.run_analysis()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()