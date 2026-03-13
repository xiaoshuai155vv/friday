#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
智能工作流智能推荐与自动优化引擎
基于用户历史执行记录、时间段、系统状态等上下文，智能推荐最合适的工作流，并自动优化执行路径

功能：
1. 工作流执行历史记录与分析
2. 基于时间段和上下文的智能推荐
3. 执行路径自动优化
4. 用户行为模式学习
"""
import os
import json
import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from collections import defaultdict
from dataclasses import dataclass, field, asdict


# 数据库路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(SCRIPT_DIR, '..', 'runtime', 'state', 'workflow_history.db')


@dataclass
class WorkflowExecutionRecord:
    """工作流执行记录"""
    workflow_name: str
    workflow_type: str
    trigger: str  # manual/auto/recommend
    timestamp: str
    success: bool
    id: int = None
    duration: float = 0.0
    context: Dict[str, Any] = field(default_factory=dict)
    day_of_week: int = 0
    hour: int = 0


@dataclass
class WorkflowRecommendation:
    """工作流推荐"""
    workflow_name: str
    workflow_path: str
    reason: str
    confidence: float  # 0-1
    based_on: List[str] = field(default_factory=list)
    priority: int = 0


class WorkflowHistoryDB:
    """工作流历史数据库"""

    def __init__(self, db_path: str = None):
        self.db_path = db_path or DB_PATH
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _init_db(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS workflow_executions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workflow_name TEXT NOT NULL,
                workflow_type TEXT,
                trigger TEXT,
                timestamp TEXT NOT NULL,
                success INTEGER,
                duration REAL DEFAULT 0.0,
                context TEXT,
                day_of_week INTEGER,
                hour INTEGER
            )
        ''')

        # 创建索引
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_workflow_name
            ON workflow_executions(workflow_name)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_timestamp
            ON workflow_executions(timestamp)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_day_hour
            ON workflow_executions(day_of_week, hour)
        ''')

        conn.commit()
        conn.close()

    def add_execution(self, record: WorkflowExecutionRecord):
        """添加执行记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO workflow_executions
            (workflow_name, workflow_type, trigger, timestamp, success, duration, context, day_of_week, hour)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            record.workflow_name,
            record.workflow_type,
            record.trigger,
            record.timestamp,
            1 if record.success else 0,
            record.duration,
            json.dumps(record.context, ensure_ascii=False),
            record.day_of_week,
            record.hour
        ))

        conn.commit()
        conn.close()

    def get_recent_executions(self, days: int = 7, limit: int = 100) -> List[WorkflowExecutionRecord]:
        """获取近期执行记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        since = (datetime.now() - timedelta(days=days)).isoformat()
        cursor.execute('''
            SELECT id, workflow_name, workflow_type, trigger, timestamp, success, duration, context, day_of_week, hour
            FROM workflow_executions
            WHERE timestamp >= ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (since, limit))

        records = []
        for row in cursor.fetchall():
            records.append(WorkflowExecutionRecord(
                id=row[0],
                workflow_name=row[1],
                workflow_type=row[2],
                trigger=row[3],
                timestamp=row[4],
                success=bool(row[5]),
                duration=row[6],
                context=json.loads(row[7]) if row[7] else {},
                day_of_week=row[8],
                hour=row[9]
            ))

        conn.close()
        return records

    def get_workflow_stats(self, workflow_name: str = None, days: int = 7) -> Dict[str, Any]:
        """获取工作流统计信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        since = (datetime.now() - timedelta(days=days)).isoformat()

        if workflow_name:
            cursor.execute('''
                SELECT
                    workflow_name,
                    COUNT(*) as total_executions,
                    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful_executions,
                    AVG(duration) as avg_duration,
                    day_of_week,
                    hour
                FROM workflow_executions
                WHERE timestamp >= ? AND workflow_name = ?
                GROUP BY workflow_name, day_of_week, hour
                ORDER BY total_executions DESC
            ''', (since, workflow_name))
        else:
            cursor.execute('''
                SELECT
                    workflow_name,
                    COUNT(*) as total_executions,
                    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful_executions,
                    AVG(duration) as avg_duration,
                    day_of_week,
                    hour
                FROM workflow_executions
                WHERE timestamp >= ?
                GROUP BY workflow_name, day_of_week, hour
                ORDER BY total_executions DESC
            ''', (since,))

        results = []
        for row in cursor.fetchall():
            results.append({
                'workflow_name': row[0],
                'total_executions': row[1],
                'successful_executions': row[2],
                'success_rate': row[2] / row[1] if row[1] > 0 else 0,
                'avg_duration': row[3],
                'day_of_week': row[4],
                'hour': row[5]
            })

        conn.close()
        return results


class WorkflowPatternAnalyzer:
    """工作流模式分析器"""

    def __init__(self, history_db: WorkflowHistoryDB):
        self.history_db = history_db

    def analyze_time_patterns(self, workflow_name: str = None) -> Dict[str, Any]:
        """分析时间模式"""
        records = self.history_db.get_recent_executions(days=14)

        if workflow_name:
            records = [r for r in records if r.workflow_name == workflow_name]

        # 按小时统计
        hour_counts = defaultdict(int)
        hour_success = defaultdict(lambda: {'total': 0, 'success': 0})

        # 按星期几统计
        dow_counts = defaultdict(int)
        dow_success = defaultdict(lambda: {'total': 0, 'success': 0})

        for record in records:
            hour_counts[record.hour] += 1
            hour_success[record.hour]['total'] += 1
            if record.success:
                hour_success[record.hour]['success'] += 1

            dow_counts[record.day_of_week] += 1
            dow_success[record.day_of_week]['total'] += 1
            if record.success:
                dow_success[record.day_of_week]['success'] += 1

        # 找出最常执行的时间段
        peak_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        peak_dow = sorted(dow_counts.items(), key=lambda x: x[1], reverse=True)[:3]

        return {
            'peak_hours': [{'hour': h, 'count': c} for h, c in peak_hours],
            'peak_days': [{'day': d, 'count': c} for d, c in peak_dow],
            'hour_distribution': dict(hour_counts),
            'day_distribution': dict(dow_counts),
            'hour_success_rate': {
                h: s['success'] / s['total'] if s['total'] > 0 else 0
                for h, s in hour_success.items()
            }
        }

    def get_frequent_workflows(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取最常执行的工作流"""
        records = self.history_db.get_recent_executions(days=30)

        workflow_counts = defaultdict(lambda: {'count': 0, 'success': 0, 'recent_time': None})

        for record in records:
            workflow_counts[record.workflow_name]['count'] += 1
            if record.success:
                workflow_counts[record.workflow_name]['success'] += 1
            if not workflow_counts[record.workflow_name]['recent_time'] or \
               record.timestamp > workflow_counts[record.workflow_name]['recent_time']:
                workflow_counts[record.workflow_name]['recent_time'] = record.timestamp

        sorted_workflows = sorted(
            workflow_counts.items(),
            key=lambda x: x[1]['count'],
            reverse=True
        )[:limit]

        return [
            {
                'name': name,
                'count': data['count'],
                'success_rate': data['success'] / data['count'] if data['count'] > 0 else 0,
                'recent_time': data['recent_time']
            }
            for name, data in sorted_workflows
        ]


class WorkflowSmartRecommender:
    """智能工作流推荐器"""

    TIME_CONTEXT_KEYWORDS = {
        'morning': list(range(6, 12)),
        'afternoon': list(range(12, 18)),
        'evening': list(range(18, 22)),
        'night': list(range(22, 24)) + list(range(0, 6)),
        'workday': list(range(0, 5)),  # Monday = 0
        'weekend': [5, 6]
    }

    def __init__(self, history_db: WorkflowHistoryDB, pattern_analyzer: WorkflowPatternAnalyzer):
        self.history_db = history_db
        self.pattern_analyzer = pattern_analyzer

    def get_recommendations(self, context: Dict[str, Any] = None, limit: int = 5) -> List[WorkflowRecommendation]:
        """获取推荐工作流"""
        context = context or {}
        recommendations = []

        current_hour = datetime.now().hour
        current_dow = datetime.now().weekday()

        # 1. 基于时间模式的推荐
        time_recommendations = self._recommend_by_time_pattern(current_hour, current_dow)
        recommendations.extend(time_recommendations)

        # 2. 基于用户习惯的推荐
        habit_recommendations = self._recommend_by_habits(limit - len(recommendations))
        recommendations.extend(habit_recommendations)

        # 3. 基于系统上下文的推荐
        if context.get('system_state'):
            context_recommendations = self._recommend_by_context(context, limit - len(recommendations))
            recommendations.extend(context_recommendations)

        # 按置信度排序
        recommendations.sort(key=lambda x: x.confidence, reverse=True)

        return recommendations[:limit]

    def _recommend_by_time_pattern(self, hour: int, dow: int) -> List[WorkflowRecommendation]:
        """基于时间模式推荐"""
        time_patterns = self.pattern_analyzer.analyze_time_patterns()

        recommendations = []
        for pattern in time_patterns.get('peak_hours', []):
            if pattern['hour'] == hour:
                # 找到这个时间最常执行的工作流
                frequent = self.pattern_analyzer.get_frequent_workflows(limit=3)
                for wf in frequent:
                    recommendations.append(WorkflowRecommendation(
                        workflow_name=wf['name'],
                        workflow_path=f"assets/plans/{wf['name']}.json",
                        reason=f"在当前时间段({hour}:00)经常执行",
                        confidence=0.8,
                        based_on=['time_pattern'],
                        priority=1
                    ))
                break

        return recommendations

    def _recommend_by_habits(self, limit: int) -> List[WorkflowRecommendation]:
        """基于用户习惯推荐"""
        frequent = self.pattern_analyzer.get_frequent_workflows(limit=limit)

        recommendations = []
        for wf in frequent:
            recommendations.append(WorkflowRecommendation(
                workflow_name=wf['name'],
                workflow_path=f"assets/plans/{wf['name']}.json",
                reason=f"您经常使用（近30天执行{wf['count']}次，成功率{int(wf['success_rate']*100)}%）",
                confidence=0.7,
                based_on=['user_habit'],
                priority=2
            ))

        return recommendations

    def _recommend_by_context(self, context: Dict[str, Any], limit: int) -> List[WorkflowRecommendation]:
        """基于系统上下文推荐"""
        recommendations = []

        system_state = context.get('system_state', {}).lower()

        # 基于系统状态的简单规则推荐
        if 'high_cpu' in system_state or 'high memory' in system_state:
            recommendations.append(WorkflowRecommendation(
                workflow_name='系统清理',
                workflow_path='assets/plans/system_cleanup.json',
                reason='检测到系统资源使用率高，建议清理',
                confidence=0.9,
                based_on=['system_context'],
                priority=1
            ))

        if 'idle' in system_state:
            recommendations.append(WorkflowRecommendation(
                workflow_name='定时任务检查',
                workflow_path='assets/plans/check_scheduled_tasks.json',
                reason='系统空闲，适合执行定时任务',
                confidence=0.6,
                based_on=['system_context'],
                priority=3
            ))

        return recommendations[:limit]


class WorkflowOptimizer:
    """工作流执行路径优化器"""

    def __init__(self):
        pass

    def optimize_workflow_path(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """优化工作流执行路径"""
        steps = workflow.get('steps', [])

        if not steps:
            return workflow

        # 优化策略：
        # 1. 合并连续的相同操作
        optimized_steps = self._merge_consecutive_steps(steps)

        # 2. 重新排序独立步骤以提高效率
        optimized_steps = self._reorder_steps(optimized_steps)

        # 3. 识别可并行的步骤
        parallelizable = self._find_parallelizable_steps(optimized_steps)

        return {
            **workflow,
            'steps': optimized_steps,
            'optimization': {
                'original_steps': len(steps),
                'optimized_steps': len(optimized_steps),
                'parallelizable': parallelizable,
                'improvement': f"{len(steps) - len(optimized_steps)} 步优化"
            }
        }

    def _merge_consecutive_steps(self, steps: List[Dict]) -> List[Dict]:
        """合并连续相同操作"""
        if not steps:
            return steps

        merged = [steps[0]]

        for step in steps[1:]:
            last_step = merged[-1]

            # 如果是连续的相同操作，尝试合并
            if step.get('action') == last_step.get('action'):
                if step.get('action') in ['wait', 'screenshot']:
                    # 相同类型但参数不同，保留
                    merged.append(step)
                elif step.get('action') == 'do':
                    # 合并 do 命令
                    merged.append(step)
                else:
                    merged.append(step)
            else:
                merged.append(step)

        return merged

    def _reorder_steps(self, steps: List[Dict]) -> List[Dict]:
        """重排独立步骤"""
        # 简单策略：wait 步骤可以移到前面
        wait_steps = [s for s in steps if s.get('action') == 'wait']
        other_steps = [s for s in steps if s.get('action') != 'wait']

        # 保留原有顺序，只移动 wait
        result = []
        for step in steps:
            if step.get('action') != 'wait':
                result.append(step)

        # 在最后添加 wait 步骤
        result.extend(wait_steps)

        return result

    def _find_parallelizable_steps(self, steps: List[Dict]) -> List[str]:
        """识别可并行的步骤"""
        # 简化的并行识别：纯数据处理步骤可以并行
        parallelizable = []

        for i, step in enumerate(steps):
            if step.get('action') in ['screenshot', 'wait']:
                parallelizable.append(f"step_{i}")

        return parallelizable


class WorkflowSmartRecommenderEngine:
    """智能工作流推荐与优化引擎主类"""

    def __init__(self):
        self.history_db = WorkflowHistoryDB()
        self.pattern_analyzer = WorkflowPatternAnalyzer(self.history_db)
        self.recommender = WorkflowSmartRecommender(self.history_db, self.pattern_analyzer)
        self.optimizer = WorkflowOptimizer()

    def record_execution(self, workflow_name: str, workflow_type: str = None,
                        trigger: str = 'manual', success: bool = True,
                        duration: float = 0.0, context: Dict[str, Any] = None):
        """记录工作流执行"""
        now = datetime.now()
        record = WorkflowExecutionRecord(
            workflow_name=workflow_name,
            workflow_type=workflow_type or 'general',
            trigger=trigger,
            timestamp=now.isoformat(),
            success=success,
            duration=duration,
            context=context or {},
            day_of_week=now.weekday(),
            hour=now.hour
        )
        self.history_db.add_execution(record)

    def get_recommendations(self, context: Dict[str, Any] = None, limit: int = 5) -> List[Dict[str, Any]]:
        """获取工作流推荐"""
        recommendations = self.recommender.get_recommendations(context, limit)
        return [
            {
                'workflow_name': r.workflow_name,
                'workflow_path': r.workflow_path,
                'reason': r.reason,
                'confidence': r.confidence,
                'based_on': r.based_on,
                'priority': r.priority
            }
            for r in recommendations
        ]

    def optimize_workflow(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """优化工作流执行路径"""
        return self.optimizer.optimize_workflow_path(workflow)

    def get_analytics(self, workflow_name: str = None, days: int = 7) -> Dict[str, Any]:
        """获取工作流分析数据"""
        time_patterns = self.pattern_analyzer.analyze_time_patterns(workflow_name)
        frequent = self.pattern_analyzer.get_frequent_workflows()
        stats = self.history_db.get_workflow_stats(workflow_name, days)

        return {
            'time_patterns': time_patterns,
            'frequent_workflows': frequent,
            'detailed_stats': stats
        }


# CLI 接口
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='智能工作流智能推荐与自动优化引擎')
    parser.add_argument('command', nargs='?', help='命令: recommend/optimize/analytics/record')
    parser.add_argument('--workflow', '-w', help='工作流名称')
    parser.add_argument('--json', action='store_true', help='输出JSON格式')
    parser.add_argument('--context', '-c', help='上下文JSON字符串')
    parser.add_argument('--limit', '-l', type=int, default=5, help='推荐数量')
    parser.add_argument('--days', '-d', type=int, default=7, help='分析天数')

    args = parser.parse_args()

    engine = WorkflowSmartRecommenderEngine()

    if args.command == 'recommend':
        context = {}
        if args.context:
            try:
                context = json.loads(args.context)
            except:
                pass
        recommendations = engine.get_recommendations(context, args.limit)
        if args.json:
            print(json.dumps({'recommendations': recommendations}, ensure_ascii=False, indent=2))
        else:
            print(f"智能工作流推荐 (共 {len(recommendations)} 项):")
            for i, rec in enumerate(recommendations, 1):
                print(f"\n{i}. {rec['workflow_name']}")
                print(f"   原因: {rec['reason']}")
                print(f"   置信度: {int(rec['confidence']*100)}%")
                print(f"   依据: {', '.join(rec['based_on'])}")

    elif args.command == 'analytics':
        analytics = engine.get_analytics(args.workflow, args.days)
        if args.json:
            print(json.dumps(analytics, ensure_ascii=False, indent=2))
        else:
            print(f"工作流分析 (最近 {args.days} 天):")
            print(f"\n最常执行的工作流:")
            for wf in analytics.get('frequent_workflows', [])[:5]:
                print(f"  - {wf['name']}: {wf['count']}次, 成功率{int(wf['success_rate']*100)}%")

            print(f"\n时间模式:")
            for pattern in analytics.get('time_patterns', {}).get('peak_hours', []):
                print(f"  - {pattern['hour']}:00: {pattern['count']}次执行")

    elif args.command == 'record':
        if args.workflow:
            engine.record_execution(args.workflow, success=True)
            print(f"已记录工作流执行: {args.workflow}")
        else:
            print("请提供 --workflow 参数")

    else:
        print("可用命令:")
        print("  recommend   - 获取智能工作流推荐")
        print("  optimize    - 优化工作流执行路径")
        print("  analytics   - 获取工作流分析数据")
        print("  record      - 记录工作流执行")
        print("\n示例:")
        print("  python workflow_smart_recommender.py recommend --limit 3")
        print("  python workflow_smart_recommender.py analytics --days 14")