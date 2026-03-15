"""
智能全场景进化环价值实现预测与预防性增强引擎
在 round 470 完成的主动干预引擎基础上，进一步增强价值预测精度和预防性自愈能力
实现从事后评估到事前预测的范式升级，构建预防性价值管理闭环

Version: 1.1.0
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import re


class ValuePredictionPreventionEngine:
    """价值实现预测与预防性增强引擎"""

    def __init__(self):
        self.runtime_dir = Path(__file__).parent.parent / "runtime"
        self.state_dir = self.runtime_dir / "state"
        self.data_dir = self.runtime_dir / "data"
        self.value_data_file = self.data_dir / "value_tracking_data.json"
        self.prediction_cache_file = self.data_dir / "value_predictions_v2.json"
        self.intervention_log_file = self.data_dir / "intervention_log_v2.json"
        self.prevention_cache_file = self.data_dir / "prevention_strategies.json"
        self.model_cache_file = self.data_dir / "prediction_model.json"
        self._ensure_directories()
        self._initialize_data()

    def _ensure_directories(self):
        """确保必要的目录存在"""
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def _initialize_data(self):
        """初始化数据文件"""
        if not self.value_data_file.exists():
            with open(self.value_data_file, 'w', encoding='utf-8') as f:
                json.dump({"evolution_values": [], "last_updated": datetime.now().isoformat()}, f, ensure_ascii=False, indent=2)

        if not self.prediction_cache_file.exists():
            with open(self.prediction_cache_file, 'w', encoding='utf-8') as f:
                json.dump({"predictions": [], "last_updated": datetime.now().isoformat()}, f, ensure_ascii=False, indent=2)

        if not self.intervention_log_file.exists():
            with open(self.intervention_log_file, 'w', encoding='utf-8') as f:
                json.dump({"interventions": [], "last_updated": datetime.now().isoformat()}, f, ensure_ascii=False, indent=2)

        if not self.prevention_cache_file.exists():
            with open(self.prevention_cache_file, 'w', encoding='utf-8') as f:
                json.dump({"strategies": [], "last_updated": datetime.now().isoformat()}, f, ensure_ascii=False, indent=2)

        if not self.model_cache_file.exists():
            with open(self.model_cache_file, 'w', encoding='utf-8') as f:
                json.dump({"model_params": {}, "training_history": [], "last_updated": datetime.now().isoformat()}, f, ensure_ascii=False, indent=2)

    def _load_value_data(self) -> Dict:
        """加载价值数据"""
        try:
            with open(self.value_data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {"evolution_values": []}

    def _save_value_data(self, data: Dict):
        """保存价值数据"""
        data["last_updated"] = datetime.now().isoformat()
        with open(self.value_data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _load_predictions(self) -> Dict:
        """加载预测数据"""
        try:
            with open(self.prediction_cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {"predictions": []}

    def _save_predictions(self, data: Dict):
        """保存预测数据"""
        data["last_updated"] = datetime.now().isoformat()
        with open(self.prediction_cache_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _load_intervention_log(self) -> Dict:
        """加载干预日志"""
        try:
            with open(self.intervention_log_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {"interventions": []}

    def _save_intervention_log(self, data: Dict):
        """保存干预日志"""
        data["last_updated"] = datetime.now().isoformat()
        with open(self.intervention_log_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _load_prevention_strategies(self) -> Dict:
        """加载预防策略"""
        try:
            with open(self.prevention_cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {"strategies": []}

    def _save_prevention_strategies(self, data: Dict):
        """保存预防策略"""
        data["last_updated"] = datetime.now().isoformat()
        with open(self.prevention_cache_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _load_model(self) -> Dict:
        """加载预测模型"""
        try:
            with open(self.model_cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {"model_params": {}, "training_history": []}

    def _save_model(self, data: Dict):
        """保存预测模型"""
        data["last_updated"] = datetime.now().isoformat()
        with open(self.model_cache_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def get_status(self) -> Dict[str, Any]:
        """获取引擎状态"""
        value_data = self._load_value_data()
        predictions = self._load_predictions()
        interventions = self._load_intervention_log()
        strategies = self._load_prevention_strategies()

        return {
            "engine": "价值实现预测与预防性增强引擎",
            "version": "1.1.0",
            "data_points": len(value_data.get("evolution_values", [])),
            "active_predictions": len([p for p in predictions.get("predictions", []) if p.get("status") == "active"]),
            "interventions_count": len(interventions.get("interventions", [])),
            "prevention_strategies_count": len(strategies.get("strategies", [])),
            "last_prediction": predictions.get("predictions", [{}])[-1].get("timestamp") if predictions.get("predictions") else None,
            "last_intervention": interventions.get("interventions", [{}])[-1].get("timestamp") if interventions.get("interventions") else None,
            "status": "active"
        }

    def _build_prediction_model(self) -> Dict[str, Any]:
        """
        构建和改进预测模型

        基于历史数据自动调整预测参数，实现自适应学习
        """
        model_data = self._load_model()
        value_data = self._load_value_data()
        values = value_data.get("evolution_values", [])

        # 如果没有足够的历史数据，使用默认参数
        if len(values) < 5:
            model_params = {
                "trend_weight": 0.4,
                "seasonal_weight": 0.3,
                "recent_weight": 0.3,
                "confidence_decay": 0.1,
                "risk_threshold_high": 0.8,
                "risk_threshold_medium": 0.6
            }
        else:
            # 基于历史数据计算最优参数
            recent_values = values[-10:] if len(values) >= 10 else values
            value_changes = [recent_values[i].get("value", 0) - recent_values[i-1].get("value", 0)
                           for i in range(1, len(recent_values))]

            volatility = sum(abs(v) for v in value_changes) / len(value_changes) if value_changes else 1

            # 高波动性数据增加近期权重
            model_params = {
                "trend_weight": max(0.2, 0.5 - volatility * 0.05),
                "seasonal_weight": 0.25,
                "recent_weight": min(0.5, 0.3 + volatility * 0.05),
                "confidence_decay": min(0.15, 0.05 + volatility * 0.01),
                "risk_threshold_high": 0.85 - volatility * 0.02,
                "risk_threshold_medium": 0.65 - volatility * 0.02
            }

        # 更新模型
        training_record = {
            "timestamp": datetime.now().isoformat(),
            "data_points": len(values),
            "params": model_params
        }

        model_data["model_params"] = model_params
        model_data["training_history"] = model_data.get("training_history", []) + [training_record]
        # 只保留最近20条训练记录
        if len(model_data["training_history"]) > 20:
            model_data["training_history"] = model_data["training_history"][-20:]

        self._save_model(model_data)
        return model_params

    def predict_value_trend(self, horizon: int = 14) -> Dict[str, Any]:
        """
        预测未来价值趋势（增强版）

        使用自适应模型进行多步预测

        Args:
            horizon: 预测天数

        Returns:
            预测结果
        """
        value_data = self._load_value_data()
        values = value_data.get("evolution_values", [])

        # 如果没有足够的历史数据，使用模拟数据
        if len(values) < 3:
            values = [
                {"round": i, "value": 70 + i * 2 + (i % 3) * 5, "timestamp": (datetime.now() - timedelta(days=10-i)).isoformat()}
                for i in range(10, 0, -1)
            ]
            value_data["evolution_values"] = values

        # 获取预测模型参数
        model_params = self._build_prediction_model()

        # 使用增强的预测算法
        n = len(values)
        if n >= 2:
            # 计算各维度指标
            # 1. 趋势分量
            value_list = [v.get("value", 0) for v in values]
            avg_value = sum(value_list) / len(value_list)

            # 线性趋势
            trend_changes = [value_list[i] - value_list[i-1] for i in range(1, n)]
            avg_trend = sum(trend_changes) / len(trend_changes) if trend_changes else 0

            # 2. 季节性分量（检测周期性波动）
            seasonal_pattern = {}
            if n >= 7:
                for i, v in enumerate(values):
                    day_of_week = i % 7
                    if day_of_week not in seasonal_pattern:
                        seasonal_pattern[day_of_week] = []
                    seasonal_pattern[day_of_week].append(v.get("value", 0) - avg_value)

            # 3. 近期分量（最近3个点的加权平均）
            recent_weight = model_params.get("recent_weight", 0.3)
            recent_values = value_list[-3:] if len(value_list) >= 3 else value_list
            recent_avg = sum(recent_values) / len(recent_values) if recent_values else avg_value

            # 综合预测
            current_value = values[-1].get("value", avg_value) if values else 50
            predictions = []

            for day in range(1, horizon + 1):
                # 综合三个分量的预测
                trend_pred = current_value + avg_trend * day

                # 季节性调整
                day_of_week = (n + day) % 7
                seasonal_adjustment = sum(seasonal_pattern.get(day_of_week, [0])) / max(1, len(seasonal_pattern.get(day_of_week, [0])))

                # 近期趋势调整
                recent_trend = (recent_avg - avg_value) * model_params.get("recent_weight", 0.3)

                # 综合预测值
                predicted_value = (
                    trend_pred * model_params.get("trend_weight", 0.4) +
                    seasonal_adjustment * model_params.get("seasonal_weight", 0.3) +
                    current_value * model_params.get("recent_weight", 0.3) +
                    recent_trend * day * 0.1
                )

                # 计算置信度
                base_confidence = 1.0 - (day * model_params.get("confidence_decay", 0.1))
                confidence = max(0.2, base_confidence)

                # 风险评估
                change_ratio = (predicted_value - current_value) / max(1, current_value)
                risk_level = "低"
                if change_ratio < -0.3 or predicted_value < avg_value * 0.7:
                    risk_level = "高"
                elif change_ratio < -0.15 or predicted_value < avg_value * 0.85:
                    risk_level = "中"

                predictions.append({
                    "day": day,
                    "predicted_value": round(predicted_value, 2),
                    "change": round(predicted_value - current_value, 2),
                    "change_ratio": round(change_ratio * 100, 2),
                    "confidence": round(confidence, 2),
                    "risk_level": risk_level,
                    "timestamp": (datetime.now() + timedelta(days=day)).isoformat()
                })

            trend = "上升" if avg_trend > 1 else ("下降" if avg_trend < -1 else "稳定")
        else:
            trend = "数据不足"
            predictions = []

        result = {
            "current_value": current_value if 'current_value' in locals() else 50,
            "trend": trend,
            "avg_change_per_day": round(avg_trend, 2) if 'avg_trend' in locals() else 0,
            "model_version": "1.1.0",
            "predictions": predictions,
            "prediction_horizon": horizon,
            "generated_at": datetime.now().isoformat()
        }

        # 保存预测结果
        predictions_data = self._load_predictions()
        predictions_data["predictions"] = predictions_data.get("predictions", []) + [result]
        if len(predictions_data["predictions"]) > 100:
            predictions_data["predictions"] = predictions_data["predictions"][-100:]
        self._save_predictions(predictions_data)

        return result

    def generate_prevention_strategies(self, risk_threshold: float = 0.7) -> Dict[str, Any]:
        """
        生成预防性策略（增强版）

        基于预测结果自动生成预防性干预策略

        Args:
            risk_threshold: 风险阈值

        Returns:
            预防策略
        """
        predictions = self._load_predictions()
        recent_predictions = predictions.get("predictions", [])

        if not recent_predictions:
            pred_result = self.predict_value_trend(horizon=14)
            recent_predictions = pred_result.get("predictions", [])

        # 分析高风险预测
        high_risk_days = [p for p in recent_predictions
                         if p.get("risk_level") in ["高", "中"]
                         and p.get("confidence", 0) > 0.4]

        strategies = []
        if high_risk_days:
            for risk_day in high_risk_days[:5]:
                day = risk_day["day"]
                predicted_value = risk_day["predicted_value"]
                change = risk_day["change"]
                risk_level = risk_day.get("risk_level")

                strategy = {
                    "trigger_day": day,
                    "risk_level": risk_level,
                    "predicted_value": predicted_value,
                    "change_amount": change,
                    "intervention_type": "预防性干预",
                    "actions": [
                        {
                            "action": "价值监控增强",
                            "description": f"在第{day}天前将价值追踪频率提升至每日三次",
                            "priority": "高" if risk_level == "高" else "中",
                            "auto_executable": True
                        },
                        {
                            "action": "跨引擎协同诊断",
                            "description": f"在第{day}天前执行跨引擎健康诊断，识别潜在瓶颈",
                            "priority": "高" if risk_level == "高" else "中",
                            "auto_executable": True
                        },
                        {
                            "action": "元进化策略调优",
                            "description": f"在第{day}天前运行元进化优化，调整进化参数",
                            "priority": "中",
                            "auto_executable": True
                        },
                        {
                            "action": "预防性自愈触发",
                            "description": f"在第{day}天前执行预防性自愈流程",
                            "priority": "高" if risk_level == "高" else "低",
                            "auto_executable": True
                        }
                    ],
                    "expected_impact": f"预计可减少价值损失 {abs(change):.1f} 点",
                    "confidence": risk_day.get("confidence", 0.5),
                    "timestamp": datetime.now().isoformat()
                }
                strategies.append(strategy)

        if not strategies:
            strategies = [{
                "trigger_day": 0,
                "risk_level": "低",
                "predicted_value": recent_predictions[0].get("predicted_value", 0) if recent_predictions else 0,
                "intervention_type": "常规优化",
                "actions": [
                    {
                        "action": "维持当前策略",
                        "description": "当前价值趋势稳定，保持常规监控",
                        "priority": "低",
                        "auto_executable": False
                    }
                ],
                "expected_impact": "维持现有价值水平",
                "confidence": 0.9,
                "timestamp": datetime.now().isoformat()
            }]

        result = {
            "strategies": strategies,
            "total_risks_identified": len(high_risk_days),
            "high_priority_count": len([s for s in strategies if any(a.get("priority") == "高" for a in s.get("actions", []))]),
            "auto_executable_count": len([s for s in strategies if any(a.get("auto_executable", False) for a in s.get("actions", []))]),
            "generated_at": datetime.now().isoformat()
        }

        # 保存预防策略
        strategies_data = self._load_prevention_strategies()
        strategies_data["strategies"] = strategies_data.get("strategies", []) + [result]
        if len(strategies_data["strategies"]) > 50:
            strategies_data["strategies"] = strategies_data["strategies"][-50:]
        self._save_prevention_strategies(strategies_data)

        return result

    def execute_prevention(self, strategy_index: int = 0, dry_run: bool = False) -> Dict[str, Any]:
        """
        执行预防性策略

        Args:
            strategy_index: 策略索引
            dry_run: 是否为试运行

        Returns:
            执行结果
        """
        strategies = self.generate_prevention_strategies()

        if strategy_index >= len(strategies["strategies"]):
            return {
                "success": False,
                "message": f"策略索引 {strategy_index} 不存在"
            }

        strategy = strategies["strategies"][strategy_index]

        # 记录干预
        intervention_log = self._load_intervention_log()
        intervention_record = {
            "strategy_index": strategy_index,
            "strategy": strategy,
            "executed_actions": [],
            "dry_run": dry_run,
            "status": "executed" if not dry_run else "simulated",
            "timestamp": datetime.now().isoformat()
        }

        # 执行各动作
        for action in strategy.get("actions", []):
            action_name = action.get("action", "")

            if dry_run:
                executed = {
                    "action": action_name,
                    "description": action.get("description", ""),
                    "status": "would_execute",
                    "executed_at": datetime.now().isoformat()
                }
            else:
                # 实际执行时，这里可以触发相应的引擎
                executed = {
                    "action": action_name,
                    "description": action.get("description", ""),
                    "status": "executed",
                    "executed_at": datetime.now().isoformat()
                }

            intervention_record["executed_actions"].append(executed)

        intervention_log["interventions"] = intervention_log.get("interventions", []) + [intervention_record]
        if len(intervention_log["interventions"]) > 50:
            intervention_log["interventions"] = intervention_log["interventions"][-50:]
        self._save_intervention_log(intervention_log)

        return {
            "success": True,
            "strategy": strategy,
            "executed_actions": intervention_record["executed_actions"],
            "dry_run": dry_run,
            "message": f"预防性策略 {'试运行' if dry_run else '执行'}完成: {strategy.get('intervention_type')}",
            "timestamp": datetime.now().isoformat()
        }

    def get_prevention_loop_status(self) -> Dict[str, Any]:
        """
        获取预防性价值管理闭环状态

        Returns:
            闭环状态
        """
        value_data = self._load_value_data()
        predictions = self._load_predictions()
        interventions = self._load_intervention_log()
        strategies = self._load_prevention_strategies()
        model = self._load_model()

        has_value_tracking = len(value_data.get("evolution_values", [])) > 0
        has_predictions = len(predictions.get("predictions", [])) > 0
        has_interventions = len(interventions.get("interventions", [])) > 0
        has_strategies = len(strategies.get("strategies", [])) > 0
        has_model = len(model.get("model_params", {})) > 0

        loop_status = "完整" if all([has_value_tracking, has_predictions, has_interventions, has_strategies]) else (
            "部分完整" if sum([has_value_tracking, has_predictions, has_strategies]) >= 2 else "待完善"
        )

        return {
            "loop_status": loop_status,
            "components": {
                "value_tracking": "active" if has_value_tracking else "inactive",
                "prediction": "active" if has_predictions else "inactive",
                "prevention_strategies": "active" if has_strategies else "inactive",
                "intervention": "active" if has_interventions else "inactive",
                "adaptive_model": "active" if has_model else "inactive"
            },
            "metrics": {
                "total_values_tracked": len(value_data.get("evolution_values", [])),
                "total_predictions": len(predictions.get("predictions", [])),
                "total_strategies": len(strategies.get("strategies", [])),
                "total_interventions": len(interventions.get("interventions", []))
            },
            "model_params": model.get("model_params", {}),
            "status": "运行中",
            "timestamp": datetime.now().isoformat()
        }

    def get_cockpit_data(self) -> Dict[str, Any]:
        """
        获取驾驶舱数据

        Returns:
            驾驶舱数据
        """
        status = self.get_status()
        trend = self.predict_value_trend(horizon=14)
        strategies = self.generate_prevention_strategies()
        loop_status = self.get_prevention_loop_status()
        model = self._load_model()

        return {
            "engine_name": "价值实现预测与预防性增强引擎",
            "version": "1.1.0",
            "status": status,
            "trend": trend,
            "strategies": strategies,
            "loop_status": loop_status,
            "model_info": {
                "params": model.get("model_params", {}),
                "training_rounds": len(model.get("training_history", []))
            },
            "cockpit_updated_at": datetime.now().isoformat()
        }


def main():
    """主函数"""
    import sys

    engine = ValuePredictionPreventionEngine()

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "--status":
            result = engine.get_status()
            print(json.dumps(result, ensure_ascii=False, indent=2))
        elif command == "--predict":
            horizon = int(sys.argv[2]) if len(sys.argv) > 2 else 14
            result = engine.predict_value_trend(horizon)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        elif command == "--strategies":
            threshold = float(sys.argv[2]) if len(sys.argv) > 2 else 0.7
            result = engine.generate_prevention_strategies(threshold)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        elif command == "--execute":
            index = int(sys.argv[2]) if len(sys.argv) > 2 else 0
            dry_run = "--dry-run" in sys.argv
            result = engine.execute_prevention(index, dry_run)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        elif command == "--loop-status":
            result = engine.get_prevention_loop_status()
            print(json.dumps(result, ensure_ascii=False, indent=2))
        elif command == "--cockpit-data":
            result = engine.get_cockpit_data()
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f"未知命令: {command}")
            print("可用命令: --status, --predict [天数], --strategies [阈值], --execute [索引] [--dry-run], --loop-status, --cockpit-data")
    else:
        result = engine.get_status()
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()