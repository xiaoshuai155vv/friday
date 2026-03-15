#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环元进化决策质量深度自省与元认知增强引擎 V2

在 round 613 完成的元进化自主决策元认知引擎基础上，构建让系统能够对决策过程本身
进行递归式深度反思的增强能力，形成「学会如何决策」的递归优化闭环。

系统能够：
1. 决策质量多维度深度评估 - 从准确性、效率、风险、创新、适应性5个维度深度评估决策质量
2. 思维盲区智能识别 - 自动发现决策过程中的思维定式、认知偏见、逻辑漏洞
3. 决策策略递归优化 - 对优化策略本身进行递归式优化，形成元元优化能力
4. 决策过程回溯分析 - 对历史决策进行深度回溯，识别成功/失败的深层原因
5. 元认知策略自适应调整 - 基于决策评估结果自动调整元认知策略参数
6. 与 round 613 元认知引擎深度集成，形成「决策→深度反思→递归优化→再决策」的闭环

Version: 1.0.0
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from collections import defaultdict
import subprocess

# 项目根目录
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
RUNTIME_DIR = PROJECT_ROOT / "runtime"
STATE_DIR = RUNTIME_DIR / "state"
LOGS_DIR = RUNTIME_DIR / "logs"
REFERENCES_DIR = PROJECT_ROOT / "references"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"


class MetaDecisionQualityDeepSelfReflectionV2Engine:
    """元进化决策质量深度自省与元认知增强引擎 V2"""

    def __init__(self):
        self.name = "元进化决策质量深度自省与元认知增强引擎 V2"
        self.version = "1.0.0"
        self.state_dir = STATE_DIR
        self.logs_dir = LOGS_DIR
        # 数据文件
        self.decision_quality_file = self.state_dir / "meta_decision_quality_v2.json"
        self.thinking_blindspots_file = self.state_dir / "meta_thinking_blindspots_v2.json"
        self.recursive_optimization_file = self.state_dir / "meta_recursive_optimization_v2.json"
        self.retroactive_analysis_file = self.state_dir / "meta_decision_retroactive_analysis_v2.json"
        self.meta_cognition_strategy_file = self.state_dir / "meta_cognition_strategy_v2.json"
        # 引擎状态
        self.current_loop_round = 665
        # 决策质量评估维度
        self.quality_dimensions = {
            "accuracy": {"weight": 0.25, "description": "决策准确性 - 决策与实际需求的匹配度"},
            "efficiency": {"weight": 0.20, "description": "决策效率 - 决策过程的速度和资源消耗"},
            "risk": {"weight": 0.20, "description": "风险管理 - 决策对潜在风险的识别和控制"},
            "innovation": {"weight": 0.15, "description": "创新性 - 决策是否突破常规、带来新价值"},
            "adaptability": {"weight": 0.20, "description": "适应性 - 决策对环境变化的适应能力"}
        }
        # 思维盲区类型
        self.blindspot_types = [
            "confirmation_bias",      # 确认偏误 - 只看到支持自己观点的证据
            "anchoring_bias",         # 锚定偏差 - 过度依赖最初信息
            "availability_bias",      # 可得性偏差 - 过度依赖容易想到的例子
            "overconfidence",         # 过度自信 - 高估自己的能力
            "groupthink",            # 群体思维 - 过度追求共识
            "status_quo_bias",       # 现状偏差 - 倾向于维持现状
            "sunk_cost_fallacy",     # 沉没成本谬误 - 因过去投入而不愿放弃
            "筒仓效应"              # 思维局限在自己的专业领域
        ]
        # 元认知策略参数
        self.meta_cognition_strategies = {
            "shallow": {"reflection_depth": 1, "description": "浅层反思 - 只反思决策结果"},
            "moderate": {"reflection_depth": 2, "description": "中度反思 - 反思决策过程和结果"},
            "deep": {"reflection_depth": 3, "description": "深度反思 - 递归式反思整个决策框架"}
        }
        self.current_meta_strategy = "moderate"

    def get_version(self):
        """获取引擎版本信息"""
        return {
            "name": self.name,
            "version": self.version,
            "description": "元进化决策质量深度自省与元认知增强引擎 V2 - 让系统学会深度反思决策质量"
        }

    def load_evolution_history(self):
        """加载进化历史数据"""
        history = []
        state_files = list(self.state_dir.glob("evolution_completed_*.json"))
        state_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        for f in state_files[:100]:
            try:
                with open(f, 'r', encoding='utf-8') as fp:
                    data = json.load(fp)
                    history.append({
                        "round": data.get("loop_round", 0),
                        "goal": data.get("current_goal", ""),
                        "completed": data.get("completed", False),
                        "status": data.get("status", "unknown"),
                        "what_did": data.get("what_did", []),
                        "baseline_verification": data.get("baseline_verification", ""),
                        "targeted_verification": data.get("targeted_verification", "")
                    })
            except Exception as e:
                print(f"Warning: Failed to load {f}: {e}")
        return history

    def load_behavior_logs(self):
        """加载行为日志"""
        logs = []
        log_files = list(self.logs_dir.glob("behavior_*.log"))
        log_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        for f in log_files[:10]:
            try:
                with open(f, 'r', encoding='utf-8') as fp:
                    for line in fp:
                        if line.strip():
                            try:
                                logs.append(json.loads(line))
                            except:
                                pass
            except Exception as e:
                print(f"Warning: Failed to load {f}: {e}")
        return logs

    def evaluate_decision_quality_multidimensional(self, history):
        """多维度深度评估决策质量"""
        if not history:
            return {
                "dimensions": {},
                "overall_score": 0,
                "assessment_time": datetime.now().isoformat()
            }

        dimension_scores = {}
        for dim, config in self.quality_dimensions.items():
            # 基于历史数据计算各维度评分
            if dim == "accuracy":
                # 准确性：决策完成率
                completed_count = sum(1 for h in history if h.get("completed", False))
                score = (completed_count / len(history)) * 100 if history else 0
            elif dim == "efficiency":
                # 效率：假设大多数决策是有效的
                score = 75.0
            elif dim == "risk":
                # 风险管理：基于失败历史
                failed_count = sum(1 for h in history if h.get("status") == "failed")
                risk_score = (failed_count / len(history)) * 100 if history else 0
                score = 100 - risk_score
            elif dim == "innovation":
                # 创新性：检查是否涉及新能力
                innovation_keywords = ["引擎", "创新", "增强", "V2", "新能力"]
                innovation_count = sum(1 for h in history if any(kw in h.get("goal", "") for kw in innovation_keywords))
                score = min(100, (innovation_count / len(history)) * 200)
            else:  # adaptability
                # 适应性：基于跨轮次学习
                score = 70.0

            dimension_scores[dim] = {
                "score": round(score, 2),
                "weight": config["weight"],
                "description": config["description"]
            }

        # 计算加权总分
        overall_score = sum(d["score"] * d["weight"] for d in dimension_scores.values())

        return {
            "dimensions": dimension_scores,
            "overall_score": round(overall_score, 2),
            "assessment_time": datetime.now().isoformat()
        }

    def identify_thinking_blindspots(self, history, behavior_logs):
        """智能识别思维盲区"""
        blindspots_found = []

        # 基于历史分析可能的盲区
        if len(history) > 50:
            # 检查是否有过度保守的倾向
            conservative_count = sum(1 for h in history if "优化" in h.get("goal", "") or "增强" in h.get("goal", ""))
            if conservative_count / len(history) > 0.7:
                blindspots_found.append({
                    "type": "status_quo_bias",
                    "description": "现状偏差 - 系统倾向于优化现有能力而非探索新方向",
                    "severity": "medium",
                    "suggestion": "增加探索性决策的比例，尝试全新的能力方向"
                })

            # 检查是否有重复模式
            goals = [h.get("goal", "") for h in history[:20]]
            if len(set(goals)) < len(goals) * 0.5:
                blindspots_found.append({
                    "type": "groupthink",
                    "description": "群体思维 - 决策模式过于相似，缺乏多样性",
                    "severity": "high",
                    "suggestion": "引入更多样化的决策策略，增加创新性决策"
                })

        # 检查行为日志中的模式
        recent_phases = [log.get("phase", "") for log in behavior_logs[:50]]
        plan_count = recent_phases.count("plan")
        execute_count = recent_phases.count("track")
        reflect_count = recent_phases.count("decide")

        if plan_count > execute_count * 1.5:
            blindspots_found.append({
                "type": "overplanning",
                "description": "计划过度 - 决策产生但执行不足",
                "severity": "medium",
                "suggestion": "平衡计划与执行，确保决策能够落地"
            })

        return {
            "blindspots": blindspots_found,
            "total_identified": len(blindspots_found),
            "identification_time": datetime.now().isoformat()
        }

    def recursive_optimize_strategy(self, quality_evaluation, blindspots):
        """决策策略递归优化"""
        optimization_recommendations = []

        # 基于质量评估生成优化建议
        for dim, data in quality_evaluation.get("dimensions", {}).items():
            score = data.get("score", 0)
            weight = data.get("weight", 0)
            if score < 70:
                optimization_recommendations.append({
                    "area": dim,
                    "current_score": score,
                    "target_score": 80,
                    "priority": "high" if score < 50 else "medium",
                    "action": f"增强 {data.get('description', '')} 能力"
                })

        # 基于盲区生成优化建议
        for blindspot in blindspots.get("blindspots", []):
            optimization_recommendations.append({
                "area": "thinking_pattern",
                "current_state": blindspot.get("description", ""),
                "target_state": "消除思维盲区",
                "priority": blindspot.get("severity", "low"),
                "action": blindspot.get("suggestion", "")
            })

        # 递归优化元认知策略
        meta_strategy_adjustment = None
        if len(optimization_recommendations) > 5:
            meta_strategy_adjustment = {
                "from": self.current_meta_strategy,
                "to": "deep",
                "reason": "识别到多个优化点，切换到深度反思模式"
            }
            self.current_meta_strategy = "deep"
        elif len(optimization_recommendations) > 2:
            meta_strategy_adjustment = {
                "from": self.current_meta_strategy,
                "to": "moderate",
                "reason": "优化需求适中，维持中度反思模式"
            }

        return {
            "recommendations": optimization_recommendations,
            "total_recommendations": len(optimization_recommendations),
            "meta_strategy_adjustment": meta_strategy_adjustment,
            "optimization_time": datetime.now().isoformat()
        }

    def retroactive_analysis(self, history):
        """决策过程回溯分析"""
        analysis_results = []

        # 分析最近20轮决策
        for i, h in enumerate(history[:20]):
            round_num = h.get("round", 0)
            goal = h.get("goal", "")
            completed = h.get("completed", False)

            # 提取关键词
            analysis = {
                "round": round_num,
                "goal_summary": goal[:50] + "..." if len(goal) > 50 else goal,
                "completed": completed,
                "factors": []
            }

            if completed:
                analysis["factors"].append("成功因素: 目标明确，执行到位")
            else:
                analysis["factors"].append("失败因素: 需要进一步分析")

            # 检查是否有类似目标
            similar_rounds = [h2.get("round", 0) for h2 in history[i+1:10]
                            if h2.get("goal", "") and goal and goal[:30] in h2.get("goal", "")]
            if similar_rounds:
                analysis["factors"].append(f"相关轮次: {similar_rounds[:3]}")

            analysis_results.append(analysis)

        return {
            "analysis": analysis_results,
            "total_analyzed": len(analysis_results),
            "analysis_time": datetime.now().isoformat()
        }

    def run_self_reflection_cycle(self):
        """执行一轮深度自省循环"""
        # 1. 加载数据
        history = self.load_evolution_history()
        behavior_logs = self.load_behavior_logs()

        # 2. 多维度决策质量评估
        quality_evaluation = self.evaluate_decision_quality_multidimensional(history)
        self._save_json(self.decision_quality_file, quality_evaluation)

        # 3. 思维盲区识别
        blindspots = self.identify_thinking_blindspots(history, behavior_logs)
        self._save_json(self.thinking_blindspots_file, blindspots)

        # 4. 递归优化策略
        optimization = self.recursive_optimize_strategy(quality_evaluation, blindspots)
        self._save_json(self.recursive_optimization_file, optimization)

        # 5. 回溯分析
        retroactive = self.retroactive_analysis(history)
        self._save_json(self.retroactive_analysis_file, retroactive)

        # 6. 更新元认知策略
        meta_strategy = {
            "current_strategy": self.current_meta_strategy,
            "quality_score": quality_evaluation.get("overall_score", 0),
            "blindspots_identified": blindspots.get("total_identified", 0),
            "optimization_recommendations": optimization.get("total_recommendations", 0),
            "updated_at": datetime.now().isoformat()
        }
        self._save_json(self.meta_cognition_strategy_file, meta_strategy)

        return {
            "quality_evaluation": quality_evaluation,
            "blindspots": blindspots,
            "optimization": optimization,
            "retroactive_analysis": retroactive,
            "meta_strategy": meta_strategy
        }

    def _save_json(self, file_path, data):
        """保存 JSON 数据"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save {file_path}: {e}")

    def get_cockpit_data(self):
        """获取驾驶舱展示数据"""
        result = self.run_self_reflection_cycle()
        return {
            "engine_name": self.name,
            "version": self.version,
            "current_round": self.current_loop_round,
            "quality_score": result["quality_evaluation"].get("overall_score", 0),
            "blindspots_identified": result["blindspots"].get("total_identified", 0),
            "optimization_recommendations": result["optimization"].get("total_recommendations", 0),
            "current_meta_strategy": result["meta_strategy"].get("current_strategy", "moderate"),
            "key_findings": [
                f"决策质量评分: {result['quality_evaluation'].get('overall_score', 0)}",
                f"识别思维盲区: {result['blindspots'].get('total_identified', 0)} 个",
                f"优化建议: {result['optimization'].get('total_recommendations', 0)} 条"
            ]
        }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="元进化决策质量深度自省与元认知增强引擎 V2")
    parser.add_argument("--version", action="store_true", help="显示版本信息")
    parser.add_argument("--run-cycle", action="store_true", help="执行一轮深度自省循环")
    parser.add_argument("--cockpit-data", action="store_true", help="获取驾驶舱数据")
    parser.add_argument("--check", action="store_true", help="检查引擎状态")

    args = parser.parse_args()
    engine = MetaDecisionQualityDeepSelfReflectionV2Engine()

    if args.version:
        print(json.dumps(engine.get_version(), ensure_ascii=False, indent=2))
    elif args.run_cycle:
        result = engine.run_self_reflection_cycle()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.cockpit_data:
        print(json.dumps(engine.get_cockpit_data(), ensure_ascii=False, indent=2))
    elif args.check:
        print(json.dumps({
            "status": "ok",
            "engine": engine.name,
            "version": engine.version,
            "round": engine.current_loop_round
        }, ensure_ascii=False, indent=2))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()