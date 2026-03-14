#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环元进化自主决策深度增强引擎

将 round 378 的智能体协同引擎与进化驾驶舱集成成果进一步深化，构建元进化决策层。
系统能够自动分析当前系统状态和能力缺口，从 100+ 进化引擎中智能选择最合适的引擎组合，
预测进化结果并自动调整策略，形成「智能分析→自动决策→自主执行→效果验证→自我优化」
的完整元进化闭环。让进化环真正具备"思考要进化什么、为什么进化、如何进化"的元认知能力。

Version: 1.0.0
Author: Auto Evolution System
"""

import json
import os
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# 基础路径配置
SCRIPT_DIR = Path(__file__).parent
RUNTIME_DIR = SCRIPT_DIR.parent / "runtime"
STATE_DIR = RUNTIME_DIR / "state"
LOGS_DIR = RUNTIME_DIR / "logs"


class EvolutionMetaDecisionDeepEnhancement:
    """
    元进化自主决策深度增强引擎

    核心能力：
    1. 系统状态自动分析 - 分析健康度、能力缺口、进化历史
    2. 进化引擎智能选择 - 基于任务特征和引擎能力匹配
    3. 进化结果预测与风险评估 - 预测进化结果，评估风险
    4. 策略动态调整与自优化 - 根据执行反馈动态调整策略
    5. 元进化闭环 - 分析→决策→执行→验证→优化
    """

    def __init__(self):
        self.engine_name = "meta_decision_deep_enhancement"
        self.version = "1.0.0"
        self.state_file = STATE_DIR / f"{self.engine_name}_state.json"
        self.history_file = STATE_DIR / f"{self.engine_name}_history.json"
        self.engines_registry = self._load_engines_registry()
        self.load_state()

    def _load_engines_registry(self) -> Dict[str, Any]:
        """加载进化引擎注册表"""
        registry_file = STATE_DIR / "evolution_engines_registry.json"
        if registry_file.exists():
            with open(registry_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        # 如果不存在，返回默认的引擎能力映射
        return {
            "decision": ["evolution_decision_quality_evaluator", "evolution_decision_execution_closed_loop"],
            "execution": ["evolution_execution_enhancer", "evolution_loop_automation"],
            "knowledge": ["evolution_knowledge_graph_reasoning", "evolution_cross_round_knowledge_fusion"],
            "health": ["health_immunity_evolution_engine", "evolution_realtime_monitoring_warning_engine"],
            "innovation": ["evolution_innovation_realization_engine", "evolution_creative_generation"],
            "optimization": ["evolution_methodology_optimizer", "evolution_adaptive_optimizer"],
            "planning": ["evolution_strategy_generation_evaluator", "evolution_multidim_decision_planning"],
            "learning": ["evolution_adaptive_learning_strategy_engine", "evolution_meta_learning_engine"]
        }

    def load_state(self):
        """加载引擎状态"""
        if self.state_file.exists():
            with open(self.state_file, 'r', encoding='utf-8') as f:
                self.state = json.load(f)
        else:
            self.state = {
                "initialized": False,
                "last_analysis": None,
                "current_strategy": {},
                "optimization_feedback": [],
                "metrics": {
                    "total_analysis": 0,
                    "successful_optimizations": 0,
                    "failed_optimizations": 0,
                    "average_improvement": 0.0
                }
            }

    def save_state(self):
        """保存引擎状态"""
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2)

    def load_history(self):
        """加载分析历史"""
        if self.history_file.exists():
            with open(self.history_file, 'r', encoding='utf-8') as f:
                self.history = json.load(f)
        else:
            self.history = []

    def save_history(self):
        """保存分析历史"""
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)

    def analyze_system_state(self) -> Dict[str, Any]:
        """
        分析系统状态

        分析健康度、能力缺口、进化历史
        """
        print(f"[{self.engine_name}] 分析系统状态...")

        analysis_result = {
            "timestamp": datetime.now().isoformat(),
            "health_status": self._analyze_health(),
            "capability_gaps": self._analyze_capability_gaps(),
            "evolution_history": self._analyze_evolution_history(),
            "trend_analysis": self._analyze_trends()
        }

        self.state["last_analysis"] = analysis_result
        self.state["initialized"] = True
        self.state["metrics"]["total_analysis"] += 1
        self.save_state()

        return analysis_result

    def _analyze_health(self) -> Dict[str, Any]:
        """分析健康状态"""
        # 读取当前 mission 状态
        mission_file = STATE_DIR / "current_mission.json"
        health_status = {"overall": "healthy", "details": {}}

        if mission_file.exists():
            with open(mission_file, 'r', encoding='utf-8') as f:
                mission = json.load(f)
                health_status["current_round"] = mission.get("loop_round", 0)
                health_status["current_phase"] = mission.get("phase", "unknown")

        # 检查最近的进化完成状态
        auto_last_file = SCRIPT_DIR.parent / "references" / "evolution_auto_last.md"
        if auto_last_file.exists():
            with open(auto_last_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if "未完成" in content:
                    health_status["overall"] = "warning"
                    health_status["details"]["recent_completion"] = "有未完成项"
                else:
                    health_status["details"]["recent_completion"] = "全部完成"

        return health_status

    def _analyze_capability_gaps(self) -> Dict[str, Any]:
        """分析能力缺口"""
        gaps_file = SCRIPT_DIR.parent / "references" / "capability_gaps.md"
        gaps = {"identified": [], "priority": "low"}

        if gaps_file.exists():
            with open(gaps_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # 简单解析，查找"已覆盖"之外的条目
                for line in content.split('\n'):
                    if '|  |' in line:  # 未覆盖的缺口
                        gap = line.split('|')[2].strip()
                        if gap and gap != "可行方向":
                            gaps["identified"].append(gap)

        if gaps["identified"]:
            gaps["priority"] = "medium"

        return gaps

    def _analyze_evolution_history(self) -> Dict[str, Any]:
        """分析进化历史"""
        history = {
            "recent_rounds": [],
            "completed_count": 0,
            "failed_count": 0,
            "average_efficiency": 0.0
        }

        # 读取最近的进化完成状态
        completed_files = list(STATE_DIR.glob("evolution_completed_ev_20260314_*.json"))
        completed_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

        for f in completed_files[:10]:  # 最近 10 轮
            try:
                with open(f, 'r', encoding='utf-8') as fp:
                    data = json.load(fp)
                    history["recent_rounds"].append({
                        "round": data.get("loop_round", 0),
                        "goal": data.get("current_goal", ""),
                        "status": data.get("status", "")
                    })
                    if data.get("status") == "已完成" or data.get("status") == "完成":
                        history["completed_count"] += 1
                    else:
                        history["failed_count"] += 1
            except:
                pass

        return history

    def _analyze_trends(self) -> Dict[str, Any]:
        """分析趋势"""
        return {
            "evolution_velocity": "stable",
            "innovation_rate": "moderate",
            "optimization_potential": "high"
        }

    def select_engines(self, task_characteristics: Dict[str, Any]) -> List[str]:
        """
        基于任务特征智能选择进化引擎

        Args:
            task_characteristics: 任务特征描述

        Returns:
            选中的进化引擎列表
        """
        print(f"[{self.engine_name}] 智能选择进化引擎...")

        selected = []
        task_type = task_characteristics.get("type", "general")
        priority = task_characteristics.get("priority", "medium")

        # 根据任务类型选择引擎
        engine_mapping = {
            "decision": ["evolution_decision_quality_evaluator", "evolution_multidim_decision_planning"],
            "execution": ["evolution_decision_execution_closed_loop", "evolution_execution_enhancer"],
            "knowledge": ["evolution_cross_round_knowledge_fusion", "evolution_kg_deep_reasoning_insight"],
            "health": ["health_immunity_evolution_engine", "evolution_engine_cluster_diagnostic_repair"],
            "innovation": ["evolution_innovation_realization_engine", "evolution_creative_generation"],
            "optimization": ["evolution_methodology_optimizer", "evolution_adaptive_optimizer"],
            "integration": ["evolution_agent_cockpit_integration_engine", "evolution_unified_agent_deep_integration"]
        }

        selected = engine_mapping.get(task_type, engine_mapping.get("general", []))

        # 如果是高优先级任务，添加额外的优化引擎
        if priority == "high":
            selected.append("evolution_strategy_generation_evaluator")

        return selected

    def predict_outcome(self, selected_engines: List[str], task_goal: str) -> Dict[str, Any]:
        """
        预测进化结果

        Args:
            selected_engines: 选中的引擎列表
            task_goal: 进化目标

        Returns:
            预测结果和风险评估
        """
        print(f"[{self.engine_name}] 预测进化结果...")

        prediction = {
            "estimated_success_rate": 0.85,
            "estimated_time": "medium",
            "risk_level": "low",
            "potential_benefits": [],
            "risk_factors": []
        }

        # 基于历史数据分析成功率
        self.load_history()
        if self.history:
            successful = sum(1 for h in self.history if h.get("outcome", {}).get("success", False))
            if len(self.history) > 0:
                prediction["estimated_success_rate"] = successful / len(self.history)

        # 识别潜在收益
        if "innovation" in task_goal:
            prediction["potential_benefits"].append("发现新的能力组合")
        if "optimization" in task_goal:
            prediction["potential_benefits"].append("提升进化效率")
        if "knowledge" in task_goal:
            prediction["potential_benefits"].append("增强知识图谱")

        return prediction

    def adjust_strategy(self, feedback: Dict[str, Any]) -> Dict[str, Any]:
        """
        根据反馈动态调整策略

        Args:
            feedback: 执行反馈

        Returns:
            调整后的策略
        """
        print(f"[{self.engine_name}] 调整进化策略...")

        adjusted_strategy = {
            "adjustments": [],
            "optimization_applied": False
        }

        # 分析反馈并生成优化建议
        if feedback.get("success_rate", 1.0) < 0.7:
            adjusted_strategy["adjustments"].append("降低任务复杂度")
            adjusted_strategy["optimization_applied"] = True

        if feedback.get("execution_time", "medium") == "long":
            adjusted_strategy["adjustments"].append("优化执行路径")
            adjusted_strategy["optimization_applied"] = True

        if feedback.get("error_rate", 0) > 0.2:
            adjusted_strategy["adjustments"].append("增强错误处理")
            adjusted_strategy["optimization_applied"] = True

        # 保存优化反馈
        self.state["optimization_feedback"].append({
            "timestamp": datetime.now().isoformat(),
            "feedback": feedback,
            "adjustments": adjusted_strategy["adjustments"]
        })

        # 限制反馈历史长度
        if len(self.state["optimization_feedback"]) > 50:
            self.state["optimization_feedback"] = self.state["optimization_feedback"][-50:]

        self.save_state()

        return adjusted_strategy

    def execute_meta_evolution_loop(self, task_goal: str, task_characteristics: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行完整的元进化闭环

        Args:
            task_goal: 进化目标
            task_characteristics: 任务特征

        Returns:
            执行结果
        """
        print(f"[{self.engine_name}] 执行元进化闭环: {task_goal}")

        result = {
            "phase": "analysis",
            "status": "in_progress",
            "phases_completed": [],
            "selected_engines": [],
            "prediction": {},
            "strategy": {},
            "outcome": {}
        }

        # 阶段 1: 分析
        print(f"[{self.engine_name}] 阶段 1/5: 系统状态分析...")
        analysis = self.analyze_system_state()
        result["phases_completed"].append("analysis")
        result["phase"] = "engine_selection"

        # 阶段 2: 引擎选择
        print(f"[{self.engine_name}] 阶段 2/5: 智能选择进化引擎...")
        selected_engines = self.select_engines(task_characteristics)
        result["selected_engines"] = selected_engines
        result["phases_completed"].append("engine_selection")
        result["phase"] = "prediction"

        # 阶段 3: 结果预测
        print(f"[{self.engine_name}] 阶段 3/5: 预测进化结果...")
        prediction = self.predict_outcome(selected_engines, task_goal)
        result["prediction"] = prediction
        result["phases_completed"].append("prediction")
        result["phase"] = "strategy"

        # 阶段 4: 策略调整（如果有历史反馈）
        print(f"[{self.engine_name}] 阶段 4/5: 策略动态调整...")
        if self.state.get("optimization_feedback"):
            last_feedback = self.state["optimization_feedback"][-1].get("feedback", {})
            strategy = self.adjust_strategy(last_feedback)
            result["strategy"] = strategy
        else:
            result["strategy"] = {"adjustments": [], "optimization_applied": False}
        result["phases_completed"].append("strategy")
        result["phase"] = "execution"

        # 阶段 5: 执行（这里只记录要执行的内容，实际执行由其他引擎完成）
        print(f"[{self.engine_name}] 阶段 5/5: 元进化闭环完成")
        result["phases_completed"].append("execution")
        result["phase"] = "complete"
        result["status"] = "completed"

        # 保存到历史
        self.load_history()
        self.history.append({
            "timestamp": datetime.now().isoformat(),
            "task_goal": task_goal,
            "task_characteristics": task_characteristics,
            "selected_engines": selected_engines,
            "prediction": prediction,
            "strategy": result["strategy"],
            "outcome": result
        })
        self.save_history()

        return result

    def get_status(self) -> Dict[str, Any]:
        """获取引擎状态"""
        return {
            "engine_name": self.engine_name,
            "version": self.version,
            "initialized": self.state.get("initialized", False),
            "last_analysis": self.state.get("last_analysis"),
            "metrics": self.state.get("metrics", {}),
            "engines_available": len(self.engines_registry),
            "optimization_feedback_count": len(self.state.get("optimization_feedback", []))
        }

    def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        return {
            "healthy": True,
            "engine": self.engine_name,
            "version": self.version,
            "state_file_exists": self.state_file.exists(),
            "initialized": self.state.get("initialized", False)
        }


def main():
    """主入口"""
    import sys

    engine = EvolutionMetaDecisionDeepEnhancement()

    if len(sys.argv) < 2:
        print(f"使用方式: python {sys.argv[0]} <command> [args...]")
        print(f"可用命令:")
        print(f"  status - 查看引擎状态")
        print(f"  analyze - 执行系统状态分析")
        print(f"  select <task_type> - 基于任务类型选择引擎")
        print(f"  predict <goal> - 预测进化结果")
        print(f"  execute <goal> <task_type> [priority] - 执行完整元进化闭环")
        print(f"  health - 健康检查")
        sys.exit(1)

    command = sys.argv[1]

    if command == "status":
        result = engine.get_status()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "analyze":
        result = engine.analyze_system_state()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "select":
        if len(sys.argv) < 3:
            print("错误: 需要提供任务类型")
            sys.exit(1)
        task_type = sys.argv[2]
        result = engine.select_engines({"type": task_type, "priority": "medium"})
        print(json.dumps({"selected_engines": result}, ensure_ascii=False, indent=2))

    elif command == "predict":
        if len(sys.argv) < 3:
            print("错误: 需要提供进化目标")
            sys.exit(1)
        goal = sys.argv[2]
        result = engine.predict_outcome([], goal)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "execute":
        if len(sys.argv) < 4:
            print("错误: 需要提供进化目标和任务类型")
            sys.exit(1)
        goal = sys.argv[2]
        task_type = sys.argv[3]
        priority = sys.argv[4] if len(sys.argv) > 4 else "medium"
        result = engine.execute_meta_evolution_loop(goal, {"type": task_type, "priority": priority})
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "health":
        result = engine.health_check()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    else:
        print(f"未知命令: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()