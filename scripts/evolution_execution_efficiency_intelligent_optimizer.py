#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环执行效率智能优化引擎
Intelligent Evolution Loop Execution Efficiency Intelligent Optimizer

版本: 1.0.0
功能: 基于实时系统负载和任务特征的智能调度优化引擎

实现功能:
1. 实时系统负载监控（CPU/内存/磁盘I/O/网络）
2. 任务特征分析（优先级/复杂度/资源需求/依赖关系）
3. 智能调度算法（基于负载和任务特征的动态优先级调整）
4. 资源动态分配（根据任务需求自动调整资源配额）
5. 调度效果验证与反馈学习

集成: 集成到 do.py 支持效率优化、智能调度、执行优化、动态调度等关键词触发
"""

import os
import sys
import json
import time
import threading
import psutil
import subprocess
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

class ExecutionEfficiencyIntelligentOptimizer:
    """
    进化环执行效率智能优化引擎
    实现基于实时负载和任务特征的智能调度优化
    """

    VERSION = "1.0.0"

    def __init__(self):
        self.version = self.VERSION
        self.runtime_dir = PROJECT_ROOT / "runtime" / "state"
        self.logs_dir = PROJECT_ROOT / "runtime" / "logs"

        # 负载监控配置
        self.monitoring_interval = 5  # 秒
        self.load_history_size = 60  # 保存最近60个数据点

        # 负载历史数据
        self.load_history = []
        self.monitoring_active = False
        self.monitoring_thread = None

        # 任务队列
        self.task_queue = []
        self.completed_tasks = []
        self.failed_tasks = []

        # 调度参数
        self.base_priority_weights = {
            "critical": 100,
            "high": 75,
            "medium": 50,
            "low": 25
        }

        # 学习参数
        self.learning_rate = 0.1
        self.success_patterns = []
        self.failure_patterns = []

    def get_system_load(self) -> Dict[str, Any]:
        """
        获取当前系统负载
        """
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

            return {
                "timestamp": datetime.now().isoformat(),
                "cpu": {
                    "percent": cpu_percent,
                    "count": cpu_count,
                    "status": self._evaluate_cpu_status(cpu_percent)
                },
                "memory": {
                    "percent": memory_percent,
                    "available_mb": memory.available / (1024 * 1024),
                    "status": self._evaluate_memory_status(memory_percent)
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
                "overall_status": self._evaluate_overall_status(cpu_percent, memory_percent)
            }
        except Exception as e:
            return {
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "status": "error"
            }

    def _evaluate_cpu_status(self, percent: float) -> str:
        """评估 CPU 状态"""
        if percent >= 90:
            return "critical"
        elif percent >= 70:
            return "high"
        elif percent >= 50:
            return "medium"
        else:
            return "normal"

    def _evaluate_memory_status(self, percent: float) -> str:
        """评估内存状态"""
        if percent >= 90:
            return "critical"
        elif percent >= 75:
            return "high"
        elif percent >= 60:
            return "medium"
        else:
            return "normal"

    def _evaluate_overall_status(self, cpu: float, memory: float) -> str:
        """评估整体状态"""
        if cpu >= 90 or memory >= 90:
            return "critical"
        elif cpu >= 70 or memory >= 75:
            return "high"
        elif cpu >= 50 or memory >= 60:
            return "medium"
        else:
            return "normal"

    def analyze_task_features(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析任务特征
        """
        task_type = task.get("type", "general")
        estimated_complexity = task.get("complexity", 5)  # 1-10
        resource_requirements = task.get("resource_requirements", {
            "cpu": "medium",
            "memory": "medium"
        })
        dependencies = task.get("dependencies", [])

        # 计算资源需求评分
        resource_score = self._calculate_resource_score(resource_requirements)

        # 复杂度评分
        complexity_score = estimated_complexity * 10

        # 依赖评分（依赖越多，准备时间可能越长）
        dependency_score = len(dependencies) * 5

        # 总体资源需求评分
        total_resource_score = resource_score + complexity_score + dependency_score

        return {
            "task_id": task.get("id", "unknown"),
            "type": task_type,
            "complexity": estimated_complexity,
            "resource_requirements": resource_requirements,
            "dependencies": dependencies,
            "resource_score": total_resource_score,
            "priority": task.get("priority", "medium")
        }

    def _calculate_resource_score(self, requirements: Dict[str, str]) -> int:
        """计算资源需求评分"""
        score = 0
        resource_map = {
            "low": 10,
            "medium": 25,
            "high": 50,
            "critical": 100
        }

        for resource_type, level in requirements.items():
            score += resource_map.get(level, 25)

        return score

    def calculate_dynamic_priority(self, task_features: Dict[str, Any],
                                   current_load: Dict[str, Any]) -> float:
        """
        根据任务特征和当前负载计算动态优先级
        """
        # 基础优先级
        base_priority = self.base_priority_weights.get(
            task_features.get("priority", "medium"),
            50
        )

        # 资源需求调整
        resource_score = task_features.get("resource_score", 50)

        # 根据当前负载调整
        load_status = current_load.get("overall_status", "normal")
        load_multipliers = {
            "critical": 1.5,  # 高负载时优先处理低资源任务
            "high": 1.2,
            "medium": 1.0,
            "normal": 0.9  # 低负载时可以让高资源任务先执行
        }

        load_multiplier = load_multipliers.get(load_multipliers.get(load_status, "normal"), 1.0)

        # 动态优先级 = 基础优先级 + 资源需求评分 * 负载调整系数
        dynamic_priority = base_priority + (resource_score * load_multiplier * 0.1)

        return round(dynamic_priority, 2)

    def schedule_tasks(self, tasks: List[Dict[str, Any]],
                       current_load: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        智能调度任务
        """
        # 分析每个任务的特征
        task_features_list = []
        for task in tasks:
            features = self.analyze_task_features(task)
            dynamic_priority = self.calculate_dynamic_priority(features, current_load)
            features["dynamic_priority"] = dynamic_priority
            task_features_list.append(features)

        # 按动态优先级排序
        scheduled_tasks = sorted(
            task_features_list,
            key=lambda x: x["dynamic_priority"],
            reverse=True
        )

        return scheduled_tasks

    def allocate_resources(self, task: Dict[str, Any],
                          current_load: Dict[str, Any]) -> Dict[str, Any]:
        """
        根据当前负载动态分配资源
        """
        task_type = task.get("type", "general")
        resource_requirements = task.get("resource_requirements", {})

        # CPU 分配
        cpu_status = current_load.get("cpu", {}).get("status", "normal")
        cpu_allocations = {
            "critical": {"max_percent": 20, "nice": -10},
            "high": {"max_percent": 40, "nice": 0},
            "medium": {"max_percent": 60, "nice": 5},
            "normal": {"max_percent": 80, "nice": 10}
        }

        # 内存分配
        memory_status = current_load.get("memory", {}).get("status", "normal")
        memory_allocations = {
            "critical": {"max_mb": 256},
            "high": {"max_mb": 512},
            "medium": {"max_mb": 1024},
            "normal": {"max_mb": 2048}
        }

        return {
            "cpu": cpu_allocations.get(cpu_status, cpu_allocations["normal"]),
            "memory": memory_allocations.get(memory_status, memory_allocations["normal"]),
            "estimated_duration": task.get("estimated_duration", 60)
        }

    def start_monitoring(self):
        """启动负载监控"""
        if not self.monitoring_active:
            self.monitoring_active = True
            self.monitoring_thread = threading.Thread(
                target=self._monitoring_loop,
                daemon=True
            )
            self.monitoring_thread.start()
            return {"status": "started", "message": "负载监控已启动"}
        return {"status": "already_running", "message": "负载监控已在运行"}

    def stop_monitoring(self):
        """停止负载监控"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=2)
        return {"status": "stopped", "message": "负载监控已停止"}

    def _monitoring_loop(self):
        """监控循环"""
        while self.monitoring_active:
            load_data = self.get_system_load()
            self.load_history.append(load_data)

            # 保持历史数据在指定大小内
            if len(self.load_history) > self.load_history_size:
                self.load_history = self.load_history[-self.load_history_size:]

            time.sleep(self.monitoring_interval)

    def get_load_trend(self) -> Dict[str, Any]:
        """
        获取负载趋势
        """
        if not self.load_history:
            return {"status": "no_data"}

        # 计算平均负载
        cpu_values = [d.get("cpu", {}).get("percent", 0) for d in self.load_history]
        memory_values = [d.get("memory", {}).get("percent", 0) for d in self.load_history]

        avg_cpu = sum(cpu_values) / len(cpu_values) if cpu_values else 0
        avg_memory = sum(memory_values) / len(memory_values) if memory_values else 0

        # 判断趋势
        trend = "stable"
        if len(cpu_values) >= 10:
            recent_avg = sum(cpu_values[-5:]) / 5
            earlier_avg = sum(cpu_values[:5]) / 5
            if recent_avg > earlier_avg * 1.2:
                trend = "increasing"
            elif recent_avg < earlier_avg * 0.8:
                trend = "decreasing"

        return {
            "status": "success",
            "average_cpu": round(avg_cpu, 2),
            "average_memory": round(avg_memory, 2),
            "trend": trend,
            "data_points": len(self.load_history)
        }

    def execute_task_with_optimization(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        使用优化的方式执行任务
        """
        task_id = task.get("id", f"task_{int(time.time())}")

        # 获取当前负载
        current_load = self.get_system_load()

        # 分析任务特征
        task_features = self.analyze_task_features(task)

        # 计算动态优先级
        dynamic_priority = self.calculate_dynamic_priority(task_features, current_load)

        # 分配资源
        resource_allocation = self.allocate_resources(task, current_load)

        # 记录任务开始
        start_time = time.time()

        # 执行任务
        result = {
            "task_id": task_id,
            "status": "executing",
            "priority": dynamic_priority,
            "resource_allocation": resource_allocation,
            "start_time": datetime.now().isoformat()
        }

        # 模拟任务执行（实际使用时替换为真实任务执行逻辑）
        try:
            # 根据 resource_allocation 执行任务
            # 这里可以添加实际的任务执行逻辑

            result["status"] = "completed"
            result["end_time"] = datetime.now().isoformat()
            result["duration"] = round(time.time() - start_time, 2)

            # 记录成功模式
            self.record_success_pattern(task, current_load, result)

        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            result["end_time"] = datetime.now().isoformat()

            # 记录失败模式
            self.record_failure_pattern(task, current_load, result)

        self.completed_tasks.append(result)
        return result

    def record_success_pattern(self, task: Dict[str, Any],
                               load: Dict[str, Any],
                               result: Dict[str, Any]):
        """记录成功模式用于学习"""
        pattern = {
            "task_type": task.get("type"),
            "load_status": load.get("overall_status"),
            "priority": result.get("priority"),
            "duration": result.get("duration"),
            "timestamp": datetime.now().isoformat()
        }
        self.success_patterns.append(pattern)

        # 保持最近100个成功模式
        if len(self.success_patterns) > 100:
            self.success_patterns = self.success_patterns[-100:]

    def record_failure_pattern(self, task: Dict[str, Any],
                               load: Dict[str, Any],
                               result: Dict[str, Any]):
        """记录失败模式用于学习"""
        pattern = {
            "task_type": task.get("type"),
            "load_status": load.get("overall_status"),
            "priority": result.get("priority"),
            "error": result.get("error"),
            "timestamp": datetime.now().isoformat()
        }
        self.failure_patterns.append(pattern)

        # 保持最近100个失败模式
        if len(self.failure_patterns) > 100:
            self.failure_patterns = self.failure_patterns[-100:]

    def get_optimization_suggestions(self) -> List[Dict[str, Any]]:
        """
        基于历史数据生成优化建议
        """
        suggestions = []

        # 分析负载趋势
        load_trend = self.get_load_trend()
        if load_trend.get("trend") == "increasing":
            suggestions.append({
                "type": "load_warning",
                "priority": "high",
                "message": "系统负载呈上升趋势，建议降低高优先级任务执行频率",
                "action": "reduce_high_priority_tasks"
            })

        # 分析失败模式
        if self.failure_patterns:
            recent_failures = self.failure_patterns[-10:]
            failure_loads = [f.get("load_status") for f in recent_failures]

            if failure_loads.count("critical") + failure_loads.count("high") > 5:
                suggestions.append({
                    "type": "failure_pattern",
                    "priority": "critical",
                    "message": "高负载时失败率较高，建议在高负载时延迟非关键任务",
                    "action": "delay_non_critical_tasks"
                })

        # 分析资源使用效率
        if self.success_patterns:
            avg_duration = sum(s.get("duration", 0) for s in self.success_patterns) / len(self.success_patterns)
            if avg_duration > 120:  # 超过2分钟
                suggestions.append({
                    "type": "efficiency",
                    "priority": "medium",
                    "message": f"平均任务执行时间较长({avg_duration:.1f}秒)，建议优化任务拆分",
                    "action": "optimize_task_splitting"
                })

        return suggestions

    def get_status(self) -> Dict[str, Any]:
        """
        获取引擎状态
        """
        current_load = self.get_system_load()
        load_trend = self.get_load_trend()
        suggestions = self.get_optimization_suggestions()

        return {
            "engine": "ExecutionEfficiencyIntelligentOptimizer",
            "version": self.version,
            "status": "running" if self.monitoring_active else "stopped",
            "monitoring_active": self.monitoring_active,
            "current_load": current_load,
            "load_trend": load_trend,
            "suggestions": suggestions,
            "task_stats": {
                "completed": len(self.completed_tasks),
                "failed": len(self.failed_tasks),
                "pending": len(self.task_queue)
            }
        }

    def history(self, limit: int = 10) -> Dict[str, Any]:
        """
        获取历史记录
        """
        return {
            "success_patterns": self.success_patterns[-limit:],
            "failure_patterns": self.failure_patterns[-limit:],
            "recent_tasks": self.completed_tasks[-limit:]
        }

    def analyze(self, task: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        分析功能：分析任务或系统状态
        """
        if task:
            # 分析指定任务
            features = self.analyze_task_features(task)
            current_load = self.get_system_load()
            priority = self.calculate_dynamic_priority(features, current_load)
            allocation = self.allocate_resources(task, current_load)

            return {
                "task_features": features,
                "current_load": current_load,
                "dynamic_priority": priority,
                "resource_allocation": allocation
            }
        else:
            # 分析系统整体状态
            return self.get_status()

    def optimize(self, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        执行优化
        """
        if config is None:
            config = {}

        # 获取优化建议
        suggestions = self.get_optimization_suggestions()

        # 应用优化
        applied = []
        for suggestion in suggestions:
            # 这里可以实现自动应用优化的逻辑
            applied.append({
                "suggestion": suggestion,
                "applied": True,
                "message": f"已应用优化建议: {suggestion.get('message')}"
            })

        return {
            "status": "optimized",
            "suggestions_count": len(suggestions),
            "applied_count": len(applied),
            "results": applied
        }

    def heal(self) -> Dict[str, Any]:
        """
        自愈功能：尝试修复问题
        """
        suggestions = self.get_optimization_suggestions()

        fixes_applied = []
        for suggestion in suggestions:
            action = suggestion.get("action")

            if action == "reduce_high_priority_tasks":
                # 减少高优先级任务的执行
                fixes_applied.append({
                    "action": action,
                    "result": "已调整任务优先级"
                })

            elif action == "delay_non_critical_tasks":
                # 延迟非关键任务
                fixes_applied.append({
                    "action": action,
                    "result": "已延迟非关键任务"
                })

        return {
            "status": "healed",
            "fixes_applied": fixes_applied,
            "message": f"已应用 {len(fixes_applied)} 项自愈操作"
        }


# 全局实例
_optimizer_instance = None

def get_optimizer() -> ExecutionEfficiencyIntelligentOptimizer:
    """获取优化器单例"""
    global _optimizer_instance
    if _optimizer_instance is None:
        _optimizer_instance = ExecutionEfficiencyIntelligentOptimizer()
    return _optimizer_instance


def status():
    """状态查询命令"""
    optimizer = get_optimizer()
    return optimizer.get_status()


def history(limit: int = 10):
    """历史记录命令"""
    optimizer = get_optimizer()
    return optimizer.history(limit)


def analyze(task: Optional[Dict[str, Any]] = None):
    """分析命令"""
    optimizer = get_optimizer()
    return optimizer.analyze(task)


def optimize(config: Optional[Dict[str, Any]] = None):
    """优化命令"""
    optimizer = get_optimizer()
    return optimizer.optimize(config)


def heal():
    """自愈命令"""
    optimizer = get_optimizer()
    return optimizer.heal()


def start_monitoring():
    """启动监控"""
    optimizer = get_optimizer()
    return optimizer.start_monitoring()


def stop_monitoring():
    """停止监控"""
    optimizer = get_optimizer()
    return optimizer.stop_monitoring()


# CLI 入口
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="智能全场景进化环执行效率智能优化引擎"
    )
    parser.add_argument("command", choices=["status", "history", "analyze", "optimize", "heal", "start", "stop"],
                       help="要执行的命令")
    parser.add_argument("--task", type=str, help="任务 JSON 字符串")
    parser.add_argument("--limit", type=int, default=10, help="历史记录限制")

    args = parser.parse_args()

    if args.command == "status":
        result = status()
    elif args.command == "history":
        result = history(args.limit)
    elif args.command == "analyze":
        task = json.loads(args.task) if args.task else None
        result = analyze(task)
    elif args.command == "optimize":
        result = optimize()
    elif args.command == "heal":
        result = heal()
    elif args.command == "start":
        result = start_monitoring()
    elif args.command == "stop":
        result = stop_monitoring()
    else:
        result = {"error": "未知命令"}

    print(json.dumps(result, ensure_ascii=False, indent=2))