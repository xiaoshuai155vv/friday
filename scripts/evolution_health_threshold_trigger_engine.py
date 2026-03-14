#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环健康分数阈值自动触发进化引擎
==================================================

round 398: 在 round 397 的统一监控驾驶舱与完全无人值守进化环深度集成基础上，
增强完全自动化的监控-执行闭环，实现基于健康分数阈值的自动触发进化能力

功能：
1. 可配置的阈值设置（警告、严重、紧急）
2. 阈值配置管理（保存、加载、调整）
3. 基于阈值的自动触发逻辑
4. 触发历史记录与分析
5. 与统一监控和无人值守引擎深度集成

version: 1.0.0
"""

import json
import os
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

# 添加 scripts 目录到路径以导入依赖模块
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, SCRIPT_DIR)

# 尝试导入依赖引擎
try:
    from evolution_unified_monitoring_unattended_integration_engine import (
        EvolutionUnifiedMonitoringUnattendedIntegrationEngine,
        get_integration_engine as get_integration_engine
    )
except ImportError:
    EvolutionUnifiedMonitoringUnattendedIntegrationEngine = None

try:
    from evolution_autonomous_unattended_enhancement_engine import (
        EvolutionAutonomousUnattendedEngine
    )
except ImportError:
    EvolutionAutonomousUnattendedEngine = None


class HealthThresholdConfig:
    """健康分数阈值配置管理器"""

    DEFAULT_THRESHOLDS = {
        "warning": 60,      # 警告阈值：低于此值触发警告
        "critical": 40,     # 严重阈值：低于此值触发严重预警
        "emergency": 20     # 紧急阈值：低于此值触发紧急自动进化
    }

    def __init__(self, config_file: str = None):
        """初始化阈值配置管理器"""
        if config_file is None:
            config_file = os.path.join(
                PROJECT_ROOT, "runtime", "state",
                "health_threshold_config.json"
            )
        self.config_file = config_file
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """加载阈值配置"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass

        # 返回默认配置
        return {
            "thresholds": self.DEFAULT_THRESHOLDS.copy(),
            "enabled": True,
            "auto_adjust": False,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }

    def _save_config(self):
        """保存阈值配置"""
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        self.config["updated_at"] = datetime.now().isoformat()
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存阈值配置失败: {e}")

    def get_thresholds(self) -> Dict[str, int]:
        """获取当前阈值设置"""
        return self.config.get("thresholds", self.DEFAULT_THRESHOLDS.copy())

    def set_threshold(self, level: str, value: int):
        """设置指定级别的阈值"""
        if level not in self.DEFAULT_THRESHOLDS:
            raise ValueError(f"无效的阈值级别: {level}，必须是 warning/critical/emergency 之一")

        if not 0 <= value <= 100:
            raise ValueError("阈值必须在 0-100 之间")

        self.config["thresholds"][level] = value
        self._save_config()

    def reset_to_default(self):
        """重置为默认阈值"""
        self.config["thresholds"] = self.DEFAULT_THRESHOLDS.copy()
        self._save_config()

    def is_enabled(self) -> bool:
        """检查是否启用阈值触发"""
        return self.config.get("enabled", True)

    def set_enabled(self, enabled: bool):
        """设置启用状态"""
        self.config["enabled"] = enabled
        self._save_config()

    def is_auto_adjust_enabled(self) -> bool:
        """检查是否启用自动调整"""
        return self.config.get("auto_adjust", False)

    def set_auto_adjust(self, enabled: bool):
        """设置自动调整启用状态"""
        self.config["auto_adjust"] = enabled
        self._save_config()


class EvolutionHealthThresholdTriggerEngine:
    """健康分数阈值自动触发进化引擎"""

    VERSION = "1.0.0"

    def __init__(self):
        """初始化阈值触发引擎"""
        self.threshold_config = HealthThresholdConfig()
        self.integration_engine = None
        self.trigger_history: List[Dict[str, Any]] = []
        self._load_integration_engine()
        self._load_trigger_history()

    def _load_integration_engine(self):
        """加载集成引擎"""
        if EvolutionUnifiedMonitoringUnattendedIntegrationEngine:
            try:
                self.integration_engine = get_integration_engine()
            except Exception as e:
                print(f"加载集成引擎失败: {e}")
                self.integration_engine = None
        else:
            print("警告: 未找到 EvolutionUnifiedMonitoringUnattendedIntegrationEngine")

    def _load_trigger_history(self):
        """加载触发历史"""
        history_file = os.path.join(
            PROJECT_ROOT, "runtime", "state",
            "health_threshold_trigger_history.json"
        )
        if os.path.exists(history_file):
            try:
                with open(history_file, "r", encoding="utf-8") as f:
                    self.trigger_history = json.load(f)
            except Exception:
                self.trigger_history = []

        # 只保留最近100条记录
        if len(self.trigger_history) > 100:
            self.trigger_history = self.trigger_history[-100:]

    def _save_trigger_history(self):
        """保存触发历史"""
        history_file = os.path.join(
            PROJECT_ROOT, "runtime", "state",
            "health_threshold_trigger_history.json"
        )
        os.makedirs(os.path.dirname(history_file), exist_ok=True)
        try:
            with open(history_file, "w", encoding="utf-8") as f:
                json.dump(self.trigger_history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存触发历史失败: {e}")

    def _add_trigger_record(self, health_score: int, trigger_level: str, action_taken: str):
        """添加触发记录"""
        record = {
            "timestamp": datetime.now().isoformat(),
            "health_score": health_score,
            "trigger_level": trigger_level,
            "action_taken": action_taken
        }
        self.trigger_history.append(record)
        self._save_trigger_history()

    def get_current_health_score(self) -> int:
        """获取当前健康分数"""
        if not self.integration_engine:
            return 100  # 默认健康分数

        try:
            status = self.integration_engine.get_status()
            # 尝试从监控数据获取健康分数
            monitoring = status.get("monitoring_engine", {})
            if isinstance(monitoring, dict):
                # 尝试多种健康分数字段
                health_score = monitoring.get("health_score")
                if health_score is None:
                    # 尝试从 unified_health_score 获取
                    health_score = monitoring.get("unified_health_score")
                if health_score is None:
                    # 尝试从健康度字段获取
                    health_score = monitoring.get("health", {}).get("score")
                if health_score is not None:
                    return int(health_score)
        except Exception as e:
            print(f"获取健康分数失败: {e}")

        return 100  # 默认值

    def check_threshold_and_trigger(self) -> Dict[str, Any]:
        """检查阈值并触发进化"""
        result = {
            "success": False,
            "timestamp": datetime.now().isoformat(),
            "health_score": 100,
            "triggered": False,
            "trigger_level": None,
            "action": None,
            "thresholds": self.threshold_config.get_thresholds()
        }

        # 检查是否启用
        if not self.threshold_config.is_enabled():
            result["message"] = "阈值触发已禁用"
            return result

        # 获取当前健康分数
        health_score = self.get_current_health_score()
        result["health_score"] = health_score

        # 获取阈值设置
        thresholds = self.threshold_config.get_thresholds()

        # 检查各个阈值级别
        trigger_level = None
        action = None

        if health_score <= thresholds.get("emergency", 20):
            trigger_level = "emergency"
            action = "立即触发紧急自动进化"
        elif health_score <= thresholds.get("critical", 40):
            trigger_level = "critical"
            action = "触发严重预警并启动自动进化"
        elif health_score <= thresholds.get("warning", 60):
            trigger_level = "warning"
            action = "触发警告级别预警"

        result["trigger_level"] = trigger_level
        result["action"] = action

        # 如果达到触发条件且集成引擎可用，触发进化
        if trigger_level and self.integration_engine:
            try:
                # 使用集成引擎的触发功能
                trigger_result = self.integration_engine.check_monitoring_and_trigger()

                result["triggered"] = True
                result["trigger_success"] = trigger_result.get("triggered", False)
                result["trigger_result"] = trigger_result

                # 记录触发历史
                self._add_trigger_record(
                    health_score,
                    trigger_level,
                    action
                )

                result["success"] = True

            except Exception as e:
                result["error"] = str(e)
                result["message"] = f"触发失败: {e}"
        elif trigger_level:
            # 没有集成引擎时，只记录预警
            result["message"] = f"健康分数 {health_score} 达到 {trigger_level} 级别，但集成引擎未加载"
            self._add_trigger_record(health_score, trigger_level, action)
            result["success"] = True
        else:
            result["message"] = f"健康分数 {health_score} 在正常范围内"
            result["success"] = True

        return result

    def get_threshold_status(self) -> Dict[str, Any]:
        """获取阈值状态"""
        health_score = self.get_current_health_score()
        thresholds = self.threshold_config.get_thresholds()

        current_level = "normal"
        if health_score <= thresholds.get("emergency", 20):
            current_level = "emergency"
        elif health_score <= thresholds.get("critical", 40):
            current_level = "critical"
        elif health_score <= thresholds.get("warning", 60):
            current_level = "warning"

        return {
            "current_health_score": health_score,
            "thresholds": thresholds,
            "current_level": current_level,
            "enabled": self.threshold_config.is_enabled(),
            "auto_adjust": self.threshold_config.is_auto_adjust_enabled()
        }

    def get_trigger_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """获取触发历史"""
        return self.trigger_history[-limit:]

    def get_statistics(self) -> Dict[str, Any]:
        """获取触发统计信息"""
        if not self.trigger_history:
            return {
                "total_triggers": 0,
                "by_level": {},
                "latest_trigger": None
            }

        by_level = {}
        for record in self.trigger_history:
            level = record.get("trigger_level", "unknown")
            by_level[level] = by_level.get(level, 0) + 1

        return {
            "total_triggers": len(self.trigger_history),
            "by_level": by_level,
            "latest_trigger": self.trigger_history[-1] if self.trigger_history else None
        }

    def set_threshold(self, level: str, value: int):
        """设置阈值"""
        self.threshold_config.set_threshold(level, value)

    def get_thresholds(self) -> Dict[str, int]:
        """获取当前阈值"""
        return self.threshold_config.get_thresholds()

    def reset_thresholds(self):
        """重置阈值为默认值"""
        self.threshold_config.reset_to_default()

    def enable(self):
        """启用阈值触发"""
        self.threshold_config.set_enabled(True)

    def disable(self):
        """禁用阈值触发"""
        self.threshold_config.set_enabled(False)

    def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        health = {
            "engine": "EvolutionHealthThresholdTriggerEngine",
            "version": self.VERSION,
            "healthy": True,
            "components": {}
        }

        # 检查集成引擎
        if self.integration_engine:
            health["components"]["integration_engine"] = "ok"
        else:
            health["components"]["integration_engine"] = "not_loaded"

        # 检查阈值配置
        health["components"]["threshold_config"] = "ok"

        # 检查状态
        status = self.get_threshold_status()
        health["components"]["current_level"] = status["current_level"]
        health["components"]["enabled"] = status["enabled"]

        return health


def get_threshold_trigger_engine() -> EvolutionHealthThresholdTriggerEngine:
    """获取阈值触发引擎单例"""
    return EvolutionHealthThresholdTriggerEngine()


def main():
    """主函数：处理命令行调用"""
    if len(sys.argv) < 2:
        print("用法:")
        print("  python evolution_health_threshold_trigger_engine.py status")
        print("  python evolution_health_threshold_trigger_engine.py check")
        print("  python evolution_health_threshold_trigger_engine.py thresholds")
        print("  python evolution_health_threshold_trigger_engine.py set <level> <value>")
        print("  python evolution_health_threshold_trigger_engine.py reset")
        print("  python evolution_health_threshold_trigger_engine.py history")
        print("  python evolution_health_threshold_trigger_engine.py stats")
        print("  python evolution_health_threshold_trigger_engine.py enable")
        print("  python evolution_health_threshold_trigger_engine.py disable")
        print("  python evolution_health_threshold_trigger_engine.py health")
        return

    engine = get_threshold_trigger_engine()
    command = sys.argv[1].lower()

    if command == "status":
        result = engine.get_threshold_status()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "check":
        result = engine.check_threshold_and_trigger()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "thresholds":
        result = engine.get_thresholds()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "set" and len(sys.argv) == 4:
        level = sys.argv[2].lower()
        try:
            value = int(sys.argv[3])
            engine.set_threshold(level, value)
            print(f"已设置 {level} 阈值为 {value}")
        except ValueError as e:
            print(f"设置失败: {e}")

    elif command == "reset":
        engine.reset_thresholds()
        print("已重置阈值为默认值")
        print(json.dumps(engine.get_thresholds(), ensure_ascii=False, indent=2))

    elif command == "history":
        result = engine.get_trigger_history()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "stats":
        result = engine.get_statistics()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "enable":
        engine.enable()
        print("已启用阈值触发")

    elif command == "disable":
        engine.disable()
        print("已禁用阈值触发")

    elif command == "health":
        result = engine.health_check()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    else:
        print(f"未知命令: {command}")
        print("可用命令: status, check, thresholds, set, reset, history, stats, enable, disable, health")


if __name__ == "__main__":
    main()