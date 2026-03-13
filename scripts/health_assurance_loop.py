#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
智能系统健康保障闭环引擎
将主动运维引擎、自愈引擎、预测预防引擎深度集成，
形成"监控→预测→运维→自愈→反馈"的完整服务保障闭环。

功能：
- 统一健康保障入口：整合主动运维、自愈、预测预防三大引擎
- 深度联动机制：问题检测→自动修复→效果追踪的闭环
- 风险预警→预防性维护→执行确认的闭环
- 健康状态报告：统一展示系统健康全景

用法:
  python health_assurance_loop.py status
  python health_assurance_loop.py scan
  python health_assurance_loop.py full-loop
  python health_assurance_loop.py report
"""

import argparse
import json
import os
import sys
import subprocess
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from collections import defaultdict

# 路径配置
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
STATE_DIR = os.path.join(PROJECT_ROOT, "runtime", "state")
ASSURANCE_LOG_FILE = os.path.join(STATE_DIR, "health_assurance_log.json")

# 导入相关引擎
sys.path.insert(0, SCRIPT_DIR)

# 尝试导入各引擎的类
try:
    from self_healing_engine import SelfHealingEngine
except ImportError:
    SelfHealingEngine = None

try:
    from predictive_prevention_engine import PredictivePreventionEngine
except ImportError:
    PredictivePreventionEngine = None

try:
    from proactive_operations_engine import ProactiveOperationsEngine
except ImportError:
    ProactiveOperationsEngine = None


def ensure_dir():
    """确保目录存在"""
    os.makedirs(STATE_DIR, exist_ok=True)


def load_assurance_log() -> Dict[str, Any]:
    """加载健康保障日志"""
    ensure_dir()
    if not os.path.exists(ASSURANCE_LOG_FILE):
        return {
            "loops": [],
            "issues_detected": [],
            "fixes_applied": [],
            "optimizations_executed": [],
            "last_updated": None
        }
    try:
        with open(ASSURANCE_LOG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {
            "loops": [],
            "issues_detected": [],
            "fixes_applied": [],
            "optimizations_executed": [],
            "last_updated": None
        }


def save_assurance_log(data: Dict[str, Any]):
    """保存健康保障日志"""
    ensure_dir()
    data["last_updated"] = datetime.now(timezone.utc).isoformat()
    with open(ASSURANCE_LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_system_metrics() -> Dict[str, Any]:
    """获取系统指标"""
    try:
        result = subprocess.run(
            ["powershell", "-Command",
             "(Get-CimInstance Win32_Processor).LoadPercentage; "
             "(Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory; "
             "(Get-CimInstance Win32_OperatingSystem).TotalVisibleMemorySize; "
             "(Get-CimInstance Win32_LogicalDisk -Filter \"DeviceID='C:'\").FreeSpace; "
             "(Get-CimInstance Win32_LogicalDisk -Filter \"DeviceID='C:'\").Size"],
            capture_output=True,
            text=True,
            timeout=10
        )
        lines = [l.strip() for l in result.stdout.strip().split('\n') if l.strip()]
        if len(lines) >= 5:
            cpu = float(lines[0])
            free_mem_kb = float(lines[1])
            total_mem_kb = float(lines[2])
            free_disk_bytes = float(lines[3])
            total_disk_bytes = float(lines[4])

            memory_percent = round((1 - free_mem_kb / total_mem_kb) * 100, 1)
            disk_percent = round((1 - free_disk_bytes / total_disk_bytes) * 100, 1)

            return {
                "cpu_percent": cpu,
                "memory_percent": memory_percent,
                "disk_percent": disk_percent,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    except Exception:
        pass
    return {
        "cpu_percent": 0,
        "memory_percent": 0,
        "disk_percent": 0,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "error": "Failed to get system metrics"
    }


class HealthAssuranceLoop:
    """智能系统健康保障闭环引擎"""

    def __init__(self):
        """初始化健康保障引擎"""
        self.log = load_assurance_log()
        self.self_healing = SelfHealingEngine() if SelfHealingEngine else None
        self.predictive = PredictivePreventionEngine() if PredictivePreventionEngine else None
        self.proactive = ProactiveOperationsEngine() if ProactiveOperationsEngine else None

    def get_status(self) -> Dict[str, Any]:
        """获取健康保障状态"""
        status = {
            "assurance_status": "active",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "engines": {}
        }

        # 获取系统指标
        status["system_metrics"] = get_system_metrics()

        # 检查各引擎状态
        if self.self_healing:
            try:
                healing_status = self.self_healing.get_status()
                status["engines"]["self_healing"] = {
                    "available": True,
                    "status": healing_status.get("overall_status", "unknown")
                }
            except Exception as e:
                status["engines"]["self_healing"] = {
                    "available": True,
                    "status": "error",
                    "error": str(e)
                }
        else:
            status["engines"]["self_healing"] = {"available": False}

        if self.predictive:
            try:
                pred_status = self.predictive.get_alert()
                status["engines"]["predictive_prevention"] = {
                    "available": True,
                    "status": "active" if pred_status else "normal"
                }
            except Exception as e:
                status["engines"]["predictive_prevention"] = {
                    "available": True,
                    "status": "error",
                    "error": str(e)
                }
        else:
            status["engines"]["predictive_prevention"] = {"available": False}

        if self.proactive:
            try:
                proactive_status = self.proactive.get_auto_execute_status()
                status["engines"]["proactive_operations"] = {
                    "available": True,
                    "auto_execute": proactive_status.get("auto_execute_enabled", False)
                }
            except Exception as e:
                status["engines"]["proactive_operations"] = {
                    "available": True,
                    "status": "error",
                    "error": str(e)
                }
        else:
            status["engines"]["proactive_operations"] = {"available": False}

        return status

    def scan(self) -> Dict[str, Any]:
        """执行健康扫描"""
        result = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "scanned": True,
            "findings": [],
            "recommendations": []
        }

        # 1. 预测预防扫描
        if self.predictive:
            try:
                pred_result = self.predictive.scan_and_predict()
                result["findings"].append({
                    "engine": "predictive_prevention",
                    "risk_level": pred_result.get("risk_level", "unknown"),
                    "issues": pred_result.get("issues", []),
                    "predictions": pred_result.get("user_needs_predictions", [])
                })
                for suggestion in pred_result.get("prevention_suggestions", []):
                    result["recommendations"].append({
                        "type": "prevention",
                        "description": suggestion
                    })
            except Exception as e:
                result["findings"].append({
                    "engine": "predictive_prevention",
                    "error": str(e)
                })

        # 2. 主动运维状态
        if self.proactive:
            try:
                proactive_status = self.proactive.get_system_status()
                result["findings"].append({
                    "engine": "proactive_operations",
                    "status": proactive_status.get("overall_status", "unknown"),
                    "cpu": proactive_status.get("cpu_percent", 0),
                    "memory": proactive_status.get("memory_percent", 0),
                    "disk": proactive_status.get("disk_percent", 0)
                })

                suggestions = proactive_status.get("suggestions", [])
                for suggestion in suggestions:
                    result["recommendations"].append({
                        "type": "optimization",
                        "description": suggestion
                    })
            except Exception as e:
                result["findings"].append({
                    "engine": "proactive_operations",
                    "error": str(e)
                })

        # 3. 自愈引擎诊断
        if self.self_healing:
            try:
                diagnoses = self.self_healing.check_all()
                detected = [d for d in diagnoses if d.detected]
                result["findings"].append({
                    "engine": "self_healing",
                    "detected_count": len(detected),
                    "issues": [d.to_dict() for d in detected]
                })
                for d in detected:
                    if d.auto_fixable:
                        result["recommendations"].append({
                            "type": "auto_fix",
                            "description": f"{d.description} - 可自动修复"
                        })
            except Exception as e:
                result["findings"].append({
                    "engine": "self_healing",
                    "error": str(e)
                })

        # 保存扫描结果
        self.log["loops"].append({
            "type": "scan",
            "timestamp": result["timestamp"],
            "findings_count": len(result["findings"]),
            "recommendations_count": len(result["recommendations"])
        })
        save_assurance_log(self.log)

        return result

    def full_loop(self, auto_execute: bool = True) -> Dict[str, Any]:
        """执行完整的健康保障闭环：监控→预测→运维→自愈→反馈"""
        loop_result = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "loop_type": "full",
            "steps": [],
            "issues_detected": [],
            "fixes_applied": [],
            "optimizations_executed": [],
            "success": True
        }

        # Step 1: 监控 - 获取系统状态
        system_metrics = get_system_metrics()
        loop_result["steps"].append({
            "step": "monitor",
            "status": "completed",
            "metrics": system_metrics
        })

        # Step 2: 预测 - 预测预防引擎扫描
        if self.predictive:
            try:
                prediction = self.predictive.scan_and_predict()
                loop_result["steps"].append({
                    "step": "predict",
                    "status": "completed",
                    "risk_level": prediction.get("risk_level", "unknown")
                })

                # 如果风险等级为 critical/high 且 auto_execute 为 True，自动触发决策
                if prediction.get("risk_level") in ["critical", "high"] and auto_execute:
                    decision = self.predictive.auto_trigger_decision(auto_execute=True)
                    loop_result["optimizations_executed"].append({
                        "source": "predictive",
                        "decision": decision
                    })
            except Exception as e:
                loop_result["steps"].append({
                    "step": "predict",
                    "status": "error",
                    "error": str(e)
                })

        # Step 3: 运维 - 主动运维引擎执行优化
        if self.proactive:
            try:
                if auto_execute:
                    opt_result = self.proactive.auto_execute_optimization(force=False)
                    loop_result["steps"].append({
                        "step": "operations",
                        "status": "completed",
                        "executed": opt_result.get("executed", False)
                    })
                    if opt_result.get("executed"):
                        loop_result["optimizations_executed"].append({
                            "source": "proactive",
                            "result": opt_result
                        })
                else:
                    suggestions = self.proactive.generate_optimization_suggestions()
                    loop_result["steps"].append({
                        "step": "operations",
                        "status": "completed",
                        "suggestions": suggestions.get("suggestions", [])
                    })
            except Exception as e:
                loop_result["steps"].append({
                    "step": "operations",
                    "status": "error",
                    "error": str(e)
                })

        # Step 4: 自愈 - 自愈引擎检测和修复
        if self.self_healing:
            try:
                diagnoses = self.self_healing.check_all()
                detected = [d for d in diagnoses if d.detected]
                loop_result["issues_detected"] = [d.to_dict() for d in detected]

                # 自动修复可修复的问题
                if auto_execute:
                    for d in detected:
                        if d.auto_fixable:
                            fix_result = self.self_healing.attempt_fix(d.id)
                            loop_result["fixes_applied"].append({
                                "issue_id": d.id,
                                "result": fix_result
                            })

                loop_result["steps"].append({
                    "step": "self_healing",
                    "status": "completed",
                    "detected": len(detected),
                    "fixed": len(loop_result["fixes_applied"])
                })
            except Exception as e:
                loop_result["steps"].append({
                    "step": "self_healing",
                    "status": "error",
                    "error": str(e)
                })

        # Step 5: 反馈 - 生成报告
        loop_result["steps"].append({
            "step": "feedback",
            "status": "completed"
        })

        # 保存闭环结果
        self.log["loops"].append(loop_result)
        self.log["issues_detected"].extend(loop_result["issues_detected"])
        self.log["fixes_applied"].extend(loop_result["fixes_applied"])
        self.log["optimizations_executed"].extend(loop_result["optimizations_executed"])
        save_assurance_log(self.log)

        return loop_result

    def get_report(self) -> str:
        """获取健康保障报告"""
        status = self.get_status()
        scan = self.scan()

        report_lines = [
            "=" * 50,
            "系统健康保障闭环报告",
            "=" * 50,
            f"生成时间: {datetime.now(timezone.utc).isoformat()}",
            "",
            "【系统状态】",
            f"  CPU: {status['system_metrics'].get('cpu_percent', 'N/A')}%",
            f"  内存: {status['system_metrics'].get('memory_percent', 'N/A')}%",
            f"  磁盘: {status['system_metrics'].get('disk_percent', 'N/A')}%",
            "",
            "【引擎状态】",
        ]

        for engine, info in status.get("engines", {}).items():
            if info.get("available", False):
                status_str = info.get("status", "active")
                report_lines.append(f"  {engine}: {status_str}")
            else:
                report_lines.append(f"  {engine}: 不可用")

        report_lines.extend([
            "",
            "【扫描结果】",
            f"  发现项: {len(scan.get('findings', []))}",
            f"  建议项: {len(scan.get('recommendations', []))}",
        ])

        for i, rec in enumerate(scan.get("recommendations", [])[:5], 1):
            report_lines.append(f"  {i}. [{rec['type']}] {rec['description']}")

        if len(scan.get("recommendations", [])) > 5:
            report_lines.append(f"  ... 还有 {len(scan.get('recommendations', [])) - 5} 条建议")

        report_lines.extend([
            "",
            "=" * 50
        ])

        return "\n".join(report_lines)

    def get_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取健康保障历史"""
        loops = self.log.get("loops", [])
        return loops[-limit:] if loops else []


def main():
    parser = argparse.ArgumentParser(description="智能系统健康保障闭环引擎")
    parser.add_argument("command", nargs="?", default="status",
                        choices=["status", "scan", "full-loop", "report", "history"],
                        help="执行命令")
    parser.add_argument("--limit", type=int, default=10,
                        help="历史记录数量限制")
    parser.add_argument("--no-auto", action="store_true",
                        help="不自动执行修复和优化")

    args = parser.parse_args()

    engine = HealthAssuranceLoop()

    if args.command == "status":
        result = engine.get_status()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == "scan":
        result = engine.scan()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == "full-loop":
        result = engine.full_loop(auto_execute=not args.no_auto)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == "report":
        print(engine.get_report())
    elif args.command == "history":
        history = engine.get_history(args.limit)
        print(json.dumps(history, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()