#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
智能跨引擎智能体自主协作引擎（增强版）

功能：
- 让70+引擎能够像人类团队一样自主协作
- 实现任务自动分配、进度自动追踪、问题自动升级的智能体社会
- 提供引擎注册、任务分发、执行监控、结果聚合等核心能力
- 实现智能体间通信协议，支持跨引擎消息传递
- 集成到 do.py 支持「智能协作」「引擎协作」「多引擎协同」「智能体协作」等关键词触发

增强功能（Round 201）：
- 新增引擎实际联动执行能力，能够真正触发和执行其他引擎的任务
- 实现从任务分配到实际执行的完整闭环
- 支持多种执行模式：同步执行、异步执行、串行执行、并行执行
- 实现执行结果聚合和状态追踪
- 集成到 do.py 支持「执行协作任务」「联动执行」等关键词触发

这是「元进化」方向的创新——系统不仅能进化能力，还能让多个引擎像团队一样协同工作。
"""

import os
import sys
import json
import subprocess
import time
import uuid
import asyncio
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor, as_completed
import shlex

# 路径设置
SCRIPT_DIR = Path(__file__).parent
RUNTIME_DIR = SCRIPT_DIR.parent / "runtime"
STATE_DIR = RUNTIME_DIR / "state"
LOGS_DIR = RUNTIME_DIR / "logs"

def ensure_dir(path):
    """确保目录存在"""
    path = Path(path)
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
    return path

# 引擎注册表（从现有引擎自动发现）
ENGINE_REGISTRY = {
    # 核心执行引擎
    "screenshot": {"module": "screenshot_tool.py", "category": "execution", "capability": "屏幕截图"},
    "mouse": {"module": "mouse_tool.py", "category": "execution", "capability": "鼠标操作"},
    "keyboard": {"module": "keyboard_tool.py", "category": "execution", "capability": "键盘操作"},
    "vision": {"module": "vision_proxy.py", "category": "execution", "capability": "视觉理解"},
    "window": {"module": "window_tool.py", "category": "execution", "capability": "窗口管理"},
    "process": {"module": "process_tool.py", "category": "execution", "capability": "进程管理"},
    "clipboard": {"module": "clipboard_tool.py", "category": "execution", "capability": "剪贴板操作"},

    # 智能决策引擎
    "decision_orchestrator": {"module": "decision_orchestrator.py", "category": "decision", "capability": "智能决策"},
    "workflow_engine": {"module": "workflow_engine.py", "category": "decision", "capability": "工作流引擎"},
    "intent_deep_reasoning": {"module": "intent_deep_reasoning_engine.py", "category": "decision", "capability": "意图推理"},

    # 学习与适应引擎
    "adaptive_learning": {"module": "adaptive_learning_engine.py", "category": "learning", "capability": "自适应学习"},
    "feedback_learning": {"module": "feedback_learning_engine.py", "category": "learning", "capability": "反馈学习"},
    "task_preference": {"module": "task_preference_engine.py", "category": "learning", "capability": "任务偏好"},

    # 主动服务引擎
    "proactive_notification": {"module": "proactive_notification_engine.py", "category": "service", "capability": "主动通知"},
    "proactive_decision": {"module": "proactive_decision_action_engine.py", "category": "service", "capability": "主动决策"},
    "proactive_operations": {"module": "proactive_operations_engine.py", "category": "service", "capability": "主动运维"},
    "scenario_recommender": {"module": "scenario_recommender.py", "category": "service", "capability": "场景推荐"},

    # 系统健康引擎
    "self_healing": {"module": "self_healing_engine.py", "category": "health", "capability": "自愈修复"},
    "system_health": {"module": "system_health_monitor.py", "category": "health", "capability": "健康监控"},
    "predictive_prevention": {"module": "predictive_prevention_engine.py", "category": "health", "capability": "预测预防"},

    # 知识与推理引擎
    "knowledge_graph": {"module": "knowledge_graph.py", "category": "knowledge", "capability": "知识图谱"},
    "knowledge_reasoning": {"module": "enhanced_knowledge_reasoning_engine.py", "category": "knowledge", "capability": "知识推理"},
    "knowledge_evolution": {"module": "knowledge_evolution_engine.py", "category": "knowledge", "capability": "知识进化"},

    # 创新与发现引擎
    "innovation_discovery": {"module": "innovation_discovery_engine.py", "category": "innovation", "capability": "创新发现"},
    "creative_generation": {"module": "creative_generation_engine.py", "category": "innovation", "capability": "创意生成"},

    # 执行增强引擎
    "execution_enhancement": {"module": "execution_enhancement_engine.py", "category": "enhancement", "capability": "执行增强"},
    "conversation_execution": {"module": "conversation_execution_engine.py", "category": "enhancement", "capability": "对话执行"},
    "auto_execution": {"module": "auto_execution_engine.py", "category": "enhancement", "capability": "自动执行"},

    # 元进化引擎
    "evolution_strategy": {"module": "evolution_strategy_engine.py", "category": "evolution", "capability": "进化策略"},
    "evolution_learning": {"module": "evolution_learning_engine.py", "category": "evolution", "capability": "进化学习"},
    "meta_evolution": {"module": "meta_evolution_engine.py", "category": "evolution", "capability": "元进化"},
}

class SubTask:
    """子任务对象 - 用于引擎联动执行"""
    def __init__(self, subtask_id: str, engine: str, command: str, args: List[str] = None, depends_on: List[str] = None):
        self.subtask_id = subtask_id
        self.engine = engine
        self.command = command
        self.args = args or []
        self.depends_on = depends_on or []  # 依赖的其他子任务ID
        self.status = "pending"  # pending, running, completed, failed
        self.result = None
        self.error = None
        self.started_at = None
        self.completed_at = None
        self.output = None


class Task:
    """任务对象"""
    def __init__(self, task_id: str, name: str, description: str, assigned_engines: List[str], priority: int = 5):
        self.task_id = task_id
        self.name = name
        self.description = description
        self.assigned_engines = assigned_engines
        self.priority = priority
        self.status = "pending"  # pending, running, completed, failed, escalated
        self.progress = 0.0
        self.result = None
        self.error = None
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
        self.completed_at = None
        self.escalation_level = 0
        self.subtasks: Dict[str, SubTask] = {}  # 增强：子任务列表
        self.execution_mode = "parallel"  # parallel, sequential, async

class AgentMessage:
    """智能体间消息"""
    def __init__(self, from_agent: str, to_agent: str, message_type: str, content: Any):
        self.message_id = str(uuid.uuid4())[:8]
        self.from_agent = from_agent
        self.to_agent = to_agent
        self.message_type = message_type  # task_request, task_response, progress_update, error_report, help_request
        self.content = content
        self.timestamp = datetime.now().isoformat()

class MultiAgentCollaborationEngine:
    """智能跨引擎智能体自主协作引擎"""

    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.message_queue: deque = deque(maxlen=100)
        self.agent_status: Dict[str, Dict] = {}
        self.task_history: List[Dict] = []
        self.collaboration_logs: List[Dict] = []
        self._init_agent_status()
        self._load_history()

    def _init_agent_status(self):
        """初始化智能体状态"""
        for engine_name in ENGINE_REGISTRY:
            self.agent_status[engine_name] = {
                "status": "idle",
                "current_task": None,
                "tasks_completed": 0,
                "tasks_failed": 0,
                "last_active": datetime.now().isoformat(),
                "capabilities": ENGINE_REGISTRY[engine_name].get("capability", ""),
                "category": ENGINE_REGISTRY[engine_name].get("category", "general")
            }

    def _load_history(self):
        """加载历史记录"""
        history_file = STATE_DIR / "multi_agent_history.json"
        if history_file.exists():
            try:
                with open(history_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.task_history = data.get("tasks", [])
                    self.collaboration_logs = data.get("logs", [])
            except Exception as e:
                print(f"加载历史记录失败: {e}")

    def _save_history(self):
        """保存历史记录"""
        ensure_dir(STATE_DIR)
        history_file = STATE_DIR / "multi_agent_history.json"
        try:
            with open(history_file, "w", encoding="utf-8") as f:
                json.dump({
                    "tasks": self.task_history[-100:],  # 只保留最近100条
                    "logs": self.collaboration_logs[-100:]
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存历史记录失败: {e}")

    def register_engine(self, engine_name: str, module: str, capability: str, category: str = "general"):
        """注册新引擎"""
        ENGINE_REGISTRY[engine_name] = {
            "module": module,
            "category": category,
            "capability": capability
        }
        self.agent_status[engine_name] = {
            "status": "idle",
            "current_task": None,
            "tasks_completed": 0,
            "tasks_failed": 0,
            "last_active": datetime.now().isoformat(),
            "capabilities": capability,
            "category": category
        }
        self._log("engine_registered", f"引擎 {engine_name} 已注册，能力: {capability}")

    def create_task(self, name: str, description: str, required_capabilities: List[str], priority: int = 5) -> str:
        """创建新任务并自动分配引擎"""
        task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:4]}"

        # 根据需求能力自动选择最合适的引擎
        assigned_engines = self._select_engines(required_capabilities)

        task = Task(task_id, name, description, assigned_engines, priority)
        self.tasks[task_id] = task

        # 向分配的引擎发送任务消息
        for engine in assigned_engines:
            self._send_message(engine, "task_request", {
                "task_id": task_id,
                "name": name,
                "description": description,
                "priority": priority
            })
            self.agent_status[engine]["status"] = "assigned"
            self.agent_status[engine]["current_task"] = task_id

        self._log("task_created", f"任务 {task_id} 已创建，分配给: {', '.join(assigned_engines)}")
        return task_id

    def _select_engines(self, required_capabilities: List[str]) -> List[str]:
        """根据需求能力智能选择引擎"""
        selected = []
        capability_to_engine = defaultdict(list)

        # 建立能力到引擎的映射
        for engine_name, engine_info in ENGINE_REGISTRY.items():
            cap = engine_info.get("capability", "")
            cat = engine_info.get("category", "")
            capability_to_engine[cap].append(engine_name)
            capability_to_engine[cat].append(engine_name)

        # 选择最匹配的引擎
        for cap in required_capabilities:
            candidates = capability_to_engine.get(cap, [])
            for candidate in candidates:
                if candidate not in selected and self.agent_status[candidate]["status"] in ["idle", "assigned"]:
                    selected.append(candidate)
                    if len(selected) >= 3:  # 最多选择3个引擎
                        break
            if len(selected) >= 3:
                break

        return selected if selected else list(ENGINE_REGISTRY.keys())[:3]

    def _send_message(self, to_agent: str, message_type: str, content: Any):
        """发送智能体间消息"""
        message = AgentMessage("coordinator", to_agent, message_type, content)
        self.message_queue.append(message)
        self._log("message_sent", f"消息发送到 {to_agent}: {message_type}")

    # ======== 增强：引擎实际联动执行能力 ========

    def _get_engine_script_path(self, engine_name: str) -> Optional[Path]:
        """获取引擎脚本路径"""
        if engine_name not in ENGINE_REGISTRY:
            return None

        module_name = ENGINE_REGISTRY[engine_name].get("module", "")
        if not module_name:
            return None

        script_path = SCRIPT_DIR / module_name
        return script_path if script_path.exists() else None

    def _execute_engine_command(self, engine: str, command: str, args: List[str] = None, timeout: int = 60) -> Dict:
        """执行单个引擎命令"""
        script_path = self._get_engine_script_path(engine)

        if not script_path:
            return {"success": False, "error": f"引擎 {engine} 脚本不存在", "output": ""}

        try:
            # 构建命令
            cmd = [sys.executable, str(script_path)]
            if command:
                cmd.append(command)
            if args:
                cmd.extend(args)

            # 执行命令
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding="utf-8",
                errors="replace"
            )

            success = result.returncode == 0
            return {
                "success": success,
                "returncode": result.returncode,
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else "",
                "engine": engine,
                "command": command
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": f"执行超时（{timeout}秒）", "output": "", "engine": engine}
        except Exception as e:
            return {"success": False, "error": str(e), "output": "", "engine": engine}

    def create_executable_task(self, name: str, description: str, subtasks: List[Dict], execution_mode: str = "parallel") -> str:
        """创建可执行的协作任务（增强版）

        Args:
            name: 任务名称
            description: 任务描述
            subtasks: 子任务列表，每个子任务包含：
                - engine: 引擎名称
                - command: 命令（如 "status", "list" 等）
                - args: 参数列表
                - depends_on: 依赖的子任务ID（用于串行执行）
            execution_mode: 执行模式 "parallel"(并行) / "sequential"(串行) / "async"(异步)

        Returns:
            任务ID
        """
        task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:4]}"

        # 创建任务
        assigned_engines = [st["engine"] for st in subtasks if "engine" in st]
        task = Task(task_id, name, description, list(set(assigned_engines)), priority=5)
        task.execution_mode = execution_mode
        self.tasks[task_id] = task

        # 创建子任务
        for i, st in enumerate(subtasks):
            subtask_id = f"{task_id}_sub_{i}"
            engine = st.get("engine", "")
            command = st.get("command", "")
            args = st.get("args", [])
            depends_on = st.get("depends_on", [])

            if engine not in ENGINE_REGISTRY:
                continue

            subtask = SubTask(subtask_id, engine, command, args, depends_on)
            task.subtasks[subtask_id] = subtask

        # 更新引擎状态
        for engine in set(assigned_engines):
            if engine in self.agent_status:
                self.agent_status[engine]["status"] = "assigned"
                self.agent_status[engine]["current_task"] = task_id

        self._log("executable_task_created", f"可执行任务 {task_id} 已创建，模式: {execution_mode}，子任务数: {len(task.subtasks)}")
        return task_id

    def execute_task(self, task_id: str, timeout: int = 120) -> Dict:
        """执行协作任务（真正触发引擎执行）

        Returns:
            执行结果，包含各子任务的执行状态和结果聚合
        """
        if task_id not in self.tasks:
            return {"success": False, "error": f"任务 {task_id} 不存在"}

        task = self.tasks[task_id]
        if not task.subtasks:
            return {"success": False, "error": "任务没有子任务"}

        task.status = "running"
        task.updated_at = datetime.now().isoformat()

        results = {}
        completed_subtasks = set()

        # 根据执行模式执行
        if task.execution_mode == "sequential":
            # 串行执行：按依赖顺序执行
            results = self._execute_sequential(task, timeout)
        elif task.execution_mode == "async":
            # 异步执行
            results = self._execute_async(task, timeout)
        else:
            # 并行执行（默认）
            results = self._execute_parallel(task, timeout)

        # 聚合结果
        success_count = sum(1 for r in results.values() if r.get("success", False))
        total_count = len(results)

        if success_count == total_count:
            task.status = "completed"
            task.result = {"subtask_results": results, "summary": f"{success_count}/{total_count} 成功"}
        else:
            task.status = "failed"
            task.error = f"部分子任务失败：{success_count}/{total_count} 成功"
            task.result = {"subtask_results": results, "summary": f"{success_count}/{total_count} 成功"}

        task.completed_at = datetime.now().isoformat()
        task.progress = 100.0
        task.updated_at = datetime.now().isoformat()

        # 更新引擎状态
        for engine in task.assigned_engines:
            if engine in self.agent_status:
                self.agent_status[engine]["status"] = "idle"
                self.agent_status[engine]["current_task"] = None
                if task.status == "completed":
                    self.agent_status[engine]["tasks_completed"] += 1
                else:
                    self.agent_status[engine]["tasks_failed"] += 1
                self.agent_status[engine]["last_active"] = datetime.now().isoformat()

        # 记录到历史
        self.task_history.append({
            "task_id": task_id,
            "name": task.name,
            "assigned_engines": task.assigned_engines,
            "status": task.status,
            "execution_mode": task.execution_mode,
            "completed_at": task.completed_at
        })

        self._log("task_executed", f"任务 {task_id} 已执行完成，状态: {task.status}，结果: {task.result.get('summary', '')}")
        self._save_history()

        return {
            "success": task.status == "completed",
            "task_id": task_id,
            "status": task.status,
            "results": results,
            "summary": task.result.get("summary", "")
        }

    def _execute_parallel(self, task: Task, timeout: int) -> Dict:
        """并行执行所有子任务"""
        results = {}

        def run_subtask(subtask_id: str, subtask: SubTask):
            subtask.status = "running"
            subtask.started_at = datetime.now().isoformat()
            result = self._execute_engine_command(subtask.engine, subtask.command, subtask.args, timeout)
            subtask.status = "completed" if result.get("success") else "failed"
            subtask.completed_at = datetime.now().isoformat()
            subtask.result = result
            subtask.output = result.get("output", "")
            subtask.error = result.get("error", "")
            return subtask_id, result

        # 并行执行
        with ThreadPoolExecutor(max_workers=len(task.subtasks)) as executor:
            futures = {
                executor.submit(run_subtask, sid, st): sid
                for sid, st in task.subtasks.items()
            }

            for future in as_completed(futures):
                try:
                    subtask_id, result = future.result(timeout=timeout)
                    results[subtask_id] = result
                except Exception as e:
                    sid = futures[future]
                    results[sid] = {"success": False, "error": str(e)}

        return results

    def _execute_sequential(self, task: Task, timeout: int) -> Dict:
        """串行执行子任务（按依赖顺序）"""
        results = {}
        completed = set()

        # 持续执行直到所有任务完成或无法继续
        max_iterations = len(task.subtasks) * 2  # 防止无限循环
        iteration = 0

        while len(completed) < len(task.subtasks) and iteration < max_iterations:
            iteration += 1
            made_progress = False

            for subtask_id, subtask in task.subtasks.items():
                if subtask_id in completed:
                    continue

                # 检查依赖是否满足
                deps_met = all(dep in completed for dep in subtask.depends_on)
                if not deps_met:
                    continue

                # 执行子任务
                subtask.status = "running"
                subtask.started_at = datetime.now().isoformat()

                result = self._execute_engine_command(subtask.engine, subtask.command, subtask.args, timeout)
                subtask.status = "completed" if result.get("success") else "failed"
                subtask.completed_at = datetime.now().isoformat()
                subtask.result = result
                subtask.output = result.get("output", "")
                subtask.error = result.get("error", "")

                results[subtask_id] = result
                completed.add(subtask_id)
                made_progress = True

                # 如果失败且不允许继续，则停止
                if not result.get("success"):
                    break

            if not made_progress:
                break

        # 标记未完成的任务
        for subtask_id in task.subtasks:
            if subtask_id not in results:
                results[subtask_id] = {"success": False, "error": "依赖未满足或执行失败"}

        return results

    def _execute_async(self, task: Task, timeout: int) -> Dict:
        """异步执行（快速返回，结果通过回调或轮询获取）"""
        # 异步执行实际上是启动后台线程执行，结果通过轮询获取
        results = {}

        def run_subtask_background(subtask_id: str, subtask: SubTask):
            subtask.status = "running"
            subtask.started_at = datetime.now().isoformat()
            result = self._execute_engine_command(subtask.engine, subtask.command, subtask.args, timeout)
            subtask.status = "completed" if result.get("success") else "failed"
            subtask.completed_at = datetime.now().isoformat()
            subtask.result = result
            subtask.output = result.get("output", "")
            subtask.error = result.get("error", "")
            results[subtask_id] = result

        # 启动后台线程
        threads = []
        for subtask_id, subtask in task.subtasks.items():
            t = threading.Thread(target=run_subtask_background, args=(subtask_id, subtask))
            t.start()
            threads.append(t)

        # 等待所有线程完成（带超时）
        for t in threads:
            t.join(timeout=timeout)

        # 标记未完成的任务
        for subtask_id, subtask in task.subtasks.items():
            if subtask_id not in results:
                results[subtask_id] = {"success": False, "error": "执行超时", "engine": subtask.engine}

        return results

    def get_execution_status(self, task_id: str) -> Optional[Dict]:
        """获取任务执行状态"""
        if task_id not in self.tasks:
            return None

        task = self.tasks[task_id]
        subtask_status = {}
        for sid, st in task.subtasks.items():
            subtask_status[sid] = {
                "engine": st.engine,
                "command": st.command,
                "status": st.status,
                "started_at": st.started_at,
                "completed_at": st.completed_at,
                "result": st.result
            }

        return {
            "task_id": task_id,
            "name": task.name,
            "status": task.status,
            "execution_mode": task.execution_mode,
            "progress": task.progress,
            "subtasks": subtask_status,
            "result": task.result,
            "error": task.error
        }

    def update_task_progress(self, task_id: str, progress: float, status: str = "running"):
        """更新任务进度"""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            task.progress = min(100.0, max(0.0, progress))
            task.status = status
            task.updated_at = datetime.now().isoformat()

            # 向所有参与引擎发送进度更新
            for engine in task.assigned_engines:
                self._send_message(engine, "progress_update", {
                    "task_id": task_id,
                    "progress": progress,
                    "status": status
                })

    def complete_task(self, task_id: str, result: Any = None):
        """完成任务"""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            task.status = "completed"
            task.progress = 100.0
            task.result = result
            task.completed_at = datetime.now().isoformat()
            task.updated_at = datetime.now().isoformat()

            # 更新引擎状态
            for engine in task.assigned_engines:
                self.agent_status[engine]["status"] = "idle"
                self.agent_status[engine]["current_task"] = None
                self.agent_status[engine]["tasks_completed"] += 1
                self.agent_status[engine]["last_active"] = datetime.now().isoformat()

            # 记录到历史
            self.task_history.append({
                "task_id": task_id,
                "name": task.name,
                "assigned_engines": task.assigned_engines,
                "status": "completed",
                "completed_at": task.completed_at
            })

            self._log("task_completed", f"任务 {task_id} 已完成")
            self._save_history()

    def escalate_task(self, task_id: str, error: str):
        """升级问题"""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            task.status = "escalated"
            task.escalation_level += 1
            task.error = error
            task.updated_at = datetime.now().isoformat()

            # 如果升级级别不高，尝试重新分配
            if task.escalation_level < 3:
                # 选择备用引擎
                backup_engines = [e for e in ENGINE_REGISTRY.keys()
                                  if e not in task.assigned_engines
                                  and self.agent_status[e]["status"] == "idle"][:2]
                if backup_engines:
                    task.assigned_engines.extend(backup_engines)
                    for engine in backup_engines:
                        self.agent_status[engine]["status"] = "assigned"
                        self._send_message(engine, "task_request", {
                            "task_id": task_id,
                            "name": task.name,
                            "description": f"[重试] {task.description}",
                            "priority": task.priority + 1
                        })
                    self._log("task_escalated", f"任务 {task_id} 已升级并重新分配，级别: {task.escalation_level}")
            else:
                # 达到最高升级级别，标记为失败
                task.status = "failed"
                task.result = {"error": error, "escalation_level": task.escalation_level}
                for engine in task.assigned_engines:
                    self.agent_status[engine]["status"] = "idle"
                    self.agent_status[engine]["current_task"] = None
                    self.agent_status[engine]["tasks_failed"] += 1

                self.task_history.append({
                    "task_id": task_id,
                    "name": task.name,
                    "assigned_engines": task.assigned_engines,
                    "status": "failed",
                    "error": error,
                    "escalation_level": task.escalation_level
                })
                self._log("task_failed", f"任务 {task_id} 失败，已达到最大升级级别")

            self._save_history()

    def get_task_status(self, task_id: str) -> Optional[Dict]:
        """获取任务状态"""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            return {
                "task_id": task.task_id,
                "name": task.name,
                "description": task.description,
                "assigned_engines": task.assigned_engines,
                "status": task.status,
                "progress": task.progress,
                "priority": task.priority,
                "escalation_level": task.escalation_level,
                "created_at": task.created_at,
                "updated_at": task.updated_at,
                "result": task.result,
                "error": task.error
            }
        return None

    def get_all_tasks(self, status: str = None) -> List[Dict]:
        """获取所有任务"""
        tasks = []
        for task_id, task in self.tasks.items():
            if status is None or task.status == status:
                tasks.append(self.get_task_status(task_id))
        return tasks

    def get_agent_status(self, engine_name: str = None) -> Dict:
        """获取引擎状态"""
        if engine_name:
            return self.agent_status.get(engine_name, {})
        return dict(self.agent_status)

    def get_collaboration_stats(self) -> Dict:
        """获取协作统计"""
        total_tasks = len(self.task_history)
        completed = len([t for t in self.task_history if t.get("status") == "completed"])
        failed = len([t for t in self.task_history if t.get("status") == "failed"])

        # 引擎活跃度
        engine_activity = {}
        for engine, status in self.agent_status.items():
            engine_activity[engine] = {
                "status": status["status"],
                "tasks_completed": status["tasks_completed"],
                "tasks_failed": status["tasks_failed"]
            }

        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed,
            "failed_tasks": failed,
            "success_rate": round(completed / total_tasks * 100, 1) if total_tasks > 0 else 0,
            "active_engines": len([s for s in self.agent_status.values() if s["status"] != "idle"]),
            "total_engines": len(ENGINE_REGISTRY),
            "engine_activity": engine_activity,
            "pending_messages": len(self.message_queue)
        }

    def _log(self, event_type: str, description: str):
        """记录协作日志"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "description": description
        }
        self.collaboration_logs.append(log_entry)
        if len(self.collaboration_logs) > 100:
            self.collaboration_logs = self.collaboration_logs[-100:]

    def get_collaboration_logs(self, limit: int = 20) -> List[Dict]:
        """获取协作日志"""
        return self.collaboration_logs[-limit:]

    def run_collaboration_example(self):
        """运行协作示例"""
        print("\n=== 智能体协作引擎演示 ===\n")

        # 示例1：创建文件整理任务
        print("1. 创建文件整理任务...")
        task_id = self.create_task(
            name="文件整理任务",
            description="整理桌面文件并分类",
            required_capabilities=["文件管理", "智能决策", "主动通知"],
            priority=5
        )
        print(f"   任务ID: {task_id}")
        print(f"   状态: {self.get_task_status(task_id)['status']}")

        # 模拟进度更新
        print("\n2. 更新任务进度...")
        self.update_task_progress(task_id, 50.0)
        print(f"   进度: 50%")

        # 完成任务
        print("\n3. 完成任务...")
        self.complete_task(task_id, {"files_organized": 15, "notification_sent": True})
        print(f"   状态: completed")

        # 获取统计
        print("\n4. 获取协作统计...")
        stats = self.get_collaboration_stats()
        print(f"   总任务数: {stats['total_tasks']}")
        print(f"   成功率: {stats['success_rate']}%")
        print(f"   活跃引擎: {stats['active_engines']}/{stats['total_engines']}")

        # 获取引擎状态
        print("\n5. 获取引擎状态...")
        for engine, status in list(self.agent_status.items())[:3]:
            print(f"   {engine}: {status['status']} (完成: {status['tasks_completed']}, 失败: {status['tasks_failed']})")

        print("\n=== 演示完成 ===\n")

# 全局实例
_collaboration_engine = None

def get_instance():
    """获取引擎实例"""
    global _collaboration_engine
    if _collaboration_engine is None:
        _collaboration_engine = MultiAgentCollaborationEngine()
    return _collaboration_engine

def main():
    """主入口"""
    engine = get_instance()

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "create_task":
            if len(sys.argv) < 4:
                print("用法: multi_agent_collaboration_engine.py create_task <任务名> <描述> [能力1,能力2,...]")
                sys.exit(1)
            name = sys.argv[2]
            description = sys.argv[3]
            capabilities = sys.argv[4].split(",") if len(sys.argv) > 4 else ["通用"]
            task_id = engine.create_task(name, description, capabilities)
            print(f"任务已创建: {task_id}")
            print(f"任务状态: {engine.get_task_status(task_id)}")

        elif command == "create_executable_task" or command == "create_exec":
            # 用法: create_executable_task <name> <description> <mode> <subtask1> <subtask2> ...
            # 子任务格式: engine:command:arg1,arg2
            if len(sys.argv) < 5:
                print("用法: multi_agent_collaboration_engine.py create_executable_task <任务名> <描述> <parallel|sequential|async> <子任务1> <子任务2> ...")
                print("子任务格式: engine:command:arg1,arg2")
                print("示例: multi_agent_collaboration_engine.py create_exec 测试任务 测试描述 parallel process:list window:activate:办公平台")
                sys.exit(1)
            name = sys.argv[2]
            description = sys.argv[3]
            execution_mode = sys.argv[4] if sys.argv[4] in ["parallel", "sequential", "async"] else "parallel"

            # 解析子任务
            subtasks = []
            for st_arg in sys.argv[5:]:
                parts = st_arg.split(":")
                if len(parts) >= 2:
                    engine_name = parts[0]
                    cmd = parts[1]
                    args = parts[2].split(",") if len(parts) > 2 and parts[2] else []
                    subtasks.append({"engine": engine_name, "command": cmd, "args": args})

            if not subtasks:
                print("错误: 至少需要一个子任务")
                sys.exit(1)

            task_id = engine.create_executable_task(name, description, subtasks, execution_mode)
            print(f"可执行任务已创建: {task_id}")
            print(f"执行模式: {execution_mode}")
            print(f"子任务数: {len(subtasks)}")

        elif command == "execute" or command == "run":
            # 用法: execute <task_id> [timeout]
            if len(sys.argv) < 3:
                print("用法: multi_agent_collaboration_engine.py execute <task_id> [超时秒数]")
                sys.exit(1)
            task_id = sys.argv[2]
            timeout = int(sys.argv[3]) if len(sys.argv) > 3 else 120

            print(f"开始执行任务: {task_id}")
            result = engine.execute_task(task_id, timeout)
            print(json.dumps(result, ensure_ascii=False, indent=2))

        elif command == "execution_status" or command == "exec_status":
            # 用法: execution_status <task_id>
            if len(sys.argv) < 3:
                print("用法: multi_agent_collaboration_engine.py execution_status <task_id>")
                sys.exit(1)
            task_id = sys.argv[2]
            status = engine.get_execution_status(task_id)
            if status:
                print(json.dumps(status, ensure_ascii=False, indent=2))
            else:
                print(f"任务 {task_id} 不存在")

        elif command == "test_execution":
            # 测试引擎联动执行能力
            print("\n=== 测试引擎联动执行能力 ===\n")

            # 创建测试任务：并行执行多个引擎
            subtasks = [
                {"engine": "process", "command": "list", "args": []},
                {"engine": "window", "command": "activate", "args": ["记事本"]},
            ]
            task_id = engine.create_executable_task(
                "测试引擎联动执行",
                "测试多引擎并行执行能力",
                subtasks,
                "parallel"
            )
            print(f"1. 创建测试任务: {task_id}")

            # 执行任务
            print(f"2. 执行任务...")
            result = engine.execute_task(task_id, 30)
            print(f"3. 执行结果: {result.get('summary', '')}")
            print(f"4. 状态: {result.get('status', '')}")

            # 显示详细信息
            exec_status = engine.get_execution_status(task_id)
            if exec_status:
                print(f"5. 子任务详情:")
                for sid, st in exec_status.get("subtasks", {}).items():
                    print(f"   - {sid}: {st['engine']}:{st['command']} -> {st['status']}")

            print("\n=== 测试完成 ===\n")

        elif command == "status":
            if len(sys.argv) > 2:
                task_id = sys.argv[2]
                status = engine.get_task_status(task_id)
                print(json.dumps(status, ensure_ascii=False, indent=2))
            else:
                tasks = engine.get_all_tasks()
                print(f"总任务数: {len(tasks)}")
                for task in tasks[:5]:
                    print(f"  - {task['task_id']}: {task['name']} ({task['status']})")

        elif command == "agents":
            agents = engine.get_agent_status()
            print(f"注册引擎数: {len(agents)}")
            for name, status in list(agents.items())[:10]:
                print(f"  - {name}: {status['status']}")

        elif command == "stats":
            stats = engine.get_collaboration_stats()
            print(json.dumps(stats, ensure_ascii=False, indent=2))

        elif command == "logs":
            logs = engine.get_collaboration_logs(10)
            for log in logs:
                print(f"[{log['timestamp']}] {log['event_type']}: {log['description']}")

        elif command == "example":
            engine.run_collaboration_example()

        else:
            print(f"未知命令: {command}")
            print("可用命令: create_task, create_executable_task, execute, execution_status, test_execution, status, agents, stats, logs, example")
    else:
        # 默认运行示例
        engine.run_collaboration_example()

if __name__ == "__main__":
    main()