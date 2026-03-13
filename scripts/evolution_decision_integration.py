#!/usr/bin/env python3
"""
智能进化执行智能决策集成引擎 (Evolution Decision Integration Engine)
将跨引擎协同智能决策引擎（round 234）与进化策略引擎深度集成，
实现进化过程的智能引擎选择与自适应执行

Version: 1.0.0
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# 添加项目根目录和脚本目录到路径
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(SCRIPT_DIR))

try:
    from cross_engine_smart_decision_engine import CrossEngineSmartDecisionEngine
except ImportError:
    CrossEngineSmartDecisionEngine = None

try:
    from evolution_strategy_optimizer import EvolutionStrategyOptimizer
except ImportError:
    EvolutionStrategyOptimizer = None


class EvolutionDecisionIntegration:
    """智能进化执行智能决策集成引擎"""

    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.scripts_dir = self.project_root / "scripts"
        self.runtime_state_dir = self.project_root / "runtime" / "state"
        self.runtime_logs_dir = self.project_root / "runtime" / "logs"

        # 初始化各组件
        self.decision_engine = None
        self.strategy_optimizer = None

        self._initialize_components()

        # 进化决策历史
        self.decision_history = []
        self.load_decision_history()

    def _initialize_components(self):
        """初始化各组件"""
        # 初始化跨引擎智能决策引擎
        if CrossEngineSmartDecisionEngine:
            try:
                self.decision_engine = CrossEngineSmartDecisionEngine()
                print("[集成引擎] 跨引擎智能决策引擎已加载")
            except Exception as e:
                print(f"[集成引擎] 跨引擎智能决策引擎加载失败: {e}")

        # 初始化进化策略优化器
        if EvolutionStrategyOptimizer:
            try:
                self.strategy_optimizer = EvolutionStrategyOptimizer()
                print("[集成引擎] 进化策略优化器已加载")
            except Exception as e:
                print(f"[集成引擎] 进化策略优化器加载失败: {e}")

    def load_decision_history(self):
        """加载决策历史"""
        history_file = self.runtime_state_dir / "evolution_decision_history.json"
        if history_file.exists():
            try:
                with open(history_file, "r", encoding="utf-8") as f:
                    self.decision_history = json.load(f)
            except Exception as e:
                print(f"[集成引擎] 加载决策历史失败: {e}")
                self.decision_history = []

    def save_decision_history(self):
        """保存决策历史"""
        history_file = self.runtime_state_dir / "evolution_decision_history.json"
        try:
            with open(history_file, "w", encoding="utf-8") as f:
                json.dump(self.decision_history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[集成引擎] 保存决策历史失败: {e}")

    def analyze_evolution_task(self, task_description: str) -> Dict[str, Any]:
        """
        分析进化任务并生成智能决策

        Args:
            task_description: 进化任务描述

        Returns:
            包含意图分析、引擎选择、策略建议的字典
        """
        result = {
            "task_description": task_description,
            "timestamp": datetime.now().isoformat(),
            "intent_analysis": {},
            "selected_engines": [],
            "execution_plan": {},
            "strategy_recommendation": {},
            "success": False,
            "error": None
        }

        try:
            # 1. 使用跨引擎智能决策引擎分析任务意图
            if self.decision_engine:
                intent_analysis = self.decision_engine.analyze_task_intent(task_description)
                result["intent_analysis"] = intent_analysis

                # 2. 智能选择最优引擎组合
                selected_engines = self.decision_engine.select_optimal_engine组合(intent_analysis)
                result["selected_engines"] = selected_engines

                # 3. 生成执行计划
                execution_plan = self.decision_engine.generate_execution_plan(
                    intent_analysis, selected_engines
                )
                result["execution_plan"] = execution_plan
            else:
                result["error"] = "跨引擎智能决策引擎未加载"
                return result

            # 4. 使用进化策略优化器提供策略建议
            if self.strategy_optimizer:
                try:
                    strategy_analysis = self.strategy_optimizer.analyze_history()
                    best_path = self.strategy_optimizer.recommend_best_path()
                    result["strategy_recommendation"] = {
                        "analysis": strategy_analysis,
                        "best_path": best_path,
                        "optimized": True
                    }
                except Exception as e:
                    result["strategy_recommendation"] = {
                        "error": str(e),
                        "optimized": False
                    }

            result["success"] = True

            # 保存到历史
            self.decision_history.append({
                "task": task_description,
                "result": result,
                "timestamp": result["timestamp"]
            })
            self.save_decision_history()

        except Exception as e:
            result["error"] = str(e)

        return result

    def smart_execute_evolution(self, evolution_goal: str, dry_run: bool = True) -> Dict[str, Any]:
        """
        智能执行进化任务

        Args:
            evolution_goal: 进化目标描述
            dry_run: 是否仅模拟执行

        Returns:
            执行结果
        """
        result = {
            "evolution_goal": evolution_goal,
            "dry_run": dry_run,
            "timestamp": datetime.now().isoformat(),
            "execution_result": {},
            "success": False
        }

        # 先分析任务
        analysis = self.analyze_evolution_task(evolution_goal)

        if not analysis.get("success"):
            result["execution_result"] = analysis
            return result

        # 如果不是 dry_run，实际执行
        if not dry_run and self.decision_engine:
            try:
                exec_result = self.decision_engine.execute_task(evolution_goal, dry_run=False)
                result["execution_result"] = exec_result
                result["success"] = True
            except Exception as e:
                result["execution_result"] = {"error": str(e)}
        else:
            # dry_run 模式返回计划
            result["execution_result"] = {
                "intent_analysis": analysis.get("intent_analysis", {}),
                "selected_engines": analysis.get("selected_engines", []),
                "execution_plan": analysis.get("execution_plan", {}),
                "strategy_recommendation": analysis.get("strategy_recommendation", {})
            }
            result["success"] = True

        return result

    def get_evolution_recommendations(self) -> Dict[str, Any]:
        """
        获取进化推荐建议

        Returns:
            进化推荐建议
        """
        recommendations = {
            "timestamp": datetime.now().isoformat(),
            "recommendations": [],
            "success": False
        }

        try:
            # 获取引擎建议
            if self.decision_engine:
                engine_suggestions = self.decision_engine.suggest_improvements()
                recommendations["engine_suggestions"] = engine_suggestions

            # 获取策略建议
            if self.strategy_optimizer:
                best_path = self.strategy_optimizer.recommend_best_path()
                predictions = self.strategy_optimizer.predict_strategy_effect("adaptive")

                recommendations["strategy_suggestions"] = {
                    "best_path": best_path,
                    "predictions": predictions
                }

            # 综合推荐
            recommendations["recommendations"] = [
                {
                    "type": "engine_integration",
                    "description": "使用跨引擎智能决策引擎优化进化执行路径",
                    "priority": "high"
                },
                {
                    "type": "strategy_optimization",
                    "description": "基于历史进化数据动态调整进化策略",
                    "priority": "medium"
                },
                {
                    "type": "auto_execution",
                    "description": "启用自动化进化执行减少人工干预",
                    "priority": "medium"
                }
            ]

            recommendations["success"] = True

        except Exception as e:
            recommendations["error"] = str(e)

        return recommendations

    def get_status(self) -> Dict[str, Any]:
        """
        获取集成引擎状态

        Returns:
            状态信息
        """
        status = {
            "timestamp": datetime.now().isoformat(),
            "decision_engine_loaded": self.decision_engine is not None,
            "strategy_optimizer_loaded": self.strategy_optimizer is not None,
            "decision_history_count": len(self.decision_history),
            "components": {}
        }

        # 获取各组件状态
        if self.decision_engine:
            try:
                status["components"]["decision_engine"] = self.decision_engine.get_status()
            except:
                status["components"]["decision_engine"] = {"status": "error"}

        if self.strategy_optimizer:
            try:
                status["components"]["strategy_optimizer"] = self.strategy_optimizer.get_status()
            except:
                status["components"]["strategy_optimizer"] = {"status": "error"}

        return status


def main():
    """主函数 - 命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(
        description="智能进化执行智能决策集成引擎"
    )
    parser.add_argument(
        "command",
        nargs="?",
        choices=["analyze", "execute", "recommend", "status"],
        default="status",
        help="执行命令"
    )
    parser.add_argument(
        "--task",
        type=str,
        help="进化任务描述"
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="实际执行（否则为 dry-run）"
    )

    args = parser.parse_args()

    # 初始化引擎
    engine = EvolutionDecisionIntegration()

    if args.command == "analyze":
        if not args.task:
            print("错误: 分析任务需要 --task 参数")
            sys.exit(1)
        result = engine.analyze_evolution_task(args.task)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "execute":
        if not args.task:
            print("错误: 执行任务需要 --task 参数")
            sys.exit(1)
        result = engine.smart_execute_evolution(args.task, dry_run=not args.execute)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "recommend":
        result = engine.get_evolution_recommendations()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "status":
        result = engine.get_status()
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()