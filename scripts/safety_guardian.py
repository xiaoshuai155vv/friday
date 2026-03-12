#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能操作安全卫士引擎
功能：主动识别危险操作、提供安全确认、防止误操作
"""

import os
import re
import json
import subprocess
from typing import Dict, List, Optional, Tuple
from pathlib import Path

# 危险操作模式定义
DANGEROUS_PATTERNS = {
    # 文件系统危险操作
    "delete_system_files": {
        "patterns": [
            r"del\s+/[qf]\s+[/\\]windows[/\\]",
            r"del\s+/[qf]\s+[/\\]system32",
            r"rm\s+-rf\s+/",
            r"rm\s+-rf\s+/etc",
            r"format\s+[a-z]:",
            r"rd\s+/[sq]\s+[/\\]windows",
            r"rmdir\s+/[sq]",
        ],
        "severity": "critical",
        "description": "删除系统关键文件或格式化磁盘",
    },
    "delete_important_dirs": {
        "patterns": [
            r"del\s+/[qf]\s+.*[/\\]文档",
            r"del\s+/[qf]\s+.*[/\\]desktop",
            r"del\s+/[qf]\s+.*[/\\]downloads",
            r"rm\s+-rf\s+.*[/\\]文档",
            r"rm\s+-rf\s+.*[/\\]desktop",
        ],
        "severity": "high",
        "description": "删除用户重要目录",
    },
    # 进程危险操作
    "kill_critical_process": {
        "patterns": [
            r"taskkill\s+/[fi]\s+explorer",
            r"taskkill\s+/[fi]\s+system",
            r"taskkill\s+/[fi]\s+csrss",
            r"kill\s+-9\s+\d+",  # PID 0-100 通常是系统进程
        ],
        "severity": "critical",
        "description": "终止关键系统进程",
    },
    # 注册表危险操作
    "registry_dangerous": {
        "patterns": [
            r"reg\s+delete.*[/\\]hkcu[/\\]software",
            r"reg\s+delete.*[/\\]hklm[/\\]software",
            r"reg\s+add.*[/\\]hkcu[/\\]run",
            r"reg\s+add.*[/\\]hklm[/\\]run",
        ],
        "severity": "high",
        "description": "修改系统注册表关键项",
    },
    # 网络危险操作
    "network_dangerous": {
        "patterns": [
            r"netsh\s+firewall\s+delete",
            r"netsh\s+advfirewall\s+delete",
            r"ipconfig\s+/release",
            r"ipconfig\s+/renew",
        ],
        "severity": "medium",
        "description": "网络配置危险操作",
    },
    # 电源危险操作
    "power_dangerous": {
        "patterns": [
            r"shutdown\s+-s\s+-t\s+0",
            r"shutdown\s+-r\s+-t\s+0",
            r"poweroff",
            r"init\s+0",
        ],
        "severity": "high",
        "description": "立即关机或重启",
    },
}

# 关键系统进程列表
CRITICAL_PROCESSES = {
    "explorer.exe", "system", "csrss.exe", "winlogon.exe", "services.exe",
    "lsass.exe", "svchost.exe", "smss.exe", "dwm.exe", "conhost.exe",
    "spoolsv.exe", "winmgmt.exe", "eventlog.exe", "Schedule"
}

# 用户确认关键词
CONFIRM_KEYWORDS = ["确认", "确定", "是", "yes", "y", "execute", "确认执行"]


class SafetyGuardian:
    """智能操作安全卫士引擎"""

    def __init__(self):
        self.dangerous_patterns = DANGEROUS_PATTERNS
        self.critical_processes = CRITICAL_PROCESSES
        self.confirmation_history: List[Dict] = []

    def analyze_command(self, command: str) -> Dict:
        """
        分析命令是否包含危险操作

        Args:
            command: 要分析的原始命令字符串

        Returns:
            分析结果字典
        """
        command_lower = command.lower()

        results = {
            "is_safe": True,
            "risk_level": "none",  # none, low, medium, high, critical
            "detected_threats": [],
            "warnings": [],
            "requires_confirmation": False,
            "safety_score": 100,  # 0-100
        }

        for threat_type, threat_info in self.dangerous_patterns.items():
            for pattern in threat_info["patterns"]:
                if re.search(pattern, command_lower, re.IGNORECASE):
                    results["is_safe"] = False
                    results["requires_confirmation"] = True

                    # 计算风险等级
                    severity = threat_info["severity"]
                    if severity == "critical":
                        results["risk_level"] = "critical"
                        results["safety_score"] = max(0, results["safety_score"] - 50)
                    elif severity == "high" and results["risk_level"] != "critical":
                        results["risk_level"] = "high"
                        results["safety_score"] = max(0, results["safety_score"] - 30)
                    elif severity == "medium" and results["risk_level"] not in ["critical", "high"]:
                        results["risk_level"] = "medium"
                        results["safety_score"] = max(0, results["safety_score"] - 15)

                    results["detected_threats"].append({
                        "type": threat_type,
                        "description": threat_info["description"],
                        "severity": severity,
                    })

                    results["warnings"].append(f"⚠️ {threat_info['description']}")

        # 检查进程终止操作
        if "kill" in command_lower or "taskkill" in command_lower:
            # 提取进程名
            process_match = re.search(r'(?:kill|taskkill).*?(\w+\.exe|\w+)', command_lower)
            if process_match:
                process_name = process_match.group(1)
                if process_name in self.critical_processes:
                    results["is_safe"] = False
                    results["requires_confirmation"] = True
                    results["risk_level"] = "critical"
                    results["safety_score"] = max(0, results["safety_score"] - 50)
                    results["detected_threats"].append({
                        "type": "kill_critical_process",
                        "description": f"尝试终止关键系统进程: {process_name}",
                        "severity": "critical",
                    })
                    results["warnings"].append(f"⚠️ 尝试终止关键系统进程: {process_name}")

        # 检查文件删除操作
        if "del " in command_lower or "rm " in command_lower or "rmdir" in command_lower:
            # 检查是否使用强制参数
            if "/f" in command_lower or "-f" in command_lower or "-rf" in command_lower:
                if results["risk_level"] not in ["critical", "high"]:
                    results["warnings"].append("ℹ️ 检测到强制删除操作，无法恢复已删除文件")

        return results

    def check_process_safety(self, process_name: str) -> Dict:
        """
        检查进程是否安全可终止

        Args:
            process_name: 进程名称

        Returns:
            检查结果
        """
        process_lower = process_name.lower()

        # 检查是否是系统关键进程
        if process_lower in self.critical_processes:
            return {
                "is_safe": False,
                "reason": f"'{process_name}' 是系统关键进程，终止可能导致系统不稳定或崩溃",
                "severity": "critical",
            }

        # 检查是否是常见应用程序
        common_apps = {
            "notepad.exe", "calc.exe", "mspaint.exe", "wordpad.exe",
            "chrome.exe", "firefox.exe", "msedge.exe", "code.exe",
            "devenv.exe", "notepad++.exe", "sublime_text.exe",
        }

        if process_lower in common_apps:
            return {
                "is_safe": True,
                "reason": f"'{process_name}' 是常见应用程序，可以安全终止",
                "severity": "low",
            }

        return {
            "is_safe": True,
            "reason": f"'{process_name}' 未在关键进程列表中",
            "severity": "none",
        }

    def get_safety_report(self) -> Dict:
        """
        获取当前安全状态报告

        Returns:
            安全状态报告
        """
        return {
            "module": "SafetyGuardian",
            "status": "active",
            "patterns_loaded": len(self.dangerous_patterns),
            "critical_processes_tracked": len(self.critical_processes),
            "confirmation_history_count": len(self.confirmation_history),
            "version": "1.0.0",
        }

    def confirm_dangerous_operation(self, operation: str, user_confirmed: bool = False) -> Dict:
        """
        记录危险操作确认状态

        Args:
            operation: 操作描述
            user_confirmed: 用户是否确认执行

        Returns:
            确认结果
        """
        record = {
            "operation": operation,
            "confirmed": user_confirmed,
            "timestamp": subprocess.run(
                ["powershell", "-Command", "Get-Date -Format 'yyyy-MM-dd HH:mm:ss'"],
                capture_output=True, text=True
            ).stdout.strip(),
        }

        self.confirmation_history.append(record)

        # 只保留最近100条记录
        if len(self.confirmation_history) > 100:
            self.confirmation_history = self.confirmation_history[-100:]

        return {
            "recorded": True,
            "operation": operation,
            "user_confirmed": user_confirmed,
            "total_records": len(self.confirmation_history),
        }


def main():
    """主函数：处理命令行调用"""
    import sys

    if len(sys.argv) < 2:
        print(json.dumps({
            "error": "用法: safety_guardian.py <command> [args]",
            "commands": ["analyze", "check_process", "report", "confirm"],
            "examples": [
                "python safety_guardian.py analyze 'del /f /q C:\\Windows\\System32'",
                "python safety_guardian.py check_process explorer.exe",
                "python safety_guardian.py report",
                "python safety_guardian.py confirm '格式化C盘' true",
            ]
        }, ensure_ascii=False, indent=2))
        sys.exit(1)

    guardian = SafetyGuardian()
    command = sys.argv[1].lower()

    try:
        if command == "analyze":
            if len(sys.argv) < 3:
                print(json.dumps({"error": "用法: analyze <command_string>"}, ensure_ascii=False))
                sys.exit(1)
            result = guardian.analyze_command(sys.argv[2])
            print(json.dumps(result, ensure_ascii=False, indent=2))

        elif command == "check_process":
            if len(sys.argv) < 3:
                print(json.dumps({"error": "用法: check_process <process_name>"}, ensure_ascii=False))
                sys.exit(1)
            result = guardian.check_process_safety(sys.argv[2])
            print(json.dumps(result, ensure_ascii=False, indent=2))

        elif command == "report":
            result = guardian.get_safety_report()
            print(json.dumps(result, ensure_ascii=False, indent=2))

        elif command == "confirm":
            if len(sys.argv) < 4:
                print(json.dumps({"error": "用法: confirm <operation> <true|false>"}, ensure_ascii=False))
                sys.exit(1)
            operation = sys.argv[2]
            confirmed = sys.argv[3].lower() == "true"
            result = guardian.confirm_dangerous_operation(operation, confirmed)
            print(json.dumps(result, ensure_ascii=False, indent=2))

        else:
            print(json.dumps({"error": f"未知命令: {command}"}, ensure_ascii=False))
            sys.exit(1)

    except Exception as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()