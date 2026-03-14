#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环价值驱动自动执行闭环引擎

将 round 365 的价值驱动决策自动执行引擎与进化环深度集成，
实现从价值分析→智能决策→自动执行→效果验证→价值反馈的完整闭环。
让进化环能够基于价值评估自主决定是否执行、如何执行、什么时候执行，
形成真正的价值驱动自动进化能力，超越被动响应式的进化模式。

Version: 1.0.0
"""

import os
import json
import sqlite3
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import threading
import time

# 路径配置
SCRIPT_DIR = Path(__file__).parent
RUNTIME_STATE_DIR = SCRIPT_DIR.parent / "runtime" / "state"
EVOLUTION_DB = RUNTIME_STATE_DIR / "evolution_history.db"

# 尝试导入相关引擎
try:
    from evolution_value_driven_decision_engine import EvolutionValueDrivenDecisionEngine
    DECISION_ENGINE_AVAILABLE = True
except ImportError:
    DECISION_ENGINE_AVAILABLE = False

try:
    from evolution_full_auto_loop import EvolutionFullAutoLoop
    FULL_AUTO_LOOP_AVAILABLE = True
except ImportError:
    FULL_AUTO_LOOP_AVAILABLE = False


class EvolutionValueDrivenLoopIntegration:
    """进化环价值驱动自动执行闭环引擎"""

    # 配置默认值
    DEFAULT_CONFIG = {
        "auto_trigger_enabled": True,          # 自动触发开关
        "value_threshold_for_trigger": 40.0,    # 触发自动进化的价值阈值
        "min_interval_minutes": 30,              # 最小触发间隔（分钟）
        "max_auto_rounds_per_day": 5,            # 每天最大自动触发轮次
        "execution_mode": "auto",                # 执行模式: auto(自动) / semi-auto(半自动) / manual(手动)
        "feedback_learning_enabled": True,        # 价值反馈学习开关
        "consecutive_low_value_threshold": 3,    # 连续低价值阈值，触发策略调整
    }

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """初始化引擎"""
        self.db_path = EVOLUTION_DB
        self.config = {**self.DEFAULT_CONFIG, **(config or {})}
        self.decision_engine = None
        self.full_auto_loop = None

        # 初始化子引擎
        if DECISION_ENGINE_AVAILABLE:
            try:
                self.decision_engine = EvolutionValueDrivenDecisionEngine()
            except Exception:
                pass

        if FULL_AUTO_LOOP_AVAILABLE:
            try:
                self.full_auto_loop = EvolutionFullAutoLoop()
            except Exception:
                pass

        self._ensure_db()
        self.last_trigger_time = None
        self.trigger_count_today = 0
        self.last_trigger_date = None

    def _ensure_db(self):
        """确保数据库存在并创建相关表"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # 创建价值驱动闭环执行记录表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS value_driven_loop_executions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trigger_type TEXT,
                value_before REAL,
                value_after REAL,
                decision_result TEXT,
                execution_result TEXT,
                feedback_learning REAL,
                timestamp TEXT
            )
        """)

        # 创建价值反馈学习记录表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS value_feedback_learning (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                round_num INTEGER,
                execution_type TEXT,
                value_delta REAL,
                learnings TEXT,
                timestamp TEXT
            )
        """)

        conn.commit()
        conn.close()

    def get_connection(self):
        """获取数据库连接"""
        return sqlite3.connect(str(self.db_path))

    def check_auto_trigger_conditions(self) -> Dict[str, Any]:
        """
        检查是否满足自动触发条件

        Returns:
            检查结果
        """
        conditions = {
            "timestamp": datetime.now().isoformat(),
            "can_trigger": False,
            "reasons": [],
            "blocked_reasons": [],
            "value_status": None
        }

        # 检查 1: 自动触发开关是否开启
        if not self.config.get("auto_trigger_enabled"):
            conditions["blocked_reasons"].append("自动触发开关已关闭")
            return conditions

        # 检查 2: 每日触发次数限制
        today = datetime.now().date()
        if self.last_trigger_date != today:
            self.trigger_count_today = 0
            self.last_trigger_date = today

        if self.trigger_count_today >= self.config.get("max_auto_rounds_per_day", 5):
            conditions["blocked_reasons"].append(f"已达到每日最大触发次数 ({self.config.get('max_auto_rounds_per_day', 5)})")
            return conditions

        # 检查 3: 最小间隔
        if self.last_trigger_time:
            elapsed_minutes = (datetime.now() - self.last_trigger_time).total_seconds() / 60
            if elapsed_minutes < self.config.get("min_interval_minutes", 30):
                conditions["blocked_reasons"].append(f"距离上次触发时间不足 ({self.config.get('min_interval_minutes', 30)} 分钟)")
                return conditions

        # 检查 4: 价值状态（核心条件）
        if self.decision_engine:
            analysis = self.decision_engine.analyze_value_for_decision()
            value = analysis.get("current_value", 0)
            trend = analysis.get("trend", "stable")

            conditions["value_status"] = {
                "current_value": value,
                "trend": trend,
                "recommendations": analysis.get("recommendations", [])
            }

            threshold = self.config.get("value_threshold_for_trigger", 40.0)

            # 基于价值的触发逻辑
            if value < threshold:
                conditions["reasons"].append(f"当前价值 {value:.1f} 低于阈值 {threshold}，需要进化")
                conditions["can_trigger"] = True
            elif trend == "declining":
                conditions["reasons"].append("价值趋势下降，需要干预")
                conditions["can_trigger"] = True
            elif trend == "improving" and value > threshold * 1.5:
                conditions["reasons"].append(f"价值表现优秀({value:.1f})，可以加速进化")
                conditions["can_trigger"] = True
        else:
            conditions["blocked_reasons"].append("决策引擎不可用")
            return conditions

        return conditions

    def execute_value_driven_evolution(self) -> Dict[str, Any]:
        """
        执行价值驱动的自动进化

        Returns:
            执行结果
        """
        result = {
            "timestamp": datetime.now().isoformat(),
            "trigger_type": None,
            "value_before": 0.0,
            "value_after": 0.0,
            "decision_result": None,
            "execution_result": None,
            "status": "ok"
        }

        # Step 1: 检查触发条件
        conditions = self.check_auto_trigger_conditions()
        result["conditions"] = conditions

        if not conditions.get("can_trigger"):
            result["status"] = "blocked"
            result["message"] = conditions.get("blocked_reasons", ["条件不满足"])
            return result

        result["trigger_type"] = "auto_value_driven"
        result["reasons"] = conditions.get("reasons", [])

        # 获取执行前价值
        if self.decision_engine:
            before_analysis = self.decision_engine.analyze_value_for_decision()
            result["value_before"] = before_analysis.get("current_value", 0)

        # Step 2: 做决策
        if self.decision_engine:
            decision = self.decision_engine.make_autonomous_decision()
            result["decision_result"] = decision
        else:
            result["decision_result"] = {"status": "degraded", "message": "决策引擎不可用"}

        # Step 3: 执行进化（如果有自动化引擎）
        if self.full_auto_loop:
            try:
                execution = self.full_auto_loop.run_evolution_cycle()
                result["execution_result"] = execution
            except Exception as e:
                result["execution_result"] = {"status": "error", "message": str(e)}
        else:
            result["execution_result"] = {"status": "skipped", "message": "全自动化引擎不可用"}

        # Step 4: 获取执行后价值
        if self.decision_engine:
            after_analysis = self.decision_engine.analyze_value_for_decision()
            result["value_after"] = after_analysis.get("current_value", 0)

        # Step 5: 价值反馈学习
        if self.config.get("feedback_learning_enabled"):
            feedback = self._perform_feedback_learning(result)
            result["feedback_learning"] = feedback

        # Step 6: 更新触发状态
        self.last_trigger_time = datetime.now()
        self.trigger_count_today += 1

        # Step 7: 记录执行
        self._record_execution(result)

        return result

    def _perform_feedback_learning(self, execution_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行价值反馈学习

        Args:
            execution_result: 执行结果

        Returns:
            学习结果
        """
        learning = {
            "timestamp": datetime.now().isoformat(),
            "value_delta": 0.0,
            "learnings": [],
            "status": "ok"
        }

        try:
            value_before = execution_result.get("value_before", 0)
            value_after = execution_result.get("value_after", 0)
            value_delta = value_after - value_before
            learning["value_delta"] = value_delta

            # 分析学习点
            if value_delta > 10:
                learning["learnings"].append("本次进化显著提升了价值，策略有效")
            elif value_delta > 0:
                learning["learnings"].append("本次进化小幅提升价值，可保持当前策略")
            elif value_delta > -5:
                learning["learnings"].append("本次进化价值变化不大，可考虑调整")
            else:
                learning["learnings"].append("本次进化导致价值下降，需要回退或调整策略")

            # 检查趋势
            value_status = execution_result.get("conditions", {}).get("value_status", {})
            trend = value_status.get("trend", "stable")

            if trend == "declining" and value_delta < 0:
                learning["learnings"].append("连续下降趋势，应采取保守策略")

            # 根据学习结果调整配置
            if self.config.get("feedback_learning_enabled"):
                self._adjust_based_on_learning(learning)

            # 记录学习结果
            self._record_learning(learning)

        except Exception as e:
            learning["status"] = "error"
            learning["error"] = str(e)

        return learning

    def _adjust_based_on_learning(self, learning: Dict[str, Any]):
        """基于学习结果调整配置"""
        value_delta = learning.get("value_delta", 0)

        if value_delta < -10:
            # 价值显著下降，增加保守度
            current_threshold = self.config.get("value_threshold_for_trigger", 40.0)
            self.config["value_threshold_for_trigger"] = current_threshold + 10
            learning["config_adjustments"] = {
                "value_threshold_for_trigger": f"{current_threshold} -> {current_threshold + 10}"
            }

        elif value_delta > 20:
            # 价值显著提升，可以更激进
            current_threshold = self.config.get("value_threshold_for_trigger", 40.0)
            if current_threshold > 30:
                self.config["value_threshold_for_trigger"] = current_threshold - 5
                learning["config_adjustments"] = {
                    "value_threshold_for_trigger": f"{current_threshold} -> {current_threshold - 5}"
                }

    def _record_execution(self, execution_result: Dict[str, Any]):
        """记录执行结果到数据库"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO value_driven_loop_executions
                (trigger_type, value_before, value_after, decision_result, execution_result, feedback_learning, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                execution_result.get("trigger_type"),
                execution_result.get("value_before", 0),
                execution_result.get("value_after", 0),
                json.dumps(execution_result.get("decision_result", {})),
                json.dumps(execution_result.get("execution_result", {})),
                json.dumps(execution_result.get("feedback_learning", {})),
                execution_result.get("timestamp")
            ))
            conn.commit()
        finally:
            conn.close()

    def _record_learning(self, learning: Dict[str, Any]):
        """记录学习结果到数据库"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO value_feedback_learning
                (round_num, execution_type, value_delta, learnings, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (
                0,  # round_num 需要从执行结果中获取
                "value_driven_auto",
                learning.get("value_delta", 0),
                json.dumps(learning.get("learnings", [])),
                learning.get("timestamp")
            ))
            conn.commit()
        finally:
            conn.close()

    def get_status(self) -> Dict[str, Any]:
        """
        获取引擎状态

        Returns:
            状态信息
        """
        status = {
            "timestamp": datetime.now().isoformat(),
            "engine_version": "1.0.0",
            "config": self.config,
            "decision_engine_available": self.decision_engine is not None,
            "full_auto_loop_available": self.full_auto_loop is not None,
            "trigger_conditions": None,
            "recent_executions": [],
            "total_executions": 0
        }

        # 获取触发条件
        conditions = self.check_auto_trigger_conditions()
        status["trigger_conditions"] = conditions

        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # 获取最近执行
            cursor.execute("""
                SELECT trigger_type, value_before, value_after, timestamp
                FROM value_driven_loop_executions
                ORDER BY id DESC
                LIMIT 5
            """)
            rows = cursor.fetchall()
            status["recent_executions"] = [
                {"type": r[0], "value_before": r[1], "value_after": r[2], "time": r[3]}
                for r in rows
            ]

            # 统计总数
            cursor.execute("SELECT COUNT(*) FROM value_driven_loop_executions")
            status["total_executions"] = cursor.fetchone()[0] or 0

            # 今日触发次数
            today = datetime.now().date()
            if self.last_trigger_date == today:
                status["trigger_count_today"] = self.trigger_count_today
            else:
                status["trigger_count_today"] = 0

        except Exception as e:
            status["error"] = str(e)
        finally:
            conn.close()

        return status

    def run_full_closed_loop(self) -> Dict[str, Any]:
        """
        运行完整的价值驱动闭环

        Returns:
            完整闭环结果
        """
        closed_loop_result = {
            "timestamp": datetime.now().isoformat(),
            "steps": [],
            "final_value": 0.0,
            "status": "ok"
        }

        # Step 1: 检查条件
        conditions = self.check_auto_trigger_conditions()
        closed_loop_result["steps"].append({
            "step": "check_conditions",
            "can_trigger": conditions.get("can_trigger"),
            "reasons": conditions.get("reasons", []),
            "blocked_reasons": conditions.get("blocked_reasons", [])
        })

        # Step 2: 如果可触发则执行
        if conditions.get("can_trigger"):
            execution = self.execute_value_driven_evolution()
            closed_loop_result["steps"].append({
                "step": "execute",
                "status": execution.get("status"),
                "value_before": execution.get("value_before"),
                "value_after": execution.get("value_after"),
                "value_delta": execution.get("value_after", 0) - execution.get("value_before", 0)
            })

            # Step 3: 反馈学习
            if execution.get("feedback_learning"):
                closed_loop_result["steps"].append({
                    "step": "feedback_learning",
                    "value_delta": execution.get("feedback_learning", {}).get("value_delta"),
                    "learnings_count": len(execution.get("feedback_learning", {}).get("learnings", []))
                })

            closed_loop_result["final_value"] = execution.get("value_after", 0)
        else:
            closed_loop_result["steps"].append({
                "step": "execute",
                "status": "skipped",
                "reason": conditions.get("blocked_reasons", ["条件不满足"])
            })
            closed_loop_result["status"] = "skipped"

        # Step 4: 获取最终状态
        final_status = self.get_status()
        closed_loop_result["steps"].append({
            "step": "status",
            "total_executions": final_status.get("total_executions", 0),
            "trigger_count_today": final_status.get("trigger_count_today", 0)
        })

        return closed_loop_result


def handle_command(args: List[str]) -> Dict[str, Any]:
    """处理命令"""
    engine = EvolutionValueDrivenLoopIntegration()

    if not args:
        return {"status": "error", "message": "需要子命令"}

    command = args[0].lower()

    if command == "status":
        # 返回引擎状态
        status = engine.get_status()
        return {
            "status": "ok",
            "message": "价值驱动自动执行闭环引擎状态",
            "data": status
        }

    elif command == "check" or command == "conditions":
        # 检查触发条件
        conditions = engine.check_auto_trigger_conditions()
        return {
            "status": "ok",
            "message": "自动触发条件检查",
            "data": conditions
        }

    elif command == "execute" or command == "run":
        # 执行价值驱动进化
        result = engine.execute_value_driven_evolution()
        return {
            "status": "ok",
            "message": "价值驱动进化执行结果",
            "data": result
        }

    elif command == "loop" or command == "closed-loop":
        # 运行完整闭环
        result = engine.run_full_closed_loop()
        return {
            "status": "ok",
            "message": "完整价值驱动闭环",
            "data": result
        }

    elif command == "enable":
        # 开启自动触发
        engine.config["auto_trigger_enabled"] = True
        return {
            "status": "ok",
            "message": "已开启自动触发"
        }

    elif command == "disable":
        # 关闭自动触发
        engine.config["auto_trigger_enabled"] = False
        return {
            "status": "ok",
            "message": "已关闭自动触发"
        }

    elif command == "config":
        # 查看/修改配置
        if len(args) > 1 and "=" in args[1]:
            key, value = args[1].split("=", 1)
            try:
                engine.config[key.strip()] = float(value.strip())
            except ValueError:
                engine.config[key.strip()] = value.strip()
            return {
                "status": "ok",
                "message": f"已设置 {key} = {value}"
            }
        else:
            return {
                "status": "ok",
                "message": "当前配置",
                "data": engine.config
            }

    else:
        return {
            "status": "error",
            "message": f"未知命令: {command}",
            "available_commands": ["status", "check", "execute", "loop", "enable", "disable", "config"]
        }


def main():
    """主函数"""
    import sys

    args = sys.argv[1:] if len(sys.argv) > 1 else []

    if not args:
        # 无参数时显示简要信息
        engine = EvolutionValueDrivenLoopIntegration()
        status = engine.get_status()
        print(f"智能全场景进化环价值驱动自动执行闭环引擎 v1.0.0")
        print(f"决策引擎可用: {status.get('decision_engine_available', False)}")
        print(f"全自动化引擎可用: {status.get('full_auto_loop_available', False)}")
        print(f"自动触发开启: {status.get('config', {}).get('auto_trigger_enabled', False)}")
        print(f"总执行次数: {status.get('total_executions', 0)}")
        print(f"今日触发次数: {status.get('trigger_count_today', 0)}")

        conditions = status.get("trigger_conditions", {})
        print(f"可触发: {conditions.get('can_trigger', False)}")
        if conditions.get("reasons"):
            print(f"触发原因: {conditions.get('reasons', [])}")
        return

    result = handle_command(args)

    if result["status"] == "ok":
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()