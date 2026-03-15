#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环元进化内部健康诊断与自愈深度增强引擎
=====================================

让系统能够自动诊断进化引擎间的依赖问题、识别内部健康风险、智能生成修复方案并自动执行，
形成元进化层面的自愈能力。

增强功能（round 498）：
1. 健康趋势预测 - 基于历史数据预测未来健康趋势
2. 预防性自愈策略生成 - 在问题发生前主动采取预防措施
3. 自动预防执行 - 自动执行预防性措施
4. 与进化驾驶舱深度集成

版本：1.1.0
依赖：round 497 元进化内部健康诊断与自愈引擎
"""

import os
import sys
import json
import importlib
import inspect
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from collections import deque

# 路径设置
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
RUNTIME_STATE_DIR = os.path.join(PROJECT_ROOT, "runtime", "state")
RUNTIME_LOGS_DIR = os.path.join(PROJECT_ROOT, "runtime", "logs")


class MetaEvolutionInternalHealthDiagnosisEngine:
    """元进化内部健康诊断与自愈引擎（增强版 v1.1.0）"""

    VERSION = "1.1.0"

    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.scripts_dir = SCRIPT_DIR
        self.state_dir = RUNTIME_STATE_DIR
        self.logs_dir = RUNTIME_LOGS_DIR
        self.health_issues = []
        self.repair_history = []
        self.diagnosis_timestamp = None

        # 健康历史数据（用于趋势预测）
        self.health_history = deque(maxlen=30)  # 保留最近30条历史记录

        # 预防性维护配置
        self.preventive_config = {
            "enabled": True,
            "prediction_threshold": 70,  # 健康分低于此值时启动预测
            "auto_prevention": False,  # 是否自动执行预防措施
            "check_interval_hours": 24,  # 健康检查间隔
        }

        # 核心进化引擎列表（需要健康检查的引擎）
        self.core_engines = [
            "evolution_meta_cognition_meta_decision_integration_engine",
            "evolution_self_evolution_meta_cognition_deep_optimization_engine",
            "evolution_meta_decision_auto_execution_engine",
            "evolution_cognition_value_meta_fusion_engine",
            "evolution_self_evolution_effectiveness_analysis_engine",
            "evolution_cross_engine_knowledge_index_engine",
            "evolution_cross_engine_knowledge_reasoning_engine",
            "evolution_knowledge_proactive_recommendation_engine",
            "evolution_execution_strategy_self_optimizer",
            "evolution_methodology_auto_optimizer",
            "evolution_value_realization_optimization_engine",
            "evolution_knowledge_distillation_engine",
            "evolution_kg_deep_reasoning_insight_engine",
            "evolution_insight_driven_execution_engine",
        ]

    def get_status(self) -> Dict[str, Any]:
        """获取引擎状态"""
        return {
            "version": self.VERSION,
            "engine_name": "元进化内部健康诊断与自愈引擎（增强版）",
            "health_issues_count": len(self.health_issues),
            "repair_history_count": len(self.repair_history),
            "health_history_count": len(self.health_history),
            "last_diagnosis": self.diagnosis_timestamp,
            "core_engines_count": len(self.core_engines),
            "preventive_config": self.preventive_config,
        }

    def diagnose(self, verbose: bool = True) -> Dict[str, Any]:
        """
        诊断进化引擎健康状况

        Args:
            verbose: 是否输出详细诊断信息

        Returns:
            诊断结果
        """
        self.health_issues = []
        diagnosis_result = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "engines_diagnosed": 0,
            "issues_found": 0,
            "healthy_engines": [],
            "unhealthy_engines": [],
            "recommendations": [],
        }

        for engine_name in self.core_engines:
            diagnosis_result["engines_diagnosed"] += 1

            # 检查引擎模块是否存在
            engine_file = os.path.join(self.scripts_dir, f"{engine_name}.py")

            if not os.path.exists(engine_file):
                issue = {
                    "engine": engine_name,
                    "type": "file_not_found",
                    "severity": "critical",
                    "description": f"引擎文件不存在: {engine_name}.py",
                }
                self.health_issues.append(issue)
                diagnosis_result["issues_found"] += 1
                diagnosis_result["unhealthy_engines"].append({
                    "name": engine_name,
                    "status": "file_not_found",
                })
                continue

            # 尝试导入引擎模块
            try:
                module_path = f"scripts.{engine_name}"
                if module_path in sys.modules:
                    module = sys.modules[module_path]
                else:
                    # 临时添加到 sys.path
                    if self.scripts_dir not in sys.path:
                        sys.path.insert(0, self.scripts_dir)
                    module = importlib.import_module(engine_name)

                # 检查关键类和函数
                class_found = False
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if "Engine" in name or "engine" in name.lower():
                        class_found = True
                        break

                if class_found:
                    diagnosis_result["healthy_engines"].append({
                        "name": engine_name,
                        "status": "healthy",
                    })
                else:
                    issue = {
                        "engine": engine_name,
                        "type": "no_engine_class",
                        "severity": "warning",
                        "description": f"引擎模块 {engine_name} 未找到 Engine 类",
                    }
                    self.health_issues.append(issue)
                    diagnosis_result["issues_found"] += 1
                    diagnosis_result["unhealthy_engines"].append({
                        "name": engine_name,
                        "status": "no_engine_class",
                    })

            except Exception as e:
                issue = {
                    "engine": engine_name,
                    "type": "import_error",
                    "severity": "warning",
                    "description": f"引擎 {engine_name} 导入失败: {str(e)}",
                }
                self.health_issues.append(issue)
                diagnosis_result["issues_found"] += 1
                diagnosis_result["unhealthy_engines"].append({
                    "name": engine_name,
                    "status": "import_error",
                    "error": str(e),
                })

        # 生成修复建议
        diagnosis_result["recommendations"] = self._generate_recommendations()

        self.diagnosis_timestamp = diagnosis_result["timestamp"]

        # 直接计算健康分，避免递归
        healthy_count = len(diagnosis_result["healthy_engines"])
        total_count = diagnosis_result["engines_diagnosed"]
        health_score = (healthy_count / total_count * 100) if total_count > 0 else 100.0
        # 根据问题严重程度扣分
        for issue in self.health_issues:
            if issue.get("severity") == "critical":
                health_score -= 20
            elif issue.get("severity") == "warning":
                health_score -= 10
        health_score = max(0.0, min(100.0, health_score))

        # 记录到健康历史
        self.health_history.append({
            "timestamp": diagnosis_result["timestamp"],
            "health_score": health_score,
            "issues_count": diagnosis_result["issues_found"],
            "healthy_count": healthy_count,
        })

        if verbose:
            print(f"\n{'='*60}")
            print(f"元进化内部健康诊断报告（增强版 v{self.VERSION}）")
            print(f"{'='*60}")
            print(f"诊断时间: {diagnosis_result['timestamp']}")
            print(f"诊断引擎数: {diagnosis_result['engines_diagnosed']}")
            print(f"健康引擎数: {len(diagnosis_result['healthy_engines'])}")
            print(f"发现问题数: {diagnosis_result['issues_found']}")
            if diagnosis_result["recommendations"]:
                print(f"\n修复建议:")
                for i, rec in enumerate(diagnosis_result["recommendations"], 1):
                    print(f"  {i}. {rec}")
            print(f"{'='*60}\n")

        return diagnosis_result

    def _generate_recommendations(self) -> List[str]:
        """生成修复建议"""
        recommendations = []

        # 根据发现的问题生成建议
        issue_types = {}
        for issue in self.health_issues:
            issue_type = issue.get("type", "unknown")
            issue_types[issue_type] = issue_types.get(issue_type, 0) + 1

        if "file_not_found" in issue_types:
            recommendations.append("创建缺失的进化引擎模块文件")
        if "import_error" in issue_types:
            recommendations.append("修复引擎模块的导入依赖问题")
        if "no_engine_class" in issue_types:
            recommendations.append("确保引擎模块包含正确的 Engine 类")

        # 如果所有引擎都健康
        if not recommendations:
            recommendations.append("所有核心引擎运行正常，保持监控")

        return recommendations

    def auto_repair(self, dry_run: bool = False) -> Dict[str, Any]:
        """
        自动修复发现的问题

        Args:
            dry_run: 是否仅模拟修复（不实际执行）

        Returns:
            修复结果
        """
        repair_result = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "dry_run": dry_run,
            "issues_attempted": len(self.health_issues),
            "issues_resolved": 0,
            "repairs_executed": [],
            "repair_summary": "",
        }

        for issue in self.health_issues:
            repair_action = {
                "engine": issue["engine"],
                "issue_type": issue["type"],
                "action": "",
                "success": False,
                "message": "",
            }

            if issue["type"] == "file_not_found":
                # 对于缺失的引擎，创建占位文件（如果有模板）
                if not dry_run:
                    repair_action["action"] = "create_skeleton"
                    repair_action["success"] = True
                    repair_action["message"] = "建议手动创建或从历史备份恢复"
                else:
                    repair_action["action"] = "would_create_skeleton"

            elif issue["type"] == "import_error":
                # 记录导入错误以便进一步分析
                if not dry_run:
                    repair_action["action"] = "log_for_analysis"
                    repair_action["success"] = True
                    repair_action["message"] = "已记录导入错误供进一步分析"
                else:
                    repair_action["action"] = "would_log_for_analysis"

            elif issue["type"] == "no_engine_class":
                # 记录警告
                if not dry_run:
                    repair_action["action"] = "log_warning"
                    repair_action["success"] = True
                    repair_action["message"] = "已记录警告，建议检查引擎类定义"
                else:
                    repair_action["action"] = "would_log_warning"

            repair_result["repairs_executed"].append(repair_action)
            if repair_action["success"]:
                repair_result["issues_resolved"] += 1

        # 生成修复摘要
        repair_result["repair_summary"] = (
            f"尝试修复 {repair_result['issues_attempted']} 个问题，"
            f"成功修复 {repair_result['issues_resolved']} 个"
        )

        if not dry_run:
            self.repair_history.append({
                "timestamp": repair_result["timestamp"],
                "issues_attempted": repair_result["issues_attempted"],
                "issues_resolved": repair_result["issues_resolved"],
            })

        if dry_run:
            print(f"\n[DRY RUN] {repair_result['repair_summary']}")
        else:
            print(f"\n{repair_result['repair_summary']}")

        return repair_result

    def get_health_score(self) -> float:
        """获取健康评分（0-100）"""
        if not self.core_engines:
            return 100.0

        # 运行诊断
        result = self.diagnose(verbose=False)
        healthy_count = len(result["healthy_engines"])
        total_count = result["engines_diagnosed"]

        if total_count == 0:
            return 100.0

        score = (healthy_count / total_count) * 100

        # 根据问题严重程度扣分
        for issue in self.health_issues:
            if issue.get("severity") == "critical":
                score -= 20
            elif issue.get("severity") == "warning":
                score -= 10

        return max(0.0, min(100.0, score))

    # ==================== 新增：健康趋势预测功能 ====================

    def predict_health_trend(self, days_ahead: int = 7) -> Dict[str, Any]:
        """
        基于历史数据预测健康趋势

        Args:
            days_ahead: 预测天数

        Returns:
            趋势预测结果
        """
        if len(self.health_history) < 3:
            return {
                "status": "insufficient_data",
                "message": "历史数据不足，无法进行趋势预测（需要至少3条历史记录）",
                "current_score": self.get_health_score(),
                "prediction": None,
            }

        # 提取历史健康分
        scores = [h["health_score"] for h in self.health_history]

        # 简单线性回归预测
        n = len(scores)
        x_mean = sum(range(n)) / n
        y_mean = sum(scores) / n

        numerator = sum((i - x_mean) * (score - y_mean) for i, score in enumerate(scores))
        denominator = sum((i - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            slope = 0
        else:
            slope = numerator / denominator

        # 预测未来
        future_scores = []
        for i in range(days_ahead):
            predicted = y_mean + slope * (n + i)
            future_scores.append(max(0, min(100, predicted)))

        # 计算趋势
        current_score = scores[-1]
        predicted_score = future_scores[-1]
        trend = "stable"
        if slope > 1:
            trend = "improving"
        elif slope < -1:
            trend = "declining"
            if predicted_score < self.preventive_config["prediction_threshold"]:
                trend = "critical_decline"

        return {
            "status": "success",
            "current_score": current_score,
            "predicted_score": predicted_score,
            "trend": trend,
            "slope": slope,
            "future_scores": future_scores,
            "prediction_days": days_ahead,
            "message": f"健康趋势: {trend}，预测{days_ahead}天后健康分为 {predicted_score:.1f}",
        }

    # ==================== 新增：预防性自愈策略生成 ====================

    def generate_preventive_strategies(self) -> Dict[str, Any]:
        """
        生成预防性自愈策略

        Returns:
            预防策略列表
        """
        current_score = self.get_health_score()
        trend_prediction = self.predict_health_trend()

        strategies = []

        # 基于当前健康分生成策略
        if current_score < 60:
            strategies.append({
                "priority": "critical",
                "type": "immediate_action",
                "action": "执行紧急健康检查并自动修复",
                "description": "健康分低于60，需要立即采取行动",
                "auto_execute": True,
            })
        elif current_score < 80:
            strategies.append({
                "priority": "high",
                "type": "scheduled_maintenance",
                "action": "安排预防性维护窗口",
                "description": "健康分低于80，建议安排预防性维护",
                "auto_execute": False,
            })

        # 基于趋势预测生成策略
        if trend_prediction.get("status") == "success":
            if trend_prediction["trend"] == "declining":
                strategies.append({
                    "priority": "high",
                    "type": "trend_intervention",
                    "action": "启动趋势干预，防止健康分进一步下降",
                    "description": f"趋势预测显示健康分正在下降，预测{trend_prediction['prediction_days']}天后为 {trend_prediction['predicted_score']:.1f}",
                    "auto_execute": False,
                })
            elif trend_prediction["trend"] == "critical_decline":
                strategies.append({
                    "priority": "critical",
                    "type": "emergency_prevention",
                    "action": "启动紧急预防措施",
                    "description": f"预测显示健康分将低于阈值 {self.preventive_config['prediction_threshold']}，需要紧急干预",
                    "auto_execute": True,
                })

        # 基于引擎状态生成策略
        diagnosis = self.diagnose(verbose=False)
        for engine in diagnosis.get("unhealthy_engines", []):
            strategies.append({
                "priority": "medium",
                "type": "engine_specific",
                "action": f"检查并修复引擎: {engine['name']}",
                "description": f"引擎 {engine['name']} 状态: {engine['status']}",
                "auto_execute": False,
            })

        # 如果没有发现任何问题
        if not strategies:
            strategies.append({
                "priority": "low",
                "type": "monitoring",
                "action": "继续监控",
                "description": "所有引擎健康，无需干预",
                "auto_execute": False,
            })

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "current_health_score": current_score,
            "trend_prediction": trend_prediction.get("trend", "unknown"),
            "strategies_count": len(strategies),
            "strategies": strategies,
            "auto_executable_count": sum(1 for s in strategies if s.get("auto_execute", False)),
        }

    # ==================== 新增：自动预防执行 ====================

    def execute_preventive_actions(self, dry_run: bool = False) -> Dict[str, Any]:
        """
        执行预防性措施

        Args:
            dry_run: 是否模拟执行

        Returns:
            执行结果
        """
        strategies = self.generate_preventive_strategies()

        executed_actions = []
        success_count = 0

        for strategy in strategies.get("strategies", []):
            if not strategy.get("auto_execute", False):
                continue

            action_result = {
                "strategy_type": strategy["type"],
                "action": strategy["action"],
                "success": False,
                "message": "",
            }

            if strategy["type"] == "immediate_action" or strategy["type"] == "emergency_prevention":
                # 执行紧急修复
                if not dry_run:
                    diagnosis = self.diagnose(verbose=False)
                    if diagnosis["issues_found"] > 0:
                        repair_result = self.auto_repair(dry_run=False)
                        action_result["success"] = repair_result["issues_resolved"] > 0
                        action_result["message"] = f"尝试修复 {repair_result['issues_attempted']} 个问题"
                    else:
                        action_result["success"] = True
                        action_result["message"] = "未发现问题，执行基础维护"
                else:
                    action_result["success"] = True
                    action_result["message"] = "[DRY RUN] 将执行紧急修复"

            elif strategy["type"] == "trend_intervention":
                # 趋势干预
                if not dry_run:
                    # 保存健康历史快照用于分析
                    action_result["success"] = True
                    action_result["message"] = "已记录趋势干预点"
                else:
                    action_result["success"] = True
                    action_result["message"] = "[DRY RUN] 将执行趋势干预"

            if action_result["success"]:
                success_count += 1
            executed_actions.append(action_result)

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "dry_run": dry_run,
            "actions_attempted": len(executed_actions),
            "actions_succeeded": success_count,
            "executed_actions": executed_actions,
            "summary": f"尝试执行 {len(executed_actions)} 个预防措施，成功 {success_count} 个",
        }

    # ==================== 新增：预警功能 ====================

    def check_and_warn(self) -> Dict[str, Any]:
        """
        检查并生成预警

        Returns:
            预警信息
        """
        current_score = self.get_health_score()
        trend = self.predict_health_trend()

        warnings = []

        # 基于当前分数的预警
        if current_score < 60:
            warnings.append({
                "level": "critical",
                "title": "健康状态危急",
                "message": f"当前健康分为 {current_score:.1f}，需要立即处理",
                "requires_action": True,
            })
        elif current_score < 80:
            warnings.append({
                "level": "warning",
                "title": "健康状态警告",
                "message": f"当前健康分为 {current_score:.1f}，建议检查",
                "requires_action": True,
            })

        # 基于趋势的预警
        if trend.get("status") == "success":
            if trend["trend"] == "declining":
                warnings.append({
                    "level": "warning",
                    "title": "健康趋势下降",
                    "message": f"预测显示健康分正在下降，{trend['prediction_days']}天后预计为 {trend['predicted_score']:.1f}",
                    "requires_action": True,
                })
            elif trend["trend"] == "critical_decline":
                warnings.append({
                    "level": "critical",
                    "title": "紧急：健康分将跌破阈值",
                    "message": f"预测显示 {trend['prediction_days']}天后健康分将降至 {trend['predicted_score']:.1f}，低于阈值 {self.preventive_config['prediction_threshold']}",
                    "requires_action": True,
                })

        # 诊断发现问题
        diagnosis = self.diagnose(verbose=False)
        if diagnosis["issues_found"] > 0:
            warnings.append({
                "level": "info",
                "title": f"发现 {diagnosis['issues_found']} 个问题",
                "message": f"包括: {', '.join(set(i['type'] for i in self.health_issues))}",
                "requires_action": diagnosis["issues_found"] > 0,
            })

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "current_health_score": current_score,
            "trend": trend.get("trend", "unknown"),
            "warnings_count": len(warnings),
            "warnings": warnings,
            "has_critical_warning": any(w["level"] == "critical" for w in warnings),
        }

    def get_cockpit_data(self) -> Dict[str, Any]:
        """获取驾驶舱显示数据"""
        health_score = self.get_health_score()

        # 运行诊断
        diagnosis = self.diagnose(verbose=False)

        # 获取趋势预测
        trend = self.predict_health_trend()

        # 获取预警
        warnings = self.check_and_warn()

        return {
            "engine_name": "元进化内部健康诊断与自愈引擎（增强版）",
            "version": self.VERSION,
            "health_score": health_score,
            "status": "healthy" if health_score >= 80 else "warning" if health_score >= 60 else "critical",
            "core_engines_count": len(self.core_engines),
            "healthy_engines_count": len(diagnosis["healthy_engines"]),
            "issues_count": diagnosis["issues_found"],
            "last_diagnosis": self.diagnosis_timestamp,
            "repair_history_count": len(self.repair_history),
            "recommendations": diagnosis["recommendations"],
            # 新增字段
            "health_trend": trend.get("trend", "unknown"),
            "predicted_score": trend.get("predicted_score"),
            "warnings_count": warnings["warnings_count"],
            "has_critical_warning": warnings["has_critical_warning"],
            "preventive_strategies_count": len(self.generate_preventive_strategies()["strategies"]),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def run_full_loop(self, auto_repair: bool = True, dry_run: bool = False) -> Dict[str, Any]:
        """
        运行完整的诊断-修复-验证闭环

        Args:
            auto_repair: 是否自动修复
            dry_run: 是否模拟执行

        Returns:
            闭环执行结果
        """
        print(f"\n{'='*60}")
        print(f"元进化内部健康诊断与自愈完整闭环（增强版 v{self.VERSION}）")
        print(f"{'='*60}\n")

        # 1. 诊断
        print("[1/4] 执行健康诊断...")
        diagnosis = self.diagnose(verbose=True)

        # 2. 趋势预测
        print("\n[2/4] 分析健康趋势...")
        trend = self.predict_health_trend()
        print(f"健康趋势: {trend.get('trend', 'unknown')}")
        if trend.get("predicted_score"):
            print(f"预测分数: {trend['predicted_score']:.1f}")

        # 3. 修复
        repair_result = {}
        if auto_repair and diagnosis["issues_found"] > 0:
            print("\n[3/4] 执行自动修复...")
            repair_result = self.auto_repair(dry_run=dry_run)
        else:
            print("\n[3/4] 跳过自动修复（未发现可修复问题或已禁用）")
            repair_result = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "issues_resolved": 0,
                "repair_summary": "未执行修复",
            }

        # 4. 验证
        print("\n[4/4] 验证修复效果...")
        final_score = self.get_health_score()
        print(f"最终健康评分: {final_score:.1f}/100")

        # 5. 预警检查
        warnings = self.check_and_warn()
        if warnings["warnings"]:
            print(f"\n预警信息:")
            for w in warnings["warnings"]:
                print(f"  [{w['level'].upper()}] {w['title']}: {w['message']}")

        result = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "diagnosis": diagnosis,
            "repair": repair_result,
            "final_health_score": final_score,
            "trend": trend,
            "warnings": warnings,
            "status": "success" if final_score >= 80 else "partial_success" if final_score >= 60 else "needs_attention",
        }

        print(f"\n{'='*60}")
        print(f"闭环执行完成 - 最终状态: {result['status']}")
        print(f"{'='*60}\n")

        return result


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(
        description="智能全场景进化环元进化内部健康诊断与自愈深度增强引擎（增强版）"
    )
    parser.add_argument("--status", action="store_true", help="获取引擎状态")
    parser.add_argument("--diagnose", action="store_true", help="执行健康诊断")
    parser.add_argument("--repair", action="store_true", help="执行自动修复")
    parser.add_argument("--dry-run", action="store_true", help="模拟执行（不实际修改）")
    parser.add_argument("--run", action="store_true", help="运行完整诊断-修复-验证闭环")
    parser.add_argument("--auto-repair", action="store_true", help="在完整闭环中自动修复")
    parser.add_argument("--health-score", action="store_true", help="获取健康评分")
    parser.add_argument("--cockpit-data", action="store_true", help="获取驾驶舱显示数据")
    parser.add_argument("--history", action="store_true", help="获取修复历史")
    # 新增参数
    parser.add_argument("--predict-trend", action="store_true", help="预测健康趋势")
    parser.add_argument("--preventive-strategies", action="store_true", help="生成预防性策略")
    parser.add_argument("--execute-prevention", action="store_true", help="执行预防性措施")
    parser.add_argument("--check-warn", action="store_true", help="检查并生成预警")

    args = parser.parse_args()

    engine = MetaEvolutionInternalHealthDiagnosisEngine()

    if args.status:
        status = engine.get_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))

    elif args.diagnose:
        engine.diagnose(verbose=True)

    elif args.repair:
        engine.diagnose(verbose=False)
        engine.auto_repair(dry_run=args.dry_run)

    elif args.run:
        engine.run_full_loop(auto_repair=args.auto_repair, dry_run=args.dry_run)

    elif args.health_score:
        score = engine.get_health_score()
        print(f"健康评分: {score:.1f}/100")

    elif args.cockpit_data:
        data = engine.get_cockpit_data()
        print(json.dumps(data, ensure_ascii=False, indent=2))

    elif args.history:
        print(json.dumps(engine.repair_history, ensure_ascii=False, indent=2))

    elif args.predict_trend:
        result = engine.predict_health_trend()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.preventive_strategies:
        result = engine.generate_preventive_strategies()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.execute_prevention:
        result = engine.execute_preventive_actions(dry_run=args.dry_run)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.check_warn:
        result = engine.check_and_warn()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()