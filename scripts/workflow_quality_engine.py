#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
智能工作流质量保障与自动优化引擎
监控工作流执行质量，自动分析失败原因并生成优化建议/自动修复

功能：
1. 工作流执行质量监控 - 记录和监控工作流执行的质量指标
2. 失败原因自动分析 - 分析工作流失败的原因
3. 自动优化建议 - 生成优化建议或自动修复方案
4. 质量趋势分析 - 分析质量趋势和模式
5. 与进化历史数据库集成 - 记录质量数据供策略引擎使用

使用方法：
    python workflow_quality_engine.py analyze <workflow_name>
    python workflow_quality_engine.py monitor <workflow_name>
    python workflow_quality_engine.py optimize <workflow_name>
    python workflow_quality_engine.py quality-stats
"""
import os
import sys
import json
import sqlite3
import subprocess
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict
from dataclasses import dataclass, field, asdict
import re

# 数据库路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(SCRIPT_DIR, '..', 'runtime', 'state', 'workflow_quality.db')
EVOLUTION_DB_PATH = os.path.join(SCRIPT_DIR, '..', 'runtime', 'state', 'evolution_history.db')


@dataclass
class WorkflowQualityRecord:
    """工作流质量记录"""
    id: int = None
    workflow_name: str = ""
    workflow_path: str = ""
    execution_time: str = ""
    duration: float = 0.0
    success: bool = False
    error_type: str = ""
    error_message: str = ""
    steps_total: int = 0
    steps_success: int = 0
    steps_failed: int = 0
    quality_score: float = 0.0  # 0-100
    retry_count: int = 0
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class QualityAnalysis:
    """质量分析结果"""
    workflow_name: str
    total_executions: int = 0
    success_rate: float = 0.0
    avg_duration: float = 0.0
    avg_quality_score: float = 0.0
    common_errors: List[Dict[str, Any]] = field(default_factory=list)
    failure_patterns: List[str] = field(default_factory=list)
    optimization_suggestions: List[str] = field(default_factory=list)
    quality_trend: str = "stable"  # improving/declining/stable


@dataclass
class OptimizationRecommendation:
    """优化建议"""
    workflow_name: str
    recommendation_type: str  # fix/retry/optimize/verify
    description: str
    confidence: float = 0.0
    estimated_improvement: float = 0.0
    action_steps: List[str] = field(default_factory=list)


class WorkflowQualityEngine:
    """工作流质量保障与自动优化引擎"""

    def __init__(self, db_path: str = None):
        self.db_path = db_path or DB_PATH
        self._init_database()

    def _init_database(self):
        """初始化数据库"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 工作流质量记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS workflow_quality (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workflow_name TEXT NOT NULL,
                workflow_path TEXT,
                execution_time TEXT NOT NULL,
                duration REAL DEFAULT 0.0,
                success INTEGER DEFAULT 0,
                error_type TEXT,
                error_message TEXT,
                steps_total INTEGER DEFAULT 0,
                steps_success INTEGER DEFAULT 0,
                steps_failed INTEGER DEFAULT 0,
                quality_score REAL DEFAULT 0.0,
                retry_count INTEGER DEFAULT 0,
                context TEXT
            )
        ''')

        # 质量分析缓存表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quality_analysis_cache (
                workflow_name TEXT PRIMARY KEY,
                analysis_json TEXT,
                updated_time TEXT
            )
        ''')

        conn.commit()
        conn.close()

    def record_execution(self, record: WorkflowQualityRecord) -> int:
        """记录工作流执行结果"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO workflow_quality (
                workflow_name, workflow_path, execution_time, duration, success,
                error_type, error_message, steps_total, steps_success, steps_failed,
                quality_score, retry_count, context
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            record.workflow_name,
            record.workflow_path,
            record.execution_time,
            record.duration,
            1 if record.success else 0,
            record.error_type,
            record.error_message,
            record.steps_total,
            record.steps_success,
            record.steps_failed,
            record.quality_score,
            record.retry_count,
            json.dumps(record.context, ensure_ascii=False)
        ))

        record_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return record_id

    def analyze_workflow(self, workflow_name: str, days: int = 30) -> QualityAnalysis:
        """分析工作流质量"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 获取历史记录
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        cursor.execute('''
            SELECT * FROM workflow_quality
            WHERE workflow_name = ? AND execution_time > ?
            ORDER BY execution_time DESC
        ''', (workflow_name, cutoff_date))

        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return QualityAnalysis(
                workflow_name=workflow_name,
                total_executions=0,
                optimization_suggestions=["暂无执行历史，无法分析"]
            )

        # 分析数据
        total = len(rows)
        success_count = sum(1 for r in rows if r[5])
        durations = [r[4] for r in rows if r[4] > 0]
        quality_scores = [r[12] for r in rows if r[12] > 0]

        # 统计错误类型
        error_counts = defaultdict(int)
        for r in rows:
            if not r[5] and r[6]:  # 失败且有错误类型
                error_counts[r[6]] += 1

        common_errors = [
            {"error_type": et, "count": c, "percentage": c/total*100}
            for et, c in sorted(error_counts.items(), key=lambda x: -x[1])[:5]
        ]

        # 质量趋势分析
        quality_trend = self._analyze_quality_trend(rows)

        # 生成优化建议
        suggestions = self._generate_suggestions(
            success_count/total if total > 0 else 0,
            sum(durations)/len(durations) if durations else 0,
            sum(quality_scores)/len(quality_scores) if quality_scores else 0,
            common_errors
        )

        return QualityAnalysis(
            workflow_name=workflow_name,
            total_executions=total,
            success_rate=success_count/total if total > 0 else 0,
            avg_duration=sum(durations)/len(durations) if durations else 0,
            avg_quality_score=sum(quality_scores)/len(quality_scores) if quality_scores else 0,
            common_errors=common_errors,
            quality_trend=quality_trend,
            optimization_suggestions=suggestions
        )

    def _analyze_quality_trend(self, rows: List[Tuple]) -> str:
        """分析质量趋势"""
        if len(rows) < 3:
            return "stable"

        # 取最近一半和最早期一半对比
        half = len(rows) // 2
        recent = rows[:half]
        older = rows[half:]

        recent_success = sum(1 for r in recent if r[5]) / len(recent) if recent else 0
        older_success = sum(1 for r in older if r[5]) / len(older) if older else 0

        diff = recent_success - older_success
        if diff > 0.15:
            return "improving"
        elif diff < -0.15:
            return "declining"
        return "stable"

    def _generate_suggestions(self, success_rate: float, avg_duration: float,
                             avg_quality: float, errors: List[Dict]) -> List[str]:
        """生成优化建议"""
        suggestions = []

        # 基于成功率
        if success_rate < 0.5:
            suggestions.append("成功率过低(<50%)，建议检查工作流步骤的可行性")
        elif success_rate < 0.7:
            suggestions.append("成功率偏低(50-70%)，建议添加错误处理和重试机制")

        # 基于错误类型
        error_types = [e["error_type"] for e in errors]
        if "vision_timeout" in error_types:
            suggestions.append("检测到视觉识别超时，建议增加等待时间或优化截图区域")
        if "window_not_found" in error_types:
            suggestions.append("检测到窗口未找到错误，建议添加窗口激活和等待步骤")
        if "click_failed" in error_types:
            suggestions.append("检测到点击失败，建议检查坐标准确性或添加重试")

        # 基于质量分数
        if avg_quality < 60:
            suggestions.append("质量分数较低，建议优化工作流步骤和错误处理")

        if not suggestions:
            suggestions.append("工作流运行良好，建议继续保持当前配置")

        return suggestions

    def get_optimization_recommendations(self, workflow_name: str) -> List[OptimizationRecommendation]:
        """获取优化建议"""
        analysis = self.analyze_workflow(workflow_name)
        recommendations = []

        # 基于分析结果生成建议
        if analysis.success_rate < 0.7:
            rec = OptimizationRecommendation(
                workflow_name=workflow_name,
                recommendation_type="fix",
                description=f"成功率仅 {analysis.success_rate*100:.1f}%，需要修复",
                confidence=0.8,
                estimated_improvement=0.2,
                action_steps=["检查失败步骤的具体原因", "添加错误处理", "增加重试机制"]
            )
            recommendations.append(rec)

        # 基于错误类型
        for error in analysis.common_errors[:3]:
            if error["count"] >= 2:
                rec = OptimizationRecommendation(
                    workflow_name=workflow_name,
                    recommendation_type="optimize",
                    description=f"频繁错误: {error['error_type']} ({error['count']}次)",
                    confidence=0.7,
                    estimated_improvement=0.15,
                    action_steps=[f"针对 {error['error_type']} 添加专门的错误处理"]
                )
                recommendations.append(rec)

        return recommendations

    def get_quality_stats(self, days: int = 30) -> Dict[str, Any]:
        """获取整体质量统计"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        cursor.execute('''
            SELECT workflow_name, COUNT(*) as total,
                   SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as success_count,
                   AVG(quality_score) as avg_quality,
                   AVG(duration) as avg_duration
            FROM workflow_quality
            WHERE execution_time > ?
            GROUP BY workflow_name
            ORDER BY total DESC
        ''', (cutoff_date,))

        rows = cursor.fetchall()
        conn.close()

        stats = {
            "period_days": days,
            "total_workflows": len(rows),
            "workflows": []
        }

        for r in rows:
            wf_stats = {
                "name": r[0],
                "total_executions": r[1],
                "success_count": r[2],
                "success_rate": r[2]/r[1] if r[1] > 0 else 0,
                "avg_quality_score": r[3] or 0,
                "avg_duration": r[4] or 0
            }
            stats["workflows"].append(wf_stats)

        return stats

    def record_from_run_plan_result(self, workflow_name: str, workflow_path: str,
                                    result: Dict[str, Any]):
        """从 run_plan 执行结果记录质量数据"""
        record = WorkflowQualityRecord(
            workflow_name=workflow_name,
            workflow_path=workflow_path,
            execution_time=datetime.now().isoformat(),
            duration=result.get("duration", 0),
            success=result.get("success", False),
            error_type=result.get("error_type", ""),
            error_message=result.get("error_message", ""),
            steps_total=result.get("steps_total", 0),
            steps_success=result.get("steps_success", 0),
            steps_failed=result.get("steps_failed", 0),
            quality_score=self._calculate_quality_score(result),
            retry_count=result.get("retry_count", 0),
            context=result.get("context", {})
        )
        self.record_execution(record)

    def _calculate_quality_score(self, result: Dict[str, Any]) -> float:
        """计算质量分数"""
        if not result.get("success", False):
            # 失败情况：基础分30 + 步骤成功比例 * 30
            steps_total = result.get("steps_total", 1)
            steps_success = result.get("steps_success", 0)
            base = 30
            step_score = (steps_success / steps_total * 30) if steps_total > 0 else 0
            return base + step_score
        else:
            # 成功情况：基础分70 + 基于执行时间的奖励/惩罚
            base = 70
            duration = result.get("duration", 0)
            # 执行时间越短越好
            if duration < 30:
                duration_bonus = 30
            elif duration < 60:
                duration_bonus = 20
            elif duration < 120:
                duration_bonus = 10
            else:
                duration_bonus = 0
            return min(100, base + duration_bonus)


def analyze_workflow(workflow_name: str) -> Dict[str, Any]:
    """分析指定工作流的质量"""
    engine = WorkflowQualityEngine()
    analysis = engine.analyze_workflow(workflow_name)
    return {
        "workflow_name": analysis.workflow_name,
        "total_executions": analysis.total_executions,
        "success_rate": f"{analysis.success_rate*100:.1f}%",
        "avg_duration": f"{analysis.avg_duration:.1f}秒",
        "avg_quality_score": f"{analysis.avg_quality_score:.1f}",
        "quality_trend": analysis.quality_trend,
        "common_errors": analysis.common_errors,
        "optimization_suggestions": analysis.optimization_suggestions
    }


def get_quality_stats(days: int = 30) -> Dict[str, Any]:
    """获取整体质量统计"""
    engine = WorkflowQualityEngine()
    return engine.get_quality_stats(days)


def get_optimization_recommendations(workflow_name: str) -> List[Dict[str, Any]]:
    """获取优化建议"""
    engine = WorkflowQualityEngine()
    recs = engine.get_optimization_recommendations(workflow_name)
    return [
        {
            "type": r.recommendation_type,
            "description": r.description,
            "confidence": f"{r.confidence*100:.0f}%",
            "estimated_improvement": f"+{r.estimated_improvement*100:.0f}%",
            "action_steps": r.action_steps
        }
        for r in recs
    ]


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="智能工作流质量保障与自动优化引擎")
    parser.add_argument("command", choices=["analyze", "stats", "optimize"],
                       help="命令: analyze-分析, stats-统计, optimize-优化建议")
    parser.add_argument("workflow_name", nargs="?", help="工作流名称")
    parser.add_argument("--days", type=int, default=30, help="分析天数")

    args = parser.parse_args()

    if args.command == "analyze":
        if not args.workflow_name:
            print("错误: 需要指定工作流名称")
            sys.exit(1)
        result = analyze_workflow(args.workflow_name)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "stats":
        result = get_quality_stats(args.days)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "optimize":
        if not args.workflow_name:
            print("错误: 需要指定工作流名称")
            sys.exit(1)
        result = get_optimization_recommendations(args.workflow_name)
        print(json.dumps(result, ensure_ascii=False, indent=2))