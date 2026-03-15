#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环动态阈值自适应优化引擎
(Evolution Dynamic Threshold Adaptive Optimization Engine)

在 round 477 完成的跨引擎协同效能预测增强引擎基础上，
进一步增强动态阈值自动调整能力，实现基于实时状态的预警阈值自适应优化。

让系统能够基于跨引擎协同效能预测结果自动调整预警阈值，
实现从「被动阈值管理」到「主动预测性阈值优化」的范式升级。

让进化环能够预测协同问题并提前调整阈值，实现真正的自适应预警管理。

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
    from evolution_cross_engine_collaboration_prediction_engine import (
        CrossEngineCollaborationPredictionEngine
    )
    COLLABORATION_PREDICTION_AVAILABLE = True
except ImportError:
    COLLABORATION_PREDICTION_AVAILABLE = False
    CrossEngineCollaborationPredictionEngine = None

try:
    from evolution_realtime_threshold_dynamic_engine import (
        RealtimeThresholdDynamicEngine,
        get_realtime_dynamic_engine
    )
    REALTIME_THRESHOLD_AVAILABLE = True
except ImportError:
    REALTIME_THRESHOLD_AVAILABLE = False
    RealtimeThresholdDynamicEngine = None


class AdaptiveThresholdOptimizer:
    """自适应阈值优化器"""

    # 默认阈值配置
    DEFAULT_THRESHOLDS = {
        "warning": 60,
        "critical": 40,
        "emergency": 20,
        "health_score": 70
    }

    def __init__(self):
        self.optimization_history: List[Dict[str, Any]] = []
        self.threshold_performance: Dict[str, List[float]] = defaultdict(list)
        self._load_optimization_history()

    def _load_optimization_history(self):
        """加载优化历史"""
        history_file = DATA_DIR / "adaptive_threshold_optimization_history.json"
        if history_file.exists():
            try:
                with open(history_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.optimization_history = data.get("history", [])
                    self.threshold_performance = defaultdict(
                        list,
                        data.get("performance", {})
                    )
            except Exception:
                pass

    def _save_optimization_history(self):
        """保存优化历史"""
        history_file = DATA_DIR / "adaptive_threshold_optimization_history.json"
        os.makedirs(DATA_DIR, exist_ok=True)
        try:
            with open(history_file, "w", encoding="utf-8") as f:
                json.dump({
                    "history": self.optimization_history[-100:],  # 只保留最近100条
                    "performance": dict(self.threshold_performance)
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存优化历史失败: {e}")

    def evaluate_threshold_performance(
        self,
        threshold_name: str,
        trigger_count: int,
        false_positive_rate: float,
        detection_rate: float
    ) -> float:
        """评估阈值性能

        Args:
            threshold_name: 阈值名称
            trigger_count: 触发次数
            false_positive_rate: 误报率
            detection_rate: 检出率

        Returns:
            综合性能分数 (0-100)
        """
        # 性能评分算法
        score = 100.0
        score -= false_positive_rate * 30  # 误报率权重30%
        score -= max(0, (trigger_count - 10) * 0.5) if trigger_count > 10 else 0  # 过多触发扣分
        score += detection_rate * 20  # 检出率奖励20%

        return max(0, min(100, score))

    def suggest_threshold_adjustment(
        self,
        current_thresholds: Dict[str, int],
        system_state: Dict[str, Any],
        collaboration_prediction: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """建议阈值调整

        Args:
            current_thresholds: 当前阈值
            system_state: 系统状态
            collaboration_prediction: 跨引擎协同预测结果

        Returns:
            调整建议
        """
        suggestions = {
            "adjustments": [],
            "reasons": [],
            "confidence": 0.0,
            "predicted_improvement": 0.0
        }

        cpu = system_state.get("cpu_usage", 50)
        memory = system_state.get("memory_usage", 50)
        health_score = system_state.get("composite_health", 50)

        # 基于系统状态调整
        if cpu > 70:
            suggestions["reasons"].append(f"CPU使用率较高({cpu}%)，建议降低预警阈值")
            suggestions["adjustments"].append({
                "level": "warning",
                "current": current_thresholds.get("warning", 60),
                "suggested": max(40, current_thresholds.get("warning", 60) - 10),
                "reason": "CPU高负载预警"
            })

        if memory > 70:
            suggestions["reasons"].append(f"内存使用率较高({memory}%)，建议降低预警阈值")
            suggestions["adjustments"].append({
                "level": "critical",
                "current": current_thresholds.get("critical", 40),
                "suggested": max(25, current_thresholds.get("critical", 40) - 8),
                "reason": "内存高负载预警"
            })

        # 基于跨引擎协同预测结果调整
        if collaboration_prediction:
            risk_level = collaboration_prediction.get("risk_assessment", {}).get("risk_level", "low")
            predicted_issues = collaboration_prediction.get("risk_assessment", {}).get("predicted_issues", [])

            if risk_level in ["high", "critical"]:
                suggestions["reasons"].append(f"跨引擎协同风险等级: {risk_level}，建议提前调整阈值")
                suggestions["confidence"] = 0.8

                # 预测到问题时，提前降低阈值以增加预警敏感度
                for issue in predicted_issues[:2]:  # 最多考虑2个问题
                    suggestions["adjustments"].append({
                        "level": "warning",
                        "current": current_thresholds.get("warning", 60),
                        "suggested": max(35, current_thresholds.get("warning", 60) - 15),
                        "reason": f"预测问题: {issue}"
                    })
            else:
                suggestions["confidence"] = 0.5
        else:
            suggestions["confidence"] = 0.3

        # 计算预期改进
        if suggestions["adjustments"]:
            suggestions["predicted_improvement"] = len(suggestions["adjustments"]) * 5

        return suggestions


class DynamicThresholdAdaptiveOptimizationEngine:
    """动态阈值自适应优化引擎核心类"""

    VERSION = "1.0.0"

    def __init__(self):
        self.name = "Evolution Dynamic Threshold Adaptive Optimization Engine"
        self.runtime_dir = PROJECT_ROOT / "runtime"
        self.state_dir = self.runtime_dir / "state"
        self.data_dir = self.runtime_dir / "data"

        # 数据文件路径
        self.config_file = self.data_dir / "dynamic_threshold_adaptive_config.json"
        self.optimization_log_file = self.data_dir / "dynamic_threshold_optimization_log.json"
        self.threshold_state_file = self.data_dir / "current_threshold_state.json"

        # 初始化组件
        self.optimizer = AdaptiveThresholdOptimizer()
        self.collaboration_engine = None
        self.realtime_threshold_engine = None

        # 配置
        self.config = self._load_config()

        # 优化状态
        self.optimization_enabled = self.config.get("enabled", True)
        self.last_optimization_time = None
        self.optimization_count = 0

        # 当前阈值状态
        self.current_thresholds = AdaptiveThresholdOptimizer.DEFAULT_THRESHOLDS.copy()
        self._load_threshold_state()

        # 监控线程
        self._running = False
        self._monitor_thread = None

        # 加载依赖引擎
        self._load_dependent_engines()

        # 启动优化监控
        if self.optimization_enabled:
            self._start_optimization_monitor()

    def _load_config(self) -> Dict[str, Any]:
        """加载配置"""
        default_config = {
            "enabled": True,
            "optimization_interval": 300,  # 优化间隔（秒）
            "min_adjust_interval": 180,  # 最小调整间隔（秒）
            "auto_adjust": True,  # 自动调整
            "max_adjust_per_cycle": 2,  # 每轮最大调整次数
            "collaboration_integration": True,  # 集成协同预测
            "performance_tracking": True,  # 性能追踪
            "threshold_margins": {
                "warning": {"min": 30, "max": 80},
                "critical": {"min": 20, "max": 60},
                "emergency": {"min": 10, "max": 40}
            }
        }

        if self.config_file.exists():
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    return {**default_config, **config}
            except Exception:
                pass

        return default_config

    def _save_config(self):
        """保存配置"""
        os.makedirs(self.data_dir, exist_ok=True)
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存配置失败: {e}")

    def _load_threshold_state(self):
        """加载当前阈值状态"""
        if self.threshold_state_file.exists():
            try:
                with open(self.threshold_state_file, "r", encoding="utf-8") as f:
                    self.current_thresholds = json.load(f)
            except Exception:
                pass

    def _save_threshold_state(self):
        """保存当前阈值状态"""
        os.makedirs(self.data_dir, exist_ok=True)
        try:
            with open(self.threshold_state_file, "w", encoding="utf-8") as f:
                json.dump(self.current_thresholds, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存阈值状态失败: {e}")

    def _load_dependent_engines(self):
        """加载依赖引擎"""
        if COLLABORATION_PREDICTION_AVAILABLE and self.config.get("collaboration_integration", True):
            try:
                self.collaboration_engine = CrossEngineCollaborationPredictionEngine()
                print("已加载跨引擎协同预测引擎")
            except Exception as e:
                print(f"加载跨引擎协同预测引擎失败: {e}")

        if REALTIME_THRESHOLD_AVAILABLE:
            try:
                self.realtime_threshold_engine = get_realtime_dynamic_engine()
                print("已加载实时阈值动态调整引擎")
            except Exception as e:
                print(f"加载实时阈值动态调整引擎失败: {e}")

    def _start_optimization_monitor(self):
        """启动优化监控线程"""
        if self._running:
            return

        self._running = True

        def monitor_loop():
            while self._running:
                try:
                    # 执行优化检查
                    self._perform_optimization_check()

                    # 等待下一个优化周期
                    time.sleep(self.config.get("optimization_interval", 300))
                except Exception as e:
                    print(f"优化监控线程异常: {e}")
                    time.sleep(60)

        self._monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self._monitor_thread.start()
        print("动态阈值自适应优化监控已启动")

    def stop_optimization(self):
        """停止优化监控"""
        self._running = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)

    def _perform_optimization_check(self):
        """执行优化检查"""
        if not self.optimization_enabled:
            return

        # 检查最小调整间隔
        if self.last_optimization_time:
            elapsed = time.time() - self.last_optimization_time
            if elapsed < self.config.get("min_adjust_interval", 180):
                return

        # 收集当前系统状态
        system_state = self._collect_system_state()

        # 获取跨引擎协同预测
        collaboration_prediction = None
        if self.collaboration_engine and self.config.get("collaboration_integration", True):
            try:
                collaboration_prediction = self.collaboration_engine.get_collaboration_prediction()
            except Exception as e:
                print(f"获取协同预测失败: {e}")

        # 生成优化建议
        suggestions = self.optimizer.suggest_threshold_adjustment(
            self.current_thresholds,
            system_state,
            collaboration_prediction
        )

        # 执行自动调整
        if self.config.get("auto_adjust", True) and suggestions.get("adjustments"):
            self._execute_threshold_adjustment(suggestions, system_state)

    def _collect_system_state(self) -> Dict[str, Any]:
        """收集系统状态"""
        state = {
            "timestamp": datetime.now().isoformat(),
            "cpu_usage": 50.0,
            "memory_usage": 50.0,
            "composite_health": 50.0
        }

        # 尝试获取真实系统状态
        try:
            import psutil
            state["cpu_usage"] = psutil.cpu_percent(interval=0.5)
            state["memory_usage"] = psutil.virtual_memory().percent
            state["composite_health"] = 100 - ((state["cpu_usage"] * 0.4 + state["memory_usage"] * 0.4))
        except Exception:
            pass

        return state

    def _execute_threshold_adjustment(
        self,
        suggestions: Dict[str, Any],
        system_state: Dict[str, Any]
    ):
        """执行阈值调整"""
        adjustments = suggestions.get("adjustments", [])
        if not adjustments:
            return

        # 限制每轮调整次数
        max_adjust = self.config.get("max_adjust_per_cycle", 2)
        adjustments = adjustments[:max_adjust]

        # 记录调整
        old_thresholds = self.current_thresholds.copy()

        for adj in adjustments:
            level = adj.get("level")
            new_value = adj.get("suggested")
            if level and new_value is not None:
                # 验证边界
                margins = self.config.get("threshold_margins", {}).get(level, {})
                min_val = margins.get("min", 10)
                max_val = margins.get("max", 90)
                new_value = max(min_val, min(max_val, new_value))

                self.current_thresholds[level] = new_value

        # 保存新状态
        self._save_threshold_state()

        # 记录优化历史
        optimization_record = {
            "timestamp": datetime.now().isoformat(),
            "old_thresholds": old_thresholds,
            "new_thresholds": self.current_thresholds.copy(),
            "adjustments": adjustments,
            "reasons": suggestions.get("reasons", []),
            "system_state": system_state,
            "confidence": suggestions.get("confidence", 0.0)
        }
        self.optimizer.optimization_history.append(optimization_record)
        self.optimizer._save_optimization_history()

        # 更新优化时间
        self.last_optimization_time = time.time()
        self.optimization_count += 1

        print(f"动态阈值自适应优化完成: {adjustments}")

    def get_optimization_status(self) -> Dict[str, Any]:
        """获取优化状态"""
        system_state = self._collect_system_state()

        collaboration_prediction = None
        if self.collaboration_engine:
            try:
                collaboration_prediction = self.collaboration_engine.get_collaboration_prediction()
            except Exception:
                pass

        suggestions = self.optimizer.suggest_threshold_adjustment(
            self.current_thresholds,
            system_state,
            collaboration_prediction
        )

        return {
            "success": True,
            "engine": self.name,
            "version": self.VERSION,
            "enabled": self.optimization_enabled,
            "current_thresholds": self.current_thresholds,
            "optimization_count": self.optimization_count,
            "last_optimization_time": (
                datetime.fromtimestamp(self.last_optimization_time).isoformat()
                if self.last_optimization_time else None
            ),
            "system_state": system_state,
            "suggestions": suggestions,
            "collaboration_prediction_available": self.collaboration_engine is not None
        }

    def get_optimization_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """获取优化历史"""
        return self.optimizer.optimization_history[-limit:]

    def get_cockpit_data(self) -> Dict[str, Any]:
        """获取驾驶舱数据"""
        status = self.get_optimization_status()

        return {
            "engine_name": self.name,
            "version": self.VERSION,
            "enabled": status["enabled"],
            "current_thresholds": status["current_thresholds"],
            "optimization_count": status["optimization_count"],
            "last_optimization": status["last_optimization_time"],
            "system_health": status["system_state"].get("composite_health", 50),
            "suggestions_count": len(status["suggestions"].get("adjustments", [])),
            "collaboration_integrated": status["collaboration_prediction_available"]
        }

    def force_optimization(self) -> Dict[str, Any]:
        """强制执行一次优化"""
        self._perform_optimization_check()

        return {
            "success": True,
            "message": "优化检查已完成",
            "current_thresholds": self.current_thresholds,
            "optimization_count": self.optimization_count
        }

    def set_threshold(self, level: str, value: int) -> bool:
        """手动设置阈值"""
        if level not in self.current_thresholds:
            return False

        margins = self.config.get("threshold_margins", {}).get(level, {})
        min_val = margins.get("min", 10)
        max_val = margins.get("max", 90)
        value = max(min_val, min(max_val, value))

        self.current_thresholds[level] = value
        self._save_threshold_state()
        return True

    def enable(self):
        """启用优化"""
        self.optimization_enabled = True
        self.config["enabled"] = True
        self._save_config()
        if not self._running:
            self._start_optimization_monitor()

    def disable(self):
        """禁用优化"""
        self.optimization_enabled = False
        self.config["enabled"] = False
        self._save_config()
        self.stop_optimization()

    def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        health = {
            "engine": self.name,
            "version": self.VERSION,
            "healthy": True,
            "components": {}
        }

        # 检查优化器
        health["components"]["optimizer"] = "ok"

        # 检查协同预测引擎
        if self.collaboration_engine:
            health["components"]["collaboration_engine"] = "ok"
        else:
            health["components"]["collaboration_engine"] = "not_loaded"

        # 检查实时阈值引擎
        if self.realtime_threshold_engine:
            health["components"]["realtime_threshold_engine"] = "ok"
        else:
            health["components"]["realtime_threshold_engine"] = "not_loaded"

        # 检查监控状态
        health["components"]["monitoring"] = self._running
        health["components"]["enabled"] = self.optimization_enabled

        return health


# 全局单例
_engine_instance = None


def get_adaptive_optimization_engine() -> DynamicThresholdAdaptiveOptimizationEngine:
    """获取引擎单例"""
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = DynamicThresholdAdaptiveOptimizationEngine()
    return _engine_instance


def main():
    """主函数：处理命令行调用"""
    if len(sys.argv) < 2:
        print("用法:")
        print("  python evolution_dynamic_threshold_adaptive_optimization_engine.py status")
        print("  python evolution_dynamic_threshold_adaptive_optimization_engine.py history")
        print("  python evolution_dynamic_threshold_adaptive_optimization_engine.py cockpit-data")
        print("  python evolution_dynamic_threshold_adaptive_optimization_engine.py optimize")
        print("  python evolution_dynamic_threshold_adaptive_optimization_engine.py enable")
        print("  python evolution_dynamic_threshold_adaptive_optimization_engine.py disable")
        print("  python evolution_dynamic_threshold_adaptive_optimization_engine.py health")
        return

    engine = get_adaptive_optimization_engine()
    command = sys.argv[1].lower()

    if command == "status":
        result = engine.get_optimization_status()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "history":
        result = engine.get_optimization_history()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "cockpit-data":
        result = engine.get_cockpit_data()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "optimize":
        result = engine.force_optimization()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "enable":
        engine.enable()
        print("已启用动态阈值自适应优化")

    elif command == "disable":
        engine.disable()
        print("已禁用动态阈值自适应优化")

    elif command == "health":
        result = engine.health_check()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    else:
        print(f"未知命令: {command}")
        print("可用命令: status, history, cockpit-data, optimize, enable, disable, health")


if __name__ == "__main__":
    main()