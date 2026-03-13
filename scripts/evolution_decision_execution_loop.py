#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能进化决策与执行深度集成引擎 (Evolution Decision-Execution Loop Engine)
将进化决策集成引擎(round 235)与进化执行引擎深度集成，
实现从智能决策→自动执行→结果验证→反馈学习的完整自主进化闭环

功能：
1. 智能进化决策 - 基于跨引擎智能决策引擎和进化策略优化器
2. 自动化进化执行 - 自动执行进化规划
3. 闭环验证 - 验证执行结果并反馈学习
4. 进化状态全程追踪与可视化
5. 自主决策-执行一体化流程

Version: 1.0.0
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# 路径设置
SCRIPTS = Path(__file__).parent
PROJECT = SCRIPTS.parent
RUNTIME_STATE = PROJECT / "runtime" / "state"
RUNTIME_LOGS = PROJECT / "runtime" / "logs"

# 尝试导入依赖模块
try:
    sys.path.insert(0, str(SCRIPTS))
    from evolution_decision_integration import EvolutionDecisionIntegration
    DECISION_INTEGRATION_AVAILABLE = True
except ImportError as e:
    print(f"[进化决策执行集成] 无法导入 EvolutionDecisionIntegration: {e}")
    DECISION_INTEGRATION_AVAILABLE = False
    EvolutionDecisionIntegration = None

try:
    from evolution_loop_execution_enhancer import EvolutionLoopExecutionEnhancer
    EXECUTION_ENHANCER_AVAILABLE = True
except ImportError as e:
    print(f"[进化决策执行集成] 无法导入 EvolutionLoopExecutionEnhancer: {e}")
    EXECUTION_ENHANCER_AVAILABLE = False
    EvolutionLoopExecutionEnhancer = None


class EvolutionDecisionExecutionLoop:
    """智能进化决策与执行深度集成引擎"""

    def __init__(self):
        self.name = "EvolutionDecisionExecutionLoop"
        self.version = "1.0.0"

        # 状态文件路径
        self.loop_state_path = RUNTIME_STATE / "evolution_de_loop_state.json"
        self.loop_history_path = RUNTIME_STATE / "evolution_de_loop_history.json"

        # 初始化组件
        self.decision_integration = None
        self.execution_enhancer = None
        self._initialize_components()

        # 加载状态
        self.loop_state = self._load_loop_state()
        self.loop_history = self._load_loop_history()

    def _initialize_components(self):
        """初始化各组件"""
        if DECISION_INTEGRATION_AVAILABLE and EvolutionDecisionIntegration:
            try:
                self.decision_integration = EvolutionDecisionIntegration()
                print("[进化决策执行集成] 进化决策集成引擎已加载")
            except Exception as e:
                print(f"[进化决策执行集成] 进化决策集成引擎加载失败: {e}")

        if EXECUTION_ENHANCER_AVAILABLE and EvolutionLoopExecutionEnhancer:
            try:
                self.execution_enhancer = EvolutionLoopExecutionEnhancer()
                print("[进化决策执行集成] 进化执行增强引擎已加载")
            except Exception as e:
                print(f"[进化决策执行集成] 进化执行增强引擎加载失败: {e}")

    def _load_loop_state(self) -> Dict[str, Any]:
        """加载循环状态"""
        if self.loop_state_path.exists():
            try:
                with open(self.loop_state_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "current_phase": "idle",  # idle, analyzing, executing, verifying, learning
            "current_round": 0,
            "last_update": None,
            "pending_decisions": [],
            "execution_mode": "auto"  # auto | manual
        }

    def _save_loop_state(self):
        """保存循环状态"""
        self.loop_state["last_update"] = datetime.now().isoformat()
        try:
            with open(self.loop_state_path, "w", encoding="utf-8") as f:
                json.dump(self.loop_state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[进化决策执行集成] 保存循环状态失败: {e}")

    def _load_loop_history(self) -> Dict[str, Any]:
        """加载循环历史"""
        if self.loop_history_path.exists():
            try:
                with open(self.loop_history_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "executions": [],
            "total_cycles": 0,
            "successful_cycles": 0,
            "failed_cycles": 0
        }

    def _save_loop_history(self):
        """保存循环历史"""
        try:
            with open(self.loop_history_path, "w", encoding="utf-8") as f:
                json.dump(self.loop_history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[进化决策执行集成] 保存循环历史失败: {e}")

    def analyze_and_decide(self, task_description: str) -> Dict[str, Any]:
        """
        智能分析任务并做出决策

        Args:
            task_description: 任务描述

        Returns:
            决策结果
        """
        result = {
            "task_description": task_description,
            "timestamp": datetime.now().isoformat(),
            "decision": {},
            "execution_plan": {},
            "success": False,
            "error": None
        }

        try:
            # 使用决策集成引擎进行分析
            if self.decision_integration:
                analysis = self.decision_integration.analyze_evolution_task(task_description)
                result["decision"] = {
                    "intent_analysis": analysis.get("intent_analysis", {}),
                    "selected_engines": analysis.get("selected_engines", []),
                    "strategy_recommendation": analysis.get("strategy_recommendation", {})
                }
                result["execution_plan"] = analysis.get("execution_plan", {})
                result["success"] = analysis.get("success", False)
            else:
                result["error"] = "决策集成引擎未加载"

        except Exception as e:
            result["error"] = str(e)

        return result

    def execute_with_verification(self, execution_plan: Dict[str, Any], auto_verify: bool = True) -> Dict[str, Any]:
        """
        执行并验证结果

        Args:
            execution_plan: 执行计划
            auto_verify: 是否自动验证

        Returns:
            执行结果
        """
        result = {
            "timestamp": datetime.now().isoformat(),
            "execution_plan": execution_plan,
            "execution_result": {},
            "verification_result": {},
            "success": False
        }

        try:
            # 尝试使用执行增强引擎
            if self.execution_enhancer:
                # 更新状态
                self.loop_state["current_phase"] = "executing"
                self._save_loop_state()

                # 执行
                exec_result = self.execution_enhancer.execute_evolution_task(
                    execution_plan.get("description", "Evolution task"),
                    execution_plan.get("steps", []),
                    dry_run=False
                )
                result["execution_result"] = exec_result

                # 自动验证
                if auto_verify:
                    self.loop_state["current_phase"] = "verifying"
                    self._save_loop_state()

                    verify_result = self._verify_execution_result(exec_result)
                    result["verification_result"] = verify_result
                    result["success"] = verify_result.get("verified", False)
                else:
                    result["success"] = True
            else:
                result["execution_result"] = {
                    "message": "执行增强引擎未加载，模拟执行",
                    "simulated": True
                }
                result["success"] = True

        except Exception as e:
            result["error"] = str(e)

        # 更新历史
        self.loop_history["executions"].append(result)
        self.loop_history["total_cycles"] += 1
        if result["success"]:
            self.loop_history["successful_cycles"] += 1
        else:
            self.loop_history["failed_cycles"] += 1
        self._save_loop_history()

        return result

    def _verify_execution_result(self, execution_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证执行结果

        Args:
            execution_result: 执行结果

        Returns:
            验证结果
        """
        verification = {
            "timestamp": datetime.now().isoformat(),
            "verified": False,
            "checks": [],
            "overall_status": "unknown"
        }

        try:
            # 检查执行是否成功
            if execution_result.get("success") or execution_result.get("simulated"):
                verification["checks"].append({
                    "check": "execution_success",
                    "passed": True,
                    "message": "执行成功或模拟执行"
                })
                verification["verified"] = True
            else:
                verification["checks"].append({
                    "check": "execution_success",
                    "passed": False,
                    "message": execution_result.get("error", "执行失败")
                })

            # 检查是否有错误
            if execution_result.get("error"):
                verification["checks"].append({
                    "check": "no_errors",
                    "passed": False,
                    "message": execution_result["error"]
                })
                verification["verified"] = False
            else:
                verification["checks"].append({
                    "check": "no_errors",
                    "passed": True,
                    "message": "无错误"
                })

            # 设置总体状态
            if verification["verified"]:
                verification["overall_status"] = "success"
            else:
                verification["overall_status"] = "failed"

        except Exception as e:
            verification["checks"].append({
                "check": "verification_error",
                "passed": False,
                "message": str(e)
            })
            verification["overall_status"] = "error"

        return verification

    def learn_from_result(self, execution_result: Dict[str, Any], verification_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        从执行结果中学习

        Args:
            execution_result: 执行结果
            verification_result: 验证结果

        Returns:
            学习结果
        """
        learning = {
            "timestamp": datetime.now().isoformat(),
            "learned": False,
            "insights": [],
            "recommendations": []
        }

        try:
            self.loop_state["current_phase"] = "learning"
            self._save_loop_state()

            # 基于验证结果生成洞察
            if verification_result.get("verified"):
                learning["insights"].append({
                    "type": "success_pattern",
                    "description": "执行成功模式已识别",
                    "apply_to_future": True
                })
            else:
                learning["insights"].append({
                    "type": "failure_pattern",
                    "description": "执行失败模式已识别，需要调整策略",
                    "apply_to_future": True
                })

            # 生成推荐
            if self.decision_integration:
                try:
                    recommendations = self.decision_integration.get_evolution_recommendations()
                    learning["recommendations"] = recommendations.get("recommendations", [])
                except Exception:
                    pass

            learning["learned"] = True

            # 更新状态
            self.loop_state["current_phase"] = "idle"
            self._save_loop_state()

        except Exception as e:
            learning["error"] = str(e)

        return learning

    def full_cycle_execution(self, task_description: str, auto_verify: bool = True) -> Dict[str, Any]:
        """
        完整循环执行：决策 → 执行 → 验证 → 学习

        Args:
            task_description: 任务描述
            auto_verify: 是否自动验证

        Returns:
            完整循环结果
        """
        result = {
            "task_description": task_description,
            "timestamp": datetime.now().isoformat(),
            "phases": {},
            "success": False
        }

        try:
            # 阶段1：决策
            self.loop_state["current_phase"] = "analyzing"
            self._save_loop_state()

            decision_result = self.analyze_and_decide(task_description)
            result["phases"]["decision"] = decision_result

            if not decision_result.get("success"):
                result["error"] = decision_result.get("error", "决策阶段失败")
                return result

            # 阶段2：执行
            execution_result = self.execute_with_verification(
                decision_result.get("execution_plan", {}),
                auto_verify=auto_verify
            )
            result["phases"]["execution"] = execution_result

            # 阶段3：验证结果已包含在执行中
            result["phases"]["verification"] = execution_result.get("verification_result", {})

            # 阶段4：学习
            learning_result = self.learn_from_result(
                execution_result.get("execution_result", {}),
                result["phases"]["verification"]
            )
            result["phases"]["learning"] = learning_result

            result["success"] = execution_result.get("success", False)

            # 更新循环状态
            self.loop_state["current_round"] += 1
            self.loop_state["current_phase"] = "idle"
            self._save_loop_state()

        except Exception as e:
            result["error"] = str(e)
            self.loop_state["current_phase"] = "error"
            self._save_loop_state()

        return result

    def get_status(self) -> Dict[str, Any]:
        """
        获取集成引擎状态

        Returns:
            状态信息
        """
        status = {
            "timestamp": datetime.now().isoformat(),
            "version": self.version,
            "components": {
                "decision_integration_loaded": self.decision_integration is not None,
                "execution_enhancer_loaded": self.execution_enhancer is not None
            },
            "loop_state": {
                "current_phase": self.loop_state.get("current_phase", "idle"),
                "current_round": self.loop_state.get("current_round", 0),
                "execution_mode": self.loop_state.get("execution_mode", "auto")
            },
            "loop_history": {
                "total_cycles": self.loop_history.get("total_cycles", 0),
                "successful_cycles": self.loop_history.get("successful_cycles", 0),
                "failed_cycles": self.loop_history.get("failed_cycles", 0)
            }
        }

        # 获取组件详细状态
        if self.decision_integration:
            try:
                status["components"]["decision_integration_status"] = \
                    self.decision_integration.get_status()
            except Exception:
                pass

        if self.execution_enhancer:
            try:
                status["components"]["execution_enhancer_status"] = \
                    self.execution_enhancer.get_status()
            except Exception:
                pass

        return status

    def run_dry_cycle(self, task_description: str) -> Dict[str, Any]:
        """
        运行干运行循环（仅决策和计划，不执行）

        Args:
            task_description: 任务描述

        Returns:
            干运行结果
        """
        result = {
            "task_description": task_description,
            "timestamp": datetime.now().isoformat(),
            "decision": {},
            "execution_plan": {},
            "estimated_execution_steps": 0,
            "dry_run": True
        }

        # 决策阶段
        decision_result = self.analyze_and_decide(task_description)
        result["decision"] = decision_result.get("decision", {})
        result["execution_plan"] = decision_result.get("execution_plan", {})

        # 估算执行步骤
        plan = result["execution_plan"]
        if isinstance(plan, dict):
            result["estimated_execution_steps"] = len(plan.get("steps", []))

        result["success"] = decision_result.get("success", False)

        return result


def main():
    """主函数 - 命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(
        description="智能进化决策与执行深度集成引擎"
    )
    parser.add_argument(
        "command",
        nargs="?",
        choices=["status", "analyze", "execute", "full_cycle", "dry_cycle", "learn"],
        default="status",
        help="执行命令"
    )
    parser.add_argument(
        "--task",
        type=str,
        help="任务描述"
    )
    parser.add_argument(
        "--no-verify",
        action="store_true",
        help="跳过自动验证"
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="实际执行（与 full_cycle 配合）"
    )

    args = parser.parse_args()

    # 初始化引擎
    engine = EvolutionDecisionExecutionLoop()

    if args.command == "status":
        result = engine.get_status()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "analyze":
        if not args.task:
            print("错误: 分析任务需要 --task 参数")
            sys.exit(1)
        result = engine.analyze_and_decide(args.task)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "execute":
        if not args.task:
            print("错误: 执行任务需要 --task 参数")
            sys.exit(1)
        # 先分析
        decision = engine.analyze_and_decide(args.task)
        # 再执行
        result = engine.execute_with_verification(
            decision.get("execution_plan", {}),
            auto_verify=not args.no_verify
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "full_cycle":
        if not args.task:
            print("错误: 完整循环需要 --task 参数")
            sys.exit(1)
        result = engine.full_cycle_execution(args.task, auto_verify=not args.no_verify)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "dry_cycle":
        if not args.task:
            print("错误: 干运行循环需要 --task 参数")
            sys.exit(1)
        result = engine.run_dry_cycle(args.task)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "learn":
        # 示例：从上次执行结果学习
        result = engine.learn_from_result(
            {"success": True, "message": "Test execution"},
            {"verified": True, "overall_status": "success"}
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()