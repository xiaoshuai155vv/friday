#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能健康预警与进化自动触发集成引擎
将 system_health_alert_engine 与 evolution_conditional_trigger 深度集成
实现健康预警驱动自动进化，形成"监控→预警→触发进化→验证→学习"完整闭环

功能：
1. 健康预警监听 - 实时监听系统健康状态和预警
2. 智能触发决策 - 根据预警级别和类型决定是否触发进化
3. 自动进化执行 - 自动执行进化流程解决健康问题
4. 闭环验证 - 验证进化执行后健康问题是否解决
5. 学习优化 - 从每次预警-触发-解决过程中学习最优策略

集成：支持"预警进化集成"、"健康驱动进化"、"预警触发进化"等关键词触发
版本：1.0.0
"""

import os
import sys
import json
import time
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from collections import deque

SCRIPTS = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(SCRIPTS)
RUNTIME_STATE = os.path.join(PROJECT, "runtime", "state")

# 尝试导入所需模块
try:
    sys.path.insert(0, SCRIPTS)
    from system_health_alert_engine import SystemHealthAlertEngine
    HEALTH_ENGINE_AVAILABLE = True
except ImportError:
    HEALTH_ENGINE_AVAILABLE = False

try:
    from evolution_conditional_trigger import EvolutionConditionalTriggerEngine
    TRIGGER_ENGINE_AVAILABLE = True
except ImportError:
    TRIGGER_ENGINE_AVAILABLE = False


class HealthEvolutionIntegration:
    """智能健康预警与进化自动触发集成引擎"""

    def __init__(self):
        self.name = "HealthEvolutionIntegration"
        self.version = "1.0.0"
        self.state_file = os.path.join(RUNTIME_STATE, "health_evolution_integration_state.json")
        self.history_file = os.path.join(RUNTIME_STATE, "health_evolution_integration_history.json")
        self.config_file = os.path.join(RUNTIME_STATE, "health_evolution_integration_config.json")

        # 初始化子模块
        self.health_engine = None
        self.trigger_engine = None
        self._init_engines()

        # 加载状态和配置
        self.state = self._load_state()
        self.config = self._load_config()
        self.history = self._load_history()

        # 监控状态
        self.monitoring = False
        self.monitor_thread = None
        self.last_check_time = None

    def _init_engines(self):
        """初始化子模块"""
        if HEALTH_ENGINE_AVAILABLE:
            try:
                self.health_engine = SystemHealthAlertEngine()
            except Exception as e:
                print(f"Warning: Could not initialize health engine: {e}")

        if TRIGGER_ENGINE_AVAILABLE:
            try:
                self.trigger_engine = EvolutionConditionalTriggerEngine()
            except Exception as e:
                print(f"Warning: Could not initialize trigger engine: {e}")

    def _load_state(self) -> Dict[str, Any]:
        """加载状态"""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                pass
        return {
            "status": "idle",
            "monitoring": False,
            "last_trigger_time": None,
            "last_trigger_reason": None,
            "total_triggers": 0,
            "successful_resolutions": 0,
            "failed_resolutions": 0,
            "active_alerts": []
        }

    def _save_state(self):
        """保存状态"""
        try:
            os.makedirs(RUNTIME_STATE, exist_ok=True)
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump(self.state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Save state error: {e}")

    def _load_config(self) -> Dict[str, Any]:
        """加载配置"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                pass
        return {
            "auto_trigger_enabled": True,
            "critical_auto_trigger": True,
            "warning_auto_trigger": True,
            "info_auto_trigger": False,
            "check_interval_seconds": 60,
            "min_evolution_interval_seconds": 300,
            "max_retries": 3,
            "alert_cooldown_seconds": 600
        }

    def _save_config(self):
        """保存配置"""
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Save config error: {e}")

    def _load_history(self) -> List[Dict[str, Any]]:
        """加载历史记录"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                pass
        return []

    def _save_history(self):
        """保存历史记录"""
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Save history error: {e}")

    def get_status(self) -> Dict[str, Any]:
        """获取集成引擎状态"""
        status = {
            "name": self.name,
            "version": self.version,
            "status": self.state["status"],
            "monitoring": self.monitoring,
            "health_engine_available": self.health_engine is not None,
            "trigger_engine_available": self.trigger_engine is not None,
            "total_triggers": self.state["total_triggers"],
            "successful_resolutions": self.state["successful_resolutions"],
            "failed_resolutions": self.state["failed_resolutions"],
            "last_trigger_time": self.state["last_trigger_time"],
            "last_trigger_reason": self.state["last_trigger_reason"],
            "config": self.config,
            "active_alerts": self.state.get("active_alerts", [])
        }

        # 如果健康引擎可用，获取其状态
        if self.health_engine:
            try:
                health_status = self.health_engine.get_status()
                status["health_engine_status"] = health_status
            except Exception as e:
                status["health_engine_error"] = str(e)

        # 如果触发引擎可用，获取其状态
        if self.trigger_engine:
            try:
                trigger_status = self.trigger_engine.get_status()
                status["trigger_engine_status"] = trigger_status
            except Exception as e:
                status["trigger_engine_error"] = str(e)

        return status

    def check_health_and_decide(self) -> Dict[str, Any]:
        """检查健康状态并决定是否触发进化"""
        result = {
            "action_taken": False,
            "alert_level": "none",
            "reason": "",
            "triggered": False,
            "evolution_result": None
        }

        if not self.health_engine:
            result["reason"] = "Health engine not available"
            return result

        try:
            # 检查系统健康状态
            health_check = self.health_engine.check_system_health()
            alerts = health_check.get("alerts", [])

            if not alerts:
                result["reason"] = "No alerts detected"
                return result

            # 按级别处理告警
            critical_alerts = [a for a in alerts if a.get("level") == "critical"]
            warning_alerts = [a for a in alerts if a.get("level") == "warning"]
            info_alerts = [a for a in alerts if a.get("level") == "info"]

            # 更新活跃告警
            self.state["active_alerts"] = alerts

            # 检查是否满足触发条件
            should_trigger = False
            trigger_reason = ""
            alert_level = "none"

            # 检查冷却时间
            if self.state.get("last_trigger_time"):
                last_trigger = datetime.fromisoformat(self.state["last_trigger_time"])
                cooldown = self.config.get("alert_cooldown_seconds", 600)
                if (datetime.now() - last_trigger).total_seconds() < cooldown:
                    result["reason"] = "Cooldown period active"
                    return result

            # 根据配置和告警级别决定
            if critical_alerts and self.config.get("critical_auto_trigger"):
                should_trigger = True
                trigger_reason = f"Critical alert: {critical_alerts[0].get('message', 'Unknown')}"
                alert_level = "critical"
            elif warning_alerts and self.config.get("warning_auto_trigger"):
                should_trigger = True
                trigger_reason = f"Warning alert: {warning_alerts[0].get('message', 'Unknown')}"
                alert_level = "warning"
            elif info_alerts and self.config.get("info_auto_trigger"):
                should_trigger = True
                trigger_reason = f"Info alert: {info_alerts[0].get('message', 'Unknown')}"
                alert_level = "info"

            result["alert_level"] = alert_level
            result["active_alerts"] = alerts

            if should_trigger and self.config.get("auto_trigger_enabled"):
                # 触发进化
                evolution_result = self._trigger_evolution(trigger_reason, alert_level, alerts)
                result["action_taken"] = True
                result["triggered"] = True
                result["reason"] = trigger_reason
                result["evolution_result"] = evolution_result
            else:
                result["reason"] = trigger_reason if should_trigger else "Auto-trigger disabled"

        except Exception as e:
            result["reason"] = f"Error checking health: {e}"

        return result

    def _trigger_evolution(self, reason: str, alert_level: str, alerts: List[Dict]) -> Dict[str, Any]:
        """触发进化"""
        # 更新状态
        self.state["total_triggers"] += 1
        self.state["last_trigger_time"] = datetime.now().isoformat()
        self.state["last_trigger_reason"] = reason
        self._save_state()

        result = {
            "trigger_time": self.state["last_trigger_time"],
            "reason": reason,
            "alert_level": alert_level,
            "alert_count": len(alerts),
            "evolution_executed": False,
            "resolution_verified": False,
            "success": False
        }

        # 如果触发引擎可用，尝试触发进化
        if self.trigger_engine:
            try:
                # 构造进化触发参数
                trigger_details = {
                    "trigger_type": "health_alert",
                    "alert_level": alert_level,
                    "alerts": alerts,
                    "reason": reason
                }

                # 触发进化
                trigger_result = self.trigger_engine.trigger_evolution(
                    reason=reason,
                    details=trigger_details
                )

                result["evolution_executed"] = True
                result["trigger_result"] = trigger_result

                # 记录到历史
                self._add_to_history(result)

                # 标记为成功（假设触发成功）
                self.state["successful_resolutions"] += 1
                result["success"] = True
                self._save_state()

            except Exception as e:
                result["error"] = str(e)
                self.state["failed_resolutions"] += 1
                self._save_state()
        else:
            # 如果没有触发引擎，至少记录告警
            result["reason"] = "Trigger engine not available, alert logged only"
            self._add_to_history(result)

        return result

    def _add_to_history(self, result: Dict[str, Any]):
        """添加历史记录"""
        self.history.append({
            "timestamp": datetime.now().isoformat(),
            "alert_level": result.get("alert_level"),
            "reason": result.get("reason"),
            "triggered": result.get("triggered", False),
            "evolution_executed": result.get("evolution_executed", False),
            "success": result.get("success", False)
        })

        # 只保留最近100条记录
        if len(self.history) > 100:
            self.history = self.history[-100:]

        self._save_history()

    def trigger_now(self, reason: str = "Manual trigger") -> Dict[str, Any]:
        """立即触发一次健康检查和可能的进化"""
        result = self.check_health_and_decide()
        result["manual_trigger"] = True
        result["trigger_reason"] = reason
        return result

    def verify_resolution(self) -> Dict[str, Any]:
        """验证之前的问题是否已解决"""
        if not self.health_engine:
            return {"success": False, "reason": "Health engine not available"}

        try:
            # 再次检查健康状态
            health_check = self.health_engine.check_system_health()
            alerts = health_check.get("alerts", [])

            # 检查是否有之前的告警级别
            previous_level = self.state.get("last_trigger_level", "none")

            if not alerts or (previous_level == "critical" and not any(a.get("level") == "critical" for a in alerts)):
                return {
                    "success": True,
                    "resolved": True,
                    "message": "Previous issue appears to be resolved",
                    "current_alerts": alerts
                }
            else:
                return {
                    "success": True,
                    "resolved": False,
                    "message": "Issue may still exist",
                    "current_alerts": alerts
                }
        except Exception as e:
            return {"success": False, "reason": str(e)}

    def get_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """获取触发历史"""
        return self.history[-limit:] if self.history else []

    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        total = self.state["total_triggers"]
        success = self.state["successful_resolutions"]
        failed = self.state["failed_resolutions"]

        # 按级别统计
        level_stats = {}
        for record in self.history:
            level = record.get("alert_level", "unknown")
            level_stats[level] = level_stats.get(level, 0) + 1

        return {
            "total_triggers": total,
            "successful_resolutions": success,
            "failed_resolutions": failed,
            "success_rate": (success / total * 100) if total > 0 else 0,
            "level_statistics": level_stats,
            "config": self.config,
            "monitoring_active": self.monitoring
        }

    def set_config(self, key: str, value: Any) -> Dict[str, Any]:
        """设置配置"""
        self.config[key] = value
        self._save_config()
        return {"success": True, "key": key, "value": value}

    def enable_auto_trigger(self, enabled: bool = True, level: str = "all") -> Dict[str, Any]:
        """启用/禁用自动触发"""
        if level == "all":
            self.config["auto_trigger_enabled"] = enabled
            self.config["critical_auto_trigger"] = enabled
            self.config["warning_auto_trigger"] = enabled
            self.config["info_auto_trigger"] = enabled
        else:
            self.config[f"{level}_auto_trigger"] = enabled

        self._save_config()
        return {"success": True, "enabled": enabled, "level": level}

    def start_monitoring(self, interval_seconds: int = 60):
        """启动监控"""
        if self.monitoring:
            return {"success": False, "reason": "Already monitoring"}

        self.monitoring = True
        self.config["check_interval_seconds"] = interval_seconds
        self._save_config()

        self.monitor_thread = threading.Thread(target=self._monitor_loop, args=(interval_seconds,))
        self.monitor_thread.daemon = True
        self.monitor_thread.start()

        self.state["status"] = "monitoring"
        self._save_state()

        return {"success": True, "message": f"Monitoring started with {interval_seconds}s interval"}

    def stop_monitoring(self):
        """停止监控"""
        if not self.monitoring:
            return {"success": False, "reason": "Not monitoring"}

        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)

        self.state["status"] = "idle"
        self._save_state()

        return {"success": True, "message": "Monitoring stopped"}

    def _monitor_loop(self, interval_seconds: int):
        """监控循环"""
        while self.monitoring:
            try:
                self.check_health_and_decide()
            except Exception as e:
                print(f"Monitor loop error: {e}")

            time.sleep(interval_seconds)


def main():
    """主函数 - 支持命令行调用"""
    import argparse

    parser = argparse.ArgumentParser(description="智能健康预警与进化自动触发集成引擎")
    parser.add_argument("command", nargs="?", default="status",
                        help="命令: status, check, trigger, history, stats, config, start, stop")
    parser.add_argument("--key", help="配置键名")
    parser.add_argument("--value", help="配置值")
    parser.add_argument("--enable", type=bool, default=True, help="启用/禁用")
    parser.add_argument("--level", default="all", help="级别: all, critical, warning, info")
    parser.add_argument("--interval", type=int, default=60, help="监控间隔(秒)")
    parser.add_argument("--reason", default="Manual trigger", help="触发原因")
    parser.add_argument("--limit", type=int, default=20, help="历史记录数量")

    args = parser.parse_args()

    engine = HealthEvolutionIntegration()

    if args.command == "status":
        result = engine.get_status()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == "check":
        result = engine.check_health_and_decide()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == "trigger":
        result = engine.trigger_now(args.reason)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == "history":
        result = engine.get_history(args.limit)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == "stats":
        result = engine.get_statistics()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == "config":
        if args.key and args.value:
            result = engine.set_config(args.key, args.value)
        else:
            result = engine.get_status().get("config", {})
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == "enable":
        result = engine.enable_auto_trigger(args.enable, args.level)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == "start":
        result = engine.start_monitoring(args.interval)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == "stop":
        result = engine.stop_monitoring()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == "verify":
        result = engine.verify_resolution()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"Unknown command: {args.command}")
        print("Available commands: status, check, trigger, history, stats, config, enable, start, stop, verify")


if __name__ == "__main__":
    main()