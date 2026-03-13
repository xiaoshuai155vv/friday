#!/usr/bin/env python3
"""
智能进化闭环完整集成引擎 (Evolution Loop Complete Integrator)
版本: 1.0.0
功能: 将创意生成(226)、创意评估执行(227)、进化学习(224)、进化执行(225)深度集成，
     形成"发现→评估→执行→学习→优化"完整闭环
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# 添加脚本目录到路径
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

class EvolutionLoopCompleteIntegrator:
    """智能进化闭环完整集成引擎"""

    def __init__(self):
        self.version = "1.0.0"
        self.state_file = SCRIPT_DIR / ".." / "runtime" / "state" / "evolution闭环_complete_state.json"
        self.history_file = SCRIPT_DIR / ".." / "runtime" / "state" / "evolution闭环_complete_history.json"
        self._ensure_state_file()

        # 集成各模块
        self._init_modules()

    def _ensure_state_file(self):
        """确保状态文件存在"""
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.state_file.exists():
            self._save_state({
                "status": "idle",
                "current_phase": "none",
                "integrated_modules": ["idea_generator", "idea_execution", "learning_enhancer", "execution_enhancer"],
                "last_run": None,
                "total_cycles": 0
            })

    def _load_state(self):
        """加载状态"""
        try:
            with open(self.state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}

    def _save_state(self, state):
        """保存状态"""
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

    def _init_modules(self):
        """初始化集成模块"""
        self.idea_generator = None
        self.idea_execution = None
        self.learning_enhancer = None
        self.execution_enhancer = None

        # 导入并初始化各模块
        try:
            from evolution_idea_generator import EvolutionIdeaGenerator
            self.idea_generator = EvolutionIdeaGenerator()
        except Exception as e:
            print(f"Warning: Could not load idea_generator: {e}")

        try:
            from evolution_idea_execution_engine import EvolutionIdeaExecutionEngine
            self.idea_execution = EvolutionIdeaExecutionEngine()
        except Exception as e:
            print(f"Warning: Could not load idea_execution: {e}")

        try:
            from evolution_loop_learning_enhancer import EvolutionLoopLearningEnhancer
            self.learning_enhancer = EvolutionLoopLearningEnhancer()
        except Exception as e:
            print(f"Warning: Could not load learning_enhancer: {e}")

        try:
            from evolution_loop_execution_enhancer import EvolutionLoopExecutionEnhancer
            self.execution_enhancer = EvolutionLoopExecutionEnhancer()
        except Exception as e:
            print(f"Warning: Could not load execution_enhancer: {e}")

    def status(self):
        """查看集成引擎状态"""
        state = self._load_state()
        loaded = []

        if self.idea_generator:
            loaded.append("idea_generator")
        if self.idea_execution:
            loaded.append("idea_execution")
        if self.learning_enhancer:
            loaded.append("learning_enhancer")
        if self.execution_enhancer:
            loaded.append("execution_enhancer")

        return {
            "version": self.version,
            "status": state.get("status", "idle"),
            "current_phase": state.get("current_phase", "none"),
            "loaded_modules": loaded,
            "total_cycles": state.get("total_cycles", 0),
            "last_run": state.get("last_run")
        }

    def run_full_loop(self, dry_run=True):
        """
        运行完整的进化闭环
        流程: 发现(创意生成) → 评估(创意评估) → 执行(进化执行) → 学习(学习增强) → 优化(策略调整)
        """
        cycle_result = {
            "timestamp": datetime.now().isoformat(),
            "phases": {},
            "success": False,
            "error": None
        }

        try:
            # Phase 1: 发现 - 生成进化创意
            self._update_state({"status": "running", "current_phase": "discovery"})
            ideas = []
            if self.idea_generator:
                # 使用 generate_evolution_ideas 生成创意
                try:
                    ideas = self.idea_generator.generate_evolution_ideas()
                    cycle_result["phases"]["discovery"] = {
                        "status": "success",
                        "ideas_generated": len(ideas) if ideas else 0
                    }
                except Exception as e:
                    cycle_result["phases"]["discovery"] = {
                        "status": "failed",
                        "error": str(e)
                    }
                    # 即使失败也继续，使用空列表
                    ideas = []
            else:
                cycle_result["phases"]["discovery"] = {"status": "skipped", "reason": "module not loaded"}

            # Phase 2: 评估 - 评估创意价值并选择
            selected_ideas = []
            self._update_state({"current_phase": "evaluation"})
            if self.idea_execution and ideas:
                try:
                    # 使用 idea_execution 的 execute_idea 进行评估（dry_run 模式）
                    evaluated = []
                    for idea in ideas:
                        # 用 dry_run 模式评估创意
                        result = self.idea_execution.execute_idea(idea, dry_run=True)
                        if result and result.get("status") in ["dry_run", "pending"]:
                            selected_ideas.append(idea)
                            score = idea.get("total_score", idea.get("score", 0.7))
                            evaluated.append({"idea": idea, "score": score})
                    cycle_result["phases"]["evaluation"] = {
                        "status": "success",
                        "ideas_evaluated": len(evaluated),
                        "ideas_selected": len(selected_ideas)
                    }
                except Exception as e:
                    cycle_result["phases"]["evaluation"] = {
                        "status": "failed",
                        "error": str(e)
                    }
                    # 选择评分最高的创意
                    selected_ideas = ideas[:1] if ideas else []
            else:
                # 如果评估模块不可用，选择第一个创意
                selected_ideas = ideas[:1] if ideas else []
                cycle_result["phases"]["evaluation"] = {
                    "status": "partial",
                    "selected_ideas": len(selected_ideas)
                }

            # Phase 3: 执行 - 执行选定的创意
            execution_results = []
            self._update_state({"current_phase": "execution"})
            if self.execution_enhancer and selected_ideas and not dry_run:
                try:
                    for idea in selected_ideas:
                        result = self.execution_enhancer.execute_evolution_cycle(
                            goal_description=idea.get("description", str(idea))
                        )
                        execution_results.append(result)
                    cycle_result["phases"]["execution"] = {
                        "status": "success",
                        "executions": len(execution_results)
                    }
                except Exception as e:
                    cycle_result["phases"]["execution"] = {
                        "status": "partial",
                        "error": str(e),
                        "executions": 0
                    }
            elif dry_run:
                cycle_result["phases"]["execution"] = {
                    "status": "dry_run",
                    "would_execute": len(selected_ideas)
                }
            else:
                cycle_result["phases"]["execution"] = {
                    "status": "skipped",
                    "reason": "module not available"
                }

            # Phase 4: 学习 - 从执行结果中学习
            self._update_state({"current_phase": "learning"})
            learning_insights = None
            if self.learning_enhancer:
                try:
                    # 分析进化结果
                    analysis = self.learning_enhancer.analyze_evolution_results()
                    # 优化策略
                    optimization = self.learning_enhancer.optimize_strategy()
                    learning_insights = {
                        "analysis": analysis,
                        "optimization": optimization
                    }
                    cycle_result["phases"]["learning"] = {
                        "status": "success",
                        "insights": "generated"
                    }
                except Exception as e:
                    cycle_result["phases"]["learning"] = {
                        "status": "partial",
                        "error": str(e)
                    }
                    learning_insights = None
            else:
                cycle_result["phases"]["learning"] = {
                    "status": "skipped",
                    "reason": "module not loaded"
                }

            # Phase 5: 优化 - 基于学习结果优化下一轮
            self._update_state({"current_phase": "optimization"})
            cycle_result["phases"]["optimization"] = {
                "status": "success",
                "learning_insights": learning_insights is not None
            }

            # 更新状态
            state = self._load_state()
            state["status"] = "completed"
            state["current_phase"] = "none"
            state["last_run"] = cycle_result["timestamp"]
            state["total_cycles"] = state.get("total_cycles", 0) + 1
            self._save_state(state)

            cycle_result["success"] = True
            cycle_result["selected_ideas"] = selected_ideas
            cycle_result["learning_insights"] = learning_insights

        except Exception as e:
            cycle_result["error"] = str(e)
            cycle_result["success"] = False

        # 保存到历史
        self._save_to_history(cycle_result)

        return cycle_result

    def _update_state(self, updates):
        """更新状态"""
        state = self._load_state()
        state.update(updates)
        self._save_state(state)

    def _save_to_history(self, result):
        """保存到历史记录"""
        history = []
        try:
            if self.history_file.exists():
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
        except:
            pass

        history.append(result)
        # 保留最近 100 条
        history = history[-100:]

        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

    def run_loop_interactive(self, mode="full"):
        """
        交互式运行闭环
        modes: full, discovery_only, evaluation_only, execution_only, learning_only
        """
        if mode == "full":
            return self.run_full_loop()
        elif mode == "discovery":
            if not self.idea_generator:
                return {"error": "idea_generator not loaded"}
            ideas = self.idea_generator.generate_evolution_ideas(count=3)
            return {"phase": "discovery", "ideas": ideas}
        elif mode == "evaluation":
            if not self.idea_generator or not self.idea_execution:
                return {"error": "modules not loaded"}
            ideas = self.idea_generator.generate_evolution_ideas()
            evaluated = []
            for idea in ideas:
                result = self.idea_execution.execute_idea(idea, dry_run=True)
                evaluated.append({"idea": idea, "evaluation": result})
            return {"phase": "evaluation", "results": evaluated}
        elif mode == "execution":
            if not self.execution_enhancer:
                return {"error": "execution_enhancer not loaded"}
            result = self.execution_enhancer.execute_evolution_cycle()
            return {"phase": "execution", "result": result}
        elif mode == "learning":
            if not self.learning_enhancer:
                return {"error": "learning_enhancer not loaded"}
            analysis = self.learning_enhancer.analyze_evolution_results()
            optimization = self.learning_enhancer.optimize_strategy()
            return {"phase": "learning", "analysis": analysis, "optimization": optimization}
        else:
            return {"error": f"Unknown mode: {mode}"}

    def get_history(self, limit=10):
        """获取闭环执行历史"""
        history = []
        try:
            if self.history_file.exists():
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
        except:
            pass
        return history[-limit:] if limit else history

    def analyze_integration(self):
        """分析集成效果"""
        state = self._load_state()
        history = self.get_history(limit=10)

        total_runs = len(history)
        successful_runs = sum(1 for h in history if h.get("success", False))

        # 分析各阶段成功率
        phase_stats = {}
        for h in history:
            for phase, data in h.get("phases", {}).items():
                if phase not in phase_stats:
                    phase_stats[phase] = {"success": 0, "total": 0}
                phase_stats[phase]["total"] += 1
                if data.get("status") in ["success", "dry_run", "partial"]:
                    phase_stats[phase]["success"] += 1

        return {
            "total_runs": total_runs,
            "successful_runs": successful_runs,
            "success_rate": successful_runs / total_runs if total_runs > 0 else 0,
            "phase_stats": phase_stats,
            "current_state": state
        }


def main():
    """命令行入口"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python evolution闭环_complete_integrator.py status")
        print("  python evolution闭环_complete_integrator.py run [full|discovery|evaluation|execution|learning]")
        print("  python evolution闭环_complete_integrator.py history [limit]")
        print("  python evolution闭环_complete_integrator.py analyze")
        return

    integrator = EvolutionLoopCompleteIntegrator()
    cmd = sys.argv[1]

    if cmd == "status":
        result = integrator.status()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif cmd == "run":
        mode = sys.argv[2] if len(sys.argv) > 2 else "full"
        result = integrator.run_loop_interactive(mode)
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    elif cmd == "history":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        result = integrator.get_history(limit)
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    elif cmd == "analyze":
        result = integrator.analyze_integration()
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    else:
        print(f"Unknown command: {cmd}")


if __name__ == "__main__":
    main()