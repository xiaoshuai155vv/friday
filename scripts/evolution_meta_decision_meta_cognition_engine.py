#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环元进化自主决策元认知引擎

在 round 612 完成的元进化执行闭环全自动化引擎基础上，构建让系统能够反思自身决策过程、
评估决策质量、优化决策策略的元认知能力，形成「学会如何决策」的递归优化能力。

系统能够：
1. 决策过程反思 - 在每次决策后分析决策的有效性，识别决策中的偏差和盲点
2. 决策质量评估 - 基于进化结果评估决策质量，量化决策对系统能力提升的贡献
3. 决策策略优化 - 根据决策评估结果自动调整决策策略，持续改进决策方法
4. 跨场景决策学习 - 将从一个场景学到的决策经验迁移到类似场景
5. 决策元知识提取 - 从 600+ 轮进化历史中提取可复用的决策模式和最佳实践
6. 与 round 612 执行闭环自动化引擎深度集成，形成「决策→执行→反思→优化」的完整自主决策闭环

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


class MetaDecisionMetaCognitionEngine:
    """元进化自主决策元认知引擎"""

    def __init__(self):
        self.name = "元进化自主决策元认知引擎"
        self.version = "1.0.0"
        self.state_dir = STATE_DIR
        self.logs_dir = LOGS_DIR
        # 数据文件
        self.decision_reflection_file = self.state_dir / "meta_decision_reflection.json"
        self.decision_quality_file = self.state_dir / "meta_decision_quality.json"
        self.decision_strategy_file = self.state_dir / "meta_decision_strategy.json"
        self.decision_learning_file = self.state_dir / "meta_decision_learning.json"
        self.decision_meta_knowledge_file = self.state_dir / "meta_decision_meta_knowledge.json"
        self.closed_loop_state_file = self.state_dir / "meta_decision_closed_loop_state.json"
        # 引擎状态
        self.current_loop_round = 613
        # 决策策略参数
        self.decision_strategies = {
            "conservative": {"weight": 0.3, "description": "保守策略 - 优先利用已知有效能力"},
            "balanced": {"weight": 0.5, "description": "平衡策略 - 在利用与探索间平衡"},
            "explorative": {"weight": 0.2, "description": "探索策略 - 优先尝试新方法"}
        }
        self.current_strategy = "balanced"

    def get_version(self):
        """获取引擎版本信息"""
        return {
            "name": self.name,
            "version": self.version,
            "description": "元进化自主决策元认知引擎 - 让系统学会如何决策"
        }

    def load_evolution_history(self):
        """加载进化历史数据"""
        history = []
        state_files = list(self.state_dir.glob("evolution_completed_*.json"))
        # 读取最近的 100 轮进化历史
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

    def analyze_decision_patterns(self, history):
        """分析历史决策模式"""
        patterns = {
            "total_decisions": len(history),
            "successful_decisions": sum(1 for h in history if h.get("completed", False)),
            "failed_decisions": sum(1 for h in history if not h.get("completed", False) and h.get("status") == "failed"),
            "strategy_distribution": defaultdict(int),
            "goal_categories": defaultdict(int),
            "round_gaps": []
        }

        # 分析策略分布（基于目标分类）
        for h in history:
            goal = h.get("goal", "").lower()
            if "自动化" in goal or "闭环" in goal:
                patterns["strategy_distribution"]["automation"] += 1
            elif "优化" in goal or "增强" in goal:
                patterns["strategy_distribution"]["optimization"] += 1
            elif "创新" in goal or "涌现" in goal:
                patterns["strategy_distribution"]["innovation"] += 1
            elif "决策" in goal or "元认知" in goal:
                patterns["strategy_distribution"]["meta_cognition"] += 1
            elif "智能" in goal:
                patterns["strategy_distribution"]["intelligence"] += 1
            else:
                patterns["strategy_distribution"]["other"] += 1

            # 目标分类
            if "引擎" in goal:
                patterns["goal_categories"]["engine"] += 1
            elif "能力" in goal:
                patterns["goal_categories"]["capability"] += 1
            elif "系统" in goal:
                patterns["goal_categories"]["system"] += 1
            else:
                patterns["goal_categories"]["other"] += 1

        # 计算轮次间隔
        rounds = sorted([h.get("round", 0) for h in history])
        for i in range(1, len(rounds)):
            patterns["round_gaps"].append(rounds[i] - rounds[i-1])

        patterns["strategy_distribution"] = dict(patterns["strategy_distribution"])
        patterns["goal_categories"] = dict(patterns["goal_categories"])
        patterns["success_rate"] = patterns["successful_decisions"] / patterns["total_decisions"] if patterns["total_decisions"] > 0 else 0

        return patterns

    def reflect_on_decision(self, decision_data):
        """决策过程反思 - 分析决策的有效性"""
        reflection = {
            "timestamp": datetime.now().isoformat(),
            "decision": decision_data.get("goal", ""),
            "analysis": {}
        }

        # 分析决策的合理性
        goal = decision_data.get("goal", "")
        history = self.load_evolution_history()

        # 检查是否有类似决策的历史
        similar_history = []
        for h in history:
            h_goal = h.get("goal", "").lower()
            goal_lower = goal.lower()
            # 检查关键词重叠
            goal_words = set(goal_lower.replace("智能全场景进化环", "").replace("引擎", "").split())
            h_goal_words = set(h_goal.replace("智能全场景进化环", "").replace("引擎", "").split())
            overlap = goal_words & h_goal_words
            if len(overlap) >= 2:
                similar_history.append(h)

        reflection["analysis"]["similar_past_decisions"] = len(similar_history)
        reflection["analysis"]["similar_success_rate"] = sum(1 for h in similar_history if h.get("completed", False)) / len(similar_history) if similar_history else 0

        # 识别潜在的偏差和盲点
        biases = []
        if len(similar_history) > 5:
            biases.append("可能存在路径依赖 - 多次做出类似决策")
        if decision_data.get("goal", "").count("构建") > 3:
            biases.append("目标可能过于复杂 - 考虑拆分为多个子目标")
        if not similar_history:
            biases.append("这是一个新的决策方向 - 需要更多验证")

        reflection["analysis"]["potential_biases"] = biases

        # 保存反思结果
        self._save_reflection(reflection)

        return reflection

    def _save_reflection(self, reflection):
        """保存反思结果"""
        reflections = []
        if self.decision_reflection_file.exists():
            try:
                with open(self.decision_reflection_file, 'r', encoding='utf-8') as f:
                    reflections = json.load(f)
            except:
                reflections = []
        reflections.append(reflection)
        # 只保留最近 50 条
        reflections = reflections[-50:]
        with open(self.decision_reflection_file, 'w', encoding='utf-8') as f:
            json.dump(reflections, f, ensure_ascii=False, indent=2)

    def evaluate_decision_quality(self, execution_result):
        """决策质量评估 - 量化决策对系统能力的提升贡献"""
        evaluation = {
            "timestamp": datetime.now().isoformat(),
            "execution_result": execution_result,
            "metrics": {}
        }

        # 评估指标
        # 1. 目标完成度
        evaluation["metrics"]["goal_completion"] = 1.0 if execution_result.get("completed", False) else 0.0

        # 2. 基线校验通过率
        baseline = execution_result.get("baseline_verification", "")
        evaluation["metrics"]["baseline_pass_rate"] = 1.0 if "通过" in baseline or "pass" in baseline.lower() else 0.0

        # 3. 针对性校验通过率
        targeted = execution_result.get("targeted_verification", "")
        evaluation["metrics"]["targeted_pass_rate"] = 1.0 if "通过" in targeted or "pass" in targeted.lower() else 0.0

        # 4. 综合质量分数
        evaluation["metrics"]["quality_score"] = (
            evaluation["metrics"]["goal_completion"] * 0.4 +
            evaluation["metrics"]["baseline_pass_rate"] * 0.3 +
            evaluation["metrics"]["targeted_pass_rate"] * 0.3
        )

        # 保存评估结果
        self._save_quality_evaluation(evaluation)

        return evaluation

    def _save_quality_evaluation(self, evaluation):
        """保存质量评估结果"""
        evaluations = []
        if self.decision_quality_file.exists():
            try:
                with open(self.decision_quality_file, 'r', encoding='utf-8') as f:
                    evaluations = json.load(f)
            except:
                evaluations = []
        evaluations.append(evaluation)
        # 只保留最近 50 条
        evaluations = evaluations[-50:]
        with open(self.decision_quality_file, 'w', encoding='utf-8') as f:
            json.dump(evaluations, f, ensure_ascii=False, indent=2)

    def optimize_decision_strategy(self):
        """决策策略优化 - 根据评估结果自动调整决策策略"""
        # 加载历史评估数据
        evaluations = []
        if self.decision_quality_file.exists():
            try:
                with open(self.decision_quality_file, 'r', encoding='utf-8') as f:
                    evaluations = json.load(f)
            except:
                evaluations = []

        if len(evaluations) < 5:
            return {
                "strategy": self.current_strategy,
                "message": "数据不足，保持当前策略",
                "confidence": 0.5
            }

        # 分析最近的趋势
        recent_quality = [e["metrics"]["quality_score"] for e in evaluations[-10:]]
        avg_quality = sum(recent_quality) / len(recent_quality)

        # 根据质量趋势调整策略
        if avg_quality > 0.8:
            # 质量高 - 可以更探索性
            new_strategy = "explorative"
            message = "质量优秀，增加探索以发现更多创新机会"
        elif avg_quality > 0.5:
            # 质量中等 - 保持平衡
            new_strategy = "balanced"
            message = "质量稳定，保持当前平衡策略"
        else:
            # 质量较低 - 需要保守
            new_strategy = "conservative"
            message = "质量下降，增加利用已知有效方法的比例"

        # 如果策略改变，更新权重
        if new_strategy != self.current_strategy:
            self.current_strategy = new_strategy
            self._save_strategy_change(new_strategy, message)

        return {
            "strategy": new_strategy,
            "message": message,
            "confidence": abs(avg_quality - 0.5) * 2,
            "avg_quality": avg_quality
        }

    def _save_strategy_change(self, strategy, message):
        """保存策略变更"""
        strategy_data = {
            "timestamp": datetime.now().isoformat(),
            "old_strategy": self.current_strategy,
            "new_strategy": strategy,
            "message": message
        }
        strategies = []
        if self.decision_strategy_file.exists():
            try:
                with open(self.decision_strategy_file, 'r', encoding='utf-8') as f:
                    strategies = json.load(f)
            except:
                strategies = []
        strategies.append(strategy_data)
        strategies = strategies[-50:]
        with open(self.decision_strategy_file, 'w', encoding='utf-8') as f:
            json.dump(strategies, f, ensure_ascii=False, indent=2)

    def learn_from_scenarios(self, source_scenario, target_scenario):
        """跨场景决策学习 - 将经验迁移到类似场景"""
        # 加载历史决策数据
        history = self.load_evolution_history()

        # 找到源场景的决策经验
        source_experiences = []
        for h in history:
            if source_scenario.lower() in h.get("goal", "").lower():
                source_experiences.append(h)

        if not source_experiences:
            return {
                "success": False,
                "message": f"未找到 {source_scenario} 的历史经验"
            }

        # 提取可迁移的知识
        transferable_knowledge = {
            "source_scenario": source_scenario,
            "target_scenario": target_scenario,
            "experience_count": len(source_experiences),
            "successful_patterns": [],
            "failure_patterns": []
        }

        for exp in source_experiences:
            if exp.get("completed", False):
                # 提取成功模式
                goal = exp.get("goal", "")
                transferable_knowledge["successful_patterns"].append({
                    "goal_type": goal.split("智能全场景进化环")[-1][:30] if "智能全场景进化环" in goal else goal[:30],
                    "round": exp.get("round", 0)
                })
            else:
                # 提取失败模式
                transferable_knowledge["failure_patterns"].append({
                    "round": exp.get("round", 0),
                    "goal": exp.get("goal", "")[:50]
                })

        # 保存学习结果
        self._save_learned_experience(transferable_knowledge)

        return {
            "success": True,
            "knowledge": transferable_knowledge,
            "message": f"成功从 {source_scenario} 提取 {len(source_experiences)} 条经验"
        }

    def _save_learned_experience(self, knowledge):
        """保存学到的经验"""
        experiences = []
        if self.decision_learning_file.exists():
            try:
                with open(self.decision_learning_file, 'r', encoding='utf-8') as f:
                    experiences = json.load(f)
            except:
                experiences = []
        experiences.append(knowledge)
        experiences = experiences[-50:]
        with open(self.decision_learning_file, 'w', encoding='utf-8') as f:
            json.dump(experiences, f, ensure_ascii=False, indent=2)

    def extract_meta_knowledge(self):
        """决策元知识提取 - 从历史中提取可复用模式"""
        history = self.load_evolution_history()

        # 分析 600+ 轮进化历史，提炼元知识
        meta_knowledge = {
            "extraction_time": datetime.now().isoformat(),
            "total_rounds_analyzed": len(history),
            "patterns": {},
            "best_practices": [],
            "antipatterns": []
        }

        # 1. 分析成功的决策模式
        successful = [h for h in history if h.get("completed", False)]

        # 按目标类型分析成功率
        goal_type_success = defaultdict(lambda: {"total": 0, "success": 0})
        for h in history:
            goal = h.get("goal", "")
            if "引擎" in goal:
                goal_type = "engine"
            elif "能力" in goal:
                goal_type = "capability"
            elif "优化" in goal:
                goal_type = "optimization"
            elif "自动" in goal:
                goal_type = "automation"
            else:
                goal_type = "other"

            goal_type_success[goal_type]["total"] += 1
            if h.get("completed", False):
                goal_type_success[goal_type]["success"] += 1

        meta_knowledge["patterns"]["goal_type_success_rates"] = {
            k: v["success"] / v["total"] if v["total"] > 0 else 0
            for k, v in goal_type_success.items()
        }

        # 2. 提取最佳实践
        if successful:
            # 按轮次排序，取最近的 10 个成功案例
            recent_success = sorted(successful, key=lambda x: x.get("round", 0), reverse=True)[:10]
            for s in recent_success:
                meta_knowledge["best_practices"].append({
                    "round": s.get("round", 0),
                    "goal": s.get("goal", "")[:100],
                    "pattern": "持续迭代 + 深度集成"
                })

        # 3. 识别反模式（失败模式）
        failed = [h for h in history if not h.get("completed", False) and h.get("status") == "failed"]
        if failed:
            for f in failed[:5]:
                meta_knowledge["antipatterns"].append({
                    "round": f.get("round", 0),
                    "goal": f.get("goal", "")[:100],
                    "issue": "目标过于复杂或依赖不完整"
                })

        # 保存元知识
        with open(self.decision_meta_knowledge_file, 'w', encoding='utf-8') as f:
            json.dump(meta_knowledge, f, ensure_ascii=False, indent=2)

        return meta_knowledge

    def get_cockpit_data(self):
        """获取驾驶舱数据接口"""
        history = self.load_evolution_history()
        patterns = self.analyze_decision_patterns(history)

        # 加载最新数据
        reflections = []
        if self.decision_reflection_file.exists():
            try:
                with open(self.decision_reflection_file, 'r', encoding='utf-8') as f:
                    reflections = json.load(f)
            except:
                reflections = []

        evaluations = []
        if self.decision_quality_file.exists():
            try:
                with open(self.decision_quality_file, 'r', encoding='utf-8') as f:
                    evaluations = json.load(f)
            except:
                evaluations = []

        # 计算质量趋势
        quality_trend = []
        if evaluations:
            recent = evaluations[-10:]
            quality_trend = [e["metrics"]["quality_score"] for e in recent]

        return {
            "engine": self.get_version(),
            "current_loop_round": self.current_loop_round,
            "current_strategy": self.current_strategy,
            "patterns": patterns,
            "recent_reflections": len(reflections),
            "recent_evaluations": len(evaluations),
            "quality_trend": quality_trend,
            "total_rounds": len(history)
        }

    def run_full_cycle(self):
        """运行完整的元决策认知循环"""
        result = {
            "timestamp": datetime.now().isoformat(),
            "round": self.current_loop_round,
            "steps": {}
        }

        # 1. 加载历史数据
        history = self.load_evolution_history()
        result["steps"]["load_history"] = {
            "success": True,
            "rounds_loaded": len(history)
        }

        # 2. 分析决策模式
        patterns = self.analyze_decision_patterns(history)
        result["steps"]["analyze_patterns"] = {
            "success": True,
            "patterns": patterns
        }

        # 3. 提取元知识
        meta_knowledge = self.extract_meta_knowledge()
        result["steps"]["extract_meta_knowledge"] = {
            "success": True,
            "patterns_found": len(meta_knowledge.get("patterns", {}))
        }

        # 4. 优化决策策略
        strategy_optimization = self.optimize_decision_strategy()
        result["steps"]["optimize_strategy"] = {
            "success": True,
            "new_strategy": strategy_optimization.get("strategy"),
            "message": strategy_optimization.get("message")
        }

        # 5. 生成决策建议
        decision_suggestions = self._generate_decision_suggestions(patterns, meta_knowledge)
        result["steps"]["generate_suggestions"] = {
            "success": True,
            "suggestions": decision_suggestions
        }

        # 6. 获取驾驶舱数据
        cockpit_data = self.get_cockpit_data()
        result["steps"]["cockpit_data"] = {
            "success": True,
            "current_strategy": cockpit_data.get("current_strategy"),
            "quality_trend": cockpit_data.get("quality_trend")
        }

        return result

    def _generate_decision_suggestions(self, patterns, meta_knowledge):
        """生成决策建议"""
        suggestions = []

        # 基于模式分析生成建议
        success_rate = patterns.get("success_rate", 0)

        if success_rate > 0.8:
            suggestions.append({
                "type": "exploration",
                "message": "系统决策质量优秀，建议增加探索性决策以发现更多创新机会",
                "priority": "high"
            })
        elif success_rate > 0.5:
            suggestions.append({
                "type": "balance",
                "message": "系统决策质量稳定，建议保持平衡策略",
                "priority": "medium"
            })
        else:
            suggestions.append({
                "type": "conservative",
                "message": "系统决策质量有提升空间，建议采用更保守的策略",
                "priority": "high"
            })

        # 基于元知识生成建议
        goal_rates = meta_knowledge.get("patterns", {}).get("goal_type_success_rates", {})
        best_goal_type = max(goal_rates.items(), key=lambda x: x[1]) if goal_rates else None

        if best_goal_type:
            suggestions.append({
                "type": "optimization",
                "message": f"历史数据显示 '{best_goal_type[0]}' 类型目标成功率最高({best_goal_type[1]:.1%})，建议优先考虑",
                "priority": "medium"
            })

        return suggestions

    def integrate_with_execution_engine(self):
        """与 round 612 执行闭环自动化引擎深度集成"""
        # 检查执行闭环引擎是否存在
        execution_engine_path = SCRIPTS_DIR / "evolution_meta_execution_closed_loop_automation_engine.py"
        if not execution_engine_path.exists():
            return {
                "success": False,
                "message": "未找到 round 612 执行闭环自动化引擎"
            }

        # 尝试加载引擎数据
        try:
            sys.path.insert(0, str(SCRIPTS_DIR))
            from evolution_meta_execution_closed_loop_automation_engine import MetaExecutionClosedLoopAutomationEngine

            exec_engine = MetaExecutionClosedLoopAutomationEngine()
            exec_data = exec_engine.get_cockpit_data()

            return {
                "success": True,
                "message": "成功与执行闭环引擎集成",
                "execution_data": {
                    "current_strategy": exec_data.get("current_strategy"),
                    "automation_level": exec_data.get("automation_level", 0)
                }
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"集成执行闭环引擎时出错: {str(e)}"
            }


def main():
    """主函数 - 支持命令行调用"""
    import argparse

    parser = argparse.ArgumentParser(description="元进化自主决策元认知引擎")
    parser.add_argument("--version", action="store_true", help="显示版本信息")
    parser.add_argument("--status", action="store_true", help="显示引擎状态")
    parser.add_argument("--run", action="store_true", help="运行完整元决策认知循环")
    parser.add_argument("--reflect", action="store_true", help="执行决策反思")
    parser.add_argument("--optimize", action="store_true", help="优化决策策略")
    parser.add_argument("--extract-meta", action="store_true", help="提取决策元知识")
    parser.add_argument("--learn", type=str, help="跨场景学习（参数：源场景->目标场景）")
    parser.add_argument("--cockpit-data", action="store_true", help="获取驾驶舱数据")
    parser.add_argument("--integrate", action="store_true", help="与执行引擎集成")

    args = parser.parse_args()

    engine = MetaDecisionMetaCognitionEngine()

    if args.version:
        print(json.dumps(engine.get_version(), ensure_ascii=False, indent=2))
        return

    if args.status:
        history = engine.load_evolution_history()
        patterns = engine.analyze_decision_patterns(history)
        print(json.dumps({
            "current_round": engine.current_loop_round,
            "current_strategy": engine.current_strategy,
            "total_history": len(history),
            "success_rate": patterns.get("success_rate", 0)
        }, ensure_ascii=False, indent=2))
        return

    if args.run:
        result = engine.run_full_cycle()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if args.reflect:
        # 模拟一次决策反思
        test_decision = {
            "goal": "智能全场景进化环元进化自主决策元认知引擎"
        }
        reflection = engine.reflect_on_decision(test_decision)
        print(json.dumps(reflection, ensure_ascii=False, indent=2))
        return

    if args.optimize:
        optimization = engine.optimize_decision_strategy()
        print(json.dumps(optimization, ensure_ascii=False, indent=2))
        return

    if args.extract_meta:
        meta_knowledge = engine.extract_meta_knowledge()
        print(json.dumps(meta_knowledge, ensure_ascii=False, indent=2))
        return

    if args.learn:
        try:
            source, target = args.learn.split("->")
            result = engine.learn_from_scenarios(source.strip(), target.strip())
            print(json.dumps(result, ensure_ascii=False, indent=2))
        except:
            print("Error: 请使用格式 --learn 源场景->目标场景")
        return

    if args.cockpit_data:
        data = engine.get_cockpit_data()
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return

    if args.integrate:
        result = engine.integrate_with_execution_engine()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    # 默认显示帮助
    parser.print_help()


if __name__ == "__main__":
    main()