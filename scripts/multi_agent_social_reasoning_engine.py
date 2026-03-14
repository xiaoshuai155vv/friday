#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景智能体自主协作与社会化推理引擎 (Multi-Agent Social Reasoning Engine)
版本: 1.0.0

让系统能够模拟人类社会中的协作模式，多个智能体之间能够自主分工、协商、协作解决问题，
实现真正的分布式智能协作。

功能：
1. 智能体社会模型 - 模拟人类社会的分工协作
2. 自主协商机制 - 智能体间任务分配和资源协商
3. 协作问题解决 - 多智能体协同完成复杂任务
4. 社会化学习 - 从协作中学习和改进
"""

import json
import os
import sys
import re
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Set
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
RUNTIME_STATE_DIR = PROJECT_ROOT / "runtime" / "state"


class AgentRole(Enum):
    """智能体角色类型"""
    COORDINATOR = "coordinator"  # 协调者 - 负责任务分配和协调
    EXECUTOR = "executor"        # 执行者 - 负责具体任务执行
    ANALYZER = "analyzer"        # 分析者 - 负责分析和规划
    MONITOR = "monitor"          # 监控者 - 负责监督和评估
    COMMUNICATOR = "communicator"  # 沟通者 - 负责信息传递


class TaskPriority(Enum):
    """任务优先级"""
    URGENT = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4


class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


@dataclass
class Agent:
    """智能体"""
    id: str
    name: str
    role: AgentRole
    capabilities: List[str] = field(default_factory=list)
    workload: int = 0  # 当前工作负载 (0-100)
    status: str = "idle"  # idle, busy, offline
    expertise: List[str] = field(default_factory=list)  # 专业领域
    collaboration_history: List[Dict] = field(default_factory=list)

    def can_handle(self, task: 'Task') -> bool:
        """判断智能体是否能处理该任务"""
        if self.status == "offline":
            return False
        if self.workload >= 90:
            return False
        # 检查能力匹配
        task_required = set(task.required_capabilities)
        agent_caps = set(self.capabilities)
        return len(task_required & agent_caps) > 0


@dataclass
class Task:
    """任务"""
    id: str
    description: str
    required_capabilities: List[str]
    priority: TaskPriority = TaskPriority.NORMAL
    status: TaskStatus = TaskStatus.PENDING
    assigned_agent: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)  # 依赖的任务ID
    result: Optional[Any] = None
    error: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None


@dataclass
class CollaborationEvent:
    """协作事件"""
    type: str  # task_assigned, task_completed, negotiation, conflict, etc.
    agents_involved: List[str]
    task_id: Optional[str] = None
    message: str = ""
    timestamp: datetime = field(default_factory=datetime.now)


class MultiAgentSocialReasoningEngine:
    """智能全场景智能体自主协作与社会化推理引擎"""

    def __init__(self):
        self.name = "智能体自主协作与社会化推理引擎"
        self.version = "1.0.0"
        self.agents: Dict[str, Agent] = {}
        self.tasks: Dict[str, Task] = {}
        self.collaboration_events: List[CollaborationEvent] = []
        self.negotiation_history: List[Dict] = []
        self.initialized = False
        self._initialize_agents()

    def _initialize_agents(self):
        """初始化智能体团队"""
        # 协调者 - 负责任务分配和整体协调
        self.agents["coordinator_1"] = Agent(
            id="coordinator_1",
            name="协调者小C",
            role=AgentRole.COORDINATOR,
            capabilities=["task_planning", "resource_allocation", "conflict_resolution", "priority_assessment"],
            expertise=["task_management", "coordination", "planning"]
        )

        # 分析者 - 负责分析任务需求和制定执行计划
        self.agents["analyzer_1"] = Agent(
            id="analyzer_1",
            name="分析者小A",
            role=AgentRole.ANALYZER,
            capabilities=["analysis", "reasoning", "pattern_recognition", "risk_assessment"],
            expertise=["analysis", "reasoning", "problem_solving"]
        )

        # 执行者 - 负责具体执行任务
        self.agents["executor_1"] = Agent(
            id="executor_1",
            name="执行者小E1",
            role=AgentRole.EXECUTOR,
            capabilities=["execution", "file_operations", "command_run", "browser_control", "data_processing"],
            expertise=["script_execution", "automation"]
        )

        self.agents["executor_2"] = Agent(
            id="executor_2",
            name="执行者小E2",
            role=AgentRole.EXECUTOR,
            capabilities=["execution", "text_processing", "vision_analysis", "data_extraction"],
            expertise=["multimodal", "text_processing"]
        )

        self.agents["executor_3"] = Agent(
            id="executor_3",
            name="执行者小E3",
            role=AgentRole.EXECUTOR,
            capabilities=["execution", "web_operations", "api_calls", "json_processing"],
            expertise=["web_services", "api_integration"]
        )

        # 监控者 - 负责监督任务执行和评估结果
        self.agents["monitor_1"] = Agent(
            id="monitor_1",
            name="监控者小M",
            role=AgentRole.MONITOR,
            capabilities=["monitoring", "quality_check", "performance_evaluation", "error_detection"],
            expertise=["quality_assurance", "monitoring"]
        )

        # 沟通者 - 负责信息传递和协作
        self.agents["communicator_1"] = Agent(
            id="communicator_1",
            name="沟通者小N",
            role=AgentRole.COMMUNICATOR,
            capabilities=["information_sharing", "status_update", "notification", "summary_generation"],
            expertise=["communication", "reporting"]
        )

        self.initialized = True

    def get_team_status(self) -> Dict[str, Any]:
        """获取团队状态"""
        return {
            "total_agents": len(self.agents),
            "agents": {
                agent_id: {
                    "name": agent.name,
                    "role": agent.role.value,
                    "status": agent.status,
                    "workload": agent.workload,
                    "expertise": agent.expertise
                }
                for agent_id, agent in self.agents.items()
            }
        }

    def create_task(self, description: str, required_capabilities: List[str],
                   priority: TaskPriority = TaskPriority.NORMAL,
                   dependencies: List[str] = None) -> str:
        """创建新任务"""
        task_id = f"task_{len(self.tasks) + 1}_{int(datetime.now().timestamp())}"
        task = Task(
            id=task_id,
            description=description,
            required_capabilities=required_capabilities,
            priority=priority,
            dependencies=dependencies or []
        )
        self.tasks[task_id] = task
        return task_id

    def analyze_task(self, task_id: str) -> Dict[str, Any]:
        """分析任务 - 由分析者执行"""
        task = self.tasks.get(task_id)
        if not task:
            return {"error": "任务不存在"}

        # 记录协作事件
        event = CollaborationEvent(
            type="task_analysis",
            agents_involved=["analyzer_1"],
            task_id=task_id,
            message=f"分析任务: {task.description}"
        )
        self.collaboration_events.append(event)

        # 分析结果
        analysis = {
            "task_id": task_id,
            "description": task.description,
            "required_capabilities": task.required_capabilities,
            "complexity": self._assess_complexity(task),
            "estimated_duration": self._estimate_duration(task),
            "suggested_agents": self._suggest_agents(task),
            "potential_risks": self._identify_risks(task),
            "analysis_by": "analyzer_1"
        }

        return analysis

    def _assess_complexity(self, task: Task) -> str:
        """评估任务复杂度"""
        complexity_score = 0
        complexity_score += len(task.required_capabilities) * 2
        complexity_score += len(task.dependencies) * 3
        complexity_score += len(task.description) // 20

        if complexity_score <= 5:
            return "简单"
        elif complexity_score <= 10:
            return "中等"
        elif complexity_score <= 15:
            return "复杂"
        else:
            return "非常复杂"

    def _estimate_duration(self, task: Task) -> str:
        """估算任务持续时间"""
        base_time = len(task.required_capabilities) * 5
        base_time += len(task.dependencies) * 3
        return f"{base_time}分钟"

    def _suggest_agents(self, task: Task) -> List[str]:
        """建议处理任务的智能体"""
        suggestions = []
        for agent_id, agent in self.agents.items():
            if agent.can_handle(task):
                suggestions.append({
                    "agent_id": agent_id,
                    "name": agent.name,
                    "role": agent.role.value,
                    "match_score": len(set(task.required_capabilities) & set(agent.capabilities))
                })
        return sorted(suggestions, key=lambda x: x["match_score"], reverse=True)[:3]

    def _identify_risks(self, task: Task) -> List[str]:
        """识别任务风险"""
        risks = []
        if task.dependencies:
            risks.append("存在依赖任务，可能被阻塞")
        if task.priority == TaskPriority.URGENT:
            risks.append("高优先级任务，需要快速响应")
        if len(task.required_capabilities) > 3:
            risks.append("需要多角色协作，协调复杂度高")
        return risks

    def negotiate_task_assignment(self, task_id: str) -> Dict[str, Any]:
        """协商任务分配 - 模拟智能体间的协商过程"""
        task = self.tasks.get(task_id)
        if not task:
            return {"error": "任务不存在"}

        # 记录协商事件
        event = CollaborationEvent(
            type="negotiation_start",
            agents_involved=["coordinator_1", "analyzer_1"],
            task_id=task_id,
            message="开始任务分配协商"
        )
        self.collaboration_events.append(event)

        # 获取可用智能体
        available_agents = [a for a in self.agents.values() if a.can_handle(task)]

        if not available_agents:
            return {
                "status": "failed",
                "reason": "没有可用的智能体",
                "task_id": task_id
            }

        # 协调者选择最佳智能体
        best_agent = min(available_agents, key=lambda a: a.workload)

        # 模拟协商过程
        negotiation_result = {
            "task_id": task_id,
            "status": "assigned",
            "assigned_agent": best_agent.id,
            "agent_name": best_agent.name,
            "reason": f"选择原因：工作负载最低({best_agent.workload}%)，具备所需能力",
            "negotiated_by": "coordinator_1",
            "timestamp": datetime.now().isoformat()
        }

        # 更新任务状态
        task.assigned_agent = best_agent.id
        task.status = TaskStatus.ASSIGNED

        # 更新智能体工作负载
        best_agent.workload = min(100, best_agent.workload + 20)

        # 记录协作事件
        event = CollaborationEvent(
            type="task_assigned",
            agents_involved=["coordinator_1", best_agent.id],
            task_id=task_id,
            message=f"任务分配给 {best_agent.name}"
        )
        self.collaboration_events.append(event)

        self.negotiation_history.append(negotiation_result)
        return negotiation_result

    def execute_task(self, task_id: str) -> Dict[str, Any]:
        """执行任务 - 由分配的智能体执行"""
        task = self.tasks.get(task_id)
        if not task:
            return {"error": "任务不存在"}

        if not task.assigned_agent:
            return {"error": "任务未分配"}

        agent = self.agents.get(task.assigned_agent)
        if not agent:
            return {"error": "分配的智能体不存在"}

        # 检查依赖是否满足
        for dep_id in task.dependencies:
            dep_task = self.tasks.get(dep_id)
            if not dep_task or dep_task.status != TaskStatus.COMPLETED:
                task.status = TaskStatus.BLOCKED
                return {
                    "status": "blocked",
                    "reason": f"依赖任务 {dep_id} 未完成",
                    "task_id": task_id
                }

        # 更新状态为执行中
        task.status = TaskStatus.IN_PROGRESS

        # 记录执行事件
        event = CollaborationEvent(
            type="task_execution_start",
            agents_involved=[agent.id],
            task_id=task_id,
            message=f"{agent.name} 开始执行任务"
        )
        self.collaboration_events.append(event)

        # 模拟任务执行结果
        execution_result = {
            "task_id": task_id,
            "status": "completed",
            "executed_by": agent.id,
            "agent_name": agent.name,
            "result": {
                "output": f"任务 '{task.description}' 已完成",
                "capabilities_used": task.required_capabilities,
                "execution_time": "模拟执行时间"
            },
            "timestamp": datetime.now().isoformat()
        }

        # 更新任务状态
        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.now()
        task.result = execution_result["result"]

        # 减少智能体工作负载
        agent.workload = max(0, agent.workload - 15)

        # 记录完成事件
        event = CollaborationEvent(
            type="task_completed",
            agents_involved=[agent.id],
            task_id=task_id,
            message=f"{agent.name} 完成任务"
        )
        self.collaboration_events.append(event)

        # 通知监控者
        self._notify_monitor(task_id, execution_result)

        return execution_result

    def _notify_monitor(self, task_id: str, result: Dict):
        """通知监控者任务完成"""
        event = CollaborationEvent(
            type="task_monitored",
            agents_involved=["monitor_1", self.tasks[task_id].assigned_agent],
            task_id=task_id,
            message=f"监控者小M 已评估任务完成结果"
        )
        self.collaboration_events.append(event)

    def collaborative_solve(self, problem: str) -> Dict[str, Any]:
        """协作解决问题 - 多智能体协同解决复杂问题"""
        # 记录协作开始
        event = CollaborationEvent(
            type="collaboration_start",
            agents_involved=list(self.agents.keys()),
            message=f"开始协作解决问题: {problem}"
        )
        self.collaboration_events.append(event)

        # 分析者分析问题
        analysis_task_id = self.create_task(
            description=f"分析问题: {problem}",
            required_capabilities=["analysis", "reasoning"],
            priority=TaskPriority.HIGH
        )
        self.negotiate_task_assignment(analysis_task_id)
        analysis_result = self.execute_task(analysis_task_id)

        # 执行者执行任务
        execution_task_id = self.create_task(
            description=problem,
            required_capabilities=["execution", "data_processing"],
            priority=TaskPriority.NORMAL,
            dependencies=[analysis_task_id]
        )
        self.negotiate_task_assignment(execution_task_id)
        execution_result = self.execute_task(execution_task_id)

        # 监控者评估
        event = CollaborationEvent(
            type="collaboration_completed",
            agents_involved=list(self.agents.keys()),
            message="协作解决问题完成"
        )
        self.collaboration_events.append(event)

        return {
            "problem": problem,
            "status": "solved",
            "analysis": analysis_result,
            "execution": execution_result,
            "collaboration_summary": {
                "agents_involved": list(self.agents.keys()),
                "tasks_created": len(self.tasks),
                "events_logged": len(self.collaboration_events)
            }
        }

    def get_collaboration_history(self, limit: int = 10) -> List[Dict]:
        """获取协作历史"""
        events = self.collaboration_events[-limit:]
        return [
            {
                "type": e.type,
                "agents": e.agents_involved,
                "task_id": e.task_id,
                "message": e.message,
                "timestamp": e.timestamp.isoformat()
            }
            for e in events
        ]

    def learn_from_collaboration(self) -> Dict[str, Any]:
        """从协作中学习 - 收集经验并改进"""
        # 分析协作效率
        total_events = len(self.collaboration_events)
        completed_tasks = len([t for t in self.tasks.values() if t.status == TaskStatus.COMPLETED])

        # 提取成功模式
        success_patterns = []
        for task in self.tasks.values():
            if task.status == TaskStatus.COMPLETED:
                pattern = {
                    "task_type": task.required_capabilities[0] if task.required_capabilities else "unknown",
                    "agent": task.assigned_agent,
                    "duration": (task.completed_at - task.created_at).seconds if task.completed_at else 0
                }
                success_patterns.append(pattern)

        return {
            "total_collaborations": total_events,
            "completed_tasks": completed_tasks,
            "success_rate": completed_tasks / len(self.tasks) if self.tasks else 0,
            "success_patterns": success_patterns[-5:],
            "team_utilization": sum(a.workload for a in self.agents.values()) / len(self.agents) if self.agents else 0,
            "learned_at": datetime.now().isoformat()
        }


# ============== CLI 接口 ==============

def main():
    """CLI 入口"""
    engine = MultiAgentSocialReasoningEngine()

    if len(sys.argv) < 2:
        print("Usage: python multi_agent_social_reasoning_engine.py <command> [args...]")
        print("\nCommands:")
        print("  status                          - 显示团队状态")
        print("  create <description>            - 创建任务")
        print("  analyze <task_id>               - 分析任务")
        print("  assign <task_id>                - 协商分配任务")
        print("  execute <task_id>               - 执行任务")
        print("  solve <problem>                 - 协作解决问题")
        print("  history [limit]                 - 获取协作历史")
        print("  learn                           - 从协作中学习")
        return

    command = sys.argv[1]

    if command == "status":
        result = engine.get_team_status()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "create":
        if len(sys.argv) < 3:
            print("Usage: python multi_agent_social_reasoning_engine.py create <description>")
            return
        description = sys.argv[2]
        task_id = engine.create_task(description, ["execution", "analysis"])
        print(json.dumps({"task_id": task_id, "description": description}, ensure_ascii=False, indent=2))

    elif command == "analyze":
        if len(sys.argv) < 3:
            print("Usage: python multi_agent_social_reasoning_engine.py analyze <task_id>")
            return
        task_id = sys.argv[2]
        result = engine.analyze_task(task_id)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "assign":
        if len(sys.argv) < 3:
            print("Usage: python multi_agent_social_reasoning_engine.py assign <task_id>")
            return
        task_id = sys.argv[2]
        result = engine.negotiate_task_assignment(task_id)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "execute":
        if len(sys.argv) < 3:
            print("Usage: python multi_agent_social_reasoning_engine.py execute <task_id>")
            return
        task_id = sys.argv[2]
        result = engine.execute_task(task_id)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "solve":
        if len(sys.argv) < 3:
            print("Usage: python multi_agent_social_reasoning_engine.py solve <problem>")
            return
        problem = sys.argv[2]
        result = engine.collaborative_solve(problem)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "history":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        result = engine.get_collaboration_history(limit)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "learn":
        result = engine.learn_from_collaboration()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()