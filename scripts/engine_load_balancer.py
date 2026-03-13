#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能引擎负载均衡与协同调度引擎 (Engine Load Balancer)

让系统能够在多引擎并发执行时智能分配资源、动态调整优先级，实现真正的「智能资源调度层」。

功能：
1. 引擎资源占用实时监控（CPU、内存、执行时间）
2. 负载均衡策略（根据资源占用分配任务）
3. 智能优先级调度（基于任务紧急度和资源状态动态调整）
4. 跨引擎协同调度（多个引擎执行时协调资源）
5. 执行效果追踪与反馈

使用方法：
    python engine_load_balancer.py status
    python engine_load_balancer.py monitor
    python engine_load_balancer.py schedule
    python engine_load_balancer.py balance
    python engine_load_balancer.py analyze
    python engine_load_balancer.py history
"""

import json
import os
import sys
import time
import subprocess
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from collections import defaultdict
from enum import Enum

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
RUNTIME_STATE = PROJECT_ROOT / "runtime" / "state"
RUNTIME_LOGS = PROJECT_ROOT / "runtime" / "logs"
REFERENCES = PROJECT_ROOT / "references"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"


class TaskPriority(Enum):
    """任务优先级"""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4


class LoadBalanceStrategy(Enum):
    """负载均衡策略"""
    ROUND_ROBIN = "round_robin"  # 轮询
    LEAST_LOADED = "least_loaded"  # 最少负载
    WEIGHTED = "weighted"  # 加权
    ADAPTIVE = "adaptive"  # 自适应


@dataclass
class EngineResourceUsage:
    """引擎资源使用情况"""
    engine_name: str
    cpu_percent: float = 0.0
    memory_mb: float = 0.0
    active_tasks: int = 0
    avg_response_time: float = 0.0
    success_rate: float = 1.0
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ScheduledTask:
    """调度任务"""
    task_id: str
    engine_name: str
    priority: str  # critical, high, medium, low
    estimated_time: float  # 预估执行时间（秒）
    resource_requirement: Dict[str, float]  # 资源需求 {cpu: 0.2, memory: 100}
    status: str = "pending"  # pending, running, completed, failed
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    result: Optional[str] = None


@dataclass
class LoadBalanceDecision:
    """负载均衡决策"""
    decision_id: str
    task_id: str
    target_engine: str
    strategy: str
    reason: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    success: bool = True


class EngineLoadBalancer:
    """智能引擎负载均衡与协同调度引擎"""

    def __init__(self):
        self.state_dir = RUNTIME_STATE
        self.logs_dir = RUNTIME_LOGS

        # 确保目录存在
        self.state_dir.mkdir(parents=True, exist_ok=True)

        # 存储文件
        self.config_file = self.state_dir / "engine_load_balancer_config.json"
        self.resource_file = self.state_dir / "engine_resource_usage.json"
        self.schedule_file = self.state_dir / "engine_schedule_log.json"
        self.decision_file = self.state_dir / "engine_load_balance_decisions.json"

        # 资源监控
        self.resource_usage: Dict[str, EngineResourceUsage] = {}
        self.task_history: List[ScheduledTask] = []
        self.decisions: List[LoadBalanceDecision] = []

        # 配置
        self.config = self._load_config()

        # 加载数据
        self._load_resource_usage()
        self._load_schedule_log()
        self._load_decisions()

        # 监控线程
        self._monitoring = False
        self._monitor_thread = None

        # 引擎注册表
        self._register_engines()

    def _register_engines(self):
        """注册引擎列表"""
        # 已知的引擎及其资源特征
        self.engine_registry = {
            "engine_realtime_optimizer": {"cpu_weight": 0.3, "memory_weight": 0.3, "priority": "high"},
            "engine_auto_optimizer": {"cpu_weight": 0.3, "memory_weight": 0.3, "priority": "high"},
            "engine_orchestration_optimizer": {"cpu_weight": 0.2, "memory_weight": 0.2, "priority": "medium"},
            "engine_combination_recommender": {"cpu_weight": 0.2, "memory_weight": 0.2, "priority": "medium"},
            "engine_performance_monitor": {"cpu_weight": 0.1, "memory_weight": 0.1, "priority": "low"},
            "engine_collaboration_optimizer": {"cpu_weight": 0.2, "memory_weight": 0.2, "priority": "medium"},
            "evolution_strategy_optimizer": {"cpu_weight": 0.4, "memory_weight": 0.4, "priority": "high"},
            "evolution_loop_self_optimizer": {"cpu_weight": 0.3, "memory_weight": 0.3, "priority": "high"},
            "evolution_knowledge_inheritance": {"cpu_weight": 0.2, "memory_weight": 0.3, "priority": "medium"},
            "evolution_direction_discovery": {"cpu_weight": 0.3, "memory_weight": 0.3, "priority": "high"},
            "unified_service_hub": {"cpu_weight": 0.2, "memory_weight": 0.2, "priority": "medium"},
            "multi_agent_collaboration": {"cpu_weight": 0.3, "memory_weight": 0.3, "priority": "high"},
            "cross_engine_task_planner": {"cpu_weight": 0.2, "memory_weight": 0.2, "priority": "medium"},
            "do": {"cpu_weight": 0.1, "memory_weight": 0.1, "priority": "high"},
        }

    def _load_config(self) -> Dict[str, Any]:
        """加载配置"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass

        # 默认配置
        default_config = {
            "monitoring_enabled": True,
            "monitoring_interval": 10,  # 秒
            "default_strategy": "adaptive",
            "strategies": {
                "round_robin": {"enabled": True, "description": "轮询分配"},
                "least_loaded": {"enabled": True, "description": "分配给负载最低的引擎"},
                "weighted": {"enabled": True, "description": "按权重分配"},
                "adaptive": {"enabled": True, "description": "自适应策略"}
            },
            "thresholds": {
                "cpu_high": 80.0,  # CPU 阈值
                "memory_high": 500.0,  # 内存阈值 (MB)
                "max_concurrent_tasks": 10,  # 最大并发任务数
                "response_time_threshold": 5.0  # 响应时间阈值
            },
            "priority_weights": {
                "critical": 1.0,
                "high": 0.8,
                "medium": 0.5,
                "low": 0.3
            }
        }
        self._save_config(default_config)
        return default_config

    def _save_config(self, config: Dict[str, Any]):
        """保存配置"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

    def _load_resource_usage(self):
        """加载资源使用数据"""
        if self.resource_file.exists():
            try:
                with open(self.resource_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for name, usage in data.items():
                        self.resource_usage[name] = EngineResourceUsage(**usage)
            except Exception:
                pass

    def _save_resource_usage(self):
        """保存资源使用数据"""
        data = {name: asdict(usage) for name, usage in self.resource_usage.items()}
        with open(self.resource_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _load_schedule_log(self):
        """加载调度日志"""
        if self.schedule_file.exists():
            try:
                with open(self.schedule_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.task_history = [ScheduledTask(**task) for task in data]
            except Exception:
                pass

    def _save_schedule_log(self):
        """保存调度日志"""
        data = [asdict(task) for task in self.task_history]
        with open(self.schedule_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _load_decisions(self):
        """加载负载均衡决策"""
        if self.decision_file.exists():
            try:
                with open(self.decision_file, 'r', encoding='utf-8') as f:
                    self.decisions = [LoadBalanceDecision(**d) for d in json.load(f)]
            except Exception:
                pass

    def _save_decisions(self):
        """保存负载均衡决策"""
        data = [asdict(d) for d in self.decisions]
        with open(self.decision_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _get_system_resources(self) -> Dict[str, float]:
        """获取系统资源使用情况（使用 wmic）"""
        cpu_percent = 0.0
        memory_percent = 0.0
        memory_available_mb = 0.0
        cpu_count = 1

        try:
            # 获取 CPU 使用率
            result = subprocess.run(
                ['wmic', 'cpu', 'get', 'loadpercentage'],
                capture_output=True, text=True, timeout=5, encoding='gbk', errors='ignore'
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1 and lines[1].strip().isdigit():
                    cpu_percent = float(lines[1].strip())
        except Exception:
            pass

        try:
            # 获取内存使用率
            result = subprocess.run(
                ['wmic', 'OS', 'get', 'FreePhysicalMemory,TotalVisibleMemorySize', '/format:list'],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                free_mem = 0
                total_mem = 0
                for line in result.stdout.split('\n'):
                    if 'FreePhysicalMemory' in line:
                        free_mem = float(line.split('=')[1].strip()) / 1024  # KB to MB
                    elif 'TotalVisibleMemorySize' in line:
                        total_mem = float(line.split('=')[1].strip()) / 1024  # KB to MB

                if total_mem > 0:
                    memory_percent = ((total_mem - free_mem) / total_mem) * 100
                    memory_available_mb = free_mem
        except Exception:
            pass

        try:
            # 获取 CPU 核心数
            result = subprocess.run(
                ['wmic', 'cpu', 'get', 'NumberOfCores'],
                capture_output=True, text=True, timeout=5, encoding='gbk', errors='ignore'
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1 and lines[1].strip().isdigit():
                    cpu_count = int(lines[1].strip())
        except Exception:
            pass

        return {
            "cpu_percent": cpu_percent,
            "memory_percent": memory_percent,
            "memory_available_mb": memory_available_mb,
            "cpu_count": cpu_count
        }

    def _estimate_engine_resources(self, engine_name: str) -> EngineResourceUsage:
        """估算引擎资源使用（基于注册表）"""
        if engine_name in self.resource_usage:
            return self.resource_usage[engine_name]

        # 基于注册表估算
        registry = self.engine_registry.get(engine_name, {})
        return EngineResourceUsage(
            engine_name=engine_name,
            cpu_percent=registry.get("cpu_weight", 0.1) * 10,
            memory_mb=registry.get("memory_weight", 0.1) * 500,
            active_tasks=0,
            avg_response_time=1.0,
            success_rate=0.95
        )

    def _update_resource_usage(self, engine_name: str, usage: EngineResourceUsage):
        """更新资源使用"""
        usage.last_updated = datetime.now().isoformat()
        self.resource_usage[engine_name] = usage
        self._save_resource_usage()

    def monitor(self) -> Dict[str, Any]:
        """监控引擎资源使用"""
        # 获取系统资源
        system_resources = self._get_system_resources()

        # 更新各引擎的资源使用情况
        for engine_name in self.engine_registry.keys():
            usage = self._estimate_engine_resources(engine_name)

            # 添加系统资源影响
            usage.cpu_percent = min(100, usage.cpu_percent + system_resources["cpu_percent"] * 0.1)
            usage.memory_mb = min(2000, usage.memory_mb + system_resources["memory_percent"])

            self._update_resource_usage(engine_name, usage)

        # 检查是否需要负载均衡
        needs_balance = self._check_load_balance_needed()

        return {
            "status": "ok",
            "system_resources": system_resources,
            "engine_usage": {name: asdict(usage) for name, usage in self.resource_usage.items()},
            "needs_balance": needs_balance,
            "timestamp": datetime.now().isoformat()
        }

    def _check_load_balance_needed(self) -> bool:
        """检查是否需要负载均衡"""
        thresholds = self.config.get("thresholds", {})

        # 检查系统资源
        system = self._get_system_resources()
        if system["cpu_percent"] > thresholds.get("cpu_high", 80):
            return True
        if system["memory_percent"] > 80:
            return True

        # 检查引擎资源
        for usage in self.resource_usage.values():
            if usage.cpu_percent > thresholds.get("cpu_high", 80):
                return True
            if usage.memory_mb > thresholds.get("memory_high", 500):
                return True
            if usage.avg_response_time > thresholds.get("response_time_threshold", 5.0):
                return True

        return False

    def schedule_task(self, task_id: str, engine_name: str, priority: str = "medium",
                     estimated_time: float = 1.0, resource_requirement: Dict[str, float] = None) -> Dict[str, Any]:
        """调度任务"""
        if resource_requirement is None:
            resource_requirement = {"cpu": 0.1, "memory": 50}

        task = ScheduledTask(
            task_id=task_id,
            engine_name=engine_name,
            priority=priority,
            estimated_time=estimated_time,
            resource_requirement=resource_requirement
        )

        # 根据策略选择目标引擎
        target_engine, strategy = self._select_target_engine(engine_name, priority, resource_requirement)

        # 创建决策
        decision = LoadBalanceDecision(
            decision_id=f"dec_{int(time.time())}",
            task_id=task_id,
            target_engine=target_engine,
            strategy=strategy,
            reason=self._generate_decision_reason(target_engine, priority, resource_requirement)
        )

        self.decisions.append(decision)
        self._save_decisions()

        # 启动任务模拟
        task.engine_name = target_engine
        task.status = "running"
        task.started_at = datetime.now().isoformat()
        self.task_history.append(task)
        self._save_schedule_log()

        # 更新引擎资源使用
        if target_engine in self.resource_usage:
            self.resource_usage[target_engine].active_tasks += 1

        return {
            "status": "scheduled",
            "task_id": task_id,
            "target_engine": target_engine,
            "strategy": strategy,
            "decision": asdict(decision),
            "timestamp": datetime.now().isoformat()
        }

    def _select_target_engine(self, requested_engine: str, priority: str,
                              resource_requirement: Dict[str, float]) -> tuple:
        """选择目标引擎"""
        strategy_name = self.config.get("default_strategy", "adaptive")

        if strategy_name == "adaptive":
            # 自适应策略：综合考虑
            strategy_name = self._choose_adaptive_strategy(priority, resource_requirement)

        if strategy_name == "least_loaded":
            # 最少负载策略
            return self._select_least_loaded_engine(resource_requirement)
        elif strategy_name == "round_robin":
            # 轮询策略
            return self._select_round_robin_engine()
        elif strategy_name == "weighted":
            # 加权策略
            return self._select_weighted_engine(priority)
        else:
            # 默认使用请求的引擎
            return requested_engine, "default"

    def _choose_adaptive_strategy(self, priority: str, resource_requirement: Dict[str, float]) -> str:
        """选择自适应策略"""
        if priority == "critical" or priority == "high":
            # 高优先级任务使用最少负载策略
            return "least_loaded"
        elif resource_requirement.get("cpu", 0) > 0.3:
            # 高资源需求使用加权策略
            return "weighted"
        else:
            # 普通任务使用轮询
            return "round_robin"

    def _select_least_loaded_engine(self, resource_requirement: Dict[str, float]) -> tuple:
        """选择负载最低的引擎"""
        min_load = float('inf')
        selected_engine = None

        for engine_name, usage in self.resource_usage.items():
            # 计算综合负载分数
            load_score = (usage.cpu_percent * 0.5 +
                        (usage.memory_mb / 500) * 0.3 +
                        usage.active_tasks * 0.2)

            # 考虑资源需求
            if resource_requirement.get("cpu", 0) > 0.3 and usage.cpu_percent > 50:
                continue

            if load_score < min_load:
                min_load = load_score
                selected_engine = engine_name

        if selected_engine is None:
            # 如果所有引擎都繁忙，返回注册表中第一个
            selected_engine = list(self.engine_registry.keys())[0]

        return selected_engine, "least_loaded"

    def _select_round_robin_engine(self) -> tuple:
        """轮询选择引擎"""
        # 基于时间选择
        idx = int(time.time()) % len(self.engine_registry)
        engine = list(self.engine_registry.keys())[idx]
        return engine, "round_robin"

    def _select_weighted_engine(self, priority: str) -> tuple:
        """加权选择引擎"""
        weights = self.config.get("priority_weights", {})
        priority_weight = weights.get(priority, 0.5)

        # 根据优先级权重选择
        candidates = []
        for engine_name, registry in self.engine_registry.items():
            engine_priority = registry.get("priority", "medium")
            engine_weight = weights.get(engine_priority, 0.5)

            # 高优先级任务优先选择高优先级引擎
            if priority_weight >= 0.8 and engine_weight >= 0.8:
                candidates.append((engine_name, engine_weight))
            elif priority_weight < 0.5 and engine_weight <= 0.5:
                candidates.append((engine_name, engine_weight))

        if candidates:
            # 随机选择一个
            import random
            return random.choice(candidates)

        # 默认返回第一个
        return list(self.engine_registry.keys())[0], "weighted"

    def _generate_decision_reason(self, target_engine: str, priority: str,
                                   resource_requirement: Dict[str, float]) -> str:
        """生成决策原因"""
        reasons = []

        if priority in ["critical", "high"]:
            reasons.append(f"高优先级任务")

        if resource_requirement.get("cpu", 0) > 0.3:
            reasons.append(f"高CPU需求")

        if resource_requirement.get("memory", 0) > 200:
            reasons.append(f"高内存需求")

        usage = self.resource_usage.get(target_engine)
        if usage:
            if usage.cpu_percent < 50:
                reasons.append(f"引擎负载低({usage.cpu_percent:.1f}%)")
            if usage.active_tasks == 0:
                reasons.append("引擎空闲")

        return "; ".join(reasons) if reasons else "默认调度"

    def balance(self) -> Dict[str, Any]:
        """执行负载均衡"""
        if not self._check_load_balance_needed():
            return {
                "status": "no_balance_needed",
                "message": "System load is balanced",
                "timestamp": datetime.now().isoformat()
            }

        # 获取高负载引擎
        high_load_engines = []
        for engine_name, usage in self.resource_usage.items():
            if usage.cpu_percent > 70 or usage.memory_mb > 400:
                high_load_engines.append((engine_name, usage))

        # 生成均衡建议
        suggestions = []
        for engine_name, usage in high_load_engines:
            # 建议降低优先级
            suggestions.append({
                "engine": engine_name,
                "action": "reduce_priority",
                "reason": f"CPU: {usage.cpu_percent:.1f}%, Memory: {usage.memory_mb:.1f}MB",
                "current_tasks": usage.active_tasks
            })

        # 记录均衡决策
        decision = LoadBalanceDecision(
            decision_id=f"bal_{int(time.time())}",
            task_id="system_balance",
            target_engine="system",
            strategy="adaptive",
            reason=f"Balanced {len(high_load_engines)} high-load engines"
        )
        self.decisions.append(decision)
        self._save_decisions()

        return {
            "status": "balanced",
            "balanced_count": len(high_load_engines),
            "suggestions": suggestions,
            "decision": asdict(decision),
            "timestamp": datetime.now().isoformat()
        }

    def analyze(self) -> Dict[str, Any]:
        """分析负载均衡效果"""
        if not self.decisions:
            return {
                "status": "no_data",
                "message": "No decisions to analyze",
                "timestamp": datetime.now().isoformat()
            }

        # 统计各引擎被选择次数
        engine_selections = defaultdict(int)
        strategy_usage = defaultdict(int)

        for decision in self.decisions:
            if decision.task_id != "system_balance":
                engine_selections[decision.target_engine] += 1
            strategy_usage[decision.strategy] += 1

        # 获取当前资源状态
        system_resources = self._get_system_resources()

        # 计算负载分布
        load_distribution = {}
        for engine_name, usage in self.resource_usage.items():
            load_distribution[engine_name] = {
                "cpu_percent": usage.cpu_percent,
                "memory_mb": usage.memory_mb,
                "active_tasks": usage.active_tasks,
                "avg_response_time": usage.avg_response_time,
                "load_score": usage.cpu_percent * 0.5 + (usage.memory_mb / 500) * 0.3 + usage.active_tasks * 0.2
            }

        return {
            "status": "ok",
            "total_decisions": len(self.decisions),
            "engine_selections": dict(engine_selections),
            "strategy_usage": dict(strategy_usage),
            "system_resources": system_resources,
            "load_distribution": load_distribution,
            "recommendations": self._generate_recommendations(load_distribution, engine_selections),
            "timestamp": datetime.now().isoformat()
        }

    def _generate_recommendations(self, load_distribution: Dict,
                                   engine_selections: Dict) -> List[Dict]:
        """生成优化建议"""
        recommendations = []

        # 找出负载最高的引擎
        high_load = [(name, data) for name, data in load_distribution.items()
                    if data["load_score"] > 50]

        if high_load:
            high_load.sort(key=lambda x: x[1]["load_score"], reverse=True)
            recommendations.append({
                "type": "high_load",
                "engines": [name for name, _ in high_load[:3]],
                "message": "Consider distributing load from high-load engines"
            })

        # 找出使用最少的引擎
        if engine_selections:
            min_used = min(engine_selections.values())
            underutilized = [name for name, count in engine_selections.items()
                           if count == min_used and count > 0]

            if underutilized:
                recommendations.append({
                    "type": "underutilized",
                    "engines": underutilized,
                    "message": "These engines are underutilized, consider increasing their usage"
                })

        # 检查系统资源
        system = self._get_system_resources()
        if system["cpu_percent"] > 80:
            recommendations.append({
                "type": "system_cpu",
                "message": f"System CPU is high ({system['cpu_percent']:.1f}%), consider reducing concurrent tasks"
            })

        return recommendations

    def history(self, limit: int = 20) -> Dict[str, Any]:
        """获取调度历史"""
        recent_tasks = self.task_history[-limit:] if self.task_history else []
        recent_decisions = self.decisions[-limit:] if self.decisions else []

        return {
            "status": "ok",
            "task_count": len(self.task_history),
            "decision_count": len(self.decisions),
            "recent_tasks": [asdict(t) for t in recent_tasks],
            "recent_decisions": [asdict(d) for d in recent_decisions],
            "timestamp": datetime.now().isoformat()
        }

    def get_status(self) -> Dict[str, Any]:
        """获取负载均衡器状态"""
        system_resources = self._get_system_resources()

        # 统计引擎状态
        total_engines = len(self.engine_registry)
        active_engines = sum(1 for u in self.resource_usage.values() if u.active_tasks > 0)
        high_load_engines = sum(1 for u in self.resource_usage.values()
                               if u.cpu_percent > 70 or u.memory_mb > 400)

        return {
            "status": "ok",
            "monitoring_enabled": self.config.get("monitoring_enabled", True),
            "default_strategy": self.config.get("default_strategy", "adaptive"),
            "system_resources": {
                "cpu_percent": system_resources["cpu_percent"],
                "memory_percent": system_resources["memory_percent"],
                "memory_available_mb": system_resources["memory_available_mb"]
            },
            "engine_stats": {
                "total": total_engines,
                "active": active_engines,
                "high_load": high_load_engines
            },
            "thresholds": self.config.get("thresholds", {}),
            "total_decisions": len(self.decisions),
            "total_tasks": len(self.task_history),
            "timestamp": datetime.now().isoformat()
        }

    def start_monitoring(self):
        """启动资源监控"""
        if self._monitoring:
            return {"status": "already_running"}

        self._monitoring = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()

        return {"status": "started", "message": "Monitoring started"}

    def stop_monitoring(self):
        """停止资源监控"""
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=2)

        return {"status": "stopped", "message": "Monitoring stopped"}

    def _monitor_loop(self):
        """监控循环"""
        interval = self.config.get("monitoring_interval", 10)

        while self._monitoring:
            try:
                self.monitor()
            except Exception:
                pass

            time.sleep(interval)


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print(__doc__)
        print("\n可用命令:")
        print("  status         - 查看负载均衡器状态")
        print("  monitor        - 监控引擎资源使用")
        print("  schedule       - 调度任务（需要参数）")
        print("  balance        - 执行负载均衡")
        print("  analyze        - 分析负载均衡效果")
        print("  history        - 查看调度历史")
        print("  start          - 启动自动监控")
        print("  stop           - 停止自动监控")
        sys.exit(1)

    command = sys.argv[1].lower()
    balancer = EngineLoadBalancer()

    if command == "status":
        result = balancer.get_status()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif command == "monitor":
        result = balancer.monitor()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif command == "schedule":
        # 解析参数: engine_name priority estimated_time
        engine_name = sys.argv[2] if len(sys.argv) > 2 else "engine_auto_optimizer"
        priority = sys.argv[3] if len(sys.argv) > 3 else "medium"
        estimated_time = float(sys.argv[4]) if len(sys.argv) > 4 else 1.0

        task_id = f"task_{int(time.time())}"
        result = balancer.schedule_task(task_id, engine_name, priority, estimated_time)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif command == "balance":
        result = balancer.balance()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif command == "analyze":
        result = balancer.analyze()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif command == "history":
        result = balancer.history()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif command == "start":
        result = balancer.start_monitoring()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif command == "stop":
        result = balancer.stop_monitoring()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"未知命令: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()