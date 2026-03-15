#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环多引擎协同智能调度深度优化引擎
Evolution Multi-Engine Collaboration Scheduling Optimizer

让系统能够智能调度多个进化引擎，实现更高效的资源利用和协同工作：
1. 任务智能分发（基于任务类型、引擎能力、当前负载）
2. 负载均衡优化（动态调整引擎执行权重）
3. 执行顺序动态调整（基于依赖关系和优先级）
4. 调度效率实时分析（监控调度效果并优化）
5. 跨引擎协同优化（识别并优化引擎间的协作模式）

集成到 do.py 支持关键词：
- 多引擎调度、引擎协同调度、智能调度、负载均衡
- 调度优化、任务分发、执行顺序、协同优化

Version: 1.0.0
"""

import os
import sys
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


@dataclass
class EngineCapability:
    """引擎能力描述"""
    name: str
    category: str  # execution, analysis, learning, optimization
    cpu_intensity: float  # 0-1
    memory_intensity: float  # 0-1
    typical_duration: float  # seconds
    dependencies: List[str] = field(default_factory=list)
    success_rate: float = 0.95


@dataclass
class SchedulingTask:
    """调度任务"""
    id: str
    engine_name: str
    priority: int  # 1-10
    estimated_duration: float
    created_at: str
    dependencies: List[str] = field(default_factory=list)


@dataclass
class SchedulingMetrics:
    """调度指标"""
    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    avg_execution_time: float = 0.0
    load_balance_score: float = 0.0
    efficiency_score: float = 0.0
    last_optimization: Optional[str] = None


class MultiEngineCollaborationSchedulingOptimizer:
    """多引擎协同智能调度深度优化引擎"""

    def __init__(self):
        self.name = "Multi-Engine Collaboration Scheduling Optimizer"
        self.version = "1.0.0"

        self.state_file = os.path.join(project_root, "runtime", "state", "scheduling_optimizer_state.json")
        self.metrics_file = os.path.join(project_root, "runtime", "state", "scheduling_metrics.json")
        self.history_file = os.path.join(project_root, "runtime", "state", "scheduling_history.json")

        # 引擎能力注册表
        self.engine_registry = self._load_engine_registry()

        # 调度状态
        self.scheduling_state = self._load_state()

        # 调度指标
        self.metrics = self._load_metrics()

        # 调度历史
        self.history = self._load_history()

    def _load_engine_registry(self) -> Dict[str, EngineCapability]:
        """加载引擎能力注册表"""
        # 基于已有进化引擎构建能力图谱
        registry = {
            "evolution_strategy_engine": EngineCapability(
                name="evolution_strategy_engine",
                category="analysis",
                cpu_intensity=0.3,
                memory_intensity=0.2,
                typical_duration=30.0,
                dependencies=[],
                success_rate=0.95
            ),
            "evolution_execution_engine": EngineCapability(
                name="evolution_execution_engine",
                category="execution",
                cpu_intensity=0.5,
                memory_intensity=0.4,
                typical_duration=60.0,
                dependencies=["evolution_strategy_engine"],
                success_rate=0.90
            ),
            "evolution_learning_engine": EngineCapability(
                name="evolution_learning_engine",
                category="learning",
                cpu_intensity=0.4,
                memory_intensity=0.5,
                typical_duration=45.0,
                dependencies=[],
                success_rate=0.92
            ),
            "evolution_optimizer": EngineCapability(
                name="evolution_optimizer",
                category="optimization",
                cpu_intensity=0.6,
                memory_intensity=0.5,
                typical_duration=40.0,
                dependencies=["evolution_execution_engine"],
                success_rate=0.88
            ),
            "evolution_meta_evolution_enhancement_engine": EngineCapability(
                name="evolution_meta_evolution_enhancement_engine",
                category="analysis",
                cpu_intensity=0.35,
                memory_intensity=0.3,
                typical_duration=35.0,
                dependencies=[],
                success_rate=0.93
            ),
            "evolution_self_evolution_enhancement_engine": EngineCapability(
                name="evolution_self_evolution_enhancement_engine",
                category="optimization",
                cpu_intensity=0.45,
                memory_intensity=0.4,
                typical_duration=50.0,
                dependencies=["evolution_meta_evolution_enhancement_engine"],
                success_rate=0.91
            ),
            "evolution_knowledge_graph_reasoning": EngineCapability(
                name="evolution_knowledge_graph_reasoning",
                category="analysis",
                cpu_intensity=0.4,
                memory_intensity=0.6,
                typical_duration=55.0,
                dependencies=[],
                success_rate=0.89
            ),
            "evolution_health_monitor": EngineCapability(
                name="evolution_health_monitor",
                category="analysis",
                cpu_intensity=0.2,
                memory_intensity=0.15,
                typical_duration=15.0,
                dependencies=[],
                success_rate=0.97
            ),
        }
        return registry

    def _load_state(self) -> Dict[str, Any]:
        """加载调度状态"""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "active_tasks": [],
            "queue": [],
            "engine_loads": {},
            "last_scheduling_time": None,
            "optimization_count": 0
        }

    def _save_state(self):
        """保存调度状态"""
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(self.scheduling_state, f, ensure_ascii=False, indent=2)

    def _load_metrics(self) -> SchedulingMetrics:
        """加载调度指标"""
        if os.path.exists(self.metrics_file):
            try:
                with open(self.metrics_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return SchedulingMetrics(**data)
            except Exception:
                pass
        return SchedulingMetrics()

    def _save_metrics(self):
        """保存调度指标"""
        os.makedirs(os.path.dirname(self.metrics_file), exist_ok=True)
        with open(self.metrics_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(self.metrics), f, ensure_ascii=False, indent=2)

    def _load_history(self) -> List[Dict]:
        """加载调度历史"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return []

    def _save_history(self):
        """保存调度历史"""
        os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
        # 只保留最近100条历史
        if len(self.history) > 100:
            self.history = self.history[-100:]
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)

    def register_engine(self, engine_name: str, capability: EngineCapability):
        """注册新引擎"""
        self.engine_registry[engine_name] = capability

    def submit_task(self, task: SchedulingTask) -> Dict[str, Any]:
        """提交任务"""
        # 检查依赖是否满足
        if task.dependencies:
            for dep_id in task.dependencies:
                if not self._is_dependency_met(dep_id):
                    return {
                        "status": "pending",
                        "message": f"任务依赖未满足: {dep_id}",
                        "task_id": task.id
                    }

        # 添加到队列
        self.scheduling_state["queue"].append({
            "id": task.id,
            "engine_name": task.engine_name,
            "priority": task.priority,
            "estimated_duration": task.estimated_duration,
            "created_at": task.created_at,
            "status": "queued"
        })
        self._save_state()

        return {
            "status": "queued",
            "message": f"任务 {task.id} 已添加到调度队列",
            "task_id": task.id
        }

    def _is_dependency_met(self, task_id: str) -> bool:
        """检查依赖是否满足"""
        for task in self.scheduling_state.get("active_tasks", []):
            if task.get("id") == task_id and task.get("status") == "completed":
                return True
        return False

    def intelligent_task_dispatch(self, available_engines: List[str] = None) -> Dict[str, Any]:
        """智能任务分发"""
        if available_engines is None:
            available_engines = list(self.engine_registry.keys())

        queue = self.scheduling_state.get("queue", [])
        if not queue:
            return {"status": "empty", "message": "调度队列为空"}

        # 按优先级排序
        queue.sort(key=lambda x: x.get("priority", 5), reverse=True)

        # 选择最佳引擎
        dispatched_tasks = []
        for task in queue[:5]:  # 每次最多分发5个任务
            engine_name = self._select_best_engine(task, available_engines)
            if engine_name:
                task["status"] = "dispatched"
                task["assigned_engine"] = engine_name
                dispatched_tasks.append({
                    "task_id": task["id"],
                    "engine": engine_name,
                    "priority": task["priority"]
                })

                # 更新引擎负载
                if engine_name not in self.scheduling_state.get("engine_loads", {}):
                    self.scheduling_state["engine_loads"][engine_name] = 0
                self.scheduling_state["engine_loads"][engine_name] += 1

        self.scheduling_state["last_scheduling_time"] = datetime.now().isoformat()
        self._save_state()

        return {
            "status": "success",
            "dispatched_tasks": dispatched_tasks,
            "queue_remaining": len(queue) - len(dispatched_tasks)
        }

    def _select_best_engine(self, task: Dict, available_engines: List[str]) -> Optional[str]:
        """选择最佳引擎"""
        engine_name = task.get("engine_name")

        # 如果指定了引擎且可用
        if engine_name in available_engines:
            current_load = self.scheduling_state.get("engine_loads", {}).get(engine_name, 0)
            # 如果引擎负载不高，使用它
            if current_load < 3:
                return engine_name

        # 否则选择负载最低的合适引擎
        best_engine = None
        min_load = float('inf')

        for eng in available_engines:
            if eng in self.engine_registry:
                capability = self.engine_registry[eng]
                # 检查任务类型是否匹配
                if capability.category in ["execution", "optimization"]:
                    load = self.scheduling_state.get("engine_loads", {}).get(eng, 0)
                    if load < min_load:
                        min_load = load
                        best_engine = eng

        return best_engine

    def optimize_load_balance(self) -> Dict[str, Any]:
        """负载均衡优化"""
        engine_loads = self.scheduling_state.get("engine_loads", {})

        if not engine_loads:
            return {"status": "no_data", "message": "无负载数据"}

        # 计算负载标准差
        loads = list(engine_loads.values())
        avg_load = sum(loads) / len(loads) if loads else 0

        if avg_load == 0:
            return {"status": "balanced", "message": "所有引擎空闲"}

        # 计算均衡度（0-1，越高越好）
        variance = sum((x - avg_load) ** 2 for x in loads) / len(loads)
        std_dev = variance ** 0.5
        balance_score = max(0, 1 - (std_dev / (avg_load + 0.1)))

        # 生成优化建议
        optimization_actions = []
        if balance_score < 0.7:
            # 需要重新平衡
            high_load_engines = [e for e, l in engine_loads.items() if l > avg_load * 1.5]
            low_load_engines = [e for e, l in engine_loads.items() if l < avg_load * 0.5]

            if high_load_engines:
                optimization_actions.append(f"考虑将任务从 {', '.join(high_load_engines[:2])} 转移")
            if low_load_engines:
                optimization_actions.append(f"可增加 {', '.join(low_load_engines[:2])} 的任务分配")

        self.metrics.load_balance_score = balance_score
        self.scheduling_state["optimization_count"] = self.scheduling_state.get("optimization_count", 0) + 1
        self.metrics.last_optimization = datetime.now().isoformat()
        self._save_state()
        self._save_metrics()

        return {
            "status": "success",
            "balance_score": balance_score,
            "avg_load": avg_load,
            "engine_loads": engine_loads,
            "optimization_actions": optimization_actions
        }

    def analyze_execution_order(self, task_sequence: List[str]) -> Dict[str, Any]:
        """分析执行顺序优化"""
        if not task_sequence:
            return {"status": "empty", "message": "任务序列为空"}

        # 构建依赖图
        dependency_graph = {}
        for task_id in task_sequence:
            for engine_name, capability in self.engine_registry.items():
                if task_id.startswith(engine_name.split('_')[0]):
                    dependency_graph[task_id] = capability.dependencies
                    break

        # 检查是否有循环依赖
        has_cycle = self._check_circular_dependency(task_sequence, dependency_graph)

        # 优化执行顺序（拓扑排序）
        optimized_order = self._topological_sort(task_sequence, dependency_graph)

        return {
            "status": "success",
            "original_order": task_sequence,
            "optimized_order": optimized_order,
            "has_circular_dependency": has_cycle,
            "optimization_potential": len(task_sequence) - len(optimized_order) if optimized_order else 0
        }

    def _check_circular_dependency(self, tasks: List[str], graph: Dict) -> bool:
        """检查循环依赖"""
        visited = set()
        rec_stack = set()

        def dfs(task):
            visited.add(task)
            rec_stack.add(task)

            for dep in graph.get(task, []):
                if dep not in visited:
                    if dfs(dep):
                        return True
                elif dep in rec_stack:
                    return True

            rec_stack.remove(task)
            return False

        for task in tasks:
            if task not in visited:
                if dfs(task):
                    return True
        return False

    def _topological_sort(self, tasks: List[str], graph: Dict) -> List[str]:
        """拓扑排序"""
        in_degree = {task: 0 for task in tasks}
        for task in tasks:
            for dep in graph.get(task, []):
                if dep in in_degree:
                    in_degree[task] += 1

        queue = [task for task, degree in in_degree.items() if degree == 0]
        result = []

        while queue:
            task = queue.pop(0)
            result.append(task)

            for next_task in tasks:
                if task in graph.get(next_task, []):
                    in_degree[next_task] -= 1
                    if in_degree[next_task] == 0:
                        queue.append(next_task)

        return result

    def calculate_efficiency_score(self) -> Dict[str, Any]:
        """计算调度效率分数"""
        total_tasks = self.metrics.total_tasks
        if total_tasks == 0:
            return {"status": "no_data", "efficiency_score": 0.0}

        # 效率分数 = 完成率 * 0.4 + 成功率 * 0.3 + 均衡度 * 0.3
        completion_rate = self.metrics.completed_tasks / total_tasks if total_tasks > 0 else 0
        success_rate = 1 - (self.metrics.failed_tasks / total_tasks) if total_tasks > 0 else 0
        balance_score = self.metrics.load_balance_score

        efficiency_score = (
            completion_rate * 0.4 +
            success_rate * 0.3 +
            balance_score * 0.3
        )

        self.metrics.efficiency_score = efficiency_score
        self._save_metrics()

        return {
            "status": "success",
            "efficiency_score": efficiency_score,
            "completion_rate": completion_rate,
            "success_rate": success_rate,
            "balance_score": balance_score
        }

    def get_status(self) -> Dict[str, Any]:
        """获取调度器状态"""
        return {
            "status": "success",
            "engine_count": len(self.engine_registry),
            "queue_length": len(self.scheduling_state.get("queue", [])),
            "active_tasks": len(self.scheduling_state.get("active_tasks", [])),
            "engine_loads": self.scheduling_state.get("engine_loads", {}),
            "total_tasks": self.metrics.total_tasks,
            "completed_tasks": self.metrics.completed_tasks,
            "load_balance_score": self.metrics.load_balance_score,
            "efficiency_score": self.metrics.efficiency_score,
            "last_optimization": self.metrics.last_optimization
        }

    def get_cockpit_data(self) -> Dict[str, Any]:
        """获取驾驶舱数据"""
        return {
            "name": self.name,
            "version": self.version,
            "status": self.get_status(),
            "efficiency_analysis": self.calculate_efficiency_score(),
            "load_balance": self.optimize_load_balance()
        }


# 全局引擎实例
_engine = None

def get_engine() -> MultiEngineCollaborationSchedulingOptimizer:
    """获取引擎实例"""
    global _engine
    if _engine is None:
        _engine = MultiEngineCollaborationSchedulingOptimizer()
    return _engine


def handle_command(args: List[str]) -> Dict[str, Any]:
    """处理命令"""
    engine = get_engine()

    if not args:
        return {"status": "error", "message": "需要子命令"}

    subcommand = args[0]

    if subcommand == "status":
        return engine.get_status()

    elif subcommand == "dispatch" or subcommand == "分发":
        result = engine.intelligent_task_dispatch()
        return result

    elif subcommand == "optimize" or subcommand == "优化":
        return engine.optimize_load_balance()

    elif subcommand == "efficiency" or subcommand == "效率":
        return engine.calculate_efficiency_score()

    elif subcommand == "order" or subcommand == "顺序":
        if len(args) < 2:
            return {"status": "error", "message": "需要任务序列"}
        task_sequence = args[1].split(',')
        return engine.analyze_execution_order(task_sequence)

    elif subcommand == "cockpit" or subcommand == "驾驶舱":
        return engine.get_cockpit_data()

    else:
        return {
            "status": "error",
            "message": f"未知命令: {subcommand}",
            "available_commands": ["status", "dispatch", "optimize", "efficiency", "order", "cockpit"]
        }


# 需要导入 dataclass 的 asdict
from dataclasses import asdict


if __name__ == "__main__":
    import sys
    result = handle_command(sys.argv[1:] if len(sys.argv) > 1 else [])
    print(json.dumps(result, ensure_ascii=False, indent=2))