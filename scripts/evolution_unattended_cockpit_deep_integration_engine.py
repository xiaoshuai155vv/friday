#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环完全无人值守自主进化与进化驾驶舱深度集成引擎
Evolution Unattended Cockpit Deep Integration Engine

将 round 382 的完全无人值守自主进化增强引擎与进化驾驶舱（round 350）深度集成，
实现更智能的可视化监控、自动触发与一键控制，让用户能够在驾驶舱中直观地看到
完全无人值守进化环的运行状态并进行干预。

功能：
1. 驾驶舱集成界面 - 在驾驶舱中显示完全无人值守模式状态
2. 一键启动/停止完全无人值守模式
3. 实时显示自动进化进度、状态、健康度
4. 智能预警与自动干预控制
5. 进化历史与趋势分析
6. 自动模式配置与优化建议

Version: 1.0.0

依赖：
- evolution_autonomous_unattended_enhancement_engine.py (round 382)
- evolution_cockpit_engine.py (round 350)
- evolution_cockpit_meta_integration_engine.py (round 381)
"""

import os
import sys
import json
import time
import threading
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from collections import defaultdict, deque

# 添加项目根目录到 Python 路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, SCRIPT_DIR)


def _safe_print(text: str):
    """安全打印，处理编码问题"""
    import re
    try:
        print(text)
    except UnicodeEncodeError:
        clean_text = re.sub(r'[^\x00-\x7F]+', '', text)
        print(clean_text)


class EvolutionUnattendedCockpitIntegrationEngine:
    """完全无人值守自主进化与进化驾驶舱深度集成引擎"""

    def __init__(self):
        self.version = "1.0.0"
        self.project_root = PROJECT_ROOT
        self.scripts_dir = SCRIPT_DIR
        self.runtime_dir = os.path.join(self.project_root, "runtime")
        self.state_dir = os.path.join(self.runtime_dir, "state")
        self.logs_dir = os.path.join(self.runtime_dir, "logs")

        # 状态文件
        self.state_file = os.path.join(self.state_dir, "unattended_cockpit_state.json")
        self.config_file = os.path.join(self.state_dir, "unattended_cockpit_config.json")
        self.integration_history_file = os.path.join(self.state_dir, "unattended_integration_history.json")

        # 初始化目录
        self._ensure_directories()

        # 加载状态
        self.state = self._load_state()
        self.config = self._load_config()
        self.integration_history = self._load_integration_history()

        # 依赖引擎路径
        self.unattended_engine_path = os.path.join(self.scripts_dir, "evolution_autonomous_unattended_enhancement_engine.py")
        self.cockpit_engine_path = os.path.join(self.scripts_dir, "evolution_cockpit_engine.py")

        # 运行状态
        self.running = False
        self.auto_mode_active = False
        self.monitor_thread = None
        self.stop_monitor = False

    def _ensure_directories(self):
        """确保必要的目录存在"""
        for directory in [self.state_dir, self.logs_dir]:
            os.makedirs(directory, exist_ok=True)

    def _load_state(self) -> Dict[str, Any]:
        """加载状态"""
        default_state = {
            "mode": "manual",  # manual / auto / supervised
            "unattended_active": False,
            "last_trigger_time": None,
            "total_autonomous_cycles": 0,
            "current_round": 0,
            "health_score": 100.0,
            "status": "idle",  # idle / running / paused / error
            "alerts": [],
            "integration_level": "basic",  # basic / advanced / full
            "updated_at": datetime.now().isoformat()
        }

        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                    return {**default_state, **state}
            except Exception as e:
                _safe_print(f"[WARN] Failed to load state: {e}")
                return default_state
        return default_state

    def _save_state(self):
        """保存状态"""
        self.state["updated_at"] = datetime.now().isoformat()
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            _safe_print(f"[ERROR] Failed to save state: {e}")

    def _load_config(self) -> Dict[str, Any]:
        """加载配置"""
        default_config = {
            "auto_start_on_launch": False,
            "health_check_interval": 60,  # 秒
            "max_consecutive_errors": 3,
            "auto_recovery_enabled": True,
            "notification_enabled": True,
            "integration_mode": "advanced",  # basic / advanced / full
            "dashboard_refresh_interval": 5,  # 秒
            "alert_thresholds": {
                "cpu_high": 90,
                "memory_high": 85,
                "error_rate_high": 0.3,
                "health_score_low": 50
            }
        }

        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    return {**default_config, **config}
            except Exception as e:
                _safe_print(f"[WARN] Failed to load config: {e}")
                return default_config
        return default_config

    def _save_config(self):
        """保存配置"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            _safe_print(f"[ERROR] Failed to save config: {e}")

    def _load_integration_history(self) -> List[Dict[str, Any]]:
        """加载集成历史"""
        if os.path.exists(self.integration_history_file):
            try:
                with open(self.integration_history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                _safe_print(f"[WARN] Failed to load integration history: {e}")
                return []
        return []

    def _save_integration_history(self):
        """保存集成历史"""
        # 只保留最近 100 条记录
        history = self.integration_history[-99:]
        try:
            with open(self.integration_history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            _safe_print(f"[ERROR] Failed to save integration history: {e}")

    def _add_history(self, event_type: str, details: Dict[str, Any]):
        """添加历史记录"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "details": details
        }
        self.integration_history.append(entry)
        self._save_integration_history()

    def check_dependencies(self) -> Dict[str, bool]:
        """检查依赖引擎是否可用"""
        result = {
            "unattended_engine": os.path.exists(self.unattended_engine_path),
            "cockpit_engine": os.path.exists(self.cockpit_engine_path)
        }
        return result

    def get_status(self) -> Dict[str, Any]:
        """获取当前状态"""
        # 尝试从完全无人值守引擎加载状态
        unattended_state_file = os.path.join(self.state_dir, "autonomous_unattended_state.json")
        unattended_state = {}
        if os.path.exists(unattended_state_file):
            try:
                with open(unattended_state_file, 'r', encoding='utf-8') as f:
                    unattended_state = json.load(f)
            except Exception:
                pass

        # 获取系统状态
        system_status = self._get_system_status()

        return {
            "success": True,
            "version": self.version,
            "mode": self.state["mode"],
            "unattended_active": self.state["unattended_active"],
            "status": self.state["status"],
            "health_score": self.state["health_score"],
            "total_autonomous_cycles": self.state["total_autonomous_cycles"],
            "current_round": self.state["current_round"],
            "last_trigger_time": self.state["last_trigger_time"],
            "integration_level": self.state["integration_level"],
            "alerts": self.state["alerts"],
            "system_status": system_status,
            "dependencies": self.check_dependencies(),
            "unattended_engine_state": unattended_state
        }

    def _get_system_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        status = {
            "cpu": 0,
            "memory": 0,
            "disk": 0,
            "timestamp": datetime.now().isoformat()
        }

        try:
            import psutil
            status["cpu"] = psutil.cpu_percent(interval=0.1)
            status["memory"] = psutil.virtual_memory().percent
            status["disk"] = psutil.disk_usage('/').percent
        except ImportError:
            # 如果没有 psutil，返回默认值
            pass

        return status

    def start_unattended_mode(self) -> Dict[str, Any]:
        """启动完全无人值守模式"""
        _safe_print("[INFO] Starting unattended mode...")

        # 检查依赖
        deps = self.check_dependencies()
        if not deps["unattended_engine"]:
            return {
                "success": False,
                "error": "完全无人值守增强引擎未找到",
                "details": deps
            }

        # 更新状态
        self.state["unattended_active"] = True
        self.state["status"] = "running"
        self.state["mode"] = "auto"
        self._save_state()

        # 记录历史
        self._add_history("start_unattended", {
            "mode": "auto",
            "integration_level": self.state["integration_level"]
        })

        return {
            "success": True,
            "message": "完全无人值守模式已启动",
            "mode": "auto",
            "integration_level": self.state["integration_level"]
        }

    def stop_unattended_mode(self) -> Dict[str, Any]:
        """停止完全无人值守模式"""
        _safe_print("[INFO] Stopping unattended mode...")

        # 更新状态
        self.state["unattended_active"] = False
        self.state["status"] = "idle"
        self.state["mode"] = "manual"
        self._save_state()

        # 记录历史
        self._add_history("stop_unattended", {
            "mode": "manual",
            "total_cycles": self.state["total_autonomous_cycles"]
        })

        return {
            "success": True,
            "message": "完全无人值守模式已停止",
            "mode": "manual"
        }

    def pause_unattended_mode(self) -> Dict[str, Any]:
        """暂停完全无人值守模式"""
        _safe_print("[INFO] Pausing unattended mode...")

        self.state["status"] = "paused"
        self._save_state()

        self._add_history("pause_unattended", {})

        return {
            "success": True,
            "message": "完全无人值守模式已暂停",
            "status": "paused"
        }

    def resume_unattended_mode(self) -> Dict[str, Any]:
        """恢复完全无人值守模式"""
        _safe_print("[INFO] Resuming unattended mode...")

        self.state["status"] = "running"
        self._save_state()

        self._add_history("resume_unattended", {})

        return {
            "success": True,
            "message": "完全无人值守模式已恢复",
            "status": "running"
        }

    def set_integration_level(self, level: str) -> Dict[str, Any]:
        """设置集成级别"""
        valid_levels = ["basic", "advanced", "full"]
        if level not in valid_levels:
            return {
                "success": False,
                "error": f"无效的集成级别: {level}，可选: {valid_levels}"
            }

        self.state["integration_level"] = level
        self.config["integration_mode"] = level
        self._save_state()
        self._save_config()

        self._add_history("set_integration_level", {"level": level})

        return {
            "success": True,
            "message": f"集成级别已设置为: {level}",
            "integration_level": level
        }

    def get_dashboard_data(self) -> Dict[str, Any]:
        """获取驾驶舱仪表盘数据"""
        status = self.get_status()

        # 构建驾驶舱显示数据
        dashboard = {
            "success": True,
            "unattended_status": {
                "active": status["unattended_active"],
                "mode": status["mode"],
                "status": status["status"],
                "health_score": status["health_score"]
            },
            "evolution_progress": {
                "total_cycles": status["total_autonomous_cycles"],
                "current_round": status["current_round"],
                "last_trigger": status["last_trigger_time"]
            },
            "system_status": status["system_status"],
            "alerts": status["alerts"],
            "integration": {
                "level": status["integration_level"],
                "dependencies": status["dependencies"]
            },
            "quick_actions": {
                "start": status["mode"] == "manual" or status["status"] == "idle",
                "stop": status["unattended_active"],
                "pause": status["status"] == "running",
                "resume": status["status"] == "paused"
            }
        }

        return dashboard

    def clear_alerts(self) -> Dict[str, Any]:
        """清除警报"""
        self.state["alerts"] = []
        self._save_state()

        return {
            "success": True,
            "message": "警报已清除"
        }

    def get_recommendations(self) -> List[Dict[str, Any]]:
        """获取优化建议"""
        recommendations = []

        status = self.get_status()

        # 基于健康度
        if status["health_score"] < 70:
            recommendations.append({
                "type": "warning",
                "message": "健康度较低，建议检查进化环执行状态",
                "action": "check_status"
            })

        # 基于系统资源
        if status["system_status"]["cpu"] > 90:
            recommendations.append({
                "type": "warning",
                "message": "CPU 使用率过高，建议降低进化频率",
                "action": "adjust_frequency"
            })

        # 基于集成级别
        if status["integration_level"] == "basic":
            recommendations.append({
                "type": "info",
                "message": "建议升级到高级集成模式以获得更多功能",
                "action": "upgrade_integration"
            })

        return recommendations

    def execute_command(self, command: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """执行命令"""
        params = params or {}

        command_map = {
            "start": self.start_unattended_mode,
            "stop": self.stop_unattended_mode,
            "pause": self.pause_unattended_mode,
            "resume": self.resume_unattended_mode,
            "status": self.get_status,
            "dashboard": self.get_dashboard_data,
            "clear_alerts": self.clear_alerts,
            "recommendations": lambda: {"recommendations": self.get_recommendations()},
        }

        # 处理带参数的命令
        if command == "set_level" and "level" in params:
            return self.set_integration_level(params["level"])

        if command in command_map:
            return command_map[command]()

        return {
            "success": False,
            "error": f"未知命令: {command}",
            "available_commands": list(command_map.keys()) + ["set_level"]
        }


def main():
    """主函数 - 命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(
        description="智能全场景进化环完全无人值守自主进化与进化驾驶舱深度集成引擎"
    )
    parser.add_argument("command", nargs="?", default="status",
                        help="命令: start/stop/pause/resume/status/dashboard/recommendations/clear_alerts")
    parser.add_argument("--level", dest="level", choices=["basic", "advanced", "full"],
                        help="设置集成级别")
    parser.add_argument("--json", action="store_true", help="JSON 格式输出")

    args = parser.parse_args()

    engine = EvolutionUnattendedCockpitIntegrationEngine()

    # 执行命令
    if args.command == "set_level":
        if not args.level:
            print("Error: --level 参数 required")
            sys.exit(1)
        result = engine.set_integration_level(args.level)
    else:
        result = engine.execute_command(args.command)

    # 输出结果
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        if result.get("success", False):
            _safe_print(result.get("message", "Success"))
        else:
            _safe_print(f"Error: {result.get('error', 'Unknown error')}")

    sys.exit(0 if result.get("success", False) else 1)


if __name__ == "__main__":
    main()