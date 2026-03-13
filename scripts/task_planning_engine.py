#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
智能任务规划与执行编排引擎
让系统能够理解用户的高级目标，自动分解为多个引擎任务并协调执行
提供真正的一站式智能服务
"""
import os
import json
import re
import subprocess
from datetime import datetime
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field


@dataclass
class TaskStep:
    """任务步骤"""
    id: str
    engine: str  # 需要调用的引擎名称
    action: str  # 引擎动作
    params: Dict[str, Any] = field(default_factory=dict)
    description: str = ""
    depends_on: List[str] = field(default_factory=list)  # 依赖的前置步骤
    status: str = "pending"  # pending/running/completed/failed


@dataclass
class TaskPlan:
    """任务计划"""
    id: str
    user_goal: str  # 用户原始目标
    steps: List[TaskStep] = field(default_factory=list)
    status: str = "planning"  # planning/ready/running/completed/failed
    created_at: str = None
    completed_at: str = None


@dataclass
class ExecutionResult:
    """执行结果"""
    plan_id: str
    status: str  # success/partial/failed
    step_results: List[Dict[str, Any]] = field(default_factory=list)
    error: str = None
    execution_time: float = 0.0


class TaskPlanningEngine:
    """智能任务规划与执行编排引擎"""

    # 引擎注册表 - 记录所有可用引擎及其能力
    ENGINE_REGISTRY = {
        # 核心基础引擎
        "screenshot": {"module": "screenshot_tool", "capabilities": ["截图", "获取屏幕"]},
        "vision": {"module": "vision_proxy", "capabilities": ["图像理解", "坐标提取"]},
        "mouse": {"module": "mouse_tool", "capabilities": ["点击", "移动", "拖拽"]},
        "keyboard": {"module": "keyboard_tool", "capabilities": ["输入", "按键", "快捷键"]},
        "window": {"module": "window_tool", "capabilities": ["窗口管理", "激活", "最大化"]},
        "process": {"module": "process_tool", "capabilities": ["进程管理"]},
        "file": {"module": "file_tool", "capabilities": ["文件操作"]},
        "clipboard": {"module": "clipboard_tool", "capabilities": ["剪贴板"]},
        # 智能引擎
        "workflow": {"module": "workflow_engine", "capabilities": ["工作流执行", "多步骤任务"]},
        "meeting": {"module": "meeting_assistant_engine", "capabilities": ["会议管理", "会议纪要"]},
        "notification": {"module": "proactive_notification_engine", "capabilities": ["通知", "提醒"]},
        "memory": {"module": "long_term_memory_engine", "capabilities": ["记忆", "目标跟踪"]},
        "learning": {"module": "adaptive_learning_engine", "capabilities": ["学习", "适应"]},
        "reasoning": {"module": "enhanced_knowledge_reasoning_engine", "capabilities": ["推理", "分析"]},
        "insight": {"module": "data_insight_engine", "capabilities": ["数据分析", "洞察"]},
        "diagnostic": {"module": "system_diagnostic_engine", "capabilities": ["诊断", "问题检测"]},
        "self_healing": {"module": "self_healing_engine", "capabilities": ["自愈", "自动修复"]},
        # 业务引擎
        "ihaier": {"module": "ihaier_integration", "capabilities": ["办公平台操作"]},
        "browser": {"module": "browser_tool", "capabilities": ["浏览器操作"]},
    }

    # 意图到引擎映射
    INTENT_ENGINE_MAPPING = {
        # 会议相关
        "会议": ["meeting", "notification"],
        "会议纪要": ["meeting", "memory"],
        # 文件相关
        "整理文件": ["file", "workflow"],
        "搜索文件": ["file"],
        # 办公相关
        "办公": ["ihaier", "workflow"],
        "绩效": ["ihaier"],
        # 数据相关
        "分析数据": ["insight", "reasoning"],
        "数据洞察": ["insight"],
        # 系统相关
        "诊断": ["diagnostic", "self_healing"],
        "健康检查": ["diagnostic"],
        # 学习相关
        "学习": ["learning"],
        "适应": ["learning"],
        # 通知相关
        "提醒": ["notification"],
        "通知": ["notification"],
    }

    def __init__(self):
        self.task_history_file = "runtime/state/task_planning_history.json"
        self.current_plan: Optional[TaskPlan] = None
        self._ensure_history_file()

    def _ensure_history_file(self):
        """确保历史记录文件存在"""
        os.makedirs(os.path.dirname(self.task_history_file), exist_ok=True)
        if not os.path.exists(self.task_history_file):
            with open(self.task_history_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)

    def analyze_goal(self, user_goal: str) -> Dict[str, Any]:
        """
        分析用户目标，确定需要哪些引擎协同工作

        Args:
            user_goal: 用户的高级目标描述

        Returns:
            分析结果，包含需要的引擎列表和任务分解
        """
        # 关键词匹配 - 识别需要的引擎
        needed_engines = []
        for keyword, engines in self.INTENT_ENGINE_MAPPING.items():
            if keyword in user_goal:
                for engine in engines:
                    if engine not in needed_engines:
                        needed_engines.append(engine)

        # 如果没有匹配到任何引擎，默认使用基础引擎
        if not needed_engines:
            needed_engines = ["workflow"]

        # 分析任务复杂度
        complexity = self._analyze_complexity(user_goal)

        # 生成任务步骤
        steps = self._generate_steps(user_goal, needed_engines)

        return {
            "user_goal": user_goal,
            "needed_engines": needed_engines,
            "complexity": complexity,
            "steps": steps,
            "estimated_steps": len(steps)
        }

    def _analyze_complexity(self, user_goal: str) -> str:
        """分析任务复杂度"""
        # 简单任务：单一动作
        if any(kw in user_goal for kw in ["打开", "关闭", "截图", "发送"]):
            return "simple"
        # 中等任务：多步骤但顺序执行
        elif any(kw in user_goal for kw in ["整理", "分析", "检查", "监控"]):
            return "medium"
        # 复杂任务：需要多引擎协同
        else:
            return "complex"

    def _generate_steps(self, user_goal: str, needed_engines: List[str]) -> List[Dict[str, Any]]:
        """生成任务步骤"""
        steps = []
        step_id = 1

        # 为每个引擎生成相应步骤
        for engine in needed_engines:
            if engine == "meeting":
                steps.append({
                    "id": f"step_{step_id}",
                    "engine": "meeting",
                    "action": "list",
                    "description": "查看当前会议",
                    "params": {}
                })
                step_id += 1

            elif engine == "notification":
                steps.append({
                    "id": f"step_{step_id}",
                    "engine": "notification",
                    "action": "send",
                    "description": "发送通知",
                    "params": {"message": f"任务已完成: {user_goal}"}
                })
                step_id += 1

            elif engine == "workflow":
                steps.append({
                    "id": f"step_{step_id}",
                    "engine": "workflow",
                    "action": "execute",
                    "description": f"执行工作流: {user_goal}",
                    "params": {"goal": user_goal}
                })
                step_id += 1

            elif engine == "file":
                # 智能判断是整理还是搜索
                if "整理" in user_goal:
                    steps.append({
                        "id": f"step_{step_id}",
                        "engine": "file",
                        "action": "organize",
                        "description": "整理文件",
                        "params": {}
                    })
                else:
                    steps.append({
                        "id": f"step_{step_id}",
                        "engine": "file",
                        "action": "search",
                        "description": "搜索文件",
                        "params": {"pattern": user_goal}
                    })
                step_id += 1

            elif engine == "insight":
                steps.append({
                    "id": f"step_{step_id}",
                    "engine": "insight",
                    "action": "analyze",
                    "description": "数据分析",
                    "params": {"goal": user_goal}
                })
                step_id += 1

            elif engine == "diagnostic":
                steps.append({
                    "id": f"step_{step_id}",
                    "engine": "diagnostic",
                    "action": "diagnose",
                    "description": "系统诊断",
                    "params": {}
                })
                step_id += 1

            elif engine == "learning":
                steps.append({
                    "id": f"step_{step_id}",
                    "engine": "learning",
                    "action": "learn",
                    "description": "学习用户行为",
                    "params": {"goal": user_goal}
                })
                step_id += 1

            elif engine == "ihaier":
                steps.append({
                    "id": f"step_{step_id}",
                    "engine": "ihaier",
                    "action": "operate",
                    "description": "办公平台操作",
                    "params": {"goal": user_goal}
                })
                step_id += 1

        # 如果没有生成任何步骤，添加默认步骤
        if not steps:
            steps.append({
                "id": f"step_{step_id}",
                "engine": "workflow",
                "action": "execute",
                "description": f"执行任务: {user_goal}",
                "params": {"goal": user_goal}
            })

        return steps

    def create_plan(self, user_goal: str) -> TaskPlan:
        """
        创建任务计划

        Args:
            user_goal: 用户的高级目标描述

        Returns:
            任务计划对象
        """
        analysis = self.analyze_goal(user_goal)

        plan = TaskPlan(
            id=f"plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            user_goal=user_goal,
            status="ready",
            created_at=datetime.now().isoformat()
        )

        # 将分析结果转换为任务步骤
        for step_data in analysis["steps"]:
            plan.steps.append(TaskStep(
                id=step_data["id"],
                engine=step_data["engine"],
                action=step_data["action"],
                params=step_data.get("params", {}),
                description=step_data["description"]
            ))

        self.current_plan = plan
        return plan

    async def execute_plan(self, plan: TaskPlan) -> ExecutionResult:
        """
        执行任务计划

        Args:
            plan: 任务计划

        Returns:
            执行结果
        """
        start_time = datetime.now()
        result = ExecutionResult(plan_id=plan.id, status="success")
        step_results = []

        for step in plan.steps:
            try:
                # 执行步骤
                step_result = await self._execute_step(step)
                step_results.append({
                    "step_id": step.id,
                    "engine": step.engine,
                    "status": "success",
                    "result": step_result
                })
                step.status = "completed"

            except Exception as e:
                step_results.append({
                    "step_id": step.id,
                    "engine": step.engine,
                    "status": "failed",
                    "error": str(e)
                })
                step.status = "failed"
                result.status = "partial"
                result.error = f"Step {step.id} failed: {str(e)}"
                break

        result.step_results = step_results
        result.execution_time = (datetime.now() - start_time).total_seconds()
        plan.status = "completed" if result.status == "success" else "failed"
        plan.completed_at = datetime.now().isoformat()

        # 保存到历史
        self._save_to_history(plan, result)

        return result

    async def _execute_step(self, step: TaskStep) -> Any:
        """执行单个任务步骤"""
        engine = step.engine
        action = step.action
        params = step.params

        # 根据引擎类型执行相应操作
        if engine == "meeting":
            return await self._execute_meeting_action(action, params)
        elif engine == "notification":
            return await self._execute_notification_action(action, params)
        elif engine == "workflow":
            return await self._execute_workflow_action(action, params)
        elif engine == "file":
            return await self._execute_file_action(action, params)
        elif engine == "insight":
            return await self._execute_insight_action(action, params)
        elif engine == "diagnostic":
            return await self._execute_diagnostic_action(action, params)
        elif engine == "learning":
            return await self._execute_learning_action(action, params)
        else:
            return {"status": "skipped", "message": f"Engine {engine} not implemented for execution"}

    async def _execute_meeting_action(self, action: str, params: Dict) -> Any:
        """执行会议引擎动作"""
        try:
            result = subprocess.run(
                ["python", "scripts/do.py", "会议"],
                capture_output=True,
                text=True,
                timeout=30
            )
            return {"output": result.stdout, "status": "success"}
        except Exception as e:
            return {"error": str(e), "status": "failed"}

    async def _execute_notification_action(self, action: str, params: Dict) -> Any:
        """执行通知引擎动作"""
        message = params.get("message", "任务完成")
        try:
            result = subprocess.run(
                ["python", "scripts/do.py", f"通知 {message}"],
                capture_output=True,
                text=True,
                timeout=30
            )
            return {"output": result.stdout, "status": "success"}
        except Exception as e:
            return {"error": str(e), "status": "failed"}

    async def _execute_workflow_action(self, action: str, params: Dict) -> Any:
        """执行工作流引擎动作"""
        goal = params.get("goal", "")
        try:
            result = subprocess.run(
                ["python", "scripts/do.py", goal],
                capture_output=True,
                text=True,
                timeout=60
            )
            return {"output": result.stdout, "status": "success"}
        except Exception as e:
            return {"error": str(e), "status": "failed"}

    async def _execute_file_action(self, action: str, params: Dict) -> Any:
        """执行文件引擎动作"""
        pattern = params.get("pattern", "")
        try:
            result = subprocess.run(
                ["python", "scripts/do.py", f"搜索文件 {pattern}"],
                capture_output=True,
                text=True,
                timeout=30
            )
            return {"output": result.stdout, "status": "success"}
        except Exception as e:
            return {"error": str(e), "status": "failed"}

    async def _execute_insight_action(self, action: str, params: Dict) -> Any:
        """执行数据洞察引擎动作"""
        try:
            result = subprocess.run(
                ["python", "scripts/do.py", "数据洞察"],
                capture_output=True,
                text=True,
                timeout=60
            )
            return {"output": result.stdout, "status": "success"}
        except Exception as e:
            return {"error": str(e), "status": "failed"}

    async def _execute_diagnostic_action(self, action: str, params: Dict) -> Any:
        """执行诊断引擎动作"""
        try:
            result = subprocess.run(
                ["python", "scripts/do.py", "系统诊断"],
                capture_output=True,
                text=True,
                timeout=60
            )
            return {"output": result.stdout, "status": "success"}
        except Exception as e:
            return {"error": str(e), "status": "failed"}

    async def _execute_learning_action(self, action: str, params: Dict) -> Any:
        """执行学习引擎动作"""
        try:
            result = subprocess.run(
                ["python", "scripts/do.py", "学习统计"],
                capture_output=True,
                text=True,
                timeout=30
            )
            return {"output": result.stdout, "status": "success"}
        except Exception as e:
            return {"error": str(e), "status": "failed"}

    def _save_to_history(self, plan: TaskPlan, result: ExecutionResult):
        """保存执行历史"""
        try:
            with open(self.task_history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)

            history.append({
                "plan_id": plan.id,
                "user_goal": plan.user_goal,
                "status": result.status,
                "steps_count": len(plan.steps),
                "execution_time": result.execution_time,
                "created_at": plan.created_at,
                "completed_at": plan.completed_at
            })

            # 只保留最近 100 条记录
            history = history[-100:]

            with open(self.task_history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"Failed to save history: {e}")

    def get_plan_status(self, plan_id: str = None) -> Dict[str, Any]:
        """获取任务计划状态"""
        if plan_id and self.current_plan and self.current_plan.id == plan_id:
            plan = self.current_plan
        else:
            plan = self.current_plan

        if not plan:
            return {"status": "no_plan", "message": "No active plan"}

        return {
            "plan_id": plan.id,
            "user_goal": plan.user_goal,
            "status": plan.status,
            "steps": [
                {
                    "id": s.id,
                    "engine": s.engine,
                    "description": s.description,
                    "status": s.status
                }
                for s in plan.steps
            ],
            "created_at": plan.created_at,
            "completed_at": plan.completed_at
        }

    def get_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取执行历史"""
        try:
            with open(self.task_history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
            return history[-limit:] if limit > 0 else history
        except Exception:
            return []

    def get_available_engines(self) -> Dict[str, Any]:
        """获取可用引擎列表"""
        return self.ENGINE_REGISTRY


# CLI 接口
def main():
    """CLI 入口"""
    import sys

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python task_planning_engine.py analyze <用户目标>")
        print("  python task_planning_engine.py plan <用户目标>")
        print("  python task_planning_engine.py execute <用户目标>")
        print("  python task_planning_engine.py status")
        print("  python task_planning_engine.py history [数量]")
        print("  python task_planning_engine.py engines")
        sys.exit(1)

    engine = TaskPlanningEngine()
    command = sys.argv[1]

    if command == "analyze" and len(sys.argv) > 2:
        user_goal = " ".join(sys.argv[2:])
        result = engine.analyze_goal(user_goal)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "plan" and len(sys.argv) > 2:
        user_goal = " ".join(sys.argv[2:])
        plan = engine.create_plan(user_goal)
        print(json.dumps({
            "plan_id": plan.id,
            "user_goal": plan.user_goal,
            "status": plan.status,
            "steps": [
                {
                    "id": s.id,
                    "engine": s.engine,
                    "action": s.action,
                    "description": s.description
                }
                for s in plan.steps
            ]
        }, ensure_ascii=False, indent=2))

    elif command == "execute" and len(sys.argv) > 2:
        user_goal = " ".join(sys.argv[2:])
        plan = engine.create_plan(user_goal)
        print(f"Created plan: {plan.id}")
        print(f"Goal: {plan.user_goal}")
        print(f"Steps: {len(plan.steps)}")
        print("\nNote: Async execution requires integration with event loop")
        print(f"Plan ready for execution with ID: {plan.id}")

    elif command == "status":
        status = engine.get_plan_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))

    elif command == "history":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        history = engine.get_history(limit)
        print(json.dumps(history, ensure_ascii=False, indent=2))

    elif command == "engines":
        engines = engine.get_available_engines()
        print(json.dumps(engines, ensure_ascii=False, indent=2))

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()