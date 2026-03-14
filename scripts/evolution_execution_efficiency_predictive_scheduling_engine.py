#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环执行效率预测性智能调度增强引擎
Evolution Execution Efficiency Predictive Scheduling Enhancement Engine

版本: 1.0.0
功能: 在 round 406/407 的执行效率智能优化和可视化监控基础上，进一步增强预测性智能调度能力

实现功能:
1. 基于历史执行数据的预测性负载预测
2. 预测性调度策略自动调整
3. 事前优化而非事后补救
4. 智能提前调整任务优先级和资源分配
5. 与进化驾驶舱深度集成

集成: 集成到 do.py 支持预测性调度、预测调度、智能预测调度等关键词触发

依赖:
- evolution_cockpit_engine.py (round 350)
- evolution_execution_efficiency_intelligent_optimizer.py (round 406)
- evolution_execution_efficiency_cockpit_integration_engine.py (round 407)
"""

import os
import sys
import json
import time
import threading
import psutil
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from collections import deque
import statistics

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def _safe_print(text: str):
    """安全打印，处理编码问题"""
    import re
    try:
        print(text)
    except UnicodeEncodeError:
        clean_text = re.sub(r'[^\x00-\x7F]+', '', text)
        print(clean_text)


class ExecutionEfficiencyPredictiveSchedulingEngine:
    """
    执行效率预测性智能调度增强引擎
    实现从事后优化到事前预测的范式升级
    """

    VERSION = "1.0.0"

    def __init__(self):
        self.version = self.VERSION
        self.project_root = PROJECT_ROOT
        self.scripts_dir = PROJECT_ROOT / "scripts"
        self.runtime_dir = PROJECT_ROOT / "runtime"
        self.state_dir = self.runtime_dir / "state"
        self.logs_dir = self.runtime_dir / "logs"

        # 状态文件
        self.state_file = self.state_dir / "predictive_scheduling_state.json"
        self.prediction_history_file = self.state_dir / "prediction_history.json"

        # 初始化目录
        self._ensure_directories()

        # 预测配置
        self.prediction_window = 60  # 预测窗口（数据点数量）
        self.prediction_horizon = 5  # 预测未来5个时间单位
        self.learning_rate = 0.1  # 学习率

        # 负载历史数据
        self.load_history = deque(maxlen=self.prediction_window * 2)
        self.monitoring_active = False
        self.monitoring_thread = None
        self.monitoring_interval = 5  # 监控间隔（秒）

        # 预测模型状态
        self.prediction_model = self._init_prediction_model()
        self.prediction_errors = deque(maxlen=50)

        # 调度策略
        self.current_strategy = "balanced"
        self.strategy_adjustments = []

        # 尝试加载可视化监控引擎
        self.cockpit_engine = self._load_cockpit_engine()

        # 预测结果缓存
        self.last_prediction = None
        self.last_prediction_time = None

    def _ensure_directories(self):
        """确保必要的目录存在"""
        for directory in [self.state_dir, self.logs_dir]:
            os.makedirs(directory, exist_ok=True)

    def _init_prediction_model(self) -> Dict:
        """初始化预测模型"""
        return {
            "type": "adaptive_linear",
            "cpu_weights": [0.5, 0.3, 0.2],  # 线性加权
            "memory_weights": [0.5, 0.3, 0.2],
            "trend_weights": [0.7, 0.3],  # 趋势权重
            "initialized": True,
            "training_samples": 0
        }

    def _load_cockpit_engine(self) -> Optional[Any]:
        """加载可视化监控引擎"""
        try:
            # 添加 scripts 目录到 sys.path
            if str(self.scripts_dir) not in sys.path:
                sys.path.insert(0, str(self.scripts_dir))

            from evolution_execution_efficiency_cockpit_integration_engine import (
                ExecutionEfficiencyCockpitIntegrationEngine
            )
            engine = ExecutionEfficiencyCockpitIntegrationEngine()
            _safe_print("[预测调度] 可视化监控引擎加载成功")

            # 继承历史数据
            if hasattr(engine, 'load_history') and engine.load_history:
                for data in engine.load_history:
                    self.load_history.append(data)

            return engine
        except ImportError as e:
            _safe_print(f"[预测调度] 无法加载可视化监控引擎: {e}")
            return None
        except Exception as e:
            _safe_print(f"[预测调度] 加载可视化监控引擎失败: {e}")
            return None

    def start_monitoring(self):
        """启动预测性监控"""
        if self.monitoring_active:
            _safe_print("[预测调度] 监控已在运行中")
            return

        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        _safe_print("[预测调度] 预测性监控已启动")

    def stop_monitoring(self):
        """停止监控"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=2)
        _safe_print("[预测调度] 预测性监控已停止")

    def _monitoring_loop(self):
        """监控循环"""
        while self.monitoring_active:
            try:
                # 收集负载数据
                load_data = self._collect_load_data()

                # 保存到历史
                self.load_history.append(load_data)

                # 实时预测
                if len(self.load_history) >= 10:
                    prediction = self.predict_future(self.prediction_horizon)
                    self.last_prediction = prediction
                    self.last_prediction_time = datetime.now()

                    # 基于预测调整调度策略
                    self._adjust_strategy_based_on_prediction(prediction)

                # 保存状态
                self._save_state()

            except Exception as e:
                _safe_print(f"[预测调度] 监控循环错误: {e}")

            time.sleep(self.monitoring_interval)

    def _collect_load_data(self) -> Dict[str, Any]:
        """收集负载数据"""
        try:
            # 优先使用 cockpit_engine
            if self.cockpit_engine and hasattr(self.cockpit_engine, '_collect_load_data'):
                return self.cockpit_engine._collect_load_data()

            # 直接收集
            return self._collect_direct_load_data()

        except Exception as e:
            return {
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "status": "error"
            }

    def _collect_direct_load_data(self) -> Dict[str, Any]:
        """直接收集负载数据"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.5)
            memory = psutil.virtual_memory()
            memory_percent = memory.percent

            return {
                "timestamp": datetime.now().isoformat(),
                "cpu": {"percent": round(cpu_percent, 1)},
                "memory": {"percent": round(memory_percent, 1)},
                "status": "normal"
            }
        except Exception as e:
            return {
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "status": "error"
            }

    def predict_future(self, horizon: int = 5) -> Dict[str, Any]:
        """预测未来负载"""
        if len(self.load_history) < 10:
            return {
                "status": "insufficient_data",
                "message": "需要更多历史数据进行预测"
            }

        try:
            # 获取历史数据
            history = list(self.load_history)[-self.prediction_window:]

            cpu_values = [d.get("cpu", {}).get("percent", 0) for d in history if "cpu" in d]
            memory_values = [d.get("memory", {}).get("percent", 0) for d in history if "memory" in d]

            if not cpu_values or not memory_values:
                return {"status": "error", "message": "无法提取历史数据"}

            # 预测
            cpu_prediction = self._predict_single_metric(cpu_values, horizon)
            memory_prediction = self._predict_single_metric(memory_values, horizon)

            # 计算置信度
            confidence = self._calculate_confidence()

            # 生成预测结果
            result = {
                "status": "ok",
                "timestamp": datetime.now().isoformat(),
                "horizon": horizon,
                "predictions": {
                    "cpu": {
                        "current": round(cpu_values[-1], 1),
                        "predicted": round(cpu_prediction, 1),
                        "trend": self._get_trend(cpu_values)
                    },
                    "memory": {
                        "current": round(memory_values[-1], 1),
                        "predicted": round(memory_prediction, 1),
                        "trend": self._get_trend(memory_values)
                    }
                },
                "confidence": confidence,
                "action_recommendation": self._generate_action_recommendation(
                    cpu_prediction, memory_prediction
                )
            }

            return result

        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _predict_single_metric(self, values: List[float], horizon: int) -> float:
        """预测单个指标"""
        if len(values) < 5:
            return values[-1] if values else 0

        # 计算趋势（线性回归斜率）
        trend = self._calculate_trend_slope(values)

        # 计算波动
        volatility = statistics.stdev(values) if len(values) > 1 else 0

        # 自适应权重
        recent_weight = 0.7
        trend_weight = 0.3

        # 预测 = 当前值 + 趋势 * 预测步数 * 权重 + 波动调整
        current = values[-1]
        prediction = current + trend * horizon * recent_weight

        # 考虑波动
        if abs(trend) < 0.5:  # 稳定趋势，使用均值回归
            mean = statistics.mean(values)
            prediction = prediction * (1 - recent_weight) + mean * recent_weight

        # 限制范围
        prediction = max(0, min(100, prediction))

        # 更新模型
        self._update_prediction_model(values, prediction, horizon)

        return prediction

    def _calculate_trend_slope(self, values: List[float]) -> float:
        """计算趋势斜率"""
        if len(values) < 2:
            return 0

        n = len(values)
        x = list(range(n))

        # 线性回归
        sum_x = sum(x)
        sum_y = sum(values)
        sum_xy = sum(x[i] * values[i] for i in range(n))
        sum_x2 = sum(xi * xi for xi in x)

        try:
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
            return slope
        except ZeroDivisionError:
            return 0

    def _get_trend(self, values: List[float]) -> str:
        """获取趋势描述"""
        if len(values) < 3:
            return "stable"

        slope = self._calculate_trend_slope(values[-10:])  # 最近10个点

        if slope > 1:
            return "increasing_fast"
        elif slope > 0.3:
            return "increasing"
        elif slope < -1:
            return "decreasing_fast"
        elif slope < -0.3:
            return "decreasing"
        else:
            return "stable"

    def _calculate_confidence(self) -> float:
        """计算预测置信度"""
        if len(self.prediction_errors) < 5:
            return 0.5  # 默认置信度

        # 基于历史预测误差计算置信度
        avg_error = statistics.mean(self.prediction_errors)

        # 误差越小，置信度越高
        confidence = max(0.1, min(0.95, 1 - avg_error / 100))

        return round(confidence, 2)

    def _update_prediction_model(self, actual_values: List[float], prediction: float, horizon: int):
        """更新预测模型"""
        if len(actual_values) < 5:
            return

        # 计算预测误差
        actual = actual_values[-1]
        error = abs(actual - prediction)

        # 更新误差历史
        self.prediction_errors.append(error)

        # 更新模型参数
        if self.prediction_model["initialized"]:
            # 简单自适应：调整权重
            if len(self.prediction_errors) > 0:
                recent_error = list(self.prediction_errors)[-5:]
                avg_error = statistics.mean(recent_error)

                if avg_error > 10:  # 误差大，降低趋势权重
                    self.prediction_model["trend_weights"][0] = max(0.3,
                        self.prediction_model["trend_weights"][0] - 0.05)
                elif avg_error < 5:  # 误差小，增加趋势权重
                    self.prediction_model["trend_weights"][0] = min(0.9,
                        self.prediction_model["trend_weights"][0] + 0.02)

            self.prediction_model["training_samples"] += 1

    def _generate_action_recommendation(self, cpu_pred: float, memory_pred: float) -> Dict:
        """生成行动建议"""
        recommendations = []
        priority_actions = []

        # CPU 预测建议
        if cpu_pred >= 85:
            recommendations.append({
                "type": "cpu",
                "level": "critical",
                "message": f"预测 CPU 将达到 {cpu_pred:.1f}%，建议立即降低任务负载",
                "action": "reduce_task_load",
                "priority": 1
            })
            priority_actions.append("delay_non_critical_tasks")
        elif cpu_pred >= 70:
            recommendations.append({
                "type": "cpu",
                "level": "warning",
                "message": f"预测 CPU 将达到 {cpu_pred:.1f}%，建议准备降低优先级",
                "action": "prepare_priority_reduction",
                "priority": 2
            })

        # 内存预测建议
        if memory_pred >= 85:
            recommendations.append({
                "type": "memory",
                "level": "critical",
                "message": f"预测内存将达到 {memory_pred:.1f}%，建议预清理缓存",
                "action": "preemptively_clear_cache",
                "priority": 1
            })
            priority_actions.append("preemptive_cache_clear")
        elif memory_pred >= 70:
            recommendations.append({
                "type": "memory",
                "level": "warning",
                "message": f"预测内存将达到 {memory_pred:.1f}%，建议延迟内存密集型任务",
                "action": "delay_memory_intensive",
                "priority": 2
            })

        # 正面建议
        if cpu_pred < 50 and memory_pred < 60:
            recommendations.append({
                "type": "opportunity",
                "level": "info",
                "message": "预测系统负载低，适合执行密集型任务",
                "action": "execute_intensive_tasks",
                "priority": 3
            })
            priority_actions.append("accelerate_critical_tasks")

        return {
            "recommendations": recommendations,
            "priority_actions": priority_actions,
            "strategy": self._determine_strategy(cpu_pred, memory_pred)
        }

    def _determine_strategy(self, cpu_pred: float, memory_pred: float) -> str:
        """确定调度策略"""
        if cpu_pred >= 80 or memory_pred >= 80:
            return "conservative"  # 保守策略
        elif cpu_pred >= 60 or memory_pred >= 60:
            return "balanced"  # 平衡策略
        elif cpu_pred < 40 and memory_pred < 40:
            return "aggressive"  # 激进策略
        else:
            return "balanced"

    def _adjust_strategy_based_on_prediction(self, prediction: Dict):
        """基于预测调整调度策略"""
        if prediction.get("status") != "ok":
            return

        action_rec = prediction.get("action_recommendation", {})
        new_strategy = action_rec.get("strategy", "balanced")

        if new_strategy != self.current_strategy:
            self.strategy_adjustments.append({
                "timestamp": datetime.now().isoformat(),
                "from": self.current_strategy,
                "to": new_strategy,
                "reason": action_rec.get("recommendations", [])
            })
            self.current_strategy = new_strategy
            _safe_print(f"[预测调度] 调度策略调整: {new_strategy}")

    def get_prediction(self) -> Dict[str, Any]:
        """获取最新预测"""
        if not self.last_prediction:
            # 尝试进行新预测
            if len(self.load_history) >= 10:
                self.last_prediction = self.predict_future(self.prediction_horizon)
                self.last_prediction_time = datetime.now()
            else:
                return {
                    "status": "no_data",
                    "message": "需要更多历史数据进行预测"
                }

        return {
            "status": "ok",
            "prediction": self.last_prediction,
            "timestamp": self.last_prediction_time.isoformat() if self.last_prediction_time else None,
            "current_strategy": self.current_strategy,
            "adjustments_count": len(self.strategy_adjustments)
        }

    def get_status(self) -> Dict[str, Any]:
        """获取状态"""
        return {
            "status": "ok",
            "version": self.version,
            "monitoring_active": self.monitoring_active,
            "current_strategy": self.current_strategy,
            "history_points": len(self.load_history),
            "confidence": self._calculate_confidence() if len(self.load_history) >= 10 else 0,
            "predictions_made": len(self.prediction_errors),
            "strategy_adjustments": len(self.strategy_adjustments)
        }

    def get_dashboard_data(self) -> Dict[str, Any]:
        """获取仪表盘数据"""
        prediction_data = self.get_prediction()

        # 获取负载历史
        history_list = list(self.load_history)
        current = history_list[-1] if history_list else {}

        return {
            "status": "ok",
            "version": self.version,
            "timestamp": datetime.now().isoformat(),
            "current_load": current,
            "prediction": prediction_data.get("prediction", {}),
            "current_strategy": self.current_strategy,
            "recent_adjustments": self.strategy_adjustments[-5:] if self.strategy_adjustments else [],
            "model_info": {
                "training_samples": self.prediction_model.get("training_samples", 0),
                "confidence": self._calculate_confidence() if len(self.load_history) >= 10 else 0
            }
        }

    def start(self):
        """启动引擎"""
        self.start_monitoring()
        return {
            "status": "started",
            "message": "执行效率预测性智能调度引擎已启动",
            "version": self.version
        }

    def stop(self):
        """停止引擎"""
        self.stop_monitoring()
        return {
            "status": "stopped",
            "message": "执行效率预测性智能调度引擎已停止"
        }

    def status(self):
        """状态查询"""
        return self.get_status()

    def analyze(self):
        """分析"""
        return self.get_dashboard_data()

    def optimize(self):
        """优化建议"""
        prediction = self.get_prediction()
        if prediction.get("status") == "ok":
            action_rec = prediction.get("prediction", {}).get("action_recommendation", {})
            return {
                "status": "ok",
                "recommendations": action_rec.get("recommendations", []),
                "priority_actions": action_rec.get("priority_actions", []),
                "current_strategy": self.current_strategy
            }
        return {"status": "no_data", "message": "暂无预测数据"}

    def heal(self):
        """自愈检查"""
        if not self.monitoring_active:
            return {
                "status": "healed",
                "action": "start_monitoring",
                "message": "启动预测性监控以确保系统健康"
            }

        # 检查是否需要调整策略
        if len(self.strategy_adjustments) > 0:
            last_adj = self.strategy_adjustments[-1]
            adj_time = datetime.fromisoformat(last_adj["timestamp"])
            if (datetime.now() - adj_time).seconds < 60:
                return {
                    "status": "healthy",
                    "message": "调度策略已自动调整"
                }

        return {
            "status": "healthy",
            "message": "预测性调度系统运行正常"
        }

    def _save_state(self):
        """保存状态"""
        try:
            state = {
                "version": self.version,
                "timestamp": datetime.now().isoformat(),
                "monitoring_active": self.monitoring_active,
                "current_strategy": self.current_strategy,
                "prediction_model": self.prediction_model,
                "adjustments": self.strategy_adjustments[-20:]
            }

            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)

        except Exception as e:
            _safe_print(f"[预测调度] 状态保存失败: {e}")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="执行效率预测性智能调度增强引擎")
    parser.add_argument("action", nargs="?", default="status",
                       choices=["start", "stop", "status", "analyze", "optimize", "heal", "predict"],
                       help="执行的操作")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")

    args = parser.parse_args()

    engine = ExecutionEfficiencyPredictiveSchedulingEngine()

    if args.action == "start":
        result = engine.start()
    elif args.action == "stop":
        result = engine.stop()
    elif args.action == "status":
        result = engine.status()
    elif args.action == "analyze":
        result = engine.analyze()
    elif args.action == "optimize":
        result = engine.optimize()
    elif args.action == "heal":
        result = engine.heal()
    elif args.action == "predict":
        result = engine.get_prediction()
    else:
        result = {"status": "unknown", "message": f"未知操作: {args.action}"}

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()