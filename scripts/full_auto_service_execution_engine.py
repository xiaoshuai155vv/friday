#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
智能全自动化服务执行引擎（Full Auto Service Execution Engine）

让系统实现真正的一键式自动服务执行，具备自主触发、自动上下文准备、
无缝执行能力，实现从「半自动闭环」到「全自动一键执行」的范式升级。

功能：
1. 一键触发机制 - 只需一个简单指令即可启动完整服务流程
2. 自动上下文准备 - 自动收集当前系统状态、用户行为、时间等上下文
3. 智能执行决策 - 基于上下文自动决定执行策略（预热强度、执行深度等）
4. 执行过程实时监控与自适应调整 - 监控执行过程，动态调整策略

与 round 220（主动服务闭环增强引擎）形成能力增强链，实现真正的一键式自动化。

Version: 1.0.0
"""

import os
import sys
import json
import argparse
import time
import threading
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

# 添加项目根目录到路径
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))

# 数据存储路径
DATA_DIR = os.path.join(PROJECT_ROOT, 'runtime', 'state')
LOGS_DIR = os.path.join(PROJECT_ROOT, 'runtime', 'logs')

# 版本
VERSION = "1.0.0"


def load_json_safe(filepath, default=None):
    """安全加载JSON文件"""
    if default is None:
        default = {}
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"[警告] 加载文件失败 {filepath}: {e}")
    return default


def save_json_safe(filepath, data):
    """安全保存JSON文件"""
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"[警告] 保存文件失败 {filepath}: {e}")
        return False


class FullAutoServiceExecutionEngine:
    """智能全自动化服务执行引擎"""

    def __init__(self):
        self.version = VERSION
        self.data_dir = DATA_DIR
        self.logs_dir = LOGS_DIR

        # 导入依赖引擎
        self._service_loop_available = False
        try:
            from active_service_loop_enhancer import ActiveServiceLoopEnhancer
            self.service_loop = ActiveServiceLoopEnhancer()
            self._service_loop_available = True
        except ImportError as e:
            print(f"[信息] 主动服务闭环增强引擎不可用: {e}")
            self._service_loop_available = False

        # 尝试导入其他引擎
        self._preheat_available = False
        self._scene_selector_available = False

        try:
            import service_preheat_engine as preheat_module
            self.preheat_module = preheat_module
            self._preheat_available = True
        except ImportError:
            pass

        try:
            from adaptive_scene_selector import AdaptiveSceneSelector
            self.scene_selector = AdaptiveSceneSelector()
            self._scene_selector_available = True
        except ImportError:
            pass

        # 执行状态跟踪
        self.execution_history_file = os.path.join(DATA_DIR, "full_auto_execution_history.json")
        self.current_execution = {}
        self.execution_lock = threading.Lock()

    def get_status(self) -> Dict[str, Any]:
        """获取引擎状态"""
        return {
            "version": self.version,
            "engines": {
                "active_service_loop": {
                    "available": self._service_loop_available,
                    "name": "主动服务闭环增强引擎 (round 220)"
                },
                "service_preheat": {
                    "available": self._preheat_available,
                    "name": "服务预热引擎 (round 219)"
                },
                "adaptive_scene_selector": {
                    "available": self._scene_selector_available,
                    "name": "自适应场景选择引擎 (round 215)"
                }
            },
            "integration_status": "ready" if self._service_loop_available else "limited",
            "capabilities": [
                "一键触发机制",
                "自动上下文准备",
                "智能执行决策",
                "实时监控与自适应调整",
                "完整闭环自动化"
            ]
        }

    def single_trigger(self, user_intent: str = "", context: Optional[Dict] = None) -> Dict[str, Any]:
        """一键触发机制 - 用户只需给出一个简单意图，引擎自动完成所有准备工作和执行

        Args:
            user_intent: 用户的简单意图描述（如"帮我处理工作"、"检查下系统"）
            context: 可选的额外上下文信息

        Returns:
            执行结果字典
        """
        result = {
            "timestamp": datetime.now().isoformat(),
            "intent": user_intent,
            "steps": [],
            "final_status": "success",
            "error": None,
            "execution_id": None
        }

        # 生成执行ID
        execution_id = f"auto_{int(time.time())}"
        result["execution_id"] = execution_id

        try:
            # 步骤 1: 自动上下文准备
            step1 = self._auto_prepare_context(context or {})
            result["steps"].append(step1)

            # 步骤 2: 智能执行决策
            step2 = self._smart_decide(user_intent, step1.get("context", {}))
            result["steps"].append(step2)

            # 步骤 3: 执行服务闭环
            step3 = self._execute_with_monitoring(step2.get("execution_plan", {}))
            result["steps"].append(step3)

            # 步骤 4: 自适应调整（如果需要）
            if step3.get("status") == "needs_adjustment":
                step4 = self._adaptive_adjust(step3, step2.get("execution_plan", {}))
                result["steps"].append(step4)

            # 保存执行历史
            self._save_execution_history(result)

        except Exception as e:
            result["final_status"] = "error"
            result["error"] = str(e)

        return result

    def _auto_prepare_context(self, context: Dict) -> Dict[str, Any]:
        """自动准备执行上下文"""
        step_result = {
            "step": "context_preparation",
            "status": "completed",
            "context": {}
        }

        try:
            # 收集系统状态
            system_context = self._collect_system_context()
            step_result["context"]["system"] = system_context

            # 收集用户行为上下文
            user_context = self._collect_user_context()
            step_result["context"]["user"] = user_context

            # 收集时间上下文
            time_context = self._collect_time_context()
            step_result["context"]["time"] = time_context

            # 合并额外上下文
            if context:
                step_result["context"].update(context)

        except Exception as e:
            step_result["status"] = "error"
            step_result["error"] = str(e)

        return step_result

    def _collect_system_context(self) -> Dict[str, Any]:
        """收集系统状态上下文"""
        context = {
            "timestamp": datetime.now().isoformat()
        }

        # 尝试获取系统资源状态
        try:
            import psutil
            context["cpu_percent"] = psutil.cpu_percent(interval=0.1)
            context["memory_percent"] = psutil.virtual_memory().percent
            context["disk_percent"] = psutil.disk_usage('/').percent
        except ImportError:
            pass

        # 尝试获取活跃窗口
        try:
            from window_tool import get_foreground_window_info
            context["active_window"] = get_foreground_window_info()
        except:
            pass

        return context

    def _collect_user_context(self) -> Dict[str, Any]:
        """收集用户行为上下文"""
        context = {}

        # 尝试从历史记录中获取用户行为模式
        history_file = os.path.join(DATA_DIR, "user_behavior_history.json")
        history = load_json_safe(history_file, {"interactions": []})

        # 获取最近的用户交互
        recent = history.get("interactions", [])[-10:] if history.get("interactions") else []
        context["recent_interactions"] = [
            {"intent": i.get("intent"), "timestamp": i.get("timestamp")}
            for i in recent
        ]

        return context

    def _collect_time_context(self) -> Dict[str, Any]:
        """收集时间上下文"""
        now = datetime.now()
        return {
            "hour": now.hour,
            "minute": now.minute,
            "weekday": now.weekday(),
            "is_weekend": now.weekday() >= 5,
            "time_of_day": self._get_time_of_day(now.hour)
        }

    def _get_time_of_day(self, hour: int) -> str:
        """获取时段描述"""
        if 5 <= hour < 9:
            return "early_morning"
        elif 9 <= hour < 12:
            return "morning"
        elif 12 <= hour < 14:
            return "noon"
        elif 14 <= hour < 18:
            return "afternoon"
        elif 18 <= hour < 22:
            return "evening"
        else:
            return "night"

    def _smart_decide(self, user_intent: str, context: Dict) -> Dict[str, Any]:
        """智能执行决策 - 基于上下文决定执行策略"""
        step_result = {
            "step": "smart_decision",
            "status": "completed",
            "execution_plan": {},
            "reasoning": []
        }

        try:
            # 分析意图
            intent_analysis = self._analyze_intent(user_intent, context)
            step_result["reasoning"].append(f"意图分析: {intent_analysis.get('intent_type', 'unknown')}")

            # 确定执行深度
            execution_depth = self._determine_execution_depth(context)
            step_result["reasoning"].append(f"执行深度: {execution_depth}")

            # 确定预热策略
            preheat_level = self._determine_preheat_level(context, execution_depth)
            step_result["reasoning"].append(f"预热级别: {preheat_level}")

            # 生成执行计划
            plan = {
                "intent": user_intent,
                "intent_type": intent_analysis.get("intent_type", "general"),
                "execution_depth": execution_depth,
                "preheat_level": preheat_level,
                "auto_execute": execution_depth == "full",
                "auto_preheat": preheat_level != "none"
            }
            step_result["execution_plan"] = plan

        except Exception as e:
            step_result["status"] = "error"
            step_result["error"] = str(e)

        return step_result

    def _analyze_intent(self, intent: str, context: Dict) -> Dict[str, Any]:
        """分析用户意图"""
        intent_lower = intent.lower()

        # 意图类型识别
        if any(kw in intent_lower for kw in ["工作", "处理", "完成", "提交"]):
            return {"intent_type": "work", "urgency": "high"}
        elif any(kw in intent_lower for kw in ["检查", "查看", "状态", "报告"]):
            return {"intent_type": "check", "urgency": "low"}
        elif any(kw in intent_lower for kw in ["优化", "提升", "改善"]):
            return {"intent_type": "optimize", "urgency": "medium"}
        elif any(kw in intent_lower for kw in ["学习", "分析", "统计"]):
            return {"intent_type": "analysis", "urgency": "medium"}
        else:
            return {"intent_type": "general", "urgency": "medium"}

    def _determine_execution_depth(self, context: Dict) -> str:
        """确定执行深度"""
        system = context.get("system", {})
        user = context.get("user", {})

        # 系统资源充足时可以进行更深的执行
        cpu = system.get("cpu_percent", 50)
        memory = system.get("memory_percent", 50)

        if cpu < 50 and memory < 70:
            return "full"  # 完全自动执行
        elif cpu < 80 and memory < 85:
            return "partial"  # 部分自动执行
        else:
            return "light"  # 轻度执行，只做建议

    def _determine_preheat_level(self, context: Dict, execution_depth: str) -> str:
        """确定预热级别"""
        if execution_depth == "full":
            return "aggressive"  # 积极预热
        elif execution_depth == "partial":
            return "normal"  # 正常预热
        else:
            return "light"  # 轻度预热

    def _execute_with_monitoring(self, plan: Dict) -> Dict[str, Any]:
        """执行服务并监控"""
        step_result = {
            "step": "execution_with_monitoring",
            "status": "completed",
            "execution_results": []
        }

        try:
            if not self._service_loop_available:
                step_result["status"] = "skipped"
                step_result["message"] = "依赖引擎不可用，跳过执行"
                return step_result

            # 执行完整闭环
            auto_preheat = plan.get("auto_preheat", True)
            auto_execute = plan.get("execution_depth") == "full"

            execution_result = self.service_loop.execute_complete_loop(
                auto_preheat=auto_preheat,
                auto_execute=auto_execute
            )

            step_result["execution_results"] = execution_result.get("steps", [])

            # 检查是否需要调整
            if execution_result.get("final_status") == "error":
                step_result["status"] = "needs_adjustment"
                step_result["needs_adjustment_reason"] = execution_result.get("error")

        except Exception as e:
            step_result["status"] = "needs_adjustment"
            step_result["needs_adjustment_reason"] = str(e)

        return step_result

    def _adaptive_adjust(self, execution_result: Dict, original_plan: Dict) -> Dict[str, Any]:
        """自适应调整 - 根据执行结果动态调整策略"""
        step_result = {
            "step": "adaptive_adjustment",
            "status": "completed",
            "adjustments": []
        }

        try:
            # 分析错误原因
            error_reason = execution_result.get("needs_adjustment_reason", "")

            if "preheat" in error_reason.lower():
                # 预热失败，降低预热级别重试
                new_plan = original_plan.copy()
                new_plan["preheat_level"] = "light"
                new_plan["auto_preheat"] = False
                step_result["adjustments"].append({
                    "type": "preheat_reduction",
                    "description": "降低预热级别重试"
                })

                # 执行调整后的计划
                retry_result = self.service_loop.execute_complete_loop(
                    auto_preheat=False,
                    auto_execute=new_plan.get("auto_execute", False)
                )
                step_result["retry_result"] = retry_result

            elif "execution" in error_reason.lower():
                # 执行失败，改为建议模式
                step_result["adjustments"].append({
                    "type": "fallback_to_suggestion",
                    "description": "改为提供建议而非自动执行"
                })

            step_result["status"] = "completed"

        except Exception as e:
            step_result["status"] = "error"
            step_result["error"] = str(e)

        return step_result

    def _save_execution_history(self, result: Dict):
        """保存执行历史"""
        history = load_json_safe(self.execution_history_file, {"executions": []})
        history["executions"].append(result)
        # 只保留最近 100 条
        history["executions"] = history["executions"][-100:]
        save_json_safe(self.execution_history_file, history)

    def get_execution_history(self, limit: int = 10) -> Dict[str, Any]:
        """获取执行历史"""
        history = load_json_safe(self.execution_history_file, {"executions": []})
        return {
            "total": len(history.get("executions", [])),
            "recent": history.get("executions", [])[-limit:]
        }


def main():
    """主函数 - 命令行入口"""
    parser = argparse.ArgumentParser(
        description="智能全自动化服务执行引擎 - 实现真正的一键式自动服务执行"
    )
    parser.add_argument("command", nargs="?", default="status",
                        help="命令: status, trigger, history")
    parser.add_argument("--intent", "-i", type=str, default="",
                        help="用户意图描述")
    parser.add_argument("--version", "-v", action="store_true",
                        help="显示版本")

    args = parser.parse_args()

    engine = FullAutoServiceExecutionEngine()

    if args.version:
        print(f"智能全自动化服务执行引擎 v{VERSION}")
        return

    if args.command == "status":
        status = engine.get_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))

    elif args.command == "trigger":
        result = engine.single_trigger(args.intent)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "history":
        history = engine.get_execution_history()
        print(json.dumps(history, ensure_ascii=False, indent=2))

    else:
        print(f"未知命令: {args.command}")
        print("可用命令: status, trigger, history")
        parser.print_help()


if __name__ == "__main__":
    main()