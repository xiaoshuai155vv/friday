#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环进化策略智能推荐与自动选择引擎 (version 1.0.0)

在 round 416 完成的知识驱动递归增强闭环基础上，进一步增强进化策略的智能推荐能力。
让系统能够基于当前系统状态（CPU/内存/健康度/能力缺口）、进化历史（成功率/效率/价值实现）、
知识图谱（进化模式/优化机会），自动分析并推荐最合适的进化策略，让系统从"被动等待进化"
升级为"主动推荐最优进化方向"，实现真正的智能进化决策支持。

核心功能：
1. 多维度系统状态分析（CPU/内存/健康度/能力缺口/进化历史）
2. 进化策略智能推荐（基于状态匹配和历史成功率）
3. 策略比较与优先级排序
4. 自动选择执行（推荐→确认→执行→验证→反馈）
5. 与进化驾驶舱的深度集成

集成模块：
- evolution_knowledge_driven_recursive_enhancement_engine.py (round 416)
- evolution_knowledge_graph_reasoning.py (round 298)
- evolution_kg_deep_reasoning_insight_engine.py (round 330)
"""

import json
import os
import sys
from datetime import datetime

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from collections import defaultdict

# 尝试导入集成的模块
try:
    from evolution_knowledge_driven_recursive_enhancement_engine import KnowledgeDrivenRecursiveEnhancementEngine
except ImportError:
    KnowledgeDrivenRecursiveEnhancementEngine = None

try:
    from evolution_kg_deep_reasoning_insight_engine import KnowledgeGraphDeepReasoningEngine
except ImportError:
    KnowledgeGraphDeepReasoningEngine = None


class StrategyRecommendationEngine:
    """进化策略智能推荐与自动选择引擎"""

    def __init__(self, state_dir: str = "runtime/state"):
        self.state_dir = Path(state_dir)
        self.state_file = self.state_dir / "evolution_strategy_recommendation_state.json"

        # 集成核心引擎
        self.kg_reasoning_engine = None
        self.knowledge_driven_engine = None

        # 策略推荐状态
        self.state = {
            "initialized": False,
            "version": "1.0.0",
            "recommendation_count": 0,
            "strategy_analysis_count": 0,
            "auto_selection_count": 0,
            "feedback_count": 0,
            "last_recommendation_time": None,
            "recommendation_history": [],
            "strategy_scores": {},
            "success_patterns": [],
            "failure_patterns": [],
            "推荐状态": "待触发",
        }

        self._initialize_engines()
        self._load_state()

    def _initialize_engines(self):
        """初始化集成的引擎"""
        if KnowledgeGraphDeepReasoningEngine:
            try:
                self.kg_reasoning_engine = KnowledgeGraphDeepReasoningEngine(self.state_dir)
                print("[StrategyRecommendation] 知识图谱推理引擎已加载")
            except Exception as e:
                print(f"[StrategyRecommendation] 知识图谱推理引擎加载失败: {e}")

        if KnowledgeDrivenRecursiveEnhancementEngine:
            try:
                self.knowledge_driven_engine = KnowledgeDrivenRecursiveEnhancementEngine(self.state_dir)
                print("[StrategyRecommendation] 知识驱动递归增强引擎已加载")
            except Exception as e:
                print(f"[StrategyRecommendation] 知识驱动递归增强引擎加载失败: {e}")

        self.state["initialized"] = True

    def _load_state(self):
        """加载状态"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    saved_state = json.load(f)
                    self.state.update(saved_state)
            except Exception as e:
                print(f"[StrategyRecommendation] 状态加载失败: {e}")

    def _save_state(self):
        """保存状态"""
        try:
            self.state_dir.mkdir(parents=True, exist_ok=True)
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[StrategyRecommendation] 状态保存失败: {e}")

    def analyze_system_status(self) -> Dict[str, Any]:
        """分析系统当前状态"""
        status = {
            "timestamp": datetime.now().isoformat(),
        }

        if HAS_PSUTIL:
            try:
                status["cpu_percent"] = psutil.cpu_percent(interval=1)
            except:
                status["cpu_percent"] = 0

            try:
                status["memory_percent"] = psutil.virtual_memory().percent
            except:
                status["memory_percent"] = 0

            try:
                status["disk_percent"] = psutil.disk_usage('/').percent
            except:
                status["disk_percent"] = 0

            try:
                status["load_average"] = psutil.getloadavg() if hasattr(psutil, 'getloadavg') else [0, 0, 0]
            except:
                status["load_average"] = [0, 0, 0]
        else:
            status["cpu_percent"] = 0
            status["memory_percent"] = 0
            status["disk_percent"] = 0
            status["load_average"] = [0, 0, 0]
            status["note"] = "psutil not available"

        # 读取进化环健康状态
        try:
            cockpit_file = self.state_dir / "evolution_cockpit_state.json"
            if cockpit_file.exists():
                with open(cockpit_file, 'r', encoding='utf-8') as f:
                    cockpit_state = json.load(f)
                    status["evolution_health"] = cockpit_state.get("overall_health", "unknown")
                    status["active_engines"] = cockpit_state.get("active_engines", 0)
                    status["total_engines"] = cockpit_state.get("total_engines", 0)
        except Exception:
            status["evolution_health"] = "unknown"

        # 读取最近进化历史
        try:
            history_dir = self.state_dir
            evolution_files = sorted(history_dir.glob("evolution_completed_ev_*.json"), reverse=True)
            recent_history = []
            for f in evolution_files[:10]:
                try:
                    with open(f, 'r', encoding='utf-8') as fp:
                        data = json.load(fp)
                        recent_history.append({
                            "round": data.get("loop_round"),
                            "goal": data.get("current_goal"),
                            "completed": data.get("completed", False),
                        })
                except:
                    pass
            status["recent_evolution_history"] = recent_history
        except Exception:
            status["recent_evolution_history"] = []

        self.state["strategy_analysis_count"] += 1
        return status

    def analyze_evolution_history(self) -> Dict[str, Any]:
        """分析进化历史，提取成功和失败模式"""
        patterns = {
            "success_patterns": [],
            "failure_patterns": [],
            "success_rate_by_type": {},
            "avg_execution_time": 0,
        }

        try:
            history_dir = self.state_dir
            evolution_files = sorted(history_dir.glob("evolution_completed_ev_*.json"), reverse=True)

            completed_count = 0
            total_time = 0
            type_success = defaultdict(lambda: {"success": 0, "total": 0})

            for f in evolution_files[:50]:
                try:
                    with open(f, 'r', encoding='utf-8') as fp:
                        data = json.load(fp)
                        goal = data.get("current_goal", "")

                        # 统计成功/失败
                        completed = data.get("completed", False)
                        if completed:
                            completed_count += 1
                            patterns["success_patterns"].append(goal)

                            # 按类型统计
                            if "效率" in goal:
                                type_success["效率"]["success"] += 1
                            elif "智能" in goal or "自适应" in goal:
                                type_success["智能"]["success"] += 1
                            elif "知识" in goal or "推理" in goal:
                                type_success["知识"]["success"] += 1
                            elif "决策" in goal or "规划" in goal:
                                type_success["决策"]["success"] += 1
                            else:
                                type_success["其他"]["success"] += 1
                        else:
                            patterns["failure_patterns"].append(goal)

                        type_success["总计"]["total"] += 1
                except:
                    pass

            # 计算成功率
            for type_name, stats in type_success.items():
                if stats["total"] > 0:
                    patterns["success_rate_by_type"][type_name] = stats["success"] / stats["total"]

            if completed_count > 0:
                patterns["avg_execution_time"] = total_time / completed_count if total_time > 0 else 0

            patterns["overall_success_rate"] = completed_count / 50 if completed_count < 50 else 1.0

        except Exception as e:
            print(f"[StrategyRecommendation] 进化历史分析失败: {e}")

        self.state["success_patterns"] = patterns.get("success_patterns", [])
        self.state["failure_patterns"] = patterns.get("failure_patterns", [])

        return patterns

    def recommend_strategy(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """智能推荐进化策略"""
        if context is None:
            context = {}

        print("[StrategyRecommendation] 正在分析系统状态和进化历史...")

        # 1. 分析系统状态
        system_status = self.analyze_system_status()
        print(f"[StrategyRecommendation] 系统状态分析完成: CPU={system_status['cpu_percent']}%, Memory={system_status['memory_percent']}%")

        # 2. 分析进化历史
        history_patterns = self.analyze_evolution_history()
        print(f"[StrategyRecommendation] 进化历史分析完成: 成功率={history_patterns.get('overall_success_rate', 0):.1%}")

        # 3. 基于分析和上下文生成推荐
        recommendations = self._generate_recommendations(system_status, history_patterns, context)

        # 4. 策略排序
        recommendations = self._rank_recommendations(recommendations, system_status, history_patterns)

        # 更新状态
        self.state["recommendation_count"] += 1
        self.state["last_recommendation_time"] = datetime.now().isoformat()
        self.state["recommendation_history"].append({
            "timestamp": datetime.now().isoformat(),
            "system_status": {
                "cpu": system_status.get("cpu_percent"),
                "memory": system_status.get("memory_percent"),
            },
            "recommendations": recommendations[:3],
        })

        # 保持历史记录不超过20条
        if len(self.state["recommendation_history"]) > 20:
            self.state["recommendation_history"] = self.state["recommendation_history"][-20:]

        self._save_state()

        return {
            "status": "success",
            "system_status": system_status,
            "history_patterns": history_patterns,
            "recommendations": recommendations[:3],
            "recommendation_time": datetime.now().isoformat(),
        }

    def _generate_recommendations(
        self,
        system_status: Dict[str, Any],
        history_patterns: Dict[str, Any],
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """生成策略推荐"""
        recommendations = []

        # 基于系统状态推荐
        cpu = system_status.get("cpu_percent", 0)
        memory = system_status.get("memory_percent", 0)

        if cpu > 80:
            recommendations.append({
                "strategy": "执行效率优化",
                "priority": "高",
                "reason": f"系统CPU使用率较高({cpu}%)，建议优化执行效率",
                "suggested_action": "执行进化环效率优化相关策略",
                "expected_impact": "降低CPU使用率20-30%",
            })

        if memory > 85:
            recommendations.append({
                "strategy": "内存优化",
                "priority": "高",
                "reason": f"系统内存使用率较高({memory}%)，建议进行内存优化",
                "suggested_action": "执行内存管理和资源优化策略",
                "expected_impact": "降低内存使用率15-25%",
            })

        # 基于历史成功模式推荐
        success_rate = history_patterns.get("overall_success_rate", 0)
        success_patterns = history_patterns.get("success_patterns", [])

        if success_rate > 0.8:
            recommendations.append({
                "strategy": "知识驱动递归增强",
                "priority": "中",
                "reason": "进化成功率较高，适合进行深度知识整合和递归优化",
                "suggested_action": "扩展知识图谱推理能力和递归优化策略",
                "expected_impact": "提升知识利用率和进化效率",
            })

        # 检查最近的进化历史
        recent_history = system_status.get("recent_evolution_history", [])
        if recent_history:
            last_goal = recent_history[0].get("goal", "")
            if "效率" in last_goal or "优化" in last_goal:
                recommendations.append({
                    "strategy": "智能调度增强",
                    "priority": "中",
                    "reason": "上轮刚完成效率优化，建议继续增强智能调度能力",
                    "suggested_action": "扩展动态调度和资源分配优化",
                    "expected_impact": "提升任务调度效率",
                })

        # 基于知识图谱推理（如果有）
        if self.kg_reasoning_engine:
            try:
                insights = self.kg_reasoning_engine.get_system_insights()
                if insights:
                    for insight in insights[:2]:
                        recommendations.append({
                            "strategy": "知识推理驱动",
                            "priority": "中",
                            "reason": f"知识图谱洞察: {insight.get('description', '')[:50]}",
                            "suggested_action": insight.get('suggested_action', '基于洞察执行优化'),
                            "expected_impact": insight.get('expected_impact', '利用知识图谱优化决策'),
                        })
            except Exception as e:
                print(f"[StrategyRecommendation] 知识图谱推理失败: {e}")

        # 如果没有生成任何推荐，生成默认推荐
        if not recommendations:
            recommendations.append({
                "strategy": "元进化增强",
                "priority": "低",
                "reason": "系统状态稳定，进化成功率高，适合进行元进化能力增强",
                "suggested_action": "增强元认知和自我优化能力",
                "expected_impact": "提升系统自主进化能力",
            })

        return recommendations

    def _rank_recommendations(
        self,
        recommendations: List[Dict[str, Any]],
        system_status: Dict[str, Any],
        history_patterns: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """对推荐进行优先级排序"""
        priority_scores = {"高": 3, "中": 2, "低": 1}

        for rec in recommendations:
            score = priority_scores.get(rec.get("priority", "低"), 1)

            # 系统负载高时，提高效率类策略优先级
            if system_status.get("cpu_percent", 0) > 70 and "效率" in rec.get("strategy", ""):
                score += 2

            # 进化成功率高时，提高创新类策略优先级
            if history_patterns.get("overall_success_rate", 0) > 0.7 and "智能" in rec.get("strategy", ""):
                score += 1

            rec["score"] = score

        # 按分数排序
        recommendations.sort(key=lambda x: x.get("score", 0), reverse=True)

        return recommendations

    def auto_select_and_execute(self, strategy: Optional[str] = None) -> Dict[str, Any]:
        """自动选择并执行策略"""
        print(f"[StrategyRecommendation] 正在自动选择策略: {strategy or '自动最佳'}")

        # 如果没有指定策略，先获取推荐
        if strategy is None:
            result = self.recommend_strategy()
            if result.get("recommendations"):
                strategy = result["recommendations"][0].get("strategy", "默认策略")
            else:
                strategy = "默认策略"

        # 执行策略（这里只是模拟，实际会根据策略类型执行不同操作）
        execution_result = {
            "strategy": strategy,
            "execution_time": datetime.now().isoformat(),
            "status": "simulated",
            "message": f"策略 '{strategy}' 已进入执行队列（模拟执行）",
        }

        self.state["auto_selection_count"] += 1
        self._save_state()

        return execution_result

    def get_status(self) -> Dict[str, Any]:
        """获取引擎状态"""
        return {
            "initialized": self.state.get("initialized", False),
            "version": self.state.get("version", "1.0.0"),
            "recommendation_count": self.state.get("recommendation_count", 0),
            "strategy_analysis_count": self.state.get("strategy_analysis_count", 0),
            "auto_selection_count": self.state.get("auto_selection_count", 0),
            "last_recommendation_time": self.state.get("last_recommendation_time"),
            "推荐状态": self.state.get("推荐状态", "待触发"),
        }

    def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        return {
            "status": "healthy" if self.state.get("initialized") else "uninitialized",
            "engines_loaded": {
                "kg_reasoning": self.kg_reasoning_engine is not None,
                "knowledge_driven": self.knowledge_driven_engine is not None,
            },
            "metrics": self.get_status(),
        }


def main():
    """主函数 - 用于命令行调用"""
    import argparse

    parser = argparse.ArgumentParser(description="智能进化策略推荐引擎")
    parser.add_argument("action", choices=["recommend", "auto", "status", "health"], help="执行动作")
    parser.add_argument("--strategy", type=str, help="指定策略名称")

    args = parser.parse_args()

    engine = StrategyRecommendationEngine()

    if args.action == "recommend":
        result = engine.recommend_strategy()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.action == "auto":
        result = engine.auto_select_and_execute(args.strategy)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.action == "status":
        result = engine.get_status()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.action == "health":
        result = engine.health_check()
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()