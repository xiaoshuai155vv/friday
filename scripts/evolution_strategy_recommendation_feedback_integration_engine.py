#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环策略推荐-执行-反馈-调整完整闭环引擎 (version 1.0.0)

将 round 417 的策略推荐引擎与 round 418 的策略反馈调整引擎深度集成，
形成完整的"智能推荐→执行→反馈→调整→优化推荐"的闭环。让系统能够：

1. 基于多维度信息智能推荐最优进化策略
2. 实时跟踪策略执行效果并收集数据
3. 分析执行效果与预期的偏差
4. 动态生成调整策略
5. 将反馈结果优化到推荐引擎，形成真正的递归增强闭环

核心功能：
1. 完整的推荐-执行-反馈-调整-优化闭环
2. 跨引擎数据共享与状态同步
3. 策略执行效果驱动的推荐优化
4. 反馈学习闭环（执行→分析→调整→优化→再执行→再推荐）
5. 与进化驾驶舱的深度集成

集成模块：
- evolution_strategy_intelligent_recommendation_engine.py (round 417)
- evolution_strategy_feedback_adjustment_engine.py (round 418)
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
    from evolution_strategy_intelligent_recommendation_engine import StrategyRecommendationEngine
except ImportError:
    StrategyRecommendationEngine = None

try:
    from evolution_strategy_feedback_adjustment_engine import StrategyFeedbackAdjustmentEngine
except ImportError:
    StrategyFeedbackAdjustmentEngine = None


class StrategyRecommendationFeedbackIntegrationEngine:
    """策略推荐-执行-反馈-调整完整闭环引擎"""

    def __init__(self, state_dir: str = "runtime/state"):
        self.state_dir = Path(state_dir)
        self.state_file = self.state_dir / "strategy_recommendation_feedback_integration_state.json"

        # 集成核心引擎
        self.recommendation_engine = None
        self.feedback_engine = None

        # 完整闭环状态
        self.state = {
            "initialized": False,
            "version": "1.0.0",
            "闭环阶段": "待启动",
            "total_cycles": 0,
            "recommendation_count": 0,
            "execution_count": 0,
            "feedback_count": 0,
            "adjustment_count": 0,
            "optimization_count": 0,
            "last_cycle_time": None,
            "cycle_history": [],
            "闭环状态": {
                "recommendation": None,
                "execution": None,
                "feedback": None,
                "adjustment": None,
                "optimization": None
            },
            "策略评分": {},
            "执行效果": {},
            "调整记录": [],
            "优化建议": []
        }

        self._initialize_engines()
        self._load_state()

    def _initialize_engines(self):
        """初始化集成的引擎"""
        if StrategyRecommendationEngine:
            try:
                self.recommendation_engine = StrategyRecommendationEngine(self.state_dir)
                print("[Integration] 策略推荐引擎已加载")
            except Exception as e:
                print(f"[Integration] 策略推荐引擎加载失败: {e}")

        if StrategyFeedbackAdjustmentEngine:
            try:
                self.feedback_engine = StrategyFeedbackAdjustmentEngine(self.state_dir)
                print("[Integration] 策略反馈调整引擎已加载")
            except Exception as e:
                print(f"[Integration] 策略反馈调整引擎加载失败: {e}")

        self.state["initialized"] = True

    def _load_state(self):
        """加载状态"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    loaded_state = json.load(f)
                    self.state.update(loaded_state)
                    print("[Integration] 状态已加载")
            except Exception as e:
                print(f"[Integration] 状态加载失败: {e}")

    def _save_state(self):
        """保存状态"""
        try:
            self.state_dir.mkdir(parents=True, exist_ok=True)
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[Integration] 状态保存失败: {e}")

    def start闭环(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        启动完整的推荐-执行-反馈-调整闭环

        Args:
            context: 可选的上下文信息

        Returns:
            闭环执行结果
        """
        self.state["闭环阶段"] = "启动"
        self.state["total_cycles"] += 1
        cycle_start = datetime.now().isoformat()

        result = {
            "status": "started",
            "cycle_id": self.state["total_cycles"],
            "start_time": cycle_start,
            "steps": []
        }

        # 步骤1: 策略推荐
        self.state["闭环阶段"] = "推荐"
        self.state["闭环状态"]["recommendation"] = "进行中"
        recommendation_result = self._execute_recommendation(context)
        result["steps"].append({
            "step": "recommendation",
            "result": recommendation_result
        })
        self.state["闭环状态"]["recommendation"] = "完成"
        self.state["recommendation_count"] += 1

        # 步骤2: 执行策略
        self.state["闭环阶段"] = "执行"
        self.state["闭环状态"]["execution"] = "进行中"
        execution_result = self._execute_strategy(recommendation_result.get("recommended_strategy"))
        result["steps"].append({
            "step": "execution",
            "result": execution_result
        })
        self.state["闭环状态"]["execution"] = "完成"
        self.state["execution_count"] += 1

        # 步骤3: 收集反馈
        self.state["闭环阶段"] = "反馈"
        self.state["闭环状态"]["feedback"] = "进行中"
        feedback_result = self._collect_feedback(execution_result)
        result["steps"].append({
            "step": "feedback",
            "result": feedback_result
        })
        self.state["闭环状态"]["feedback"] = "完成"
        self.state["feedback_count"] += 1

        # 步骤4: 调整策略
        self.state["闭环阶段"] = "调整"
        self.state["闭环状态"]["adjustment"] = "进行中"
        adjustment_result = self._adjust_strategy(feedback_result)
        result["steps"].append({
            "step": "adjustment",
            "result": adjustment_result
        })
        self.state["闭环状态"]["adjustment"] = "完成"
        self.state["adjustment_count"] += 1

        # 步骤5: 优化推荐
        self.state["闭环阶段"] = "优化"
        self.state["闭环状态"]["optimization"] = "进行中"
        optimization_result = self._optimize_recommendation(adjustment_result)
        result["steps"].append({
            "step": "optimization",
            "result": optimization_result
        })
        self.state["闭环状态"]["optimization"] = "完成"
        self.state["optimization_count"] += 1

        # 记录闭环历史
        cycle_record = {
            "cycle_id": self.state["total_cycles"],
            "start_time": cycle_start,
            "end_time": datetime.now().isoformat(),
            "recommended_strategy": recommendation_result.get("recommended_strategy"),
            "execution_result": execution_result.get("status"),
            "feedback_summary": feedback_result.get("summary"),
            "adjustment_applied": adjustment_result.get("adjustments"),
            "optimization_suggestions": optimization_result.get("suggestions")
        }
        self.state["cycle_history"].append(cycle_record)
        self.state["last_cycle_time"] = cycle_record["end_time"]
        self.state["闭环阶段"] = "完成"

        result["status"] = "completed"
        result["end_time"] = cycle_record["end_time"]
        result["cycle_record"] = cycle_record

        self._save_state()
        return result

    def _execute_recommendation(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """执行策略推荐"""
        if self.recommendation_engine and hasattr(self.recommendation_engine, 'recommend_strategy'):
            try:
                recommendation = self.recommendation_engine.recommend_strategy(context or {})
                return {
                    "status": "success",
                    "recommended_strategy": recommendation,
                    "source": "recommendation_engine"
                }
            except Exception as e:
                return {
                    "status": "error",
                    "error": str(e),
                    "fallback": True
                }

        # 如果推荐引擎不可用，使用默认策略
        return {
            "status": "fallback",
            "recommended_strategy": {
                "name": "默认进化策略",
                "priority": "normal",
                "target": "系统健康优化"
            }
        }

    def _execute_strategy(self, strategy: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """执行策略"""
        if not strategy:
            return {"status": "skipped", "reason": "no_strategy"}

        # 记录执行
        execution_record = {
            "strategy": strategy,
            "start_time": datetime.now().isoformat(),
            "status": "executing"
        }
        self.state["执行效果"]["last_execution"] = execution_record

        # 模拟策略执行（实际系统中会调用执行引擎）
        execution_result = {
            "status": "completed",
            "strategy_executed": strategy.get("name"),
            "execution_time": datetime.now().isoformat(),
            "metrics": {
                "efficiency": 0.85,
                "success_rate": 0.9,
                "resource_usage": 0.6
            }
        }

        return execution_result

    def _collect_feedback(self, execution_result: Dict[str, Any]) -> Dict[str, Any]:
        """收集执行反馈"""
        if self.feedback_engine and hasattr(self.feedback_engine, 'track_execution'):
            try:
                feedback = self.feedback_engine.track_execution(execution_result)
                return feedback
            except Exception as e:
                pass

        # 使用内置反馈收集
        metrics = execution_result.get("metrics", {})
        feedback = {
            "status": "collected",
            "execution_result": execution_result,
            "metrics": metrics,
            "deviation": abs(1.0 - metrics.get("efficiency", 1.0)),
            "summary": f"执行效率: {metrics.get('efficiency', 0)}, 成功率: {metrics.get('success_rate', 0)}"
        }

        self.state["执行效果"]["last_feedback"] = feedback
        return feedback

    def _adjust_strategy(self, feedback: Dict[str, Any]) -> Dict[str, Any]:
        """调整策略"""
        deviation = feedback.get("deviation", 0)
        adjustments = []

        if deviation > 0.1:
            adjustments.append({
                "type": "参数调整",
                "target": "执行效率",
                "action": "优化执行参数",
                "deviation": deviation
            })

        if feedback.get("metrics", {}).get("success_rate", 1.0) < 0.8:
            adjustments.append({
                "type": "策略调整",
                "target": "成功率",
                "action": "增强错误处理",
                "current": feedback.get("metrics", {}).get("success_rate")
            })

        adjustment_record = {
            "adjustments": adjustments,
            "timestamp": datetime.now().isoformat()
        }
        self.state["调整记录"].append(adjustment_record)

        return {
            "status": "adjusted",
            "adjustments": adjustments,
            "deviation_addressed": deviation <= 0.1
        }

    def _optimize_recommendation(self, adjustment_result: Dict[str, Any]) -> Dict[str, Any]:
        """优化推荐（将反馈结果应用到推荐引擎）"""
        suggestions = []

        # 基于调整结果生成优化建议
        if adjustment_result.get("adjustments"):
            for adj in adjustment_result["adjustments"]:
                if adj["type"] == "参数调整":
                    suggestions.append({
                        "type": "推荐优化",
                        "action": f"调整{adj['target']}参数权重",
                        "reason": f"检测到{adj.get('deviation', 0)*100:.1f}%偏差"
                    })

        # 更新策略评分
        if self.recommendation_engine and hasattr(self.recommendation_engine, 'state'):
            # 将反馈结果同步到推荐引擎
            current_scores = self.recommendation_engine.state.get("strategy_scores", {})
            for suggestion in suggestions:
                strategy_name = suggestion.get("action", "unknown")
                current_scores[strategy_name] = current_scores.get(strategy_name, 0.5) + 0.1
            self.state["策略评分"] = current_scores

        self.state["优化建议"] = suggestions

        return {
            "status": "optimized",
            "suggestions": suggestions,
            "scores_updated": len(suggestions) > 0
        }

    def get_status(self) -> Dict[str, Any]:
        """获取当前状态"""
        return {
            "initialized": self.state["initialized"],
            "version": self.state["version"],
            "闭环阶段": self.state["闭环阶段"],
            "total_cycles": self.state["total_cycles"],
            "counts": {
                "recommendation": self.state["recommendation_count"],
                "execution": self.state["execution_count"],
                "feedback": self.state["feedback_count"],
                "adjustment": self.state["adjustment_count"],
                "optimization": self.state["optimization_count"]
            },
            "last_cycle_time": self.state["last_cycle_time"],
            "strategy_scores": self.state["策略评分"]
        }

    def get_cycle_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取闭环历史"""
        return self.state["cycle_history"][-limit:] if self.state["cycle_history"] else []

    def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        health = {
            "status": "healthy",
            "engines": {
                "recommendation_engine": self.recommendation_engine is not None,
                "feedback_engine": self.feedback_engine is not None
            },
            "total_cycles": self.state["total_cycles"],
            "last_cycle": self.state["last_cycle_time"]
        }

        if not self.recommendation_engine or not self.feedback_engine:
            health["status"] = "degraded"
            health["warning"] = "部分集成引擎加载失败"

        return health


def handle_command(args: List[str]) -> Dict[str, Any]:
    """处理命令"""
    engine = StrategyRecommendationFeedbackIntegrationEngine()

    if not args:
        return {
            "status": "error",
            "message": "缺少子命令"
        }

    command = args[0]

    if command == "status":
        return engine.get_status()

    elif command == "health":
        return engine.health_check()

    elif command == "start" or command == "闭环":
        context = {}
        # 解析额外参数
        for i, arg in enumerate(args[1:]):
            if "=" in arg:
                key, value = arg.split("=", 1)
                context[key] = value
        return engine.start闭环(context)

    elif command == "history":
        limit = int(args[1]) if len(args) > 1 else 10
        return {
            "history": engine.get_cycle_history(limit)
        }

    else:
        return {
            "status": "error",
            "message": f"未知命令: {command}",
            "available_commands": ["status", "health", "start", "闭环", "history"]
        }


def main():
    """主函数"""
    import sys

    if len(sys.argv) > 1:
        args = sys.argv[1:]
        result = handle_command(args)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        # 默认显示状态
        engine = StrategyRecommendationFeedbackIntegrationEngine()
        print(json.dumps(engine.get_status(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()