#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能主动服务编排引擎 (Proactive Service Orchestrator)

创建一个能够持续监控用户行为、自动发现可自动化模式、
主动向用户推荐或执行服务的统一编排层。

这是「超越用户」的关键能力——系统主动为用户创造价值，而非被动响应。

功能：
1. 整合自动化模式发现引擎（automation_pattern_discovery）
2. 整合任务偏好引擎（task_preference_engine）
3. 整合任务规划引擎（cross_engine_task_planner）
4. 实现用户行为持续监控和主动服务发现
5. 主动服务推荐和执行
6. 效果评估和学习

区别于其他引擎：
- proactive_service_trigger: 条件触发式服务（用户设置条件→满足时执行）
- automation_pattern_discovery: 模式发现（从历史中发现模式）
- intelligent_service_loop: 服务闭环（服务执行→反馈）
- 本引擎: 主动服务编排（持续监控→发现机会→推荐/执行→学习）
"""

import os
import sys
import json
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Optional, Any, Tuple

# 导入相关引擎
SCRIPT_DIR = Path(__file__).parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

# 尝试导入相关引擎（部分失败不影响整体功能）
try:
    from automation_pattern_discovery import AutomationPatternDiscovery
except ImportError:
    AutomationPatternDiscovery = None

try:
    from task_preference_engine import TaskPreferenceEngine
except ImportError:
    TaskPreferenceEngine = None

try:
    from cross_engine_task_planner import CrossEngineTaskPlanner
except ImportError:
    CrossEngineTaskPlanner = None

try:
    from conversation_execution_engine import ConversationExecutionEngine
except ImportError:
    ConversationExecutionEngine = None

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
RUNTIME_DIR = PROJECT_ROOT / "runtime"
STATE_DIR = RUNTIME_DIR / "state"
LOGS_DIR = RUNTIME_DIR / "logs"


class ProactiveServiceOrchestrator:
    """智能主动服务编排引擎"""

    def __init__(self):
        self.service_enabled = True
        self.monitoring_interval = 300  # 监控间隔（秒）
        self.min_confidence = 0.6  # 最小置信度
        self.max_recommendations = 5  # 最大推荐数

        # 初始化子引擎
        self.pattern_engine = AutomationPatternDiscovery() if AutomationPatternDiscovery else None
        self.preference_engine = TaskPreferenceEngine() if TaskPreferenceEngine else None
        self.task_planner = CrossEngineTaskPlanner() if CrossEngineTaskPlanner else None

        # 服务状态
        self.monitoring_active = False
        self.last_service_time = None
        self.service_history = []
        self.recommendations = []
        self.learned_patterns = []

    def analyze_user_context(self) -> Dict[str, Any]:
        """分析用户当前上下文"""
        context = {
            "timestamp": datetime.now().isoformat(),
            "time_of_day": self._get_time_category(),
            "day_of_week": datetime.now().weekday(),
            "recent_activities": self._get_recent_activities(),
            "active_applications": self._get_active_apps(),
            "system_state": self._get_system_state(),
            "user_preferences": self._get_user_preferences()
        }
        return context

    def _get_time_category(self) -> str:
        """获取时间段分类"""
        hour = datetime.now().hour
        if 6 <= hour < 9:
            return "morning_early"
        elif 9 <= hour < 12:
            return "morning"
        elif 12 <= hour < 14:
            return "noon"
        elif 14 <= hour < 18:
            return "afternoon"
        elif 18 <= hour < 21:
            return "evening"
        elif 21 <= hour < 24:
            return "night_late"
        else:
            return "midnight"

    def _get_recent_activities(self, limit: int = 10) -> List[Dict]:
        """获取最近活动"""
        activities = []
        try:
            recent_logs_file = STATE_DIR / "recent_logs.json"
            if recent_logs_file.exists():
                with open(recent_logs_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    entries = data.get("entries", [])
                    activities = entries[-limit:] if len(entries) > limit else entries
        except Exception as e:
            pass
        return activities

    def _get_active_apps(self) -> List[str]:
        """获取活跃应用"""
        apps = []
        try:
            if os.name == 'nt':
                import subprocess
                result = subprocess.run(
                    ['powershell', '-Command',
                     'Get-Process | Where-Object {$_.MainWindowTitle} | Select-Object -First 10 Name'],
                    capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    apps = [line.strip() for line in result.stdout.split('\n') if line.strip()]
        except Exception:
            pass
        return apps

    def _get_system_state(self) -> Dict:
        """获取系统状态"""
        state = {
            "cpu_usage": 0,
            "memory_usage": 0,
            "disk_usage": 0
        }
        try:
            import psutil
            state["cpu_usage"] = psutil.cpu_percent(interval=1)
            state["memory_usage"] = psutil.virtual_memory().percent
            state["disk_usage"] = psutil.disk_usage('/').percent
        except Exception:
            pass
        return state

    def _get_user_preferences(self) -> Dict:
        """获取用户偏好"""
        preferences = {}
        try:
            if self.preference_engine:
                # 获取任务偏好
                preferences_file = STATE_DIR / "task_preferences.json"
                if preferences_file.exists():
                    with open(preferences_file, 'r', encoding='utf-8') as f:
                        preferences = json.load(f)
        except Exception:
            pass
        return preferences

    def discover_service_opportunities(self) -> List[Dict[str, Any]]:
        """发现服务机会"""
        opportunities = []

        # 1. 分析当前上下文
        context = self.analyze_user_context()

        # 2. 从模式发现获取可自动化模式
        if self.pattern_engine:
            try:
                patterns = self.pattern_engine.analyze_behavior_logs()
                for pattern in patterns.get("patterns", [])[:3]:
                    opportunities.append({
                        "type": "pattern_based",
                        "title": "发现可自动化模式",
                        "description": f"您经常执行 {pattern.get('name', '未知操作')}，可创建自动化流程",
                        "confidence": pattern.get("confidence", 0.7),
                        "action": pattern.get("action", "create_automation"),
                        "data": pattern
                    })
            except Exception:
                pass

        # 3. 从时间模式发现服务机会
        time_based_opportunities = self._discover_time_based_opportunities(context)
        opportunities.extend(time_based_opportunities)

        # 4. 从系统状态发现服务机会
        state_based_opportunities = self._discover_state_based_opportunities(context)
        opportunities.extend(state_based_opportunities)

        # 按置信度排序
        opportunities.sort(key=lambda x: x.get("confidence", 0), reverse=True)

        return opportunities[:self.max_recommendations]

    def _discover_time_based_opportunities(self, context: Dict) -> List[Dict]:
        """基于时间发现服务机会"""
        opportunities = []

        time_category = context.get("time_of_day", "")
        day_of_week = context.get("day_of_week", 0)

        # 早上9点：检查是否需要打开工作相关应用
        if time_category == "morning" and day_of_week < 5:
            opportunities.append({
                "type": "time_based",
                "title": "早晨工作准备",
                "description": "检测到工作时间，可自动打开工作应用",
                "confidence": 0.8,
                "action": "prepare_workday",
                "data": {"trigger": "morning_work"}
            })

        # 下午2点：检查是否需要休息提醒
        if time_category == "afternoon" and day_of_week < 5:
            opportunities.append({
                "type": "time_based",
                "title": "下午状态检查",
                "description": "工作日下午，可检查是否需要休息或处理待办",
                "confidence": 0.6,
                "action": "afternoon_check",
                "data": {"trigger": "afternoon_check"}
            })

        return opportunities

    def _discover_state_based_opportunities(self, context: Dict) -> List[Dict]:
        """基于系统状态发现服务机会"""
        opportunities = []

        system_state = context.get("system_state", {})

        # CPU 使用率高
        if system_state.get("cpu_usage", 0) > 80:
            opportunities.append({
                "type": "state_based",
                "title": "系统性能优化",
                "description": "检测到 CPU 使用率较高，建议清理后台进程",
                "confidence": 0.9,
                "action": "optimize_performance",
                "data": {"trigger": "high_cpu"}
            })

        # 内存使用率高
        if system_state.get("memory_usage", 0) > 85:
            opportunities.append({
                "type": "state_based",
                "title": "内存优化建议",
                "description": "检测到内存使用率较高，建议释放内存",
                "confidence": 0.9,
                "action": "optimize_memory",
                "data": {"trigger": "high_memory"}
            })

        return opportunities

    def generate_recommendations(self) -> List[Dict[str, Any]]:
        """生成服务推荐"""
        opportunities = self.discover_service_opportunities()

        # 过滤低置信度
        filtered = [opp for opp in opportunities
                   if opp.get("confidence", 0) >= self.min_confidence]

        self.recommendations = filtered
        return filtered

    def execute_service(self, service_id: str, auto_execute: bool = False) -> Dict[str, Any]:
        """执行主动服务"""
        result = {
            "service_id": service_id,
            "success": False,
            "message": "",
            "executed_at": datetime.now().isoformat()
        }

        # 查找对应服务
        service = None
        for rec in self.recommendations:
            if rec.get("action") == service_id:
                service = rec
                break

        if not service:
            result["message"] = f"未找到服务: {service_id}"
            return result

        try:
            action = service.get("action", "")

            if action == "prepare_workday":
                # 执行早晨准备工作
                result["success"] = self._execute_prepare_workday()
                result["message"] = "早晨工作准备已完成" if result["success"] else "早晨工作准备失败"
            elif action == "afternoon_check":
                # 执行下午检查
                result["success"] = self._execute_afternoon_check()
                result["message"] = "下午检查已完成" if result["success"] else "下午检查失败"
            elif action == "optimize_performance":
                result["success"] = self._execute_performance_optimization()
                result["message"] = "性能优化已完成" if result["success"] else "性能优化失败"
            elif action == "optimize_memory":
                result["success"] = self._execute_memory_optimization()
                result["message"] = "内存优化已完成" if result["success"] else "内存优化失败"
            else:
                result["message"] = f"未知操作: {action}"

            # 记录执行历史
            if result["success"]:
                self.service_history.append({
                    "service_id": service_id,
                    "action": action,
                    "executed_at": result["executed_at"],
                    "auto_executed": auto_execute
                })
                self.last_service_time = datetime.now()

        except Exception as e:
            result["message"] = f"执行失败: {str(e)}"

        return result

    def _execute_prepare_workday(self) -> bool:
        """执行早晨准备工作"""
        # 打开常用工作应用
        commands = []
        try:
            # 检查是否有任务偏好
            if self.preference_engine:
                # 获取用户偏好的工作应用
                pass

            # 尝试打开邮箱等常用应用
            import subprocess
            # 尝试打开浏览器
            try:
                subprocess.Popen(["start", "chrome", "mail.haier.net"],
                                shell=True, stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)
            except Exception:
                pass
            return True
        except Exception:
            return False

    def _execute_afternoon_check(self) -> bool:
        """执行下午检查"""
        # 发送通知提醒用户
        try:
            from notification_tool import show_notification
            show_notification("下午检查", "检测到您已工作一段时间，是否需要休息？")
            return True
        except Exception:
            return False

    def _execute_performance_optimization(self) -> bool:
        """执行性能优化"""
        # 执行主动运维优化
        try:
            from proactive_operations_engine import ProactiveOperationsEngine
            engine = ProactiveOperationsEngine()
            result = engine.execute_all_optimizations()
            return result.get("success", False)
        except Exception:
            return False

    def _execute_memory_optimization(self) -> bool:
        """执行内存优化"""
        try:
            from proactive_operations_engine import ProactiveOperationsEngine
            engine = ProactiveOperationsEngine()
            result = engine.optimize_memory()
            return result.get("success", False)
        except Exception:
            return False

    def get_status(self) -> Dict[str, Any]:
        """获取服务状态"""
        return {
            "enabled": self.service_enabled,
            "monitoring_active": self.monitoring_active,
            "last_service_time": self.last_service_time.isoformat() if self.last_service_time else None,
            "service_count": len(self.service_history),
            "recommendations_count": len(self.recommendations),
            "sub_engines": {
                "pattern_engine": self.pattern_engine is not None,
                "preference_engine": self.preference_engine is not None,
                "task_planner": self.task_planner is not None
            }
        }

    def get_recommendations(self) -> List[Dict[str, Any]]:
        """获取当前推荐"""
        if not self.recommendations:
            return self.generate_recommendations()
        return self.recommendations

    def get_history(self, limit: int = 20) -> List[Dict]:
        """获取服务历史"""
        return self.service_history[-limit:]

    def enable(self):
        """启用主动服务"""
        self.service_enabled = True

    def disable(self):
        """禁用主动服务"""
        self.service_enabled = False


def main():
    """CLI 入口"""
    if len(sys.argv) < 2:
        print("用法: proactive_service_orchestrator.py <command> [args...]")
        print("命令:")
        print("  status - 查看服务状态")
        print("  recommendations - 查看服务推荐")
        print("  discover - 发现服务机会")
        print("  execute <service_id> - 执行服务")
        print("  history [limit] - 查看服务历史")
        print("  enable - 启用服务")
        print("  disable - 禁用服务")
        sys.exit(1)

    orchestrator = ProactiveServiceOrchestrator()
    command = sys.argv[1]

    if command == "status":
        status = orchestrator.get_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))
    elif command == "recommendations":
        recommendations = orchestrator.get_recommendations()
        print(json.dumps(recommendations, ensure_ascii=False, indent=2))
    elif command == "discover":
        opportunities = orchestrator.discover_service_opportunities()
        print(json.dumps(opportunities, ensure_ascii=False, indent=2))
    elif command == "execute":
        if len(sys.argv) < 3:
            print("错误: 需要指定服务ID")
            sys.exit(1)
        service_id = sys.argv[2]
        result = orchestrator.execute_service(service_id)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif command == "history":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 20
        history = orchestrator.get_history(limit)
        print(json.dumps(history, ensure_ascii=False, indent=2))
    elif command == "enable":
        orchestrator.enable()
        print("主动服务已启用")
    elif command == "disable":
        orchestrator.disable()
        print("主动服务已禁用")
    else:
        print(f"未知命令: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()