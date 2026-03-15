"""
智能全场景进化环创新投资回报自动评估与策略优化引擎

该模块实现创新投资回报（ROI）自动评估与策略优化能力：
1. 分析历史进化数据，评估各进化方向的投入产出比
2. 预测不同进化任务的潜在价值
3. 自动优先处理高ROI进化任务
4. 持续优化进化策略
5. 与进化驾驶舱深度集成

version: 1.0.0
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple


class EvolutionROIAssessmentEngine:
    """创新投资回报自动评估与策略优化引擎"""

    def __init__(self, runtime_dir: str = None):
        """初始化引擎"""
        self.runtime_dir = Path(runtime_dir) if runtime_dir else Path(__file__).parent.parent / "runtime"
        self.state_dir = self.runtime_dir / "state"
        self.logs_dir = self.runtime_dir / "logs"

        # 进化历史数据缓存
        self.evolution_history = []
        self.engine_metrics = {}

        # ROI评估参数
        self.roi_weights = {
            "value_realization": 0.3,      # 价值实现权重
            "efficiency_improvement": 0.25,  # 效率提升权重
            "capability_gain": 0.25,       # 能力获得权重
            "system_health": 0.2           # 系统健康权重
        }

    def load_evolution_history(self) -> List[Dict]:
        """加载进化历史数据"""
        history = []

        # 加载已完成进化的历史记录
        completed_dir = self.state_dir
        if completed_dir.exists():
            for f in completed_dir.glob("evolution_completed_*.json"):
                try:
                    with open(f, 'r', encoding='utf-8') as file:
                        data = json.load(file)
                        if isinstance(data, dict):
                            history.append(data)
                except Exception as e:
                    print(f"加载 {f} 失败: {e}")

        self.evolution_history = history
        return history

    def calculate_evolution_roi(self, evolution_data: Dict) -> float:
        """计算单次进化的ROI"""
        if not evolution_data:
            return 0.0

        # 提取关键指标
        value_score = evolution_data.get("value_score", 0.5)
        efficiency_score = evolution_data.get("efficiency_score", 0.5)
        capability_score = evolution_data.get("capability_score", 0.5)
        health_impact = evolution_data.get("health_impact", 0.5)

        # 计算综合ROI
        roi = (
            value_score * self.roi_weights["value_realization"] +
            efficiency_score * self.roi_weights["efficiency_improvement"] +
            capability_score * self.roi_weights["capability_gain"] +
            health_impact * self.roi_weights["system_health"]
        )

        return round(roi, 3)

    def analyze_roi_trends(self) -> Dict[str, Any]:
        """分析ROI趋势"""
        if not self.evolution_history:
            self.load_evolution_history()

        if not self.evolution_history:
            return {
                "status": "no_data",
                "message": "没有足够的进化历史数据进行分析"
            }

        # 按时间分组分析
        roi_by_period = {}
        recent_roi = []

        for evo in self.evolution_history:
            timestamp = evo.get("completed_at", "")
            if timestamp:
                try:
                    date = timestamp[:10]  # 取日期部分
                    roi = self.calculate_evolution_roi(evo)
                    if date not in roi_by_period:
                        roi_by_period[date] = []
                    roi_by_period[date].append(roi)

                    # 最近30天的数据
                    if len(recent_roi) < 30:
                        recent_roi.append(roi)
                except Exception:
                    pass

        # 计算趋势
        avg_roi = sum(recent_roi) / len(recent_roi) if recent_roi else 0

        return {
            "status": "success",
            "total_evolution_count": len(self.evolution_history),
            "average_roi": round(avg_roi, 3),
            "roi_by_period": {k: round(sum(v) / len(v), 3) for k, v in roi_by_period.items()},
            "trend": "improving" if avg_roi > 0.6 else "stable" if avg_roi > 0.4 else "declining"
        }

    def predict_roi(self, evolution_type: str, context: Dict = None) -> Dict[str, Any]:
        """预测特定进化类型的ROI"""
        # 基于历史数据预测
        similar_evo = [
            evo for evo in self.evolution_history
            if evolution_type.lower() in evo.get("current_goal", "").lower()
        ]

        if similar_evo:
            predicted_roi = sum(
                self.calculate_evolution_roi(evo) for evo in similar_evo
            ) / len(similar_evo)
        else:
            # 基于类型默认预测
            type_roi_map = {
                "knowledge": 0.7,
                "optimization": 0.75,
                "meta": 0.8,
                "integration": 0.65,
                "engine": 0.7,
                "self": 0.85,
                "value": 0.7,
                "cognition": 0.75
            }

            predicted_roi = 0.5
            for key, value in type_roi_map.items():
                if key in evolution_type.lower():
                    predicted_roi = value
                    break

        # 考虑上下文调整
        if context:
            system_load = context.get("system_load", 0.5)
            health_score = context.get("health_score", 0.7)

            # 系统负载高时降低预期ROI
            if system_load > 0.8:
                predicted_roi *= 0.8
            # 系统健康度低时降低预期ROI
            if health_score < 0.5:
                predicted_roi *= 0.7

        return {
            "evolution_type": evolution_type,
            "predicted_roi": round(predicted_roi, 3),
            "confidence": "high" if similar_evo else "medium",
            "similar_evolution_count": len(similar_evo)
        }

    def optimize_strategy(self, available_tasks: List[Dict]) -> List[Dict]:
        """优化进化策略 - 优先处理高ROI任务"""
        if not available_tasks:
            # 如果没有可用任务，自动生成候选
            available_tasks = self.generate_candidate_tasks()

        # 为每个任务预测ROI
        task_roi = []
        for task in available_tasks:
            task_type = task.get("type", task.get("current_goal", "general"))
            prediction = self.predict_roi(task_type)
            task_with_roi = {**task, "predicted_roi": prediction["predicted_roi"]}
            task_roi.append(task_with_roi)

        # 按ROI排序
        sorted_tasks = sorted(task_roi, key=lambda x: x.get("predicted_roi", 0), reverse=True)

        # 选择Top N个任务
        top_tasks = sorted_tasks[:5]

        return {
            "status": "success",
            "optimized_tasks": top_tasks,
            "total_candidates": len(available_tasks),
            "selection_criteria": "predicted_roi DESC"
        }

    def generate_candidate_tasks(self) -> List[Dict]:
        """自动生成候选进化任务"""
        candidates = [
            {"type": "knowledge", "current_goal": "知识驱动自动化触发增强", "description": "增强知识驱动能力"},
            {"type": "optimization", "current_goal": "执行策略自优化", "description": "优化执行策略"},
            {"type": "meta", "current_goal": "元进化能力增强", "description": "增强元进化能力"},
            {"type": "integration", "current_goal": "跨引擎协同优化", "description": "改进跨引擎协同"},
            {"type": "self", "current_goal": "自我进化效能分析", "description": "分析自我进化效能"}
        ]
        return candidates

    def get_cockpit_data(self) -> Dict[str, Any]:
        """获取驾驶舱展示数据"""
        trends = self.analyze_roi_trends()
        optimized = self.optimize_strategy([])

        return {
            "roi_trends": trends,
            "optimized_strategy": optimized,
            "total_evolution_count": len(self.evolution_history),
            "recommendations": self.generate_recommendations()
        }

    def generate_recommendations(self) -> List[Dict]:
        """生成优化建议"""
        trends = self.analyze_roi_trends()

        recommendations = []

        if trends.get("trend") == "declining":
            recommendations.append({
                "type": "warning",
                "message": "ROI呈下降趋势，建议调整进化策略方向",
                "action": "增加高价值进化任务的优先级"
            })

        if trends.get("average_roi", 0) < 0.5:
            recommendations.append({
                "type": "info",
                "message": "平均ROI偏低，建议加强效能分析",
                "action": "优化资源配置和执行策略"
            })

        # 基于系统健康状况建议
        recommendations.append({
            "type": "suggestion",
            "message": "持续监控ROI变化，自动调整进化策略",
            "action": "启用自动策略优化功能"
        })

        return recommendations


def main():
    """主函数 - 支持命令行调用"""
    import argparse

    parser = argparse.ArgumentParser(
        description="智能全场景进化环创新投资回报自动评估与策略优化引擎"
    )
    parser.add_argument("--status", action="store_true", help="显示ROI状态")
    parser.add_argument("--trends", action="store_true", help="分析ROI趋势")
    parser.add_argument("--predict", type=str, help="预测特定进化类型的ROI")
    parser.add_argument("--optimize", action="store_true", help="优化进化策略")
    parser.add_argument("--cockpit-data", action="store_true", help="获取驾驶舱数据")
    parser.add_argument("--recommendations", action="store_true", help="生成优化建议")

    args = parser.parse_args()

    engine = EvolutionROIAssessmentEngine()

    if args.status:
        result = engine.analyze_roi_trends()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.trends:
        result = engine.analyze_roi_trends()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.predict:
        result = engine.predict_roi(args.predict)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.optimize:
        result = engine.optimize_strategy([])
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.cockpit_data:
        result = engine.get_cockpit_data()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.recommendations:
        result = engine.generate_recommendations()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    else:
        # 默认显示状态
        result = engine.analyze_roi_trends()
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()