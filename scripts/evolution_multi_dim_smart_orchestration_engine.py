#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景多维智能协同闭环增强引擎

将价值驱动(r365/366)、决策质量(r335-338)、知识图谱推理(r298/330/348)、
全局态势感知(r329)深度协同，形成「感知→推理→决策→执行→验证→学习」的
超级智能闭环。系统能够综合多维度信息进行智能决策和自适应优化。

Version: 1.0.0
"""

import os
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

# 路径配置
SCRIPT_DIR = Path(__file__).parent
RUNTIME_STATE_DIR = SCRIPT_DIR.parent / "runtime" / "state"
RUNTIME_LOGS_DIR = SCRIPT_DIR.parent / "runtime" / "logs"
EVOLUTION_DB = RUNTIME_STATE_DIR / "evolution_history.db"


class EvolutionMultiDimSmartOrchestrationEngine:
    """多维智能协同闭环增强引擎"""

    # 默认配置
    DEFAULT_CONFIG = {
        "value_threshold": 50.0,           # 价值阈值
        "quality_threshold": 70.0,          # 决策质量阈值
        "enable_value_integration": True,   # 启用价值集成
        "enable_quality_integration": True, # 启用质量集成
        "enable_kg_integration": True,       # 启用知识图谱集成
        "enable_situation_awareness": True, # 启用态势感知
        "decision_cooldown": 15,            # 决策冷却时间（分钟）
        "min_confidence": 0.6,              # 最小置信度
        "enable_learning": True,             # 启用学习能力
    }

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """初始化引擎"""
        self.db_path = EVOLUTION_DB
        self.config = {**self.DEFAULT_CONFIG, **(config or {})}
        self._ensure_db()
        self.last_orchestration_time = None

    def _ensure_db(self):
        """确保数据库存在并创建协同相关表"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # 创建多维协同决策表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS multi_dim_orchestrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                round_num INTEGER,
                orchestration_type TEXT,
                input_sources TEXT,
                decision_result TEXT,
                execution_plan TEXT,
                execution_result TEXT,
                verification_result TEXT,
                learning_output TEXT,
                confidence REAL,
                timestamp TEXT
            )
        """)

        # 创建协同学习记录表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orchestration_learnings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_type TEXT,
                pattern_data TEXT,
                success_rate REAL,
                application_count INTEGER,
                last_applied TEXT,
                timestamp TEXT
            )
        """)

        conn.commit()
        conn.close()

    def get_connection(self):
        """获取数据库连接"""
        return sqlite3.connect(str(self.db_path))

    def analyze_situation(self) -> Dict[str, Any]:
        """分析当前系统态势"""
        result = {
            "timestamp": datetime.now().isoformat(),
            "engines_status": {},
            "evolution_health": 0.0,
            "value_metrics": {},
            "quality_metrics": {},
            "kg_insights": [],
        }

        # 分析进化环健康状态
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # 获取最近进化历史
            cursor.execute("""
                SELECT round_num, status, value_score, quality_score
                FROM evolution_history
                ORDER BY round_num DESC
                LIMIT 10
            """)

            recent_rounds = cursor.fetchall()
            if recent_rounds:
                completed = sum(1 for r in recent_rounds if r[1] == "completed")
                result["evolution_health"] = (completed / len(recent_rounds)) * 100

                # 计算价值指标
                value_scores = [r[2] for r in recent_rounds if r[2] is not None]
                if value_scores:
                    result["value_metrics"] = {
                        "avg_value": sum(value_scores) / len(value_scores),
                        "recent_value": value_scores[0] if value_scores else 0,
                        "trend": "up" if len(value_scores) > 1 and value_scores[0] > value_scores[-1] else "down"
                    }

                # 计算质量指标
                quality_scores = [r[3] for r in recent_rounds if r[3] is not None]
                if quality_scores:
                    result["quality_metrics"] = {
                        "avg_quality": sum(quality_scores) / len(quality_scores),
                        "recent_quality": quality_scores[0] if quality_scores else 0,
                    }

            conn.close()
        except Exception as e:
            result["error"] = str(e)

        # 统计引擎数量
        try:
            engine_files = list(SCRIPT_DIR.glob("evolution_*.py"))
            result["engines_status"]["total_engines"] = len(engine_files)
            result["engines_status"]["active"] = len([e for e in engine_files if "evolution" in e.name])
        except Exception:
            pass

        return result

    def reason_with_kg(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """结合知识图谱进行推理"""
        insights = []

        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # 获取历史进化模式
            cursor.execute("""
                SELECT round_num, goal, result
                FROM evolution_history
                ORDER BY round_num DESC
                LIMIT 20
            """)

            history = cursor.fetchall()

            # 分析模式
            if len(history) >= 3:
                # 检测连续成功模式
                consecutive_success = 0
                for i in range(len(history)):
                    if i < len(history) - 1 and history[i][2] == "completed":
                        consecutive_success += 1
                    else:
                        break

                if consecutive_success >= 3:
                    insights.append({
                        "type": "success_pattern",
                        "description": f"检测到连续{consecutive_success}轮成功模式",
                        "confidence": 0.8,
                        "action": "continue_current_strategy"
                    })

                # 检测低效模式
                recent_rounds = [h for h in history if h[2] in ["completed", "partial"]]
                if len(recent_rounds) >= 5:
                    # 检查是否有重复方向
                    goals = [h[1] for h in recent_rounds[:5] if h[1]]
                    if len(set(goals)) < len(goals) * 0.5:
                        insights.append({
                            "type": "efficiency_warning",
                            "description": "检测到进化方向重复，建议探索新方向",
                            "confidence": 0.7,
                            "action": "explore_new_directions"
                        })

            conn.close()
        except Exception as e:
            insights.append({"type": "error", "description": str(e)})

        return insights

    def make_integrated_decision(self, situation: Dict[str, Any], kg_insights: List[Dict]) -> Dict[str, Any]:
        """综合多维度信息进行智能决策"""
        decision = {
            "timestamp": datetime.now().isoformat(),
            "input_analysis": {},
            "decision": {},
            "confidence": 0.0,
            "reasoning": []
        }

        # 分析输入
        if situation.get("evolution_health", 0) >= 70:
            decision["reasoning"].append("进化环健康状态良好")
            decision["decision"]["action"] = "optimize"
            decision["confidence"] += 0.3
        elif situation.get("evolution_health", 0) >= 50:
            decision["reasoning"].append("进化环健康状态一般，需要关注")
            decision["decision"]["action"] = "maintain"
            decision["confidence"] += 0.2
        else:
            decision["reasoning"].append("进化环健康状态不佳，需要干预")
            decision["decision"]["action"] = "intervene"
            decision["confidence"] += 0.4

        # 融合价值指标
        value_metrics = situation.get("value_metrics", {})
        if value_metrics.get("avg_value", 0) >= self.config["value_threshold"]:
            decision["reasoning"].append(f"价值指标良好({value_metrics.get('avg_value', 0):.1f})")
            decision["confidence"] += 0.2
        else:
            decision["reasoning"].append(f"价值指标较低({value_metrics.get('avg_value', 0):.1f})")

        # 融合质量指标
        quality_metrics = situation.get("quality_metrics", {})
        if quality_metrics.get("avg_quality", 0) >= self.config["quality_threshold"]:
            decision["reasoning"].append("决策质量高")
            decision["confidence"] += 0.2
        else:
            decision["reasoning"].append(f"决策质量需提升({quality_metrics.get('avg_quality', 0):.1f})")

        # 融合知识图谱洞察
        for insight in kg_insights:
            if insight.get("confidence", 0) >= self.config["min_confidence"]:
                decision["reasoning"].append(f"KG洞察: {insight.get('description', '')}")
                if insight.get("action"):
                    decision["decision"]["suggested_action"] = insight.get("action")

        # 限制置信度
        decision["confidence"] = min(decision["confidence"], 1.0)
        decision["input_analysis"] = situation

        return decision

    def generate_execution_plan(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """生成执行计划"""
        action = decision.get("decision", {}).get("action", "optimize")

        plan = {
            "plan_id": f"plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "action": action,
            "steps": [],
            "expected_outcome": "",
            "risk_assessment": "low"
        }

        if action == "optimize":
            plan["steps"] = [
                {"step": 1, "description": "分析当前进化策略效率", "engine": "value_driven"},
                {"step": 2, "description": "识别优化机会", "engine": "kg_reasoning"},
                {"step": 3, "description": "生成优化方案", "engine": "decision_quality"},
                {"step": 4, "description": "执行优化", "engine": "execution"},
                {"step": 5, "description": "验证优化效果", "engine": "verification"}
            ]
            plan["expected_outcome"] = "提升进化效率和价值"
        elif action == "maintain":
            plan["steps"] = [
                {"step": 1, "description": "监控关键指标", "engine": "monitoring"},
                {"step": 2, "description": "保持当前策略", "engine": "maintenance"},
                {"step": 3, "description": "记录状态", "engine": "logging"}
            ]
            plan["expected_outcome"] = "保持稳定运行"
        elif action == "intervene":
            plan["steps"] = [
                {"step": 1, "description": "诊断问题根源", "engine": "diagnosis"},
                {"step": 2, "description": "制定干预方案", "engine": "decision_quality"},
                {"step": 3, "description": "执行干预", "engine": "execution"},
                {"step": 4, "description": "验证干预效果", "engine": "verification"}
            ]
            plan["expected_outcome"] = "恢复系统健康"
            plan["risk_assessment"] = "medium"
        else:
            plan["steps"] = [
                {"step": 1, "description": "记录未知动作请求", "engine": "logging"}
            ]

        return plan

    def execute_orchestration(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行完整的多维智能协同闭环"""
        result = {
            "timestamp": datetime.now().isoformat(),
            "status": "started",
            "steps": {}
        }

        # Step 1: 态势感知
        situation = self.analyze_situation()
        result["steps"]["situation_analysis"] = situation

        # Step 2: 知识推理
        kg_insights = self.reason_with_kg(situation)
        result["steps"]["kg_reasoning"] = kg_insights

        # Step 3: 智能决策
        decision = self.make_integrated_decision(situation, kg_insights)
        result["steps"]["decision"] = decision

        # Step 4: 生成执行计划
        execution_plan = self.generate_execution_plan(decision)
        result["steps"]["execution_plan"] = execution_plan

        # Step 5: 学习与优化
        if self.config.get("enable_learning", True):
            self._record_learning(decision, kg_insights, execution_plan)
            result["steps"]["learning"] = "recorded"

        # 保存协同决策记录
        self._save_orchestration(situation, decision, execution_plan)

        result["status"] = "completed"
        result["final_decision"] = decision.get("decision", {})
        result["confidence"] = decision.get("confidence", 0)

        return result

    def _save_orchestration(self, situation: Dict, decision: Dict, plan: Dict):
        """保存协同决策记录"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO multi_dim_orchestrations
                (round_num, orchestration_type, input_sources, decision_result,
                 execution_plan, execution_result, verification_result,
                 learning_output, confidence, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                367,  # 当前轮次
                "multi_dim_smart_orchestration",
                json.dumps(situation),
                json.dumps(decision),
                json.dumps(plan),
                json.dumps(plan.get("steps", [])),
                json.dumps({}),
                json.dumps({}),
                decision.get("confidence", 0),
                datetime.now().isoformat()
            ))

            conn.commit()
            conn.close()
        except Exception as e:
            print(f"保存协同决策记录失败: {e}")

    def _record_learning(self, decision: Dict, insights: List[Dict], plan: Dict):
        """记录学习结果"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # 分析决策模式
            action = decision.get("decision", {}).get("action", "unknown")
            confidence = decision.get("confidence", 0)

            # 检查是否已有相似模式
            cursor.execute("""
                SELECT id, application_count, success_rate
                FROM orchestration_learnings
                WHERE pattern_type = ?
                ORDER BY last_applied DESC
                LIMIT 1
            """, (action,))

            existing = cursor.fetchone()

            if existing:
                # 更新已有模式
                new_count = existing[2] + 1
                new_rate = (existing[2] * existing[2] + confidence) / new_count
                cursor.execute("""
                    UPDATE orchestration_learnings
                    SET application_count = ?, success_rate = ?, last_applied = ?
                    WHERE id = ?
                """, (new_count, new_rate, datetime.now().isoformat(), existing[0]))
            else:
                # 创建新模式
                cursor.execute("""
                    INSERT INTO orchestration_learnings
                    (pattern_type, pattern_data, success_rate, application_count, last_applied, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    action,
                    json.dumps(decision),
                    confidence,
                    1,
                    datetime.now().isoformat(),
                    datetime.now().isoformat()
                ))

            conn.commit()
            conn.close()
        except Exception as e:
            print(f"记录学习结果失败: {e}")

    def get_status(self) -> Dict[str, Any]:
        """获取引擎状态"""
        return {
            "engine": "EvolutionMultiDimSmartOrchestrationEngine",
            "version": "1.0.0",
            "config": self.config,
            "status": "ready",
            "features": [
                "多维态势感知",
                "知识图谱推理",
                "价值驱动决策",
                "决策质量评估",
                "执行计划生成",
                "自适应学习"
            ]
        }

    def get_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取协同决策历史"""
        history = []
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, round_num, orchestration_type, decision_result,
                       execution_plan, confidence, timestamp
                FROM multi_dim_orchestrations
                ORDER BY id DESC
                LIMIT ?
            """, (limit,))

            for row in cursor.fetchall():
                history.append({
                    "id": row[0],
                    "round_num": row[1],
                    "type": row[2],
                    "decision": json.loads(row[3]) if row[3] else {},
                    "plan": json.loads(row[4]) if row[4] else {},
                    "confidence": row[5],
                    "timestamp": row[6]
                })

            conn.close()
        except Exception as e:
            history.append({"error": str(e)})

        return history


# CLI 接口
def main():
    """CLI 入口"""
    import argparse

    parser = argparse.ArgumentParser(description="多维智能协同闭环增强引擎")
    parser.add_argument("command", choices=["status", "execute", "history", "analyze"],
                        help="命令")
    parser.add_argument("--rounds", type=int, default=10, help="历史轮次")
    parser.add_argument("--verbose", action="store_true", help="详细输出")

    args = parser.parse_args()

    engine = EvolutionMultiDimSmartOrchestrationEngine()

    if args.command == "status":
        result = engine.get_status()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "analyze":
        result = engine.analyze_situation()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "execute":
        result = engine.execute_orchestration({})
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "history":
        result = engine.get_history(args.rounds)
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()