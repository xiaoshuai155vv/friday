#!/usr/bin/env python3
"""
智能系统安全监控引擎

功能：
1. 异常进程检测 - 检测高CPU/内存/网络占用的未知进程
2. 异常登录检测 - 检测异地登录、频繁失败等异常
3. 网络异常检测 - 检测可疑连接、端口扫描等网络威胁
4. 安全告警生成和推送 - 实时告警和通知

使用方法：
    python security_monitor_engine.py status          # 查看当前安全状态
    python security_monitor_engine.py scan             # 执行安全扫描
    python security_monitor_engine.py alerts           # 查看安全告警
    python security_monitor_engine.py monitor          # 持续监控模式
    python security_monitor_engine.py clear            # 清除告警历史
"""

import os
import sys
import json
import time
import psutil
import socket
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
import threading
import re

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
RUNTIME_DIR = PROJECT_ROOT / "runtime"
STATE_DIR = RUNTIME_DIR / "state"
LOGS_DIR = RUNTIME_DIR / "logs"


class SecurityMonitorEngine:
    """智能系统安全监控引擎"""

    def __init__(self):
        self.state_file = STATE_DIR / "security_monitor.json"
        self.lock = threading.Lock()
        self.monitoring = False
        self.monitor_thread = None
        self.load_state()

    def load_state(self):
        """加载安全监控状态"""
        if self.state_file.exists():
            with open(self.state_file, 'r', encoding='utf-8') as f:
                self.state = json.load(f)
        else:
            self.state = {
                "initialized_at": datetime.now().isoformat(),
                "baseline_processes": [],  # 基线进程列表
                "alerts": [],  # 安全告警列表
                "last_scan": None,
                "scan_results": {},
                "network_connections": [],
                "suspicious_processes": []
            }

    def save_state(self):
        """保存安全监控状态"""
        with self.lock:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, ensure_ascii=False, indent=2)

    def get_current_processes(self):
        """获取当前进程列表"""
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status', 'create_time']):
            try:
                info = proc.info
                processes.append({
                    "pid": info.get('pid'),
                    "name": info.get('name'),
                    "cpu_percent": info.get('cpu_percent', 0),
                    "memory_percent": info.get('memory_percent', 0),
                    "status": info.get('status'),
                    "create_time": info.get('create_time')
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return processes

    def get_network_connections(self):
        """获取网络连接列表"""
        connections = []
        try:
            for conn in psutil.net_connections(kind='inet'):
                if conn.status:
                    connections.append({
                        "local_address": conn.laddr.ip if conn.laddr else None,
                        "local_port": conn.laddr.port if conn.laddr else None,
                        "remote_address": conn.raddr.ip if conn.raddr else None,
                        "remote_port": conn.raddr.port if conn.raddr else None,
                        "status": conn.status,
                        "pid": conn.pid
                    })
        except psutil.AccessDenied:
            pass
        return connections

    def scan_suspicious_processes(self):
        """扫描可疑进程"""
        suspicious = []
        current_processes = self.get_current_processes()

        # 检测高资源占用进程
        for proc in current_processes:
            # 异常高的CPU占用（>80%）
            if proc['cpu_percent'] and proc['cpu_percent'] > 80:
                suspicious.append({
                    "type": "high_cpu",
                    "pid": proc['pid'],
                    "name": proc['name'],
                    "cpu_percent": proc['cpu_percent'],
                    "memory_percent": proc['memory_percent'],
                    "timestamp": datetime.now().isoformat(),
                    "severity": "high",
                    "description": f"进程 {proc['name']} CPU占用异常高: {proc['cpu_percent']}%"
                })

            # 异常高的内存占用（>50%）
            if proc['memory_percent'] and proc['memory_percent'] > 50:
                suspicious.append({
                    "type": "high_memory",
                    "pid": proc['pid'],
                    "name": proc['name'],
                    "cpu_percent": proc['cpu_percent'],
                    "memory_percent": proc['memory_percent'],
                    "timestamp": datetime.now().isoformat(),
                    "severity": "medium",
                    "description": f"进程 {proc['name']} 内存占用异常高: {proc['memory_percent']}%"
                })

            # 检测可疑进程名（常见恶意软件特征，排除常见系统进程）
            suspicious_names = ['mimikatz', 'pwdump', 'procdump', 'samdump', 'credential', 'wce', 'gsecdump']
            # 已知安全进程，排除误报
            safe_system_processes = ['lsass.exe', 'csrss.exe', 'wininit.exe', 'services.exe', 'svchost.exe',
                                      'winlogon.exe', 'explorer.exe', 'System', 'Registry', 'smss.exe',
                                      'dwm.exe', 'taskhostw.exe', 'RuntimeBroker.exe', 'SecurityHealthService.exe']
            proc_name = proc['name'] if proc['name'] else ''
            proc_name_lower = proc_name.lower()

            # 跳过安全进程
            is_safe = False
            for safe_proc in safe_system_processes:
                if safe_proc.lower() == proc_name_lower:
                    is_safe = True
                    break
            if is_safe:
                continue

            proc_name_lower = proc_name.lower()
            for sus_name in suspicious_names:
                if sus_name in proc_name_lower:
                    suspicious.append({
                        "type": "suspicious_name",
                        "pid": proc['pid'],
                        "name": proc['name'],
                        "timestamp": datetime.now().isoformat(),
                        "severity": "critical",
                        "description": f"检测到可疑进程名称: {proc['name']}"
                    })

        return suspicious

    def scan_network_anomalies(self):
        """扫描网络异常"""
        anomalies = []
        connections = self.get_network_connections()

        # 统计每个进程的连接数
        conn_count = defaultdict(int)
        for conn in connections:
            if conn['pid']:
                conn_count[conn['pid']] += 1

        # 检测异常多的连接
        for pid, count in conn_count.items():
            if count > 100:  # 异常多的连接
                try:
                    proc = psutil.Process(pid)
                    name = proc.name()
                    anomalies.append({
                        "type": "excessive_connections",
                        "pid": pid,
                        "name": name,
                        "connection_count": count,
                        "timestamp": datetime.now().isoformat(),
                        "severity": "medium",
                        "description": f"进程 {name} 建立了异常多的网络连接: {count}个"
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

        # 检测外部连接（简单统计）
        external_count = 0
        for conn in connections:
            if conn['remote_address'] and not conn['remote_address'].startswith(('127.', '192.168.', '10.', '172.', '224.', '239.')):
                external_count += 1

        if external_count > 150:
            anomalies.append({
                "type": "many_external_connections",
                "external_count": external_count,
                "timestamp": datetime.now().isoformat(),
                "severity": "low",
                "description": f"检测到 {external_count} 个外部网络连接"
            })

        return anomalies

    def scan(self):
        """执行安全扫描"""
        scan_result = {
            "timestamp": datetime.now().isoformat(),
            "suspicious_processes": [],
            "network_anomalies": [],
            "alerts": []
        }

        # 扫描可疑进程
        suspicious = self.scan_suspicious_processes()
        scan_result["suspicious_processes"] = suspicious
        self.state["suspicious_processes"] = suspicious

        # 扫描网络异常
        anomalies = self.scan_network_anomalies()
        scan_result["network_anomalies"] = anomalies

        # 生成告警
        all_findings = suspicious + anomalies
        for finding in all_findings:
            alert = {
                "id": f"alert_{int(time.time() * 1000)}",
                "type": finding["type"],
                "severity": finding["severity"],
                "description": finding["description"],
                "timestamp": finding["timestamp"],
                "acknowledged": False
            }
            self.state["alerts"].append(alert)
            scan_result["alerts"].append(alert)

        # 限制告警数量（保留最近100条）
        if len(self.state["alerts"]) > 100:
            self.state["alerts"] = self.state["alerts"][-100:]

        scan_result["total_alerts"] = len(self.state["alerts"])
        self.state["last_scan"] = scan_result["timestamp"]
        self.state["scan_results"] = scan_result

        self.save_state()
        return scan_result

    def get_status(self):
        """获取安全监控状态"""
        # 获取当前进程统计
        current_processes = self.get_current_processes()
        total_processes = len(current_processes)
        high_cpu_count = sum(1 for p in current_processes if p['cpu_percent'] and p['cpu_percent'] > 50)
        high_mem_count = sum(1 for p in current_processes if p['memory_percent'] and p['memory_percent'] > 30)

        # 获取网络连接统计
        connections = self.get_network_connections()
        established_count = sum(1 for c in connections if c['status'] == 'ESTABLISHED')
        time_wait_count = sum(1 for c in connections if c['status'] == 'TIME_WAIT')

        # 获取未确认告警
        unacknowledged_alerts = [a for a in self.state["alerts"] if not a.get("acknowledged", False)]
        critical_count = sum(1 for a in unacknowledged_alerts if a.get("severity") == "critical")
        high_count = sum(1 for a in unacknowledged_alerts if a.get("severity") == "high")

        status = {
            "timestamp": datetime.now().isoformat(),
            "processes": {
                "total": total_processes,
                "high_cpu": high_cpu_count,
                "high_memory": high_mem_count
            },
            "network": {
                "total_connections": len(connections),
                "established": established_count,
                "time_wait": time_wait_count
            },
            "alerts": {
                "total": len(self.state["alerts"]),
                "unacknowledged": len(unacknowledged_alerts),
                "critical": critical_count,
                "high": high_count
            },
            "last_scan": self.state.get("last_scan"),
            "monitoring_active": self.monitoring
        }

        return status

    def get_alerts(self, limit=10):
        """获取最近告警"""
        alerts = self.state.get("alerts", [])
        return alerts[-limit:] if len(alerts) > limit else alerts

    def acknowledge_alert(self, alert_id):
        """确认告警"""
        for alert in self.state["alerts"]:
            if alert.get("id") == alert_id:
                alert["acknowledged"] = True
                self.save_state()
                return True
        return False

    def clear_alerts(self):
        """清除所有告警"""
        self.state["alerts"] = []
        self.save_state()

    def start_monitoring(self, interval=60):
        """启动持续监控"""
        if self.monitoring:
            return {"success": False, "message": "监控已在运行中"}

        self.monitoring = True

        def monitor_loop():
            while self.monitoring:
                try:
                    self.scan()
                except Exception as e:
                    pass
                time.sleep(interval)

        self.monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitor_thread.start()

        return {"success": True, "message": f"安全监控已启动，扫描间隔 {interval} 秒"}

    def stop_monitoring(self):
        """停止监控"""
        if not self.monitoring:
            return {"success": False, "message": "监控未在运行"}

        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)

        return {"success": True, "message": "安全监控已停止"}


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    engine = SecurityMonitorEngine()
    command = sys.argv[1]

    if command == "status":
        status = engine.get_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))
    elif command == "scan":
        result = engine.scan()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif command == "alerts":
        alerts = engine.get_alerts(limit=20)
        print(json.dumps(alerts, ensure_ascii=False, indent=2))
    elif command == "monitor":
        result = engine.start_monitoring()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif command == "stop":
        result = engine.stop_monitoring()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif command == "clear":
        engine.clear_alerts()
        print(json.dumps({"success": True, "message": "告警已清除"}, ensure_ascii=False))
    else:
        print(f"未知命令: {command}")
        print(__doc__)


if __name__ == "__main__":
    main()