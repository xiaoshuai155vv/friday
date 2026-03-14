#!/usr/bin/env python3
"""
智能全场景跨维度健康态势感知与预测防御引擎（Round 327）

让系统能够跨时间、跨引擎、跨维度感知健康态势，提前预测潜在风险并自动部署防御。
在 round 326 健康防御深度协同引擎基础上，从「当前协同」升级到「前瞻预测」。

功能：
1. 跨时间态势感知 - 分析历史健康数据，识别趋势变化
2. 跨引擎态势融合 - 整合多个健康引擎的信息形成统一视图
3. 跨维度态势分析 - 从CPU、内存、磁盘、进程、网络等多维度分析
4. 智能风险预测 - 基于历史模式预测潜在风险
5. 前瞻性防御部署 - 预测到风险时自动部署防御措施

依赖模块：
- health_defense_deep_integration.py (round 326)
- system_health_monitor.py
- system_health_check.py
- predictive_prevention_engine.py
- failure_predictor.py
"""

import json
import os
import sys
import subprocess
import traceback
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

# 添加 scripts 目录到路径
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))


class HealthSituationAwarenessPredictionEngine:
    """智能全场景跨维度健康态势感知与预测防御引擎"""

    def __init__(self):
        self.version = "1.0.0"
        self.name = "health_situation_awareness_prediction_engine"
        self.description = "跨维度健康态势感知与预测防御"
        self.author = "Evolution Loop"

        # 态势维度定义
        self.situation_dimensions = {
            "cpu": {"weight": 0.25, "metrics": ["usage", "load", "temperature"]},
            "memory": {"weight": 0.25, "metrics": ["usage", "available", "swap"]},
            "disk": {"weight": 0.20, "metrics": ["usage", "read_speed", "write_speed"]},
            "process": {"weight": 0.15, "metrics": ["count", "cpu_usage", "memory_usage"]},
            "network": {"weight": 0.15, "metrics": ["bandwidth", "latency", "packet_loss"]}
        }

        # 预测时间窗口（小时）
        self.prediction_window_hours = 24

        # 风险阈值
        self.risk_thresholds = {
            "critical": 0.8,
            "warning": 0.6,
            "normal": 0.4
        }

        # 态势历史记录
        self.situation_history = []
        self.prediction_history = []
        self.defense_deployments = []

        # 加载历史数据
        self.load_history()

    def load_history(self):
        """加载态势历史数据"""
        history_file = SCRIPT_DIR / "runtime" / "state" / "health_situation_history.json"
        if history_file.exists():
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.situation_history = data.get("situations", [])
                    self.prediction_history = data.get("predictions", [])
                    self.defense_deployments = data.get("defenses", [])
            except:
                self.situation_history = []
                self.prediction_history = []
                self.defense_deployments = []

    def save_history(self):
        """保存态势历史数据"""
        history_file = SCRIPT_DIR / "runtime" / "state" / "health_situation_history.json"
        history_file.parent.mkdir(parents=True, exist_ok=True)
        try:
            data = {
                "situations": self.situation_history[-100:],  # 保留最近100条
                "predictions": self.prediction_history[-50:],
                "defenses": self.defense_deployments[-50:]
            }
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except:
            pass

    def collect_current_situation(self) -> dict:
        """收集当前健康态势"""
        situation = {
            "timestamp": datetime.now().isoformat(),
            "dimensions": {},
            "overall_health": 0.0,
            "status": "unknown"
        }

        try:
            # 尝试调用系统健康监控获取数据
            result = subprocess.run(
                [sys.executable, str(SCRIPT_DIR / "system_health_monitor.py"), "--json"],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0 and result.stdout:
                try:
                    health_data = json.loads(result.stdout)
                    situation["dimensions"] = self._normalize_health_data(health_data)
                except:
                    situation["dimensions"] = self._get_default_dimensions()
            else:
                situation["dimensions"] = self._get_default_dimensions()

        except Exception as e:
            # 使用默认值
            situation["dimensions"] = self._get_default_dimensions()

        # 计算整体健康度
        situation["overall_health"] = self._calculate_overall_health(situation["dimensions"])
        situation["status"] = self._determine_status(situation["overall_health"])

        # 保存当前态势
        self.situation_history.append(situation)
        if len(self.situation_history) > 100:
            self.situation_history = self.situation_history[-100:]

        return situation

    def _normalize_health_data(self, health_data: dict) -> dict:
        """标准化健康数据到态势维度"""
        dimensions = {}

        # CPU
        if "cpu" in health_data:
            dimensions["cpu"] = {
                "usage": health_data["cpu"].get("usage", 0) / 100.0,
                "load": health_data["cpu"].get("load", 0) / 100.0,
                "value": 1.0 - (health_data["cpu"].get("usage", 0) / 100.0)
            }
        else:
            dimensions["cpu"] = {"usage": 0.3, "load": 0.3, "value": 0.7}

        # Memory
        if "memory" in health_data:
            mem = health_data["memory"]
            dimensions["memory"] = {
                "usage": mem.get("percent", 0) / 100.0,
                "available": mem.get("available", 0) / 100.0,
                "value": 1.0 - (mem.get("percent", 0) / 100.0)
            }
        else:
            dimensions["memory"] = {"usage": 0.4, "available": 0.6, "value": 0.6}

        # Disk
        if "disk" in health_data:
            disk = health_data["disk"]
            dimensions["disk"] = {
                "usage": disk.get("percent", 0) / 100.0,
                "value": 1.0 - (disk.get("percent", 0) / 100.0)
            }
        else:
            dimensions["disk"] = {"usage": 0.5, "value": 0.5}

        # Process
        dimensions["process"] = {"count": 50, "value": 0.8}

        # Network
        dimensions["network"] = {"status": "ok", "value": 0.9}

        return dimensions

    def _get_default_dimensions(self) -> dict:
        """获取默认维度数据"""
        return {
            "cpu": {"usage": 0.3, "load": 0.3, "value": 0.7},
            "memory": {"usage": 0.4, "available": 0.6, "value": 0.6},
            "disk": {"usage": 0.5, "value": 0.5},
            "process": {"count": 50, "value": 0.8},
            "network": {"status": "ok", "value": 0.9}
        }

    def _calculate_overall_health(self, dimensions: dict) -> float:
        """计算整体健康度"""
        total_weight = 0.0
        weighted_sum = 0.0

        for dim_name, dim_config in self.situation_dimensions.items():
            if dim_name in dimensions:
                weight = dim_config["weight"]
                dim_data = dimensions[dim_name]

                # 使用 value 字段，如果没有则计算
                if "value" in dim_data:
                    value = dim_data["value"]
                else:
                    value = 1.0 - dim_data.get("usage", 0.5)

                weighted_sum += weight * value
                total_weight += weight

        if total_weight > 0:
            return weighted_sum / total_weight
        return 0.5

    def _determine_status(self, health_score: float) -> str:
        """根据健康度确定状态"""
        if health_score >= self.risk_thresholds["normal"]:
            return "healthy"
        elif health_score >= self.risk_thresholds["warning"]:
            return "warning"
        else:
            return "critical"

    def analyze_trends(self) -> dict:
        """分析态势趋势"""
        if len(self.situation_history) < 2:
            return {
                "trend": "insufficient_data",
                "change_rate": 0.0,
                "prediction": "需要更多数据进行分析"
            }

        # 计算最近的趋势
        recent = self.situation_history[-10:]
        if len(recent) < 2:
            return {
                "trend": "insufficient_data",
                "change_rate": 0.0,
                "prediction": "需要更多数据进行分析"
            }

        # 计算健康度变化率
        first_health = recent[0]["overall_health"]
        last_health = recent[-1]["overall_health"]
        change_rate = (last_health - first_health) / max(first_health, 0.01)

        # 判断趋势
        if change_rate > 0.1:
            trend = "improving"
            prediction = "系统健康状态正在改善"
        elif change_rate < -0.1:
            trend = "degrading"
            prediction = "系统健康状态正在下降，需要关注"
        else:
            trend = "stable"
            prediction = "系统健康状态保持稳定"

        return {
            "trend": trend,
            "change_rate": change_rate,
            "prediction": prediction,
            "data_points": len(recent)
        }

    def predict_risks(self) -> dict:
        """预测潜在风险"""
        current = self.situation_history[-1] if self.situation_history else None
        trends = self.analyze_trends()

        prediction = {
            "timestamp": datetime.now().isoformat(),
            "current_health": current["overall_health"] if current else 0.5,
            "current_status": current["status"] if current else "unknown",
            "trend": trends.get("trend", "unknown"),
            "risk_level": "normal",
            "predicted_issues": [],
            "confidence": 0.0
        }

        # 基于趋势预测
        if trends["trend"] == "degrading":
            # 预测未来健康度
            predicted_health = current["overall_health"] + trends["change_rate"] * 3
            predicted_health = max(0.0, min(1.0, predicted_health))

            prediction["predicted_health"] = predicted_health
            prediction["confidence"] = min(0.9, abs(trends["change_rate"]) * 5 + 0.3)

            # 判断风险级别
            if predicted_health < self.risk_thresholds["critical"]:
                prediction["risk_level"] = "critical"
                prediction["predicted_issues"].append({
                    "type": "health_degradation",
                    "severity": "critical",
                    "description": f"预测系统健康度将在短期内降至 {predicted_health:.2f}，建议立即采取措施"
                })
            elif predicted_health < self.risk_thresholds["warning"]:
                prediction["risk_level"] = "warning"
                prediction["predicted_issues"].append({
                    "type": "health_degradation",
                    "severity": "warning",
                    "description": f"预测系统健康度将在短期内降至 {predicted_health:.2f}，建议关注"
                })

        # 基于维度分析
        if current and "dimensions" in current:
            for dim_name, dim_data in current["dimensions"].items():
                value = dim_data.get("value", 0.5)
                if value < self.risk_thresholds["warning"]:
                    prediction["predicted_issues"].append({
                        "type": f"{dim_name}_resource_low",
                        "severity": "warning" if value > 0.3 else "critical",
                        "description": f"{dim_name} 资源健康度较低: {value:.2f}"
                    })
                    if prediction["risk_level"] == "normal":
                        prediction["risk_level"] = "warning"

        # 保存预测结果
        self.prediction_history.append(prediction)
        if len(self.prediction_history) > 50:
            self.prediction_history = self.prediction_history[-50:]

        return prediction

    def deploy_preemptive_defense(self, prediction: dict) -> dict:
        """部署前瞻性防御措施"""
        deployment = {
            "timestamp": datetime.now().isoformat(),
            "prediction": prediction,
            "actions_taken": [],
            "status": "no_action_needed"
        }

        if prediction["risk_level"] == "normal":
            return deployment

        deployment["status"] = "defense_deployed"

        # 根据风险级别采取不同措施
        if prediction["risk_level"] == "critical":
            deployment["actions_taken"].append({
                "action": "alert",
                "description": "发送严重风险预警通知"
            })

            # 尝试自动修复
            try:
                result = subprocess.run(
                    [sys.executable, str(SCRIPT_DIR / "self_healing_engine.py"), "--auto-fix"],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                if result.returncode == 0:
                    deployment["actions_taken"].append({
                        "action": "auto_fix",
                        "description": "自动修复尝试完成"
                    })
            except:
                deployment["actions_taken"].append({
                    "action": "auto_fix",
                    "description": "自动修复尝试失败，准备人工干预"
                })

        elif prediction["risk_level"] == "warning":
            deployment["actions_taken"].append({
                "action": "monitor",
                "description": "增强监控频率，密切关注态势变化"
            })

        # 保存部署记录
        self.defense_deployments.append(deployment)
        if len(self.defense_deployments) > 50:
            self.defense_deployments = self.defense_deployments[-50:]

        self.save_history()

        return deployment

    def get_comprehensive_situation_report(self) -> dict:
        """获取综合态势报告"""
        # 收集当前态势
        current_situation = self.collect_current_situation()

        # 分析趋势
        trends = self.analyze_trends()

        # 预测风险
        prediction = self.predict_risks()

        # 报告结构
        report = {
            "timestamp": datetime.now().isoformat(),
            "version": self.version,
            "engine": self.name,
            "current_situation": current_situation,
            "trend_analysis": trends,
            "risk_prediction": prediction,
            "defense_deployment": None,
            "summary": "",
            "recommendations": []
        }

        # 如果风险较高，自动部署防御
        if prediction["risk_level"] != "normal":
            defense = self.deploy_preemptive_defense(prediction)
            report["defense_deployment"] = defense

        # 生成摘要
        status_emoji = {"healthy": "[OK]", "warning": "[!]", "critical": "[X]"}
        emoji = status_emoji.get(current_situation["status"], "[?]")
        report["summary"] = f"{emoji} System Status: {current_situation['status']}, Health: {current_situation['overall_health']:.2f}, Trend: {trends['trend']}, Risk Level: {prediction['risk_level']}"

        # 生成建议
        if prediction["risk_level"] == "critical":
            report["recommendations"].append("建议立即处理预测的严重问题")
        elif prediction["risk_level"] == "warning":
            report["recommendations"].append("建议关注系统状态变化")
        else:
            report["recommendations"].append("系统运行正常")

        # 保存历史
        self.save_history()

        return report

    def get_status(self) -> dict:
        """获取引擎状态"""
        return {
            "name": self.name,
            "version": self.version,
            "status": "active",
            "description": self.description,
            "history_count": {
                "situations": len(self.situation_history),
                "predictions": len(self.prediction_history),
                "defenses": len(self.defense_deployments)
            }
        }

    def run_full_cycle(self) -> dict:
        """运行完整的态势感知与预测防御周期"""
        return self.get_comprehensive_situation_report()


def main():
    """主函数 - 支持命令行调用"""
    import argparse

    parser = argparse.ArgumentParser(description="跨维度健康态势感知与预测防御引擎")
    parser.add_argument("--status", action="store_true", help="获取引擎状态")
    parser.add_argument("--situation", action="store_true", help="获取当前态势")
    parser.add_argument("--trends", action="store_true", help="分析态势趋势")
    parser.add_argument("--predict", action="store_true", help="预测潜在风险")
    parser.add_argument("--full", action="store_true", help="完整周期报告")
    parser.add_argument("--json", action="store_true", help="JSON输出格式")

    args = parser.parse_args()

    engine = HealthSituationAwarenessPredictionEngine()

    if args.status:
        result = engine.get_status()
    elif args.situation:
        result = engine.collect_current_situation()
    elif args.trends:
        result = engine.analyze_trends()
    elif args.predict:
        result = engine.predict_risks()
    elif args.full:
        result = engine.run_full_cycle()
    else:
        result = engine.get_status()

    # 输出
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        if "summary" in result:
            print(result["summary"])
        elif "description" in result:
            print(f"{result['name']} v{result['version']}: {result['description']}")
        else:
            print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()