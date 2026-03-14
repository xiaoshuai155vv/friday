#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环价值-知识双闭环递归增强引擎 (version 1.0.0)

将 round 374 的价值闭环引擎与 round 373 的知识整合引擎深度集成，形成
「知识发现→价值评估→自动执行→效果验证→知识更新」的完整递归增强闭环。

核心功能：
1. 价值执行结果自动反馈到知识图谱
2. 基于实际价值实现动态调整知识权重
3. 知识驱动的价值机会优先级排序
4. 递归增强闭环（知识→价值→执行→验证→新知识）

集成模块：
- evolution_value_closed_loop_execution_engine.py (round 374)
- evolution_knowledge_deep_integration_engine.py (round 373)
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

# 尝试导入集成的模块
try:
    from evolution_value_closed_loop_execution_engine import ValueClosedLoopEngine
except ImportError:
    ValueClosedLoopEngine = None

try:
    from evolution_knowledge_deep_integration_engine import KnowledgeDeepIntegrationEngine
except ImportError:
    KnowledgeDeepIntegrationEngine = None


class ValueKnowledgeClosedLoopEngine:
    """价值-知识双闭环递归增强引擎"""

    def __init__(self, state_dir: str = "runtime/state"):
        self.state_dir = Path(state_dir)
        self.state_file = self.state_dir / "evolution_value_knowledge_state.json"

        # 集成两个引擎
        self.value_engine = None
        self.knowledge_engine = None

        # 递归增强闭环状态
        self.state = {
            "initialized": False,
            "recursive_cycles": 0,
            "knowledge_value_feedback_count": 0,
            "priority_adjustments": 0,
            "innovation_from_feedback": 0,
            "last_cycle_time": None,
            "knowledge_weights": {},  # 知识权重（基于价值实现调整）
            "priority_queue": [],  # 价值机会优先级队列
            "feedback_history": [],  # 反馈历史
        }

        self._initialize_engines()

    def _initialize_engines(self):
        """初始化集成的引擎"""
        if ValueClosedLoopEngine:
            try:
                self.value_engine = ValueClosedLoopEngine(self.state_dir)
                print("[ValueKnowledgeClosedLoop] 价值闭环引擎已加载")
            except Exception as e:
                print(f"[ValueKnowledgeClosedLoop] 价值闭环引擎加载失败: {e}")

        if KnowledgeDeepIntegrationEngine:
            try:
                self.knowledge_engine = KnowledgeDeepIntegrationEngine(self.state_dir)
                print("[ValueKnowledgeClosedLoop] 知识整合引擎已加载")
            except Exception as e:
                print(f"[ValueKnowledgeClosedLoop] 知识整合引擎加载失败: {e}")

        if self.value_engine and self.knowledge_engine:
            self.state["initialized"] = True

        self.load_state()

    def load_state(self) -> bool:
        """加载状态"""
        if self.state_file.exists():
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    saved_state = json.load(f)
                    self.state.update(saved_state)
                print(f"[ValueKnowledgeClosedLoop] 状态已加载: {len(self.state.get('feedback_history', []))} 条反馈记录")
                return True
            except Exception as e:
                print(f"[ValueKnowledgeClosedLoop] 状态加载失败: {e}")
        return False

    def save_state(self):
        """保存状态"""
        self.state_dir.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump(self.state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[ValueKnowledgeClosedLoop] 状态保存失败: {e}")

    def get_status(self) -> Dict[str, Any]:
        """获取引擎状态"""
        status = {
            "initialized": self.state["initialized"],
            "recursive_cycles": self.state["recursive_cycles"],
            "knowledge_value_feedback_count": self.state["knowledge_value_feedback_count"],
            "priority_adjustments": self.state["priority_adjustments"],
            "innovation_from_feedback": self.state["innovation_from_feedback"],
            "last_cycle_time": self.state["last_cycle_time"],
            "knowledge_weights_count": len(self.state.get("knowledge_weights", {})),
            "priority_queue_length": len(self.state.get("priority_queue", [])),
            "feedback_history_length": len(self.state.get("feedback_history", [])),
        }

        # 集成引擎状态
        if self.value_engine:
            try:
                status["value_engine"] = self.value_engine.get_status()
            except:
                status["value_engine"] = "unavailable"

        if self.knowledge_engine:
            try:
                status["knowledge_engine"] = self.knowledge_engine.get_status()
            except:
                status["knowledge_engine"] = "unavailable"

        return status

    def feedback_value_to_knowledge(self, execution_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        核心功能1：价值执行结果自动反馈到知识图谱

        将价值执行的结果（成功/失败/效率提升等）反馈到知识图谱，
        更新相关知识的权重和关联关系。
        """
        if not self.knowledge_engine:
            return {"success": False, "error": "知识整合引擎未加载"}

        feedback_result = {
            "timestamp": datetime.now().isoformat(),
            "execution_id": execution_result.get("execution_id", "unknown"),
            "value_achieved": execution_result.get("value_metrics", {}),
            "knowledge_updates": [],
        }

        try:
            # 提取执行结果中的关键信息
            value_metrics = execution_result.get("value_metrics", {})
            opportunity_id = execution_result.get("opportunity_id", "")
            execution_time = execution_result.get("execution_time", 0)
            success = execution_result.get("success", False)

            # 1. 更新知识权重（基于价值实现）
            if success and value_metrics.get("total_value", 0) > 0:
                # 高价值执行 -> 增加相关知识权重
                weight_increase = min(1.0, value_metrics.get("total_value", 0) / 100)
                self._adjust_knowledge_weight(opportunity_id, weight_increase)
                feedback_result["knowledge_updates"].append({
                    "type": "weight_increase",
                    "knowledge_id": opportunity_id,
                    "increase": weight_increase
                })

            # 2. 记录失败模式（用于下次规避）
            if not success:
                failure_reason = execution_result.get("error", "unknown")
                self._record_failure_pattern(opportunity_id, failure_reason)
                feedback_result["knowledge_updates"].append({
                    "type": "failure_recorded",
                    "knowledge_id": opportunity_id,
                    "reason": failure_reason
                })

            # 3. 记录执行效率（用于优化）
            efficiency_score = self._calculate_efficiency_score(execution_result)
            self._update_efficiency_knowledge(opportunity_id, efficiency_score)
            feedback_result["knowledge_updates"].append({
                "type": "efficiency_updated",
                "knowledge_id": opportunity_id,
                "efficiency": efficiency_score
            })

            # 更新反馈计数
            self.state["knowledge_value_feedback_count"] += 1
            self.state["last_cycle_time"] = datetime.now().isoformat()

            # 保存到历史
            self.state["feedback_history"].append(feedback_result)
            if len(self.state["feedback_history"]) > 100:  # 保留最近100条
                self.state["feedback_history"] = self.state["feedback_history"][-100:]

            self.save_state()

            feedback_result["success"] = True
            return feedback_result

        except Exception as e:
            feedback_result["success"] = False
            feedback_result["error"] = str(e)
            return feedback_result

    def _adjust_knowledge_weight(self, knowledge_id: str, weight_increase: float):
        """调整知识权重"""
        current_weight = self.state["knowledge_weights"].get(knowledge_id, 0.5)  # 默认0.5
        new_weight = min(1.0, current_weight + weight_increase)
        self.state["knowledge_weights"][knowledge_id] = new_weight

    def _record_failure_pattern(self, knowledge_id: str, failure_reason: str):
        """记录失败模式"""
        failure_key = f"failure_{knowledge_id}"
        if failure_key not in self.state:
            self.state[failure_key] = []
        self.state[failure_key].append({
            "reason": failure_reason,
            "timestamp": datetime.now().isoformat()
        })

    def _calculate_efficiency_score(self, execution_result: Dict[str, Any]) -> float:
        """计算效率分数"""
        execution_time = execution_result.get("execution_time", 1)
        steps_count = len(execution_result.get("steps_executed", []))
        if execution_time == 0 or steps_count == 0:
            return 0.5

        # 效率 = 步骤数 / 执行时间（归一化到 0-1）
        base_score = steps_count / max(execution_time, 1)
        return min(1.0, base_score / 10)  # 假设10 steps/sec 为满分

    def _update_efficiency_knowledge(self, knowledge_id: str, efficiency: float):
        """更新效率知识"""
        efficiency_key = f"efficiency_{knowledge_id}"
        self.state[efficiency_key] = efficiency

    def evaluate_knowledge_value(self, knowledge_id: str) -> Dict[str, Any]:
        """
        核心功能2：知识价值评估

        基于实际价值实现评估知识的价值，调整优先级和建议。
        """
        evaluation = {
            "knowledge_id": knowledge_id,
            "base_weight": 0.5,
            "value_multiplier": 1.0,
            "efficiency_factor": 0.5,
            "final_value_score": 0.5,
        }

        # 获取基础权重
        evaluation["base_weight"] = self.state["knowledge_weights"].get(knowledge_id, 0.5)

        # 计算价值乘数（基于历史反馈）
        feedback_count = sum(1 for f in self.state.get("feedback_history", [])
                            if f.get("execution_id") == knowledge_id)
        if feedback_count > 0:
            successful_feedbacks = sum(1 for f in self.state.get("feedback_history", [])
                                      if f.get("execution_id") == knowledge_id
                                      and f.get("value_achieved", {}).get("total_value", 0) > 0)
            evaluation["value_multiplier"] = 1.0 + (successful_feedbacks / feedback_count)

        # 计算效率因子
        efficiency_key = f"efficiency_{knowledge_id}"
        evaluation["efficiency_factor"] = self.state.get(efficiency_key, 0.5)

        # 计算最终价值分数
        evaluation["final_value_score"] = (
            evaluation["base_weight"] *
            evaluation["value_multiplier"] *
            evaluation["efficiency_factor"]
        )

        return evaluation

    def prioritize_opportunities(self, opportunities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        核心功能3：知识驱动的价值机会优先级排序

        基于知识权重和价值评估对机会进行优先级排序。
        """
        prioritized = []

        for opp in opportunities:
            opportunity_id = opp.get("id", "")

            # 获取知识价值评估
            value_eval = self.evaluate_knowledge_value(opportunity_id)

            # 获取失败历史（用于降权）
            failure_key = f"failure_{opportunity_id}"
            failure_count = len(self.state.get(failure_key, []))
            failure_penalty = min(0.5, failure_count * 0.1)  # 每次失败降权10%，最多50%

            # 计算最终优先级分数
            base_priority = opp.get("priority", 0.5)
            priority_score = (
                base_priority *
                value_eval["final_value_score"] *
                (1.0 - failure_penalty)
            )

            # 添加知识驱动的调整
            if opportunity_id in self.state["knowledge_weights"]:
                weight_boost = self.state["knowledge_weights"][opportunity_id] * 0.2
                priority_score += weight_boost

            prioritized.append({
                **opp,
                "priority_score": priority_score,
                "value_evaluation": value_eval,
                "failure_count": failure_count,
            })

        # 按优先级分数排序
        prioritized.sort(key=lambda x: x.get("priority_score", 0), reverse=True)

        self.state["priority_queue"] = [p["id"] for p in prioritized]
        self.state["priority_adjustments"] += 1
        self.save_state()

        return prioritized

    def run_recursive_enhancement_cycle(self) -> Dict[str, Any]:
        """
        核心功能4：递归增强闭环

        执行完整的「知识→价值→执行→验证→新知识」递归增强闭环。
        """
        if not self.value_engine or not self.knowledge_engine:
            return {
                "success": False,
                "error": "引擎未完全初始化",
                "value_engine_available": self.value_engine is not None,
                "knowledge_engine_available": self.knowledge_engine is not None
            }

        cycle_result = {
            "cycle_id": self.state["recursive_cycles"] + 1,
            "timestamp": datetime.now().isoformat(),
            "steps": [],
            "innovations_discovered": [],
            "value_achieved": {},
        }

        try:
            # 步骤1：知识驱动发现 - 从知识图谱获取创新机会
            knowledge_result = self.knowledge_engine.discover_innovation_opportunities()
            opportunities = knowledge_result.get("opportunities", [])
            cycle_result["steps"].append({
                "step": "knowledge_discovery",
                "opportunities_found": len(opportunities),
                "success": True
            })

            # 步骤2：知识驱动的优先级排序
            prioritized_opportunities = self.prioritize_opportunities(opportunities)
            cycle_result["steps"].append({
                "step": "knowledge_driven_prioritization",
                "opportunities_prioritized": len(prioritized_opportunities),
                "success": True
            })

            # 步骤3：选择最高优先级的机会执行
            if prioritized_opportunities:
                top_opportunity = prioritized_opportunities[0]

                # 价值评估
                evaluation = self.value_engine.evaluate_opportunity(top_opportunity)
                cycle_result["steps"].append({
                    "step": "value_evaluation",
                    "opportunity_id": top_opportunity.get("id"),
                    "evaluation": evaluation,
                    "success": True
                })

                # 生成执行计划
                if evaluation.get("recommended_action") == "execute":
                    plan = self.value_engine.generate_execution_plan(evaluation)
                    cycle_result["steps"].append({
                        "step": "plan_generation",
                        "success": True
                    })

                    # 执行计划
                    execution = self.value_engine.execute_plan(plan)
                    cycle_result["steps"].append({
                        "step": "execution",
                        "execution_id": execution.get("execution_id"),
                        "success": execution.get("success", False)
                    })

                    # 步骤4：效果验证
                    validation = self.value_engine.validate_results(execution)
                    cycle_result["steps"].append({
                        "step": "validation",
                        "value_metrics": validation.get("value_metrics", {}),
                        "success": True
                    })

                    # 步骤5：价值反馈到知识图谱（递归增强的关键）
                    feedback = self.feedback_value_to_knowledge({
                        "execution_id": execution.get("execution_id"),
                        "opportunity_id": top_opportunity.get("id"),
                        "value_metrics": validation.get("value_metrics", {}),
                        "success": validation.get("success", False),
                        "execution_time": execution.get("execution_time", 0),
                        "steps_executed": execution.get("steps_executed", []),
                    })
                    cycle_result["steps"].append({
                        "step": "knowledge_feedback",
                        "updates": feedback.get("knowledge_updates", []),
                        "success": feedback.get("success", False)
                    })

                    cycle_result["value_achieved"] = validation.get("value_metrics", {})

                    # 检查是否发现新创新
                    if feedback.get("knowledge_updates"):
                        self.state["innovation_from_feedback"] += 1

            # 更新递归循环计数
            self.state["recursive_cycles"] += 1
            self.state["last_cycle_time"] = datetime.now().isoformat()
            self.save_state()

            cycle_result["success"] = True
            return cycle_result

        except Exception as e:
            cycle_result["success"] = False
            cycle_result["error"] = str(e)
            return cycle_result

    def get_metrics(self) -> Dict[str, Any]:
        """获取性能指标"""
        return {
            "recursive_cycles": self.state["recursive_cycles"],
            "knowledge_value_feedback_count": self.state["knowledge_value_feedback_count"],
            "priority_adjustments": self.state["priority_adjustments"],
            "innovation_from_feedback": self.state["innovation_from_feedback"],
            "knowledge_weights": len(self.state.get("knowledge_weights", {})),
            "feedback_history": len(self.state.get("feedback_history", [])),
        }

    def get_knowledge_value_insights(self) -> Dict[str, Any]:
        """获取知识价值洞察"""
        return {
            "top_weighted_knowledge": sorted(
                self.state.get("knowledge_weights", {}).items(),
                key=lambda x: x[1],
                reverse=True
            )[:10],
            "recent_feedback": self.state.get("feedback_history", [])[-5:],
            "failure_patterns": {
                k: v for k, v in self.state.items()
                if k.startswith("failure_")
            }[:5],
        }


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(
        description="智能全场景进化环价值-知识双闭环递归增强引擎"
    )
    parser.add_argument("command", choices=["status", "metrics", "cycle", "insights"],
                       help="要执行的命令")
    parser.add_argument("--state-dir", default="runtime/state",
                       help="状态目录")

    args = parser.parse_args()

    engine = ValueKnowledgeClosedLoopEngine(args.state_dir)

    if args.command == "status":
        status = engine.get_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))
    elif args.command == "metrics":
        metrics = engine.get_metrics()
        print(json.dumps(metrics, ensure_ascii=False, indent=2))
    elif args.command == "cycle":
        result = engine.run_recursive_enhancement_cycle()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == "insights":
        insights = engine.get_knowledge_value_insights()
        print(json.dumps(insights, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()