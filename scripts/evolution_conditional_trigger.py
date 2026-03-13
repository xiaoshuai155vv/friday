#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能进化闭环条件自动触发引擎 (Evolution Conditional Trigger Engine)
版本: 1.0.0
功能: 让进化环能够基于条件自动触发，包括能力缺口变化、失败模式、系统状态、
     定时任务等条件，实现真正的无人值守持续进化

集成到 do.py 支持关键词：
- 进化条件触发、设置进化触发条件、查看触发条件
- 触发引擎状态、触发引擎统计
- 立即触发进化、条件触发
"""

import json
import os
import sys
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum

# 添加脚本目录到路径
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))


class TriggerConditionType(Enum):
    """触发条件类型"""
    CAPABILITY_GAP = "capability_gap"     # 能力缺口变化触发
    FAILURE_DETECTED = "failure_detected"  # 失败模式触发
    SYSTEM_HEALTH = "system_health"        # 系统健康状态触发
    TIMED = "timed"                        # 定时触发
    MANUAL = "manual"                      # 手动触发
    COMPOSITE = "composite"                # 组合条件触发
    EVENT = "event"                        # 事件触发


@dataclass
class TriggerCondition:
    """触发条件"""
    id: str
    type: str
    enabled: bool = True
    params: Dict[str, Any] = field(default_factory=dict)
    last_triggered: Optional[str] = None
    trigger_count: int = 0


@dataclass
class TriggerEvent:
    """触发事件"""
    id: str
    condition_id: str
    timestamp: str
    reason: str
    details: Dict[str, Any] = field(default_factory=dict)


class EvolutionConditionalTriggerEngine:
    """智能进化闭环条件自动触发引擎"""

    def __init__(self):
        self.version = "1.0.0"
        self.state_dir = SCRIPT_DIR / ".." / "runtime" / "state"
        self.state_dir.mkdir(parents=True, exist_ok=True)

        self.trigger_conditions: List[TriggerCondition] = []
        self.trigger_events: List[TriggerEvent] = []
        self.is_running = False
        self.monitor_thread = None
        self._stop_event = threading.Event()

        # 加载状态
        self._load_state()

        # 初始化默认条件
        self._init_default_conditions()

    def _load_state(self):
        """加载状态"""
        state_file = self.state_dir / "evolution_conditional_trigger_state.json"
        if state_file.exists():
            try:
                with open(state_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.trigger_conditions = [TriggerCondition(**c) for c in data.get("conditions", [])]
                    self.trigger_events = [TriggerEvent(**e) for e in data.get("events", [])]
            except Exception as e:
                print(f"加载状态失败: {e}")

    def _save_state(self):
        """保存状态"""
        state_file = self.state_dir / "evolution_conditional_trigger_state.json"
        try:
            with open(state_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "conditions": [c.__dict__ for c in self.trigger_conditions],
                    "events": [e.__dict__ for e in self.trigger_events[-100:]],  # 保留最近100条
                    "updated_at": datetime.now().isoformat()
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存状态失败: {e}")

    def _init_default_conditions(self):
        """初始化默认条件"""
        if not self.trigger_conditions:
            # 添加默认触发条件
            self.trigger_conditions.extend([
                TriggerCondition(
                    id="capability_gap_001",
                    type=TriggerConditionType.CAPABILITY_GAP.value,
                    enabled=True,
                    params={
                        "check_interval_seconds": 300,  # 5分钟检查一次
                        "watch_files": ["references/capability_gaps.md", "references/assumed_demands.md"]
                    }
                ),
                TriggerCondition(
                    id="failure_001",
                    type=TriggerConditionType.FAILURE_DETECTED.value,
                    enabled=True,
                    params={
                        "check_interval_seconds": 300,
                        "watch_file": "references/failures.md",
                        "new_failure_weight": 0.8  # 新失败触发权重
                    }
                ),
                TriggerCondition(
                    id="timed_001",
                    type=TriggerConditionType.TIMED.value,
                    enabled=False,  # 默认不启用定时
                    params={
                        "interval_minutes": 60,
                        "start_time": "02:00",
                        "end_time": "06:00"
                    }
                )
            ])

    def add_condition(self, condition_type: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """添加触发条件"""
        condition_id = f"{condition_type}_{len(self.trigger_conditions) + 1:03d}"
        condition = TriggerCondition(
            id=condition_id,
            type=condition_type,
            enabled=True,
            params=params or {}
        )
        self.trigger_conditions.append(condition)
        self._save_state()

        return {
            "success": True,
            "message": f"已添加触发条件: {condition_id}",
            "condition": {
                "id": condition_id,
                "type": condition_type,
                "enabled": True,
                "params": params or {}
            }
        }

    def remove_condition(self, condition_id: str) -> Dict[str, Any]:
        """移除触发条件"""
        for i, c in enumerate(self.trigger_conditions):
            if c.id == condition_id:
                removed = self.trigger_conditions.pop(i)
                self._save_state()
                return {
                    "success": True,
                    "message": f"已移除触发条件: {condition_id}"
                }
        return {
            "success": False,
            "message": f"未找到触发条件: {condition_id}"
        }

    def enable_condition(self, condition_id: str) -> Dict[str, Any]:
        """启用触发条件"""
        for c in self.trigger_conditions:
            if c.id == condition_id:
                c.enabled = True
                self._save_state()
                return {
                    "success": True,
                    "message": f"已启用触发条件: {condition_id}"
                }
        return {
            "success": False,
            "message": f"未找到触发条件: {condition_id}"
        }

    def disable_condition(self, condition_id: str) -> Dict[str, Any]:
        """禁用触发条件"""
        for c in self.trigger_conditions:
            if c.id == condition_id:
                c.enabled = False
                self._save_state()
                return {
                    "success": True,
                    "message": f"已禁用触发条件: {condition_id}"
                }
        return {
            "success": False,
            "message": f"未找到触发条件: {condition_id}"
        }

    def list_conditions(self) -> Dict[str, Any]:
        """列出所有触发条件"""
        conditions = []
        for c in self.trigger_conditions:
            conditions.append({
                "id": c.id,
                "type": c.type,
                "enabled": c.enabled,
                "params": c.params,
                "last_triggered": c.last_triggered,
                "trigger_count": c.trigger_count
            })
        return {
            "success": True,
            "conditions": conditions,
            "total": len(conditions),
            "enabled_count": sum(1 for c in self.trigger_conditions if c.enabled)
        }

    def check_capability_gap_change(self, condition: TriggerCondition) -> bool:
        """检查能力缺口是否有变化"""
        try:
            # 读取最新的 capability_gaps.md 内容
            gap_file = SCRIPT_DIR / ".." / "references" / "capability_gaps.md"
            if not gap_file.exists():
                return False

            # 读取内容
            with open(gap_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # 检查是否有新的"可行方向"
            has_new_direction = "可行方向" in content and "-" in content

            # 检查 assumed_demands.md 是否有新需求
            demands_file = SCRIPT_DIR / ".." / "references" / "assumed_demands.md"
            if demands_file.exists():
                with open(demands_file, 'r', encoding='utf-8') as f:
                    demands = f.read()
                # 检查是否有待实现的需求
                has_pending = "待实现" in demands or "待规划" in demands

                if has_pending:
                    return True

            return has_new_direction

        except Exception as e:
            print(f"检查能力缺口变化失败: {e}")
            return False

    def check_failure_detected(self, condition: TriggerCondition) -> bool:
        """检查是否有新失败"""
        try:
            failures_file = SCRIPT_DIR / ".." / "references" / "failures.md"
            if not failures_file.exists():
                return False

            with open(failures_file, 'r', encoding='utf-8') as f:
                failures = f.read()

            # 检查最近是否有新的失败记录（简化：检查日期）
            lines = failures.strip().split('\n')
            recent_failures = 0
            today = datetime.now().strftime("%Y-%m-%d")

            for line in lines:
                if today in line:
                    recent_failures += 1

            # 如果今天有新失败，触发
            return recent_failures > 0

        except Exception as e:
            print(f"检查失败检测失败: {e}")
            return False

    def check_timed_trigger(self, condition: TriggerCondition) -> bool:
        """检查定时触发"""
        try:
            params = condition.params
            interval_minutes = params.get("interval_minutes", 60)

            # 检查上次触发时间
            if condition.last_triggered:
                last = datetime.fromisoformat(condition.last_triggered)
                now = datetime.now()
                if (now - last).total_seconds() < interval_minutes * 60:
                    return False

            # 检查时间窗口
            start_time = params.get("start_time")
            end_time = params.get("end_time")
            if start_time and end_time:
                now = datetime.now().time()
                start = datetime.strptime(start_time, "%H:%M").time()
                end = datetime.strptime(end_time, "%H:%M").time()
                if not (start <= now <= end):
                    return False

            return True

        except Exception as e:
            print(f"检查定时触发失败: {e}")
            return False

    def check_system_health(self, condition: TriggerCondition) -> bool:
        """检查系统健康状态触发"""
        try:
            # 读取系统健康报告
            health_file = self.state_dir / "system_health_report.json"
            if not health_file.exists():
                return False

            with open(health_file, 'r', encoding='utf-8') as f:
                health = json.load(f)

            # 检查是否有健康问题
            healthy = health.get("healthy", True)
            if not healthy:
                return True

            # 检查关键指标
            checks = health.get("checks", {})
            for check_name, check_data in checks.items():
                status = check_data.get("status", "ok")
                if status == "critical" or status == "warning":
                    return True

            return False

        except Exception as e:
            print(f"检查系统健康失败: {e}")
            return False

    def should_trigger(self, condition: TriggerCondition) -> bool:
        """检查条件是否满足"""
        if not condition.enabled:
            return False

        condition_type = condition.type

        if condition_type == TriggerConditionType.CAPABILITY_GAP.value:
            return self.check_capability_gap_change(condition)
        elif condition_type == TriggerConditionType.FAILURE_DETECTED.value:
            return self.check_failure_detected(condition)
        elif condition_type == TriggerConditionType.TIMED.value:
            return self.check_timed_trigger(condition)
        elif condition_type == TriggerConditionType.SYSTEM_HEALTH.value:
            return self.check_system_health(condition)

        return False

    def trigger_evolution(self, reason: str, details: Dict[str, Any] = None) -> Dict[str, Any]:
        """触发进化环"""
        try:
            # 尝试调用进化环
            from evolution_autonomy_engine import EvolutionAutonomyEngine
            engine = EvolutionAutonomyEngine()
            result = engine._execute_evolution_cycle({
                "reason": reason,
                "details": details or {}
            })

            return {
                "success": True,
                "message": f"已触发进化: {reason}",
                "result": result
            }

        except ImportError:
            # 如果模块不可用，模拟执行
            return {
                "success": True,
                "simulated": True,
                "message": f"已触发进化（模拟）: {reason}",
                "round": len(self.trigger_events) + 1,
                "reason": reason
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"触发进化失败: {str(e)}",
                "error": str(e)
            }

    def start_monitoring(self) -> Dict[str, Any]:
        """启动条件监控"""
        if self.is_running:
            return {
                "success": False,
                "message": "监控已在运行中"
            }

        self.is_running = True
        self._stop_event.clear()

        def monitor_loop():
            while not self._stop_event.is_set():
                for condition in self.trigger_conditions:
                    if not condition.enabled:
                        continue

                    try:
                        if self.should_trigger(condition):
                            # 触发进化
                            reason = f"条件满足: {condition.type} ({condition.id})"
                            result = self.trigger_evolution(reason, {"condition_id": condition.id})

                            # 记录触发事件
                            event = TriggerEvent(
                                id=f"evt_{len(self.trigger_events) + 1:06d}",
                                condition_id=condition.id,
                                timestamp=datetime.now().isoformat(),
                                reason=reason,
                                details=result
                            )
                            self.trigger_events.append(event)

                            # 更新条件状态
                            condition.last_triggered = datetime.now().isoformat()
                            condition.trigger_count += 1

                            self._save_state()
                    except Exception as e:
                        print(f"检查条件 {condition.id} 失败: {e}")

                # 每分钟检查一次
                time.sleep(60)

        self.monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitor_thread.start()

        return {
            "success": True,
            "message": "已启动条件监控"
        }

    def stop_monitoring(self) -> Dict[str, Any]:
        """停止条件监控"""
        if not self.is_running:
            return {
                "success": False,
                "message": "监控未在运行"
            }

        self.is_running = False
        self._stop_event.set()

        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5)

        return {
            "success": True,
            "message": "已停止条件监控"
        }

    def trigger_now(self) -> Dict[str, Any]:
        """立即手动触发一次进化"""
        reason = "手动触发"
        result = self.trigger_evolution(reason)

        # 记录触发事件
        event = TriggerEvent(
            id=f"evt_{len(self.trigger_events) + 1:06d}",
            condition_id="manual",
            timestamp=datetime.now().isoformat(),
            reason=reason,
            details=result
        )
        self.trigger_events.append(event)
        self._save_state()

        return result

    def get_status(self) -> Dict[str, Any]:
        """获取引擎状态"""
        return {
            "engine": "evolution_conditional_trigger",
            "version": self.version,
            "is_running": self.is_running,
            "conditions_count": len(self.trigger_conditions),
            "enabled_conditions": sum(1 for c in self.trigger_conditions if c.enabled),
            "events_count": len(self.trigger_events)
        }

    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        stats = {
            "total_triggers": len(self.trigger_events),
            "by_condition": {},
            "recent_events": []
        }

        # 按条件统计
        for event in self.trigger_events:
            cond_id = event.condition_id
            if cond_id not in stats["by_condition"]:
                stats["by_condition"][cond_id] = 0
            stats["by_condition"][cond_id] += 1

        # 最近5条事件
        stats["recent_events"] = [
            {
                "id": e.id,
                "condition_id": e.condition_id,
                "timestamp": e.timestamp,
                "reason": e.reason
            }
            for e in self.trigger_events[-5:]
        ]

        return stats


# ==================== CLI 接口 ====================

def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="智能进化闭环条件自动触发引擎")
    parser.add_argument("command", choices=[
        "start", "stop", "status", "stats", "list",
        "add", "remove", "enable", "disable", "trigger"
    ], help="命令")
    parser.add_argument("--type", "-t", help="条件类型 (add 命令时使用)")
    parser.add_argument("--params", "-p", help="条件参数 (JSON格式)")
    parser.add_argument("--id", help="条件ID (remove/enable/disable 命令时使用)")

    args = parser.parse_args()

    # 创建引擎实例
    engine = EvolutionConditionalTriggerEngine()

    if args.command == "start":
        result = engine.start_monitoring()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "stop":
        result = engine.stop_monitoring()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "status":
        result = engine.get_status()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "stats":
        result = engine.get_statistics()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "list":
        result = engine.list_conditions()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "add":
        params = json.loads(args.params) if args.params else {}
        result = engine.add_condition(args.type or "timed", params)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "remove":
        result = engine.remove_condition(args.id or "")
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "enable":
        result = engine.enable_condition(args.id or "")
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "disable":
        result = engine.disable_condition(args.id or "")
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "trigger":
        result = engine.trigger_now()
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()