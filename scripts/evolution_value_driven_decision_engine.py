#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环价值驱动决策自动执行引擎

将 round 364 的价值量化能力与进化决策深度集成，
实现从"量化价值"→"自动决策"→"执行优化"→"效果验证"的完整价值驱动闭环。
系统能够基于价值评估结果自动选择进化方向、调整策略参数、优化执行路径。

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
EVOLUTION_DB = RUNTIME_STATE_DIR / "evolution_history.db"

# 尝试导入价值量化引擎
try:
    from evolution_value_quantization_engine import EvolutionValueQuantizationEngine
    VALUE_ENGINE_AVAILABLE = True
except ImportError:
    VALUE_ENGINE_AVAILABLE = False


class EvolutionValueDrivenDecisionEngine:
    """进化环价值驱动决策自动执行引擎"""

    # 决策阈值配置
    DEFAULT_CONFIG = {
        "value_threshold_high": 60.0,    # 高价值阈值
        "value_threshold_low": 30.0,      # 低价值阈值
        "efficiency_threshold": 50.0,      # 效率阈值
        "trend_threshold": 5.0,           # 趋势变化阈值
        "min_rounds_for_analysis": 3,    # 最小分析轮次
        "auto_adjust_enabled": True,       # 自动调整开关
        "decision_cooldown": 10,           # 决策冷却时间（分钟）
    }

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """初始化引擎"""
        self.db_path = EVOLUTION_DB
        self.config = {**self.DEFAULT_CONFIG, **(config or {})}
        self.value_engine = None
        if VALUE_ENGINE_AVAILABLE:
            try:
                self.value_engine = EvolutionValueQuantizationEngine()
            except Exception:
                pass
        self._ensure_db()
        self.last_decision_time = None

    def _ensure_db(self):
        """确保数据库存在并创建决策相关表"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # 创建价值驱动决策表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS value_driven_decisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                round_num INTEGER,
                decision_type TEXT,
                decision_reason TEXT,
                target_round INTEGER,
                parameters TEXT,
                result TEXT,
                value_before REAL,
                value_after REAL,
                timestamp TEXT
            )
        """)

        # 创建策略参数调整记录表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS strategy_parameter_adjustments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                parameter_name TEXT,
                old_value REAL,
                new_value REAL,
                reason TEXT,
                timestamp TEXT
            )
        """)

        conn.commit()
        conn.close()

    def get_connection(self):
        """获取数据库连接"""
        return sqlite3.connect(str(self.db_path))

    def analyze_value_for_decision(self, rounds: int = 10) -> Dict[str, Any]:
        """
        分析价值数据以支持决策

        Args:
            rounds: 分析的轮次数

        Returns:
            分析结果
        """
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "rounds_analyzed": rounds,
            "current_value": 0.0,
            "trend": "stable",
            "recommendations": [],
            "auto_actions": [],
            "status": "ok"
        }

        try:
            if self.value_engine:
                # 使用价值量化引擎进行分析
                trends = self.value_engine.analyze_value_trends(rounds)
                summary = self.value_engine.get_quantized_value_summary()

                analysis["current_value"] = summary.get("average_value", 0)
                analysis["trend"] = trends.get("trend", "stable")
                analysis["trend_details"] = trends

                # 基于分析生成决策建议
                self._generate_decision_recommendations(analysis, trends, summary)
            else:
                # 降级：从数据库直接读取
                analysis = self._fallback_analysis(rounds)

        except Exception as e:
            analysis["status"] = "error"
            analysis["error"] = str(e)

        return analysis

    def _fallback_analysis(self, rounds: int) -> Dict[str, Any]:
        """降级分析（当价值引擎不可用时）"""
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "rounds_analyzed": rounds,
            "current_value": 50.0,
            "trend": "stable",
            "recommendations": [],
            "auto_actions": [],
            "status": "degraded",
            "note": "价值引擎不可用，使用默认分析"
        }
        return analysis

    def _generate_decision_recommendations(
        self,
        analysis: Dict[str, Any],
        trends: Dict[str, Any],
        summary: Dict[str, Any]
    ):
        """基于分析生成决策建议"""
        recommendations = []
        auto_actions = []

        # 基于趋势的决策
        trend = analysis.get("trend", "stable")
        current_value = analysis.get("current_value", 0)

        if trend == "declining":
            recommendations.append({
                "type": "trend_correction",
                "priority": "high",
                "title": "价值趋势下降 - 需要干预",
                "description": "进化环价值呈下降趋势，建议立即调整进化策略",
                "suggested_actions": [
                    "检查最近进化的目标和执行效率",
                    "分析低价值轮次的原因",
                    "考虑回退到更保守的进化策略"
                ]
            })
            auto_actions.append({
                "action": "adjust_strategy",
                "reason": "trend_declining",
                "parameters": {"conservatism": 0.2}
            })

        elif trend == "improving" and current_value > self.config["value_threshold_high"]:
            recommendations.append({
                "type": "accelerate",
                "priority": "medium",
                "title": "价值上升 - 可以加速进化",
                "description": "系统表现优秀，可以考虑更激进的进化策略",
                "suggested_actions": [
                    "增加并行进化任务",
                    "尝试更复杂的目标",
                    "扩大探索范围"
                ]
            })
            auto_actions.append({
                "action": "accelerate_evolution",
                "reason": "trend_improving_high_value",
                "parameters": {"parallel_limit": 3}
            })

        # 基于当前价值的决策
        if current_value < self.config["value_threshold_low"]:
            recommendations.append({
                "type": "urgent_recovery",
                "priority": "critical",
                "title": "价值过低 - 需要紧急修复",
                "description": "当前价值低于阈值，需要立即调整",
                "suggested_actions": [
                    "暂停复杂进化任务",
                    "优先执行简单的优化任务",
                    "检查系统健康状态"
                ]
            })
            auto_actions.append({
                "action": "pause_complex",
                "reason": "value_too_low",
                "parameters": {"pause_until_value": 40}
            })

        # 基于效率的决策
        if trends.get("top_rounds"):
            top = trends["top_rounds"][0]
            recommendations.append({
                "type": "pattern_learning",
                "priority": "low",
                "title": f"学习 round {top['round']} 的成功模式",
                "description": "识别最高价值轮次的特征",
                "suggested_actions": [
                    "分析成功轮次的共同特征",
                    "提取可复制的策略参数"
                ]
            })

        # 如果没有明确问题，给出积极建议
        if not recommendations:
            recommendations.append({
                "type": "maintain",
                "priority": "low",
                "title": "系统运行良好",
                "description": "当前价值水平良好，保持现有策略",
                "suggested_actions": [
                    "继续当前进化方向",
                    "定期监控价值趋势"
                ]
            })

        analysis["recommendations"] = recommendations
        analysis["auto_actions"] = auto_actions

    def make_autonomous_decision(self) -> Dict[str, Any]:
        """
        基于价值分析做出自动决策

        Returns:
            决策结果
        """
        decision = {
            "timestamp": datetime.now().isoformat(),
            "decision_type": None,
            "parameters": {},
            "reason": "",
            "status": "no_action"
        }

        # 检查冷却时间
        if self.last_decision_time:
            cooldown_seconds = self.config.get("decision_cooldown", 10) * 60
            elapsed = (datetime.now() - self.last_decision_time).total_seconds()
            if elapsed < cooldown_seconds:
                decision["status"] = "cooldown"
                decision["reason"] = f"决策冷却中，剩余 {int(cooldown_seconds - elapsed)} 秒"
                return decision

        # 分析价值
        analysis = self.analyze_value_for_decision()
        auto_actions = analysis.get("auto_actions", [])

        # 执行自动动作
        if auto_actions and self.config.get("auto_adjust_enabled"):
            action = auto_actions[0]  # 取第一个建议动作
            decision["decision_type"] = action.get("action")
            decision["parameters"] = action.get("parameters", {})
            decision["reason"] = action.get("reason")
            decision["status"] = "executed"
            decision["analysis"] = analysis

            # 记录决策
            self._record_decision(analysis, decision)

            self.last_decision_time = datetime.now()
        else:
            decision["status"] = "no_auto_action"
            decision["reason"] = "无自动动作或自动调整已禁用"
            decision["recommendations"] = analysis.get("recommendations", [])

        return decision

    def _record_decision(self, analysis: Dict[str, Any], decision: Dict[str, Any]):
        """记录决策到数据库"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO value_driven_decisions
                (round_num, decision_type, decision_reason, result, value_before, value_after, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                analysis.get("rounds_analyzed", 0),
                decision.get("decision_type"),
                decision.get("reason"),
                json.dumps(decision.get("parameters", {})),
                analysis.get("current_value", 0),
                analysis.get("current_value", 0),  # 执行后价值需后续更新
                decision.get("timestamp")
            ))
            conn.commit()
        finally:
            conn.close()

    def adjust_strategy_parameters(self, adjustments: Dict[str, Any]) -> Dict[str, Any]:
        """
        调整策略参数

        Args:
            adjustments: 参数字典 {"参数名": 新值, ...}

        Returns:
            调整结果
        """
        result = {
            "timestamp": datetime.now().isoformat(),
            "adjustments": [],
            "status": "ok"
        }

        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            for param_name, new_value in adjustments.items():
                # 获取旧值（从配置或默认值）
                old_value = self.config.get(param_name, 0)

                # 记录调整
                cursor.execute("""
                    INSERT INTO strategy_parameter_adjustments
                    (parameter_name, old_value, new_value, reason, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    param_name,
                    old_value,
                    new_value,
                    "value_driven_adjustment",
                    datetime.now().isoformat()
                ))

                # 更新配置
                self.config[param_name] = new_value

                result["adjustments"].append({
                    "parameter": param_name,
                    "old_value": old_value,
                    "new_value": new_value
                })

            conn.commit()
            result["message"] = f"已调整 {len(adjustments)} 个参数"

        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
        finally:
            conn.close()

        return result

    def get_decision_status(self) -> Dict[str, Any]:
        """
        获取决策引擎状态

        Returns:
            状态信息
        """
        status = {
            "timestamp": datetime.now().isoformat(),
            "engine_version": "1.0.0",
            "config": self.config,
            "value_engine_available": self.value_engine is not None,
            "last_decision": None,
            "recent_decisions": [],
            "total_decisions": 0
        }

        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # 获取最近决策
            cursor.execute("""
                SELECT decision_type, decision_reason, timestamp
                FROM value_driven_decisions
                ORDER BY id DESC
                LIMIT 5
            """)
            rows = cursor.fetchall()
            status["recent_decisions"] = [
                {"type": r[0], "reason": r[1], "time": r[2]}
                for r in rows
            ]
            if rows:
                status["last_decision"] = status["recent_decisions"][0]

            # 统计总决策数
            cursor.execute("SELECT COUNT(*) FROM value_driven_decisions")
            status["total_decisions"] = cursor.fetchone()[0] or 0

            # 获取参数调整数
            cursor.execute("SELECT COUNT(*) FROM strategy_parameter_adjustments")
            status["total_adjustments"] = cursor.fetchone()[0] or 0

        except Exception as e:
            status["error"] = str(e)
        finally:
            conn.close()

        return status

    def run_full_cycle(self) -> Dict[str, Any]:
        """
        运行完整的价值驱动决策周期

        Returns:
            完整周期结果
        """
        cycle_result = {
            "timestamp": datetime.now().isoformat(),
            "steps": [],
            "final_value": 0.0,
            "status": "ok"
        }

        # Step 1: 分析价值
        analysis = self.analyze_value_for_decision()
        cycle_result["steps"].append({
            "step": "analyze",
            "status": analysis.get("status"),
            "current_value": analysis.get("current_value"),
            "trend": analysis.get("trend")
        })

        # Step 2: 做出决策
        decision = self.make_autonomous_decision()
        cycle_result["steps"].append({
            "step": "decide",
            "status": decision.get("status"),
            "decision_type": decision.get("decision_type"),
            "reason": decision.get("reason")
        })

        # Step 3: 应用建议
        recommendations = analysis.get("recommendations", [])
        cycle_result["steps"].append({
            "step": "recommend",
            "recommendations_count": len(recommendations),
            "top_recommendation": recommendations[0].get("title") if recommendations else None
        })

        # Step 4: 获取最终状态
        final_status = self.get_decision_status()
        cycle_result["steps"].append({
            "step": "status",
            "total_decisions": final_status.get("total_decisions", 0),
            "total_adjustments": final_status.get("total_adjustments", 0)
        })

        cycle_result["final_value"] = analysis.get("current_value", 0)
        return cycle_result


def handle_command(args: List[str]) -> Dict[str, Any]:
    """处理命令"""
    engine = EvolutionValueDrivenDecisionEngine()

    if not args:
        return {"status": "error", "message": "需要子命令"}

    command = args[0].lower()

    if command == "status":
        # 返回决策引擎状态
        status = engine.get_decision_status()
        return {
            "status": "ok",
            "message": "价值驱动决策引擎状态",
            "data": status
        }

    elif command == "analyze":
        # 分析价值并生成决策建议
        rounds = int(args[1]) if len(args) > 1 and args[1].isdigit() else 10
        analysis = engine.analyze_value_for_decision(rounds)
        return {
            "status": "ok",
            "message": f"价值分析 (最近 {rounds} 轮)",
            "data": analysis
        }

    elif command == "decide" or command == "auto-decide":
        # 自动做出决策
        decision = engine.make_autonomous_decision()
        return {
            "status": "ok",
            "message": "自动决策结果",
            "data": decision
        }

    elif command == "adjust":
        # 调整策略参数
        adjustments = {}
        i = 1
        while i < len(args):
            if "=" in args[i]:
                key, value = args[i].split("=", 1)
                try:
                    adjustments[key.strip()] = float(value.strip())
                except ValueError:
                    adjustments[key.strip()] = value.strip()
            i += 1

        if not adjustments:
            return {
                "status": "error",
                "message": "需要提供参数调整，格式: param1=value1 param2=value2"
            }

        result = engine.adjust_strategy_parameters(adjustments)
        return {
            "status": "ok",
            "message": "参数调整结果",
            "data": result
        }

    elif command == "cycle" or command == "full-cycle":
        # 运行完整周期
        result = engine.run_full_cycle()
        return {
            "status": "ok",
            "message": "完整价值驱动决策周期",
            "data": result
        }

    elif command == "recommend" or command == "recommendations":
        # 获取决策建议
        analysis = engine.analyze_value_for_decision()
        return {
            "status": "ok",
            "message": "价值驱动决策建议",
            "data": {
                "recommendations": analysis.get("recommendations", []),
                "auto_actions": analysis.get("auto_actions", [])
            }
        }

    else:
        return {
            "status": "error",
            "message": f"未知命令: {command}",
            "available_commands": ["status", "analyze", "decide", "adjust", "cycle", "recommend"]
        }


def main():
    """主函数"""
    import sys

    args = sys.argv[1:] if len(sys.argv) > 1 else []

    if not args:
        # 无参数时显示简要信息
        engine = EvolutionValueDrivenDecisionEngine()
        status = engine.get_decision_status()
        print(f"智能全场景进化环价值驱动决策自动执行引擎 v1.0.0")
        print(f"价值引擎可用: {status.get('value_engine_available', False)}")
        print(f"总决策数: {status.get('total_decisions', 0)}")
        print(f"总参数调整数: {status.get('total_adjustments', 0)}")
        print(f"最近决策: {status.get('last_decision', {}).get('type', '无')}")
        return

    result = handle_command(args)

    if result["status"] == "ok":
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()