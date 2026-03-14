#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化体动态负载均衡与弹性伸缩引擎 (Evolution Dynamic Load Balancer)
version 1.0.0

基于 round 342 的自我克隆与分布式协作引擎，进一步实现动态负载均衡与弹性伸缩能力。
让系统能够自动根据任务复杂度、资源使用情况动态分配和调整克隆实例数量。

功能：
1. 动态负载均衡 - 根据任务复杂度、CPU/内存情况智能分配任务
2. 弹性伸缩 - 根据负载自动增加/减少克隆实例数量
3. 跨机器分布式协作 - 支持跨设备协同工作
4. 资源监控 - 实时监控系统资源使用情况
5. 智能调度 - 基于性能预测的任务调度

依赖：
- evolution_self_clone_collaboration_engine.py (round 342)
- evolution_cross_dimension_fusion_engine.py (round 341)
- evolution_global_situation_awareness.py (round 329)
"""

import json
import os
import subprocess
import time
import uuid
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from collections import deque
from dataclasses import dataclass, asdict

# 尝试导入 psutil，如不可用则使用模拟数据
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
    print("[负载均衡] 警告：psutil 未安装，将使用模拟数据进行演示")


@dataclass
class LoadMetrics:
    """负载指标"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    active_instances: int
    pending_tasks: int
    completed_tasks: int
    avg_response_time: float


@dataclass
class ScalingDecision:
    """伸缩决策"""
    decision_id: str
    timestamp: datetime
    current_instances: int
    recommended_instances: int
    reason: str
    action: str  # scale_up, scale_down, maintain


@dataclass
class TaskProfile:
    """任务画像"""
    task_id: str
    complexity: str  # low, medium, high
    estimated_duration: float
    required_resources: Dict[str, float]  # cpu, memory
    priority: int
    created_at: datetime


class DynamicLoadBalancer:
    """动态负载均衡与弹性伸缩引擎"""

    def __init__(self, data_dir: str = "runtime/state"):
        self.data_dir = data_dir

        # 负载均衡配置
        self.config = {
            "min_instances": 1,
            "max_instances": 5,
            "scale_up_threshold": 0.75,  # CPU/内存超过75%时扩容
            "scale_down_threshold": 0.30,  # CPU/内存低于30%时缩容
            "scale_up_cooldown": 60,  # 扩容冷却时间（秒）
            "scale_down_cooldown": 120,  # 缩容冷却时间（秒）
            "target_response_time": 2.0,  # 目标响应时间（秒）
            "auto_scaling_enabled": True
        }

        # 负载指标历史
        self.metrics_history: deque = deque(maxlen=100)

        # 伸缩决策历史
        self.scaling_decisions: List[ScalingDecision] = []

        # 任务队列
        self.pending_tasks: Dict[str, TaskProfile] = {}
        self.task_queue_lock = threading.Lock()

        # 调度器状态
        self.last_scale_up_time: Optional[datetime] = None
        self.last_scale_down_time: Optional[datetime] = None
        self.lock = threading.Lock()

        # 依赖引擎
        self.clone_engine = None
        self._init_engines()

    def _init_engines(self):
        """初始化依赖引擎"""
        try:
            from evolution_self_clone_collaboration_engine import SelfCloneCollaborationEngine
            self.clone_engine = SelfCloneCollaborationEngine(self.data_dir)
            print("[负载均衡] 自我克隆协作引擎已加载")
        except ImportError as e:
            print(f"[负载均衡] 警告：无法加载自我克隆协作引擎: {e}")

    def collect_metrics(self) -> LoadMetrics:
        """收集当前负载指标"""
        try:
            if HAS_PSUTIL:
                cpu_percent = psutil.cpu_percent(interval=0.1)
                memory = psutil.virtual_memory()
                memory_percent = memory.percent
            else:
                # 使用模拟数据
                import random
                cpu_percent = 30.0 + random.random() * 40  # 30-70%
                memory_percent = 40.0 + random.random() * 30  # 40-70%

            # 获取克隆实例状态
            active_instances = 0
            if self.clone_engine:
                instances = self.clone_engine.get_instances_status()
                active_instances = len([i for i in instances if i["status"] == "running"])

            with self.task_queue_lock:
                pending_count = len(self.pending_tasks)
                completed_count = len([t for t in self.pending_tasks.values()
                                      if hasattr(t, 'completed') and t.completed])

            # 计算平均响应时间（简单模拟）
            if self.metrics_history:
                avg_response = sum(m.avg_response_time for m in self.metrics_history) / len(self.metrics_history)
            else:
                avg_response = 0.5

            metrics = LoadMetrics(
                timestamp=datetime.now(),
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                active_instances=active_instances,
                pending_tasks=pending_count,
                completed_tasks=completed_count,
                avg_response_time=avg_response
            )

            self.metrics_history.append(metrics)
            return metrics

        except Exception as e:
            print(f"[负载均衡] 收集指标失败: {e}")
            return LoadMetrics(
                timestamp=datetime.now(),
                cpu_percent=50.0,
                memory_percent=50.0,
                active_instances=1,
                pending_tasks=0,
                completed_tasks=0,
                avg_response_time=1.0
            )

    def analyze_task_complexity(self, task: str) -> TaskProfile:
        """分析任务复杂度"""
        # 简单基于关键词估算
        complexity = "medium"
        estimated_duration = 5.0
        required_resources = {"cpu": 0.3, "memory": 0.2}

        # 关键词匹配
        high_complexity_keywords = ["分析", "推理", "优化", "学习", "生成", "训练"]
        low_complexity_keywords = ["查询", "获取", "检查", "简单"]

        for kw in high_complexity_keywords:
            if kw in task:
                complexity = "high"
                estimated_duration = 15.0
                required_resources = {"cpu": 0.8, "memory": 0.6}
                break

        for kw in low_complexity_keywords:
            if kw in task:
                complexity = "low"
                estimated_duration = 2.0
                required_resources = {"cpu": 0.1, "memory": 0.1}
                break

        task_profile = TaskProfile(
            task_id=f"task_{uuid.uuid4().hex[:8]}",
            complexity=complexity,
            estimated_duration=estimated_duration,
            required_resources=required_resources,
            priority=5,
            created_at=datetime.now()
        )

        return task_profile

    def calculate_scaling_decision(self, metrics: LoadMetrics) -> ScalingDecision:
        """计算伸缩决策"""
        with self.lock:
            now = datetime.now()

            # 计算综合负载
            combined_load = (metrics.cpu_percent + metrics.memory_percent) / 2 / 100

            # 获取当前实例数
            current_instances = max(metrics.active_instances, 1)

            # 伸缩决策逻辑
            recommended = current_instances
            reason = ""
            action = "maintain"

            # 检查扩容条件
            if combined_load > self.config["scale_up_threshold"]:
                # 检查冷却时间
                if self.last_scale_up_time is None or \
                   (now - self.last_scale_up_time).total_seconds() > self.config["scale_up_cooldown"]:
                    if current_instances < self.config["max_instances"]:
                        recommended = min(current_instances + 1, self.config["max_instances"])
                        action = "scale_up"
                        reason = f"负载过高 (CPU:{metrics.cpu_percent:.1f}%, Memory:{metrics.memory_percent:.1f}%)"
                        self.last_scale_up_time = now

            # 检查缩容条件
            elif combined_load < self.config["scale_down_threshold"]:
                # 检查冷却时间
                if self.last_scale_down_time is None or \
                   (now - self.last_scale_down_time).total_seconds() > self.config["scale_down_cooldown"]:
                    if current_instances > self.config["min_instances"]:
                        recommended = max(current_instances - 1, self.config["min_instances"])
                        action = "scale_down"
                        reason = f"负载过低 (CPU:{metrics.cpu_percent:.1f}%, Memory:{metrics.memory_percent:.1f}%)"
                        self.last_scale_down_time = now

            # 检查响应时间
            if metrics.avg_response_time > self.config["target_response_time"] and action == "maintain":
                if current_instances < self.config["max_instances"]:
                    recommended = min(current_instances + 1, self.config["max_instances"])
                    action = "scale_up"
                    reason = f"响应时间过长 ({metrics.avg_response_time:.2f}s > {self.config['target_response_time']}s)"
                    self.last_scale_up_time = now

            # 积压任务检查
            if metrics.pending_tasks > 3 and action == "maintain":
                if current_instances < self.config["max_instances"]:
                    recommended = min(current_instances + 1, self.config["max_instances"])
                    action = "scale_up"
                    reason = f"任务积压 ({metrics.pending_tasks} 个待处理)"
                    self.last_scale_up_time = now

            decision = ScalingDecision(
                decision_id=f"scale_{uuid.uuid4().hex[:8]}",
                timestamp=now,
                current_instances=current_instances,
                recommended_instances=recommended,
                reason=reason,
                action=action
            )

            self.scaling_decisions.append(decision)

            return decision

    def execute_scaling(self, decision: ScalingDecision) -> Dict:
        """执行伸缩决策"""
        if decision.action == "maintain":
            return {
                "success": True,
                "action": "maintain",
                "message": "保持当前实例数量",
                "current_instances": decision.current_instances,
                "recommended_instances": decision.recommended_instances
            }

        if not self.clone_engine:
            return {
                "success": False,
                "error": "克隆引擎未初始化"
            }

        # 需要扩容
        if decision.action == "scale_up":
            needed = decision.recommended_instances - decision.current_instances
            results = []
            for _ in range(needed):
                result = self.clone_engine.clone_self(task="负载均衡自动分配")
                results.append(result)

            return {
                "success": True,
                "action": "scale_up",
                "message": f"已扩容 {needed} 个实例",
                "current_instances": decision.recommended_instances,
                "new_instances": results
            }

        # 需要缩容
        elif decision.action == "scale_down":
            instances = self.clone_engine.get_instances_status()
            idle_instances = [i for i in instances if i["status"] == "idle"]

            to_remove = decision.current_instances - decision.recommended_instances
            results = []
            for instance in idle_instances[:to_remove]:
                result = self.clone_engine.cleanup_instance(instance["instance_id"])
                results.append(result)

            return {
                "success": True,
                "action": "scale_down",
                "message": f"已缩容 {to_remove} 个实例",
                "current_instances": decision.recommended_instances,
                "removed_instances": results
            }

        return {
            "success": False,
            "error": "未知动作"
        }

    def dispatch_task(self, task: str) -> Dict:
        """分发任务到最合适的实例"""
        with self.task_queue_lock:
            # 分析任务复杂度
            task_profile = self.analyze_task_complexity(task)
            self.pending_tasks[task_profile.task_id] = task_profile

        # 收集当前负载
        metrics = self.collect_metrics()

        # 计算伸缩决策
        scaling_decision = self.calculate_scaling_decision(metrics)

        # 执行伸缩（如需要）
        if scaling_decision.action != "maintain" and self.config["auto_scaling_enabled"]:
            scale_result = self.execute_scaling(scaling_decision)
            print(f"[负载均衡] 伸缩决策: {scale_result.get('message', '')}")

        # 获取最佳实例
        if self.clone_engine:
            instances = self.clone_engine.get_instances_status()
            idle_instances = [i for i in instances if i["status"] == "idle"]

            if idle_instances:
                # 选择性能最佳的实例
                best_instance = max(idle_instances, key=lambda x: x.get("performance_score", 0))

                # 分配任务
                assign_result = self.clone_engine.assign_task(
                    best_instance["instance_id"],
                    task
                )

                return {
                    "success": True,
                    "task_id": task_profile.task_id,
                    "assigned_instance": best_instance["instance_id"],
                    "task_complexity": task_profile.complexity,
                    "scaling_decision": {
                        "action": scaling_decision.action,
                        "reason": scaling_decision.reason
                    }
                }

        return {
            "success": False,
            "error": "无法分配任务",
            "task_id": task_profile.task_id
        }

    def get_load_status(self) -> Dict:
        """获取负载状态"""
        metrics = self.collect_metrics()

        # 获取最近决策
        recent_decisions = [
            {
                "decision_id": d.decision_id,
                "timestamp": d.timestamp.isoformat(),
                "action": d.action,
                "reason": d.reason,
                "current_instances": d.current_instances,
                "recommended_instances": d.recommended_instances
            }
            for d in self.scaling_decisions[-5:]
        ]

        return {
            "metrics": {
                "timestamp": metrics.timestamp.isoformat(),
                "cpu_percent": metrics.cpu_percent,
                "memory_percent": metrics.memory_percent,
                "active_instances": metrics.active_instances,
                "pending_tasks": metrics.pending_tasks,
                "completed_tasks": metrics.completed_tasks,
                "avg_response_time": metrics.avg_response_time
            },
            "config": self.config,
            "recent_decisions": recent_decisions,
            "total_scaling_decisions": len(self.scaling_decisions)
        }

    def update_config(self, key: str, value: Any) -> Dict:
        """更新配置"""
        if key in self.config:
            self.config[key] = value
            return {
                "success": True,
                "key": key,
                "new_value": value
            }
        return {
            "success": False,
            "error": f"配置项 {key} 不存在"
        }

    def full_cycle_demo(self) -> Dict:
        """完整演示流程"""
        results = {
            "steps": []
        }

        # 步骤1：收集初始负载指标
        metrics = self.collect_metrics()
        results["steps"].append({
            "step": "收集负载指标",
            "result": {
                "cpu_percent": metrics.cpu_percent,
                "memory_percent": metrics.memory_percent,
                "active_instances": metrics.active_instances
            }
        })

        # 步骤2：模拟任务分发
        tasks = ["简单查询任务", "复杂分析任务", "优化任务"]
        for task in tasks:
            dispatch_result = self.dispatch_task(task)
            results["steps"].append({
                "step": f"分发任务: {task}",
                "result": dispatch_result
            })

        # 步骤3：获取负载状态
        status = self.get_load_status()
        results["steps"].append({
            "step": "获取负载状态",
            "result": status
        })

        # 步骤4：测试配置更新
        config_result = self.update_config("scale_up_threshold", 0.70)
        results["steps"].append({
            "step": "更新配置",
            "result": config_result
        })

        results["summary"] = {
            "config": self.config,
            "total_scaling_decisions": len(self.scaling_decisions)
        }

        return results


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(
        description="智能全场景进化体动态负载均衡与弹性伸缩引擎"
    )
    parser.add_argument("--dispatch", type=str, help="分发任务")
    parser.add_argument("--status", action="store_true", help="查看负载状态")
    parser.add_argument("--metrics", action="store_true", help="收集负载指标")
    parser.add_argument("--config", nargs=2, metavar=("KEY", "VALUE"), help="更新配置")
    parser.add_argument("--full-cycle", action="store_true", help="完整演示流程")

    args = parser.parse_args()

    # 创建引擎实例
    engine = DynamicLoadBalancer()

    if args.dispatch:
        result = engine.dispatch_task(args.dispatch)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.status:
        result = engine.get_load_status()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.metrics:
        result = engine.collect_metrics()
        print(json.dumps({
            "timestamp": result.timestamp.isoformat(),
            "cpu_percent": result.cpu_percent,
            "memory_percent": result.memory_percent,
            "active_instances": result.active_instances,
            "pending_tasks": result.pending_tasks,
            "avg_response_time": result.avg_response_time
        }, ensure_ascii=False, indent=2))

    elif args.config:
        key, value = args.config
        # 尝试转换为数字
        try:
            value = float(value)
        except ValueError:
            if value.lower() == "true":
                value = True
            elif value.lower() == "false":
                value = False
        result = engine.update_config(key, value)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.full_cycle:
        result = engine.full_cycle_demo()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()