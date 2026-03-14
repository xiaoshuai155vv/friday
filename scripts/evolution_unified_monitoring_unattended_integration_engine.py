#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环统一监控驾驶舱与完全无人值守进化环深度集成引擎
====================================================================

round 397: 将 round 396 的统一监控驾驶舱与 round 382/383 的完全无人值守进化环深度集成

功能：
1. 集成统一监控驾驶舱(round 396)的监控数据获取能力
2. 集成完全无人值守进化环(round 382)的自动触发执行能力
3. 实现基于监控数据的智能预警与自动响应
4. 实现监控-分析-决策-执行-验证的完整无人值守闭环

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
    from evolution_cockpit_unified_monitoring_integration_engine import (
        EvolutionCockpitUnifiedMonitoringIntegrationEngine,
        get_integration_engine as get_monitoring_engine
    )
except ImportError:
    EvolutionCockpitUnifiedMonitoringIntegrationEngine = None

try:
    from evolution_autonomous_unattended_enhancement_engine import (
        EvolutionAutonomousUnattendedEngine
    )
except ImportError:
    EvolutionAutonomousUnattendedEngine = None


class EvolutionUnifiedMonitoringUnattendedIntegrationEngine:
    """统一监控驾驶舱与完全无人值守进化环深度集成引擎"""

    VERSION = "1.0.0"

    def __init__(self):
        """初始化深度集成引擎"""
        self.monitoring_engine = None
        self.unattended_engine = None
        self.integration_state = {
            "enabled": False,
            "auto_mode": False,
            "last_integration_cycle": None,
            "trigger_count": 0,
            "success_count": 0,
            "last_error": None
        }
        self._load_engines()
        self._ensure_directories()

    def _ensure_directories(self):
        """确保必要的目录存在"""
        runtime_dir = os.path.join(PROJECT_ROOT, "runtime", "state")
        os.makedirs(runtime_dir, exist_ok=True)

    def _load_engines(self):
        """加载依赖引擎"""
        # 加载统一监控驾驶舱引擎
        if EvolutionCockpitUnifiedMonitoringIntegrationEngine:
            try:
                self.monitoring_engine = get_monitoring_engine()
            except Exception as e:
                self._safe_print(f"加载监控引擎失败: {e}")
                self.monitoring_engine = None
        else:
            self._safe_print("警告: 未找到 EvolutionCockpitUnifiedMonitoringIntegrationEngine")

        # 加载完全无人值守进化引擎
        if EvolutionAutonomousUnattendedEngine:
            try:
                self.unattended_engine = EvolutionAutonomousUnattendedEngine()
            except Exception as e:
                self._safe_print(f"加载无人值守引擎失败: {e}")
                self.unattended_engine = None
        else:
            self._safe_print("警告: 未找到 EvolutionAutonomousUnattendedEngine")

    @staticmethod
    def _safe_print(text: str):
        """安全打印"""
        try:
            print(text)
        except Exception:
            pass

    def _get_integration_state(self) -> Dict[str, Any]:
        """获取当前集成状态"""
        state = {
            "enabled": self.integration_state["enabled"],
            "auto_mode": self.integration_state["auto_mode"],
            "last_cycle": self.integration_state["last_integration_cycle"],
            "trigger_count": self.integration_state["trigger_count"],
            "success_count": self.integration_state["success_count"],
            "last_error": self.integration_state["last_error"],
            "engines_loaded": {
                "monitoring": self.monitoring_engine is not None,
                "unattended": self.unattended_engine is not None
            }
        }
        return state

    def get_status(self) -> Dict[str, Any]:
        """获取深度集成引擎整体状态"""
        status = self._get_integration_state()

        # 获取各引擎状态
        if self.monitoring_engine:
            try:
                monitoring_status = self.monitoring_engine.get_integrated_status()
                status["monitoring_engine"] = monitoring_status
            except Exception as e:
                status["monitoring_engine_error"] = str(e)

        if self.unattended_engine:
            try:
                unattended_status = self.unattended_engine.get_status()
                status["unattended_engine"] = unattended_status
            except Exception as e:
                status["unattended_engine_error"] = str(e)

        return status

    def get_dashboard_data(self) -> Dict[str, Any]:
        """获取集成仪表盘数据"""
        dashboard = {
            "timestamp": datetime.now().isoformat(),
            "integration_version": self.VERSION,
            "state": self._get_integration_state()
        }

        # 合并监控引擎仪表盘数据
        if self.monitoring_engine:
            try:
                monitoring_dashboard = self.monitoring_engine.get_dashboard_data()
                dashboard["monitoring_dashboard"] = monitoring_dashboard
            except Exception as e:
                dashboard["monitoring_error"] = str(e)

        # 合并无人值守引擎指标
        if self.unattended_engine:
            try:
                unattended_metrics = self.unattended_engine.get_metrics()
                dashboard["unattended_metrics"] = unattended_metrics
            except Exception as e:
                dashboard["unattended_error"] = str(e)

        return dashboard

    def enable_auto_mode(self) -> Dict[str, Any]:
        """启用自动模式：基于监控数据自动触发进化"""
        if not self.monitoring_engine or not self.unattended_engine:
            return {
                "success": False,
                "error": "依赖引擎未加载"
            }

        # 启用无人值守引擎的自动模式
        try:
            result = self.unattended_engine.enable_auto_mode()
            self.integration_state["auto_mode"] = True
            self.integration_state["enabled"] = True
            self._save_state()
            return {
                "success": True,
                "message": "已启用自动模式：监控数据将驱动无人值守进化",
                "unattended_result": result
            }
        except Exception as e:
            self.integration_state["last_error"] = str(e)
            return {
                "success": False,
                "error": str(e)
            }

    def disable_auto_mode(self) -> Dict[str, Any]:
        """禁用自动模式"""
        if self.unattended_engine:
            try:
                result = self.unattended_engine.disable_auto_mode()
            except Exception as e:
                result = {"error": str(e)}

        self.integration_state["auto_mode"] = False
        self._save_state()
        return {
            "success": True,
            "message": "已禁用自动模式",
            "unattended_result": result
        }

    def _analyze_monitoring_data(self, monitoring_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析监控数据，确定是否需要触发进化"""
        analysis = {
            "should_trigger": False,
            "reason": "",
            "trigger_conditions": [],
            "priority": "normal"
        }

        # 分析健康分数
        health_score = monitoring_data.get("health_score", 100)
        if health_score < 50:
            analysis["should_trigger"] = True
            analysis["reason"] = f"健康分数过低: {health_score}"
            analysis["trigger_conditions"].append("low_health")
            analysis["priority"] = "high"

        # 分析预警列表
        warnings = monitoring_data.get("warnings", [])
        critical_warnings = [w for w in warnings if w.get("level") == "critical"]
        if critical_warnings:
            analysis["should_trigger"] = True
            analysis["reason"] = f"存在 {len(critical_warnings)} 个严重预警"
            analysis["trigger_conditions"].append("critical_warning")
            analysis["priority"] = "critical"

        # 分析引擎状态
        engine_status = monitoring_data.get("engine_status", {})
        failed_engines = [name for name, status in engine_status.items()
                         if status.get("status") == "failed"]
        if failed_engines:
            analysis["should_trigger"] = True
            analysis["reason"] = f"存在 {len(failed_engines)} 个故障引擎"
            analysis["trigger_conditions"].append("engine_failure")
            analysis["priority"] = "high"

        return analysis

    def _run_integration_cycle(self) -> Dict[str, Any]:
        """运行监控-执行集成循环"""
        cycle_result = {
            "timestamp": datetime.now().isoformat(),
            "success": False,
            "stages": {}
        }

        # 阶段1: 获取监控数据
        if self.monitoring_engine:
            try:
                monitoring_data = self.monitoring_engine.get_integrated_status()
                cycle_result["stages"]["monitoring"] = {
                    "success": True,
                    "data": monitoring_data
                }
            except Exception as e:
                cycle_result["stages"]["monitoring"] = {
                    "success": False,
                    "error": str(e)
                }
                cycle_result["error"] = f"监控数据获取失败: {e}"
                return cycle_result
        else:
            cycle_result["error"] = "监控引擎未加载"
            return cycle_result

        # 阶段2: 分析监控数据
        analysis = self._analyze_monitoring_data(monitoring_data)
        cycle_result["stages"]["analysis"] = {
            "success": True,
            "result": analysis
        }

        # 阶段3: 根据分析结果决定是否触发进化
        if analysis["should_trigger"] and self.unattended_engine:
            try:
                # 使用无人值守引擎的触发检查
                trigger_result = self.unattended_engine.check_and_trigger()
                cycle_result["stages"]["trigger"] = {
                    "success": True,
                    "triggered": analysis["should_trigger"],
                    "analysis": analysis,
                    "unattended_result": trigger_result
                }
                self.integration_state["trigger_count"] += 1

                # 检查触发结果
                if trigger_result.get("triggered"):
                    self.integration_state["success_count"] += 1

            except Exception as e:
                cycle_result["stages"]["trigger"] = {
                    "success": False,
                    "error": str(e)
                }
                self.integration_state["last_error"] = str(e)
        else:
            cycle_result["stages"]["trigger"] = {
                "success": True,
                "triggered": False,
                "reason": "无需触发"
            }

        # 阶段4: 更新集成状态
        self.integration_state["last_integration_cycle"] = datetime.now().isoformat()
        self._save_state()

        cycle_result["success"] = True
        return cycle_result

    def run_full_integration_cycle(self) -> Dict[str, Any]:
        """运行完整的监控-执行集成闭环"""
        # 获取仪表盘数据
        dashboard = self.get_dashboard_data()

        # 运行集成循环
        cycle_result = self._run_integration_cycle()

        # 获取最终状态
        final_status = self.get_status()

        return {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "dashboard": dashboard,
            "cycle_result": cycle_result,
            "final_status": final_status
        }

    def check_monitoring_and_trigger(self) -> Dict[str, Any]:
        """检查监控状态并根据需要触发进化（单步检查）"""
        if not self.monitoring_engine or not self.unattended_engine:
            return {
                "success": False,
                "error": "依赖引擎未加载"
            }

        # 获取监控数据
        monitoring_data = self.monitoring_engine.get_integrated_status()

        # 分析数据
        analysis = self._analyze_monitoring_data(monitoring_data)

        result = {
            "timestamp": datetime.now().isoformat(),
            "monitoring_data": monitoring_data,
            "analysis": analysis,
            "triggered": False,
            "trigger_result": None
        }

        # 如果需要触发，则执行
        if analysis["should_trigger"]:
            try:
                trigger_result = self.unattended_engine.check_and_trigger()
                result["triggered"] = True
                result["trigger_result"] = trigger_result
                self.integration_state["trigger_count"] += 1

                if trigger_result.get("triggered"):
                    self.integration_state["success_count"] += 1

                self._save_state()
            except Exception as e:
                result["error"] = str(e)
                self.integration_state["last_error"] = str(e)

        return result

    def _save_state(self):
        """保存集成状态"""
        state_file = os.path.join(
            PROJECT_ROOT, "runtime", "state",
            "integration_engine_state.json"
        )
        try:
            with open(state_file, "w", encoding="utf-8") as f:
                json.dump(self.integration_state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self._safe_print(f"保存状态失败: {e}")

    def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        health = {
            "engine": "EvolutionUnifiedMonitoringUnattendedIntegrationEngine",
            "version": self.VERSION,
            "healthy": True,
            "components": {}
        }

        # 检查监控引擎
        if self.monitoring_engine:
            health["components"]["monitoring_engine"] = "ok"
        else:
            health["components"]["monitoring_engine"] = "not_loaded"
            health["healthy"] = False

        # 检查无人值守引擎
        if self.unattended_engine:
            health["components"]["unattended_engine"] = "ok"
        else:
            health["components"]["unattended_engine"] = "not_loaded"
            health["healthy"] = False

        # 检查集成状态
        health["components"]["integration_state"] = "ok" if self.integration_state["enabled"] else "disabled"

        return health


def get_integration_engine() -> EvolutionUnifiedMonitoringUnattendedIntegrationEngine:
    """获取深度集成引擎单例"""
    return EvolutionUnifiedMonitoringUnattendedIntegrationEngine()


def main():
    """主函数：处理命令行调用"""
    if len(sys.argv) < 2:
        print("用法:")
        print("  python evolution_unified_monitoring_unattended_integration_engine.py status")
        print("  python evolution_unified_monitoring_unattended_integration_engine.py dashboard")
        print("  python evolution_unified_monitoring_unattended_integration_engine.py enable")
        print("  python evolution_unified_monitoring_unattended_integration_engine.py disable")
        print("  python evolution_unified_monitoring_unattended_integration_engine.py cycle")
        print("  python evolution_unified_monitoring_unattended_integration_engine.py check_trigger")
        print("  python evolution_unified_monitoring_unattended_integration_engine.py health")
        return

    engine = get_integration_engine()
    command = sys.argv[1].lower()

    if command == "status":
        result = engine.get_status()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "dashboard":
        result = engine.get_dashboard_data()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "enable":
        result = engine.enable_auto_mode()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "disable":
        result = engine.disable_auto_mode()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "cycle":
        result = engine.run_full_integration_cycle()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "check_trigger" or command == "check":
        result = engine.check_monitoring_and_trigger()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "health":
        result = engine.health_check()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    else:
        print(f"未知命令: {command}")
        print("可用命令: status, dashboard, enable, disable, cycle, check_trigger, health")


if __name__ == "__main__":
    main()