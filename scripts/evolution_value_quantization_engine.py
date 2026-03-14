#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环价值实现追踪深度量化引擎（增强版）

在 round 318/323 的价值实现追踪能力基础上，进一步深化量化分析能力。
让系统能够精准量化每轮进化的真实价值贡献，建立价值评估指标体系，
将价值评估结果深度反馈到进化决策中，形成真正的价值驱动进化闭环。

Round 438 增强：
1. 新增价值驱动自动优化建议生成功能（generate_optimization_recommendations）
2. 新增跨轮价值模式发现功能（discover_value_patterns）
3. 新增价值预测功能（predict_future_value）
4. 新增与进化驾驶舱深度集成（get_cockpit_metrics）
5. 新增价值阈值自动调整功能（auto_adjust_thresholds）
6. 新增完整价值闭环验证（validate_value_closed_loop）

Version: 1.1.0
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

    # ============ Round 438 新增功能 ============

    def generate_optimization_recommendations(self) -> List[Dict[str, Any]]:
        """
        生成价值驱动的自动优化建议（增强版）

        基于价值评估结果，自动生成可执行的优化建议，
        并将这些建议与进化决策深度集成。

        Returns:
            优化建议列表
        """
        recommendations = []
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # 获取最近 N 轮数据
            cursor.execute("""
                SELECT round_number, current_goal, status, execution_time, result
                FROM evolution_rounds
                ORDER BY round_number DESC
                LIMIT 20
            """)
            rounds = cursor.fetchall()

            if not rounds:
                return [{
                    "type": "no_data",
                    "priority": "low",
                    "title": "暂无进化数据",
                    "description": "系统暂无足够的历史进化数据进行分析",
                    "action": "等待更多进化轮次完成"
                }]

            # 分析低效轮次
            low_efficiency_rounds = [
                r for r in rounds
                if r[3] and r[3] > 300  # 执行时间超过 5 分钟
            ]

            if low_efficiency_rounds:
                recommendations.append({
                    "type": "efficiency_optimization",
                    "priority": "high",
                    "title": "检测到低效率进化轮次",
                    "description": f"发现 {len(low_efficiency_rounds)} 轮执行时间过长，建议优化执行策略",
                    "action": "分析低效原因，考虑并行执行或简化流程",
                    "affected_rounds": [r[0] for r in low_efficiency_rounds[:5]]
                })

            # 分析失败轮次
            failed_rounds = [r for r in rounds if r[2] != "completed"]
            if failed_rounds:
                recommendations.append({
                    "type": "failure_recovery",
                    "priority": "high",
                    "title": "检测到未完成进化",
                    "description": f"发现 {len(failed_rounds)} 轮未完成，需分析失败原因",
                    "action": "检查失败轮次的执行日志，修复问题",
                    "affected_rounds": [r[0] for r in failed_rounds[:5]]
                })

            # 分析成功模式
            completed_rounds = [r for r in rounds if r[2] == "completed"]
            if completed_rounds:
                avg_time = sum(r[3] for r in completed_rounds if r[3]) / len(completed_rounds)
                fast_rounds = [r for r in completed_rounds if r[3] and r[3] < avg_time * 0.7]

                if fast_rounds:
                    recommendations.append({
                        "type": "success_pattern",
                        "priority": "medium",
                        "title": "发现高效进化模式",
                        "description": f"有 {len(fast_rounds)} 轮执行效率高于平均，建议提取成功特征",
                        "action": "分析快速完成的轮次，找出成功因素",
                        "model_rounds": [r[0] for r in fast_rounds[:3]]
                    })

            # 价值趋势建议
            trends = self.analyze_value_trends(10)
            if trends.get("trend") == "declining":
                recommendations.append({
                    "type": "strategy_adjustment",
                    "priority": "high",
                    "title": "价值趋势下降",
                    "description": "进化环价值呈下降趋势，需调整进化方向",
                    "action": "重新评估进化目标，优化策略"
                })
            elif trends.get("trend") == "improving":
                recommendations.append({
                    "type": "maintain_momentum",
                    "priority": "low",
                    "title": "价值趋势上升",
                    "description": "进化环价值持续上升，保持当前策略",
                    "action": "继续当前进化方向"
                })

            # 自动阈值调整建议
            summary = self.get_quantized_value_summary()
            if summary.get("average_value", 0) < 30:
                recommendations.append({
                    "type": "threshold_adjustment",
                    "priority": "high",
                    "title": "建议调整价值阈值",
                    "description": "当前平均价值得分较低，建议降低阈值或调整评估标准",
                    "action": "调用 auto_adjust_thresholds() 调整阈值"
                })

        except Exception as e:
            recommendations.append({
                "type": "error",
                "priority": "medium",
                "title": "分析错误",
                "description": f"生成优化建议时出错：{str(e)}",
                "action": "检查数据完整性"
            })
        finally:
            conn.close()

        return recommendations

    def discover_value_patterns(self, rounds: int = 20) -> Dict[str, Any]:
        """
        发现跨轮价值模式

        分析历史进化数据，发现隐藏的价值模式和关联规律。

        Args:
            rounds: 分析的轮次数

        Returns:
            发现的价值模式
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        patterns = {
            "rounds_analyzed": rounds,
            "patterns": [],
            "correlations": [],
            "insights": []
        }

        try:
            cursor.execute("""
                SELECT round_number, current_goal, status, execution_time, result
                FROM evolution_rounds
                ORDER BY round_number DESC
                LIMIT ?
            """, (rounds,))

            rounds_data = cursor.fetchall()

            if len(rounds_data) < 5:
                patterns["insights"].append("数据量不足，需更多轮次才能发现有效模式")
                return patterns

            # 按状态分组分析
            completed = [r for r in rounds_data if r[2] == "completed"]
            failed = [r for r in rounds_data if r[2] != "completed"]

            # 执行时间分析
            completed_with_time = [r for r in completed if r[3]]
            if completed_with_time:
                avg_time = sum(r[3] for r in completed_with_time) / len(completed_with_time)
                fast_count = len([r for r in completed_with_time if r[3] < avg_time])

                patterns["patterns"].append({
                    "type": "execution_time",
                    "description": f"完成率 {len(completed)}/{len(rounds_data)}，平均执行时间 {avg_time:.1f}秒，{fast_count}轮快于平均"
                })

            # 目标类型分析
            goals = [r[1] for r in rounds_data if r[1]]
            if goals:
                # 简单关键词统计
                knowledge_goals = sum(1 for g in goals if "知识" in str(g))
                value_goals = sum(1 for g in goals if "价值" in str(g))
                optimize_goals = sum(1 for g in goals if "优化" in str(g))

                patterns["patterns"].append({
                    "type": "goal_distribution",
                    "description": f"知识类{knowledge_goals}轮、价值类{value_goals}轮、优化类{optimize_goals}轮"
                })

                # 价值与目标类型关联
                if value_goals > 0 and len(completed) > 0:
                    patterns["correlations"].append({
                        "factors": ["目标类型=价值类", "状态=完成"],
                        "strength": "positive",
                        "description": "价值类目标完成率较高"
                    })

            # 生成洞察
            if len(completed) / len(rounds_data) > 0.8:
                patterns["insights"].append("系统进化成功率较高，整体运行良好")
            elif len(completed) / len(rounds_data) < 0.5:
                patterns["insights"].append("系统进化成功率较低，建议检查执行策略")

            if patterns.get("patterns"):
                patterns["insights"].append(f"从 {rounds} 轮数据中发现 {len(patterns['patterns'])} 种模式")

        except Exception as e:
            patterns["error"] = str(e)
        finally:
            conn.close()

        return patterns

    def predict_future_value(self, rounds_ahead: int = 5) -> Dict[str, Any]:
        """
        预测未来价值趋势

        基于历史数据，预测未来 N 轮的价值趋势。

        Args:
            rounds_ahead: 预测的轮次数

        Returns:
            预测结果
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        prediction = {
            "rounds_ahead": rounds_ahead,
            "predicted_trend": "stable",
            "confidence": "low",
            "predicted_value_range": {"min": 0, "max": 100},
            "factors": []
        }

        try:
            # 获取最近数据
            cursor.execute("""
                SELECT round_number, execution_time, status
                FROM evolution_rounds
                ORDER BY round_number DESC
                LIMIT 20
            """)
            history = cursor.fetchall()

            if len(history) < 5:
                prediction["factors"].append("数据量不足，预测置信度低")
                return prediction

            # 简单线性趋势预测
            values = []
            for i, (num, time, status) in enumerate(reversed(history)):
                v = 50 if status == "completed" else 0
                if time and time > 0:
                    v += min(50, 1000 / time)  # 执行效率加分
                values.append(v)

            if len(values) >= 3:
                # 计算趋势
                recent_avg = sum(values[-3:]) / 3
                older_avg = sum(values[:3]) / 3
                trend = recent_avg - older_avg

                if trend > 10:
                    prediction["predicted_trend"] = "improving"
                    prediction["confidence"] = "medium"
                elif trend < -10:
                    prediction["predicted_trend"] = "declining"
                    prediction["confidence"] = "medium"
                else:
                    prediction["predicted_trend"] = "stable"
                    prediction["confidence"] = "high"

                # 预测值范围
                prediction["predicted_value_range"] = {
                    "min": max(0, recent_avg - 20),
                    "max": min(100, recent_avg + 20)
                }

                prediction["factors"].append(f"基于最近 {len(values)} 轮数据分析")
                prediction["factors"].append(f"当前趋势: {prediction['predicted_trend']}")

        except Exception as e:
            prediction["error"] = str(e)
        finally:
            conn.close()

        return prediction

    def get_cockpit_metrics(self) -> Dict[str, Any]:
        """
        获取进化驾驶舱需要的指标数据

        Returns:
            驾驶舱指标
        """
        summary = self.get_quantized_value_summary()
        trends = self.analyze_value_trends(10)
        patterns = self.discover_value_patterns(20)
        prediction = self.predict_future_value(5)

        return {
            "generated_at": datetime.now().isoformat(),
            "value_summary": {
                "total_rounds": summary.get("total_rounds", 0),
                "average_value": summary.get("average_value", 0),
                "trend": summary.get("trend", "unknown")
            },
            "trends": {
                "trend": trends.get("trend", "unknown"),
                "value_change": trends.get("value_change", 0),
                "avg_value": trends.get("avg_value", 0)
            },
            "patterns": {
                "count": len(patterns.get("patterns", [])),
                "insights": patterns.get("insights", [])[:3]
            },
            "prediction": {
                "trend": prediction.get("predicted_trend", "unknown"),
                "confidence": prediction.get("confidence", "low")
            },
            "recommendations": summary.get("recommendations", [])[:3]
        }

    def auto_adjust_thresholds(self) -> Dict[str, Any]:
        """
        自动调整价值阈值

        基于历史数据自动调整评估阈值，使评估更加合理。

        Returns:
            调整结果
        """
        result = {
            "adjusted": False,
            "previous_thresholds": {},
            "new_thresholds": {},
            "reason": ""
        }

        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # 获取历史价值数据
            cursor.execute("""
                SELECT metric_value
                FROM value_metrics
                WHERE metric_name = 'overall_value'
                ORDER BY round_num DESC
                LIMIT 30
            """)
            values = [r[0] for r in cursor.fetchall() if r[0]]

            if len(values) < 10:
                result["reason"] = "数据量不足，无法自动调整"
                return result

            # 计算统计信息
            avg = sum(values) / len(values)
            import statistics
            try:
                std_dev = statistics.stdev(values) if len(values) > 1 else 0
            except:
                std_dev = 10

            # 设置新阈值
            result["adjusted"] = True
            result["previous_thresholds"] = {
                "low": 30,
                "medium": 50,
                "high": 70
            }
            result["new_thresholds"] = {
                "low": max(10, avg - std_dev - 10),
                "medium": avg,
                "high": min(90, avg + std_dev + 10)
            }
            result["reason"] = f"基于历史数据自动调整：平均值={avg:.2f}，标准差={std_dev:.2f}"

            # 保存新阈值
            thresholds_file = RUNTIME_STATE_DIR / "value_thresholds.json"
            with open(thresholds_file, 'w', encoding='utf-8') as f:
                json.dump(result["new_thresholds"], f, indent=2)

        except Exception as e:
            result["error"] = str(e)
            result["reason"] = f"调整失败：{str(e)}"
        finally:
            conn.close()

        return result

    def validate_value_closed_loop(self) -> Dict[str, Any]:
        """
        验证价值闭环是否正常工作

        Returns:
            验证结果
        """
        validation = {
            "loop_status": "unknown",
            "components": {},
            "issues": [],
            "recommendations": []
        }

        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # 检查数据收集
            cursor.execute("SELECT COUNT(*) FROM evolution_rounds")
            rounds_count = cursor.fetchone()[0] or 0

            validation["components"]["data_collection"] = {
                "status": "ok" if rounds_count > 0 else "empty",
                "rounds_count": rounds_count
            }

            # 检查价值计算
            cursor.execute("SELECT COUNT(*) FROM value_metrics")
            metrics_count = cursor.fetchone()[0] or 0

            validation["components"]["value_calculation"] = {
                "status": "ok" if metrics_count > 0 else "empty",
                "metrics_count": metrics_count
            }

            # 检查趋势分析
            trends = self.analyze_value_trends(10)
            validation["components"]["trend_analysis"] = {
                "status": "ok" if "error" not in trends else "error",
                "trend": trends.get("trend", "unknown")
            }

            # 检查优化建议生成
            try:
                recommendations = self.generate_optimization_recommendations()
                validation["components"]["optimization_recommendations"] = {
                    "status": "ok",
                    "count": len(recommendations)
                }
            except Exception as e:
                validation["components"]["optimization_recommendations"] = {
                    "status": "error",
                    "error": str(e)
                }

            # 综合评估
            component_statuses = [c["status"] for c in validation["components"].values() if isinstance(c, dict)]
            if all(s == "ok" for s in component_statuses):
                validation["loop_status"] = "healthy"
            elif any(s == "error" for s in component_statuses):
                validation["loop_status"] = "degraded"
                validation["issues"].append("部分组件运行异常")
            else:
                validation["loop_status"] = "initializing"

            if rounds_count < 10:
                validation["recommendations"].append("数据量较少，建议积累更多进化轮次后再进行深度分析")

        except Exception as e:
            validation["error"] = str(e)
            validation["loop_status"] = "error"
        finally:
            conn.close()

        return validation


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

    # ============ Round 438 新增命令 ============

    elif command == "optimize" or command == "optimization":
        # 生成优化建议
        recommendations = engine.generate_optimization_recommendations()
        return {
            "status": "ok",
            "message": "价值驱动自动优化建议",
            "data": recommendations
        }

    elif command == "patterns":
        # 发现价值模式
        rounds = int(args[1]) if len(args) > 1 else 20
        patterns = engine.discover_value_patterns(rounds)
        return {
            "status": "ok",
            "message": f"跨轮价值模式分析（最近{rounds}轮）",
            "data": patterns
        }

    elif command == "predict" or command == "prediction":
        # 预测未来价值
        rounds_ahead = int(args[1]) if len(args) > 1 else 5
        prediction = engine.predict_future_value(rounds_ahead)
        return {
            "status": "ok",
            "message": f"未来 {rounds_ahead} 轮价值预测",
            "data": prediction
        }

    elif command == "cockpit":
        # 获取驾驶舱指标
        metrics = engine.get_cockpit_metrics()
        return {
            "status": "ok",
            "message": "进化驾驶舱指标数据",
            "data": metrics
        }

    elif command == "adjust" or command == "adjust_thresholds":
        # 自动调整阈值
        result = engine.auto_adjust_thresholds()
        return {
            "status": "ok",
            "message": "价值阈值自动调整",
            "data": result
        }

    elif command == "validate" or command == "validate_loop":
        # 验证价值闭环
        validation = engine.validate_value_closed_loop()
        return {
            "status": "ok",
            "message": "价值闭环验证",
            "data": validation
        }

    elif command == "enhanced_loop" or command == "full_loop":
        # 完整的增强闭环
        summary = engine.get_quantized_value_summary()
        trends = engine.analyze_value_trends(10)
        patterns = engine.discover_value_patterns(20)
        prediction = engine.predict_future_value(5)
        recommendations = engine.generate_optimization_recommendations()
        validation = engine.validate_value_closed_loop()

        return {
            "status": "ok",
            "message": "增强版价值量化闭环分析",
            "data": {
                "summary": summary,
                "trends": trends,
                "patterns": patterns,
                "prediction": prediction,
                "recommendations": recommendations,
                "validation": validation
            }
        }

    else:
        return {
            "status": "error",
            "message": f"未知命令: {command}",
            "available_commands": [
                "status", "analyze", "trends", "recommend", "report", "summary",
                "optimize", "patterns", "predict", "cockpit", "adjust", "validate", "enhanced_loop"
            ]
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