"""
智能全场景进化环全局态势感知与自适应决策增强引擎
版本: 1.0.0
功能: 让系统从全局视角感知70+引擎的整体运行状态、进化环健康度、知识图谱完整性等多维度信息，
      并基于这些信息自适应调整进化决策，实现更高级的自主智能

核心能力:
- 多维度全局态势感知（引擎状态、进化效率、知识图谱、健康指标、决策质量）
- 智能态势分析（多维度信息融合分析，识别关键优化点）
- 自适应决策增强（基于态势动态调整进化策略）
- 动态优化建议生成

作者: Claude Sonnet 4.6
日期: 2026-03-14
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict


class EvolutionGlobalSituationAwarenessEngine:
    """全局态势感知与自适应决策增强引擎主类"""

    VERSION = "1.0.0"

    def __init__(self):
        self.name = "Evolution Global Situation Awareness Engine"
        self.project_root = Path(__file__).parent.parent
        self.scripts_dir = self.project_root / "scripts"
        self.runtime_dir = self.project_root / "runtime"
        self.state_dir = self.runtime_dir / "state"
        self.logs_dir = self.runtime_dir / "logs"

        # 态势数据缓存
        self.situation_data: Dict[str, Any] = {}
        self.analysis_results: Dict[str, Any] = {}
        self.decision_enhancements: Dict[str, Any] = {}

    def get_engine_states(self) -> Dict[str, Any]:
        """获取各引擎的运行状态"""
        engine_states = {
            "timestamp": datetime.now().isoformat(),
            "total_engines": 0,
            "active_engines": 0,
            "healthy_engines": 0,
            "warning_engines": 0,
            "error_engines": 0,
            "engine_details": {}
        }

        # 统计 scripts 目录下的进化引擎数量
        evolution_engines = list(self.scripts_dir.glob("evolution_*.py"))
        engine_states["total_engines"] = len(evolution_engines)

        # 检查各引擎的健康状态（通过检查文件修改时间和错误日志）
        current_time = datetime.now()
        for engine_file in evolution_engines:
            engine_name = engine_file.stem

            # 检查最近的错误日志
            error_count = 0
            log_file = self.logs_dir / f"{engine_name}.log"
            if log_file.exists():
                try:
                    with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        error_count = content.lower().count('error') + content.lower().count('failed')

                    # 检查文件修改时间
                    mtime = datetime.fromtimestamp(engine_file.stat().st_mtime)
                    age_hours = (current_time - mtime).total_seconds() / 3600

                    # 判断健康状态
                    if error_count > 10:
                        status = "error"
                        engine_states["error_engines"] += 1
                    elif error_count > 3 or age_hours > 168:  # 一周未更新
                        status = "warning"
                        engine_states["warning_engines"] += 1
                    else:
                        status = "healthy"
                        engine_states["healthy_engines"] += 1

                    engine_states["active_engines"] += 1

                    engine_states["engine_details"][engine_name] = {
                        "status": status,
                        "last_modified": mtime.isoformat(),
                        "age_hours": round(age_hours, 1),
                        "error_count": error_count
                    }
                except Exception as e:
                    engine_states["engine_details"][engine_name] = {
                        "status": "unknown",
                        "error": str(e)
                    }

        return engine_states

    def get_evolution_efficiency(self) -> Dict[str, Any]:
        """获取进化效率数据"""
        efficiency_data = {
            "timestamp": datetime.now().isoformat(),
            "rounds_completed": 0,
            "rounds_in_progress": 0,
            "average_completion_time_hours": 0,
            "success_rate": 0.0,
            "efficiency_trend": "stable",
            "recent_rounds": []
        }

        # 读取 evolution_completed_*.json 文件统计
        if self.state_dir.exists():
            completed_files = list(self.state_dir.glob("evolution_completed_ev_*.json"))
            efficiency_data["rounds_completed"] = len(completed_files)

            # 分析最近10轮的完成情况
            recent_files = sorted(completed_files, key=lambda x: x.stat().st_mtime, reverse=True)[:10]

            completion_times = []
            success_count = 0

            for f in recent_files:
                try:
                    with open(f, 'r', encoding='utf-8') as fp:
                        data = json.load(fp)
                        if "做了什么" in data:
                            efficiency_data["recent_rounds"].append({
                                "round": data.get("loop_round", "unknown"),
                                "goal": data.get("current_goal", "")[:50],
                                "completed": data.get("是否完成", "未知") == "已完成"
                            })

                        # 检查是否标记为完成
                        if data.get("是否完成") == "已完成":
                            success_count += 1

                        # 计算完成时间（如果可用）
                        if "updated_at" in data and "created_at" in data:
                            try:
                                created = datetime.fromisoformat(data["created_at"])
                                updated = datetime.fromisoformat(data["updated_at"])
                                hours = (updated - created).total_seconds() / 3600
                                completion_times.append(hours)
                            except:
                                pass
                except:
                    pass

            if completion_times:
                efficiency_data["average_completion_time_hours"] = round(sum(completion_times) / len(completion_times), 1)

            if efficiency_data["recent_rounds"]:
                efficiency_data["success_rate"] = round(success_count / len(efficiency_data["recent_rounds"]) * 100, 1)

            # 计算效率趋势
            if len(completion_times) >= 5:
                first_half = sum(completion_times[:len(completion_times)//2]) / (len(completion_times)//2)
                second_half = sum(completion_times[len(completion_times)//2:]) / (len(completion_times) - len(completion_times)//2)
                if second_half < first_half * 0.8:
                    efficiency_data["efficiency_trend"] = "improving"
                elif second_half > first_half * 1.2:
                    efficiency_data["efficiency_trend"] = "declining"

        return efficiency_data

    def get_knowledge_graph_completeness(self) -> Dict[str, Any]:
        """获取知识图谱完整性"""
        kg_data = {
            "timestamp": datetime.now().isoformat(),
            "kg_files": 0,
            "total_entities": 0,
            "total_relations": 0,
            "completeness_score": 0.0,
            "last_updated": None,
            "coverage_areas": []
        }

        # 检查知识图谱相关文件
        kg_files = list(self.state_dir.glob("*knowledge*.json")) + \
                   list(self.state_dir.glob("*graph*.json"))

        kg_data["kg_files"] = len(kg_files)

        total_entities = 0
        total_relations = 0

        for f in kg_files:
            try:
                with open(f, 'r', encoding='utf-8') as fp:
                    data = json.load(fp)
                    if isinstance(data, dict):
                        total_entities += len(data.get("entities", data.get("nodes", [])))
                        total_relations += len(data.get("relations", data.get("edges", [])))

                        # 更新最后更新时间
                        mtime = datetime.fromtimestamp(f.stat().st_mtime)
                        if kg_data["last_updated"] is None or mtime > kg_data["last_updated"]:
                            kg_data["last_updated"] = mtime.isoformat()
            except:
                pass

        kg_data["total_entities"] = total_entities
        kg_data["total_relations"] = total_relations

        # 估算完整性分数（基于实体和关系数量）
        completeness = min(100, (total_entities / 1000) * 50 + (total_relations / 2000) * 50)
        kg_data["completeness_score"] = round(completeness, 1)

        # 覆盖领域
        kg_data["coverage_areas"] = ["evolution_history", "engine_capabilities", "failure_patterns", "user_scenarios"]

        return kg_data

    def get_health_metrics(self) -> Dict[str, Any]:
        """获取健康指标"""
        health_data = {
            "timestamp": datetime.now().isoformat(),
            "overall_health_score": 0.0,
            "cpu_usage": 0,
            "memory_usage": 0,
            "disk_usage": 0,
            "process_count": 0,
            "system_stability": "unknown",
            "daemon_status": {}
        }

        # 读取系统健康报告
        health_report_file = self.state_dir / "system_health_report.json"
        if health_report_file.exists():
            try:
                with open(health_report_file, 'r', encoding='utf-8') as f:
                    health_data = json.load(f)
            except:
                pass

        # 检查守护进程状态
        daemon_files = list(self.logs_dir.glob("daemon*.log"))
        for daemon_log in daemon_files:
            daemon_name = daemon_log.stem
            try:
                with open(daemon_log, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    last_line = content.strip().split('\n')[-1] if content else ""
                    health_data["daemon_status"][daemon_name] = "running" if last_line else "stopped"
            except:
                health_data["daemon_status"][daemon_name] = "unknown"

        return health_data

    def get_decision_quality(self) -> Dict[str, Any]:
        """获取决策质量数据"""
        decision_data = {
            "timestamp": datetime.now().isoformat(),
            "decisions_made": 0,
            "successful_decisions": 0,
            "decision_accuracy_rate": 0.0,
            "avg_decision_time_ms": 0,
            "decision_patterns": [],
            "improvement_suggestions": []
        }

        # 从行为日志分析决策质量
        behavior_files = list(self.logs_dir.glob("behavior_*.log"))
        if behavior_files:
            recent_file = sorted(behavior_files, key=lambda x: x.stat().st_mtime, reverse=True)[0]

            decision_count = 0
            success_count = 0
            decision_times = []

            try:
                with open(recent_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    lines = content.split('\n')

                    for line in lines:
                        if '"phase": "决策"' in line or '"phase": "规划"' in line:
                            decision_count += 1
                            if '"result": "pass"' in line:
                                success_count += 1

                    decision_data["decisions_made"] = decision_count
                    decision_data["successful_decisions"] = success_count

                    if decision_count > 0:
                        decision_data["decision_accuracy_rate"] = round(success_count / decision_count * 100, 1)
            except:
                pass

        return decision_data

    def perceive_global_situation(self) -> Dict[str, Any]:
        """执行全局态势感知"""
        print("=" * 60)
        print("全局态势感知中...")
        print("=" * 60)

        situation = {
            "timestamp": datetime.now().isoformat(),
            "engines": self.get_engine_states(),
            "efficiency": self.get_evolution_efficiency(),
            "knowledge_graph": self.get_knowledge_graph_completeness(),
            "health": self.get_health_metrics(),
            "decision_quality": self.get_decision_quality()
        }

        # 计算综合态势分数
        engine_health_score = (situation["engines"]["healthy_engines"] /
                              max(1, situation["engines"]["total_engines"]) * 100)
        efficiency_score = situation["efficiency"]["success_rate"]
        kg_score = situation["knowledge_graph"]["completeness_score"]
        health_score = situation["health"].get("overall_health_score", 50)
        decision_score = situation["decision_quality"]["decision_accuracy_rate"]

        situation["overall_situation_score"] = round(
            (engine_health_score * 0.2 +
             efficiency_score * 0.25 +
             kg_score * 0.15 +
             health_score * 0.2 +
             decision_score * 0.2), 1
        )

        self.situation_data = situation

        print(f"\n综合态势分数: {situation['overall_situation_score']}/100")
        print(f"  - 引擎健康度: {engine_health_score:.1f}/100")
        print(f"  - 进化效率: {efficiency_score:.1f}/100")
        print(f"  - 知识图谱完整度: {kg_score:.1f}/100")
        print(f"  - 系统健康度: {health_score:.1f}/100")
        print(f"  - 决策质量: {decision_score:.1f}/100")

        return situation

    def analyze_situation(self, situation: Dict[str, Any]) -> Dict[str, Any]:
        """智能态势分析 - 识别关键优化点"""
        print("\n" + "=" * 60)
        print("智能态势分析中...")
        print("=" * 60)

        analysis = {
            "timestamp": datetime.now().isoformat(),
            "key_findings": [],
            "optimization_opportunities": [],
            "risk_factors": [],
            "priority_actions": []
        }

        # 分析引擎状态
        if situation["engines"]["warning_engines"] > 5:
            analysis["risk_factors"].append({
                "type": "engine_health",
                "severity": "high",
                "description": f"{situation['engines']['warning_engines']} 个引擎存在警告",
                "recommendation": "检查并修复警告引擎"
            })

        # 分析进化效率
        if situation["efficiency"]["efficiency_trend"] == "declining":
            analysis["risk_factors"].append({
                "type": "efficiency_trend",
                "severity": "medium",
                "description": "进化效率呈下降趋势",
                "recommendation": "分析效率下降原因并优化"
            })

        # 分析知识图谱
        if situation["knowledge_graph"]["completeness_score"] < 50:
            analysis["optimization_opportunities"].append({
                "type": "knowledge_graph",
                "priority": "high",
                "description": "知识图谱完整性不足",
                "recommendation": "增加知识积累和图谱建设"
            })

        # 分析决策质量
        if situation["decision_quality"]["decision_accuracy_rate"] < 70:
            analysis["key_findings"].append({
                "type": "decision_quality",
                "severity": "medium",
                "description": f"决策准确率仅 {situation['decision_quality']['decision_accuracy_rate']}%",
                "recommendation": "优化决策算法和策略"
            })

        # 综合态势分析
        overall = situation.get("overall_situation_score", 0)
        if overall >= 80:
            analysis["key_findings"].append({
                "type": "overall_status",
                "description": "系统整体态势良好",
                "recommendation": "保持现状，持续监控"
            })
        elif overall >= 60:
            analysis["key_findings"].append({
                "type": "overall_status",
                "description": "系统整体态势一般",
                "recommendation": "关注薄弱环节，持续优化"
            })
        else:
            analysis["key_findings"].append({
                "type": "overall_status",
                "severity": "high",
                "description": "系统整体态势需要关注",
                "recommendation": "优先处理关键问题"
            })

        # 生成优先级行动
        analysis["priority_actions"] = [
            {
                "priority": 1,
                "action": "持续监控各引擎运行状态",
                "reason": "确保系统稳定运行"
            },
            {
                "priority": 2,
                "action": "优化进化效率",
                "reason": "提升进化质量"
            },
            {
                "priority": 3,
                "action": "完善知识图谱",
                "reason": "增强决策支持能力"
            }
        ]

        # 添加风险因子到优先级行动
        for risk in analysis["risk_factors"]:
            if risk["severity"] == "high":
                analysis["priority_actions"].insert(0, {
                    "priority": 0,
                    "action": risk["recommendation"],
                    "reason": f"高优先级风险: {risk['description']}"
                })

        self.analysis_results = analysis

        # 打印分析结果
        print(f"\n关键发现: {len(analysis['key_findings'])} 项")
        for finding in analysis["key_findings"]:
            print(f"  - {finding['description']}")

        print(f"\n优化机会: {len(analysis['optimization_opportunities'])} 项")
        for opt in analysis["optimization_opportunities"]:
            print(f"  - {opt['description']}")

        print(f"\n风险因子: {len(analysis['risk_factors'])} 项")
        for risk in analysis["risk_factors"]:
            print(f"  - [{risk['severity'].upper()}] {risk['description']}")

        return analysis

    def enhance_adaptive_decision(self, situation: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """自适应决策增强"""
        print("\n" + "=" * 60)
        print("自适应决策增强中...")
        print("=" * 60)

        enhancements = {
            "timestamp": datetime.now().isoformat(),
            "strategy_adjustments": [],
            "resource_allocations": [],
            "optimization_suggestions": []
        }

        # 基于态势的策略调整
        overall_score = situation.get("overall_situation_score", 0)

        if overall_score >= 80:
            enhancements["strategy_adjustments"].append({
                "type": "conservative",
                "description": "系统状态良好，采用保守进化策略",
                "rationale": "避免破坏稳定状态"
            })
        elif overall_score >= 60:
            enhancements["strategy_adjustments"].append({
                "type": "balanced",
                "description": "系统状态一般，采用平衡进化策略",
                "rationale": "兼顾效率与稳定"
            })
        else:
            enhancements["strategy_adjustments"].append({
                "type": "aggressive",
                "description": "系统状态需要关注，采用积极优化策略",
                "rationale": "快速改善系统状态"
            })

        # 基于分析结果的自适应调整
        for risk in analysis.get("risk_factors", []):
            if risk["type"] == "engine_health":
                enhancements["resource_allocations"].append({
                    "resource": "engine_maintenance",
                    "priority": "high",
                    "action": "增加引擎健康检查频率"
                })

        for opt in analysis.get("optimization_opportunities", []):
            if opt["type"] == "knowledge_graph":
                enhancements["resource_allocations"].append({
                    "resource": "knowledge_accumulation",
                    "priority": "medium",
                    "action": "增加知识图谱建设投入"
                })

        # 生成优化建议
        enhancements["optimization_suggestions"] = [
            {
                "category": "strategy",
                "suggestion": "根据当前态势动态调整进化策略",
                "expected_impact": "提升进化效率"
            },
            {
                "category": "resources",
                "suggestion": "优化资源分配，优先处理高优先级问题",
                "expected_impact": "改善系统整体状态"
            },
            {
                "category": "monitoring",
                "suggestion": "加强关键指标监控，及时发现异常",
                "expected_impact": "提高系统稳定性"
            }
        ]

        self.decision_enhancements = enhancements

        # 打印决策增强结果
        print(f"\n策略调整: {len(enhancements['strategy_adjustments'])} 项")
        for adj in enhancements["strategy_adjustments"]:
            print(f"  - [{adj['type']}] {adj['description']}")

        print(f"\n资源配置: {len(enhancements['resource_allocations'])} 项")
        for alloc in enhancements["resource_allocations"]:
            print(f"  - [{alloc['priority']}] {alloc['action']}")

        return enhancements

    def generate_optimization_suggestions(self, situation: Dict[str, Any],
                                          analysis: Dict[str, Any],
                                          enhancements: Dict[str, Any]) -> Dict[str, Any]:
        """生成动态优化建议"""
        suggestions = {
            "timestamp": datetime.now().isoformat(),
            "short_term": [],
            "medium_term": [],
            "long_term": [],
            "execution_priority": []
        }

        # 短期建议（立即可执行）
        for risk in analysis.get("risk_factors", []):
            if risk["severity"] == "high":
                suggestions["short_term"].append({
                    "action": risk["recommendation"],
                    "reason": risk["description"],
                    "impact": "high"
                })

        # 中期建议（本周内执行）
        for opt in analysis.get("optimization_opportunities", []):
            suggestions["medium_term"].append({
                "action": opt["recommendation"],
                "reason": opt["description"],
                "impact": opt["priority"]
            })

        # 长期建议（持续改进）
        suggestions["long_term"] = [
            {
                "action": "构建更完善的全局态势感知体系",
                "reason": "提升系统自我感知能力",
                "impact": "high"
            },
            {
                "action": "增强自适应决策算法",
                "reason": "提高决策质量和效率",
                "impact": "high"
            },
            {
                "action": "建立动态资源优化机制",
                "reason": "实现智能资源分配",
                "impact": "medium"
            }
        ]

        # 执行优先级
        suggestions["execution_priority"] = [
            {"step": 1, "action": suggestions["short_term"][0]["action"] if suggestions["short_term"] else "监控态势"},
            {"step": 2, "action": "应用自适应策略调整" if enhancements["strategy_adjustments"] else "保持当前策略"},
            {"step": 3, "action": "执行资源配置建议" if enhancements["resource_allocations"] else "维持现状"}
        ]

        # 打印建议
        print("\n" + "=" * 60)
        print("优化建议生成完成")
        print("=" * 60)
        print(f"\n短期建议: {len(suggestions['short_term'])} 项")
        print(f"中期建议: {len(suggestions['medium_term'])} 项")
        print(f"长期建议: {len(suggestions['long_term'])} 项")

        return suggestions

    def run_full_cycle(self) -> Dict[str, Any]:
        """运行完整的态势感知与决策增强流程"""
        print("\n" + "=" * 60)
        print("进化环全局态势感知与自适应决策增强引擎")
        print(f"版本: {self.VERSION}")
        print("=" * 60)

        # 1. 全局态势感知
        situation = self.perceive_global_situation()

        # 2. 智能态势分析
        analysis = self.analyze_situation(situation)

        # 3. 自适应决策增强
        enhancements = self.enhance_adaptive_decision(situation, analysis)

        # 4. 生成优化建议
        suggestions = self.generate_optimization_suggestions(situation, analysis, enhancements)

        # 汇总结果
        result = {
            "timestamp": datetime.now().isoformat(),
            "version": self.VERSION,
            "situation": situation,
            "analysis": analysis,
            "enhancements": enhancements,
            "suggestions": suggestions,
            "overall_situation_score": situation.get("overall_situation_score", 0)
        }

        print("\n" + "=" * 60)
        print("完整流程执行完成")
        print(f"综合态势分数: {result['overall_situation_score']}/100")
        print("=" * 60)

        return result

    def get_status(self) -> Dict[str, Any]:
        """获取引擎状态"""
        return {
            "version": self.VERSION,
            "name": self.name,
            "capabilities": [
                "全局态势感知",
                "智能态势分析",
                "自适应决策增强",
                "动态优化建议生成"
            ]
        }


def main():
    """主函数 - 支持命令行调用"""
    import argparse

    parser = argparse.ArgumentParser(
        description="智能全场景进化环全局态势感知与自适应决策增强引擎"
    )
    parser.add_argument(
        "command",
        nargs="?",
        default="status",
        choices=["status", "perceive", "analyze", "enhance", "full-cycle"],
        help="执行命令: status=查看状态, perceive=态势感知, analyze=态势分析, enhance=决策增强, full-cycle=完整流程"
    )
    parser.add_argument("--output", "-o", help="输出 JSON 文件路径")

    args = parser.parse_args()
    engine = EvolutionGlobalSituationAwarenessEngine()

    if args.command == "status":
        result = engine.get_status()
    elif args.command == "perceive":
        result = engine.perceive_global_situation()
    elif args.command == "analyze":
        situation = engine.perceive_global_situation()
        result = engine.analyze_situation(situation)
    elif args.command == "enhance":
        situation = engine.perceive_global_situation()
        analysis = engine.analyze_situation(situation)
        result = engine.enhance_adaptive_decision(situation, analysis)
    else:  # full-cycle
        result = engine.run_full_cycle()

    # 输出结果
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n结果已保存到: {args.output}")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))

    return result


if __name__ == "__main__":
    main()