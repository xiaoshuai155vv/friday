#!/usr/bin/env python3
"""
智能全场景进化环全维度价值-风险平衡自适应优化引擎

版本: 1.0.0
功能: 让系统能够全面评估进化的多维度价值（效率、质量、创新、可持续性）、
      智能识别风险并评估影响、自动平衡价值追求与风险管控、自适应调整优化策略

依赖:
- round 540 的决策执行质量闭环评估引擎
- round 539 的战略执行闭环引擎
- round 538 的自我进化意识与战略规划引擎

集成到 do.py 支持: 价值风险平衡、风险评估、价值优化、多维度优化、risk balance 等关键词触发
"""

import os
import sys
import json
import time
import argparse
import subprocess
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from collections import defaultdict

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
RUNTIME_DIR = PROJECT_ROOT / "runtime"
STATE_DIR = RUNTIME_DIR / "state"
LOGS_DIR = RUNTIME_DIR / "logs"


class EvolutionValueRiskBalanceOptimizerEngine:
    """全维度价值-风险平衡自适应优化引擎"""

    VERSION = "1.0.0"

    def __init__(self):
        self.name = "EvolutionValueRiskBalanceOptimizerEngine"
        self.version = self.VERSION
        self.state_file = STATE_DIR / "value_risk_balance_state.json"
        self.analysis_history_file = STATE_DIR / "value_risk_analysis_history.json"
        self.quality_state_file = STATE_DIR / "execution_quality_state.json"
        self.strategy_execution_file = STATE_DIR / "strategy_execution_history.json"
        self.self_evolution_file = STATE_DIR / "self_evolution_state.json"

    def _load_json(self, filepath: Path, default: Any = None) -> Any:
        """安全加载 JSON 文件"""
        if filepath.exists():
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载文件失败 {filepath}: {e}")
        return default if default is not None else {}

    def _save_json(self, filepath: Path, data: Any) -> bool:
        """安全保存 JSON 文件"""
        try:
            filepath.parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存文件失败 {filepath}: {e}")
            return False

    def get_execution_data(self) -> Dict[str, Any]:
        """获取执行数据用于分析"""
        # 从决策执行质量引擎获取质量数据
        quality_data = self._load_json(self.quality_state_file, {
            "metrics": {},
            "quality_trends": [],
            "recent_executions": []
        })

        # 从战略执行引擎获取执行历史
        strategy_data = self._load_json(self.strategy_execution_file, {
            "executions": [],
            "efficiency_metrics": {}
        })

        # 从自我进化意识引擎获取自我评估数据
        self_evolution_data = self._load_json(self.self_evolution_file, {
            "self_assessment": {},
            "strategic_planning": {}
        })

        return {
            "quality": quality_data,
            "strategy": strategy_data,
            "self_evolution": self_evolution_data
        }

    def evaluate_multidimensional_value(self, execution_data: Dict[str, Any]) -> Dict[str, float]:
        """
        评估多维度价值
        维度包括: 效率、质量、创新、可持续性、用户价值、系统价值
        """
        value_scores = {
            "efficiency": 0.0,       # 执行效率
            "quality": 0.0,          # 输出质量
            "innovation": 0.0,       # 创新程度
            "sustainability": 0.0,  # 可持续性
            "user_value": 0.0,       # 用户价值
            "system_value": 0.0     # 系统价值
        }

        # 从执行数据中提取价值指标
        quality_data = execution_data.get("quality", {})
        strategy_data = execution_data.get("strategy", {})

        # 评估效率 (基于执行时间和资源使用)
        efficiency_metrics = strategy_data.get("efficiency_metrics", {})
        avg_execution_time = efficiency_metrics.get("avg_execution_time", 60)
        if avg_execution_time > 0:
            # 越快越好，转换为 0-100 分
            value_scores["efficiency"] = max(0, min(100, 100 - (avg_execution_time / 2)))

        # 评估质量 (基于质量评估数据)
        quality_metrics = quality_data.get("metrics", {})
        overall_quality = quality_metrics.get("overall_quality_score", 75)
        value_scores["quality"] = overall_quality

        # 评估创新 (基于进化环历史分析)
        # 模拟数据：实际应从历史分析中获取
        self_evolution = execution_data.get("self_evolution", {})
        strategic_planning = self_evolution.get("strategic_planning", {})
        innovation_score = strategic_planning.get("innovation_potential", 75)
        value_scores["innovation"] = innovation_score

        # 评估可持续性 (基于系统健康和稳定性)
        system_health = quality_metrics.get("system_health_score", 80)
        value_scores["sustainability"] = system_health

        # 评估用户价值 (基于任务完成度和用户满意度)
        task_completion = quality_metrics.get("task_completion_rate", 85)
        value_scores["user_value"] = task_completion

        # 评估系统价值 (基于能力提升和进化效果)
        capability_improvement = strategic_planning.get("capability_growth", 70)
        value_scores["system_value"] = capability_improvement

        return value_scores

    def identify_and_assess_risks(self, execution_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        智能识别风险并评估影响
        风险类型: 技术风险、运营风险、机会成本、级联风险
        """
        risk_analysis = {
            "identified_risks": [],
            "risk_scores": {
                "technical_risk": 0.0,
                "operational_risk": 0.0,
                "opportunity_cost_risk": 0.0,
                "cascading_risk": 0.0
            },
            "overall_risk_level": "low",
            "risk_trends": []
        }

        quality_data = execution_data.get("quality", {})
        strategy_data = execution_data.get("strategy", {})

        # 识别技术风险 (基于执行失败率和错误类型)
        quality_metrics = quality_data.get("metrics", {})
        failure_rate = quality_metrics.get("failure_rate", 5)
        error_recovery_time = quality_metrics.get("error_recovery_time", 10)

        technical_risk_score = min(100, failure_rate * 5 + error_recovery_time * 0.5)
        risk_analysis["risk_scores"]["technical_risk"] = technical_risk_score

        if technical_risk_score > 30:
            risk_analysis["identified_risks"].append({
                "type": "technical",
                "description": "执行失败率较高或错误恢复时间较长",
                "severity": "high" if technical_risk_score > 60 else "medium",
                "score": technical_risk_score
            })

        # 识别运营风险 (基于资源使用和系统负载)
        efficiency_metrics = strategy_data.get("efficiency_metrics", {})
        resource_usage = efficiency_metrics.get("resource_usage", 50)

        operational_risk_score = resource_usage
        risk_analysis["risk_scores"]["operational_risk"] = operational_risk_score

        if operational_risk_score > 70:
            risk_analysis["identified_risks"].append({
                "type": "operational",
                "description": "系统资源使用率较高，可能影响稳定性",
                "severity": "high" if operational_risk_score > 85 else "medium",
                "score": operational_risk_score
            })

        # 识别机会成本风险 (基于优化空间和遗漏的机会)
        optimization_gaps = efficiency_metrics.get("optimization_gaps", 20)
        opportunity_cost_risk = optimization_gaps
        risk_analysis["risk_scores"]["opportunity_cost_risk"] = opportunity_cost_risk

        if opportunity_cost_risk > 40:
            risk_analysis["identified_risks"].append({
                "type": "opportunity_cost",
                "description": "存在未捕获的优化机会",
                "severity": "medium",
                "score": opportunity_cost_risk
            })

        # 评估级联风险 (基于历史模式识别)
        recent_trends = quality_data.get("quality_trends", [])
        if len(recent_trends) >= 3:
            # 检查是否存在连续下降趋势
            if all(recent_trends[i] > recent_trends[i+1] for i in range(len(recent_trends)-1)):
                cascading_risk_score = 65
                risk_analysis["risk_scores"]["cascading_risk"] = cascading_risk_score
                risk_analysis["identified_risks"].append({
                    "type": "cascading",
                    "description": "质量指标呈下降趋势，可能引发连锁反应",
                    "severity": "high",
                    "score": cascading_risk_score
                })

        # 计算整体风险等级
        avg_risk = sum(risk_analysis["risk_scores"].values()) / 4
        if avg_risk < 25:
            risk_analysis["overall_risk_level"] = "low"
        elif avg_risk < 50:
            risk_analysis["overall_risk_level"] = "medium"
        elif avg_risk < 75:
            risk_analysis["overall_risk_level"] = "high"
        else:
            risk_analysis["overall_risk_level"] = "critical"

        return risk_analysis

    def calculate_balance_strategy(
        self,
        value_scores: Dict[str, float],
        risk_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        价值-风险平衡算法
        使用帕累托最优和加权评分方法计算最优策略
        """
        balance_strategy = {
            "recommended_strategy": "balanced",
            "strategy_parameters": {},
            "value_weights": {},
            "risk_mitigation": {},
            "expected_outcome": {}
        }

        # 计算价值权重 (基于当前价值和风险)
        risk_scores = risk_analysis.get("risk_scores", {})

        # 价值权重计算：风险高时降低对应维度权重
        value_weights = {}
        for dimension, score in value_scores.items():
            risk_adjustment = 0
            if "efficiency" in dimension and risk_scores.get("technical_risk", 0) > 40:
                risk_adjustment = 10
            elif "quality" in dimension and risk_scores.get("technical_risk", 0) > 50:
                risk_adjustment = 15
            elif "innovation" in dimension and risk_scores.get("operational_risk", 0) > 60:
                risk_adjustment = 20

            adjusted_score = max(0, score - risk_adjustment)
            value_weights[dimension] = adjusted_score

        balance_strategy["value_weights"] = value_weights

        # 确定推荐策略
        avg_value = sum(value_scores.values()) / len(value_scores)
        avg_risk = sum(risk_scores.values()) / len(risk_scores)

        if avg_risk > 60:
            if avg_value > 70:
                balance_strategy["recommended_strategy"] = "cautious_growth"
            else:
                balance_strategy["recommended_strategy"] = "risk_mitigation"
        elif avg_risk > 40:
            if avg_value > 65:
                balance_strategy["recommended_strategy"] = "balanced"
            else:
                balance_strategy["recommended_strategy"] = "value_focused"
        else:
            if avg_value > 75:
                balance_strategy["recommended_strategy"] = "aggressive_growth"
            else:
                balance_strategy["recommended_strategy"] = "consolidate"

        # 生成策略参数
        strategy = balance_strategy["recommended_strategy"]
        if strategy == "aggressive_growth":
            balance_strategy["strategy_parameters"] = {
                "innovation_weight": 1.3,
                "efficiency_weight": 1.2,
                "risk_tolerance": "high",
                "resource_allocation": "expand"
            }
        elif strategy == "balanced":
            balance_strategy["strategy_parameters"] = {
                "innovation_weight": 1.0,
                "efficiency_weight": 1.0,
                "risk_tolerance": "medium",
                "resource_allocation": "maintain"
            }
        elif strategy == "risk_mitigation":
            balance_strategy["strategy_parameters"] = {
                "innovation_weight": 0.7,
                "efficiency_weight": 0.9,
                "risk_tolerance": "low",
                "resource_allocation": "consolidate"
            }
        else:  # consolidate
            balance_strategy["strategy_parameters"] = {
                "innovation_weight": 0.8,
                "efficiency_weight": 1.1,
                "risk_tolerance": "low",
                "resource_allocation": "optimize"
            }

        # 风险缓解措施
        risk_mitigation = {}
        for risk_type, score in risk_scores.items():
            if score > 40:
                mitigation_key = risk_type.replace("_risk", "")
                if risk_type == "technical_risk":
                    risk_mitigation[mitigation_key] = [
                        "增加错误处理和恢复机制",
                        "实施更严格的测试流程",
                        "准备备用执行方案"
                    ]
                elif risk_type == "operational_risk":
                    risk_mitigation[mitigation_key] = [
                        "优化资源使用策略",
                        "实施负载均衡",
                        "设置资源使用上限"
                    ]
                elif risk_type == "opportunity_cost_risk":
                    risk_mitigation[mitigation_key] = [
                        "扩展优化搜索空间",
                        "引入更先进的优化算法",
                        "增加探索性任务"
                    ]
                elif risk_type == "cascading_risk":
                    risk_mitigation[mitigation_key] = [
                        "实施预防性维护",
                        "建立预警机制",
                        "准备应急预案"
                    ]

        balance_strategy["risk_mitigation"] = risk_mitigation

        # 预期结果
        balance_strategy["expected_outcome"] = {
            "expected_value_improvement": max(0, avg_value + 5 - avg_risk * 0.2),
            "expected_risk_reduction": max(0, avg_risk * 0.3),
            "confidence": 0.85 if avg_risk < 50 else 0.7,
            "strategy_confidence": balance_strategy["strategy_parameters"].get("risk_tolerance", "medium")
        }

        return balance_strategy

    def adaptively_optimize_strategy(
        self,
        balance_strategy: Dict[str, Any],
        previous_strategy: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        自适应优化策略调整
        基于平衡策略和历史策略进行动态调整
        """
        optimized = {
            "applied_strategy": balance_strategy["recommended_strategy"],
            "adjusted_parameters": {},
            "optimization_applied": [],
            "learning_feedback": {}
        }

        strategy_params = balance_strategy.get("strategy_parameters", {})

        # 如果有历史策略，进行对比学习
        if previous_strategy:
            prev_params = previous_strategy.get("adjusted_parameters", {})
            for param, value in strategy_params.items():
                prev_value = prev_params.get(param)
                # 如果参数变化超过阈值，记录优化
                if prev_value is not None:
                    try:
                        # 尝试将值转换为数值进行比较
                        curr_num = float(value) if isinstance(value, (int, float, str)) and str(value).replace('.', '').isdigit() else None
                        prev_num = float(prev_value) if isinstance(prev_value, (int, float, str)) and str(prev_value).replace('.', '').isdigit() else None
                        if curr_num is not None and prev_num is not None and abs(curr_num - prev_num) > 0.1:
                            direction = "increase" if curr_num > prev_num else "decrease"
                            optimized["optimization_applied"].append({
                                "parameter": param,
                                "direction": direction,
                                "previous": prev_value,
                                "current": value,
                                "reason": f"{param}调整以优化{balance_strategy['recommended_strategy']}策略"
                            })
                    except (TypeError, ValueError):
                        pass  # 如果无法比较则跳过

        optimized["adjusted_parameters"] = strategy_params

        # 学习反馈
        strategy = balance_strategy["recommended_strategy"]
        if strategy == "aggressive_growth":
            optimized["learning_feedback"] = {
                "focus": "保持创新动力同时监控风险",
                "next_iteration": "如风险上升则转向平衡策略"
            }
        elif strategy == "risk_mitigation":
            optimized["learning_feedback"] = {
                "focus": "优先控制风险",
                "next_iteration": "风险降低后可尝试渐进式增长"
            }
        else:
            optimized["learning_feedback"] = {
                "focus": "保持当前平衡",
                "next_iteration": "根据效果持续微调"
            }

        return optimized

    def analyze_and_optimize(self, include_history: bool = True) -> Dict[str, Any]:
        """
        完整的价值-风险平衡分析与优化流程
        """
        result = {
            "timestamp": datetime.now().isoformat(),
            "version": self.version,
            "analysis_result": {},
            "balance_strategy": {},
            "optimized_strategy": {},
            "cockpit_data": {}
        }

        # 1. 获取执行数据
        execution_data = self.get_execution_data()

        # 2. 评估多维度价值
        value_scores = self.evaluate_multidimensional_value(execution_data)
        result["analysis_result"]["value_scores"] = value_scores

        # 3. 识别和评估风险
        risk_analysis = self.identify_and_assess_risks(execution_data)
        result["analysis_result"]["risk_analysis"] = risk_analysis

        # 4. 计算平衡策略
        balance_strategy = self.calculate_balance_strategy(value_scores, risk_analysis)
        result["balance_strategy"] = balance_strategy

        # 5. 加载历史策略（如有）
        previous_strategy = None
        if include_history:
            history = self._load_json(self.state_file, {})
            previous_strategy = history.get("last_optimized_strategy")

        # 6. 自适应优化策略
        optimized_strategy = self.adaptively_optimize_strategy(balance_strategy, previous_strategy)
        result["optimized_strategy"] = optimized_strategy

        # 7. 生成驾驶舱数据
        avg_value = sum(value_scores.values()) / len(value_scores)
        avg_risk = sum(risk_analysis.get("risk_scores", {}).values()) / 4

        cockpit_data = {
            "overall_value_score": avg_value,
            "overall_risk_score": avg_risk,
            "risk_level": risk_analysis.get("overall_risk_level", "low"),
            "recommended_strategy": balance_strategy.get("recommended_strategy", "balanced"),
            "value_dimensions": value_scores,
            "risk_dimensions": risk_analysis.get("risk_scores", {}),
            "mitigation_count": len(balance_strategy.get("risk_mitigation", {}))
        }

        result["cockpit_data"] = cockpit_data

        # 保存状态（包括驾驶舱数据）
        current_state = {
            "timestamp": result["timestamp"],
            "value_scores": value_scores,
            "risk_analysis": risk_analysis,
            "balance_strategy": balance_strategy,
            "last_optimized_strategy": optimized_strategy,
            "cockpit_data": cockpit_data
        }
        self._save_json(self.state_file, current_state)

        # 8. 记录到历史
        if include_history:
            history = self._load_json(self.analysis_history_file, {"analyses": []})
            history["analyses"].append({
                "timestamp": result["timestamp"],
                "value_score": avg_value,
                "risk_score": avg_risk,
                "strategy": result["optimized_strategy"]["applied_strategy"]
            })
            # 只保留最近 100 条
            history["analyses"] = history["analyses"][-100:]
            self._save_json(self.analysis_history_file, history)

        return result

    def get_cockpit_data(self) -> Dict[str, Any]:
        """获取驾驶舱数据接口"""
        state = self._load_json(self.state_file, {})
        return state.get("cockpit_data", {
            "overall_value_score": 0,
            "overall_risk_score": 0,
            "risk_level": "unknown",
            "recommended_strategy": "pending_analysis"
        })

    def get_status_summary(self) -> Dict[str, Any]:
        """获取状态摘要"""
        state = self._load_json(self.state_file, {})

        if not state:
            return {
                "status": "not_analyzed",
                "message": "尚未执行价值-风险分析，请先运行分析"
            }

        cockpit = state.get("cockpit_data", {})
        return {
            "status": "ready",
            "last_analysis": state.get("timestamp", "unknown"),
            "overall_value": cockpit.get("overall_value_score", 0),
            "overall_risk": cockpit.get("overall_risk_score", 0),
            "risk_level": cockpit.get("risk_level", "unknown"),
            "recommended_strategy": cockpit.get("recommended_strategy", "unknown"),
            "version": self.version
        }


def main():
    """主入口函数"""
    parser = argparse.ArgumentParser(
        description="全维度价值-风险平衡自适应优化引擎"
    )
    parser.add_argument(
        "--analyze",
        action="store_true",
        help="执行完整的价值-风险平衡分析"
    )
    parser.add_argument(
        "--cockpit-data",
        action="store_true",
        help="获取驾驶舱数据"
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="获取状态摘要"
    )
    parser.add_argument(
        "--no-history",
        action="store_true",
        help="不记录到历史"
    )

    args = parser.parse_args()

    engine = EvolutionValueRiskBalanceOptimizerEngine()

    if args.analyze:
        result = engine.analyze_and_optimize(include_history=not args.no_history)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.cockpit_data:
        data = engine.get_cockpit_data()
        print(json.dumps(data, ensure_ascii=False, indent=2))
    elif args.status:
        status = engine.get_status_summary()
        print(json.dumps(status, ensure_ascii=False, indent=2))
    else:
        parser.print_help()
        print("\n示例:")
        print("  python evolution_value_risk_balance_optimizer_engine.py --analyze")
        print("  python evolution_value_risk_balance_optimizer_engine.py --cockpit-data")
        print("  python evolution_value_risk_balance_optimizer_engine.py --status")


if __name__ == "__main__":
    main()