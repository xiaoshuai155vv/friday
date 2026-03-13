#!/usr/bin/env python3
"""
自适应优先级调整引擎
让进化环能够根据实时系统负载和用户需求变化动态调整进化任务优先级

功能：
1. 实时监控系统负载（CPU、内存、磁盘）
2. 分析用户行为和需求变化
3. 动态调整进化任务优先级
4. 实现智能资源分配
5. 集成到 do.py 支持关键词触发
"""

import os
import json
import sys
import time
import threading
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from collections import deque
from dataclasses import dataclass, asdict

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
    print("警告: psutil 模块未安装，系统监控功能将受限")

# 添加 scripts 目录到路径
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPTS_DIR)

# 状态和日志目录
PROJECT_DIR = os.path.dirname(SCRIPTS_DIR)  # 项目根目录
RUNTIME_DIR = os.path.join(PROJECT_DIR, "runtime")
STATE_DIR = os.path.join(RUNTIME_DIR, "state")
LOGS_DIR = os.path.join(RUNTIME_DIR, "logs")


@dataclass
class SystemMetrics:
    """系统指标"""
    timestamp: str
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    active_processes: int
    network_sent: int
    network_recv: int


@dataclass
class PriorityTask:
    """优先级任务"""
    task_id: str
    task_name: str
    base_priority: int  # 1-10, 10最高
    current_priority: int
    last_adjusted: str
    adjustment_reason: str


class SystemMonitor:
    """系统监控器"""

    def __init__(self, history_size: int = 60):
        self.history_size = history_size
        self.metrics_history: deque = deque(maxlen=history_size)
        self.monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None

    def get_current_metrics(self) -> SystemMetrics:
        """获取当前系统指标"""
        if not HAS_PSUTIL:
            # 没有 psutil 时返回默认值
            return SystemMetrics(
                timestamp=datetime.now().isoformat(),
                cpu_percent=30.0,
                memory_percent=50.0,
                disk_percent=60.0,
                active_processes=100,
                network_sent=0,
                network_recv=0
            )

        cpu = psutil.cpu_percent(interval=0.5)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        # 尝试获取网络IO
        try:
            net_io = psutil.net_io_counters()
            net_sent = net_io.bytes_sent if net_io else 0
            net_recv = net_io.bytes_recv if net_io else 0
        except Exception:
            net_sent = 0
            net_recv = 0

        # 活跃进程数
        try:
            active_processes = len(psutil.pids())
        except Exception:
            active_processes = 0

        return SystemMetrics(
            timestamp=datetime.now().isoformat(),
            cpu_percent=cpu,
            memory_percent=memory.percent,
            disk_percent=disk.percent,
            active_processes=active_processes,
            network_sent=net_sent,
            network_recv=net_recv
        )

    def start_monitoring(self, interval: float = 5.0):
        """开始监控"""
        if self.monitoring:
            return

        self.monitoring = True

        def monitor_loop():
            while self.monitoring:
                metrics = self.get_current_metrics()
                self.metrics_history.append(metrics)
                time.sleep(interval)

        self.monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitor_thread.start()

    def stop_monitoring(self):
        """停止监控"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)

    def get_load_level(self) -> str:
        """获取系统负载等级"""
        if not self.metrics_history:
            return "unknown"

        recent = list(self.metrics_history)[-5:]  # 最近5个样本
        avg_cpu = sum(m.cpu_percent for m in recent) / len(recent)
        avg_memory = sum(m.memory_percent for m in recent) / len(recent)

        # 计算综合负载分数
        load_score = (avg_cpu * 0.5) + (avg_memory * 0.5)

        if load_score < 30:
            return "low"
        elif load_score < 60:
            return "normal"
        elif load_score < 80:
            return "high"
        else:
            return "critical"

    def get_metrics_summary(self) -> Dict[str, Any]:
        """获取指标摘要"""
        if not self.metrics_history:
            return {"error": "No metrics available"}

        metrics_list = list(self.metrics_history)

        return {
            "current": asdict(metrics_list[-1]) if metrics_list else None,
            "average_cpu": sum(m.cpu_percent for m in metrics_list) / len(metrics_list),
            "average_memory": sum(m.memory_percent for m in metrics_list) / len(metrics_list),
            "average_disk": sum(m.disk_percent for m in metrics_list) / len(metrics_list),
            "max_cpu": max(m.cpu_percent for m in metrics_list),
            "max_memory": max(m.memory_percent for m in metrics_list),
            "load_level": self.get_load_level(),
            "sample_count": len(metrics_list)
        }


class UserBehaviorAnalyzer:
    """用户行为分析器"""

    def __init__(self):
        self.recent_interactions: deque = deque(maxlen=20)
        self.interaction_history: List[Dict[str, Any]] = []

    def record_interaction(self, interaction_type: str, content: str, timestamp: str = None):
        """记录用户交互"""
        if timestamp is None:
            timestamp = datetime.now().isoformat()

        interaction = {
            "type": interaction_type,
            "content": content,
            "timestamp": timestamp
        }

        self.recent_interactions.append(interaction)
        self.interaction_history.append(interaction)

    def get_current_demand_level(self) -> int:
        """
        获取当前用户需求等级 (1-10)
        基于最近交互频率和类型
        """
        if not self.recent_interactions:
            return 5  # 默认中等

        # 计算最近5分钟内的交互次数
        now = datetime.now()
        recent_count = 0

        for interaction in self.recent_interactions:
            try:
                # 尝试解析时间戳
                ts = datetime.fromisoformat(interaction["timestamp"])
                if (now - ts).total_seconds() < 300:  # 5分钟
                    recent_count += 1
            except Exception:
                pass

        # 根据交互频率计算需求等级
        if recent_count >= 10:
            return 10  # 非常高
        elif recent_count >= 7:
            return 8   # 高
        elif recent_count >= 4:
            return 6   # 中高
        elif recent_count >= 2:
            return 5   # 中
        elif recent_count >= 1:
            return 3   # 低
        else:
            return 2   # 很低

    def get_interaction_summary(self) -> Dict[str, Any]:
        """获取交互摘要"""
        return {
            "recent_count": len(self.recent_interactions),
            "demand_level": self.get_current_demand_level(),
            "interaction_types": list(set(i["type"] for i in self.recent_interactions)),
            "last_interaction": self.recent_interactions[-1] if self.recent_interactions else None
        }


class PriorityManager:
    """优先级管理器"""

    def __init__(self):
        self.tasks: Dict[str, PriorityTask] = {}
        self.adjustment_history: List[Dict[str, Any]] = []

    def register_task(self, task_id: str, task_name: str, base_priority: int = 5):
        """注册任务"""
        task = PriorityTask(
            task_id=task_id,
            task_name=task_name,
            base_priority=base_priority,
            current_priority=base_priority,
            last_adjusted=datetime.now().isoformat(),
            adjustment_reason="initial"
        )
        self.tasks[task_id] = task
        return task

    def adjust_priority(
        self,
        task_id: str,
        system_load_level: str,
        user_demand_level: int
    ) -> Optional[PriorityTask]:
        """调整任务优先级"""
        if task_id not in self.tasks:
            return None

        task = self.tasks[task_id]
        old_priority = task.current_priority

        # 基于系统负载和用户需求计算新优先级
        adjustment = 0

        # 系统负载影响
        if system_load_level == "critical":
            adjustment -= 3
        elif system_load_level == "high":
            adjustment -= 1
        elif system_load_level == "low":
            adjustment += 1

        # 用户需求影响
        if user_demand_level >= 8:
            adjustment += 2
        elif user_demand_level >= 6:
            adjustment += 1
        elif user_demand_level <= 3:
            adjustment -= 1

        # 计算新优先级 (1-10)
        new_priority = max(1, min(10, task.base_priority + adjustment))

        # 更新任务
        task.current_priority = new_priority
        task.last_adjusted = datetime.now().isoformat()
        task.adjustment_reason = f"load={system_load_level}, demand={user_demand_level}"

        # 记录调整历史
        if old_priority != new_priority:
            self.adjustment_history.append({
                "task_id": task_id,
                "old_priority": old_priority,
                "new_priority": new_priority,
                "adjustment": adjustment,
                "timestamp": datetime.now().isoformat(),
                "reason": task.adjustment_reason
            })

        return task

    def get_sorted_tasks(self) -> List[PriorityTask]:
        """获取按优先级排序的任务列表"""
        return sorted(self.tasks.values(), key=lambda t: t.current_priority, reverse=True)

    def get_task_summary(self) -> Dict[str, Any]:
        """获取任务摘要"""
        sorted_tasks = self.get_sorted_tasks()

        return {
            "total_tasks": len(self.tasks),
            "tasks": [asdict(t) for t in sorted_tasks],
            "adjustment_count": len(self.adjustment_history)
        }


class AdaptivePriorityEngine:
    """自适应优先级调整引擎"""

    def __init__(self):
        self.system_monitor = SystemMonitor()
        self.user_analyzer = UserBehaviorAnalyzer()
        self.priority_manager = PriorityManager()

    def start(self):
        """启动引擎"""
        self.system_monitor.start_monitoring()

        # 注册默认进化任务
        default_tasks = [
            ("meta_learning", "元学习分析", 6),
            ("prediction", "进化预测", 7),
            ("self_evaluation", "自我评估", 5),
            ("history_analysis", "历史分析", 4),
            ("health_check", "健康检查", 5)
        ]

        for task_id, task_name, priority in default_tasks:
            self.priority_manager.register_task(task_id, task_name, priority)

    def stop(self):
        """停止引擎"""
        self.system_monitor.stop_monitoring()

    def analyze_and_adjust(self) -> Dict[str, Any]:
        """分析并调整优先级"""
        # 获取系统状态
        load_level = self.system_monitor.get_load_level()
        metrics_summary = self.system_monitor.get_metrics_summary()

        # 获取用户需求
        demand_level = self.user_analyzer.get_current_demand_level()
        interaction_summary = self.user_analyzer.get_interaction_summary()

        # 调整所有任务优先级
        for task_id in self.priority_manager.tasks:
            self.priority_manager.adjust_priority(task_id, load_level, demand_level)

        # 生成结果
        result = {
            "timestamp": datetime.now().isoformat(),
            "system": {
                "load_level": load_level,
                "metrics": metrics_summary
            },
            "user": {
                "demand_level": demand_level,
                "interactions": interaction_summary
            },
            "tasks": self.priority_manager.get_task_summary(),
            "recommendations": self._generate_recommendations(load_level, demand_level)
        }

        return result

    def _generate_recommendations(self, load_level: str, demand_level: int) -> List[str]:
        """生成推荐建议"""
        recommendations = []

        # 基于系统负载
        if load_level == "critical":
            recommendations.append("系统负载极高，建议降低进化任务优先级或暂停")
        elif load_level == "high":
            recommendations.append("系统负载较高，建议减少并行任务数量")

        # 基于用户需求
        if demand_level >= 8:
            recommendations.append("用户需求高，建议优先完成当前任务")
        elif demand_level <= 3:
            recommendations.append("用户需求低，可以执行后台进化任务")

        return recommendations

    def record_user_interaction(self, interaction_type: str, content: str):
        """记录用户交互"""
        self.user_analyzer.record_interaction(interaction_type, content)


# 全局引擎实例
_engine: Optional[AdaptivePriorityEngine] = None


def get_engine() -> AdaptivePriorityEngine:
    """获取引擎实例"""
    global _engine
    if _engine is None:
        _engine = AdaptivePriorityEngine()
        _engine.start()
    return _engine


def run_priority_analysis() -> Dict[str, Any]:
    """运行优先级分析"""
    print("=" * 60)
    print("自适应优先级调整引擎")
    print("=" * 60)

    # 获取引擎
    engine = get_engine()

    # 分析并调整
    print("\n[1/3] 收集系统指标...")
    print(f"    系统负载等级: {engine.system_monitor.get_load_level()}")

    print("\n[2/3] 分析用户行为...")
    print(f"    用户需求等级: {engine.user_analyzer.get_current_demand_level()}")

    print("\n[3/3] 调整任务优先级...")
    result = engine.analyze_and_adjust()

    # 保存结果
    result_file = os.path.join(STATE_DIR, "adaptive_priority_result.json")
    os.makedirs(STATE_DIR, exist_ok=True)
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n结果已保存到: {result_file}")

    # 打印摘要
    print("\n" + "=" * 60)
    print("优先级调整摘要")
    print("=" * 60)
    print(f"\n系统状态:")
    print(f"  - 负载等级: {result['system']['load_level']}")
    print(f"  - CPU: {result['system']['metrics'].get('average_cpu', 0):.1f}%")
    print(f"  - 内存: {result['system']['metrics'].get('average_memory', 0):.1f}%")

    print(f"\n用户状态:")
    print(f"  - 需求等级: {result['user']['demand_level']}/10")

    print(f"\n任务优先级:")
    for task in result['tasks']['tasks'][:5]:
        print(f"  - {task['task_name']}: {task['current_priority']}/10 ({task['adjustment_reason']})")

    print(f"\n建议:")
    for rec in result.get('recommendations', []):
        print(f"  - {rec}")

    return result


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="自适应优先级调整引擎")
    parser.add_argument("--analyze", action="store_true", help="运行优先级分析")
    parser.add_argument("--monitor", action="store_true", help="启动持续监控")
    parser.add_argument("--status", action="store_true", help="查看当前优先级状态")
    parser.add_argument("--record", type=str, help="记录用户交互")
    parser.add_argument("--format", choices=["json", "text"], default="text", help="输出格式")

    args = parser.parse_args()

    # 如果没有指定参数，默认运行分析
    if not any([args.analyze, args.monitor, args.status, args.record]):
        args.analyze = True

    engine = get_engine()

    if args.analyze:
        result = run_priority_analysis()
        if args.format == "json":
            print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.monitor:
        print("启动持续监控模式 (按 Ctrl+C 停止)...")
        try:
            while True:
                result = engine.analyze_and_adjust()
                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 负载:{result['system']['load_level']} 需求:{result['user']['demand_level']}/10")
                for task in result['tasks']['tasks'][:3]:
                    print(f"  - {task['task_name']}: {task['current_priority']}")
                time.sleep(10)
        except KeyboardInterrupt:
            print("\n停止监控")
            engine.stop()

    elif args.status:
        result = engine.analyze_and_adjust()
        if args.format == "json":
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print("\n当前优先级状态:")
            for task in result['tasks']['tasks']:
                print(f"  - {task['task_name']}: {task['current_priority']}/10")

    elif args.record:
        engine.record_user_interaction("manual", args.record)
        print(f"已记录交互: {args.record}")


if __name__ == "__main__":
    main()