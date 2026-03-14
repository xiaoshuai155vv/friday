#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景情境感知与主动服务编排引擎 (Context-Aware Service Orchestrator)
Version: 1.0.0

让系统能够综合时间、用户行为、系统状态、历史交互，主动识别服务机会并智能编排多引擎协同工作，
实现从被动响应到主动感知与预服务的范式升级。

功能：
1. 多维度情境感知（时间、行为、系统状态、历史交互）
2. 服务机会自动识别（基于模式分析）
3. 多引擎智能编排（协同调度70+引擎）
4. 主动服务推送（预测性服务推荐）
5. 上下文记忆与学习（持续优化服务策略）

集成到 do.py 支持：
- 情境感知、情境分析、主动服务、编排服务、服务机会等关键词触发
"""

import json
import os
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import threading
import time

# 路径配置
SCRIPT_DIR = Path(__file__).parent
RUNTIME_DIR = SCRIPT_DIR.parent / "runtime"
STATE_DIR = RUNTIME_DIR / "state"
LOGS_DIR = RUNTIME_DIR / "logs"


class ContextAwareServiceOrchestrator:
    """智能全场景情境感知与主动服务编排引擎"""

    def __init__(self):
        self.name = "情境感知服务编排引擎"
        self.version = "1.0.0"
        self.context_data = {}  # 当前上下文数据
        self.service_patterns = {}  # 服务模式库
        self.interaction_history = []  # 交互历史
        self.last_analysis_time = None  # 上次分析时间

        # 加载情境感知配置
        self.config = self._load_config()

        # 初始化各维度感知器
        self._init_perceptors()

        # 加载交互历史
        self._load_interaction_history()

    def _load_config(self) -> Dict:
        """加载配置"""
        config_path = STATE_DIR / "context_aware_config.json"
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Failed to load config: {e}")

        # 默认配置
        return {
            "enable_time_context": True,
            "enable_behavior_context": True,
            "enable_system_context": True,
            "enable_history_context": True,
            "service_opportunity_threshold": 0.6,
            "max_history_items": 100,
            "analysis_interval_seconds": 300,  # 5分钟
            "auto_service_enabled": False  # 默认不自动执行，只推荐
        }

    def _init_perceptors(self):
        """初始化各维度感知器"""
        self.perceptors = {
            "time": self._perceive_time_context,
            "behavior": self._perceive_behavior_context,
            "system": self._perceive_system_context,
            "history": self._perceive_history_context
        }

    def _perceive_time_context(self) -> Dict:
        """感知时间维度上下文"""
        now = datetime.now()

        # 基础时间信息
        time_context = {
            "hour": now.hour,
            "minute": now.minute,
            "day_of_week": now.weekday(),
            "is_weekend": now.weekday() >= 5,
            "is_morning": 6 <= now.hour < 12,
            "is_afternoon": 12 <= now.hour < 18,
            "is_evening": 18 <= now.hour < 22,
            "is_night": now.hour >= 22 or now.hour < 6,
            "date": now.strftime("%Y-%m-%d"),
            "time_str": now.strftime("%H:%M")
        }

        # 时间模式分析
        time_context["likely_activity"] = self._analyze_time_activity(now)

        return time_context

    def _analyze_time_activity(self, now: datetime) -> str:
        """基于时间分析可能的活动"""
        hour = now.hour

        if 6 <= hour < 9:
            return "morning_routine"
        elif 9 <= hour < 12:
            return "work_morning"
        elif 12 <= hour < 13:
            return "lunch_time"
        elif 13 <= hour < 18:
            return "work_afternoon"
        elif 18 <= hour < 20:
            return "evening_routine"
        elif 20 <= hour < 22:
            return "leisure_time"
        elif 22 <= hour < 24:
            return "night_routine"
        else:
            return "late_night"

    def _perceive_behavior_context(self) -> Dict:
        """感知行为上下文（从最近交互中学习）"""
        behavior_context = {
            "recent_intents": [],
            "frequent_engines": {},
            "session_duration": 0,
            "last_intent": None
        }

        # 从交互历史中分析
        try:
            recent_logs_path = STATE_DIR / "recent_logs.json"
            if recent_logs_path.exists():
                with open(recent_logs_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if "entries" in data and data["entries"]:
                        # 获取最近10条
                        recent = data["entries"][-10:]

                        # 分析最近意图
                        for entry in recent:
                            if "desc" in entry:
                                behavior_context["recent_intents"].append(entry["desc"])

                        # 最后意图
                        if recent:
                            behavior_context["last_intent"] = recent[-1].get("desc", "")

                        # 粗略计算会话时长
                        if len(recent) >= 2:
                            try:
                                first_time = datetime.fromisoformat(recent[0]["time"].replace('Z', '+00:00'))
                                last_time = datetime.fromisoformat(recent[-1]["time"].replace('Z', '+00:00'))
                                behavior_context["session_duration"] = (last_time - first_time).total_seconds()
                            except:
                                pass
        except Exception as e:
            print(f"Warning: Failed to analyze behavior context: {e}")

        return behavior_context

    def _perceive_system_context(self) -> Dict:
        """感知系统状态上下文"""
        system_context = {
            "cpu_usage": 0,
            "memory_usage": 0,
            "running_processes": [],
            "active_window": None
        }

        # 获取 CPU/内存使用率
        try:
            import psutil

            system_context["cpu_usage"] = psutil.cpu_percent(interval=0.1)
            system_context["memory_usage"] = psutil.virtual_memory().percent

            # 获取运行中的进程
            for proc in psutil.process_iter(['name', 'cpu_percent']):
                try:
                    cpu = proc.info['cpu_percent']
                    if cpu and cpu > 1.0:
                        system_context["running_processes"].append({
                            "name": proc.info['name'],
                            "cpu": cpu
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

            # 取前5个CPU占用最高的进程
            system_context["running_processes"] = sorted(
                system_context["running_processes"],
                key=lambda x: x.get('cpu', 0),
                reverse=True
            )[:5]

        except ImportError:
            pass  # psutil 未安装时跳过
        except Exception as e:
            print(f"Warning: Failed to get system context: {e}")

        # 获取活动窗口
        try:
            import subprocess
            result = subprocess.run(
                ['powershell', '-Command',
                 '(Get-Process | Where-Object {$_.MainWindowTitle -ne ""} | Select-Object -First 1).MainWindowTitle'],
                capture_output=True, text=True, timeout=2
            )
            if result.stdout.strip():
                system_context["active_window"] = result.stdout.strip()
        except Exception:
            pass

        return system_context

    def _perceive_history_context(self) -> Dict:
        """感知历史交互上下文"""
        history_context = {
            "total_interactions": len(self.interaction_history),
            "today_interactions": 0,
            "dominant_intent_type": None,
            "recent_service_requests": []
        }

        # 统计今日交互
        today = datetime.now().strftime("%Y-%m-%d")
        for interaction in self.interaction_history:
            if interaction.get("date", "").startswith(today):
                history_context["today_interactions"] += 1

        # 获取最近的服务请求
        history_context["recent_service_requests"] = [
            i.get("service_type", "unknown")
            for i in self.interaction_history[-10:]
        ]

        return history_context

    def _load_interaction_history(self):
        """加载交互历史"""
        history_file = STATE_DIR / "interaction_history.json"
        if history_file.exists():
            try:
                with open(history_time, 'r', encoding='utf-8') as f:
                    self.interaction_history = json.load(f)
            except Exception as e:
                print(f"Warning: Failed to load interaction history: {e}")
                self.interaction_history = []

    def perceive(self) -> Dict:
        """综合感知所有维度上下文"""
        context = {
            "time": {},
            "behavior": {},
            "system": {},
            "history": {},
            "timestamp": datetime.now().isoformat()
        }

        # 时间维度
        if self.config.get("enable_time_context", True):
            context["time"] = self._perceive_time_context()

        # 行为维度
        if self.config.get("enable_behavior_context", True):
            context["behavior"] = self._perceive_behavior_context()

        # 系统维度
        if self.config.get("enable_system_context", True):
            context["system"] = self._perceive_system_context()

        # 历史维度
        if self.config.get("enable_history_context", True):
            context["history"] = self._perceive_history_context()

        self.context_data = context
        self.last_analysis_time = datetime.now()

        return context

    def identify_service_opportunities(self) -> List[Dict]:
        """识别服务机会"""
        if not self.context_data:
            self.perceive()

        opportunities = []

        # 基于时间模式识别
        time_opportunities = self._identify_time_based_opportunities()
        opportunities.extend(time_opportunities)

        # 基于行为模式识别
        behavior_opportunities = self._identify_behavior_based_opportunities()
        opportunities.extend(behavior_opportunities)

        # 基于系统状态识别
        system_opportunities = self._identify_system_based_opportunities()
        opportunities.extend(system_opportunities)

        # 按置信度排序
        opportunities.sort(key=lambda x: x.get("confidence", 0), reverse=True)

        # 只返回置信度高于阈值的
        threshold = self.config.get("service_opportunity_threshold", 0.6)
        return [o for o in opportunities if o.get("confidence", 0) >= threshold]

    def _identify_time_based_opportunities(self) -> List[Dict]:
        """基于时间识别服务机会"""
        opportunities = []
        time_ctx = self.context_data.get("time", {})
        likely_activity = time_ctx.get("likely_activity", "")

        # 基于时间的主动服务建议
        time_based_services = {
            "morning_routine": [
                {"type": "check_schedule", "confidence": 0.8, "reason": "早上查看日程"},
                {"type": "check_weather", "confidence": 0.7, "reason": "查看天气出门"},
                {"type": "focus_mode", "confidence": 0.6, "reason": "开始专注工作"}
            ],
            "lunch_time": [
                {"type": "nutrition_reminder", "confidence": 0.7, "reason": "午餐时间提醒"},
                {"type": "break_suggestion", "confidence": 0.8, "reason": "休息建议"}
            ],
            "evening_routine": [
                {"type": "daily_summary", "confidence": 0.8, "reason": "每日总结"},
                {"type": "tomorrow_preview", "confidence": 0.7, "reason": "预览明日安排"},
                {"type": "relaxation_suggestion", "confidence": 0.6, "reason": "放松建议"}
            ],
            "night_routine": [
                {"type": "sleep_reminder", "confidence": 0.9, "reason": "睡觉提醒"},
                {"type": "do_not_disturb", "confidence": 0.7, "reason": "建议开启勿扰模式"}
            ]
        }

        if likely_activity in time_based_services:
            for service in time_based_services[likely_activity]:
                opportunities.append({
                    "type": service["type"],
                    "confidence": service["confidence"],
                    "reason": service["reason"],
                    "source": "time",
                    "activity": likely_activity
                })

        return opportunities

    def _identify_behavior_based_opportunities(self) -> List[Dict]:
        """基于行为识别服务机会"""
        opportunities = []
        behavior_ctx = self.context_data.get("behavior", {})

        # 分析会话时长
        session_duration = behavior_ctx.get("session_duration", 0)

        # 长时间会话提醒
        if session_duration > 3600:  # 超过1小时
            opportunities.append({
                "type": "break_reminder",
                "confidence": 0.8,
                "reason": "已持续工作超过1小时",
                "source": "behavior",
                "duration": session_duration
            })

        # 频繁相同操作建议自动化
        recent_intents = behavior_ctx.get("recent_intents", [])
        if len(recent_intents) >= 3:
            # 检查是否有重复模式
            if len(set(recent_intents[-3:])) == 1:
                opportunities.append({
                    "type": "automation_suggestion",
                    "confidence": 0.7,
                    "reason": "检测到重复操作模式",
                    "source": "behavior"
                })

        return opportunities

    def _identify_system_based_opportunities(self) -> List[Dict]:
        """基于系统状态识别服务机会"""
        opportunities = []
        system_ctx = self.context_data.get("system", {})

        # CPU/内存过高
        cpu = system_ctx.get("cpu_usage", 0)
        memory = system_ctx.get("memory_usage", 0)

        if cpu > 80:
            opportunities.append({
                "type": "performance_optimization",
                "confidence": 0.9,
                "reason": f"CPU使用率过高 ({cpu}%)",
                "source": "system",
                "action": "检查高CPU进程"
            })

        if memory > 85:
            opportunities.append({
                "type": "memory_optimization",
                "confidence": 0.9,
                "reason": f"内存使用率过高 ({memory}%)",
                "source": "system",
                "action": "建议清理内存"
            })

        # 运行特定应用时的建议
        running_procs = system_ctx.get("running_processes", [])
        proc_names = [p.get("name", "").lower() for p in running_procs]

        if "code" in proc_names or "pycharm" in proc_names:
            opportunities.append({
                "type": "dev_mode",
                "confidence": 0.7,
                "reason": "检测到开发环境运行",
                "source": "system"
            })

        return opportunities

    def orchestrate_services(self, opportunities: List[Dict]) -> Dict:
        """编排服务执行"""
        if not opportunities:
            return {
                "status": "no_opportunities",
                "message": "当前没有识别到服务机会",
                "actions": []
            }

        # 准备编排计划
        orchestration_plan = {
            "opportunities_count": len(opportunities),
            "selected_actions": [],
            "engine_sequence": [],
            "estimated_duration": 0
        }

        # 选择最高置信度的机会
        top_opportunity = opportunities[0]

        # 生成服务动作
        action = self._generate_service_action(top_opportunity)
        if action:
            orchestration_plan["selected_actions"].append(action)
            orchestration_plan["engine_sequence"] = action.get("engines", [])
            orchestration_plan["estimated_duration"] = action.get("duration", 30)

        return orchestration_plan

    def _generate_service_action(self, opportunity: Dict) -> Optional[Dict]:
        """生成服务动作"""
        service_type = opportunity.get("type", "")
        reason = opportunity.get("reason", "")

        action_map = {
            "break_reminder": {
                "name": "休息提醒",
                "engines": ["notification_tool", "focus_reminder"],
                "duration": 10,
                "steps": [
                    {"type": "notify", "message": "您已持续工作较长时间，建议休息5-10分钟"},
                    {"type": "suggest", "content": "可以喝杯水，伸展一下身体"}
                ]
            },
            "daily_summary": {
                "name": "每日总结",
                "engines": ["data_insight_engine", "proactive_notification_engine"],
                "duration": 30,
                "steps": [
                    {"type": "analyze", "target": "today_activities"},
                    {"type": "report", "format": "summary"}
                ]
            },
            "focus_mode": {
                "name": "专注模式",
                "engines": ["focus_reminder"],
                "duration": 15,
                "steps": [
                    {"type": "enable", "mode": "focus"},
                    {"type": "notify", "message": "已开启专注模式"}
                ]
            },
            "performance_optimization": {
                "name": "性能优化",
                "engines": ["process_tool", "proactive_decision_action_engine"],
                "duration": 60,
                "steps": [
                    {"type": "analyze", "target": "high_cpu_processes"},
                    {"type": "suggest", "content": "建议结束不必要的进程"}
                ]
            },
            "check_schedule": {
                "name": "查看日程",
                "engines": ["calendar_tool"],
                "duration": 20,
                "steps": [
                    {"type": "query", "target": "today"},
                    {"type": "report", "format": "schedule"}
                ]
            },
            "check_weather": {
                "name": "查看天气",
                "engines": ["web_search"],
                "duration": 15,
                "steps": [
                    {"type": "search", "query": "today weather"}
                ]
            }
        }

        return action_map.get(service_type, {
            "name": service_type,
            "engines": [],
            "duration": 10,
            "steps": [{"type": "notify", "message": reason}]
        })

    def get_status(self) -> Dict:
        """获取引擎状态"""
        return {
            "name": self.name,
            "version": self.version,
            "context_loaded": bool(self.context_data),
            "last_analysis": self.last_analysis_time.isoformat() if self.last_analysis_time else None,
            "total_interactions": len(self.interaction_history),
            "config": {
                "enable_time_context": self.config.get("enable_time_context", True),
                "enable_behavior_context": self.config.get("enable_behavior_context", True),
                "enable_system_context": self.config.get("enable_system_context", True),
                "service_opportunity_threshold": self.config.get("service_opportunity_threshold", 0.6)
            }
        }

    def record_interaction(self, service_type: str, result: str):
        """记录交互用于学习"""
        self.interaction_history.append({
            "date": datetime.now().isoformat(),
            "service_type": service_type,
            "result": result
        })

        # 限制历史长度
        max_items = self.config.get("max_history_items", 100)
        if len(self.interaction_history) > max_items:
            self.interaction_history = self.interaction_history[-max_items:]

        # 保存历史
        self._save_interaction_history()

    def _save_interaction_history(self):
        """保存交互历史"""
        history_file = STATE_DIR / "interaction_history.json"
        try:
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(self.interaction_history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save interaction history: {e}")


# 全局实例
_orchestrator_instance = None
_instance_lock = threading.Lock()


def get_orchestrator() -> ContextAwareServiceOrchestrator:
    """获取全局实例（线程安全）"""
    global _orchestrator_instance

    if _orchestrator_instance is None:
        with _instance_lock:
            if _orchestrator_instance is None:
                _orchestrator_instance = ContextAwareServiceOrchestrator()

    return _orchestrator_instance


# 命令行接口
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="智能全场景情境感知与主动服务编排引擎")
    parser.add_argument("command", choices=["status", "perceive", "opportunities", "orchestrate", "record"],
                        help="要执行的命令")
    parser.add_argument("--type", help="服务类型（用于record命令）")
    parser.add_argument("--result", help="执行结果（用于record命令）")

    args = parser.parse_args()

    orchestrator = get_orchestrator()

    if args.command == "status":
        result = orchestrator.get_status()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "perceive":
        result = orchestrator.perceive()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "opportunities":
        opportunities = orchestrator.identify_service_opportunities()
        print(json.dumps(opportunities, ensure_ascii=False, indent=2))

    elif args.command == "orchestrate":
        opportunities = orchestrator.identify_service_opportunities()
        result = orchestrator.orchestrate_services(opportunities)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "record":
        if args.type and args.result:
            orchestrator.record_interaction(args.type, args.result)
            print(f"已记录交互: {args.type} -> {args.result}")
        else:
            print("Error: 需要 --type 和 --result 参数")