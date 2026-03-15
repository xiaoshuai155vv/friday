#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环决策-执行-学习完整闭环深度集成引擎
(Decision-Execution-Learning Closed-Loop Deep Integration Engine)

让系统能够从决策到执行到学习的完整数据流转、实现决策效果的实时反馈、
让学习结果直接驱动下一轮决策，形成「决策→执行→学习→优化决策」的持续改进闭环。
系统将消除决策与执行之间的割裂，让进化环的智能决策能力在实际执行中不断验证和提升。

这是 round 511 完成的「决策执行结果学习与深度优化引擎」和
round 510 完成的「决策自动执行引擎」的深度集成与增强。

Version: 1.0.0

功能特性：
1. 决策到执行的完整数据流（决策输出→执行输入）
2. 执行结果的实时反馈（执行效果→学习输入）
3. 学习驱动的决策优化（学习结果→决策改进）
4. 闭环效果评估与报告
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


class DecisionExecutionLearningIntegrationEngine:
    """决策-执行-学习完整闭环深度集成引擎"""

    def __init__(self):
        self.db_path = DATA_DIR / "decision_execution_learning_integration.db"
        self._init_database()
        self.closed_loop_history = []

    def _init_database(self):
        """初始化数据库"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # 决策记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS decisions (
                decision_id TEXT PRIMARY KEY,
                decision_type TEXT,
                decision_content TEXT,
                context TEXT,
                timestamp TEXT,
                executed INTEGER DEFAULT 0,
                execution_id TEXT
            )
        ''')

        # 执行反馈表
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
                timestamp TEXT
            )
        ''')

        # 学习洞察表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learning_insights (
                insight_id TEXT PRIMARY KEY,
                source TEXT,
                content TEXT,
                confidence REAL,
                actionable INTEGER,
                timestamp TEXT,
                applied INTEGER DEFAULT 0,
                application_result TEXT
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
                effectiveness_score REAL
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
                (decision_id, decision_type, decision_content, context, timestamp, executed, execution_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                decision.decision_id,
                decision.decision_type.value,
                decision.decision_content,
                json.dumps(decision.context),
                decision.timestamp,
                int(decision.executed),
                decision.execution_id
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
                (execution_id, decision_id, status, success_count, failed_count, duration, errors, adjustments, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                feedback.execution_id,
                feedback.decision_id,
                feedback.status.value,
                feedback.success_count,
                feedback.failed_count,
                feedback.duration,
                json.dumps(feedback.errors),
                json.dumps(feedback.adjustments),
                feedback.timestamp
            ))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"存储执行反馈失败: {e}")
            return False

    def generate_learning_insights(self) -> List[LearningInsight]:
        """基于决策-执行-执行反馈生成学习洞察"""
        insights = []
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # 查询已执行的决策及其执行反馈
        cursor.execute('''
            SELECT d.decision_id, d.decision_type, d.decision_content, d.context,
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
            decision_id, decision_type, decision_content, context_str, \
                execution_id, status, success_count, failed_count, duration, errors = row

            context = json.loads(context_str) if context_str else {}
            error_list = json.loads(errors) if errors else []

            if status == "completed" and failed_count == 0:
                success_patterns[decision_type].append({
                    "decision_id": decision_id,
                    "content": decision_content,
                    "context": context,
                    "duration": duration
                })
            elif status == "failed" or failed_count > 0:
                failure_patterns[decision_type].append({
                    "decision_id": decision_id,
                    "content": decision_content,
                    "context": context,
                    "errors": error_list
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
                    timestamp=datetime.now().isoformat()
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
                        timestamp=datetime.now().isoformat()
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
                (insight_id, source, content, confidence, actionable, timestamp, applied, application_result)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                insight.insight_id,
                insight.source.value,
                insight.content,
                insight.confidence,
                int(insight.actionable),
                insight.timestamp,
                int(insight.applied),
                insight.application_result
            ))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"存储学习洞察失败: {e}")
            return False

    def apply_learning_to_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """将学习结果应用到新决策"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # 获取高置信度、可执行且未应用的学习洞察
        cursor.execute('''
            SELECT insight_id, source, content, confidence
            FROM learning_insights
            WHERE actionable = 1 AND applied = 0 AND confidence > 0.5
            ORDER BY confidence DESC
            LIMIT 10
        ''')

        insights = cursor.fetchall()
        conn.close()

        optimization_hints = []
        for insight in insights:
            insight_id, source, content, confidence = insight
            optimization_hints.append({
                "insight_id": insight_id,
                "content": content,
                "confidence": confidence
            })

        return {
            "optimization_applied": len(optimization_hints) > 0,
            "optimization_hints": optimization_hints,
            "context_enhanced": {**context, "optimization_hints": optimization_hints}
        }

    def execute_closed_loop(self, decision: Dict[str, Any], execute_fn=None) -> Dict[str, Any]:
        """执行完整的决策-执行-学习闭环"""
        loop_id = f"loop_{int(time.time()*1000)}"

        # 步骤1：存储决策
        decision_record = DecisionRecord(
            decision_id=decision.get("decision_id", f"dec_{loop_id}"),
            decision_type=DecisionType(decision.get("decision_type", "strategy")),
            decision_content=decision.get("content", ""),
            context=decision.get("context", {}),
            timestamp=datetime.now().isoformat()
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
                timestamp=datetime.now().isoformat()
            )
            self.store_execution_feedback(feedback)

        # 步骤4：生成学习洞察
        insights = self.generate_learning_insights()

        # 步骤5：应用学习到决策
        optimization_result = self.apply_learning_to_decision(decision.get("context", {}))

        # 记录闭环
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        insight_ids = ",".join([i.insight_id for i in insights[:3]])
        effectiveness = 1.0 if execution_result["status"] == "completed" else 0.5

        cursor.execute('''
            INSERT INTO closed_loop_records
            (loop_id, decision_id, execution_id, insight_id, optimization_applied, timestamp, effectiveness_score)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            loop_id,
            decision_record.decision_id,
            execution_id,
            insight_ids,
            str(optimization_result["optimization_applied"]),
            datetime.now().isoformat(),
            effectiveness
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
            "timestamp": datetime.now().isoformat()
        })

        return {
            "loop_id": loop_id,
            "decision_id": decision_record.decision_id,
            "execution_id": execution_id,
            "execution_result": execution_result,
            "insights_generated": len(insights),
            "optimization_applied": optimization_result["optimization_applied"],
            "optimization_hints": optimization_result.get("optimization_hints", []),
            "effectiveness_score": effectiveness,
            "timestamp": datetime.now().isoformat()
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
            "closed_loops_count": len(self.closed_loop_history),
            "database_path": str(self.db_path)
        }

    def get_recent_loops(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取最近的闭环记录"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute('''
            SELECT loop_id, decision_id, execution_id, insight_id,
                   optimization_applied, timestamp, effectiveness_score
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
                "effectiveness_score": row[6]
            }
            for row in rows
        ]

    def get_cockpit_data(self) -> Dict[str, Any]:
        """获取驾驶舱数据"""
        status = self.get_closed_loop_status()
        recent = self.get_recent_loops(5)

        return {
            "closed_loop_status": status,
            "recent_loops": recent,
            "version": "1.0.0"
        }


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(
        description="决策-执行-学习完整闭环深度集成引擎"
    )
    parser.add_argument("--status", action="store_true", help="查看闭环状态")
    parser.add_argument("--recent", type=int, default=5, help="查看最近N条闭环记录")
    parser.add_argument("--execute-loop", type=str, help="执行完整闭环（JSON格式的决策）")
    parser.add_argument("--generate-insights", action="store_true", help="生成学习洞察")
    parser.add_argument("--apply-learning", type=str, help="将学习应用到决策（JSON格式的上下文）")
    parser.add_argument("--cockpit-data", action="store_true", help="获取驾驶舱数据")

    args = parser.parse_args()

    engine = DecisionExecutionLearningIntegrationEngine()

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
            result = engine.execute_closed_loop(decision)
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
            result = engine.apply_learning_to_decision(context)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        except json.JSONDecodeError as e:
            print(f"JSON解析失败: {e}")
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