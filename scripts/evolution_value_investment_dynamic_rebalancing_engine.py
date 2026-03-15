#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环价值投资动态再平衡与持续优化引擎
价值投资动态再平衡引擎 - 在 round 585 完成的 ROI 智能评估基础上，
构建价值投资的动态再平衡能力。让系统能够基于 ROI 评估结果动态调整进化投资组合、
实时优化资源配置、实现价值最大化的持续优化。

version: 1.0.0
"""

import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict

# 确保可以导入 ROI 评估引擎
try:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from evolution_value_investment_roi_assessment_engine import ValueInvestmentROIAssessmentEngine
    ROI_ENGINE_AVAILABLE = True
except ImportError:
    ROI_ENGINE_AVAILABLE = False


class ValueInvestmentDynamicRebalancingEngine:
    """价值投资动态再平衡引擎"""

    def __init__(self, state_dir: str = None):
        self.version = "1.0.0"
        self.state_dir = state_dir or "runtime/state"
        self.history_file = os.path.join(self.state_dir, "evolution_completed_*.json")
        self.roi_data_file = os.path.join(self.state_dir, "roi_assessment_data.json")

        # 投资组合配置
        self.investment_categories = {
            "价值实现": {"weight": 0.25, "min_weight": 0.15, "max_weight": 0.40},
            "效率优化": {"weight": 0.20, "min_weight": 0.10, "max_weight": 0.35},
            "创新探索": {"weight": 0.20, "min_weight": 0.10, "max_weight": 0.35},
            "能力增强": {"weight": 0.20, "min_weight": 0.10, "max_weight": 0.35},
            "基础保障": {"weight": 0.15, "min_weight": 0.05, "max_weight": 0.25}
        }

        # 再平衡参数
        self.rebalance_threshold = 0.10  # 权重偏离阈值，超过则触发再平衡
        self.trend_window = 10  # 趋势分析窗口（轮次）
        self.optimization_interval = 5  # 优化间隔（轮次）

        # 历史数据
        self.roi_history = []
        self.rebalance_history = []
        self.optimization_history = []

    def load_roi_data(self) -> List[Dict]:
        """加载 ROI 评估数据"""
        roi_data = []
        if os.path.exists(self.roi_data_file):
            try:
                with open(self.roi_data_file, 'r', encoding='utf-8') as f:
                    roi_data = json.load(f)
                    if isinstance(roi_data, list):
                        self.roi_history = roi_data
                    else:
                        self.roi_history = [roi_data]
            except Exception as e:
                print(f"加载 ROI 数据失败: {e}")

        # 尝试从历史文件加载
        import glob
        state_files = glob.glob(os.path.join(self.state_dir, "evolution_completed_ev_*.json"))
        for f in sorted(state_files, reverse=True)[:50]:  # 取最近50轮
            try:
                with open(f, 'r', encoding='utf-8') as fp:
                    data = json.load(fp)
                    if "做了什么" in data:
                        roi_entry = {
                            "round": data.get("loop_round", 0),
                            "timestamp": data.get("timestamp", ""),
                            "description": data.get("做了什么", ""),
                            "roi": data.get("roi_assessment", {}),
                            "status": data.get("是否完成", "未知")
                        }
                        roi_data.append(roi_entry)
            except Exception:
                continue

        return roi_data

    def analyze_roi_trends(self, roi_data: List[Dict] = None) -> Dict[str, Any]:
        """分析 ROI 趋势"""
        if roi_data is None:
            roi_data = self.load_roi_data()

        if not roi_data:
            return {
                "trend": "unknown",
                "slope": 0,
                "volatility": 0,
                "pattern": "无足够数据",
                "insights": ["暂无 ROI 历史数据，无法分析趋势"]
            }

        # 按轮次排序
        sorted_data = sorted(roi_data, key=lambda x: x.get("round", 0), reverse=True)
        recent_data = sorted_data[:self.trend_window]

        # 计算趋势
        if len(recent_data) >= 3:
            rounds = [d.get("round", 0) for d in recent_data]
            roi_values = []

            for d in recent_data:
                roi_info = d.get("roi", {})
                if isinstance(roi_info, dict):
                    # 尝试获取 ROI 值
                    roi_value = roi_info.get("roi", 0.5) if isinstance(roi_info, dict) else 0.5
                else:
                    roi_value = 0.5
                roi_values.append(roi_value)

            # 计算斜率（简单线性回归）
            n = len(rounds)
            if n >= 2 and rounds[0] != rounds[-1]:
                sum_x = sum(rounds)
                sum_y = sum(roi_values)
                sum_xy = sum(r * v for r, v in zip(rounds, roi_values))
                sum_x2 = sum(r ** 2 for r in rounds)

                slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2) if (n * sum_x2 - sum_x ** 2) != 0 else 0
            else:
                slope = 0

            # 计算波动性
            if len(roi_values) >= 2:
                mean = sum(roi_values) / len(roi_values)
                variance = sum((v - mean) ** 2 for v in roi_values) / len(roi_values)
                volatility = variance ** 0.5
            else:
                volatility = 0

            # 判断趋势
            if slope > 0.01:
                trend = "rising"
                pattern = "上升趋势"
            elif slope < -0.01:
                trend = "declining"
                pattern = "下降趋势"
            else:
                trend = "stable"
                pattern = "稳定趋势"

            # 生成洞察
            insights = []
            if trend == "rising":
                insights.append("投资回报呈上升趋势，建议适度增加投资")
            elif trend == "declining":
                insights.append("投资回报呈下降趋势，需要调整投资组合")
            else:
                insights.append("投资回报保持稳定，可维持当前策略")

            if volatility > 0.2:
                insights.append("波动性较高，建议增加稳健型投资比例")

            return {
                "trend": trend,
                "slope": round(slope, 4),
                "volatility": round(volatility, 4),
                "pattern": pattern,
                "insights": insights,
                "recent_rounds": len(recent_data)
            }

        return {
            "trend": "insufficient_data",
            "slope": 0,
            "volatility": 0,
            "pattern": "数据不足",
            "insights": ["数据不足，无法准确分析趋势"]
        }

    def calculate_current_allocation(self) -> Dict[str, float]:
        """计算当前投资配置"""
        allocation = {}
        for category, config in self.investment_categories.items():
            allocation[category] = config["weight"]
        return allocation

    def generate_rebalance_plan(self, trends: Dict = None) -> Dict[str, Any]:
        """生成再平衡计划"""
        if trends is None:
            trends = self.analyze_roi_trends()

        current_allocation = self.calculate_current_allocation()
        recommended_allocation = current_allocation.copy()

        trend = trends.get("trend", "unknown")

        # 根据趋势调整配置
        if trend == "rising":
            # 上升趋势：增加创新探索和能力增强
            recommended_allocation["创新探索"] = min(0.30, recommended_allocation["创新探索"] + 0.05)
            recommended_allocation["能力增强"] = min(0.30, recommended_allocation["能力增强"] + 0.05)
            recommended_allocation["效率优化"] = max(0.15, recommended_allocation["效率优化"] - 0.05)

        elif trend == "declining":
            # 下降趋势：增加基础保障和效率优化
            recommended_allocation["基础保障"] = min(0.25, recommended_allocation["基础保障"] + 0.05)
            recommended_allocation["效率优化"] = min(0.30, recommended_allocation["效率优化"] + 0.05)
            recommended_allocation["创新探索"] = max(0.10, recommended_allocation["创新探索"] - 0.05)

        else:
            # 稳定趋势：保持均衡
            pass

        # 归一化
        total = sum(recommended_allocation.values())
        for k in recommended_allocation:
            recommended_allocation[k] = recommended_allocation[k] / total

        # 检查是否需要再平衡
        needs_rebalance = False
        changes = {}
        for category in current_allocation:
            diff = abs(recommended_allocation[category] - current_allocation[category])
            if diff > self.rebalance_threshold:
                needs_rebalance = True
                changes[category] = {
                    "from": round(current_allocation[category], 3),
                    "to": round(recommended_allocation[category], 3),
                    "change": round(recommended_allocation[category] - current_allocation[category], 3)
                }

        return {
            "needs_rebalance": needs_rebalance,
            "current_allocation": {k: round(v, 3) for k, v in current_allocation.items()},
            "recommended_allocation": {k: round(v, 3) for k, v in recommended_allocation.items()},
            "changes": changes,
            "trend_analysis": trends,
            "rebalance_reason": "权重偏离超过阈值" if needs_rebalance else "配置合理，无需调整"
        }

    def optimize_resource_allocation(self, rebalance_plan: Dict = None) -> Dict[str, Any]:
        """优化资源配置"""
        if rebalance_plan is None:
            rebalance_plan = self.generate_rebalance_plan()

        allocation = rebalance_plan.get("recommended_allocation", {})
        trend = rebalance_plan.get("trend_analysis", {}).get("trend", "unknown")

        # 生成优化建议
        optimization_suggestions = []

        for category, weight in allocation.items():
            config = self.investment_categories.get(category, {})
            min_w = config.get("min_weight", 0.1)
            max_w = config.get("max_weight", 0.4)

            if weight > max_w:
                optimization_suggestions.append({
                    "category": category,
                    "action": "减少",
                    "reason": f"配置比例({weight:.1%})超过上限({max_w:.1%})",
                    "priority": "high" if weight - max_w > 0.1 else "medium"
                })
            elif weight < min_w:
                optimization_suggestions.append({
                    "category": category,
                    "action": "增加",
                    "reason": f"配置比例({weight:.1%})低于下限({min_w:.1%})",
                    "priority": "high" if min_w - weight > 0.1 else "medium"
                })

        # 添加趋势相关的优化建议
        if trend == "declining":
            optimization_suggestions.append({
                "category": "整体",
                "action": "收缩",
                "reason": "投资回报呈下降趋势，建议降低风险敞口",
                "priority": "high"
            })
        elif trend == "rising":
            optimization_suggestions.append({
                "category": "整体",
                "action": "扩张",
                "reason": "投资回报呈上升趋势，建议把握机会增加投入",
                "priority": "medium"
            })

        return {
            "rebalance_plan": rebalance_plan,
            "optimization_suggestions": optimization_suggestions,
            "total_suggestions": len(optimization_suggestions),
            "high_priority_count": len([s for s in optimization_suggestions if s.get("priority") == "high"])
        }

    def execute_rebalance(self, optimization: Dict = None) -> Dict[str, Any]:
        """执行再平衡"""
        if optimization is None:
            optimization = self.optimize_resource_allocation()

        rebalance_plan = optimization.get("rebalance_plan", {})

        # 记录再平衡历史
        rebalance_record = {
            "timestamp": datetime.now().isoformat(),
            "needs_rebalance": rebalance_plan.get("needs_rebalance", False),
            "current_allocation": rebalance_plan.get("current_allocation", {}),
            "recommended_allocation": rebalance_plan.get("recommended_allocation", {}),
            "changes": rebalance_plan.get("changes", {}),
            "suggestions": optimization.get("optimization_suggestions", [])
        }

        self.rebalance_history.append(rebalance_record)

        # 更新配置
        for category, weight in rebalance_plan.get("recommended_allocation", {}).items():
            if category in self.investment_categories:
                self.investment_categories[category]["weight"] = weight

        return {
            "success": True,
            "rebalance_record": rebalance_record,
            "message": "再平衡执行成功" if rebalance_record["needs_rebalance"] else "无需再平衡，配置已优化"
        }

    def run_full_optimization_cycle(self) -> Dict[str, Any]:
        """运行完整优化周期"""
        # 1. 加载 ROI 数据
        roi_data = self.load_roi_data()

        # 2. 分析趋势
        trends = self.analyze_roi_trends(roi_data)

        # 3. 生成再平衡计划
        rebalance_plan = self.generate_rebalance_plan(trends)

        # 4. 优化资源配置
        optimization = self.optimize_resource_allocation(rebalance_plan)

        # 5. 执行再平衡
        result = self.execute_rebalance(optimization)

        return {
            "roi_data_count": len(roi_data),
            "trends": trends,
            "rebalance_plan": rebalance_plan,
            "optimization": optimization,
            "execution_result": result,
            "timestamp": datetime.now().isoformat()
        }

    def get_cockpit_data(self) -> Dict[str, Any]:
        """获取驾驶舱数据"""
        trends = self.analyze_roi_trends()
        rebalance_plan = self.generate_rebalance_plan(trends)
        optimization = self.optimize_resource_allocation(rebalance_plan)

        return {
            "engine": "价值投资动态再平衡引擎",
            "version": self.version,
            "current_allocation": self.calculate_current_allocation(),
            "trends": trends,
            "rebalance_plan": rebalance_plan,
            "optimization_suggestions": optimization.get("optimization_suggestions", []),
            "needs_rebalance": rebalance_plan.get("needs_rebalance", False),
            "high_priority_suggestions": optimization.get("high_priority_count", 0),
            "rebalance_history_count": len(self.rebalance_history),
            "timestamp": datetime.now().isoformat()
        }

    def get_status(self) -> Dict[str, Any]:
        """获取引擎状态"""
        trends = self.analyze_roi_trends()
        return {
            "engine": "价值投资动态再平衡引擎",
            "version": self.version,
            "status": "running",
            "trends": trends,
            "needs_rebalance": trends.get("trend") in ["rising", "declining"],
            "investment_categories": list(self.investment_categories.keys()),
            "rebalance_threshold": self.rebalance_threshold,
            "trend_window": self.trend_window,
            "timestamp": datetime.now().isoformat()
        }


def main():
    """主函数 - 命令行入口"""
    import argparse
    parser = argparse.ArgumentParser(description="价值投资动态再平衡引擎")
    parser.add_argument("--status", action="store_true", help="获取引擎状态")
    parser.add_argument("--analyze-trends", action="store_true", help="分析 ROI 趋势")
    parser.add_argument("--rebalance-plan", action="store_true", help="生成再平衡计划")
    parser.add_argument("--optimize", action="store_true", help="优化资源配置")
    parser.add_argument("--run", action="store_true", help="运行完整优化周期")
    parser.add_argument("--cockpit-data", action="store_true", help="获取驾驶舱数据")
    parser.add_argument("--state-dir", type=str, default="runtime/state", help="状态目录")

    args = parser.parse_args()

    engine = ValueInvestmentDynamicRebalancingEngine(args.state_dir)

    if args.status:
        result = engine.get_status()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.analyze_trends:
        result = engine.analyze_roi_trends()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.rebalance_plan:
        result = engine.generate_rebalance_plan()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.optimize:
        result = engine.optimize_resource_allocation()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.run:
        result = engine.run_full_optimization_cycle()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.cockpit_data:
        result = engine.get_cockpit_data()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()