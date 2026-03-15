#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环元进化智能体集群协同优化引擎

在 round 615 完成的元进化能力缺口主动发现与自愈引擎基础上，构建让系统能够自动协调
多个元进化引擎的工作，实现更高效的协同进化。实现从「单引擎独立工作」到「多引擎智能协同」
的范式升级。

系统能够：
1. 多引擎协同调度 - 智能调度多个元进化引擎协同工作
2. 任务智能分配 - 根据引擎能力自动分配任务
3. 负载均衡优化 - 动态调整引擎工作负载
4. 协同结果汇总 - 整合多引擎执行结果
5. 协同学习优化 - 从协同工作中学习最优协同模式

与 round 600-615 所有元进化引擎深度集成，形成「智能调度→协同执行→结果汇总→学习优化」的
完整协同闭环。

Version: 1.0.0
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from collections import defaultdict
import subprocess

# 项目根目录
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
RUNTIME_DIR = PROJECT_ROOT / "runtime"
STATE_DIR = RUNTIME_DIR / "state"
LOGS_DIR = RUNTIME_DIR / "logs"
REFERENCES_DIR = PROJECT_ROOT / "references"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"


class MetaAgentClusterCollaborationOptimizer:
    """元进化智能体集群协同优化引擎"""

    def __init__(self):
        self.name = "元进化智能体集群协同优化引擎"
        self.version = "1.0.0"
        self.state_dir = STATE_DIR
        self.logs_dir = LOGS_DIR
        # 数据文件
        self.cluster_state_file = self.state_dir / "meta_cluster_state.json"
        self.task_allocation_file = self.state_dir / "meta_task_allocation.json"
        self.collaboration_history_file = self.state_dir / "meta_collaboration_history.json"
        self.learning_data_file = self.state_dir / "meta_cluster_learning.json"
        # 已注册的元进化引擎
        self.registered_engines = {}
        # 当前循环轮次
        self.current_loop_round = 616

    def get_version(self):
        """获取引擎版本信息"""
        return {
            "name": self.name,
            "version": self.version,
            "description": "元进化智能体集群协同优化引擎 - 让系统协调多个元进化引擎协同工作"
        }

    def register_engines(self):
        """注册所有可用的元进化引擎"""
        engines = {}

        # 扫描 scripts 目录下的元进化引擎
        meta_engines = [
            "evolution_meta_learning_engine.py",
            "evolution_meta_optimizer.py",
            "evolution_meta_coordination_engine.py",
            "evolution_meta_cognition_deep_enhancement_engine.py",
            "evolution_meta_decision_deep_enhancement_engine.py",
            "evolution_meta_autonomous_consciousness_deep_engine.py",
            "evolution_meta_evolution_enhancement_engine.py",
            "evolution_meta_driven_adaptive_value_deep_optimization_engine.py",
            "evolution_meta_cognition_meta_decision_integration_engine.py",
            "evolution_meta_evolution_internal_health_diagnosis_self_healing_engine.py",
            "evolution_meta_knowledge_graph_reasoning_engine.py",
            "evolution_meta_methodology_auto_optimizer.py",
            "evolution_meta_health_diagnosis_self_healing_engine.py",
            "evolution_meta_decision_auto_execution_engine.py",
            "evolution_meta_self_reflection_deep_introspection_engine.py",
            "evolution_meta_value_prediction_prevention_engine.py",
            "evolution_meta_evolution_full_auto_loop_engine.py",
            "evolution_meta_self_awareness_deep_enhancement_engine.py",
            "evolution_meta_self_optimization_engine.py",
            "evolution_meta_active_innovation_engine.py",
            "evolution_meta_cognitive_distillation_inheritance_engine.py",
            "evolution_meta_value_strategy_prediction_adaptive_optimizer.py",
            "evolution_meta_system_emergence_deep_enhancement_engine.py",
            "evolution_meta_value_prediction_strategic_investment_engine.py",
            "evolution_meta_value_strategy_prediction_execution_closed_loop_engine.py",
            "evolution_meta_value_investment_intelligent_decision_engine.py",
            "evolution_meta_optimization_opportunity_discovery_engine.py",
            "evolution_meta_efficiency_adaptive_continual_optimizer.py",
            "evolution_meta_agency_autonomous_consciousness_engine.py",
            "evolution_meta_self_reflection_intelligent_decision_engine.py",
            "evolution_meta_evolution_full_link_smart_orchestration_engine.py",
            "evolution_meta_cognition_deep_self_reflection_recursive_optimizer_engine.py",
            "evolution_meta_wisdom_extraction_strategic_planning_engine.py",
            "evolution_meta_emergence_innovation_engine.py",
            "evolution_meta_innovation_investment_execution_engine.py",
            "evolution_meta_methodology_self_reflection_optimizer.py",
            "evolution_meta_value_prediction_prevention_v2_engine.py",
            "evolution_meta_execution_closed_loop_automation_engine.py",
            "evolution_meta_decision_meta_cognition_engine.py",
            "evolution_meta_value_self_reinforcement_engine.py",
            "evolution_meta_capability_gap_discovery_self_healing_engine.py",
        ]

        for engine_file in meta_engines:
            engine_path = SCRIPTS_DIR / engine_file
            if engine_path.exists():
                engine_name = engine_file.replace(".py", "")
                engines[engine_name] = {
                    "path": str(engine_path),
                    "status": "available",
                    "capabilities": self._infer_engine_capabilities(engine_name)
                }

        self.registered_engines = engines
        return engines

    def _infer_engine_capabilities(self, engine_name):
        """根据引擎名称推断其能力"""
        capabilities = []

        if "capability_gap" in engine_name or "self_healing" in engine_name:
            capabilities.extend(["capability_discovery", "self_repair", "gap_analysis"])
        if "value" in engine_name and "prediction" in engine_name:
            capabilities.extend(["value_prediction", "trend_analysis"])
        if "innovation" in engine_name:
            capabilities.extend(["innovation", "idea_generation"])
        if "decision" in engine_name:
            capabilities.extend(["decision_making", "strategy"])
        if "optimization" in engine_name:
            capabilities.extend(["optimization", "efficiency"])
        if "learning" in engine_name:
            capabilities.extend(["learning", "adaptation"])
        if "self_reflection" in engine_name or "meta_cognition" in engine_name:
            capabilities.extend(["self_reflection", "meta_cognition"])
        if "health" in engine_name or "diagnosis" in engine_name:
            capabilities.extend(["health_check", "diagnosis"])
        if "collaboration" in engine_name or "coordination" in engine_name:
            capabilities.extend(["collaboration", "coordination"])

        return capabilities if capabilities else ["general"]

    def smart_task_allocation(self, task_requirements):
        """任务智能分配 - 根据任务需求分配到最合适的引擎"""
        # 确保引擎已注册
        if not self.registered_engines:
            self.register_engines()

        # 分析任务需求
        required_capabilities = task_requirements.get("capabilities", [])
        priority = task_requirements.get("priority", "medium")
        estimated_complexity = task_requirements.get("complexity", 1)

        # 查找最合适的引擎
        suitable_engines = []
        for engine_name, engine_info in self.registered_engines.items():
            engine_caps = set(engine_info["capabilities"])
            required_caps = set(required_capabilities)

            # 计算匹配度
            match_score = len(engine_caps.intersection(required_caps)) / max(len(required_caps), 1)

            if match_score > 0:
                suitable_engines.append({
                    "engine_name": engine_name,
                    "engine_info": engine_info,
                    "match_score": match_score,
                    "current_load": self._get_engine_load(engine_name)
                })

        # 按匹配度和负载排序
        suitable_engines.sort(key=lambda x: (x["match_score"], -x["current_load"]), reverse=True)

        # 分配任务
        allocated_engines = []
        remaining_complexity = estimated_complexity

        for engine in suitable_engines:
            if remaining_complexity <= 0:
                break
            allocated_engines.append(engine)
            remaining_complexity -= 1

        # 保存任务分配结果
        allocation_result = {
            "task_requirements": task_requirements,
            "allocated_engines": allocated_engines,
            "allocation_time": datetime.now().isoformat(),
            "round": self.current_loop_round
        }
        self._save_task_allocation(allocation_result)

        return allocation_result

    def _get_engine_load(self, engine_name):
        """获取引擎当前负载（基于历史任务数）"""
        history_file = self.collaboration_history_file
        if history_file.exists():
            try:
                with open(history_file, "r", encoding="utf-8") as f:
                    history = json.load(f)
                # 统计最近任务数
                recent_tasks = [t for t in history.get("tasks", [])
                              if t.get("engine") == engine_name]
                return len(recent_tasks)
            except:
                pass
        return 0

    def coordinate_collaborative_execution(self, task_plan):
        """协调多个引擎协同执行任务"""
        # 任务分配
        allocation = self.smart_task_allocation({
            "capabilities": task_plan.get("required_capabilities", []),
            "priority": task_plan.get("priority", "medium"),
            "complexity": task_plan.get("complexity", 1)
        })

        # 执行任务（模拟）
        execution_results = []
        for engine_info in allocation["allocated_engines"]:
            engine_name = engine_info["engine_name"]
            result = {
                "engine": engine_name,
                "status": "ready",
                "execution_time": datetime.now().isoformat(),
                "capabilities_used": engine_info["engine_info"]["capabilities"]
            }
            execution_results.append(result)

        # 保存执行结果
        collaboration_result = {
            "task_plan": task_plan,
            "allocation": allocation,
            "execution_results": execution_results,
            "collaboration_time": datetime.now().isoformat(),
            "round": self.current_loop_round
        }
        self._save_collaboration_history(collaboration_result)

        return collaboration_result

    def optimize_cluster_performance(self):
        """优化集群性能 - 基于历史数据优化协同模式"""
        # 加载协作历史
        history = self._load_collaboration_history()

        if not history or len(history.get("tasks", [])) < 3:
            return {"status": "insufficient_data", "message": "需要更多历史数据来优化"}

        # 分析协同模式
        engine_performance = defaultdict(lambda: {"success": 0, "total": 0})
        for task in history.get("tasks", []):
            engine = task.get("engine")
            if engine:
                engine_performance[engine]["total"] += 1
                if task.get("status") == "success":
                    engine_performance[engine]["success"] += 1

        # 生成优化建议
        optimization_suggestions = []
        for engine, stats in engine_performance.items():
            success_rate = stats["success"] / max(stats["total"], 1)
            if success_rate < 0.5:
                optimization_suggestions.append({
                    "engine": engine,
                    "issue": "success_rate_low",
                    "suggestion": f"建议优化 {engine} 的执行策略，当前成功率仅 {success_rate:.1%}"
                })

        # 保存优化结果
        optimization_result = {
            "analysis_time": datetime.now().isoformat(),
            "engine_performance": dict(engine_performance),
            "optimization_suggestions": optimization_suggestions,
            "round": self.current_loop_round
        }
        self._save_learning_data(optimization_result)

        return optimization_result

    def get_cluster_status(self):
        """获取集群状态"""
        if not self.registered_engines:
            self.register_engines()

        # 获取各引擎状态
        engine_status = {}
        for engine_name, engine_info in self.registered_engines.items():
            engine_status[engine_name] = {
                "status": engine_info["status"],
                "capabilities": engine_info["capabilities"],
                "current_load": self._get_engine_load(engine_name)
            }

        # 计算集群负载
        total_load = sum(s.get("current_load", 0) for s in engine_status.values())
        avg_load = total_load / max(len(engine_status), 1)

        return {
            "total_engines": len(self.registered_engines),
            "active_engines": len([e for e in self.registered_engines.values() if e["status"] == "available"]),
            "total_load": total_load,
            "average_load": avg_load,
            "engine_status": engine_status,
            "round": self.current_loop_round
        }

    def get_cockpit_data(self):
        """获取驾驶舱数据接口"""
        cluster_status = self.get_cluster_status()
        optimization = self.optimize_cluster_performance()

        return {
            "cluster_status": cluster_status,
            "optimization": optimization,
            "engines": list(self.registered_engines.keys()),
            "round": self.current_loop_round,
            "updated_at": datetime.now().isoformat()
        }

    def _save_task_allocation(self, allocation):
        """保存任务分配结果"""
        self.task_allocation_file.parent.mkdir(parents=True, exist_ok=True)

        # 读取现有数据
        existing = {}
        if self.task_allocation_file.exists():
            try:
                with open(self.task_allocation_file, "r", encoding="utf-8") as f:
                    existing = json.load(f)
            except:
                pass

        # 追加新分配
        if "allocations" not in existing:
            existing["allocations"] = []
        existing["allocations"].append(allocation)

        # 只保留最近20条
        existing["allocations"] = existing["allocations"][-20:]

        with open(self.task_allocation_file, "w", encoding="utf-8") as f:
            json.dump(existing, f, ensure_ascii=False, indent=2)

    def _save_collaboration_history(self, result):
        """保存协作历史"""
        self.collaboration_history_file.parent.mkdir(parents=True, exist_ok=True)

        existing = {"tasks": []}
        if self.collaboration_history_file.exists():
            try:
                with open(self.collaboration_history_file, "r", encoding="utf-8") as f:
                    existing = json.load(f)
            except:
                pass

        existing["tasks"].append(result)
        existing["tasks"] = existing["tasks"][-100:]  # 保留最近100条

        with open(self.collaboration_history_file, "w", encoding="utf-8") as f:
            json.dump(existing, f, ensure_ascii=False, indent=2)

    def _load_collaboration_history(self):
        """加载协作历史"""
        if self.collaboration_history_file.exists():
            try:
                with open(self.collaboration_history_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                pass
        return {"tasks": []}

    def _save_learning_data(self, data):
        """保存学习数据"""
        self.learning_data_file.parent.mkdir(parents=True, exist_ok=True)

        existing = []
        if self.learning_data_file.exists():
            try:
                with open(self.learning_data_file, "r", encoding="utf-8") as f:
                    existing = json.load(f)
            except:
                pass

        existing.append(data)
        existing = existing[-20:]  # 保留最近20条

        with open(self.learning_data_file, "w", encoding="utf-8") as f:
            json.dump(existing, f, ensure_ascii=False, indent=2)

    def run(self, action="status", **kwargs):
        """运行引擎"""
        if action == "version":
            return self.get_version()
        elif action == "status":
            return self.get_cluster_status()
        elif action == "register":
            return self.register_engines()
        elif action == "allocate":
            return self.smart_task_allocation(kwargs.get("task_requirements", {}))
        elif action == "coordinate":
            return self.coordinate_collaborative_execution(kwargs.get("task_plan", {}))
        elif action == "optimize":
            return self.optimize_cluster_performance()
        elif action == "cockpit":
            return self.get_cockpit_data()
        else:
            return {"error": f"未知动作: {action}"}


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="元进化智能体集群协同优化引擎")
    parser.add_argument("--action", default="status", choices=["version", "status", "register", "allocate", "coordinate", "optimize", "cockpit"],
                       help="要执行的动作")
    parser.add_argument("--task-requirements", type=str, help="任务需求 JSON 字符串")
    parser.add_argument("--task-plan", type=str, help="任务计划 JSON 字符串")
    parser.add_argument("--run", action="store_true", help="运行引擎")
    parser.add_argument("--version", action="store_true", help="显示版本信息")
    parser.add_argument("--status", action="store_true", help="显示集群状态")
    parser.add_argument("--cockpit", action="store_true", help="获取驾驶舱数据")

    args = parser.parse_args()

    engine = MetaAgentClusterCollaborationOptimizer()

    if args.version:
        print(json.dumps(engine.get_version(), ensure_ascii=False, indent=2))
    elif args.status:
        print(json.dumps(engine.get_cluster_status(), ensure_ascii=False, indent=2))
    elif args.cockpit:
        print(json.dumps(engine.get_cockpit_data(), ensure_ascii=False, indent=2))
    elif args.run:
        result = engine.run(args.action)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        # 默认显示版本和状态
        print("=== 元进化智能体集群协同优化引擎 ===")
        print(json.dumps(engine.get_version(), ensure_ascii=False, indent=2))
        print("\n=== 集群状态 ===")
        print(json.dumps(engine.get_cluster_status(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()