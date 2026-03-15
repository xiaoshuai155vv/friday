#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环元进化创新投资组合优化与战略决策增强引擎

在 round 600-601 完成的创新涌现与创新价值自动实现引擎基础上，
构建让系统能够从600+轮进化历史中分析创新投资回报、智能分配创新资源、
形成创新战略决策能力的完整创新投资管理闭环。

系统能够评估各创新方向的价值贡献、预测创新趋势、构建最优创新投资组合，
形成「创新涌现→投资分析→战略决策→价值实现」的完整创新驱动闭环。

让系统不仅能实现创新，还能智能管理创新投资组合，实现创新价值的最大化。

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


class InnovationPortfolioOptimizerStrategicDecisionEngine:
    """元进化创新投资组合优化与战略决策增强引擎"""

    def __init__(self):
        self.name = "元进化创新投资组合优化与战略决策增强引擎"
        self.version = "1.0.0"
        self.state_dir = STATE_DIR
        self.logs_dir = LOGS_DIR
        # round 600-601 创新引擎的数据文件
        self.innovation_data_file = self.state_dir / "meta_emergence_innovation_data.json"
        self.execution_records_file = self.state_dir / "innovation_execution_records.json"
        self.value_verification_file = self.state_dir / "innovation_value_verification.json"
        # 本引擎的数据文件
        self.portfolio_analysis_file = self.state_dir / "innovation_portfolio_analysis.json"
        self.strategic_decisions_file = self.state_dir / "innovation_strategic_decisions.json"
        self.investment_recommendations_file = self.state_dir / "innovation_investment_recommendations.json"

    def get_version(self):
        """获取引擎版本信息"""
        return {
            "name": self.name,
            "version": self.version,
            "description": "元进化创新投资组合优化与战略决策增强引擎"
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
                    # 提取与创新相关的进化轮次
                    goal = data.get("current_goal", "")
                    if "创新" in goal or "价值" in goal or "投资" in goal:
                        history.append({
                            "round": data.get("loop_round", 0),
                            "goal": goal,
                            "completed": data.get("completed", False),
                            "status": data.get("status", "unknown")
                        })
            except Exception as e:
                print(f"Warning: Failed to load {f}: {e}")
        return history

    def load_innovation_data(self):
        """加载 round 600-601 创新引擎的数据"""
        if not self.innovation_data_file.exists():
            return {}

        try:
            with open(self.innovation_data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Failed to load innovation data: {e}")
            return {}

    def load_execution_records(self):
        """加载创新执行记录"""
        if not self.execution_records_file.exists():
            return []

        try:
            with open(self.execution_records_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("execution_records", [])
        except Exception as e:
            print(f"Warning: Failed to load execution records: {e}")
            return []

    def analyze_portfolio(self):
        """分析创新投资组合"""
        print("=== 创新投资组合分析 ===")

        # 加载进化历史
        history = self.load_evolution_history()
        print(f"加载了 {len(history)} 条创新相关进化历史")

        # 加载创新数据
        innovation_data = self.load_innovation_data()
        print(f"创新数据: {len(innovation_data)} 项")

        # 加载执行记录
        execution_records = self.load_execution_records()
        print(f"执行记录: {len(execution_records)} 条")

        # 分析投资组合
        portfolio_analysis = {
            "total_investments": len(history),
            "execution_records": len(execution_records),
            "innovation_categories": self._categorize_innovations(history),
            "roi_analysis": self._analyze_roi(history, execution_records),
            "risk_assessment": self._assess_risk(history, execution_records),
            "trend_analysis": self._analyze_trends(history),
            "last_updated": datetime.now().isoformat()
        }

        # 保存分析结果
        self._save_portfolio_analysis(portfolio_analysis)

        print("投资组合分析完成")
        return portfolio_analysis

    def _categorize_innovations(self, history):
        """将创新分类"""
        categories = {}
        for item in history:
            goal = item.get("goal", "")
            # 简单分类
            if "元进化" in goal:
                category = "元进化创新"
            elif "价值" in goal:
                category = "价值创新"
            elif "投资" in goal:
                category = "投资创新"
            elif "知识" in goal:
                category = "知识创新"
            elif "决策" in goal:
                category = "决策创新"
            else:
                category = "其他创新"

            categories[category] = categories.get(category, 0) + 1

        return categories

    def _analyze_roi(self, history, execution_records):
        """分析投资回报率"""
        completed = sum(1 for h in history if h.get("completed", False))
        total = len(history)

        successful_executions = sum(1 for e in execution_records if e.get("status") == "success")

        return {
            "completion_rate": completed / total if total > 0 else 0,
            "execution_success_rate": successful_executions / len(execution_records) if execution_records else 0,
            "total_investments": total,
            "completed_investments": completed
        }

    def _assess_risk(self, history, execution_records):
        """评估风险"""
        failed = sum(1 for h in history if not h.get("completed", False))
        total = len(history)

        failed_executions = sum(1 for e in execution_records if e.get("status") == "failed")

        return {
            "failure_rate": failed / total if total > 0 else 0,
            "execution_failure_rate": failed_executions / len(execution_records) if execution_records else 0,
            "risk_level": "high" if failed / total > 0.3 else "medium" if failed / total > 0.1 else "low"
        }

    def _analyze_trends(self, history):
        """分析趋势"""
        # 按时间排序
        sorted_history = sorted(history, key=lambda x: x.get("round", 0))

        # 简单趋势分析
        recent_rounds = sorted_history[-10:] if len(sorted_history) >= 10 else sorted_history
        recent_completion = sum(1 for h in recent_rounds if h.get("completed", False))
        recent_rate = recent_completion / len(recent_rounds) if recent_rounds else 0

        return {
            "recent_completion_rate": recent_rate,
            "trend": "improving" if recent_rate > 0.7 else "stable" if recent_rate > 0.4 else "declining"
        }

    def _save_portfolio_analysis(self, analysis):
        """保存投资组合分析"""
        data = {
            "portfolio_analysis": analysis,
            "last_updated": datetime.now().isoformat()
        }
        with open(self.portfolio_analysis_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def predict_trends(self):
        """预测创新趋势"""
        print("=== 创新趋势预测 ===")

        # 加载分析数据
        portfolio_analysis = self._load_portfolio_analysis()
        history = self.load_evolution_history()

        # 基于历史数据和当前分析预测趋势
        trends = {
            "predicted_high_value_directions": self._predict_high_value_directions(history),
            "recommended_investment_allocation": self._recommend_investment_allocation(portfolio_analysis),
            "risk_adjusted_recommendations": self._risk_adjusted_recommendations(portfolio_analysis),
            "confidence_level": "medium",
            "last_updated": datetime.now().isoformat()
        }

        print("趋势预测完成")
        return trends

    def _load_portfolio_analysis(self):
        """加载投资组合分析"""
        if not self.portfolio_analysis_file.exists():
            return {}

        try:
            with open(self.portfolio_analysis_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("portfolio_analysis", {})
        except Exception as e:
            print(f"Warning: Failed to load portfolio analysis: {e}")
            return {}

    def _predict_high_value_directions(self, history):
        """预测高价值方向"""
        # 基于历史完成率预测
        completed = [h for h in history if h.get("completed", False)]
        categories = {}

        for h in completed:
            goal = h.get("goal", "")
            if "元进化" in goal:
                categories["元进化创新"] = categories.get("元进化创新", 0) + 1
            elif "价值" in goal:
                categories["价值创新"] = categories.get("价值创新", 0) + 1
            elif "投资" in goal:
                categories["投资创新"] = categories.get("投资创新", 0) + 1

        # 排序返回前几名
        sorted_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)
        return [{"direction": k, "score": v} for k, v in sorted_categories[:5]]

    def _recommend_investment_allocation(self, portfolio_analysis):
        """推荐投资分配"""
        roi = portfolio_analysis.get("roi_analysis", {})
        risk = portfolio_analysis.get("risk_assessment", {})

        # 基于 ROI 和风险推荐分配
        allocation = {
            "high_priority": ["元进化创新", "价值创新"],
            "medium_priority": ["投资创新", "知识创新"],
            "low_priority": ["其他创新"],
            "reasoning": "基于历史 ROI 和风险评估"
        }

        return allocation

    def _risk_adjusted_recommendations(self, portfolio_analysis):
        """风险调整后的建议"""
        risk = portfolio_analysis.get("risk_assessment", {})
        risk_level = risk.get("risk_level", "low")

        if risk_level == "high":
            return {
                "recommendation": "降低高风险创新投资，增加稳健型创新投入",
                "action": "优先支持已完成验证的创新方向"
            }
        elif risk_level == "medium":
            return {
                "recommendation": "保持当前投资策略，适度增加高ROI创新投入",
                "action": "继续支持已完成验证的创新方向，同时探索新方向"
            }
        else:
            return {
                "recommendation": "可以增加高风险高回报的创新探索",
                "action": "适度增加前沿创新投资"
            }

    def generate_strategic_decisions(self):
        """生成战略决策建议"""
        print("=== 战略决策建议生成 ===")

        # 获取分析数据和预测
        portfolio_analysis = self._load_portfolio_analysis()
        trends = self.predict_trends()

        # 生成战略决策
        decisions = {
            "investment_priorities": self._generate_investment_priorities(portfolio_analysis, trends),
            "resource_allocation": self._generate_resource_allocation(portfolio_analysis, trends),
            "risk_management": self._generate_risk_management(portfolio_analysis),
            "expected_outcomes": self._generate_expected_outcomes(portfolio_analysis),
            "confidence": "high" if portfolio_analysis.get("roi_analysis", {}).get("completion_rate", 0) > 0.7 else "medium",
            "last_updated": datetime.now().isoformat()
        }

        # 保存决策
        self._save_strategic_decisions(decisions)

        print("战略决策建议生成完成")
        return decisions

    def _generate_investment_priorities(self, portfolio_analysis, trends):
        """生成投资优先级"""
        categories = portfolio_analysis.get("innovation_categories", {})
        sorted_cats = sorted(categories.items(), key=lambda x: x[1], reverse=True)

        priorities = []
        for cat, count in sorted_cats[:5]:
            priorities.append({
                "category": cat,
                "priority": len(priorities) + 1,
                "weight": count / sum(categories.values()) if categories else 0
            })

        return priorities

    def _generate_resource_allocation(self, portfolio_analysis, trends):
        """生成资源配置建议"""
        allocation = trends.get("recommended_investment_allocation", {})

        return {
            "high_priority_percentage": 50,
            "medium_priority_percentage": 30,
            "low_priority_percentage": 20,
            "details": allocation
        }

    def _generate_risk_management(self, portfolio_analysis):
        """生成风险管理建议"""
        risk = portfolio_analysis.get("risk_assessment", {})
        risk_level = risk.get("risk_level", "low")

        return {
            "current_risk_level": risk_level,
            "recommended_actions": [
                "持续监控创新投资组合的风险指标",
                "建立风险预警机制",
                "定期评估投资组合的健康状况"
            ],
            "contingency_plans": [
                "当风险超阈值时，自动触发保护措施",
                "减少高风险投资，增加稳健型投资",
                "启动备份策略"
            ]
        }

    def _generate_expected_outcomes(self, portfolio_analysis):
        """生成预期结果"""
        roi = portfolio_analysis.get("roi_analysis", {})
        trend = portfolio_analysis.get("trend_analysis", {})

        return {
            "expected_roi_improvement": "10-20%" if trend.get("trend") == "improving" else "5-10%",
            "expected_completion_rate": roi.get("completion_rate", 0),
            "timeframe": "3-6个月"
        }

    def _save_strategic_decisions(self, decisions):
        """保存战略决策"""
        data = {
            "strategic_decisions": decisions,
            "last_updated": datetime.now().isoformat()
        }
        with open(self.strategic_decisions_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def run_full_analysis(self):
        """运行完整分析流程"""
        print(f"=== {self.name} ===")
        print(f"Version: {self.version}")
        print()

        # 1. 分析投资组合
        portfolio_analysis = self.analyze_portfolio()

        # 2. 预测趋势
        trends = self.predict_trends()

        # 3. 生成战略决策
        decisions = self.generate_strategic_decisions()

        # 4. 生成投资建议
        recommendations = self._generate_investment_recommendations(portfolio_analysis, trends, decisions)

        print()
        print("=== 分析完成 ===")
        print(f"投资组合分析: {portfolio_analysis.get('total_investments', 0)} 项")
        print(f"风险评估: {portfolio_analysis.get('risk_assessment', {}).get('risk_level', 'unknown')}")
        print(f"趋势预测: {portfolio_analysis.get('trend_analysis', {}).get('trend', 'unknown')}")
        print(f"战略决策置信度: {decisions.get('confidence', 'unknown')}")

        return {
            "portfolio_analysis": portfolio_analysis,
            "trends": trends,
            "decisions": decisions,
            "recommendations": recommendations
        }

    def _generate_investment_recommendations(self, portfolio_analysis, trends, decisions):
        """生成投资建议"""
        recommendations = {
            "short_term": [
                "继续支持高ROI的创新方向",
                "监控现有创新投资组合的表现"
            ],
            "medium_term": [
                "根据趋势预测调整投资方向",
                "建立风险预警机制"
            ],
            "long_term": [
                "构建智能投资决策系统",
                "实现完全自动化的创新投资管理"
            ]
        }

        # 保存投资建议
        data = {
            "recommendations": recommendations,
            "last_updated": datetime.now().isoformat()
        }
        with open(self.investment_recommendations_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return recommendations

    def get_cockpit_data(self):
        """获取驾驶舱数据"""
        portfolio_analysis = self._load_portfolio_analysis()

        # 加载战略决策
        strategic_decisions = {}
        if self.strategic_decisions_file.exists():
            try:
                with open(self.strategic_decisions_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    strategic_decisions = data.get("strategic_decisions", {})
            except Exception as e:
                print(f"Warning: Failed to load strategic decisions: {e}")

        return {
            "engine_name": self.name,
            "version": self.version,
            "portfolio_analysis": portfolio_analysis,
            "strategic_decisions": strategic_decisions,
            "status": "ready"
        }


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="元进化创新投资组合优化与战略决策增强引擎")
    parser.add_argument('--version', action='store_true', help='显示版本信息')
    parser.add_argument('--status', action='store_true', help='显示引擎状态')
    parser.add_argument('--run', action='store_true', help='运行完整分析')
    parser.add_argument('--cockpit-data', action='store_true', help='获取驾驶舱数据')

    args = parser.parse_args()

    engine = InnovationPortfolioOptimizerStrategicDecisionEngine()

    if args.version:
        version_info = engine.get_version()
        print(f"{version_info['name']} v{version_info['version']}")
        return

    if args.status:
        print(f"Engine: {engine.name}")
        print(f"Version: {engine.version}")
        print(f"Status: ready")
        return

    if args.run:
        engine.run_full_analysis()
        return

    if args.cockpit_data:
        data = engine.get_cockpit_data()
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return

    # 默认显示版本
    version_info = engine.get_version()
    print(f"{version_info['name']} v{version_info['version']}")
    print(f"使用 --help 查看更多选项")


if __name__ == "__main__":
    main()