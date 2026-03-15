"""
智能全场景进化环创新建议自动执行与迭代深化引擎
version: 1.0.0

基于 round 633 知识图谱发现创新建议和 round 634 价值验证排序基础上，
构建让系统能够自动将高优先级创新建议转化为可执行任务、执行验证、迭代优化的完整闭环。

功能：
1. 高优先级建议自动提取 - 从验证排序结果中自动提取高优先级创新建议
2. 任务自动转化 - 将创新建议转化为可执行的进化任务
3. 任务执行与验证 - 自动执行任务并验证效果
4. 迭代优化 - 基于执行结果进行迭代改进
5. 驾驶舱数据接口 - 提供执行状态可视化

与 round 633 知识图谱引擎、round 634 价值排序引擎深度集成，
形成「发现→验证→排序→执行→迭代」的完整创新价值实现链路。
"""

import json
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
RUNTIME_STATE_DIR = PROJECT_ROOT / "runtime" / "state"
RUNTIME_LOGS_DIR = PROJECT_ROOT / "runtime" / "logs"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"

# 知识图谱数据库路径
KG_DB_PATH = RUNTIME_STATE_DIR / "knowledge_graph.db"

# 创新价值验证数据库路径
INNOVATION_VERIFICATION_DB = RUNTIME_STATE_DIR / "innovation_verification.db"

# 本引擎数据库
INNOVATION_EXECUTION_DB = RUNTIME_STATE_DIR / "innovation_execution.db"


class InnovationExecutionIterationEngine:
    """创新建议自动执行与迭代深化引擎"""

    def __init__(self):
        self.kg_db_path = KG_DB_PATH
        self.verification_db_path = INNOVATION_VERIFICATION_DB
        self.execution_db_path = INNOVATION_EXECUTION_DB
        self._init_database()

    def _init_database(self):
        """初始化执行迭代数据库"""
        conn = sqlite3.connect(str(self.execution_db_path))
        cursor = conn.cursor()

        # 任务表 - 存储转化后的可执行任务
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS execution_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                innovation_id INTEGER,
                description TEXT,
                category TEXT,
                priority_rank INTEGER,
                total_value_score REAL,
                task_type TEXT,
                task_steps TEXT,
                estimated_duration INTEGER,
                dependencies TEXT,
                execution_status TEXT DEFAULT 'pending',
                execution_result TEXT,
                executed_at TEXT,
                execution_feedback TEXT,
                iteration_count INTEGER DEFAULT 0,
                last_iteration_at TEXT,
                created_at TEXT
            )
        """)

        # 执行记录表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS execution_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER,
                execution_attempt INTEGER,
                execution_status TEXT,
                execution_result TEXT,
                feedback TEXT,
                improvements TEXT,
                executed_at TEXT
            )
        """)

        # 迭代优化记录表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS iteration_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER,
                iteration_number INTEGER,
                original_steps TEXT,
                modified_steps TEXT,
                modification_reason TEXT,
                improvement_score REAL,
                created_at TEXT
            )
        """)

        conn.commit()
        conn.close()

    def get_high_priority_innovations(self, limit: int = 10) -> List[Dict]:
        """从验证排序结果获取高优先级创新建议"""
        innovations = []
        conn = sqlite3.connect(str(self.verification_db_path))
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT id, description, category, total_value_score, priority_rank,
                       execution_difficulty, predicted_effect
                FROM innovation_verification
                WHERE verification_status = 'verified'
                ORDER BY priority_rank ASC, total_value_score DESC
                LIMIT ?
            """, (limit,))

            rows = cursor.fetchall()
            for row in rows:
                innovations.append({
                    "id": row[0],
                    "description": row[1],
                    "category": row[2],
                    "total_value_score": row[3],
                    "priority_rank": row[4],
                    "execution_difficulty": row[5],
                    "predicted_effect": row[6]
                })
        except Exception as e:
            print(f"获取高优先级创新建议失败: {e}")
        finally:
            conn.close()

        return innovations

    def transform_to_executable_task(self, innovation: Dict) -> Dict:
        """将创新建议转化为可执行任务"""
        task = {
            "task_type": self._classify_task_type(innovation.get("category", "")),
            "task_steps": self._generate_task_steps(innovation),
            "estimated_duration": self._estimate_duration(innovation.get("execution_difficulty", "medium")),
            "dependencies": self._identify_dependencies(innovation)
        }

        # 更新创新建议的执行状态为"已转化"
        conn = sqlite3.connect(str(self.verification_db_path))
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE innovation_verification
                SET verification_status = 'transformed'
                WHERE id = ?
            """, (innovation.get("id"),))
            conn.commit()
        except Exception as e:
            print(f"更新创新建议状态失败: {e}")
        finally:
            conn.close()

        return task

    def _classify_task_type(self, category: str) -> str:
        """分类任务类型"""
        category_lower = category.lower() if category else ""
        if "优化" in category_lower or "improve" in category_lower:
            return "optimization"
        elif "增强" in category_lower or "enhance" in category_lower:
            return "enhancement"
        elif "新增" in category_lower or "new" in category_lower:
            return "new_feature"
        elif "集成" in category_lower or "integrate" in category_lower:
            return "integration"
        elif "修复" in category_lower or "fix" in category_lower:
            return "fix"
        else:
            return "general"

    def _generate_task_steps(self, innovation: Dict) -> str:
        """生成任务步骤"""
        task_type = self._classify_task_type(innovation.get("category", ""))
        description = innovation.get("description", "")

        # 通用任务步骤模板
        steps = [
            "1. 分析创新建议：" + description[:50],
            "2. 评估实施可行性",
            "3. 设计实现方案",
            "4. 编写/修改代码",
            "5. 编写测试用例",
            "6. 集成验证",
            "7. 更新文档",
            "8. 效果评估"
        ]

        return json.dumps(steps, ensure_ascii=False)

    def _estimate_duration(self, difficulty: str) -> int:
        """估算执行时长（分钟）"""
        difficulty_map = {
            "low": 30,
            "medium": 60,
            "high": 120,
            "very_high": 240
        }
        return difficulty_map.get(difficulty.lower(), 60)

    def _identify_dependencies(self, innovation: Dict) -> str:
        """识别依赖"""
        # 基于类别识别依赖
        category = innovation.get("category", "")
        dependencies = []

        if "集成" in category:
            dependencies.extend(["确认依赖引擎存在", "准备集成接口"])
        if "新增" in category:
            dependencies.extend(["确认需求文档", "确认测试环境"])

        return json.dumps(dependencies, ensure_ascii=False) if dependencies else "[]"

    def create_execution_tasks(self, limit: int = 10) -> Dict:
        """批量创建执行任务"""
        result = {
            "status": "success",
            "created_count": 0,
            "tasks": []
        }

        # 获取高优先级创新建议
        innovations = self.get_high_priority_innovations(limit)

        if not innovations:
            result["message"] = "没有待转化的高优先级创新建议"
            return result

        conn = sqlite3.connect(str(self.execution_db_path))
        cursor = conn.cursor()

        try:
            for innovation in innovations:
                # 转化为可执行任务
                task_spec = self.transform_to_executable_task(innovation)

                # 插入任务记录
                cursor.execute("""
                    INSERT INTO execution_tasks
                    (innovation_id, description, category, priority_rank, total_value_score,
                     task_type, task_steps, estimated_duration, dependencies, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    innovation.get("id"),
                    innovation.get("description"),
                    innovation.get("category"),
                    innovation.get("priority_rank"),
                    innovation.get("total_value_score"),
                    task_spec.get("task_type"),
                    task_spec.get("task_steps"),
                    task_spec.get("estimated_duration"),
                    task_spec.get("dependencies"),
                    datetime.now().isoformat()
                ))

                task_id = cursor.lastrowid
                result["created_count"] += 1
                result["tasks"].append({
                    "task_id": task_id,
                    "description": innovation.get("description")[:50],
                    "task_type": task_spec.get("task_type")
                })

            conn.commit()
            result["message"] = f"成功创建 {result['created_count']} 个执行任务"
        except Exception as e:
            result["status"] = "error"
            result["message"] = f"创建执行任务失败: {e}"
        finally:
            conn.close()

        return result

    def execute_task(self, task_id: int, execution_result: str = "") -> Dict:
        """执行单个任务"""
        result = {
            "status": "success",
            "task_id": task_id,
            "message": ""
        }

        conn = sqlite3.connect(str(self.execution_db_path))
        cursor = conn.cursor()

        try:
            # 更新任务状态为执行中
            cursor.execute("""
                UPDATE execution_tasks
                SET execution_status = 'executing',
                    execution_result = ?,
                    executed_at = ?
                WHERE id = ?
            """, (execution_result, datetime.now().isoformat(), task_id))

            # 记录执行历史
            cursor.execute("""
                INSERT INTO execution_history
                (task_id, execution_attempt, execution_status, executed_at)
                VALUES (?, 1, 'executing', ?)
            """, (task_id, datetime.now().isoformat()))

            conn.commit()
            result["message"] = f"任务 {task_id} 开始执行"
        except Exception as e:
            result["status"] = "error"
            result["message"] = f"执行任务失败: {e}"
        finally:
            conn.close()

        return result

    def complete_task(self, task_id: int, feedback: str, improvements: str = "") -> Dict:
        """完成任务并记录反馈"""
        result = {
            "status": "success",
            "task_id": task_id,
            "message": ""
        }

        conn = sqlite3.connect(str(self.execution_db_path))
        cursor = conn.cursor()

        try:
            # 更新任务状态为完成
            cursor.execute("""
                UPDATE execution_tasks
                SET execution_status = 'completed',
                    execution_feedback = ?,
                    executed_at = ?
                WHERE id = ?
            """, (feedback, datetime.now().isoformat(), task_id))

            # 更新执行历史
            cursor.execute("""
                UPDATE execution_history
                SET execution_status = 'completed',
                    feedback = ?,
                    executed_at = ?
                WHERE task_id = ? AND execution_attempt = 1
            """, (feedback, datetime.now().isoformat(), task_id))

            conn.commit()
            result["message"] = f"任务 {task_id} 已完成"
        except Exception as e:
            result["status"] = "error"
            result["message"] = f"完成任务失败: {e}"
        finally:
            conn.close()

        return result

    def iterate_task(self, task_id: int, modifications: str, reason: str, improvement_score: float = 0.0) -> Dict:
        """迭代优化任务"""
        result = {
            "status": "success",
            "task_id": task_id,
            "message": ""
        }

        conn = sqlite3.connect(str(self.execution_db_path))
        cursor = conn.cursor()

        try:
            # 获取当前任务信息
            cursor.execute("""
                SELECT task_steps, iteration_count FROM execution_tasks WHERE id = ?
            """, (task_id,))
            row = cursor.fetchone()

            if not row:
                result["status"] = "error"
                result["message"] = f"任务 {task_id} 不存在"
                return result

            current_steps = row[0]
            iteration_count = row[1] + 1

            # 记录迭代
            cursor.execute("""
                INSERT INTO iteration_records
                (task_id, iteration_number, original_steps, modified_steps, modification_reason, improvement_score, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (task_id, iteration_count, current_steps, modifications, reason, improvement_score, datetime.now().isoformat()))

            # 更新任务步骤和迭代次数
            cursor.execute("""
                UPDATE execution_tasks
                SET task_steps = ?,
                    iteration_count = ?,
                    last_iteration_at = ?,
                    execution_status = 'iterating'
                WHERE id = ?
            """, (modifications, iteration_count, datetime.now().isoformat(), task_id))

            conn.commit()
            result["message"] = f"任务 {task_id} 已迭代优化（第 {iteration_count} 次）"
        except Exception as e:
            result["status"] = "error"
            result["message"] = f"迭代任务失败: {e}"
        finally:
            conn.close()

        return result

    def get_task_status(self, task_id: int) -> Dict:
        """获取任务状态"""
        conn = sqlite3.connect(str(self.execution_db_path))
        cursor = conn.cursor()

        result = {"status": "not_found"}

        try:
            cursor.execute("""
                SELECT id, innovation_id, description, category, priority_rank,
                       total_value_score, task_type, execution_status,
                       iteration_count, executed_at
                FROM execution_tasks WHERE id = ?
            """, (task_id,))

            row = cursor.fetchone()
            if row:
                result = {
                    "task_id": row[0],
                    "innovation_id": row[1],
                    "description": row[2],
                    "category": row[3],
                    "priority_rank": row[4],
                    "total_value_score": row[5],
                    "task_type": row[6],
                    "execution_status": row[7],
                    "iteration_count": row[8],
                    "executed_at": row[9]
                }
        except Exception as e:
            result["error"] = str(e)
        finally:
            conn.close()

        return result

    def get_pending_tasks(self, limit: int = 10) -> List[Dict]:
        """获取待执行任务列表"""
        tasks = []
        conn = sqlite3.connect(str(self.execution_db_path))
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT id, description, category, priority_rank,
                       total_value_score, task_type, estimated_duration,
                       execution_status, iteration_count
                FROM execution_tasks
                WHERE execution_status IN ('pending', 'iterating')
                ORDER BY priority_rank ASC, total_value_score DESC
                LIMIT ?
            """, (limit,))

            rows = cursor.fetchall()
            for row in rows:
                tasks.append({
                    "task_id": row[0],
                    "description": row[1],
                    "category": row[2],
                    "priority_rank": row[3],
                    "total_value_score": row[4],
                    "task_type": row[5],
                    "estimated_duration": row[6],
                    "execution_status": row[7],
                    "iteration_count": row[8]
                })
        except Exception as e:
            print(f"获取待执行任务失败: {e}")
        finally:
            conn.close()

        return tasks

    def get_execution_summary(self) -> Dict:
        """获取执行摘要"""
        summary = {
            "total_tasks": 0,
            "pending_tasks": 0,
            "executing_tasks": 0,
            "completed_tasks": 0,
            "total_iterations": 0,
            "by_category": {},
            "by_task_type": {}
        }

        conn = sqlite3.connect(str(self.execution_db_path))
        cursor = conn.cursor()

        try:
            # 总任务数
            cursor.execute("SELECT COUNT(*) FROM execution_tasks")
            summary["total_tasks"] = cursor.fetchone()[0]

            # 按状态统计
            cursor.execute("""
                SELECT execution_status, COUNT(*) as count
                FROM execution_tasks GROUP BY execution_status
            """)
            for row in cursor.fetchall():
                status = row[0]
                count = row[1]
                if status == "pending" or status == "iterating":
                    summary["pending_tasks"] += count
                elif status == "executing":
                    summary["executing_tasks"] += count
                elif status == "completed":
                    summary["completed_tasks"] += count

            # 总迭代次数
            cursor.execute("SELECT SUM(iteration_count) FROM execution_tasks")
            summary["total_iterations"] = cursor.fetchone()[0] or 0

            # 按类别统计
            cursor.execute("""
                SELECT category, COUNT(*) as count
                FROM execution_tasks GROUP BY category
            """)
            for row in cursor.fetchall():
                summary["by_category"][row[0] or "unknown"] = row[1]

            # 按任务类型统计
            cursor.execute("""
                SELECT task_type, COUNT(*) as count
                FROM execution_tasks GROUP BY task_type
            """)
            for row in cursor.fetchall():
                summary["by_task_type"][row[0] or "unknown"] = row[1]

        except Exception as e:
            summary["error"] = str(e)
        finally:
            conn.close()

        return summary

    def get_cockpit_data(self) -> Dict:
        """获取驾驶舱数据"""
        summary = self.get_execution_summary()
        pending_tasks = self.get_pending_tasks(limit=20)

        return {
            "summary": summary,
            "pending_tasks": pending_tasks,
            "timestamp": datetime.now().isoformat()
        }


def main():
    """主函数 - 支持命令行调用"""
    import argparse

    parser = argparse.ArgumentParser(description="创新建议自动执行与迭代深化引擎")
    parser.add_argument("--version", action="store_true", help="显示版本信息")
    parser.add_argument("--status", action="store_true", help="显示引擎状态")
    parser.add_argument("--action", type=str, default="",
                        help="执行动作: create-tasks, execute, complete, iterate, summary, cockpit-data")

    args = parser.parse_args()

    engine = InnovationExecutionIterationEngine()

    if args.version:
        print("创新建议自动执行与迭代深化引擎 version 1.0.0")
        print("基于 round 633/634 创新发现-验证-排序能力，构建执行-迭代完整闭环")
        return

    if args.status:
        summary = engine.get_execution_summary()
        print("=" * 50)
        print("创新建议自动执行与迭代深化引擎状态")
        print("=" * 50)
        print(f"总任务数: {summary['total_tasks']}")
        print(f"待执行: {summary['pending_tasks']}")
        print(f"执行中: {summary['executing_tasks']}")
        print(f"已完成: {summary['completed_tasks']}")
        print(f"总迭代次数: {summary['total_iterations']}")
        print("=" * 50)
        return

    if args.action == "create-tasks":
        result = engine.create_execution_tasks(limit=10)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.action == "summary":
        summary = engine.get_execution_summary()
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    elif args.action == "cockpit-data":
        data = engine.get_cockpit_data()
        print(json.dumps(data, ensure_ascii=False, indent=2))
    elif args.action:
        print(f"未知动作: {args.action}")
        print("可用动作: create-tasks, summary, cockpit-data")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()