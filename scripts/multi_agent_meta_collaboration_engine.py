#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景智能体元协作与社会化学习增强引擎 (Multi-Agent Meta-Collaboration Engine)
版本: 1.0.0

让系统能够增强多智能体之间的协作能力，增加社会化学习、群体智慧聚合、经验共享能力，
实现真正的智能体团队协作进化。

功能：
1. 元协作增强 - 高层次协作模式和组织结构
2. 社会化学习 - 智能体之间互相学习最佳实践
3. 群体智慧聚合 - 汇总多个智能体的意见形成更好的决策
4. 经验共享机制 - 跨任务、跨场景的经验传递
5. 协作进化 - 智能体团队共同进化和能力提升
"""

import json
import os
import sys
import re
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Set
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
import math

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
RUNTIME_STATE_DIR = PROJECT_ROOT / "runtime" / "state"
LOGS_DIR = PROJECT_ROOT / "runtime" / "logs"

# 尝试导入现有的多智能体协作引擎
try:
    sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
    from multi_agent_social_reasoning_engine import (
        MultiAgentSocialReasoningEngine as BaseEngine,
        Agent, Task, AgentRole, TaskPriority, TaskStatus
    )
    BASE_ENGINE_AVAILABLE = True
except ImportError:
    BASE_ENGINE_AVAILABLE = False
    # 如果导入失败，定义基础类
    class AgentRole(Enum):
        COORDINATOR = "coordinator"
        EXECUTOR = "executor"
        ANALYZER = "analyzer"
        MONITOR = "monitor"
        COMMUNICATOR = "communicator"

    class TaskPriority(Enum):
        URGENT = 1
        HIGH = 2
        NORMAL = 3
        LOW = 4

    @dataclass
    class Agent:
        id: str
        name: str
        role: AgentRole
        capabilities: List[str] = field(default_factory=list)
        workload: int = 0
        status: str = "idle"
        expertise: List[str] = field(default_factory=list)

    @dataclass
    class Task:
        id: str
        description: str
        required_capabilities: List[str]
        priority: TaskPriority = TaskPriority.NORMAL
        result: Any = None


class CollaborationPattern(Enum):
    """协作模式"""
    HIERARCHICAL = "hierarchical"       # 层级协作
    DISTRIBUTED = "distributed"         # 分布式协作
    SWARM = "swarm"                      # 群体协作
    PEER_TO_PEER = "peer_to_peer"        # 点对点协作
    META_COLLABORATION = "meta"          # 元协作（协作的协作）


class LearningMode(Enum):
    """学习模式"""
    SUPERVISED = "supervised"            # 监督学习 - 从明确反馈学习
    IMITATION = "imitation"              # 模仿学习 - 模仿成功案例
    REINFORCEMENT = "reinforcement"      # 强化学习 - 从结果反馈学习
    SOCIAL_LEARNING = "social"           # 社会化学习 - 从其他智能体学习
    COLLECTIVE = "collective"            # 群体学习 - 集体智慧


@dataclass
class AgentExperience:
    """智能体经验"""
    task_type: str
    success_patterns: List[str] = field(default_factory=list)
    failure_patterns: List[str] = field(default_factory=list)
    best_strategies: List[str] = field(default_factory=list)
    execution_count: int = 0
    success_count: int = 0
    avg_execution_time: float = 0.0
    last_used: Optional[datetime] = None
    confidence: float = 0.5  # 经验置信度


@dataclass
class CollectiveWisdom:
    """群体智慧"""
    topic: str
    votes: Dict[str, int] = field(default_factory=dict)  # 选项 -> 票数
    reasoning_paths: List[str] = field(default_factory=list)
    consensus_score: float = 0.0
    participant_count: int = 0
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class CollaborationMetric:
    """协作指标"""
    collaboration_id: str
    pattern: CollaborationPattern
    efficiency: float = 0.0          # 协作效率
    quality: float = 0.0             # 结果质量
    learning_gain: float = 0.0       # 学习收益
    knowledge_sharing: float = 0.0   # 知识共享程度
    evolution_score: float = 0.0    # 进化程度


class MultiAgentMetaCollaborationEngine:
    """智能体元协作与社会化学习增强引擎"""

    def __init__(self):
        self.state_file = RUNTIME_STATE_DIR / "meta_collaboration_state.json"
        self.experiences_file = RUNTIME_STATE_DIR / "agent_experiences.json"
        self.wisdom_file = RUNTIME_STATE_DIR / "collective_wisdom.json"
        self.metrics_file = RUNTIME_STATE_DIR / "collaboration_metrics.json"

        # 状态数据
        self.state = self._load_state()

        # 智能体注册表
        self.agents: Dict[str, Agent] = {}

        # 经验库（社会化学习用）
        self.experiences: Dict[str, List[AgentExperience]] = {}

        # 群体智慧库
        self.collective_wisdom: Dict[str, CollectiveWisdom] = {}

        # 协作历史
        self.collaboration_history: List[Dict] = []

        # 初始化
        self._ensure_directories()
        self._load_experiences()
        self._load_collective_wisdom()

    def _ensure_directories(self):
        """确保必要的目录存在"""
        RUNTIME_STATE_DIR.mkdir(parents=True, exist_ok=True)
        LOGS_DIR.mkdir(parents=True, exist_ok=True)

    def _load_state(self) -> Dict:
        """加载状态"""
        if self.state_file.exists():
            with open(self.state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "initialized_at": datetime.now().isoformat(),
            "collaboration_rounds": 0,
            "total_learning_events": 0,
            "wisdom_topics": []
        }

    def _save_state(self):
        """保存状态"""
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2)

    def _load_experiences(self):
        """加载经验库"""
        if self.experiences_file.exists():
            with open(self.experiences_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for agent_id, exp_list in data.items():
                    self.experiences[agent_id] = [
                        AgentExperience(
                            task_type=e["task_type"],
                            success_patterns=e.get("success_patterns", []),
                            failure_patterns=e.get("failure_patterns", []),
                            best_strategies=e.get("best_strategies", []),
                            execution_count=e.get("execution_count", 0),
                            success_count=e.get("success_count", 0),
                            avg_execution_time=e.get("avg_execution_time", 0.0),
                            confidence=e.get("confidence", 0.5)
                        ) for e in exp_list
                    ]

    def _save_experiences(self):
        """保存经验库"""
        data = {}
        for agent_id, exp_list in self.experiences.items():
            data[agent_id] = [
                {
                    "task_type": e.task_type,
                    "success_patterns": e.success_patterns,
                    "failure_patterns": e.failure_patterns,
                    "best_strategies": e.best_strategies,
                    "execution_count": e.execution_count,
                    "success_count": e.success_count,
                    "avg_execution_time": e.avg_execution_time,
                    "confidence": e.confidence
                } for e in exp_list
            ]
        with open(self.experiences_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _load_collective_wisdom(self):
        """加载群体智慧库"""
        if self.wisdom_file.exists():
            with open(self.wisdom_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for topic, wisdom in data.items():
                    self.collective_wisdom[topic] = CollectiveWisdom(
                        topic=wisdom["topic"],
                        votes=wisdom.get("votes", {}),
                        reasoning_paths=wisdom.get("reasoning_paths", []),
                        consensus_score=wisdom.get("consensus_score", 0.0),
                        participant_count=wisdom.get("participant_count", 0)
                    )

    def _save_collective_wisdom(self):
        """保存群体智慧库"""
        data = {}
        for topic, wisdom in self.collective_wisdom.items():
            data[topic] = {
                "topic": wisdom.topic,
                "votes": wisdom.votes,
                "reasoning_paths": wisdom.reasoning_paths,
                "consensus_score": wisdom.consensus_score,
                "participant_count": wisdom.participant_count,
                "created_at": wisdom.created_at.isoformat()
            }
        with open(self.wisdom_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def register_agent(self, agent: Agent) -> bool:
        """注册智能体"""
        if agent.id in self.agents:
            return False  # 已存在

        self.agents[agent.id] = agent

        # 为新智能体初始化经验存储
        if agent.id not in self.experiences:
            self.experiences[agent.id] = []

        self._save_state()
        return True

    def unregister_agent(self, agent_id: str) -> bool:
        """注销智能体"""
        if agent_id not in self.agents:
            return False

        del self.agents[agent_id]
        self._save_state()
        return True

    def record_experience(self, agent_id: str, task_type: str,
                          success: bool, execution_time: float,
                          pattern: str, strategy: str):
        """记录智能体经验（社会化学习基础）"""
        if agent_id not in self.experiences:
            self.experiences[agent_id] = []

        # 查找现有经验
        exp = None
        for e in self.experiences[agent_id]:
            if e.task_type == task_type:
                exp = e
                break

        if exp is None:
            # 创建新经验
            exp = AgentExperience(task_type=task_type)
            self.experiences[agent_id].append(exp)

        # 更新经验
        exp.execution_count += 1
        if success:
            exp.success_count += 1
            if pattern not in exp.success_patterns:
                exp.success_patterns.append(pattern)
            if strategy not in exp.best_strategies:
                exp.best_strategies.append(strategy)
        else:
            if pattern not in exp.failure_patterns:
                exp.failure_patterns.append(pattern)

        # 更新执行时间和置信度
        exp.avg_execution_time = (
            (exp.avg_execution_time * (exp.execution_count - 1) + execution_time)
            / exp.execution_count
        )
        exp.confidence = min(1.0, exp.success_count / exp.execution_count)
        exp.last_used = datetime.now()

        self._save_experiences()

        # 更新状态
        self.state["total_learning_events"] = self.state.get("total_learning_events", 0) + 1
        self._save_state()

    def get_best_practices(self, agent_id: str, task_type: str) -> List[str]:
        """获取某类任务的最佳实践（社会化学习核心）"""
        if agent_id not in self.experiences:
            return []

        # 查找相关经验
        for exp in self.experiences[agent_id]:
            if exp.task_type == task_type:
                # 按置信度排序返回最佳策略
                if exp.confidence >= 0.5 and exp.best_strategies:
                    return exp.best_strategies[:3]

        # 如果本地没有，尝试从其他智能体学习
        return self._social_learn(agent_id, task_type)

    def _social_learn(self, agent_id: str, task_type: str) -> List[str]:
        """社会化学习：从其他智能体学习"""
        best_practices = []

        # 查找其他智能体对该任务的经验
        for other_id, exp_list in self.experiences.items():
            if other_id == agent_id:
                continue

            for exp in exp_list:
                if exp.task_type == task_type and exp.confidence >= 0.6:
                    best_practices.extend(exp.best_strategies[:2])

        # 去重并返回
        return list(set(best_practices))[:3]

    def gather_collective_wisdom(self, topic: str,
                                 perspectives: List[Tuple[str, str]]) -> CollectiveWisdom:
        """收集群体智慧（多个智能体对同一问题的观点）"""
        wisdom = CollectiveWisdom(topic=topic)

        # 统计投票
        for agent_id, perspective in perspectives:
            wisdom.votes[perspective] = wisdom.votes.get(perspective, 0) + 1
            wisdom.reasoning_paths.append(f"{agent_id}: {perspective}")

        wisdom.participant_count = len(perspectives)

        # 计算共识分数（基于最多票数占比）
        if wisdom.votes:
            max_votes = max(wisdom.votes.values())
            total_votes = sum(wisdom.votes.values())
            wisdom.consensus_score = max_votes / total_votes if total_votes > 0 else 0

        # 保存
        self.collective_wisdom[topic] = wisdom
        self._save_collective_wisdom()

        return wisdom

    def query_wisdom(self, topic: str) -> Optional[Dict]:
        """查询群体智慧"""
        if topic not in self.collective_wisdom:
            return None

        wisdom = self.collective_wisdom[topic]
        return {
            "topic": wisdom.topic,
            "votes": wisdom.votes,
            "consensus_score": wisdom.consensus_score,
            "reasoning_paths": wisdom.reasoning_paths[:5],
            "participant_count": wisdom.participant_count
        }

    def get_collaboration_recommendation(self, task_complexity: str,
                                         available_agents: List[str]) -> Dict:
        """获取协作推荐（基于任务复杂度和可用智能体）"""
        # 基于任务复杂度选择协作模式
        if task_complexity == "high":
            pattern = CollaborationPattern.SWARM
        elif task_complexity == "medium":
            pattern = CollaborationPattern.DISTRIBUTED
        else:
            pattern = CollaborationPattern.PEER_TO_PEER

        # 评估每个智能体
        agent_scores = []
        for agent_id in available_agents:
            if agent_id not in self.agents:
                continue

            agent = self.agents[agent_id]

            # 计算得分（考虑经验、工作负载、状态）
            exp_score = 0
            if agent_id in self.experiences:
                exps = self.experiences[agent_id]
                if exps:
                    exp_score = sum(e.confidence for e in exps) / len(exps)

            workload_penalty = agent.workload / 100.0
            status_bonus = 1.0 if agent.status == "idle" else 0.5

            score = (exp_score * 0.4 + status_bonus * 0.6) * (1 - workload_penalty)
            agent_scores.append((agent_id, score))

        # 排序并返回推荐
        agent_scores.sort(key=lambda x: x[1], reverse=True)

        return {
            "recommended_pattern": pattern.value,
            "recommended_agents": [a[0] for a in agent_scores[:5]],
            "reasoning": f"基于{len(available_agents)}个可用智能体的经验和状态分析"
        }

    def analyze_collaboration_effectiveness(self) -> Dict:
        """分析协作有效性"""
        if not self.agents:
            return {"efficiency": 0, "quality": 0, "learning_gain": 0}

        # 计算平均经验置信度
        total_confidence = 0
        total_experiences = 0
        for agent_id, exp_list in self.experiences.items():
            for exp in exp_list:
                total_confidence += exp.confidence
                total_experiences += 1

        learning_gain = total_confidence / total_experiences if total_experiences > 0 else 0

        # 计算协作效率（基于智能体数量和工作负载分布）
        avg_workload = sum(a.workload for a in self.agents.values()) / len(self.agents)
        efficiency = 1 - (avg_workload / 100)

        # 知识共享程度
        knowledge_sharing = min(1.0, len(self.collective_wisdom) / 10)

        return {
            "efficiency": round(efficiency, 2),
            "quality": round(learning_gain, 2),
            "learning_gain": round(learning_gain, 2),
            "knowledge_sharing": round(knowledge_sharing, 2),
            "agent_count": len(self.agents),
            "experience_count": total_experiences,
            "wisdom_topics": len(self.collective_wisdom)
        }

    def evolve_collaboration(self) -> Dict:
        """协作进化：根据效果分析优化协作策略"""
        analysis = self.analyze_collaboration_effectiveness()

        suggestions = []

        # 基于分析生成进化建议
        if analysis["efficiency"] < 0.5:
            suggestions.append("建议：优化任务分配，减少工作负载不均")

        if analysis["learning_gain"] < 0.5:
            suggestions.append("建议：加强社会化学习，增加经验共享频率")

        if analysis["knowledge_sharing"] < 0.3:
            suggestions.append("建议：增加群体智慧收集，覆盖更多主题")

        # 更新协作模式（基于效果调整）
        self.state["collaboration_rounds"] = self.state.get("collaboration_rounds", 0) + 1

        # 生成进化报告
        return {
            "evolution_round": self.state["collaboration_rounds"],
            "current_metrics": analysis,
            "suggestions": suggestions,
            "next_actions": suggestions[:2] if suggestions else ["继续监控和优化"]
        }

    def execute_meta_collaboration(self, task: Dict) -> Dict:
        """执行元协作（协作的协作）"""
        task_id = task.get("id", f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        task_type = task.get("type", "general")
        complexity = task.get("complexity", "low")

        # 步骤1：获取协作推荐
        available_agents = list(self.agents.keys())
        if not available_agents:
            # 如果没有注册智能体，创建默认智能体
            default_agent = Agent(
                id="meta_agent_1",
                name="MetaAgent-1",
                role=AgentRole.COORDINATOR,
                capabilities=["analysis", "execution", "learning"]
            )
            self.register_agent(default_agent)
            available_agents = ["meta_agent_1"]

        recommendation = self.get_collaboration_recommendation(complexity, available_agents)

        # 步骤2：收集群体智慧（对于复杂任务）
        wisdom_result = None
        if complexity == "high":
            perspectives = []
            for agent_id in recommendation["recommended_agents"][:3]:
                agent = self.agents.get(agent_id)
                if agent:
                    perspectives.append((agent_id, f"智能体{agent.name}的分析视角"))

            if perspectives:
                wisdom_result = self.gather_collective_wisdom(f"task_{task_id}", perspectives)

        # 步骤3：执行并记录经验
        execution_result = {
            "task_id": task_id,
            "collaboration_pattern": recommendation["recommended_pattern"],
            "agents_used": recommendation["recommended_agents"],
            "wisdom_collected": wisdom_result is not None,
            "wisdom_consensus": wisdom_result.consensus_score if wisdom_result else 0
        }

        # 记录历史
        self.collaboration_history.append({
            "task_id": task_id,
            "timestamp": datetime.now().isoformat(),
            **execution_result
        })

        # 更新状态
        self._save_state()

        return {
            "success": True,
            "task_id": task_id,
            "collaboration": execution_result,
            "recommendation": recommendation,
            "wisdom": wisdom_result.topic if wisdom_result else None
        }


# 独立运行入口
if __name__ == "__main__":
    engine = MultiAgentMetaCollaborationEngine()

    # 测试：注册一些智能体
    agents = [
        Agent(id="analyzer_1", name="Analyzer-1", role=AgentRole.ANALYZER,
              capabilities=["analysis", "planning"], expertise=["data_analysis"]),
        Agent(id="executor_1", name="Executor-1", role=AgentRole.EXECUTOR,
              capabilities=["execution", "automation"], expertise=["task_execution"]),
        Agent(id="coordinator_1", name="Coordinator-1", role=AgentRole.COORDINATOR,
              capabilities=["coordination", "monitoring"], expertise=["team_management"])
    ]

    for agent in agents:
        engine.register_agent(agent)

    # 测试：记录一些经验
    engine.record_experience("analyzer_1", "data_analysis", True, 2.5, "pattern_a", "strategy_x")
    engine.record_experience("analyzer_1", "data_analysis", True, 2.3, "pattern_b", "strategy_y")
    engine.record_experience("executor_1", "task_execution", True, 1.8, "pattern_c", "strategy_z")

    # 测试：获取最佳实践（社会化学习）
    best = engine.get_best_practices("analyzer_1", "data_analysis")
    print(f"Best practices: {best}")

    # 测试：获取协作推荐
    recommendation = engine.get_collaboration_recommendation("high", ["analyzer_1", "executor_1", "coordinator_1"])
    print(f"Recommendation: {recommendation}")

    # 测试：执行元协作
    result = engine.execute_meta_collaboration({
        "type": "complex_analysis",
        "complexity": "high"
    })
    print(f"Meta collaboration result: {result}")

    # 测试：协作进化
    evolution = engine.evolve_collaboration()
    print(f"Evolution: {evolution}")

    # 测试：分析有效性
    analysis = engine.analyze_collaboration_effectiveness()
    print(f"Analysis: {analysis}")