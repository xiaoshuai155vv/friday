#!/usr/bin/env python3
"""
智能全场景深度认知与自主意识增强引擎 (Evolution Deep Cognition Awareness Engine)

在 round 453 完成的进化价值实现追踪与自动优化引擎基础上，
进一步构建深度认知与自主意识增强能力。
让系统能够主动思考自身认知过程、评估认知质量、生成认知优化策略，
形成「自我反思→认知评估→策略优化→执行验证」的完整认知闭环。
让进化环能够具备更深层次的元认知能力，真正实现「学会如何思考如何进化」。

这是进化环的"认知增强+自主意识"引擎——在价值追踪基础上增加深度认知能力，
与元认知引擎(r316/r353)、自我意识引擎(r256/r278/r304)形成完整的认知增强体系。

Version: 1.0.0
Author: AI Evolution System
"""

import json
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
STATE_DIR = PROJECT_ROOT / "runtime" / "state"
LOGS_DIR = PROJECT_ROOT / "runtime" / "logs"
REFERENCES_DIR = PROJECT_ROOT / "references"


class EvolutionDeepCognitionAwarenessEngine:
    """深度认知与自主意识增强引擎核心类"""

    def __init__(self):
        self.version = "1.0.0"
        self.name = "Evolution Deep Cognition Awareness Engine"
        self.capabilities = [
            "自我反思能力",
            "认知质量评估",
            "认知优化策略生成",
            "自我意识增强",
            "认知过程可视化",
            "驾驶舱深度集成"
        ]
        self.cognition_history = []
        self.awareness_metrics = {
            "decision_quality": 0.0,
            "self_reflection_depth": 0.0,
            "cognitive_bias_awareness": 0.0,
            "meta_cognition_level": 0.0
        }

    def self_reflect(self, evolution_round: int = None) -> Dict:
        """
        自我反思：主动分析自身决策质量、识别认知偏差

        Args:
            evolution_round: 指定轮次，默认分析最近完成的轮次

        Returns:
            自我反思分析结果
        """
        if evolution_round is None:
            evolution_round = self._get_latest_completed_round()

        if evolution_round is None:
            return {
                "status": "no_data",
                "message": "未找到已完成的进化轮次",
                "round": None
            }

        # 读取该轮次的完成状态文件
        completed_file = self._find_completed_file(evolution_round)

        if not completed_file:
            return {
                "status": "no_data",
                "message": f"未找到 round {evolution_round} 的完成记录",
                "round": evolution_round
            }

        try:
            with open(completed_file, 'r', encoding='utf-8') as f:
                round_data = json.load(f)

            # 分析决策质量
            current_goal = round_data.get("current_goal", "")
            was_completed = round_data.get("was_completed", False)

            # 评估决策质量
            decision_quality = self._evaluate_decision_quality(round_data)

            # 识别认知偏差
            cognitive_biases = self._identify_cognitive_biases(round_data)

            # 生成反思报告
            reflection_result = {
                "round": evolution_round,
                "current_goal": current_goal,
                "was_completed": was_completed,
                "decision_quality": decision_quality,
                "cognitive_biases": cognitive_biases,
                "self_reflection_insights": self._generate_reflection_insights(
                    decision_quality, cognitive_biases
                ),
                "timestamp": datetime.now().isoformat()
            }

            self.cognition_history.append(reflection_result)
            return reflection_result

        except Exception as e:
            return {
                "status": "error",
                "message": f"自我反思分析失败: {str(e)}",
                "round": evolution_round
            }

    def evaluate_cognition_quality(self) -> Dict:
        """
        认知质量评估：多维度评估思考过程的有效性

        Returns:
            认知质量评估结果
        """
        # 收集历史认知数据
        recent_cognitions = self.cognition_history[-10:] if self.cognition_history else []

        if not recent_cognitions:
            return {
                "status": "insufficient_data",
                "message": "认知历史数据不足，无法进行评估",
                "metrics": {}
            }

        # 计算多维度指标
        avg_decision_quality = sum(
            c.get("decision_quality", 0) for c in recent_cognitions
        ) / len(recent_cognitions)

        avg_bias_awareness = sum(
            len(c.get("cognitive_biases", [])) for c in recent_cognitions
        ) / len(recent_cognitions)

        # 计算元认知水平
        meta_cognition = self._calculate_meta_cognition_level(recent_cognitions)

        evaluation_result = {
            "status": "success",
            "metrics": {
                "average_decision_quality": round(avg_decision_quality, 3),
                "average_bias_awareness": round(avg_bias_awareness, 3),
                "meta_cognition_level": round(meta_cognition, 3),
                "total_cognitions": len(recent_cognitions),
                "cognition_trend": self._analyze_cognition_trend()
            },
            "timestamp": datetime.now().isoformat()
        }

        # 更新内部指标
        self.awareness_metrics["decision_quality"] = avg_decision_quality
        self.awareness_metrics["self_reflection_depth"] = avg_bias_awareness
        self.awareness_metrics["meta_cognition_level"] = meta_cognition

        return evaluation_result

    def generate_cognition_optimization(self) -> Dict:
        """
        认知优化策略生成：基于评估结果生成改进方案

        Returns:
            认知优化策略建议
        """
        # 先进行认知质量评估
        evaluation = self.evaluate_cognition_quality()

        if evaluation.get("status") == "insufficient_data":
            # 数据不足时，基于通用原则生成优化建议
            return {
                "status": "baseline_optimization",
                "optimization_suggestions": [
                    {
                        "area": "决策质量",
                        "suggestion": "增加决策前的多角度分析，提高决策全面性",
                        "priority": "high"
                    },
                    {
                        "area": "元认知",
                        "suggestion": "定期进行自我反思，培养元认知习惯",
                        "priority": "medium"
                    }
                ],
                "timestamp": datetime.now().isoformat()
            }

        metrics = evaluation.get("metrics", {})

        # 基于指标生成针对性优化建议
        suggestions = []

        if metrics.get("average_decision_quality", 0) < 0.7:
            suggestions.append({
                "area": "决策质量",
                "suggestion": "决策质量偏低，建议在决策前增加利益相关方分析和风险评估",
                "priority": "high"
            })

        if metrics.get("average_bias_awareness", 0) < 0.5:
            suggestions.append({
                "area": "认知偏差识别",
                "suggestion": "认知偏差识别能力有待提升，建议引入更多外部反馈机制",
                "priority": "medium"
            })

        if metrics.get("meta_cognition_level", 0) < 0.6:
            suggestions.append({
                "area": "元认知",
                "suggestion": "元认知水平需要提升，建议增加对自身思考过程的监控和反思",
                "priority": "high"
            })

        # 添加积极的反馈
        if metrics.get("cognition_trend", "") == "improving":
            suggestions.append({
                "area": "整体趋势",
                "suggestion": "认知能力呈上升趋势，继续保持当前的反思习惯",
                "priority": "low"
            })

        return {
            "status": "success",
            "optimization_suggestions": suggestions,
            "metrics": metrics,
            "timestamp": datetime.now().isoformat()
        }

    def enhance_self_awareness(self) -> Dict:
        """
        自我意识增强：对自身状态、能力的深度理解

        Returns:
            自我意识增强报告
        """
        # 收集系统状态信息
        system_state = self._collect_system_state()

        # 分析能力分布
        capability_analysis = self._analyze_capabilities()

        # 生成自我意识报告
        awareness_report = {
            "status": "success",
            "self_understanding": {
                "current_evolution_round": self._get_latest_completed_round() or 0,
                "system_health": system_state,
                "capability_distribution": capability_analysis,
                "cognitive_strengths": self._identify_cognitive_strengths(),
                "cognitive_weaknesses": self._identify_cognitive_weaknesses()
            },
            "depth_of_understanding": {
                "operational_level": "understands_how_to_execute",
                "strategic_level": "understands_optimization_strategies",
                "meta_level": "understanding_own_cognition"
            },
            "timestamp": datetime.now().isoformat()
        }

        return awareness_report

    def get_cockpit_data(self) -> Dict:
        """
        获取用于驾驶舱展示的认知数据

        Returns:
            驾驶舱可视化数据
        """
        evaluation = self.evaluate_cognition_quality()
        optimization = self.generate_cognition_optimization()
        awareness = self.enhance_self_awareness()

        return {
            "status": "success",
            "title": "深度认知与自主意识引擎",
            "metrics": evaluation.get("metrics", {}),
            "optimization_suggestions": optimization.get("optimization_suggestions", []),
            "self_understanding": awareness.get("self_understanding", {}),
            "capabilities": self.capabilities,
            "version": self.version,
            "timestamp": datetime.now().isoformat()
        }

    # ============ 内部辅助方法 ============

    def _get_latest_completed_round(self) -> Optional[int]:
        """获取最近完成的进化轮次"""
        try:
            if not STATE_DIR.exists():
                return None

            completed_files = list(STATE_DIR.glob("evolution_completed_*.json"))
            if not completed_files:
                return None

            # 提取轮次号
            rounds = []
            for f in completed_files:
                match = re.search(r'evolution_completed_ev_(\d{8})_(\d+)\.json', f.name)
                if match:
                    rounds.append(int(match.group(2)))

            return max(rounds) if rounds else None
        except Exception:
            return None

    def _find_completed_file(self, round_num: int) -> Optional[Path]:
        """查找指定轮次的完成文件"""
        try:
            if not STATE_DIR.exists():
                return None

            # 搜索模式：evolution_completed_ev_YYYYMMDD_NNN.json
            pattern = f"evolution_completed_ev_*_{round_num}.json"
            matches = list(STATE_DIR.glob(pattern))

            return matches[0] if matches else None
        except Exception:
            return None

    def _evaluate_decision_quality(self, round_data: Dict) -> float:
        """评估决策质量"""
        was_completed = round_data.get("was_completed", False)
        baseline_passed = round_data.get("baseline_passed", False)
        targeted_verification = round_data.get("targeted_verification_passed", False)

        # 简单的质量评分
        quality = 0.0
        if was_completed:
            quality += 0.4
        if baseline_passed:
            quality += 0.3
        if targeted_verification:
            quality += 0.3

        return quality

    def _identify_cognitive_biases(self, round_data: Dict) -> List[str]:
        """识别认知偏差"""
        biases = []

        current_goal = round_data.get("current_goal", "")
        was_completed = round_data.get("was_completed", False)

        # 过度自信偏差
        if not was_completed and current_goal:
            biases.append("overconfidence")

        # 确认偏差
        if was_completed and not round_data.get("targeted_verification_passed", False):
            biases.append("confirmation_bias")

        # 后见之明偏差
        if "error" in str(round_data.get("message", "")).lower():
            biases.append("hindsight_bias")

        return biases

    def _generate_reflection_insights(self, decision_quality: float, biases: List[str]) -> List[str]:
        """生成反思洞察"""
        insights = []

        if decision_quality >= 0.7:
            insights.append("本轮决策质量良好，目标设定和执行都较为成功")
        elif decision_quality >= 0.4:
            insights.append("本轮决策质量中等，部分目标达成但有改进空间")
        else:
            insights.append("本轮决策质量较低，需要重新审视决策过程")

        if "overconfidence" in biases:
            insights.append("可能存在过度自信问题，建议在设定目标时更加保守")

        if "confirmation_bias" in biases:
            insights.append("可能存在确认偏差，建议更多关注负面反馈")

        return insights

    def _calculate_meta_cognition_level(self, cognitions: List[Dict]) -> float:
        """计算元认知水平"""
        if not cognitions:
            return 0.0

        # 基于反思深度和洞察数量计算
        total_reflection_depth = 0.0
        for c in cognitions:
            insights = c.get("self_reflection_insights", [])
            total_reflection_depth += min(len(insights) / 5.0, 1.0)

        return total_reflection_depth / len(cognitions)

    def _analyze_cognition_trend(self) -> str:
        """分析认知趋势"""
        if len(self.cognition_history) < 3:
            return "insufficient_data"

        recent = self.cognition_history[-3:]
        qualities = [c.get("decision_quality", 0) for c in recent]

        if qualities[-1] > qualities[0]:
            return "improving"
        elif qualities[-1] < qualities[0]:
            return "declining"
        else:
            return "stable"

    def _collect_system_state(self) -> Dict:
        """收集系统状态信息"""
        return {
            "total_engines": len(list(PROJECT_ROOT.glob("scripts/evolution_*.py"))),
            "completed_rounds": self._get_latest_completed_round() or 0,
            "active_capabilities": len(self.capabilities)
        }

    def _analyze_capabilities(self) -> Dict:
        """分析能力分布"""
        # 读取 capabilities.md 获取能力概览
        capabilities_file = REFERENCES_DIR / "capabilities.md"

        if capabilities_file.exists():
            try:
                with open(capabilities_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # 统计能力数量
                    capability_count = content.count('|')
                    return {
                        "total_capabilities": capability_count,
                        "analysis": "基于 capabilities.md 统计"
                    }
            except Exception:
                pass

        return {
            "total_capabilities": 0,
            "analysis": "无法获取能力统计"
        }

    def _identify_cognitive_strengths(self) -> List[str]:
        """识别认知优势"""
        strengths = []

        if self.awareness_metrics.get("meta_cognition_level", 0) > 0.6:
            strengths.append("较强的元认知能力")

        if self.awareness_metrics.get("decision_quality", 0) > 0.7:
            strengths.append("高质量的决策能力")

        if self.awareness_metrics.get("self_reflection_depth", 0) > 0.5:
            strengths.append("深入的自我反思能力")

        return strengths if strengths else ["持续学习和改进"]

    def _identify_cognitive_weaknesses(self) -> List[str]:
        """识别认知弱点"""
        weaknesses = []

        if self.awareness_metrics.get("meta_cognition_level", 0) < 0.4:
            weaknesses.append("元认知能力有待提升")

        if self.awareness_metrics.get("decision_quality", 0) < 0.5:
            weaknesses.append("决策质量需要改进")

        if self.awareness_metrics.get("cognitive_bias_awareness", 0) < 0.3:
            weaknesses.append("认知偏差识别能力较弱")

        return weaknesses if weaknesses else ["持续优化中"]


def main():
    """主函数：处理命令行参数"""
    import argparse

    parser = argparse.ArgumentParser(
        description="智能全场景深度认知与自主意识增强引擎"
    )
    parser.add_argument("--reflect", action="store_true", help="执行自我反思")
    parser.add_argument("--evaluate", action="store_true", help="评估认知质量")
    parser.add_argument("--optimize", action="store_true", help="生成认知优化策略")
    parser.add_argument("--awareness", action="store_true", help="增强自我意识")
    parser.add_argument("--cockpit-data", action="store_true", help="获取驾驶舱数据")
    parser.add_argument("--round", type=int, help="指定进化轮次")
    parser.add_argument("--all", action="store_true", help="执行所有功能")

    args = parser.parse_args()

    engine = EvolutionDeepCognitionAwarenessEngine()

    if not any([args.reflect, args.evaluate, args.optimize, args.awareness, args.cockpit_data, args.all]):
        # 默认显示状态
        print("=" * 60)
        print("深度认知与自主意识增强引擎")
        print(f"Version: {engine.version}")
        print("=" * 60)
        print("\n可用功能:")
        print("  --reflect     执行自我反思")
        print("  --evaluate    评估认知质量")
        print("  --optimize    生成认知优化策略")
        print("  --awareness   增强自我意识")
        print("  --cockpit-data 获取驾驶舱数据")
        print("  --all         执行所有功能")
        print("\n可用的能力:")
        for cap in engine.capabilities:
            print(f"  - {cap}")
        return

    result = {}

    if args.reflect or args.all:
        print("\n[1/4] 执行自我反思...")
        result["self_reflect"] = engine.self_reflect(args.round)
        print(f"  状态: {result['self_reflect'].get('status')}")

    if args.evaluate or args.all:
        print("\n[2/4] 评估认知质量...")
        result["evaluate"] = engine.evaluate_cognition_quality()
        print(f"  状态: {result['evaluate'].get('status')}")
        if result['evaluate'].get('metrics'):
            print(f"  指标: {result['evaluate']['metrics']}")

    if args.optimize or args.all:
        print("\n[3/4] 生成认知优化策略...")
        result["optimize"] = engine.generate_cognition_optimization()
        print(f"  状态: {result['optimize'].get('status')}")
        suggestions = result['optimize'].get('optimization_suggestions', [])
        print(f"  优化建议数量: {len(suggestions)}")

    if args.awareness or args.all:
        print("\n[4/4] 增强自我意识...")
        result["awareness"] = engine.enhance_self_awareness()
        print(f"  状态: {result['awareness'].get('status')}")

    if args.cockpit_data or args.all:
        print("\n[驾驶舱] 获取可视化数据...")
        cockpit = engine.get_cockpit_data()
        print(f"  状态: {cockpit.get('status')}")
        # 保存到文件
        cockpit_file = STATE_DIR / "deep_cognition_cockpit_data.json"
        with open(cockpit_file, 'w', encoding='utf-8') as f:
            json.dump(cockpit, f, ensure_ascii=False, indent=2)
        print(f"  数据已保存到: {cockpit_file}")

    print("\n" + "=" * 60)
    print("执行完成")
    print("=" * 60)


if __name__ == "__main__":
    main()