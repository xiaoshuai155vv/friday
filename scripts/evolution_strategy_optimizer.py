#!/usr/bin/env python3
"""
智能进化策略自适应优化引擎 (Evolution Strategy Adaptive Optimizer)
让系统能够自动分析进化历史、识别进化模式、动态调整进化策略，找出最佳进化路径。

功能：
1. 进化历史深度分析 - 分析轮次效率、识别进化模式、挖掘趋势
2. 进化策略自适应调整 - 基于历史效果动态优化策略参数
3. 最佳路径推荐 - 分析多条进化路径并推荐最优
4. 策略效果预测 - 预测不同策略的效果
"""

import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from collections import defaultdict

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
RUNTIME_STATE_DIR = PROJECT_ROOT / "runtime" / "state"
RUNTIME_LOGS_DIR = PROJECT_ROOT / "runtime" / "logs"
REFERENCES_DIR = PROJECT_ROOT / "references"


class EvolutionStrategyOptimizer:
    """智能进化策略自适应优化引擎"""

    def __init__(self):
        self.name = "EvolutionStrategyOptimizer"
        self.version = "1.0.0"
        self.strategy_config = self._load_strategy_config()
        self.evolution_history = self._load_evolution_history()

    def _load_strategy_config(self) -> Dict:
        """加载策略配置"""
        config_file = REFERENCES_DIR / "evolution_strategy_config.json"
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass

        # 默认配置
        return {
            "strategy_weights": {
                "innovation": 0.3,
                "stability": 0.2,
                "efficiency": 0.25,
                "user_need": 0.25
            },
            "optimization_interval": 10,
            "pattern_detection_threshold": 5,
            "strategy_adjustment_rate": 0.1
        }

    def _load_evolution_history(self) -> List[Dict]:
        """加载进化历史"""
        history = []
        state_dir = RUNTIME_STATE_DIR

        if not state_dir.exists():
            return history

        # 加载所有进化完成记录
        for f in state_dir.glob("evolution_completed_*.json"):
            try:
                with open(f, 'r', encoding='utf-8') as fp:
                    data = json.load(fp)
                    if isinstance(data, dict):
                        history.append(data)
            except Exception:
                continue

        # 按时间排序
        history.sort(key=lambda x: x.get('completed_at', ''), reverse=True)
        return history

    def analyze_history(self) -> Dict[str, Any]:
        """深度分析进化历史"""
        if not self.evolution_history:
            return {
                "status": "no_data",
                "message": "暂无进化历史数据"
            }

        analysis = {
            "total_rounds": len(self.evolution_history),
            "completion_rate": self._calculate_completion_rate(),
            "efficiency_trends": self._analyze_efficiency_trends(),
            "pattern_clusters": self._detect_pattern_clusters(),
            "high_value_rounds": self._identify_high_value_rounds(),
            "low_value_rounds": self._identify_low_value_rounds(),
            "repeated_improvements": self._detect_repeated_improvements(),
            "strategy_effectiveness": self._evaluate_strategy_effectiveness()
        }

        return analysis

    def _calculate_completion_rate(self) -> float:
        """计算完成率"""
        completed = sum(1 for h in self.evolution_history if h.get('status') == 'completed')
        total = len(self.evolution_history)
        return completed / total if total > 0 else 0.0

    def _analyze_efficiency_trends(self) -> Dict[str, Any]:
        """分析效率趋势"""
        if len(self.evolution_history) < 3:
            return {"status": "insufficient_data"}

        # 按时间窗口分析
        recent = self.evolution_history[:10]
        older = self.evolution_history[10:20] if len(self.evolution_history) > 10 else []

        recent_avg = sum(h.get('value_score', 50) for h in recent) / len(recent) if recent else 0

        trend = "stable"
        if older:
            older_avg = sum(h.get('value_score', 50) for h in older) / len(older)
            if recent_avg > older_avg * 1.1:
                trend = "improving"
            elif recent_avg < older_avg * 0.9:
                trend = "declining"

        return {
            "recent_average_score": recent_avg,
            "trend": trend,
            "change_percentage": ((recent_avg - (sum(h.get('value_score', 50) for h in older) / len(older) if older else recent_avg)) /
                                 (sum(h.get('value_score', 50) for h in older) / len(older) if older else 1)) * 100
        }

    def _detect_pattern_clusters(self) -> List[Dict[str, Any]]:
        """检测进化模式聚类"""
        # 按进化类型聚类
        type_clusters = defaultdict(list)
        for h in self.evolution_history:
            goal = h.get('current_goal', '')
            # 提取主要类型
            if '引擎' in goal or 'engine' in goal.lower():
                type_clusters['engine'].append(h)
            elif '智能' in goal:
                type_clusters['intelligent'].append(h)
            elif '自动' in goal:
                type_clusters['automation'].append(h)
            elif '优化' in goal or '增强' in goal:
                type_clusters['optimization'].append(h)
            else:
                type_clusters['other'].append(h)

        clusters = []
        for cluster_type, items in type_clusters.items():
            if len(items) >= 2:
                avg_score = sum(h.get('value_score', 50) for h in items) / len(items)
                clusters.append({
                    "type": cluster_type,
                    "count": len(items),
                    "average_score": avg_score,
                    "examples": [h.get('current_goal', '')[:50] for h in items[:3]]
                })

        return sorted(clusters, key=lambda x: x['count'], reverse=True)[:5]

    def _identify_high_value_rounds(self) -> List[Dict]:
        """识别高价值轮次"""
        high_value = [h for h in self.evolution_history if h.get('value_score', 0) >= 70]
        return [
            {
                "round": h.get('loop_round', 'N/A'),
                "goal": h.get('current_goal', '')[:60],
                "score": h.get('value_score', 0)
            }
            for h in sorted(high_value, key=lambda x: x.get('value_score', 0), reverse=True)[:5]
        ]

    def _identify_low_value_rounds(self) -> List[Dict]:
        """识别低价值轮次"""
        low_value = [h for h in self.evolution_history if h.get('value_score', 100) <= 30]
        return [
            {
                "round": h.get('loop_round', 'N/A'),
                "goal": h.get('current_goal', '')[:60],
                "score": h.get('value_score', 0)
            }
            for h in sorted(low_value, key=lambda x: x.get('value_score', 100))[:5]
        ]

    def _detect_repeated_improvements(self) -> List[Dict]:
        """检测重复改进"""
        # 基于目标文本相似度检测
        goals = [h.get('current_goal', '') for h in self.evolution_history]

        repeated = []
        seen = {}

        for i, goal in enumerate(goals):
            # 提取关键词
            keywords = []
            for kw in ['优化', '增强', '引擎', '智能', '自动', '自适应', '协同', '执行', '服务']:
                if kw in goal:
                    keywords.append(kw)

            key = tuple(sorted(keywords))
            if key in seen:
                if seen[key]['count'] >= 1:
                    repeated.append({
                        "keywords": list(key),
                        "rounds": seen[key]['rounds'] + [self.evolution_history[i].get('loop_round', i)],
                        "count": seen[key]['count'] + 1
                    })
                seen[key]['count'] += 1
                seen[key]['rounds'].append(self.evolution_history[i].get('loop_round', i))
            else:
                seen[key] = {
                    'count': 1,
                    'rounds': [self.evolution_history[i].get('loop_round', i)]
                }

        return sorted([r for r in repeated if r['count'] >= 2], key=lambda x: x['count'], reverse=True)[:5]

    def _evaluate_strategy_effectiveness(self) -> Dict[str, float]:
        """评估策略有效性"""
        if not self.evolution_history:
            return {}

        weights = self.strategy_config.get('strategy_weights', {})

        # 根据历史数据评估各策略权重效果
        effectiveness = {}
        for strategy, weight in weights.items():
            # 简单估算：高分轮次的权重倾向
            high_score_rounds = [h for h in self.evolution_history if h.get('value_score', 50) >= 60]
            effectiveness[strategy] = weight * (len(high_score_rounds) / len(self.evolution_history) if self.evolution_history else 0)

        return effectiveness

    def optimize_strategy(self) -> Dict[str, Any]:
        """优化进化策略"""
        analysis = self.analyze_history()

        if analysis.get('status') == 'no_data':
            return {
                "status": "error",
                "message": "暂无足够数据用于策略优化"
            }

        # 基于分析结果生成优化建议
        optimized_weights = dict(self.strategy_config.get('strategy_weights', {}))

        # 根据效率趋势调整
        efficiency = analysis.get('efficiency_trends', {})
        if efficiency.get('trend') == 'declining':
            # 效率下降时，增加稳定性权重
            optimized_weights['stability'] = min(0.35, optimized_weights.get('stability', 0.2) + 0.1)
            optimized_weights['efficiency'] = max(0.15, optimized_weights.get('efficiency', 0.25) - 0.1)
        elif efficiency.get('trend') == 'improving':
            # 效率上升时，增加创新权重
            optimized_weights['innovation'] = min(0.45, optimized_weights.get('innovation', 0.3) + 0.1)

        # 根据重复改进检测调整
        repeated = analysis.get('repeated_improvements', [])
        if len(repeated) > 3:
            # 重复过多时，增加用户需求权重
            optimized_weights['user_need'] = min(0.4, optimized_weights.get('user_need', 0.25) + 0.1)
            optimized_weights['innovation'] = max(0.2, optimized_weights.get('innovation', 0.3) - 0.1)

        # 根据模式聚类调整
        clusters = analysis.get('pattern_clusters', [])
        if clusters and clusters[0].get('count', 0) > 10:
            # 某种类型过多时，平衡其他类型
            optimized_weights['innovation'] = max(0.25, optimized_weights.get('innovation', 0.3) - 0.05)

        return {
            "original_weights": self.strategy_config.get('strategy_weights', {}),
            "optimized_weights": optimized_weights,
            "adjustments": [
                f"{k}: {self.strategy_config.get('strategy_weights', {}).get(k, 0)} -> {v}"
                for k, v in optimized_weights.items()
                if self.strategy_config.get('strategy_weights', {}).get(k, 0) != v
            ],
            "reasoning": self._generate_optimization_reasoning(analysis)
        }

    def _generate_optimization_reasoning(self, analysis: Dict) -> List[str]:
        """生成优化推理"""
        reasoning = []

        efficiency = analysis.get('efficiency_trends', {})
        if efficiency.get('trend') == 'declining':
            reasoning.append("检测到进化效率下降趋势，增加了稳定性权重以确保进化质量")
        elif efficiency.get('trend') == 'improving':
            reasoning.append("检测到进化效率上升趋势，增加了创新权重以加速进化")

        repeated = analysis.get('repeated_improvements', [])
        if len(repeated) > 3:
            reasoning.append(f"检测到{len(repeated)}组重复改进，增加了用户需求权重以推动更有价值的进化")

        clusters = analysis.get('pattern_clusters', [])
        if clusters and clusters[0].get('count', 0) > 10:
            reasoning.append(f"检测到主导模式类型（{clusters[0].get('type', 'N/A')}），调整权重以平衡进化方向")

        if not reasoning:
            reasoning.append("当前策略配置已较为均衡，保持现有权重")

        return reasoning

    def recommend_best_path(self) -> Dict[str, Any]:
        """推荐最佳进化路径"""
        analysis = self.analyze_history()

        if analysis.get('status') == 'no_data':
            return {
                "status": "error",
                "message": "暂无足够数据用于路径推荐"
            }

        # 基于模式聚类和效率趋势生成推荐
        clusters = analysis.get('pattern_clusters', [])
        high_value = analysis.get('high_value_rounds', [])
        low_value = analysis.get('low_value_rounds', [])

        # 推荐路径
        recommended_paths = []

        # 路径1: 创新驱动
        if clusters:
            innovation_types = [c for c in clusters if c['type'] in ['intelligent', 'automation']]
            if innovation_types:
                recommended_paths.append({
                    "path": "innovation_driven",
                    "description": "聚焦智能化和自动化创新",
                    "priority": "高",
                    "expected_impact": "可能带来显著能力提升"
                })

        # 路径2: 稳定性优先
        if low_value:
            recommended_paths.append({
                "path": "stability_focused",
                "description": "修复低价值轮次发现的问题",
                "priority": "中",
                "expected_impact": "提升整体进化质量"
            })

        # 路径3: 用户需求驱动
        recommended_paths.append({
            "path": "user_need_driven",
            "description": "基于用户实际需求驱动进化",
            "priority": "高",
            "expected_impact": "确保进化方向与用户需求一致"
        })

        # 路径4: 效率优化
        recommended_paths.append({
            "path": "efficiency_optimized",
            "description": "优化进化流程，减少重复工作",
            "priority": "中",
            "expected_impact": "提升进化效率"
        })

        return {
            "recommended_paths": recommended_paths,
            "primary_recommendation": recommended_paths[0] if recommended_paths else None,
            "reasoning": self._generate_path_reasoning(analysis, clusters, high_value)
        }

    def _generate_path_reasoning(self, analysis: Dict, clusters: List, high_value: List) -> List[str]:
        """生成路径推荐推理"""
        reasoning = []

        if high_value:
            top_round = high_value[0]
            reasoning.append(f"高价值轮次 #{top_round.get('round', 'N/A')} 展示了良好方向：{top_round.get('goal', '')[:40]}")

        if clusters:
            top_cluster = clusters[0]
            reasoning.append(f"当前最常见的进化类型是 {top_cluster.get('type', 'N/A')} ({top_cluster.get('count', 0)}轮)")

        efficiency = analysis.get('efficiency_trends', {})
        if efficiency.get('trend') == 'improving':
            reasoning.append("进化效率正在提升，建议保持当前方向并适度创新")

        return reasoning

    def predict_strategy_effect(self, strategy_type: str) -> Dict[str, Any]:
        """预测策略效果"""
        analysis = self.analyze_history()

        if analysis.get('status') == 'no_data':
            return {"status": "error", "message": "暂无足够数据"}

        # 基于历史数据预测
        predictions = {
            "innovation_driven": {
                "expected_score_range": (55, 75),
                "risk_level": "中",
                "potential_benefit": "高",
                "rationale": "创新驱动的进化往往能带来突破性进展，但风险较高"
            },
            "stability_focused": {
                "expected_score_range": (45, 65),
                "risk_level": "低",
                "potential_benefit": "中",
                "rationale": "稳定性优化可以确保系统质量，但可能缺乏突破"
            },
            "user_need_driven": {
                "expected_score_range": (60, 80),
                "risk_level": "低",
                "potential_benefit": "高",
                "rationale": "用户需求驱动的进化通常价值较高"
            },
            "efficiency_optimized": {
                "expected_score_range": (50, 70),
                "risk_level": "低",
                "potential_benefit": "中",
                "rationale": "效率优化可以提升进化效率"
            }
        }

        return predictions.get(strategy_type, {
            "expected_score_range": (40, 60),
            "risk_level": "中",
            "potential_benefit": "中",
            "rationale": "通用策略"
        })

    def get_status(self) -> Dict[str, Any]:
        """获取优化器状态"""
        return {
            "name": self.name,
            "version": self.version,
            "history_rounds": len(self.evolution_history),
            "current_strategy_weights": self.strategy_config.get('strategy_weights', {}),
            "optimization_interval": self.strategy_config.get('optimization_interval', 10)
        }


def main():
    """主函数 - 支持命令行调用"""
    import argparse

    parser = argparse.ArgumentParser(description='智能进化策略自适应优化引擎')
    parser.add_argument('command', nargs='?', default='status',
                        choices=['status', 'analyze', 'optimize', 'recommend', 'predict'],
                        help='要执行的命令')
    parser.add_argument('--strategy', type=str, default='innovation_driven',
                        help='策略类型 (用于 predict 命令)')

    args = parser.parse_args()

    optimizer = EvolutionStrategyOptimizer()

    if args.command == 'status':
        result = optimizer.get_status()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == 'analyze':
        result = optimizer.analyze_history()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == 'optimize':
        result = optimizer.optimize_strategy()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == 'recommend':
        result = optimizer.recommend_best_path()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == 'predict':
        result = optimizer.predict_strategy_effect(args.strategy)
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()