#!/usr/bin/env python3
"""
智能跨会话知识传承引擎
让系统能够跨会话传递关键知识、决策上下文和进化经验

功能：
1. 会话知识摘要生成 - 自动从会话中提取关键信息
2. 关键上下文保存 - 保存决策上下文、用户偏好、任务状态等
3. 知识传承机制 - 新会话可以访问之前会话的知识
4. 进化经验传承 - 将进化过程中的经验传递给后续轮次

集成方式：do.py 支持「知识传承」「传承知识」「会话接续」「跨会话」「知识摘要」等关键词触发
"""

import json
import os
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional


class KnowledgeInheritanceEngine:
    """智能跨会话知识传承引擎"""

    def __init__(self, db_path: str = None):
        if db_path is None:
            base_dir = Path(__file__).parent.parent
            db_path = base_dir / "runtime" / "state" / "knowledge_inheritance.db"
        self.db_path = str(db_path)
        self._init_database()

    def _init_database(self):
        """初始化数据库"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 创建会话知识表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS session_knowledge (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                knowledge_type TEXT NOT NULL,
                key TEXT NOT NULL,
                value TEXT NOT NULL,
                importance INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                access_count INTEGER DEFAULT 0
            )
        """)

        # 创建决策上下文表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS decision_context (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                decision_type TEXT NOT NULL,
                context TEXT NOT NULL,
                reasoning TEXT,
                result TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 创建进化经验表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS evolution_experience (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                round_number INTEGER,
                evolution_type TEXT NOT NULL,
                experience TEXT NOT NULL,
                lessons TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 创建会话摘要表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS session_summaries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL UNIQUE,
                summary TEXT NOT NULL,
                key_points TEXT NOT NULL,
                user_preferences TEXT,
                task_states TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()

    def add_knowledge(self, session_id: str, knowledge_type: str, key: str,
                      value: Any, importance: int = 1) -> bool:
        """添加知识到传承库"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 检查是否已存在
            cursor.execute("""
                SELECT id FROM session_knowledge
                WHERE session_id = ? AND knowledge_type = ? AND key = ?
            """, (session_id, knowledge_type, key))

            existing = cursor.fetchone()

            if existing:
                # 更新
                cursor.execute("""
                    UPDATE session_knowledge
                    SET value = ?, importance = ?, last_accessed = CURRENT_TIMESTAMP
                    WHERE session_id = ? AND knowledge_type = ? AND key = ?
                """, (json.dumps(value), importance, session_id, knowledge_type, key))
            else:
                # 插入
                cursor.execute("""
                    INSERT INTO session_knowledge (session_id, knowledge_type, key, value, importance)
                    VALUES (?, ?, ?, ?, ?)
                """, (session_id, knowledge_type, key, json.dumps(value), importance))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"添加知识失败: {e}")
            return False

    def get_knowledge(self, session_id: str = None, knowledge_type: str = None,
                      key: str = None, limit: int = 10) -> List[Dict]:
        """获取知识"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            query = "SELECT session_id, knowledge_type, key, value, importance, created_at, access_count FROM session_knowledge WHERE 1=1"
            params = []

            if session_id:
                query += " AND session_id = ?"
                params.append(session_id)
            if knowledge_type:
                query += " AND knowledge_type = ?"
                params.append(knowledge_type)
            if key:
                query += " AND key LIKE ?"
                params.append(f"%{key}%")

            query += " ORDER BY importance DESC, last_accessed DESC LIMIT ?"
            params.append(limit)

            cursor.execute(query, params)
            rows = cursor.fetchall()

            conn.close()

            return [
                {
                    "session_id": row[0],
                    "knowledge_type": row[1],
                    "key": row[2],
                    "value": json.loads(row[3]),
                    "importance": row[4],
                    "created_at": row[5],
                    "access_count": row[6]
                }
                for row in rows
            ]
        except Exception as e:
            print(f"获取知识失败: {e}")
            return []

    def add_decision_context(self, session_id: str, decision_type: str,
                             context: Dict, reasoning: str = None,
                             result: Any = None) -> bool:
        """添加决策上下文"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO decision_context (session_id, decision_type, context, reasoning, result)
                VALUES (?, ?, ?, ?, ?)
            """, (session_id, decision_type, json.dumps(context), reasoning,
                  json.dumps(result) if result else None))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"添加决策上下文失败: {e}")
            return False

    def get_decision_context(self, session_id: str = None,
                             decision_type: str = None,
                             limit: int = 10) -> List[Dict]:
        """获取决策上下文"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            query = "SELECT session_id, decision_type, context, reasoning, result, created_at FROM decision_context WHERE 1=1"
            params = []

            if session_id:
                query += " AND session_id = ?"
                params.append(session_id)
            if decision_type:
                query += " AND decision_type = ?"
                params.append(decision_type)

            query += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)

            cursor.execute(query, params)
            rows = cursor.fetchall()

            conn.close()

            return [
                {
                    "session_id": row[0],
                    "decision_type": row[1],
                    "context": json.loads(row[2]),
                    "reasoning": row[3],
                    "result": json.loads(row[4]) if row[4] else None,
                    "created_at": row[5]
                }
                for row in rows
            ]
        except Exception as e:
            print(f"获取决策上下文失败: {e}")
            return []

    def add_evolution_experience(self, round_number: int, evolution_type: str,
                                 experience: str, lessons: str = None) -> bool:
        """添加进化经验"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO evolution_experience (round_number, evolution_type, experience, lessons)
                VALUES (?, ?, ?, ?)
            """, (round_number, evolution_type, experience, lessons))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"添加进化经验失败: {e}")
            return False

    def get_evolution_experience(self, round_number: int = None,
                                  evolution_type: str = None,
                                  limit: int = 10) -> List[Dict]:
        """获取进化经验"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            query = "SELECT round_number, evolution_type, experience, lessons, created_at FROM evolution_experience WHERE 1=1"
            params = []

            if round_number:
                query += " AND round_number = ?"
                params.append(round_number)
            if evolution_type:
                query += " AND evolution_type = ?"
                params.append(evolution_type)

            query += " ORDER BY round_number DESC LIMIT ?"
            params.append(limit)

            cursor.execute(query, params)
            rows = cursor.fetchall()

            conn.close()

            return [
                {
                    "round_number": row[0],
                    "evolution_type": row[1],
                    "experience": row[2],
                    "lessons": row[3],
                    "created_at": row[4]
                }
                for row in rows
            ]
        except Exception as e:
            print(f"获取进化经验失败: {e}")
            return []

    def save_session_summary(self, session_id: str, summary: str,
                              key_points: List[str],
                              user_preferences: Dict = None,
                              task_states: Dict = None) -> bool:
        """保存会话摘要"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT OR REPLACE INTO session_summaries (session_id, summary, key_points, user_preferences, task_states, updated_at)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (session_id, summary, json.dumps(key_points),
                  json.dumps(user_preferences) if user_preferences else None,
                  json.dumps(task_states) if task_states else None))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"保存会话摘要失败: {e}")
            return False

    def get_session_summary(self, session_id: str) -> Optional[Dict]:
        """获取会话摘要"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT session_id, summary, key_points, user_preferences, task_states, created_at, updated_at
                FROM session_summaries
                WHERE session_id = ?
            """, (session_id,))

            row = cursor.fetchone()
            conn.close()

            if row:
                return {
                    "session_id": row[0],
                    "summary": row[1],
                    "key_points": json.loads(row[2]),
                    "user_preferences": json.loads(row[3]) if row[3] else None,
                    "task_states": json.loads(row[4]) if row[4] else None,
                    "created_at": row[5],
                    "updated_at": row[6]
                }
            return None
        except Exception as e:
            print(f"获取会话摘要失败: {e}")
            return None

    def get_recent_sessions(self, days: int = 7, limit: int = 10) -> List[Dict]:
        """获取最近的会话摘要"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT session_id, summary, key_points, user_preferences, task_states, created_at
                FROM session_summaries
                WHERE created_at >= datetime('now', '-' || ? || ' days')
                ORDER BY created_at DESC
                LIMIT ?
            """, (days, limit))

            rows = cursor.fetchall()
            conn.close()

            return [
                {
                    "session_id": row[0],
                    "summary": row[1],
                    "key_points": json.loads(row[2]),
                    "user_preferences": json.loads(row[3]) if row[3] else None,
                    "task_states": json.loads(row[4]) if row[4] else None,
                    "created_at": row[5]
                }
                for row in rows
            ]
        except Exception as e:
            print(f"获取最近会话失败: {e}")
            return []

    def get_knowledge_summary(self) -> Dict:
        """获取知识传承概览"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 统计各项数量
            cursor.execute("SELECT COUNT(*) FROM session_knowledge")
            knowledge_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM decision_context")
            decision_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM evolution_experience")
            evolution_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM session_summaries")
            session_count = cursor.fetchone()[0]

            # 获取知识类型分布
            cursor.execute("""
                SELECT knowledge_type, COUNT(*) as cnt
                FROM session_knowledge
                GROUP BY knowledge_type
                ORDER BY cnt DESC
            """)
            type_dist = [{"type": row[0], "count": row[1]} for row in cursor.fetchall()]

            conn.close()

            return {
                "knowledge_items": knowledge_count,
                "decision_contexts": decision_count,
                "evolution_experiences": evolution_count,
                "session_summaries": session_count,
                "knowledge_type_distribution": type_dist,
                "status": "active"
            }
        except Exception as e:
            print(f"获取知识总结失败: {e}")
            return {"status": "error", "message": str(e)}


def handle_command(args: List[str]) -> str:
    """处理命令行调用"""
    engine = KnowledgeInheritanceEngine()

    if not args:
        return "用法: knowledge_inheritance <command> [options]\n\n命令:\n  summary - 显示知识传承概览\n  list [type] - 列出知识条目\n  sessions [days] - 列出最近会话\n  decisions [type] - 列出决策上下文\n  evolution [round] - 列出进化经验\n  get <session_id> - 获取特定会话摘要\n  help - 显示帮助"

    command = args[0]

    if command == "summary":
        result = engine.get_knowledge_summary()
        return json.dumps(result, indent=2, ensure_ascii=False)

    elif command == "list":
        knowledge_type = args[1] if len(args) > 1 else None
        result = engine.get_knowledge(knowledge_type=knowledge_type, limit=20)
        if not result:
            return "暂无知识条目"
        return json.dumps(result, indent=2, ensure_ascii=False)

    elif command == "sessions":
        days = int(args[1]) if len(args) > 1 and args[1].isdigit() else 7
        result = engine.get_recent_sessions(days=days)
        if not result:
            return f"最近 {days} 天内无会话记录"
        return json.dumps(result, indent=2, ensure_ascii=False)

    elif command == "decisions":
        decision_type = args[1] if len(args) > 1 else None
        result = engine.get_decision_context(decision_type=decision_type, limit=20)
        if not result:
            return "暂无决策上下文"
        return json.dumps(result, indent=2, ensure_ascii=False)

    elif command == "evolution":
        round_number = int(args[1]) if len(args) > 1 and args[1].isdigit() else None
        result = engine.get_evolution_experience(round_number=round_number)
        if not result:
            return "暂无进化经验"
        return json.dumps(result, indent=2, ensure_ascii=False)

    elif command == "get":
        if len(args) < 2:
            return "用法: knowledge_inheritance get <session_id>"
        result = engine.get_session_summary(args[1])
        if not result:
            return f"未找到会话 {args[1]} 的摘要"
        return json.dumps(result, indent=2, ensure_ascii=False)

    elif command == "help":
        return """智能跨会话知识传承引擎

让系统能够跨会话传递关键知识、决策上下文和进化经验。

命令:
  summary           - 显示知识传承概览
  list [type]       - 列出知识条目（可选按类型过滤）
  sessions [days]   - 列出最近会话（默认7天）
  decisions [type]  - 列出决策上下文（可选按类型过滤）
  evolution [round] - 列出进化经验（可选按轮次过滤）
  get <session_id> - 获取特定会话摘要
  help              - 显示本帮助

示例:
  python scripts/knowledge_inheritance_engine.py summary
  python scripts/knowledge_inheritance_engine.py list user_preference
  python scripts/knowledge_inheritance_engine.py sessions 30
"""

    else:
        return f"未知命令: {command}\n输入 'knowledge_inheritance help' 查看帮助"


if __name__ == "__main__":
    import sys
    args = sys.argv[1:] if len(sys.argv) > 1 else []
    result = handle_command(args)
    print(result)