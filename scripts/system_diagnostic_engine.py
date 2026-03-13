"""
智能系统综合诊断引擎
集成多个诊断模块的能力，实现跨模块的问题追踪和综合诊断
"""
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

# 添加脚本目录到路径
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))


class SystemDiagnosticEngine:
    """智能系统综合诊断引擎"""

    def __init__(self):
        self.diagnostics_dir = SCRIPT_DIR.parent / "runtime" / "state"
        self.diagnostics_dir.mkdir(parents=True, exist_ok=True)
        self.diagnostic_history_file = self.diagnostics_dir / "diagnostic_history.json"
        self.diagnostic_history = self._load_diagnostic_history()

    def _load_diagnostic_history(self) -> List[Dict]:
        """加载诊断历史"""
        if self.diagnostic_history_file.exists():
            try:
                with open(self.diagnostic_history_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return []
        return []

    def _save_diagnostic_history(self):
        """保存诊断历史"""
        try:
            with open(self.diagnostic_history_file, "w", encoding="utf-8") as f:
                json.dump(self.diagnostic_history[-100:], f, ensure_ascii=False, indent=2)
        except:
            pass

    def run_comprehensive_diagnostic(self, include_modules: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        运行综合诊断

        Args:
            include_modules: 要包含的诊断模块列表，None 表示全部

        Returns:
            包含所有诊断结果的综合报告
        """
        diagnostic_result = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "healthy",
            "issues_found": [],
            "module_diagnostics": {},
            "recommendations": [],
            "cross_module_analysis": {}
        }

        modules_to_run = include_modules or ["self_healing", "predictive_prevention", "system_health", "evolution_health"]

        # 1. 自愈引擎诊断
        if "self_healing" in modules_to_run:
            self._run_self_healing_diagnostic(diagnostic_result)

        # 2. 预测预防引擎诊断
        if "predictive_prevention" in modules_to_run:
            self._run_predictive_prevention_diagnostic(diagnostic_result)

        # 3. 系统健康监控诊断
        if "system_health" in modules_to_run:
            self._run_system_health_diagnostic(diagnostic_result)

        # 4. 进化环健康诊断
        if "evolution_health" in modules_to_run:
            self._run_evolution_health_diagnostic(diagnostic_result)

        # 5. 跨模块问题关联分析
        self._analyze_cross_module_issues(diagnostic_result)

        # 6. 生成智能修复建议
        self._generate_recommendations(diagnostic_result)

        # 7. 确定整体状态
        if diagnostic_result["issues_found"]:
            critical_count = sum(1 for i in diagnostic_result["issues_found"] if i.get("severity") == "critical")
            if critical_count > 0:
                diagnostic_result["overall_status"] = "critical"
            else:
                diagnostic_result["overall_status"] = "warning"

        # 保存诊断历史
        self.diagnostic_history.append({
            "timestamp": diagnostic_result["timestamp"],
            "overall_status": diagnostic_result["overall_status"],
            "issues_count": len(diagnostic_result["issues_found"])
        })
        self._save_diagnostic_history()

        return diagnostic_result

    def _run_self_healing_diagnostic(self, result: Dict[str, Any]):
        """运行自愈引擎诊断"""
        try:
            from self_healing_engine import SelfHealingEngine
            healer = SelfHealingEngine()
            check_results = healer.check_all()

            issues = []
            for check in check_results:
                # DiagnosticResult 使用 detected 表示是否检测到问题
                if check.detected and check.severity in ["warning", "critical", "error"]:
                    issues.append({
                        "module": "self_healing",
                        "check": check.issue_type,
                        "status": check.severity,
                        "message": check.description,
                        "suggestion": check.solution
                    })

            result["module_diagnostics"]["self_healing"] = {
                "status": "ok" if not issues else "issues_found",
                "checks_run": len(check_results),
                "issues": issues
            }

            if issues:
                result["issues_found"].extend(issues)

        except Exception as e:
            result["module_diagnostics"]["self_healing"] = {
                "status": "error",
                "error": str(e)
            }
            result["issues_found"].append({
                "module": "self_healing",
                "severity": "warning",
                "message": f"自愈引擎诊断失败: {str(e)}"
            })

    def _run_predictive_prevention_diagnostic(self, result: Dict[str, Any]):
        """运行预测预防引擎诊断"""
        try:
            from predictive_prevention_engine import PredictivePreventionEngine
            predictor = PredictivePreventionEngine()

            scan_result = scan_result = predictor.scan_and_predict()

            issues = []
            if scan_result.get("system_risk_level") in ["critical", "high"]:
                issues.append({
                    "module": "predictive_prevention",
                    "check": "system_risk",
                    "status": scan_result.get("system_risk_level"),
                    "message": f"系统风险等级: {scan_result.get('system_risk_level')}",
                    "metrics": scan_result.get("metrics", {})
                })

            predicted_issues = scan_result.get("predicted_issues", [])
            for issue in predicted_issues:
                if issue.get("risk_level") in ["critical", "high"]:
                    issues.append({
                        "module": "predictive_prevention",
                        "check": "predicted_issue",
                        "status": issue.get("risk_level"),
                        "message": issue.get("description", ""),
                        "suggestion": issue.get("suggestion", "")
                    })

            result["module_diagnostics"]["predictive_prevention"] = {
                "status": "ok" if not issues else "warning",
                "risk_level": scan_result.get("system_risk_level", "unknown"),
                "issues": issues
            }

            if issues:
                result["issues_found"].extend(issues)

        except Exception as e:
            result["module_diagnostics"]["predictive_prevention"] = {
                "status": "error",
                "error": str(e)
            }

    def _run_system_health_diagnostic(self, result: Dict[str, Any]):
        """运行系统健康监控诊断"""
        try:
            from system_health_monitor import SystemHealthMonitor
            monitor = SystemHealthMonitor()

            # 使用 get_health_report() 获取详细信息
            health_report = monitor.get_health_report()
            system_status = monitor.get_system_status()

            issues = []
            # 检查各项指标
            metrics = health_report.get("system_metrics", {})

            # CPU 检查
            cpu = metrics.get("cpu_percent", 0)
            if cpu > 90:
                issues.append({
                    "module": "system_health",
                    "check": "cpu",
                    "status": "critical",
                    "message": f"CPU使用率过高: {cpu}%",
                    "suggestion": "关闭不必要的进程或重启系统"
                })

            # 内存检查
            memory = metrics.get("memory_percent", 0)
            if memory > 90:
                issues.append({
                    "module": "system_health",
                    "check": "memory",
                    "status": "critical",
                    "message": f"内存使用率过高: {memory}%",
                    "suggestion": "释放内存或增加物理内存"
                })

            # 磁盘检查
            disk = metrics.get("disk_percent", 0)
            if disk > 90:
                issues.append({
                    "module": "system_health",
                    "check": "disk",
                    "status": "warning",
                    "message": f"磁盘使用率过高: {disk}%",
                    "suggestion": "清理磁盘空间"
                })

            result["module_diagnostics"]["system_health"] = {
                "status": "ok" if not issues else "warning",
                "metrics": metrics,
                "issues": issues
            }

            if issues:
                result["issues_found"].extend(issues)

        except Exception as e:
            result["module_diagnostics"]["system_health"] = {
                "status": "error",
                "error": str(e)
            }

    def _run_evolution_health_diagnostic(self, result: Dict[str, Any]):
        """运行进化环健康诊断"""
        try:
            # 检查进化环状态
            current_mission_file = self.diagnostics_dir.parent / "state" / "current_mission.json"
            evolution_state = {}

            if current_mission_file.exists():
                with open(current_mission_file, "r", encoding="utf-8") as f:
                    evolution_state = json.load(f)

            issues = []

            # 检查进化轮次
            loop_round = evolution_state.get("loop_round", 0)
            if loop_round < 100:
                issues.append({
                    "module": "evolution_health",
                    "check": "evolution_round",
                    "status": "info",
                    "message": f"进化轮次: {loop_round}",
                    "suggestion": "系统正在持续进化中"
                })

            # 检查进化状态
            phase = evolution_state.get("phase", "unknown")
            if phase in ["假设", "规划", "执行", "校验", "反思"]:
                pass  # 正常状态
            else:
                issues.append({
                    "module": "evolution_health",
                    "check": "evolution_phase",
                    "status": "warning",
                    "message": f"进化阶段异常: {phase}",
                    "suggestion": "检查进化环状态"
                })

            result["module_diagnostics"]["evolution_health"] = {
                "status": "ok",
                "loop_round": loop_round,
                "phase": phase,
                "issues": issues
            }

        except Exception as e:
            result["module_diagnostics"]["evolution_health"] = {
                "status": "error",
                "error": str(e)
            }

    def _analyze_cross_module_issues(self, result: Dict[str, Any]):
        """跨模块问题关联分析"""
        cross_analysis = {
            "correlated_issues": [],
            "root_causes": []
        }

        issues = result.get("issues_found", [])

        # 检查是否有多个模块报告相同类型的问题
        issue_types = {}
        for issue in issues:
            module = issue.get("module", "unknown")
            check = issue.get("check", "unknown")
            key = f"{module}:{check}"
            issue_types[key] = issue_types.get(key, 0) + 1

        # 找出重复问题
        for key, count in issue_types.items():
            if count > 1:
                cross_analysis["correlated_issues"].append({
                    "issue_key": key,
                    "affected_modules": count,
                    "description": f"问题 {key} 被多个模块报告"
                })

        # 根因分析
        # 如果系统健康和预测预防都报告问题，可能是系统资源问题
        has_system_health_issue = any(i.get("module") == "system_health" for i in issues)
        has_predictive_issue = any(i.get("module") == "predictive_prevention" for i in issues)

        if has_system_health_issue and has_predictive_issue:
            cross_analysis["root_causes"].append({
                "likely_cause": "系统资源不足",
                "confidence": "high",
                "description": "系统健康和预测预防引擎同时发现问题，可能是系统资源不足导致的连锁反应"
            })

        result["cross_module_analysis"] = cross_analysis

    def _generate_recommendations(self, result: Dict[str, Any]):
        """生成智能修复建议"""
        recommendations = []

        issues = result.get("issues_found", [])

        # 按模块分组
        by_module = {}
        for issue in issues:
            module = issue.get("module", "unknown")
            if module not in by_module:
                by_module[module] = []
            by_module[module].append(issue)

        # 生成建议
        for module, module_issues in by_module.items():
            severity = "low"
            for issue in module_issues:
                if issue.get("status") == "critical":
                    severity = "critical"
                    break
                elif issue.get("status") == "warning" and severity != "critical":
                    severity = "warning"

            if module == "system_health":
                recommendations.append({
                    "priority": 1 if severity == "critical" else 2,
                    "category": "系统资源",
                    "action": "优化系统资源使用",
                    "details": "检查并关闭占用资源过多的进程"
                })
            elif module == "self_healing":
                recommendations.append({
                    "priority": 2,
                    "category": "自愈修复",
                    "action": "运行自愈引擎自动修复",
                    "details": "执行自愈引擎的自动修复功能"
                })
            elif module == "predictive_prevention":
                recommendations.append({
                    "priority": 2,
                    "category": "预防措施",
                    "action": "执行预防性优化",
                    "details": "根据预测结果执行预防措施"
                })

        # 跨模块建议
        if len(by_module) > 1:
            recommendations.append({
                "priority": 1,
                "category": "综合",
                "action": "运行完整系统诊断",
                "details": "多个模块发现问题，建议运行完整综合诊断"
            })

        # 按优先级排序
        recommendations.sort(key=lambda x: x.get("priority", 999))
        result["recommendations"] = recommendations

    def get_diagnostic_history(self, limit: int = 10) -> List[Dict]:
        """获取诊断历史"""
        return self.diagnostic_history[-limit:]

    def get_quick_status(self) -> Dict[str, Any]:
        """快速状态检查"""
        try:
            result = self.run_comprehensive_diagnostic()
            return {
                "status": result["overall_status"],
                "issues_count": len(result.get("issues_found", [])),
                "recommendations_count": len(result.get("recommendations", [])),
                "timestamp": result["timestamp"]
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }


def main():
    """CLI 入口"""
    import argparse

    parser = argparse.ArgumentParser(description="智能系统综合诊断引擎")
    parser.add_argument("--diagnose", "-d", action="store_true", help="运行完整综合诊断")
    parser.add_argument("--quick", "-q", action="store_true", help="快速状态检查")
    parser.add_argument("--history", action="store_true", help="查看诊断历史")
    parser.add_argument("--modules", nargs="+", help="指定要运行的诊断模块")
    parser.add_argument("--output", "-o", help="输出到文件")

    args = parser.parse_args()

    engine = SystemDiagnosticEngine()

    if args.diagnose or (not args.quick and not args.history):
        result = engine.run_comprehensive_diagnostic(args.modules)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"\n诊断报告已保存到: {args.output}")

    elif args.quick:
        result = engine.get_quick_status()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.history:
        history = engine.get_diagnostic_history()
        print(json.dumps(history, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()