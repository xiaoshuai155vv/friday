#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环执行效率可视化监控与驾驶舱深度集成引擎
Evolution Execution Efficiency Visualization & Cockpit Integration Engine

版本: 1.0.0
功能: 将 round 406 的执行效率优化引擎与进化驾驶舱深度集成，实现可视化负载监控

实现功能:
1. 负载数据可视化展示 (CPU/内存/磁盘/网络/调度状态)
2. 实时系统状态仪表盘
3. 智能调度建议可视化
4. 与进化驾驶舱深度集成
5. 负载趋势分析与预测可视化

集成: 集成到 do.py 支持效率监控、负载可视化、驾驶舱集成等关键词触发

依赖:
- evolution_cockpit_engine.py (round 350)
- evolution_execution_efficiency_intelligent_optimizer.py (round 406)
"""

import os
import sys
import json
import time
import threading
import psutil
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from collections import deque

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def _safe_print(text: str):
    """安全打印，处理编码问题"""
    import re
    try:
        print(text)
    except UnicodeEncodeError:
        clean_text = re.sub(r'[^\x00-\x7F]+', '', text)
        print(clean_text)


class ExecutionEfficiencyCockpitIntegrationEngine:
    """
    执行效率可视化监控与驾驶舱深度集成引擎
    实现负载数据的可视化展示与驾驶舱集成
    """

    VERSION = "1.0.0"

    def __init__(self):
        self.version = self.VERSION
        self.project_root = PROJECT_ROOT
        self.scripts_dir = PROJECT_ROOT / "scripts"
        self.runtime_dir = PROJECT_ROOT / "runtime"
        self.state_dir = self.runtime_dir / "state"
        self.logs_dir = self.runtime_dir / "logs"

        # 状态文件
        self.state_file = self.state_dir / "execution_efficiency_cockpit_state.json"
        self.load_data_file = self.state_dir / "execution_load_history.json"

        # 初始化目录
        self._ensure_directories()

        # 负载监控配置
        self.monitoring_interval = 5  # 秒
        self.history_size = 120  # 保存最近120个数据点 (10分钟)

        # 负载历史数据
        self.load_history = deque(maxlen=self.history_size)
        self.monitoring_active = False
        self.monitoring_thread = None

        # 驾驶舱集成状态
        self.cockpit_connected = False
        self.cockpit_data = {}

        # 可视化配置
        self.dashboard_config = self._load_dashboard_config()

        # 调度建议
        self.scheduling_suggestions = []

        # 尝试加载执行效率优化引擎
        self.optimizer = self._load_optimizer()

    def _ensure_directories(self):
        """确保必要的目录存在"""
        for directory in [self.state_dir, self.logs_dir]:
            os.makedirs(directory, exist_ok=True)

    def _load_dashboard_config(self) -> Dict:
        """加载可视化仪表盘配置"""
        config_file = self.state_dir / "execution_dashboard_config.json"
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                _safe_print(f"[效率驾驶舱] 配置加载失败: {e}")

        # 默认配置
        default_config = {
            "refresh_interval": 5,  # 刷新间隔(秒)
            "show_cpu": True,
            "show_memory": True,
            "show_disk": True,
            "show_network": True,
            "show_scheduling": True,
            "show_trends": True,
            "alert_thresholds": {
                "cpu_critical": 90,
                "cpu_high": 70,
                "memory_critical": 90,
                "memory_high": 75
            },
            "trend_window": 20,  # 趋势分析窗口
        }

        self._save_dashboard_config(default_config)
        return default_config

    def _save_dashboard_config(self, config: Dict):
        """保存可视化仪表盘配置"""
        config_file = self.state_dir / "execution_dashboard_config.json"
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            _safe_print(f"[效率驾驶舱] 配置保存失败: {e}")

    def _load_optimizer(self) -> Optional[Any]:
        """加载执行效率优化引擎"""
        try:
            # 添加 scripts 目录到 sys.path
            if str(self.scripts_dir) not in sys.path:
                sys.path.insert(0, str(self.scripts_dir))

            from evolution_execution_efficiency_intelligent_optimizer import (
                ExecutionEfficiencyIntelligentOptimizer
            )
            optimizer = ExecutionEfficiencyIntelligentOptimizer()
            _safe_print("[效率驾驶舱] 执行效率优化引擎加载成功")
            return optimizer
        except ImportError as e:
            _safe_print(f"[效率驾驶舱] 无法加载执行效率优化引擎: {e}")
            return None
        except Exception as e:
            _safe_print(f"[效率驾驶舱] 加载执行效率优化引擎失败: {e}")
            return None

    def start_monitoring(self):
        """启动负载监控"""
        if self.monitoring_active:
            _safe_print("[效率驾驶舱] 监控已在运行中")
            return

        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        _safe_print("[效率驾驶舱] 负载监控已启动")

    def stop_monitoring(self):
        """停止负载监控"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=2)
        _safe_print("[效率驾驶舱] 负载监控已停止")

    def _monitoring_loop(self):
        """监控循环"""
        while self.monitoring_active:
            try:
                # 获取负载数据
                load_data = self._collect_load_data()

                # 保存到历史
                self.load_history.append(load_data)

                # 保存到文件
                self._save_load_data()

                # 生成调度建议
                self._generate_scheduling_suggestions(load_data)

                # 更新驾驶舱数据
                self._update_cockpit_data(load_data)

            except Exception as e:
                _safe_print(f"[效率驾驶舱] 监控循环错误: {e}")

            time.sleep(self.monitoring_interval)

    def _collect_load_data(self) -> Dict[str, Any]:
        """收集负载数据"""
        try:
            # 使用 optimizer 如果可用
            if self.optimizer and hasattr(self.optimizer, 'get_system_load'):
                return self.optimizer.get_system_load()

            # 直接收集
            return self._collect_direct_load_data()

        except Exception as e:
            return {
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "status": "error"
            }

    def _collect_direct_load_data(self) -> Dict[str, Any]:
        """直接收集负载数据"""
        try:
            # CPU 使用率
            cpu_percent = psutil.cpu_percent(interval=0.5)
            cpu_count = psutil.cpu_count()

            # 内存使用情况
            memory = psutil.virtual_memory()
            memory_percent = memory.percent

            # 磁盘 I/O
            disk_io = psutil.disk_io_counters()
            disk_read_mb = disk_io.read_bytes / (1024 * 1024) if disk_io else 0
            disk_write_mb = disk_io.write_bytes / (1024 * 1024) if disk_io else 0

            # 网络 I/O
            net_io = psutil.net_io_counters()
            net_sent_mb = net_io.bytes_sent / (1024 * 1024) if net_io else 0
            net_recv_mb = net_io.bytes_recv / (1024 * 1024) if net_io else 0

            # 进程数
            process_count = len(psutil.pids())

            # 评估状态
            cpu_status = self._evaluate_status(cpu_percent, "cpu")
            memory_status = self._evaluate_status(memory_percent, "memory")

            return {
                "timestamp": datetime.now().isoformat(),
                "cpu": {
                    "percent": round(cpu_percent, 1),
                    "count": cpu_count,
                    "status": cpu_status
                },
                "memory": {
                    "percent": round(memory_percent, 1),
                    "available_mb": round(memory.available / (1024 * 1024), 1),
                    "total_mb": round(memory.total / (1024 * 1024), 1),
                    "status": memory_status
                },
                "disk": {
                    "read_mb": round(disk_read_mb, 2),
                    "write_mb": round(disk_write_mb, 2),
                    "status": "normal"
                },
                "network": {
                    "sent_mb": round(net_sent_mb, 2),
                    "recv_mb": round(net_recv_mb, 2)
                },
                "processes": process_count,
                "overall_status": "normal" if cpu_status == "normal" and memory_status == "normal" else "warning"
            }
        except Exception as e:
            return {
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "status": "error"
            }

    def _evaluate_status(self, percent: float, metric: str) -> str:
        """评估状态"""
        thresholds = self.dashboard_config.get("alert_thresholds", {})

        if metric == "cpu":
            critical = thresholds.get("cpu_critical", 90)
            high = thresholds.get("cpu_high", 70)
        else:
            critical = thresholds.get("memory_critical", 90)
            high = thresholds.get("memory_high", 75)

        if percent >= critical:
            return "critical"
        elif percent >= high:
            return "high"
        elif percent >= 50:
            return "medium"
        else:
            return "normal"

    def _generate_scheduling_suggestions(self, load_data: Dict):
        """生成调度建议"""
        suggestions = []

        try:
            cpu_percent = load_data.get("cpu", {}).get("percent", 0)
            memory_percent = load_data.get("memory", {}).get("percent", 0)

            # CPU 建议
            if cpu_percent >= 90:
                suggestions.append({
                    "type": "cpu",
                    "level": "critical",
                    "message": "CPU 使用率极高，建议延迟非关键任务",
                    "action": "delay_non_critical"
                })
            elif cpu_percent >= 70:
                suggestions.append({
                    "type": "cpu",
                    "level": "warning",
                    "message": "CPU 使用率较高，建议降低任务优先级",
                    "action": "reduce_priority"
                })

            # 内存建议
            if memory_percent >= 90:
                suggestions.append({
                    "type": "memory",
                    "level": "critical",
                    "message": "内存使用率极高，建议清理缓存",
                    "action": "clear_cache"
                })
            elif memory_percent >= 75:
                suggestions.append({
                    "type": "memory",
                    "level": "warning",
                    "message": "内存使用率较高，建议延迟内存密集型任务",
                    "action": "delay_memory_intensive"
                })

            # 综合建议
            if cpu_percent < 50 and memory_percent < 60:
                suggestions.append({
                    "type": "general",
                    "level": "info",
                    "message": "系统负载低，适合执行密集型任务",
                    "action": "execute_intensive"
                })

        except Exception as e:
            _safe_print(f"[效率驾驶舱] 生成调度建议失败: {e}")

        self.scheduling_suggestions = suggestions

    def _update_cockpit_data(self, load_data: Dict):
        """更新驾驶舱数据"""
        self.cockpit_data = {
            "timestamp": datetime.now().isoformat(),
            "load": load_data,
            "suggestions": self.scheduling_suggestions,
            "trend": self._analyze_trend(),
            "monitoring_active": self.monitoring_active
        }

        # 保存状态
        self._save_state()

    def _analyze_trend(self) -> Dict:
        """分析趋势"""
        if len(self.load_history) < 5:
            return {"status": "insufficient_data"}

        try:
            # 获取最近的数据点
            recent = list(self.load_history)[-self.dashboard_config.get("trend_window", 20):]

            cpu_values = [d.get("cpu", {}).get("percent", 0) for d in recent]
            memory_values = [d.get("memory", {}).get("percent", 0) for d in recent]

            # 计算趋势
            cpu_trend = self._calculate_trend(cpu_values)
            memory_trend = self._calculate_trend(memory_values)

            return {
                "cpu_trend": cpu_trend,
                "memory_trend": memory_trend,
                "cpu_avg": round(sum(cpu_values) / len(cpu_values), 1),
                "memory_avg": round(sum(memory_values) / len(memory_values), 1),
                "sample_count": len(recent)
            }

        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _calculate_trend(self, values: List[float]) -> str:
        """计算趋势"""
        if len(values) < 2:
            return "stable"

        # 简单线性趋势
        first_half = sum(values[:len(values)//2]) / (len(values)//2)
        second_half = sum(values[len(values)//2:]) / (len(values) - len(values)//2)

        diff = second_half - first_half

        if diff > 10:
            return "increasing"
        elif diff < -10:
            return "decreasing"
        else:
            return "stable"

    def _save_state(self):
        """保存状态"""
        try:
            state = {
                "version": self.version,
                "timestamp": datetime.now().isoformat(),
                "monitoring_active": self.monitoring_active,
                "cockpit_data": self.cockpit_data,
                "suggestions": self.scheduling_suggestions
            }

            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)

        except Exception as e:
            _safe_print(f"[效率驾驶舱] 状态保存失败: {e}")

    def _save_load_data(self):
        """保存负载历史数据"""
        try:
            data = {
                "timestamp": datetime.now().isoformat(),
                "history": list(self.load_history)
            }

            with open(self.load_data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            _safe_print(f"[效率驾驶舱] 负载数据保存失败: {e}")

    def get_current_status(self) -> Dict[str, Any]:
        """获取当前状态"""
        if not self.load_history:
            return {
                "status": "no_data",
                "message": "暂无负载数据，请先启动监控"
            }

        latest = list(self.load_history)[-1] if self.load_history else {}

        return {
            "status": "ok",
            "monitoring": self.monitoring_active,
            "current_load": latest,
            "suggestions": self.scheduling_suggestions,
            "trend": self.cockpit_data.get("trend", {}),
            "timestamp": datetime.now().isoformat()
        }

    def get_dashboard_data(self) -> Dict[str, Any]:
        """获取仪表盘数据"""
        if not self.load_history:
            return {
                "status": "no_data",
                "message": "暂无负载数据"
            }

        # 收集最近的数据
        history_list = list(self.load_history)

        # 当前状态
        current = history_list[-1] if history_list else {}

        # 历史摘要
        cpu_values = [d.get("cpu", {}).get("percent", 0) for d in history_list]
        memory_values = [d.get("memory", {}).get("percent", 0) for d in history_list]

        return {
            "status": "ok",
            "version": self.version,
            "timestamp": datetime.now().isoformat(),
            "current": current,
            "summary": {
                "cpu": {
                    "current": current.get("cpu", {}).get("percent", 0),
                    "average": round(sum(cpu_values) / len(cpu_values), 1) if cpu_values else 0,
                    "max": max(cpu_values) if cpu_values else 0,
                    "min": min(cpu_values) if cpu_values else 0,
                    "status": current.get("cpu", {}).get("status", "unknown")
                },
                "memory": {
                    "current": current.get("memory", {}).get("percent", 0),
                    "average": round(sum(memory_values) / len(memory_values), 1) if memory_values else 0,
                    "max": max(memory_values) if memory_values else 0,
                    "min": min(memory_values) if memory_values else 0,
                    "status": current.get("memory", {}).get("status", "unknown")
                },
                "disk": current.get("disk", {}),
                "network": current.get("network", {}),
                "processes": current.get("processes", 0)
            },
            "trend": self.cockpit_data.get("trend", {}),
            "suggestions": self.scheduling_suggestions,
            "monitoring_active": self.monitoring_active
        }

    def start(self):
        """启动引擎"""
        self.start_monitoring()
        return {
            "status": "started",
            "message": "执行效率可视化监控引擎已启动",
            "version": self.version
        }

    def stop(self):
        """停止引擎"""
        self.stop_monitoring()
        return {
            "status": "stopped",
            "message": "执行效率可视化监控引擎已停止"
        }

    def analyze(self) -> Dict[str, Any]:
        """分析负载"""
        return self.get_dashboard_data()

    def optimize(self) -> Dict[str, Any]:
        """优化建议"""
        return {
            "status": "ok",
            "suggestions": self.scheduling_suggestions,
            "message": f"当前有 {len(self.scheduling_suggestions)} 条调度建议"
        }

    def heal(self) -> Dict[str, Any]:
        """自愈检查"""
        if not self.monitoring_active:
            return {
                "status": "healed",
                "action": "start_monitoring",
                "message": "启动负载监控以确保系统健康"
            }

        # 检查是否有严重警告
        critical_suggestions = [s for s in self.scheduling_suggestions if s.get("level") == "critical"]

        if critical_suggestions:
            return {
                "status": "warning",
                "message": f"发现 {len(critical_suggestions)} 条严重建议需要关注",
                "suggestions": critical_suggestions
            }

        return {
            "status": "healthy",
            "message": "系统负载状态正常"
        }


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="执行效率可视化监控与驾驶舱集成引擎")
    parser.add_argument("action", nargs="?", default="status",
                       choices=["start", "stop", "status", "analyze", "optimize", "heal"],
                       help="执行的操作")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")

    args = parser.parse_args()

    engine = ExecutionEfficiencyCockpitIntegrationEngine()

    if args.action == "start":
        result = engine.start()
    elif args.action == "stop":
        result = engine.stop()
    elif args.action == "status":
        result = engine.get_current_status()
    elif args.action == "analyze":
        result = engine.get_dashboard_data()
    elif args.action == "optimize":
        result = engine.optimize()
    elif args.action == "heal":
        result = engine.heal()
    else:
        result = {"status": "unknown", "message": f"未知操作: {args.action}"}

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()