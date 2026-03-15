#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环价值投资风险预警与自适应保护引擎
价值投资风险预警与自适应保护引擎 - 在 round 586 完成的价值投资动态再平衡引擎基础上，
构建价值投资的风险预警与自适应保护能力。让系统能够实时监控价值投资组合的风险状态、
提前预警潜在风险、触发自适应保护机制，形成从「动态再平衡」到「风险预警」再到
「自适应保护」的完整风险管控闭环。

version: 1.0.0
"""

import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
from enum import Enum

# 确保可以导入动态再平衡引擎
try:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from evolution_value_investment_dynamic_rebalancing_engine import ValueInvestmentDynamicRebalancingEngine
    REBALANCING_ENGINE_AVAILABLE = True
except ImportError:
    REBALANCING_ENGINE_AVAILABLE = False


class RiskLevel(Enum):
    """风险等级"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class ProtectionAction(Enum):
    """保护动作"""
    NONE = "none"
    WARNING = "warning"
    REDUCE_RISK = "reduce_risk"
    STOP_INVESTMENT = "stop_investment"
    ROLLBACK = "rollback"
    EMERGENCY = "emergency"


class ValueInvestmentRiskWarningAdaptiveProtectionEngine:
    """价值投资风险预警与自适应保护引擎"""

    def __init__(self, state_dir: str = None):
        self.version = "1.0.0"
        self.state_dir = state_dir or "runtime/state"
        self.history_file = os.path.join(self.state_dir, "evolution_completed_*.json")

        # 风险监控参数
        self.risk_thresholds = {
            "roi_decline_rate": -0.15,  # ROI 下降速率阈值
            "volatility_high": 0.25,    # 高波动性阈值
            "concentration_max": 0.50, # 单一投资集中度上限
            "drawdown_max": 0.30,       # 回撤最大允许值
            "correlation_high": 0.80    # 高相关性阈值
        }

        # 保护动作阈值
        self.protection_thresholds = {
            "warning": {
                "roi_decline": -0.05,
                "volatility": 0.15,
                "concentration": 0.35,
                "drawdown": 0.10
            },
            "reduce_risk": {
                "roi_decline": -0.10,
                "volatility": 0.20,
                "concentration": 0.42,
                "drawdown": 0.20
            },
            "stop_investment": {
                "roi_decline": -0.20,
                "volatility": 0.30,
                "concentration": 0.48,
                "drawdown": 0.25
            },
            "emergency": {
                "roi_decline": -0.30,
                "volatility": 0.40,
                "concentration": 0.55,
                "drawdown": 0.35
            }
        }

        # 趋势分析窗口
        self.trend_window = 10
        self.protection_cooldown = 3  # 保护动作冷却轮次

        # 初始化子引擎
        self.rebalancing_engine = None
        if REBALANCING_ENGINE_AVAILABLE:
            try:
                self.rebalancing_engine = ValueInvestmentDynamicRebalancingEngine(state_dir)
            except Exception:
                pass

        # 风险历史记录
        self.risk_history = []
        self.warning_history = []
        self.protection_history = []
        self.last_protection_round = 0

    def load_evolution_history(self) -> List[Dict]:
        """加载进化历史数据"""
        history = []
        import glob
        state_files = glob.glob(os.path.join(self.state_dir, "evolution_completed_ev_*.json"))

        for f in sorted(state_files, reverse=True)[:self.trend_window * 2]:
            try:
                with open(f, 'r', encoding='utf-8') as fp:
                    data = json.load(fp)
                    history.append(data)
            except Exception:
                continue

        return history

    def calculate_risk_indicators(self, history: List[Dict] = None) -> Dict[str, Any]:
        """计算风险指标"""
        if history is None:
            history = self.load_evolution_history()

        if not history:
            return {
                "risk_level": RiskLevel.UNKNOWN.value,
                "indicators": {},
                "message": "暂无足够数据计算风险指标"
            }

        # 按轮次排序
        sorted_history = sorted(history, key=lambda x: x.get("loop_round", 0), reverse=True)
        recent_history = sorted_history[:self.trend_window]

        # 计算各项指标
        indicators = {}

        # 1. ROI 变化趋势
        roi_values = []
        for h in recent_history:
            roi_info = h.get("roi_assessment", {})
            if isinstance(roi_info, dict):
                roi = roi_info.get("roi", 0.5)
            else:
                roi = 0.5
            roi_values.append(roi)

        if len(roi_values) >= 2:
            # 计算下降速率
            recent_roi = roi_values[:3] if len(roi_values) >= 3 else roi_values
            older_roi = roi_values[3:] if len(roi_values) > 3 else roi_values[1:]

            if recent_roi and older_roi:
                avg_recent = sum(recent_roi) / len(recent_roi)
                avg_older = sum(older_roi) / len(older_roi)
                roi_change = (avg_recent - avg_older) / avg_older if avg_older != 0 else 0
                indicators["roi_change_rate"] = round(roi_change, 4)
            else:
                indicators["roi_change_rate"] = 0

            # 计算波动性
            if len(roi_values) >= 2:
                mean = sum(roi_values) / len(roi_values)
                variance = sum((v - mean) ** 2 for v in roi_values) / len(roi_values)
                indicators["volatility"] = round(variance ** 0.5, 4)
            else:
                indicators["volatility"] = 0

            # 计算回撤
            if roi_values:
                max_roi = max(roi_values)
                min_roi = min(roi_values)
                indicators["drawdown"] = round((max_roi - min_roi) / max_roi if max_roi != 0 else 0, 4)
            else:
                indicators["drawdown"] = 0
        else:
            indicators["roi_change_rate"] = 0
            indicators["volatility"] = 0
            indicators["drawdown"] = 0

        # 2. 投资集中度（分析投资类别分布）
        if self.rebalancing_engine:
            allocation = self.rebalancing_engine.calculate_current_allocation()
            max_concentration = max(allocation.values()) if allocation else 0
            indicators["max_concentration"] = round(max_concentration, 4)
        else:
            indicators["max_concentration"] = 0.25  # 默认假设均匀分布

        # 3. 完成率（衡量投资效率）
        completed_count = sum(1 for h in recent_history if h.get("是否完成") == "已完成")
        indicators["completion_rate"] = round(completed_count / len(recent_history), 4) if recent_history else 0

        # 4. 异常检测（检查是否有失败轮次）
        failed_count = sum(1 for h in recent_history if h.get("是否完成") in ["未完成", "失败"])
        indicators["failure_rate"] = round(failed_count / len(recent_history), 4) if recent_history else 0

        return {
            "indicators": indicators,
            "recent_rounds": len(recent_history),
            "data_coverage": len(recent_history) / self.trend_window
        }

    def assess_risk_level(self, indicators: Dict = None) -> Dict[str, Any]:
        """评估风险等级"""
        if indicators is None:
            risk_data = self.calculate_risk_indicators()
            indicators = risk_data.get("indicators", {})

        if not indicators:
            return {
                "risk_level": RiskLevel.UNKNOWN.value,
                "score": 0,
                "triggered_factors": [],
                "message": "数据不足，无法评估风险"
            }

        # 计算风险分数（0-100）
        risk_score = 0
        triggered_factors = []

        # ROI 下降风险
        roi_change = indicators.get("roi_change_rate", 0)
        if roi_change < self.risk_thresholds["roi_decline_rate"]:
            risk_score += 30
            triggered_factors.append("ROI大幅下降")
        elif roi_change < -0.05:
            risk_score += 15
            triggered_factors.append("ROI有所下降")

        # 波动性风险
        volatility = indicators.get("volatility", 0)
        if volatility > self.risk_thresholds["volatility_high"]:
            risk_score += 25
            triggered_factors.append("高波动性")
        elif volatility > 0.15:
            risk_score += 10
            triggered_factors.append("波动性上升")

        # 集中度风险
        concentration = indicators.get("max_concentration", 0)
        if concentration > self.risk_thresholds["concentration_max"]:
            risk_score += 25
            triggered_factors.append("投资过于集中")
        elif concentration > 0.35:
            risk_score += 10
            triggered_factors.append("集中度偏高")

        # 回撤风险
        drawdown = indicators.get("drawdown", 0)
        if drawdown > self.risk_thresholds["drawdown_max"]:
            risk_score += 30
            triggered_factors.append("回撤过大")
        elif drawdown > 0.15:
            risk_score += 10
            triggered_factors.append("存在回撤")

        # 失败率风险
        failure_rate = indicators.get("failure_rate", 0)
        if failure_rate > 0.3:
            risk_score += 20
            triggered_factors.append("失败率较高")

        # 确定风险等级
        if risk_score >= 70:
            risk_level = RiskLevel.CRITICAL.value
        elif risk_score >= 50:
            risk_level = RiskLevel.HIGH.value
        elif risk_score >= 25:
            risk_level = RiskLevel.MEDIUM.value
        else:
            risk_level = RiskLevel.LOW.value

        return {
            "risk_level": risk_level,
            "score": min(100, risk_score),
            "triggered_factors": triggered_factors,
            "indicators": indicators,
            "message": f"风险等级: {risk_level} (分数: {risk_score})"
        }

    def check_protection_needed(self, risk_assessment: Dict = None) -> Dict[str, Any]:
        """检查是否需要触发保护机制"""
        if risk_assessment is None:
            risk_assessment = self.assess_risk_level()

        risk_level = risk_assessment.get("risk_level", RiskLevel.UNKNOWN.value)
        risk_score = risk_assessment.get("score", 0)
        indicators = risk_assessment.get("indicators", {})

        # 检查冷却期
        current_round = risk_assessment.get("recent_rounds", 0)
        if current_round - self.last_protection_round < self.protection_cooldown:
            return {
                "protection_needed": False,
                "action": ProtectionAction.NONE.value,
                "reason": "保护动作冷却期内",
                "cooldown_remaining": self.protection_cooldown - (current_round - self.last_protection_round)
            }

        # 根据风险等级确定保护动作
        if risk_level == RiskLevel.CRITICAL.value or risk_score >= 70:
            return {
                "protection_needed": True,
                "action": ProtectionAction.EMERGENCY.value,
                "reason": "风险等级达到紧急水平",
                "priority": "critical",
                "risk_level": risk_level,
                "risk_score": risk_score
            }
        elif risk_level == RiskLevel.HIGH.value or risk_score >= 50:
            # 检查是否需要停止投资
            roi_change = indicators.get("roi_change_rate", 0)
            if roi_change < self.protection_thresholds["stop_investment"]["roi_decline"]:
                return {
                    "protection_needed": True,
                    "action": ProtectionAction.STOP_INVESTMENT.value,
                    "reason": "ROI下降严重，停止新的高风险投资",
                    "priority": "high",
                    "risk_level": risk_level,
                    "risk_score": risk_score
                }
            else:
                return {
                    "protection_needed": True,
                    "action": ProtectionAction.REDUCE_RISK.value,
                    "reason": "风险等级高，需要降低风险敞口",
                    "priority": "high",
                    "risk_level": risk_level,
                    "risk_score": risk_score
                }
        elif risk_level == RiskLevel.MEDIUM.value or risk_score >= 25:
            return {
                "protection_needed": True,
                "action": ProtectionAction.WARNING.value,
                "reason": "风险等级中等，发布预警",
                "priority": "medium",
                "risk_level": risk_level,
                "risk_score": risk_score
            }
        else:
            return {
                "protection_needed": False,
                "action": ProtectionAction.NONE.value,
                "reason": "风险在可控范围内",
                "priority": "low",
                "risk_level": risk_level,
                "risk_score": risk_score
            }

    def execute_protection_action(self, protection_decision: Dict = None) -> Dict[str, Any]:
        """执行保护动作"""
        if protection_decision is None:
            protection_decision = self.check_protection_needed()

        action = protection_decision.get("action", ProtectionAction.NONE.value)
        reason = protection_decision.get("reason", "")

        protection_record = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "reason": reason,
            "priority": protection_decision.get("priority", "none"),
            "risk_level": protection_decision.get("risk_level", "unknown"),
            "risk_score": protection_decision.get("risk_score", 0)
        }

        # 执行相应的保护动作
        action_details = {}

        if action == ProtectionAction.WARNING.value:
            # 生成预警信息
            action_details = {
                "type": "warning",
                "message": f"风险预警: {reason}",
                "recommendations": [
                    "密切关注投资组合表现",
                    "准备风险应对方案",
                    "增加监控频率"
                ]
            }

        elif action == ProtectionAction.REDUCE_RISK.value:
            # 降低风险
            if self.rebalancing_engine:
                rebalance_plan = self.rebalancing_engine.generate_rebalance_plan()
                action_details = {
                    "type": "reduce_risk",
                    "message": f"风险控制: {reason}",
                    "actions_taken": [
                        "启动动态再平衡",
                        "降低高风险投资比例",
                        "增加稳健型投资"
                    ],
                    "rebalance_plan": rebalance_plan
                }
                # 执行再平衡
                try:
                    self.rebalancing_engine.execute_rebalance()
                except Exception as e:
                    action_details["execution_error"] = str(e)

        elif action == ProtectionAction.STOP_INVESTMENT.value:
            # 停止新投资
            action_details = {
                "type": "stop_investment",
                "message": f"投资停止: {reason}",
                "actions_taken": [
                    "暂停新的高风险投资",
                    "保留现有投资",
                    "等待风险缓解"
                ],
                "recovery_conditions": [
                    "ROI 稳定或回升",
                    "波动性降低",
                    "风险评估改善"
                ]
            }

        elif action == ProtectionAction.EMERGENCY.value:
            # 紧急保护
            action_details = {
                "type": "emergency",
                "message": f"紧急保护: {reason}",
                "actions_taken": [
                    "立即停止高风险操作",
                    "启动安全备份策略",
                    "回滚到稳定配置"
                ],
                "emergency_measures": [
                    "保存当前状态",
                    "记录保护触发点",
                    "准备恢复计划"
                ]
            }
            self.last_protection_round = protection_record.get("timestamp", 0)

        else:
            action_details = {
                "type": "none",
                "message": "无需保护动作"
            }

        # 记录保护历史
        protection_record["action_details"] = action_details
        self.protection_history.append(protection_record)

        return {
            "success": True,
            "protection_record": protection_record,
            "action_details": action_details,
            "message": f"保护动作执行完成: {action}"
        }

    def generate_risk_report(self, risk_assessment: Dict = None, protection_result: Dict = None) -> Dict[str, Any]:
        """生成风险评估报告"""
        if risk_assessment is None:
            risk_assessment = self.assess_risk_level()

        indicators = risk_assessment.get("indicators", {})

        # 生成风险描述
        risk_descriptions = []
        if risk_assessment.get("risk_level") in [RiskLevel.HIGH.value, RiskLevel.CRITICAL.value]:
            triggered = risk_assessment.get("triggered_factors", [])
            for factor in triggered:
                if "ROI" in factor:
                    risk_descriptions.append(f"ROI{indicators.get('roi_change_rate', 0):.1%}")
                if "波动" in factor:
                    risk_descriptions.append(f"波动性{indicators.get('volatility', 0):.1%}")
                if "集中" in factor:
                    risk_descriptions.append(f"集中度{indicators.get('max_concentration', 0):.1%}")
                if "回撤" in factor:
                    risk_descriptions.append(f"回撤{indicators.get('drawdown', 0):.1%}")

        report = {
            "report_type": "价值投资风险评估报告",
            "generated_at": datetime.now().isoformat(),
            "risk_summary": {
                "risk_level": risk_assessment.get("risk_level", "unknown"),
                "risk_score": risk_assessment.get("score", 0),
                "triggered_factors": risk_assessment.get("triggered_factors", []),
                "risk_descriptions": risk_descriptions
            },
            "risk_indicators": {
                "roi_change_rate": indicators.get("roi_change_rate", 0),
                "volatility": indicators.get("volatility", 0),
                "max_concentration": indicators.get("max_concentration", 0),
                "drawdown": indicators.get("drawdown", 0),
                "completion_rate": indicators.get("completion_rate", 0),
                "failure_rate": indicators.get("failure_rate", 0)
            },
            "thresholds": self.risk_thresholds,
            "protection_status": {
                "last_action": protection_result.get("protection_record", {}).get("action", "none") if protection_result else "none",
                "protection_count": len(self.protection_history),
                "cooldown_remaining": max(0, self.protection_cooldown - (len(self.risk_history) - self.last_protection_round))
            },
            "recommendations": self._generate_recommendations(risk_assessment),
            "timestamp": datetime.now().isoformat()
        }

        return report

    def _generate_recommendations(self, risk_assessment: Dict) -> List[Dict]:
        """生成建议"""
        recommendations = []
        risk_level = risk_assessment.get("risk_level", "unknown")
        indicators = risk_assessment.get("indicators", {})
        triggered = risk_assessment.get("triggered_factors", [])

        # 基于触发因素生成建议
        for factor in triggered:
            if "ROI下降" in factor or "ROI大幅下降" in factor:
                recommendations.append({
                    "category": "投资策略",
                    "priority": "high",
                    "recommendation": "审查当前投资策略，考虑减少高风险投入",
                    "action": "重新评估投资组合配置"
                })
            if "波动" in factor:
                recommendations.append({
                    "category": "风险管理",
                    "priority": "high" if risk_level == RiskLevel.HIGH.value else "medium",
                    "recommendation": "增加稳健型投资比例以降低波动",
                    "action": "调整资产配置"
                })
            if "集中" in factor:
                recommendations.append({
                    "category": "投资分散",
                    "priority": "medium",
                    "recommendation": "分散投资，降低单一类别集中度",
                    "action": "执行动态再平衡"
                })
            if "回撤" in factor:
                recommendations.append({
                    "category": "风险控制",
                    "priority": "high",
                    "recommendation": "设置止损点，防止进一步回撤",
                    "action": "启动保护机制"
                })

        # 如果没有触发因素
        if not recommendations:
            recommendations.append({
                "category": "维持",
                "priority": "low",
                "recommendation": "当前风险在可控范围内，保持现有策略",
                "action": "常规监控"
            })

        return recommendations

    def run_full_risk_cycle(self) -> Dict[str, Any]:
        """运行完整风险管控周期"""
        # 1. 计算风险指标
        risk_indicators = self.calculate_risk_indicators()

        # 2. 评估风险等级
        risk_assessment = self.assess_risk_level(risk_indicators.get("indicators", {}))

        # 3. 检查是否需要保护
        protection_decision = self.check_protection_needed(risk_assessment)

        # 4. 执行保护动作
        protection_result = self.execute_protection_action(protection_decision)

        # 5. 生成风险报告
        risk_report = self.generate_risk_report(risk_assessment, protection_result)

        # 记录风险历史
        risk_record = {
            "timestamp": datetime.now().isoformat(),
            "risk_assessment": risk_assessment,
            "protection_decision": protection_decision,
            "protection_result": protection_result.get("action_details", {})
        }
        self.risk_history.append(risk_record)

        return {
            "risk_indicators": risk_indicators,
            "risk_assessment": risk_assessment,
            "protection_decision": protection_decision,
            "protection_result": protection_result,
            "risk_report": risk_report,
            "timestamp": datetime.now().isoformat()
        }

    def get_cockpit_data(self) -> Dict[str, Any]:
        """获取驾驶舱数据"""
        risk_indicators = self.calculate_risk_indicators()
        risk_assessment = self.assess_risk_level(risk_indicators.get("indicators", {}))
        protection_decision = self.check_protection_needed(risk_assessment)

        return {
            "engine": "价值投资风险预警与自适应保护引擎",
            "version": self.version,
            "risk_level": risk_assessment.get("risk_level", "unknown"),
            "risk_score": risk_assessment.get("score", 0),
            "triggered_factors": risk_assessment.get("triggered_factors", []),
            "protection_needed": protection_decision.get("protection_needed", False),
            "protection_action": protection_decision.get("action", "none"),
            "risk_indicators": risk_assessment.get("indicators", {}),
            "protection_history_count": len(self.protection_history),
            "warning_history_count": len(self.warning_history),
            "timestamp": datetime.now().isoformat()
        }

    def get_status(self) -> Dict[str, Any]:
        """获取引擎状态"""
        risk_indicators = self.calculate_risk_indicators()
        risk_assessment = self.assess_risk_level(risk_indicators.get("indicators", {}))
        protection_decision = self.check_protection_needed(risk_assessment)

        return {
            "engine": "价值投资风险预警与自适应保护引擎",
            "version": self.version,
            "status": "running",
            "risk_level": risk_assessment.get("risk_level", "unknown"),
            "risk_score": risk_assessment.get("score", 0),
            "protection_needed": protection_decision.get("protection_needed", False),
            "thresholds": self.risk_thresholds,
            "protection_cooldown": self.protection_cooldown,
            "rebalancing_engine_available": REBALANCING_ENGINE_AVAILABLE,
            "timestamp": datetime.now().isoformat()
        }


def main():
    """主函数 - 命令行入口"""
    import argparse
    parser = argparse.ArgumentParser(description="价值投资风险预警与自适应保护引擎")
    parser.add_argument("--status", action="store_true", help="获取引擎状态")
    parser.add_argument("--risk-indicators", action="store_true", help="计算风险指标")
    parser.add_argument("--risk-assessment", action="store_true", help="评估风险等级")
    parser.add_argument("--check-protection", action="store_true", help="检查保护需求")
    parser.add_argument("--protect", action="store_true", help="执行保护动作")
    parser.add_argument("--report", action="store_true", help="生成风险报告")
    parser.add_argument("--run", action="store_true", help="运行完整风险管控周期")
    parser.add_argument("--cockpit-data", action="store_true", help="获取驾驶舱数据")
    parser.add_argument("--state-dir", type=str, default="runtime/state", help="状态目录")

    args = parser.parse_args()

    engine = ValueInvestmentRiskWarningAdaptiveProtectionEngine(args.state_dir)

    if args.status:
        result = engine.get_status()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.risk_indicators:
        result = engine.calculate_risk_indicators()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.risk_assessment:
        result = engine.assess_risk_level()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.check_protection:
        result = engine.check_protection_needed()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.protect:
        result = engine.execute_protection_action()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.report:
        result = engine.generate_risk_report()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.run:
        result = engine.run_full_risk_cycle()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.cockpit_data:
        result = engine.get_cockpit_data()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()