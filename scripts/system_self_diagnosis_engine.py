"""
智能系统自检与健康报告引擎
让系统能够自动进行全面健康检查、生成详细状态报告、提供健康建议，实现元进化方向的自我审视能力

功能：
1. 全面健康检查：整合各引擎状态、执行历史、资源使用
2. 智能分析：基于检查结果进行智能分析，识别问题模式
3. 报告生成：生成详细的状态报告，包含健康评分和建议
4. 趋势分析：追踪健康指标变化趋势
5. 自动化建议：根据分析结果提供具体的优化建议
"""

import sys
import io
# 设置 UTF-8 编码，避免 Windows 下的 UnicodeEncodeError
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import json
import os
import subprocess
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
RUNTIME_STATE = PROJECT_ROOT / "runtime" / "state"
RUNTIME_LOGS = PROJECT_ROOT / "runtime" / "logs"


class SystemSelfDiagnosisEngine:
    """智能系统自检与健康报告引擎"""

    def __init__(self):
        self.data_dir = RUNTIME_STATE
        self.logs_dir = RUNTIME_LOGS
        self.results = {}
        self.health_score = 0
        self.issues = []
        self.recommendations = []

    def run_full_diagnosis(self, verbose: bool = True) -> Dict[str, Any]:
        """运行全面健康诊断"""
        if verbose:
            print("=" * 60)
            print("🔍 智能系统自检与健康报告")
            print("=" * 60)

        # 1. 检查各引擎状态
        engine_status = self._check_engines_status()
        if verbose:
            total_engines = engine_status.get('total', 0)
            active_count = len(engine_status.get('active', []))
            print(f"\n📊 引擎状态检查：{active_count}/{total_engines} 活跃")

        # 2. 检查执行历史
        execution_history = self._check_execution_history()
        if verbose:
            recent_count = execution_history.get('recent_24h', {}).get('total', 0)
            print(f"📈 执行历史检查：过去24小时执行 {recent_count} 次")

        # 3. 检查资源使用
        resource_status = self._check_resources()
        if verbose:
            print(f"💾 资源使用：CPU {resource_status.get('cpu_percent', 'N/A')}%, 内存 {resource_status.get('memory_percent', 'N/A')}%")

        # 4. 检查进化历史
        evolution_status = self._check_evolution_history()
        if verbose:
            print(f"🔄 进化状态：{evolution_status.get('completed_rounds', 0)} 轮完成")

        # 5. 检查守护进程
        daemon_status = self._check_daemons()
        if verbose:
            print(f"🛡️ 守护进程：{daemon_status.get('running_count', 0)}/{daemon_status.get('total', 0)} 运行中")

        # 6. 智能分析和生成报告
        self._analyze_results(engine_status, execution_history, resource_status, evolution_status, daemon_status)

        # 7. 计算健康评分
        self._calculate_health_score()

        # 8. 生成报告
        report = self._generate_report(engine_status, execution_history, resource_status, evolution_status, daemon_status)

        if verbose:
            print(f"\n📋 健康评分：{self.health_score}/100")
            if self.recommendations:
                print(f"\n💡 建议：")
                for i, rec in enumerate(self.recommendations[:5], 1):
                    print(f"   {i}. {rec}")

        return report

    def _check_engines_status(self) -> Dict[str, Any]:
        """检查各引擎状态"""
        # 扫描 scripts 目录下的引擎
        scripts_dir = PROJECT_ROOT / "scripts"
        engines = []

        for f in scripts_dir.glob("*.py"):
            if f.name.startswith("_") or f.name in ["do.py", "run_with_env.py"]:
                continue
            # 统计引擎文件（排除测试和工具类）
            if f.stat().st_size > 1000:  # 大于1KB的可能是引擎
                engines.append(f.name)

        # 检查引擎注册表或相关状态
        engine_registry = RUNTIME_STATE / "engine_registry.json"
        active_engines = []
        if engine_registry.exists():
            try:
                with open(engine_registry, "r", encoding="utf-8") as f:
                    registry = json.load(f)
                    active_engines = list(registry.keys()) if isinstance(registry, dict) else []
            except:
                pass

        return {
            "total": len(engines),
            "active": active_engines,
            "timestamp": datetime.now().isoformat()
        }

    def _check_execution_history(self) -> Dict[str, Any]:
        """检查执行历史"""
        history = {
            "recent_24h": {"total": 0, "success": 0, "failed": 0},
            "recent_7d": {"total": 0, "success": 0, "failed": 0}
        }

        # 读取 recent_logs.json
        recent_logs = RUNTIME_STATE / "recent_logs.json"
        if recent_logs.exists():
            try:
                with open(recent_logs, "r", encoding="utf-8") as f:
                    logs = json.load(f)
                    entries = logs.get("entries", [])

                    now = datetime.now()
                    for entry in entries:
                        # 解析时间
                        try:
                            entry_time = datetime.fromisoformat(entry.get("time", "").replace("+00:00", ""))
                            age_hours = (now - entry_time).total_seconds() / 3600

                            if age_hours <= 24:
                                history["recent_24h"]["total"] += 1
                                if entry.get("result") == "pass":
                                    history["recent_24h"]["success"] += 1
                                elif entry.get("result") == "fail":
                                    history["recent_24h"]["failed"] += 1

                            if age_hours <= 168:  # 7天
                                history["recent_7d"]["total"] += 1
                                if entry.get("result") == "pass":
                                    history["recent_7d"]["success"] += 1
                                elif entry.get("result") == "fail":
                                    history["recent_7d"]["failed"] += 1
                        except:
                            continue
            except:
                pass

        return history

    def _check_resources(self) -> Dict[str, Any]:
        """检查资源使用"""
        resources = {
            "cpu_percent": "N/A",
            "memory_percent": "N/A",
            "disk_percent": "N/A"
        }

        try:
            import psutil

            resources["cpu_percent"] = psutil.cpu_percent(interval=0.5)
            resources["memory_percent"] = psutil.virtual_memory().percent
            resources["disk_percent"] = psutil.disk_usage('/').percent

        except ImportError:
            # 如果没有 psutil，使用基本方法
            pass
        except Exception:
            pass

        return resources

    def _check_evolution_history(self) -> Dict[str, Any]:
        """检查进化历史"""
        evolution_status = {
            "completed_rounds": 0,
            "last_evolution": None,
            "pending_count": 0
        }

        # 读取 current_mission.json
        current_mission = RUNTIME_STATE / "current_mission.json"
        if current_mission.exists():
            try:
                with open(current_mission, "r", encoding="utf-8") as f:
                    mission = json.load(f)
                    evolution_status["current_round"] = mission.get("loop_round", 0)
            except:
                pass

        # 统计完成的进化轮次
        completed_count = 0
        for f in RUNTIME_STATE.glob("evolution_completed_*.json"):
            completed_count += 1

        evolution_status["completed_rounds"] = completed_count

        # 查找最新的进化记录
        latest_file = RUNTIME_STATE / "evolution_auto_last.md"
        if latest_file.exists():
            try:
                content = latest_file.read_text(encoding="utf-8")
                match = re.search(r'Round (\d+)', content)
                if match:
                    evolution_status["last_round"] = int(match.group(1))
            except:
                pass

        return evolution_status

    def _check_daemons(self) -> Dict[str, Any]:
        """检查守护进程状态"""
        daemon_status = {
            "total": 0,
            "running_count": 0,
            "daemons": []
        }

        # 检查守护进程状态文件
        daemon_state = RUNTIME_STATE / "daemon_status.json"
        if daemon_state.exists():
            try:
                with open(daemon_state, "r", encoding="utf-8") as f:
                    status = json.load(f)
                    daemon_status["total"] = status.get("total", 0)
                    daemon_status["running_count"] = status.get("running_count", 0)
                    daemon_status["daemons"] = status.get("daemons", [])
            except:
                pass

        return daemon_status

    def _analyze_results(self, engine_status, execution_history, resource_status, evolution_status, daemon_status):
        """分析结果并生成问题和建议"""
        self.issues = []
        self.recommendations = []

        # 分析引擎状态
        total_engines = engine_status.get("total", 0)
        active_engines = len(engine_status.get("active", []))
        if total_engines > 0 and active_engines < total_engines * 0.5:
            self.issues.append(f"引擎活跃度较低：{active_engines}/{total_engines}")
            self.recommendations.append("检查引擎注册，确保引擎被正确加载")

        # 分析执行历史
        recent_24h = execution_history.get("recent_24h", {})
        if recent_24h.get("total", 0) == 0:
            self.recommendations.append("近期无执行记录，系统可能处于空闲状态")
        elif recent_24h.get("failed", 0) > recent_24h.get("total", 1) * 0.3:
            self.issues.append(f"失败率较高：{recent_24h['failed']}/{recent_24h['total']}")
            self.recommendations.append("检查执行失败原因，优化执行策略")

        # 分析资源使用
        cpu = resource_status.get("cpu_percent")
        memory = resource_status.get("memory_percent")
        if cpu != "N/A" and cpu > 80:
            self.issues.append(f"CPU 使用率较高：{cpu}%")
            self.recommendations.append("优化系统资源使用，关闭不必要的进程")
        if memory != "N/A" and memory > 80:
            self.issues.append(f"内存使用率较高：{memory}%")
            self.recommendations.append("清理内存，释放资源")

        # 分析守护进程
        daemon = daemon_status
        if daemon.get("total", 0) > 0:
            running = daemon.get("running_count", 0)
            total = daemon.get("total", 1)
            if running < total * 0.5:
                self.issues.append(f"守护进程运行较少：{running}/{total}")
                self.recommendations.append("检查守护进程配置，确保关键守护进程运行")

        # 如果没有问题，添加正面反馈
        if not self.issues:
            self.recommendations.append("系统运行正常，继续保持")
        else:
            self.recommendations.append("建议运行智能自动化质量保障引擎进行详细检测")

    def _calculate_health_score(self):
        """计算健康评分"""
        score = 100

        # 根据问题数量扣分
        score -= len(self.issues) * 10

        # 根据建议数量调整
        if self.recommendations:
            score -= len(self.recommendations) * 2

        # 确保分数在 0-100 范围内
        self.health_score = max(0, min(100, score))

    def _generate_report(self, engine_status, execution_history, resource_status, evolution_status, daemon_status) -> Dict[str, Any]:
        """生成完整报告"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "health_score": self.health_score,
            "issues": self.issues,
            "recommendations": self.recommendations,
            "details": {
                "engines": engine_status,
                "execution": execution_history,
                "resources": resource_status,
                "evolution": evolution_status,
                "daemons": daemon_status
            }
        }

        # 保存报告
        report_path = self.data_dir / "system_health_diagnosis_report.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        return report

    def get_quick_status(self) -> Dict[str, Any]:
        """快速获取状态摘要"""
        return {
            "health_score": self.health_score,
            "issues_count": len(self.issues),
            "recommendations_count": len(self.recommendations),
            "timestamp": datetime.now().isoformat()
        }

    def get_detailed_report(self) -> Dict[str, Any]:
        """获取详细报告"""
        report_path = self.data_dir / "system_health_diagnosis_report.json"
        if report_path.exists():
            with open(report_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}


def main():
    """CLI 入口"""
    import argparse

    parser = argparse.ArgumentParser(description="智能系统自检与健康报告引擎")
    parser.add_argument("--full", action="store_true", help="运行全面健康诊断")
    parser.add_argument("--quick", action="store_true", help="快速状态检查")
    parser.add_argument("--report", action="store_true", help="显示详细报告")
    parser.add_argument("--verbose", "-v", action="store_true", default=True, help="详细输出")

    args = parser.parse_args()

    engine = SystemSelfDiagnosisEngine()

    if args.full or not args.quick:
        report = engine.run_full_diagnosis(verbose=args.verbose)
        print(f"\n📄 报告已保存到：{RUNTIME_STATE / 'system_health_diagnosis_report.json'}")
    elif args.quick:
        status = engine.get_quick_status()
        print(f"健康评分：{status['health_score']}/100")
        print(f"问题数量：{status['issues_count']}")
        print(f"建议数量：{status['recommendations_count']}")

    if args.report:
        print("\n" + "=" * 60)
        print("📋 详细报告")
        print("=" * 60)
        report = engine.get_detailed_report()
        print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()