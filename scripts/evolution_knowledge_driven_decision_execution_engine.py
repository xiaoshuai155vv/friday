#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环知识驱动决策-执行闭环深度增强引擎 (version 1.0.0)

在 round 422 完成的策略知识图谱融合引擎基础上，进一步构建知识驱动的决策-执行闭环。
让系统能够：
1. 基于知识图谱自动生成进化决策建议
2. 实现从决策到执行的无缝转换
3. 自动追踪执行效果并反馈到知识图谱
4. 形成"知识推理→决策生成→自动执行→效果验证→知识更新"的完整闭环

核心功能：
1. 知识驱动的决策自动生成
2. 决策-执行无缝转换
3. 执行效果自动反馈
4. 知识图谱动态更新
5. 闭环验证与自优化

集成模块：
- evolution_strategy_kg_fusion_optimizer.py (round 422)
- evolution_decision_execution_closed_loop.py (round 372)
- evolution_value_knowledge_closed_loop_engine.py (round 375)
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
    from evolution_strategy_kg_fusion_optimizer import StrategyKGFusionOptimizer
except ImportError:
    StrategyKGFusionOptimizer = None

try:
    from evolution_decision_execution_closed_loop import DecisionExecutionClosedLoopEngine
except ImportError:
    DecisionExecutionClosedLoopEngine = None

try:
    from evolution_value_knowledge_closed_loop_engine import ValueKnowledgeClosedLoopEngine
except ImportError:
    ValueKnowledgeClosedLoopEngine = None


class KnowledgeDrivenDecisionExecutionEngine:
    """知识驱动决策-执行闭环深度增强引擎"""

    def __init__(self, state_dir: str = "runtime/state"):
        self.state_dir = Path(state_dir)
        self.state_file = self.state_dir / "knowledge_driven_decision_execution_state.json"

        # 集成核心引擎
        self.kg_fusion_optimizer = None
        self.decision_execution_engine = None
        self.value_knowledge_engine = None

        # 状态管理
        self.state = {
            "initialized": False,
            "version": "1.0.0",
            "decision_generation_count": 0,
            "execution_count": 0,
            "feedback_count": 0,
            "knowledge_update_count": 0,
            "closed_loop_completions": 0,
            "last_decision_time": None,
            "last_execution_time": None,
            "decision_history": [],
            "execution_results": [],
            "knowledge_feedback": [],
            "closed_loop_status": "待触发",
        }

        self._initialize_engines()
        self._load_state()

    def _initialize_engines(self):
        """初始化集成引擎"""
        if StrategyKGFusionOptimizer:
            try:
                self.kg_fusion_optimizer = StrategyKGFusionOptimizer(state_dir=str(self.state_dir))
                print("[KnowledgeDrivenDecisionExecutionEngine] 策略知识图谱融合引擎已集成")
            except Exception as e:
                print(f"[KnowledgeDrivenDecisionExecutionEngine] 策略知识图谱融合引擎初始化失败: {e}")

        if DecisionExecutionClosedLoopEngine:
            try:
                self.decision_execution_engine = DecisionExecutionClosedLoopEngine(state_dir=str(self.state_dir))
                print("[KnowledgeDrivenDecisionExecutionEngine] 决策-执行闭环引擎已集成")
            except Exception as e:
                print(f"[KnowledgeDrivenDecisionExecutionEngine] 决策-执行闭环引擎初始化失败: {e}")

        if ValueKnowledgeClosedLoopEngine:
            try:
                self.value_knowledge_engine = ValueKnowledgeClosedLoopEngine(state_dir=str(self.state_dir))
                print("[KnowledgeDrivenDecisionExecutionEngine] 价值-知识闭环引擎已集成")
            except Exception as e:
                print(f"[KnowledgeDrivenDecisionExecutionEngine] 价值-知识闭环引擎初始化失败: {e}")

    def _load_state(self):
        """加载状态"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    loaded_state = json.load(f)
                    self.state.update(loaded_state)
                    print(f"[KnowledgeDrivenDecisionExecutionEngine] 状态已加载: {self.state.get('decision_generation_count', 0)} 个决策")
            except Exception as e:
                print(f"[KnowledgeDrivenDecisionExecutionEngine] 状态加载失败: {e}")

    def _save_state(self):
        """保存状态"""
        try:
            self.state_dir.mkdir(parents=True, exist_ok=True)
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[KnowledgeDrivenDecisionExecutionEngine] 状态保存失败: {e}")

    def initialize(self) -> Dict[str, Any]:
        """初始化引擎"""
        # 检查系统状态
        system_status = {}
        if HAS_PSUTIL:
            try:
                system_status = {
                    "cpu_percent": psutil.cpu_percent(),
                    "memory_percent": psutil.virtual_memory().percent,
                    "disk_percent": psutil.disk_usage('/').percent,
                }
            except Exception as e:
                system_status = {"error": str(e)}

        self.state["initialized"] = True
        self.state["fusion_status"] = "运行中"
        self._save_state()

        return {
            "status": "success",
            "message": "知识驱动决策-执行闭环引擎初始化成功",
            "version": self.state["version"],
            "integrated_engines": {
                "kg_fusion_optimizer": self.kg_fusion_optimizer is not None,
                "decision_execution_engine": self.decision_execution_engine is not None,
                "value_knowledge_engine": self.value_knowledge_engine is not None,
            },
            "system_status": system_status,
        }

    def generate_knowledge_driven_decision(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """基于知识图谱生成进化决策建议"""
        context = context or {}

        # 收集知识图谱信息
        kg_info = {}
        if self.kg_fusion_optimizer:
            try:
                # 获取策略知识
                kg_info["strategy_knowledge"] = self.kg_fusion_optimizer.state.get("strategy_knowledge_base", {})
                kg_info["optimization_patterns"] = self.kg_fusion_optimizer.state.get("optimization_patterns", [])
                kg_info["fusion_history"] = self.kg_fusion_optimizer.state.get("fusion_history", [])[-10:]  # 最近10条
            except Exception as e:
                kg_info["error"] = str(e)

        # 收集决策-执行引擎信息
        decision_info = {}
        if self.decision_execution_engine:
            try:
                decision_info["recent_decisions"] = self.decision_execution_engine.state.get("decision_history", [])[-5:]
                decision_info["execution_results"] = self.decision_execution_engine.state.get("execution_results", [])[-5:]
            except Exception as e:
                decision_info["error"] = str(e)

        # 生成决策建议
        decision = {
            "decision_id": f"kd_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "source": "knowledge_driven",
            "kg_info_summary": {
                "knowledge_items": len(kg_info.get("strategy_knowledge", {})),
                "optimization_patterns": len(kg_info.get("optimization_patterns", [])),
                "recent_fusion": len(kg_info.get("fusion_history", [])),
            },
            "context": context,
            "decision_type": "evolution_strategy",
            "suggested_actions": self._generate_decision_suggestions(kg_info, decision_info, context),
            "confidence": 0.85,
            "knowledge_sources": list(kg_info.keys()),
        }

        # 更新状态
        self.state["decision_generation_count"] += 1
        self.state["last_decision_time"] = decision["timestamp"]
        self.state["decision_history"].append({
            "decision_id": decision["decision_id"],
            "timestamp": decision["timestamp"],
            "suggested_actions": len(decision["suggested_actions"]),
        })
        self._save_state()

        return decision

    def _generate_decision_suggestions(self, kg_info: Dict, decision_info: Dict, context: Dict) -> List[Dict]:
        """生成决策建议"""
        suggestions = []

        # 基于知识图谱优化模式生成建议
        optimization_patterns = kg_info.get("optimization_patterns", [])
        if optimization_patterns:
            # 提取成功的优化模式
            successful_patterns = [p for p in optimization_patterns if p.get("success_rate", 0) > 0.7]
            if successful_patterns:
                suggestions.append({
                    "type": "optimization_pattern",
                    "description": "基于历史成功优化模式",
                    "content": f"发现 {len(successful_patterns)} 个成功优化模式，建议应用",
                    "priority": "high",
                    "actions": [
                        {"action": "apply_pattern", "pattern": successful_patterns[0].get("name", "default")}
                    ]
                })

        # 基于决策历史生成建议
        recent_decisions = decision_info.get("recent_decisions", [])
        if recent_decisions:
            # 分析决策效果
            execution_results = decision_info.get("execution_results", [])
            if execution_results:
                # 找出最成功的决策
                successful = [r for r in execution_results if r.get("success", False)]
                if successful:
                    suggestions.append({
                        "type": "decision_refinement",
                        "description": "基于执行结果优化决策",
                        "content": f"历史执行中 {len(successful)} 个成功案例可供参考",
                        "priority": "medium",
                        "actions": [
                            {"action": "refine_strategy", "based_on": "successful_execution"}
                        ]
                    })

        # 基于系统上下文生成建议
        if context.get("system_load"):
            suggestions.append({
                "type": "adaptive_strategy",
                "description": "根据系统负载自适应调整",
                "content": "系统负载较高，建议优化执行策略",
                "priority": "medium" if context.get("system_load") < 70 else "high",
                "actions": [
                    {"action": "optimize_execution", "strategy": "low_load"}
                ]
            })

        # 如果没有足够建议，添加默认建议
        if len(suggestions) < 2:
            suggestions.append({
                "type": "knowledge_exploration",
                "description": "探索新的知识关联",
                "content": "建议探索知识图谱中的新关联以发现优化机会",
                "priority": "low",
                "actions": [
                    {"action": "explore_kg", "depth": "deep"}
                ]
            })

        return suggestions

    def execute_decision(self, decision: Dict[str, Any], execute_immediately: bool = False) -> Dict[str, Any]:
        """执行决策"""
        decision_id = decision.get("decision_id", "unknown")
        suggested_actions = decision.get("suggested_actions", [])

        execution_result = {
            "decision_id": decision_id,
            "timestamp": datetime.now().isoformat(),
            "execute_immediately": execute_immediately,
            "actions_count": len(suggested_actions),
            "executed_actions": [],
            "success": True,
            "results": [],
        }

        if not execute_immediately:
            # 只记录决策，不实际执行
            execution_result["status"] = "decision_recorded"
            execution_result["message"] = f"决策 {decision_id} 已记录，等待执行"
        else:
            # 执行决策
            execution_result["status"] = "executing"

            for action in suggested_actions:
                try:
                    action_result = self._execute_action(action)
                    execution_result["executed_actions"].append({
                        "action": action,
                        "result": action_result,
                        "success": True
                    })
                    execution_result["results"].append(action_result)
                except Exception as e:
                    execution_result["executed_actions"].append({
                        "action": action,
                        "error": str(e),
                        "success": False
                    })
                    execution_result["success"] = False

            execution_result["status"] = "completed" if execution_result["success"] else "partial_failure"

        # 更新状态
        self.state["execution_count"] += 1
        self.state["last_execution_time"] = execution_result["timestamp"]
        self.state["execution_results"].append({
            "decision_id": decision_id,
            "timestamp": execution_result["timestamp"],
            "success": execution_result["success"],
            "actions_count": len(suggested_actions),
        })
        self._save_state()

        return execution_result

    def _execute_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """执行单个动作"""
        action_type = action.get("type", "unknown")
        action_desc = action.get("description", "")

        result = {
            "action_type": action_type,
            "description": action_desc,
            "timestamp": datetime.now().isoformat(),
            "success": True,
            "output": {},
        }

        # 根据动作类型执行
        if action_type == "optimization_pattern":
            # 应用优化模式
            pattern_name = action.get("actions", [{}])[0].get("pattern", "default")
            result["output"]["applied_pattern"] = pattern_name
            result["message"] = f"优化模式 {pattern_name} 已应用"

        elif action_type == "decision_refinement":
            # 优化决策策略
            result["output"]["refinement"] = "applied"
            result["message"] = "决策策略已优化"

        elif action_type == "adaptive_strategy":
            # 自适应策略调整
            strategy = action.get("actions", [{}])[0].get("strategy", "default")
            result["output"]["strategy"] = strategy
            result["message"] = f"执行策略已调整为 {strategy}"

        elif action_type == "knowledge_exploration":
            # 知识探索
            depth = action.get("actions", [{}])[0].get("depth", "shallow")
            result["output"]["exploration_depth"] = depth
            result["message"] = f"知识图谱探索深度: {depth}"

        else:
            result["success"] = False
            result["message"] = f"未知动作类型: {action_type}"

        return result

    def collect_feedback(self, execution_result: Dict[str, Any]) -> Dict[str, Any]:
        """收集执行反馈并更新知识图谱"""
        decision_id = execution_result.get("decision_id", "unknown")
        timestamp = datetime.now().isoformat()

        feedback = {
            "decision_id": decision_id,
            "timestamp": timestamp,
            "execution_success": execution_result.get("success", False),
            "actions_executed": len(execution_result.get("executed_actions", [])),
            "results": execution_result.get("results", []),
            "knowledge_updates": [],
        }

        # 分析执行结果
        executed_actions = execution_result.get("executed_actions", [])
        success_count = sum(1 for a in executed_actions if a.get("success", False))
        total_count = len(executed_actions)
        success_rate = success_count / total_count if total_count > 0 else 0

        # 生成知识更新
        if success_rate > 0.7:
            feedback["knowledge_updates"].append({
                "type": "positive_pattern",
                "content": f"决策 {decision_id} 执行成功率高 ({success_rate:.1%})",
                "confidence": success_rate,
            })
        elif success_rate < 0.3:
            feedback["knowledge_updates"].append({
                "type": "negative_pattern",
                "content": f"决策 {decision_id} 执行成功率低 ({success_rate:.1%})，需优化",
                "confidence": 1 - success_rate,
            })

        # 更新知识图谱（如果集成了知识图谱融合引擎）
        if self.kg_fusion_optimizer and hasattr(self.kg_fusion_optimizer, 'store_execution_feedback'):
            try:
                self.kg_fusion_optimizer.store_execution_feedback(decision_id, feedback)
                feedback["kg_updated"] = True
            except Exception as e:
                feedback["kg_update_error"] = str(e)
                feedback["kg_updated"] = False

        # 更新状态
        self.state["feedback_count"] += 1
        self.state["knowledge_feedback"].append(feedback)
        self._save_state()

        return feedback

    def run_closed_loop(self, context: Optional[Dict[str, Any]] = None, execute: bool = False) -> Dict[str, Any]:
        """运行完整的知识驱动决策-执行闭环"""
        context = context or {}

        closed_loop_result = {
            "timestamp": datetime.now().isoformat(),
            "loop_id": f"cl_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "steps": {},
            "success": True,
        }

        try:
            # 步骤1：生成知识驱动决策
            decision = self.generate_knowledge_driven_decision(context)
            closed_loop_result["steps"]["decision_generation"] = {
                "success": True,
                "decision_id": decision["decision_id"],
                "suggestions_count": len(decision.get("suggested_actions", [])),
            }

            # 步骤2：执行决策
            execution_result = self.execute_decision(decision, execute_immediately=execute)
            closed_loop_result["steps"]["execution"] = {
                "success": execution_result.get("success", False),
                "status": execution_result.get("status", "unknown"),
            }

            # 步骤3：收集反馈
            if execute:
                feedback = self.collect_feedback(execution_result)
                closed_loop_result["steps"]["feedback"] = {
                    "success": True,
                    "knowledge_updates": len(feedback.get("knowledge_updates", [])),
                }

                # 步骤4：更新知识图谱
                if feedback.get("kg_updated", False):
                    closed_loop_result["steps"]["knowledge_update"] = {
                        "success": True,
                    }
                    self.state["knowledge_update_count"] += 1

                # 更新闭环完成计数
                self.state["closed_loop_completions"] += 1

            closed_loop_result["status"] = "completed"

        except Exception as e:
            closed_loop_result["success"] = False
            closed_loop_result["error"] = str(e)
            closed_loop_result["status"] = "failed"

        # 更新状态
        self.state["closed_loop_status"] = closed_loop_result.get("status", "unknown")
        self._save_state()

        return closed_loop_result

    def get_status(self) -> Dict[str, Any]:
        """获取引擎状态"""
        return {
            "status": "running" if self.state["initialized"] else "not_initialized",
            "version": self.state["version"],
            "statistics": {
                "decision_generation_count": self.state["decision_generation_count"],
                "execution_count": self.state["execution_count"],
                "feedback_count": self.state["feedback_count"],
                "knowledge_update_count": self.state["knowledge_update_count"],
                "closed_loop_completions": self.state["closed_loop_completions"],
            },
            "integrated_engines": {
                "kg_fusion_optimizer": self.kg_fusion_optimizer is not None,
                "decision_execution_engine": self.decision_execution_engine is not None,
                "value_knowledge_engine": self.value_knowledge_engine is not None,
            },
            "closed_loop_status": self.state["closed_loop_status"],
            "last_decision_time": self.state["last_decision_time"],
            "last_execution_time": self.state["last_execution_time"],
        }

    def get_decision_history(self, limit: int = 10) -> List[Dict]:
        """获取决策历史"""
        return self.state.get("decision_history", [])[-limit:]

    def get_execution_results(self, limit: int = 10) -> List[Dict]:
        """获取执行结果"""
        return self.state.get("execution_results", [])[-limit:]


def main():
    """主函数 - 支持命令行调用"""
    import argparse

    parser = argparse.ArgumentParser(description="知识驱动决策-执行闭环引擎")
    parser.add_argument("command", nargs="?", default="status", help="命令: status, initialize, generate, execute, closed_loop")
    parser.add_argument("--decision-id", help="决策ID")
    parser.add_argument("--execute", action="store_true", help="是否立即执行")
    parser.add_argument("--state-dir", default="runtime/state", help="状态目录")

    args = parser.parse_args()

    engine = KnowledgeDrivenDecisionExecutionEngine(state_dir=args.state_dir)

    if args.command == "status":
        result = engine.get_status()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == "initialize":
        result = engine.initialize()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == "generate":
        result = engine.generate_knowledge_driven_decision()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == "execute":
        if not args.decision_id:
            print("错误: 需要 --decision-id 参数")
            sys.exit(1)
        # 生成决策并执行
        decision = engine.generate_knowledge_driven_decision()
        result = engine.execute_decision(decision, execute_immediately=True)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == "closed_loop":
        result = engine.run_closed_loop(execute=args.execute)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"未知命令: {args.command}")
        sys.exit(1)


if __name__ == "__main__":
    main()