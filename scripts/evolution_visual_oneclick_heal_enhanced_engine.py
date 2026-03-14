#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化引擎集群可视化一键自愈增强引擎

将 round 384 的跨引擎深度健康自愈引擎与 round 385 的驾驶舱深度集成引擎进一步增强，
实现真正的可视化一键自愈功能。

功能：
1. 增强可视化界面 - 显示更详细的健康状态和自愈进度
2. 增强一键自愈 - 让自愈过程更直观可控
3. 实现实时状态监控 - 实时显示引擎健康状态
4. 实现自愈进度显示 - 显示自愈的详细步骤和进度
5. 实现自愈结果验证 - 自动验证自愈效果

使用方法（直接运行）：
    python evolution_visual_oneclick_heal_enhanced_engine.py dashboard       - 增强的驾驶舱视图
    python evolution_visual_oneclick_heal_enhanced_engine.py health         - 详细健康态势
    python evolution_visual_oneclick_heal_enhanced_engine.py self_heal       - 可视化一键自愈
    python evolution_visual_oneclick_heal_enhanced_engine.py visualize       - 增强可视化
    python evolution_visual_oneclick_heal_enhanced_engine.py status         - 增强状态查询
    python evolution_visual_oneclick_heal_enhanced_engine.py verify         - 验证自愈结果
    python evolution_visual_oneclick_heal_enhanced_engine.py monitor         - 实时监控模式

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


class EvolutionVisualOneClickHealEnhancedEngine:
    """进化引擎集群可视化一键自愈增强引擎"""

    def __init__(self):
        self.version = "1.0.0"
        self.state_file = RUNTIME_STATE / "evolution_visual_heal_enhanced_state.json"
        self.state = self._load_state()

        # 加载依赖模块
        self.cockpit_integration_script = None
        self.deep_health_script = None
        self.cockpit_script = None
        self.load_dependencies()

    def load_dependencies(self):
        """加载依赖的引擎模块（通过 subprocess 调用）"""
        import sys

        # 检查驾驶舱集成引擎是否存在
        cockpit_integration = SCRIPTS_DIR / "evolution_engine_cluster_cockpit_integration_engine.py"
        if cockpit_integration.exists():
            self.cockpit_integration_script = str(cockpit_integration)
            print(f"已找到驾驶舱集成引擎: {self.cockpit_integration_script}")
        else:
            self.cockpit_integration_script = None
            print(f"驾驶舱集成引擎未找到", file=sys.stderr)

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
            "last_verify": None,
            "heal_progress": None,
            "auto_heal_enabled": True,
            "health_metrics": {},
            "monitoring_enabled": False,
            "monitor_interval": 30,
            "alerts": [],
            "heal_history": [],
            "verify_history": []
        }

    def _save_state(self):
        """保存状态"""
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存状态失败: {e}", file=sys.stderr)

    def _call_subprocess(self, script: Optional[str], command: str, timeout: int = 30) -> Dict[str, Any]:
        """调用子进程执行命令"""
        import subprocess
        import sys

        if not script:
            return {"error": "脚本未找到"}

        try:
            result = subprocess.run(
                [sys.executable, script, command],
                cwd=str(PROJECT_ROOT),
                capture_output=True,
                text=True,
                timeout=timeout
            )
            if result.returncode == 0 and result.stdout:
                try:
                    return json.loads(result.stdout)
                except:
                    return {"raw_output": result.stdout}
            else:
                return {"error": result.stderr or "执行失败"}
        except subprocess.TimeoutExpired:
            return {"error": "执行超时"}
        except Exception as e:
            return {"error": str(e)}

    def get_enhanced_dashboard(self) -> Dict[str, Any]:
        """获取增强的驾驶舱视图"""
        dashboard = {
            "integration_status": self.state.get("integration_status", "unknown"),
            "timestamp": datetime.now().isoformat(),
            "dashboard_type": "enhanced",
            "health_overview": None,
            "self_heal_status": None,
            "visualization": None,
            "monitoring": {
                "enabled": self.state.get("monitoring_enabled", False),
                "interval": self.state.get("monitor_interval", 30)
            }
        }

        # 获取健康态势
        if self.cockpit_integration_script:
            dashboard["health_overview"] = self._call_subprocess(
                self.cockpit_integration_script, "health"
            )

        # 获取自愈状态
        if self.cockpit_integration_script:
            dashboard["self_heal_status"] = self._call_subprocess(
                self.cockpit_integration_script, "status"
            )

        # 增强的可视化数据
        health = dashboard.get("health_overview", {})
        dashboard["visualization"] = {
            "health_score": health.get("overall_score", 0),
            "engine_count": health.get("engine_count", 0),
            "healthy_engines": health.get("healthy_count", 0),
            "issues_found": health.get("issue_count", 0),
            "warning_engines": health.get("warning_count", 0),
            "critical_engines": health.get("critical_count", 0),
            "last_heal": self.state.get("last_self_heal"),
            "last_verify": self.state.get("last_verify"),
            "heal_progress": self.state.get("heal_progress"),
            "alerts": self.state.get("alerts", []),
            "heal_success_rate": self._calculate_heal_success_rate()
        }

        return dashboard

    def _calculate_heal_success_rate(self) -> float:
        """计算自愈成功率"""
        history = self.state.get("heal_history", [])
        if not history:
            return 0.0

        success = sum(1 for h in history if h.get("status") == "success")
        return round(success / len(history) * 100, 1)

    def get_detailed_health(self) -> Dict[str, Any]:
        """获取详细健康态势"""
        result = {
            "timestamp": datetime.now().isoformat(),
            "source": "evolution_visual_oneclick_heal_enhanced",
            "type": "detailed_health"
        }

        # 调用驾驶舱集成引擎获取健康态势
        if self.cockpit_integration_script:
            health = self._call_subprocess(self.cockpit_integration_script, "health", timeout=30)
            result.update(health)

        # 添加增强信息
        result["enhanced_info"] = {
            "monitoring_enabled": self.state.get("monitoring_enabled", False),
            "auto_heal_enabled": self.state.get("auto_heal_enabled", True),
            "success_rate": self._calculate_heal_success_rate(),
            "total_heals": len(self.state.get("heal_history", [])),
            "total_verifies": len(self.state.get("verify_history", []))
        }

        # 更新状态
        self.state["last_health_check"] = datetime.now().isoformat()
        self.state["health_metrics"] = result
        self._save_state()

        return result

    def trigger_visual_self_heal(self) -> Dict[str, Any]:
        """触发可视化一键自愈（带进度显示）"""
        result = {
            "timestamp": datetime.now().isoformat(),
            "action": "visual_self_heal",
            "status": "started",
            "progress": []
        }

        # 阶段 1: 健康检查
        result["progress"].append({
            "stage": "health_check",
            "status": "running",
            "message": "正在进行健康检查..."
        })

        health_check = self.get_detailed_health()
        result["progress"][-1]["status"] = "completed"
        result["progress"][-1]["result"] = health_check.get("overall_score", 0)

        # 阶段 2: 问题诊断
        result["progress"].append({
            "stage": "diagnosis",
            "status": "running",
            "message": "正在诊断问题..."
        })

        issues = health_check.get("issue_count", 0)
        result["progress"][-1]["status"] = "completed"
        result["progress"][-1]["issues_found"] = issues

        # 阶段 3: 自愈执行
        if issues > 0 or self.state.get("auto_heal_enabled"):
            result["progress"].append({
                "stage": "self_heal",
                "status": "running",
                "message": "正在执行自愈..."
            })

            if self.deep_health_script:
                heal_result = self._call_subprocess(self.deep_health_script, "full_cycle", timeout=60)
                result["progress"][-1]["status"] = "completed"
                result["progress"][-1]["result"] = heal_result
            elif self.cockpit_integration_script:
                # 使用驾驶舱集成引擎的一键自愈
                heal_result = self._call_subprocess(self.cockpit_integration_script, "self_heal", timeout=60)
                result["progress"][-1]["status"] = "completed"
                result["progress"][-1]["result"] = heal_result
        else:
            result["progress"].append({
                "stage": "self_heal",
                "status": "skipped",
                "message": "无需自愈，系统健康"
            })

        # 阶段 4: 结果验证
        result["progress"].append({
            "stage": "verification",
            "status": "running",
            "message": "正在验证自愈结果..."
        })

        verify_result = self.verify_heal_result()
        result["progress"][-1]["status"] = "completed"
        result["progress"][-1]["result"] = verify_result

        # 阶段 5: 完成
        result["progress"].append({
            "stage": "completed",
            "status": "completed",
            "message": "自愈流程完成",
            "success": verify_result.get("heal_success", False),
            "new_score": verify_result.get("new_health_score", 0)
        })

        result["status"] = "completed"
        result["heal_success"] = verify_result.get("heal_success", False)

        # 保存到历史
        self.state["last_self_heal"] = datetime.now().isoformat()
        self.state["heal_progress"] = result["progress"]

        heal_history = self.state.get("heal_history", [])
        heal_history.append({
            "timestamp": datetime.now().isoformat(),
            "result": result,
            "issues_found": issues
        })
        self.state["heal_history"] = heal_history[-20:]
        self._save_state()

        return result

    def verify_heal_result(self) -> Dict[str, Any]:
        """验证自愈结果"""
        result = {
            "timestamp": datetime.now().isoformat(),
            "action": "verify",
            "status": "started"
        }

        # 获取最新的健康态势
        health = self.get_detailed_health()
        new_score = health.get("overall_score", 0)

        # 获取上次自愈前的健康分数
        heal_history = self.state.get("heal_history", [])
        old_score = 0
        if heal_history:
            last_heal = heal_history[-1]
            old_score = last_heal.get("result", {}).get("progress", [{}])[0].get("result", 0)

        # 计算改进
        score_improvement = new_score - old_score

        result["old_health_score"] = old_score
        result["new_health_score"] = new_score
        result["score_improvement"] = score_improvement
        result["heal_success"] = new_score >= 80 or score_improvement > 0
        result["issues_remaining"] = health.get("issue_count", 0)

        # 保存验证历史
        self.state["last_verify"] = datetime.now().isoformat()
        verify_history = self.state.get("verify_history", [])
        verify_history.append({
            "timestamp": datetime.now().isoformat(),
            "old_score": old_score,
            "new_score": new_score,
            "success": result["heal_success"]
        })
        self.state["verify_history"] = verify_history[-20:]
        self._save_state()

        return result

    def get_enhanced_visualize(self) -> Dict[str, Any]:
        """获取增强可视化数据"""
        viz_data = {
            "timestamp": datetime.now().isoformat(),
            "visualization_type": "enhanced_health_dashboard"
        }

        try:
            # 获取当前健康态势
            health = self.get_detailed_health()

            # 构建增强的可视化数据结构
            viz_data["components"] = [
                {
                    "type": "gauge",
                    "name": "整体健康度",
                    "value": health.get("overall_score", 0),
                    "max": 100,
                    "unit": "%",
                    "color": self._get_health_color(health.get("overall_score", 0))
                },
                {
                    "type": "progress_ring",
                    "name": "自愈进度",
                    "data": self.state.get("heal_progress", [])
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
                    "type": "timeline",
                    "name": "验证历史",
                    "data": self.state.get("verify_history", [])[-10:]
                },
                {
                    "type": "alert_list",
                    "name": "当前告警",
                    "data": self.state.get("alerts", [])
                },
                {
                    "type": "stats",
                    "name": "统计信息",
                    "data": {
                        "total_heals": len(self.state.get("heal_history", [])),
                        "success_rate": self._calculate_heal_success_rate(),
                        "total_verifies": len(self.state.get("verify_history", [])),
                        "monitoring_enabled": self.state.get("monitoring_enabled", False)
                    }
                }
            ]

            viz_data["summary"] = {
                "total_engines": health.get("engine_count", 0),
                "healthy_engines": health.get("healthy_count", 0),
                "issues_detected": health.get("issue_count", 0),
                "auto_heal_enabled": self.state.get("auto_heal_enabled", True),
                "last_heal": self.state.get("last_self_heal"),
                "last_verify": self.state.get("last_verify")
            }

        except Exception as e:
            viz_data["error"] = str(e)

        return viz_data

    def _get_health_color(self, score: float) -> str:
        """根据健康分数返回颜色"""
        if score >= 80:
            return "green"
        elif score >= 60:
            return "yellow"
        else:
            return "red"

    def get_enhanced_status(self) -> Dict[str, Any]:
        """获取增强状态"""
        status = {
            "version": self.version,
            "integration_status": self.state.get("integration_status", "unknown"),
            "type": "enhanced",
            "dependencies": {
                "cockpit_integration_engine": self.cockpit_integration_script is not None,
                "deep_health_engine": self.deep_health_script is not None,
                "cockpit_engine": self.cockpit_script is not None
            },
            "features": {
                "enhanced_visualization": True,
                "one_click_heal": True,
                "progress_tracking": True,
                "auto_verify": True,
                "monitoring": self.state.get("monitoring_enabled", False)
            },
            "last_health_check": self.state.get("last_health_check"),
            "last_self_heal": self.state.get("last_self_heal"),
            "last_verify": self.state.get("last_verify"),
            "statistics": {
                "total_heals": len(self.state.get("heal_history", [])),
                "success_rate": self._calculate_heal_success_rate(),
                "total_verifies": len(self.state.get("verify_history", [])),
                "alerts_count": len(self.state.get("alerts", []))
            }
        }

        # 更新状态为已初始化
        if status["integration_status"] == "initializing":
            status["integration_status"] = "ready"
            self.state["integration_status"] = "ready"
            self._save_state()

        return status

    def start_monitoring(self) -> Dict[str, Any]:
        """启动实时监控"""
        self.state["monitoring_enabled"] = True
        self._save_state()
        return {
            "status": "started",
            "timestamp": datetime.now().isoformat(),
            "message": "实时监控已启动"
        }

    def stop_monitoring(self) -> Dict[str, Any]:
        """停止实时监控"""
        self.state["monitoring_enabled"] = False
        self._save_state()
        return {
            "status": "stopped",
            "timestamp": datetime.now().isoformat(),
            "message": "实时监控已停止"
        }

    def get_monitor_data(self) -> Dict[str, Any]:
        """获取监控数据"""
        if not self.state.get("monitoring_enabled"):
            return {
                "status": "disabled",
                "message": "监控未启用，使用 start_monitoring 启用"
            }

        return {
            "status": "enabled",
            "timestamp": datetime.now().isoformat(),
            "health": self.get_detailed_health(),
            "last_heal": self.state.get("last_self_heal"),
            "alerts": self.state.get("alerts", [])
        }


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(
        description="智能全场景进化引擎集群可视化一键自愈增强引擎"
    )
    parser.add_argument(
        "command",
        nargs="?",
        default="status",
        choices=["dashboard", "health", "self_heal", "visualize", "status", "verify", "monitor", "start_monitor", "stop_monitor"],
        help="要执行的命令"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="显示详细信息"
    )

    args = parser.parse_args()

    # 创建引擎实例
    engine = EvolutionVisualOneClickHealEnhancedEngine()

    if args.command == "dashboard":
        result = engine.get_enhanced_dashboard()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == "health":
        result = engine.get_detailed_health()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == "self_heal":
        result = engine.trigger_visual_self_heal()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == "visualize":
        result = engine.get_enhanced_visualize()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == "status":
        result = engine.get_enhanced_status()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == "verify":
        result = engine.verify_heal_result()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == "monitor":
        result = engine.get_monitor_data()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == "start_monitor":
        result = engine.start_monitoring()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == "stop_monitor":
        result = engine.stop_monitoring()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    return 0


if __name__ == "__main__":
    sys.exit(main())