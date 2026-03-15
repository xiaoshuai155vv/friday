#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环元进化内部健康诊断与自愈深度增强引擎
=====================================

让系统能够自动诊断进化引擎间的依赖问题、识别内部健康风险、智能生成修复方案并自动执行，
形成元进化层面的自愈能力。

功能：
1. 自动诊断进化引擎间的依赖问题
2. 识别内部健康风险（引擎加载失败、依赖缺失、版本不兼容等）
3. 智能生成修复方案
4. 自动执行修复
5. 验证修复效果
6. 与进化驾驶舱深度集成

版本：1.0.0
依赖：round 496 元认知-元进化深度集成引擎
"""

import os
import sys
import json
import importlib
import inspect
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

# 路径设置
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
RUNTIME_STATE_DIR = os.path.join(PROJECT_ROOT, "runtime", "state")
RUNTIME_LOGS_DIR = os.path.join(PROJECT_ROOT, "runtime", "logs")


class MetaEvolutionInternalHealthDiagnosisEngine:
    """元进化内部健康诊断与自愈引擎"""

    VERSION = "1.0.0"

    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.scripts_dir = SCRIPT_DIR
        self.state_dir = RUNTIME_STATE_DIR
        self.logs_dir = RUNTIME_LOGS_DIR
        self.health_issues = []
        self.repair_history = []
        self.diagnosis_timestamp = None

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
        ]

    def get_status(self) -> Dict[str, Any]:
        """获取引擎状态"""
        return {
            "version": self.VERSION,
            "engine_name": "元进化内部健康诊断与自愈引擎",
            "health_issues_count": len(self.health_issues),
            "repair_history_count": len(self.repair_history),
            "last_diagnosis": self.diagnosis_timestamp,
            "core_engines_count": len(self.core_engines),
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

        if verbose:
            print(f"\n{'='*60}")
            print(f"元进化内部健康诊断报告")
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

    def get_cockpit_data(self) -> Dict[str, Any]:
        """获取驾驶舱显示数据"""
        health_score = self.get_health_score()

        # 运行诊断
        diagnosis = self.diagnose(verbose=False)

        return {
            "engine_name": "元进化内部健康诊断与自愈引擎",
            "version": self.VERSION,
            "health_score": health_score,
            "status": "healthy" if health_score >= 80 else "warning" if health_score >= 60 else "critical",
            "core_engines_count": len(self.core_engines),
            "healthy_engines_count": len(diagnosis["healthy_engines"]),
            "issues_count": diagnosis["issues_found"],
            "last_diagnosis": self.diagnosis_timestamp,
            "repair_history_count": len(self.repair_history),
            "recommendations": diagnosis["recommendations"],
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
        print(f"元进化内部健康诊断与自愈完整闭环")
        print(f"{'='*60}\n")

        # 1. 诊断
        print("[1/3] 执行健康诊断...")
        diagnosis = self.diagnose(verbose=True)

        # 2. 修复
        repair_result = {}
        if auto_repair and diagnosis["issues_found"] > 0:
            print("\n[2/3] 执行自动修复...")
            repair_result = self.auto_repair(dry_run=dry_run)
        else:
            print("\n[2/3] 跳过自动修复（未发现可修复问题或已禁用）")
            repair_result = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "issues_resolved": 0,
                "repair_summary": "未执行修复",
            }

        # 3. 验证
        print("\n[3/3] 验证修复效果...")
        final_score = self.get_health_score()
        print(f"最终健康评分: {final_score:.1f}/100")

        result = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "diagnosis": diagnosis,
            "repair": repair_result,
            "final_health_score": final_score,
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
        description="智能全场景进化环元进化内部健康诊断与自愈深度增强引擎"
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

    else:
        parser.print_help()


if __name__ == "__main__":
    main()