"""
智能全场景进化环跨轮次知识积累与复用可视化引擎
====================================================

基于 round 414 的知识驱动递归增强闭环引擎，进一步增强
跨轮次知识积累与复用的可视化能力。

功能：
- 知识积累历史可视化
- 知识复用统计可视化
- 跨轮次知识演进趋势展示
- 知识价值分布热力图
- 知识关联网络可视化

Version: 1.0.0
"""

import json
import os
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import defaultdict

# 确保能导入项目模块
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
import sys
sys.path.insert(0, str(PROJECT_ROOT))


class EvolutionKnowledgeVisualizationEngine:
    """跨轮次知识积累与复用可视化引擎"""

    def __init__(self, project_root: Optional[str] = None):
        self.project_root = Path(project_root) if project_root else PROJECT_ROOT
        self.state_dir = self.project_root / "runtime" / "state"
        self.logs_dir = self.project_root / "runtime" / "logs"

        # 知识图谱数据库路径
        self.kg_db_path = self.state_dir / "knowledge_graph.db"

        # 进化历史数据库路径
        self.evolution_history_path = self.state_dir / "evolution_history.db"

    def get_knowledge_accumulation_history(self, rounds: int = 50) -> Dict[str, Any]:
        """获取跨轮次知识积累历史"""
        history = {
            "rounds": [],
            "knowledge_nodes_added": [],
            "knowledge_edges_added": [],
            "total_knowledge": 0,
            "total_edges": 0
        }

        try:
            if self.evolution_history_path.exists():
                conn = sqlite3.connect(str(self.evolution_history_path))
                cursor = conn.cursor()

                # 获取最近的进化历史
                cursor.execute("""
                    SELECT round_number, created_modules, modified_modules, status
                    FROM evolution_history
                    ORDER BY round_number DESC
                    LIMIT ?
                """, (rounds,))

                rows = cursor.fetchall()
                for row in rows:
                    round_num, created, modified, status = row
                    history["rounds"].append({
                        "round": round_num,
                        "created_modules": created or "",
                        "modified_modules": modified or "",
                        "status": status
                    })

                # 获取知识节点总数趋势
                if self.kg_db_path.exists():
                    kg_conn = sqlite3.connect(str(self.kg_db_path))
                    kg_cursor = kg_conn.cursor()

                    try:
                        # 尝试获取知识节点数量
                        kg_cursor.execute("SELECT COUNT(*) FROM knowledge_nodes")
                        history["total_knowledge"] = kg_cursor.fetchone()[0]

                        kg_cursor.execute("SELECT COUNT(*) FROM knowledge_edges")
                        history["total_edges"] = kg_cursor.fetchone()[0]
                    except:
                        pass

                    kg_conn.close()

                conn.close()
        except Exception as e:
            print(f"获取知识积累历史失败: {e}")

        return history

    def get_knowledge_reuse_statistics(self) -> Dict[str, Any]:
        """获取知识复用统计"""
        stats = {
            "total_reuse_count": 0,
            "top_reused_knowledge": [],
            "reuse_by_category": {},
            "reuse_trend": []
        }

        try:
            if self.kg_db_path.exists():
                conn = sqlite3.connect(str(self.kg_db_path))
                cursor = conn.cursor()

                # 获取知识复用统计表
                try:
                    cursor.execute("""
                        SELECT knowledge_node, usage_count, success_count, computed_value
                        FROM knowledge_value_ranking
                        ORDER BY usage_count DESC
                        LIMIT 20
                    """)

                    rows = cursor.fetchall()
                    stats["total_reuse_count"] = sum(row[1] for row in rows)

                    for row in rows:
                        node, usage, success, value = row
                        stats["top_reused_knowledge"].append({
                            "knowledge_node": node,
                            "usage_count": usage,
                            "success_count": success,
                            "computed_value": value,
                            "success_rate": success / max(usage, 1)
                        })
                except:
                    # 如果表不存在，尝试其他方式
                    pass

                conn.close()
        except Exception as e:
            print(f"获取知识复用统计失败: {e}")

        return stats

    def get_knowledge_evolution_trend(self, rounds: int = 20) -> List[Dict[str, Any]]:
        """获取知识演进趋势"""
        trend = []

        try:
            if self.evolution_history_path.exists():
                conn = sqlite3.connect(str(self.evolution_history_path))
                cursor = conn.cursor()

                # 获取进化历史
                cursor.execute("""
                    SELECT round_number, current_goal, status, created_modules
                    FROM evolution_history
                    ORDER BY round_number DESC
                    LIMIT ?
                """, (rounds,))

                rows = cursor.fetchall()
                for row in rows:
                    round_num, goal, status, created = row

                    # 统计知识相关关键词
                    knowledge_keywords = ["knowledge", "知识", "图谱", "graph",
                                         "learn", "学习", "reasoning", "推理"]
                    has_knowledge = any(kw in str(goal).lower() for kw in knowledge_keywords)

                    trend.append({
                        "round": round_num,
                        "goal": goal,
                        "status": status,
                        "has_knowledge_focus": has_knowledge,
                        "modules_created": len(str(created).split(',')) if created else 0
                    })

                conn.close()
        except Exception as e:
            print(f"获取知识演进趋势失败: {e}")

        return trend

    def get_knowledge_value_distribution(self) -> Dict[str, Any]:
        """获取知识价值分布"""
        distribution = {
            "high_value": [],
            "medium_value": [],
            "low_value": [],
            "value_thresholds": {
                "high": 1.5,
                "medium": 0.8,
                "low": 0.0
            }
        }

        try:
            if self.kg_db_path.exists():
                conn = sqlite3.connect(str(self.kg_db_path))
                cursor = conn.cursor()

                try:
                    cursor.execute("""
                        SELECT knowledge_node, computed_value, usage_count
                        FROM knowledge_value_ranking
                        ORDER BY computed_value DESC
                    """)

                    rows = cursor.fetchall()
                    for row in rows:
                        node, value, usage = row

                        entry = {
                            "knowledge_node": node,
                            "value": value,
                            "usage_count": usage
                        }

                        if value >= distribution["value_thresholds"]["high"]:
                            distribution["high_value"].append(entry)
                        elif value >= distribution["value_thresholds"]["medium"]:
                            distribution["medium_value"].append(entry)
                        else:
                            distribution["low_value"].append(entry)
                except:
                    pass

                conn.close()
        except Exception as e:
            print(f"获取知识价值分布失败: {e}")

        return distribution

    def get_knowledge_correlation_network(self, limit: int = 30) -> Dict[str, Any]:
        """获取知识关联网络"""
        network = {
            "nodes": [],
            "edges": [],
            "communities": []
        }

        try:
            if self.kg_db_path.exists():
                conn = sqlite3.connect(str(self.kg_db_path))
                cursor = conn.cursor()

                # 获取知识节点
                try:
                    cursor.execute("""
                        SELECT DISTINCT knowledge_node
                        FROM knowledge_nodes
                        LIMIT ?
                    """, (limit,))

                    nodes = cursor.fetchall()
                    node_id_map = {}

                    for i, (node,) in enumerate(nodes):
                        node_id_map[node] = i
                        network["nodes"].append({
                            "id": i,
                            "label": node,
                            "size": 10
                        })

                    # 获取边（关联关系）
                    cursor.execute("""
                        SELECT source_node, target_node, relation_type
                        FROM knowledge_edges
                        LIMIT ?
                    """, (limit * 2,))

                    edges = cursor.fetchall()
                    for source, target, rel_type in edges:
                        if source in node_id_map and target in node_id_map:
                            network["edges"].append({
                                "source": node_id_map[source],
                                "target": node_id_map[target],
                                "relation": rel_type
                            })
                except:
                    pass

                conn.close()
        except Exception as e:
            print(f"获取知识关联网络失败: {e}")

        return network

    def generate_visualization_report(self) -> Dict[str, Any]:
        """生成完整的可视化报告"""
        print("=" * 70)
        print("跨轮次知识积累与复用可视化引擎")
        print("=" * 70)

        report = {
            "generated_at": datetime.now().isoformat(),
            "version": "1.0.0"
        }

        # 1. 知识积累历史
        print("\n[1/5] 分析知识积累历史...")
        report["accumulation_history"] = self.get_knowledge_accumulation_history()
        print(f"  - 已有 {report['accumulation_history']['total_knowledge']} 个知识节点")
        print(f"  - 已有 {report['accumulation_history']['total_edges']} 条知识边")

        # 2. 知识复用统计
        print("\n[2/5] 分析知识复用统计...")
        report["reuse_statistics"] = self.get_knowledge_reuse_statistics()
        print(f"  - 总复用次数: {report['reuse_statistics']['total_reuse_count']}")
        print(f"  - 高复用知识项: {len(report['reuse_statistics']['top_reused_knowledge'])}")

        # 3. 知识演进趋势
        print("\n[3/5] 分析知识演进趋势...")
        report["evolution_trend"] = self.get_knowledge_evolution_trend()
        knowledge_focus_rounds = sum(1 for t in report["evolution_trend"] if t.get("has_knowledge_focus"))
        print(f"  - 分析最近 {len(report['evolution_trend'])} 轮")
        print(f"  - 知识焦点轮次: {knowledge_focus_rounds}")

        # 4. 知识价值分布
        print("\n[4/5] 分析知识价值分布...")
        report["value_distribution"] = self.get_knowledge_value_distribution()
        print(f"  - 高价值知识: {len(report['value_distribution']['high_value'])}")
        print(f"  - 中价值知识: {len(report['value_distribution']['medium_value'])}")
        print(f"  - 低价值知识: {len(report['value_distribution']['low_value'])}")

        # 5. 知识关联网络
        print("\n[5/5] 构建知识关联网络...")
        report["correlation_network"] = self.get_knowledge_correlation_network()
        print(f"  - 节点数: {len(report['correlation_network']['nodes'])}")
        print(f"  - 边数: {len(report['correlation_network']['edges'])}")

        print("\n" + "=" * 70)
        print("可视化报告生成完成")
        print("=" * 70)

        return report

    def get_status(self) -> Dict[str, Any]:
        """获取引擎状态"""
        return {
            "status": "running",
            "kg_db_exists": self.kg_db_path.exists(),
            "evolution_history_exists": self.evolution_history_path.exists(),
            "version": "1.0.0"
        }

    def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        result = {
            "healthy": True,
            "checks": {},
            "version": "1.0.0"
        }

        # 检查数据库文件
        if self.kg_db_path.exists():
            result["checks"]["knowledge_db"] = "exists"
        else:
            result["checks"]["knowledge_db"] = "not_found"
            result["healthy"] = False

        if self.evolution_history_path.exists():
            result["checks"]["evolution_history"] = "exists"
        else:
            result["checks"]["evolution_history"] = "not_found"

        return result


def main():
    """主入口"""
    import argparse
    parser = argparse.ArgumentParser(
        description="跨轮次知识积累与复用可视化引擎"
    )
    parser.add_argument(
        'command',
        nargs='?',
        default='report',
        help='命令: report(生成可视化报告), status(状态), health(健康检查), history(历史), trend(趋势)'
    )
    parser.add_argument(
        '--rounds',
        type=int,
        default=20,
        help='分析轮数'
    )

    args = parser.parse_args()

    engine = EvolutionKnowledgeVisualizationEngine()

    if args.command == 'report':
        report = engine.generate_visualization_report()
        print(json.dumps(report, ensure_ascii=False, indent=2))

    elif args.command == 'status':
        status = engine.get_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))

    elif args.command == 'health':
        health = engine.health_check()
        print(f"健康检查: {'通过' if health['healthy'] else '失败'}")
        print(json.dumps(health, ensure_ascii=False, indent=2))

    elif args.command == 'history':
        history = engine.get_knowledge_accumulation_history(rounds=args.rounds)
        print(json.dumps(history, ensure_ascii=False, indent=2))

    elif args.command == 'trend':
        trend = engine.get_knowledge_evolution_trend(rounds=args.rounds)
        print(json.dumps(trend, ensure_ascii=False, indent=2))

    else:
        parser.print_help()


if __name__ == '__main__':
    main()