#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化引擎集群驾驶舱深度集成引擎

将 round 384 的跨引擎深度健康自愈引擎与进化驾驶舱 round 350 深度集成，
实现可视化的跨引擎健康监控与一键自愈功能。

功能：
1. 驾驶舱内显示跨引擎健康态势
2. 驾驶舱内一键触发跨引擎协同自愈
3. 驾驶舱内显示元进化优化建议
4. 实现健康数据实时可视化
5. 实现一键自愈与优化联动

使用方法（直接运行）：
    python evolution_engine_cluster_cockpit_integration_engine.py dashboard       - 查看驾驶舱集成视图
    python evolution_engine_cluster_cockpit_integration_engine.py health         - 获取跨引擎健康态势
    python evolution_engine_cluster_cockpit_integration_engine.py self_heal       - 驾驶舱一键自愈
    python evolution_engine_cluster_cockpit_integration_engine.py visualize       - 可视化健康数据
    python evolution_engine_cluster_cockpit_integration_engine.py status         - 集成状态查询

Version: 1.0.0
"""

import os
import sys
import json
import time
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
RUNTIME_STATE = PROJECT_ROOT / "runtime" / "state"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"

# 确保目录存在
RUNTIME_STATE.mkdir(parents=True, exist_ok=True)


class EvolutionEngineCockpitIntegration:
    """进化引擎集群驾驶舱深度集成引擎"""

    def __init__(self):
        self.version = "1.0.0"
        self.state_file = RUNTIME_STATE / "evolution_engine_cockpit_integration_state.json"
        self.state = self._load_state()

        # 加载依赖模块
        self.cockpit_engine = None
        self.deep_health_engine = None
        self.load_dependencies()

    def load_dependencies(self):
        """加载依赖的引擎模块（通过 subprocess 调用）"""
        import sys

        # 检查深度健康引擎是否存在
        health_script = SCRIPTS_DIR / "evolution_engine_cluster_deep_health_meta_evolution_engine.py"
        if health_script.exists():
            self.deep_health_script = str(health_script)
            print(f"已找到深度健康引擎: {self.deep_health_script}")
        else:
            self.deep_health_script = None
            print(f"深度健康引擎未找到", file=sys.stderr)

        # 检查驾驶舱引擎是否存在
        cockpit_script = SCRIPTS_DIR / "evolution_cockpit_engine.py"
        if cockpit_script.exists():
            self.cockpit_script = str(cockpit_script)
            print(f"已找到进化驾驶舱引擎: {self.cockpit_script}")
        else:
            self.cockpit_script = None
            print(f"进化驾驶舱引擎未找到", file=sys.stderr)

    def _load_state(self) -> Dict[str, Any]:
        """加载状态"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return self._get_default_state()

    def _get_default_state(self) -> Dict[str, Any]:
        """获取默认状态"""
        return {
            "version": self.version,
            "integration_status": "initializing",
            "last_health_check": None,
            "last_self_heal": None,
            "cockpit_health_display": True,
            "one_click_heal_enabled": True,
            "health_metrics": {},
            "auto_refresh_interval": 30,
            "alerts": [],
            "heal_history": []
        }

    def _save_state(self):
        """保存状态"""
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存状态失败: {e}", file=sys.stderr)

    def get_dashboard(self) -> Dict[str, Any]:
        """获取驾驶舱集成视图"""
        import subprocess

        dashboard = {
            "integration_status": self.state.get("integration_status", "unknown"),
            "timestamp": datetime.now().isoformat(),
            "health_overview": None,
            "self_heal_status": None,
            "visualization": None
        }

        # 获取健康态势（通过 subprocess 调用）
        try:
            if self.deep_health_script:
                result = subprocess.run(
                    [sys.executable, self.deep_health_script, "health"],
                    cwd=str(PROJECT_ROOT),
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if result.returncode == 0 and result.stdout:
                    try:
                        dashboard["health_overview"] = json.loads(result.stdout)
                    except:
                        dashboard["health_overview"] = {"raw_output": result.stdout}
        except Exception as e:
            dashboard["health_overview"] = {"error": str(e)}

        # 获取自愈状态
        try:
            if self.deep_health_script:
                result = subprocess.run(
                    [sys.executable, self.deep_health_script, "status"],
                    cwd=str(PROJECT_ROOT),
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if result.returncode == 0 and result.stdout:
                    try:
                        dashboard["self_heal_status"] = json.loads(result.stdout)
                    except:
                        dashboard["self_heal_status"] = {"raw_output": result.stdout}
        except Exception as e:
            dashboard["self_heal_status"] = {"error": str(e)}

        # 可视化数据
        dashboard["visualization"] = {
            "health_score": dashboard.get("health_overview", {}).get("overall_score", 0),
            "engine_count": dashboard.get("health_overview", {}).get("engine_count", 0),
            "healthy_engines": dashboard.get("health_overview", {}).get("healthy_count", 0),
            "issues_found": dashboard.get("health_overview", {}).get("issue_count", 0),
            "last_heal": self.state.get("last_self_heal"),
            "alerts": self.state.get("alerts", [])
        }

        return dashboard

    def get_health(self) -> Dict[str, Any]:
        """获取跨引擎健康态势（集成到驾驶舱）"""
        import subprocess

        result = {
            "timestamp": datetime.now().isoformat(),
            "source": "evolution_engine_cluster_cockpit_integration",
            "integration": True
        }

        try:
            if self.deep_health_script:
                result_sub = subprocess.run(
                    [sys.executable, self.deep_health_script, "health"],
                    cwd=str(PROJECT_ROOT),
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if result_sub.returncode == 0 and result_sub.stdout:
                    try:
                        health = json.loads(result_sub.stdout)
                        result.update(health)
                        self.state["last_health_check"] = datetime.now().isoformat()
                        self.state["health_metrics"] = health
                        self._save_state()
                    except:
                        result["error"] = "解析失败"
            else:
                result["error"] = "深度健康引擎未加载"
        except Exception as e:
            result["error"] = str(e)

        return result

    def trigger_self_heal(self) -> Dict[str, Any]:
        """驾驶舱一键触发跨引擎协同自愈"""
        import subprocess

        result = {
            "timestamp": datetime.now().isoformat(),
            "action": "self_heal",
            "status": "started"
        }

        try:
            if self.deep_health_script:
                result_sub = subprocess.run(
                    [sys.executable, self.deep_health_script, "self_heal"],
                    cwd=str(PROJECT_ROOT),
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                if result_sub.returncode == 0 and result_sub.stdout:
                    try:
                        heal_result = json.loads(result_sub.stdout)
                        result.update(heal_result)
                        self.state["last_self_heal"] = datetime.now().isoformat()

                        # 记录自愈历史
                        heal_history = self.state.get("heal_history", [])
                        heal_history.append({
                            "timestamp": datetime.now().isoformat(),
                            "result": heal_result
                        })
                        # 保留最近 20 条记录
                        self.state["heal_history"] = heal_history[-20:]
                        self._save_state()
                    except:
                        result["error"] = "解析失败"
            else:
                result["status"] = "failed"
                result["error"] = "深度健康引擎未加载"
        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)

        return result

    def visualize(self) -> Dict[str, Any]:
        """可视化健康数据"""
        viz_data = {
            "timestamp": datetime.now().isoformat(),
            "visualization_type": "health_dashboard"
        }

        try:
            # 获取当前健康态势
            health = self.get_health()

            # 构建可视化数据结构
            viz_data["components"] = [
                {
                    "type": "gauge",
                    "name": "整体健康度",
                    "value": health.get("overall_score", 0),
                    "max": 100,
                    "unit": "%"
                },
                {
                    "type": "bar",
                    "name": "引擎健康分布",
                    "data": {
                        "healthy": health.get("healthy_count", 0),
                        "warning": health.get("warning_count", 0),
                        "critical": health.get("critical_count", 0)
                    }
                },
                {
                    "type": "timeline",
                    "name": "自愈历史",
                    "data": self.state.get("heal_history", [])[-10:]
                },
                {
                    "type": "alert_list",
                    "name": "当前告警",
                    "data": self.state.get("alerts", [])
                }
            ]

            viz_data["summary"] = {
                "total_engines": health.get("engine_count", 0),
                "healthy_engines": health.get("healthy_count", 0),
                "issues_detected": health.get("issue_count", 0),
                "auto_heal_enabled": self.state.get("one_click_heal_enabled", True)
            }

        except Exception as e:
            viz_data["error"] = str(e)

        return viz_data

    def get_status(self) -> Dict[str, Any]:
        """获取集成状态"""
        status = {
            "version": self.version,
            "integration_status": self.state.get("integration_status", "unknown"),
            "dependencies": {
                "cockpit_engine": self.cockpit_engine is not None,
                "deep_health_engine": self.deep_health_engine is not None
            },
            "features": {
                "health_display": self.state.get("cockpit_health_display", True),
                "one_click_heal": self.state.get("one_click_heal_enabled", True),
                "visualization": True,
                "auto_refresh": self.state.get("auto_refresh_interval", 30)
            },
            "last_health_check": self.state.get("last_health_check"),
            "last_self_heal": self.state.get("last_self_heal"),
            "statistics": {
                "total_heals": len(self.state.get("heal_history", [])),
                "alerts_count": len(self.state.get("alerts", []))
            }
        }

        # 更新状态为已初始化
        if status["integration_status"] == "initializing":
            status["integration_status"] = "ready"
            self.state["integration_status"] = "ready"
            self._save_state()

        return status


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(
        description="智能全场景进化引擎集群驾驶舱深度集成引擎"
    )
    parser.add_argument(
        "command",
        nargs="?",
        default="status",
        choices=["dashboard", "health", "self_heal", "visualize", "status"],
        help="要执行的命令"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="显示详细信息"
    )

    args = parser.parse_args()

    # 创建引擎实例
    engine = EvolutionEngineCockpitIntegration()

    if args.command == "dashboard":
        result = engine.get_dashboard()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == "health":
        result = engine.get_health()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == "self_heal":
        result = engine.trigger_self_heal()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == "visualize":
        result = engine.visualize()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == "status":
        result = engine.get_status()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    return 0


if __name__ == "__main__":
    sys.exit(main())