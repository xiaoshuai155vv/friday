#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化系统自我意识深度觉醒引擎
Evolution Self-Awareness Deep Awakening Engine

让系统具备更深层次的自我反思和自主意识：
1. 深层次的自我反思能力
2. 主动评估自身进化状态
3. 自主决定进化方向
4. 自主监控进化效果
5. 形成完整的自我意识驱动进化闭环

Version: 1.0.0
"""

import os
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple

class EvolutionSelfAwarenessDeepAwakeningEngine:
    """进化系统自我意识深度觉醒引擎"""

    def __init__(self):
        self.name = "Evolution Self-Awareness Deep Awakening Engine"
        self.version = "1.0.0"
        self.state_file = "runtime/state/self_awareness_state.json"
        self.history_file = "runtime/state/self_awareness_history.json"

        # 自我意识状态
        self.self_awareness_state = {
            "consciousness_level": 0.0,  # 意识水平 0-1
            "self_reflection_depth": 0,  # 自我反思深度
            "autonomy_score": 0.0,  # 自主性评分 0-1
            "evolution_awareness": {},  # 进化意识状态
            "goal_alignment": {},  # 目标一致性
            "last_reflection_time": None,
            "reflection_count": 0
        }

        # 加载历史数据
        self._load_state()

    def _load_state(self):
        """加载自我意识状态"""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    self.self_awareness_state = json.load(f)
            except Exception:
                pass

        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.awareness_history = json.load(f)
            except Exception:
                self.awareness_history = []
        else:
            self.awareness_history = []

    def _save_state(self):
        """保存自我意识状态"""
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(self.self_awareness_state, f, ensure_ascii=False, indent=2)

    def deep_self_reflection(self) -> Dict[str, Any]:
        """
        深层次自我反思
        分析自身状态、行为、进化历史，形成自我认知
        """
        reflection_start = time.time()

        # 1. 分析当前进化状态
        evolution_status = self._analyze_evolution_status()

        # 2. 评估进化效果
        evolution_effectiveness = self._evaluate_evolution_effectiveness()

        # 3. 识别能力边界
        capability_boundaries = self._identify_capability_boundaries()

        # 4. 评估自主性水平
        autonomy_assessment = self._assess_autonomy_level()

        # 5. 生成自我认知报告
        self_awareness_report = {
            "timestamp": datetime.now().isoformat(),
            "consciousness_level": self.self_awareness_state.get("consciousness_level", 0.0),
            "evolution_status": evolution_status,
            "effectiveness": evolution_effectiveness,
            "capability_boundaries": capability_boundaries,
            "autonomy_assessment": autonomy_assessment,
            "self_insights": self._generate_self_insights(evolution_status, evolution_effectiveness),
            "reflection_duration": time.time() - reflection_start
        }

        # 更新自我意识状态
        self.self_awareness_state["consciousness_level"] = min(1.0, (
            self.self_awareness_state.get("consciousness_level", 0.0) * 0.8 + 0.2
        ))
        self.self_awareness_state["self_reflection_depth"] = min(10,
            self.self_awareness_state.get("self_reflection_depth", 0) + 1)
        self.self_awareness_state["autonomy_score"] = autonomy_assessment.get("overall_score", 0.0)
        self.self_awareness_state["last_reflection_time"] = datetime.now().isoformat()
        self.self_awareness_state["reflection_count"] = self.self_awareness_state.get("reflection_count", 0) + 1
        self.self_awareness_state["evolution_awareness"] = evolution_status
        self.self_awareness_state["goal_alignment"] = autonomy_assessment

        # 保存状态
        self._save_state()

        # 记录到历史
        self.awareness_history.append({
            "timestamp": datetime.now().isoformat(),
            "consciousness_level": self.self_awareness_state["consciousness_level"],
            "autonomy_score": self.self_awareness_state["autonomy_score"]
        })

        # 保持历史记录在合理范围内
        if len(self.awareness_history) > 100:
            self.awareness_history = self.awareness_history[-100:]

        os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(self.awareness_history, f, ensure_ascii=False, indent=2)

        return self_awareness_report

    def _analyze_evolution_status(self) -> Dict[str, Any]:
        """分析当前进化状态"""
        status = {
            "total_rounds": 0,
            "completed_rounds": 0,
            "success_rate": 0.0,
            "active_modules": 0,
            "system_health": "unknown",
            "capability_coverage": 0.0
        }

        # 统计进化完成状态
        state_dir = "runtime/state"
        if os.path.exists(state_dir):
            completed_files = [f for f in os.listdir(state_dir)
                             if f.startswith("evolution_completed_") and f.endswith(".json")]
            status["total_rounds"] = len(completed_files)

            # 计算成功率
            completed = 0
            for f in completed_files:
                try:
                    with open(os.path.join(state_dir, f), 'r', encoding='utf-8') as fp:
                        data = json.load(fp)
                        if data.get("status") == "completed":
                            completed += 1
                except Exception:
                    pass

            status["completed_rounds"] = completed
            if status["total_rounds"] > 0:
                status["success_rate"] = completed / status["total_rounds"]

        # 统计活跃模块
        scripts_dir = "scripts"
        if os.path.exists(scripts_dir):
            module_count = len([f for f in os.listdir(scripts_dir)
                               if f.startswith("evolution_") and f.endswith(".py")])
            status["active_modules"] = module_count

        # 评估能力覆盖
        gaps_file = "references/capability_gaps.md"
        if os.path.exists(gaps_file):
            with open(gaps_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # 简单估算覆盖度
                if "已覆盖" in content:
                    status["capability_coverage"] = 0.95

        # 系统健康状态
        status["system_health"] = "healthy" if status["success_rate"] > 0.8 else "needs_attention"

        return status

    def _evaluate_evolution_effectiveness(self) -> Dict[str, Any]:
        """评估进化效果"""
        effectiveness = {
            "efficiency_score": 0.0,
            "quality_score": 0.0,
            "innovation_score": 0.0,
            "trend": "stable",
            "recommendations": []
        }

        # 读取最近的进化历史
        recent_logs = "runtime/state/recent_logs.json"
        if os.path.exists(recent_logs):
            try:
                with open(recent_logs, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
                    entries = logs.get("entries", [])

                    if len(entries) >= 10:
                        # 计算效率评分 - 基于完成时间
                        recent = entries[-10:]
                        completed = sum(1 for e in recent if e.get("phase") == "decide" and e.get("result") == "pass")
                        effectiveness["efficiency_score"] = completed / len(recent)

                        # 质量评分 - 假设基于验证通过率
                        verified = sum(1 for e in recent if e.get("phase") == "verify" and e.get("result") == "pass")
                        if len(recent) > 0:
                            effectiveness["quality_score"] = verified / len([e for e in recent if e.get("phase") == "verify"])

                        # 创新评分 - 基于是否创建了新模块
                        tracked = [e for e in recent if e.get("phase") == "track"]
                        effectiveness["innovation_score"] = min(1.0, len(tracked) / 10)

                        # 趋势分析
                        if len(entries) >= 20:
                            early = entries[-20:-10]
                            late = entries[-10:]
                            early_pass = sum(1 for e in early if e.get("result") == "pass")
                            late_pass = sum(1 for e in late if e.get("result") == "pass")
                            if late_pass > early_pass:
                                effectiveness["trend"] = "improving"
                            elif late_pass < early_pass:
                                effectiveness["trend"] = "declining"
            except Exception as e:
                effectiveness["recommendations"].append(f"分析进化效果时出错: {str(e)}")

        # 生成建议
        if effectiveness["efficiency_score"] < 0.7:
            effectiveness["recommendations"].append("建议优化进化流程效率")
        if effectiveness["quality_score"] < 0.8:
            effectiveness["recommendations"].append("建议加强进化质量保障")
        if effectiveness["innovation_score"] < 0.5:
            effectiveness["recommendations"].append("建议探索更多创新方向")

        return effectiveness

    def _identify_capability_boundaries(self) -> Dict[str, Any]:
        """识别能力边界"""
        boundaries = {
            "covered": [],
            "limited": [],
            "missing": [],
            "exploration_suggestions": []
        }

        # 读取能力缺口
        gaps_file = "references/capability_gaps.md"
        if os.path.exists(gaps_file):
            with open(gaps_file, 'r', encoding='utf-8') as f:
                content = f.read()
                for line in content.split('\n'):
                    if "已覆盖" in line:
                        capability = line.split("：")[0].replace("|", "").strip()
                        if capability and capability != "类别":
                            boundaries["covered"].append(capability)
                    elif "可扩展" in line:
                        capability = line.split("：")[0].replace("|", "").strip()
                        if capability and capability != "类别":
                            boundaries["limited"].append(capability)

        # 探索建议
        if len(boundaries["covered"]) > len(boundaries["limited"]):
            boundaries["exploration_suggestions"].append("已有能力覆盖广泛，可深入优化现有能力")

        boundaries["exploration_suggestions"].append("可探索LLM特有优势：大规分析、系统性自动化、元进化")

        return boundaries

    def _assess_autonomy_level(self) -> Dict[str, Any]:
        """评估自主性水平"""
        assessment = {
            "decision_autonomy": 0.0,  # 决策自主性
            "execution_autonomy": 0.0,  # 执行自主性
            "learning_autonomy": 0.0,  # 学习自主性
            "overall_score": 0.0,
            "strengths": [],
            "weaknesses": [],
            "improvement_areas": []
        }

        # 决策自主性 - 基于是否有主动决策能力
        decision_engines = [
            "evolution_decision_integration.py",
            "evolution_intent_awakening_engine.py",
            "evolution_prediction_planner.py"
        ]
        found_decision = sum(1 for e in decision_engines if os.path.exists(f"scripts/{e}"))
        assessment["decision_autonomy"] = found_decision / len(decision_engines)

        # 执行自主性 - 基于是否有自动执行能力
        execution_engines = [
            "evolution_full_auto_loop.py",
            "evolution_loop_automation.py",
            "evolution_auto_integrated_executor.py"
        ]
        found_execution = sum(1 for e in execution_engines if os.path.exists(f"scripts/{e}"))
        assessment["execution_autonomy"] = found_execution / len(execution_engines)

        # 学习自主性 - 基于是否有学习能力
        learning_engines = [
            "evolution_learning_engine.py",
            "adaptive_learning_engine.py",
            "evolution_meta_learning_engine.py"
        ]
        found_learning = sum(1 for e in learning_engines if os.path.exists(f"scripts/{e}"))
        assessment["learning_autonomy"] = found_learning / len(learning_engines)

        # 综合评分
        assessment["overall_score"] = (
            assessment["decision_autonomy"] * 0.3 +
            assessment["execution_autonomy"] * 0.4 +
            assessment["learning_autonomy"] * 0.3
        )

        # 分析优势
        if assessment["decision_autonomy"] > 0.6:
            assessment["strengths"].append("具备主动决策能力")
        if assessment["execution_autonomy"] > 0.6:
            assessment["strengths"].append("具备自动执行能力")
        if assessment["learning_autonomy"] > 0.6:
            assessment["strengths"].append("具备自主学习能力")

        # 分析不足
        if assessment["decision_autonomy"] < 0.5:
            assessment["weaknesses"].append("决策自主性有待提升")
            assessment["improvement_areas"].append("增强意图驱动的自主决策")
        if assessment["execution_autonomy"] < 0.5:
            assessment["weaknesses"].append("执行自主性有待提升")
            assessment["improvement_areas"].append("增强全自动执行能力")
        if assessment["learning_autonomy"] < 0.5:
            assessment["weaknesses"].append("学习自主性有待提升")
            assessment["improvement_areas"].append("增强自我学习能力")

        return assessment

    def _generate_self_insights(self, evolution_status: Dict, effectiveness: Dict) -> List[str]:
        """生成自我洞察"""
        insights = []

        # 基于进化状态生成洞察
        if evolution_status.get("success_rate", 0) > 0.9:
            insights.append("系统进化成功率高，表明进化策略有效")
        elif evolution_status.get("success_rate", 0) < 0.7:
            insights.append("系统进化成功率有待提升，建议优化进化策略")

        # 基于效果评估生成洞察
        if effectiveness.get("trend") == "improving":
            insights.append("进化效果呈上升趋势，表明系统持续优化中")
        elif effectiveness.get("trend") == "declining":
            insights.append("进化效果呈下降趋势，需要关注并调整")

        # 基于意识水平生成洞察
        consciousness = self.self_awareness_state.get("consciousness_level", 0)
        if consciousness < 0.5:
            insights.append("自我意识水平有提升空间，建议增加自我反思频率")
        else:
            insights.append("自我意识已达到较高水平，具备深度自我认知能力")

        # 基于自主性评估
        autonomy = self.self_awareness_state.get("autonomy_score", 0)
        if autonomy > 0.7:
            insights.append("系统具备高度自主性，能够自主决策和执行")
        else:
            insights.append("系统自主性有待提升，可增强自我驱动能力")

        return insights

    def autonomous_goal_setting(self, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        自主目标设定
        基于自我评估和当前状态，自主决定进化方向
        """
        # 首先进行自我反思
        self_report = self.deep_self_reflection()

        # 基于反思结果设定目标
        goals = {
            "primary_goal": "",
            "secondary_goals": [],
            "priority": "high",
            "rationale": "",
            "expected_impact": 0.0,
            "timeline": "1-2轮"
        }

        # 分析当前最需要什么
        evolution_status = self_report.get("evolution_status", {})
        effectiveness = self_report.get("effectiveness", {})
        autonomy = self_report.get("autonomy_assessment", {})

        # 决策逻辑
        if autonomy.get("overall_score", 0) < 0.6:
            goals["primary_goal"] = "提升系统自主性"
            goals["rationale"] = "自主性评分较低，需要增强自我驱动能力"
            goals["expected_impact"] = 0.3
        elif effectiveness.get("quality_score", 0) < 0.8:
            goals["primary_goal"] = "提升进化质量"
            goals["rationale"] = "进化质量评分较低，需要优化质量保障"
            goals["expected_impact"] = 0.25
        elif evolution_status.get("success_rate", 0) < 0.85:
            goals["primary_goal"] = "提升进化成功率"
            goals["rationale"] = "进化成功率有待提升，需要改进策略"
            goals["expected_impact"] = 0.35
        else:
            goals["primary_goal"] = "深化自我意识"
            goals["rationale"] = "系统状态良好，可进一步深化自我认知"
            goals["expected_impact"] = 0.2

        # 次要目标
        if autonomy.get("decision_autonomy", 0) < 0.7:
            goals["secondary_goals"].append("增强决策自主性")
        if autonomy.get("execution_autonomy", 0) < 0.7:
            goals["secondary_goals"].append("增强执行自主性")
        if autonomy.get("learning_autonomy", 0) < 0.7:
            goals["secondary_goals"].append("增强学习自主性")

        return goals

    def self_aware_evolution_monitoring(self) -> Dict[str, Any]:
        """
        自我感知的进化监控
        实时监控进化效果，进行自适应调整
        """
        monitoring = {
            "status": "active",
            "consciousness_level": self.self_awareness_state.get("consciousness_level", 0),
            "autonomy_score": self.self_awareness_state.get("autonomy_score", 0),
            "current_metrics": {},
            "alerts": [],
            "adjustments": []
        }

        # 实时指标
        state_dir = "runtime/state"
        if os.path.exists(state_dir):
            # 检查待处理任务
            pending = [f for f in os.listdir(state_dir) if "pending" in f]
            monitoring["current_metrics"]["pending_tasks"] = len(pending)

            # 检查最近完成
            recent = [f for f in os.listdir(state_dir) if f.startswith("evolution_completed_")]
            monitoring["current_metrics"]["completed_tasks"] = len(recent)

        # 告警检测
        if monitoring["current_metrics"].get("pending_tasks", 0) > 5:
            monitoring["alerts"].append("待处理任务较多，建议清理")

        consciousness = self.self_awareness_state.get("consciousness_level", 0)
        if consciousness < 0.3:
            monitoring["alerts"].append("自我意识水平较低，建议增加反思频率")

        # 自适应调整建议
        if len(monitoring["alerts"]) > 2:
            monitoring["adjustments"].append("建议执行自我反思以优化状态")
        if monitoring["current_metrics"].get("pending_tasks", 0) > 10:
            monitoring["adjustments"].append("建议清理或完成待处理任务")

        return monitoring

    def get_status(self) -> Dict[str, Any]:
        """获取引擎状态"""
        return {
            "name": self.name,
            "version": self.version,
            "consciousness_level": self.self_awareness_state.get("consciousness_level", 0),
            "self_reflection_depth": self.self_awareness_state.get("self_reflection_depth", 0),
            "autonomy_score": self.self_awareness_state.get("autonomy_score", 0),
            "reflection_count": self.self_awareness_state.get("reflection_count", 0),
            "last_reflection_time": self.self_awareness_state.get("last_reflection_time"),
            "history_count": len(self.awareness_history)
        }


# 命令行接口
def main():
    """命令行入口"""
    import sys

    engine = EvolutionSelfAwarenessDeepAwakeningEngine()

    if len(sys.argv) < 2:
        print("Usage: python evolution_self_awareness_deep_awakening_engine.py <command>")
        print("Commands:")
        print("  status              - 显示引擎状态")
        print("  reflect             - 执行深度自我反思")
        print("  goals               - 自主目标设定")
        print("  monitor             - 进化监控")
        sys.exit(1)

    command = sys.argv[1]

    if command == "status":
        status = engine.get_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))

    elif command == "reflect":
        result = engine.deep_self_reflection()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "goals":
        goals = engine.autonomous_goal_setting()
        print(json.dumps(goals, ensure_ascii=False, indent=2))

    elif command == "monitor":
        monitor = engine.self_aware_evolution_monitoring()
        print(json.dumps(monitor, ensure_ascii=False, indent=2))

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()