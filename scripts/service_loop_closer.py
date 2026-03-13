#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
智能推荐-编排-执行-解释完整闭环引擎

深度集成 unified_recommender、dynamic_engine_orchestrator、auto_execution_engine、decision_explainer_engine
实现从「推荐→编排→执行→解释」的完整服务闭环

这是 round 198 后推荐的增强方向：实现从推荐/编排到解释的完整闭环

功能：
1. 统一推荐入口 - 根据用户意图获取推荐
2. 智能编排 - 将推荐转化为可执行计划
3. 自动执行 - 执行编排计划
4. 决策解释 - 解释每个步骤的原因和决策点

形成「推荐→编排→执行→解释→反馈」的完整闭环
"""

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# 确保 scripts 目录在路径中
SCRIPT_DIR = Path(__file__).parent
RUNTIME_DIR = SCRIPT_DIR.parent
STATE_DIR = RUNTIME_DIR / "state"
LOGS_DIR = RUNTIME_DIR / "logs"

# 导入各引擎
sys.path.insert(0, str(SCRIPT_DIR))

# 导入统一推荐引擎
try:
    from unified_recommender import UnifiedRecommenderEngine
    UNIFIED_RECOMMENDER_AVAILABLE = True
except ImportError:
    UNIFIED_RECOMMENDER_AVAILABLE = False
    print("警告: unified_recommender 模块不可用")

# 导入动态编排引擎
try:
    from dynamic_engine_orchestrator import DynamicEngineOrchestrator
    DYNAMIC_ORCHESTRATOR_AVAILABLE = True
except ImportError:
    DYNAMIC_ORCHESTRATOR_AVAILABLE = False
    print("警告: dynamic_engine_orchestrator 模块不可用")

# 导入自动化执行引擎
try:
    from auto_execution_engine import AutoExecutionEngine, ExecutionMode
    AUTO_EXECUTION_AVAILABLE = True
except ImportError:
    AUTO_EXECUTION_AVAILABLE = False
    print("警告: auto_execution_engine 模块不可用")

# 导入决策可解释性增强器
try:
    from decision_explainer_engine import DecisionExplainerEngine
    DECISION_EXPLAINER_AVAILABLE = True
except ImportError:
    DECISION_EXPLAINER_AVAILABLE = False
    print("警告: decision_explainer_engine 模块不可用")


class ServiceLoopCloser:
    """智能推荐-编排-执行-解释完整闭环引擎"""

    def __init__(self):
        self.state_file = STATE_DIR / "service_loop_closer_state.json"
        self.history_file = STATE_DIR / "service_loop_closer_history.json"

        # 初始化各子引擎
        self.recommender = None
        self.orchestrator = None
        self.executor = None
        self.explainer = None

        self._init_engines()
        self.state = self._load_state()

    def _init_engines(self):
        """初始化各子引擎"""
        if UNIFIED_RECOMMENDER_AVAILABLE:
            try:
                self.recommender = UnifiedRecommenderEngine()
                print("[OK] Unified Recommender Engine loaded")
            except Exception as e:
                print(f"[FAIL] Unified Recommender Engine: {e}")

        if DYNAMIC_ORCHESTRATOR_AVAILABLE:
            try:
                self.orchestrator = DynamicEngineOrchestrator()
                print("[OK] Dynamic Orchestrator Engine loaded")
            except Exception as e:
                print(f"[FAIL] Dynamic Orchestrator Engine: {e}")

        if AUTO_EXECUTION_AVAILABLE:
            try:
                self.executor = AutoExecutionEngine()
                print("[OK] Auto Execution Engine loaded")
            except Exception as e:
                print(f"[FAIL] Auto Execution Engine: {e}")

        if DECISION_EXPLAINER_AVAILABLE:
            try:
                self.explainer = DecisionExplainerEngine()
                print("[OK] Decision Explainer Engine loaded")
            except Exception as e:
                print(f"[FAIL] Decision Explainer Engine: {e}")

    def _load_state(self) -> Dict:
        """加载状态"""
        if self.state_file.exists():
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "total_runs": 0,
            "successful_runs": 0,
            "last_run": None,
            "engines_status": {
                "recommender": UNIFIED_RECOMMENDER_AVAILABLE,
                "orchestrator": DYNAMIC_ORCHESTRATOR_AVAILABLE,
                "executor": AUTO_EXECUTION_AVAILABLE,
                "explainer": DECISION_EXPLAINER_AVAILABLE
            }
        }

    def _save_state(self):
        """保存状态"""
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2)

    def _load_history(self) -> List[Dict]:
        """加载执行历史"""
        if self.history_file.exists():
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return []

    def _save_history(self, history: List[Dict]):
        """保存执行历史"""
        # 只保留最近 50 条
        history = history[-50:]
        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

    def run_full_loop(self, user_intent: str, auto_execute: bool = True) -> Dict:
        """
        执行完整的「推荐→编排→执行→解释」闭环

        Args:
            user_intent: 用户意图描述
            auto_execute: 是否自动执行（True=自动执行，False=仅生成计划）

        Returns:
            包含推荐、编排、执行、解释的完整结果
        """
        result = {
            "timestamp": datetime.now().isoformat(),
            "user_intent": user_intent,
            "recommendations": [],
            "orchestration_plan": None,
            "execution_result": None,
            "explanations": [],
            "status": "init",
            "errors": []
        }

        # 步骤 1: 获取推荐
        print("\n=== 步骤 1: 获取推荐 ===")
        if self.recommender:
            try:
                # 使用统一推荐引擎获取推荐
                if hasattr(self.recommender, 'get_recommendations'):
                    recommendations = self.recommender.get_recommendations(user_intent)
                    result["recommendations"] = [
                        {
                            "name": r.name if hasattr(r, 'name') else str(r),
                            "description": r.description if hasattr(r, 'description') else "",
                            "reason": r.reason if hasattr(r, 'reason') else "",
                            "confidence": r.confidence if hasattr(r, 'confidence') else 0.0,
                            "action": r.action if hasattr(r, 'action') else ""
                        }
                        for r in recommendations[:3]  # 取前 3 个推荐
                    ]
                    print(f"✓ 获取到 {len(result['recommendations'])} 个推荐")

                    # 解释推荐理由
                    if self.explainer:
                        recommendation_explanation = self.explainer.explain_recommendation(
                            user_intent,
                            result["recommendations"]
                        )
                        result["explanations"].append({
                            "phase": "recommendation",
                            "explanation": recommendation_explanation
                        })
            except Exception as e:
                error_msg = f"推荐阶段错误: {e}"
                print(f"✗ {error_msg}")
                result["errors"].append(error_msg)

        # 步骤 2: 智能编排
        print("\n=== 步骤 2: 智能编排 ===")
        if self.orchestrator and result["recommendations"]:
            try:
                # 使用第一个推荐作为编排输入
                primary_recommendation = result["recommendations"][0]
                plan = self.orchestrator.create_orchestration_plan(
                    user_intent,
                    primary_recommendation.get("action", "")
                )
                result["orchestration_plan"] = plan
                print("✓ 编排计划已生成")

                # 解释编排决策
                if self.explainer:
                    orchestration_explanation = self.explainer.explain_workflow(
                        plan.get("steps", []) if plan else []
                    )
                    result["explanations"].append({
                        "phase": "orchestration",
                        "explanation": orchestration_explanation
                    })
            except Exception as e:
                error_msg = f"编排阶段错误: {e}"
                print(f"✗ {error_msg}")
                result["errors"].append(error_msg)

        # 步骤 3: 执行计划
        print("\n=== 步骤 3: 执行计划 ===")
        if self.executor and result["orchestration_plan"]:
            try:
                if auto_execute:
                    # 自动执行
                    exec_result = self.executor.execute_plan(result["orchestration_plan"])
                    result["execution_result"] = {
                        "status": exec_result.get("status", "unknown"),
                        "message": exec_result.get("message", ""),
                        "details": exec_result
                    }
                    print(f"✓ 执行完成: {exec_result.get('status', 'unknown')}")
                else:
                    # 仅生成计划，不执行
                    result["execution_result"] = {
                        "status": "planned_only",
                        "message": "计划已生成，等待用户确认后执行",
                        "plan": result["orchestration_plan"]
                    }
                    print("✓ 计划已生成（待执行）")
            except Exception as e:
                error_msg = f"执行阶段错误: {e}"
                print(f"✗ {error_msg}")
                result["errors"].append(error_msg)

        # 步骤 4: 生成完整解释
        print("\n=== 步骤 4: 生成完整解释 ===")
        if self.explainer:
            try:
                # 生成完整的决策解释报告
                full_explanation = self.explainer.generate_full_report(result)
                result["full_explanation"] = full_explanation
                print("✓ 决策解释报告已生成")
            except Exception as e:
                error_msg = f"解释生成错误: {e}"
                print(f"✗ {error_msg}")
                result["errors"].append(error_msg)

        # 更新状态
        result["status"] = "completed" if not result["errors"] else "partial"
        self.state["total_runs"] += 1
        if result["status"] == "completed":
            self.state["successful_runs"] += 1
        self.state["last_run"] = datetime.now().isoformat()
        self._save_state()

        # 保存到历史
        history = self._load_history()
        history.append({
            "timestamp": result["timestamp"],
            "user_intent": user_intent,
            "status": result["status"],
            "recommendations_count": len(result["recommendations"]),
            "has_plan": result["orchestration_plan"] is not None,
            "has_execution": result["execution_result"] is not None
        })
        self._save_history(history)

        return result

    def get_status(self) -> Dict:
        """获取服务闭环状态"""
        return {
            "engines_status": self.state.get("engines_status", {}),
            "total_runs": self.state.get("total_runs", 0),
            "successful_runs": self.state.get("successful_runs", 0),
            "success_rate": (
                self.state.get("successful_runs", 0) / max(self.state.get("total_runs", 1), 1)
            ) * 100,
            "last_run": self.state.get("last_run"),
            "闭环状态": "就绪" if all(self.state.get("engines_status", {}).values()) else "部分就绪"
        }

    def explain_current_state(self) -> str:
        """解释当前系统状态"""
        status = self.get_status()
        recommender_status = "[OK]" if status['engines_status'].get('recommender') else "[FAIL]"
        orchestrator_status = "[OK]" if status['engines_status'].get('orchestrator') else "[FAIL]"
        executor_status = "[OK]" if status['engines_status'].get('executor') else "[FAIL]"
        explainer_status = "[OK]" if status['engines_status'].get('explainer') else "[FAIL]"

        explanation = f"""[Service Loop Closer - Status Report]

Engine Status:
- Unified Recommender: {recommender_status}
- Dynamic Orchestrator: {orchestrator_status}
- Auto Executor: {executor_status}
- Decision Explainer: {explainer_status}

Execution Stats:
- Total Runs: {status['total_runs']}
- Successful Runs: {status['successful_runs']}
- Success Rate: {status['success_rate']:.1f}%
- Last Run: {status['last_run'] or 'N/A'}

Loop Status: {status['闭环状态']}

This engine implements the complete service loop:
Recommendation -> Orchestration -> Execution -> Explanation
Integrates: unified_recommender, dynamic_engine_orchestrator,
auto_execution_engine, decision_explainer_engine
"""
        return explanation


def main():
    parser = argparse.ArgumentParser(
        description="智能推荐-编排-执行-解释完整闭环引擎"
    )
    parser.add_argument(
        "command",
        nargs="?",
        default="status",
        choices=["status", "run", "explain"],
        help="命令: status=查看状态, run=运行闭环, explain=解释状态"
    )
    parser.add_argument(
        "--intent", "-i",
        type=str,
        help="用户意图（run 命令时使用）"
    )
    parser.add_argument(
        "--no-auto-execute",
        action="store_true",
        help="仅生成计划，不自动执行"
    )

    args = parser.parse_args()

    # 创建引擎实例
    closer = ServiceLoopCloser()

    if args.command == "status":
        # 查看状态
        status = closer.get_status()
        print(closer.explain_current_state())

    elif args.command == "run":
        # 运行完整闭环
        if not args.intent:
            print("错误: run 命令需要 --intent 参数")
            sys.exit(1)

        result = closer.run_full_loop(
            args.intent,
            auto_execute=not args.no_auto_execute
        )

        print("\n" + "=" * 60)
        print("执行结果:")
        print(f"状态: {result['status']}")
        print(f"推荐数量: {len(result['recommendations'])}")
        print(f"有编排计划: {'是' if result['orchestration_plan'] else '否'}")
        print(f"有执行结果: {'是' if result['execution_result'] else '否'}")

        if result.get("full_explanation"):
            print("\n" + "-" * 60)
            print("决策解释:")
            print(result["full_explanation"])

    elif args.command == "explain":
        # 解释当前状态
        print(closer.explain_current_state())


if __name__ == "__main__":
    main()