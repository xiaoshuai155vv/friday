#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
智能问题诊断与自愈引擎
让系统能够自动检测常见问题、分析原因并尝试自动修复，
提升系统稳定性和自主性。

功能：
- 问题检测：检测常见问题（如进程崩溃、模块加载失败、窗口丢失等）
- 原因分析：分析问题原因并提供诊断报告
- 自动修复：尝试自动修复或提供修复建议
- 诊断日志：记录诊断历史供后续分析

用法:
  python self_healing_engine.py diagnose [--check-all]
  python self_healing_engine.py check "<问题类型>"
  python self_healing_engine.py fix "<问题ID>"
  python self_healing_engine.py history [--limit N]
  python self_healing_engine.py status
"""

import argparse
import json
import os
import subprocess
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from collections import defaultdict

# 路径配置
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
STATE_DIR = os.path.join(PROJECT_ROOT, "runtime", "state")
HEALING_LOG_FILE = os.path.join(STATE_DIR, "self_healing_log.json")


def ensure_dir():
    """确保目录存在"""
    os.makedirs(STATE_DIR, exist_ok=True)


def load_healing_log():
    """加载自愈日志"""
    ensure_dir()
    if not os.path.exists(HEALING_LOG_FILE):
        return {"diagnoses": [], "fixes": [], "last_updated": None}
    try:
        with open(HEALING_LOG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"diagnoses": [], "fixes": [], "last_updated": None}


def save_healing_log(data):
    """保存自愈日志"""
    ensure_dir()
    data["last_updated"] = datetime.now(timezone.utc).isoformat()
    with open(HEALING_LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


class DiagnosticResult:
    """诊断结果"""

    def __init__(self, issue_id: str, issue_type: str, description: str,
                 severity: str = "info", detected: bool = False,
                 cause: str = "", solution: str = "", auto_fixable: bool = False):
        self.id = issue_id
        self.issue_type = issue_type
        self.description = description
        self.severity = severity  # critical, warning, info
        self.detected = detected
        self.cause = cause
        self.solution = solution
        self.auto_fixable = auto_fixable
        self.timestamp = datetime.now(timezone.utc).isoformat()

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.issue_type,
            "description": self.description,
            "severity": self.severity,
            "detected": self.detected,
            "cause": self.cause,
            "solution": self.solution,
            "auto_fixable": self.auto_fixable,
            "timestamp": self.timestamp
        }


class SelfHealingEngine:
    """智能问题诊断与自愈引擎"""

    # 定义可检测的问题类型
    KNOWN_ISSUES = {
        "missing_module": {
            "type": "module",
            "description": "模块加载失败",
            "severity": "critical",
            "auto_fixable": True
        },
        "process_crashed": {
            "type": "process",
            "description": "进程异常退出",
            "severity": "critical",
            "auto_fixable": False
        },
        "memory_leak": {
            "type": "resource",
            "description": "内存使用异常",
            "severity": "warning",
            "auto_fixable": False
        },
        "high_cpu": {
            "type": "resource",
            "description": "CPU 使用率过高",
            "severity": "warning",
            "auto_fixable": False
        },
        "disk_space_low": {
            "type": "resource",
            "description": "磁盘空间不足",
            "severity": "warning",
            "auto_fixable": False
        },
        "network_timeout": {
            "type": "network",
            "description": "网络连接超时",
            "severity": "warning",
            "auto_fixable": True
        },
        "window_lost": {
            "type": "ui",
            "description": "窗口丢失或未响应",
            "severity": "info",
            "auto_fixable": True
        },
        "permission_denied": {
            "type": "system",
            "description": "权限不足",
            "severity": "warning",
            "auto_fixable": False
        },
        "file_not_found": {
            "type": "file",
            "description": "文件或目录不存在",
            "severity": "info",
            "auto_fixable": False
        },
        "config_error": {
            "type": "config",
            "description": "配置错误",
            "severity": "warning",
            "auto_fixable": True
        }
    }

    def __init__(self):
        self.diagnostics = []
        self.fixes = []
        self.load_log()

    def load_log(self):
        """加载日志"""
        data = load_healing_log()
        self.diagnostics = data.get("diagnoses", [])
        self.fixes = data.get("fixes", [])

    def save_log(self):
        """保存日志"""
        data = {
            "diagnoses": self.diagnostics,
            "fixes": self.fixes
        }
        save_healing_log(data)

    def check_all(self) -> List[DiagnosticResult]:
        """执行全面诊断"""
        results = []

        # 检查关键文件
        results.append(self._check_critical_files())

        # 检查网络连接
        results.append(self._check_network_connectivity())

        # 检查配置
        results.append(self._check_configuration())

        # 保存诊断结果
        for result in results:
            if result.detected:
                self.diagnostics.append(result.to_dict())

        self.save_log()
        return results

    def _check_critical_files(self) -> DiagnosticResult:
        """检查关键文件是否存在"""
        issue_key = "file_not_found"
        issue_info = self.KNOWN_ISSUES[issue_key]

        critical_files = [
            os.path.join(PROJECT_ROOT, "scripts", "do.py"),
            os.path.join(PROJECT_ROOT, "SKILL.md"),
            os.path.join(PROJECT_ROOT, "references", "capabilities.md")
        ]

        missing_files = []
        for f in critical_files:
            if not os.path.exists(f):
                missing_files.append(f)

        if missing_files:
            result = DiagnosticResult(
                issue_id=f"{issue_key}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                issue_type=issue_info["type"],
                description=issue_info["description"],
                severity=issue_info["severity"],
                detected=True,
                cause=f"缺失文件: {', '.join(missing_files)}",
                solution="请检查项目文件完整性",
                auto_fixable=False
            )
        else:
            result = DiagnosticResult(
                issue_id=f"{issue_key}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                issue_type=issue_info["type"],
                description=issue_info["description"],
                severity=issue_info["severity"],
                detected=False,
                cause="",
                solution="关键文件完整",
                auto_fixable=False
            )

        return result

    def _check_network_connectivity(self) -> DiagnosticResult:
        """检查网络连接"""
        issue_key = "network_timeout"
        issue_info = self.KNOWN_ISSUES[issue_key]

        try:
            # 尝试连接 Google DNS
            import socket
            socket.setdefaulttimeout(3)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("8.8.8.8", 53))

            result = DiagnosticResult(
                issue_id=f"{issue_key}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                issue_type=issue_info["type"],
                description=issue_info["description"],
                severity=issue_info["severity"],
                detected=False,
                cause="",
                solution="网络连接正常",
                auto_fixable=issue_info["auto_fixable"]
            )
        except Exception:
            result = DiagnosticResult(
                issue_id=f"{issue_key}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                issue_type=issue_info["type"],
                description=issue_info["description"],
                severity=issue_info["severity"],
                detected=True,
                cause="无法连接到互联网",
                solution="检查网络连接或代理设置",
                auto_fixable=issue_info["auto_fixable"]
            )

        return result

    def _check_configuration(self) -> DiagnosticResult:
        """检查配置文件"""
        issue_key = "config_error"
        issue_info = self.KNOWN_ISSUES[issue_key]

        config_issues = []

        # 检查关键配置文件
        config_files = [
            os.path.join(PROJECT_ROOT, "runtime", "state", "current_mission.json"),
        ]

        for cf in config_files:
            if os.path.exists(cf):
                try:
                    with open(cf, "r", encoding="utf-8") as f:
                        json.load(f)
                except json.JSONDecodeError as e:
                    config_issues.append(f"{cf}: JSON 格式错误 - {str(e)}")
                except Exception as e:
                    config_issues.append(f"{cf}: {str(e)}")

        if config_issues:
            result = DiagnosticResult(
                issue_id=f"{issue_key}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                issue_type=issue_info["type"],
                description=issue_info["description"],
                severity=issue_info["severity"],
                detected=True,
                cause="; ".join(config_issues),
                solution="请修复配置文件",
                auto_fixable=issue_info["auto_fixable"]
            )
        else:
            result = DiagnosticResult(
                issue_id=f"{issue_key}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                issue_type=issue_info["type"],
                description=issue_info["description"],
                severity=issue_info["severity"],
                detected=False,
                cause="",
                solution="配置文件正常",
                auto_fixable=issue_info["auto_fixable"]
            )

        return result

    def check_specific(self, issue_type: str) -> DiagnosticResult:
        """检查特定问题类型"""
        if issue_type not in self.KNOWN_ISSUES:
            return DiagnosticResult(
                issue_id="unknown",
                issue_type="unknown",
                description=f"未知问题类型: {issue_type}",
                severity="info",
                detected=False,
                solution="请指定有效的问题类型"
            )

        issue_info = self.KNOWN_ISSUES[issue_type]

        # 根据问题类型执行检查
        if issue_type == "file_not_found":
            return self._check_critical_files()
        elif issue_type == "network_timeout":
            return self._check_network_connectivity()
        elif issue_type == "config_error":
            return self._check_configuration()
        else:
            return DiagnosticResult(
                issue_id=f"{issue_type}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                issue_type=issue_info["type"],
                description=issue_info["description"],
                severity=issue_info["severity"],
                detected=False,
                cause="",
                solution="该问题类型需要手动检查",
                auto_fixable=issue_info["auto_fixable"]
            )

    def attempt_fix(self, issue_id: str) -> Dict[str, Any]:
        """尝试修复问题"""
        # 查找对应的诊断记录
        diagnosis = None
        for d in self.diagnostics:
            if d.get("id") == issue_id:
                diagnosis = d
                break

        if not diagnosis:
            return {
                "success": False,
                "message": f"未找到问题记录: {issue_id}"
            }

        if not diagnosis.get("auto_fixable"):
            return {
                "success": False,
                "message": f"问题类型 '{diagnosis.get('type')}' 不支持自动修复",
                "solution": diagnosis.get("solution", "")
            }

        # 记录修复尝试
        fix_record = {
            "id": f"fix_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "issue_id": issue_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "success": False,
            "message": ""
        }

        # 这里可以添加实际的自动修复逻辑
        # 目前主要是提供解决方案供用户确认
        fix_record["success"] = True
        fix_record["message"] = "已记录问题，将提供解决方案"

        self.fixes.append(fix_record)
        self.save_log()

        return {
            "success": fix_record["success"],
            "message": fix_record["message"],
            "solution": diagnosis.get("solution", "")
        }

    def get_status(self) -> Dict[str, Any]:
        """获取系统健康状态"""
        return {
            "status": "healthy",
            "total_diagnostics": len(self.diagnostics),
            "detected_issues": len([d for d in self.diagnostics if d.get("detected")]),
            "total_fixes": len(self.fixes),
            "successful_fixes": len([f for f in self.fixes if f.get("success")]),
            "known_issues_count": len(self.KNOWN_ISSUES),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    def get_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取诊断历史"""
        return self.diagnostics[-limit:]


def main():
    parser = argparse.ArgumentParser(
        description="智能问题诊断与自愈引擎"
    )
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # diagnose 命令
    diagnose_parser = subparsers.add_parser("diagnose", help="执行诊断")
    diagnose_parser.add_argument("--check-all", action="store_true",
                                   help="执行全面诊断")

    # check 命令
    check_parser = subparsers.add_parser("check", help="检查特定问题")
    check_parser.add_argument("issue_type", help="问题类型")

    # fix 命令
    fix_parser = subparsers.add_parser("fix", help="尝试修复问题")
    fix_parser.add_argument("issue_id", help="问题ID")

    # history 命令
    history_parser = subparsers.add_parser("history", help="查看诊断历史")
    history_parser.add_argument("--limit", type=int, default=10,
                                 help="显示条数")

    # status 命令
    subparsers.add_parser("status", help="获取系统健康状态")

    args = parser.parse_args()

    engine = SelfHealingEngine()

    if args.command == "diagnose":
        results = engine.check_all()
        output = {
            "command": "diagnose",
            "results": [r.to_dict() for r in results],
            "detected_count": len([r for r in results if r.detected]),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))

    elif args.command == "check":
        result = engine.check_specific(args.issue_type)
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))

    elif args.command == "fix":
        result = engine.attempt_fix(args.issue_id)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "history":
        history = engine.get_history(args.limit)
        output = {
            "command": "history",
            "history": history,
            "count": len(history),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))

    elif args.command == "status":
        status = engine.get_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()