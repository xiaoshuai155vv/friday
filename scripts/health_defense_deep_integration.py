#!/usr/bin/env python3
"""
智能全场景系统健康防御深度协同引擎（Round 326）

深度协同各健康相关引擎（健康监控、预警、自愈、预测预防），形成统一防御闭环。

功能：
1. 统一健康入口 - 一个接口协同所有健康引擎
2. 全链路防御协同 - 预警→诊断→修复→验证自动流转
3. 智能防御策略 - 根据问题类型自动选择最优修复方案
4. 防御效果追踪与分析

依赖模块：
- system_health_check.py / system_health_monitor.py
- system_health_report_engine.py
- health_assurance_loop.py
- self_healing_engine.py
- evolution_loop_self_healing_engine.py
- evolution_loop_self_healing_advanced.py
- predictive_prevention_engine.py
- failure_predictor.py
- system_health_alert_engine.py
"""

import json
import os
import sys
import subprocess
import traceback
from datetime import datetime
from pathlib import Path

# 添加 scripts 目录到路径
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))


class HealthDefenseDeepIntegration:
    """智能全场景系统健康防御深度协同引擎"""

    def __init__(self):
        self.version = "1.0.0"
        self.name = "health_defense_deep_integration"
        self.description = "深度协同各健康引擎，形成统一防御闭环"

        # 健康引擎注册表
        self.health_engines = {
            "health_monitor": {
                "path": "system_health_monitor.py",
                "capability": "实时监控系统健康状态"
            },
            "health_check": {
                "path": "system_health_check.py",
                "capability": "执行健康检查"
            },
            "health_report": {
                "path": "system_health_report_engine.py",
                "capability": "生成健康报告"
            },
            "health_assurance": {
                "path": "health_assurance_loop.py",
                "capability": "健康保障闭环"
            },
            "self_healing": {
                "path": "self_healing_engine.py",
                "capability": "自动问题修复"
            },
            "evolution_self_healing": {
                "path": "evolution_loop_self_healing_engine.py",
                "capability": "进化环自愈"
            },
            "evolution_self_healing_advanced": {
                "path": "evolution_loop_self_healing_advanced.py",
                "capability": "进化环高级自愈"
            },
            "predictive_prevention": {
                "path": "predictive_prevention_engine.py",
                "capability": "预测预防"
            },
            "failure_predictor": {
                "path": "failure_predictor.py",
                "capability": "故障预测"
            },
            "health_alert": {
                "path": "system_health_alert_engine.py",
                "capability": "健康预警"
            }
        }

        # 防御策略映射
        self.defense_strategies = {
            "critical": {
                "priority": 1,
                "engines": ["health_alert", "self_healing", "health_assurance"],
                "auto_fix": True
            },
            "warning": {
                "priority": 2,
                "engines": ["predictive_prevention", "failure_predictor", "health_check"],
                "auto_fix": True
            },
            "info": {
                "priority": 3,
                "engines": ["health_monitor", "health_report"],
                "auto_fix": False
            }
        }

        # 防御历史记录
        self.defense_history = []
        self.load_history()

    def load_history(self):
        """加载防御历史"""
        history_file = SCRIPT_DIR / "runtime" / "state" / "health_defense_history.json"
        if history_file.exists():
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    self.defense_history = json.load(f)
            except:
                self.defense_history = []

    def save_history(self):
        """保存防御历史"""
        history_file = SCRIPT_DIR / "runtime" / "state" / "health_defense_history.json"
        history_file.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(self.defense_history, f, ensure_ascii=False, indent=2)
        except:
            pass

    def check_engine_available(self, engine_name: str) -> bool:
        """检查引擎是否可用"""
        if engine_name not in self.health_engines:
            return False

        engine_path = SCRIPT_DIR / self.health_engines[engine_name]["path"]
        return engine_path.exists()

    def coordinate_health_check(self) -> dict:
        """协同健康检查 - 一次调用获取全面健康状态"""
        result = {
            "timestamp": datetime.now().isoformat(),
            "engines_checked": [],
            "overall_status": "unknown",
            "issues": [],
            "recommendations": []
        }

        # 1. 执行基础健康检查
        try:
            if self.check_engine_available("health_check"):
                check_result = self._call_engine("health_check", ["--json"])
                result["engines_checked"].append("health_check")
                if check_result:
                    result["issues"].extend(check_result.get("issues", []))
        except Exception as e:
            result["issues"].append(f"health_check error: {str(e)}")

        # 2. 执行健康监控
        try:
            if self.check_engine_available("health_monitor"):
                monitor_result = self._call_engine("health_monitor", ["--status"])
                result["engines_checked"].append("health_monitor")
                if monitor_result:
                    result["issues"].extend(monitor_result.get("issues", []))
        except Exception as e:
            result["issues"].append(f"health_monitor error: {str(e)}")

        # 3. 生成健康报告
        try:
            if self.check_engine_available("health_report"):
                report_result = self._call_engine("health_report", ["--brief"])
                result["engines_checked"].append("health_report")
                if report_result:
                    result["recommendations"].extend(report_result.get("recommendations", []))
        except Exception as e:
            result["issues"].append(f"health_report error: {str(e)}")

        # 4. 预测预防检查
        try:
            if self.check_engine_available("predictive_prevention"):
                prediction_result = self._call_engine("predictive_prevention", ["--predict"])
                result["engines_checked"].append("predictive_prevention")
                if prediction_result:
                    result["recommendations"].extend(prediction_result.get("warnings", []))
        except Exception as e:
            result["issues"].append(f"predictive_prevention error: {str(e)}")

        # 5. 故障预测检查
        try:
            if self.check_engine_available("failure_predictor"):
                failure_result = self._call_engine("failure_predictor", ["--analyze"])
                result["engines_checked"].append("failure_predictor")
                if failure_result:
                    result["recommendations"].extend(failure_result.get("predictions", []))
        except Exception as e:
            result["issues"].append(f"failure_predictor error: {str(e)}")

        # 确定总体状态
        if len(result["issues"]) > 5:
            result["overall_status"] = "critical"
        elif len(result["issues"]) > 0:
            result["overall_status"] = "warning"
        else:
            result["overall_status"] = "healthy"

        return result

    def auto_repair(self, issue: dict) -> dict:
        """自动修复问题"""
        issue_type = issue.get("type", "unknown")
        result = {
            "issue": issue_type,
            "repair_attempted": False,
            "repair_success": False,
            "engines_used": [],
            "message": ""
        }

        # 根据问题类型选择修复策略
        if issue_type in ["process", "memory", "cpu"]:
            # 使用自愈引擎
            try:
                if self.check_engine_available("self_healing"):
                    repair_result = self._call_engine("self_healing", ["--fix", issue_type])
                    result["repair_attempted"] = True
                    result["engines_used"].append("self_healing")
                    if repair_result and repair_result.get("success"):
                        result["repair_success"] = True
                        result["message"] = f"使用 self_healing 成功修复 {issue_type}"
            except Exception as e:
                result["message"] = f"self_healing 修复失败: {str(e)}"

        elif issue_type in ["evolution", "loop"]:
            # 使用进化环自愈引擎
            try:
                if self.check_engine_available("evolution_self_healing_advanced"):
                    repair_result = self._call_engine("evolution_loop_self_healing_advanced", ["--repair"])
                    result["repair_attempted"] = True
                    result["engines_used"].append("evolution_self_healing_advanced")
                    if repair_result and repair_result.get("success"):
                        result["repair_success"] = True
                        result["message"] = f"使用 evolution_self_healing_advanced 成功修复 {issue_type}"
            except Exception as e:
                result["message"] = f"evolution_self_healing 修复失败: {str(e)}"

        else:
            result["message"] = f"未知问题类型: {issue_type}"

        return result

    def run_full_defense_cycle(self) -> dict:
        """运行完整防御周期 - 预警→诊断→修复→验证"""
        cycle_result = {
            "start_time": datetime.now().isoformat(),
            "stages": {},
            "issues_found": 0,
            "issues_repaired": 0,
            "overall_status": "unknown"
        }

        # 阶段1: 预警
        try:
            if self.check_engine_available("health_alert"):
                alert_result = self._call_engine("health_alert", ["--check"])
                cycle_result["stages"]["warning"] = {
                    "executed": True,
                    "alerts": alert_result.get("alerts", []) if alert_result else []
                }
        except Exception as e:
            cycle_result["stages"]["warning"] = {"executed": False, "error": str(e)}

        # 阶段2: 诊断
        diagnosis_result = self.coordinate_health_check()
        cycle_result["stages"]["diagnosis"] = diagnosis_result
        cycle_result["issues_found"] = len(diagnosis_result.get("issues", [])) + len(diagnosis_result.get("recommendations", []))

        # 阶段3: 修复 (仅对关键和警告级别)
        if diagnosis_result["overall_status"] in ["critical", "warning"]:
            repaired_issues = []
            for issue in diagnosis_result.get("issues", []):
                repair_result = self.auto_repair(issue)
                if repair_result["repair_success"]:
                    repaired_issues.append(repair_result)
                    cycle_result["issues_repaired"] += 1

            cycle_result["stages"]["repair"] = {
                "executed": True,
                "repaired": repaired_issues
            }

        # 阶段4: 验证
        verification_result = self.coordinate_health_check()
        cycle_result["stages"]["verification"] = verification_result
        cycle_result["end_time"] = datetime.now().isoformat()

        # 确定最终状态
        if verification_result["overall_status"] == "healthy":
            cycle_result["overall_status"] = "success"
        elif verification_result["overall_status"] == "warning":
            cycle_result["overall_status"] = "partial"
        else:
            cycle_result["overall_status"] = "failed"

        # 记录到历史
        self.defense_history.append(cycle_result)
        self.save_history()

        return cycle_result

    def _call_engine(self, engine_name: str, args: list) -> dict:
        """调用其他引擎"""
        engine_path = self.health_engines.get(engine_name, {}).get("path", "")
        if not engine_path:
            return {}

        full_path = SCRIPT_DIR / engine_path
        if not full_path.exists():
            return {}

        try:
            cmd = [sys.executable, str(full_path)] + args
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                encoding='utf-8',
                errors='ignore'
            )
            # 尝试解析 JSON 输出
            try:
                return json.loads(result.stdout)
            except:
                return {"output": result.stdout, "success": result.returncode == 0}
        except subprocess.TimeoutExpired:
            return {"error": "timeout"}
        except Exception as e:
            return {"error": str(e)}

    def get_status(self) -> dict:
        """获取防御系统状态"""
        return {
            "name": self.name,
            "version": self.version,
            "engines_registered": len(self.health_engines),
            "engines_available": sum(1 for k in self.health_engines if self.check_engine_available(k)),
            "defense_strategies": len(self.defense_strategies),
            "history_entries": len(self.defense_history),
            "capabilities": [
                "统一健康入口 - 一个接口协同所有健康引擎",
                "全链路防御协同 - 预警→诊断→修复→验证自动流转",
                "智能防御策略 - 根据问题类型自动选择最优修复方案",
                "防御效果追踪与分析"
            ]
        }

    def get_dashboard(self) -> dict:
        """获取防御仪表盘"""
        # 快速健康检查
        health_status = self.coordinate_health_check()

        # 最近防御记录
        recent_defenses = self.defense_history[-5:] if len(self.defense_history) >= 5 else self.defense_history

        # 引擎状态
        engine_status = {}
        for engine_name in self.health_engines:
            engine_status[engine_name] = self.check_engine_available(engine_name)

        return {
            "system_status": health_status.get("overall_status", "unknown"),
            "engines_available": sum(1 for v in engine_status.values() if v),
            "engines_total": len(engine_status),
            "recent_defenses": len(recent_defenses),
            "engine_status": engine_status,
            "last_check": health_status.get("timestamp")
        }


def main():
    """主入口"""
    import argparse

    parser = argparse.ArgumentParser(description="智能全场景系统健康防御深度协同引擎")
    parser.add_argument("--status", action="store_true", help="获取防御系统状态")
    parser.add_argument("--dashboard", action="store_true", help="获取防御仪表盘")
    parser.add_argument("--check", action="store_true", help="执行协同健康检查")
    parser.add_argument("--full-cycle", action="store_true", help="运行完整防御周期")
    parser.add_argument("--repair", type=str, help="自动修复指定问题类型")

    args = parser.parse_args()

    engine = HealthDefenseDeepIntegration()

    if args.status:
        result = engine.get_status()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.dashboard:
        result = engine.get_dashboard()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.check:
        result = engine.coordinate_health_check()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.full_cycle:
        result = engine.run_full_defense_cycle()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.repair:
        result = engine.auto_repair({"type": args.repair})
        print(json.dumps(result, ensure_ascii=False, indent=2))

    else:
        # 默认显示状态
        result = engine.get_status()
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()