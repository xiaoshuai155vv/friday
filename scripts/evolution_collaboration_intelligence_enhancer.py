#!/usr/bin/env python3
"""
智能全场景进化环智能协同与自主决策增强引擎
Evolution Collaboration Intelligence and Autonomous Decision Enhancement Engine

版本: 1.0.0
创建日期: 2026-03-14
功能描述:
  让系统能够基于多维度信息（系统状态、进化历史、知识图谱、当前能力缺口）
  进行更智能的协同决策，实现从"多引擎独立运行"到"多引擎智能协同自治"的
  范式升级。

主要功能:
1. 多引擎智能协同编排 - 让70+引擎能够根据任务需求自动组成协同团队
2. 自主决策增强 - 让系统能够基于实时状态自主决定使用哪些引擎组合
3. 协同效果实时评估 - 评估多引擎协同执行的效果并自动优化

触发关键词: 智能协同、协同编排、协同决策、协同增强、多引擎协同
"""

import json
import os
import sys
import subprocess
import shutil
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set, Tuple
from pathlib import Path
from collections import defaultdict

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
RUNTIME_STATE_DIR = PROJECT_ROOT / "runtime" / "state"
RUNTIME_LOGS_DIR = PROJECT_ROOT / "runtime" / "logs"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
REFERENCES_DIR = PROJECT_ROOT / "references"


class EvolutionCollaborationIntelligenceEnhancer:
    """智能协同与自主决策增强引擎"""

    def __init__(self):
        self.name = "EvolutionCollaborationIntelligenceEnhancer"
        self.version = "1.0.0"
        self.collaboration_state_file = RUNTIME_STATE_DIR / "collaboration_intelligence_state.json"
        self.decision_log_file = RUNTIME_STATE_DIR / "collaboration_decisions.json"
        self.evaluation_log_file = RUNTIME_STATE_DIR / "collaboration_evaluations.json"

        # 初始化状态
        self.collaboration_state = self._load_state()
        self.decision_log = self._load_decision_log()
        self.evaluation_log = self._load_evaluation_log()

        # 引擎能力分类
        self.engine_categories = {
            "execution": ["workflow_engine", "run_plan", "auto_execution"],
            "analysis": ["evolution_log_analyzer", "execution_log_analyzer", "data_insight"],
            "learning": ["adaptive_learning_engine", "evolution_learning_engine"],
            "decision": ["decision_orchestrator", "evolution_strategy_engine"],
            "health": ["system_health_report_engine", "self_healing_engine"],
            "service": ["unified_service_hub", "service_orchestration_optimizer"],
            "collaboration": ["multi_agent_collaboration_engine", "module_linkage_engine"]
        }

    def _load_state(self) -> Dict:
        """加载协同智能状态"""
        if self.collaboration_state_file.exists():
            try:
                with open(self.collaboration_state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass

        return {
            "active_teams": [],
            "team_performance": {},
            "collaboration_patterns": [],
            "decision_history": [],
            "last_updated": datetime.now().isoformat()
        }

    def _load_decision_log(self) -> Dict:
        """加载决策日志"""
        if self.decision_log_file.exists():
            try:
                with open(self.decision_log_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass

        return {"decisions": [], "last_updated": datetime.now().isoformat()}

    def _load_evaluation_log(self) -> Dict:
        """加载评估日志"""
        if self.evaluation_log_file.exists():
            try:
                with open(self.evaluation_log_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass

        return {"evaluations": [], "last_updated": datetime.now().isoformat()}

    def _save_state(self):
        """保存协同智能状态"""
        self.collaboration_state["last_updated"] = datetime.now().isoformat()
        try:
            with open(self.collaboration_state_file, 'w', encoding='utf-8') as f:
                json.dump(self.collaboration_state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存状态失败: {e}")

    def _save_decision_log(self):
        """保存决策日志"""
        self.decision_log["last_updated"] = datetime.now().isoformat()
        try:
            with open(self.decision_log_file, 'w', encoding='utf-8') as f:
                json.dump(self.decision_log, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存决策日志失败: {e}")

    def _save_evaluation_log(self):
        """保存评估日志"""
        self.evaluation_log["last_updated"] = datetime.now().isoformat()
        try:
            with open(self.evaluation_log_file, 'w', encoding='utf-8') as f:
                json.dump(self.evaluation_log, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存评估日志失败: {e}")

    def analyze_task_requirements(self, task_description: str) -> Dict[str, Any]:
        """
        分析任务需求，识别需要哪些类型的引擎

        Args:
            task_description: 任务描述

        Returns:
            任务分析结果，包含所需引擎类型和优先级
        """
        task_lower = task_description.lower()

        # 基于关键词匹配识别需要的引擎类型
        required_categories = []

        if any(kw in task_lower for kw in ["执行", "运行", "操作", "完成", "处理"]):
            required_categories.append("execution")

        if any(kw in task_lower for kw in ["分析", "评估", "检查", "检测", "诊断"]):
            required_categories.append("analysis")

        if any(kw in task_lower for kw in ["学习", "适应", "优化", "改进"]):
            required_categories.append("learning")

        if any(kw in task_lower for kw in ["决策", "规划", "选择", "决定"]):
            required_categories.append("decision")

        if any(kw in task_lower for kw in ["健康", "修复", "自愈", "监控"]):
            required_categories.append("health")

        if any(kw in task_lower for kw in ["服务", "协同", "协作", "多引擎"]):
            required_categories.append("service")

        # 默认至少需要执行引擎
        if not required_categories:
            required_categories = ["execution", "analysis"]

        return {
            "task": task_description,
            "required_categories": required_categories,
            "priority": self._calculate_task_priority(task_description),
            "estimated_complexity": len(required_categories)
        }

    def _calculate_task_priority(self, task_description: str) -> str:
        """计算任务优先级"""
        high_priority_keywords = ["紧急", "立即", "重要", "关键", "优先"]
        low_priority_keywords = ["可以", "稍后", "不急", "以后"]

        task_lower = task_description.lower()
        if any(kw in task_lower for kw in high_priority_keywords):
            return "high"
        elif any(kw in task_lower for kw in low_priority_keywords):
            return "low"
        return "normal"

    def form_collaboration_team(self, task_analysis: Dict) -> Dict[str, Any]:
        """
        根据任务分析结果，组建智能协同团队

        Args:
            task_analysis: 任务分析结果

        Returns:
            协同团队配置
        """
        required_categories = task_analysis.get("required_categories", [])

        # 扫描可用引擎
        available_engines = self._scan_available_engines()

        # 根据需要的引擎类型组建团队
        team_members = []
        for category in required_categories:
            if category in self.engine_categories:
                for engine in self.engine_categories[category]:
                    if engine in available_engines:
                        team_members.append({
                            "engine": engine,
                            "category": category,
                            "role": self._assign_role(category, len(team_members))
                        })

        team_id = f"team_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        team = {
            "team_id": team_id,
            "task": task_analysis.get("task", ""),
            "members": team_members,
            "priority": task_analysis.get("priority", "normal"),
            "complexity": task_analysis.get("estimated_complexity", 1),
            "created_at": datetime.now().isoformat(),
            "status": "forming"
        }

        # 保存团队信息
        self.collaboration_state["active_teams"].append(team)
        self._save_state()

        return team

    def _scan_available_engines(self) -> Set[str]:
        """扫描可用的引擎"""
        available = set()

        # 扫描 scripts 目录下的进化引擎
        if SCRIPTS_DIR.exists():
            for f in SCRIPTS_DIR.glob("evolution_*.py"):
                engine_name = f.stem
                available.add(engine_name)

        return available

    def _assign_role(self, category: str, member_index: int) -> str:
        """为团队成员分配角色"""
        role_mapping = {
            "execution": ["主执行引擎", "辅助执行引擎"],
            "analysis": ["主分析引擎", "辅助分析引擎"],
            "learning": ["学习引擎"],
            "decision": ["决策引擎", "策略引擎"],
            "health": ["健康监控引擎"],
            "service": ["服务协调引擎"],
            "collaboration": ["协同引擎"]
        }

        roles = role_mapping.get(category, ["通用引擎"])
        return roles[min(member_index, len(roles) - 1)]

    def get_collaboration_recommendation(self, task_description: str) -> Dict[str, Any]:
        """
        获取协同建议（主入口）

        Args:
            task_description: 任务描述

        Returns:
            协同建议
        """
        # 1. 分析任务需求
        task_analysis = self.analyze_task_requirements(task_description)

        # 2. 组建协同团队
        team = self.form_collaboration_team(task_analysis)

        # 3. 记录决策
        decision = {
            "task": task_description,
            "analysis": task_analysis,
            "team": team,
            "timestamp": datetime.now().isoformat()
        }

        self.decision_log["decisions"].append(decision)
        self._save_decision_log()

        return {
            "success": True,
            "task_analysis": task_analysis,
            "recommended_team": team,
            "message": f"已为任务组建包含 {len(team['members'])} 个引擎的协同团队"
        }

    def evaluate_collaboration_effectiveness(self, team_id: str, execution_result: Dict) -> Dict[str, Any]:
        """
        评估协同效果

        Args:
            team_id: 团队ID
            execution_result: 执行结果

        Returns:
            评估结果
        """
        # 计算效果评分
        success = execution_result.get("success", False)
        duration = execution_result.get("duration", 0)
        error_count = execution_result.get("error_count", 0)

        # 效果评分算法
        effectiveness_score = 0
        if success:
            effectiveness_score += 60
            # 根据执行时间加分（越快越好）
            if duration < 10:
                effectiveness_score += 20
            elif duration < 30:
                effectiveness_score += 10
            # 根据错误数减分
            effectiveness_score -= error_count * 10

        effectiveness_score = max(0, min(100, effectiveness_score))

        # 效果等级
        if effectiveness_score >= 80:
            level = "excellent"
        elif effectiveness_score >= 60:
            level = "good"
        elif effectiveness_score >= 40:
            level = "fair"
        else:
            level = "poor"

        evaluation = {
            "team_id": team_id,
            "score": effectiveness_score,
            "level": level,
            "success": success,
            "duration": duration,
            "error_count": error_count,
            "timestamp": datetime.now().isoformat()
        }

        # 保存评估结果
        self.evaluation_log["evaluations"].append(evaluation)

        # 更新团队绩效
        if team_id not in self.collaboration_state["team_performance"]:
            self.collaboration_state["team_performance"][team_id] = []
        self.collaboration_state["team_performance"][team_id].append(evaluation)

        self._save_evaluation_log()
        self._save_state()

        return evaluation

    def get_collaboration_insights(self) -> Dict[str, Any]:
        """获取协同洞察"""
        insights = {
            "active_teams_count": len(self.collaboration_state.get("active_teams", [])),
            "total_decisions": len(self.decision_log.get("decisions", [])),
            "total_evaluations": len(self.evaluation_log.get("evaluations", [])),
            "performance_summary": self._get_performance_summary(),
            "recommendations": self._generate_recommendations()
        }

        return insights

    def _get_performance_summary(self) -> Dict[str, Any]:
        """获取性能摘要"""
        evaluations = self.evaluation_log.get("evaluations", [])

        if not evaluations:
            return {"total": 0, "average_score": 0, "excellent_count": 0}

        total = len(evaluations)
        average_score = sum(e["score"] for e in evaluations) / total
        excellent_count = sum(1 for e in evaluations if e["level"] == "excellent")

        return {
            "total": total,
            "average_score": round(average_score, 2),
            "excellent_count": excellent_count,
            "success_rate": round(sum(1 for e in evaluations if e["success"]) / total * 100, 2)
        }

    def _generate_recommendations(self) -> List[str]:
        """生成优化建议"""
        recommendations = []

        evaluations = self.evaluation_log.get("evaluations", [])
        if len(evaluations) > 5:
            recent = evaluations[-5:]
            avg_score = sum(e["score"] for e in recent) / len(recent)

            if avg_score < 50:
                recommendations.append("建议简化协同流程，减少参与引擎数量")
                recommendations.append("考虑使用更专注于单一任务的引擎组合")
            elif avg_score < 70:
                recommendations.append("可以优化引擎选择策略，提高协同效率")
            else:
                recommendations.append("协同策略运行良好，可保持当前配置")

        # 基于团队规模建议
        active_teams = self.collaboration_state.get("active_teams", [])
        if active_teams:
            avg_size = sum(len(t.get("members", [])) for t in active_teams) / len(active_teams)
            if avg_size > 5:
                recommendations.append("平均协同团队规模较大，考虑优化为更精简的组合")

        if not recommendations:
            recommendations.append("系统运行正常，继续保持当前协同策略")

        return recommendations


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(
        description="智能协同与自主决策增强引擎"
    )
    parser.add_argument(
        "command",
        choices=["recommend", "evaluate", "insights"],
        help="执行命令"
    )
    parser.add_argument(
        "--task",
        type=str,
        help="任务描述（用于 recommend 命令）"
    )
    parser.add_argument(
        "--team-id",
        type=str,
        help="团队ID（用于 evaluate 命令）"
    )
    parser.add_argument(
        "--result",
        type=str,
        help="执行结果 JSON 字符串（用于 evaluate 命令）"
    )

    args = parser.parse_args()

    enhancer = EvolutionCollaborationIntelligenceEnhancer()

    if args.command == "recommend":
        if not args.task:
            print("错误: --task 参数为必填")
            sys.exit(1)

        result = enhancer.get_collaboration_recommendation(args.task)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "evaluate":
        if not args.team_id or not args.result:
            print("错误: --team-id 和 --result 参数为必填")
            sys.exit(1)

        try:
            execution_result = json.loads(args.result)
        except json.JSONDecodeError:
            print("错误: --result 必须是有效的 JSON 字符串")
            sys.exit(1)

        result = enhancer.evaluate_collaboration_effectiveness(args.team_id, execution_result)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "insights":
        result = enhancer.get_collaboration_insights()
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()