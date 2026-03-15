"""
元进化价值投资智能决策引擎
Evolution Meta Value Investment Intelligent Decision Engine

version: 1.0.0
description: 在 round 588 完成的价值投资组合智能复盘与持续学习引擎基础上，
构建让系统能够综合 ROI 评估(r585)、动态再平衡(r586)、风险预警(r587)、智能复盘(r588)等环节的决策结果，
生成统一的投资决策建议，实现从各环节独立决策到统一智能决策的范式升级。

功能：
1. 多环节决策结果综合分析 - 整合 ROI、动态再平衡、风险预警、复盘数据
2. 统一投资决策建议生成 - 基于多环节数据的智能决策
3. 投资策略智能推荐 - 基于综合分析的策略建议
4. 与 round 585-588 各价值投资引擎的深度集成
5. 驾驶舱数据接口
6. do.py 集成支持

依赖：
- round 588: 价值投资组合智能复盘与持续学习引擎
- round 587: 价值投资风险预警与自适应保护引擎
- round 586: 价值投资动态再平衡引擎
- round 585: 价值投资回报智能评估引擎
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path


class MetaValueInvestmentIntelligentDecisionEngine:
    """元进化价值投资智能决策引擎"""

    VERSION = "1.0.0"

    def __init__(self, runtime_dir: str = None):
        self.runtime_dir = runtime_dir or os.path.join(os.path.dirname(__file__), "..", "runtime")
        self.state_dir = os.path.join(self.runtime_dir, "state")
        self.logs_dir = os.path.join(self.runtime_dir, "logs")

        # 各环节数据文件路径
        self.roi_data_file = os.path.join(self.state_dir, "evolution_completed_ev_20260315_105152.json")
        self.rebalancing_data_file = os.path.join(self.state_dir, "evolution_completed_ev_20260315_105655.json")
        self.risk_data_file = os.path.join(self.state_dir, "evolution_completed_ev_20260315_110159.json")
        self.review_data_file = os.path.join(self.state_dir, "evolution_completed_ev_20260315_110848.json")

        # 决策缓存
        self.decision_cache_file = os.path.join(self.state_dir, "investment_decision_cache.json")
        self.current_decisions = {}

    def load_round_data(self, file_path: str) -> Dict:
        """加载指定轮次的数据"""
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"[元决策引擎] 加载数据失败 {file_path}: {e}")
        return {}

    def analyze_roi_data(self) -> Dict:
        """分析 round 585 ROI 评估数据"""
        data = self.load_round_data(self.roi_data_file)
        if not data:
            return {
                "status": "no_data",
                "message": "未找到 ROI 评估数据"
            }

        return {
            "round": 585,
            "goal": data.get("current_goal", ""),
            "status": data.get("是否完成", ""),
            "key_findings": data.get("创新点", []),
            "analysis": "ROI 评估引擎已完成价值投资回报的量化评估，为投资决策提供基础数据支撑"
        }

    def analyze_rebalancing_data(self) -> Dict:
        """分析 round 586 动态再平衡数据"""
        data = self.load_round_data(self.rebalancing_data_file)
        if not data:
            return {
                "status": "no_data",
                "message": "未找到动态再平衡数据"
            }

        return {
            "round": 586,
            "goal": data.get("current_goal", ""),
            "status": data.get("是否完成", ""),
            "key_findings": data.get("创新点", []),
            "analysis": "动态再平衡引擎已完成投资组合的动态调整，根据 ROI 趋势优化资源配置"
        }

    def analyze_risk_data(self) -> Dict:
        """分析 round 587 风险预警数据"""
        data = self.load_round_data(self.risk_data_file)
        if not data:
            return {
                "status": "no_data",
                "message": "未找到风险预警数据"
            }

        return {
            "round": 587,
            "goal": data.get("current_goal", ""),
            "status": data.get("是否完成", ""),
            "key_findings": data.get("创新点", []),
            "analysis": "风险预警引擎已完成投资风险的实时监控与预警，构建自适应保护机制"
        }

    def analyze_review_data(self) -> Dict:
        """分析 round 588 智能复盘数据"""
        data = self.load_round_data(self.review_data_file)
        if not data:
            return {
                "status": "no_data",
                "message": "未找到智能复盘数据"
            }

        return {
            "round": 588,
            "goal": data.get("current_goal", ""),
            "status": data.get("是否完成", ""),
            "key_findings": data.get("创新点", []),
            "analysis": "智能复盘引擎已完成投资决策的复盘分析，从历史案例中提取经验，持续优化策略"
        }

    def comprehensive_analysis(self) -> Dict:
        """综合分析所有环节的决策数据

        Returns:
            综合分析结果
        """
        roi_analysis = self.analyze_roi_data()
        rebalancing_analysis = self.analyze_rebalancing_data()
        risk_analysis = self.analyze_risk_data()
        review_analysis = self.analyze_review_data()

        # 构建综合分析报告
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "analysis_summary": {
                "roi": roi_analysis,
                "rebalancing": rebalancing_analysis,
                "risk": risk_analysis,
                "review": review_analysis
            },
            "overall_status": "健康",
            "findings": [],
            "recommendations": []
        }

        # 分析各环节状态
        all_complete = all([
            roi_analysis.get("status") == "已完成",
            rebalancing_analysis.get("status") == "已完成",
            risk_analysis.get("status") == "已完成",
            review_analysis.get("status") == "已完成"
        ])

        if all_complete:
            analysis["findings"].append("价值投资闭环完整：ROI评估 → 动态再平衡 → 风险预警 → 智能复盘 → 持续学习")
            analysis["findings"].append("各环节均已完成，形成了完整的投资进化闭环")
        else:
            incomplete = []
            if roi_analysis.get("status") != "已完成":
                incomplete.append("ROI评估")
            if rebalancing_analysis.get("status") != "已完成":
                incomplete.append("动态再平衡")
            if risk_analysis.get("status") != "已完成":
                incomplete.append("风险预警")
            if review_analysis.get("status") != "已完成":
                incomplete.append("智能复盘")
            analysis["findings"].append(f"待完成环节: {', '.join(incomplete)}")

        # 生成投资决策建议
        analysis["recommendations"] = self._generate_recommendations(analysis)

        # 缓存决策结果
        self.current_decisions = analysis
        self._save_decision_cache(analysis)

        return analysis

    def _generate_recommendations(self, analysis: Dict) -> List[Dict]:
        """基于综合分析生成投资决策建议"""
        recommendations = []

        # 基于闭环完整性建议
        if "价值投资闭环完整" in str(analysis.get("findings", [])):
            recommendations.append({
                "type": "投资方向",
                "priority": "高",
                "title": "深化价值投资闭环",
                "description": "当前投资闭环完整，建议继续深化各环节的智能化程度",
                "actions": [
                    "增强 ROI 预测模型的准确性",
                    "优化动态再平衡的触发阈值",
                    "完善风险预警的早期检测能力",
                    "建立更丰富的复盘案例库"
                ]
            })

            recommendations.append({
                "type": "创新方向",
                "priority": "中",
                "title": "探索跨领域价值投资",
                "description": "可考虑将价值投资能力扩展到其他领域，如创新投资、效能投资等",
                "actions": [
                    "分析创新驱动的投资回报模式",
                    "探索效能提升与价值实现的关联",
                    "构建跨领域价值评估体系"
                ]
            })

        # 基于系统健康状态建议
        analysis_summary = analysis.get("analysis_summary", {})
        for key, data in analysis_summary.items():
            if data.get("status") == "no_data":
                recommendations.append({
                    "type": "数据补充",
                    "priority": "高",
                    "title": f"补充 {key.upper()} 环节数据",
                    "description": f"缺少 {key} 环节的数据，需要补充以支持完整决策",
                    "actions": [
                        f"检查 round 数据文件是否存在",
                        "如有缺失需要补充相应环节的执行"
                    ]
                })

        # 默认建议
        if not recommendations:
            recommendations.append({
                "type": "常规优化",
                "priority": "中",
                "title": "持续优化投资策略",
                "description": "基于当前数据分析，建议持续优化投资决策",
                "actions": [
                    "定期更新投资组合配置",
                    "监控投资回报趋势",
                    "保持风险控制意识"
                ]
            })

        return recommendations

    def _save_decision_cache(self, analysis: Dict):
        """保存决策缓存"""
        try:
            with open(self.decision_cache_file, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[元决策引擎] 保存决策缓存失败: {e}")

    def get_cockpit_data(self) -> Dict:
        """获取驾驶舱数据接口

        Returns:
            驾驶舱展示数据
        """
        # 获取最新分析结果
        if not self.current_decisions:
            self.comprehensive_analysis()

        return {
            "engine_name": "元进化价值投资智能决策引擎",
            "version": self.VERSION,
            "round": 589,
            "status": "running",
            "components": {
                "roi_analysis": "已完成" if self.analyze_roi_data().get("status") == "已完成" else "待补充",
                "rebalancing_analysis": "已完成" if self.analyze_rebalancing_data().get("status") == "已完成" else "待补充",
                "risk_analysis": "已完成" if self.analyze_risk_data().get("status") == "已完成" else "待补充",
                "review_analysis": "已完成" if self.analyze_review_data().get("status") == "已完成" else "待补充"
            },
            "overall_status": self.current_decisions.get("overall_status", "unknown"),
            "findings": self.current_decisions.get("findings", []),
            "recommendations_count": len(self.current_decisions.get("recommendations", [])),
            "last_analysis": self.current_decisions.get("timestamp", "")
        }

    def get_decision_summary(self) -> Dict:
        """获取决策摘要

        Returns:
            决策摘要信息
        """
        if not self.current_decisions:
            self.comprehensive_analysis()

        recommendations = self.current_decisions.get("recommendations", [])

        return {
            "total_recommendations": len(recommendations),
            "high_priority": len([r for r in recommendations if r.get("priority") == "高"]),
            "medium_priority": len([r for r in recommendations if r.get("priority") == "中"]),
            "low_priority": len([r for r in recommendations if r.get("priority") == "低"]),
            "recommendations": recommendations[:5]  # 返回前5条
        }


def main():
    """主函数：支持命令行调用"""
    import argparse

    parser = argparse.ArgumentParser(description="元进化价值投资智能决策引擎")
    parser.add_argument("--analyze", action="store_true", help="执行综合分析")
    parser.add_argument("--roi", action="store_true", help="分析 ROI 数据")
    parser.add_argument("--rebalancing", action="store_true", help="分析动态再平衡数据")
    parser.add_argument("--risk", action="store_true", help="分析风险预警数据")
    parser.add_argument("--review", action="store_true", help="分析智能复盘数据")
    parser.add_argument("--cockpit-data", action="store_true", help="获取驾驶舱数据")
    parser.add_argument("--summary", action="store_true", help="获取决策摘要")
    parser.add_argument("--version", action="store_true", help="显示版本信息")
    parser.add_argument("--status", action="store_true", help="显示引擎状态")

    args = parser.parse_args()

    engine = MetaValueInvestmentIntelligentDecisionEngine()

    # 版本信息
    if args.version:
        print(f"元进化价值投资智能决策引擎 v{engine.VERSION}")
        return

    # 引擎状态
    if args.status:
        data = engine.get_cockpit_data()
        print(f"引擎状态: {data['status']}")
        print(f"整体状态: {data['overall_status']}")
        print(f"各环节分析状态:")
        for component, status in data['components'].items():
            print(f"  - {component}: {status}")
        return

    # 驾驶舱数据
    if args.cockpit_data:
        data = engine.get_cockpit_data()
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return

    # 决策摘要
    if args.summary:
        data = engine.get_decision_summary()
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return

    # ROI 数据分析
    if args.roi:
        data = engine.analyze_roi_data()
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return

    # 动态再平衡数据分析
    if args.rebalancing:
        data = engine.analyze_rebalancing_data()
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return

    # 风险预警数据分析
    if args.risk:
        data = engine.analyze_risk_data()
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return

    # 智能复盘数据分析
    if args.review:
        data = engine.analyze_review_data()
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return

    # 综合分析
    if args.analyze:
        data = engine.comprehensive_analysis()
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return

    # 默认显示帮助
    parser.print_help()


if __name__ == "__main__":
    main()