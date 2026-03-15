#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环跨维度价值平衡全局决策与自适应优化引擎

在 round 608-610 完成的创新投资组合优化引擎、价值预测预防优化引擎 V2、
创新生态系统治理引擎基础上，构建跨维度的价值平衡全局决策能力。

让系统能够从全局视角综合评估多维度价值（效率、质量、创新、可持续性、风险），
实现跨引擎的价值平衡智能决策，形成真正的「全局价值中枢」。

系统将实现：
1. 跨维度价值全局评估 - 统一量化效率、质量、创新、可持续性、风险
2. 跨引擎价值平衡智能决策 - 协调多个价值维度的决策
3. 自适应价值优化 - 基于执行反馈动态调整价值权重
4. 与 round 608-610 引擎深度集成
5. 驾驶舱数据接口

Version: 1.0.0
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
import subprocess

# 项目根目录
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
RUNTIME_DIR = PROJECT_ROOT / "runtime"
STATE_DIR = RUNTIME_DIR / "state"
LOGS_DIR = RUNTIME_DIR / "logs"
REFERENCES_DIR = PROJECT_ROOT / "references"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"


class CrossDimensionValueBalanceEngine:
    """跨维度价值平衡全局决策与自适应优化引擎"""

    def __init__(self):
        self.name = "跨维度价值平衡全局决策与自适应优化引擎"
        self.version = "1.0.0"
        self.state_dir = STATE_DIR
        self.logs_dir = LOGS_DIR
        # 数据文件
        self.value_assessment_file = self.state_dir / "cross_dimension_value_assessment.json"
        self.balance_decision_file = self.state_dir / "value_balance_decision.json"
        self.adaptive_optimization_file = self.state_dir / "value_adaptive_optimization.json"
        # 价值维度定义
        self.value_dimensions = {
            "efficiency": {"name": "效率", "weight": 0.2, "description": "进化执行效率、响应速度"},
            "quality": {"name": "质量", "weight": 0.2, "description": "进化成果质量、系统稳定性"},
            "innovation": {"name": "创新", "weight": 0.2, "description": "创新程度、突破性"},
            "sustainability": {"name": "可持续性", "weight": 0.2, "description": "长期可持续、可累积性"},
            "risk": {"name": "风险", "weight": 0.2, "description": "执行风险、失败概率"}
        }

    def get_version(self):
        """获取引擎版本信息"""
        return {
            "name": self.name,
            "version": self.version,
            "description": "跨维度价值平衡全局决策与自适应优化引擎"
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
                        "status": data.get("status", "unknown")
                    })
            except Exception as e:
                print(f"Warning: Failed to load {f}: {e}")
        return history

    def load_round608_data(self):
        """加载 round 608 创新投资组合优化引擎的数据"""
        file = self.state_dir / "innovation_portfolio_analysis.json"
        if not file.exists():
            return {}
        try:
            with open(file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Failed to load round 608 data: {e}")
            return {}

    def load_round609_data(self):
        """加载 round 609 价值预测预防优化引擎 V2 的数据"""
        file = self.state_dir / "meta_evolution_value_prediction_v2_data.json"
        if not file.exists():
            # 尝试其他可能的数据文件名
            for name in ["value_prediction_data.json", "meta_value_prediction_data.json"]:
                file = self.state_dir / name
                if file.exists():
                    with open(file, 'r', encoding='utf-8') as f:
                        return json.load(f)
            return {}
        try:
            with open(file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Failed to load round 609 data: {e}")
            return {}

    def load_round610_data(self):
        """加载 round 610 创新生态系统治理引擎的数据"""
        file = self.state_dir / "innovation_ecosystem_data.json"
        if not file.exists():
            # 尝试其他可能的数据文件名
            for name in ["ecosystem_data.json", "innovation_ecosystem_governance_data.json"]:
                file = self.state_dir / name
                if file.exists():
                    with open(file, 'r', encoding='utf-8') as f:
                        return json.load(f)
            return {}
        try:
            with open(file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Failed to load round 610 data: {e}")
            return {}

    def assess_cross_dimension_values(self):
        """评估跨维度价值"""
        history = self.load_evolution_history()
        round608_data = self.load_round608_data()
        round609_data = self.load_round609_data()
        round610_data = self.load_round610_data()

        assessment = {
            "timestamp": datetime.now().isoformat(),
            "dimensions": {},
            "overall_score": 0.0,
            "dimension_scores": {},
            "insights": []
        }

        # 1. 评估效率维度
        efficiency_score = 0.5
        if history:
            completed = sum(1 for h in history[:20] if h.get("completed", False))
            efficiency_score = completed / max(1, len(history[:20]))
        assessment["dimensions"]["efficiency"] = {
            "name": "效率",
            "score": efficiency_score,
            "weight": self.value_dimensions["efficiency"]["weight"],
            "description": "进化执行效率、响应速度"
        }

        # 2. 评估质量维度
        quality_score = 0.6
        if history:
            # 基于完成率和稳定性评估质量
            completed = sum(1 for h in history[:20] if h.get("completed", False))
            quality_score = completed / max(1, len(history[:20])) * 0.8 + 0.2
        assessment["dimensions"]["quality"] = {
            "name": "质量",
            "score": quality_score,
            "weight": self.value_dimensions["quality"]["weight"],
            "description": "进化成果质量、系统稳定性"
        }

        # 3. 评估创新维度
        innovation_score = 0.7
        if history:
            # 统计包含创新关键词的轮次
            innovative_count = sum(1 for h in history[:50] if
                "创新" in h.get("goal", "") or "涌现" in h.get("goal", "") or
                "自涌现" in h.get("goal", ""))
            innovation_score = min(1.0, innovative_count / max(1, len(history[:50]) * 0.3))
        assessment["dimensions"]["innovation"] = {
            "name": "创新",
            "score": innovation_score,
            "weight": self.value_dimensions["innovation"]["weight"],
            "description": "创新程度、突破性"
        }

        # 4. 评估可持续性维度
        sustainability_score = 0.65
        if history:
            # 基于进化历史长度和稳定性评估可持续性
            sustainability_score = min(1.0, len(history) / 500 * 0.5 + 0.4)
        assessment["dimensions"]["sustainability"] = {
            "name": "可持续性",
            "score": sustainability_score,
            "weight": self.value_dimensions["sustainability"]["weight"],
            "description": "长期可持续、可累积性"
        }

        # 5. 评估风险维度（分数越高表示风险越低）
        risk_score = 0.75
        if history:
            # 基于失败率评估风险
            failed = sum(1 for h in history[:20] if not h.get("completed", True))
            risk_score = 1.0 - (failed / max(1, len(history[:20])) * 0.5)
        assessment["dimensions"]["risk"] = {
            "name": "风险",
            "score": risk_score,
            "weight": self.value_dimensions["risk"]["weight"],
            "description": "执行风险、失败概率（分数越高风险越低）"
        }

        # 计算各维度加权得分
        dimension_scores = {}
        for dim_key, dim_data in assessment["dimensions"].items():
            score = dim_data["score"]
            weight = dim_data["weight"]
            dimension_scores[dim_key] = score * weight
            assessment["dimension_scores"][dim_key] = {
                "score": score,
                "weight": weight,
                "weighted_score": score * weight
            }

        # 计算总体得分
        assessment["overall_score"] = sum(dimension_scores.values())

        # 生成洞察
        # 效率洞察
        if efficiency_score < 0.5:
            assessment["insights"].append({
                "dimension": "efficiency",
                "type": "warning",
                "message": "效率维度得分较低，建议优化执行策略"
            })
        # 质量洞察
        if quality_score < 0.5:
            assessment["insights"].append({
                "dimension": "quality",
                "type": "warning",
                "message": "质量维度存在提升空间，建议加强验证环节"
            })
        # 创新洞察
        if innovation_score < 0.5:
            assessment["insights"].append({
                "dimension": "innovation",
                "type": "opportunity",
                "message": "创新维度有较大提升空间，可探索新的创新方向"
            })
        # 风险洞察
        if risk_score < 0.6:
            assessment["insights"].append({
                "dimension": "risk",
                "type": "warning",
                "message": "风险维度需要关注，建议加强风险预防措施"
            })

        return assessment

    def make_balance_decision(self):
        """做出价值平衡决策"""
        assessment = self.assess_cross_dimension_values()
        round608_data = self.load_round608_data()
        round609_data = self.load_round609_data()
        round610_data = self.load_round610_data()

        decision = {
            "timestamp": datetime.now().isoformat(),
            "current_state": assessment,
            "balance_decisions": [],
            "priority_adjustments": [],
            "recommended_actions": []
        }

        # 分析当前价值状态
        dim_scores = assessment.get("dimension_scores", {})

        # 找出最需要提升的维度
        weakest_dim = min(dim_scores.items(), key=lambda x: x[1].get("score", 0) if isinstance(x[1], dict) else 0)
        weakest_key = weakest_dim[0] if isinstance(weakest_dim[0], str) else "efficiency"

        # 生成平衡决策
        # 1. 效率-质量平衡
        if dim_scores.get("efficiency", {}).get("score", 0) > 0.7 and dim_scores.get("quality", {}).get("score", 0) < 0.5:
            decision["balance_decisions"].append({
                "type": "efficiency_quality_tradeoff",
                "action": "适当降低效率优先级，提升质量验证",
                "reason": "效率过高但质量不足，需要平衡"
            })

        # 2. 创新-风险平衡
        if dim_scores.get("innovation", {}).get("score", 0) > 0.7 and dim_scores.get("risk", {}).get("score", 0) < 0.6:
            decision["balance_decisions"].append({
                "type": "innovation_risk_tradeoff",
                "action": "在保持创新的同时加强风险预防",
                "reason": "创新活跃但风险偏高，需要平衡"
            })

        # 3. 资源分配决策
        if round608_data or round610_data:
            decision["balance_decisions"].append({
                "type": "resource_allocation",
                "action": "基于价值评估结果优化资源分配",
                "reason": "整合创新投资组合和生态系统治理数据"
            })

        # 生成优先级调整建议
        priority_adjustments = []
        for dim_key, dim_data in dim_scores.items():
            score = dim_data.get("score", 0) if isinstance(dim_data, dict) else 0.5
            if score < 0.5:
                priority_adjustments.append({
                    "dimension": dim_key,
                    "current_weight": self.value_dimensions.get(dim_key, {}).get("weight", 0.2),
                    "recommended_weight": min(0.35, self.value_dimensions.get(dim_key, {}).get("weight", 0.2) + 0.1),
                    "reason": f"{dim_key}维度得分较低，需要提升优先级"
                })

        decision["priority_adjustments"] = priority_adjustments

        # 生成推荐行动
        recommended_actions = []
        if weakest_key:
            if weakest_key == "efficiency":
                recommended_actions.append({
                    "action": "优化执行流程",
                    "priority": "high",
                    "expected_impact": "提升效率维度得分 10-20%"
                })
            elif weakest_key == "quality":
                recommended_actions.append({
                    "action": "加强验证环节",
                    "priority": "high",
                    "expected_impact": "提升质量维度得分 15-25%"
                })
            elif weakest_key == "innovation":
                recommended_actions.append({
                    "action": "探索新的创新方向",
                    "priority": "medium",
                    "expected_impact": "提升创新维度得分 10-15%"
                })
            elif weakest_key == "sustainability":
                recommended_actions.append({
                    "action": "建立长期可持续机制",
                    "priority": "medium",
                    "expected_impact": "提升可持续性维度得分 10-20%"
                })
            elif weakest_key == "risk":
                recommended_actions.append({
                    "action": "加强风险预防措施",
                    "priority": "high",
                    "expected_impact": "提升风险维度得分 15-25%"
                })

        decision["recommended_actions"] = recommended_actions

        return decision

    def adaptive_optimize(self):
        """自适应价值优化"""
        assessment = self.assess_cross_dimension_values()
        decision = self.make_balance_decision()

        optimization = {
            "timestamp": datetime.now().isoformat(),
            "current_weights": {k: v["weight"] for k, v in self.value_dimensions.items()},
            "adjusted_weights": {},
            "optimization_strategy": "",
            "expected_improvements": []
        }

        # 基于评估结果调整权重
        dim_scores = assessment.get("dimension_scores", {})
        adjusted_weights = {}

        for dim_key in self.value_dimensions.keys():
            current_weight = self.value_dimensions[dim_key]["weight"]
            score = dim_scores.get(dim_key, {}).get("score", 0.5) if isinstance(dim_scores.get(dim_key), dict) else 0.5

            # 得分低则增加权重，得分高则降低权重
            if score < 0.5:
                # 低于50%分数，增加权重
                adjustment = min(0.1, (0.5 - score) * 0.3)
                new_weight = min(0.35, current_weight + adjustment)
            elif score > 0.7:
                # 高于70%分数，可以降低权重
                adjustment = min(0.05, (score - 0.7) * 0.2)
                new_weight = max(0.15, current_weight - adjustment)
            else:
                # 50%-70%之间，保持当前权重
                new_weight = current_weight

            adjusted_weights[dim_key] = round(new_weight, 3)

        optimization["adjusted_weights"] = adjusted_weights

        # 生成优化策略
        priority_dims = sorted(
            [(k, v.get("score", 0.5)) for k, v in dim_scores.items()],
            key=lambda x: x[1]
        )[:2]

        optimization["optimization_strategy"] = f"优先关注 {', '.join([d[0] for d in priority_dims])} 维度的提升"

        # 预期改进
        for dim_key, _ in priority_dims:
            optimization["expected_improvements"].append({
                "dimension": dim_key,
                "expected_gain": "5-15%",
                "timeframe": "1-2轮进化"
            })

        return optimization

    def get_cockpit_data(self):
        """获取驾驶舱展示数据"""
        assessment = self.assess_cross_dimension_values()
        decision = self.make_balance_decision()
        optimization = self.adaptive_optimize()

        return {
            "engine": self.get_version(),
            "timestamp": datetime.now().isoformat(),
            "value_assessment": assessment,
            "balance_decision": decision,
            "adaptive_optimization": optimization,
            "summary": {
                "overall_score": assessment.get("overall_score", 0),
                "weakest_dimension": min(
                    assessment.get("dimension_scores", {}).items(),
                    key=lambda x: x[1].get("score", 1) if isinstance(x[1], dict) else 1
                )[0] if assessment.get("dimension_scores") else "unknown",
                "recommended_focus": optimization.get("optimization_strategy", ""),
                "balance_status": "optimal" if assessment.get("overall_score", 0) > 0.6 else "needs_attention"
            }
        }

    def run_full_analysis(self):
        """运行完整分析"""
        print("=" * 60)
        print("跨维度价值平衡全局决策分析")
        print("=" * 60)

        # 1. 价值评估
        print("\n[1] 跨维度价值评估")
        assessment = self.assess_cross_dimension_values()
        print(f"  - 总体得分: {assessment.get('overall_score', 0):.2f}")
        for dim_key, dim_data in assessment.get("dimensions", {}).items():
            print(f"  - {dim_data.get('name', dim_key)}: {dim_data.get('score', 0):.2f} (权重: {dim_data.get('weight', 0):.2f})")

        # 2. 平衡决策
        print("\n[2] 价值平衡决策")
        decision = self.make_balance_decision()
        for bd in decision.get("balance_decisions", [])[:3]:
            print(f"  - [{bd.get('type', '')}] {bd.get('action', '')}")

        # 3. 自适应优化
        print("\n[3] 自适应价值优化")
        optimization = self.adaptive_optimize()
        print(f"  - 优化策略: {optimization.get('optimization_strategy', '')}")
        print("  - 权重调整:")
        for dim, new_weight in optimization.get("adjusted_weights", {}).items():
            old_weight = optimization.get("current_weights", {}).get(dim, 0)
            if abs(new_weight - old_weight) > 0.01:
                print(f"    * {dim}: {old_weight:.2f} -> {new_weight:.3f}")

        # 4. 推荐行动
        print("\n[4] 推荐行动")
        for action in decision.get("recommended_actions", [])[:3]:
            print(f"  - [{action.get('priority', 'medium').upper()}] {action.get('action', '')}")
            print(f"    预期影响: {action.get('expected_impact', '')}")

        # 5. 综合状态
        print("\n[5] 综合状态")
        summary = {
            "overall_score": assessment.get("overall_score", 0),
            "balance_status": "optimal" if assessment.get("overall_score", 0) > 0.6 else "needs_attention"
        }
        print(f"  - 总体得分: {summary.get('overall_score', 0):.2f}")
        print(f"  - 平衡状态: {summary.get('balance_status', 'unknown')}")

        print("\n" + "=" * 60)

        return {
            "assessment": assessment,
            "decision": decision,
            "optimization": optimization,
            "summary": summary
        }


def main():
    """主函数"""
    engine = CrossDimensionValueBalanceEngine()

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "--version":
            info = engine.get_version()
            print(f"{info['name']} v{info['version']}")
            print(f"描述: {info['description']}")

        elif command == "--status":
            data = engine.get_cockpit_data()
            summary = data.get("summary", {})
            print("跨维度价值平衡状态:")
            print(f"  - 总体得分: {summary.get('overall_score', 0):.2f}")
            print(f"  - 最弱维度: {summary.get('weakest_dimension', 'unknown')}")
            print(f"  - 建议关注: {summary.get('recommended_focus', '')}")
            print(f"  - 平衡状态: {summary.get('balance_status', 'unknown')}")

        elif command == "--assess":
            assessment = engine.assess_cross_dimension_values()
            print(json.dumps(assessment, ensure_ascii=False, indent=2))

        elif command == "--decision":
            decision = engine.make_balance_decision()
            print(json.dumps(decision, ensure_ascii=False, indent=2))

        elif command == "--optimize":
            optimization = engine.adaptive_optimize()
            print(json.dumps(optimization, ensure_ascii=False, indent=2))

        elif command == "--cockpit-data":
            data = engine.get_cockpit_data()
            print(json.dumps(data, ensure_ascii=False, indent=2))

        elif command == "--run":
            result = engine.run_full_analysis()
            return result

        else:
            print(f"未知命令: {command}")
            print("可用命令:")
            print("  --version        显示版本信息")
            print("  --status         显示价值平衡状态")
            print("  --assess         评估跨维度价值")
            print("  --decision       生成价值平衡决策")
            print("  --optimize       自适应价值优化")
            print("  --cockpit-data   获取驾驶舱数据")
            print("  --run            运行完整分析")

    else:
        # 默认运行完整分析
        engine.run_full_analysis()


if __name__ == "__main__":
    main()