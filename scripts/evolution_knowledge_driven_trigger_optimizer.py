#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环知识驱动自动触发与自优化引擎 (Evolution Knowledge Driven Trigger & Optimizer Engine)
version 1.0.0

让系统能够基于 round 410 蒸馏的知识，自动分析系统状态、智能识别进化方向、
自动触发相应进化引擎，并基于执行结果自优化触发策略。
实现从"积累知识"到"应用知识指导进化"的范式升级。

功能：
1. 知识自动分析 - 读取蒸馏知识，分析当前系统状态与知识的相关性
2. 进化方向识别 - 基于知识图谱和当前状态识别需要进化的方向
3. 自动触发机制 - 根据识别结果自动触发相应进化引擎
4. 自优化能力 - 基于执行结果自动优化触发策略，形成知识→分析→触发→执行→验证→优化的闭环

依赖：
- evolution_cross_engine_knowledge_distillation_engine.py (round 410)
- evolution_knowledge_graph_reasoning.py (round 298)
- evolution_cockpit_engine.py (round 350)
"""

import json
import os
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict
import re


class KnowledgeDrivenTriggerOptimizer:
    """知识驱动自动触发与自优化引擎"""

    def __init__(self, data_dir: str = "runtime/state"):
        self.data_dir = data_dir
        # 触发策略配置
        self.config = {
            "auto_trigger_enabled": True,
            "trigger_cooldown_minutes": 30,
            "min_confidence_threshold": 0.7,
            "max_triggers_per_round": 3,
            "optimization_enabled": True
        }

        # 触发历史与优化数据
        self.trigger_history = []
        self.optimization_data = {}
        self.knowledge_analysis_cache = {}

        # 加载已有数据
        self._load_trigger_history()
        self._load_optimization_data()

    def _load_trigger_history(self):
        """加载触发历史"""
        history_file = os.path.join(self.data_dir, "trigger_history.json")
        if os.path.exists(history_file):
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.trigger_history = data.get("history", [])
            except Exception as e:
                print(f"[知识触发] 警告：加载触发历史失败: {e}")

    def _save_trigger_history(self):
        """保存触发历史"""
        history_file = os.path.join(self.data_dir, "trigger_history.json")
        try:
            os.makedirs(os.path.dirname(history_file), exist_ok=True)
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "history": self.trigger_history,
                    "last_update": datetime.now().isoformat()
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[知识触发] 警告：保存触发历史失败: {e}")

    def _load_optimization_data(self):
        """加载优化数据"""
        opt_file = os.path.join(self.data_dir, "trigger_optimization.json")
        if os.path.exists(opt_file):
            try:
                with open(opt_file, 'r', encoding='utf-8') as f:
                    self.optimization_data = json.load(f)
            except Exception as e:
                print(f"[知识触发] 警告：加载优化数据失败: {e}")

    def _save_optimization_data(self):
        """保存优化数据"""
        opt_file = os.path.join(self.data_dir, "trigger_optimization.json")
        try:
            os.makedirs(os.path.dirname(opt_file), exist_ok=True)
            with open(opt_file, 'w', encoding='utf-8') as f:
                json.dump(self.optimization_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[知识触发] 警告：保存优化数据失败: {e}")

    def load_distilled_knowledge(self) -> Dict[str, Any]:
        """加载蒸馏知识"""
        knowledge_file = os.path.join(self.data_dir, "distilled_knowledge.json")
        if os.path.exists(knowledge_file):
            try:
                with open(knowledge_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"[知识触发] 警告：加载蒸馏知识失败: {e}")
        return {"knowledge": {}, "quality_scores": {}}

    def analyze_system_state(self) -> Dict[str, Any]:
        """分析当前系统状态"""
        state = {
            "loop_round": 0,
            "recent_completions": [],
            "engine_health": {},
            "capabilities": [],
            "gaps": []
        }

        # 获取当前轮次
        mission_file = os.path.join(self.data_dir, "current_mission.json")
        if os.path.exists(mission_file):
            try:
                with open(mission_file, 'r', encoding='utf-8') as f:
                    mission = json.load(f)
                    state["loop_round"] = mission.get("loop_round", 0)
            except Exception:
                pass

        # 获取最近完成的进化
        state_dir = self.data_dir
        try:
            completed_files = sorted(
                [f for f in os.listdir(state_dir) if f.startswith("evolution_completed_ev_")],
                reverse=True
            )[:5]

            for f in completed_files:
                try:
                    with open(os.path.join(state_dir, f), 'r', encoding='utf-8') as file:
                        data = json.load(file)
                        state["recent_completions"].append({
                            "round": data.get("loop_round"),
                            "goal": data.get("current_goal"),
                            "status": data.get("status")
                        })
                except Exception:
                    pass
        except Exception as e:
            print(f"[知识触发] 警告：获取最近进化失败: {e}")

        # 加载能力缺口
        gaps_file = "references/capability_gaps.md"
        if os.path.exists(gaps_file):
            try:
                with open(gaps_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # 简单提取缺口
                    for line in content.split('\n'):
                        if '已覆盖' not in line and '|' in line:
                            state["gaps"].append(line.strip())
            except Exception:
                pass

        return state

    def analyze_knowledge_relevance(self, knowledge: Dict, system_state: Dict) -> List[Dict]:
        """分析知识与系统状态的相关性"""
        relevant_knowledge = []

        knowledge_items = knowledge.get("knowledge", {})
        quality_scores = knowledge.get("quality_scores", {})

        current_round = system_state.get("loop_round", 0)
        recent_goals = [c.get("goal", "") for c in system_state.get("recent_completions", [])[:3]]

        for kid, item in knowledge_items.items():
            # 计算相关性分数
            relevance_score = quality_scores.get(kid, 0.0)

            # 基于当前轮次和最近进化调整相关性
            if item.get("type") == "evolution_success":
                # 成功的进化经验相关性高
                content = item.get("content", {})
                if isinstance(content, dict):
                    goal = content.get("goal", "")
                    if goal and goal not in recent_goals:
                        relevance_score += 0.1

            # 检查是否是最近需要的能力
            for gap in system_state.get("gaps", []):
                content_str = str(item.get("content", ""))
                if gap.lower() in content_str.lower():
                    relevance_score += 0.15

            if relevance_score >= self.config["min_confidence_threshold"]:
                relevant_knowledge.append({
                    "id": kid,
                    "type": item.get("type"),
                    "content": item.get("content"),
                    "relevance_score": min(relevance_score, 1.0),
                    "quality": quality_scores.get(kid, 0.0)
                })

        return sorted(relevant_knowledge, key=lambda x: x["relevance_score"], reverse=True)

    def identify_evolution_directions(self, relevant_knowledge: List[Dict], system_state: Dict) -> List[Dict]:
        """识别进化方向"""
        directions = []

        # 基于知识识别进化方向
        for item in relevant_knowledge[:5]:  # 最多取前5个
            direction = {
                "knowledge_id": item["id"],
                "type": item["type"],
                "relevance": item["relevance_score"],
                "suggested_action": None,
                "confidence": 0.0
            }

            # 分析知识类型，生成建议
            if item["type"] == "execution_pattern":
                direction["suggested_action"] = "优化执行策略"
                direction["confidence"] = 0.75
            elif item["type"] == "execution_insight":
                direction["suggested_action"] = "应用洞察改进"
                direction["confidence"] = 0.8
            elif item["type"] == "evolution_success":
                direction["suggested_action"] = "扩展成功模式"
                direction["confidence"] = 0.85

            directions.append(direction)

        # 基于系统状态补充进化方向
        recent_rounds = system_state.get("recent_completions", [])
        if len(recent_rounds) < 3:
            # 最近进化较少，可以建议扩展能力
            directions.append({
                "knowledge_id": "system_gap",
                "type": "capability_expansion",
                "relevance": 0.7,
                "suggested_action": "扩展系统能力",
                "confidence": 0.65
            })

        return sorted(directions, key=lambda x: x["confidence"], reverse=True)

    def generate_trigger_recommendations(self, directions: List[Dict]) -> List[Dict]:
        """生成触发推荐"""
        recommendations = []

        for direction in directions[:self.config["max_triggers_per_round"]]:
            if direction["confidence"] < self.config["min_confidence_threshold"]:
                continue

            rec = {
                "action": direction["suggested_action"],
                "reason": f"基于{direction['type']}知识，相关性{direction['relevance']:.2f}",
                "confidence": direction["confidence"],
                "priority": "high" if direction["confidence"] > 0.8 else "medium"
            }
            recommendations.append(rec)

        return recommendations

    def analyze_and_trigger(self) -> Dict[str, Any]:
        """执行知识分析并生成触发推荐"""
        print("[知识触发] 开始知识驱动的自动分析与触发...")

        result = {
            "success": False,
            "system_state": {},
            "relevant_knowledge": [],
            "directions": [],
            "recommendations": [],
            "triggered": []
        }

        # 1. 加载蒸馏知识
        knowledge = self.load_distilled_knowledge()
        print(f"[知识触发] 加载了 {len(knowledge.get('knowledge', {}))} 条蒸馏知识")

        # 2. 分析系统状态
        system_state = self.analyze_system_state()
        result["system_state"] = system_state
        print(f"[知识触发] 当前系统状态：round {system_state.get('loop_round', 0)}")

        # 3. 分析知识相关性
        relevant_knowledge = self.analyze_knowledge_relevance(knowledge, system_state)
        result["relevant_knowledge"] = relevant_knowledge
        print(f"[知识触发] 发现 {len(relevant_knowledge)} 条相关知识")

        # 4. 识别进化方向
        directions = self.identify_evolution_directions(relevant_knowledge, system_state)
        result["directions"] = directions
        print(f"[知识触发] 识别了 {len(directions)} 个进化方向")

        # 5. 生成触发推荐
        recommendations = self.generate_trigger_recommendations(directions)
        result["recommendations"] = recommendations
        print(f"[知识触发生成了 {len(recommendations)} 个触发推荐")

        # 6. 保存分析结果
        self.knowledge_analysis_cache = result.copy()

        result["success"] = True
        return result

    def record_trigger_result(self, trigger_action: str, success: bool, feedback: str = ""):
        """记录触发结果用于自优化"""
        record = {
            "timestamp": datetime.now().isoformat(),
            "action": trigger_action,
            "success": success,
            "feedback": feedback
        }

        self.trigger_history.append(record)

        # 限制历史长度
        if len(self.trigger_history) > 100:
            self.trigger_history = self.trigger_history[-100:]

        self._save_trigger_history()

        # 更新优化数据
        if self.config["optimization_enabled"]:
            self._update_optimization(trigger_action, success)

    def _update_optimization(self, action: str, success: bool):
        """更新优化数据"""
        if action not in self.optimization_data:
            self.optimization_data[action] = {
                "attempts": 0,
                "successes": 0,
                "failure_reasons": []
            }

        self.optimization_data[action]["attempts"] += 1
        if success:
            self.optimization_data[action]["successes"] += 1
        else:
            self.optimization_data[action]["failure_reasons"].append(datetime.now().isoformat())

        self._save_optimization_data()

    def get_optimization_suggestions(self) -> Dict[str, Any]:
        """获取优化建议"""
        suggestions = {
            "action_success_rates": {},
            "low_performing_actions": [],
            "optimization_recommendations": []
        }

        for action, data in self.optimization_data.items():
            attempts = data.get("attempts", 0)
            if attempts >= 3:
                success_rate = data.get("successes", 0) / attempts
                suggestions["action_success_rates"][action] = {
                    "success_rate": success_rate,
                    "attempts": attempts
                }

                if success_rate < 0.5:
                    suggestions["low_performing_actions"].append(action)
                    suggestions["optimization_recommendations"].append(
                        f"建议优化或减少触发'{action}'，当前成功率仅{success_rate:.1%}"
                    )

        return suggestions

    def get_status(self) -> Dict[str, Any]:
        """获取引擎状态"""
        knowledge = self.load_distilled_knowledge()

        return {
            "version": "1.0.0",
            "auto_trigger_enabled": self.config["auto_trigger_enabled"],
            "total_distilled_knowledge": len(knowledge.get("knowledge", {})),
            "trigger_history_count": len(self.trigger_history),
            "optimization_data_count": len(self.optimization_data),
            "last_analysis": self.knowledge_analysis_cache.get("system_state", {}).get("loop_round", 0)
        }


def handle_command(command: str, args: List[str] = None) -> Dict[str, Any]:
    """处理命令"""
    args = args or []
    engine = KnowledgeDrivenTriggerOptimizer()

    if command == "analyze" or command == "trigger":
        # 分析知识并生成触发推荐
        return engine.analyze_and_trigger()

    elif command == "recommend" or command == "recommends":
        # 直接获取触发推荐
        result = engine.analyze_and_trigger()
        return {
            "success": True,
            "recommendations": result.get("recommendations", [])
        }

    elif command == "optimize" or command == "optimization":
        # 获取优化建议
        return engine.get_optimization_suggestions()

    elif command == "record":
        # 记录触发结果
        if len(args) >= 2:
            action = args[0]
            success = args[1].lower() in ["true", "1", "yes", "success"]
            feedback = args[2] if len(args) > 2 else ""
            engine.record_trigger_result(action, success, feedback)
            return {"success": True, "message": "触发结果已记录"}
        else:
            return {"success": False, "error": "用法: record <action> <success> [feedback]"}

    elif command == "status":
        # 获取状态
        return engine.get_status()

    elif command == "help":
        return {
            "success": True,
            "commands": {
                "analyze/trigger": "分析知识并生成触发推荐",
                "recommend/recommends": "获取触发推荐",
                "optimize/optimization": "获取优化建议",
                "record <action> <success> [feedback]": "记录触发结果",
                "status": "获取引擎状态"
            }
        }

    else:
        return {
            "success": False,
            "error": f"未知命令: {command}"
        }


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("知识驱动自动触发与自优化引擎 v1.0.0")
        print("用法:")
        print("  python evolution_knowledge_driven_trigger_optimizer.py analyze")
        print("  python evolution_knowledge_driven_trigger_optimizer.py recommend")
        print("  python evolution_knowledge_driven_trigger_optimizer.py optimization")
        print("  python evolution_knowledge_driven_trigger_optimizer.py status")
        sys.exit(1)

    command = sys.argv[1]
    args = sys.argv[2:] if len(sys.argv) > 2 else []

    result = handle_command(command, args)
    print(json.dumps(result, ensure_ascii=False, indent=2))