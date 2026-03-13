#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能进化闭环自治引擎（Evolution Autonomy Engine）
让系统能够完全自主运行进化环，实现无人值守的持续进化管理

功能：
1. 自动触发进化环（基于定时/条件/系统状态）
2. 进化结果自动评估与反馈
3. 进化策略自动调整
4. 无人值守的持续进化管理
5. 进化健康监控与自愈

集成到 do.py 支持关键词：
- 进化自治、自动进化、启动进化环、停止进化环、进化状态
- 进化自治状态、查看进化自治、自动进化状态
"""

import sys
import os
import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum

# 简单的定时调度器（不依赖外部库）
class SimpleScheduler:
    """简单定时调度器"""
    def __init__(self):
        self.jobs = []
        self.running = False

    def every(self, minutes):
        """每N分钟执行一次"""
        return Job(minutes)

    def run_pending(self):
        """运行待执行的任务"""
        now = time.time()
        for job in self.jobs:
            if job.next_run <= now:
                job.func()
                job.next_run = time.time() + job.interval

    def clear(self):
        """清除所有任务"""
        self.jobs = []


class Job:
    """任务"""
    def __init__(self, minutes):
        self.interval = minutes * 60
        self.func = None
        self.next_run = time.time() + self.interval

    def do(self, func):
        """设置执行函数"""
        self.func = func
        return self


# 全局调度器实例
schedule = SimpleScheduler()

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


class EvolutionState(Enum):
    """进化状态"""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"


class TriggerType(Enum):
    """触发类型"""
    TIMED = "timed"           # 定时触发
    CONDITION = "condition"   # 条件触发
    MANUAL = "manual"         # 手动触发
    EVENT = "event"           # 事件触发


@dataclass
class EvolutionCycle:
    """进化周期"""
    round_number: int
    start_time: str
    end_time: Optional[str] = None
    goal: str = ""
    status: str = "pending"  # pending, running, completed, failed
    result: Optional[Dict] = None


@dataclass
class AutonomyConfig:
    """自治配置"""
    auto_start: bool = False                    # 系统启动时自动开始
    check_interval_minutes: int = 60           # 检查间隔（分钟）
    max_concurrent_cycles: int = 1             # 最大并发进化数
    retry_on_failure: bool = True              # 失败时重试
    max_retries: int = 3                       # 最大重试次数
    notify_on_completion: bool = True           # 完成时通知
    enable_health_check: bool = True           # 启用健康检查


class EvolutionAutonomyEngine:
    """智能进化闭环自治引擎"""

    def __init__(self, config: AutonomyConfig = None):
        """
        初始化进化自治引擎

        Args:
            config: 自治配置
        """
        self.config = config or AutonomyConfig()
        self.state = EvolutionState.IDLE
        self.current_cycle: Optional[EvolutionCycle] = None
        self.cycle_history: List[EvolutionCycle] = []
        self.trigger_conditions: List[Dict] = []
        self.health_status: Dict[str, Any] = {}
        self.is_running = False
        self.scheduler_thread = None
        self._stop_event = threading.Event()

        # 加载配置
        self._load_config()
        self._load_history()

    def _load_config(self):
        """加载配置"""
        config_path = "runtime/state/evolution_autonomy_config.json"
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.config = AutonomyConfig(**data.get("config", {}))
            except Exception as e:
                print(f"加载配置失败: {e}")

    def _save_config(self):
        """保存配置"""
        config_path = "runtime/state/evolution_autonomy_config.json"
        try:
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "config": {
                        "auto_start": self.config.auto_start,
                        "check_interval_minutes": self.config.check_interval_minutes,
                        "max_concurrent_cycles": self.config.max_concurrent_cycles,
                        "retry_on_failure": self.config.retry_on_failure,
                        "max_retries": self.config.max_retries,
                        "notify_on_completion": self.config.notify_on_completion,
                        "enable_health_check": self.config.enable_health_check
                    }
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存配置失败: {e}")

    def _load_history(self):
        """加载历史"""
        history_path = "runtime/state/evolution_autonomy_history.json"
        if os.path.exists(history_path):
            try:
                with open(history_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.cycle_history = [EvolutionCycle(**c) for c in data.get("cycles", [])]
            except Exception as e:
                print(f"加载历史失败: {e}")

    def _save_history(self):
        """保存历史"""
        history_path = "runtime/state/evolution_autonomy_history.json"
        try:
            os.makedirs(os.path.dirname(history_path), exist_ok=True)
            with open(history_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "cycles": [
                        {
                            "round_number": c.round_number,
                            "start_time": c.start_time,
                            "end_time": c.end_time,
                            "goal": c.goal,
                            "status": c.status,
                            "result": c.result
                        }
                        for c in self.cycle_history[-50:]  # 保留最近50条
                    ],
                    "updated_at": datetime.now().isoformat()
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存历史失败: {e}")

    def start_autonomy(self, trigger_type: TriggerType = TriggerType.MANUAL) -> Dict[str, Any]:
        """
        启动自治模式

        Args:
            trigger_type: 触发类型

        Returns:
            启动结果
        """
        if self.is_running:
            return {
                "success": False,
                "message": "自治模式已经在运行中",
                "state": self.state.value
            }

        self.is_running = True
        self.state = EvolutionState.RUNNING
        self._stop_event.clear()

        # 根据触发类型启动
        if trigger_type == TriggerType.TIMED:
            self._start_scheduler()
        elif trigger_type == TriggerType.CONDITION:
            self._start_condition_monitor()
        else:
            # 手动触发，立即执行一次进化
            self._execute_evolution_cycle()

        self._save_config()

        return {
            "success": True,
            "message": f"已启动进化自治模式，触发类型: {trigger_type.value}",
            "state": self.state.value,
            "config": {
                "auto_start": self.config.auto_start,
                "check_interval_minutes": self.config.check_interval_minutes
            }
        }

    def stop_autonomy(self) -> Dict[str, Any]:
        """
        停止自治模式

        Returns:
            停止结果
        """
        if not self.is_running:
            return {
                "success": False,
                "message": "自治模式未在运行",
                "state": self.state.value
            }

        self.is_running = False
        self._stop_event.set()
        self.state = EvolutionState.IDLE

        # 停止调度器
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            self.scheduler_thread.join(timeout=5)

        self._save_config()

        return {
            "success": True,
            "message": "已停止进化自治模式",
            "state": self.state.value
        }

    def _start_scheduler(self):
        """启动定时调度器"""
        def run_scheduler():
            while not self._stop_event.is_set():
                schedule.run_pending()
                time.sleep(60)  # 每分钟检查一次

        # 设置定时任务
        schedule.clear()
        schedule.every(self.config.check_interval_minutes).minutes.do(self._execute_evolution_cycle)

        # 启动调度线程
        self.scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        self.scheduler_thread.start()

    def _start_condition_monitor(self):
        """启动条件监控器"""
        def monitor_conditions():
            while not self._stop_event.is_set():
                # 检查触发条件
                for condition in self.trigger_conditions:
                    if self._check_condition(condition):
                        self._execute_evolution_cycle(condition)
                time.sleep(60)  # 每分钟检查一次

        monitor_thread = threading.Thread(target=monitor_conditions, daemon=True)
        monitor_thread.start()

    def _check_condition(self, condition: Dict) -> bool:
        """检查条件是否满足"""
        condition_type = condition.get("type", "")

        if condition_type == "system_idle":
            # 检查系统是否空闲
            return self._is_system_idle()
        elif condition_type == "time_window":
            # 检查是否在时间窗口内
            return self._is_in_time_window(condition.get("start"), condition.get("end"))
        elif condition_type == "resource_available":
            # 检查资源是否可用
            return self._are_resources_available(condition.get("min_free_memory_gb", 2))

        return False

    def _is_system_idle(self) -> bool:
        """检查系统是否空闲"""
        # 简单实现：检查是否有活跃进程
        try:
            import psutil
            cpu_percent = psutil.cpu_percent(interval=1)
            return cpu_percent < 30  # CPU 使用率低于 30% 视为空闲
        except:
            return True  # 如果无法检测，假设空闲

    def _is_in_time_window(self, start: str, end: str) -> bool:
        """检查是否在时间窗口内"""
        now = datetime.now().time()
        try:
            start_time = datetime.strptime(start, "%H:%M").time()
            end_time = datetime.strptime(end, "%H:%M").time()
            return start_time <= now <= end_time
        except:
            return True  # 如果解析失败，假设在时间窗口内

    def _are_resources_available(self, min_free_gb: float) -> bool:
        """检查资源是否可用"""
        try:
            import psutil
            memory = psutil.virtual_memory()
            free_gb = memory.available / (1024 ** 3)
            return free_gb >= min_free_gb
        except:
            return True  # 如果无法检测，假设资源可用

    def _execute_evolution_cycle(self, trigger_info: Dict = None):
        """执行进化周期"""
        # 获取下一轮编号
        round_number = self._get_next_round_number()

        cycle = EvolutionCycle(
            round_number=round_number,
            start_time=datetime.now().isoformat(),
            goal="自主进化",
            status="running"
        )
        self.current_cycle = cycle

        try:
            # 检查系统健康状态
            if self.config.enable_health_check:
                health = self.check_health()
                if not health.get("healthy", False):
                    # 系统不健康，跳过本次进化
                    cycle.status = "skipped"
                    cycle.result = {"reason": "system_unhealthy", "health": health}
                    self.cycle_history.append(cycle)
                    self._save_history()
                    return

            # 执行进化（调用进化环）
            result = self._run_evolution_round()

            cycle.end_time = datetime.now().isoformat()
            cycle.status = "completed"
            cycle.result = result

        except Exception as e:
            cycle.end_time = datetime.now().isoformat()
            cycle.status = "failed"
            cycle.result = {"error": str(e)}

            # 重试逻辑
            if self.config.retry_on_failure:
                retry_count = cycle.result.get("retry_count", 0)
                if retry_count < self.config.max_retries:
                    cycle.result["retry_count"] = retry_count + 1
                    # 重试
                    self._execute_evolution_cycle()

        self.cycle_history.append(cycle)
        self._save_history()

    def _get_next_round_number(self) -> int:
        """获取下一轮编号"""
        if self.cycle_history:
            return max(c.round_number for c in self.cycle_history) + 1
        return 223  # 从当前轮开始

    def _run_evolution_round(self) -> Dict[str, Any]:
        """运行进化轮次"""
        # 调用进化环执行
        try:
            # 尝试导入并调用进化环
            from scripts.evolution_loop_automation import EvolutionLoopAutomation
            loop = EvolutionLoopAutomation()
            result = loop.run_full_cycle()
            return {"success": True, "result": result}
        except ImportError:
            # 如果进化环模块不可用，模拟执行
            return {
                "success": True,
                "simulated": True,
                "message": "进化环模块不可用，执行模拟进化",
                "round": self.current_cycle.round_number if self.current_cycle else 223
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def add_trigger_condition(self, condition: Dict) -> Dict[str, Any]:
        """
        添加触发条件

        Args:
            condition: 条件字典

        Returns:
            添加结果
        """
        self.trigger_conditions.append(condition)
        return {
            "success": True,
            "message": f"已添加触发条件: {condition.get('type')}",
            "conditions_count": len(self.trigger_conditions)
        }

    def remove_trigger_condition(self, index: int) -> Dict[str, Any]:
        """
        移除触发条件

        Args:
            index: 条件索引

        Returns:
            移除结果
        """
        if 0 <= index < len(self.trigger_conditions):
            removed = self.trigger_conditions.pop(index)
            return {
                "success": True,
                "message": f"已移除触发条件: {removed.get('type')}",
                "conditions_count": len(self.trigger_conditions)
            }
        return {
            "success": False,
            "message": "索引无效"
        }

    def check_health(self) -> Dict[str, Any]:
        """
        检查系统健康状态

        Returns:
            健康状态
        """
        health = {
            "timestamp": datetime.now().isoformat(),
            "healthy": True,
            "checks": {}
        }

        try:
            # 尝试导入 psutil
            import psutil
            # CPU 检查
            cpu_percent = psutil.cpu_percent(interval=1)
            health["checks"]["cpu"] = {
                "percent": cpu_percent,
                "status": "ok" if cpu_percent < 80 else "warning"
            }
            if cpu_percent >= 80:
                health["healthy"] = False

            # 内存检查
            memory = psutil.virtual_memory()
            health["checks"]["memory"] = {
                "percent": memory.percent,
                "available_gb": round(memory.available / (1024 ** 3), 2),
                "status": "ok" if memory.percent < 85 else "warning"
            }
            if memory.percent >= 85:
                health["healthy"] = False

            # 磁盘检查
            disk = psutil.disk_usage('/')
            health["checks"]["disk"] = {
                "percent": disk.percent,
                "free_gb": round(disk.free / (1024 ** 3), 2),
                "status": "ok" if disk.percent < 90 else "warning"
            }
            if disk.percent >= 90:
                health["healthy"] = False

        except ImportError:
            # psutil 不可用，使用简化检查
            health["checks"]["cpu"] = {"status": "unknown", "message": "psutil not available"}
            health["checks"]["memory"] = {"status": "unknown", "message": "psutil not available"}
            health["checks"]["disk"] = {"status": "unknown", "message": "psutil not available"}
            health["message"] = "psutil not available, using basic health check"
        except Exception as e:
            health["error"] = str(e)

        self.health_status = health
        return health

    def get_status(self) -> Dict[str, Any]:
        """获取引擎状态"""
        return {
            "engine": "evolution_autonomy",
            "version": "1.0.0",
            "state": self.state.value,
            "is_running": self.is_running,
            "current_cycle": {
                "round_number": self.current_cycle.round_number if self.current_cycle else None,
                "status": self.current_cycle.status if self.current_cycle else None,
                "start_time": self.current_cycle.start_time if self.current_cycle else None
            } if self.current_cycle else None,
            "config": {
                "auto_start": self.config.auto_start,
                "check_interval_minutes": self.config.check_interval_minutes,
                "max_concurrent_cycles": self.config.max_concurrent_cycles,
                "retry_on_failure": self.config.retry_on_failure,
                "enable_health_check": self.config.enable_health_check
            },
            "trigger_conditions_count": len(self.trigger_conditions),
            "cycle_history_count": len(self.cycle_history),
            "health_status": self.health_status
        }

    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        total = len(self.cycle_history)
        completed = sum(1 for c in self.cycle_history if c.status == "completed")
        failed = sum(1 for c in self.cycle_history if c.status == "failed")
        skipped = sum(1 for c in self.cycle_history if c.status == "skipped")

        return {
            "total_cycles": total,
            "completed": completed,
            "failed": failed,
            "skipped": skipped,
            "success_rate": round(completed / total * 100, 1) if total > 0 else 0
        }

    def update_config(self, config_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        更新配置

        Args:
            config_dict: 配置字典

        Returns:
            更新结果
        """
        for key, value in config_dict.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)

        self._save_config()

        return {
            "success": True,
            "message": "配置已更新",
            "config": {
                "auto_start": self.config.auto_start,
                "check_interval_minutes": self.config.check_interval_minutes,
                "max_concurrent_cycles": self.config.max_concurrent_cycles,
                "retry_on_failure": self.config.retry_on_failure,
                "max_retries": self.config.max_retries,
                "notify_on_completion": self.config.notify_on_completion,
                "enable_health_check": self.config.enable_health_check
            }
        }

    def trigger_now(self) -> Dict[str, Any]:
        """
        立即触发一次进化

        Returns:
            触发结果
        """
        if not self.is_running:
            return {
                "success": False,
                "message": "请先启动自治模式"
            }

        self._execute_evolution_cycle()

        return {
            "success": True,
            "message": f"已触发第 {self.current_cycle.round_number} 轮进化" if self.current_cycle else "已触发进化",
            "cycle": {
                "round_number": self.current_cycle.round_number if self.current_cycle else None,
                "status": self.current_cycle.status if self.current_cycle else None
            }
        }


# ==================== CLI 接口 ====================

def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="智能进化闭环自治引擎")
    parser.add_argument("command", choices=[
        "start", "stop", "status", "health", "stats",
        "add-condition", "remove-condition", "trigger", "update-config"
    ], help="命令")
    parser.add_argument("--type", "-t", choices=["timed", "condition", "manual"],
                        default="manual", help="触发类型")
    parser.add_argument("--condition-type", help="条件类型（add-condition时使用）")
    parser.add_argument("--condition-params", help="条件参数（JSON格式）")
    parser.add_argument("--index", "-i", type=int, help="索引（remove-condition时使用）")
    parser.add_argument("--config", "-c", help="配置参数（JSON格式）")

    args = parser.parse_args()

    # 创建引擎实例
    engine = EvolutionAutonomyEngine()

    if args.command == "start":
        trigger_type = TriggerType(args.type)
        result = engine.start_autonomy(trigger_type)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "stop":
        result = engine.stop_autonomy()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "status":
        result = engine.get_status()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "health":
        result = engine.check_health()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "stats":
        result = engine.get_statistics()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "add-condition":
        condition = {"type": args.condition_type or "system_idle"}
        if args.condition_params:
            try:
                condition.update(json.loads(args.condition_params))
            except:
                pass
        result = engine.add_trigger_condition(condition)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "remove-condition":
        result = engine.remove_trigger_condition(args.index or 0)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "trigger":
        result = engine.trigger_now()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "update-config":
        config_dict = json.loads(args.config) if args.config else {}
        result = engine.update_config(config_dict)
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()