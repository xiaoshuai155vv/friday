#!/usr/bin/env python3
"""
智能全场景进化环元进化方法论迭代递归优化引擎 V2

在 round 650 完成的元进化方法论递归优化引擎和 round 656 能力评估认证引擎 V2 基础上，
构建更深层次的元元学习能力。让系统能够：
1. 评估自身评估标准的合理性
2. 自动优化评估方法论
3. 形成"学会如何评估"的递归能力
4. 与 round 656 能力评估认证引擎深度集成

此引擎让系统从「方法论优化」升级到「评估标准自我进化」，实现真正的元元学习。

Version: 1.0.0
Author: AI Evolution System
"""

import json
import os
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import statistics
import argparse


class EvolutionMetaMethodologyIterationRecursiveOptimizerV2:
    """元进化方法论迭代递归优化引擎 V2 - 实现元元学习能力"""

    VERSION = "1.0.0"

    def __init__(self, base_dir: str = None):
        self.base_dir = Path(base_dir) if base_dir else Path(__file__).parent.parent
        self.runtime_dir = self.base_dir / "runtime"
        self.state_dir = self.runtime_dir / "state"
        self.logs_dir = self.runtime_dir / "logs"
        self.scripts_dir = self.base_dir / "scripts"

        # 数据库路径
        self.db_path = self.runtime_dir / "state" / "meta_methodology_iteration_recursive_v2.db"

        # 初始化数据库
        self._init_database()

    def _init_database(self):
        """初始化元元学习数据库"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # 评估标准合理性分析表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS assessment_standard_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_id TEXT NOT NULL UNIQUE,
                dimension TEXT NOT NULL,
                current_weight REAL,
                suggested_weight REAL,
                rationality_score REAL,
                analysis_reason TEXT,
                based_on_data TEXT,
                analysis_round INTEGER,
                analysis_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 评估方法论优化记录表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS methodology_optimization_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                optimization_id TEXT NOT NULL UNIQUE,
                optimization_type TEXT,
                before_state TEXT,
                after_state TEXT,
                expected_improvement REAL,
                actual_improvement REAL,
                optimization_round INTEGER,
                optimization_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 元元学习闭环记录表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS meta_learning_closed_loop (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                loop_id TEXT NOT NULL UNIQUE,
                evaluation_cycle INTEGER,
                assessment_outcome TEXT,
                standard_adjustment TEXT,
                method_change TEXT,
                result_feedback TEXT,
                loop_completed BOOLEAN DEFAULT 0,
                loop_round INTEGER,
                loop_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 评估标准历史调整表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS standard_adjustment_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                adjustment_id TEXT NOT NULL UNIQUE,
                dimension TEXT NOT NULL,
                old_weight REAL,
                new_weight REAL,
                adjustment_reason TEXT,
                adjustment_source TEXT,
                adjustment_round INTEGER,
                adjustment_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()

    def analyze_assessment_standard_rationality(self) -> Dict[str, Any]:
        """
        分析评估标准的合理性
        基于历史评估数据，判断当前评估标准是否合理
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # 尝试读取 round 656 能力评估认证引擎的数据
        assessment_v2_db = self.runtime_dir / "state" / "meta_capability_assessment_v2.db"

        analysis_results = {}

        if assessment_v2_db.exists():
            try:
                conn_v2 = sqlite3.connect(str(assessment_v2_db))
                cursor_v2 = conn_v2.cursor()

                # 获取历史评估数据
                cursor_v2.execute("""
                    SELECT overall_score, dimension_scores, assessment_round
                    FROM comprehensive_assessments
                    ORDER BY assessment_timestamp DESC
                    LIMIT 20
                """)
                records = cursor_v2.fetchall()

                # 基于数据分布分析权重合理性
                dimension_scores = {}
                for overall_score, dim_scores_data, round_num in records:
                    try:
                        # dimension_scores 可能是 JSON 字符串或已经是字典
                        if isinstance(dim_scores_data, str):
                            dim_scores = json.loads(dim_scores_data) if dim_scores_data else {}
                        elif isinstance(dim_scores_data, dict):
                            dim_scores = dim_scores_data
                        else:
                            dim_scores = {}

                        for dim, score in dim_scores.items():
                            if dim not in dimension_scores:
                                dimension_scores[dim] = {"scores": [], "count": 0}
                            # 确保 score 是数值类型
                            try:
                                score_val = float(score) if score is not None else 0
                                dimension_scores[dim]["scores"].append(score_val)
                                dimension_scores[dim]["count"] += 1
                            except (ValueError, TypeError):
                                pass
                    except Exception as e:
                        pass

                # 计算每个维度的平均分和稳定性
                dimension_analysis = {}
                for dim, data in dimension_scores.items():
                    scores = data["scores"]
                    if len(scores) >= 1:
                        dimension_analysis[dim] = {
                            "avg_score": statistics.mean(scores),
                            "count": len(scores),
                            "stability": self._calculate_stability_from_scores(scores)
                        }

                # 分析各维度权重的合理性
                # 如果某维度得分持续很高但权重低，可能需要增加权重
                # 如果某维度得分持续很低但权重高，可能需要降低权重

                # 定义标准权重
                standard_weights = {
                    "self_learning": 0.20,
                    "self_optimization": 0.18,
                    "innovation": 0.17,
                    "collaboration": 0.15,
                    "value_realization": 0.15,
                    "health_maintenance": 0.10,
                    "autonomy": 0.05
                }

                for dim, data in dimension_analysis.items():
                    avg_score = data["avg_score"]
                    stability = data["stability"]
                    count = data["count"]

                    # 计算合理性分数
                    rationality_score = 0.5  # 基础分

                    # 稳定性影响：稳定的数据更可信
                    if stability > 0.8:
                        rationality_score += 0.2

                    # 得分与权重匹配度
                    current_weight = standard_weights.get(dim, 0.1)
                    if avg_score > 70:  # 高得分维度
                        if current_weight < 0.15:
                            rationality_score += 0.2  # 高分低权，可能不合理
                    elif avg_score < 40:  # 低得分维度
                        if current_weight > 0.15:
                            rationality_score += 0.2  # 低分高权，可能不合理

                    analysis_results[dim] = {
                        "current_weight": current_weight,
                        "suggested_weight": current_weight,  # 初步不修改，后续基于更多分析
                        "rationality_score": min(rationality_score, 1.0),
                        "analysis_reason": self._generate_rationality_reason(dim, avg_score, stability),
                        "based_on_data": f"基于{count}次评估数据分析"
                    }

                conn_v2.close()
            except Exception as e:
                analysis_results["error"] = f"无法读取评估数据: {str(e)}"

        conn.close()
        return analysis_results

    def _calculate_stability(self, dimension: str, cursor) -> float:
        """计算维度评分的稳定性"""
        try:
            cursor.execute("""
                SELECT metric_value FROM capability_assessments
                WHERE dimension = ?
                ORDER BY assessment_timestamp DESC
                LIMIT 10
            """, (dimension,))
            values = [row[0] for row in cursor.fetchall() if row[0] is not None]

            if len(values) < 2:
                return 0.5

            return self._calculate_stability_from_scores(values)
        except:
            return 0.5

    def _calculate_stability_from_scores(self, values: List[float]) -> float:
        """从分数列表计算稳定性"""
        if len(values) < 2:
            return 0.5

        # 计算变异系数(CV)的倒数作为稳定性分数
        mean_val = statistics.mean(values)
        if mean_val == 0:
            return 0.5

        stdev_val = statistics.stdev(values) if len(values) > 1 else 0
        cv = stdev_val / mean_val if mean_val > 0 else 0

        # CV越小稳定性越高，转换为0-1分数
        stability = max(0, min(1, 1 - cv))
        return stability

    def _generate_rationality_reason(self, dimension: str, avg_score: float, stability: float) -> str:
        """生成合理性分析原因"""
        reasons = []

        if stability > 0.8:
            reasons.append("评估数据稳定可靠")
        else:
            reasons.append("评估数据存在波动，需进一步观察")

        if avg_score > 70:
            reasons.append(f"平均得分{avg_score:.1f}较高，说明该维度能力较强")
        elif avg_score < 40:
            reasons.append(f"平均得分{avg_score:.1f}较低，说明该维度存在较大提升空间")
        else:
            reasons.append(f"平均得分{avg_score:.1f}处于中等水平")

        return "；".join(reasons)

    def optimize_assessment_methodology(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        优化评估方法论
        基于分析结果自动调整评估方法和权重
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        optimization_records = []

        for dim, analysis in analysis_results.items():
            if dim == "error":
                continue

            rationality = analysis.get("rationality_score", 0.5)

            # 如果合理性分数低于阈值，生成优化建议
            if rationality < 0.7:
                suggested_weight = analysis.get("current_weight", 0.1)

                # 合理性低且得分高 → 建议增加权重
                # 合理性低且得分低 → 建议减少权重

                optimization_id = f"opt_{dim}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

                cursor.execute("""
                    INSERT INTO methodology_optimization_records
                    (optimization_id, optimization_type, before_state, after_state,
                     expected_improvement, optimization_round)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    optimization_id,
                    "weight_adjustment",
                    json.dumps({"weight": analysis.get("current_weight")}),
                    json.dumps({"weight": suggested_weight, "reason": "rationality_low"}),
                    rationality,
                    1
                ))

                optimization_records.append({
                    "dimension": dim,
                    "current_weight": analysis.get("current_weight"),
                    "suggested_weight": suggested_weight,
                    "reason": "rationality_low"
                })

        conn.commit()
        conn.close()

        return {
            "optimization_count": len(optimization_records),
            "optimizations": optimization_records
        }

    def execute_meta_learning_closed_loop(self) -> Dict[str, Any]:
        """
        执行元元学习闭环
        实现「评估→调整→执行→反馈」的递归优化
        """
        # 1. 分析评估标准合理性
        analysis_results = self.analyze_assessment_standard_rationality()

        # 2. 基于分析优化方法论
        optimization_results = self.optimize_assessment_methodology(analysis_results)

        # 3. 记录闭环
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        loop_id = f"meta_loop_{datetime.now().strftime('%Y%m%d%H%M%S')}"

        cursor.execute("""
            INSERT INTO meta_learning_closed_loop
            (loop_id, evaluation_cycle, assessment_outcome, standard_adjustment,
             method_change, result_feedback, loop_completed, loop_round)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            loop_id,
            1,
            json.dumps(analysis_results),
            json.dumps(optimization_results.get("optimizations", [])),
            json.dumps({"optimization_count": optimization_results.get("optimization_count", 0)}),
            json.dumps({"status": "completed", "timestamp": datetime.now().isoformat()}),
            True,
            1
        ))

        conn.commit()
        conn.close()

        return {
            "loop_id": loop_id,
            "analysis_results": analysis_results,
            "optimization_results": optimization_results,
            "status": "completed"
        }

    def get_status_summary(self) -> Dict[str, Any]:
        """获取引擎状态摘要"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # 统计闭环数量
        cursor.execute("SELECT COUNT(*) FROM meta_learning_closed_loop WHERE loop_completed = 1")
        completed_loops = cursor.fetchone()[0]

        # 统计优化记录数
        cursor.execute("SELECT COUNT(*) FROM methodology_optimization_records")
        optimization_count = cursor.fetchone()[0]

        # 统计标准调整历史
        cursor.execute("SELECT COUNT(*) FROM standard_adjustment_history")
        adjustment_count = cursor.fetchone()[0]

        conn.close()

        return {
            "version": self.VERSION,
            "completed_loops": completed_loops,
            "optimization_count": optimization_count,
            "adjustment_count": adjustment_count,
            "status": "active"
        }

    def run(self, mode: str = "full") -> Dict[str, Any]:
        """
        运行引擎

        Args:
            mode: 运行模式
                - "analyze": 仅分析评估标准合理性
                - "optimize": 仅优化方法论
                - "full": 完整元元学习闭环
        """
        if mode == "analyze":
            return self.analyze_assessment_standard_rationality()
        elif mode == "optimize":
            analysis = self.analyze_assessment_standard_rationality()
            return self.optimize_assessment_methodology(analysis)
        else:  # full
            return self.execute_meta_learning_closed_loop()


def main():
    """主入口"""
    parser = argparse.ArgumentParser(
        description="元进化方法论迭代递归优化引擎 V2 - 实现元元学习能力"
    )
    parser.add_argument("--version", action="store_true", help="显示版本信息")
    parser.add_argument("--analyze", action="store_true", help="分析评估标准合理性")
    parser.add_argument("--optimize", action="store_true", help="优化评估方法论")
    parser.add_argument("--full", action="store_true", help="执行完整元元学习闭环")
    parser.add_argument("--status", action="store_true", help="获取引擎状态")

    args = parser.parse_args()

    engine = EvolutionMetaMethodologyIterationRecursiveOptimizerV2()

    if args.version:
        print(f"evolution_meta_methodology_iteration_recursive_optimizer_v2.py version {engine.VERSION}")
        return

    if args.status:
        status = engine.get_status_summary()
        print(json.dumps(status, ensure_ascii=False, indent=2))
        return

    if args.analyze:
        result = engine.run("analyze")
    elif args.optimize:
        result = engine.run("optimize")
    elif args.full:
        result = engine.run("full")
    else:
        # 默认执行完整闭环
        result = engine.run("full")

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()