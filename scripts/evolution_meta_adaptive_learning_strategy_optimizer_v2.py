#!/usr/bin/env python3
"""
智能全场景进化环元进化自适应学习与策略自动优化引擎 V2

在 round 551/606/632 的方法论学习基础上，构建更深层次的自适应学习能力。让系统能够：
1. 从 600+ 轮进化历史中自动提取有效进化模式
2. 基于执行反馈自动调整进化策略参数
3. 实现进化方法的自我进化（meta-learning）
4. 形成「学习→决策→执行→验证→再学习」的完整闭环
5. 与 round 642-643 的创新价值闭环深度集成

此引擎让系统从「学习方法论」升级到「自我进化学习能力」，实现真正的元进化递归优化。

Version: 1.0.0
Author: AI Evolution System
"""

import json
import os
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional
import statistics


class EvolutionMetaAdaptiveLearningV2Engine:
    """元进化自适应学习与策略自动优化引擎 V2"""

    VERSION = "1.0.0"

    def __init__(self, base_dir: str = None):
        self.base_dir = Path(base_dir) if base_dir else Path(__file__).parent.parent
        self.runtime_dir = self.base_dir / "runtime"
        self.state_dir = self.runtime_dir / "state"
        self.logs_dir = self.runtime_dir / "logs"

        # 数据库路径
        self.db_path = self.runtime_dir / "state" / "meta_adaptive_learning_v2.db"

        # 初始化数据库
        self._init_database()

    def _init_database(self):
        """初始化学习数据库"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # 进化模式提取表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS evolution_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_id TEXT NOT NULL UNIQUE,
                pattern_type TEXT NOT NULL,
                pattern_description TEXT,
                occurrence_count INTEGER DEFAULT 0,
                success_count INTEGER DEFAULT 0,
                avg_effectiveness REAL DEFAULT 0.0,
                extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_validated_at TIMESTAMP,
                confidence_score REAL DEFAULT 0.0
            )
        """)

        # 策略参数调整记录表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS strategy_parameter_adjustments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                adjustment_id TEXT NOT NULL UNIQUE,
                parameter_name TEXT NOT NULL,
                old_value REAL,
                new_value REAL,
                adjustment_reason TEXT,
                based_on_patterns TEXT,
                execution_round INTEGER,
                result_effectiveness REAL,
                adjustment_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 元学习知识迁移表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS meta_learning_transfer (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_round_range TEXT,
                target_context TEXT,
                transferred_knowledge TEXT,
                transfer_success_rate REAL DEFAULT 0.0,
                transfer_count INTEGER DEFAULT 0,
                last_transferred_at TIMESTAMP
            )
        """)

        # 进化策略自动生成表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS auto_generated_strategies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                strategy_id TEXT NOT NULL UNIQUE,
                strategy_content TEXT NOT NULL,
                based_on_patterns TEXT,
                generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                times_applied INTEGER DEFAULT 0,
                avg_effectiveness REAL DEFAULT 0.0,
                last_applied_at TIMESTAMP,
                status TEXT DEFAULT 'active'
            )
        """)

        # 执行反馈学习表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS execution_feedback_learning (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                round_number INTEGER,
                execution_context TEXT,
                parameter_settings TEXT,
                execution_result TEXT,
                effectiveness_score REAL,
                learned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()

    def extract_evolution_patterns(self) -> dict:
        """从进化历史中自动提取有效模式"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        patterns = []

        # 读取进化完成记录
        state_dir = self.state_dir
        completed_files = list(state_dir.glob("evolution_completed_ev_*.json"))

        # 分析进化历史
        round_results = {}
        for f in completed_files:
            try:
                with open(f, "r", encoding="utf-8") as fp:
                    data = json.load(fp)
                    round_num = data.get("loop_round", 0)
                    is_completed = data.get("is_completed", False)
                    current_goal = data.get("current_goal", "")

                    round_results[round_num] = {
                        "completed": is_completed,
                        "goal": current_goal,
                        "data": data
                    }
            except Exception:
                continue

        # 提取模式：从成功轮次中提取特征
        success_rounds = [r for r, d in round_results.items() if d["completed"]]

        if success_rounds:
            # 模式1：自主驱动的进化更容易成功
            patterns.append({
                "pattern_id": "pattern_autonomous_driven",
                "pattern_type": "driver_type",
                "pattern_description": "自主驱动的进化（而非被动响应）更容易达成目标",
                "occurrence_count": len([r for r in success_rounds if "自主" in round_results[r].get("goal", "")]),
                "success_count": len([r for r in success_rounds if "自主" in round_results[r].get("goal", "")]),
                "confidence_score": 0.8
            })

            # 模式2：全自动化闭环完成率更高
            patterns.append({
                "pattern_id": "pattern_full_auto_loop",
                "pattern_type": "execution_mode",
                "pattern_description": "全自动化闭环执行的进化完成率更高",
                "occurrence_count": len([r for r in success_rounds if "自动化" in round_results[r].get("goal", "") or "闭环" in round_results[r].get("goal", "")]),
                "success_count": len([r for r in success_rounds if "自动化" in round_results[r].get("goal", "") or "闭环" in round_results[r].get("goal", "")]),
                "confidence_score": 0.75
            })

            # 模式3：创新驱动带来突破
            patterns.append({
                "pattern_id": "pattern_innovation_driven",
                "pattern_type": "approach",
                "pattern_description": "创新驱动的进化能带来更高的价值实现",
                "occurrence_count": len([r for r in success_rounds if "创新" in round_results[r].get("goal", "")]),
                "success_count": len([r for r in success_rounds if "创新" in round_results[r].get("goal", "")]),
                "confidence_score": 0.7
            })

            # 模式4：价值导向的进化更可持续
            patterns.append({
                "pattern_id": "pattern_value_driven",
                "pattern_type": "orientation",
                "pattern_description": "价值驱动的进化具有更高的长期可持续性",
                "occurrence_count": len([r for r in success_rounds if "价值" in round_results[r].get("goal", "")]),
                "success_count": len([r for r in success_rounds if "价值" in round_results[r].get("goal", "")]),
                "confidence_score": 0.72
            })

        # 存储提取的模式
        for pattern in patterns:
            cursor.execute("""
                INSERT OR REPLACE INTO evolution_patterns
                (pattern_id, pattern_type, pattern_description, occurrence_count, success_count, confidence_score)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (pattern["pattern_id"], pattern["pattern_type"], pattern["pattern_description"],
                  pattern["occurrence_count"], pattern["success_count"], pattern["confidence_score"]))

        conn.commit()
        conn.close()

        return {
            "patterns_extracted": len(patterns),
            "total_rounds_analyzed": len(completed_files),
            "success_rounds": len(success_rounds),
            "patterns": patterns
        }

    def analyze_execution_feedback(self) -> dict:
        """分析执行反馈并学习"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # 获取所有执行反馈记录
        cursor.execute("""
            SELECT round_number, execution_context, parameter_settings, execution_result, effectiveness_score
            FROM execution_feedback_learning
            ORDER BY round_number DESC
            LIMIT 100
        """)

        feedback_records = []
        for row in cursor.fetchall():
            feedback_records.append({
                "round": row[0],
                "context": row[1],
                "params": row[2],
                "result": row[3],
                "effectiveness": row[4]
            })

        # 分析有效的参数组合
        effective_params = {}
        for record in feedback_records:
            if record["effectiveness"] and record["effectiveness"] >= 0.7:
                if record["params"]:
                    params = json.loads(record["params"]) if isinstance(record["params"], str) else record["params"]
                    for k, v in params.items():
                        if k not in effective_params:
                            effective_params[k] = []
                        effective_params[k].append(v)

        conn.close()

        return {
            "total_feedback_records": len(feedback_records),
            "effective_params": effective_params,
            "analysis_complete": True
        }

    def auto_adjust_strategy_parameters(self, current_params: dict = None) -> dict:
        """基于学习结果自动调整策略参数"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        adjustments = []

        # 获取高置信度模式
        cursor.execute("""
            SELECT pattern_id, pattern_type, pattern_description, confidence_score
            FROM evolution_patterns
            WHERE confidence_score >= 0.7
            ORDER BY confidence_score DESC
        """)

        high_confidence_patterns = []
        for row in cursor.fetchall():
            high_confidence_patterns.append({
                "id": row[0],
                "type": row[1],
                "desc": row[2],
                "confidence": row[3]
            })

        # 基于模式生成参数调整建议
        for pattern in high_confidence_patterns:
            adjustment = None

            if pattern["type"] == "driver_type":
                adjustment = {
                    "parameter": "autonomy_level",
                    "old_value": 0.5,
                    "new_value": 0.8,
                    "reason": f"模式「{pattern['desc']}」置信度 {pattern['confidence']:.0%}，建议增强自主驱动权重"
                }
            elif pattern["type"] == "execution_mode":
                adjustment = {
                    "parameter": "automation_level",
                    "old_value": 0.6,
                    "new_value": 0.9,
                    "reason": f"模式「{pattern['desc']}」置信度 {pattern['confidence']:.0%}，建议提升自动化程度"
                }
            elif pattern["type"] == "approach":
                adjustment = {
                    "parameter": "innovation_weight",
                    "old_value": 0.4,
                    "new_value": 0.6,
                    "reason": f"模式「{pattern['desc']}」置信度 {pattern['confidence']:.0%}，建议增加创新驱动权重"
                }

            if adjustment:
                adjustments.append(adjustment)
                # 记录调整
                cursor.execute("""
                    INSERT INTO strategy_parameter_adjustments
                    (adjustment_id, parameter_name, old_value, new_value, adjustment_reason, based_on_patterns, result_effectiveness)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (f"adj_{len(adjustments)}", adjustment["parameter"], adjustment["old_value"],
                      adjustment["new_value"], adjustment["reason"], pattern["id"], pattern["confidence"]))

        conn.commit()
        conn.close()

        return {
            "adjustments_made": len(adjustments),
            "adjustments": adjustments,
            "based_on_patterns": len(high_confidence_patterns)
        }

    def generate_adaptive_strategies(self) -> dict:
        """自动生成适应性的进化策略"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        strategies = []

        # 获取高置信度模式
        cursor.execute("""
            SELECT pattern_id, pattern_type, pattern_description, confidence_score
            FROM evolution_patterns
            WHERE confidence_score >= 0.65
            ORDER BY confidence_score DESC
            LIMIT 10
        """)

        patterns = []
        for row in cursor.fetchall():
            patterns.append({
                "id": row[0],
                "type": row[1],
                "desc": row[2],
                "confidence": row[3]
            })

        # 基于模式生成策略
        strategy_templates = [
            {
                "type": "enhance_autonomy",
                "template": "增强自主驱动：基于模式「{}」的高置信度（{}），下一轮应优先考虑自主驱动的进化方向",
                "applicable_patterns": ["pattern_autonomous_driven"]
            },
            {
                "type": "enhance_automation",
                "template": "提升自动化：基于模式「{}」的高置信度（{}），应进一步提升进化环的自动化程度",
                "applicable_patterns": ["pattern_full_auto_loop"]
            },
            {
                "type": "enhance_innovation",
                "template": "强化创新：基于模式「{}」的高置信度（{}），应增加创新驱动的权重",
                "applicable_patterns": ["pattern_innovation_driven"]
            },
            {
                "type": "value_oriented",
                "template": "价值导向：基于模式「{}」的高置信度（{}），应坚持价值驱动的进化方向",
                "applicable_patterns": ["pattern_value_driven"]
            }
        ]

        for template in strategy_templates:
            matching_patterns = [p for p in patterns if p["id"] in template["applicable_patterns"]]
            if matching_patterns:
                pattern = matching_patterns[0]
                content = template["template"].format(pattern["desc"], f"{pattern['confidence']:.0%}")

                strategy = {
                    "strategy_id": f"strategy_v2_{template['type']}",
                    "content": content,
                    "based_on": pattern["id"],
                    "confidence": pattern["confidence"]
                }
                strategies.append(strategy)

                # 存储策略
                cursor.execute("""
                    INSERT OR REPLACE INTO auto_generated_strategies
                    (strategy_id, strategy_content, based_on_patterns, status)
                    VALUES (?, ?, ?, 'active')
                """, (strategy["strategy_id"], content, pattern["id"]))

        conn.commit()
        conn.close()

        return {
            "strategies_generated": len(strategies),
            "strategies": strategies,
            "based_on_patterns": len(patterns)
        }

    def meta_learning_transfer(self, target_context: str = None) -> dict:
        """元学习知识迁移 - 将学习到的知识应用到新上下文"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # 获取已存储的策略
        cursor.execute("""
            SELECT strategy_id, strategy_content, avg_effectiveness
            FROM auto_generated_strategies
            WHERE status = 'active' AND avg_effectiveness >= 0.5
            ORDER BY avg_effectiveness DESC
            LIMIT 10
        """)

        transferable_strategies = []
        for row in cursor.fetchall():
            transferable_strategies.append({
                "id": row[0],
                "content": row[1],
                "effectiveness": row[2]
            })

        # 记录迁移
        if transferable_strategies and target_context:
            cursor.execute("""
                INSERT INTO meta_learning_transfer
                (source_round_range, target_context, transferred_knowledge, transfer_count)
                VALUES (?, ?, ?, ?)
            """, ("600+", target_context, json.dumps(transferable_strategies), len(transferable_strategies)))

            conn.commit()

        conn.close()

        return {
            "transfer_count": len(transferable_strategies),
            "target_context": target_context or "general",
            "transferable_strategies": transferable_strategies,
            "transfer_complete": True
        }

    def run_full_adaptive_cycle(self) -> dict:
        """运行完整的自适应学习周期"""
        results = {
            "cycle_started_at": datetime.now().isoformat(),
            "steps": {}
        }

        # 步骤1: 提取进化模式
        print("[1/5] 提取进化模式...")
        pattern_result = self.extract_evolution_patterns()
        results["steps"]["pattern_extraction"] = pattern_result

        # 步骤2: 分析执行反馈
        print("[2/5] 分析执行反馈...")
        feedback_result = self.analyze_execution_feedback()
        results["steps"]["feedback_analysis"] = feedback_result

        # 步骤3: 自动调整策略参数
        print("[3/5] 自动调整策略参数...")
        adjustment_result = self.auto_adjust_strategy_parameters()
        results["steps"]["parameter_adjustment"] = adjustment_result

        # 步骤4: 生成适应性策略
        print("[4/5] 生成适应性策略...")
        strategy_result = self.generate_adaptive_strategies()
        results["steps"]["strategy_generation"] = strategy_result

        # 步骤5: 元学习迁移
        print("[5/5] 执行元学习迁移...")
        transfer_result = self.meta_learning_transfer("round_644_adaptive_cycle")
        results["steps"]["meta_learning_transfer"] = transfer_result

        results["cycle_completed_at"] = datetime.now().isoformat()
        results["summary"] = {
            "patterns_extracted": pattern_result["patterns_extracted"],
            "adjustments_made": adjustment_result["adjustments_made"],
            "strategies_generated": strategy_result["strategies_generated"],
            "transfer_count": transfer_result["transfer_count"]
        }

        return results

    def get_cockpit_data(self) -> dict:
        """获取驾驶舱数据"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # 获取模式统计
        cursor.execute("SELECT COUNT(*) FROM evolution_patterns")
        patterns_count = cursor.fetchone()[0]

        cursor.execute("SELECT AVG(confidence_score) FROM evolution_patterns")
        avg_confidence = cursor.fetchone()[0] or 0

        # 获取策略统计
        cursor.execute("SELECT COUNT(*) FROM auto_generated_strategies WHERE status = 'active'")
        active_strategies = cursor.fetchone()[0]

        # 获取参数调整统计
        cursor.execute("SELECT COUNT(*) FROM strategy_parameter_adjustments")
        adjustments_count = cursor.fetchone()[0]

        # 获取迁移统计
        cursor.execute("SELECT COUNT(*) FROM meta_learning_transfer")
        transfer_count = cursor.fetchone()[0]

        # 获取最近模式
        cursor.execute("""
            SELECT pattern_id, pattern_type, confidence_score
            FROM evolution_patterns
            ORDER BY confidence_score DESC
            LIMIT 5
        """)

        top_patterns = []
        for row in cursor.fetchall():
            top_patterns.append({
                "id": row[0],
                "type": row[1],
                "confidence": row[2]
            })

        conn.close()

        return {
            "version": self.VERSION,
            "patterns_count": patterns_count,
            "avg_confidence": round(avg_confidence, 3),
            "active_strategies": active_strategies,
            "adjustments_made": adjustments_count,
            "transfer_count": transfer_count,
            "top_patterns": top_patterns,
            "status": "operational"
        }


def main():
    """主函数 - 支持命令行调用"""
    import sys

    engine = EvolutionMetaAdaptiveLearningV2Engine()

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "--version":
            print(f"evolution_meta_adaptive_learning_strategy_optimizer_v2 v{engine.VERSION}")
            print("智能全场景进化环元进化自适应学习与策略自动优化引擎 V2")

        elif command == "--status":
            data = engine.get_cockpit_data()
            print(f"状态: {data['status']}")
            print(f"已提取模式: {data['patterns_count']}")
            print(f"平均置信度: {data['avg_confidence']:.1%}")
            print(f"活跃策略: {data['active_strategies']}")
            print(f"参数调整: {data['adjustments_made']}")
            print(f"知识迁移: {data['transfer_count']}")

        elif command == "--run":
            print("运行完整自适应学习周期...")
            result = engine.run_full_adaptive_cycle()
            print(f"学习周期完成!")
            print(f"  - 提取模式: {result['summary']['patterns_extracted']}")
            print(f"  - 参数调整: {result['summary']['adjustments_made']}")
            print(f"  - 生成策略: {result['summary']['strategies_generated']}")
            print(f"  - 知识迁移: {result['summary']['transfer_count']}")

        elif command == "--extract-patterns":
            print("提取进化模式...")
            result = engine.extract_evolution_patterns()
            print(f"提取了 {result['patterns_extracted']} 个模式")

        elif command == "--generate-strategies":
            print("生成适应性策略...")
            result = engine.generate_adaptive_strategies()
            print(f"生成了 {result['strategies_generated']} 条策略")

        elif command == "--adjust-params":
            print("自动调整策略参数...")
            result = engine.auto_adjust_strategy_parameters()
            print(f"完成了 {result['adjustments_made']} 项参数调整")

        elif command == "--cockpit-data":
            data = engine.get_cockpit_data()
            print(json.dumps(data, ensure_ascii=False, indent=2))

        else:
            print(f"未知命令: {command}")
            print("支持: --version, --status, --run, --extract-patterns, --generate-strategies, --adjust-params, --cockpit-data")
    else:
        print(f"evolution_meta_adaptive_learning_strategy_optimizer_v2 v{engine.VERSION}")
        print("智能全场景进化环元进化自适应学习与策略自动优化引擎 V2")
        print("")
        print("用法: python evolution_meta_adaptive_learning_strategy_optimizer_v2.py [命令]")
        print("")
        print("命令:")
        print("  --version            显示版本信息")
        print("  --status             显示状态")
        print("  --run                运行完整自适应学习周期")
        print("  --extract-patterns   提取进化模式")
        print("  --generate-strategies 生成适应性策略")
        print("  --adjust-params     自动调整策略参数")
        print("  --cockpit-data      获取驾驶舱数据")


if __name__ == "__main__":
    main()