#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环跨轮次长期学习记忆引擎

在 round 511 完成的决策执行结果学习与深度优化引擎基础上，进一步增强跨轮次的长期学习记忆能力。
让系统能够：
1. 长期记忆存储 - 持久化存储跨轮次的关键学习成果
2. 跨轮次数据收集 - 自动从历史进化中提取学习数据
3. 记忆检索与复用 - 基于上下文智能检索和复用历史学习成果
4. 学习效果评估 - 评估记忆复用的效果并持续优化

版本：1.0.0
依赖：round 511 evolution_decision_learning_optimizer_engine.py
"""

import os
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
import hashlib


class EvolutionLongTermLearningMemoryEngine:
    """跨轮次长期学习记忆引擎"""

    VERSION = "1.0.0"

    def __init__(self, base_dir: str = None):
        if base_dir is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        self.base_dir = Path(base_dir)
        self.runtime_dir = self.base_dir.parent / "runtime"
        self.state_dir = self.runtime_dir / "state"
        self.data_dir = self.runtime_dir / "learning_data"
        self.data_dir.mkdir(exist_ok=True)

        # 数据库路径
        self.db_path = self.data_dir / "long_term_memory.db"
        self._init_database()

    def _init_database(self):
        """初始化数据库"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # 创建记忆表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS long_term_memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                memory_type TEXT NOT NULL,
                key_data TEXT NOT NULL,
                value_data TEXT NOT NULL,
                context_json TEXT,
                importance_score REAL DEFAULT 0.5,
                access_count INTEGER DEFAULT 0,
                last_accessed TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                tags TEXT,
                source_round INTEGER,
                effectiveness_score REAL DEFAULT 0.0
            )
        """)

        # 创建学习模式表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS learning_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_type TEXT NOT NULL,
                pattern_data TEXT NOT NULL,
                success_count INTEGER DEFAULT 0,
                failure_count INTEGER DEFAULT 0,
                success_rate REAL DEFAULT 0.0,
                last_validated TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                applicability_context TEXT
            )
        """)

        # 创建记忆检索历史表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS retrieval_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT NOT NULL,
                retrieved_memory_ids TEXT,
                selected_memory_id INTEGER,
                reuse_success BOOLEAN,
                retrieval_time TEXT NOT NULL,
                context_json TEXT
            )
        """)

        # 创建跨轮次学习记录表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cross_round_learning (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                round_from INTEGER NOT NULL,
                round_to INTEGER NOT NULL,
                learning_type TEXT NOT NULL,
                learning_data TEXT NOT NULL,
                applied_success BOOLEAN,
                applied_at TEXT,
                effectiveness REAL DEFAULT 0.0,
                notes TEXT,
                created_at TEXT NOT NULL
            )
        """)

        conn.commit()
        conn.close()

    def add_memory(self, memory_type: str, key_data: str, value_data: Any,
                   context: Dict = None, importance: float = 0.5,
                   tags: List[str] = None, source_round: int = None) -> int:
        """添加长期记忆"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        now = datetime.now().isoformat()
        context_json = json.dumps(context) if context else None
        tags_str = json.dumps(tags) if tags else None

        cursor.execute("""
            INSERT INTO long_term_memories
            (memory_type, key_data, value_data, context_json, importance_score,
             last_accessed, created_at, updated_at, tags, source_round)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (memory_type, key_data, json.dumps(value_data), context_json,
              importance, now, now, now, tags_str, source_round))

        memory_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return memory_id

    def retrieve_memories(self, query: str = None, memory_type: str = None,
                          tags: List[str] = None, limit: int = 10,
                          min_importance: float = 0.0) -> List[Dict]:
        """检索记忆"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        conditions = []
        params = []

        if query:
            conditions.append("(key_data LIKE ? OR value_data LIKE ?)")
            params.extend([f"%{query}%", f"%{query}%"])

        if memory_type:
            conditions.append("memory_type = ?")
            params.append(memory_type)

        if tags:
            for tag in tags:
                conditions.append("tags LIKE ?")
                params.append(f"%\"{tag}\"%")

        if min_importance > 0:
            conditions.append("importance_score >= ?")
            params.append(min_importance)

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        cursor.execute(f"""
            SELECT * FROM long_term_memories
            WHERE {where_clause}
            ORDER BY importance_score DESC, access_count DESC
            LIMIT ?
        """, params + [limit])

        results = []
        for row in cursor.fetchall():
            memory = dict(row)
            if memory.get('context_json'):
                memory['context'] = json.loads(memory['context_json'])
            if memory.get('tags'):
                memory['tags'] = json.loads(memory['tags'])
            if memory.get('value_data'):
                memory['value_data'] = json.loads(memory['value_data'])
            results.append(memory)

        # 更新访问计数
        for mem in results:
            cursor.execute("""
                UPDATE long_term_memories
                SET access_count = access_count + 1, last_accessed = ?
                WHERE id = ?
            """, (datetime.now().isoformat(), mem['id']))

        conn.commit()
        conn.close()
        return results

    def update_memory_effectiveness(self, memory_id: int, effectiveness: float):
        """更新记忆效果评分"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE long_term_memories
            SET effectiveness_score = ?, updated_at = ?
            WHERE id = ?
        """, (effectiveness, datetime.now().isoformat(), memory_id))

        conn.commit()
        conn.close()

    def add_learning_pattern(self, pattern_type: str, pattern_data: Any,
                             success_count: int = 0, failure_count: int = 0,
                             applicability_context: str = None) -> int:
        """添加学习模式"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        now = datetime.now().isoformat()
        success_rate = success_count / (success_count + failure_count) if (success_count + failure_count) > 0 else 0.0

        cursor.execute("""
            INSERT INTO learning_patterns
            (pattern_type, pattern_data, success_count, failure_count,
             success_rate, last_validated, created_at, updated_at, applicability_context)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (pattern_type, json.dumps(pattern_data), success_count, failure_count,
              success_rate, now, now, now, applicability_context))

        pattern_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return pattern_id

    def get_relevant_patterns(self, context: str = None, pattern_type: str = None,
                               min_success_rate: float = 0.5, limit: int = 10) -> List[Dict]:
        """获取相关学习模式"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        conditions = []
        params = []

        if context:
            conditions.append("applicability_context LIKE ?")
            params.append(f"%{context}%")

        if pattern_type:
            conditions.append("pattern_type = ?")
            params.append(pattern_type)

        if min_success_rate > 0:
            conditions.append("success_rate >= ?")
            params.append(min_success_rate)

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        cursor.execute(f"""
            SELECT * FROM learning_patterns
            WHERE {where_clause}
            ORDER BY success_rate DESC, success_count DESC
            LIMIT ?
        """, params + [limit])

        results = []
        for row in cursor.fetchall():
            pattern = dict(row)
            pattern['pattern_data'] = json.loads(pattern['pattern_data'])
            results.append(pattern)

        conn.close()
        return results

    def update_pattern_success(self, pattern_id: int, success: bool):
        """更新模式成功/失败计数"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        if success:
            cursor.execute("""
                UPDATE learning_patterns
                SET success_count = success_count + 1,
                    success_rate = CAST(success_count + 1 AS REAL) / (success_count + failure_count + 1),
                    last_validated = ?, updated_at = ?
                WHERE id = ?
            """, (datetime.now().isoformat(), datetime.now().isoformat(), pattern_id))
        else:
            cursor.execute("""
                UPDATE learning_patterns
                SET failure_count = failure_count + 1,
                    success_rate = CAST(success_count AS REAL) / (success_count + failure_count + 1),
                    last_validated = ?, updated_at = ?
                WHERE id = ?
            """, (datetime.now().isoformat(), datetime.now().isoformat(), pattern_id))

        conn.commit()
        conn.close()

    def record_cross_round_learning(self, round_from: int, round_to: int,
                                      learning_type: str, learning_data: Any,
                                      notes: str = None) -> int:
        """记录跨轮次学习"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO cross_round_learning
            (round_from, round_to, learning_type, learning_data, applied_success, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (round_from, round_to, learning_type, json.dumps(learning_data),
              None, datetime.now().isoformat()))

        record_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return record_id

    def get_cross_round_learning(self, round_from: int = None,
                                  round_to: int = None,
                                  learning_type: str = None) -> List[Dict]:
        """获取跨轮次学习记录"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        conditions = []
        params = []

        if round_from is not None:
            conditions.append("round_from >= ?")
            params.append(round_from)

        if round_to is not None:
            conditions.append("round_to <= ?")
            params.append(round_to)

        if learning_type:
            conditions.append("learning_type = ?")
            params.append(learning_type)

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        cursor.execute(f"""
            SELECT * FROM cross_round_learning
            WHERE {where_clause}
            ORDER BY round_from DESC, round_to DESC
            LIMIT 50
        """, params)

        results = []
        for row in cursor.fetchall():
            record = dict(row)
            record['learning_data'] = json.loads(record['learning_data'])
            results.append(record)

        conn.close()
        return results

    def apply_cross_round_learning(self, record_id: int, applied_success: bool,
                                    effectiveness: float = 0.0):
        """应用跨轮次学习结果"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE cross_round_learning
            SET applied_success = ?, applied_at = ?, effectiveness = ?
            WHERE id = ?
        """, (applied_success, datetime.now().isoformat(), effectiveness, record_id))

        conn.commit()
        conn.close()

    def collect_learning_data_from_history(self, recent_rounds: int = 20) -> Dict:
        """从历史进化中收集学习数据"""
        learning_data = {
            "decision_patterns": [],
            "execution_patterns": [],
            "success_strategies": [],
            "failure_patterns": [],
            "round_insights": []
        }

        # 从 evolution_completed_*.json 文件中收集
        state_dir = self.state_dir
        if not state_dir.exists():
            return learning_data

        completed_files = sorted(state_dir.glob("evolution_completed_ev_*.json"),
                                 key=lambda x: x.stat().st_mtime,
                                 reverse=True)[:recent_rounds]

        for file_path in completed_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                    # 提取决策模式
                    if data.get('current_goal'):
                        learning_data["decision_patterns"].append({
                            "goal": data['current_goal'],
                            "completed": data.get('是否完成', '') == '已完成',
                            "round": data.get('loop_round', 0)
                        })

                    # 提取成功策略
                    if data.get('是否完成') == '已完成':
                        learning_data["success_strategies"].append({
                            "goal": data.get('current_goal', ''),
                            "affected_files": data.get('affected_files', []),
                            "round": data.get('loop_round', 0)
                        })

                    # 记录轮次洞察
                    if data.get('下一轮建议'):
                        learning_data["round_insights"].append({
                            "insight": data.get('下一轮建议', ''),
                            "round": data.get('loop_round', 0)
                        })

            except Exception as e:
                continue

        return learning_data

    def extract_and_store_memories(self, recent_rounds: int = 20):
        """从历史数据中提取并存储重要记忆"""
        learning_data = self.collect_learning_data_from_history(recent_rounds)

        # 存储成功策略
        for strategy in learning_data.get("success_strategies", []):
            if strategy.get("completed"):
                self.add_memory(
                    memory_type="success_strategy",
                    key_data=strategy.get("goal", ""),
                    value_data={
                        "strategy": strategy.get("goal", ""),
                        "affected_files": strategy.get("affected_files", []),
                        "reusable_aspects": "goal_achieving_approach"
                    },
                    context={"round": strategy.get("round", 0)},
                    importance=0.8,
                    tags=["strategy", "success", f"round_{strategy.get('round', 0)}"],
                    source_round=strategy.get("round", 0)
                )

        # 存储洞察
        for insight in learning_data.get("round_insights", []):
            if insight.get("insight"):
                self.add_memory(
                    memory_type="round_insight",
                    key_data=insight.get("insight", "")[:100],
                    value_data={"insight": insight.get("insight", "")},
                    context={"round": insight.get("round", 0)},
                    importance=0.6,
                    tags=["insight", "round_insight"],
                    source_round=insight.get("round", 0)
                )

    def get_memory_statistics(self) -> Dict:
        """获取记忆统计信息"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # 记忆数量统计
        cursor.execute("SELECT memory_type, COUNT(*) as count FROM long_term_memories GROUP BY memory_type")
        memory_counts = {row[0]: row[1] for row in cursor.fetchall()}

        # 模式数量统计
        cursor.execute("SELECT pattern_type, COUNT(*) as count, AVG(success_rate) as avg_rate FROM learning_patterns GROUP BY pattern_type")
        pattern_stats = {row[0]: {"count": row[1], "avg_success_rate": row[2]} for row in cursor.fetchall()}

        # 跨轮次学习记录数
        cursor.execute("SELECT COUNT(*) FROM cross_round_learning")
        cross_round_count = cursor.fetchone()[0]

        # 检索历史数
        cursor.execute("SELECT COUNT(*) FROM retrieval_history")
        retrieval_count = cursor.fetchone()[0]

        conn.close()

        return {
            "memory_counts": memory_counts,
            "pattern_stats": pattern_stats,
            "cross_round_learning_count": cross_round_count,
            "retrieval_count": retrieval_count,
            "version": self.VERSION
        }

    def get_cockpit_data(self) -> Dict:
        """获取驾驶舱数据接口"""
        stats = self.get_memory_statistics()

        # 获取最近的记忆
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM long_term_memories
            ORDER BY importance_score DESC, access_count DESC
            LIMIT 10
        """)
        recent_memories = [dict(row) for row in cursor.fetchall()]

        # 获取高效模式
        cursor.execute("""
            SELECT * FROM learning_patterns
            WHERE success_rate >= 0.7
            ORDER BY success_count DESC
            LIMIT 10
        """)
        high_performing_patterns = [dict(row) for row in cursor.fetchall()]

        conn.close()

        return {
            "engine_name": "跨轮次长期学习记忆引擎",
            "version": self.VERSION,
            "statistics": stats,
            "recent_memories": recent_memories,
            "high_performing_patterns": high_performing_patterns,
            "last_updated": datetime.now().isoformat()
        }

    def run_full_cycle(self):
        """运行完整的学习记忆周期"""
        print("=== 跨轮次长期学习记忆引擎 v{} ===".format(self.VERSION))

        # 1. 收集学习数据
        print("\n[1/4] 从历史进化中收集学习数据...")
        learning_data = self.collect_learning_data_from_history(20)
        print(f"  - 决策模式: {len(learning_data.get('decision_patterns', []))}")
        print(f"  - 成功策略: {len(learning_data.get('success_strategies', []))}")
        print(f"  - 轮次洞察: {len(learning_data.get('round_insights', []))}")

        # 2. 提取并存储记忆
        print("\n[2/4] 提取并存储重要记忆...")
        self.extract_and_store_memories(20)
        print("  - 记忆提取完成")

        # 3. 获取统计信息
        print("\n[3/4] 记忆统计信息...")
        stats = self.get_memory_statistics()
        print(f"  - 总记忆数: {sum(stats['memory_counts'].values())}")
        print(f"  - 学习模式数: {sum(stats['pattern_stats'].values())}")
        print(f"  - 跨轮次学习记录: {stats['cross_round_learning_count']}")

        # 4. 检索测试
        print("\n[4/4] 记忆检索测试...")
        test_memories = self.retrieve_memories(limit=5)
        print(f"  - 检索到 {len(test_memories)} 条相关记忆")

        print("\n=== 完整周期执行完成 ===")
        return True

    def show_status(self):
        """显示状态信息"""
        stats = self.get_memory_statistics()
        print("\n=== 跨轮次长期学习记忆引擎状态 ===")
        print(f"版本: {stats['version']}")
        print(f"\n记忆统计:")
        for mem_type, count in stats['memory_counts'].items():
            print(f"  - {mem_type}: {count}")

        print(f"\n学习模式:")
        for pattern_type, info in stats['pattern_stats'].items():
            print(f"  - {pattern_type}: {info['count']}个 (平均成功率: {info['avg_success_rate']:.1%})")

        print(f"\n跨轮次学习记录: {stats['cross_round_learning_count']}")
        print(f"检索历史: {stats['retrieval_count']}")
        print("=" * 40)


def main():
    """主入口"""
    import argparse

    parser = argparse.ArgumentParser(description="智能全场景进化环跨轮次长期学习记忆引擎")
    parser.add_argument("--status", action="store_true", help="显示状态信息")
    parser.add_argument("--collect", action="store_true", help="收集学习数据")
    parser.add_argument("--store", action="store_true", help="提取并存储记忆")
    parser.add_argument("--retrieve", type=str, help="检索记忆（传入查询词）")
    parser.add_argument("--full-cycle", action="store_true", help="运行完整周期")
    parser.add_argument("--cockpit-data", action="store_true", help="获取驾驶舱数据")
    parser.add_argument("--patterns", type=str, help="获取相关模式（传入上下文）")

    args = parser.parse_args()

    engine = EvolutionLongTermLearningMemoryEngine()

    if args.status:
        engine.show_status()
    elif args.collect:
        data = engine.collect_learning_data_from_history(20)
        print(json.dumps(data, indent=2, ensure_ascii=False))
    elif args.store:
        engine.extract_and_store_memories(20)
        print("记忆提取并存储完成")
    elif args.retrieve:
        results = engine.retrieve_memories(query=args.retrieve, limit=10)
        print(f"检索到 {len(results)} 条记忆:")
        for r in results:
            print(f"  - [{r['memory_type']}] {r['key_data']} (importance: {r['importance_score']:.2f})")
    elif args.full_cycle:
        engine.run_full_cycle()
    elif args.cockpit_data:
        data = engine.get_cockpit_data()
        print(json.dumps(data, indent=2, ensure_ascii=False))
    elif args.patterns:
        patterns = engine.get_relevant_patterns(context=args.patterns, limit=10)
        print(f"找到 {len(patterns)} 个相关模式:")
        for p in patterns:
            print(f"  - [{p['pattern_type']}] 成功率: {p['success_rate']:.1%}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()