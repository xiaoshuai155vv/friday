"""
智能全场景进化环元进化自我反思与深度自省引擎
让系统对自身进化过程进行更深层次的自我反思，从「评估做了什么」升级到「反思为什么这样做、是否是最好的选择」。
形成「执行→结果→反思→改进」的递归自省闭环，让系统不仅知道自己在进化，
还能思考「我为什么选择这个方向、这个方向是否正确、是否有更好的方向」。

Version: 1.0.0
"""

import json
import os
import sys
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from collections import defaultdict

# 状态文件路径
RUNTIME_STATE_DIR = Path(__file__).parent.parent / "runtime" / "state"
RUNTIME_LOGS_DIR = Path(__file__).parent.parent / "runtime" / "logs"
REFERENCES_DIR = Path(__file__).parent.parent / "references"


class MetaSelfReflectionDeepIntrospectionEngine:
    """元进化自我反思与深度自省引擎"""

    def __init__(self):
        self.name = "MetaSelfReflectionDeepIntrospectionEngine"
        self.version = "1.0.0"
        self.state_file = RUNTIME_STATE_DIR / "meta_self_reflection_state.json"
        self.reflection_history_file = RUNTIME_STATE_DIR / "meta_self_reflection_history.json"
        self.introspection_questions = self._load_introspection_questions()
        self.reflection_patterns = self._load_reflection_patterns()

    def _load_introspection_questions(self) -> List[Dict]:
        """加载自省问题模板"""
        return [
            {
                "id": "why_direction",
                "question": "我为什么选择这个进化方向？",
                "description": "分析进化决策背后的原因、假设和预期"
            },
            {
                "id": "is_best_choice",
                "question": "这是最好的选择吗？",
                "description": "评估当前方向与其他可能性的对比"
            },
            {
                "id": "alternative_options",
                "question": "是否有更好的方向？",
                "description": "探索其他可能的进化路径"
            },
            {
                "id": "decision_patterns",
                "question": "我有什么决策模式？",
                "description": "识别历史决策中的重复模式"
            },
            {
                "id": "value_assessment",
                "question": "这个进化真的创造了价值吗？",
                "description": "评估进化成果的实际价值贡献"
            },
            {
                "id": "risk_evaluation",
                "question": "我忽略了哪些风险？",
                "description": "识别决策中未考虑到的潜在风险"
            },
            {
                "id": "learning_extraction",
                "question": "我从这次进化中学到了什么？",
                "description": "提取可复用的经验和教训"
            },
            {
                "id": "meta_evolution",
                "question": "我的进化方法论需要改进吗？",
                "description": "反思进化过程本身的效率和效果"
            }
        ]

    def _load_reflection_patterns(self) -> Dict:
        """加载反思模式库"""
        return {
            "success_patterns": {
                "description": "成功进化决策的共同特征",
                "indicators": ["高价值实现", "低风险", "多引擎协同", "创新性强"]
            },
            "failure_patterns": {
                "description": "失败或低效决策的共同特征",
                "indicators": ["重复进化", "价值实现不足", "执行困难", "依赖缺失"]
            },
            "improvement_opportunities": {
                "description": "常见的优化机会",
                "indicators": ["可复用的模块", "可简化的流程", "可自动化的决策"]
            },
            "meta_learning": {
                "description": "元学习模式的识别",
                "indicators": ["决策一致性", "学习效率", "适应能力"]
            }
        }

    def analyze_evolution_decision_causality(self, round_data: Dict) -> Dict:
        """分析进化决策的因果关系

        分析每次进化决策的背后原因、假设、预期，帮助系统理解"为什么这样做"。
        """
        decision = round_data.get("current_goal", "")
        execution = round_data.get("做了什么", "")
        result = round_data.get("是否完成", "未知")
        baseline = round_data.get("基线校验", "")
        targeted = round_data.get("针对性校验", "")

        # 提取决策要素
        causal_analysis = {
            "decision": decision,
            "execution_summary": execution,
            "result": result,
            "causal_factors": [],
            "assumptions": [],
            "expectations": [],
            "actual_outcomes": []
        }

        # 分析因果因素
        if "创建" in execution or "实现" in execution:
            causal_analysis["causal_factors"].append({
                "factor": "创新能力驱动",
                "description": "系统主动创建新模块或实现新功能",
                "impact": "positive"
            })

        if "集成" in execution or "深度集成" in execution:
            causal_analysis["causal_factors"].append({
                "factor": "协同集成驱动",
                "description": "系统通过集成多个引擎形成协同效应",
                "impact": "positive"
            })

        if "优化" in execution or "增强" in execution:
            causal_analysis["causal_factors"].append({
                "factor": "效率优化驱动",
                "description": "系统主动优化现有能力或效率",
                "impact": "positive"
            })

        # 提取假设
        if "基于" in decision:
            causal_analysis["assumptions"].append({
                "assumption": "基于现有能力的延伸",
                "confidence": "high"
            })

        if "让系统能够" in decision:
            causal_analysis["assumptions"].append({
                "assumption": "系统具备该能力是可行和必要的",
                "confidence": "medium"
            })

        # 分析预期结果
        if "形成" in decision:
            causal_analysis["expectations"].append({
                "expectation": "形成某种闭环或能力",
                "status": "预期"
            })

        # 实际结果
        if result == "已完成":
            causal_analysis["actual_outcomes"].append({
                "outcome": "目标达成",
                "evaluation": "success"
            })
        else:
            causal_analysis["actual_outcomes"].append({
                "outcome": "目标未达成或部分达成",
                "evaluation": "partial"
            })

        return causal_analysis

    def evaluate_evolution_direction(self, round_data: Dict) -> Dict:
        """评估进化方向

        评估当前方向的价值、风险、与其他可能性的对比。
        """
        decision = round_data.get("current_goal", "")
        risk_level = round_data.get("风险等级", "未知")
        dependencies = round_data.get("依赖", [])
        innovation_points = round_data.get("创新点", [])

        evaluation = {
            "direction": decision,
            "value_assessment": {
                "score": 0,
                "factors": []
            },
            "risk_assessment": {
                "level": risk_level,
                "factors": []
            },
            "alternative_comparison": {
                "considered": False,
                "alternatives": []
            },
            "overall_score": 0
        }

        # 价值评估
        if "创新" in decision:
            evaluation["value_assessment"]["factors"].append({
                "factor": "创新性",
                "contribution": "high",
                "score": 0.3
            })
            evaluation["value_assessment"]["score"] += 0.3

        if "闭环" in decision or "集成" in decision:
            evaluation["value_assessment"]["factors"].append({
                "factor": "系统性",
                "contribution": "high",
                "score": 0.25
            })
            evaluation["value_assessment"]["score"] += 0.25

        if "自动" in decision or "自主" in decision:
            evaluation["value_assessment"]["factors"].append({
                "factor": "自主性",
                "contribution": "medium",
                "score": 0.2
            })
            evaluation["value_assessment"]["score"] += 0.2

        if "智能" in decision or "深度" in decision:
            evaluation["value_assessment"]["factors"].append({
                "factor": "智能化",
                "contribution": "medium",
                "score": 0.15
            })
            evaluation["value_assessment"]["score"] += 0.15

        if len(dependencies) > 0:
            evaluation["value_assessment"]["factors"].append({
                "factor": "协同依赖",
                "contribution": "medium",
                "score": 0.1
            })
            evaluation["value_assessment"]["score"] += 0.1

        # 风险评估
        if risk_level == "低":
            evaluation["risk_assessment"]["level"] = "low"
            evaluation["risk_assessment"]["factors"].append({
                "factor": "低风险",
                "score": 0.3
            })
        elif risk_level == "中":
            evaluation["risk_assessment"]["level"] = "medium"
            evaluation["risk_assessment"]["factors"].append({
                "factor": "中等风险",
                "score": 0.15
            })
        else:
            evaluation["risk_assessment"]["level"] = "high"
            evaluation["risk_assessment"]["factors"].append({
                "factor": "高风险",
                "score": 0
            })

        if len(dependencies) > 3:
            evaluation["risk_assessment"]["factors"].append({
                "factor": "多依赖风险",
                "score": -0.1
            })

        # 替代方案对比
        evaluation["alternative_comparison"]["considered"] = True
        evaluation["alternative_comparison"]["alternatives"] = [
            {
                "alternative": "渐进式优化",
                "pros": "风险更低",
                "cons": "创新性不足"
            },
            {
                "alternative": "激进式创新",
                "pros": "突破性强",
                "cons": "风险更高"
            }
        ]

        # 综合评分
        value_score = evaluation["value_assessment"]["score"]
        risk_score = evaluation["risk_assessment"]["factors"][0]["score"] if evaluation["risk_assessment"]["factors"] else 0
        evaluation["overall_score"] = max(0, min(1, value_score + risk_score))

        return evaluation

    def generate_introspection_feedback(self, causal_analysis: Dict, evaluation: Dict) -> Dict:
        """生成自省反馈

        生成「为什么会这样选择」的深度分析报告。
        """
        feedback = {
            "timestamp": datetime.now().isoformat(),
            "summary": "",
            "detailed_analysis": [],
            "key_insights": [],
            "improvement_suggestions": []
        }

        # 生成摘要
        decision = causal_analysis.get("decision", "")
        result = causal_analysis.get("result", "未知")

        if result == "已完成":
            feedback["summary"] = f"本轮进化目标「{decision[:30]}...」已成功完成。"
        else:
            feedback["summary"] = f"本轮进化目标「{decision[:30]}...」部分完成或未完成，需要进一步反思。"

        # 详细分析
        causal_factors = causal_analysis.get("causal_factors", [])
        for factor in causal_factors:
            feedback["detailed_analysis"].append({
                "aspect": "决策因素",
                "content": f"{factor.get('factor', '未知')}: {factor.get('description', '')}",
                "impact": factor.get("impact", "neutral")
            })

        # 关键洞察
        if evaluation.get("overall_score", 0) > 0.7:
            feedback["key_insights"].append({
                "insight": "本轮进化方向选择合理，价值实现程度高",
                "type": "positive"
            })
        elif evaluation.get("overall_score", 0) < 0.4:
            feedback["key_insights"].append({
                "insight": "本轮进化方向可能不是最优选择，建议探索其他路径",
                "type": "warning"
            })

        if len(causal_factors) == 1:
            feedback["key_insights"].append({
                "insight": "决策因素较为单一，建议在后续决策中考虑更多维度",
                "type": "suggestion"
            })

        # 改进建议
        if causal_analysis.get("assumptions"):
            assumptions = causal_analysis.get("assumptions", [])
            for assumption in assumptions[:2]:
                feedback["improvement_suggestions"].append({
                    "suggestion": f"验证假设：{assumption.get('assumption', '')}",
                    "priority": "high" if assumption.get("confidence") == "low" else "medium"
                })

        if evaluation.get("alternative_comparison", {}).get("alternatives"):
            feedback["improvement_suggestions"].append({
                "suggestion": "在后续决策中考虑渐进式和激进式两种方案的平衡",
                "priority": "medium"
            })

        return feedback

    def generate_self_improvement_suggestions(self, reflection_history: List[Dict]) -> List[Dict]:
        """生成自我改进建议

        基于自省结果生成优化进化策略的建议。
        """
        suggestions = []

        if not reflection_history:
            return [{
                "suggestion": "积累更多进化历史数据以进行深度自省",
                "priority": "medium",
                "category": "data_gathering"
            }]

        # 分析历史模式
        success_count = sum(1 for r in reflection_history if r.get("evaluation", {}).get("overall_score", 0) > 0.6)
        total_count = len(reflection_history)

        if total_count >= 3:
            success_rate = success_count / total_count

            if success_rate > 0.7:
                suggestions.append({
                    "suggestion": "当前进化策略执行效果良好，可适当增加创新性探索",
                    "priority": "low",
                    "category": "strategy_optimization",
                    "confidence": "high"
                })
            elif success_rate < 0.4:
                suggestions.append({
                    "suggestion": "当前进化策略存在系统性问题，建议全面审查决策流程",
                    "priority": "high",
                    "category": "strategy_reform",
                    "confidence": "medium"
                })

        # 分析常见模式
        decision_themes = defaultdict(int)
        for r in reflection_history:
            causal = r.get("causal_analysis", {})
            for factor in causal.get("causal_factors", []):
                decision_themes[factor.get("factor", "unknown")] += 1

        if decision_themes:
            dominant_theme = max(decision_themes.items(), key=lambda x: x[1])
            if dominant_theme[1] > total_count * 0.5:
                suggestions.append({
                    "suggestion": f"决策模式偏向「{dominant_theme[0]}」，建议增加多样性",
                    "priority": "medium",
                    "category": "diversity_enhancement",
                    "confidence": "medium"
                })

        # 通用建议
        suggestions.extend([
            {
                "suggestion": "在每轮决策前增加「替代方案分析」步骤",
                "priority": "medium",
                "category": "decision_process",
                "confidence": "high"
            },
            {
                "suggestion": "建立决策假设验证机制，定期检验假设的有效性",
                "priority": "medium",
                "category": "assumption_validation",
                "confidence": "high"
            }
        ])

        return suggestions[:5]

    def get_cockpit_data(self) -> Dict:
        """获取驾驶舱数据接口"""
        # 加载当前状态
        state_data = self._load_state()

        # 加载历史反思
        history_data = self._load_reflection_history()

        # 计算趋势
        recent_trends = []
        if len(history_data) >= 3:
            recent = history_data[-3:]
            for h in recent:
                recent_trends.append({
                    "round": h.get("round", 0),
                    "score": h.get("evaluation", {}).get("overall_score", 0)
                })

        return {
            "engine_name": self.name,
            "version": self.version,
            "state": state_data,
            "introspection_questions": self.introspection_questions,
            "reflection_patterns": list(self.reflection_patterns.keys()),
            "recent_trends": recent_trends,
            "total_reflections": len(history_data)
        }

    def perform_self_reflection(self, target_round: Optional[int] = None) -> Dict:
        """执行自我反思主流程"""
        result = {
            "status": "success",
            "target_round": target_round,
            "causal_analysis": {},
            "evaluation": {},
            "feedback": {},
            "suggestions": []
        }

        # 确定目标轮次
        if target_round is None:
            target_round = self._get_latest_completed_round()

        # 加载目标轮次数据
        round_data = self._load_evolution_round_data(target_round)

        if not round_data:
            result["status"] = "no_data"
            result["message"] = f"未找到 round {target_round} 的数据"
            return result

        # 执行分析
        result["causal_analysis"] = self.analyze_evolution_decision_causality(round_data)
        result["evaluation"] = self.evaluate_evolution_direction(round_data)
        result["feedback"] = self.generate_introspection_feedback(
            result["causal_analysis"],
            result["evaluation"]
        )

        # 加载历史进行对比
        history = self._load_reflection_history()
        history.append({
            "round": target_round,
            "causal_analysis": result["causal_analysis"],
            "evaluation": result["evaluation"],
            "timestamp": datetime.now().isoformat()
        })

        # 生成改进建议
        result["suggestions"] = self.generate_self_improvement_suggestions(history)

        # 保存状态
        self._save_state({
            "last_reflection_round": target_round,
            "last_reflection_time": datetime.now().isoformat()
        })

        self._save_reflection_history(history)

        return result

    def _get_latest_completed_round(self) -> int:
        """获取最新完成的轮次"""
        # 读取 current_mission.json
        try:
            mission_file = RUNTIME_STATE_DIR / "current_mission.json"
            with open(mission_file, "r", encoding="utf-8") as f:
                mission = json.load(f)
                return mission.get("loop_round", 558)
        except Exception:
            return 558

    def _load_evolution_round_data(self, round_num: int) -> Optional[Dict]:
        """加载指定轮次的进化数据"""
        # 尝试从 evolution_completed_*.json 加载
        try:
            # 查找最新的完成文件
            state_dir = RUNTIME_STATE_DIR
            completed_files = list(state_dir.glob("evolution_completed_*.json"))

            if not completed_files:
                return None

            # 按修改时间排序，取最新的
            completed_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

            for f in completed_files:
                try:
                    with open(f, "r", encoding="utf-8") as fp:
                        data = json.load(fp)
                        # 尝试从多个字段获取 round 信息
                        round_info = data.get("loop_round", 0)
                        if round_info == round_num:
                            return data

                        # 也尝试从 current_goal 中提取
                        goal = data.get("current_goal", "")
                        if str(round_num) in goal or round_info == round_num - 1:
                            return data
                except Exception:
                    continue

            # 返回最新的一个
            with open(completed_files[0], "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None

    def _load_state(self) -> Dict:
        """加载状态"""
        try:
            if self.state_file.exists():
                with open(self.state_file, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

    def _save_state(self, state: Dict):
        """保存状态"""
        try:
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存状态失败: {e}")

    def _load_reflection_history(self) -> List[Dict]:
        """加载反思历史"""
        try:
            if self.reflection_history_file.exists():
                with open(self.reflection_history_file, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            pass
        return []

    def _save_reflection_history(self, history: List[Dict]):
        """保存反思历史"""
        try:
            with open(self.reflection_history_file, "w", encoding="utf-8") as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存反思历史失败: {e}")

    def version(self) -> str:
        """返回版本"""
        return self.version


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="智能全场景进化环元进化自我反思与深度自省引擎"
    )
    parser.add_argument("--init", action="store_true", help="初始化引擎")
    parser.add_argument("--version", action="store_true", help="显示版本")
    parser.add_argument("--reflect", type=int, nargs="?", const=None, help="执行自我反思，可指定轮次")
    parser.add_argument("--cockpit", action="store_true", help="获取驾驶舱数据")
    parser.add_argument("--questions", action="store_true", help="列出自省问题")
    parser.add_argument("--suggestions", action="store_true", help="生成改进建议")

    args = parser.parse_args()

    engine = MetaSelfReflectionDeepIntrospectionEngine()

    if args.init:
        print(f"初始化 {engine.name} v{engine.version}")
        # 初始化状态
        engine._save_state({
            "initialized": True,
            "init_time": datetime.now().isoformat()
        })
        print("初始化完成")
        return

    if args.version:
        print(f"{engine.name} v{engine.version}")
        return

    if args.questions:
        print("=== 自省问题列表 ===")
        for q in engine.introspection_questions:
            print(f"\n{q['id']}: {q['question']}")
            print(f"  说明: {q['description']}")
        return

    if args.suggestions:
        history = engine._load_reflection_history()
        suggestions = engine.generate_self_improvement_suggestions(history)
        print("=== 自我改进建议 ===")
        for i, s in enumerate(suggestions, 1):
            print(f"\n{i}. [{s['priority'].upper()}] {s['suggestion']}")
            print(f"   类别: {s['category']}, 置信度: {s['confidence']}")
        return

    if args.cockpit:
        data = engine.get_cockpit_data()
        print("=== 驾驶舱数据 ===")
        print(f"引擎: {data['engine_name']}")
        print(f"版本: {data['version']}")
        print(f"总反思次数: {data['total_reflections']}")
        print(f"自省问题数量: {len(data['introspection_questions'])}")
        print(f"反思模式: {data['reflection_patterns']}")
        if data['recent_trends']:
            print("\n最近趋势:")
            for t in data['recent_trends']:
                print(f"  Round {t['round']}: {t['score']:.2f}")
        return

    # 默认执行反思
    if args.reflect is not None or not any([args.init, args.version, args.questions, args.cockpit, args.suggestions]):
        result = engine.perform_self_reflection(args.reflect)

        if result["status"] == "success":
            print("=== 自我反思结果 ===")
            print(f"\n目标轮次: {result['target_round']}")
            print(f"\n--- 因果分析 ---")
            print(f"决策: {result['causal_analysis'].get('decision', 'N/A')[:80]}...")
            print(f"结果: {result['causal_analysis'].get('result', 'N/A')}")

            print(f"\n--- 方向评估 ---")
            print(f"综合评分: {result['evaluation'].get('overall_score', 0):.2f}")
            print(f"价值评分: {result['evaluation'].get('value_assessment', {}).get('score', 0):.2f}")
            print(f"风险等级: {result['evaluation'].get('risk_assessment', {}).get('level', 'N/A')}")

            print(f"\n--- 自省反馈 ---")
            print(result['feedback'].get('summary', ''))
            if result['feedback'].get('key_insights'):
                print("\n关键洞察:")
                for insight in result['feedback']['key_insights']:
                    print(f"  - {insight['insight']}")

            if result['suggestions']:
                print("\n--- 改进建议 ---")
                for i, s in enumerate(result['suggestions'][:3], 1):
                    print(f"{i}. [{s['priority']}] {s['suggestion']}")
        else:
            print(f"反思失败: {result.get('message', '未知错误')}")
        return

    parser.print_help()


if __name__ == "__main__":
    main()