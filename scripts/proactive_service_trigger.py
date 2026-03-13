"""
主动服务触发引擎 (Proactive Service Trigger Engine)
在 intelligent_service_loop 基础上，实现条件触发的自动服务
让系统在检测到特定条件（时间、系统状态、用户行为）时，无需用户指令即可自动执行服务闭环

功能：
1. 多种触发条件：时间触发、事件触发、状态触发
2. 条件监听与自动执行
3. 与 intelligent_service_loop 集成实现完整闭环
4. 触发日志和效果评估
5. CLI 接口

触发条件类型：
- time: 定时触发（如每30分钟、每小时）
- event: 事件触发（如系统空闲、用户长时间无操作）
- state: 状态触发（如CPU使用率高、内存不足）
- schedule: 计划触发（如工作时间开始、午休时间）
"""

import json
import os
import sys
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
from pathlib import Path
from enum import Enum

# 添加 scripts 目录到路径
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


class TriggerType(Enum):
    """触发类型"""
    TIME = "time"           # 定时触发
    EVENT = "event"         # 事件触发
    STATE = "state"         # 状态触发
    SCHEDULE = "schedule"   # 计划触发


class TriggerCondition:
    """触发条件"""

    def __init__(self, trigger_type: str, config: Dict[str, Any]):
        self.trigger_type = trigger_type
        self.config = config
        self.last_trigger_time = None
        self.trigger_count = 0
        self.enabled = config.get("enabled", True)

    def should_trigger(self, current_time: datetime = None) -> bool:
        """检查是否应该触发"""
        if not self.enabled:
            return False

        current_time = current_time or datetime.now()

        if self.trigger_type == TriggerType.TIME.value:
            return self._check_time_trigger(current_time)
        elif self.trigger_type == TriggerType.EVENT.value:
            return self._check_event_trigger()
        elif self.trigger_type == TriggerType.STATE.value:
            return self._check_state_trigger()
        elif self.trigger_type == TriggerType.SCHEDULE.value:
            return self._check_schedule_trigger(current_time)

        return False

    def _check_time_trigger(self, current_time: datetime) -> bool:
        """检查时间触发条件"""
        interval_minutes = self.config.get("interval_minutes", 60)

        if self.last_trigger_time is None:
            return True

        time_diff = (current_time - self.last_trigger_time).total_seconds() / 60
        return time_diff >= interval_minutes

    def _check_event_trigger(self) -> bool:
        """检查事件触发条件"""
        event_type = self.config.get("event_type", "")

        # 用户空闲检测
        if event_type == "user_idle":
            idle_seconds = self.config.get("idle_seconds", 300)  # 默认5分钟
            try:
                if PSUTIL_AVAILABLE:
                    # 使用 psutil 获取空闲时间
                    import ctypes
                    class LASTINPUTINFO(ctypes.Structure):
                        _fields_ = [('cbSize', ctypes.c_uint32), ('dwTime', ctypes.c_uint32)]

                    lii = LASTINPUTINFO()
                    lii.cbSize = ctypes.sizeof(LASTINPUTINFO)
                    if ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lii)):
                        idle_time = (ctypes.windll.kernel32.GetTickCount() - lii.dwTime) / 1000
                        return idle_time >= idle_seconds
            except Exception:
                pass
            return False

        return False

    def _check_state_trigger(self) -> bool:
        """检查状态触发条件"""
        if not PSUTIL_AVAILABLE:
            return False

        state_type = self.config.get("state_type", "")
        threshold = self.config.get("threshold", 80)

        try:
            if state_type == "cpu_high":
                cpu_percent = psutil.cpu_percent(interval=1)
                return cpu_percent >= threshold
            elif state_type == "memory_high":
                memory = psutil.virtual_memory()
                return memory.percent >= threshold
            elif state_type == "disk_high":
                disk = psutil.disk_usage('C:\\')
                return disk.percent >= threshold
        except Exception:
            pass

        return False

    def _check_schedule_trigger(self, current_time: datetime) -> bool:
        """检查计划触发条件"""
        schedule_type = self.config.get("schedule_type", "")

        if schedule_type == "work_hours_start":
            # 每天工作开始（9:00）
            start_hour = self.config.get("hour", 9)
            if current_time.hour == start_hour and current_time.minute < 5:
                # 确保同一天不重复触发
                if self.last_trigger_time is None or self.last_trigger_time.date() != current_time.date():
                    return True

        elif schedule_type == "lunch_time":
            # 午休时间（12:00-13:00）
            if 12 <= current_time.hour < 13:
                if self.last_trigger_time is None or self.last_trigger_time.hour != current_time.hour:
                    return True

        elif schedule_type == "work_hours_end":
            # 工作结束（18:00）
            end_hour = self.config.get("hour", 18)
            if current_time.hour == end_hour and current_time.minute < 5:
                if self.last_trigger_time is None or self.last_trigger_time.date() != current_time.date():
                    return True

        return False

    def update_last_trigger(self, current_time: datetime = None):
        """更新最后触发时间"""
        self.last_trigger_time = current_time or datetime.now()
        self.trigger_count += 1


class ProactiveServiceTrigger:
    """主动服务触发引擎"""

    def __init__(self):
        self.state_file = SCRIPT_DIR.parent / "runtime" / "state" / "proactive_trigger_state.json"
        self.trigger_log_file = SCRIPT_DIR.parent / "runtime" / "state" / "proactive_trigger_log.json"
        self._ensure_state_dir()

        self.conditions: List[TriggerCondition] = []
        self.service_loop = None
        self.daemon_thread = None
        self.is_running = False

        # 加载状态和触发条件
        self._load_conditions()

    def _ensure_state_dir(self):
        """确保状态目录存在"""
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.trigger_log_file.parent.mkdir(parents=True, exist_ok=True)

    def _load_state(self) -> Dict[str, Any]:
        """加载状态"""
        if self.state_file.exists():
            with open(self.state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "enabled": True,
            "daemon_mode": False,
            "check_interval": 60,  # 检查间隔（秒）
            "auto_execute": False
        }

    def _save_state(self, state: Dict[str, Any]):
        """保存状态"""
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

    def _load_conditions(self):
        """加载触发条件"""
        # 默认触发条件
        default_conditions = [
            {
                "id": "hourly_check",
                "name": "每小时健康检查",
                "type": "time",
                "enabled": True,
                "config": {
                    "interval_minutes": 60,
                    "action": "health_check"
                }
            },
            {
                "id": "idle_reminder",
                "name": "用户空闲提醒",
                "type": "event",
                "enabled": False,  # 默认关闭
                "config": {
                    "event_type": "user_idle",
                    "idle_seconds": 1800,  # 30分钟
                    "action": "suggest_break"
                }
            },
            {
                "id": "work_hours_start",
                "name": "工作日开始提醒",
                "type": "schedule",
                "enabled": False,  # 默认关闭
                "config": {
                    "schedule_type": "work_hours_start",
                    "hour": 9,
                    "action": "morning_service"
                }
            },
            {
                "id": "system_health",
                "name": "系统健康监控",
                "type": "state",
                "enabled": True,
                "config": {
                    "state_type": "memory_high",
                    "threshold": 85,
                    "action": "health_alert"
                }
            }
        ]

        # 从状态文件加载自定义条件
        state = self._load_state()
        custom_conditions = state.get("custom_conditions", [])

        # 合并条件
        all_conditions = default_conditions + custom_conditions

        # 创建触发条件对象
        for cond in all_conditions:
            if cond.get("enabled", True):
                trigger = TriggerCondition(cond["type"], cond.get("config", {}))
                trigger.last_trigger_time = None
                self.conditions.append({
                    "id": cond["id"],
                    "name": cond["name"],
                    "condition": trigger,
                    "action": cond.get("action", "service_loop")
                })

    def _load_trigger_log(self) -> List[Dict[str, Any]]:
        """加载触发日志"""
        if self.trigger_log_file.exists():
            with open(self.trigger_log_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def _save_trigger_log(self, log: List[Dict[str, Any]]):
        """保存触发日志"""
        # 只保留最近 100 条
        log = log[-100:]
        with open(self.trigger_log_file, 'w', encoding='utf-8') as f:
            json.dump(log, f, ensure_ascii=False, indent=2)

    def _load_service_loop(self):
        """加载智能服务闭环引擎"""
        if self.service_loop is None:
            try:
                from intelligent_service_loop import IntelligentServiceLoop
                self.service_loop = IntelligentServiceLoop()
            except ImportError as e:
                print(f"警告: 无法加载智能服务闭环引擎: {e}")

    def check_and_trigger(self) -> List[Dict[str, Any]]:
        """检查所有条件并触发"""
        current_time = datetime.now()
        triggered_actions = []

        for cond in self.conditions:
            try:
                if cond["condition"].should_trigger(current_time):
                    action_result = self._execute_action(cond["action"], cond["name"])

                    # 更新触发条件状态
                    cond["condition"].update_last_trigger(current_time)

                    triggered_actions.append({
                        "trigger_id": cond["id"],
                        "name": cond["name"],
                        "action": cond["action"],
                        "timestamp": current_time.isoformat(),
                        "result": action_result
                    })

                    # 记录到日志
                    log = self._load_trigger_log()
                    log.append({
                        "trigger_id": cond["id"],
                        "name": cond["name"],
                        "action": cond["action"],
                        "timestamp": current_time.isoformat(),
                        "status": action_result.get("status", "unknown")
                    })
                    self._save_trigger_log(log)

            except Exception as e:
                print(f"检查触发条件 {cond['id']} 时出错: {e}")

        return triggered_actions

    def _execute_action(self, action: str, trigger_name: str) -> Dict[str, Any]:
        """执行触发动作"""
        state = self._load_state()
        auto_execute = state.get("auto_execute", False)

        result = {
            "action": action,
            "status": "executed"
        }

        if action == "service_loop":
            # 执行智能服务闭环
            self._load_service_loop()
            if self.service_loop:
                try:
                    loop_result = self.service_loop.run_service_loop(auto_execute=auto_execute)
                    result["service_loop_result"] = loop_result
                except Exception as e:
                    result["status"] = "error"
                    result["error"] = str(e)
            else:
                result["status"] = "skipped"
                result["message"] = "服务闭环引擎未加载"

        elif action == "health_check":
            # 执行健康检查
            self._load_service_loop()
            if self.service_loop:
                try:
                    status = self.service_loop.get_service_status()
                    result["health_status"] = status
                except Exception as e:
                    result["status"] = "error"
                    result["error"] = str(e)

        elif action == "health_alert":
            # 发送健康预警
            if PSUTIL_AVAILABLE:
                memory = psutil.virtual_memory()
                result["memory_percent"] = memory.percent

                # 如果服务闭环可用，发送预警
                self._load_service_loop()
                if self.service_loop:
                    try:
                        # 调用预测引擎获取预警
                        if self.service_loop.predictive_engine:
                            prediction = self.service_loop.predictive_engine.scan_and_predict()
                            result["prediction"] = prediction
                    except Exception as e:
                        result["prediction_error"] = str(e)

        elif action == "suggest_break":
            # 建议休息
            result["message"] = "检测到用户长时间空闲，建议休息"

        elif action == "morning_service":
            # 早晨服务
            self._load_service_loop()
            if self.service_loop:
                try:
                    recommendations = self.service_loop.get_recommendations({"context": "morning"})
                    result["recommendations"] = recommendations
                except Exception as e:
                    result["status"] = "error"
                    result["error"] = str(e)

        return result

    def start_daemon(self, check_interval: int = 60):
        """启动守护进程模式"""
        if self.is_running:
            return {"status": "already_running"}

        self.is_running = True

        def daemon_loop():
            while self.is_running:
                try:
                    self.check_and_trigger()
                except Exception as e:
                    print(f"守护进程错误: {e}")

                time.sleep(check_interval)

        self.daemon_thread = threading.Thread(target=daemon_loop, daemon=True)
        self.daemon_thread.start()

        # 更新状态
        state = self._load_state()
        state["daemon_mode"] = True
        state["check_interval"] = check_interval
        self._save_state(state)

        return {
            "status": "started",
            "check_interval": check_interval,
            "conditions_count": len(self.conditions)
        }

    def stop_daemon(self):
        """停止守护进程"""
        if not self.is_running:
            return {"status": "not_running"}

        self.is_running = False

        # 更新状态
        state = self._load_state()
        state["daemon_mode"] = False
        self._save_state(state)

        return {"status": "stopped"}

    def get_status(self) -> Dict[str, Any]:
        """获取触发器状态"""
        state = self._load_state()
        trigger_log = self._load_trigger_log()

        # 计算触发统计
        total_triggers = len(trigger_log)
        success_triggers = sum(1 for t in trigger_log if t.get("status") == "executed")

        return {
            "enabled": state.get("enabled", True),
            "daemon_mode": state.get("daemon_mode", False),
            "is_running": self.is_running,
            "check_interval": state.get("check_interval", 60),
            "auto_execute": state.get("auto_execute", False),
            "conditions_count": len(self.conditions),
            "conditions": [
                {
                    "id": c["id"],
                    "name": c["name"],
                    "type": c["condition"].trigger_type,
                    "enabled": c["condition"].enabled,
                    "trigger_count": c["condition"].trigger_count
                }
                for c in self.conditions
            ],
            "total_triggers": total_triggers,
            "success_triggers": success_triggers,
            "recent_triggers": trigger_log[-10:] if trigger_log else []
        }

    def add_condition(self, condition: Dict[str, Any]) -> Dict[str, Any]:
        """添加触发条件"""
        state = self._load_state()

        if "custom_conditions" not in state:
            state["custom_conditions"] = []

        # 检查是否已存在
        for existing in state["custom_conditions"]:
            if existing["id"] == condition["id"]:
                return {"status": "error", "message": f"条件 {condition['id']} 已存在"}

        state["custom_conditions"].append(condition)
        self._save_state(state)

        # 重新加载条件
        self.conditions = []
        self._load_conditions()

        return {"status": "success", "message": f"条件 {condition['id']} 已添加"}

    def remove_condition(self, condition_id: str) -> Dict[str, Any]:
        """移除触发条件"""
        state = self._load_state()

        if "custom_conditions" in state:
            original_count = len(state["custom_conditions"])
            state["custom_conditions"] = [
                c for c in state["custom_conditions"] if c["id"] != condition_id
            ]

            if len(state["custom_conditions"]) < original_count:
                self._save_state(state)
                # 重新加载条件
                self.conditions = []
                self._load_conditions()
                return {"status": "success", "message": f"条件 {condition_id} 已移除"}

        return {"status": "error", "message": f"条件 {condition_id} 不存在或无法移除"}

    def manual_trigger(self, condition_id: str = None) -> Dict[str, Any]:
        """手动触发"""
        if condition_id:
            # 触发指定条件
            for cond in self.conditions:
                if cond["id"] == condition_id:
                    result = self._execute_action(cond["action"], cond["name"])
                    cond["condition"].update_last_trigger()
                    return {"status": "success", "result": result}
            return {"status": "error", "message": f"条件 {condition_id} 不存在"}
        else:
            # 触发所有条件
            results = self.check_and_trigger()
            return {"status": "success", "triggered": len(results), "results": results}


def main():
    """CLI 入口"""
    import argparse

    parser = argparse.ArgumentParser(description="主动服务触发引擎")
    parser.add_argument("action", nargs="?", choices=["status", "trigger", "start", "stop", "add", "remove", "list"],
                        default="status", help="执行动作")
    parser.add_argument("--id", "-i", help="条件ID")
    parser.add_argument("--name", "-n", help="条件名称")
    parser.add_argument("--type", "-t", choices=["time", "event", "state", "schedule"], help="触发类型")
    parser.add_argument("--interval", type=int, help="时间间隔（分钟）")
    parser.add_argument("--auto", "-a", action="store_true", help="自动执行服务")
    parser.add_argument("--check-interval", type=int, default=60, help="守护进程检查间隔（秒）")

    args = parser.parse_args()

    engine = ProactiveServiceTrigger()

    if args.action == "status":
        status = engine.get_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))

    elif args.action == "trigger":
        result = engine.manual_trigger(args.id)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.action == "start":
        result = engine.start_daemon(args.check_interval)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.action == "stop":
        result = engine.stop_daemon()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.action == "add":
        if not args.id or not args.name or not args.type:
            print("错误: 需要提供 --id, --name, --type")
            sys.exit(1)

        condition = {
            "id": args.id,
            "name": args.name,
            "type": args.type,
            "enabled": True,
            "config": {
                "interval_minutes": args.interval or 60,
                "action": "service_loop"
            }
        }

        result = engine.add_condition(condition)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.action == "remove":
        if not args.id:
            print("错误: 需要提供 --id")
            sys.exit(1)

        result = engine.remove_condition(args.id)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.action == "list":
        status = engine.get_status()
        print(f"触发条件数量: {status['conditions_count']}")
        for cond in status.get("conditions", []):
            print(f"  - {cond['id']}: {cond['name']} ({cond['type']}) - 触发次数: {cond['trigger_count']}")


if __name__ == "__main__":
    main()