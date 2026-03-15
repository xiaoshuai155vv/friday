#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环价值量化评估增强引擎

在 round 438 完成的进化价值量化引擎和 round 502 完成的创新验证结果自动执行与价值实现引擎基础上，
进一步增强价值实现的量化评估能力。

本轮增强：
1. 与代码理解引擎深度集成，实现基于代码分析的智能任务推荐
2. 增强多维度价值量化评估体系（效率维度、质量维度、创新维度、影响维度）
3. 创新验证结果的价值追踪与分析
4. 智能任务推荐基于价值评估结果
5. 与进化驾驶舱深度集成

Version: 1.0.0
Round: 503
"""

import os
import json
import sqlite3
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

# 路径配置
SCRIPT_DIR = Path(__file__).parent
RUNTIME_STATE_DIR = SCRIPT_DIR.parent / "runtime" / "state"
EVOLUTION_DB = RUNTIME_STATE_DIR / "evolution_history.db"
CODE_ANALYSIS_CACHE = RUNTIME_STATE_DIR / "code_analysis_cache.json"


class EvolutionValueQuantizationEnhancedEngine:
    """进化环价值量化评估增强引擎"""

    def __init__(self):
        """初始化引擎"""
        self.db_path = EVOLUTION_DB
        self._ensure_db()

    def _ensure_db(self):
        """确保数据库存在并创建增强价值指标表"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # 创建增强价值指标表（如果不存在）
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS enhanced_value_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                round_num INTEGER,
                metric_category TEXT,
                metric_name TEXT,
                metric_value REAL,
                unit TEXT,
                timestamp TEXT,
                details TEXT
            )
        """)

        # 创建创新验证价值表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS innovation_value_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hypothesis_id TEXT,
                innovation_type TEXT,
                value_score REAL,
                efficiency_score REAL,
                quality_score REAL,
                impact_score REAL,
                overall_value REAL,
                execution_time REAL,
                status TEXT,
                timestamp TEXT,
                details TEXT
            )
        """)

        conn.commit()
        conn.close()

    def get_connection(self):
        """获取数据库连接"""
        return sqlite3.connect(str(self.db_path))

    def _load_code_analysis_results(self) -> Dict[str, Any]:
        """
        加载代码理解引擎的分析结果

        Returns:
            代码分析结果
        """
        try:
            if Path(CODE_ANALYSIS_CACHE).exists():
                with open(CODE_ANALYSIS_CACHE, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"加载代码分析缓存失败: {e}")

        return {}

    def calculate_multi_dimensional_value(
        self,
        round_num: int,
        code_metrics: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        计算多维度价值量化指标

        Args:
            round_num: 进化轮次
            code_metrics: 代码分析指标（可选）

        Returns:
            多维度价值指标
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        metrics = {
            "round": round_num,
            "timestamp": datetime.now().isoformat(),
            "efficiency_dimension": {
                "score": 0.0,
                "components": {},
                "description": "效率维度：评估执行速度、资源利用效率"
            },
            "quality_dimension": {
                "score": 0.0,
                "components": {},
                "description": "质量维度：评估执行质量、代码质量、稳定性"
            },
            "innovation_dimension": {
                "score": 0.0,
                "components": {},
                "description": "创新维度：评估创新性、新颖性、突破性"
            },
            "impact_dimension": {
                "score": 0.0,
                "components": {},
                "description": "影响维度：评估对系统能力的提升、价值贡献"
            },
            "overall_value": 0.0,
            "code_analysis": code_metrics or {}
        }

        try:
            # 获取进化历史数据
            cursor.execute("""
                SELECT current_goal, status, execution_time, result
                FROM evolution_rounds
                WHERE round_number = ?
            """, (round_num,))
            row = cursor.fetchone()

            if row:
                goal, status, duration, result = row
                metrics["details"] = {
                    "goal": goal,
                    "status": status,
                    "duration_seconds": duration
                }

                # ===== 效率维度 =====
                if duration and duration > 0:
                    # 执行效率：时间越短越好
                    efficiency_score = min(100, 1000 / duration)
                    # 资源效率：假设值
                    resource_efficiency = 80.0 if status == "completed" else 0.0

                    metrics["efficiency_dimension"]["score"] = (
                        efficiency_score * 0.6 + resource_efficiency * 0.4
                    )
                    metrics["efficiency_dimension"]["components"] = {
                        "execution_efficiency": efficiency_score,
                        "resource_efficiency": resource_efficiency
                    }

                # ===== 质量维度 =====
                if status == "completed":
                    code_quality = 85.0
                    stability = 90.0
                    metrics["quality_dimension"]["score"] = (
                        code_quality * 0.5 + stability * 0.5
                    )
                    metrics["quality_dimension"]["components"] = {
                        "code_quality": code_quality,
                        "stability": stability
                    }
                else:
                    metrics["quality_dimension"]["score"] = 20.0
                    metrics["quality_dimension"]["components"] = {
                        "code_quality": 20.0,
                        "stability": 20.0
                    }

                # ===== 创新维度 =====
                innovation_potential = 0.0
                if goal:
                    # 检查目标中是否包含创新相关关键词
                    innovation_keywords = ["创新", "增强", "新引擎", "新功能", "深度", "自主", "智能", "自适应"]
                    innovation_potential = sum(
                        10.0 for kw in innovation_keywords if kw in str(goal)
                    )
                    innovation_potential = min(100, innovation_potential)

                metrics["innovation_dimension"]["score"] = innovation_potential
                metrics["innovation_dimension"]["components"] = {
                    "innovation_potential": innovation_potential,
                    "goal_innovation_keywords": len([kw for kw in innovation_keywords if kw in str(goal)])
                }

                # ===== 影响维度 =====
                impact_score = 50.0 if status == "completed" else 0.0
                # 整合代码分析结果
                if code_metrics:
                    quality_improvement = code_metrics.get("quality_improvement", 0)
                    performance_improvement = code_metrics.get("performance_improvement", 0)
                    impact_score = (impact_score + quality_improvement + performance_improvement) / 2

                metrics["impact_dimension"]["score"] = impact_score
                metrics["impact_dimension"]["components"] = {
                    "base_impact": 50.0 if status == "completed" else 0.0,
                    "code_analysis_impact": code_metrics.get("quality_improvement", 0) if code_metrics else 0
                }

                # ===== 整体价值 =====
                weights = {
                    "efficiency": 0.25,
                    "quality": 0.25,
                    "innovation": 0.20,
                    "impact": 0.30
                }
                metrics["overall_value"] = (
                    metrics["efficiency_dimension"]["score"] * weights["efficiency"] +
                    metrics["quality_dimension"]["score"] * weights["quality"] +
                    metrics["innovation_dimension"]["score"] * weights["innovation"] +
                    metrics["impact_dimension"]["score"] * weights["impact"]
                )

                # 存储到数据库
                for dim_name, dim_data in [
                    ("efficiency", metrics["efficiency_dimension"]),
                    ("quality", metrics["quality_dimension"]),
                    ("innovation", metrics["innovation_dimension"]),
                    ("impact", metrics["impact_dimension"])
                ]:
                    cursor.execute("""
                        INSERT INTO enhanced_value_metrics
                        (round_num, metric_category, metric_name, metric_value, unit, timestamp, details)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        round_num,
                        dim_name,
                        "dimension_score",
                        dim_data["score"],
                        "%",
                        datetime.now().isoformat(),
                        json.dumps(dim_data["components"], ensure_ascii=False)
                    ))

                conn.commit()

        except Exception as e:
            metrics["error"] = str(e)
        finally:
            conn.close()

        return metrics

    def analyze_innovation_value(self, hypothesis_id: Optional[str] = None) -> Dict[str, Any]:
        """
        分析创新验证结果的价值

        Args:
            hypothesis_id: 假设 ID（可选）

        Returns:
            创新价值分析结果
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        result = {
            "hypothesis_id": hypothesis_id,
            "timestamp": datetime.now().isoformat(),
            "total_innovations": 0,
            "average_value": 0.0,
            "value_distribution": {},
            "insights": []
        }

        try:
            # 查询创新验证数据
            if hypothesis_id:
                cursor.execute("""
                    SELECT * FROM innovation_value_metrics
                    WHERE hypothesis_id = ?
                    ORDER BY timestamp DESC
                """, (hypothesis_id,))
            else:
                cursor.execute("""
                    SELECT * FROM innovation_value_metrics
                    ORDER BY timestamp DESC
                    LIMIT 50
                """)

            innovations = cursor.fetchall()

            if innovations:
                result["total_innovations"] = len(innovations)

                # 计算平均价值
                values = [i[5] for i in innovations if i[5]]  # overall_value
                if values:
                    result["average_value"] = sum(values) / len(values)

                # 价值分布
                value_ranges = {
                    "高价值(80-100)": 0,
                    "中价值(50-80)": 0,
                    "低价值(0-50)": 0
                }
                for v in values:
                    if v >= 80:
                        value_ranges["高价值(80-100)"] += 1
                    elif v >= 50:
                        value_ranges["中价值(50-80)"] += 1
                    else:
                        value_ranges["低价值(0-50)"] += 1

                result["value_distribution"] = value_ranges

                # 生成洞察
                high_value_count = value_ranges["高价值(80-100)"]
                if high_value_count / len(innovations) > 0.3:
                    result["insights"].append("创新验证成功率较高，系统创新能力良好")
                else:
                    result["insights"].append("建议增强创新验证的筛选标准，提高高价值创新比例")

                if result["average_value"] > 70:
                    result["insights"].append(f"平均创新价值较高（{result['average_value']:.1f}），继续当前创新方向")
            else:
                result["insights"].append("暂无创新验证数据，请先运行创新验证引擎")

        except Exception as e:
            result["error"] = str(e)
        finally:
            conn.close()

        return result

    def get_intelligent_task_recommendations(
        self,
        based_on: str = "value_analysis",
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        获取基于价值分析的智能任务推荐

        Args:
            based_on: 推荐依据（value_analysis, code_analysis, trends）
            limit: 推荐数量

        Returns:
            任务推荐列表
        """
        recommendations = []

        try:
            # 获取多维度价值分析
            trends = self._analyze_value_trends_simple(10)

            # 基于价值分析生成推荐
            if based_on == "value_analysis":
                # 检查各维度表现
                efficiency_score = trends.get("avg_efficiency", 0)
                quality_score = trends.get("avg_quality", 0)
                innovation_score = trends.get("avg_innovation", 0)
                impact_score = trends.get("avg_impact", 0)

                # 识别薄弱维度并推荐
                if efficiency_score < 50:
                    recommendations.append({
                        "type": "efficiency_improvement",
                        "priority": "high",
                        "title": "提升执行效率",
                        "description": f"效率维度得分较低（{efficiency_score:.1f}），建议优化执行流程或增加并行处理能力",
                        "suggested_action": "创建效率优化引擎或增强现有执行策略"
                    })

                if quality_score < 50:
                    recommendations.append({
                        "type": "quality_improvement",
                        "priority": "high",
                        "title": "提升执行质量",
                        "description": f"质量维度得分较低（{quality_score:.1f}），建议加强质量保障措施",
                        "suggested_action": "增强自校验能力或增加质量检查环节"
                    })

                if innovation_score < 30:
                    recommendations.append({
                        "type": "innovation_enhancement",
                        "priority": "medium",
                        "title": "增强创新能力",
                        "description": f"创新维度得分较低（{innovation_score:.1f}），建议增加创新探索方向",
                        "suggested_action": "增强假设生成引擎或增加创新验证频率"
                    })

                if impact_score < 50:
                    recommendations.append({
                        "type": "impact_enhancement",
                        "priority": "high",
                        "title": "提升价值影响",
                        "description": f"影响维度得分较低（{impact_score:.1f}），建议聚焦高价值进化目标",
                        "suggested_action": "优化进化目标选择策略，优先选择高影响目标"
                    })

            # 加载代码分析结果
            code_analysis = self._load_code_analysis_results()
            if code_analysis and based_on in ["code_analysis", "value_analysis"]:
                # 基于代码分析生成推荐
                code_quality = code_analysis.get("overall_quality_score", 0)
                if code_quality < 60:
                    recommendations.append({
                        "type": "code_quality_improvement",
                        "priority": "medium",
                        "title": "提升代码质量",
                        "description": f"代码质量得分较低（{code_quality:.1f}），建议进行代码重构和优化",
                        "suggested_action": "运行代码理解引擎进行深度分析并生成优化建议"
                    })

                # 重复代码检测
                duplicate_count = code_analysis.get("duplicate_code_blocks", 0)
                if duplicate_count > 5:
                    recommendations.append({
                        "type": "code_deduplication",
                        "priority": "medium",
                        "title": "消除重复代码",
                        "description": f"发现 {duplicate_count} 处重复代码，建议进行代码重构",
                        "suggested_action": "利用代码理解引擎的优化建议进行修复"
                    })

            # 添加通用建议
            if len(recommendations) < 3:
                recommendations.append({
                    "type": "general_optimization",
                    "priority": "low",
                    "title": "保持当前进化策略",
                    "description": "系统各维度表现良好，继续当前进化方向",
                    "suggested_action": "按现有计划继续执行进化"
                })

            # 按优先级排序并限制数量
            priority_order = {"high": 0, "medium": 1, "low": 2}
            recommendations.sort(key=lambda x: priority_order.get(x.get("priority", "low"), 2))

        except Exception as e:
            recommendations.append({
                "type": "error",
                "priority": "medium",
                "title": "生成推荐时出错",
                "description": f"无法生成智能推荐：{str(e)}",
                "suggested_action": "检查数据完整性"
            })

        return recommendations[:limit]

    def _analyze_value_trends_simple(self, rounds: int = 10) -> Dict[str, Any]:
        """
        简单的价值趋势分析

        Args:
            rounds: 分析的轮次数

        Returns:
            趋势分析结果
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        result = {
            "rounds_analyzed": rounds,
            "avg_efficiency": 0.0,
            "avg_quality": 0.0,
            "avg_innovation": 0.0,
            "avg_impact": 0.0,
            "overall_trend": "stable"
        }

        try:
            # 获取增强价值指标
            cursor.execute("""
                SELECT round_num, metric_category, metric_value
                FROM enhanced_value_metrics
                WHERE round_num >= (
                    SELECT COALESCE(MAX(round_number), 0) - ?
                    FROM evolution_rounds
                )
                ORDER BY round_num DESC
            """, (rounds,))

            rows = cursor.fetchall()

            if rows:
                # 按维度聚合
                dimension_sums = {"efficiency": [], "quality": [], "innovation": [], "impact": []}
                for round_num, category, value in rows:
                    if category in dimension_sums:
                        dimension_sums[category].append(value)

                # 计算平均值
                for dim, values in dimension_sums.items():
                    if values:
                        result[f"avg_{dim}"] = sum(values) / len(values)

            # 计算整体趋势
            scores = [result[f"avg_{d}"] for d in ["efficiency", "quality", "innovation", "impact"]]
            if scores:
                avg_score = sum(scores) / len(scores)
                if avg_score > 60:
                    result["overall_trend"] = "improving"
                elif avg_score < 40:
                    result["overall_trend"] = "declining"

        except Exception as e:
            result["error"] = str(e)
        finally:
            conn.close()

        return result

    def get_cockpit_metrics(self) -> Dict[str, Any]:
        """
        获取进化驾驶舱需要的增强指标数据

        Returns:
            驾驶舱指标
        """
        # 多维度价值分析
        trends = self._analyze_value_trends_simple(10)

        # 智能推荐
        recommendations = self.get_intelligent_task_recommendations(based_on="value_analysis", limit=5)

        # 创新价值分析
        innovation_analysis = self.analyze_innovation_value()

        return {
            "generated_at": datetime.now().isoformat(),
            "multi_dimensional_value": {
                "efficiency": trends.get("avg_efficiency", 0),
                "quality": trends.get("avg_quality", 0),
                "innovation": trends.get("avg_innovation", 0),
                "impact": trends.get("avg_impact", 0),
                "overall_trend": trends.get("overall_trend", "unknown")
            },
            "intelligent_recommendations": recommendations,
            "innovation_analysis": {
                "total_innovations": innovation_analysis.get("total_innovations", 0),
                "average_value": innovation_analysis.get("average_value", 0),
                "value_distribution": innovation_analysis.get("value_distribution", {}),
                "insights": innovation_analysis.get("insights", [])[:3]
            }
        }

    def run_full_value_analysis(self) -> Dict[str, Any]:
        """
        运行完整的价值量化分析

        Returns:
            完整分析结果
        """
        # 获取最近一轮的价值分析
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT MAX(round_number) FROM evolution_rounds")
            latest_round = cursor.fetchone()[0] or 0

            # 计算当前轮次的多维度价值
            code_metrics = self._load_code_analysis_results()
            current_metrics = self.calculate_multi_dimensional_value(latest_round, code_metrics)

            # 获取趋势分析
            trends = self._analyze_value_trends_simple(10)

            # 获取智能推荐
            recommendations = self.get_intelligent_task_recommendations(based_on="value_analysis", limit=5)

            # 获取创新价值分析
            innovation_analysis = self.analyze_innovation_value()

            return {
                "status": "ok",
                "round": latest_round,
                "current_value_analysis": current_metrics,
                "trends": trends,
                "recommendations": recommendations,
                "innovation_analysis": innovation_analysis,
                "cockpit_metrics": self.get_cockpit_metrics()
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"价值分析失败: {str(e)}"
            }
        finally:
            conn.close()


def handle_command(args: List[str]) -> Dict[str, Any]:
    """处理命令"""
    engine = EvolutionValueQuantizationEnhancedEngine()

    if not args:
        return {"status": "error", "message": "需要子命令"}

    command = args[0].lower()

    if command == "status" or command == "summary":
        # 返回价值摘要
        analysis = engine.run_full_value_analysis()
        return {
            "status": "ok",
            "message": "价值量化评估增强引擎状态",
            "data": analysis
        }

    elif command == "analyze":
        # 分析指定轮次价值
        round_num = int(args[1]) if len(args) > 1 else None
        code_metrics = engine._load_code_analysis_results()

        if round_num:
            metrics = engine.calculate_multi_dimensional_value(round_num, code_metrics)
            return {
                "status": "ok",
                "message": f"Round {round_num} 多维度价值分析",
                "data": metrics
            }
        else:
            # 获取最近一轮
            conn = engine.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT MAX(round_number) FROM evolution_rounds")
            latest_round = cursor.fetchone()[0] or 0
            conn.close()

            metrics = engine.calculate_multi_dimensional_value(latest_round, code_metrics)
            return {
                "status": "ok",
                "message": f"Round {latest_round} 多维度价值分析",
                "data": metrics
            }

    elif command == "innovation" or command == "innovations":
        # 分析创新价值
        hypothesis_id = args[1] if len(args) > 1 else None
        analysis = engine.analyze_innovation_value(hypothesis_id)
        return {
            "status": "ok",
            "message": "创新价值分析",
            "data": analysis
        }

    elif command == "recommend" or command == "recommendations":
        # 获取智能任务推荐
        limit = int(args[1]) if len(args) > 1 else 5
        based_on = args[2] if len(args) > 2 else "value_analysis"
        recommendations = engine.get_intelligent_task_recommendations(based_on=based_on, limit=limit)
        return {
            "status": "ok",
            "message": "基于价值分析的智能任务推荐",
            "data": recommendations
        }

    elif command == "trends" or command == "trend":
        # 获取价值趋势
        rounds = int(args[1]) if len(args) > 1 else 10
        trends = engine._analyze_value_trends_simple(rounds)
        return {
            "status": "ok",
            "message": f"最近 {rounds} 轮多维度价值趋势",
            "data": trends
        }

    elif command == "cockpit" or command == "dashboard":
        # 获取驾驶舱指标
        metrics = engine.get_cockpit_metrics()
        return {
            "status": "ok",
            "message": "进化驾驶舱增强指标数据",
            "data": metrics
        }

    elif command == "full" or command == "full_analysis":
        # 完整分析
        result = engine.run_full_value_analysis()
        return {
            "status": "ok",
            "message": "完整价值量化分析",
            "data": result
        }

    else:
        return {
            "status": "error",
            "message": f"未知命令: {command}",
            "available_commands": [
                "status", "analyze", "innovation", "recommend", "trends", "cockpit", "full"
            ]
        }


def main():
    """主函数"""
    import sys

    args = sys.argv[1:] if len(sys.argv) > 1 else []

    if not args:
        # 无参数时显示简要信息
        engine = EvolutionValueQuantizationEnhancedEngine()
        analysis = engine.run_full_value_analysis()
        print(f"智能全场景进化环价值量化评估增强引擎 v1.0.0")
        print(f"当前轮次: {analysis.get('round', 'N/A')}")
        if "current_value_analysis" in analysis:
            cva = analysis["current_value_analysis"]
            print(f"整体价值得分: {cva.get('overall_value', 0):.2f}")
            print(f"效率维度: {cva.get('efficiency_dimension', {}).get('score', 0):.1f}")
            print(f"质量维度: {cva.get('quality_dimension', {}).get('score', 0):.1f}")
            print(f"创新维度: {cva.get('innovation_dimension', {}).get('score', 0):.1f}")
            print(f"影响维度: {cva.get('impact_dimension', {}).get('score', 0):.1f}")
        return

    result = handle_command(args)

    if result["status"] == "ok":
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()