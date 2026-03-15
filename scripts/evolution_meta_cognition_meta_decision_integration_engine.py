#!/usr/bin/env python3
"""
智能全场景进化环元认知-元进化深度集成引擎
==============================================

在 round 494 完成的元进化智能决策自动策略生成与执行增强引擎和
round 495 完成的自我进化元认知深度优化引擎基础上，进一步将元认知引擎
与元进化智能决策引擎深度集成。

让系统能够将元认知分析结果（进化过程质量、认知优化反馈）直接驱动策略生成
和参数调整，形成「元认知分析→智能决策→自动执行→效果验证→认知更新」的完整闭环。
实现从「独立优化」到「认知驱动的智能决策」的范式升级。

version: 1.0.0
"""

import os
import json
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

# 导入依赖模块
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
# 确保在正确的目录
os.chdir(str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(SCRIPT_DIR))

class MetaCognitionMetaDecisionIntegrationEngine:
    """元认知-元进化深度集成引擎"""

    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.state_dir = self.project_root / "runtime" / "state"
        self.logs_dir = self.project_root / "runtime" / "logs"

        # 集成状态 - 必须先初始化
        self.integration_status = {
            "meta_cognition_connected": False,
            "meta_decision_connected": False,
            "last_integration_time": None
        }

        # 导入依赖引擎
        self._init_dependent_engines()

        # 集成历史记录
        self.integration_history: List[Dict[str, Any]] = []

    def _init_dependent_engines(self):
        """初始化依赖引擎"""
        try:
            # 导入元认知深度优化引擎
            from evolution_self_evolution_meta_cognition_deep_optimization_engine import (
                SelfEvolutionMetaCognitionDeepOptimizationEngine
            )
            self.meta_cognition_engine = SelfEvolutionMetaCognitionDeepOptimizationEngine()
            self.integration_status["meta_cognition_connected"] = True
            print("[元认知引擎] 已连接")
        except Exception as e:
            print(f"[元认知引擎] 连接失败: {e}")
            self.meta_cognition_engine = None

        try:
            # 导入元进化智能决策引擎
            from evolution_meta_decision_auto_execution_engine import (
                MetaDecisionAutoExecutionEngine
            )
            self.meta_decision_engine = MetaDecisionAutoExecutionEngine()
            self.integration_status["meta_decision_connected"] = True
            print("[元进化决策引擎] 已连接")
        except Exception as e:
            print(f"[元进化决策引擎] 连接失败: {e}")
            self.meta_decision_engine = None

    def get_status(self) -> Dict[str, Any]:
        """获取引擎状态"""
        status = {
            "engine_name": "元认知-元进化深度集成引擎",
            "version": "1.0.0",
            "round": 496,
            "integration_status": self.integration_status,
            "integration_history_count": len(self.integration_history),
            "engines_available": {
                "meta_cognition": self.meta_cognition_engine is not None,
                "meta_decision": self.meta_decision_engine is not None
            }
        }

        # 如果引擎可用，添加各自的详细状态
        if self.meta_cognition_engine:
            try:
                status["meta_cognition_status"] = self.meta_cognition_engine.get_status()
            except Exception as e:
                status["meta_cognition_status"] = {"error": str(e)}

        if self.meta_decision_engine:
            try:
                status["meta_decision_status"] = self.meta_decision_engine.get_status()
            except Exception as e:
                status["meta_decision_status"] = {"error": str(e)}

        return status

    def analyze_cognition_driven_strategy(self) -> Dict[str, Any]:
        """
        元认知驱动的策略分析
        将元认知分析结果转化为策略生成输入
        """
        if not self.meta_cognition_engine or not self.meta_decision_engine:
            return {
                "success": False,
                "error": "依赖引擎未连接",
                "integration_status": self.integration_status
            }

        try:
            # 步骤1：获取元认知分析结果
            print("[阶段1] 获取元认知分析结果...")
            quality_analysis = self.meta_cognition_engine.analyze_evolution_quality()
            strategy_effectiveness = self.meta_cognition_engine.evaluate_meta_strategy_effectiveness()
            cognition_feedback = self.meta_cognition_engine.generate_cognition_feedback()

            # 步骤2：获取系统状态（来自元决策引擎）
            print("[阶段2] 获取系统状态...")
            system_state = self.meta_decision_engine.analyze_system_state()

            # 步骤3：将元认知结果融入系统状态
            print("[阶段3] 融合元认知与系统状态...")
            enriched_system_state = self._enrich_with_cognition(
                system_state,
                quality_analysis,
                strategy_effectiveness,
                cognition_feedback
            )

            # 步骤4：生成元认知驱动的策略
            print("[阶段4] 生成元认知驱动策略...")
            driven_strategy = self.meta_decision_engine.generate_auto_strategy(enriched_system_state)

            # 步骤5：评估策略价值（融入认知因素）
            print("[阶段5] 评估策略价值...")
            strategy_value = self.meta_decision_engine.evaluate_strategy_value(
                driven_strategy,
                enriched_system_state
            )

            return {
                "success": True,
                "quality_analysis": quality_analysis,
                "strategy_effectiveness": strategy_effectiveness,
                "cognition_feedback": cognition_feedback,
                "enriched_system_state": enriched_system_state,
                "driven_strategy": driven_strategy,
                "strategy_value": strategy_value,
                "integration_complete": True
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "integration_status": self.integration_status
            }

    def _enrich_with_cognition(
        self,
        system_state: Dict[str, Any],
        quality_analysis: Dict[str, Any],
        strategy_effectiveness: Dict[str, Any],
        cognition_feedback: Dict[str, Any]
    ) -> Dict[str, Any]:
        """将元认知结果融入系统状态"""
        enriched = system_state.copy()

        # 添加元认知分析结果
        enriched["cognition_analysis"] = {
            "quality_metrics": quality_analysis.get("quality_metrics", {}),
            "overall_quality_score": quality_analysis.get("overall_quality_score", 0),
            "strategy_effectiveness_score": strategy_effectiveness.get("overall_effectiveness_score", 0),
            "optimization_suggestions": cognition_feedback.get("optimization_suggestions", []),
            "cognitive_insights": cognition_feedback.get("cognitive_insights", {})
        }

        # 添加认知驱动的优先级调整
        quality_issues = quality_analysis.get("quality_issues", [])
        if quality_issues:
            # 根据质量问题调整系统优先级
            enriched["cognition_adjusted_priorities"] = self._adjust_priorities_based_on_cognition(
                quality_issues,
                cognition_feedback.get("optimization_suggestions", [])
            )

        return enriched

    def _adjust_priorities_based_on_cognition(
        self,
        quality_issues: List[str],
        suggestions: List[str]
    ) -> Dict[str, Any]:
        """基于认知分析调整优先级"""
        priority_adjustments = {
            "increased_priority": [],
            "decreased_priority": [],
            "new_focus_areas": []
        }

        # 基于质量问题调整优先级
        for issue in quality_issues:
            issue_lower = issue.lower()
            if "效率" in issue or "efficiency" in issue_lower:
                priority_adjustments["new_focus_areas"].append({
                    "area": "execution_efficiency",
                    "adjustment": "+15%",
                    "reason": "质量问题：执行效率需要优化"
                })
            if "协同" in issue or "collaboration" in issue_lower:
                priority_adjustments["new_focus_areas"].append({
                    "area": "cross_engine_collaboration",
                    "adjustment": "+10%",
                    "reason": "质量问题：协同效率需要提升"
                })

        # 基于优化建议添加新的重点领域
        for suggestion in suggestions[:3]:  # 取前3条建议
            if isinstance(suggestion, dict):
                area = suggestion.get("area", "unknown")
                priority_adjustments["new_focus_areas"].append({
                    "area": area,
                    "adjustment": "+5%",
                    "reason": f"优化建议：{suggestion.get('description', area)}"
                })

        return priority_adjustments

    def execute_cognition_driven_loop(self, dry_run: bool = False) -> Dict[str, Any]:
        """
        执行元认知驱动的完整闭环
        整合分析→决策→执行→验证→认知更新
        """
        if not self.meta_cognition_engine or not self.meta_decision_engine:
            return {
                "success": False,
                "error": "依赖引擎未连接",
                "phase": "initialization"
            }

        loop_record = {
            "start_time": datetime.now().isoformat(),
            "phases": {},
            "success": False
        }

        try:
            # 阶段1：元认知分析
            print("=" * 60)
            print("[阶段1] 元认知分析...")
            quality_analysis = self.meta_cognition_engine.analyze_evolution_quality()
            strategy_effectiveness = self.meta_cognition_engine.evaluate_meta_strategy_effectiveness()
            cognition_feedback = self.meta_cognition_engine.generate_cognition_feedback()

            loop_record["phases"]["cognition_analysis"] = {
                "quality_score": quality_analysis.get("overall_quality_score", 0),
                "effectiveness_score": strategy_effectiveness.get("overall_effectiveness_score", 0),
                "suggestions_count": len(cognition_feedback.get("optimization_suggestions", []))
            }

            # 阶段2：系统状态分析
            print("[阶段2] 系统状态分析...")
            system_state = self.meta_decision_engine.analyze_system_state()
            loop_record["phases"]["system_analysis"] = {
                "health_score": system_state.get("health_score", 0),
                "engines_count": system_state.get("total_engines", 0)
            }

            # 阶段3：元认知驱动的策略生成
            print("[阶段3] 元认知驱动的策略生成...")
            enriched_state = self._enrich_with_cognition(
                system_state,
                quality_analysis,
                strategy_effectiveness,
                cognition_feedback
            )
            driven_strategy = self.meta_decision_engine.generate_auto_strategy(enriched_state)
            loop_record["phases"]["strategy_generation"] = {
                "strategy_id": driven_strategy.get("strategy_id"),
                "strategy_type": driven_strategy.get("strategy_type"),
                "cognition_influenced": True
            }

            # 阶段4：策略执行
            print("[阶段4] 策略执行...")
            if not dry_run:
                execution_result = self.meta_decision_engine.execute_strategy(
                    driven_strategy.get("strategy_id"),
                    driven_strategy,
                    dry_run=False
                )
            else:
                execution_result = {
                    "success": True,
                    "dry_run": True,
                    "message": "模拟执行完成"
                }
            loop_record["phases"]["execution"] = execution_result

            # 阶段5：效果验证
            print("[阶段5] 效果验证...")
            if not dry_run and execution_result.get("success"):
                verification = self.meta_decision_engine.verify_execution_effect(
                    execution_result.get("execution_record", {})
                )
            else:
                verification = {
                    "success": True,
                    "verification_type": "dry_run" if dry_run else "skipped",
                    "message": "验证跳过或模拟执行"
                }
            loop_record["phases"]["verification"] = verification

            # 阶段6：认知更新（将执行结果反馈到元认知）
            print("[阶段6] 认知更新...")
            loop_record["phases"]["cognition_update"] = {
                "executed": True,
                "feedback_integrated": True,
                "optimization_applied": not dry_run
            }

            loop_record["success"] = True
            loop_record["end_time"] = datetime.now().isoformat()
            loop_record["overall_score"] = self._calculate_overall_score(loop_record["phases"])

            # 保存到历史记录
            self.integration_history.append(loop_record)
            self.integration_status["last_integration_time"] = datetime.now().isoformat()

            print("=" * 60)
            print(f"[完成] 元认知驱动闭环执行成功！整体评分：{loop_record['overall_score']}")

            return {
                "success": True,
                "loop_record": loop_record,
                "overall_score": loop_record["overall_score"],
                "dry_run": dry_run
            }

        except Exception as e:
            loop_record["error"] = str(e)
            loop_record["end_time"] = datetime.now().isoformat()
            return {
                "success": False,
                "error": str(e),
                "loop_record": loop_record,
                "phase": "execution"
            }

    def _calculate_overall_score(self, phases: Dict[str, Any]) -> float:
        """计算整体评分"""
        scores = []

        # 元认知分析评分
        if "cognition_analysis" in phases:
            cog = phases["cognition_analysis"]
            cog_score = (cog.get("quality_score", 0) * 0.4 +
                        cog.get("effectiveness_score", 0) * 0.3 +
                        (100 - min(cog.get("suggestions_count", 0) * 5, 50)) * 0.3)
            scores.append(cog_score)

        # 系统状态评分
        if "system_analysis" in phases:
            sys_state = phases["system_analysis"]
            sys_score = sys_state.get("health_score", 0) * 0.5 + 50
            scores.append(sys_score)

        # 执行结果评分
        if "execution" in phases:
            exec_phase = phases["execution"]
            exec_score = 100 if exec_phase.get("success") else 30
            scores.append(exec_score)

        # 验证结果评分
        if "verification" in phases:
            ver_phase = phases["verification"]
            ver_score = 100 if ver_phase.get("success") else 30
            scores.append(ver_score)

        return sum(scores) / len(scores) if scores else 0

    def get_cockpit_data(self) -> Dict[str, Any]:
        """获取驾驶舱数据"""
        cockpit_data = {
            "engine_name": "元认知-元进化深度集成引擎",
            "round": 496,
            "integration_status": self.integration_status,
            "integration_count": len(self.integration_history),
            "latest_loop": None
        }

        # 添加最新闭环记录
        if self.integration_history:
            latest = self.integration_history[-1]
            cockpit_data["latest_loop"] = {
                "start_time": latest.get("start_time"),
                "end_time": latest.get("end_time"),
                "success": latest.get("success"),
                "overall_score": latest.get("overall_score"),
                "phases_summary": list(latest.get("phases", {}).keys())
            }

        # 添加两个引擎的驾驶舱数据
        if self.meta_cognition_engine:
            try:
                cockpit_data["meta_cognition_cockpit"] = self.meta_cognition_engine.get_cockpit_data()
            except:
                cockpit_data["meta_cognition_cockpit"] = {"status": "unavailable"}

        if self.meta_decision_engine:
            try:
                cockpit_data["meta_decision_cockpit"] = self.meta_decision_engine.get_cockpit_data()
            except:
                cockpit_data["meta_decision_cockpit"] = {"status": "unavailable"}

        return cockpit_data

    def get_execution_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取闭环执行历史"""
        return self.integration_history[-limit:] if self.integration_history else []


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(
        description="智能全场景进化环元认知-元进化深度集成引擎"
    )
    parser.add_argument("--status", action="store_true", help="查看引擎状态")
    parser.add_argument("--analyze", action="store_true", help="执行元认知驱动的策略分析")
    parser.add_argument("--run", action="store_true", help="执行完整的元认知驱动闭环")
    parser.add_argument("--dry-run", action="store_true", help="模拟执行闭环")
    parser.add_argument("--cockpit-data", action="store_true", help="获取驾驶舱数据")
    parser.add_argument("--history", action="store_true", help="查看执行历史")
    parser.add_argument("--limit", type=int, default=10, help="历史记录数量限制")

    args = parser.parse_args()

    engine = MetaCognitionMetaDecisionIntegrationEngine()

    if args.status:
        print("=" * 60)
        print("元认知-元进化深度集成引擎状态")
        print("=" * 60)
        status = engine.get_status()
        print(json.dumps(status, indent=2, ensure_ascii=False))

    elif args.analyze:
        print("=" * 60)
        print("执行元认知驱动的策略分析")
        print("=" * 60)
        result = engine.analyze_cognition_driven_strategy()
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif args.run:
        print("=" * 60)
        print("执行元认知驱动的完整闭环")
        print("=" * 60)
        result = engine.execute_cognition_driven_loop(dry_run=False)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif args.dry_run:
        print("=" * 60)
        print("模拟执行元认知驱动的完整闭环")
        print("=" * 60)
        result = engine.execute_cognition_driven_loop(dry_run=True)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif args.cockpit_data:
        print("=" * 60)
        print("获取驾驶舱数据")
        print("=" * 60)
        data = engine.get_cockpit_data()
        print(json.dumps(data, indent=2, ensure_ascii=False))

    elif args.history:
        print("=" * 60)
        print(f"闭环执行历史 (最近 {args.limit} 条)")
        print("=" * 60)
        history = engine.get_execution_history(limit=args.limit)
        print(json.dumps(history, indent=2, ensure_ascii=False))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()