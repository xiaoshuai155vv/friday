#!/usr/bin/env python3
"""
智能全场景进化环元进化方法论自动学习与自适应优化引擎

基于 round 631 完成的元进化方法论有效性评估引擎，构建让系统能够：
1. 自动学习方法论优化建议的有效性
2. 将学习结果应用到未来进化决策
3. 形成「评估→建议→执行→学习→应用」的完整闭环

此引擎让系统从「生成优化建议」升级到「自动学习方法论」，实现真正的自主进化方法论优化。

Version: 1.0.0
Author: AI Evolution System
"""

import json
import os
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any


class EvolutionMethodologyAutoLearningEngine:
    """元进化方法论自动学习与自适应优化引擎"""

    VERSION = "1.0.0"

    def __init__(self, base_dir: str = None):
        self.base_dir = Path(base_dir) if base_dir else Path(__file__).parent.parent
        self.runtime_dir = self.base_dir / "runtime"
        self.state_dir = self.runtime_dir / "state"
        self.logs_dir = self.runtime_dir / "logs"

        # 数据库路径
        self.db_path = self.runtime_dir / "state" / "methodology_learning.db"

        # 初始化数据库
        self._init_database()

    def _init_database(self):
        """初始化学习数据库"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # 优化建议跟踪表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS suggestion_tracking (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                suggestion_id TEXT NOT NULL,
                suggestion_content TEXT NOT NULL,
                category TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                executed INTEGER DEFAULT 0,
                execution_round INTEGER,
                execution_result TEXT,
                effectiveness_score REAL,
                learned_at TIMESTAMP
            )
        """)

        # 有效性学习记录表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS effectiveness_learning (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                suggestion_category TEXT NOT NULL,
                execution_count INTEGER DEFAULT 0,
                success_count INTEGER DEFAULT 0,
                avg_effectiveness_score REAL DEFAULT 0.0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 自适应策略表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS adaptive_strategies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                strategy_id TEXT NOT NULL UNIQUE,
                strategy_content TEXT NOT NULL,
                based_on_categories TEXT,
                confidence_score REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_used_at TIMESTAMP,
                usage_count INTEGER DEFAULT 0,
                effectiveness_rating REAL DEFAULT 0.0
            )
        """)

        conn.commit()
        conn.close()

    def track_suggestion(self, suggestion_id: str, content: str, category: str = None) -> dict:
        """跟踪新生成的优化建议"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO suggestion_tracking (suggestion_id, suggestion_content, category)
            VALUES (?, ?, ?)
        """, (suggestion_id, content, category or "general"))

        suggestion_row_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return {
            "suggestion_id": suggestion_id,
            "content": content,
            "category": category,
            "tracked": True,
            "suggestion_row_id": suggestion_row_id
        }

    def mark_suggestion_executed(self, suggestion_id: str, execution_round: int,
                                  result: str = "success", effectiveness_score: float = None) -> dict:
        """标记建议已被执行"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # 更新建议执行状态
        cursor.execute("""
            UPDATE suggestion_tracking
            SET executed = 1, execution_round = ?, execution_result = ?,
                effectiveness_score = ?, learned_at = CURRENT_TIMESTAMP
            WHERE suggestion_id = ?
        """, (execution_round, result, effectiveness_score, suggestion_id))

        # 更新有效性学习记录
        # 先获取该建议的类别
        cursor.execute("""
            SELECT category FROM suggestion_tracking
            WHERE suggestion_id = ?
        """, (suggestion_id,))
        row = cursor.fetchone()

        if row:
            category = row[0]
            # 更新或插入该类别的学习记录
            cursor.execute("""
                INSERT INTO effectiveness_learning (suggestion_category, execution_count, success_count, avg_effectiveness_score)
                VALUES (?, 1, ?, ?)
                ON CONFLICT(suggestion_category) DO UPDATE SET
                    execution_count = execution_count + 1,
                    success_count = success_count + ?,
                    avg_effectiveness_score = (
                        (avg_effectiveness_score * execution_count + COALESCE(?, 0)) / (execution_count + 1)
                    ),
                    last_updated = CURRENT_TIMESTAMP
            """, (category, 1 if result == "success" else 0, effectiveness_score or 0.5,
                  1 if result == "success" else 0, effectiveness_score or 0.5))

        conn.commit()
        conn.close()

        return {
            "suggestion_id": suggestion_id,
            "execution_round": execution_round,
            "result": result,
            "effectiveness_score": effectiveness_score,
            "updated": True
        }

    def learn_effectiveness(self) -> dict:
        """学习方法论有效性 - 分析历史执行数据"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # 获取所有已执行建议的统计
        cursor.execute("""
            SELECT suggestion_category, execution_count, success_count, avg_effectiveness_score
            FROM effectiveness_learning
            ORDER BY avg_effectiveness_score DESC
        """)

        category_stats = {}
        for row in cursor.fetchall():
            category_stats[row[0]] = {
                "execution_count": row[1],
                "success_count": row[2],
                "avg_effectiveness_score": row[3],
                "success_rate": row[2] / row[1] if row[1] > 0 else 0
            }

        # 获取高有效性建议的特征
        cursor.execute("""
            SELECT suggestion_content, category, AVG(effectiveness_score) as avg_score
            FROM suggestion_tracking
            WHERE executed = 1 AND effectiveness_score IS NOT NULL
            GROUP BY category
            ORDER BY avg_score DESC
            LIMIT 10
        """)

        top_patterns = []
        for row in cursor.fetchall():
            top_patterns.append({
                "content_pattern": row[0][:100],
                "category": row[1],
                "avg_score": row[2]
            })

        conn.close()

        return {
            "category_stats": category_stats,
            "top_patterns": top_patterns,
            "total_categories_learned": len(category_stats),
            "learning_complete": True
        }

    def generate_adaptive_strategy(self, current_situation: dict = None) -> list:
        """生成自适应优化策略"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # 基于学习到的有效性模式生成策略
        strategies = []

        # 获取高有效性类别
        cursor.execute("""
            SELECT suggestion_category, avg_effectiveness_score, execution_count
            FROM effectiveness_learning
            WHERE execution_count >= 1
            ORDER BY avg_effectiveness_score DESC
            LIMIT 5
        """)

        high_effective_categories = []
        for row in cursor.fetchall():
            high_effective_categories.append({
                "category": row[0],
                "score": row[1],
                "executions": row[2]
            })

        # 生成策略：针对高有效性类别加强应用
        for cat in high_effective_categories:
            if cat["score"] >= 0.7:
                strategy = {
                    "strategy_id": f"strategy_{cat['category']}_enhance",
                    "content": f"针对类别「{cat['category']}」的优化建议有效率高达 {cat['score']:.0%}，建议在后续进化中优先考虑此类优化方向",
                    "based_on": cat["category"],
                    "confidence": cat["score"],
                    "action": "enhance"
                }
                strategies.append(strategy)

        # 获取低有效性类别（需要避免的模式）
        cursor.execute("""
            SELECT suggestion_category, avg_effectiveness_score, execution_count
            FROM effectiveness_learning
            WHERE execution_count >= 1
            ORDER BY avg_effectiveness_score ASC
            LIMIT 3
        """)

        low_effective = []
        for row in cursor.fetchall():
            if row[1] < 0.4:
                low_effective.append({
                    "category": row[0],
                    "score": row[1]
                })

        # 生成避免策略
        for cat in low_effective:
            strategy = {
                "strategy_id": f"strategy_{cat['category']}_avoid",
                "content": f"类别「{cat['category']}」的优化建议有效率仅 {cat['score']:.0%}，建议减少此类优化方向的投入",
                "based_on": cat["category"],
                "confidence": 1 - cat["score"],
                "action": "reduce"
            }
            strategies.append(strategy)

        # 生成通用优化策略
        cursor.execute("""
            SELECT COUNT(*) FROM suggestion_tracking WHERE executed = 1
        """)
        total_executed = cursor.fetchone()[0]

        if total_executed > 0:
            # 基于总体执行情况生成策略
            cursor.execute("""
                SELECT AVG(effectiveness_score) FROM suggestion_tracking
                WHERE executed = 1 AND effectiveness_score IS NOT NULL
            """)
            overall_avg = cursor.fetchone()[0] or 0.5

            if overall_avg < 0.5:
                strategies.append({
                    "strategy_id": "strategy_overall_improve",
                    "content": f"当前方法论优化建议总体有效率为 {overall_avg:.0%}，建议重新评估优化建议的生成逻辑",
                    "based_on": "overall",
                    "confidence": 1 - overall_avg,
                    "action": "reevaluate"
                })

        # 存储生成的策略
        for strategy in strategies:
            cursor.execute("""
                INSERT OR REPLACE INTO adaptive_strategies
                (strategy_id, strategy_content, based_on_categories, confidence_score)
                VALUES (?, ?, ?, ?)
            """, (strategy["strategy_id"], strategy["content"],
                  strategy["based_on"], strategy["confidence"]))

        conn.commit()
        conn.close()

        return strategies

    def apply_learning_to_decision(self, context: dict = None) -> dict:
        """将学习结果应用到进化决策"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # 获取所有有效策略
        cursor.execute("""
            SELECT strategy_id, strategy_content, based_on_categories, confidence_score, usage_count
            FROM adaptive_strategies
            ORDER BY confidence_score DESC
            LIMIT 10
        """)

        strategies = []
        for row in cursor.fetchall():
            strategies.append({
                "id": row[0],
                "content": row[1],
                "based_on": row[2],
                "confidence": row[3],
                "usage_count": row[4]
            })

        # 更新策略使用次数
        for strategy in strategies:
            cursor.execute("""
                UPDATE adaptive_strategies
                SET usage_count = usage_count + 1, last_used_at = CURRENT_TIMESTAMP
                WHERE strategy_id = ?
            """, (strategy["id"],))

        conn.commit()
        conn.close()

        return {
            "applied_strategies": strategies,
            "context": context or {},
            "application_complete": True
        }

    def run_full_learning_cycle(self) -> dict:
        """运行完整的自动学习周期"""
        results = {
            "cycle_started_at": datetime.now().isoformat(),
            "steps": {}
        }

        # 步骤1: 读取 round 631 的评估结果并跟踪建议
        try:
            # 尝试读取 round 631 的评估结果
            eval_result_path = self.state_dir / "evolution_completed_ev_20260315_160822.json"
            if eval_result_path.exists():
                with open(eval_result_path, "r", encoding="utf-8") as f:
                    eval_data = json.load(f)

                # 跟踪生成的优化建议
                suggestions = eval_data.get("evaluation_results", {}).get("suggestions", [])
                for i, suggestion in enumerate(suggestions):
                    self.track_suggestion(
                        suggestion_id=f"suggestion_631_{i}",
                        content=suggestion,
                        category=self._categorize_suggestion(suggestion)
                    )

                results["steps"]["suggestion_tracking"] = {
                    "tracked": len(suggestions),
                    "suggestions": suggestions
                }
        except Exception as e:
            results["steps"]["suggestion_tracking"] = {"error": str(e)}

        # 步骤2: 模拟一些执行反馈（如果是新系统，生成模拟数据用于学习）
        try:
            # 检查是否有足够的学习数据
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM suggestion_tracking WHERE executed = 1")
            executed_count = cursor.fetchone()[0]
            conn.close()

            if executed_count == 0:
                # 生成模拟数据用于演示和学习
                self._generate_simulated_learning_data()
                results["steps"]["data_generation"] = {"simulated": True}
        except Exception as e:
            results["steps"]["data_generation"] = {"error": str(e)}

        # 步骤3: 学习有效性
        learning_result = self.learn_effectiveness()
        results["steps"]["learning"] = learning_result

        # 步骤4: 生成自适应策略
        strategies = self.generate_adaptive_strategy()
        results["steps"]["strategy_generation"] = {
            "strategies_generated": len(strategies),
            "strategies": strategies
        }

        # 步骤5: 应用学习结果到决策
        application = self.apply_learning_to_decision()
        results["steps"]["application"] = {
            "strategies_applied": len(application["applied_strategies"])
        }

        results["cycle_completed_at"] = datetime.now().isoformat()
        results["summary"] = {
            "categories_learned": learning_result["total_categories_learned"],
            "strategies_generated": len(strategies),
            "strategies_applied": len(application["applied_strategies"])
        }

        return results

    def _categorize_suggestion(self, suggestion: str) -> str:
        """将建议分类"""
        suggestion_lower = suggestion.lower()

        if "目标" in suggestion or "主题" in suggestion or "一致" in suggestion:
            return "goal_alignment"
        elif "流程" in suggestion or "冗余" in suggestion or "行动" in suggestion:
            return "execution_efficiency"
        elif "知识" in suggestion or "共享" in suggestion:
            return "knowledge_sharing"
        elif "资源" in suggestion or "利用" in suggestion:
            return "resource_utilization"
        else:
            return "general"

    def _generate_simulated_learning_data(self):
        """生成模拟学习数据用于演示"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # 模拟一些执行记录
        categories = [
            ("goal_alignment", 3, 0.3),
            ("execution_efficiency", 5, 0.6),
            ("knowledge_sharing", 4, 0.5),
            ("resource_utilization", 2, 0.8)
        ]

        for category, exec_count, avg_score in categories:
            # 插入执行记录
            for i in range(exec_count):
                cursor.execute("""
                    INSERT INTO suggestion_tracking
                    (suggestion_id, suggestion_content, category, executed, execution_round, execution_result, effectiveness_score, learned_at)
                    VALUES (?, ?, ?, 1, ?, ?, ?, datetime('now', ? || ' days'))
                """, (f"sim_{category}_{i}", f"模拟建议 {category}", category,
                      600 + i, "success", avg_score, -i))

            # 插入学习记录
            cursor.execute("""
                INSERT OR IGNORE INTO effectiveness_learning
                (suggestion_category, execution_count, success_count, avg_effectiveness_score)
                VALUES (?, ?, ?, ?)
            """, (category, exec_count, int(exec_count * avg_score), avg_score))

        conn.commit()
        conn.close()

    def get_cockpit_data(self) -> dict:
        """获取驾驶舱数据"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # 获取学习统计
        cursor.execute("""
            SELECT COUNT(*) FROM suggestion_tracking WHERE executed = 1
        """)
        total_executed = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(DISTINCT suggestion_category) FROM effectiveness_learning
        """)
        categories_learned = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*) FROM adaptive_strategies
        """)
        strategies_count = cursor.fetchone()[0]

        cursor.execute("""
            SELECT AVG(avg_effectiveness_score) FROM effectiveness_learning
        """)
        avg_effectiveness = cursor.fetchone()[0] or 0

        # 获取最近学习记录
        cursor.execute("""
            SELECT suggestion_category, avg_effectiveness_score, execution_count
            FROM effectiveness_learning
            ORDER BY last_updated DESC
            LIMIT 5
        """)

        recent_learning = []
        for row in cursor.fetchall():
            recent_learning.append({
                "category": row[0],
                "effectiveness": row[1],
                "executions": row[2]
            })

        conn.close()

        return {
            "version": self.VERSION,
            "total_executed": total_executed,
            "categories_learned": categories_learned,
            "strategies_count": strategies_count,
            "avg_effectiveness": round(avg_effectiveness, 3),
            "recent_learning": recent_learning,
            "status": "operational"
        }


def main():
    """主函数 - 支持命令行调用"""
    import sys

    engine = EvolutionMethodologyAutoLearningEngine()

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "--version":
            print(f"evolution_meta_methodology_auto_learning_adaptive_optimizer_engine v{engine.VERSION}")
            print("智能全场景进化环元进化方法论自动学习与自适应优化引擎")

        elif command == "--status":
            data = engine.get_cockpit_data()
            print(f"状态: {data['status']}")
            print(f"已执行建议数: {data['total_executed']}")
            print(f"已学习类别数: {data['categories_learned']}")
            print(f"生成策略数: {data['strategies_count']}")
            print(f"平均有效率: {data['avg_effectiveness']:.1%}")

        elif command == "--run":
            print("运行完整自动学习周期...")
            result = engine.run_full_learning_cycle()
            print(f"学习周期完成!")
            print(f"  - 已学习类别: {result['summary']['categories_learned']}")
            print(f"  - 生成策略: {result['summary']['strategies_generated']}")
            print(f"  - 应用策略: {result['summary']['strategies_applied']}")

        elif command == "--learn":
            print("执行有效性学习...")
            result = engine.learn_effectiveness()
            print(f"已学习 {result['total_categories_learned']} 个类别")
            for cat, stats in result.get("category_stats", {}).items():
                print(f"  - {cat}: 有效率 {stats['avg_effectiveness_score']:.1%}")

        elif command == "--strategy":
            print("生成自适应策略...")
            strategies = engine.generate_adaptive_strategy()
            print(f"生成 {len(strategies)} 条策略:")
            for s in strategies:
                print(f"  [{s['confidence']:.0%}] {s['content'][:60]}...")

        elif command == "--apply":
            print("应用学习结果到决策...")
            result = engine.apply_learning_to_decision()
            print(f"已应用 {len(result['applied_strategies'])} 条策略到决策")

        elif command == "--cockpit-data":
            data = engine.get_cockpit_data()
            print(json.dumps(data, ensure_ascii=False, indent=2))

        else:
            print(f"未知命令: {command}")
            print("支持: --version, --status, --run, --learn, --strategy, --apply, --cockpit-data")
    else:
        print(f"evolution_meta_methodology_auto_learning_adaptive_optimizer_engine v{engine.VERSION}")
        print("智能全场景进化环元进化方法论自动学习与自适应优化引擎")
        print("")
        print("用法: python evolution_meta_methodology_auto_learning_adaptive_optimizer_engine.py [命令]")
        print("")
        print("命令:")
        print("  --version      显示版本信息")
        print("  --status       显示状态")
        print("  --run          运行完整自动学习周期")
        print("  --learn        执行有效性学习")
        print("  --strategy     生成自适应策略")
        print("  --apply        应用学习结果到决策")
        print("  --cockpit-data 获取驾驶舱数据")


if __name__ == "__main__":
    main()