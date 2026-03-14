#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环实时阈值动态调整引擎
==================================================

round 400: 在 round 399 的阈值自动调整引擎基础上，增强实时阈值动态调整能力，
根据实时系统状态动态调整阈值，实现更精准的预防性阈值管理

功能：
1. 实时系统状态监控（CPU、内存、负载、时间模式）
2. 基于实时状态的动态阈值调整
3. 预防性阈值管理（趋势预测、提前调整）
4. 与现有阈值触发引擎和自动调整引擎深度集成
5. 智能预警与自动应对

version: 1.0.0
"""

import json
import os
import sys
import time
import threading
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from collections import deque

# 添加 scripts 目录到路径以导入依赖模块
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, SCRIPT_DIR)

# 尝试导入依赖引擎
try:
    from evolution_health_threshold_trigger_engine import (
        EvolutionHealthThresholdTriggerEngine,
        get_threshold_trigger_engine
    )
except ImportError:
    EvolutionHealthThresholdTriggerEngine = None

try:
    from evolution_health_threshold_auto_adjust_engine import (
        ThresholdAutoAdjustEngine,
        get_auto_adjust_engine
    )
except ImportError:
    ThresholdAutoAdjustEngine = None


class RealtimeSystemMonitor:
    """实时系统状态监控器"""

    def __init__(self, sample_interval: int = 30):
        """初始化监控系统

        Args:
            sample_interval: 采样间隔（秒）
        """
        self.sample_interval = sample_interval
        self.history_size = 60  # 保留最近60个样本（约30分钟）
        self.cpu_history = deque(maxlen=self.history_size)
        self.memory_history = deque(maxlen=self.history_size)
        self.load_history = deque(maxlen=self.history_size)
        self._running = False
        self._monitor_thread = None

    def get_cpu_usage(self) -> float:
        """获取CPU使用率"""
        try:
            import psutil
            return psutil.cpu_percent(interval=1)
        except Exception:
            # 尝试从系统获取CPU信息
            try:
                import subprocess
                result = subprocess.run(
                    ['wmic', 'cpu', 'get', 'loadpercentage'],
                    capture_output=True, text=True, timeout=3
                )
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1 and lines[1].strip().isdigit():
                    return float(lines[1].strip())
            except Exception:
                pass
            return 50.0  # 默认值

    def get_memory_usage(self) -> float:
        """获取内存使用率"""
        try:
            import psutil
            return psutil.virtual_memory().percent
        except Exception:
            try:
                import subprocess
                result = subprocess.run(
                    ['wmic', 'OS', 'get', 'FreePhysicalMemory,TotalVisibleMemorySize', '/format:list'],
                    capture_output=True, text=True, timeout=3
                )
                for line in result.stdout.split('\n'):
                    if 'FreePhysicalMemory=' in line:
                        free = int(line.split('=')[1].strip())
                    if 'TotalVisibleMemorySize=' in line:
                        total = int(line.split('=')[1].strip())
                if 'free' in dir() and 'total' in dir():
                    used = total - free
                    return (used / total) * 100
            except Exception:
                pass
            return 50.0  # 默认值

    def get_system_load(self) -> float:
        """获取系统负载"""
        try:
            import psutil
            return psutil.getloadavg()[0] if hasattr(psutil, 'getloadavg') else 0.0
        except Exception:
            # Windows 上可能不可用，返回综合指标
            cpu = self.get_cpu_usage()
            mem = self.get_memory_usage()
            return (cpu + mem) / 2

    def get_time_based_modifier(self) -> float:
        """获取基于时间的调节因子

        根据时间段调整阈值：
        - 工作时间(9-18): 正常敏感度
        - 非工作时间: 降低敏感度（减少误报）
        - 凌晨(0-6): 最低敏感度
        """
        now = datetime.now()
        hour = now.hour

        if 0 <= hour < 6:
            return 0.7  # 凌晨降低30%敏感度
        elif 6 <= hour < 9:
            return 0.85  # 早晨降低15%敏感度
        elif 9 <= hour < 18:
            return 1.0  # 工作时间正常敏感度
        elif 18 <= hour < 22:
            return 0.9  # 晚间稍微降低
        else:
            return 0.75  # 深夜降低

    def collect_current_state(self) -> Dict[str, Any]:
        """收集当前系统状态"""
        cpu = self.get_cpu_usage()
        memory = self.get_memory_usage()
        load = self.get_system_load()
        time_modifier = self.get_time_based_modifier()

        # 综合健康分数
        composite_health = 100 - ((cpu * 0.4 + memory * 0.4 + load * 0.2))

        return {
            "timestamp": datetime.now().isoformat(),
            "cpu_usage": round(cpu, 1),
            "memory_usage": round(memory, 1),
            "system_load": round(load, 1),
            "time_modifier": time_modifier,
            "composite_health": round(composite_health, 1)
        }

    def record_state(self):
        """记录当前状态到历史"""
        state = self.collect_current_state()
        self.cpu_history.append(state["cpu_usage"])
        self.memory_history.append(state["memory_usage"])
        self.load_history.append(state["system_load"])
        return state

    def get_trend(self, metric: str = "cpu") -> str:
        """获取指标趋势（递增/递减/稳定）

        Args:
            metric: 指标类型 (cpu/memory/load)

        Returns:
            趋势描述
        """
        history = {
            "cpu": self.cpu_history,
            "memory": self.memory_history,
            "load": self.load_history
        }.get(metric, self.cpu_history)

        if len(history) < 5:
            return "insufficient_data"

        # 比较前后两半的平均值
        mid = len(history) // 2
        first_half = list(history)[:mid]
        second_half = list(history)[mid:]

        first_avg = sum(first_half) / len(first_half) if first_half else 0
        second_avg = sum(second_half) / len(second_half) if second_half else 0

        if second_avg > first_half * 1.2:
            return "increasing"
        elif second_avg < first_half * 0.8:
            return "decreasing"
        else:
            return "stable"

    def predict_next_state(self, metric: str = "cpu", steps: int = 3) -> float:
        """预测未来状态（简单线性预测）

        Args:
            metric: 指标类型
            steps: 预测步数

        Returns:
            预测值
        """
        history = {
            "cpu": self.cpu_history,
            "memory": self.memory_history,
            "load": self.load_history
        }.get(metric, self.cpu_history)

        if len(history) < 5:
            return list(history)[-1] if history else 50.0

        # 简单线性回归
        n = len(history)
        x = list(range(n))
        y = list(history)

        # 计算斜率
        x_mean = sum(x) / n
        y_mean = sum(y) / n

        numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            return y[-1]

        slope = numerator / denominator
        intercept = y_mean - slope * x_mean

        # 预测未来steps步
        predicted = intercept + slope * (n + steps)
        return max(0, min(100, predicted))


class RealtimeThresholdDynamicEngine:
    """实时阈值动态调整引擎"""

    VERSION = "1.0.0"

    # 动态调整配置
    DEFAULT_CONFIG = {
        "enabled": True,
        "sample_interval": 30,  # 采样间隔（秒）
        "adjust_threshold": 10,  # 变化超过此值才调整
        "min_adjust_interval": 60,  # 最小调整间隔（秒）
        "predictive_enabled": True,  # 启用预测性调整
        "predict_steps": 3,  # 预测步数
        "time_based_enabled": True,  # 启用时间调节
        "trend_based_enabled": True,  # 启用趋势调节
    }

    def __init__(self):
        """初始化实时阈值动态调整引擎"""
        self.monitor = RealtimeSystemMonitor()
        self.trigger_engine = None
        self.auto_adjust_engine = None
        self.config = self._load_config()

        # 动态调整历史
        self.dynamic_log: List[Dict[str, Any]] = []
        self._load_dynamic_log()

        # 加载依赖引擎
        self._load_dependent_engines()

        # 最后调整时间
        self.last_adjust_time = None

        # 监控线程状态（必须在启动监控前初始化）
        self._running = False

        # 启动实时监控线程
        if self.config.get("enabled", True):
            self._start_monitoring()

    def _load_config(self) -> Dict[str, Any]:
        """加载配置"""
        config_file = os.path.join(
            PROJECT_ROOT, "runtime", "state",
            "realtime_threshold_dynamic_config.json"
        )

        if os.path.exists(config_file):
            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    return {**self.DEFAULT_CONFIG, **json.load(f)}
            except Exception:
                pass

        return self.DEFAULT_CONFIG.copy()

    def _save_config(self):
        """保存配置"""
        config_file = os.path.join(
            PROJECT_ROOT, "runtime", "state",
            "realtime_threshold_dynamic_config.json"
        )
        os.makedirs(os.path.dirname(config_file), exist_ok=True)
        try:
            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存配置失败: {e}")

    def _load_dynamic_log(self):
        """加载动态调整日志"""
        log_file = os.path.join(
            PROJECT_ROOT, "runtime", "state",
            "realtime_threshold_dynamic_log.json"
        )
        if os.path.exists(log_file):
            try:
                with open(log_file, "r", encoding="utf-8") as f:
                    self.dynamic_log = json.load(f)
            except Exception:
                self.dynamic_log = []

        # 只保留最近200条
        if len(self.dynamic_log) > 200:
            self.dynamic_log = self.dynamic_log[-200:]

    def _save_dynamic_log(self):
        """保存动态调整日志"""
        log_file = os.path.join(
            PROJECT_ROOT, "runtime", "state",
            "realtime_threshold_dynamic_log.json"
        )
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        try:
            with open(log_file, "w", encoding="utf-8") as f:
                json.dump(self.dynamic_log, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存动态日志失败: {e}")

    def _load_dependent_engines(self):
        """加载依赖引擎"""
        if EvolutionHealthThresholdTriggerEngine:
            try:
                self.trigger_engine = get_threshold_trigger_engine()
            except Exception as e:
                print(f"加载阈值触发引擎失败: {e}")

        if ThresholdAutoAdjustEngine:
            try:
                self.auto_adjust_engine = get_auto_adjust_engine()
            except Exception as e:
                print(f"加载自动调整引擎失败: {e}")

    def _start_monitoring(self):
        """启动实时监控线程"""
        if self._running:
            return

        self._running = True

        def monitor_loop():
            while self._running:
                try:
                    # 记录当前状态
                    state = self.monitor.record_state()

                    # 检查是否需要动态调整
                    self._check_and_adjust()

                    # 等待下一个采样间隔
                    time.sleep(self.config.get("sample_interval", 30))
                except Exception as e:
                    print(f"监控线程异常: {e}")
                    time.sleep(10)

        self._monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self._monitor_thread.start()

    def stop_monitoring(self):
        """停止监控"""
        self._running = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)

    def _check_and_adjust(self):
        """检查并执行动态调整"""
        # 检查是否启用
        if not self.config.get("enabled", True):
            return

        # 检查最小调整间隔
        if self.last_adjust_time:
            elapsed = time.time() - self.last_adjust_time
            if elapsed < self.config.get("min_adjust_interval", 60):
                return

        # 获取当前状态
        current_state = self.monitor.collect_current_state()

        if not self.trigger_engine:
            return

        # 获取当前阈值
        current_thresholds = self.trigger_engine.get_thresholds()

        # 计算建议的动态阈值
        suggested = self._calculate_dynamic_thresholds(current_state)

        # 检查是否需要调整
        needs_adjust = False
        adjustments = []

        for level in ["warning", "critical", "emergency"]:
            current = current_thresholds.get(level, 60 if level == "warning" else 40 if level == "critical" else 20)
            suggested_value = suggested.get(level, current)

            if abs(current - suggested_value) >= self.config.get("adjust_threshold", 10):
                needs_adjust = True
                adjustments.append({
                    "level": level,
                    "old_value": current,
                    "new_value": suggested_value
                })

        # 执行调整
        if needs_adjust:
            self._execute_adjustment(adjustments, current_state)

    def _calculate_dynamic_thresholds(self, state: Dict[str, Any]) -> Dict[str, int]:
        """计算动态阈值

        Args:
            state: 当前系统状态

        Returns:
            动态调整后的阈值
        """
        cpu = state.get("cpu_usage", 50)
        memory = state.get("memory_usage", 50)
        load = state.get("system_load", 50)
        time_modifier = state.get("time_modifier", 1.0)

        # 基础阈值
        base_warning = 60
        base_critical = 40
        base_emergency = 20

        # 计算综合负载
        composite = (cpu + memory + load) / 3

        # 应用时间调节因子
        time_adjusted_composite = composite * time_modifier

        # 趋势调节
        trend_adjustment = 0
        if self.config.get("trend_based_enabled", True):
            cpu_trend = self.monitor.get_trend("cpu")
            mem_trend = self.monitor.get_trend("memory")

            if cpu_trend == "increasing":
                trend_adjustment += 5  # CPU上升趋势，提高敏感度
            elif cpu_trend == "decreasing":
                trend_adjustment -= 3  # CPU下降趋势，降低敏感度

            if mem_trend == "increasing":
                trend_adjustment += 5
            elif mem_trend == "decreasing":
                trend_adjustment -= 3

        # 预测性调节
        predictive_adjustment = 0
        if self.config.get("predictive_enabled", True):
            predict_steps = self.config.get("predict_steps", 3)

            predicted_cpu = self.monitor.predict_next_state("cpu", predict_steps)
            predicted_mem = self.monitor.predict_next_state("memory", predict_steps)

            # 如果预测值显著高于当前值，提前调整
            if predicted_cpu > cpu + 15:
                predictive_adjustment += 3
            if predicted_mem > memory + 15:
                predictive_adjustment += 3

        # 计算最终阈值（负载越高，阈值越低，更早预警）
        adjustment = int(time_adjusted_composite / 10 + trend_adjustment + predictive_adjustment)

        return {
            "warning": max(30, min(80, base_warning - adjustment)),
            "critical": max(20, min(60, base_critical - adjustment)),
            "emergency": max(10, min(40, base_emergency - adjustment))
        }

    def _execute_adjustment(self, adjustments: List[Dict[str, Any]], state: Dict[str, Any]):
        """执行阈值调整"""
        if not self.trigger_engine:
            return

        old_thresholds = self.trigger_engine.get_thresholds()
        new_thresholds = old_thresholds.copy()

        try:
            for adj in adjustments:
                level = adj["level"]
                new_value = adj["new_value"]
                self.trigger_engine.set_threshold(level, new_value)
                new_thresholds[level] = new_value

            # 记录调整
            self.last_adjust_time = time.time()

            # 记录到日志
            record = {
                "timestamp": datetime.now().isoformat(),
                "trigger": "dynamic_adjust",
                "old_thresholds": old_thresholds,
                "new_thresholds": new_thresholds,
                "adjustments": adjustments,
                "system_state": state,
                "reason": self._get_adjust_reason(state)
            }
            self.dynamic_log.append(record)
            self._save_dynamic_log()

            print(f"实时动态阈值调整完成: {adjustments}")

        except Exception as e:
            print(f"执行动态调整失败: {e}")

    def _get_adjust_reason(self, state: Dict[str, Any]) -> str:
        """获取调整原因描述"""
        reasons = []

        cpu = state.get("cpu_usage", 0)
        memory = state.get("memory_usage", 0)
        time_mod = state.get("time_modifier", 1.0)

        if cpu > 70:
            reasons.append(f"CPU使用率较高({cpu}%)")
        if memory > 70:
            reasons.append(f"内存使用率较高({memory}%)")
        if time_mod < 1.0:
            reasons.append(f"非工作时间调节({time_mod})")

        cpu_trend = self.monitor.get_trend("cpu")
        mem_trend = self.monitor.get_trend("memory")

        if cpu_trend == "increasing":
            reasons.append("CPU上升趋势")
        if mem_trend == "increasing":
            reasons.append("内存上升趋势")

        return "; ".join(reasons) if reasons else "系统状态变化"

    def get_current_state(self) -> Dict[str, Any]:
        """获取当前系统状态和阈值"""
        state = self.monitor.collect_current_state()

        thresholds = {}
        if self.trigger_engine:
            thresholds = self.trigger_engine.get_thresholds()

        suggested = self._calculate_dynamic_thresholds(state)

        # 获取趋势
        trends = {
            "cpu": self.monitor.get_trend("cpu"),
            "memory": self.monitor.get_trend("memory"),
            "load": self.monitor.get_trend("load")
        }

        # 获取预测
        predictions = {}
        if self.config.get("predictive_enabled", True):
            predictions = {
                "cpu_next": round(self.monitor.predict_next_state("cpu", 3), 1),
                "memory_next": round(self.monitor.predict_next_state("memory", 3), 1)
            }

        return {
            "success": True,
            "system_state": state,
            "current_thresholds": thresholds,
            "suggested_thresholds": suggested,
            "trends": trends,
            "predictions": predictions,
            "time_modifier": state.get("time_modifier", 1.0)
        }

    def get_dynamic_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """获取动态调整历史"""
        return self.dynamic_log[-limit:]

    def enable(self):
        """启用实时动态调整"""
        self.config["enabled"] = True
        self._save_config()
        if not self._running:
            self._start_monitoring()

    def disable(self):
        """禁用实时动态调整"""
        self.config["enabled"] = False
        self._save_config()
        self.stop_monitoring()

    def force_adjust(self) -> Dict[str, Any]:
        """强制执行一次动态调整"""
        current_state = self.monitor.record_state()
        suggested = self._calculate_dynamic_thresholds(current_state)

        if not self.trigger_engine:
            return {"success": False, "message": "触发引擎未加载"}

        old_thresholds = self.trigger_engine.get_thresholds()
        adjustments = []

        for level in ["warning", "critical", "emergency"]:
            old = old_thresholds.get(level, 60 if level == "warning" else 40 if level == "critical" else 20)
            new = suggested.get(level, old)
            if old != new:
                self.trigger_engine.set_threshold(level, new)
                adjustments.append({"level": level, "old_value": old, "new_value": new})

        if adjustments:
            self.last_adjust_time = time.time()
            self._save_dynamic_log()
            return {
                "success": True,
                "message": "动态调整完成",
                "old_thresholds": old_thresholds,
                "new_thresholds": suggested,
                "adjustments": adjustments
            }
        else:
            return {
                "success": True,
                "message": "当前阈值已是最优，无需调整",
                "current_thresholds": old_thresholds
            }

    def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        health = {
            "engine": "RealtimeThresholdDynamicEngine",
            "version": self.VERSION,
            "healthy": True,
            "components": {}
        }

        # 检查监控器
        health["components"]["monitor"] = "ok"

        # 检查触发引擎
        if self.trigger_engine:
            health["components"]["trigger_engine"] = "ok"
        else:
            health["components"]["trigger_engine"] = "not_loaded"
            health["healthy"] = False

        # 检查自动调整引擎
        if self.auto_adjust_engine:
            health["components"]["auto_adjust_engine"] = "ok"
        else:
            health["components"]["auto_adjust_engine"] = "not_loaded"

        # 检查配置
        health["components"]["enabled"] = self.config.get("enabled", True)
        health["components"]["monitoring"] = self._running

        return health


def get_realtime_dynamic_engine() -> RealtimeThresholdDynamicEngine:
    """获取实时动态调整引擎单例"""
    return RealtimeThresholdDynamicEngine()


def main():
    """主函数：处理命令行调用"""
    if len(sys.argv) < 2:
        print("用法:")
        print("  python evolution_realtime_threshold_dynamic_engine.py state")
        print("  python evolution_realtime_threshold_dynamic_engine.py adjust")
        print("  python evolution_realtime_threshold_dynamic_engine.py history")
        print("  python evolution_realtime_threshold_dynamic_engine.py enable")
        print("  python evolution_realtime_threshold_dynamic_engine.py disable")
        print("  python evolution_realtime_threshold_dynamic_engine.py health")
        return

    engine = get_realtime_dynamic_engine()
    command = sys.argv[1].lower()

    if command == "state":
        result = engine.get_current_state()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "adjust":
        result = engine.force_adjust()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "history":
        result = engine.get_dynamic_history()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "enable":
        engine.enable()
        print("已启用实时动态阈值调整")

    elif command == "disable":
        engine.disable()
        print("已禁用实时动态阈值调整")

    elif command == "health":
        result = engine.health_check()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    else:
        print(f"未知命令: {command}")
        print("可用命令: state, adjust, history, enable, disable, health")


if __name__ == "__main__":
    main()