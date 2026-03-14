"""
智能全场景进化环执行结果知识图谱反馈闭环引擎
Evolution Execution Feedback Knowledge Graph Integration Engine

版本: 1.0.0
功能: 将进化执行结果自动反馈到知识图谱进行更新，形成知识→触发→执行→验证→知识更新的递归增强闭环
依赖: evolution_trigger_execution_integration.py, evolution_knowledge_graph_reasoning.py
"""

import json
import os
import sqlite3
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path


class EvolutionExecutionFeedbackKGIntegration:
    """执行结果知识图谱反馈闭环引擎"""

    def __init__(self, project_root: Optional[str] = None):
        self.project_root = Path(project_root) if project_root else Path(__file__).parent.parent
        self.runtime_dir = self.project_root / "runtime"
        self.state_dir = self.runtime_dir / "state"
        self.kg_db_path = self.state_dir / "knowledge_graph.db"
        self.execution_history_path = self.state_dir / "execution_history.db"

        # 初始化知识图谱数据库
        self._init_knowledge_graph_db()

    def _init_knowledge_graph_db(self):
        """初始化知识图谱数据库"""
        if not self.kg_db_path.exists():
            self.kg_db_path.parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(str(self.kg_db_path))
        cursor = conn.cursor()

        # 创建知识图谱表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS kg_nodes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                node_type TEXT NOT NULL,
                name TEXT NOT NULL,
                properties TEXT,
                weight REAL DEFAULT 1.0,
                last_updated TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS kg_edges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_node TEXT NOT NULL,
                target_node TEXT NOT NULL,
                relation_type TEXT NOT NULL,
                weight REAL DEFAULT 1.0,
                last_updated TEXT,
                UNIQUE(source_node, target_node, relation_type)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS execution_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                execution_id TEXT NOT NULL,
                execution_type TEXT NOT NULL,
                success BOOLEAN,
                result_summary TEXT,
                execution_time REAL,
                knowledge_updates TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS knowledge_value_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                knowledge_node TEXT NOT NULL,
                usage_count INTEGER DEFAULT 0,
                success_count INTEGER DEFAULT 0,
                failure_count INTEGER DEFAULT 0,
                avg_execution_time REAL DEFAULT 0,
                last_used TEXT,
                computed_value REAL DEFAULT 0,
                last_computed TEXT
            )
        """)

        conn.commit()
        conn.close()

    def record_execution_feedback(self, execution_id: str, execution_type: str,
                                    success: bool, result_summary: str = "",
                                    execution_time: float = 0) -> bool:
        """记录执行反馈到知识图谱"""
        try:
            conn = sqlite3.connect(str(self.kg_db_path))
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO execution_feedback
                (execution_id, execution_type, success, result_summary, execution_time)
                VALUES (?, ?, ?, ?, ?)
            """, (execution_id, execution_type, success, result_summary, execution_time))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"记录执行反馈失败: {e}")
            return False

    def update_knowledge_weights_from_feedback(self, execution_results: List[Dict]) -> bool:
        """根据执行结果更新知识权重"""
        try:
            conn = sqlite3.connect(str(self.kg_db_path))
            cursor = conn.cursor()

            for result in execution_results:
                execution_id = result.get("execution_id", "")
                execution_type = result.get("execution_type", "")
                success = result.get("success", False)
                result_summary = result.get("result_summary", "")
                execution_time = result.get("execution_time", 0)
                affected_knowledge = result.get("affected_knowledge", [])

                # 记录执行反馈
                self.record_execution_feedback(
                    execution_id, execution_type, success, result_summary, execution_time
                )

                # 更新受影响知识的权重
                for knowledge_node in affected_knowledge:
                    if success:
                        # 成功：增加权重
                        cursor.execute("""
                            INSERT INTO knowledge_value_metrics
                            (knowledge_node, usage_count, success_count, avg_execution_time, last_used, computed_value, last_computed)
                            VALUES (?, 1, 1, ?, datetime('now'), ?, datetime('now'))
                            ON CONFLICT(knowledge_node) DO UPDATE SET
                                usage_count = usage_count + 1,
                                success_count = success_count + 1,
                                avg_execution_time = (avg_execution_time * usage_count + ?) / (usage_count + 1),
                                last_used = datetime('now'),
                                computed_value = computed_value * 1.1
                        """, (knowledge_node, execution_time, 1.1, execution_time))
                    else:
                        # 失败：降低权重
                        cursor.execute("""
                            INSERT INTO knowledge_value_metrics
                            (knowledge_node, usage_count, failure_count, last_used, computed_value, last_computed)
                            VALUES (?, 1, 1, datetime('now'), ?, datetime('now'))
                            ON CONFLICT(knowledge_node) DO UPDATE SET
                                usage_count = usage_count + 1,
                                failure_count = failure_count + 1,
                                last_used = datetime('now'),
                                computed_value = max(0.1, computed_value * 0.9)
                        """, (knowledge_node, 0.9))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"更新知识权重失败: {e}")
            return False

    def get_knowledge_value_ranking(self, limit: int = 10) -> List[Dict]:
        """获取知识价值排名"""
        try:
            conn = sqlite3.connect(str(self.kg_db_path))
            cursor = conn.cursor()

            cursor.execute("""
                SELECT knowledge_node, usage_count, success_count, failure_count,
                       avg_execution_time, computed_value, last_used
                FROM knowledge_value_metrics
                ORDER BY computed_value DESC
                LIMIT ?
            """, (limit,))

            results = []
            for row in cursor.fetchall():
                results.append({
                    "knowledge_node": row[0],
                    "usage_count": row[1],
                    "success_count": row[2],
                    "failure_count": row[3],
                    "avg_execution_time": row[4],
                    "computed_value": row[5],
                    "last_used": row[6]
                })

            conn.close()
            return results
        except Exception as e:
            print(f"获取知识价值排名失败: {e}")
            return []

    def analyze_execution_trends(self, days: int = 7) -> Dict[str, Any]:
        """分析执行趋势"""
        try:
            conn = sqlite3.connect(str(self.kg_db_path))
            cursor = conn.cursor()

            cursor.execute("""
                SELECT execution_type, success, COUNT(*) as count
                FROM execution_feedback
                WHERE created_at >= datetime('now', '-' || ? || ' days')
                GROUP BY execution_type, success
            """, (days,))

            trends = {}
            for row in cursor.fetchall():
                exec_type = row[0]
                success = row[1]
                count = row[2]

                if exec_type not in trends:
                    trends[exec_type] = {"success": 0, "failure": 0}

                if success:
                    trends[exec_type]["success"] = count
                else:
                    trends[exec_type]["failure"] = count

            conn.close()
            return {
                "period_days": days,
                "trends": trends,
                "analyzed_at": datetime.now().isoformat()
            }
        except Exception as e:
            print(f"分析执行趋势失败: {e}")
            return {}

    def optimize_trigger_recommendations(self) -> List[Dict]:
        """基于知识价值优化触发推荐"""
        try:
            # 获取高价值知识
            high_value_knowledge = self.get_knowledge_value_ranking(limit=20)

            # 基于知识价值生成优化后的触发推荐
            optimized_recommendations = []

            for knowledge in high_value_knowledge:
                if knowledge["computed_value"] >= 1.0 and knowledge["usage_count"] >= 2:
                    # 高价值知识：增加触发权重
                    recommendation = {
                        "knowledge_node": knowledge["knowledge_node"],
                        "trigger_weight": min(1.0, knowledge["computed_value"]),
                        "reason": f"高价值知识(computed_value={knowledge['computed_value']:.2f}), 成功次数:{knowledge['success_count']}",
                        "estimated_roi": knowledge["computed_value"] / max(knowledge["avg_execution_time"], 0.1)
                    }
                    optimized_recommendations.append(recommendation)

            return optimized_recommendations
        except Exception as e:
            print(f"优化触发推荐失败: {e}")
            return []

    def close_loop(self, execution_id: str, execution_results: List[Dict]) -> Dict[str, Any]:
        """执行完整的知识反馈闭环"""
        # 1. 更新知识权重
        weight_update_success = self.update_knowledge_weights_from_feedback(execution_results)

        # 2. 分析执行趋势
        trends = self.analyze_execution_trends()

        # 3. 优化触发推荐
        optimized_recs = self.optimize_trigger_recommendations()

        return {
            "execution_id": execution_id,
            "weight_update_success": weight_update_success,
            "trends": trends,
            "optimized_recommendations": optimized_recs,
            "loop_completed_at": datetime.now().isoformat()
        }

    def get_status(self) -> Dict[str, Any]:
        """获取引擎状态"""
        try:
            conn = sqlite3.connect(str(self.kg_db_path))
            cursor = conn.cursor()

            # 统计执行反馈数量
            cursor.execute("SELECT COUNT(*) FROM execution_feedback")
            feedback_count = cursor.fetchone()[0]

            # 统计知识价值指标数量
            cursor.execute("SELECT COUNT(*) FROM knowledge_value_metrics")
            metrics_count = cursor.fetchone()[0]

            # 获取最近一次执行
            cursor.execute("""
                SELECT execution_id, execution_type, success, result_summary, created_at
                FROM execution_feedback
                ORDER BY created_at DESC
                LIMIT 1
            """)
            last_execution = cursor.fetchone()

            conn.close()

            return {
                "status": "running",
                "feedback_count": feedback_count,
                "knowledge_metrics_count": metrics_count,
                "last_execution": {
                    "execution_id": last_execution[0] if last_execution else None,
                    "execution_type": last_execution[1] if last_execution else None,
                    "success": last_execution[2] if last_execution else None,
                    "result_summary": last_execution[3] if last_execution else None,
                    "created_at": last_execution[4] if last_execution else None
                } if last_execution else None,
                "version": "1.0.0"
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            # 测试数据库连接
            conn = sqlite3.connect(str(self.kg_db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.execute("SELECT COUNT(*) FROM kg_nodes")
            conn.close()

            return {
                "healthy": True,
                "database_accessible": True,
                "version": "1.0.0"
            }
        except Exception as e:
            return {
                "healthy": False,
                "database_accessible": False,
                "error": str(e),
                "version": "1.0.0"
            }


# ========== 命令行入口 ==========
def main():
    import argparse
    parser = argparse.ArgumentParser(description="执行结果知识图谱反馈闭环引擎")
    parser.add_argument("command", nargs="?", default="status",
                       help="命令: status, health, analyze, feedback, optimize, close_loop")
    parser.add_argument("--execution-id", help="执行ID")
    parser.add_argument("--execution-type", help="执行类型")
    parser.add_argument("--success", type=lambda x: x.lower() == "true", help="是否成功")
    parser.add_argument("--result-summary", help="结果摘要")
    parser.add_argument("--execution-time", type=float, help="执行时间")
    parser.add_argument("--affected-knowledge", nargs="*", help="受影响的知识节点")
    parser.add_argument("--days", type=int, default=7, help="分析天数")

    args = parser.parse_args()

    engine = EvolutionExecutionFeedbackKGIntegration()

    if args.command == "status":
        result = engine.get_status()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif args.command == "health":
        result = engine.health_check()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif args.command == "analyze":
        result = engine.analyze_execution_trends(args.days)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif args.command == "feedback":
        if not args.execution_id or not args.execution_type:
            print("错误: --execution-id 和 --execution-type 是必需参数")
            return
        result = engine.record_execution_feedback(
            args.execution_id,
            args.execution_type,
            args.success if args.success is not None else True,
            args.result_summary or "",
            args.execution_time or 0
        )
        print(json.dumps({"success": result}, indent=2))
    elif args.command == "optimize":
        result = engine.optimize_trigger_recommendations()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif args.command == "close_loop":
        if not args.execution_id:
            print("错误: --execution-id 是必需参数")
            return
        execution_results = [{
            "execution_id": args.execution_id,
            "execution_type": args.execution_type or "unknown",
            "success": args.success if args.success is not None else True,
            "result_summary": args.result_summary or "",
            "execution_time": args.execution_time or 0,
            "affected_knowledge": args.affected_knowledge or []
        }]
        result = engine.close_loop(args.execution_id, execution_results)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"未知命令: {args.command}")
        parser.print_help()


if __name__ == "__main__":
    main()