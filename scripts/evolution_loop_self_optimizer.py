#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能进化闭环自我优化引擎 (Evolution Loop Self-Optimizer)
让系统能够自动分析自身执行效果、智能调整进化策略参数、自动识别优化机会，
实现真正的自主迭代优化能力，形成「分析→优化→执行→验证」的完整闭环。

功能：
1. 进化执行效果分析 - 分析最近N轮的完成情况、效率、趋势
2. 策略参数自动调整 - 基于分析结果自动调整进化策略参数
3. 优化机会自动识别 - 识别低效、重复、可改进点
4. 自我优化建议生成 - 生成可执行的优化建议

集成：支持"进化自我优化"、"闭环优化"、"自我迭代"、"优化进化环"等关键词触发
"""

import os
import sys
import json
import glob
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict

SCRIPTS = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(SCRIPTS)
RUNTIME_STATE = os.path.join(PROJECT, "runtime", "state")
RUNTIME_LOGS = os.path.join(PROJECT, "runtime", "logs")
REFERENCES = os.path.join(PROJECT, "references")


class EvolutionLoopSelfOptimizer:
    """智能进化闭环自我优化引擎"""

    def __init__(self):
        self.name = "EvolutionLoopSelfOptimizer"
        self.version = "1.0.0"
        self.config_path = os.path.join(RUNTIME_STATE, "evolution_loop_self_optimizer_config.json")
        self.analysis_path = os.path.join(RUNTIME_STATE, "evolution_loop_analysis.json")
        self.optimization_history_path = os.path.join(RUNTIME_STATE, "evolution_optimization_history.json")

        self.config = self._load_config()
        self.analysis = self._load_analysis()
        self.optimization_history = self._load_optimization_history()

    def _load_config(self) -> Dict:
        """加载配置"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass

        # 默认配置
        return {
            "analysis_settings": {
                "rounds_to_analyze": 30,  # 分析最近30轮
                "min_rounds_for_trend": 5,  # 至少5轮才能分析趋势
                "efficiency_threshold": 0.7,  # 效率阈值
                "trend_significance": 0.2  # 趋势显著性
            },
            "optimization_settings": {
                "auto_adjust_params": True,  # 自动调整参数
                "auto_execute_suggestions": False,  # 自动执行建议
                "max_optimizations_per_round": 3,  # 每轮最多优化次数
                "conservative_mode": True  # 保守模式（防止过度优化）
            },
            "strategy_params": {
                "assume_phase_weight": 0.2,  # 假设阶段权重
                "decision_phase_weight": 0.25,  # 决策阶段权重
                "execution_phase_weight": 0.3,  # 执行阶段权重
                "verify_phase_weight": 0.15,  # 校验阶段权重
                "reflect_phase_weight": 0.1,  # 反思阶段权重
                "risk_tolerance": 0.3,  # 风险容忍度
                "innovation_rate": 0.2  # 创新率
            },
            "thresholds": {
                "low_efficiency": 0.5,
                "medium_efficiency": 0.7,
                "high_efficiency": 0.85,
                "slow_execution_time": 600,  # 10分钟
                "optimization_interval": 3600  # 1小时
            },
            "last_optimization_time": None,
            "total_optimizations": 0
        }

    def _save_config(self):
        """保存配置"""
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存配置失败: {e}")

    def _load_analysis(self) -> Dict:
        """加载分析数据"""
        if os.path.exists(self.analysis_path):
            try:
                with open(self.analysis_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass

        return {
            "rounds_analyzed": [],
            "efficiency_trends": {},
            "bottlenecks": [],
            "opportunities": [],
            "last_analyzed": None
        }

    def _save_analysis(self):
        """保存分析数据"""
        try:
            self.analysis["last_analyzed"] = datetime.now().isoformat()
            with open(self.analysis_path, "w", encoding="utf-8") as f:
                json.dump(self.analysis, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存分析数据失败: {e}")

    def _load_optimization_history(self) -> Dict:
        """加载优化历史"""
        if os.path.exists(self.optimization_history_path):
            try:
                with open(self.optimization_history_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass

        return {
            "optimizations": [],
            "param_adjustments": [],
            "results": [],
            "last_updated": None
        }

    def _save_optimization_history(self):
        """保存优化历史"""
        try:
            self.optimization_history["last_updated"] = datetime.now().isoformat()
            with open(self.optimization_history_path, "w", encoding="utf-8") as f:
                json.dump(self.optimization_history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存优化历史失败: {e}")

    def _load_completed_evolutions(self, limit: int = 30) -> List[Dict]:
        """加载已完成的进化记录"""
        evolutions = []
        state_dir = RUNTIME_STATE

        # 查找所有 evolution_completed_*.json 文件
        pattern = os.path.join(state_dir, "evolution_completed_*.json")
        files = glob.glob(pattern)

        # 按修改时间排序
        files.sort(key=os.path.getmtime, reverse=True)

        for file in files[:limit]:
            try:
                with open(file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    evolutions.append(data)
            except Exception:
                continue

        return evolutions

    def analyze_execution_effectiveness(self) -> Dict[str, Any]:
        """分析执行效果"""
        rounds = self._load_completed_evolutions(self.config["analysis_settings"]["rounds_to_analyze"])

        if not rounds:
            return {
                "status": "no_data",
                "message": "暂无进化数据可供分析"
            }

        # 基本统计
        total_rounds = len(rounds)
        completed = sum(1 for r in rounds if r.get("status") == "completed" or r.get("is_completed") == True)
        failed = sum(1 for r in rounds if r.get("status") in ["failed", "error"] or r.get("is_completed") == False)
        incomplete = total_rounds - completed - failed

        # 成功率
        success_rate = completed / total_rounds if total_rounds > 0 else 0

        # 分析各阶段表现
        phase_analysis = self._analyze_phases(rounds)

        # 检测趋势
        trends = self._detect_trends(rounds)

        # 识别瓶颈
        bottlenecks = self._identify_bottlenecks(rounds, phase_analysis)

        # 识别优化机会
        opportunities = self._identify_opportunities(rounds, trends, bottlenecks)

        # 保存分析结果
        self.analysis = {
            "rounds_analyzed": total_rounds,
            "success_rate": success_rate,
            "completed": completed,
            "failed": failed,
            "incomplete": incomplete,
            "phase_analysis": phase_analysis,
            "trends": trends,
            "bottlenecks": bottlenecks,
            "opportunities": opportunities,
            "last_analyzed": datetime.now().isoformat()
        }
        self._save_analysis()

        return {
            "status": "analyzed",
            "summary": {
                "total_rounds": total_rounds,
                "success_rate": success_rate,
                "completed": completed,
                "failed": failed
            },
            "phase_analysis": phase_analysis,
            "trends": trends,
            "bottlenecks": bottlenecks,
            "opportunities": opportunities
        }

    def _analyze_phases(self, rounds: List[Dict]) -> Dict[str, Any]:
        """分析各阶段表现"""
        phases = {
            "假设": [],
            "决策": [],
            "执行": [],
            "校验": [],
            "反思": []
        }

        for round_data in rounds:
            # 从 current_goal 或做了什么中提取阶段信息
            goal = round_data.get("current_goal", "")
            if "假设" in goal or "假设" in str(round_data.get("做了什么", "")):
                phases["假设"].append(round_data)
            if "决策" in goal or "规划" in goal:
                phases["决策"].append(round_data)
            if "执行" in goal:
                phases["执行"].append(round_data)
            if "校验" in goal or "验证" in goal:
                phases["校验"].append(round_data)
            if "反思" in goal or "优化" in goal:
                phases["反思"].append(round_data)

        # 计算各阶段效率
        phase_efficiency = {}
        for phase, data in phases.items():
            if data:
                phase_completed = sum(1 for r in data if r.get("status") == "completed" or r.get("is_completed") == True)
                phase_efficiency[phase] = {
                    "count": len(data),
                    "completed": phase_completed,
                    "efficiency": phase_completed / len(data) if data else 0
                }
            else:
                phase_efficiency[phase] = {
                    "count": 0,
                    "completed": 0,
                    "efficiency": 0
                }

        return phase_efficiency

    def _detect_trends(self, rounds: List[Dict]) -> Dict[str, Any]:
        """检测趋势"""
        if len(rounds) < self.config["analysis_settings"]["min_rounds_for_trend"]:
            return {"status": "insufficient_data"}

        # 将数据分为前半和后半
        mid = len(rounds) // 2
        first_half = rounds[mid:]
        second_half = rounds[:mid]

        # 计算成功率趋势
        first_success = sum(1 for r in first_half if r.get("status") == "completed" or r.get("is_completed") == True) / len(first_half) if first_half else 0
        second_success = sum(1 for r in second_half if r.get("status") == "completed" or r.get("is_completed") == True) / len(second_half) if second_half else 0

        success_trend = second_success - first_success

        # 计算效率趋势（基于做了什么字段的长度）
        def calc_efficiency(r):
            content = str(r.get("做了什么", ""))
            return min(len(content) / 500, 1.0)  # 简化计算

        first_eff = sum(calc_efficiency(r) for r in first_half) / len(first_half) if first_half else 0
        second_eff = sum(calc_efficiency(r) for r in second_half) / len(second_half) if second_half else 0

        efficiency_trend = second_eff - first_eff

        return {
            "success_rate_trend": success_trend,
            "efficiency_trend": efficiency_trend,
            "trend_direction": "improving" if success_trend > 0.1 else ("declining" if success_trend < -0.1 else "stable"),
            "significance": abs(success_trend) > self.config["analysis_settings"]["trend_significance"]
        }

    def _identify_bottlenecks(self, rounds: List[Dict], phase_analysis: Dict) -> List[Dict]:
        """识别瓶颈"""
        bottlenecks = []

        # 找出效率最低的阶段
        for phase, data in phase_analysis.items():
            if data["count"] > 0 and data["efficiency"] < self.config["thresholds"]["low_efficiency"]:
                bottlenecks.append({
                    "type": "phase_bottleneck",
                    "phase": phase,
                    "efficiency": data["efficiency"],
                    "description": f"{phase}阶段效率较低 ({data['efficiency']:.1%})",
                    "severity": "high" if data["efficiency"] < 0.3 else "medium"
                })

        # 识别重复失败的模式
        failed_rounds = [r for r in rounds if r.get("status") in ["failed", "error"] or r.get("is_completed") == False]
        if len(failed_rounds) >= 3:
            bottlenecks.append({
                "type": "repeated_failures",
                "count": len(failed_rounds),
                "description": f"近期有 {len(failed_rounds)} 轮未完成或失败",
                "severity": "high"
            })

        return bottlenecks

    def _identify_opportunities(self, rounds: List[Dict], trends: Dict, bottlenecks: List[Dict]) -> List[Dict]:
        """识别优化机会"""
        opportunities = []

        # 机会1：成功率提升空间
        if trends.get("trend_direction") == "stable" and trends.get("success_rate_trend", 0) < 0.5:
            opportunities.append({
                "type": "success_rate_improvement",
                "description": "当前成功率有提升空间",
                "potential_impact": "high",
                "suggestion": "优化决策和执行阶段的策略"
            })

        # 机会2：效率优化
        if trends.get("efficiency_trend", 0) < 0:
            opportunities.append({
                "type": "efficiency_improvement",
                "description": "执行效率有下降趋势",
                "potential_impact": "medium",
                "suggestion": "优化执行流程，减少不必要的步骤"
            })

        # 机会3：瓶颈优化
        for bottleneck in bottlenecks:
            if bottleneck["severity"] == "high":
                opportunities.append({
                    "type": "bottleneck_resolution",
                    "description": bottleneck["description"],
                    "potential_impact": "high",
                    "suggestion": f"优先解决{bottleneck.get('phase', '该')}阶段的效率问题"
                })

        # 机会4：创新探索
        if len(rounds) >= 10:
            recent = rounds[:5]
            if all(r.get("status") == "completed" for r in recent):
                opportunities.append({
                    "type": "innovation_exploration",
                    "description": "近期表现稳定，可尝试创新方向",
                    "potential_impact": "medium",
                    "suggestion": "可探索新的进化方向或能力组合"
                })

        return opportunities

    def auto_adjust_params(self) -> Dict[str, Any]:
        """自动调整策略参数"""
        if not self.config["optimization_settings"]["auto_adjust_params"]:
            return {
                "status": "disabled",
                "message": "自动调整参数功能已禁用"
            }

        # 首先分析当前状态
        analysis = self.analyze_execution_effectiveness()

        if analysis.get("status") == "no_data":
            return {
                "status": "no_data",
                "message": "暂无数据可供优化"
            }

        original_params = dict(self.config["strategy_params"])
        adjustments = []
        new_params = dict(original_params)

        # 基于分析结果调整参数
        trends = analysis.get("trends", {})
        bottlenecks = analysis.get("bottlenecks", [])
        opportunities = analysis.get("opportunities", [])

        # 调整1：如果成功率下降，增加决策和校验权重
        if trends.get("trend_direction") == "declining":
            new_params["decision_phase_weight"] = min(0.4, original_params["decision_phase_weight"] + 0.1)
            new_params["verify_phase_weight"] = min(0.25, original_params["verify_phase_weight"] + 0.05)
            adjustments.append("增加决策和校验阶段权重以应对成功率下降")

        # 调整2：如果效率下降，增加执行权重
        if trends.get("efficiency_trend", 0) < -0.1:
            new_params["execution_phase_weight"] = min(0.45, original_params["execution_phase_weight"] + 0.1)
            adjustments.append("增加执行阶段权重以提升效率")

        # 调整3：解决瓶颈
        for bottleneck in bottlenecks:
            if bottleneck.get("phase") == "假设":
                new_params["assume_phase_weight"] = min(0.35, original_params["assume_phase_weight"] + 0.1)
                adjustments.append(f"增加{bottleneck['phase']}阶段权重")
            elif bottleneck.get("phase") == "执行":
                new_params["execution_phase_weight"] = min(0.45, original_params["execution_phase_weight"] + 0.1)
                adjustments.append(f"增加{bottleneck['phase']}阶段权重")

        # 调整4：保守模式
        if self.config["optimization_settings"]["conservative_mode"]:
            # 保守模式下，每次调整幅度不超过10%
            for key in new_params:
                if new_params[key] != original_params.get(key):
                    diff = new_params[key] - original_params[key]
                    if abs(diff) > 0.1:
                        new_params[key] = original_params[key] + (0.1 if diff > 0 else -0.1)
                        adjustments.append(f"保守模式：限制 {key} 调整幅度")

        # 确保权重总和为1
        total = sum(new_params.values())
        if abs(total - 1.0) > 0.01:
            for key in new_params:
                new_params[key] = new_params[key] / total

        # 保存调整记录
        self.config["strategy_params"] = new_params
        self.config["last_optimization_time"] = datetime.now().isoformat()
        self.config["total_optimizations"] = self.config.get("total_optimizations", 0) + 1
        self._save_config()

        # 记录到优化历史
        self.optimization_history["optimizations"].append({
            "time": datetime.now().isoformat(),
            "type": "auto_adjust_params",
            "adjustments": adjustments,
            "original_params": original_params,
            "new_params": new_params
        })
        self._save_optimization_history()

        return {
            "status": "adjusted",
            "original_params": original_params,
            "new_params": new_params,
            "adjustments": adjustments,
            "optimization_count": self.config["total_optimizations"]
        }

    def generate_optimization_suggestions(self) -> Dict[str, Any]:
        """生成优化建议"""
        # 先进行分析
        analysis = self.analyze_execution_effectiveness()

        if analysis.get("status") == "no_data":
            return {
                "status": "no_data",
                "suggestions": ["暂无足够数据生成优化建议"]
            }

        suggestions = []

        # 基于瓶颈生成建议
        for bottleneck in analysis.get("bottlenecks", []):
            if bottleneck["severity"] == "high":
                suggestions.append({
                    "priority": "high",
                    "category": "bottleneck",
                    "description": bottleneck["description"],
                    "action": bottleneck.get("suggestion", "分析并解决该问题"),
                    "auto_executable": True
                })

        # 基于机会生成建议
        for opportunity in analysis.get("opportunities", []):
            suggestions.append({
                "priority": "medium",
                "category": "opportunity",
                "description": opportunity["description"],
                "action": opportunity.get("suggestion", ""),
                "auto_executable": opportunity.get("potential_impact") == "high"
            })

        # 基于趋势生成建议
        trends = analysis.get("trends", {})
        if trends.get("trend_direction") == "declining":
            suggestions.append({
                "priority": "high",
                "category": "trend",
                "description": "整体趋势下降，需要关注",
                "action": "调用 auto_adjust_params() 自动调整策略参数",
                "auto_executable": True
            })
        elif trends.get("trend_direction") == "improving":
            suggestions.append({
                "priority": "low",
                "category": "trend",
                "description": "整体趋势向好",
                "action": "可尝试创新方向或优化细节",
                "auto_executable": False
            })

        # 添加参数调整建议
        if self.config["optimization_settings"]["auto_adjust_params"]:
            suggestions.append({
                "priority": "medium",
                "category": "optimization",
                "description": "可自动调整策略参数",
                "action": "运行 auto_adjust_params() 优化进化策略",
                "auto_executable": True
            })

        return {
            "status": "ready",
            "suggestions": suggestions,
            "summary": {
                "total": len(suggestions),
                "high_priority": len([s for s in suggestions if s["priority"] == "high"]),
                "auto_executable": len([s for s in suggestions if s.get("auto_executable", False)])
            }
        }

    def execute_optimization(self, suggestion_index: int = None) -> Dict[str, Any]:
        """执行优化建议"""
        suggestions = self.generate_optimization_suggestions()

        if suggestions.get("status") != "ready":
            return suggestions

        suggestion_list = suggestions.get("suggestions", [])

        # 如果没有指定建议索引，自动选择最高优先级的可执行建议
        if suggestion_index is None:
            executable = [s for s in suggestion_list if s.get("auto_executable", False)]
            if executable:
                suggestion = executable[0]
            else:
                return {
                    "status": "no_executable",
                    "message": "没有可自动执行的优化建议"
                }
        else:
            if suggestion_index < len(suggestion_list):
                suggestion = suggestion_list[suggestion_index]
            else:
                return {
                    "status": "invalid_index",
                    "message": f"建议索引无效，有效范围 0-{len(suggestion_list)-1}"
                }

        # 执行优化
        if "auto_adjust_params" in suggestion.get("action", "").lower() or suggestion.get("category") == "optimization":
            result = self.auto_adjust_params()
            result["executed_suggestion"] = suggestion["description"]
            return result
        else:
            return {
                "status": "manual_required",
                "message": f"该建议需要手动执行: {suggestion['action']}",
                "suggestion": suggestion
            }

    def get_self_optimization_status(self) -> Dict[str, Any]:
        """获取自我优化状态"""
        return {
            "name": self.name,
            "version": self.version,
            "config": {
                "auto_adjust": self.config["optimization_settings"]["auto_adjust_params"],
                "conservative_mode": self.config["optimization_settings"]["conservative_mode"],
                "total_optimizations": self.config.get("total_optimizations", 0),
                "last_optimization": self.config.get("last_optimization_time")
            },
            "current_params": self.config["strategy_params"],
            "analysis": {
                "rounds_analyzed": self.analysis.get("rounds_analyzed", 0),
                "last_analyzed": self.analysis.get("last_analyzed"),
                "success_rate": self.analysis.get("success_rate", 0),
                "bottleneck_count": len(self.analysis.get("bottlenecks", [])),
                "opportunity_count": len(self.analysis.get("opportunities", []))
            },
            "optimization_history": {
                "total": len(self.optimization_history.get("optimizations", []))
            }
        }

    def get_recommendations_for_next_round(self) -> Dict[str, Any]:
        """获取下一轮建议（供进化环在决策时调用）"""
        # 快速获取建议
        suggestions = self.generate_optimization_suggestions()

        if suggestions.get("status") != "ready":
            return {
                "status": "no_recommendations",
                "message": "暂无建议"
            }

        # 筛选高优先级和可执行的建议
        priority_suggestions = [s for s in suggestions.get("suggestions", []) if s["priority"] == "high"]
        executable = [s for s in suggestions.get("suggestions", []) if s.get("auto_executable", False)]

        recommendations = []

        if priority_suggestions:
            recommendations.append({
                "type": "priority_action",
                "description": priority_suggestions[0]["description"],
                "action": priority_suggestions[0]["action"]
            })

        if executable:
            recommendations.append({
                "type": "auto_executable",
                "description": executable[0]["description"],
                "action": "调用 execute_optimization() 执行优化"
            })

        # 添加当前状态摘要
        status = self.get_self_optimization_status()

        return {
            "status": "ready",
            "recommendations": recommendations,
            "current_status": {
                "success_rate": status["analysis"]["success_rate"],
                "trend": self.analysis.get("trends", {}).get("trend_direction", "unknown"),
                "optimization_needed": len(priority_suggestions) > 0
            }
        }


def main():
    """主入口"""
    import argparse

    parser = argparse.ArgumentParser(description="智能进化闭环自我优化引擎")
    parser.add_argument("command", nargs="?", default="status",
                       help="命令: status|analyze|adjust|suggestions|execute|recommend")
    parser.add_argument("--index", type=int, help="建议索引（用于execute命令）")

    args = parser.parse_args()

    optimizer = EvolutionLoopSelfOptimizer()

    if args.command == "status":
        result = optimizer.get_self_optimization_status()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "analyze":
        result = optimizer.analyze_execution_effectiveness()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "adjust":
        result = optimizer.auto_adjust_params()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "suggestions":
        result = optimizer.generate_optimization_suggestions()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "execute":
        result = optimizer.execute_optimization(args.index)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "recommend":
        result = optimizer.get_recommendations_for_next_round()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    else:
        print(f"未知命令: {args.command}")
        print("可用命令: status, analyze, adjust, suggestions, execute, recommend")
        sys.exit(1)


if __name__ == "__main__":
    main()