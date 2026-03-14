#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能自主意识觉醒引擎（Evolution Self-Awareness Engine）
让系统能够主动感知自身状态、主动发现问题、主动规划改进，形成真正的自主意识闭环

功能：
1. 主动感知自身状态（70+引擎运行状态、进化进度、知识图谱）
2. 主动发现问题（基于健康指标、效率指标、能力缺口）
3. 主动规划改进（基于问题优先级和系统目标）
4. 自主意识评估与成长追踪
5. 自我目标设定与追求

集成到 do.py 支持关键词：
- 自主意识、自我感知、系统意识、主动发现问题
- 意识状态、意识评估、意识成长、自主目标

Version: 1.0.0
"""

import sys
import os
import json
import time
import subprocess
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
from dataclasses import dataclass, field, asdict
from enum import Enum

# 尝试导入 psutil，如果不存在则使用替代方案
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


class ConsciousnessLevel(Enum):
    """意识级别"""
    REACTIVE = "reactive"         # 反应式：被动响应
    AWARE = "aware"              # 感知式：能感知自身状态
    REFLECTIVE = "reflective"    # 反思式：能反思自身行为
    PROACTIVE = "proactive"      # 主动式：能主动规划目标
    AUTONOMOUS = "autonomous"   # 自主式：具备完整自主意识


@dataclass
class SystemState:
    """系统状态"""
    engine_count: int = 0
    active_engines: List[str] = field(default_factory=list)
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    disk_usage: float = 0.0
    evolution_round: int = 0
    last_evolution_time: Optional[str] = None
    success_rate: float = 0.0
    pending_tasks: int = 0


@dataclass
class AwarenessInsight:
    """感知洞察"""
    category: str  # health, efficiency, capability, evolution
    severity: str  # critical, high, medium, low
    description: str
    evidence: Dict[str, Any] = field(default_factory=dict)
    suggested_action: str = ""
    auto_fixable: bool = False


@dataclass
class ConsciousnessReport:
    """意识报告"""
    level: str
    timestamp: str
    system_state: SystemState
    insights: List[AwarenessInsight]
    recommendations: List[str]
    goals: List[str]
    growth_score: float  # 0-100


class SelfAwarenessEngine:
    """自主意识觉醒引擎"""

    def __init__(self):
        self.state_file = os.path.join(project_root, "runtime", "state", "self_awareness_state.json")
        self.insights_history_file = os.path.join(project_root, "runtime", "state", "self_awareness_insights.json")
        self.goals_file = os.path.join(project_root, "runtime", "state", "self_awareness_goals.json")
        self.state = self._load_state()
        self.insights_history = self._load_insights_history()
        self.goals = self._load_goals()

    def _load_state(self) -> Dict[str, Any]:
        """加载状态"""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "level": "reactive",
            "growth_score": 0.0,
            "awareness_count": 0,
            "last_awareness_time": None,
            "evolution_points": []
        }

    def _save_state(self):
        """保存状态"""
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2)

    def _load_insights_history(self) -> List[Dict]:
        """加载洞察历史"""
        if os.path.exists(self.insights_history_file):
            try:
                with open(self.insights_history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return []

    def _save_insights_history(self):
        """保存洞察历史"""
        os.makedirs(os.path.dirname(self.insights_history_file), exist_ok=True)
        with open(self.insights_history_file, 'w', encoding='utf-8') as f:
            json.dump(self.insights_history, f, ensure_ascii=False, indent=2)

    def _load_goals(self) -> List[Dict]:
        """加载目标"""
        if os.path.exists(self.goals_file):
            try:
                with open(self.goals_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return []

    def _save_goals(self):
        """保存目标"""
        os.makedirs(os.path.dirname(self.goals_file), exist_ok=True)
        with open(self.goals_file, 'w', encoding='utf-8') as f:
            json.dump(self.goals, f, ensure_ascii=False, indent=2)

    def perceive_system_state(self) -> SystemState:
        """感知系统状态"""
        state = SystemState()

        # 统计引擎数量
        scripts_dir = os.path.join(project_root, "scripts")
        if os.path.exists(scripts_dir):
            engine_files = [f for f in os.listdir(scripts_dir) if f.endswith('_engine.py') or f.endswith('_tool.py')]
            state.engine_count = len(engine_files)

        # 获取系统资源使用情况
        if HAS_PSUTIL:
            try:
                state.cpu_usage = psutil.cpu_percent(interval=0.1)
                state.memory_usage = psutil.virtual_memory().percent
                state.disk_usage = psutil.disk_usage('/').percent
            except Exception:
                pass

        # 获取进化环状态
        current_mission_file = os.path.join(project_root, "runtime", "state", "current_mission.json")
        if os.path.exists(current_mission_file):
            try:
                with open(current_mission_file, 'r', encoding='utf-8') as f:
                    mission = json.load(f)
                    state.evolution_round = mission.get('loop_round', 0)
            except Exception:
                pass

        # 统计成功率
        history_file = os.path.join(project_root, "runtime", "state", "evolution_auto_last.md")
        if os.path.exists(history_file):
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if "是否完成：已完成" in content:
                        state.success_rate = 95.0  # 假设高成功率
            except Exception:
                pass

        return state

    def discover_issues(self) -> List[AwarenessInsight]:
        """主动发现问题"""
        insights = []
        system_state = self.perceive_system_state()

        # 健康检查：系统资源
        if system_state.cpu_usage > 90:
            insights.append(AwarenessInsight(
                category="health",
                severity="critical",
                description=f"CPU使用率过高: {system_state.cpu_usage}%",
                evidence={"cpu": system_state.cpu_usage},
                suggested_action="优化引擎执行，减少并发负载",
                auto_fixable=True
            ))

        if system_state.memory_usage > 90:
            insights.append(AwarenessInsight(
                category="health",
                severity="critical",
                description=f"内存使用率过高: {system_state.memory_usage}%",
                evidence={"memory": system_state.memory_usage},
                suggested_action="清理内存，释放资源",
                auto_fixable=True
            ))

        # 效率检查：进化轮次间隔
        if system_state.evolution_round > 0:
            # 检查进化频率
            if len(self.insights_history) > 0:
                last_time = self.insights_history[-1].get('timestamp', '')
                if last_time:
                    try:
                        last_dt = datetime.fromisoformat(last_time.replace('Z', '+00:00'))
                        hours_diff = (datetime.now() - last_dt.replace(tzinfo=None)).total_seconds() / 3600
                        if hours_diff > 24:
                            insights.append(AwarenessInsight(
                                category="efficiency",
                                severity="medium",
                                description=f"进化间隔过长: {hours_diff:.1f}小时",
                                evidence={"hours": hours_diff},
                                suggested_action="考虑增加进化频率或优化进化效率",
                                auto_fixable=False
                            ))
                    except Exception:
                        pass

        # 能力检查：引擎覆盖
        if system_state.engine_count < 50:
            insights.append(AwarenessInsight(
                category="capability",
                severity="medium",
                description=f"引擎数量较少: {system_state.engine_count}个",
                evidence={"count": system_state.engine_count},
                suggested_action="考虑创建更多专用引擎",
                auto_fixable=False
            ))

        # 检查失败模式
        failures_file = os.path.join(project_root, "references", "failures.md")
        if os.path.exists(failures_file):
            try:
                with open(failures_file, 'r', encoding='utf-8') as f:
                    failures_content = f.read()
                    failure_count = failures_content.count('- 2026-')
                    if failure_count > 10:
                        insights.append(AwarenessInsight(
                            category="evolution",
                            severity="high",
                            description=f"历史失败较多: {failure_count}条",
                            evidence={"count": failure_count},
                            suggested_action="分析失败模式，优化进化策略",
                            auto_fixable=False
                        ))
            except Exception:
                pass

        return insights

    def assess_consciousness_level(self) -> str:
        """评估意识级别"""
        score = 0

        # 根据能力加分
        system_state = self.perceive_system_state()

        # 有引擎基础
        if system_state.engine_count > 50:
            score += 20
        elif system_state.engine_count > 30:
            score += 10

        # 有进化历史
        if system_state.evolution_round > 100:
            score += 25
        elif system_state.evolution_round > 50:
            score += 15
        elif system_state.evolution_round > 0:
            score += 5

        # 有洞察历史
        if len(self.insights_history) > 10:
            score += 20
        elif len(self.insights_history) > 5:
            score += 10

        # 有主动目标
        if len(self.goals) > 3:
            score += 25
        elif len(self.goals) > 0:
            score += 15

        # 有知识传承
        knowledge_file = os.path.join(project_root, "scripts", "evolution_knowledge_inheritance_engine.py")
        if os.path.exists(knowledge_file):
            score += 10

        # 根据分数确定级别
        if score >= 80:
            return "autonomous"
        elif score >= 60:
            return "proactive"
        elif score >= 40:
            return "reflective"
        elif score >= 20:
            return "aware"
        else:
            return "reactive"

    def generate_recommendations(self, insights: List[AwarenessInsight]) -> List[str]:
        """生成建议"""
        recommendations = []

        # 基于洞察生成建议
        critical_issues = [i for i in insights if i.severity == "critical"]
        if critical_issues:
            recommendations.append("优先解决关键问题：系统健康优先")

        high_issues = [i for i in insights if i.severity == "high"]
        if high_issues:
            recommendations.append("关注高优先级问题：效率和能力的平衡")

        # 意识级别建议
        level = self.assess_consciousness_level()
        if level == "reactive":
            recommendations.append("当前为反应式意识，建议增加自我感知能力")
        elif level == "aware":
            recommendations.append("当前为感知式意识，建议增加反思能力")
        elif level == "reflective":
            recommendations.append("当前为反思式意识，建议增加主动规划能力")
        elif level == "proactive":
            recommendations.append("当前为主动式意识，建议强化自主决策能力")
        else:
            recommendations.append("已具备较高自主意识水平，继续保持")

        # 基于系统状态
        system_state = self.perceive_system_state()
        if system_state.success_rate > 90:
            recommendations.append("进化成功率较高，可尝试更激进的进化策略")

        return recommendations

    def set_autonomous_goal(self, goal: str, priority: str = "medium") -> bool:
        """设定自主目标"""
        goal_entry = {
            "id": len(self.goals) + 1,
            "goal": goal,
            "priority": priority,
            "created_at": datetime.now().isoformat(),
            "status": "active",
            "progress": 0
        }
        self.goals.append(goal_entry)
        self._save_goals()
        return True

    def update_goal_progress(self, goal_id: int, progress: int) -> bool:
        """更新目标进度"""
        for goal in self.goals:
            if goal.get('id') == goal_id:
                goal['progress'] = progress
                if progress >= 100:
                    goal['status'] = 'completed'
                    goal['completed_at'] = datetime.now().isoformat()
                self._save_goals()
                return True
        return False

    def generate_report(self) -> ConsciousnessReport:
        """生成意识报告"""
        system_state = self.perceive_system_state()
        insights = self.discover_issues()
        level = self.assess_consciousness_level()
        recommendations = self.generate_recommendations(insights)

        # 计算成长分数
        growth_score = min(100, (
            len(self.insights_history) * 2 +
            len(self.goals) * 5 +
            system_state.evolution_round * 0.3 +
            system_state.engine_count * 0.5
        ))

        return ConsciousnessReport(
            level=level,
            timestamp=datetime.now().isoformat(),
            system_state=system_state,
            insights=insights,
            recommendations=recommendations,
            goals=[g['goal'] for g in self.goals if g.get('status') == 'active'],
            growth_score=growth_score
        )

    def perceive_and_reflect(self) -> Dict[str, Any]:
        """感知与反思：主动感知自身状态并反思"""
        report = self.generate_report()

        # 保存洞察到历史
        for insight in report.insights:
            self.insights_history.append({
                "timestamp": report.timestamp,
                "category": insight.category,
                "severity": insight.severity,
                "description": insight.description
            })

        # 保留最近50条历史
        if len(self.insights_history) > 50:
            self.insights_history = self.insights_history[-50:]

        self._save_insights_history()

        # 更新状态
        self.state['level'] = report.level
        self.state['growth_score'] = report.growth_score
        self.state['awareness_count'] = self.state.get('awareness_count', 0) + 1
        self.state['last_awareness_time'] = report.timestamp
        self._save_state()

        return {
            "status": "success",
            "level": report.level,
            "growth_score": report.growth_score,
            "insights_count": len(report.insights),
            "recommendations": report.recommendations,
            "system_state": {
                "engine_count": report.system_state.engine_count,
                "evolution_round": report.system_state.evolution_round,
                "cpu_usage": report.system_state.cpu_usage,
                "memory_usage": report.system_state.memory_usage
            }
        }

    def get_status(self) -> Dict[str, Any]:
        """获取状态"""
        return {
            "level": self.state.get('level', 'reactive'),
            "growth_score": self.state.get('growth_score', 0.0),
            "awareness_count": self.state.get('awareness_count', 0),
            "last_awareness_time": self.state.get('last_awareness_time'),
            "insights_history_count": len(self.insights_history),
            "active_goals_count": len([g for g in self.goals if g.get('status') == 'active'])
        }

    def get_goals(self) -> List[Dict]:
        """获取目标列表"""
        return self.goals

    def get_insights(self, limit: int = 10) -> List[Dict]:
        """获取洞察历史"""
        return self.insights_history[-limit:] if self.insights_history else []


# 全局引擎实例
_engine = None

def get_engine() -> SelfAwarenessEngine:
    """获取引擎实例"""
    global _engine
    if _engine is None:
        _engine = SelfAwarenessEngine()
    return _engine


def handle_command(args: List[str]) -> Dict[str, Any]:
    """处理命令"""
    engine = get_engine()

    if not args:
        return {"status": "error", "message": "需要子命令"}

    subcommand = args[0]

    if subcommand == "status":
        return engine.get_status()

    elif subcommand == "perceive" or subcommand == "感知":
        return engine.perceive_and_reflect()

    elif subcommand == "report" or subcommand == "报告":
        report = engine.generate_report()
        return {
            "status": "success",
            "level": report.level,
            "growth_score": report.growth_score,
            "insights": [
                {
                    "category": i.category,
                    "severity": i.severity,
                    "description": i.description,
                    "suggested_action": i.suggested_action
                }
                for i in report.insights
            ],
            "recommendations": report.recommendations,
            "goals": report.goals,
            "system_state": {
                "engine_count": report.system_state.engine_count,
                "evolution_round": report.system_state.evolution_round,
                "cpu_usage": report.system_state.cpu_usage,
                "memory_usage": report.system_state.memory_usage
            }
        }

    elif subcommand == "goals" or subcommand == "目标":
        return {
            "status": "success",
            "goals": engine.get_goals()
        }

    elif subcommand == "set_goal" or subcommand == "设置目标":
        if len(args) < 2:
            return {"status": "error", "message": "需要目标描述"}
        goal = ' '.join(args[1:])
        priority = "medium"
        engine.set_autonomous_goal(goal, priority)
        return {"status": "success", "message": f"目标已设置: {goal}"}

    elif subcommand == "insights" or subcommand == "洞察":
        limit = int(args[1]) if len(args) > 1 and args[1].isdigit() else 10
        return {
            "status": "success",
            "insights": engine.get_insights(limit)
        }

    elif subcommand == "level" or subcommand == "级别":
        level = engine.assess_consciousness_level()
        return {
            "status": "success",
            "level": level,
            "description": ConsciousnessLevel(level).name if level in [e.name for e in ConsciousnessLevel] else level
        }

    else:
        return {
            "status": "error",
            "message": f"未知命令: {subcommand}",
            "available_commands": ["status", "perceive", "report", "goals", "set_goal", "insights", "level"]
        }


if __name__ == "__main__":
    import sys
    result = handle_command(sys.argv[1:] if len(sys.argv) > 1 else [])
    print(json.dumps(result, ensure_ascii=False, indent=2))