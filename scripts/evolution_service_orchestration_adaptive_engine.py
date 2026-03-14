"""
智能全场景服务协同编排与自适应执行引擎
(Evolution Service Orchestration Adaptive Engine)

功能：
1. 模糊需求深度理解（自然语言解析+意图推断+上下文推断）
2. 任务自动拆分与子任务编排
3. 多引擎协同执行与实时监控
4. 自适应执行策略调整（失败重试、路径优化、资源调度）
5. 端到端闭环执行与结果反馈
6. 与 do.py 深度集成

继承能力：
- unified_service_hub (round 202) - 统一服务入口
- intelligent_service_fusion_engine (round 206) - 智能服务融合
- cross_engine_task_planner (round 152) - 跨引擎任务规划

版本：1.0.0
"""

import json
import os
import sys
import subprocess
import asyncio
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"


class ExecutionStrategy(Enum):
    """执行策略"""
    SEQUENTIAL = "sequential"  # 顺序执行
    PARALLEL = "parallel"     # 并行执行
    ADAPTIVE = "adaptive"     # 自适应执行


@dataclass
class Task:
    """任务定义"""
    id: str
    name: str
    description: str
    engine: str  # 使用的引擎
    params: Dict[str, Any] = field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    execution_time: float = 0.0

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "engine": self.engine,
            "params": self.params,
            "status": self.status.value,
            "result": self.result,
            "error": self.error,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "execution_time": self.execution_time
        }


@dataclass
class ExecutionContext:
    """执行上下文"""
    user_input: str
    intent: Optional[str] = None
    entities: Dict[str, Any] = field(default_factory=dict)
    tasks: List[Task] = field(default_factory=list)
    strategy: ExecutionStrategy = ExecutionStrategy.SEQUENTIAL
    state: Dict[str, Any] = field(default_factory=dict)
    start_time: float = field(default_factory=time.time)
    completed_tasks: List[Task] = field(default_factory=list)


class ServiceOrchestrationAdaptiveEngine:
    """智能服务协同编排与自适应执行引擎"""

    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.scripts_dir = self.project_root / "scripts"
        self.state_dir = self.project_root / "runtime" / "state"

        # 引擎能力映射表
        self.engine_capabilities = self._load_engine_capabilities()

        # 执行历史缓存
        self.execution_history: List[Dict] = []

        # 已加载的引擎模块缓存
        self.engine_cache: Dict[str, Any] = {}

    def _load_engine_capabilities(self) -> Dict[str, Dict]:
        """加载引擎能力映射表"""
        return {
            # 文件操作
            "file_read": {"engines": ["file_tool", "file_manager"], "capabilities": ["read", "list"]},
            "file_write": {"engines": ["file_tool", "file_manager"], "capabilities": ["write", "create"]},
            "file_search": {"engines": ["file_tool", "file_manager"], "capabilities": ["search", "find"]},

            # 应用操作
            "open_app": {"engines": ["launcher", "window_tool"], "capabilities": ["open", "activate"]},
            "close_app": {"engines": ["process_tool", "window_tool"], "capabilities": ["close", "kill"]},

            # 浏览器操作
            "browser_navigate": {"engines": ["launch_browser"], "capabilities": ["navigate", "open_url"]},
            "browser_click": {"engines": ["mouse_tool", "keyboard_tool"], "capabilities": ["click", "type"]},

            # 截图与视觉
            "screenshot": {"engines": ["screenshot_tool"], "capabilities": ["capture", "save"]},
            "vision_understand": {"engines": ["vision_proxy"], "capabilities": ["analyze", "describe"]},
            "vision_locate": {"engines": ["vision_coords"], "capabilities": ["locate", "find_coords"]},

            # 鼠标键盘
            "mouse_click": {"engines": ["mouse_tool"], "capabilities": ["click", "right_click", "double_click"]},
            "mouse_drag": {"engines": ["mouse_tool"], "capabilities": ["drag"]},
            "keyboard_type": {"engines": ["keyboard_tool"], "capabilities": ["type", "paste"]},
            "keyboard_shortcut": {"engines": ["keyboard_tool"], "capabilities": ["key", "shortcut"]},

            # 系统操作
            "system_info": {"engines": ["system_health_check", "network_tool"], "capabilities": ["info", "status"]},
            "system_control": {"engines": ["power_tool", "focus_reminder"], "capabilities": ["sleep", "reboot", "remind"]},

            # 通知与消息
            "send_notification": {"engines": ["notification_tool"], "capabilities": ["show", "send"]},
            "ihaier_message": {"engines": ["window_tool", "mouse_tool", "keyboard_tool"], "capabilities": ["send_message"]},

            # 工作流执行
            "run_plan": {"engines": ["workflow_engine", "run_plan"], "capabilities": ["execute", "run"]},

            # 进化能力
            "evolution_analyze": {"engines": ["intelligent_evolution_engine"], "capabilities": ["analyze", "plan"]},
            "knowledge_reasoning": {"engines": ["knowledge_graph", "enhanced_knowledge_reasoning_engine"], "capabilities": ["reason", "infer"]},
        }

    def understand_ambiguous_requirement(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        """
        深度理解模糊需求
        1. 自然语言解析
        2. 意图推断
        3. 上下文推断
        """
        # 构建理解提示
        understanding_prompt = f"""分析用户输入，提取关键信息：

用户输入：{user_input}

请提取：
1. 核心意图（用户想要做什么）
2. 涉及的操作对象（文件、应用、数据等）
3. 操作类型（读取、发送、打开等）
4. 约束条件（时间、格式、范围等）
5. 可能的上下文（用户当前状态、历史交互等）

返回 JSON 格式：
{{
    "intent": "核心意图",
    "objects": ["操作对象列表"],
    "operations": ["操作类型列表"],
    "constraints": {{"约束条件"}},
    "context_hints": ["上下文提示"],
    "confidence": 0.0-1.0
}}
"""
        # 使用简单的规则解析作为 fallback
        # 在实际环境中可以调用 LLM 进行深度理解
        result = self._rule_based_understanding(user_input, context)

        return result

    def _rule_based_understanding(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        """基于规则的模糊需求理解"""
        user_input_lower = user_input.lower()

        # 意图关键词映射
        intent_keywords = {
            "打开": ["open", "启动", "运行", "launch"],
            "关闭": ["close", "quit", "exit", "stop"],
            "读取": ["read", "查看", "看", "获取"],
            "写入": ["write", "保存", "存", "新建", "创建"],
            "发送": ["send", "发", "传递"],
            "搜索": ["search", "找", "搜", "查询"],
            "执行": ["execute", "运行", "跑", "执行"],
            "截图": ["screenshot", "截屏", "截图"],
            "操作": ["click", "点击", "操作"],
        }

        intent = "unknown"
        for intent_key, keywords in intent_keywords.items():
            if any(kw in user_input_lower for kw in keywords):
                intent = intent_key
                break

        # 操作对象识别
        objects = []
        if "文件" in user_input or "folder" in user_input_lower:
            objects.append("file")
        if "应用" in user_input or "app" in user_input_lower:
            objects.append("application")
        if "浏览器" in user_input or "browser" in user_input_lower or "网站" in user_input:
            objects.append("browser")
        if "消息" in user_input or "消息" in user_input or "微信" in user_input or "ihaier" in user_input_lower:
            objects.append("message")
        if "截图" in user_input or "屏幕" in user_input:
            objects.append("screenshot")

        # 操作类型推断
        operations = []
        if intent in ["打开", "关闭"]:
            operations.append("control")
        elif intent in ["读取"]:
            operations.append("read")
        elif intent in ["写入"]:
            operations.append("write")
        elif intent in ["发送"]:
            operations.append("send")
        elif intent in ["搜索"]:
            operations.append("search")
        elif intent in ["截图"]:
            operations.append("capture")

        return {
            "intent": intent,
            "objects": objects,
            "operations": operations,
            "constraints": {},
            "context_hints": [context] if context else [],
            "confidence": 0.6 if intent != "unknown" else 0.3
        }

    def decompose_task(self, understanding: Dict, context: Optional[Dict] = None) -> List[Task]:
        """
        任务自动拆分与子任务编排
        """
        tasks = []
        intent = understanding.get("intent", "unknown")
        objects = understanding.get("objects", [])
        operations = understanding.get("operations", [])

        task_id = 1

        # 根据意图-对象组合生成任务
        for obj in objects:
            for op in operations:
                task = self._create_task_from_intent_object(
                    task_id, intent, obj, op, understanding, context
                )
                if task:
                    tasks.append(task)
                    task_id += 1

        # 如果没有生成任务，创建一个通用理解任务
        if not tasks:
            tasks.append(Task(
                id="task_1",
                name="理解用户需求",
                description=f"理解并执行用户请求：{understanding.get('intent', 'unknown')}",
                engine="unified_service_hub",
                params={"understanding": understanding}
            ))

        return tasks

    def _create_task_from_intent_object(
        self, task_id: int, intent: str, obj: str, op: str,
        understanding: Dict, context: Optional[Dict]
    ) -> Optional[Task]:
        """根据意图和对象创建任务"""

        # 映射表：intent+object -> engine
        intent_object_to_engine = {
            ("打开", "application"): ("launcher", {"action": "open"}),
            ("打开", "browser"): ("launch_browser", {"action": "open_url"}),
            ("读取", "file"): ("file_tool", {"action": "read"}),
            ("写入", "file"): ("file_tool", {"action": "write"}),
            ("搜索", "file"): ("file_tool", {"action": "search"}),
            ("发送", "message"): ("window_tool", {"action": "send_message"}),
            ("截图", "screenshot"): ("screenshot_tool", {"action": "capture"}),
            ("关闭", "application"): ("process_tool", {"action": "close"}),
        }

        key = (intent, obj)
        if key in intent_object_to_engine:
            engine, params = intent_object_to_engine[key]
            return Task(
                id=f"task_{task_id}",
                name=f"{intent}{obj}",
                description=f"{intent} {obj}",
                engine=engine,
                params={**params, "understanding": understanding, "context": context or {}}
            )

        return None

    def select_optimal_engines(self, tasks: List[Task]) -> List[Task]:
        """智能选择最优引擎组合"""
        for task in tasks:
            if task.engine in self.engine_capabilities:
                # 已有映射，直接使用
                continue

            # 根据任务描述推断引擎
            desc_lower = task.description.lower()
            if "打开" in task.description or "启动" in task.description:
                task.engine = "launcher"
            elif "读取" in task.description or "查看" in task.description:
                task.engine = "file_tool"
            elif "截图" in task.description:
                task.engine = "screenshot_tool"
            elif "点击" in task.description:
                task.engine = "mouse_tool"
            elif "输入" in task.description:
                task.engine = "keyboard_tool"
            else:
                task.engine = "unified_service_hub"  # 默认使用统一服务

        return tasks

    def execute_task(self, task: Task) -> Tuple[bool, Any, Optional[str]]:
        """执行单个任务"""
        start_time = time.time()
        task.status = TaskStatus.RUNNING

        try:
            # 根据引擎类型执行任务
            if task.engine == "unified_service_hub":
                result = self._execute_via_unified_service(task)
            elif task.engine == "launcher":
                result = self._execute_launcher(task)
            elif task.engine == "file_tool":
                result = self._execute_file_tool(task)
            elif task.engine == "screenshot_tool":
                result = self._execute_screenshot(task)
            elif task.engine == "mouse_tool":
                result = self._execute_mouse(task)
            elif task.engine == "keyboard_tool":
                result = self._execute_keyboard(task)
            elif task.engine == "run_plan":
                result = self._execute_run_plan(task)
            else:
                # 通用执行：通过 do.py
                result = self._execute_via_do(task)

            task.result = result
            task.status = TaskStatus.COMPLETED
            task.execution_time = time.time() - start_time
            return True, result, None

        except Exception as e:
            task.error = str(e)
            task.status = TaskStatus.FAILED
            task.execution_time = time.time() - start_time
            return False, None, str(e)

    def _execute_via_unified_service(self, task: Task) -> Any:
        """通过统一服务中枢执行"""
        from unified_service_hub import UnifiedServiceHub
        hub = UnifiedServiceHub()
        return hub.handle_service(task.params.get("understanding", {}))

    def _execute_launcher(self, task: Task) -> Any:
        """执行 launcher 引擎"""
        action = task.params.get("action", "open")
        target = task.params.get("target", "")

        cmd = f"python {self.scripts_dir / 'do.py'} 打开 {target}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
        return result.stdout

    def _execute_file_tool(self, task: Task) -> Any:
        """执行 file_tool 引擎"""
        action = task.params.get("action", "read")
        target = task.params.get("target", "")

        cmd = f"python {self.scripts_dir / 'do.py'} {action} {target}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
        return result.stdout

    def _execute_screenshot(self, task: Task) -> Any:
        """执行截图引擎"""
        cmd = f"python {self.scripts_dir / 'screenshot_tool.py'}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return result.stdout

    def _execute_mouse(self, task: Task) -> Any:
        """执行鼠标引擎"""
        action = task.params.get("action", "click")
        coords = task.params.get("coords", (0, 0))

        cmd = f"python {self.scripts_dir / 'mouse_tool.py'} {action} {coords[0]} {coords[1]}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return result.stdout

    def _execute_keyboard(self, task: Task) -> Any:
        """执行键盘引擎"""
        action = task.params.get("action", "type")
        text = task.params.get("text", "")

        cmd = f"python {self.scripts_dir / 'keyboard_tool.py'} {action} \"{text}\""
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return result.stdout

    def _execute_run_plan(self, task: Task) -> Any:
        """执行 run_plan"""
        plan_path = task.params.get("plan_path", "")
        cmd = f"python {self.scripts_dir / 'run_plan.py'} {plan_path}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)
        return result.stdout

    def _execute_via_do(self, task: Task) -> Any:
        """通过 do.py 执行通用任务"""
        description = task.description
        cmd = f"python {self.scripts_dir / 'do.py'} {description}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=120)
        return result.stdout

    def adaptive_execute(self, context: ExecutionContext) -> Dict:
        """
        自适应执行策略
        1. 失败重试机制
        2. 路径优化
        3. 资源调度
        """
        results = []
        failed_tasks = []

        for task in context.tasks:
            success, result, error = self.execute_task(task)

            if success:
                results.append({
                    "task_id": task.id,
                    "status": "success",
                    "result": result
                })
                context.completed_tasks.append(task)
            else:
                # 失败重试
                if task.retry_count < task.max_retries:
                    task.retry_count += 1
                    task.status = TaskStatus.RETRYING
                    # 等待后重试
                    time.sleep(1)
                    success, result, error = self.execute_task(task)
                    if success:
                        results.append({
                            "task_id": task.id,
                            "status": "success_after_retry",
                            "result": result,
                            "retry_count": task.retry_count
                        })
                        context.completed_tasks.append(task)
                    else:
                        failed_tasks.append(task)
                        results.append({
                            "task_id": task.id,
                            "status": "failed",
                            "error": error,
                            "retry_count": task.retry_count
                        })
                else:
                    failed_tasks.append(task)
                    results.append({
                        "task_id": task.id,
                        "status": "failed",
                        "error": error,
                        "max_retries_reached": True
                    })

        # 自适应策略调整
        if len(failed_tasks) > 0 and len(context.completed_tasks) > 0:
            # 部分失败，尝试备选方案
            alternative_result = self._try_alternative_approach(failed_tasks, context)
            results.extend(alternative_result)

        return {
            "results": results,
            "total_tasks": len(context.tasks),
            "completed": len(context.completed_tasks),
            "failed": len(failed_tasks),
            "execution_time": time.time() - context.start_time
        }

    def _try_alternative_approach(self, failed_tasks: List[Task], context: ExecutionContext) -> List[Dict]:
        """尝试备选方案"""
        alternatives = []

        for task in failed_tasks:
            # 尝试通用 do.py 执行
            try:
                cmd = f"python {self.scripts_dir / 'do.py'} {task.description}"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=120)
                alternatives.append({
                    "task_id": task.id,
                    "status": "success_via_alternative",
                    "result": result.stdout,
                    "alternative_method": "do.py"
                })
            except Exception as e:
                alternatives.append({
                    "task_id": task.id,
                    "status": "alternative_failed",
                    "error": str(e)
                })

        return alternatives

    def close_loop_feedback(self, execution_result: Dict, original_requirement: str) -> Dict:
        """
        端到端闭环执行与结果反馈
        """
        total = execution_result.get("total_tasks", 0)
        completed = execution_result.get("completed", 0)
        failed = execution_result.get("failed", 0)
        execution_time = execution_result.get("execution_time", 0)

        # 计算成功率
        success_rate = (completed / total * 100) if total > 0 else 0

        # 生成反馈报告
        feedback = {
            "requirement": original_requirement,
            "status": "completed" if failed == 0 else "partially_completed" if completed > 0 else "failed",
            "summary": {
                "total_tasks": total,
                "completed": completed,
                "failed": failed,
                "success_rate": f"{success_rate:.1f}%",
                "execution_time": f"{execution_time:.2f}s"
            },
            "details": execution_result.get("results", []),
            "recommendations": self._generate_recommendations(execution_result, success_rate)
        }

        # 保存执行历史
        self._save_execution_history(feedback)

        return feedback

    def _generate_recommendations(self, execution_result: Dict, success_rate: float) -> List[str]:
        """生成改进建议"""
        recommendations = []

        if success_rate < 50:
            recommendations.append("执行成功率较低，建议简化需求或分步执行")
        elif success_rate < 80:
            recommendations.append("部分任务失败，可以尝试更明确的表述")

        failed_count = execution_result.get("failed", 0)
        if failed_count > 0:
            recommendations.append(f"有 {failed_count} 个任务失败，可尝试使用备选方案")

        # 基于历史执行
        if len(self.execution_history) > 5:
            recent_failures = sum(1 for h in self.execution_history[-5:] if h.get("status") == "failed")
            if recent_failures >= 3:
                recommendations.append("近期失败率较高，建议检查系统状态")

        return recommendations

    def _save_execution_history(self, feedback: Dict):
        """保存执行历史"""
        history_file = self.state_dir / "service_orchestration_history.json"

        # 读取现有历史
        history = []
        if history_file.exists():
            try:
                with open(history_file, "r", encoding="utf-8") as f:
                    history = json.load(f)
            except:
                pass

        # 添加新记录
        history.append({
            "timestamp": datetime.now().isoformat(),
            "feedback": feedback
        })

        # 保留最近 100 条
        history = history[-100:]

        # 写入
        try:
            with open(history_file, "w", encoding="utf-8") as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
        except:
            pass

        self.execution_history.append(feedback)

    def execute_complete_flow(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        """
        完整的端到端服务执行流程：
        1. 理解用户模糊需求
        2. 任务拆分与编排
        3. 引擎选择与执行
        4. 自适应策略调整
        5. 闭环反馈
        """
        # 1. 理解需求
        understanding = self.understand_ambiguous_requirement(user_input, context)

        # 2. 任务拆分
        tasks = self.decompose_task(understanding, context)

        # 3. 引擎选择
        tasks = self.select_optimal_engines(tasks)

        # 4. 构建执行上下文
        exec_context = ExecutionContext(
            user_input=user_input,
            intent=understanding.get("intent"),
            entities=understanding,
            tasks=tasks
        )

        # 5. 自适应执行
        execution_result = self.adaptive_execute(exec_context)

        # 6. 闭环反馈
        feedback = self.close_loop_feedback(execution_result, user_input)

        return {
            "understanding": understanding,
            "tasks": [t.to_dict() for t in tasks],
            "execution": execution_result,
            "feedback": feedback
        }


# CLI 入口
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="智能服务协同编排与自适应执行引擎")
    parser.add_argument("command", nargs="?", help="命令：execute/understand/plan")
    parser.add_argument("--input", "-i", help="用户输入")
    parser.add_argument("--context", "-c", help="上下文 JSON")
    parser.add_argument("--plan", "-p", help="计划路径")

    args = parser.parse_args()

    engine = ServiceOrchestrationAdaptiveEngine()

    if args.command == "execute" and args.input:
        context = json.loads(args.context) if args.context else None
        result = engine.execute_complete_flow(args.input, context)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == "understand" and args.input:
        context = json.loads(args.context) if args.context else None
        result = engine.understand_ambiguous_requirement(args.input, context)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == "plan" and args.input:
        context = json.loads(args.context) if args.context else None
        understanding = engine.understand_ambiguous_requirement(args.input, context)
        tasks = engine.decompose_task(understanding, context)
        print(json.dumps([t.to_dict() for t in tasks], ensure_ascii=False, indent=2))
    else:
        # 交互式模式
        print("智能服务协同编排与自适应执行引擎")
        print("用法:")
        print("  python evolution_service_orchestration_adaptive_engine.py execute --input '用户输入'")
        print("  python evolution_service_orchestration_adaptive_engine.py understand --input '用户输入'")
        print("  python evolution_service_orchestration_adaptive_engine.py plan --input '用户输入'")
        print()

        # 简单测试
        if args.input:
            result = engine.execute_complete_flow(args.input)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            # 演示
            test_input = "帮我打开浏览器访问百度"
            print(f"测试输入: {test_input}")
            result = engine.execute_complete_flow(test_input)
            print(json.dumps(result, ensure_ascii=False, indent=2))