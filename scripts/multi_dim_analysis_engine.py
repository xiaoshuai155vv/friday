#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
智能多维融合智能分析引擎 (Multi-Dimensional Analysis Engine)

集成系统自检、主动服务、预测预防等引擎的洞察，
实现统一的智能态势感知与跨引擎协同增强。

功能：
1. 多维度数据融合 - 整合系统健康、引擎状态、用户行为等多维度数据
2. 智能态势感知 - 基于融合数据提供统一的智能态势分析
3. 跨引擎协同增强 - 分析引擎间协同模式，提供协同优化建议
4. 前瞻性洞察 - 预测潜在问题，提供预防性建议
5. 统一分析入口 - 提供单一入口获取系统全维度分析

用法:
  python multi_dim_analysis_engine.py analyze
  python multi_dim_analysis_engine.py situation
  python multi_dim_analysis_engine.py synergy
  python multi_dim_analysis_engine.py predict
  python multi_dim_analysis_engine.py full
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional

# 路径配置
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
STATE_DIR = os.path.join(PROJECT_ROOT, "runtime", "state")

# 尝试导入各引擎的类
sys.path.insert(0, SCRIPT_DIR)

try:
    from system_health_report_engine import SystemHealthReportEngine
except ImportError:
    SystemHealthReportEngine = None

try:
    from health_assurance_loop import HealthAssuranceLoop
except ImportError:
    HealthAssuranceLoop = None


def load_state_file(filename: str) -> Dict[str, Any]:
    """加载状态文件"""
    filepath = os.path.join(STATE_DIR, filename)
    if not os.path.exists(filepath):
        return {}
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}


def get_current_mission() -> Dict[str, Any]:
    """获取当前任务状态"""
    return load_state_file("current_mission.json")


def get_evolution_completed() -> List[Dict[str, Any]]:
    """获取已完成的进化项"""
    completed = []
    if not os.path.exists(STATE_DIR):
        return completed

    for f in os.listdir(STATE_DIR):
        if f.startswith("evolution_completed_") and f.endswith(".json"):
            try:
                with open(os.path.join(STATE_DIR, f), 'r', encoding='utf-8') as fp:
                    data = json.load(fp)
                    completed.append({
                        "file": f,
                        "goal": data.get("current_goal", ""),
                        "status": data.get("status", ""),
                        "round": data.get("loop_round", 0),
                        "completed_at": data.get("completed_at", "")
                    })
            except Exception:
                pass

    # 按 round 排序，取最近的 10 个
    completed = sorted(completed, key=lambda x: x.get("round", 0), reverse=True)[:10]
    return completed


def get_recent_behavior_logs() -> List[Dict[str, Any]]:
    """获取最近的行为日志"""
    logs_file = os.path.join(PROJECT_ROOT, "runtime", "state", "recent_logs.json")
    if not os.path.exists(logs_file):
        return []

    try:
        with open(logs_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("logs", [])[-20:]  # 取最近 20 条
    except Exception:
        return []


class MultiDimAnalysisEngine:
    """智能多维融合智能分析引擎"""

    def __init__(self):
        """初始化多维分析引擎"""
        self.project_root = PROJECT_ROOT
        self.scripts_dir = SCRIPT_DIR
        self.state_dir = STATE_DIR

        # 初始化各引擎
        self.health_report_engine = SystemHealthReportEngine() if SystemHealthReportEngine else None
        self.health_assurance_loop = HealthAssuranceLoop() if HealthAssuranceLoop else None

    def analyze_system_health(self) -> Dict[str, Any]:
        """分析系统健康维度"""
        if self.health_report_engine:
            try:
                report = self.health_report_engine.generate_health_report()
                return {
                    "dimension": "system_health",
                    "data": report,
                    "status": "ok",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            except Exception as e:
                return {
                    "dimension": "system_health",
                    "error": str(e),
                    "status": "error",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
        return {
            "dimension": "system_health",
            "error": "健康报告引擎不可用",
            "status": "unavailable",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    def analyze_assurance_loop(self) -> Dict[str, Any]:
        """分析健康保障维度"""
        if self.health_assurance_loop:
            try:
                status = self.health_assurance_loop.get_status()
                return {
                    "dimension": "health_assurance",
                    "data": status,
                    "status": "ok",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            except Exception as e:
                return {
                    "dimension": "health_assurance",
                    "error": str(e),
                    "status": "error",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
        return {
            "dimension": "health_assurance",
            "error": "健康保障引擎不可用",
            "status": "unavailable",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    def analyze_evolution_state(self) -> Dict[str, Any]:
        """分析进化状态维度"""
        try:
            mission = get_current_mission()
            completed = get_evolution_completed()

            return {
                "dimension": "evolution",
                "data": {
                    "current_mission": mission,
                    "recent_completed": completed
                },
                "status": "ok",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            return {
                "dimension": "evolution",
                "error": str(e),
                "status": "error",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

    def analyze_behavior_patterns(self) -> Dict[str, Any]:
        """分析行为模式维度"""
        try:
            logs = get_recent_behavior_logs()

            # 分析行为模式
            phases = {}
            for log in logs:
                phase = log.get("phase", "unknown")
                phases[phase] = phases.get(phase, 0) + 1

            return {
                "dimension": "behavior_patterns",
                "data": {
                    "total_logs": len(logs),
                    "phase_distribution": phases,
                    "recent_logs": logs[-5:] if logs else []
                },
                "status": "ok",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            return {
                "dimension": "behavior_patterns",
                "error": str(e),
                "status": "error",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

    def analyze_engine_synergy(self) -> Dict[str, Any]:
        """分析引擎协同模式"""
        try:
            # 扫描所有引擎文件
            engines = []
            for f in os.listdir(self.scripts_dir):
                if f.endswith("_engine.py") or f.endswith("_orchestrator.py") or f.endswith("_hub.py"):
                    engines.append(f)

            # 分析最近完成的进化项中的引擎组合
            completed = get_evolution_completed()
            recent_goals = [c.get("goal", "") for c in completed[:5]]

            # 识别协同模式
            synergy_patterns = []
            for goal in recent_goals:
                if "统一" in goal or "集成" in goal or "协同" in goal:
                    synergy_patterns.append(goal)

            return {
                "dimension": "engine_synergy",
                "data": {
                    "total_engines": len(engines),
                    "engine_list": sorted(engines),
                    "synergy_patterns": synergy_patterns,
                    "recent_collaborations": len(synergy_patterns)
                },
                "status": "ok",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            return {
                "dimension": "engine_synergy",
                "error": str(e),
                "status": "error",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

    def generate_situation_awareness(self) -> Dict[str, Any]:
        """生成统一智能态势感知"""
        try:
            # 收集各维度数据
            dims = [
                self.analyze_system_health(),
                self.analyze_assurance_loop(),
                self.analyze_evolution_state(),
                self.analyze_behavior_patterns(),
                self.analyze_engine_synergy()
            ]

            # 计算综合态势评分
            score = 100
            issues = []

            # 系统健康维度
            health = dims[0]
            if health.get("status") == "ok":
                health_score = health.get("data", {}).get("health_score", {})
                h_level = health_score.get("level", "unknown")
                if h_level == "poor":
                    score -= 20
                    issues.append("系统健康状况较差")
                elif h_level == "fair":
                    score -= 10
                    issues.append("系统健康状况一般")

            # 进化状态维度
            evolution = dims[2]
            if evolution.get("status") == "ok":
                mission = evolution.get("data", {}).get("current_mission", {})
                if not mission.get("current_goal"):
                    score -= 5
                    issues.append("当前无明确进化目标")

            # 引擎协同维度
            synergy = dims[4]
            if synergy.get("status") == "ok":
                recent_collab = synergy.get("data", {}).get("recent_collaborations", 0)
                if recent_collab == 0:
                    issues.append("近期无引擎协同进化")

            return {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "dimensions": dims,
                "situation_score": max(0, score),
                "situation_level": "excellent" if score >= 90 else "good" if score >= 70 else "fair" if score >= 50 else "poor",
                "issues": issues,
                "summary": self._generate_summary(dims, score, issues)
            }
        except Exception as e:
            return {
                "error": str(e),
                "status": "error",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

    def _generate_summary(self, dims: List[Dict], score: int, issues: List[str]) -> str:
        """生成态势摘要"""
        lines = [
            "=== 智能态势感知报告 ===",
            f"综合态势评分: {score}/100",
            f"态势等级: {'优秀' if score >= 90 else '良好' if score >= 70 else '一般' if score >= 50 else '需关注'}",
            ""
        ]

        # 系统健康
        health = dims[0]
        if health.get("status") == "ok":
            health_score = health.get("data", {}).get("health_score", {})
            lines.append(f"系统健康: {health_score.get('score', 0)}/100 ({health_score.get('level', 'unknown')})")

        # 引擎数量
        synergy = dims[4]
        if synergy.get("status") == "ok":
            total = synergy.get("data", {}).get("total_engines", 0)
            lines.append(f"引擎总数: {total}")

        # 进化轮次
        evolution = dims[2]
        if evolution.get("status") == "ok":
            mission = evolution.get("data", {}).get("current_mission", {})
            round_num = mission.get("loop_round", 0)
            lines.append(f"当前进化轮次: {round_num}")

        # 问题列表
        if issues:
            lines.append("")
            lines.append("需要关注:")
            for issue in issues:
                lines.append(f"  - {issue}")

        return "\n".join(lines)

    def generate_predictive_insights(self) -> Dict[str, Any]:
        """生成预测性洞察"""
        try:
            # 基于当前态势和历史数据预测
            situation = self.generate_situation_awareness()

            insights = []

            # 基于系统健康预测
            health = situation.get("dimensions", [])[0]
            if health.get("status") == "ok":
                health_score = health.get("data", {}).get("health_score", {})
                if health_score.get("level") == "fair":
                    insights.append({
                        "type": "warning",
                        "category": "system_health",
                        "message": "系统健康状况一般，建议关注资源使用情况",
                        "recommendation": "可运行健康检查并根据建议优化"
                    })

            # 基于引擎协同预测
            synergy = situation.get("dimensions", [])[4]
            if synergy.get("status") == "ok":
                recent_collab = synergy.get("data", {}).get("recent_collaborations", 0)
                if recent_collab < 3:
                    insights.append({
                        "type": "suggestion",
                        "category": "engine_collaboration",
                        "message": "近期引擎协同较少，可能存在优化空间",
                        "recommendation": "可探索引擎组合优化或创建新的协同引擎"
                    })

            # 基于进化状态预测
            mission = get_current_mission()
            if not mission.get("current_goal"):
                insights.append({
                    "type": "action",
                    "category": "evolution",
                    "message": "当前无明确进化目标",
                    "recommendation": "建议进入假设阶段，确定下一轮进化方向"
                })

            # 如果没有发现任何问题，添加积极洞察
            if not insights:
                insights.append({
                    "type": "positive",
                    "category": "overall",
                    "message": "系统运行良好，各项指标正常",
                    "recommendation": "继续保持当前状态，持续监控"
                })

            return {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "insights": insights,
                "prediction_count": len(insights)
            }
        except Exception as e:
            return {
                "error": str(e),
                "status": "error",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

    def generate_cross_enhancement_suggestions(self) -> Dict[str, Any]:
        """生成跨引擎协同增强建议"""
        try:
            suggestions = []

            # 分析引擎文件
            engines = []
            for f in os.listdir(self.scripts_dir):
                if f.endswith("_engine.py") or f.endswith("_orchestrator.py") or f.endswith("_hub.py"):
                    engines.append(f.replace(".py", ""))

            # 基于当前态势提供协同建议
            situation = self.generate_situation_awareness()
            score = situation.get("situation_score", 100)

            if score < 90:
                suggestions.append({
                    "category": "health_enhancement",
                    "suggestion": "建议加强系统健康保障与自检引擎的联动",
                    "engines": ["system_health_report_engine", "health_assurance_loop"],
                    "priority": "high" if score < 70 else "medium"
                })

            # 检查是否有足够的主动服务能力
            proactive_engines = [e for e in engines if "proactive" in e or "predict" in e]
            if len(proactive_engines) < 2:
                suggestions.append({
                    "category": "proactive_enhancement",
                    "suggestion": "建议增强主动服务与预测预防能力",
                    "engines": ["proactive_service", "predictive_prevention"],
                    "priority": "medium"
                })

            # 检查统一服务能力
            unified_engines = [e for e in engines if "unified" in e or "hub" in e]
            if len(unified_engines) < 3:
                suggestions.append({
                    "category": "unified_enhancement",
                    "suggestion": "建议增强统一服务中枢能力，整合更多引擎入口",
                    "engines": ["unified_service_hub"],
                    "priority": "low"
                })

            if not suggestions:
                suggestions.append({
                    "category": "status_quo",
                    "suggestion": "当前引擎协同状态良好，暂无需强制的跨引擎增强",
                    "engines": [],
                    "priority": "info"
                })

            return {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "suggestions": suggestions,
                "total_engines": len(engines)
            }
        except Exception as e:
            return {
                "error": str(e),
                "status": "error",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

    def full_analysis(self) -> Dict[str, Any]:
        """执行全维度分析"""
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "round": 204,
            "situation_awareness": self.generate_situation_awareness(),
            "predictive_insights": self.generate_predictive_insights(),
            "cross_enhancement": self.generate_cross_enhancement_suggestions()
        }

    def run_analysis(self, analysis_type: str = "full") -> str:
        """运行分析并返回结果"""
        if analysis_type == "situation":
            result = self.generate_situation_awareness()
        elif analysis_type == "synergy":
            result = self.generate_cross_enhancement_suggestions()
        elif analysis_type == "predict":
            result = self.generate_predictive_insights()
        else:  # full
            result = self.full_analysis()

        return json.dumps(result, ensure_ascii=False, indent=2)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="智能多维融合智能分析引擎")
    parser.add_argument("action", nargs="?", default="full",
                        choices=["analyze", "situation", "synergy", "predict", "full"],
                        help="分析类型")
    parser.add_argument("--output", choices=["json", "summary"], default="json",
                        help="输出格式")

    args = parser.parse_args()

    engine = MultiDimAnalysisEngine()
    result = engine.run_analysis(args.action)

    print(result)


if __name__ == "__main__":
    main()