#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环跨轮次学习记忆深度增强引擎

在 round 512 完成的长期学习记忆引擎基础上，进一步增强跨轮次的学习记忆能力：
1. 跨时间窗口知识整合 - 跨月/季/年的学习成果聚合
2. 记忆衰减与强化机制 - 重要知识强化，过时知识淡化
3. 记忆检索与复用机制增强 - 基于当前上下文智能检索

版本：1.0.0
依赖：round 512 evolution_long_term_learning_memory_engine.py
"""

import os
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
import hashlib


class EvolutionCrossRoundLearningMemoryEngine:
    """跨轮次学习记忆深度增强引擎"""

    VERSION = "1.0.0"

    def __init__(self, base_dir: str = None):
        if base_dir is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        self.base_dir = Path(base_dir)
        self.runtime_dir = self.base_dir.parent / "runtime"
        self.state_dir = self.runtime_dir / "state"
        self.data_dir = self.runtime_dir / "learning_data"
        self.data_dir.mkdir(exist_ok=True)

        # 数据库路径 - 复用或创建新的增强数据库
        self.db_path = self.data_dir / "cross_round_learning_enhanced.db"
        self.legacy_db_path = self.data_dir / "long_term_memory.db"
        self._init_database()

    def _init_database(self):
        """初始化增强版数据库"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # 创建增强记忆表 - 添加时间窗口字段
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS enhanced_memories (
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
                effectiveness_score REAL DEFAULT 0.0,
                time_window TEXT DEFAULT 'short',  -- short/medium/long
                decay_factor REAL DEFAULT 1.0,     -- 衰减因子
                reinforcement_count INTEGER DEFAULT 0  -- 强化次数
            )
        """)

        # 创建时间窗口聚合表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS time_window_aggregation (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                window_type TEXT NOT NULL,  -- monthly/quarterly/yearly
                window_start TEXT NOT NULL,
                window_end TEXT NOT NULL,
                aggregated_data TEXT NOT NULL,
                summary_json TEXT,
                created_at TEXT NOT NULL
            )
        """)

        # 创建记忆衰减记录表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memory_decay_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                memory_id INTEGER NOT NULL,
                decay_type TEXT NOT NULL,  -- time_based/context_based/reinforcement
                old_value REAL,
                new_value REAL,
                reason TEXT,
                created_at TEXT NOT NULL
            )
        """)

        # 创建上下文感知检索表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS context_aware_retrieval (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query_context TEXT NOT NULL,
                retrieved_memory_ids TEXT,
                relevance_scores TEXT,
                retrieval_time TEXT NOT NULL,
                context_match_score REAL DEFAULT 0.0
            )
        """)

        # 创建知识整合记录表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS knowledge_integration (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                integration_type TEXT NOT NULL,  -- cross_time/cross_domain/cross_task
                source_memories TEXT NOT NULL,
                integrated_knowledge TEXT NOT NULL,
                integration_method TEXT,
                effectiveness REAL DEFAULT 0.0,
                created_at TEXT NOT NULL
            )
        """)

        conn.commit()
        conn.close()

    def add_enhanced_memory(self, memory_type: str, key_data: str, value_data: Any,
                            context: Dict = None, importance: float = 0.5,
                            tags: List[str] = None, source_round: int = None,
                            time_window: str = 'short') -> int:
        """添加增强记忆"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        now = datetime.now().isoformat()
        context_json = json.dumps(context) if context else None
        tags_str = json.dumps(tags) if tags else None

        cursor.execute("""
            INSERT INTO enhanced_memories
            (memory_type, key_data, value_data, context_json, importance_score,
             last_accessed, created_at, updated_at, tags, source_round, time_window, decay_factor)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (memory_type, key_data, json.dumps(value_data), context_json,
              importance, now, now, now, tags_str, source_round, time_window, 1.0))

        memory_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return memory_id

    def apply_memory_decay(self, dry_run: bool = False) -> Dict:
        """应用记忆衰减机制 - 重要知识强化，过时知识淡化"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # 计算当前时间
        now = datetime.now()

        # 定义时间窗口阈值
        short_term_days = 30    # 短期记忆
        medium_term_days = 90   # 中期记忆
        long_term_days = 180    # 长期记忆

        # 获取所有记忆进行衰减计算
        cursor.execute("SELECT * FROM enhanced_memories")
        memories = cursor.fetchall()

        decay_log = []
        for mem in memories:
            mem_dict = dict(mem)
            memory_id = mem_dict.get('id')
            created_at_str = mem_dict.get('created_at', '')
            try:
                created_at = datetime.fromisoformat(created_at_str)
                days_since_created = (now - created_at).days
            except:
                days_since_created = 0
                created_at = now

            access_count = mem_dict.get('access_count', 0)
            importance = mem_dict.get('importance_score', 0.5)
            reinforcement_count = mem_dict.get('reinforcement_count', 0)
            old_decay = mem_dict.get('decay_factor', 1.0)

            # 基于时间的衰减因子
            if days_since_created < short_term_days:
                time_decay = 1.0  # 不衰减
            elif days_since_created < medium_term_days:
                time_decay = max(0.7, 1.0 - (days_since_created - short_term_days) / (medium_term_days - short_term_days) * 0.2)
            elif days_since_created < long_term_days:
                time_decay = max(0.5, 0.7 - (days_since_created - medium_term_days) / (long_term_days - medium_term_days) * 0.2)
            else:
                time_decay = max(0.3, 0.5 - (days_since_created - long_term_days) * 0.01)

            # 访问频率强化因子
            access_boost = min(1.3, 1.0 + access_count * 0.05)

            # 强化次数强化因子
            reinforcement_boost = min(1.5, 1.0 + reinforcement_count * 0.1)

            # 综合衰减因子
            new_decay_factor = time_decay * access_boost * reinforcement_boost

            if not dry_run and new_decay_factor != old_decay:
                cursor.execute("""
                    UPDATE enhanced_memories
                    SET decay_factor = ?, updated_at = ?
                    WHERE id = ?
                """, (new_decay_factor, now.isoformat(), memory_id))

                decay_log.append({
                    "memory_id": memory_id,
                    "old_factor": old_decay,
                    "new_factor": new_decay_factor,
                    "days_since_created": days_since_created
                })

                # 记录衰减日志
                cursor.execute("""
                    INSERT INTO memory_decay_log
                    (memory_id, decay_type, old_value, new_value, reason, created_at)
                    VALUES (?, 'time_based', ?, ?, ?, ?)
                """, (memory_id, old_decay, new_decay_factor,
                      f"days={days_since_created}, access={access_count}, reinforce={reinforcement_count}",
                      now.isoformat()))

        conn.commit()
        conn.close()

        return {
            "status": "completed",
            "decayed_count": len(decay_log),
            "details": decay_log[:10]  # 返回前10条详情
        }

    def reinforce_memory(self, memory_id: int, success: bool = True):
        """强化记忆 - 重要知识强化"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        if success:
            cursor.execute("""
                UPDATE enhanced_memories
                SET reinforcement_count = reinforcement_count + 1,
                    importance_score = MIN(1.0, importance_score + 0.05),
                    decay_factor = MIN(1.5, decay_factor + 0.1),
                    updated_at = ?
                WHERE id = ?
            """, (datetime.now().isoformat(), memory_id))
        else:
            cursor.execute("""
                UPDATE enhanced_memories
                SET reinforcement_count = MAX(0, reinforcement_count - 1),
                    importance_score = MAX(0.1, importance_score - 0.02),
                    decay_factor = MAX(0.3, decay_factor - 0.05),
                    updated_at = ?
                WHERE id = ?
            """, (datetime.now().isoformat(), memory_id))

        # 记录强化日志
        cursor.execute("""
            INSERT INTO memory_decay_log
            (memory_id, decay_type, old_value, new_value, reason, created_at)
            VALUES (?, 'reinforcement', ?, ?, ?, ?)
        """, (memory_id, 1.0 if success else 0.0, 1.0 if success else 0.0,
              "success" if success else "failure", datetime.now().isoformat()))

        conn.commit()
        conn.close()

    def time_window_aggregation(self, window_type: str = 'monthly') -> Dict:
        """跨时间窗口知识整合"""
        if not self.legacy_db_path.exists():
            return {"status": "no_data", "aggregated_count": 0}

        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        now = datetime.now()

        # 计算时间窗口边界
        if window_type == 'monthly':
            window_delta = timedelta(days=30)
            start_date = now - timedelta(days=90)  # 过去3个月
        elif window_type == 'quarterly':
            window_delta = timedelta(days=90)
            start_date = now - timedelta(days=270)  # 过去9个月
        elif window_type == 'yearly':
            window_delta = timedelta(days=365)
            start_date = now - timedelta(days=730)  # 过去2年
        else:
            window_type = 'monthly'
            window_delta = timedelta(days=30)
            start_date = now - timedelta(days=90)

        # 按时间窗口聚合
        window_data = {}
        current_start = start_date

        while current_start < now:
            window_end = current_start + window_delta

            # 查询该窗口内的记忆
            cursor.execute("""
                SELECT * FROM enhanced_memories
                WHERE created_at >= ? AND created_at < ?
                ORDER BY importance_score DESC
            """, (current_start.isoformat(), window_end.isoformat()))

            memories = []
            for row in cursor.fetchall():
                memory = dict(row)
                memory['value_data'] = json.loads(memory['value_data'])
                memories.append(memory)

            if memories:
                window_key = f"{window_type}_{current_start.strftime('%Y%m%d')}"
                window_data[window_key] = {
                    "start": current_start.isoformat(),
                    "end": window_end.isoformat(),
                    "memory_count": len(memories),
                    "top_memories": [m['key_data'][:50] for m in memories[:5]],
                    "avg_importance": sum(m['importance_score'] for m in memories) / len(memories) if memories else 0
                }

            current_start = window_end

        # 存储聚合结果
        cursor.execute("""
            INSERT INTO time_window_aggregation
            (window_type, window_start, window_end, aggregated_data, summary_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (window_type, start_date.isoformat(), now.isoformat(),
              json.dumps(window_data), json.dumps({"window_type": window_type}), now.isoformat()))

        conn.commit()
        conn.close()

        return {
            "status": "completed",
            "window_type": window_type,
            "window_count": len(window_data),
            "windows": window_data
        }

    def get_context_aware_retrieval(self, query: str, context: Dict = None,
                                     limit: int = 10) -> List[Dict]:
        """基于上下文的智能检索"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # 基础关键词检索
        conditions = []
        params = []

        if query:
            conditions.append("(key_data LIKE ? OR value_data LIKE ?)")
            params.extend([f"%{query}%", f"%{query}%"])

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        cursor.execute(f"""
            SELECT * FROM enhanced_memories
            WHERE {where_clause}
            ORDER BY importance_score * decay_factor DESC, access_count DESC
            LIMIT ?
        """, params + [limit * 2])  # 获取更多候选

        candidates = []
        for row in cursor.fetchall():
            memory = dict(row)
            memory['value_data'] = json.loads(memory['value_data'])
            if memory.get('context_json'):
                memory['context'] = json.loads(memory['context_json'])

            # 计算上下文相关性得分
            context_score = 0.0
            if context:
                # 检查记忆的上下文与当前上下文是否匹配
                mem_context = memory.get('context', {})
                for key, value in context.items():
                    if key in mem_context and mem_context[key] == value:
                        context_score += 1.0
                    elif key in str(mem_context):
                        context_score += 0.5

            # 综合得分 = 重要性 * 衰减因子 * 上下文相关性
            final_score = (memory.get('importance_score', 0.5) *
                          memory.get('decay_factor', 1.0) *
                          (1.0 + context_score * 0.2))

            memory['context_score'] = context_score
            memory['final_score'] = final_score
            candidates.append(memory)

        # 按最终得分排序
        candidates.sort(key=lambda x: x.get('final_score', 0), reverse=True)

        # 更新访问计数
        for mem in candidates[:limit]:
            cursor.execute("""
                UPDATE enhanced_memories
                SET access_count = access_count + 1, last_accessed = ?
                WHERE id = ?
            """, (datetime.now().isoformat(), mem['id']))

            # 记录检索历史
            cursor.execute("""
                INSERT INTO context_aware_retrieval
                (query_context, retrieved_memory_ids, relevance_scores, retrieval_time, context_match_score)
                VALUES (?, ?, ?, ?, ?)
            """, (query, json.dumps([mem['id'] for mem in candidates[:limit]]),
                  json.dumps([c.get('context_score', 0) for c in candidates[:limit]]),
                  datetime.now().isoformat(), context_score if context else 0.0))

        conn.commit()
        conn.close()

        return candidates[:limit]

    def integrate_cross_window_knowledge(self) -> Dict:
        """跨时间窗口知识整合"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # 获取不同时间窗口的高价值记忆
        cursor.execute("""
            SELECT * FROM enhanced_memories
            WHERE importance_score * decay_factor > 0.6
            ORDER BY created_at DESC
            LIMIT 100
        """)

        memories = []
        for row in cursor.fetchall():
            memory = dict(row)
            memory['value_data'] = json.loads(memory['value_data'])
            if memory.get('context_json'):
                memory['context'] = json.loads(memory['context_json'])
            memories.append(memory)

        # 识别可整合的知识模式
        integration_results = {
            "cross_time": [],
            "cross_domain": [],
            "cross_task": []
        }

        # 基于时间窗口的整合
        by_time = defaultdict(list)
        for mem in memories:
            created = datetime.fromisoformat(mem['created_at'])
            window = f"month_{created.strftime('%Y%m')}"
            by_time[window].append(mem)

        for window, window_memories in by_time.items():
            if len(window_memories) >= 3:
                # 发现跨月重复模式
                integration_results["cross_time"].append({
                    "window": window,
                    "pattern_count": len(window_memories),
                    "key_themes": list(set(m.get('memory_type', '') for m in window_memories))
                })

        # 基于域的整合
        by_domain = defaultdict(list)
        for mem in memories:
            mem_type = mem.get('memory_type', 'unknown')
            by_domain[mem_type].append(mem)

        for domain, domain_memories in by_domain.items():
            if len(domain_memories) >= 5:
                integration_results["cross_domain"].append({
                    "domain": domain,
                    "memory_count": len(domain_memories),
                    "top_keys": [m['key_data'][:50] for m in domain_memories[:3]]
                })

        # 记录整合结果
        cursor.execute("""
            INSERT INTO knowledge_integration
            (integration_type, source_memories, integrated_knowledge, integration_method, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, ("cross_window", json.dumps(list(by_time.keys())),
              json.dumps(integration_results), "time_window_clustering", datetime.now().isoformat()))

        conn.commit()
        conn.close()

        return {
            "status": "completed",
            "integrations": integration_results,
            "total_memories_processed": len(memories)
        }

    def get_enhanced_statistics(self) -> Dict:
        """获取增强版统计信息"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # 增强记忆统计
        cursor.execute("""
            SELECT memory_type, COUNT(*) as count,
                   AVG(importance_score) as avg_importance,
                   AVG(decay_factor) as avg_decay,
                   SUM(reinforcement_count) as total_reinforcement
            FROM enhanced_memories
            GROUP BY memory_type
        """)
        memory_stats = {}
        for row in cursor.fetchall():
            memory_stats[row[0]] = {
                "count": row[1],
                "avg_importance": row[2] or 0,
                "avg_decay": row[3] or 1.0,
                "total_reinforcement": row[4] or 0
            }

        # 时间窗口聚合数
        cursor.execute("SELECT COUNT(DISTINCT window_type) FROM time_window_aggregation")
        window_types = cursor.fetchone()[0]

        # 衰减日志数
        cursor.execute("SELECT COUNT(*) FROM memory_decay_log")
        decay_count = cursor.fetchone()[0]

        # 知识整合数
        cursor.execute("SELECT COUNT(*) FROM knowledge_integration")
        integration_count = cursor.fetchone()[0]

        # 上下文感知检索数
        cursor.execute("SELECT COUNT(*) FROM context_aware_retrieval")
        retrieval_count = cursor.fetchone()[0]

        conn.close()

        return {
            "version": self.VERSION,
            "memory_stats": memory_stats,
            "window_types_aggregated": window_types,
            "decay_operations": decay_count,
            "knowledge_integrations": integration_count,
            "context_aware_retrievals": retrieval_count
        }

    def get_cockpit_data(self) -> Dict:
        """获取驾驶舱数据接口"""
        stats = self.get_enhanced_statistics()

        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # 获取高价值记忆
        cursor.execute("""
            SELECT * FROM enhanced_memories
            ORDER BY importance_score * decay_factor DESC
            LIMIT 10
        """)
        top_memories = []
        for row in cursor.fetchall():
            memory = dict(row)
            memory['value_data'] = json.loads(memory['value_data'])
            top_memories.append(memory)

        # 获取最近强化记忆
        cursor.execute("""
            SELECT * FROM enhanced_memories
            WHERE reinforcement_count > 0
            ORDER BY reinforcement_count DESC
            LIMIT 5
        """)
        reinforced_memories = [dict(row) for row in cursor.fetchall()]

        conn.close()

        return {
            "engine_name": "跨轮次学习记忆深度增强引擎",
            "version": self.VERSION,
            "statistics": stats,
            "top_memories": top_memories,
            "reinforced_memories": reinforced_memories,
            "last_updated": datetime.now().isoformat()
        }

    def run_full_cycle(self):
        """运行完整的增强学习记忆周期"""
        print("=== 跨轮次学习记忆深度增强引擎 v{} ===".format(self.VERSION))

        # 1. 应用记忆衰减机制
        print("\n[1/5] 应用记忆衰减与强化机制...")
        decay_result = self.apply_memory_decay()
        print(f"  - 衰减操作完成: {decay_result.get('decayed_count', 0)} 条记忆已处理")

        # 2. 跨时间窗口知识整合
        print("\n[2/5] 跨时间窗口知识整合...")
        monthly_agg = self.time_window_aggregation('monthly')
        print(f"  - 月度聚合: {monthly_agg.get('window_count', 0)} 个窗口")

        # 3. 跨窗口知识整合
        print("\n[3/5] 跨窗口知识整合...")
        integration = self.integrate_cross_window_knowledge()
        print(f"  - 知识整合完成: 处理 {integration.get('total_memories_processed', 0)} 条记忆")

        # 4. 上下文感知检索测试
        print("\n[4/5] 上下文感知检索测试...")
        test_results = self.get_context_aware_retrieval("学习", context={"round": 500}, limit=5)
        print(f"  - 检索到 {len(test_results)} 条相关记忆")

        # 5. 获取统计信息
        print("\n[5/5] 增强统计信息...")
        stats = self.get_enhanced_statistics()
        print(f"  - 记忆类型数: {len(stats['memory_stats'])}")
        print(f"  - 衰减操作数: {stats['decay_operations']}")
        print(f"  - 知识整合数: {stats['knowledge_integrations']}")

        print("\n=== 完整周期执行完成 ===")
        return True

    def migrate_from_legacy(self):
        """从旧版数据库迁移数据"""
        if not self.legacy_db_path.exists():
            print("未找到旧版数据库，跳过迁移")
            return {"status": "skipped", "migrated": 0}

        print("开始从旧版数据库迁移数据...")

        # 读取旧版数据
        legacy_conn = sqlite3.connect(str(self.legacy_db_path))
        legacy_conn.row_factory = sqlite3.Row
        legacy_cursor = legacy_conn.cursor()

        # 迁移长期记忆
        legacy_cursor.execute("SELECT * FROM long_term_memories")
        legacy_memories = legacy_cursor.fetchall()

        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        migrated_count = 0
        for mem in legacy_memories:
            mem_dict = dict(mem)
            # 判断时间窗口类型
            created_at_str = mem_dict.get('created_at', '')
            if created_at_str:
                try:
                    created_at = datetime.fromisoformat(created_at_str)
                    days_since = (datetime.now() - created_at).days
                except:
                    days_since = 0
            else:
                days_since = 0

            if days_since < 30:
                time_window = 'short'
            elif days_since < 90:
                time_window = 'medium'
            else:
                time_window = 'long'

            cursor.execute("""
                INSERT INTO enhanced_memories
                (memory_type, key_data, value_data, context_json, importance_score,
                 access_count, last_accessed, created_at, updated_at, tags, source_round,
                 time_window, decay_factor)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (mem_dict.get('memory_type', ''), mem_dict.get('key_data', ''),
                  mem_dict.get('value_data', '{}'), mem_dict.get('context_json'),
                  mem_dict.get('importance_score', 0.5), mem_dict.get('access_count', 0),
                  mem_dict.get('last_accessed'), mem_dict.get('created_at'),
                  mem_dict.get('updated_at'), mem_dict.get('tags'),
                  mem_dict.get('source_round'), time_window, 1.0))
            migrated_count += 1

        conn.commit()
        legacy_conn.close()
        conn.close()

        print(f"迁移完成: {migrated_count} 条记忆")
        return {"status": "completed", "migrated": migrated_count}

    def show_status(self):
        """显示状态信息"""
        stats = self.get_enhanced_statistics()
        print("\n=== 跨轮次学习记忆深度增强引擎状态 ===")
        print(f"版本: {stats['version']}")

        print(f"\n记忆统计:")
        for mem_type, info in stats['memory_stats'].items():
            print(f"  - {mem_type}: {info['count']}条 (平均重要性: {info['avg_importance']:.2f}, 强化次数: {info['total_reinforcement']})")

        print(f"\n时间窗口聚合: {stats['window_types_aggregated']} 种类型")
        print(f"衰减操作: {stats['decay_operations']} 次")
        print(f"知识整合: {stats['knowledge_integrations']} 次")
        print(f"上下文检索: {stats['context_aware_retrievals']} 次")
        print("=" * 45)


def main():
    """主入口"""
    import argparse

    parser = argparse.ArgumentParser(description="智能全场景进化环跨轮次学习记忆深度增强引擎")
    parser.add_argument("--status", action="store_true", help="显示状态信息")
    parser.add_argument("--migrate", action="store_true", help="从旧版数据库迁移数据")
    parser.add_argument("--decay", action="store_true", help="应用记忆衰减机制")
    parser.add_argument("--decay-dry-run", action="store_true", help="模拟运行衰减机制（不实际修改）")
    parser.add_argument("--aggregate", type=str, choices=['monthly', 'quarterly', 'yearly'],
                       help="跨时间窗口知识整合")
    parser.add_argument("--integrate", action="store_true", help="跨窗口知识整合")
    parser.add_argument("--retrieve", type=str, help="上下文感知检索（传入查询词）")
    parser.add_argument("--retrieve-context", type=str, help="检索时的上下文（JSON格式）")
    parser.add_argument("--full-cycle", action="store_true", help="运行完整周期")
    parser.add_argument("--cockpit-data", action="store_true", help="获取驾驶舱数据")

    args = parser.parse_args()

    engine = EvolutionCrossRoundLearningMemoryEngine()

    if args.status:
        engine.show_status()
    elif args.migrate:
        result = engine.migrate_from_legacy()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif args.decay:
        result = engine.apply_memory_decay()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif args.decay_dry_run:
        result = engine.apply_memory_decay(dry_run=True)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif args.aggregate:
        result = engine.time_window_aggregation(args.aggregate)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif args.integrate:
        result = engine.integrate_cross_window_knowledge()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif args.retrieve:
        context = None
        if args.retrieve_context:
            try:
                context = json.loads(args.retrieve_context)
            except:
                pass
        results = engine.get_context_aware_retrieval(args.retrieve, context=context, limit=10)
        print(f"检索到 {len(results)} 条记忆:")
        for r in results:
            print(f"  - [{r['memory_type']}] {r['key_data'][:40]} (得分: {r.get('final_score', 0):.2f})")
    elif args.full_cycle:
        engine.run_full_cycle()
    elif args.cockpit_data:
        data = engine.get_cockpit_data()
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()