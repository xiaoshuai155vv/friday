#!/usr/bin/env python3
"""
智能全场景进化环元进化优化策略自评估与自适应调整引擎

在 round 662 完成的系统自驱动持续优化引擎基础上，构建让系统能够
评估自身优化策略有效性的能力，形成「优化→评估→自适应调整」的完整
递归闭环。系统能够：
1. 自动收集优化策略执行数据（效率、效果、资源消耗等）
2. 评估不同优化策略的有效性
3. 识别低效优化模式
4. 生成优化策略调整建议
5. 实现策略自适应调整
6. 与 round 662 自驱动优化引擎深度集成，形成元优化循环

此引擎让系统从「能优化」升级到「学会如何优化」，实现真正的元元优化
（meta-optimization）能力。

Version: 1.0.0
Author: AI Evolution System
"""

import json
import os
import sqlite3
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import uuid
import argparse


class EvolutionMetaOptimizationStrategySelfEvaluationEngine:
    """元进化优化策略自评估与自适应调整引擎"""

    VERSION = "1.0.0"

    def __init__(self, base_dir: str = None):
        self.base_dir = Path(base_dir) if base_dir else Path(__file__).parent.parent
        self.runtime_dir = self.base_dir / "runtime"
        self.state_dir = self.runtime_dir / "state"
        self.logs_dir = self.runtime_dir / "logs"
        self.scripts_dir = self.base_dir / "scripts"

        # 数据库路径
        self.db_path = self.runtime_dir / "state" / "meta_optimization_strategy_self_evaluation.db"

        # 初始化数据库
        self._init_database()

    def _init_database(self):
        """初始化元优化评估数据库"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # 优化策略执行数据表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS optimization_strategy_executions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                execution_id TEXT NOT NULL UNIQUE,
                strategy_type TEXT,
                strategy_params TEXT,
                execution_context TEXT,
                execution_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                execution_duration REAL,
                resource_usage_cpu REAL,
                resource_usage_memory REAL,
                execution_result TEXT,
                outcome_score REAL
            )
        """)

        # 策略有效性评估表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS strategy_effectiveness_evaluations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                evaluation_id TEXT NOT NULL UNIQUE,
                strategy_type TEXT,
                evaluation_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                effectiveness_score REAL,
                efficiency_score REAL,
                resource_efficiency_score REAL,
                outcome_quality_score REAL,
                evaluation_details TEXT,
                sample_size INTEGER
            )
        """)

        # 低效模式识别表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS inefficient_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_id TEXT NOT NULL UNIQUE,
                pattern_type TEXT,
                detected_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                pattern_description TEXT,
                frequency_count INTEGER,
                severity_level REAL,
                suggested_adjustment TEXT,
                status TEXT DEFAULT 'pending'
            )
        """)

        # 策略调整记录表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS strategy_adjustments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                adjustment_id TEXT NOT NULL UNIQUE,
                source_strategy_type TEXT,
                adjustment_type TEXT,
                adjustment_params TEXT,
                adjustment_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reason TEXT,
                expected_improvement REAL,
                actual_improvement REAL,
                adjustment_applied INTEGER DEFAULT 0
            )
        """)

        # 元优化认知表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS meta_optimization_cognition (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cognition_id TEXT NOT NULL UNIQUE,
                cognition_type TEXT,
                previous_belief TEXT,
                new_belief TEXT,
                evidence_strength REAL,
                created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()

    def collect_strategy_execution_data(self) -> List[Dict]:
        """收集自驱动优化引擎的执行数据"""
        # 从 round 662 的数据库获取执行数据
        optimizer_db_path = self.runtime_dir / "state" / "meta_self_driven_continual_optimizer.db"

        if not optimizer_db_path.exists():
            return []

        try:
            conn = sqlite3.connect(str(optimizer_db_path))
            cursor = conn.cursor()

            # 获取最近的优化任务执行数据
            cursor.execute("""
                SELECT task_id, task_name, task_type, priority_score,
                       estimated_impact, estimated_effort, status,
                       executed_timestamp, completed_timestamp,
                       execution_result, validation_result
                FROM optimization_tasks
                WHERE executed_timestamp IS NOT NULL
                ORDER BY executed_timestamp DESC
                LIMIT 50
            """)

            executions = []
            for row in cursor.fetchall():
                execution = {
                    "execution_id": str(uuid.uuid4()),
                    "task_id": row[0],
                    "task_name": row[1],
                    "strategy_type": row[2],
                    "priority_score": row[3],
                    "estimated_impact": row[4],
                    "estimated_effort": row[5],
                    "status": row[6],
                    "executed_timestamp": row[7],
                    "completed_timestamp": row[8],
                    "execution_result": json.loads(row[9]) if row[9] else {},
                    "validation_result": json.loads(row[10]) if row[10] else {}
                }

                # 计算执行时长
                if row[7] and row[8]:
                    try:
                        exec_time = datetime.fromisoformat(row[8].replace('Z', '+00:00')) - \
                                   datetime.fromisoformat(row[7].replace('Z', '+00:00'))
                        execution["execution_duration"] = exec_time.total_seconds()
                    except:
                        execution["execution_duration"] = 0
                else:
                    execution["execution_duration"] = 0

                executions.append(execution)

            conn.close()
            return executions

        except Exception as e:
            print(f"收集执行数据失败: {e}")
            return []

    def evaluate_strategy_effectiveness(self, executions: List[Dict]) -> Dict:
        """评估优化策略的有效性"""
        if not executions:
            return {
                "evaluation_id": str(uuid.uuid4()),
                "effectiveness_score": 0,
                "evaluations": [],
                "message": "无执行数据可供评估"
            }

        # 按策略类型分组
        strategy_groups = {}
        for exec_data in executions:
            strategy_type = exec_data.get("strategy_type", "unknown")
            if strategy_type not in strategy_groups:
                strategy_groups[strategy_type] = []
            strategy_groups[strategy_type].append(exec_data)

        evaluations = []

        for strategy_type, group in strategy_groups.items():
            if not group:
                continue

            # 计算各维度评分
            total_count = len(group)
            success_count = sum(1 for e in group if e.get("status") == "completed")
            validation_pass_count = sum(
                1 for e in group
                if e.get("execution_result", {}).get("executed", False) and
                   e.get("validation_result", {}).get("passed", False)
            )

            # 效率评分：基于执行时长和任务复杂度
            avg_duration = sum(
                e.get("execution_duration", 0) for e in group
            ) / total_count if total_count > 0 else 0

            efficiency_score = 1.0 / (1.0 + avg_duration / 60)  # 标准化

            # 效果评分：成功率
            effectiveness_score = success_count / total_count if total_count > 0 else 0

            # 质量评分：验证通过率
            outcome_quality = validation_pass_count / success_count if success_count > 0 else 0

            # 资源效率评分（基于 estimated_effort）
            avg_effort = sum(e.get("estimated_effort", 0.5) for e in group) / total_count
            resource_efficiency = 1.0 - avg_effort

            evaluation = {
                "strategy_type": strategy_type,
                "total_executions": total_count,
                "success_count": success_count,
                "validation_pass_count": validation_pass_count,
                "effectiveness_score": effectiveness_score,
                "efficiency_score": efficiency_score,
                "outcome_quality_score": outcome_quality,
                "resource_efficiency_score": resource_efficiency,
                "avg_execution_duration": avg_duration,
                "avg_priority_score": sum(e.get("priority_score", 0) for e in group) / total_count,
                "avg_estimated_impact": sum(e.get("estimated_impact", 0) for e in group) / total_count
            }
            evaluations.append(evaluation)

            # 保存评估结果到数据库
            self._save_evaluation(strategy_type, evaluation, total_count)

        # 计算总体评分
        overall_effectiveness = sum(e["effectiveness_score"] for e in evaluations) / len(evaluations) if evaluations else 0
        overall_efficiency = sum(e["efficiency_score"] for e in evaluations) / len(evaluations) if evaluations else 0

        return {
            "evaluation_id": str(uuid.uuid4()),
            "overall_effectiveness_score": overall_effectiveness,
            "overall_efficiency_score": overall_efficiency,
            "strategy_evaluations": evaluations,
            "total_strategies_evaluated": len(evaluations),
            "timestamp": datetime.now().isoformat()
        }

    def _save_evaluation(self, strategy_type: str, evaluation: Dict, sample_size: int):
        """保存策略评估结果"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        evaluation_id = str(uuid.uuid4())
        cursor.execute("""
            INSERT INTO strategy_effectiveness_evaluations
            (evaluation_id, strategy_type, effectiveness_score, efficiency_score,
             resource_efficiency_score, outcome_quality_score, evaluation_details, sample_size)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            evaluation_id,
            strategy_type,
            evaluation.get("effectiveness_score", 0),
            evaluation.get("efficiency_score", 0),
            evaluation.get("resource_efficiency_score", 0),
            evaluation.get("outcome_quality_score", 0),
            json.dumps(evaluation),
            sample_size
        ))

        conn.commit()
        conn.close()

    def identify_inefficient_patterns(self, evaluations: Dict) -> List[Dict]:
        """识别低效优化模式"""
        inefficient_patterns = []

        strategy_evaluations = evaluations.get("strategy_evaluations", [])

        for eval_data in strategy_evaluations:
            strategy_type = eval_data.get("strategy_type")
            effectiveness = eval_data.get("effectiveness_score", 0)
            efficiency = eval_data.get("efficiency_score", 0)
            quality = eval_data.get("outcome_quality_score", 0)

            # 识别低效模式
            if effectiveness < 0.5:
                pattern = {
                    "pattern_id": str(uuid.uuid4()),
                    "pattern_type": "low_effectiveness",
                    "pattern_description": f"策略 {strategy_type} 效果低（{effectiveness:.1%}）",
                    "frequency_count": 1,
                    "severity_level": 1.0 - effectiveness,
                    "suggested_adjustment": "建议调整策略参数或更换策略类型"
                }
                inefficient_patterns.append(pattern)

            if efficiency < 0.3:
                pattern = {
                    "pattern_id": str(uuid.uuid4()),
                    "pattern_type": "low_efficiency",
                    "pattern_description": f"策略 {strategy_type} 效率低（{efficiency:.1%}）",
                    "frequency_count": 1,
                    "severity_level": 1.0 - efficiency,
                    "suggested_adjustment": "建议优化执行流程或减少资源消耗"
                }
                inefficient_patterns.append(pattern)

            if quality < 0.3 and eval_data.get("total_executions", 0) > 3:
                pattern = {
                    "pattern_id": str(uuid.uuid4()),
                    "pattern_type": "low_quality",
                    "pattern_description": f"策略 {strategy_type} 质量不稳定（{quality:.1%}）",
                    "frequency_count": eval_data.get("total_executions", 0),
                    "severity_level": 1.0 - quality,
                    "suggested_adjustment": "建议加强策略验证或增加容错机制"
                }
                inefficient_patterns.append(pattern)

        # 保存低效模式
        self._save_inefficient_patterns(inefficient_patterns)

        return inefficient_patterns

    def _save_inefficient_patterns(self, patterns: List[Dict]):
        """保存低效模式到数据库"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        for pattern in patterns:
            # 检查是否已存在相同模式
            cursor.execute("""
                SELECT pattern_id FROM inefficient_patterns
                WHERE pattern_type = ? AND status = 'pending'
            """, (pattern["pattern_type"],))

            if not cursor.fetchone():
                cursor.execute("""
                    INSERT INTO inefficient_patterns
                    (pattern_id, pattern_type, pattern_description, frequency_count,
                     severity_level, suggested_adjustment, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    pattern["pattern_id"],
                    pattern["pattern_type"],
                    pattern["pattern_description"],
                    pattern["frequency_count"],
                    pattern["severity_level"],
                    pattern["suggested_adjustment"],
                    pattern.get("status", "pending")
                ))

        conn.commit()
        conn.close()

    def generate_strategy_adjustment_suggestions(self, evaluations: Dict,
                                                   patterns: List[Dict]) -> List[Dict]:
        """生成策略调整建议"""
        suggestions = []

        # 基于评估结果生成调整建议
        strategy_evaluations = evaluations.get("strategy_evaluations", [])

        for eval_data in strategy_evaluations:
            strategy_type = eval_data.get("strategy_type")
            effectiveness = eval_data.get("effectiveness_score", 0)
            efficiency = eval_data.get("efficiency_score", 0)

            # 效果差但效率高的策略：建议优化策略参数
            if effectiveness < 0.6 and efficiency > 0.5:
                suggestion = {
                    "adjustment_id": str(uuid.uuid4()),
                    "source_strategy_type": strategy_type,
                    "adjustment_type": "parameter_optimization",
                    "adjustment_params": {
                        "strategy_type": strategy_type,
                        "focus": "effectiveness",
                        "action": "调整策略参数以提高效果"
                    },
                    "reason": f"策略 {strategy_type} 效率高但效果差",
                    "expected_improvement": 0.3
                }
                suggestions.append(suggestion)

            # 效果高但效率低的策略：建议优化执行效率
            if effectiveness > 0.7 and efficiency < 0.4:
                suggestion = {
                    "adjustment_id": str(uuid.uuid4()),
                    "source_strategy_type": strategy_type,
                    "adjustment_type": "efficiency_optimization",
                    "adjustment_params": {
                        "strategy_type": strategy_type,
                        "focus": "efficiency",
                        "action": "优化执行流程以提高效率"
                    },
                    "reason": f"策略 {strategy_type} 效果好但效率低",
                    "expected_improvement": 0.25
                }
                suggestions.append(suggestion)

        # 基于低效模式生成建议
        for pattern in patterns:
            if pattern.get("severity_level", 0) > 0.5:
                suggestion = {
                    "adjustment_id": str(uuid.uuid4()),
                    "source_strategy_type": pattern.get("pattern_type"),
                    "adjustment_type": "pattern_based_fix",
                    "adjustment_params": {
                        "pattern_type": pattern.get("pattern_type"),
                        "action": pattern.get("suggested_adjustment")
                    },
                    "reason": f"检测到严重低效模式: {pattern.get('pattern_description')}",
                    "expected_improvement": pattern.get("severity_level", 0)
                }
                suggestions.append(suggestion)

        # 保存调整建议
        self._save_strategy_adjustments(suggestions)

        return suggestions

    def _save_strategy_adjustments(self, suggestions: List[Dict]):
        """保存策略调整建议"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        for suggestion in suggestions:
            cursor.execute("""
                INSERT INTO strategy_adjustments
                (adjustment_id, source_strategy_type, adjustment_type,
                 adjustment_params, reason, expected_improvement, adjustment_applied)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                suggestion["adjustment_id"],
                suggestion["source_strategy_type"],
                suggestion["adjustment_type"],
                json.dumps(suggestion["adjustment_params"]),
                suggestion["reason"],
                suggestion.get("expected_improvement", 0),
                0
            ))

        conn.commit()
        conn.close()

    def apply_strategy_adjustment(self, adjustment: Dict) -> Dict:
        """应用策略调整"""
        adjustment_id = adjustment.get("adjustment_id")

        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE strategy_adjustments
            SET adjustment_applied = 1
            WHERE adjustment_id = ?
        """, (adjustment_id,))

        conn.commit()
        conn.close()

        # 记录元优化认知更新
        self._update_meta_optimization_cognition(
            adjustment.get("source_strategy_type"),
            adjustment.get("adjustment_type"),
            adjustment.get("expected_improvement", 0)
        )

        return {
            "adjustment_id": adjustment_id,
            "applied": True,
            "applied_timestamp": datetime.now().isoformat()
        }

    def _update_meta_optimization_cognition(self, strategy_type: str,
                                             adjustment_type: str,
                                             expected_improvement: float):
        """更新元优化认知"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cognition_id = str(uuid.uuid4())

        # 读取之前的认知
        cursor.execute("""
            SELECT new_belief FROM meta_optimization_cognition
            WHERE cognition_type = ?
            ORDER BY created_timestamp DESC
            LIMIT 1
        """, (strategy_type,))

        row = cursor.fetchone()
        previous_belief = json.loads(row[0]) if row else {}

        # 更新认知
        new_belief = {
            "strategy_type": strategy_type,
            "last_adjustment_type": adjustment_type,
            "expected_improvement": expected_improvement,
            "belief_strength": min(previous_belief.get("belief_strength", 0) + 0.1, 1.0)
        }

        cursor.execute("""
            INSERT INTO meta_optimization_cognition
            (cognition_id, cognition_type, previous_belief, new_belief, evidence_strength)
            VALUES (?, ?, ?, ?, ?)
        """, (
            cognition_id,
            strategy_type,
            json.dumps(previous_belief),
            json.dumps(new_belief),
            expected_improvement
        ))

        conn.commit()
        conn.close()

    def run_meta_optimization_cycle(self) -> Dict:
        """运行完整的元优化循环"""
        cycle_result = {
            "cycle_timestamp": datetime.now().isoformat(),
            "stages_completed": []
        }

        # 阶段1：收集执行数据
        executions = self.collect_strategy_execution_data()
        cycle_result["stages_completed"].append("data_collection")
        cycle_result["executions_collected"] = len(executions)

        # 阶段2：评估策略有效性
        evaluations = self.evaluate_strategy_effectiveness(executions)
        cycle_result["stages_completed"].append("strategy_evaluation")
        cycle_result["evaluations"] = evaluations

        # 阶段3：识别低效模式
        patterns = self.identify_inefficient_patterns(evaluations)
        cycle_result["stages_completed"].append("pattern_identification")
        cycle_result["patterns_detected"] = len(patterns)

        # 阶段4：生成调整建议
        suggestions = self.generate_strategy_adjustment_suggestions(evaluations, patterns)
        cycle_result["stages_completed"].append("adjustment_generation")
        cycle_result["suggestions_generated"] = len(suggestions)

        # 阶段5：应用高优先级调整
        applied_count = 0
        for suggestion in suggestions[:2]:  # 最多应用2个
            result = self.apply_strategy_adjustment(suggestion)
            if result.get("applied"):
                applied_count += 1

        cycle_result["stages_completed"].append("adjustment_application")
        cycle_result["adjustments_applied"] = applied_count

        # 阶段6：生成循环报告
        cycle_result["stages_completed"].append("cycle_completion")
        cycle_result["success"] = applied_count > 0

        return cycle_result

    def get_meta_optimization_status(self) -> Dict:
        """获取当前元优化状态"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # 统计策略评估
        cursor.execute("""
            SELECT strategy_type, AVG(effectiveness_score) as avg_effectiveness,
                   AVG(efficiency_score) as avg_efficiency
            FROM strategy_effectiveness_evaluations
            WHERE evaluation_timestamp > datetime('now', '-24 hours')
            GROUP BY strategy_type
        """)

        strategy_stats = {}
        for row in cursor.fetchall():
            strategy_stats[row[0]] = {
                "avg_effectiveness": row[1],
                "avg_efficiency": row[2]
            }

        # 统计低效模式
        cursor.execute("""
            SELECT COUNT(*) FROM inefficient_patterns
            WHERE status = 'pending'
        """)
        pending_patterns = cursor.fetchone()[0]

        # 统计策略调整
        cursor.execute("""
            SELECT COUNT(*) FROM strategy_adjustments
            WHERE adjustment_applied = 1
            AND adjustment_timestamp > datetime('now', '-24 hours')
        """)
        recent_adjustments = cursor.fetchone()[0]

        # 统计元优化认知更新
        cursor.execute("""
            SELECT COUNT(*) FROM meta_optimization_cognition
            WHERE created_timestamp > datetime('now', '-24 hours')
        """)
        cognition_updates = cursor.fetchone()[0]

        conn.close()

        return {
            "strategy_statistics": strategy_stats,
            "pending_inefficient_patterns": pending_patterns,
            "recent_adjustments_applied": recent_adjustments,
            "cognition_updates_last_24h": cognition_updates,
            "timestamp": datetime.now().isoformat()
        }


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="元进化优化策略自评估与自适应调整引擎"
    )
    parser.add_argument(
        "--run-cycle",
        action="store_true",
        help="运行完整的元优化循环"
    )
    parser.add_argument(
        "--collect-data",
        action="store_true",
        help="收集策略执行数据"
    )
    parser.add_argument(
        "--evaluate",
        action="store_true",
        help="评估策略有效性"
    )
    parser.add_argument(
        "--identify-patterns",
        action="store_true",
        help="识别低效模式"
    )
    parser.add_argument(
        "--generate-suggestions",
        action="store_true",
        help="生成策略调整建议"
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="获取当前元优化状态"
    )
    parser.add_argument(
        "--cockpit",
        action="store_true",
        help="输出完整统计数据（驾驶舱用）"
    )

    args = parser.parse_args()

    engine = EvolutionMetaOptimizationStrategySelfEvaluationEngine()

    if args.run_cycle:
        result = engine.run_meta_optimization_cycle()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.collect_data:
        data = engine.collect_strategy_execution_data()
        print(json.dumps(data, ensure_ascii=False, indent=2))
    elif args.evaluate:
        executions = engine.collect_strategy_execution_data()
        result = engine.evaluate_strategy_effectiveness(executions)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.identify_patterns:
        executions = engine.collect_strategy_execution_data()
        evaluations = engine.evaluate_strategy_effectiveness(executions)
        patterns = engine.identify_inefficient_patterns(evaluations)
        print(json.dumps(patterns, ensure_ascii=False, indent=2))
    elif args.generate_suggestions:
        executions = engine.collect_strategy_execution_data()
        evaluations = engine.evaluate_strategy_effectiveness(executions)
        patterns = engine.identify_inefficient_patterns(evaluations)
        suggestions = engine.generate_strategy_adjustment_suggestions(evaluations, patterns)
        print(json.dumps(suggestions, ensure_ascii=False, indent=2))
    elif args.status:
        status = engine.get_meta_optimization_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))
    elif args.cockpit:
        status = engine.get_meta_optimization_status()
        executions = engine.collect_strategy_execution_data()
        evaluations = engine.evaluate_strategy_effectiveness(executions)

        cockpit_data = {
            "engine_name": "元进化优化策略自评估与自适应调整引擎",
            "version": engine.VERSION,
            "current_status": status,
            "recent_evaluation": evaluations,
            "executions_analyzed": len(executions),
            "timestamp": datetime.now().isoformat()
        }
        print(json.dumps(cockpit_data, ensure_ascii=False, indent=2))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()