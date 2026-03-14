#!/usr/bin/env python3
"""
智能全场景自进化健康保障闭环引擎 (Evolution Health Assurance Loop Engine)
让系统能够自动监控自身运行状态、健康度、进化效果，在发现问题时自动诊断、修复或触发进化，
形成完整的自主健康保障闭环。

功能：
1. 实时健康监控 - 监控各引擎执行状态、资源使用、错误率
2. 自动问题诊断 - 发现异常时自动分析根因
3. 自愈与修复 - 能够自动尝试修复常见问题
4. 进化健康评估 - 评估每轮进化的实际效果
5. 主动干预 - 在问题恶化前主动干预
"""

import json
import os
import sys
import subprocess
import time
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any, Optional
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
RUNTIME_STATE_DIR = PROJECT_ROOT / "runtime" / "state"
RUNTIME_LOGS_DIR = PROJECT_ROOT / "runtime" / "logs"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
REFERENCES_DIR = PROJECT_ROOT / "references"


class EvolutionHealthAssuranceLoop:
    """智能全场景自进化健康保障闭环引擎"""

    def __init__(self):
        self.name = "EvolutionHealthAssuranceLoop"
        self.version = "1.0.0"
        self.health_data_file = RUNTIME_STATE_DIR / "evolution_health_data.json"
        self.health_history_file = RUNTIME_STATE_DIR / "evolution_health_history.json"
        self.alerts_file = RUNTIME_STATE_DIR / "evolution_health_alerts.json"
        self.interventions_file = RUNTIME_STATE_DIR / "evolution_health_interventions.json"
        self.thresholds = {
            "cpu_percent": 80.0,
            "memory_percent": 85.0,
            "disk_percent": 90.0,
            "error_rate_threshold": 0.1,
            "response_time_threshold": 5.0,
            "failed_rounds_threshold": 3,
        }

    def check_system_health(self) -> Dict[str, Any]:
        """检查系统整体健康状态"""
        try:
            if not HAS_PSUTIL:
                # 没有 psutil 时，返回默认健康状态
                return {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "health_score": 100.0,
                    "status": "healthy",
                    "metrics": {
                        "cpu": {"percent": 0, "threshold": self.thresholds["cpu_percent"], "note": "psutil not available"},
                        "memory": {"percent": 0, "threshold": self.thresholds["memory_percent"], "note": "psutil not available"},
                        "disk": {"percent": 0, "threshold": self.thresholds["disk_percent"], "note": "psutil not available"},
                    },
                }

            cpu_percent = psutil.cpu_percent(interval=0.5)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            health_score = 100.0

            # 计算健康得分
            if cpu_percent > self.thresholds["cpu_percent"]:
                health_score -= 15
            if memory.percent > self.thresholds["memory_percent"]:
                health_score -= 15
            if disk.percent > self.thresholds["disk_percent"]:
                health_score -= 10

            health_status = "healthy"
            if health_score < 60:
                health_status = "critical"
            elif health_score < 80:
                health_status = "warning"

            return {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "health_score": max(0, health_score),
                "status": health_status,
                "metrics": {
                    "cpu": {"percent": cpu_percent, "threshold": self.thresholds["cpu_percent"]},
                    "memory": {"percent": memory.percent, "threshold": self.thresholds["memory_percent"]},
                    "disk": {"percent": disk.percent, "threshold": self.thresholds["disk_percent"]},
                },
            }
        except Exception as e:
            return {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "health_score": 0,
                "status": "unknown",
                "error": str(e),
            }

    def check_engine_health(self) -> Dict[str, Any]:
        """检查各引擎的健康状态"""
        engine_health = {}

        # 检查关键脚本文件是否存在
        key_scripts = [
            "do.py",
            "state_tracker.py",
            "behavior_log.py",
            "self_verify_capabilities.py",
        ]

        for script in key_scripts:
            script_path = SCRIPTS_DIR / script
            engine_health[script] = {
                "exists": script_path.exists(),
                "path": str(script_path),
            }

        # 检查 state 目录状态
        state_files = list(RUNTIME_STATE_DIR.glob("*.json"))
        engine_health["state_files"] = {
            "count": len(state_files),
            "recent": [f.name for f in sorted(state_files, key=lambda x: x.stat().st_mtime, reverse=True)[:5]]
        }

        # 检查最近是否有错误日志
        error_logs = []
        if RUNTIME_LOGS_DIR.exists():
            for log_file in RUNTIME_LOGS_DIR.glob("behavior_*.log"):
                try:
                    with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        if "error" in content.lower() or "fail" in content.lower():
                            error_logs.append(log_file.name)
                except Exception:
                    pass

        engine_health["error_logs"] = {
            "count": len(error_logs),
            "files": error_logs[-5:] if error_logs else []
        }

        return engine_health

    def check_evolution_health(self) -> Dict[str, Any]:
        """检查进化环的健康状态"""
        # 加载最近的进化完成记录
        recent_completions = []
        if RUNTIME_STATE_DIR.exists():
            for f in RUNTIME_STATE_DIR.glob("evolution_completed_*.json"):
                try:
                    with open(f, 'r', encoding='utf-8') as fp:
                        data = json.load(fp)
                        if isinstance(data, dict):
                            recent_completions.append(data)
                except Exception:
                    continue

        # 按时间排序
        recent_completions.sort(key=lambda x: x.get('completed_at', ''), reverse=True)
        recent_completions = recent_completions[:10]

        # 分析进化成功率
        completed = sum(1 for c in recent_completions if c.get('status') == '已完成')
        failed = sum(1 for c in recent_completions if c.get('status') in ['失败', 'stale_failed'])

        total = len(recent_completions)
        success_rate = completed / total if total > 0 else 0

        # 检查是否有连续失败
        consecutive_failures = 0
        for c in recent_completions:
            if c.get('status') in ['失败', 'stale_failed']:
                consecutive_failures += 1
            else:
                break

        evolution_status = "healthy"
        if success_rate < 0.5 or consecutive_failures >= self.thresholds["failed_rounds_threshold"]:
            evolution_status = "critical"
        elif success_rate < 0.8:
            evolution_status = "warning"

        return {
            "recent_rounds": len(recent_completions),
            "completed": completed,
            "failed": failed,
            "success_rate": success_rate,
            "consecutive_failures": consecutive_failures,
            "status": evolution_status,
            "last_round": recent_completions[0] if recent_completions else None,
        }

    def diagnose_issues(self, health_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """自动诊断发现的问题"""
        issues = []

        # 检查系统健康
        if health_data.get("system", {}).get("status") in ["warning", "critical"]:
            issues.append({
                "type": "system_health",
                "severity": health_data["system"]["status"],
                "description": f"系统健康度: {health_data['system'].get('health_score', 0)}%",
                "metrics": health_data.get("system", {}).get("metrics", {}),
            })

        # 检查引擎健康
        engine_health = health_data.get("engine", {})
        for engine, status in engine_health.items():
            if isinstance(status, dict) and not status.get("exists", True):
                issues.append({
                    "type": "engine_missing",
                    "severity": "critical",
                    "description": f"关键引擎缺失: {engine}",
                })

        # 检查错误日志
        if engine_health.get("error_logs", {}).get("count", 0) > 0:
            issues.append({
                "type": "error_logs",
                "severity": "warning",
                "description": f"发现 {engine_health['error_logs']['count']} 个错误日志",
            })

        # 检查进化健康
        evolution = health_data.get("evolution", {})
        if evolution.get("status") in ["warning", "critical"]:
            issues.append({
                "type": "evolution_health",
                "severity": evolution["status"],
                "description": f"进化成功率: {evolution.get('success_rate', 0)*100:.1f}%, 连续失败: {evolution.get('consecutive_failures', 0)}",
            })

        return issues

    def attempt_self_healing(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        """尝试自动修复问题"""
        result = {
            "issue_type": issue.get("type"),
            "attempted": False,
            "success": False,
            "actions": [],
        }

        issue_type = issue.get("type", "")

        if issue_type == "error_logs":
            # 尝试清理旧的错误日志
            try:
                if RUNTIME_LOGS_DIR.exists():
                    for log_file in RUNTIME_LOGS_DIR.glob("behavior_*.log"):
                        if log_file.stat().st_size > 10 * 1024 * 1024:  # > 10MB
                            # 备份并截断
                            backup_name = log_file.with_suffix('.log.old')
                            log_file.rename(backup_name)
                            result["actions"].append(f"备份大日志文件: {log_file.name}")
                result["success"] = True
            except Exception as e:
                result["actions"].append(f"清理失败: {str(e)}")
            result["attempted"] = True

        elif issue_type == "system_health":
            # 系统资源问题，尝试释放内存
            try:
                import gc
                gc.collect()
                result["actions"].append("执行垃圾回收释放内存")
                result["success"] = True
            except Exception as e:
                result["actions"].append(f"释放内存失败: {str(e)}")
            result["attempted"] = True

        return result

    def evaluate_evolution_effectiveness(self, round_data: Dict[str, Any]) -> Dict[str, Any]:
        """评估单轮进化的有效性"""
        evaluation = {
            "round": round_data.get("loop_round"),
            "goal": round_data.get("current_goal"),
            "status": round_data.get("status"),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # 基于多种因素评估
        score = 50.0  # 基础分

        # 检查是否完成
        if round_data.get("status") == "已完成":
            score += 30
        elif round_data.get("status") == "失败":
            score -= 20

        # 检查验证结果
        verification = round_data.get("verification", {})
        if verification.get("baseline") == "通过":
            score += 10
        if verification.get("targeted"):
            score += 10

        # 检查做了什么
        what_done = round_data.get("what_done", [])
        if len(what_done) >= 3:
            score += 10

        evaluation["score"] = max(0, min(100, score))
        evaluation["rating"] = "excellent" if score >= 90 else "good" if score >= 70 else "fair" if score >= 50 else "poor"

        return evaluation

    def proactive_intervention(self, health_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """主动干预：在问题恶化前采取行动"""
        interventions = []

        # 检查是否需要主动干预
        system = health_data.get("system", {})
        evolution = health_data.get("evolution", {})

        # 系统健康严重下降
        if system.get("status") == "critical":
            interventions.append({
                "type": "system_critical",
                "action": "建议立即执行系统清理，释放资源",
                "priority": "high",
                "auto_executable": True,
            })

        # 进化连续失败
        if evolution.get("consecutive_failures", 0) >= 2:
            interventions.append({
                "type": "evolution_failure",
                "action": "连续进化失败，建议检查进化策略或回滚到稳定状态",
                "priority": "high",
                "auto_executable": False,
            })

        # 进化成功率低
        if evolution.get("success_rate", 1.0) < 0.6:
            interventions.append({
                "type": "evolution_low_success",
                "action": "进化成功率较低，建议分析失败原因并调整策略",
                "priority": "medium",
                "auto_executable": False,
            })

        return interventions

    def run_full_health_check(self) -> Dict[str, Any]:
        """执行完整健康检查"""
        # 1. 系统健康检查
        system_health = self.check_system_health()

        # 2. 引擎健康检查
        engine_health = self.check_engine_health()

        # 3. 进化健康检查
        evolution_health = self.check_evolution_health()

        # 整合健康数据
        health_data = {
            "system": system_health,
            "engine": engine_health,
            "evolution": evolution_health,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # 4. 问题诊断
        issues = self.diagnose_issues(health_data)
        health_data["issues"] = issues

        # 5. 主动干预
        interventions = self.proactive_intervention(health_data)
        health_data["interventions"] = interventions

        # 保存健康数据
        self._save_health_data(health_data)

        return health_data

    def _save_health_data(self, health_data: Dict[str, Any]):
        """保存健康数据"""
        try:
            RUNTIME_STATE_DIR.mkdir(parents=True, exist_ok=True)

            # 保存当前健康数据
            with open(self.health_data_file, 'w', encoding='utf-8') as f:
                json.dump(health_data, f, ensure_ascii=False, indent=2)

            # 更新历史记录
            history = []
            if self.health_history_file.exists():
                try:
                    with open(self.health_history_file, 'r', encoding='utf-8') as f:
                        history = json.load(f)
                except Exception:
                    pass

            history.append({
                "timestamp": health_data["timestamp"],
                "system_score": health_data.get("system", {}).get("health_score", 0),
                "evolution_success_rate": health_data.get("evolution", {}).get("success_rate", 0),
                "issues_count": len(health_data.get("issues", [])),
            })

            # 只保留最近100条历史
            history = history[-100:]

            with open(self.health_history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"保存健康数据失败: {e}", file=sys.stderr)

    def get_health_summary(self) -> str:
        """获取健康摘要"""
        health_data = self.run_full_health_check()

        summary_lines = [
            "=== 智能全场景自进化健康保障闭环 ===",
            f"检查时间: {health_data.get('timestamp', 'N/A')}",
            "",
            "【系统健康】",
            f"  状态: {health_data.get('system', {}).get('status', 'unknown')}",
            f"  得分: {health_data.get('system', {}).get('health_score', 0):.1f}/100",
            "",
            "【进化健康】",
            f"  状态: {health_data.get('evolution', {}).get('status', 'unknown')}",
            f"  成功率: {health_data.get('evolution', {}).get('success_rate', 0)*100:.1f}%",
            f"  连续失败: {health_data.get('evolution', {}).get('consecutive_failures', 0)}轮",
            "",
        ]

        issues = health_data.get("issues", [])
        if issues:
            summary_lines.append("【发现问题】")
            for issue in issues:
                summary_lines.append(f"  - [{issue.get('severity', 'unknown')}] {issue.get('description', 'N/A')}")
            summary_lines.append("")

        interventions = health_data.get("interventions", [])
        if interventions:
            summary_lines.append("【主动干预建议】")
            for item in interventions:
                summary_lines.append(f"  - [{item.get('priority', 'N/A')}] {item.get('action', 'N/A')}")
            summary_lines.append("")

        return "\n".join(summary_lines)


def main():
    """主入口"""
    import argparse

    parser = argparse.ArgumentParser(description="智能全场景自进化健康保障闭环引擎")
    parser.add_argument("command", nargs="?", default="check",
                       choices=["check", "summary", "diagnose", "heal", "evaluate"],
                       help="执行命令")
    parser.add_argument("--round", type=int, help="指定轮次用于评估")
    parser.add_argument("--issue", type=str, help="指定问题类型用于修复")

    args = parser.parse_args()

    engine = EvolutionHealthAssuranceLoop()

    if args.command == "check":
        # 执行完整健康检查
        result = engine.run_full_health_check()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "summary":
        # 获取健康摘要
        print(engine.get_health_summary())

    elif args.command == "diagnose":
        # 诊断问题
        health_data = engine.run_full_health_check()
        issues = engine.diagnose_issues(health_data)
        print(json.dumps(issues, ensure_ascii=False, indent=2))

    elif args.command == "heal":
        # 尝试修复
        health_data = engine.run_full_health_check()
        issues = engine.diagnose_issues(health_data)
        results = []
        for issue in issues:
            result = engine.attempt_self_healing(issue)
            results.append(result)
        print(json.dumps(results, ensure_ascii=False, indent=2))

    elif args.command == "evaluate":
        # 评估进化效果
        if not args.round:
            print("请指定 --round 参数", file=sys.stderr)
            return

        # 加载指定轮次的数据
        round_file = RUNTIME_STATE_DIR / f"evolution_completed_ev_20260314_{args.round:05d}.json"
        if not round_file.exists():
            # 尝试其他格式
            for f in RUNTIME_STATE_DIR.glob(f"evolution_completed_*.json"):
                try:
                    with open(f, 'r', encoding='utf-8') as fp:
                        data = json.load(fp)
                        if data.get("loop_round") == args.round:
                            round_file = f
                            break
                except Exception:
                    continue

        if round_file.exists():
            with open(round_file, 'r', encoding='utf-8') as f:
                round_data = json.load(f)
            evaluation = engine.evaluate_evolution_effectiveness(round_data)
            print(json.dumps(evaluation, ensure_ascii=False, indent=2))
        else:
            print(f"未找到轮次 {args.round} 的数据", file=sys.stderr)


if __name__ == "__main__":
    main()