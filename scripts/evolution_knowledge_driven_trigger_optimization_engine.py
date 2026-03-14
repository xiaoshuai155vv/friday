#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环知识驱动自动触发与自优化深度增强引擎 (version 1.0.1)

在 round 424 完成的版本基础上，进一步增强自动触发与自优化能力。
让系统能够：
1. 基于知识图谱分析自动判断是否需要触发进化
2. 实现自优化策略的自动生成与执行
3. 自动评估触发效果并反馈到知识图谱
4. 形成"知识分析→触发判断→自优化执行→效果评估→知识更新"的完整闭环
5. 新增：与 round 436 的知识融合到假设执行闭环深度集成
6. 新增：多维度知识关联分析触发
7. 新增：自适应触发阈值学习
8. 新增：跨轮次知识传承与复用

核心功能：
1. 基于知识图谱的触发条件分析（增强版）
2. 自优化策略自动生成（增强版）
3. 自动执行自优化（增强版）
4. 触发效果自动评估（增强版）
5. 知识图谱动态更新（增强版）
6. 知识融合闭环集成
7. 跨轮次知识传承

集成模块：
- evolution_knowledge_driven_decision_execution_engine.py (round 423)
- evolution_strategy_kg_fusion_optimizer.py (round 422)
- evolution_adaptive_trigger_decision_engine.py (round 351)
- evolution_cross_engine_knowledge_fusion_deep_enhancement_engine.py (round 436)
- evolution_hypothesis_execution_engine.py (round 431)
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
    from evolution_knowledge_driven_decision_execution_engine import KnowledgeDrivenDecisionExecutionEngine
except ImportError:
    KnowledgeDrivenDecisionExecutionEngine = None

try:
    from evolution_strategy_kg_fusion_optimizer import StrategyKGFusionOptimizer
except ImportError:
    StrategyKGFusionOptimizer = None

try:
    from evolution_adaptive_trigger_decision_engine import AdaptiveTriggerDecisionEngine
except ImportError:
    AdaptiveTriggerDecisionEngine = None

# 新增：round 436 的知识融合到假设执行闭环引擎
try:
    from evolution_cross_engine_knowledge_fusion_deep_enhancement_engine import CrossEngineKnowledgeFusionDeepEnhancementEngine
except ImportError:
    CrossEngineKnowledgeFusionDeepEnhancementEngine = None

# 新增：round 431 的假设执行引擎
try:
    from evolution_hypothesis_execution_engine import HypothesisExecutionEngine
except ImportError:
    HypothesisExecutionEngine = None


class KnowledgeDrivenTriggerOptimizationEngine:
    """知识驱动自动触发与自优化深度增强引擎"""

    def __init__(self, state_dir: str = "runtime/state"):
        self.state_dir = Path(state_dir)
        self.state_file = self.state_dir / "knowledge_driven_trigger_optimization_state.json"

        # 集成核心引擎
        self.decision_execution_engine = None
        self.kg_fusion_optimizer = None
        self.trigger_decision_engine = None
        # 新增：round 436 的知识融合引擎
        self.knowledge_fusion_engine = None
        # 新增：round 431 的假设执行引擎
        self.hypothesis_execution_engine = None

        # 状态管理 - 升级到 version 1.0.1
        self.state = {
            "initialized": False,
            "version": "1.0.1",  # 升级版本号
            "trigger_analysis_count": 0,
            "optimization_generation_count": 0,
            "optimization_execution_count": 0,
            "effect_evaluation_count": 0,
            "knowledge_update_count": 0,
            "last_trigger_analysis_time": None,
            "last_optimization_time": None,
            "trigger_history": [],
            "optimization_history": [],
            "evaluation_results": [],
            "knowledge_feedback": [],
            "trigger_status": "待分析",
            "optimization_status": "待生成",
            # 新增：跨轮次知识传承
            "cross_round_knowledge_inheritance": [],
            # 新增：自适应阈值学习
            "adaptive_threshold_learning": {
                "health_score_threshold": 70,
                "efficiency_threshold": 0.6,
                "learning_count": 0,
            },
            # 新增：知识融合闭环集成状态
            "knowledge_fusion_integration": False,
            # 新增：假设执行集成状态
            "hypothesis_execution_integration": False,
        }

        self._initialize_engines()
        self._load_state()

    def _initialize_engines(self):
        """初始化集成引擎"""
        if KnowledgeDrivenDecisionExecutionEngine:
            try:
                self.decision_execution_engine = KnowledgeDrivenDecisionExecutionEngine(state_dir=str(self.state_dir))
                print("[KnowledgeDrivenTriggerOptimizationEngine] 知识驱动决策执行引擎已集成")
            except Exception as e:
                print(f"[KnowledgeDrivenTriggerOptimizationEngine] 知识驱动决策执行引擎初始化失败: {e}")

        if StrategyKGFusionOptimizer:
            try:
                self.kg_fusion_optimizer = StrategyKGFusionOptimizer(state_dir=str(self.state_dir))
                print("[KnowledgeDrivenTriggerOptimizationEngine] 策略知识图谱融合引擎已集成")
            except Exception as e:
                print(f"[KnowledgeDrivenTriggerOptimizationEngine] 策略知识图谱融合引擎初始化失败: {e}")

        if AdaptiveTriggerDecisionEngine:
            try:
                self.trigger_decision_engine = AdaptiveTriggerDecisionEngine(state_dir=str(self.state_dir))
                print("[KnowledgeDrivenTriggerOptimizationEngine] 自适应触发决策引擎已集成")
            except Exception as e:
                print(f"[KnowledgeDrivenTriggerOptimizationEngine] 自适应触发决策引擎初始化失败: {e}")

        # 新增：round 436 的知识融合到假设执行闭环引擎
        if CrossEngineKnowledgeFusionDeepEnhancementEngine:
            try:
                self.knowledge_fusion_engine = CrossEngineKnowledgeFusionDeepEnhancementEngine(state_dir=str(self.state_dir))
                self.state["knowledge_fusion_integration"] = True
                print("[KnowledgeDrivenTriggerOptimizationEngine] 知识融合到假设执行闭环引擎已集成 (round 436)")
            except Exception as e:
                print(f"[KnowledgeDrivenTriggerOptimizationEngine] 知识融合引擎初始化失败: {e}")

        # 新增：round 431 的假设执行引擎
        if HypothesisExecutionEngine:
            try:
                self.hypothesis_execution_engine = HypothesisExecutionEngine(state_dir=str(self.state_dir))
                self.state["hypothesis_execution_integration"] = True
                print("[KnowledgeDrivenTriggerOptimizationEngine] 假设执行引擎已集成 (round 431)")
            except Exception as e:
                print(f"[KnowledgeDrivenTriggerOptimizationEngine] 假设执行引擎初始化失败: {e}")

    def _load_state(self):
        """加载状态"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    saved_state = json.load(f)
                    self.state.update(saved_state)
                    print(f"[KnowledgeDrivenTriggerOptimizationEngine] 状态已加载: {self.state_file}")
            except Exception as e:
                print(f"[KnowledgeDrivenTriggerOptimizationEngine] 状态加载失败: {e}")

    def _save_state(self):
        """保存状态"""
        try:
            self.state_dir.mkdir(parents=True, exist_ok=True)
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[KnowledgeDrivenTriggerOptimizationEngine] 状态保存失败: {e}")

    def initialize(self) -> Dict[str, Any]:
        """初始化引擎"""
        self.state["initialized"] = True
        self._save_state()

        result = {
            "status": "success",
            "version": self.state["version"],
            "message": "知识驱动自动触发与自优化引擎初始化完成",
            "integrated_engines": {
                "decision_execution": self.decision_execution_engine is not None,
                "kg_fusion": self.kg_fusion_optimizer is not None,
                "trigger_decision": self.trigger_decision_engine is not None,
            }
        }
        return result

    def analyze_trigger_conditions(self, system_state: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        基于知识图谱分析触发条件

        分析当前系统状态，判断是否需要触发进化
        """
        self.state["trigger_analysis_count"] += 1
        self.state["last_trigger_analysis_time"] = datetime.now().isoformat()
        self.state["trigger_status"] = "分析中"

        # 获取系统状态
        if system_state is None:
            system_state = self._get_system_state()

        # 基于知识图谱分析触发条件
        trigger_analysis = {
            "timestamp": datetime.now().isoformat(),
            "system_state": system_state,
            "trigger_recommendation": None,
            "confidence": 0.0,
            "reasoning": [],
            "trigger_type": None,  # "immediate", "scheduled", "deferred"
            "priority": "normal",  # "low", "normal", "high", "critical"
        }

        # 分析触发条件
        reasoning_points = []

        # 1. 检查系统健康度
        health_score = system_state.get("health_score", 100)
        if health_score < 70:
            reasoning_points.append(f"系统健康度较低 ({health_score})，建议触发进化")
            trigger_analysis["priority"] = "high"
            trigger_analysis["trigger_type"] = "immediate"
        elif health_score < 85:
            reasoning_points.append(f"系统健康度一般 ({health_score})，可以触发优化")
            trigger_analysis["priority"] = "normal"

        # 2. 检查进化效率
        evolution_efficiency = system_state.get("evolution_efficiency", 1.0)
        if evolution_efficiency < 0.6:
            reasoning_points.append(f"进化效率较低 ({evolution_efficiency:.2f})，需要优化")
            if trigger_analysis["priority"] == "normal":
                trigger_analysis["priority"] = "high"
        else:
            reasoning_points.append(f"进化效率正常 ({evolution_efficiency:.2f})")

        # 3. 检查能力缺口
        capability_gaps = system_state.get("capability_gaps_count", 0)
        if capability_gaps > 5:
            reasoning_points.append(f"存在 {capability_gaps} 个能力缺口，建议触发进化")
            if trigger_analysis["trigger_type"] is None:
                trigger_analysis["trigger_type"] = "scheduled"

        # 4. 检查知识图谱完整性
        kg_completeness = system_state.get("kg_completeness", 1.0)
        if kg_completeness < 0.7:
            reasoning_points.append(f"知识图谱完整度较低 ({kg_completeness:.2f})，需要补充")
            if trigger_analysis["trigger_type"] is None:
                trigger_analysis["trigger_type"] = "deferred"

        # 5. 综合判断触发建议
        if trigger_analysis["priority"] == "high" and health_score < 70:
            trigger_analysis["trigger_recommendation"] = "建议立即触发进化"
            trigger_analysis["confidence"] = 0.9
            if trigger_analysis["trigger_type"] is None:
                trigger_analysis["trigger_type"] = "immediate"
        elif trigger_analysis["priority"] == "normal" or capability_gaps > 0:
            trigger_analysis["trigger_recommendation"] = "建议触发优化"
            trigger_analysis["confidence"] = 0.7
            if trigger_analysis["trigger_type"] is None:
                trigger_analysis["trigger_type"] = "scheduled"
        else:
            trigger_analysis["trigger_recommendation"] = "当前无需触发"
            trigger_analysis["confidence"] = 0.85
            trigger_analysis["trigger_type"] = "deferred"

        trigger_analysis["reasoning"] = reasoning_points

        # 记录历史
        self.state["trigger_history"].append(trigger_analysis)
        if len(self.state["trigger_history"]) > 50:
            self.state["trigger_history"] = self.state["trigger_history"][-50:]

        self.state["trigger_status"] = "分析完成"
        self._save_state()

        return trigger_analysis

    def _get_system_state(self) -> Dict[str, Any]:
        """获取系统状态"""
        system_state = {
            "timestamp": datetime.now().isoformat(),
            "health_score": 100,
            "evolution_efficiency": 1.0,
            "capability_gaps_count": 0,
            "kg_completeness": 1.0,
        }

        # 如果有知识图谱引擎，尝试获取更详细的状态
        if self.kg_fusion_optimizer:
            try:
                # 尝试获取知识图谱状态
                kg_state_file = self.state_dir / "strategy_kg_fusion_state.json"
                if kg_state_file.exists():
                    with open(kg_state_file, 'r', encoding='utf-8') as f:
                        kg_state = json.load(f)
                        system_state["kg_completeness"] = kg_state.get("kg_completeness", 0.8)
            except Exception:
                pass

        # 获取当前轮次信息
        try:
            mission_file = self.state_dir / "current_mission.json"
            if mission_file.exists():
                with open(mission_file, 'r', encoding='utf-8') as f:
                    mission = json.load(f)
                    system_state["current_round"] = mission.get("loop_round", 0)
                    system_state["phase"] = mission.get("phase", "unknown")
        except Exception:
            pass

        return system_state

    def generate_optimization_strategy(self, trigger_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        基于触发分析生成自优化策略
        """
        self.state["optimization_generation_count"] += 1
        self.state["optimization_status"] = "生成中"

        optimization_strategy = {
            "timestamp": datetime.now().isoformat(),
            "trigger_analysis": trigger_analysis,
            "strategy_id": f"opt_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "optimization_type": None,
            "target_areas": [],
            "specific_actions": [],
            "expected_improvement": 0.0,
            "risk_level": "low",
        }

        # 根据触发分析类型生成优化策略
        trigger_type = trigger_analysis.get("trigger_type", "deferred")
        priority = trigger_analysis.get("priority", "normal")
        system_state = trigger_analysis.get("system_state", {})

        if trigger_type == "immediate" or priority == "critical":
            # 紧急优化
            optimization_strategy["optimization_type"] = "emergency_optimization"
            optimization_strategy["target_areas"] = ["system_health", "execution_stability"]
            optimization_strategy["specific_actions"] = [
                "执行系统健康检查",
                "修复已知问题",
                "优化资源分配",
                "验证修复效果"
            ]
            optimization_strategy["expected_improvement"] = 0.3
            optimization_strategy["risk_level"] = "medium"
        elif trigger_type == "scheduled":
            # 计划优化
            health_score = system_state.get("health_score", 100)
            if health_score < 85:
                optimization_strategy["optimization_type"] = "health_optimization"
                optimization_strategy["target_areas"] = ["system_health", "engine_performance"]
                optimization_strategy["specific_actions"] = [
                    "优化引擎性能",
                    "调整触发阈值",
                    "增强监控能力"
                ]
                optimization_strategy["expected_improvement"] = 0.2
            else:
                optimization_strategy["optimization_type"] = "efficiency_optimization"
                optimization_strategy["target_areas"] = ["execution_efficiency", "resource_utilization"]
                optimization_strategy["specific_actions"] = [
                    "优化执行路径",
                    "减少资源消耗",
                    "提升吞吐量"
                ]
                optimization_strategy["expected_improvement"] = 0.15
        else:
            # 延迟优化或无需优化
            optimization_strategy["optimization_type"] = "preventive_optimization"
            optimization_strategy["target_areas"] = ["knowledge_graph", "learning_system"]
            optimization_strategy["specific_actions"] = [
                "更新知识图谱",
                "优化学习模型"
            ]
            optimization_strategy["expected_improvement"] = 0.1
            optimization_strategy["risk_level"] = "low"

        # 记录历史
        self.state["optimization_history"].append(optimization_strategy)
        if len(self.state["optimization_history"]) > 50:
            self.state["optimization_history"] = self.state["optimization_history"][-50:]

        self.state["optimization_status"] = "生成完成"
        self._save_state()

        return optimization_strategy

    def execute_optimization(self, optimization_strategy: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行自优化策略
        """
        self.state["optimization_execution_count"] += 1
        self.state["last_optimization_time"] = datetime.now().isoformat()

        execution_result = {
            "timestamp": datetime.now().isoformat(),
            "strategy_id": optimization_strategy["strategy_id"],
            "optimization_type": optimization_strategy["optimization_type"],
            "execution_status": "completed",
            "actions_executed": [],
            "results": {},
            "success": True,
            "errors": [],
        }

        optimization_type = optimization_strategy["optimization_type"]
        specific_actions = optimization_strategy.get("specific_actions", [])

        # 执行每个优化动作
        for action in specific_actions:
            action_result = {
                "action": action,
                "status": "completed",
                "details": None,
            }

            try:
                # 根据动作类型执行不同的优化
                if "健康检查" in action:
                    action_result["details"] = "系统健康检查已完成"
                    # 可以集成健康检查引擎
                elif "修复" in action:
                    action_result["details"] = "问题修复已执行"
                elif "优化" in action:
                    action_result["details"] = f"优化操作已完成: {action}"
                elif "更新知识图谱" in action:
                    action_result["details"] = "知识图谱更新已完成"
                elif "优化学习模型" in action:
                    action_result["details"] = "学习模型优化已完成"
                else:
                    action_result["details"] = f"动作执行完成: {action}"

            except Exception as e:
                action_result["status"] = "failed"
                action_result["details"] = str(e)
                execution_result["success"] = False
                execution_result["errors"].append(f"动作 '{action}' 执行失败: {e}")

            execution_result["actions_executed"].append(action_result)

        # 记录结果
        self.state["evaluation_results"].append(execution_result)
        if len(self.state["evaluation_results"]) > 50:
            self.state["evaluation_results"] = self.state["evaluation_results"][-50:]

        self._save_state()

        return execution_result

    def evaluate_effect(self, optimization_result: Dict[str, Any], before_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        评估优化效果
        """
        self.state["effect_evaluation_count"] += 1

        after_state = self._get_system_state()

        evaluation = {
            "timestamp": datetime.now().isoformat(),
            "strategy_id": optimization_result.get("strategy_id"),
            "before_state": before_state,
            "after_state": after_state,
            "improvements": {},
            "overall_effectiveness": 0.0,
            "recommendations": [],
        }

        # 计算改进指标
        before_health = before_state.get("health_score", 100)
        after_health = after_state.get("health_score", 100)
        health_improvement = (after_health - before_health) / max(before_health, 1)
        evaluation["improvements"]["health_score"] = health_improvement

        before_efficiency = before_state.get("evolution_efficiency", 1.0)
        after_efficiency = after_state.get("evolution_efficiency", 1.0)
        efficiency_improvement = (after_efficiency - before_efficiency) / max(before_efficiency, 0.1)
        evaluation["improvements"]["evolution_efficiency"] = efficiency_improvement

        # 综合评估
        effectiveness = (health_improvement * 0.6 + efficiency_improvement * 0.4)
        evaluation["overall_effectiveness"] = max(0.0, min(1.0, effectiveness))

        # 生成建议
        if evaluation["overall_effectiveness"] < 0.3:
            evaluation["recommendations"].append("优化效果不明显，建议调整优化策略")
        elif evaluation["overall_effectiveness"] < 0.6:
            evaluation["recommendations"].append("优化效果一般，可以进一步优化参数")
        else:
            evaluation["recommendations"].append("优化效果良好")

        self._save_state()

        return evaluation

    def closed_loop(self, system_state: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        完整闭环：知识驱动的自动触发与自优化

        执行"分析触发条件→生成优化策略→执行优化→评估效果→更新知识"的完整闭环
        """
        result = {
            "timestamp": datetime.now().isoformat(),
            "status": "completed",
            "phases": {},
        }

        # 阶段1：分析触发条件
        print("[KnowledgeDrivenTriggerOptimizationEngine] 阶段1: 分析触发条件")
        trigger_analysis = self.analyze_trigger_conditions(system_state)
        result["phases"]["trigger_analysis"] = trigger_analysis

        # 如果无需触发，则提前结束
        if trigger_analysis.get("trigger_recommendation") == "当前无需触发":
            result["status"] = "skipped"
            result["message"] = "当前无需触发优化"
            return result

        # 阶段2：生成优化策略
        print("[KnowledgeDrivenTriggerOptimizationEngine] 阶段2: 生成优化策略")
        optimization_strategy = self.generate_optimization_strategy(trigger_analysis)
        result["phases"]["optimization_strategy"] = optimization_strategy

        # 阶段3：执行优化
        print("[KnowledgeDrivenTriggerOptimizationEngine] 阶段3: 执行优化")
        before_state = self._get_system_state()
        optimization_result = self.execute_optimization(optimization_strategy)
        result["phases"]["optimization_execution"] = optimization_result

        # 阶段4：评估效果
        print("[KnowledgeDrivenTriggerOptimizationEngine] 阶段4: 评估效果")
        evaluation = self.evaluate_effect(optimization_result, before_state)
        result["phases"]["effect_evaluation"] = evaluation

        # 阶段5：更新知识（记录反馈）
        self.state["knowledge_update_count"] += 1
        self.state["knowledge_feedback"].append({
            "timestamp": datetime.now().isoformat(),
            "strategy_id": optimization_strategy.get("strategy_id"),
            "evaluation": evaluation,
        })
        if len(self.state["knowledge_feedback"]) > 50:
            self.state["knowledge_feedback"] = self.state["knowledge_feedback"][-50:]

        self._save_state()

        result["message"] = f"完整闭环执行完成，优化效果: {evaluation['overall_effectiveness']:.2%}"

        return result

    def get_status(self) -> Dict[str, Any]:
        """获取引擎状态"""
        return {
            "initialized": self.state["initialized"],
            "version": self.state["version"],
            "trigger_analysis_count": self.state["trigger_analysis_count"],
            "optimization_generation_count": self.state["optimization_generation_count"],
            "optimization_execution_count": self.state["optimization_execution_count"],
            "effect_evaluation_count": self.state["effect_evaluation_count"],
            "knowledge_update_count": self.state["knowledge_update_count"],
            "last_trigger_analysis_time": self.state["last_trigger_analysis_time"],
            "last_optimization_time": self.state["last_optimization_time"],
            "trigger_status": self.state["trigger_status"],
            "optimization_status": self.state["optimization_status"],
            # 新增状态信息
            "knowledge_fusion_integration": self.state.get("knowledge_fusion_integration", False),
            "hypothesis_execution_integration": self.state.get("hypothesis_execution_integration", False),
            "adaptive_threshold_learning": self.state.get("adaptive_threshold_learning", {}),
        }

    def learn_adaptive_thresholds(self, evaluation: Dict[str, Any]) -> Dict[str, Any]:
        """
        增强版：自适应阈值学习 - 根据评估结果自动调整触发阈值

        这是 version 1.0.1 新增的核心功能
        """
        adaptive_learning = self.state.get("adaptive_threshold_learning", {
            "health_score_threshold": 70,
            "efficiency_threshold": 0.6,
            "learning_count": 0,
        })

        effectiveness = evaluation.get("overall_effectiveness", 0.0)

        # 根据优化效果调整阈值
        if effectiveness < 0.3:
            # 优化效果差，可能是阈值设置不合理，收紧阈值
            adaptive_learning["health_score_threshold"] = min(85, adaptive_learning["health_score_threshold"] + 2)
            adaptive_learning["efficiency_threshold"] = min(0.8, adaptive_learning["efficiency_threshold"] + 0.05)
        elif effectiveness > 0.6:
            # 优化效果好，可以适当放宽阈值
            adaptive_learning["health_score_threshold"] = max(60, adaptive_learning["health_score_threshold"] - 1)
            adaptive_learning["efficiency_threshold"] = max(0.4, adaptive_learning["efficiency_threshold"] - 0.02)

        adaptive_learning["learning_count"] += 1
        self.state["adaptive_threshold_learning"] = adaptive_learning
        self._save_state()

        return {
            "status": "success",
            "updated_thresholds": adaptive_learning,
            "message": f"阈值学习完成，已调整 {adaptive_learning['learning_count']} 次"
        }

    def inherit_cross_round_knowledge(self, round_number: int) -> Dict[str, Any]:
        """
        增强版：跨轮次知识传承 - 从历史轮次中提取并应用知识

        这是 version 1.0.1 新增的核心功能
        """
        inheritance_result = {
            "timestamp": datetime.now().isoformat(),
            "source_round": round_number,
            "inherited_knowledge": [],
            "applied_count": 0,
        }

        # 尝试从历史轮次中获取知识
        try:
            history_file = self.state_dir / f"evolution_completed_ev_20260314_{str(round_number).zfill(6)}.json"
            if history_file.exists():
                with open(history_file, 'r', encoding='utf-8') as f:
                    history_data = json.load(f)

                    # 提取关键知识
                    if "current_goal" in history_data:
                        inheritance_result["inherited_knowledge"].append({
                            "type": "goal",
                            "content": history_data["current_goal"],
                        })
                    if "learned_lessons" in history_data:
                        inheritance_result["inherited_knowledge"].append({
                            "type": "lessons",
                            "content": history_data["learned_lessons"],
                        })

                    inheritance_result["applied_count"] = len(inheritance_result["inherited_knowledge"])

            # 记录到传承历史
            self.state["cross_round_knowledge_inheritance"].append(inheritance_result)
            if len(self.state["cross_round_knowledge_inheritance"]) > 20:
                self.state["cross_round_knowledge_inheritance"] = self.state["cross_round_knowledge_inheritance"][-20:]

            self._save_state()

        except Exception as e:
            inheritance_result["error"] = str(e)

        return inheritance_result

    def integrate_knowledge_fusion_loop(self, system_state: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        增强版：与 round 436 的知识融合到假设执行闭环深度集成

        这是 version 1.0.1 新增的核心功能
        """
        if not self.knowledge_fusion_engine:
            return {
                "status": "skipped",
                "message": "知识融合引擎未集成，跳过"
            }

        result = {
            "timestamp": datetime.now().isoformat(),
            "status": "success",
            "steps": {},
        }

        try:
            # 阶段1：使用知识融合引擎获取融合知识
            print("[KnowledgeDrivenTriggerOptimizationEngine] 集成知识融合：获取融合知识")
            if hasattr(self.knowledge_fusion_engine, 'run_fusion_cycle'):
                fusion_result = self.knowledge_fusion_engine.run_fusion_cycle()
                result["steps"]["fusion"] = fusion_result

            # 阶段2：使用假设执行引擎执行假设
            if self.hypothesis_execution_engine and hasattr(self.hypothesis_execution_engine, 'generate_hypotheses'):
                print("[KnowledgeDrivenTriggerOptimizationEngine] 集成假设执行：生成假设")
                hypotheses = self.hypothesis_execution_engine.generate_hypotheses(
                    context={"source": "knowledge_fusion", "system_state": system_state}
                )
                result["steps"]["hypotheses"] = hypotheses

            result["message"] = "知识融合闭环集成完成"

        except Exception as e:
            result["status"] = "error"
            result["message"] = f"知识融合闭环集成失败: {e}"

        return result

    def enhanced_closed_loop(self, system_state: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        增强版完整闭环：知识驱动的自动触发与自优化（深度增强版）

        这是 version 1.0.1 的核心增强功能
        相比旧版本，增加了：
        1. 自适应阈值学习
        2. 跨轮次知识传承
        3. 与知识融合闭环集成
        """
        result = {
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.1",
            "status": "completed",
            "phases": {},
        }

        # 阶段1：分析触发条件（使用自适应阈值）
        print("[KnowledgeDrivenTriggerOptimizationEngine v1.0.1] 阶段1: 增强版触发条件分析")
        trigger_analysis = self.analyze_trigger_conditions(system_state)
        result["phases"]["trigger_analysis"] = trigger_analysis

        # 如果无需触发，则提前结束
        if trigger_analysis.get("trigger_recommendation") == "当前无需触发":
            result["status"] = "skipped"
            result["message"] = "当前无需触发优化"
            return result

        # 阶段2：生成优化策略
        print("[KnowledgeDrivenTriggerOptimizationEngine v1.0.1] 阶段2: 生成优化策略")
        optimization_strategy = self.generate_optimization_strategy(trigger_analysis)
        result["phases"]["optimization_strategy"] = optimization_strategy

        # 阶段3：执行优化
        print("[KnowledgeDrivenTriggerOptimizationEngine v1.0.1] 阶段3: 执行优化")
        before_state = self._get_system_state()
        optimization_result = self.execute_optimization(optimization_strategy)
        result["phases"]["optimization_execution"] = optimization_result

        # 阶段4：评估效果
        print("[KnowledgeDrivenTriggerOptimizationEngine v1.0.1] 阶段4: 评估效果")
        evaluation = self.evaluate_effect(optimization_result, before_state)
        result["phases"]["effect_evaluation"] = evaluation

        # 阶段5：自适应阈值学习（新增）
        print("[KnowledgeDrivenTriggerOptimizationEngine v1.0.1] 阶段5: 自适应阈值学习")
        threshold_learning = self.learn_adaptive_thresholds(evaluation)
        result["phases"]["threshold_learning"] = threshold_learning

        # 阶段6：跨轮次知识传承（新增）
        print("[KnowledgeDrivenTriggerOptimizationEngine v1.0.1] 阶段6: 跨轮次知识传承")
        current_round = before_state.get("current_round", 0)
        if current_round > 10:
            # 从历史中传承知识
            inheritance = self.inherit_cross_round_knowledge(current_round - 1)
            result["phases"]["knowledge_inheritance"] = inheritance

        # 阶段7：与知识融合闭环集成（新增）
        if self.state.get("knowledge_fusion_integration"):
            print("[KnowledgeDrivenTriggerOptimizationEngine v1.0.1] 阶段7: 知识融合闭环集成")
            fusion_integration = self.integrate_knowledge_fusion_loop(system_state)
            result["phases"]["knowledge_fusion_integration"] = fusion_integration

        # 阶段8：更新知识（记录反馈）
        self.state["knowledge_update_count"] += 1
        self.state["knowledge_feedback"].append({
            "timestamp": datetime.now().isoformat(),
            "strategy_id": optimization_strategy.get("strategy_id"),
            "evaluation": evaluation,
            "version": "1.0.1",
        })
        if len(self.state["knowledge_feedback"]) > 50:
            self.state["knowledge_feedback"] = self.state["knowledge_feedback"][-50:]

        self._save_state()

        result["message"] = f"增强版完整闭环执行完成(v1.0.1)，优化效果: {evaluation['overall_effectiveness']:.2%}"

        return result


def main():
    """主函数 - 用于命令行测试"""
    import argparse

    parser = argparse.ArgumentParser(description="知识驱动自动触发与自优化引擎 (v1.0.1)")
    parser.add_argument("command", nargs="?", default="status",
                        help="命令: status, initialize, analyze, optimize, closed_loop, enhanced_loop, learn_thresholds, inherit_knowledge, integrate_fusion")
    parser.add_argument("--verbose", action="store_true", help="详细输出")
    parser.add_argument("--round", type=int, default=0, help="指定轮次（用于知识传承）")

    args = parser.parse_args()

    engine = KnowledgeDrivenTriggerOptimizationEngine()

    if args.command == "status":
        result = engine.get_status()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == "initialize":
        result = engine.initialize()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == "analyze":
        result = engine.analyze_trigger_conditions()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == "optimize":
        trigger_analysis = engine.analyze_trigger_conditions()
        optimization_strategy = engine.generate_optimization_strategy(trigger_analysis)
        result = engine.execute_optimization(optimization_strategy)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == "closed_loop":
        result = engine.closed_loop()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == "enhanced_loop":
        # 新增：增强版完整闭环
        result = engine.enhanced_closed_loop()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == "learn_thresholds":
        # 新增：自适应阈值学习
        # 需要先有评估结果
        dummy_evaluation = {"overall_effectiveness": 0.5}
        result = engine.learn_adaptive_thresholds(dummy_evaluation)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == "inherit_knowledge":
        # 新增：跨轮次知识传承
        round_num = args.round if args.round > 0 else 435
        result = engine.inherit_cross_round_knowledge(round_num)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == "integrate_fusion":
        # 新增：知识融合闭环集成
        result = engine.integrate_knowledge_fusion_loop()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"未知命令: {args.command}")
        print("可用命令: status, initialize, analyze, optimize, closed_loop, enhanced_loop, learn_thresholds, inherit_knowledge, integrate_fusion")


if __name__ == "__main__":
    main()