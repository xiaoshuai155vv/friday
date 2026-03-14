#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环价值实现追踪深度量化引擎

在 round 318/323 的价值实现追踪能力基础上，进一步深化量化分析能力。
让系统能够精准量化每轮进化的真实价值贡献，建立价值评估指标体系，
将价值评估结果深度反馈到进化决策中，形成真正的价值驱动进化闭环。

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


class EvolutionValueQuantizationEngine:
    """进化环价值实现追踪深度量化引擎"""

    def __init__(self):
        """初始化引擎"""
        self.db_path = EVOLUTION_DB
        self._ensure_db()

    def _ensure_db(self):
        """确保数据库存在并创建价值指标表"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # 创建价值指标表（如果不存在）
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS value_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                round_num INTEGER,
                metric_name TEXT,
                metric_value REAL,
                unit TEXT,
                timestamp TEXT
            )
        """)
        conn.commit()
        conn.close()

    def get_connection(self):
        """获取数据库连接"""
        return sqlite3.connect(str(self.db_path))

    def calculate_value_metrics(self, round_num: int) -> Dict[str, Any]:
        """
        计算指定轮次的价值指标

        Args:
            round_num: 进化轮次

        Returns:
            价值指标字典
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        metrics = {
            "round": round_num,
            "timestamp": datetime.now().isoformat(),
            "efficiency_score": 0.0,
            "capability_gain": 0.0,
            "error_reduction": 0.0,
            "roi": 0.0,
            "overall_value": 0.0,
            "details": {}
        }

        try:
            # 获取进化历史（使用已有的 evolution_rounds 表）
            cursor.execute("""
                SELECT current_goal, status, execution_time, result
                FROM evolution_rounds
                WHERE round_number = ?
            """, (round_num,))
            row = cursor.fetchone()

            if row:
                goal, status, duration, result = row

                # 效率分数：基于执行时长
                if duration and duration > 0:
                    metrics["efficiency_score"] = min(100, 1000 / duration)

                # 能力增益：基于状态
                metrics["capability_gain"] = 50.0 if status == "completed" else 0.0

                # 错误减少：基于状态
                metrics["error_reduction"] = 100.0 if status == "completed" else 0.0

                # ROI 计算：假设每轮价值为50（完成状态）
                if status == "completed" and duration and duration > 0:
                    estimated_value = 50
                    cost = duration / 3600  # 转换为小时
                    metrics["roi"] = (estimated_value / cost) if cost > 0 else 0

                metrics["details"]["goal"] = goal
                metrics["details"]["status"] = status
                metrics["details"]["duration_seconds"] = duration

            # 计算整体价值（加权平均）
            weights = {"efficiency": 0.3, "capability": 0.3, "error_reduction": 0.4}
            metrics["overall_value"] = (
                metrics["efficiency_score"] * weights["efficiency"] +
                metrics["capability_gain"] * weights["capability"] +
                metrics["error_reduction"] * weights["error_reduction"]
            ) / 100

            # 存储指标到数据库
            for key in ["efficiency_score", "capability_gain", "error_reduction", "roi", "overall_value"]:
                if isinstance(metrics[key], (int, float)):
                    cursor.execute("""
                        INSERT INTO value_metrics (round_num, metric_name, metric_value, unit, timestamp)
                        VALUES (?, ?, ?, ?, ?)
                    """, (round_num, key, metrics[key], "%" if "score" in key or "reduction" in key else "value", datetime.now().isoformat()))

            conn.commit()

        except Exception as e:
            metrics["error"] = str(e)
        finally:
            conn.close()

        return metrics

    def analyze_value_trends(self, rounds: int = 10) -> Dict[str, Any]:
        """
        分析价值趋势

        Args:
            rounds: 分析的轮次数

        Returns:
            趋势分析结果
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        result = {
            "rounds_analyzed": rounds,
            "trend": "stable",
            "avg_value": 0.0,
            "value_change": 0.0,
            "top_rounds": [],
            "bottom_rounds": [],
            "insights": []
        }

        try:
            # 获取最近 N 轮的价值指标
            cursor.execute("""
                SELECT round_num, metric_name, metric_value
                FROM value_metrics
                WHERE metric_name = 'overall_value'
                ORDER BY round_num DESC
                LIMIT ?
            """, (rounds,))

            rows = cursor.fetchall()
            if not rows:
                # 如果没有存储的指标，从 evolution_rounds 动态计算
                cursor.execute("""
                    SELECT round_number, execution_time, status
                    FROM evolution_rounds
                    ORDER BY round_number DESC
                    LIMIT ?
                """, (rounds,))

                history_rows = cursor.fetchall()
                values = []
                for round_number, execution_time, status in history_rows:
                    # 简化的价值计算
                    value = 0
                    if status == "completed":
                        value += 50
                    if execution_time and execution_time > 0:
                        value += 1000 / execution_time  # 越快越高
                    values.append((round_number, value))

                if len(values) >= 2:
                    result["avg_value"] = sum(v[1] for v in values) / len(values)
                    result["value_change"] = values[0][1] - values[-1][1]
                    result["trend"] = "improving" if result["value_change"] > 0 else "declining"

                # 取前几轮
                values.sort(key=lambda x: x[1], reverse=True)
                result["top_rounds"] = [{"round": r[0], "value": r[1]} for r in values[:3]]
                result["bottom_rounds"] = [{"round": r[0], "value": r[1]} for r in values[-3:]]
            else:
                values = [(r[0], r[2]) for r in rows]
                if len(values) >= 2:
                    result["avg_value"] = sum(v[1] for v in values) / len(values)
                    result["value_change"] = values[0][1] - values[-1][1]
                    result["trend"] = "improving" if result["value_change"] > 5 else "declining" if result["value_change"] < -5 else "stable"

                values.sort(key=lambda x: x[1], reverse=True)
                result["top_rounds"] = [{"round": r[0], "value": r[1]} for r in values[:3]]
                result["bottom_rounds"] = [{"round": r[0], "value": r[1]} for r in values[-3:]]

            # 生成洞察
            if result["trend"] == "improving":
                result["insights"].append("进化环价值呈上升趋势，系统持续优化")
            elif result["trend"] == "declining":
                result["insights"].append("进化环价值呈下降趋势，建议检查进化策略")
            else:
                result["insights"].append("进化环价值保持稳定")

            if result["avg_value"] > 50:
                result["insights"].append("平均价值得分较高，系统进化效率良好")

        except Exception as e:
            result["error"] = str(e)
        finally:
            conn.close()

        return result

    def get_value_driven_recommendations(self) -> List[Dict[str, Any]]:
        """
        获取价值驱动的进化建议

        Returns:
            建议列表
        """
        recommendations = []

        try:
            # 分析趋势
            trends = self.analyze_value_trends(10)

            # 基于趋势生成建议
            if trends.get("trend") == "declining":
                recommendations.append({
                    "type": "strategy_adjustment",
                    "priority": "high",
                    "title": "调整进化策略",
                    "description": "价值趋势下降，建议重新评估进化方向和执行效率",
                    "action": "检查最近进化的目标和执行过程"
                })

            # 基于轮次分析
            if trends.get("bottom_rounds"):
                lowest = trends["bottom_rounds"][0]
                recommendations.append({
                    "type": "investigation",
                    "priority": "medium",
                    "title": f"调查 round {lowest['round']} 的低价值原因",
                    "description": f"该轮价值得分较低，需分析原因以避免类似情况",
                    "action": f"检查 round {lowest['round']} 的执行日志"
                })

            # 效率建议
            if trends.get("avg_value", 0) < 30:
                recommendations.append({
                    "type": "efficiency",
                    "priority": "high",
                    "title": "提升进化效率",
                    "description": "平均价值得分较低，建议优化执行策略",
                    "action": "考虑并行执行、减少重复、优化资源分配"
                })

            # 成功模式建议
            if trends.get("top_rounds"):
                top = trends["top_rounds"][0]
                recommendations.append({
                    "type": "pattern",
                    "priority": "low",
                    "title": f"学习 round {top['round']} 的成功模式",
                    "description": "该轮价值最高，分析其成功因素",
                    "action": "提取成功特征并应用到后续进化"
                })

            if not recommendations:
                recommendations.append({
                    "type": "maintain",
                    "priority": "low",
                    "title": "保持当前进化策略",
                    "description": "系统运行良好，继续当前方向",
                    "action": "按现有计划继续进化"
                })

        except Exception as e:
            recommendations.append({
                "type": "error",
                "priority": "medium",
                "title": "分析错误",
                "description": f"无法生成建议：{str(e)}",
                "action": "检查数据完整性"
            })

        return recommendations

    def get_quantized_value_summary(self) -> Dict[str, Any]:
        """
        获取量化价值摘要

        Returns:
            价值摘要
        """
        summary = {
            "generated_at": datetime.now().isoformat(),
            "total_rounds": 0,
            "average_value": 0.0,
            "trend": "unknown",
            "recommendations": []
        }

        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # 统计总轮次
            cursor.execute("SELECT COUNT(*) FROM evolution_rounds")
            summary["total_rounds"] = cursor.fetchone()[0] or 0

            # 计算平均价值
            cursor.execute("""
                SELECT AVG(metric_value)
                FROM value_metrics
                WHERE metric_name = 'overall_value'
            """)
            avg = cursor.fetchone()[0]
            if avg:
                summary["average_value"] = round(avg, 2)

            # 获取趋势
            trends = self.analyze_value_trends(10)
            summary["trend"] = trends.get("trend", "unknown")

            # 获取建议
            summary["recommendations"] = self.get_value_driven_recommendations()

        except Exception as e:
            summary["error"] = str(e)
        finally:
            conn.close()

        return summary

    def export_value_report(self, output_path: Optional[str] = None) -> str:
        """
        导出价值报告

        Args:
            output_path: 输出路径

        Returns:
            报告内容
        """
        summary = self.get_quantized_value_summary()
        trends = self.analyze_value_trends(10)
        recommendations = self.get_value_driven_recommendations()

        report = {
            "title": "进化环价值量化分析报告",
            "generated_at": summary["generated_at"],
            "summary": summary,
            "trends": trends,
            "recommendations": recommendations
        }

        report_json = json.dumps(report, indent=2, ensure_ascii=False)

        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report_json)

        return report_json


def handle_command(args: List[str]) -> Dict[str, Any]:
    """处理命令"""
    engine = EvolutionValueQuantizationEngine()

    if not args:
        return {"status": "error", "message": "需要子命令"}

    command = args[0].lower()

    if command == "status":
        # 返回价值摘要
        summary = engine.get_quantized_value_summary()
        return {
            "status": "ok",
            "message": "价值量化引擎状态",
            "data": summary
        }

    elif command == "analyze":
        # 分析指定轮次价值
        round_num = int(args[1]) if len(args) > 1 else None
        if round_num:
            metrics = engine.calculate_value_metrics(round_num)
            return {
                "status": "ok",
                "message": f"Round {round_num} 价值分析",
                "data": metrics
            }
        else:
            # 分析趋势
            trends = engine.analyze_value_trends()
            return {
                "status": "ok",
                "message": "价值趋势分析",
                "data": trends
            }

    elif command == "trends":
        # 获取价值趋势
        rounds = int(args[1]) if len(args) > 1 else 10
        trends = engine.analyze_value_trends(rounds)
        return {
            "status": "ok",
            "message": f"最近 {rounds} 轮价值趋势",
            "data": trends
        }

    elif command == "recommend" or command == "recommendations":
        # 获取价值驱动建议
        recommendations = engine.get_value_driven_recommendations()
        return {
            "status": "ok",
            "message": "价值驱动进化建议",
            "data": recommendations
        }

    elif command == "report":
        # 导出报告
        output_path = args[1] if len(args) > 1 else None
        report = engine.export_value_report(output_path)
        return {
            "status": "ok",
            "message": f"价值报告已生成" + (f" -> {output_path}" if output_path else ""),
            "data": json.loads(report)
        }

    elif command == "summary":
        # 简化的摘要
        summary = engine.get_quantized_value_summary()
        return {
            "status": "ok",
            "message": "价值量化摘要",
            "data": {
                "total_rounds": summary.get("total_rounds", 0),
                "average_value": summary.get("average_value", 0),
                "trend": summary.get("trend", "unknown"),
                "recommendations_count": len(summary.get("recommendations", []))
            }
        }

    else:
        return {
            "status": "error",
            "message": f"未知命令: {command}",
            "available_commands": ["status", "analyze", "trends", "recommend", "report", "summary"]
        }


def main():
    """主函数"""
    import sys

    args = sys.argv[1:] if len(sys.argv) > 1 else []

    if not args:
        # 无参数时显示简要信息
        engine = EvolutionValueQuantizationEngine()
        summary = engine.get_quantized_value_summary()
        print(f"智能全场景进化环价值实现追踪深度量化引擎 v1.0.0")
        print(f"总进化轮次: {summary.get('total_rounds', 0)}")
        print(f"平均价值得分: {summary.get('average_value', 0):.2f}")
        print(f"趋势: {summary.get('trend', 'unknown')}")
        return

    result = handle_command(args)

    if result["status"] == "ok":
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()