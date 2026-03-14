#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环进化效能预测与预防性优化引擎
(Evolution Effectiveness Prediction & Preventive Optimization Engine)

在 round 475 完成的自我进化效能深度分析与自适应优化引擎基础上，
进一步构建进化效能的预测与预防性优化能力。

让系统能够基于历史进化数据预测未来效能趋势、在问题发生前主动部署预防措施，
实现从「被动分析」到「主动预测预防」的范式升级。

让进化环能够不仅分析过去发生了什么，还能预测未来会发生什么，
并提前采取行动避免问题。

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
    from evolution_self_evolution_effectiveness_analysis_engine import (
        SelfEvolutionEffectivenessAnalysisEngine
    )
    EFFECTIVENESS_ANALYSIS_AVAILABLE = True
except ImportError:
    EFFECTIVENESS_ANALYSIS_AVAILABLE = False


class EvolutionEffectivenessPredictionPreventionEngine:
    """进化效能预测与预防性优化引擎核心类"""

    def __init__(self):
        self.version = "1.0.0"
        self.name = "Evolution Effectiveness Prediction & Preventive Optimization Engine"
        self.runtime_dir = PROJECT_ROOT / "runtime"
        self.state_dir = self.runtime_dir / "state"
        self.data_dir = self.runtime_dir / "data"

        # 数据文件路径
        self.config_file = self.data_dir / "effectiveness_prediction_config.json"
        self.prediction_log_file = self.data_dir / "effectiveness_prediction_log.json"
        self.preventive_actions_file = self.data_dir / "effectiveness_preventive_actions.json"
        self.trend_history_file = self.data_dir / "effectiveness_trend_history.json"

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
                "prediction": {
                    "enabled": True,
                    "horizon_rounds": 5,  # 预测未来多少轮
                    "confidence_threshold": 0.7,  # 置信度阈值
                    "metrics": [
                        "success_rate",
                        "execution_time",
                        "resource_usage",
                        "baseline_pass_rate",
                        "targeted_pass_rate"
                    ]
                },
                "preventive_optimization": {
                    "enabled": True,
                    "auto_apply": False,  # 需要确认后再应用
                    "risk_threshold": 0.3,  # 风险阈值，低于此值触发预防
                    "action_types": [
                        "parameter_adjustment",
                        "strategy_change",
                        "resource_reallocation",
                        "priority_adjustment"
                    ]
                },
                "trend_analysis": {
                    "enabled": True,
                    "window_size": 10,  # 分析窗口大小
                    "degradation_threshold": 0.15  # 退化阈值
                },
                "prediction_history": [],
                "preventive_actions_history": []
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, ensure_ascii=False, indent=2)

        if not self.prediction_log_file.exists():
            with open(self.prediction_log_file, 'w', encoding='utf-8') as f:
                json.dump({"predictions": [], "last_prediction": None}, f, ensure_ascii=False, indent=2)

        if not self.preventive_actions_file.exists():
            with open(self.preventive_actions_file, 'w', encoding='utf-8') as f:
                json.dump({"actions": [], "total_applied": 0}, f, ensure_ascii=False, indent=2)

        if not self.trend_history_file.exists():
            with open(self.trend_history_file, 'w', encoding='utf-8') as f:
                json.dump({"trends": [], "last_analysis": None}, f, ensure_ascii=False, indent=2)

    def _load_config(self) -> Dict:
        """加载配置"""
        with open(self.config_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def collect_historical_data(self) -> List[Dict]:
        """收集历史效能数据"""
        print("[进化效能预测] 收集历史效能数据...")

        # 收集 evolution_completed_*.json 文件
        completed_files = list(self.state_dir.glob("evolution_completed_*.json"))

        historical_data = []
        for file in sorted(completed_files, key=lambda x: x.name):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if "loop_round" in data:
                        round_info = {
                            "round": data.get("loop_round", 0),
                            "goal": data.get("current_goal", ""),
                            "status": data.get("status", ""),
                            "completed_at": data.get("completed_at", ""),
                            "baseline_passed": data.get("baseline_passed", None),
                            "targeted_passed": data.get("targeted_passed", None)
                        }
                        historical_data.append(round_info)
            except Exception as e:
                print(f"  警告：读取 {file.name} 失败: {e}")

        # 按轮次排序
        historical_data.sort(key=lambda x: x.get("round", 0))

        print(f"[进化效能预测] 收集完成 - 共 {len(historical_data)} 轮历史数据")
        return historical_data

    def analyze_trends(self) -> Dict[str, Any]:
        """分析效能趋势"""
        print("[进化效能预测] 分析效能趋势...")

        config = self._load_config()
        window_size = config.get("trend_analysis", {}).get("window_size", 10)
        degradation_threshold = config.get("trend_analysis", {}).get("degradation_threshold", 0.15)

        historical_data = self.collect_historical_data()

        if len(historical_data) < window_size:
            print(f"[进化效能预测] 数据不足，需要至少 {window_size} 轮数据")
            return {
                "status": "insufficient_data",
                "available_rounds": len(historical_data),
                "required_rounds": window_size,
                "trends": {}
            }

        # 计算各项指标的趋势
        trends = {
            "analysis_time": datetime.now().isoformat(),
            "window_size": window_size,
            "metrics": {}
        }

        # 分析成功率趋势
        success_rates = []
        for data in historical_data[-window_size:]:
            status = data.get("status", "").lower()
            if "完成" in status or "completed" in status or "pass" in status:
                success_rates.append(1)
            elif "未完成" in status or "failed" in status or "incomplete" in status:
                success_rates.append(0)
            else:
                success_rates.append(0.5)  # 未知状态

        if success_rates:
            # 计算趋势（简单线性回归斜率）
            trend = self._calculate_trend(success_rates)
            trends["metrics"]["success_rate"] = {
                "values": success_rates,
                "trend": trend,
                "direction": "improving" if trend > degradation_threshold else ("degrading" if trend < -degradation_threshold else "stable"),
                "avg_recent": statistics.mean(success_rates[-3:]) if len(success_rates) >= 3 else statistics.mean(success_rates)
            }

        # 分析基线通过率趋势
        baseline_rates = []
        for data in historical_data[-window_size:]:
            bp = data.get("baseline_passed")
            if bp is True:
                baseline_rates.append(1)
            elif bp is False:
                baseline_rates.append(0)
            else:
                baseline_rates.append(0.5)

        if baseline_rates:
            trend = self._calculate_trend(baseline_rates)
            trends["metrics"]["baseline_pass_rate"] = {
                "values": baseline_rates,
                "trend": trend,
                "direction": "improving" if trend > degradation_threshold else ("degrading" if trend < -degradation_threshold else "stable"),
                "avg_recent": statistics.mean(baseline_rates[-3:]) if len(baseline_rates) >= 3 else statistics.mean(baseline_rates)
            }

        # 分析针对性校验通过率趋势
        targeted_rates = []
        for data in historical_data[-window_size:]:
            tp = data.get("targeted_passed")
            if tp is True:
                targeted_rates.append(1)
            elif tp is False:
                targeted_rates.append(0)
            else:
                targeted_rates.append(0.5)

        if targeted_rates:
            trend = self._calculate_trend(targeted_rates)
            trends["metrics"]["targeted_pass_rate"] = {
                "values": targeted_rates,
                "trend": trend,
                "direction": "improving" if trend > degradation_threshold else ("degrading" if trend < -degradation_threshold else "stable"),
                "avg_recent": statistics.mean(targeted_rates[-3:]) if len(targeted_rates) >= 3 else statistics.mean(targeted_rates)
            }

        # 保存趋势历史
        with open(self.trend_history_file, 'w', encoding='utf-8') as f:
            json.dump(trends, f, ensure_ascii=False, indent=2)

        # 输出趋势分析结果
        print(f"[进化效能预测] 趋势分析完成:")
        for metric, info in trends.get("metrics", {}).items():
            direction = info.get("direction", "unknown")
            print(f"  - {metric}: {direction} (趋势值: {info.get('trend', 0):.3f})")

        return trends

    def _calculate_trend(self, values: List[float]) -> float:
        """计算简单趋势（线性回归斜率）"""
        if len(values) < 2:
            return 0

        n = len(values)
        x = list(range(n))

        # 简单线性回归
        x_mean = sum(x) / n
        y_mean = sum(values) / n

        numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            return 0

        return numerator / denominator

    def predict_future(self) -> Dict[str, Any]:
        """预测未来效能"""
        print("[进化效能预测] 预测未来效能...")

        config = self._load_config()
        horizon = config.get("prediction", {}).get("horizon_rounds", 5)
        confidence_threshold = config.get("prediction", {}).get("confidence_threshold", 0.7)

        # 分析趋势
        trends = self.analyze_trends()

        if trends.get("status") == "insufficient_data":
            return {"status": "insufficient_data", "message": "数据不足无法预测"}

        prediction = {
            "prediction_time": datetime.now().isoformat(),
            "horizon": horizon,
            "predictions": {},
            "risk_assessment": {}
        }

        # 对每个指标进行预测
        for metric, info in trends.get("metrics", {}).items():
            if isinstance(info, dict) and "trend" in info and "values" in info:
                trend = info.get("trend", 0)
                current_avg = info.get("avg_recent", 0.5)

                # 预测未来值
                future_values = []
                for h in range(1, horizon + 1):
                    predicted = current_avg + (trend * h)
                    # 限制在 [0, 1] 范围内
                    predicted = max(0, min(1, predicted))
                    future_values.append(predicted)

                # 计算置信度（基于趋势稳定性）
                values = info.get("values", [])
                stability = 1 - min(1, statistics.stdev(values) if len(values) > 1 else 0)
                confidence = stability

                prediction["predictions"][metric] = {
                    "current": current_avg,
                    "future": future_values,
                    "trend": trend,
                    "confidence": confidence,
                    "risk_level": self._assess_risk(future_values[-1], confidence)
                }

        # 整体风险评估
        overall_risk = self._calculate_overall_risk(prediction.get("predictions", {}))
        prediction["risk_assessment"] = {
            "overall_risk": overall_risk,
            "risk_level": "high" if overall_risk > 0.7 else ("medium" if overall_risk > 0.3 else "low"),
            "recommendation": self._generate_recommendation(overall_risk)
        }

        # 保存预测结果
        with open(self.prediction_log_file, 'w', encoding='utf-8') as f:
            json.dump(prediction, f, ensure_ascii=False, indent=2)

        # 输出预测结果
        print(f"[进化效能预测] 预测完成:")
        for metric, pred in prediction.get("predictions", {}).items():
            print(f"  - {metric}: 当前 {pred.get('current', 0):.2%}, "
                  f"预测 {horizon} 轮后 {pred.get('future', [0])[-1]:.2%}, "
                  f"风险等级: {pred.get('risk_level', 'unknown')}")

        print(f"\n整体风险评估: {prediction['risk_assessment'].get('risk_level', 'unknown')} "
              f"({prediction['risk_assessment'].get('overall_risk', 0):.1%})")
        print(f"建议: {prediction['risk_assessment'].get('recommendation', '')}")

        return prediction

    def _assess_risk(self, predicted_value: float, confidence: float) -> str:
        """评估风险等级"""
        if predicted_value < 0.5:
            return "high"
        elif predicted_value < 0.7:
            return "medium"
        else:
            return "low"

    def _calculate_overall_risk(self, predictions: Dict) -> float:
        """计算整体风险"""
        if not predictions:
            return 0.5

        risk_scores = []
        for metric, pred in predictions.items():
            future_val = pred.get("future", [0.5])[-1]
            risk = 1 - future_val  # 价值越低，风险越高
            risk_scores.append(risk)

        return statistics.mean(risk_scores) if risk_scores else 0.5

    def _generate_recommendation(self, overall_risk: float) -> str:
        """生成建议"""
        if overall_risk > 0.7:
            return "高风险！建议立即采取预防性优化措施"
        elif overall_risk > 0.3:
            return "中等风险，建议密切关注并准备预防措施"
        else:
            return "风险较低，维持当前策略"

    def generate_preventive_actions(self) -> List[Dict[str, Any]]:
        """生成预防性优化措施"""
        print("[进化效能预测] 生成预防性优化措施...")

        config = self._load_config()
        risk_threshold = config.get("preventive_optimization", {}).get("risk_threshold", 0.3)
        action_types = config.get("preventive_optimization", {}).get("action_types", [])

        # 获取预测结果
        prediction = self.predict_future()

        if prediction.get("status") == "insufficient_data":
            print("[进化效能预测] 数据不足，无法生成预防措施")
            return []

        predictions = prediction.get("predictions", {})
        overall_risk = prediction.get("risk_assessment", {}).get("overall_risk", 0)

        actions = []

        # 基于风险评估生成预防措施
        if overall_risk > risk_threshold:
            # 成功率风险
            if "success_rate" in predictions:
                pred = predictions["success_rate"]
                if pred.get("risk_level") in ["high", "medium"]:
                    actions.append({
                        "type": "strategy_change",
                        "priority": "high",
                        "target": "success_rate",
                        "description": "调整进化策略，增加保守策略比例",
                        "suggested_action": "在后续进化中增加验证步骤，使用更稳妥的执行方案",
                        "reason": f"预测成功率下降至 {pred.get('future', [0])[-1]:.1%}"
                    })

            # 基线通过率风险
            if "baseline_pass_rate" in predictions:
                pred = predictions["baseline_pass_rate"]
                if pred.get("risk_level") in ["high", "medium"]:
                    actions.append({
                        "type": "parameter_adjustment",
                        "priority": "high",
                        "target": "baseline_pass_rate",
                        "description": "增强基础能力保障",
                        "suggested_action": "在执行新功能前先验证基础能力未退化",
                        "reason": f"预测基线通过率下降至 {pred.get('future', [0])[-1]:.1%}"
                    })

            # 针对性校验风险
            if "targeted_pass_rate" in predictions:
                pred = predictions["targeted_pass_rate"]
                if pred.get("risk_level") in ["high", "medium"]:
                    actions.append({
                        "type": "resource_reallocation",
                        "priority": "medium",
                        "target": "targeted_pass_rate",
                        "description": "增加测试资源投入",
                        "suggested_action": "增强针对性测试覆盖，确保新功能正确实现",
                        "reason": f"预测针对性通过率下降至 {pred.get('future', [0])[-1]:.1%}"
                    })

            # 通用预防措施
            actions.append({
                "type": "priority_adjustment",
                "priority": "medium",
                "target": "overall",
                "description": "增强监控频率",
                "suggested_action": "增加效能监控频率，及早发现退化趋势",
                "reason": f"整体风险等级: {prediction.get('risk_assessment', {}).get('risk_level', 'unknown')}"
            })

        # 保存预防措施
        with open(self.preventive_actions_file, 'w', encoding='utf-8') as f:
            json.dump({"actions": actions, "total_generated": len(actions)}, f, ensure_ascii=False, indent=2)

        # 输出预防措施
        print(f"[进化效能预测] 生成了 {len(actions)} 项预防性措施:")
        for i, action in enumerate(actions, 1):
            print(f"  {i}. [{action.get('priority', 'unknown').upper()}] {action.get('description')}")
            print(f"     原因: {action.get('reason', '')}")
            print(f"     建议: {action.get('suggested_action', '')}")

        return actions

    def apply_preventive_optimization(self, action_index: int = -1) -> Dict[str, Any]:
        """执行预防性优化"""
        print("[进化效能预测] 执行预防性优化...")

        # 生成预防措施
        actions = self.generate_preventive_actions()

        if not actions:
            print("[进化效能预测] 无需执行的预防措施")
            return {"status": "no_actions", "message": "当前无需预防性优化"}

        # 选择要执行的操作（默认执行最高优先级）
        if action_index < 0 or action_index >= len(actions):
            action = actions[0]  # 执行第一个（最高优先级）
        else:
            action = actions[action_index]

        result = {
            "execution_time": datetime.now().isoformat(),
            "action": action,
            "status": "applied",
            "message": f"已应用预防性措施: {action.get('description', '')}"
        }

        # 更新预防措施历史
        preventive_history = {}
        if self.preventive_actions_file.exists():
            with open(self.preventive_actions_file, 'r', encoding='utf-8') as f:
                preventive_history = json.load(f)

        preventive_history["total_applied"] = preventive_history.get("total_applied", 0) + 1
        if "applied_actions" not in preventive_history:
            preventive_history["applied_actions"] = []
        preventive_history["applied_actions"].append({
            "time": datetime.now().isoformat(),
            "action": action
        })

        with open(self.preventive_actions_file, 'w', encoding='utf-8') as f:
            json.dump(preventive_history, f, ensure_ascii=False, indent=2)

        print(f"[进化效能预测] 预防性优化已执行: {action.get('description', '')}")

        return result

    def get_cockpit_data(self) -> Dict[str, Any]:
        """获取驾驶舱展示数据"""
        print("[进化效能预测] 生成驾驶舱数据...")

        # 收集数据
        trends = self.analyze_trends()
        prediction = self.predict_future()

        # 读取预防措施
        preventive_data = {}
        if self.preventive_actions_file.exists():
            with open(self.preventive_actions_file, 'r', encoding='utf-8') as f:
                preventive_data = json.load(f)

        cockpit_data = {
            "engine": self.name,
            "version": self.version,
            "generation_time": datetime.now().isoformat(),
            "trends": trends.get("metrics", {}),
            "predictions": prediction.get("predictions", {}),
            "risk_assessment": prediction.get("risk_assessment", {}),
            "preventive_actions_generated": preventive_data.get("total_generated", 0),
            "preventive_actions_applied": preventive_data.get("total_applied", 0)
        }

        print("[进化效能预测] 驾驶舱数据生成完成")
        return cockpit_data

    def run_full_analysis(self) -> Dict[str, Any]:
        """运行完整分析"""
        print("="*60)
        print("[进化效能预测与预防性优化引擎] 开始运行...")
        print("="*60)

        result = {
            "engine": self.name,
            "version": self.version,
            "execution_time": datetime.now().isoformat(),
            "steps": {}
        }

        # 步骤1: 收集历史数据
        print("\n[步骤1] 收集历史数据...")
        historical = self.collect_historical_data()
        result["steps"]["data_collection"] = {"status": "completed", "rounds": len(historical)}

        # 步骤2: 分析趋势
        print("\n[步骤2] 分析效能趋势...")
        trends = self.analyze_trends()
        result["steps"]["trend_analysis"] = {"status": "completed", "metrics_analyzed": len(trends.get("metrics", {}))}

        # 步骤3: 预测未来
        print("\n[步骤3] 预测未来效能...")
        prediction = self.predict_future()
        result["steps"]["prediction"] = {"status": "completed", "predictions_made": len(prediction.get("predictions", {}))}

        # 步骤4: 生成预防措施
        print("\n[步骤4] 生成预防性措施...")
        actions = self.generate_preventive_actions()
        result["steps"]["preventive_actions"] = {"status": "completed", "actions_generated": len(actions)}

        print("\n" + "="*60)
        print("[进化效能预测与预防性优化引擎] 分析完成!")
        print("="*60)

        return result


def main():
    """主函数 - 命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(
        description="智能全场景进化环进化效能预测与预防性优化引擎"
    )
    parser.add_argument("--status", action="store_true", help="查看引擎状态")
    parser.add_argument("--collect", action="store_true", help="收集历史数据")
    parser.add_argument("--trends", action="store_true", help="分析效能趋势")
    parser.add_argument("--predict", action="store_true", help="预测未来效能")
    parser.add_argument("--prevent", action="store_true", help="生成预防性措施")
    parser.add_argument("--apply", action="store_true", help="执行预防性优化")
    parser.add_argument("--run", action="store_true", help="运行完整分析")
    parser.add_argument("--cockpit-data", action="store_true", help="获取驾驶舱数据")

    args = parser.parse_args()

    engine = EvolutionEffectivenessPredictionPreventionEngine()

    if args.status:
        config = engine._load_config()
        print(f"引擎版本: {engine.version}")
        print(f"预测启用: {config.get('prediction_enabled', True)}")
        print(f"预防性优化: {config.get('preventive_optimization', {}).get('enabled', True)}")
        print(f"预测范围: {config.get('prediction', {}).get('horizon_rounds', 5)} 轮")
        print(f"风险阈值: {config.get('preventive_optimization', {}).get('risk_threshold', 0.3):.1%}")

    elif args.collect:
        result = engine.collect_historical_data()
        print(f"\n收集到 {len(result)} 轮历史数据")

    elif args.trends:
        result = engine.analyze_trends()
        if result.get("status") == "insufficient_data":
            print(f"\n数据不足: {result.get('available_rounds')} / {result.get('required_rounds')}")
        else:
            print(f"\n趋势分析完成:")
            for metric, info in result.get("metrics", {}).items():
                print(f"  - {metric}: {info.get('direction', 'unknown')}")

    elif args.predict:
        result = engine.predict_future()
        if result.get("status") == "insufficient_data":
            print("\n数据不足，无法预测")
        else:
            print(f"\n整体风险: {result.get('risk_assessment', {}).get('risk_level', 'unknown')} "
                  f"({result.get('risk_assessment', {}).get('overall_risk', 0):.1%})")
            print(f"建议: {result.get('risk_assessment', {}).get('recommendation', '')}")

    elif args.prevent:
        actions = engine.generate_preventive_actions()
        print(f"\n生成了 {len(actions)} 项预防措施")

    elif args.apply:
        result = engine.apply_preventive_optimization()
        print(f"\n执行结果: {result.get('message', '')}")

    elif args.run:
        result = engine.run_full_analysis()
        print(f"\n执行结果:")
        print(f"  - 数据收集: {result['steps']['data_collection']['rounds']} 轮")
        print(f"  - 趋势分析: {result['steps']['trend_analysis']['metrics_analyzed']} 个指标")
        print(f"  - 预测: {result['steps']['prediction']['predictions_made']} 个指标")
        print(f"  - 预防措施: {result['steps']['preventive_actions']['actions_generated']} 项")

    elif args.cockpit_data:
        data = engine.get_cockpit_data()
        print(json.dumps(data, ensure_ascii=False, indent=2))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()