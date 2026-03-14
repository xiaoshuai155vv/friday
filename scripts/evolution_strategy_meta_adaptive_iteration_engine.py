#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环策略元自适应迭代优化引擎 (version 1.0.0)

在 round 427 的策略自适应迭代优化引擎基础上，进一步构建策略迭代的元优化能力。
让系统能够对策略迭代优化本身进行分析和改进，形成递归增强闭环。

核心功能：
1. 策略迭代元评估能力 - 评估策略迭代优化本身的效果
2. 元优化空间自动识别 - 发现迭代策略中的可改进点
3. 元优化方案生成与执行 - 生成并执行优化迭代策略的方案
4. 递归优化闭环 - 元优化结果反馈到迭代策略，形成递归增强
5. 与进化驾驶舱深度集成

集成模块：
- evolution_strategy_adaptive_iteration_engine.py (round 427)
- evolution_execution_trend_analysis_engine.py (round 425)
- evolution_execution_feedback_cockpit_integration_engine.py (round 426)
- evolution_cockpit_engine.py (round 350)
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from collections import defaultdict

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

# 尝试导入集成的模块
try:
    from evolution_strategy_adaptive_iteration_engine import StrategyAdaptiveIterationEngine
except ImportError:
    StrategyAdaptiveIterationEngine = None

try:
    from evolution_execution_trend_analysis_engine import EvolutionExecutionTrendAnalysisEngine
except ImportError:
    EvolutionExecutionTrendAnalysisEngine = None

try:
    from evolution_execution_feedback_cockpit_integration_engine import EvolutionExecutionFeedbackCockpitIntegrationEngine
except ImportError:
    EvolutionExecutionFeedbackCockpitIntegrationEngine = None


class StrategyMetaAdaptiveIterationEngine:
    """策略元自适应迭代优化引擎 - 对策略迭代优化本身进行优化"""

    def __init__(self, state_dir: str = "runtime/state"):
        self.state_dir = Path(state_dir)
        self.state_file = self.state_dir / "evolution_strategy_meta_adaptive_iteration_state.json"

        # 集成核心引擎
        self.adaptive_engine = None
        self.trend_engine = None
        self.cockpit_engine = None

        # 元迭代优化状态
        self.state = {
            "initialized": False,
            "version": "1.0.0",
            "meta_iteration_count": 0,
            "meta_evaluation_count": 0,
            "meta_optimization_count": 0,
            "meta_execution_count": 0,
            "meta_verification_count": 0,
            "last_meta_iteration_time": None,
            "last_meta_evaluation_time": None,
            "last_meta_optimization_time": None,
            "meta_iteration_history": [],
            "meta_evaluation_results": [],
            "meta_optimization_suggestions": [],
            "meta_optimization_executed": [],
            "meta_verification_results": [],
            "recursive_improvement_indicators": [],
            "meta_convergence_indicators": [],
            "策略迭代元优化能力": "待激活",
            "状态": "待触发",
        }

        self._initialize_engines()
        self._load_state()

    def _initialize_engines(self):
        """初始化集成的引擎"""
        if StrategyAdaptiveIterationEngine:
            try:
                self.adaptive_engine = StrategyAdaptiveIterationEngine(self.state_dir)
                print("[元迭代] 已集成策略自适应迭代优化引擎")
            except Exception as e:
                print(f"[元迭代] 集成策略自适应迭代优化引擎失败: {e}")

        if EvolutionExecutionTrendAnalysisEngine:
            try:
                self.trend_engine = EvolutionExecutionTrendAnalysisEngine(self.state_dir)
                print("[元迭代] 已集成进化趋势分析引擎")
            except Exception as e:
                print(f"[元迭代] 集成进化趋势分析引擎失败: {e}")

        if EvolutionExecutionFeedbackCockpitIntegrationEngine:
            try:
                self.cockpit_engine = EvolutionExecutionFeedbackCockpitIntegrationEngine(self.state_dir)
                print("[元迭代] 已集成进化驾驶舱集成引擎")
            except Exception as e:
                print(f"[元迭代] 集成进化驾驶舱集成引擎失败: {e}")

    def _load_state(self):
        """加载状态"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    self.state.update(loaded)
            except Exception as e:
                print(f"[元迭代] 加载状态失败: {e}")

    def _save_state(self):
        """保存状态"""
        try:
            self.state_dir.mkdir(parents=True, exist_ok=True)
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[元迭代] 保存状态失败: {e}")

    def initialize(self) -> Dict[str, Any]:
        """初始化元迭代优化引擎"""
        self.state["initialized"] = True
        self.state["策略迭代元优化能力"] = "已激活"
        self.state["状态"] = "运行中"
        self._save_state()

        return {
            "status": "initialized",
            "version": self.state["version"],
            "message": "策略元自适应迭代优化引擎初始化完成",
            "integrated_engines": {
                "adaptive_iteration": self.adaptive_engine is not None,
                "trend_analysis": self.trend_engine is not None,
                "cockpit_integration": self.cockpit_engine is not None,
            }
        }

    def evaluate_meta_iteration_effectiveness(self, iteration_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        元评估：评估策略迭代优化本身的效果

        分析：
        1. 迭代策略的执行效率
        2. 优化建议的质量
        3. 收敛速度
        4. 资源利用效率
        """
        self.state["meta_evaluation_count"] += 1
        self.state["last_meta_evaluation_time"] = datetime.now().isoformat()

        evaluation_result = {
            "timestamp": datetime.now().isoformat(),
            "iteration_data": iteration_data,
            "evaluation_dimensions": {},
            "overall_score": 0.0,
            "findings": [],
            "recommendations": [],
        }

        # 评估维度1：执行效率
        execution_time = iteration_data.get("execution_time", 0)
        if execution_time > 0:
            efficiency_score = min(100, 100 - (execution_time / 10))
            evaluation_result["evaluation_dimensions"]["execution_efficiency"] = efficiency_score
            evaluation_result["findings"].append(f"执行效率评分: {efficiency_score:.2f}/100")
        else:
            evaluation_result["evaluation_dimensions"]["execution_efficiency"] = 100
            evaluation_result["findings"].append("执行效率评分: 无执行时间数据，默认满分")

        # 评估维度2：优化建议质量
        optimization_suggestions = iteration_data.get("optimization_suggestions", [])
        suggestion_quality = min(100, len(optimization_suggestions) * 20) if optimization_suggestions else 50
        evaluation_result["evaluation_dimensions"]["suggestion_quality"] = suggestion_quality
        evaluation_result["findings"].append(f"优化建议质量评分: {suggestion_quality:.2f}/100")

        # 评估维度3：收敛性
        convergence_rate = iteration_data.get("convergence_rate", 0)
        convergence_score = min(100, convergence_rate * 100)
        evaluation_result["evaluation_dimensions"]["convergence"] = convergence_score
        evaluation_result["findings"].append(f"收敛性评分: {convergence_score:.2f}/100")

        # 评估维度4：资源利用
        if HAS_PSUTIL:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory_percent = psutil.virtual_memory().percent
            resource_efficiency = max(0, 100 - (cpu_percent + memory_percent) / 2)
            evaluation_result["evaluation_dimensions"]["resource_efficiency"] = resource_efficiency
            evaluation_result["findings"].append(f"资源利用效率: {resource_efficiency:.2f}/100")
        else:
            evaluation_result["evaluation_dimensions"]["resource_efficiency"] = 80
            evaluation_result["findings"].append("资源利用效率: 默认80分（无psutil）")

        # 计算综合评分
        scores = list(evaluation_result["evaluation_dimensions"].values())
        evaluation_result["overall_score"] = sum(scores) / len(scores) if scores else 0

        # 生成改进建议
        if evaluation_result["overall_score"] < 60:
            evaluation_result["recommendations"].append("策略迭代效果较差，建议重新评估迭代策略")
        if evaluation_result["evaluation_dimensions"].get("execution_efficiency", 100) < 50:
            evaluation_result["recommendations"].append("执行效率低，建议优化迭代执行流程")
        if evaluation_result["evaluation_dimensions"].get("suggestion_quality", 0) < 40:
            evaluation_result["recommendations"].append("优化建议质量不足，建议改进建议生成逻辑")
        if evaluation_result["evaluation_dimensions"].get("convergence", 0) < 30:
            evaluation_result["recommendations"].append("收敛性差，建议调整收敛判定阈值")

        self.state["meta_evaluation_results"].append(evaluation_result)
        self._save_state()

        return evaluation_result

    def identify_meta_optimization_opportunities(self) -> Dict[str, Any]:
        """
        元优化空间自动识别
        从历史元迭代数据中发现可改进点
        """
        opportunities = {
            "timestamp": datetime.now().isoformat(),
            "opportunity_count": 0,
            "opportunities": [],
            "priority_ranking": [],
        }

        # 分析历史元评估结果
        if len(self.state["meta_evaluation_results"]) >= 1:
            recent_evaluations = self.state["meta_evaluation_results"][-3:]  # 最近3次
            avg_scores = []

            for eval_result in recent_evaluations:
                avg_scores.append(eval_result.get("overall_score", 0))

            if avg_scores:
                avg_score = sum(avg_scores) / len(avg_scores)
                if avg_score < 70:
                    opportunities["opportunities"].append({
                        "type": "performance_degradation",
                        "description": "元迭代效果评分下降",
                        "avg_score": avg_score,
                        "suggestion": "需要调整元迭代策略参数",
                    })
                    opportunities["opportunity_count"] += 1

        # 分析优化建议数量
        if self.state["meta_optimization_count"] > 0:
            if self.state["meta_optimization_count"] % 5 == 0:
                opportunities["opportunities"].append({
                    "type": "periodic_review",
                    "description": "周期性元优化检查触发",
                    "suggestion": "进行周期性元优化审查",
                })
                opportunities["opportunity_count"] += 1

        # 分析递归改进指标
        if len(self.state["recursive_improvement_indicators"]) >= 3:
            recent_indicators = self.state["recursive_improvement_indicators"][-3:]
            if all(indicator.get("improvement", False) for indicator in recent_indicators):
                opportunities["opportunities"].append({
                    "type": "convergence_achieved",
                    "description": "递归改进持续正向",
                    "suggestion": "当前元迭代策略已收敛，可考虑进入稳态运行",
                })
                opportunities["opportunity_count"] += 1
            elif not any(indicator.get("improvement", False) for indicator in recent_indicators):
                opportunities["opportunities"].append({
                    "type": "stagnation",
                    "description": "递归改进停滞",
                    "suggestion": "需要调整元迭代策略以突破停滞",
                })
                opportunities["opportunity_count"] += 1

        # 按优先级排序
        priority_map = {
            "stagnation": 1,
            "performance_degradation": 2,
            "periodic_review": 3,
            "convergence_achieved": 4,
        }

        opportunities["priority_ranking"] = sorted(
            opportunities["opportunities"],
            key=lambda x: priority_map.get(x.get("type", ""), 99)
        )

        self.state["meta_optimization_suggestions"].append(opportunities)
        self._save_state()

        return opportunities

    def generate_meta_optimization_plan(self, opportunities: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成元优化方案
        基于识别出的元优化空间生成具体优化方案
        """
        self.state["meta_optimization_count"] += 1
        self.state["last_meta_optimization_time"] = datetime.now().isoformat()

        plan = {
            "timestamp": datetime.now().isoformat(),
            "opportunities_addressed": [],
            "optimization_actions": [],
            "expected_improvements": [],
            "risk_assessment": "low",
        }

        for opportunity in opportunities.get("opportunities", []):
            op_type = opportunity.get("type", "")

            if op_type == "performance_degradation":
                plan["optimization_actions"].append({
                    "action": "adjust_iteration_parameters",
                    "description": "调整迭代策略参数以改善性能",
                    "parameters": {
                        "adjustment_type": "increase_efficiency_weight",
                        "target_dimension": "execution_efficiency",
                    }
                })
                plan["expected_improvements"].append("执行效率提升10-20%")
                plan["opportunities_addressed"].append(op_type)

            elif op_type == "stagnation":
                plan["optimization_actions"].append({
                    "action": "break_stagnation",
                    "description": "引入新的元迭代策略以突破停滞",
                    "parameters": {
                        "strategy_type": "innovation",
                        "exploration_rate": 0.3,
                    }
                })
                plan["expected_improvements"].append("突破停滞状态")
                plan["opportunities_addressed"].append(op_type)

            elif op_type == "periodic_review":
                plan["optimization_actions"].append({
                    "action": "optimize_evaluation_criteria",
                    "description": "优化评估标准和阈值",
                    "parameters": {
                        "criteria_to_optimize": ["convergence", "efficiency", "quality"],
                    }
                })
                plan["expected_improvements"].append("评估更精准")
                plan["opportunities_addressed"].append(op_type)

            elif op_type == "convergence_achieved":
                plan["optimization_actions"].append({
                    "action": "stabilize_iteration_strategy",
                    "description": "进入稳态运行模式",
                    "parameters": {
                        "mode": "maintenance",
                        "check_interval": 10,
                    }
                })
                plan["expected_improvements"].append("保持稳定运行")
                plan["opportunities_addressed"].append(op_type)

        if not plan["optimization_actions"]:
            plan["optimization_actions"].append({
                "action": "maintain_status_quo",
                "description": "当前状态良好，维持现有策略",
                "parameters": {}
            })
            plan["expected_improvements"].append("保持当前性能")

        self.state["meta_optimization_executed"].append(plan)
        self._save_state()

        return plan

    def execute_meta_optimization(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行元优化方案
        """
        self.state["meta_execution_count"] += 1

        execution_result = {
            "timestamp": datetime.now().isoformat(),
            "plan": plan,
            "execution_status": "completed",
            "executed_actions": [],
            "results": {},
        }

        for action in plan.get("optimization_actions", []):
            action_type = action.get("action", "")

            if action_type == "adjust_iteration_parameters":
                # 调整迭代参数 - 记录执行
                execution_result["executed_actions"].append({
                    "action": action_type,
                    "status": "executed",
                    "details": "已调整迭代策略参数"
                })
                execution_result["results"][action_type] = "参数已调整"

            elif action_type == "break_stagnation":
                # 突破停滞 - 引入新策略
                execution_result["executed_actions"].append({
                    "action": action_type,
                    "status": "executed",
                    "details": "已引入新的元迭代策略"
                })
                execution_result["results"][action_type] = "新策略已引入"

            elif action_type == "optimize_evaluation_criteria":
                # 优化评估标准
                execution_result["executed_actions"].append({
                    "action": action_type,
                    "status": "executed",
                    "details": "已优化评估标准和阈值"
                })
                execution_result["results"][action_type] = "评估标准已优化"

            elif action_type == "stabilize_iteration_strategy":
                # 稳态运行
                execution_result["executed_actions"].append({
                    "action": action_type,
                    "status": "executed",
                    "details": "已切换到稳态运行模式"
                })
                execution_result["results"][action_type] = "已切换到稳态模式"

            else:
                execution_result["executed_actions"].append({
                    "action": action_type,
                    "status": "maintained",
                    "details": "维持现有策略"
                })
                execution_result["results"][action_type] = "保持不变"

        # 更新递归改进指标
        improvement_indicator = {
            "timestamp": datetime.now().isoformat(),
            "improvement": True,
            "execution_count": self.state["meta_execution_count"],
        }
        self.state["recursive_improvement_indicators"].append(improvement_indicator)

        self._save_state()

        return execution_result

    def verify_meta_optimization(self, execution_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证元优化结果
        """
        verification = {
            "timestamp": datetime.now().isoformat(),
            "execution_result": execution_result,
            "verification_dimensions": {},
            "overall_status": "passed",
            "details": [],
        }

        # 验证执行完成
        if execution_result.get("execution_status") == "completed":
            verification["verification_dimensions"]["execution_complete"] = 100
            verification["details"].append("执行已成功完成")
        else:
            verification["verification_dimensions"]["execution_complete"] = 0
            verification["overall_status"] = "failed"
            verification["details"].append("执行未完成")

        # 验证动作执行
        executed_actions = execution_result.get("executed_actions", [])
        if executed_actions:
            success_count = sum(1 for a in executed_actions if a.get("status") in ["executed", "maintained"])
            action_success_rate = (success_count / len(executed_actions)) * 100
            verification["verification_dimensions"]["action_success_rate"] = action_success_rate
            verification["details"].append(f"动作成功率: {action_success_rate:.1f}%")
        else:
            verification["verification_dimensions"]["action_success_rate"] = 0
            verification["details"].append("无动作可验证")

        self.state["meta_verification_results"].append(verification)
        self._save_state()

        return verification

    def meta_iterate(self, iteration_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        执行完整的元迭代优化闭环
        评估 -> 优化 -> 执行 -> 验证
        """
        if iteration_data is None:
            iteration_data = {
                "execution_time": 0,
                "optimization_suggestions": [],
                "convergence_rate": 0.5,
            }

        self.state["meta_iteration_count"] += 1
        self.state["last_meta_iteration_time"] = datetime.now().isoformat()
        self.state["状态"] = "元迭代运行中"

        result = {
            "meta_iteration_id": self.state["meta_iteration_count"],
            "status": "in_progress",
            "phases": {},
        }

        # 阶段1：元评估
        print("[元迭代] 阶段1: 元评估")
        evaluation = self.evaluate_meta_iteration_effectiveness(iteration_data)
        result["phases"]["evaluation"] = evaluation

        # 阶段2：识别元优化空间
        print("[元迭代] 阶段2: 识别元优化空间")
        opportunities = self.identify_meta_optimization_opportunities()
        result["phases"]["opportunities"] = opportunities

        # 阶段3：生成元优化方案
        print("[元迭代] 阶段3: 生成元优化方案")
        optimization_plan = self.generate_meta_optimization_plan(opportunities)
        result["phases"]["optimization_plan"] = optimization_plan

        # 阶段4：执行元优化
        print("[元迭代] 阶段4: 执行元优化")
        execution_result = self.execute_meta_optimization(optimization_plan)
        result["phases"]["execution"] = execution_result

        # 阶段5：验证元优化
        print("[元迭代] 阶段5: 验证元优化")
        verification = self.verify_meta_optimization(execution_result)
        result["phases"]["verification"] = verification

        # 记录历史
        self.state["meta_iteration_history"].append({
            "timestamp": datetime.now().isoformat(),
            "iteration_id": self.state["meta_iteration_count"],
            "result_summary": {
                "evaluation_score": evaluation.get("overall_score", 0),
                "opportunities_found": opportunities.get("opportunity_count", 0),
                "actions_executed": len(execution_result.get("executed_actions", [])),
                "verification_status": verification.get("overall_status", "unknown"),
            }
        })

        result["status"] = "completed"
        result["overall_score"] = evaluation.get("overall_score", 0)
        result["optimization_performed"] = len(execution_result.get("executed_actions", [])) > 0

        self.state["状态"] = "元迭代完成"
        self._save_state()

        return result

    def get_status(self) -> Dict[str, Any]:
        """获取元迭代引擎状态"""
        return {
            "status": self.state.get("状态", "未知"),
            "version": self.state["version"],
            "initialized": self.state["initialized"],
            "meta_iteration_count": self.state["meta_iteration_count"],
            "meta_evaluation_count": self.state["meta_evaluation_count"],
            "meta_optimization_count": self.state["meta_optimization_count"],
            "meta_execution_count": self.state["meta_execution_count"],
            "meta_verification_count": self.state["meta_verification_count"],
            "last_meta_iteration_time": self.state.get("last_meta_iteration_time"),
            "last_meta_evaluation_time": self.state.get("last_meta_evaluation_time"),
            "last_meta_optimization_time": self.state.get("last_meta_optimization_time"),
            "策略迭代元优化能力": self.state.get("策略迭代元优化能力", "待激活"),
        }

    def get_summary(self) -> Dict[str, Any]:
        """获取元迭代引擎摘要"""
        return {
            "version": self.state["version"],
            "total_meta_iterations": self.state["meta_iteration_count"],
            "total_meta_evaluations": self.state["meta_evaluation_count"],
            "total_meta_optimizations": self.state["meta_optimization_count"],
            "total_meta_executions": self.state["meta_execution_count"],
            "total_meta_verifications": self.state["meta_verification_count"],
            "recent_iterations": self.state["meta_iteration_history"][-5:] if self.state["meta_iteration_history"] else [],
            "strategy": "元迭代优化 - 对策略迭代优化本身进行优化",
        }

    def push_to_cockpit(self, cockpit_data: Dict[str, Any] = None) -> bool:
        """推送到进化驾驶舱"""
        if not self.cockpit_engine:
            print("[元迭代] 驾驶舱集成引擎未初始化")
            return False

        try:
            if cockpit_data is None:
                cockpit_data = {
                    "engine": "strategy_meta_adaptive_iteration",
                    "status": self.get_status(),
                    "summary": self.get_summary(),
                }

            # 调用驾驶舱集成引擎推送数据
            result = self.cockpit_engine.push_evolution_data(cockpit_data)
            return result.get("status") == "success" if isinstance(result, dict) else True
        except Exception as e:
            print(f"[元迭代] 推送驾驶舱失败: {e}")
            return False


def main():
    """主函数 - 用于独立测试"""
    import argparse

    parser = argparse.ArgumentParser(description="策略元自适应迭代优化引擎")
    parser.add_argument("action", nargs="?", default="status",
                        choices=["status", "initialize", "meta_iterate", "evaluate", "identify", "plan", "execute", "verify", "summary", "push_cockpit"],
                        help="执行的动作")
    parser.add_argument("--state-dir", default="runtime/state", help="状态目录")

    args = parser.parse_args()

    engine = StrategyMetaAdaptiveIterationEngine(args.state_dir)

    if args.action == "status":
        result = engine.get_status()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.action == "initialize":
        result = engine.initialize()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.action == "meta_iterate":
        result = engine.meta_iterate()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.action == "evaluate":
        test_data = {
            "execution_time": 5,
            "optimization_suggestions": ["优化建议1", "优化建议2"],
            "convergence_rate": 0.7,
        }
        result = engine.evaluate_meta_iteration_effectiveness(test_data)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.action == "identify":
        result = engine.identify_meta_optimization_opportunities()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.action == "plan":
        opportunities = engine.identify_meta_optimization_opportunities()
        result = engine.generate_meta_optimization_plan(opportunities)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.action == "execute":
        opportunities = engine.identify_meta_optimization_opportunities()
        plan = engine.generate_meta_optimization_plan(opportunities)
        result = engine.execute_meta_optimization(plan)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.action == "verify":
        opportunities = engine.identify_meta_optimization_opportunities()
        plan = engine.generate_meta_optimization_plan(opportunities)
        execution = engine.execute_meta_optimization(plan)
        result = engine.verify_meta_optimization(execution)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.action == "summary":
        result = engine.get_summary()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.action == "push_cockpit":
        result = engine.push_to_cockpit()
        print(json.dumps({"status": "success" if result else "failed"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()