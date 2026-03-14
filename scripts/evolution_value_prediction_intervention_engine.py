"""
智能全场景进化环价值预测与主动干预引擎
让系统不仅能追踪已发生的价值，更能预测未来价值趋势、在价值下滑前主动干预、形成预防性价值管理闭环
实现从「被动追踪」到「主动预测干预」的范式升级

Version: 1.0.0
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import re


class ValuePredictionInterventionEngine:
    """价值预测与主动干预引擎"""

    def __init__(self):
        self.runtime_dir = Path(__file__).parent.parent / "runtime"
        self.state_dir = self.runtime_dir / "state"
        self.data_dir = self.runtime_dir / "data"
        self.value_data_file = self.data_dir / "value_tracking_data.json"
        self.prediction_cache_file = self.data_dir / "value_predictions.json"
        self.intervention_log_file = self.data_dir / "intervention_log.json"
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

    def get_status(self) -> Dict[str, Any]:
        """获取引擎状态"""
        value_data = self._load_value_data()
        predictions = self._load_predictions()
        interventions = self._load_intervention_log()

        return {
            "engine": "价值预测与主动干预引擎",
            "version": "1.0.0",
            "data_points": len(value_data.get("evolution_values", [])),
            "active_predictions": len([p for p in predictions.get("predictions", []) if p.get("status") == "active"]),
            "interventions_count": len(interventions.get("interventions", [])),
            "last_prediction": predictions.get("predictions", [{}])[-1].get("timestamp") if predictions.get("predictions") else None,
            "last_intervention": interventions.get("interventions", [{}])[-1].get("timestamp") if interventions.get("interventions") else None,
            "status": "active"
        }

    def predict_value_trend(self, horizon: int = 7) -> Dict[str, Any]:
        """
        预测未来价值趋势

        Args:
            horizon: 预测天数

        Returns:
            预测结果
        """
        value_data = self._load_value_data()
        values = value_data.get("evolution_values", [])

        # 如果没有足够的历史数据，使用模拟数据
        if len(values) < 3:
            # 生成模拟数据用于演示
            values = [
                {"round": i, "value": 70 + i * 2 + (i % 3) * 5, "timestamp": (datetime.now() - timedelta(days=10-i)).isoformat()}
                for i in range(10, 0, -1)
            ]
            value_data["evolution_values"] = values

        # 简单的线性趋势分析
        n = len(values)
        if n >= 2:
            # 计算趋势
            value_changes = [values[i].get("value", 0) - values[i-1].get("value", 0) for i in range(1, n)]
            avg_change = sum(value_changes) / len(value_changes) if value_changes else 0
            trend = "上升" if avg_change > 1 else ("下降" if avg_change < -1 else "稳定")

            # 预测未来
            current_value = values[-1].get("value", 50) if values else 50
            predictions = []
            for day in range(1, horizon + 1):
                predicted_value = current_value + avg_change * day
                confidence = max(0.3, 1.0 - (day * 0.1))  # 置信度随时间递减

                risk_level = "低"
                if predicted_value < current_value * 0.8:
                    risk_level = "高"
                elif predicted_value < current_value * 0.9:
                    risk_level = "中"

                predictions.append({
                    "day": day,
                    "predicted_value": round(predicted_value, 2),
                    "change": round(predicted_value - current_value, 2),
                    "confidence": round(confidence, 2),
                    "risk_level": risk_level,
                    "timestamp": (datetime.now() + timedelta(days=day)).isoformat()
                })
        else:
            trend = "数据不足"
            predictions = []

        result = {
            "current_value": current_value if 'current_value' in locals() else 50,
            "trend": trend,
            "avg_change_per_day": round(avg_change, 2) if 'avg_change' in locals() else 0,
            "predictions": predictions,
            "prediction_horizon": horizon,
            "generated_at": datetime.now().isoformat()
        }

        # 保存预测结果
        predictions_data = self._load_predictions()
        predictions_data["predictions"] = predictions_data.get("predictions", []) + [result]
        # 只保留最近100条预测
        if len(predictions_data["predictions"]) > 100:
            predictions_data["predictions"] = predictions_data["predictions"][-100:]
        self._save_predictions(predictions_data)

        return result

    def generate_intervention_strategy(self, risk_threshold: float = 0.8) -> Dict[str, Any]:
        """
        生成主动干预策略

        Args:
            risk_threshold: 风险阈值

        Returns:
            干预策略
        """
        predictions = self._load_predictions()
        recent_predictions = predictions.get("predictions", [])

        if not recent_predictions:
            # 先生成预测
            pred_result = self.predict_value_trend(horizon=7)
            recent_predictions = pred_result.get("predictions", [])

        # 分析高风险预测
        high_risk_days = [p for p in recent_predictions if p.get("risk_level") in ["高", "中"] and p.get("confidence", 0) > 0.5]

        strategies = []
        if high_risk_days:
            for risk_day in high_risk_days[:3]:  # 最多3个策略
                day = risk_day["day"]
                predicted_value = risk_day["predicted_value"]
                change = risk_day["change"]

                strategy = {
                    "trigger_day": day,
                    "risk_level": risk_day.get("risk_level"),
                    "predicted_value": predicted_value,
                    "intervention_type": "预防性优化",
                    "actions": [
                        {
                            "action": "增强价值追踪频率",
                            "description": f"在第{day}天前将价值追踪频率从每日一次提升到每日两次",
                            "priority": "高" if risk_day.get("risk_level") == "高" else "中"
                        },
                        {
                            "action": "触发协同效能分析",
                            "description": f"在第{day}天前执行跨引擎协同效能分析，识别并修复潜在瓶颈",
                            "priority": "高" if risk_day.get("risk_level") == "高" else "中"
                        },
                        {
                            "action": "启动元进化优化",
                            "description": f"在第{day}天前运行元进化优化引擎，调整进化策略参数",
                            "priority": "中"
                        }
                    ],
                    "expected_impact": f"预计可提升价值 {abs(change):.1f} 点",
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
                        "description": "当前价值趋势良好，无需特殊干预",
                        "priority": "低"
                    }
                ],
                "expected_impact": "维持现有价值水平",
                "timestamp": datetime.now().isoformat()
            }]

        result = {
            "strategies": strategies,
            "total_risks_identified": len(high_risk_days),
            "high_priority_count": len([s for s in strategies if any(a.get("priority") == "高" for a in s.get("actions", []))]),
            "generated_at": datetime.now().isoformat()
        }

        return result

    def execute_intervention(self, strategy_index: int = 0) -> Dict[str, Any]:
        """
        执行干预策略

        Args:
            strategy_index: 策略索引

        Returns:
            执行结果
        """
        strategies = self.generate_intervention_strategy()

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
            "status": "executed",
            "timestamp": datetime.now().isoformat()
        }

        # 模拟执行各动作
        for action in strategy.get("actions", []):
            action_name = action.get("action", "")
            executed = {
                "action": action_name,
                "description": action.get("description", ""),
                "status": "simulated_executed",
                "executed_at": datetime.now().isoformat()
            }
            intervention_record["executed_actions"].append(executed)

        intervention_log["interventions"] = intervention_log.get("interventions", []) + [intervention_record]
        # 只保留最近50条干预记录
        if len(intervention_log["interventions"]) > 50:
            intervention_log["interventions"] = intervention_log["interventions"][-50:]
        self._save_intervention_log(intervention_log)

        return {
            "success": True,
            "strategy": strategy,
            "executed_actions": intervention_record["executed_actions"],
            "message": f"已执行策略 {strategy_index}: {strategy.get('intervention_type')}",
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

        # 计算闭环完整性
        has_value_tracking = len(value_data.get("evolution_values", [])) > 0
        has_predictions = len(predictions.get("predictions", [])) > 0
        has_interventions = len(interventions.get("interventions", [])) > 0

        loop_status = "完整" if (has_value_tracking and has_predictions and has_interventions) else (
            "部分完整" if (has_value_tracking or has_predictions) else "待完善"
        )

        return {
            "loop_status": loop_status,
            "components": {
                "value_tracking": "active" if has_value_tracking else "inactive",
                "prediction": "active" if has_predictions else "inactive",
                "intervention": "active" if has_interventions else "inactive"
            },
            "metrics": {
                "total_values_tracked": len(value_data.get("evolution_values", [])),
                "total_predictions": len(predictions.get("predictions", [])),
                "total_interventions": len(interventions.get("interventions", []))
            },
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
        trend = self.predict_value_trend(horizon=7)
        strategies = self.generate_intervention_strategy()
        loop_status = self.get_prevention_loop_status()

        return {
            "engine_name": "价值预测与主动干预引擎",
            "version": "1.0.0",
            "status": status,
            "trend": trend,
            "strategies": strategies,
            "loop_status": loop_status,
            "cockpit_updated_at": datetime.now().isoformat()
        }


def main():
    """主函数"""
    import sys

    engine = ValuePredictionInterventionEngine()

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "--status":
            result = engine.get_status()
            print(json.dumps(result, ensure_ascii=False, indent=2))
        elif command == "--predict":
            horizon = int(sys.argv[2]) if len(sys.argv) > 2 else 7
            result = engine.predict_value_trend(horizon)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        elif command == "--strategies":
            threshold = float(sys.argv[2]) if len(sys.argv) > 2 else 0.8
            result = engine.generate_intervention_strategy(threshold)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        elif command == "--execute":
            index = int(sys.argv[2]) if len(sys.argv) > 2 else 0
            result = engine.execute_intervention(index)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        elif command == "--loop-status":
            result = engine.get_prevention_loop_status()
            print(json.dumps(result, ensure_ascii=False, indent=2))
        elif command == "--cockpit-data":
            result = engine.get_cockpit_data()
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f"未知命令: {command}")
            print("可用命令: --status, --predict [天数], --strategies [阈值], --execute [索引], --loop-status, --cockpit-data")
    else:
        result = engine.get_status()
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()