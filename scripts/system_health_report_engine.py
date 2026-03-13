"""
智能系统自检与健康报告引擎 (System Health Report Engine)

让系统能够自动进行全面健康检查、生成详细状态报告、提供健康建议，
实现元进化方向的自我审视能力。

功能：
1. 自动健康检查 - 检查系统资源、进程、引擎状态
2. 详细状态报告 - 生成结构化的健康报告
3. 健康建议 - 基于检查结果提供优化建议
4. 自我审视 - 为元进化提供系统健康洞察
"""

import json
import os
import sys
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# 尝试导入 psutil，如果失败则使用替代方案
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class SystemHealthReportEngine:
    """智能系统自检与健康报告引擎"""

    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.scripts_dir = self.project_root / "scripts"
        self.state_dir = self.project_root / "runtime" / "state"
        self.logs_dir = self.project_root / "runtime" / "logs"

        # 健康检查阈值
        self.thresholds = {
            "cpu_percent_warning": 80.0,
            "cpu_percent_critical": 95.0,
            "memory_percent_warning": 80.0,
            "memory_percent_critical": 95.0,
            "disk_percent_warning": 85.0,
            "disk_percent_critical": 95.0
        }

    def check_system_resources(self) -> Dict[str, Any]:
        """检查系统资源使用情况"""
        result = {
            "timestamp": datetime.now().isoformat(),
            "cpu": {},
            "memory": {},
            "disk": {}
        }

        if HAS_PSUTIL:
            try:
                # CPU 检查
                cpu_percent = psutil.cpu_percent(interval=1)
                cpu_count = psutil.cpu_count()
                result["cpu"] = {
                    "percent": cpu_percent,
                    "count": cpu_count,
                    "status": self._get_status(cpu_percent, self.thresholds["cpu_percent_warning"], self.thresholds["cpu_percent_critical"])
                }

                # 内存检查
                memory = psutil.virtual_memory()
                result["memory"] = {
                    "total": memory.total,
                    "available": memory.available,
                    "percent": memory.percent,
                    "status": self._get_status(memory.percent, self.thresholds["memory_percent_warning"], self.thresholds["memory_percent_critical"])
                }

                # 磁盘检查
                disk = psutil.disk_usage('/')
                result["disk"] = {
                    "total": disk.total,
                    "used": disk.used,
                    "free": disk.free,
                    "percent": disk.percent,
                    "status": self._get_status(disk.percent, self.thresholds["disk_percent_warning"], self.thresholds["disk_percent_critical"])
                }

            except Exception as e:
                result["error"] = str(e)
        else:
            # 使用替代方案：通过 powershell 获取系统信息
            try:
                # 使用 powershell 获取 CPU 使用率
                cpu_cmd = subprocess.run(
                    ["powershell", "-Command", "(Get-Counter '\\Processor(_Total)\\% Processor Time').CounterSamples.CookedValue"],
                    capture_output=True, text=True, timeout=10
                )
                cpu_percent = float(cpu_cmd.stdout.strip()) if cpu_cmd.stdout.strip() else 0

                result["cpu"] = {
                    "percent": cpu_percent,
                    "count": os.cpu_count() or 1,
                    "status": self._get_status(cpu_percent, self.thresholds["cpu_percent_warning"], self.thresholds["cpu_percent_critical"])
                }

                # 使用 powershell 获取内存信息
                mem_cmd = subprocess.run(
                    ["powershell", "-Command", "$os = Get-CimInstance Win32_OperatingSystem; [PSCustomObject]@{Total=$os.TotalVisibleMemorySize * 1024; Free=$os.FreePhysicalMemory * 1024}"],
                    capture_output=True, text=True, timeout=10
                )
                if mem_cmd.stdout.strip():
                    for line in mem_cmd.stdout.strip().split("\n"):
                        if "Total" in line:
                            import re
                            match = re.search(r'Total\s*[:=]\s*(\d+)', line)
                            total = int(match.group(1)) if match else 0
                        if "Free" in line:
                            match = re.search(r'Free\s*[:=]\s*(\d+)', line)
                            free = int(match.group(1)) if match else 0
                    if total > 0 and free > 0:
                        used = total - free
                        mem_percent = (used / total) * 100
                        result["memory"] = {
                            "total": total,
                            "available": free,
                            "percent": mem_percent,
                            "status": self._get_status(mem_percent, self.thresholds["memory_percent_warning"], self.thresholds["memory_percent_critical"])
                        }

                # 使用 wmic 获取磁盘信息
                disk_cmd = subprocess.run(
                    ["wmic", "logicaldisk", "where", "DeviceID='C:'", "get", "Size,FreeSpace"],
                    capture_output=True, text=True, timeout=10
                )
                disk_output = disk_cmd.stdout.strip().split("\n")
                if len(disk_output) > 1:
                    parts = disk_output[1].split()
                    if len(parts) >= 2 and parts[0] and parts[1]:
                        free_disk = int(parts[1])
                        # 估算总大小
                        total_disk = 500 * 1024 * 1024 * 1024  # 500GB
                        used_disk = total_disk - free_disk
                        disk_percent = (used_disk / total_disk) * 100
                        result["disk"] = {
                            "total": total_disk,
                            "used": used_disk,
                            "free": free_disk,
                            "percent": disk_percent,
                            "status": self._get_status(disk_percent, self.thresholds["disk_percent_warning"], self.thresholds["disk_percent_critical"])
                        }

                result["note"] = "使用 PowerShell/wmic 获取（psutil 不可用）"

            except Exception as e:
                result["error"] = str(e)

        return result

    def _get_status(self, value: float, warning: float, critical: float) -> str:
        """获取状态"""
        if value >= critical:
            return "critical"
        elif value >= warning:
            return "warning"
        else:
            return "normal"

    def check_processes(self) -> Dict[str, Any]:
        """检查关键进程状态"""
        result = {
            "timestamp": datetime.now().isoformat(),
            "running_processes": [],
            "high_cpu_processes": [],
            "high_memory_processes": []
        }

        if HAS_PSUTIL:
            try:
                # 获取所有进程
                for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                    try:
                        pinfo = proc.info
                        result["running_processes"].append({
                            "pid": pinfo['pid'],
                            "name": pinfo['name'],
                            "cpu_percent": pinfo['cpu_percent'],
                            "memory_percent": pinfo['memory_percent']
                        })

                        # 高 CPU 进程
                        if pinfo['cpu_percent'] and pinfo['cpu_percent'] > 50.0:
                            result["high_cpu_processes"].append({
                                "pid": pinfo['pid'],
                                "name": pinfo['name'],
                                "cpu_percent": pinfo['cpu_percent']
                            })

                        # 高内存进程
                        if pinfo['memory_percent'] and pinfo['memory_percent'] > 20.0:
                            result["high_memory_processes"].append({
                                "pid": pinfo['pid'],
                                "name": pinfo['name'],
                                "memory_percent": pinfo['memory_percent']
                            })

                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass

                # 按 CPU 和内存排序，取前 10
                result["high_cpu_processes"] = sorted(
                    result["high_cpu_processes"],
                    key=lambda x: x.get('cpu_percent', 0),
                    reverse=True
                )[:10]

                result["high_memory_processes"] = sorted(
                    result["high_memory_processes"],
                    key=lambda x: x.get('memory_percent', 0),
                    reverse=True
                )[:10]

                result["status"] = "ok"

            except Exception as e:
                result["error"] = str(e)
                result["status"] = "error"
        else:
            # 使用 tasklist 作为替代
            try:
                task_cmd = subprocess.run(["tasklist", "/FO", "CSV", "/NH"], capture_output=True, text=True, timeout=30)
                for line in task_cmd.stdout.strip().split("\n"):
                    parts = line.split('","')
                    if len(parts) >= 2:
                        name = parts[0].replace('"', '')
                        pid = parts[1].replace('"', '')
                        result["running_processes"].append({
                            "pid": pid,
                            "name": name,
                            "cpu_percent": None,
                            "memory_percent": None
                        })

                result["note"] = "使用 tasklist 获取（psutil 不可用）"
                result["status"] = "ok"

            except Exception as e:
                result["error"] = str(e)
                result["status"] = "error"

        return result

    def check_engine_states(self) -> Dict[str, Any]:
        """检查各引擎状态"""
        result = {
            "timestamp": datetime.now().isoformat(),
            "engines": {}
        }

        try:
            # 扫描 scripts 目录下的引擎文件
            engine_files = [
                "unified_service_hub.py",
                "multi_agent_collaboration_engine.py",
                "cross_engine_task_planner.py",
                "unified_learning_hub.py",
                "health_assurance_loop.py",
                "proactive_decision_action_engine.py",
                "behavior_sequence_prediction_engine.py",
                "task_continuation_engine.py"
            ]

            for engine_file in engine_files:
                engine_path = self.scripts_dir / engine_file
                if engine_path.exists():
                    stat = engine_path.stat()
                    result["engines"][engine_file] = {
                        "exists": True,
                        "size": stat.st_size,
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        "status": "available"
                    }
                else:
                    result["engines"][engine_file] = {
                        "exists": False,
                        "status": "not_found"
                    }

            result["status"] = "ok"

        except Exception as e:
            result["error"] = str(e)
            result["status"] = "error"

        return result

    def check_evolution_state(self) -> Dict[str, Any]:
        """检查进化环状态"""
        result = {
            "timestamp": datetime.now().isoformat(),
            "current_mission": {},
            "evolution_completed": [],
            "recent_logs": {}
        }

        try:
            # 读取当前任务状态
            mission_file = self.state_dir / "current_mission.json"
            if mission_file.exists():
                with open(mission_file, 'r', encoding='utf-8') as f:
                    result["current_mission"] = json.load(f)

            # 读取进化完成状态
            state_files = list(self.state_dir.glob("evolution_completed_*.json"))
            # 只读取最近的5个
            state_files = sorted(state_files, key=lambda x: x.stat().st_mtime, reverse=True)[:5]
            for f in state_files:
                try:
                    with open(f, 'r', encoding='utf-8') as fp:
                        data = json.load(fp)
                        result["evolution_completed"].append({
                            "file": f.name,
                            "goal": data.get("current_goal", ""),
                            "status": data.get("status", ""),
                            "completed_at": data.get("completed_at", "")
                        })
                except Exception:
                    pass

            # 读取最近日志
            log_file = self.logs_dir / "behavior_2026-03-13.log"
            if log_file.exists():
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    result["recent_logs"]["total_lines"] = len(lines)
                    result["recent_logs"]["last_line"] = lines[-1].strip() if lines else ""

            result["status"] = "ok"

        except Exception as e:
            result["error"] = str(e)
            result["status"] = "error"

        return result

    def check_runtime_state(self) -> Dict[str, Any]:
        """检查运行时状态"""
        result = {
            "timestamp": datetime.now().isoformat(),
            "files": {}
        }

        try:
            # 检查关键文件
            key_files = [
                "runtime/state/current_mission.json",
                "runtime/state/evolution_session_pending.json",
                "references/capabilities.md",
                "references/capability_gaps.md",
                "SKILL.md"
            ]

            for kf in key_files:
                fpath = self.project_root / kf
                if fpath.exists():
                    stat = fpath.stat()
                    result["files"][kf] = {
                        "exists": True,
                        "size": stat.st_size,
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                    }
                else:
                    result["files"][kf] = {
                        "exists": False
                    }

            result["status"] = "ok"

        except Exception as e:
            result["error"] = str(e)
            result["status"] = "error"

        return result

    def generate_health_report(self) -> Dict[str, Any]:
        """生成完整健康报告"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "round": 203,
            "sections": {}
        }

        # 1. 系统资源
        report["sections"]["system_resources"] = self.check_system_resources()

        # 2. 进程状态
        report["sections"]["processes"] = self.check_processes()

        # 3. 引擎状态
        report["sections"]["engine_states"] = self.check_engine_states()

        # 4. 进化环状态
        report["sections"]["evolution_state"] = self.check_evolution_state()

        # 5. 运行时状态
        report["sections"]["runtime_state"] = self.check_runtime_state()

        # 计算总体健康评分
        report["health_score"] = self._calculate_health_score(report["sections"])

        # 生成建议
        report["recommendations"] = self._generate_recommendations(report["sections"])

        return report

    def _calculate_health_score(self, sections: Dict) -> Dict[str, Any]:
        """计算健康评分"""
        score = 100
        issues = []

        # 检查资源状态
        sys_res = sections.get("system_resources", {})
        cpu_status = sys_res.get("cpu", {}).get("status", "normal")
        mem_status = sys_res.get("memory", {}).get("status", "normal")
        disk_status = sys_res.get("disk", {}).get("status", "normal")

        if cpu_status == "critical":
            score -= 20
            issues.append("CPU 使用率过高")
        elif cpu_status == "warning":
            score -= 10

        if mem_status == "critical":
            score -= 20
            issues.append("内存使用率过高")
        elif mem_status == "warning":
            score -= 10

        if disk_status == "critical":
            score -= 15
            issues.append("磁盘使用率过高")
        elif disk_status == "warning":
            score -= 5

        # 检查引擎状态
        engines = sections.get("engine_states", {}).get("engines", {})
        missing_engines = [k for k, v in engines.items() if not v.get("exists", False)]
        if missing_engines:
            score -= 5 * len(missing_engines)
            issues.append(f"缺少 {len(missing_engines)} 个引擎文件")

        # 检查进化环状态
        mission = sections.get("evolution_state", {}).get("current_mission", {})
        if not mission.get("current_goal"):
            score -= 5
            issues.append("当前无明确进化目标")

        return {
            "score": max(0, score),
            "level": "excellent" if score >= 90 else "good" if score >= 70 else "fair" if score >= 50 else "poor",
            "issues": issues
        }

    def _generate_recommendations(self, sections: Dict) -> List[Dict[str, str]]:
        """生成健康建议"""
        recommendations = []

        # 资源建议
        sys_res = sections.get("system_resources", {})
        cpu_status = sys_res.get("cpu", {}).get("status", "normal")
        mem_status = sys_res.get("memory", {}).get("status", "normal")
        disk_status = sys_res.get("disk", {}).get("status", "normal")

        if cpu_status == "critical":
            recommendations.append({
                "category": "性能",
                "priority": "high",
                "issue": "CPU 使用率过高",
                "suggestion": "检查运行中的高 CPU 进程，考虑关闭不必要的程序或增加系统资源"
            })
        elif cpu_status == "warning":
            recommendations.append({
                "category": "性能",
                "priority": "medium",
                "issue": "CPU 使用率较高",
                "suggestion": "监控 CPU 使用情况，必要时优化后台进程"
            })

        if mem_status == "critical":
            recommendations.append({
                "category": "资源",
                "priority": "high",
                "issue": "内存使用率过高",
                "suggestion": "释放内存空间，关闭占用内存较高的应用"
            })
        elif mem_status == "warning":
            recommendations.append({
                "category": "资源",
                "priority": "medium",
                "issue": "内存使用率较高",
                "suggestion": "监控内存使用，考虑增加内存"
            })

        if disk_status == "critical":
            recommendations.append({
                "category": "存储",
                "priority": "high",
                "issue": "磁盘空间不足",
                "suggestion": "清理磁盘空间，删除不必要的文件或增加存储"
            })
        elif disk_status == "warning":
            recommendations.append({
                "category": "存储",
                "priority": "medium",
                "issue": "磁盘空间紧张",
                "suggestion": "监控磁盘使用，适时清理"
            })

        # 引擎建议
        engines = sections.get("engine_states", {}).get("engines", {})
        missing = [k for k, v in engines.items() if not v.get("exists", False)]
        if missing:
            recommendations.append({
                "category": "引擎",
                "priority": "medium",
                "issue": f"缺少 {len(missing)} 个引擎文件",
                "suggestion": "检查引擎文件是否完整，必要时重新创建"
            })

        # 进化建议
        mission = sections.get("evolution_state", {}).get("current_mission", {})
        if not mission.get("current_goal"):
            recommendations.append({
                "category": "进化",
                "priority": "medium",
                "issue": "当前无明确进化目标",
                "suggestion": "继续进行假设分析，确定本轮进化方向"
            })

        # 默认建议
        if not recommendations:
            recommendations.append({
                "category": "系统",
                "priority": "low",
                "issue": "系统运行正常",
                "suggestion": "保持当前状态，持续监控"
            })

        return recommendations

    def run_health_check(self, output_format: str = "json") -> str:
        """运行健康检查并返回报告"""
        report = self.generate_health_report()

        if output_format == "json":
            return json.dumps(report, ensure_ascii=False, indent=2)
        elif output_format == "summary":
            return self._format_summary(report)
        else:
            return json.dumps(report, ensure_ascii=False, indent=2)

    def _format_summary(self, report: Dict) -> str:
        """格式化报告摘要"""
        score = report.get("health_score", {})
        sections = report.get("sections", {})

        summary_lines = [
            f"=== 系统健康报告 ===",
            f"时间: {report.get('timestamp', '')}",
            f"轮次: {report.get('round', '')}",
            "",
            f"健康评分: {score.get('score', 0)}/100 ({score.get('level', 'unknown')})",
            ""
        ]

        # 系统资源
        sys_res = sections.get("system_resources", {})
        cpu = sys_res.get("cpu", {})
        mem = sys_res.get("memory", {})
        disk = sys_res.get("disk", {})

        summary_lines.extend([
            "--- 系统资源 ---",
            f"CPU: {cpu.get('percent', 0):.1f}% ({cpu.get('status', 'unknown')})",
            f"内存: {mem.get('percent', 0):.1f}% ({mem.get('status', 'unknown')})",
            f"磁盘: {disk.get('percent', 0):.1f}% ({disk.get('status', 'unknown')})",
            ""
        ])

        # 引擎状态
        engines = sections.get("engine_states", {})
        available = sum(1 for e in engines.get("engines", {}).values() if e.get("exists", False))
        total = len(engines.get("engines", {}))
        summary_lines.extend([
            "--- 引擎状态 ---",
            f"可用引擎: {available}/{total}",
            ""
        ])

        # 建议
        recommendations = report.get("recommendations", [])
        if recommendations:
            summary_lines.append("--- 优化建议 ---")
            for rec in recommendations[:5]:
                summary_lines.append(f"[{rec.get('priority', '').upper()}] {rec.get('issue', '')}")
                summary_lines.append(f"  建议: {rec.get('suggestion', '')}")
            summary_lines.append("")

        return "\n".join(summary_lines)


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="智能系统自检与健康报告引擎")
    parser.add_argument("--check", action="store_true", help="运行健康检查")
    parser.add_argument("--report", action="store_true", help="生成详细报告")
    parser.add_argument("--summary", action="store_true", help="生成摘要报告")
    parser.add_argument("--output", choices=["json", "summary"], default="json", help="输出格式")

    args = parser.parse_args()

    engine = SystemHealthReportEngine()

    if args.check or args.report or args.summary or (not args.check and not args.report and not args.summary):
        output = engine.run_health_check(output_format=args.output)
        print(output)


if __name__ == "__main__":
    main()