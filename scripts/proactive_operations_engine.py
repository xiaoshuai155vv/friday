#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能系统主动运维引擎 (Proactive System Operations Engine)

让系统能够主动监控系统资源（CPU/内存/磁盘/进程）、预测资源瓶颈、
自动执行预防性维护（清理临时文件、释放内存、结束不必要进程）。
这是超越用户的能力——用户只能被动响应问题，AI可以主动预防系统问题发生之前。

区别于：
- predictive_prevention_engine: 预测问题
- self_healing_engine: 问题后修复
- 本模块: 持续性主动管理

作者: Claude Code
日期: 2026-03-13
"""

import os
import sys
import time
import json
import shutil
import psutil
import threading
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

class ProactiveOperationsEngine:
    """智能系统主动运维引擎"""

    def __init__(self):
        self.name = "Proactive Operations Engine"
        self.version = "1.0.0"
        self.state_dir = PROJECT_ROOT / "runtime" / "state"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.state_dir / "proactive_operations_config.json"
        self.history_file = self.state_dir / "proactive_operations_history.json"

        # 监控阈值
        self.thresholds = {
            "cpu_warning": 80.0,      # CPU 使用率警告阈值
            "cpu_critical": 90.0,    # CPU 使用率危险阈值
            "memory_warning": 80.0,   # 内存使用率警告阈值
            "memory_critical": 90.0,  # 内存使用率危险阈值
            "disk_warning": 85.0,    # 磁盘使用率警告阈值
            "disk_critical": 95.0,   # 磁盘使用率危险阈值
        }

        # 加载配置
        self.config = self._load_config()

        # 监控状态
        self.monitoring = False
        self.monitor_thread = None
        self.monitor_interval = 60  # 默认监控间隔 60 秒

        # 系统信息缓存
        self._last_check = None
        self._system_status = {}

    def _load_config(self) -> Dict:
        """加载配置"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "enabled": True,
            "auto_cleanup": True,
            "auto_optimize": True,
            "monitor_interval": 60,
            "thresholds": self.thresholds,
            "cleanup_paths": [
                os.environ.get('TEMP', 'C:\\Users\\%s\\AppData\\Local\\Temp' % os.environ.get('USERNAME', '')),
                str(PROJECT_ROOT / "runtime" / "logs"),
            ],
            "excluded_processes": ["explorer", "system", "csrss", "smss", "wininit", "services", "lsass", "svchost"]
        }

    def _save_config(self):
        """保存配置"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)

    def get_system_status(self) -> Dict:
        """获取系统状态"""
        try:
            # CPU 使用率
            cpu_percent = psutil.cpu_percent(interval=1)

            # 内存使用率
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_available = memory.available / (1024**3)  # GB

            # 磁盘使用率
            disk = psutil.disk_usage('C:\\')
            disk_percent = disk.percent
            disk_free = disk.free / (1024**3)  # GB

            # 进程统计
            process_count = len(psutil.pids())

            # 危险进程（高CPU/内存）
            dangerous_processes = []
            for proc in psutil.process_iter(['name', 'cpu_percent', 'memory_percent']):
                try:
                    pinfo = proc.info
                    if pinfo['cpu_percent'] and pinfo['cpu_percent'] > 50:
                        dangerous_processes.append({
                            'name': pinfo['name'],
                            'cpu': pinfo['cpu_percent'],
                            'memory': pinfo.get('memory_percent', 0)
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

            self._system_status = {
                "timestamp": datetime.now().isoformat(),
                "cpu": {
                    "percent": cpu_percent,
                    "status": self._get_status(cpu_percent, 'cpu')
                },
                "memory": {
                    "percent": memory_percent,
                    "available_gb": round(memory_available, 2),
                    "status": self._get_status(memory_percent, 'memory')
                },
                "disk": {
                    "percent": disk_percent,
                    "free_gb": round(disk_free, 2),
                    "status": self._get_status(disk_percent, 'disk')
                },
                "process_count": process_count,
                "dangerous_processes": dangerous_processes[:5],  # 最多5个
                "overall_status": self._calculate_overall_status(cpu_percent, memory_percent, disk_percent)
            }

            self._last_check = datetime.now()
            return self._system_status

        except Exception as e:
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def _get_status(self, value: float, resource_type: str) -> str:
        """获取资源状态"""
        thresholds = self.thresholds
        if resource_type == 'cpu':
            if value >= thresholds['cpu_critical']:
                return "critical"
            elif value >= thresholds['cpu_warning']:
                return "warning"
        elif resource_type == 'memory':
            if value >= thresholds['memory_critical']:
                return "critical"
            elif value >= thresholds['memory_warning']:
                return "warning"
        elif resource_type == 'disk':
            if value >= thresholds['disk_critical']:
                return "critical"
            elif value >= thresholds['disk_warning']:
                return "warning"
        return "normal"

    def _calculate_overall_status(self, cpu: float, memory: float, disk: float) -> str:
        """计算整体状态"""
        if (cpu >= self.thresholds['cpu_critical'] or
            memory >= self.thresholds['memory_critical'] or
            disk >= self.thresholds['disk_critical']):
            return "critical"
        if (cpu >= self.thresholds['cpu_warning'] or
            memory >= self.thresholds['memory_warning'] or
            disk >= self.thresholds['disk_warning']):
            return "warning"
        return "normal"

    def predict_bottleneck(self, look_ahead_minutes: int = 30) -> Dict:
        """预测资源瓶颈

        基于当前趋势预测未来资源使用情况
        """
        # 简化预测：基于当前状态和历史数据估算
        current = self.get_system_status()

        predictions = {
            "timestamp": datetime.now().isoformat(),
            "look_ahead_minutes": look_ahead_minutes,
            "current_status": current,
            "predictions": {},
            "risk_level": "low",
            "recommendations": []
        }

        # 预测 CPU
        cpu = current.get('cpu', {}).get('percent', 0)
        if cpu > 70:
            predictions["predictions"]["cpu"] = {
                "predicted_percent": min(cpu * 1.2, 100),
                "risk": "high" if cpu > 85 else "medium"
            }
            predictions["recommendations"].append(f"CPU 使用率较高 ({cpu}%)，建议关注")

        # 预测内存
        memory = current.get('memory', {}).get('percent', 0)
        if memory > 70:
            predictions["predictions"]["memory"] = {
                "predicted_percent": min(memory * 1.15, 100),
                "risk": "high" if memory > 85 else "medium"
            }
            predictions["recommendations"].append(f"内存使用率较高 ({memory}%)，建议清理不必要进程")

        # 预测磁盘
        disk = current.get('disk', {}).get('percent', 0)
        if disk > 80:
            predictions["predictions"]["disk"] = {
                "predicted_percent": min(disk + 2, 100),
                "risk": "high" if disk > 90 else "medium"
            }
            predictions["recommendations"].append(f"磁盘空间不足 ({disk}%)，建议清理临时文件")

        # 计算整体风险等级
        risks = [p.get('risk', 'low') for p in predictions["predictions"].values()]
        if 'high' in risks:
            predictions["risk_level"] = "high"
        elif 'medium' in risks:
            predictions["risk_level"] = "medium"

        return predictions

    def auto_cleanup(self) -> Dict:
        """自动清理临时文件和日志"""
        results = {
            "timestamp": datetime.now().isoformat(),
            "cleaned_files": [],
            "total_freed_mb": 0,
            "errors": []
        }

        cleanup_paths = self.config.get("cleanup_paths", [])

        for path in cleanup_paths:
            try:
                path = path.replace('%USERNAME%', os.environ.get('USERNAME', ''))
                path = path.replace('%TEMP%', os.environ.get('TEMP', ''))

                if not os.path.exists(path):
                    continue

                # 清理旧日志文件（超过7天的）
                cutoff_time = time.time() - (7 * 24 * 60 * 60)
                for root, dirs, files in os.walk(path):
                    for file in files:
                        if file.endswith('.log') or file.endswith('.tmp'):
                            file_path = os.path.join(root, file)
                            try:
                                mtime = os.path.getmtime(file_path)
                                if mtime < cutoff_time:
                                    size = os.path.getsize(file_path)
                                    os.remove(file_path)
                                    results["cleaned_files"].append(file_path)
                                    results["total_freed_mb"] += size / (1024 * 1024)
                            except Exception:
                                pass

            except Exception as e:
                results["errors"].append(f"清理路径 {path} 时出错: {str(e)}")

        results["total_freed_mb"] = round(results["total_freed_mb"], 2)

        # 保存历史记录
        self._save_history("auto_cleanup", results)

        return results

    def optimize_memory(self) -> Dict:
        """内存优化：结束不必要的高内存进程"""
        results = {
            "timestamp": datetime.now().isoformat(),
            "terminated_processes": [],
            "freed_memory_mb": 0,
            "errors": []
        }

        excluded = self.config.get("excluded_processes", [])

        # 查找高内存进程
        high_memory_procs = []
        for proc in psutil.process_iter(['name', 'memory_info']):
            try:
                pinfo = proc.info
                if pinfo['name'].lower() not in excluded:
                    mem_mb = pinfo['memory_info'].rss / (1024 * 1024)
                    if mem_mb > 500:  # 超过 500MB
                        high_memory_procs.append({
                            'pid': proc.pid,
                            'name': pinfo['name'],
                            'memory_mb': round(mem_mb, 2)
                        })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        # 按内存使用排序，终止最高的几个（如果有危险状态）
        overall_status = self._system_status.get('overall_status', 'normal')
        if overall_status in ['warning', 'critical']:
            high_memory_procs.sort(key=lambda x: x['memory_mb'], reverse=True)
            # 最多终止3个进程
            for proc in high_memory_procs[:3]:
                try:
                    p = psutil.Process(proc['pid'])
                    p.terminate()
                    results["terminated_processes"].append(proc['name'])
                    results["freed_memory_mb"] += proc['memory_mb']
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

        results["freed_memory_mb"] = round(results["freed_memory_mb"], 2)
        self._save_history("optimize_memory", results)

        return results

    def generate_optimization_suggestions(self) -> Dict:
        """生成优化建议"""
        status = self.get_system_status()
        suggestions = {
            "timestamp": datetime.now().isoformat(),
            "current_status": status,
            "suggestions": [],
            "actions": []
        }

        # CPU 建议
        cpu = status.get('cpu', {})
        if cpu.get('status') in ['warning', 'critical']:
            suggestions["suggestions"].append(f"CPU 使用率{cpu.get('percent')}%，建议关闭不必要的后台程序")
            suggestions["actions"].append({
                "type": "cpu_optimization",
                "description": "检查并关闭高CPU进程",
                "command": "proactive_ops optimize"
            })

        # 内存建议
        memory = status.get('memory', {})
        if memory.get('status') in ['warning', 'critical']:
            suggestions["suggestions"].append(f"内存使用率{memory.get('percent')}%，可用{memory.get('available_gb')}GB，建议清理内存")
            suggestions["actions"].append({
                "type": "memory_optimization",
                "description": "执行内存优化",
                "command": "proactive_ops optimize"
            })

        # 磁盘建议
        disk = status.get('disk', {})
        if disk.get('status') in ['warning', 'critical']:
            suggestions["suggestions"].append(f"磁盘使用率{disk.get('percent')}%，剩余{disk.get('free_gb')}GB，建议清理临时文件")
            suggestions["actions"].append({
                "type": "disk_cleanup",
                "description": "执行磁盘清理",
                "command": "proactive_ops cleanup"
            })

        if not suggestions["suggestions"]:
            suggestions["suggestions"].append("系统运行状态良好，无需优化")

        return suggestions

    def auto_execute_optimization(self, force: bool = False) -> Dict:
        """自动执行优化 - 根据系统状态自动决定执行哪些优化

        这是"超越用户"的关键能力 - 用户只能收到建议但需要手动操作，
        AI 可以自动完成从建议到执行的全过程。

        Args:
            force: 是否强制执行（忽略阈值检查）

        Returns:
            执行结果摘要
        """
        results = {
            "timestamp": datetime.now().isoformat(),
            "executed_actions": [],
            "total_freed_mb": 0,
            "summary": "",
            "errors": []
        }

        # 获取当前系统状态
        status = self.get_system_status()

        # 检查是否需要执行优化（除非 force=True）
        overall_status = status.get('overall_status', 'normal')
        if not force and overall_status == 'normal':
            results["summary"] = "系统状态正常，无需自动优化"
            return results

        # 根据状态自动执行相应优化
        # 1. 如果磁盘有压力，执行清理
        disk = status.get('disk', {})
        if force or disk.get('status') in ['warning', 'critical']:
            try:
                cleanup_result = self.auto_cleanup()
                results["executed_actions"].append({
                    "action": "auto_cleanup",
                    "result": cleanup_result
                })
                results["total_freed_mb"] += cleanup_result.get('total_freed_mb', 0)
            except Exception as e:
                results["errors"].append(f"自动清理失败: {str(e)}")

        # 2. 如果内存有压力，执行内存优化
        memory = status.get('memory', {})
        if force or memory.get('status') in ['warning', 'critical']:
            try:
                optimize_result = self.optimize_memory()
                results["executed_actions"].append({
                    "action": "optimize_memory",
                    "result": optimize_result
                })
                results["total_freed_mb"] += optimize_result.get('freed_memory_mb', 0)
            except Exception as e:
                results["errors"].append(f"内存优化失败: {str(e)}")

        results["total_freed_mb"] = round(results["total_freed_mb"], 2)

        # 生成摘要
        if results["executed_actions"]:
            action_names = [a["action"] for a in results["executed_actions"]]
            results["summary"] = f"自动执行优化完成：{', '.join(action_names)}，释放 {results['total_freed_mb']} MB"
        else:
            results["summary"] = "无需执行优化"

        # 保存历史
        self._save_history("auto_execute_optimization", results)

        return results

    def execute_all_optimizations(self) -> Dict:
        """一键执行所有优化操作

        强制执行所有优化操作，不考虑当前系统状态。
        用于用户主动触发或预防性维护。

        Returns:
            执行结果摘要
        """
        results = {
            "timestamp": datetime.now().isoformat(),
            "executed_actions": [],
            "total_freed_mb": 0,
            "errors": []
        }

        # 1. 执行自动清理
        try:
            cleanup_result = self.auto_cleanup()
            results["executed_actions"].append({
                "action": "auto_cleanup",
                "cleaned_files": len(cleanup_result.get('cleaned_files', [])),
                "freed_mb": cleanup_result.get('total_freed_mb', 0)
            })
            results["total_freed_mb"] += cleanup_result.get('total_freed_mb', 0)
        except Exception as e:
            results["errors"].append(f"清理失败: {str(e)}")

        # 2. 执行内存优化
        try:
            optimize_result = self.optimize_memory()
            results["executed_actions"].append({
                "action": "optimize_memory",
                "terminated": len(optimize_result.get('terminated_processes', [])),
                "freed_mb": optimize_result.get('freed_memory_mb', 0)
            })
            results["total_freed_mb"] += optimize_result.get('freed_memory_mb', 0)
        except Exception as e:
            results["errors"].append(f"内存优化失败: {str(e)}")

        results["total_freed_mb"] = round(results["total_freed_mb"], 2)

        # 保存历史
        self._save_history("execute_all_optimizations", results)

        return results

    def get_auto_execute_status(self) -> Dict:
        """获取自动执行状态"""
        return {
            "enabled": self.config.get("auto_execute", False),
            "auto_cleanup": self.config.get("auto_cleanup", True),
            "auto_optimize": self.config.get("auto_optimize", True),
            "thresholds": self.thresholds
        }

    def set_auto_execute(self, enabled: bool) -> Dict:
        """设置是否启用自动执行"""
        self.config["auto_execute"] = enabled
        self._save_config()
        return {"auto_execute": enabled, "status": "updated"}

    def _save_history(self, action: str, result: Dict):
        """保存操作历史"""
        history = []
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            except Exception:
                pass

        history.append({
            "action": action,
            "result": result
        })

        # 只保留最近100条
        history = history[-100:]

        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)

    def start_monitoring(self, interval: int = 60):
        """启动守护进程监控"""
        if self.monitoring:
            return {"status": "already_running"}

        self.monitoring = True
        self.monitor_interval = interval

        def monitor_loop():
            while self.monitoring:
                try:
                    status = self.get_system_status()
                    if status.get('overall_status') in ['warning', 'critical']:
                        # 可以在这里触发自动优化或通知
                        pass
                except Exception:
                    pass
                time.sleep(self.monitor_interval)

        self.monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitor_thread.start()

        return {"status": "started", "interval": interval}

    def stop_monitoring(self):
        """停止守护进程监控"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        return {"status": "stopped"}

    def run_command(self, command: str, args: List[str] = None) -> Dict:
        """执行命令"""
        args = args or []

        if command in ["status", "monitor"]:
            return self.get_system_status()

        elif command in ["predict", "prediction"]:
            look_ahead = 30
            if args and args[0].isdigit():
                look_ahead = int(args[0])
            return self.predict_bottleneck(look_ahead)

        elif command == "cleanup":
            if self.config.get("auto_cleanup", True):
                return self.auto_cleanup()
            else:
                return {"error": "自动清理已禁用"}

        elif command == "optimize":
            if self.config.get("auto_optimize", True):
                return self.optimize_memory()
            else:
                return {"error": "自动优化已禁用"}

        elif command in ["suggestions", "suggest", "advice"]:
            return self.generate_optimization_suggestions()

        elif command == "start":
            interval = self.monitor_interval
            if args and args[0].isdigit():
                interval = int(args[0])
            return self.start_monitoring(interval)

        elif command == "stop":
            return self.stop_monitoring()

        elif command == "daemon":
            # 守护进程模式
            result = self.start_monitoring()
            if result.get("status") == "started":
                # 保持运行
                while self.monitoring:
                    time.sleep(10)
            return {"status": "daemon_mode"}

        elif command in ["execute", "auto_execute"]:
            # 自动执行优化（根据系统状态决定执行哪些）
            force = "--force" in args or "-f" in args
            return self.auto_execute_optimization(force)

        elif command in ["auto", "execute_all", "all"]:
            # 一键执行所有优化
            return self.execute_all_optimizations()

        elif command == "auto_status":
            # 获取自动执行状态
            return self.get_auto_execute_status()

        elif command in ["auto_enable", "enable_auto"]:
            # 启用自动执行
            return self.set_auto_execute(True)

        elif command in ["auto_disable", "disable_auto"]:
            # 禁用自动执行
            return self.set_auto_execute(False)

        elif command == "help":
            return {
                "commands": {
                    "status": "获取系统状态",
                    "predict [minutes]": "预测资源瓶颈",
                    "cleanup": "自动清理临时文件",
                    "optimize": "内存优化",
                    "suggestions": "生成优化建议",
                    "execute [--force]": "自动执行优化（根据系统状态）",
                    "auto/execute_all": "一键执行所有优化",
                    "auto_status": "获取自动执行状态",
                    "auto_enable/auto_disable": "启用/禁用自动执行",
                    "start [interval]": "启动守护进程监控",
                    "stop": "停止守护进程监控",
                    "daemon": "守护进程模式（持续运行）"
                }
            }

        else:
            return {"error": f"未知命令: {command}"}


def main():
    """CLI 入口"""
    import argparse

    parser = argparse.ArgumentParser(description="智能系统主动运维引擎")
    parser.add_argument("command", nargs="?", default="status", help="命令: status/predict/cleanup/optimize/suggestions/execute/auto/auto_status/start/stop/daemon/help")
    parser.add_argument("args", nargs="*", help="命令参数")
    parser.add_argument("--json", action="store_true", help="JSON 输出")

    args = parser.parse_args()

    engine = ProactiveOperationsEngine()
    result = engine.run_command(args.command, args.args)

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        # 友好输出
        if args.command == "status":
            status = result
            print(f"=== 系统状态 ({status.get('timestamp', '')}) ===")
            print(f"整体状态: {status.get('overall_status', 'unknown')}")
            print(f"CPU: {status.get('cpu', {}).get('percent', 0)}% ({status.get('cpu', {}).get('status', 'unknown')})")
            print(f"内存: {status.get('memory', {}).get('percent', 0)}% ({status.get('memory', {}).get('status', 'unknown')}) - 可用 {status.get('memory', {}).get('available_gb', 0)} GB")
            print(f"磁盘: {status.get('disk', {}).get('percent', 0)}% ({status.get('disk', {}).get('status', 'unknown')}) - 剩余 {status.get('disk', {}).get('free_gb', 0)} GB")
            print(f"进程数: {status.get('process_count', 0)}")
        elif args.command == "suggestions":
            print("=== 优化建议 ===")
            for suggestion in result.get("suggestions", []):
                print(f"- {suggestion}")
            if result.get("actions"):
                print("\n可执行操作:")
                for action in result.get("actions", []):
                    print(f"- {action['command']}: {action['description']}")
        elif args.command == "cleanup":
            print(f"=== 自动清理结果 ===")
            print(f"清理文件: {len(result.get('cleaned_files', []))}")
            print(f"释放空间: {result.get('total_freed_mb', 0)} MB")
            if result.get("errors"):
                print("错误:")
                for err in result["errors"]:
                    print(f"  - {err}")
        elif args.command == "optimize":
            print(f"=== 内存优化结果 ===")
            print(f"终止进程: {', '.join(result.get('terminated_processes', []))}")
            print(f"释放内存: {result.get('freed_memory_mb', 0)} MB")
        elif args.command in ["execute", "auto_execute", "auto", "execute_all"]:
            print(f"=== 自动优化执行结果 ===")
            print(f"摘要: {result.get('summary', '')}")
            print(f"执行操作: {len(result.get('executed_actions', []))}")
            print(f"释放空间: {result.get('total_freed_mb', 0)} MB")
            if result.get("errors"):
                print("错误:")
                for err in result["errors"]:
                    print(f"  - {err}")
        elif args.command == "auto_status":
            print(f"=== 自动执行状态 ===")
            print(f"自动执行: {'已启用' if result.get('enabled') else '已禁用'}")
            print(f"自动清理: {'已启用' if result.get('auto_cleanup') else '已禁用'}")
            print(f"自动优化: {'已启用' if result.get('auto_optimize') else '已禁用'}")
        elif "error" in result:
            print(f"错误: {result['error']}")
        elif result.get("status") == "started":
            print(f"守护进程已启动，监控间隔: {result.get('interval')}秒")
        elif result.get("status") == "stopped":
            print("守护进程已停止")
        elif result.get("status") == "daemon_mode":
            print("守护进程模式启动中...")
        else:
            print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()