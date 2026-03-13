#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能统一系统监控仪表盘引擎
整合所有引擎的监控数据（健康保障、主动运维、执行历史、守护进程状态等），提供统一的实时系统状态视图
"""
import os
import sys
import json
import time
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import subprocess

# 确保可以导入项目模块
SCRIPTS = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(SCRIPTS)
sys.path.insert(0, SCRIPTS)

class SystemDashboardEngine:
    """智能统一系统监控仪表盘引擎"""

    def __init__(self):
        self.project = PROJECT
        self.runtime = os.path.join(PROJECT, "runtime")
        self.state_dir = os.path.join(self.runtime, "state")
        self.logs_dir = os.path.join(self.runtime, "logs")

    def get_status(self) -> Dict[str, Any]:
        """获取完整的系统监控仪表盘数据"""
        dashboard = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "dashboard_version": "1.0",
            "sections": {}
        }

        # 1. 守护进程状态
        dashboard["sections"]["daemon_status"] = self._get_daemon_status()

        # 2. 健康保障状态
        dashboard["sections"]["health_assurance"] = self._get_health_assurance_status()

        # 3. 主动运维状态
        dashboard["sections"]["proactive_operations"] = self._get_proactive_operations_status()

        # 4. 进化环状态
        dashboard["sections"]["evolution"] = self._get_evolution_status()

        # 5. 执行历史统计
        dashboard["sections"]["execution_stats"] = self._get_execution_stats()

        # 6. 系统资源状态
        dashboard["sections"]["system_resources"] = self._get_system_resources()

        # 7. 告警和提醒
        dashboard["sections"]["alerts"] = self._get_alerts()

        # 8. 总体健康评分
        dashboard["overall_health"] = self._calculate_overall_health(dashboard["sections"])

        return dashboard

    def _get_daemon_status(self) -> Dict[str, Any]:
        """获取守护进程状态"""
        status = {
            "daemons": [],
            "active_count": 0,
            "total_count": 0
        }
        try:
            result = subprocess.run(
                [sys.executable, os.path.join(SCRIPTS, "daemon_manager.py"), "status"],
                capture_output=True, text=True, timeout=10
            )
            status["raw_output"] = result.stdout[:500] if result.stdout else ""
            status["active_count"] = result.stdout.count("Running") if result.stdout else 0
            # 统计总守护进程数
            status["total_count"] = len([l for l in result.stdout.split('\n') if 'daemon' in l.lower() or 'Running' in l or 'Stopped' in l])
        except Exception as e:
            status["error"] = str(e)
        return status

    def _get_health_assurance_status(self) -> Dict[str, Any]:
        """获取健康保障状态"""
        status = {"status": "unknown", "components": {}}
        try:
            from health_assurance_loop import HealthAssuranceLoop
            engine = HealthAssuranceLoop()
            health_status = engine.get_status()
            status = {
                "status": health_status.get("assurance_status", "unknown"),
                "components": {
                    "self_healing": health_status.get("engines", {}).get("self_healing", {}).get("status", "unknown"),
                    "predictive": health_status.get("engines", {}).get("predictive", {}).get("status", "unknown"),
                    "proactive_ops": health_status.get("engines", {}).get("proactive", {}).get("status", "unknown")
                },
                "last_check": health_status.get("timestamp", "")
            }
        except Exception as e:
            status["error"] = str(e)
        return status

    def _get_proactive_operations_status(self) -> Dict[str, Any]:
        """获取主动运维状态"""
        status = {"status": "unknown", "optimizations": {}}
        try:
            from proactive_operations_engine import ProactiveOperationsEngine
            engine = ProactiveOperationsEngine()
            ops_status = engine.get_status()
            status = {
                "status": ops_status.get("status", "unknown"),
                "optimizations": {
                    "auto_clean": ops_status.get("auto_clean_enabled", False),
                    "auto_memory": ops_status.get("auto_memory_optimization", False),
                    "auto_process": ops_status.get("auto_process_optimization", False)
                },
                "last_optimization": ops_status.get("last_optimization_time", "")
            }
        except Exception as e:
            status["error"] = str(e)
        return status

    def _get_evolution_status(self) -> Dict[str, Any]:
        """获取进化环状态"""
        status = {"current_round": 0, "phase": "unknown"}
        try:
            mission_path = os.path.join(self.state_dir, "current_mission.json")
            if os.path.exists(mission_path):
                with open(mission_path, "r", encoding="utf-8") as f:
                    mission = json.load(f)
                    status = {
                        "current_round": mission.get("loop_round", 0),
                        "phase": mission.get("phase", "unknown"),
                        "current_goal": mission.get("current_goal", ""),
                        "next_action": mission.get("next_action", "")
                    }
        except Exception as e:
            status["error"] = str(e)
        return status

    def _get_execution_stats(self) -> Dict[str, Any]:
        """获取执行统计"""
        stats = {"total_executions": 0, "recent_executions": 0}
        try:
            # 读取最近日志
            recent_logs_path = os.path.join(self.state_dir, "recent_logs.json")
            if os.path.exists(recent_logs_path):
                with open(recent_logs_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    entries = data.get("entries", [])
                    stats["total_executions"] = len(entries)
                    # 最近1小时的执行
                    one_hour_ago = time.time() - 3600
                    stats["recent_executions"] = sum(
                        1 for e in entries
                        if e.get("time", "") and self._parse_time(e["time"]) > one_hour_ago
                    )
        except Exception as e:
            stats["error"] = str(e)
        return stats

    def _parse_time(self, time_str: str) -> float:
        """解析时间字符串"""
        try:
            dt = datetime.fromisoformat(time_str.replace('+00:00', '+00:00'))
            return dt.timestamp()
        except:
            return 0

    def _get_system_resources(self) -> Dict[str, Any]:
        """获取系统资源状态"""
        resources = {"cpu": {}, "memory": {}, "disk": {}}
        try:
            import psutil
            resources = {
                "cpu": {
                    "usage_percent": psutil.cpu_percent(interval=0.1),
                    "count": psutil.cpu_count()
                },
                "memory": {
                    "total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
                    "available_gb": round(psutil.virtual_memory().available / (1024**3), 2),
                    "usage_percent": psutil.virtual_memory().percent
                },
                "disk": {
                    "total_gb": round(psutil.disk_usage('/').total / (1024**3), 2),
                    "free_gb": round(psutil.disk_usage('/').free / (1024**3), 2),
                    "usage_percent": psutil.disk_usage('/').percent
                }
            }
        except ImportError:
            resources["error"] = "psutil not installed, using basic info"
            # 基础信息
            try:
                result = subprocess.run(["wmic", "OS", "get", "FreePhysicalMemory,TotalVisibleMemorySize", "/Value"],
                                        capture_output=True, text=True, timeout=5)
                resources["raw"] = result.stdout[:200]
            except:
                pass
        except Exception as e:
            resources["error"] = str(e)
        return resources

    def _get_alerts(self) -> Dict[str, Any]:
        """获取告警和提醒"""
        alerts = {"count": 0, "items": [], "high_priority": []}
        try:
            # 检查健康保障告警
            try:
                from health_assurance_loop import HealthAssuranceLoop
                engine = HealthAssuranceLoop()
                health = engine.get_status()
                # 检查是否有告警
                for component, data in health.get("engines", {}).items():
                    if data.get("status") == "critical":
                        alerts["high_priority"].append({
                            "source": f"health_assurance.{component}",
                            "message": f"Critical: {component} is in critical state"
                        })
            except:
                pass

            # 检查系统资源告警
            resources = self._get_system_resources()
            if resources.get("memory", {}).get("usage_percent", 0) > 90:
                alerts["high_priority"].append({
                    "source": "system_resources",
                    "message": "Memory usage above 90%"
                })
            if resources.get("disk", {}).get("usage_percent", 0) > 90:
                alerts["high_priority"].append({
                    "source": "system_resources",
                    "message": "Disk usage above 90%"
                })

            alerts["count"] = len(alerts["high_priority"])
            alerts["items"] = alerts["high_priority"][:5]  # 最多5条
        except Exception as e:
            alerts["error"] = str(e)
        return alerts

    def _calculate_overall_health(self, sections: Dict[str, Any]) -> Dict[str, Any]:
        """计算总体健康评分"""
        score = 100
        factors = []

        # 检查守护进程
        daemon_status = sections.get("daemon_status", {})
        if daemon_status.get("active_count", 0) > 0:
            factors.append({"name": "daemons", "contribution": 0})
        else:
            score -= 10
            factors.append({"name": "daemons", "contribution": -10})

        # 检查健康保障
        health = sections.get("health_assurance", {})
        if health.get("status") == "active":
            factors.append({"name": "health_assurance", "contribution": 0})
        else:
            score -= 15
            factors.append({"name": "health_assurance", "contribution": -15})

        # 检查主动运维
        proactive = sections.get("proactive_operations", {})
        if proactive.get("status") == "active":
            factors.append({"name": "proactive_operations", "contribution": 0})
        else:
            score -= 10
            factors.append({"name": "proactive_operations", "contribution": -10})

        # 检查告警
        alerts = sections.get("alerts", {})
        alert_count = alerts.get("count", 0)
        score -= min(alert_count * 5, 25)
        factors.append({"name": "alerts", "contribution": -min(alert_count * 5, 25)})

        score = max(score, 0)  # 最低0分

        # 评级
        if score >= 90:
            grade = "A"
        elif score >= 75:
            grade = "B"
        elif score >= 60:
            grade = "C"
        else:
            grade = "D"

        return {
            "score": score,
            "grade": grade,
            "factors": factors,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    def get_summary(self) -> str:
        """获取简短的系统状态摘要"""
        try:
            status = self.get_status()
            health = status.get("overall_health", {})
            daemon = status.get("sections", {}).get("daemon_status", {})
            alerts = status.get("sections", {}).get("alerts", {})

            summary = f"""[System Dashboard]

Overall Health Score: {health.get('score', 0)} ({health.get('grade', 'N')})
Active Daemons: {daemon.get('active_count', 0)}/{daemon.get('total_count', 0)}
High Priority Alerts: {alerts.get('count', 0)}

Evolution Status:
   Round: {status.get('sections', {}).get('evolution', {}).get('current_round', 0)}
   Phase: {status.get('sections', {}).get('evolution', {}).get('phase', 'N/A')}

System Resources:
   CPU: {status.get('sections', {}).get('system_resources', {}).get('cpu', {}).get('usage_percent', 'N/A')}%
   Memory: {status.get('sections', {}).get('system_resources', {}).get('memory', {}).get('usage_percent', 'N/A')}%
   Disk: {status.get('sections', {}).get('system_resources', {}).get('disk', {}).get('usage_percent', 'N/A')}%
"""
            # 添加告警详情
            if alerts.get("high_priority"):
                summary += "\nAlert Details:\n"
                for alert in alerts.get("high_priority", [])[:3]:
                    summary += f"   - {alert.get('message', 'Unknown')}\n"

            return summary
        except Exception as e:
            return f"Failed to get system status: {str(e)}"

    def get_dashboard_json(self) -> str:
        """获取完整的仪表盘 JSON 数据"""
        try:
            status = self.get_status()
            return json.dumps(status, ensure_ascii=False, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False, indent=2)

def main():
    """主入口"""
    import argparse
    parser = argparse.ArgumentParser(description="智能统一系统监控仪表盘引擎")
    parser.add_argument("command", nargs="?", default="status", help="命令: status|summary|json")
    parser.add_argument("--refresh", action="store_true", help="强制刷新")
    args = parser.parse_args()

    engine = SystemDashboardEngine()

    if args.command == "status" or args.command == "summary":
        print(engine.get_summary())
    elif args.command == "json":
        print(engine.get_dashboard_json())
    else:
        print(f"未知命令: {args.command}")
        print("可用命令: status, summary, json")

if __name__ == "__main__":
    main()