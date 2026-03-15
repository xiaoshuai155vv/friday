#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环跨轮次决策-执行-学习深度集成增强引擎
(Cross-Round Decision-Execution-Learning Deep Integration Engine)

在 round 514 完成的决策-执行-学习完整闭环深度集成引擎基础上，
进一步增强跨轮次的决策-执行-学习闭环。让系统能够将跨轮次学习记忆能力
与决策-执行闭环深度集成，实现跨轮次的经验复用、策略传承和递归优化。

让进化环不仅能在单轮内形成决策-执行-学习闭环，还能跨越多个轮次
积累和传承学习成果，形成真正的「代际进化」能力。

Version: 1.1.0

功能特性：
1. 跨轮次决策经验传承（将历史决策结果和效果传递给后续轮次）
2. 跨轮次执行模式复用（识别并复用成功的执行策略）
3. 跨轮次学习闭环（将学习结果跨轮次传递并应用到决策优化）
4. 跨轮次价值评估与优化建议生成
5. 与进化驾驶舱深度集成
"""

import json
import os
import sys
import subprocess
import time
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from enum import Enum

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
STATE_DIR = PROJECT_ROOT / "runtime" / "state"
DATA_DIR = PROJECT_ROOT / "runtime" / "data"
LOGS_DIR = PROJECT_ROOT / "runtime" / "logs"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"

# 添加 scripts 目录到路径以便导入
sys.path.insert(0, str(SCRIPTS_DIR))


class DecisionType(Enum):
    """决策类型"""
    STRATEGY = "strategy"
    PARAMETER = "parameter"
    ENGINE_SELECTION = "engine_selection"
    TIMEOUT = "timeout"
    PRIORITY = "priority"


class ExecutionStatus(Enum):
    """执行状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"


class LearningSource(Enum):
    """学习来源"""
    DECISION_OUTCOME = "decision_outcome"  # 决策结果
    EXECUTION_RESULT = "execution_result"  # 执行结果
    PATTERN_ANALYSIS = "pattern_analysis"  # 模式分析
    OPTIMIZATION_FEEDBACK = "optimization_feedback"  # 优化反馈
    CROSS_ROUND = "cross_round"  # 跨轮次学习


@dataclass
class DecisionRecord:
    """决策记录"""
    decision_id: str
    decision_type: DecisionType
    decision_content: str
    context: Dict[str, Any]
    timestamp: str
    executed: bool = False
    execution_id: str = ""
    source_round: int = 0  # 新增：来源轮次


@dataclass
class ExecutionFeedback:
    """执行反馈"""
    execution_id: str
    decision_id: str
    status: ExecutionStatus
    success_count: int
    failed_count: int
    duration: float
    errors: List[str] = field(default_factory=list)
    adjustments: List[str] = field(default_factory=list)
    timestamp: str = ""
    execution_round: int = 0  # 新增：执行轮次


@dataclass
class LearningInsight:
    """学习洞察"""
    insight_id: str
    source: LearningSource
    content: str
    confidence: float
    actionable: bool
    timestamp: str
    applied: bool = False
    application_result: str = ""
    applicable_rounds: List[int] = field(default_factory=list)  # 新增：适用轮次


@dataclass
class CrossRoundExperience:
    """跨轮次经验"""
    experience_id: str
    round_from: int
    round_to: int
    decision_type: str
    success_pattern: Dict[str, Any]
    failure_pattern: Dict[str, Any]
    effectiveness_score: float
    inherited: bool = False


class CrossRoundDecisionExecutionLearningEngine:
    """跨轮次决策-执行-学习深度集成增强引擎"""

    VERSION = "1.1.0"

    def __init__(self):
        self.db_path = DATA_DIR / "cross_round_del_integration.db"
        self.cross_round_memory_db = DATA_DIR / "learning_data" / "cross_round_learning_enhanced.db"
        self._init_database()
        self.closed_loop_history = []

    def _init_database(self):
        """初始化数据库"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # 决策记录表（增加轮次字段）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS decisions (
                decision_id TEXT PRIMARY KEY,
                decision_type TEXT,
                decision_content TEXT,
                context TEXT,
                timestamp TEXT,
                executed INTEGER DEFAULT 0,
                execution_id TEXT,
                source_round INTEGER DEFAULT 0
            )
        ''')

        # 执行反馈表（增加轮次字段）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS execution_feedback (
                execution_id TEXT PRIMARY KEY,
                decision_id TEXT,
                status TEXT,
                success_count INTEGER,
                failed_count INTEGER,
                duration REAL,
                errors TEXT,
                adjustments TEXT,
                timestamp TEXT,
                execution_round INTEGER DEFAULT 0
            )
        ''')

        # 学习洞察表（增加适用轮次字段）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learning_insights (
                insight_id TEXT PRIMARY KEY,
                source TEXT,
                content TEXT,
                confidence REAL,
                actionable INTEGER,
                timestamp TEXT,
                applied INTEGER DEFAULT 0,
                application_result TEXT,
                applicable_rounds TEXT
            )
        ''')

        # 闭环记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS closed_loop_records (
                loop_id TEXT PRIMARY KEY,
                decision_id TEXT,
                execution_id TEXT,
                insight_id TEXT,
                optimization_applied TEXT,
                timestamp TEXT,
                effectiveness_score REAL,
                loop_round INTEGER DEFAULT 0
            )
        ''')

        # 新增：跨轮次经验传承表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cross_round_experiences (
                experience_id TEXT PRIMARY KEY,
                round_from INTEGER,
                round_to INTEGER,
                decision_type TEXT,
                success_pattern TEXT,
                failure_pattern TEXT,
                effectiveness_score REAL,
                applied INTEGER DEFAULT 0,
                applied_at TEXT,
                created_at TEXT
            )
        ''')

        # 新增：跨轮次价值评估表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cross_round_value_assessment (
                assessment_id TEXT PRIMARY KEY,
                round_number INTEGER,
                decision_type TEXT,
                execution_strategy TEXT,
                success_rate REAL,
                average_duration REAL,
                value_score REAL,
                trend TEXT,
                recommendations TEXT,
                created_at TEXT
            )
        ''')

        conn.commit()
        conn.close()

    def store_decision(self, decision: DecisionRecord) -> bool:
        """存储决策记录"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO decisions
                (decision_id, decision_type, decision_content, context, timestamp, executed, execution_id, source_round)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                decision.decision_id,
                decision.decision_type.value,
                decision.decision_content,
                json.dumps(decision.context),
                decision.timestamp,
                int(decision.executed),
                decision.execution_id,
                decision.source_round
            ))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"存储决策失败: {e}")
            return False

    def link_decision_to_execution(self, decision_id: str, execution_id: str) -> bool:
        """将决策链接到执行"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE decisions
                SET executed = 1, execution_id = ?
                WHERE decision_id = ?
            ''', (execution_id, decision_id))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"链接决策到执行失败: {e}")
            return False

    def store_execution_feedback(self, feedback: ExecutionFeedback) -> bool:
        """存储执行反馈"""
        try:
            if not feedback.timestamp:
                feedback.timestamp = datetime.now().isoformat()

            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO execution_feedback
                (execution_id, decision_id, status, success_count, failed_count, duration, errors, adjustments, timestamp, execution_round)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                feedback.execution_id,
                feedback.decision_id,
                feedback.status.value,
                feedback.success_count,
                feedback.failed_count,
                feedback.duration,
                json.dumps(feedback.errors),
                json.dumps(feedback.adjustments),
                feedback.timestamp,
                feedback.execution_round
            ))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"存储执行反馈失败: {e}")
            return False

    def extract_cross_round_experiences(self, current_round: int, min_rounds: int = 3) -> List[CrossRoundExperience]:
        """从历史数据中提取跨轮次经验"""
        experiences = []
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # 获取历史决策和执行数据
        cursor.execute('''
            SELECT d.decision_id, d.decision_type, d.decision_content, d.context, d.source_round,
                   e.execution_id, e.status, e.success_count, e.failed_count, e.duration
            FROM decisions d
            LEFT JOIN execution_feedback e ON d.execution_id = e.execution_id
            WHERE d.source_round < ?
            ORDER BY d.source_round DESC
            LIMIT 100
        ''', (current_round - min_rounds,))

        rows = cursor.fetchall()
        conn.close()

        # 按决策类型分组分析
        decision_patterns = defaultdict(list)
        for row in rows:
            decision_id, decision_type, decision_content, context_str, source_round, \
                execution_id, status, success_count, failed_count, duration = row

            context = json.loads(context_str) if context_str else {}
            pattern = {
                "decision_id": decision_id,
                "content": decision_content,
                "context": context,
                "source_round": source_round,
                "success": status == "completed" and failed_count == 0,
                "duration": duration
            }
            decision_patterns[decision_type].append(pattern)

        # 为每种决策类型提取经验
        for decision_type, patterns in decision_patterns.items():
            if len(patterns) >= min_rounds:
                # 分析成功模式
                success_patterns = [p for p in patterns if p["success"]]
                failure_patterns = [p for p in patterns if not p["success"]]

                if success_patterns:
                    # 计算平均效果分数
                    avg_duration = sum(p["duration"] for p in success_patterns) / len(success_patterns)
                    effectiveness = min(1.0, len(success_patterns) / len(patterns))

                    experience = CrossRoundExperience(
                        experience_id=f"exp_{decision_type}_{current_round}",
                        round_from=min(p["source_round"] for p in patterns),
                        round_to=current_round,
                        decision_type=decision_type,
                        success_pattern={
                            "common_context": self._extract_common_context(success_patterns),
                            "average_duration": avg_duration,
                            "sample_count": len(success_patterns)
                        },
                        failure_pattern={
                            "common_context": self._extract_common_context(failure_patterns) if failure_patterns else {},
                            "failure_count": len(failure_patterns)
                        } if failure_patterns else {},
                        effectiveness_score=effectiveness
                    )
                    experiences.append(experience)

        # 存储提取的经验
        for exp in experiences:
            self._store_cross_round_experience(exp, current_round)

        return experiences

    def _extract_common_context(self, patterns: List[Dict]) -> Dict:
        """提取共同的上下文特征"""
        if not patterns:
            return {}

        # 简化：取第一个成功模式的上下文作为代表
        return patterns[0].get("context", {})

    def _store_cross_round_experience(self, experience: CrossRoundExperience, current_round: int):
        """存储跨轮次经验"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO cross_round_experiences
                (experience_id, round_from, round_to, decision_type, success_pattern, failure_pattern, effectiveness_score, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                experience.experience_id,
                experience.round_from,
                experience.round_to,
                experience.decision_type,
                json.dumps(experience.success_pattern),
                json.dumps(experience.failure_pattern),
                effectiveness,
                datetime.now().isoformat()
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"存储跨轮次经验失败: {e}")

    def get_inherited_experiences(self, decision_type: str = None) -> List[Dict[str, Any]]:
        """获取可继承的经验"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        if decision_type:
            cursor.execute('''
                SELECT experience_id, round_from, round_to, decision_type,
                       success_pattern, failure_pattern, effectiveness_score, applied
                FROM cross_round_experiences
                WHERE decision_type = ? AND applied = 0
                ORDER BY effectiveness_score DESC
                LIMIT 10
            ''', (decision_type,))
        else:
            cursor.execute('''
                SELECT experience_id, round_from, round_to, decision_type,
                       success_pattern, failure_pattern, effectiveness_score, applied
                FROM cross_round_experiences
                WHERE applied = 0
                ORDER BY effectiveness_score DESC
                LIMIT 20
            ''')

        rows = cursor.fetchall()
        conn.close()

        return [
            {
                "experience_id": row[0],
                "round_from": row[1],
                "round_to": row[2],
                "decision_type": row[3],
                "success_pattern": json.loads(row[4]) if row[4] else {},
                "failure_pattern": json.loads(row[5]) if row[5] else {},
                "effectiveness_score": row[6],
                "applied": bool(row[7])
            }
            for row in rows
        ]

    def apply_cross_round_learning(self, decision_context: Dict[str, Any], current_round: int) -> Dict[str, Any]:
        """将跨轮次学习应用到决策"""
        # 获取可继承的经验
        decision_type = decision_context.get("decision_type", "strategy")
        inherited_experiences = self.get_inherited_experiences(decision_type)

        if not inherited_experiences:
            # 如果没有特定决策类型的经验，获取所有类型的经验
            inherited_experiences = self.get_inherited_experiences()

        # 生成优化建议
        optimization_hints = []
        for exp in inherited_experiences[:5]:
            hint = {
                "experience_id": exp["experience_id"],
                "decision_type": exp["decision_type"],
                "effectiveness_score": exp["effectiveness_score"],
                "success_pattern": exp["success_pattern"],
                "warning": f"基于 round {exp['round_from']} 的经验（效果分数: {exp['effectiveness_score']:.2f}）"
            }
            optimization_hints.append(hint)

        # 提取轮次传承建议
        inheritance_recommendations = []
        if decision_type == "strategy":
            # 策略类决策：基于历史成功策略
            for exp in inherited_experiences[:3]:
                if exp["effectiveness_score"] > 0.7:
                    inheritance_recommendations.append({
                        "type": "strategy_inheritance",
                        "recommendation": f"采用类似 round {exp['round_from']} 的策略模式",
                        "confidence": exp["effectiveness_score"]
                    })

        return {
            "cross_round_learning_applied": len(optimization_hints) > 0,
            "inheritance_recommendations": inheritance_recommendations,
            "optimization_hints": optimization_hints,
            "context_enhanced": {
                **decision_context,
                "cross_round_experiences": optimization_hints,
                "inheritance_applied": len(inheritance_recommendations) > 0
            }
        }

    def generate_cross_round_value_assessment(self, current_round: int) -> Dict[str, Any]:
        """生成跨轮次价值评估"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # 按决策类型和轮次统计
        cursor.execute('''
            SELECT d.decision_type, d.source_round,
                   COUNT(*) as total,
                   SUM(CASE WHEN e.status = 'completed' THEN 1 ELSE 0 END) as success,
                   AVG(e.duration) as avg_duration
            FROM decisions d
            LEFT JOIN execution_feedback e ON d.execution_id = e.execution_id
            WHERE d.source_round > 0
            GROUP BY d.decision_type, d.source_round
            ORDER BY d.source_round DESC
        ''')

        rows = cursor.fetchall()
        conn.close()

        # 按决策类型聚合
        type_assessments = defaultdict(lambda: {"rounds": [], "success_rates": [], "durations": []})

        for row in rows:
            decision_type, round_num, total, success, avg_duration = row
            if total and success is not None:
                success_rate = success / total if total > 0 else 0
                type_assessments[decision_type]["rounds"].append(round_num)
                type_assessments[decision_type]["success_rates"].append(success_rate)
                type_assessments[decision_type]["durations"].append(avg_duration or 0)

        # 生成评估结果
        assessments = []
        trends = []

        for decision_type, data in type_assessments.items():
            if len(data["success_rates"]) >= 2:
                # 计算趋势
                recent_rate = data["success_rates"][0]
                older_rate = data["success_rates"][-1]
                trend = "improving" if recent_rate > older_rate else "declining" if recent_rate < older_rate else "stable"

                # 计算价值分数
                avg_success = sum(data["success_rates"]) / len(data["success_rates"])
                avg_duration = sum(data["durations"]) / len(data["durations"])
                value_score = avg_success * 0.7 + (1 / (1 + avg_duration / 60)) * 0.3  # 权重：成功率70%，效率30%

                # 生成建议
                recommendations = []
                if trend == "declining":
                    recommendations.append("该类型决策成功率下降，需分析失败原因并调整策略")
                elif trend == "improving":
                    recommendations.append("该类型决策持续改进，可考虑扩展应用范围")
                else:
                    recommendations.append("该类型决策保持稳定，可作为基准参考")

                assessment = {
                    "assessment_id": f"assess_{decision_type}_{current_round}",
                    "round_number": current_round,
                    "decision_type": decision_type,
                    "success_rate": recent_rate,
                    "average_duration": avg_duration,
                    "value_score": value_score,
                    "trend": trend,
                    "recommendations": recommendations
                }
                assessments.append(assessment)
                trends.append({
                    "type": decision_type,
                    "trend": trend,
                    "value_score": value_score
                })

                # 存储评估
                self._store_value_assessment(assessment)

        return {
            "assessments": assessments,
            "overall_trends": trends,
            "summary": {
                "total_types": len(assessments),
                "improving_count": sum(1 for t in trends if t["trend"] == "improving"),
                "declining_count": sum(1 for t in trends if t["trend"] == "declining"),
                "stable_count": sum(1 for t in trends if t["trend"] == "stable")
            }
        }

    def _store_value_assessment(self, assessment: Dict[str, Any]):
        """存储价值评估"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO cross_round_value_assessment
                (assessment_id, round_number, decision_type, execution_strategy, success_rate,
                 average_duration, value_score, trend, recommendations, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                assessment["assessment_id"],
                assessment["round_number"],
                assessment["decision_type"],
                "",  # execution_strategy
                assessment["success_rate"],
                assessment["average_duration"],
                assessment["value_score"],
                assessment["trend"],
                json.dumps(assessment["recommendations"]),
                datetime.now().isoformat()
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"存储价值评估失败: {e}")

    def generate_learning_insights(self) -> List[LearningInsight]:
        """基于决策-执行-执行反馈生成学习洞察（增强跨轮次版）"""
        insights = []
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # 查询已执行的决策及其执行反馈
        cursor.execute('''
            SELECT d.decision_id, d.decision_type, d.decision_content, d.context, d.source_round,
                   e.execution_id, e.status, e.success_count, e.failed_count, e.duration, e.errors
            FROM decisions d
            JOIN execution_feedback e ON d.execution_id = e.execution_id
            WHERE d.executed = 1
            ORDER BY e.timestamp DESC
            LIMIT 50
        ''')

        rows = cursor.fetchall()
        conn.close()

        # 分析模式并生成洞察
        success_patterns = defaultdict(list)
        failure_patterns = defaultdict(list)

        for row in rows:
            decision_id, decision_type, decision_content, context_str, source_round, \
                execution_id, status, success_count, failed_count, duration, errors = row

            context = json.loads(context_str) if context_str else {}
            error_list = json.loads(errors) if errors else []

            if status == "completed" and failed_count == 0:
                success_patterns[decision_type].append({
                    "decision_id": decision_id,
                    "content": decision_content,
                    "context": context,
                    "duration": duration,
                    "source_round": source_round
                })
            elif status == "failed" or failed_count > 0:
                failure_patterns[decision_type].append({
                    "decision_id": decision_id,
                    "content": decision_content,
                    "context": context,
                    "errors": error_list,
                    "source_round": source_round
                })

        # 生成优化洞察
        for decision_type, patterns in success_patterns.items():
            if len(patterns) >= 3:
                insight = LearningInsight(
                    insight_id=f"insight_{int(time.time()*1000)}",
                    source=LearningSource.DECISION_OUTCOME,
                    content=f"决策类型 {decision_type} 在过去表现良好，成功率较高，可考虑复用此策略",
                    confidence=min(0.9, len(patterns) * 0.1),
                    actionable=True,
                    timestamp=datetime.now().isoformat(),
                    applicable_rounds=[p["source_round"] for p in patterns]
                )
                insights.append(insight)

        # 生成跨轮次洞察
        if len(rows) >= 10:
            insight = LearningInsight(
                insight_id=f"cross_round_insight_{int(time.time()*1000)}",
                source=LearningSource.CROSS_ROUND,
                content="检测到跨轮次学习机会，可提取成功模式并应用到当前轮次决策",
                confidence=0.75,
                actionable=True,
                timestamp=datetime.now().isoformat(),
                applicable_rounds=list(range(500, 516))
            )
            insights.append(insight)

        for decision_type, patterns in failure_patterns.items():
            if len(patterns) >= 2:
                common_errors = []
                for p in patterns:
                    common_errors.extend(p.get("errors", []))
                error_counts = defaultdict(int)
                for err in common_errors:
                    error_counts[err] += 1

                if error_counts:
                    most_common_error = max(error_counts.items(), key=lambda x: x[1])
                    insight = LearningInsight(
                        insight_id=f"insight_{int(time.time()*1000)}",
                        source=LearningSource.EXECUTION_RESULT,
                        content=f"决策类型 {decision_type} 常见错误: {most_common_error[0]}，建议调整策略",
                        confidence=min(0.9, len(patterns) * 0.15),
                        actionable=True,
                        timestamp=datetime.now().isoformat(),
                        applicable_rounds=[p["source_round"] for p in patterns]
                    )
                    insights.append(insight)

        # 存储洞察
        for insight in insights:
            self.store_learning_insight(insight)

        return insights

    def store_learning_insight(self, insight: LearningInsight) -> bool:
        """存储学习洞察"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO learning_insights
                (insight_id, source, content, confidence, actionable, timestamp, applied, application_result, applicable_rounds)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                insight.insight_id,
                insight.source.value,
                insight.content,
                insight.confidence,
                int(insight.actionable),
                insight.timestamp,
                int(insight.applied),
                insight.application_result,
                json.dumps(insight.applicable_rounds)
            ))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"存储学习洞察失败: {e}")
            return False

    def apply_learning_to_decision(self, context: Dict[str, Any], current_round: int = 515) -> Dict[str, Any]:
        """将学习结果应用到新决策（增强跨轮次版）"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # 获取高置信度、可执行且未应用的学习洞察
        cursor.execute('''
            SELECT insight_id, source, content, confidence, applicable_rounds
            FROM learning_insights
            WHERE actionable = 1 AND applied = 0 AND confidence > 0.5
            ORDER BY confidence DESC
            LIMIT 10
        ''')

        insights = cursor.fetchall()
        conn.close()

        optimization_hints = []
        for insight in insights:
            insight_id, source, content, confidence, applicable_rounds_str = insight
            optimization_hints.append({
                "insight_id": insight_id,
                "content": content,
                "confidence": confidence,
                "applicable_rounds": json.loads(applicable_rounds_str) if applicable_rounds_str else []
            })

        # 应用跨轮次学习
        cross_round_result = self.apply_cross_round_learning(context, current_round)

        return {
            "optimization_applied": len(optimization_hints) > 0 or cross_round_result["cross_round_learning_applied"],
            "optimization_hints": optimization_hints,
            "cross_round_learning": cross_round_result,
            "context_enhanced": {
                **context,
                "optimization_hints": optimization_hints,
                "cross_round_experiences": cross_round_result.get("optimization_hints", []),
                "inheritance_applied": cross_round_result.get("inheritance_applied", False)
            }
        }

    def execute_closed_loop(self, decision: Dict[str, Any], current_round: int = 515, execute_fn=None) -> Dict[str, Any]:
        """执行完整的决策-执行-学习闭环（增强跨轮次版）"""
        loop_id = f"loop_{int(time.time()*1000)}"

        # 步骤1：存储决策
        decision_record = DecisionRecord(
            decision_id=decision.get("decision_id", f"dec_{loop_id}"),
            decision_type=DecisionType(decision.get("decision_type", "strategy")),
            decision_content=decision.get("content", ""),
            context=decision.get("context", {}),
            timestamp=datetime.now().isoformat(),
            source_round=current_round
        )
        self.store_decision(decision_record)

        # 步骤2：执行决策（如果提供了执行函数）
        execution_id = ""
        execution_result = {
            "status": "pending",
            "success_count": 0,
            "failed_count": 0,
            "duration": 0.0,
            "errors": []
        }

        if execute_fn:
            start_time = time.time()
            try:
                exec_output = execute_fn(decision)
                execution_result = {
                    "status": "completed",
                    "success_count": 1,
                    "failed_count": 0,
                    "duration": time.time() - start_time,
                    "errors": [],
                    "output": exec_output
                }
                execution_id = f"exec_{loop_id}"
            except Exception as e:
                execution_result = {
                    "status": "failed",
                    "success_count": 0,
                    "failed_count": 1,
                    "duration": time.time() - start_time,
                    "errors": [str(e)]
                }
                execution_id = f"exec_{loop_id}"

            # 链接决策到执行
            self.link_decision_to_execution(decision_record.decision_id, execution_id)

            # 步骤3：存储执行反馈
            feedback = ExecutionFeedback(
                execution_id=execution_id,
                decision_id=decision_record.decision_id,
                status=ExecutionStatus(execution_result["status"]),
                success_count=execution_result["success_count"],
                failed_count=execution_result["failed_count"],
                duration=execution_result["duration"],
                errors=execution_result.get("errors", []),
                adjustments=execution_result.get("adjustments", []),
                timestamp=datetime.now().isoformat(),
                execution_round=current_round
            )
            self.store_execution_feedback(feedback)

        # 步骤4：提取跨轮次经验
        self.extract_cross_round_experiences(current_round)

        # 步骤5：生成学习洞察
        insights = self.generate_learning_insights()

        # 步骤6：应用学习到决策
        optimization_result = self.apply_learning_to_decision(decision.get("context", {}), current_round)

        # 步骤7：生成跨轮次价值评估
        value_assessment = self.generate_cross_round_value_assessment(current_round)

        # 记录闭环
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        insight_ids = ",".join([i.insight_id for i in insights[:3]])
        effectiveness = 1.0 if execution_result["status"] == "completed" else 0.5

        cursor.execute('''
            INSERT INTO closed_loop_records
            (loop_id, decision_id, execution_id, insight_id, optimization_applied, timestamp, effectiveness_score, loop_round)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            loop_id,
            decision_record.decision_id,
            execution_id,
            insight_ids,
            str(optimization_result["optimization_applied"]),
            datetime.now().isoformat(),
            effectiveness,
            current_round
        ))
        conn.commit()
        conn.close()

        self.closed_loop_history.append({
            "loop_id": loop_id,
            "decision_id": decision_record.decision_id,
            "execution_id": execution_id,
            "insights_count": len(insights),
            "optimization_applied": optimization_result["optimization_applied"],
            "effectiveness": effectiveness,
            "timestamp": datetime.now().isoformat(),
            "loop_round": current_round
        })

        return {
            "loop_id": loop_id,
            "decision_id": decision_record.decision_id,
            "execution_id": execution_id,
            "execution_result": execution_result,
            "insights_generated": len(insights),
            "optimization_applied": optimization_result["optimization_applied"],
            "optimization_hints": optimization_result.get("optimization_hints", []),
            "cross_round_learning": optimization_result.get("cross_round_learning", {}),
            "value_assessment": value_assessment,
            "effectiveness_score": effectiveness,
            "timestamp": datetime.now().isoformat(),
            "version": self.VERSION
        }

    def get_closed_loop_status(self) -> Dict[str, Any]:
        """获取闭环状态"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # 统计
        cursor.execute("SELECT COUNT(*) FROM decisions")
        total_decisions = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM decisions WHERE executed = 1")
        executed_decisions = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM execution_feedback WHERE status = 'completed'")
        successful_executions = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM execution_feedback WHERE status = 'failed'")
        failed_executions = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM learning_insights WHERE applied = 1")
        applied_insights = cursor.fetchone()[0]

        cursor.execute("SELECT AVG(effectiveness_score) FROM closed_loop_records")
        avg_effectiveness = cursor.fetchone()[0] or 0.0

        # 跨轮次统计
        cursor.execute("SELECT COUNT(*) FROM cross_round_experiences WHERE applied = 0")
        pending_experiences = cursor.fetchone()[0]

        conn.close()

        return {
            "total_decisions": total_decisions,
            "executed_decisions": executed_decisions,
            "execution_rate": executed_decisions / total_decisions if total_decisions > 0 else 0,
            "successful_executions": successful_executions,
            "failed_executions": failed_executions,
            "success_rate": successful_executions / (successful_executions + failed_executions) if (successful_executions + failed_executions) > 0 else 0,
            "applied_insights": applied_insights,
            "average_effectiveness": round(avg_effectiveness, 3),
            "pending_cross_round_experiences": pending_experiences,
            "closed_loops_count": len(self.closed_loop_history),
            "database_path": str(self.db_path),
            "version": self.VERSION
        }

    def get_recent_loops(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取最近的闭环记录"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute('''
            SELECT loop_id, decision_id, execution_id, insight_id,
                   optimization_applied, timestamp, effectiveness_score, loop_round
            FROM closed_loop_records
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))

        rows = cursor.fetchall()
        conn.close()

        return [
            {
                "loop_id": row[0],
                "decision_id": row[1],
                "execution_id": row[2],
                "insight_id": row[3],
                "optimization_applied": row[4],
                "timestamp": row[5],
                "effectiveness_score": row[6],
                "loop_round": row[7]
            }
            for row in rows
        ]

    def get_cockpit_data(self) -> Dict[str, Any]:
        """获取驾驶舱数据"""
        status = self.get_closed_loop_status()
        recent = self.get_recent_loops(5)

        # 获取跨轮次价值评估
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute('''
            SELECT decision_type, AVG(value_score) as avg_value, trend
            FROM cross_round_value_assessment
            GROUP BY decision_type
            ORDER BY avg_value DESC
            LIMIT 5
        ''')
        value_trends = cursor.fetchall()
        conn.close()

        return {
            "closed_loop_status": status,
            "recent_loops": recent,
            "value_trends": [
                {"decision_type": row[0], "avg_value": row[1], "trend": row[2]}
                for row in value_trends
            ],
            "version": self.VERSION
        }


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(
        description="跨轮次决策-执行-学习深度集成增强引擎"
    )
    parser.add_argument("--status", action="store_true", help="查看闭环状态")
    parser.add_argument("--recent", type=int, default=5, help="查看最近N条闭环记录")
    parser.add_argument("--execute-loop", type=str, help="执行完整闭环（JSON格式的决策）")
    parser.add_argument("--round", type=int, default=515, help="当前轮次（默认515）")
    parser.add_argument("--generate-insights", action="store_true", help="生成学习洞察")
    parser.add_argument("--apply-learning", type=str, help="将学习应用到决策（JSON格式的上下文）")
    parser.add_argument("--extract-experiences", action="store_true", help="提取跨轮次经验")
    parser.add_argument("--value-assessment", action="store_true", help="生成跨轮次价值评估")
    parser.add_argument("--cockpit-data", action="store_true", help="获取驾驶舱数据")

    args = parser.parse_args()

    engine = CrossRoundDecisionExecutionLearningEngine()

    if args.status:
        status = engine.get_closed_loop_status()
        print(json.dumps(status, indent=2, ensure_ascii=False))
        return

    if args.recent > 0:
        recent = engine.get_recent_loops(args.recent)
        print(json.dumps(recent, indent=2, ensure_ascii=False))
        return

    if args.execute_loop:
        try:
            decision = json.loads(args.execute_loop)
            result = engine.execute_closed_loop(decision, args.round)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        except json.JSONDecodeError as e:
            print(f"JSON解析失败: {e}")
        return

    if args.generate_insights:
        insights = engine.generate_learning_insights()
        print(json.dumps([asdict(i) for i in insights], indent=2, ensure_ascii=False))
        return

    if args.apply_learning:
        try:
            context = json.loads(args.apply_learning)
            result = engine.apply_learning_to_decision(context, args.round)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        except json.JSONDecodeError as e:
            print(f"JSON解析失败: {e}")
        return

    if args.extract_experiences:
        experiences = engine.extract_cross_round_experiences(args.round)
        print(json.dumps([asdict(e) for e in experiences], indent=2, ensure_ascii=False))
        return

    if args.value_assessment:
        assessment = engine.generate_cross_round_value_assessment(args.round)
        print(json.dumps(assessment, indent=2, ensure_ascii=False))
        return

    if args.cockpit_data:
        data = engine.get_cockpit_data()
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return

    # 默认显示状态
    status = engine.get_closed_loop_status()
    print(json.dumps(status, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()