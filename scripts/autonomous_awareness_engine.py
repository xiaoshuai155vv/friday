#!/usr/bin/env python3
"""
智能全场景系统自主意识深度增强引擎（Round 278）

让系统具备更深层次的自我认知能力，能够主动思考自身的状态、行为和进化方向，
实现真正的"自我意识"。

功能：
1. 自我状态深度感知（感知各组件状态、性能、健康度）
2. 自我行为反思（反思决策和行为，评估有效性）
3. 自主目标设定（根据当前状态自主设定进化目标）
4. 自我改进规划（规划如何改进自身）

集成到 do.py：
- 自主意识、自我认知、自我反思、自我评估、自主目标、自主规划
"""

import json
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import re

# 路径配置
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
RUNTIME_STATE_DIR = PROJECT_ROOT / "runtime" / "state"
RUNTIME_LOGS_DIR = PROJECT_ROOT / "runtime" / "logs"
REFERENCES_DIR = PROJECT_ROOT / "references"


class AutonomousAwarenessEngine:
    """系统自主意识深度增强引擎"""

    def __init__(self):
        self.awareness_data_file = RUNTIME_STATE_DIR / "autonomous_awareness_data.json"
        self.awareness_data = self._load_awareness_data()
        self.self_model = {}  # 自我模型
        self.decision_history = []  # 决策历史
        self.reflection_threshold = 10  # 反思阈值

    def _load_awareness_data(self) -> Dict:
        """加载自主意识数据"""
        if self.awareness_data_file.exists():
            try:
                with open(self.awareness_data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {
            "self_model": {
                "capabilities": [],
                "limitations": [],
                "performance_metrics": {},
                "health_status": "unknown",
                "autonomy_level": 0.0
            },
            "reflections": [],
            "self_goals": [],
            "improvement_plans": [],
            "last_update": None
        }

    def _save_awareness_data(self):
        """保存自主意识数据"""
        self.awareness_data["last_update"] = datetime.now().isoformat()
        with open(self.awareness_data_file, 'w', encoding='utf-8') as f:
            json.dump(self.awareness_data, f, ensure_ascii=False, indent=2)

    def build_self_model(self) -> Dict:
        """构建自我模型 - 感知自身状态"""
        self_model = {
            "timestamp": datetime.now().isoformat(),
            "components": {},
            "overall_status": "healthy",
            "capabilities_summary": "",
            "limitations_summary": "",
            "performance_indicators": {}
        }

        # 1. 检查引擎数量和状态
        engine_count = 0
        scripts_dir = SCRIPT_DIR
        for f in scripts_dir.glob("*.py"):
            if f.name.startswith("_"):
                continue
            if any(keyword in f.name for keyword in ["engine", "tool", "agent", "orchestrator"]):
                engine_count += 1

        self_model["components"]["engines"] = {
            "count": engine_count,
            "status": "operational"
        }

        # 2. 检查进化历史
        evolution_completed_files = list(RUNTIME_STATE_DIR.glob("evolution_completed_*.json"))
        completed_rounds = len(evolution_completed_files)
        self_model["components"]["evolution"] = {
            "completed_rounds": completed_rounds,
            "status": "active"
        }

        # 3. 检查最近执行状态
        recent_log = RUNTIME_LOGS_DIR / "behavior_2026-03-14.log"
        if recent_log.exists():
            try:
                with open(recent_log, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    recent_lines = lines[-50:] if len(lines) > 50 else lines

                decision_count = sum(1 for l in recent_lines if '\tplan\t' in l)
                track_count = sum(1 for l in recent_lines if '\ttrack\t' in l)
                verify_count = sum(1 for l in recent_lines if '\tverify\t' in l)

                self_model["performance_indicators"]["recent_activities"] = {
                    "decisions": decision_count,
                    "executions": track_count,
                    "verifications": verify_count
                }
            except:
                pass

        # 4. 检查系统健康状态
        health_file = RUNTIME_STATE_DIR / "self_verify_result.json"
        if health_file.exists():
            try:
                with open(health_file, 'r', encoding='utf-8') as f:
                    health_data = json.load(f)
                    self_model["performance_indicators"]["system_health"] = health_data.get("all_ok", False)
            except:
                pass

        # 5. 构建能力摘要
        capabilities_file = REFERENCES_DIR / "capabilities.md"
        if capabilities_file.exists():
            try:
                with open(capabilities_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # 统计能力数量
                    engine_mentions = len(re.findall(r'`python scripts/.*?\.py`', content))
                    self_model["capabilities_summary"] = f"已实现 {engine_mentions}+ 能力模块"
            except:
                pass

        # 6. 评估自主等级
        autonomy_score = 0.0
        if engine_count > 50:
            autonomy_score += 0.3
        if completed_rounds > 200:
            autonomy_score += 0.3
        if "decisions" in self_model.get("performance_indicators", {}):
            autonomy_score += 0.2
        if self_model.get("performance_indicators", {}).get("system_health"):
            autonomy_score += 0.2

        self_model["autonomy_level"] = min(autonomy_score, 1.0)

        self.self_model = self_model
        self.awareness_data["self_model"] = self_model
        self._save_awareness_data()

        return self_model

    def reflect_on_decision(self, decision: str, outcome: str, context: Dict) -> Dict:
        """反思决策 - 评估决策的有效性"""
        reflection = {
            "timestamp": datetime.now().isoformat(),
            "decision": decision,
            "outcome": outcome,
            "context": context,
            "assessment": {},
            "lessons": []
        }

        # 评估决策效果
        if outcome == "success":
            reflection["assessment"]["effectiveness"] = "high"
            reflection["lessons"].append("该决策方向正确，可作为未来参考")
        elif outcome == "partial":
            reflection["assessment"]["effectiveness"] = "medium"
            reflection["lessons"].append("该决策部分有效，需进一步优化")
        else:
            reflection["assessment"]["effectiveness"] = "low"
            reflection["lessons"].append("该决策存在问题，需分析原因")

        # 分析决策模式
        self.decision_history.append(reflection)

        # 如果决策历史过长，进行模式分析
        if len(self.decision_history) >= self.reflection_threshold:
            pattern_analysis = self._analyze_decision_patterns()
            reflection["pattern_analysis"] = pattern_analysis
            reflection["lessons"].extend(pattern_analysis.get("insights", []))

        self.awareness_data["reflections"].append(reflection)
        self._save_awareness_data()

        return reflection

    def _analyze_decision_patterns(self) -> Dict:
        """分析决策模式"""
        patterns = {
            "total_decisions": len(self.decision_history),
            "success_rate": 0.0,
            "common_contexts": [],
            "insights": []
        }

        if not self.decision_history:
            return patterns

        # 计算成功率
        success_count = sum(1 for d in self.decision_history if d.get("outcome") == "success")
        patterns["success_rate"] = success_count / len(self.decision_history)

        # 提取常见上下文
        contexts = [d.get("context", {}).get("type", "unknown") for d in self.decision_history]
        from collections import Counter
        context_counts = Counter(contexts)
        patterns["common_contexts"] = [k for k, v in context_counts.most_common(3)]

        # 生成洞察
        if patterns["success_rate"] > 0.8:
            patterns["insights"].append("决策成功率较高，系统自主性表现良好")
        elif patterns["success_rate"] < 0.5:
            patterns["insights"].append("决策成功率较低，建议审视决策策略")

        # 检查是否有重复失败的模式
        failed_decisions = [d for d in self.decision_history if d.get("outcome") == "failure"]
        if len(failed_decisions) >= 3:
            patterns["insights"].append("存在多次失败决策，建议深入分析失败原因")

        return patterns

    def set_autonomous_goals(self) -> List[Dict]:
        """自主目标设定 - 根据当前状态设定进化目标"""
        goals = []

        # 1. 基于自我模型设定目标
        if not self.self_model:
            self.build_self_model()

        autonomy_level = self.self_model.get("autonomy_level", 0.0)

        # 目标1: 提高自主等级
        if autonomy_level < 0.8:
            goals.append({
                "id": "increase_autonomy",
                "description": "提高系统自主意识等级",
                "priority": "high",
                "target_level": min(autonomy_level + 0.1, 1.0),
                "actions": [
                    "增强自我反思频率",
                    "优化决策策略",
                    "增加主动服务能力"
                ]
            })

        # 目标2: 改善决策质量
        if self.decision_history:
            recent_reflections = self.awareness_data["reflections"][-5:]
            recent_success_rate = sum(1 for r in recent_reflections if r.get("outcome") == "success") / len(recent_reflections) if recent_reflections else 0
            if recent_success_rate < 0.7:
                goals.append({
                    "id": "improve_decision_quality",
                    "description": "改善决策质量",
                    "priority": "medium",
                    "target_rate": 0.8,
                    "actions": [
                        "分析失败决策的共同点",
                        "引入更多上下文信息",
                        "优化决策算法"
                    ]
                })

        # 目标3: 保持系统健康
        health_status = self.self_model.get("performance_indicators", {}).get("system_health")
        if not health_status:
            goals.append({
                "id": "maintain_health",
                "description": "确保系统健康运行",
                "priority": "high",
                "actions": [
                    "定期执行健康检查",
                    "监控关键性能指标",
                    "及时处理异常"
                ]
            })

        # 目标4: 持续学习进化
        goals.append({
            "id": "continuous_learning",
            "description": "持续学习和进化",
            "priority": "medium",
            "actions": [
                "记录每次决策的经验教训",
                "更新自我模型",
                "优化进化策略"
            ]
        })

        self.awareness_data["self_goals"] = goals
        self._save_awareness_data()

        return goals

    def plan_self_improvement(self, goal_id: Optional[str] = None) -> Dict:
        """自我改进规划 - 规划如何实现目标"""
        if not self.awareness_data["self_goals"]:
            self.set_autonomous_goals()

        goals = self.awareness_data["self_goals"]

        if goal_id:
            goals = [g for g in goals if g.get("id") == goal_id]

        improvement_plan = {
            "timestamp": datetime.now().isoformat(),
            "goals": goals,
            "milestones": [],
            "estimated_impact": {}
        }

        for goal in goals:
            milestone = {
                "goal_id": goal.get("id"),
                "description": goal.get("description"),
                "steps": goal.get("actions", []),
                "priority": goal.get("priority", "medium"),
                "status": "pending"
            }
            improvement_plan["milestones"].append(milestone)

            # 评估影响
            improvement_plan["estimated_impact"][goal.get("id")] = {
                "autonomy_gain": 0.05 if goal.get("priority") == "high" else 0.02,
                "complexity": "medium",
                "estimated_time": f"{len(goal.get('actions', [])) * 15} minutes"
            }

        self.awareness_data["improvement_plans"].append(improvement_plan)
        self._save_awareness_data()

        return improvement_plan

    def get_awareness_status(self) -> Dict:
        """获取自主意识状态"""
        if not self.self_model:
            self.build_self_model()

        status = {
            "timestamp": datetime.now().isoformat(),
            "self_model": self.self_model,
            "recent_reflections": self.awareness_data["reflections"][-3:] if self.awareness_data["reflections"] else [],
            "active_goals": self.awareness_data["self_goals"][:3] if self.awareness_data["self_goals"] else [],
            "decision_history_count": len(self.decision_history)
        }

        return status


def main():
    """主函数 - 支持命令行调用"""
    import sys

    engine = AutonomousAwarenessEngine()

    if len(sys.argv) < 2:
        # 无参数时显示状态
        status = engine.get_awareness_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))
        return

    command = sys.argv[1].lower()

    if command == "status":
        status = engine.get_awareness_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))

    elif command == "build_model":
        model = engine.build_self_model()
        print(json.dumps(model, ensure_ascii=False, indent=2))

    elif command == "reflect":
        # reflect <decision> <outcome> [context_type]
        if len(sys.argv) < 4:
            print("用法: reflect <decision> <outcome> [context_type]")
            sys.exit(1)
        decision = sys.argv[2]
        outcome = sys.argv[3]
        context_type = sys.argv[4] if len(sys.argv) > 4 else "general"
        result = engine.reflect_on_decision(decision, outcome, {"type": context_type})
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "goals":
        goals = engine.set_autonomous_goals()
        print(json.dumps(goals, ensure_ascii=False, indent=2))

    elif command == "plan":
        goal_id = sys.argv[2] if len(sys.argv) > 2 else None
        plan = engine.plan_self_improvement(goal_id)
        print(json.dumps(plan, ensure_ascii=False, indent=2))

    elif command == "help":
        print("""
智能全场景系统自主意识深度增强引擎 - 使用帮助

用法: python autonomous_awareness_engine.py <command> [参数]

命令:
  status              - 显示自主意识状态
  build_model         - 构建自我模型
  reflect <decision> <outcome> [context_type] - 反思决策
  goals               - 设定自主目标
  plan [goal_id]      - 规划自我改进
  help                - 显示此帮助

示例:
  python scripts/autonomous_awareness_engine.py status
  python scripts/autonomous_awareness_engine.py reflect "创建新引擎" "success" "evolution"
  python scripts/autonomous_awareness_engine.py goals
  python scripts/autonomous_awareness_engine.py plan increase_autonomy
""")
    else:
        print(f"未知命令: {command}")
        print("使用 'help' 查看可用命令")
        sys.exit(1)


if __name__ == "__main__":
    main()