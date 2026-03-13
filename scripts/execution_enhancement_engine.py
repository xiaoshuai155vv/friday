#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
智能执行增强与自适应优化引擎
在对话执行引擎基础上，增强执行效果追踪、智能策略分析和自适应执行优化，让系统能够从每次执行中学习并优化执行方式

功能：
1. 执行效果追踪 - 记录和追踪执行步骤、耗时、成功率等指标
2. 智能策略分析 - 分析哪些执行策略更有效
3. 自适应执行优化 - 根据上下文自动选择最优执行策略
4. 执行建议生成 - 基于历史数据生成执行优化建议
5. 与对话执行引擎集成 - 提供增强的执行能力

使用方法：
    python execution_enhancement_engine.py track <execution_data>
    python execution_enhancement_engine.py analyze <intent>
    python execution_enhancement_engine.py optimize <context>
    python execution_enhancement_engine.py recommend
    python execution_enhancement_engine.py stats
"""
import os
import sys
import json
import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict
from dataclasses import dataclass, field, asdict

# 路径配置
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(SCRIPT_DIR, '..', 'runtime', 'state', 'execution_enhancement.db')
RUNTIME_DIR = os.path.join(SCRIPT_DIR, '..', 'runtime')


@dataclass
class ExecutionRecord:
    """执行记录"""
    id: int = None
    intent: str = ""
    execution_type: str = ""  # direct/sequential/parallel/fallback
    steps: List[Dict[str, Any]] = field(default_factory=list)
    duration: float = 0.0
    success: bool = False
    error_message: str = ""
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = ""


@dataclass
class StrategyAnalysis:
    """策略分析结果"""
    strategy_name: str
    total_executions: int = 0
    success_rate: float = 0.0
    avg_duration: float = 0.0
    avg_steps: float = 0.0
    trend: str = "stable"  # improving/declining/stable
    score: float = 0.0  # 综合评分 0-100


@dataclass
class OptimizationResult:
    """优化结果"""
    recommended_strategy: str
    confidence: float
    reasoning: str
    alternative_strategies: List[Dict[str, Any]] = field(default_factory=list)
    expected_improvement: float = 0.0


class ExecutionEnhancementEngine:
    """智能执行增强与自适应优化引擎"""

    def __init__(self, db_path: str = None):
        self.db_path = db_path or DB_PATH
        self._init_database()
        self._load_strategy_templates()

    def _init_database(self):
        """初始化数据库"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 执行记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS execution_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                intent TEXT NOT NULL,
                execution_type TEXT,
                steps_json TEXT,
                duration REAL DEFAULT 0.0,
                success INTEGER DEFAULT 0,
                error_message TEXT,
                context_json TEXT,
                timestamp TEXT NOT NULL
            )
        ''')

        # 策略效果表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS strategy_effectiveness (
                strategy_name TEXT PRIMARY KEY,
                total_executions INTEGER DEFAULT 0,
                success_count INTEGER DEFAULT 0,
                total_duration REAL DEFAULT 0.0,
                total_steps INTEGER DEFAULT 0,
                last_updated TEXT
            )
        ''')

        # 上下文模式表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS context_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                context_key TEXT NOT NULL,
                context_value TEXT NOT NULL,
                best_strategy TEXT,
                success_count INTEGER DEFAULT 0,
                total_count INTEGER DEFAULT 0,
                last_updated TEXT
            )
        ''')

        conn.commit()
        conn.close()

    def _load_strategy_templates(self):
        """加载策略模板"""
        self.strategy_templates = {
            "direct": {
                "name": "直接执行",
                "description": "一步到位，直接执行用户请求",
                "best_for": ["简单任务", "明确指令"],
                "steps": 1
            },
            "sequential": {
                "name": "顺序执行",
                "description": "按步骤顺序执行，每步确认后再执行下一步",
                "best_for": ["复杂任务", "多步骤操作"],
                "steps": "multiple"
            },
            "parallel": {
                "name": "并行执行",
                "description": "同时执行多个独立任务",
                "best_for": ["批量操作", "独立任务"],
                "steps": "multiple"
            },
            "fallback": {
                "name": "降级执行",
                "description": "主策略失败时使用备用方案",
                "best_for": ["容错场景", "关键任务"],
                "steps": "multiple"
            },
            "exploratory": {
                "name": "探索执行",
                "description": "先尝试性执行，根据结果调整",
                "best_for": ["不确定任务", "新场景"],
                "steps": "adaptive"
            },
            "conservative": {
                "name": "保守执行",
                "description": "步步确认，频繁反馈",
                "best_for": ["高风险操作", "新用户"],
                "steps": "multiple"
            }
        }

    def record_execution(self, intent: str, execution_type: str, steps: List[Dict],
                        duration: float, success: bool, error_message: str = "",
                        context: Optional[Dict] = None) -> int:
        """记录执行结果"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        timestamp = datetime.now().isoformat()

        cursor.execute('''
            INSERT INTO execution_records (
                intent, execution_type, steps_json, duration, success,
                error_message, context_json, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            intent,
            execution_type,
            json.dumps(steps, ensure_ascii=False),
            duration,
            1 if success else 0,
            error_message,
            json.dumps(context or {}, ensure_ascii=False),
            timestamp
        ))

        record_id = cursor.lastrowid

        # 更新策略效果
        self._update_strategy_effectiveness(cursor, execution_type, success, duration, len(steps))

        # 更新上下文模式
        if context:
            self._update_context_patterns(cursor, context, execution_type, success)

        conn.commit()
        conn.close()
        return record_id

    def _update_strategy_effectiveness(self, cursor, strategy: str, success: bool,
                                       duration: float, steps: int):
        """更新策略效果"""
        cursor.execute('''
            SELECT * FROM strategy_effectiveness WHERE strategy_name = ?
        ''', (strategy,))

        row = cursor.fetchone()
        if row:
            cursor.execute('''
                UPDATE strategy_effectiveness SET
                    total_executions = total_executions + 1,
                    success_count = success_count + ?,
                    total_duration = total_duration + ?,
                    total_steps = total_steps + ?,
                    last_updated = ?
                WHERE strategy_name = ?
            ''', (1 if success else 0, duration, steps, datetime.now().isoformat(), strategy))
        else:
            cursor.execute('''
                INSERT INTO strategy_effectiveness (
                    strategy_name, total_executions, success_count,
                    total_duration, total_steps, last_updated
                ) VALUES (?, 1, ?, ?, ?, ?)
            ''', (strategy, 1 if success else 0, duration, steps, datetime.now().isoformat()))

    def _update_context_patterns(self, cursor, context: Dict, strategy: str, success: bool):
        """更新上下文模式"""
        # 提取关键上下文特征
        key_features = []
        if "time_of_day" in context:
            key_features.append(("time_of_day", context["time_of_day"]))
        if "user_type" in context:
            key_features.append(("user_type", context["user_type"]))
        if "task_complexity" in context:
            key_features.append(("task_complexity", context["task_complexity"]))
        if "system_load" in context:
            key_features.append(("system_load", context["system_load"]))

        for key, value in key_features:
            cursor.execute('''
                SELECT * FROM context_patterns
                WHERE context_key = ? AND context_value = ?
            ''', (key, value))

            row = cursor.fetchone()
            if row:
                new_success = row[4] + (1 if success else 0)
                new_total = row[5] + 1
                # 如果这个组合当前用的策略效果好，更新最佳策略
                best_strategy = row[3]
                if success and (row[3] != strategy):
                    best_strategy = strategy

                cursor.execute('''
                    UPDATE context_patterns SET
                        best_strategy = ?,
                        success_count = ?,
                        total_count = ?,
                        last_updated = ?
                    WHERE context_key = ? AND context_value = ?
                ''', (best_strategy, new_success, new_total, datetime.now().isoformat(), key, value))
            else:
                cursor.execute('''
                    INSERT INTO context_patterns (
                        context_key, context_value, best_strategy,
                        success_count, total_count, last_updated
                    ) VALUES (?, ?, ?, 1, 1, ?)
                ''', (key, value, strategy if success else "", datetime.now().isoformat()))

    def analyze_strategy(self, strategy_name: str, days: int = 30) -> StrategyAnalysis:
        """分析指定策略的效果"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cutoff = (datetime.now() - timedelta(days=days)).isoformat()

        cursor.execute('''
            SELECT * FROM execution_records
            WHERE execution_type = ? AND timestamp > ?
            ORDER BY timestamp DESC
        ''', (strategy_name, cutoff))

        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return StrategyAnalysis(
                strategy_name=strategy_name,
                total_executions=0,
                score=0
            )

        total = len(rows)
        success_count = sum(1 for r in rows if r[5])
        durations = [r[4] for r in rows if r[4] > 0]
        step_counts = [len(json.loads(r[3])) for r in rows if r[3]]

        # 计算趋势
        trend = self._calculate_trend(rows)

        # 计算综合评分
        success_rate = success_count / total if total > 0 else 0
        avg_duration = sum(durations) / len(durations) if durations else 0
        avg_steps = sum(step_counts) / len(step_counts) if step_counts else 0

        # 评分算法：成功率 * 60 + (速度得分) * 20 + (步骤效率) * 20
        speed_score = max(0, 100 - avg_duration) / 100 if avg_duration <= 100 else 0
        step_score = max(0, 1 - (avg_steps - 1) / 10)  # 假设1步为基准，10步以上为0

        score = success_rate * 60 + speed_score * 20 + step_score * 20

        return StrategyAnalysis(
            strategy_name=strategy_name,
            total_executions=total,
            success_rate=success_rate,
            avg_duration=avg_duration,
            avg_steps=avg_steps,
            trend=trend,
            score=score
        )

    def _calculate_trend(self, rows: List[Tuple]) -> str:
        """计算策略趋势"""
        if len(rows) < 3:
            return "stable"

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

    def get_optimization(self, intent: str, context: Optional[Dict] = None) -> OptimizationResult:
        """获取执行优化建议"""
        context = context or {}

        # 分析各策略效果
        strategy_scores = []
        for strategy_name in self.strategy_templates.keys():
            analysis = self.analyze_strategy(strategy_name)
            if analysis.total_executions > 0:
                strategy_scores.append({
                    "name": strategy_name,
                    "score": analysis.score,
                    "success_rate": analysis.success_rate,
                    "trend": analysis.trend,
                    "executions": analysis.total_executions
                })

        # 根据上下文调整评分
        context_bonus = self._get_context_bonus(context)

        # 选择最佳策略
        if strategy_scores:
            best = max(strategy_scores, key=lambda x: x["score"] + context_bonus.get(x["name"], 0))
            reasoning = self._generate_reasoning(best, context)

            # 生成备选策略
            alternatives = [
                {"strategy": s["name"], "score": s["score"]}
                for s in sorted(strategy_scores, key=lambda x: -x["score"])[1:4]
            ]

            return OptimizationResult(
                recommended_strategy=best["name"],
                confidence=min(0.95, 0.5 + best["score"] / 200),  # 置信度基于评分
                reasoning=reasoning,
                alternative_strategies=alternatives,
                expected_improvement=best["score"] / 100
            )
        else:
            # 无历史数据，使用默认策略
            return OptimizationResult(
                recommended_strategy="sequential",
                confidence=0.5,
                reasoning="基于任务复杂度选择顺序执行策略",
                alternative_strategies=[
                    {"strategy": "direct", "score": 0},
                    {"strategy": "exploratory", "score": 0}
                ],
                expected_improvement=0.0
            )

    def _get_context_bonus(self, context: Dict) -> Dict[str, float]:
        """根据上下文获取策略加分"""
        bonus = {}

        if not context:
            return bonus

        # 时间段加分
        time_of_day = context.get("time_of_day", "")
        if "morning" in time_of_day or "afternoon" in time_of_day:
            bonus["direct"] = bonus.get("direct", 0) + 5  # 工作时间倾向快速执行

        # 用户类型加分
        user_type = context.get("user_type", "")
        if user_type == "new":
            bonus["conservative"] = bonus.get("conservative", 0) + 10  # 新用户倾向保守
        elif user_type == "experienced":
            bonus["direct"] = bonus.get("direct", 0) + 10  # 熟练用户倾向快速

        # 任务复杂度
        complexity = context.get("task_complexity", "medium")
        if complexity == "high":
            bonus["sequential"] = bonus.get("sequential", 0) + 10
            bonus["fallback"] = bonus.get("fallback", 0) + 5
        elif complexity == "low":
            bonus["direct"] = bonus.get("direct", 0) + 10

        # 系统负载
        system_load = context.get("system_load", "normal")
        if system_load == "high":
            bonus["direct"] = bonus.get("direct", 0) + 15  # 高负载时选择简单策略
            bonus["parallel"] = bonus.get("parallel", 0) - 10

        return bonus

    def _generate_reasoning(self, best_strategy: Dict, context: Dict) -> str:
        """生成策略选择理由"""
        template = self.strategy_templates.get(best_strategy["name"], {})

        reasons = []

        # 基于策略特性
        if "name" in template:
            reasons.append(f"使用{template['name']}策略")

        # 基于成功率
        if best_strategy["success_rate"] > 0.8:
            reasons.append(f"历史成功率高({best_strategy['success_rate']*100:.0f}%)")

        # 基于趋势
        if best_strategy["trend"] == "improving":
            reasons.append("近期表现提升")

        # 基于上下文
        if context.get("task_complexity") == "high":
            reasons.append("任务复杂需要多步确认")
        elif context.get("task_complexity") == "low":
            reasons.append("任务简单适合直接执行")

        return "，".join(reasons) if reasons else "综合评估最优选择"

    def get_recommendations(self, intent: str = "") -> List[Dict[str, Any]]:
        """获取执行优化建议列表"""
        recommendations = []

        # 分析所有策略
        for strategy_name in self.strategy_templates.keys():
            analysis = self.analyze_strategy(strategy_name)
            if analysis.total_executions > 0:
                rec = {
                    "strategy": strategy_name,
                    "strategy_name": self.strategy_templates[strategy_name]["name"],
                    "description": self.strategy_templates[strategy_name]["description"],
                    "best_for": self.strategy_templates[strategy_name]["best_for"],
                    "success_rate": f"{analysis.success_rate*100:.1f}%",
                    "avg_duration": f"{analysis.avg_duration:.1f}秒",
                    "score": f"{analysis.score:.1f}",
                    "trend": analysis.trend,
                    "executions": analysis.total_executions
                }
                recommendations.append(rec)

        # 按评分排序
        recommendations.sort(key=lambda x: float(x["score"]), reverse=True)

        return recommendations

    def get_stats(self, days: int = 30) -> Dict[str, Any]:
        """获取执行统计"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cutoff = (datetime.now() - timedelta(days=days)).isoformat()

        # 总执行次数
        cursor.execute('''
            SELECT COUNT(*), SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END),
                   AVG(duration)
            FROM execution_records WHERE timestamp > ?
        ''', (cutoff,))

        row = cursor.fetchone()
        total = row[0] or 0
        success = row[1] or 0
        avg_duration = row[2] or 0

        # 按策略统计
        cursor.execute('''
            SELECT execution_type, COUNT(*), SUM(success)
            FROM execution_records
            WHERE timestamp > ?
            GROUP BY execution_type
        ''', (cutoff,))

        strategy_stats = []
        for r in cursor.fetchall():
            strategy_stats.append({
                "strategy": r[0],
                "total": r[1],
                "success": r[2] or 0,
                "rate": f"{(r[2] or 0) / r[1] * 100:.1f}%" if r[1] > 0 else "0%"
            })

        conn.close()

        return {
            "period_days": days,
            "total_executions": total,
            "success_count": success,
            "success_rate": f"{success/total*100:.1f}%" if total > 0 else "0%",
            "avg_duration": f"{avg_duration:.1f}秒",
            "by_strategy": strategy_stats
        }


def track_execution(intent: str, execution_type: str, steps: List[Dict],
                   duration: float, success: bool, error_message: str = "",
                   context: Optional[Dict] = None) -> Dict[str, Any]:
    """记录执行结果（供外部调用）"""
    engine = ExecutionEnhancementEngine()
    record_id = engine.record_execution(intent, execution_type, steps, duration, success, error_message, context)
    return {"record_id": record_id, "status": "recorded"}


def analyze_intent(intent: str) -> Dict[str, Any]:
    """分析意图并返回策略建议"""
    engine = ExecutionEnhancementEngine()
    optimization = engine.get_optimization(intent)
    return {
        "intent": intent,
        "recommended_strategy": optimization.recommended_strategy,
        "confidence": f"{optimization.confidence*100:.0f}%",
        "reasoning": optimization.reasoning,
        "expected_improvement": f"+{optimization.expected_improvement*100:.0f}%",
        "alternatives": optimization.alternative_strategies
    }


def get_optimization(context: Dict) -> Dict[str, Any]:
    """根据上下文获取优化建议"""
    engine = ExecutionEnhancementEngine()
    optimization = engine.get_optimization("", context)
    return {
        "recommended_strategy": optimization.recommended_strategy,
        "confidence": f"{optimization.confidence*100:.0f}%",
        "reasoning": optimization.reasoning,
        "expected_improvement": f"+{optimization.expected_improvement*100:.0f}%",
        "alternatives": optimization.alternative_strategies
    }


def get_recommendations() -> List[Dict[str, Any]]:
    """获取所有策略推荐"""
    engine = ExecutionEnhancementEngine()
    return engine.get_recommendations()


def get_stats(days: int = 30) -> Dict[str, Any]:
    """获取执行统计"""
    engine = ExecutionEnhancementEngine()
    return engine.get_stats(days)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="智能执行增强与自适应优化引擎")
    parser.add_argument("command", choices=["track", "analyze", "optimize", "recommend", "stats"],
                       help="命令: track-记录执行, analyze-分析意图, optimize-获取优化, recommend-策略推荐, stats-统计")
    parser.add_argument("data", nargs="?", help="执行数据(JSON字符串)")
    parser.add_argument("--days", type=int, default=30, help="统计天数")

    args = parser.parse_args()

    if args.command == "track":
        if not args.data:
            print("错误: 需要提供执行数据(JSON)")
            sys.exit(1)
        try:
            data = json.loads(args.data)
            result = track_execution(
                data.get("intent", ""),
                data.get("execution_type", "sequential"),
                data.get("steps", []),
                data.get("duration", 0),
                data.get("success", False),
                data.get("error_message", ""),
                data.get("context")
            )
            print(json.dumps(result, ensure_ascii=False, indent=2))
        except json.JSONDecodeError:
            print("错误: 数据必须是有效的JSON格式")
            sys.exit(1)

    elif args.command == "analyze":
        if not args.data:
            print("错误: 需要提供意图")
            sys.exit(1)
        result = analyze_intent(args.data)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "optimize":
        context = {}
        if args.data:
            try:
                context = json.loads(args.data)
            except json.JSONDecodeError:
                print("警告: 无法解析上下文，使用默认")

        result = get_optimization(context)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "recommend":
        result = get_recommendations()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "stats":
        result = get_stats(args.days)
        print(json.dumps(result, ensure_ascii=False, indent=2))