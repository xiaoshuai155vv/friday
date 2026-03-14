#!/usr/bin/env python3
"""
智能全场景进化价值实现追踪与闭环优化引擎 (Evolution Value Tracking Loop Engine)

让系统能够追踪每轮进化的实际价值实现过程，量化进化对系统能力的真实提升，
将价值反馈到进化决策过程中，形成价值驱动的进化优化闭环。

这是进化环的"价值层面"优化器——追踪价值实现、评估价值贡献、
驱动进化决策、优化进化路径，与目标优化器（evolution_goal_optimizer_engine.py）
和执行优化器（evolution_loop_self_optimizer.py）形成完整的三维优化体系。

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


class EvolutionValueTrackingLoopEngine:
    """进化价值实现追踪与闭环优化引擎核心类"""

    def __init__(self):
        self.version = "1.0.0"
        self.name = "Evolution Value Tracking Loop Engine"
        self.capabilities = [
            "价值实现追踪",
            "价值量化评估",
            "价值驱动决策",
            "价值闭环优化",
            "价值趋势分析",
            "价值反馈学习"
        ]

    def track_value_implementation(self, evolution_round: int = None) -> Dict:
        """
        追踪进化价值实现情况

        Args:
            evolution_round: 指定轮次，默认追踪最近完成的轮次

        Returns:
            价值实现追踪结果
        """
        # 查找最近完成的进化轮次
        if evolution_round is None:
            evolution_round = self._get_latest_completed_round()

        if evolution_round is None:
            return {
                "status": "no_data",
                "message": "未找到已完成的进化轮次",
                "round": None
            }

        # 读取该轮次的完成状态文件
        completed_file = STATE_DIR / f"evolution_completed_ev_{self._get_round_timestamp(evolution_round)}.json"

        # 尝试查找任意匹配的文件
        if not completed_file.exists():
            # 查找最新的完成文件
            completed_files = sorted(STATE_DIR.glob("evolution_completed_*.json"), reverse=True)
            if completed_files:
                completed_file = completed_files[0]
            else:
                return {
                    "status": "no_data",
                    "message": "未找到进化完成记录",
                    "round": evolution_round
                }

        try:
            with open(completed_file, 'r', encoding='utf-8') as f:
                evolution_data = json.load(f)

            # 分析价值实现情况
            current_goal = evolution_data.get('current_goal', '')
            status = evolution_data.get('status', 'unknown')
            completed_at = evolution_data.get('completed_at', '')

            # 计算价值实现得分
            value_score = self._calculate_value_score(status, current_goal)

            return {
                "status": "success",
                "round": evolution_round,
                "current_goal": current_goal,
                "evolution_status": status,
                "completed_at": completed_at,
                "value_score": value_score,
                "value_factors": self._analyze_value_factors(current_goal, status)
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "round": evolution_round
            }

    def quantify_value_contribution(self, evolution_round: int = None) -> Dict:
        """
        量化进化对系统能力的真实提升

        Args:
            evolution_round: 指定轮次

        Returns:
            价值贡献量化结果
        """
        # 追踪多轮进化的价值
        recent_rounds = self._get_recent_rounds(10)  # 最近10轮

        if not recent_rounds:
            return {
                "status": "no_data",
                "message": "无足够的历史数据进行价值量化"
            }

        contributions = []
        total_value = 0.0

        for round_num in recent_rounds:
            # 获取每轮的价值实现情况
            round_value = self.track_value_implementation(round_num)
            if round_value.get('status') == 'success':
                score = round_value.get('value_score', 0.0)
                contributions.append({
                    "round": round_num,
                    "value_score": score,
                    "goal": round_value.get('current_goal', '')
                })
                total_value += score

        avg_value = total_value / len(contributions) if contributions else 0.0

        return {
            "status": "success",
            "recent_rounds": len(contributions),
            "average_value": round(avg_value, 2),
            "total_value_contribution": round(total_value, 2),
            "contributions": contributions,
            "analysis_time": datetime.now().isoformat()
        }

    def value_driven_decision(self, proposed_goals: List[str]) -> Dict:
        """
        价值驱动的进化决策 - 根据历史价值实现情况选择最佳进化方向

        Args:
            proposed_goals: 候选进化目标列表

        Returns:
            价值驱动的决策建议
        """
        if not proposed_goals:
            return {
                "status": "no_goals",
                "message": "无候选目标"
            }

        # 获取历史价值数据
        value_data = self.quantify_value_contribution()

        # 基于价值分析对候选目标进行评分
        scored_goals = []
        for goal in proposed_goals:
            # 分析目标与历史高价值进化的相关性
            relevance_score = self._calculate_goal_relevance(goal, value_data)

            # 评估目标的潜在价值
            potential_score = self._evaluate_potential_value(goal)

            # 综合得分
            combined_score = (relevance_score * 0.4 + potential_score * 0.6)

            scored_goals.append({
                "goal": goal,
                "relevance_score": round(relevance_score, 2),
                "potential_score": round(potential_score, 2),
                "combined_score": round(combined_score, 2)
            })

        # 按综合得分排序
        scored_goals.sort(key=lambda x: x['combined_score'], reverse=True)

        return {
            "status": "success",
            "recommended_goal": scored_goals[0]['goal'] if scored_goals else None,
            "recommendation_reason": self._generate_recommendation_reason(scored_goals[0] if scored_goals else None, value_data),
            "scored_goals": scored_goals,
            "decision_time": datetime.now().isoformat()
        }

    def value_based_loop_optimization(self) -> Dict:
        """
        基于价值实现效果的进化路径优化

        Returns:
            价值闭环优化建议
        """
        # 获取最近进化的价值实现数据
        value_data = self.quantify_value_contribution()

        if value_data.get('status') != 'success':
            return {
                "status": "insufficient_data",
                "message": "无足够数据用于优化"
            }

        # 分析价值趋势
        contributions = value_data.get('contributions', [])
        if len(contributions) < 3:
            return {
                "status": "insufficient_data",
                "message": "需要至少3轮进化数据才能进行优化"
            }

        # 计算趋势
        scores = [c['value_score'] for c in contributions]
        avg_score = sum(scores) / len(scores)

        # 识别高价值模式
        high_value_rounds = [c for c in contributions if c['value_score'] >= avg_score]
        low_value_rounds = [c for c in contributions if c['value_score'] < avg_score]

        # 生成优化建议
        optimization_suggestions = []

        if len(high_value_rounds) >= 2:
            high_value_goals = [c['goal'] for c in high_value_rounds]
            optimization_suggestions.append({
                "type": "reinforce_success",
                "description": "强化成功模式",
                "details": f"历史高价值进化({len(high_value_rounds)}轮)具有共同特点，建议在相似方向继续深化",
                "related_goals": high_value_goals[:3]
            })

        if len(low_value_rounds) >= 1:
            low_value_goals = [c['goal'] for c in low_value_rounds]
            optimization_suggestions.append({
                "type": "avoid_failure",
                "description": "规避低效模式",
                "details": f"识别到{len(low_value_rounds)}轮低价值进化，建议避免类似方向",
                "related_goals": low_value_goals[:2]
            })

        # 添加整体优化建议
        optimization_suggestions.append({
            "type": "overall_strategy",
            "description": "整体优化策略",
            "details": f"基于{len(contributions)}轮进化分析，平均价值得分{avg_score:.2f}，建议{'聚焦高价值方向' if avg_score > 0.7 else '探索新的价值增长点'}",
            "average_score": round(avg_score, 2)
        })

        return {
            "status": "success",
            "optimization_suggestions": optimization_suggestions,
            "analysis_summary": {
                "total_rounds_analyzed": len(contributions),
                "average_value": round(avg_score, 2),
                "high_value_count": len(high_value_rounds),
                "low_value_count": len(low_value_rounds)
            },
            "optimization_time": datetime.now().isoformat()
        }

    def analyze_value_trends(self, time_range: int = 30) -> Dict:
        """
        分析进化价值趋势

        Args:
            time_range: 分析的时间范围（天数）

        Returns:
            价值趋势分析结果
        """
        # 获取指定时间范围内的进化数据
        value_data = self.quantify_value_contribution()

        if value_data.get('status') != 'success':
            return {
                "status": "no_data",
                "message": "无足够数据用于趋势分析"
            }

        contributions = value_data.get('contributions', [])

        if len(contributions) < 2:
            return {
                "status": "insufficient_data",
                "message": "需要至少2轮进化数据才能分析趋势"
            }

        # 计算趋势方向
        scores = [c['value_score'] for c in contributions]

        # 简单的线性趋势判断
        if len(scores) >= 3:
            first_half_avg = sum(scores[:len(scores)//2]) / (len(scores)//2)
            second_half_avg = sum(scores[len(scores)//2:]) / (len(scores) - len(scores)//2)

            if second_half_avg > first_half_avg + 0.1:
                trend = "improving"
                trend_description = "进化价值实现呈上升趋势"
            elif second_half_avg < first_half_avg - 0.1:
                trend = "declining"
                trend_description = "进化价值实现呈下降趋势，需要关注"
            else:
                trend = "stable"
                trend_description = "进化价值实现保持稳定"
        else:
            trend = "insufficient_data"
            trend_description = "数据不足，无法准确判断趋势"

        return {
            "status": "success",
            "trend": trend,
            "trend_description": trend_description,
            "scores": scores,
            "analysis_time": datetime.now().isoformat()
        }

    def _get_latest_completed_round(self) -> Optional[int]:
        """获取最近完成的进化轮次"""
        try:
            # 读取 current_mission 获取当前轮次
            mission_file = STATE_DIR / "current_mission.json"
            if mission_file.exists():
                with open(mission_file, 'r', encoding='utf-8') as f:
                    mission = json.load(f)
                    return mission.get('loop_round', 322) - 1  # 返回上一轮
        except Exception:
            pass
        return 322  # 默认返回 322

    def _get_round_timestamp(self, round_num: int) -> str:
        """获取轮次对应的时间戳（简化实现）"""
        # 简化：使用日期格式
        return f"20260314_{str(round_num).zfill(5)}"

    def _calculate_value_score(self, status: str, goal: str) -> float:
        """计算价值实现得分"""
        base_score = 0.5

        # 基于状态调整
        if status == 'completed' or status == '已完成':
            base_score += 0.3
        elif status == 'partial':
            base_score += 0.1

        # 基于目标复杂度调整
        if any(kw in goal for kw in ['深度集成', '全面', '完整闭环', '统一']):
            base_score += 0.15

        # 标准化到 0-1 范围
        return min(1.0, max(0.0, base_score))

    def _analyze_value_factors(self, goal: str, status: str) -> List[str]:
        """分析影响价值的因素"""
        factors = []

        if '集成' in goal or '融合' in goal:
            factors.append("涉及多组件协同，集成复杂度高")
        if '自动化' in goal:
            factors.append("自动化程度高，长期价值大")
        if '优化' in goal:
            factors.append("直接提升系统效率")
        if '智能' in goal:
            factors.append("增强系统智能水平")

        if status == 'completed':
            factors.append("已成功完成实现")

        return factors[:3]  # 最多返回3个因素

    def _get_recent_rounds(self, count: int) -> List[int]:
        """获取最近N轮进化"""
        # 简化实现：从 current_mission 获取当前轮次，倒推
        current_round = self._get_latest_completed_round()
        return list(range(max(1, current_round - count + 1), current_round + 1))

    def _calculate_goal_relevance(self, goal: str, value_data: Dict) -> float:
        """计算目标与历史高价值进化的相关性"""
        if value_data.get('status') != 'success':
            return 0.5

        contributions = value_data.get('contributions', [])
        if not contributions:
            return 0.5

        # 获取高价值进化的关键词
        high_value_keywords = set()
        for c in contributions:
            if c.get('value_score', 0) >= 0.7:
                goal_text = c.get('goal', '')
                # 提取关键词（简化：取前5个字）
                for i in range(0, len(goal_text), 5):
                    high_value_keywords.add(goal_text[i:i+5])

        # 计算相关度
        goal_keywords = set(goal[i:i+5] for i in range(0, min(len(goal), 25), 5))
        intersection = high_value_keywords & goal_keywords
        relevance = len(intersection) / max(1, len(goal_keywords))

        return min(1.0, relevance + 0.3)  # 基础分数 0.3

    def _evaluate_potential_value(self, goal: str) -> float:
        """评估目标的潜在价值"""
        potential = 0.5

        # 评估目标的创新性
        innovation_keywords = ['新', '创造', '创新', '首次', '突破']
        if any(kw in goal for kw in innovation_keywords):
            potential += 0.2

        # 评估目标的综合性
        integration_keywords = ['集成', '融合', '协同', '统一', '闭环']
        if any(kw in goal for kw in integration_keywords):
            potential += 0.15

        # 评估目标的自主性
        autonomy_keywords = ['自主', '自动', '自我', '自适应']
        if any(kw in goal for kw in autonomy_keywords):
            potential += 0.15

        return min(1.0, potential)

    def _generate_recommendation_reason(self, top_goal: Dict, value_data: Dict) -> str:
        """生成推荐理由"""
        if not top_goal:
            return "无足够数据生成推荐"

        avg_value = value_data.get('average_value', 0.5)
        combined = top_goal.get('combined_score', 0)

        if combined >= 0.8:
            return f"该目标综合得分{combined:.2f}，高于历史平均({avg_value:.2f})，具有高价值实现潜力"
        elif combined >= 0.6:
            return f"该目标综合得分{combined:.2f}，接近历史平均，具备一定价值实现可能"
        else:
            return f"该目标综合得分{combined:.2f}，建议进一步评估其价值实现路径"

    def get_status(self) -> Dict:
        """获取引擎状态"""
        return {
            "name": self.name,
            "version": self.version,
            "capabilities": self.capabilities,
            "status": "active",
            "timestamp": datetime.now().isoformat()
        }

    def get_dashboard(self) -> Dict:
        """获取价值追踪仪表盘"""
        tracking = self.track_value_implementation()
        quantification = self.quantify_value_contribution()
        trends = self.analyze_value_trends()
        optimization = self.value_based_loop_optimization()

        return {
            "engine": self.name,
            "version": self.version,
            "latest_tracking": tracking,
            "quantification": quantification,
            "trends": trends,
            "optimization": optimization,
            "timestamp": datetime.now().isoformat()
        }


def main():
    """主函数 - 支持命令行调用"""
    import argparse

    parser = argparse.ArgumentParser(description='进化价值追踪与闭环优化引擎')
    parser.add_argument('--status', action='store_true', help='获取引擎状态')
    parser.add_argument('--dashboard', action='store_true', help='获取价值追踪仪表盘')
    parser.add_argument('--track', type=int, nargs='?', const=None, help='追踪指定轮次（默认最近）')
    parser.add_argument('--quantify', action='store_true', help='量化价值贡献')
    parser.add_argument('--decision', type=str, nargs='*', help='价值驱动的决策（候选目标）')
    parser.add_argument('--optimize', action='store_true', help='基于价值的闭环优化')
    parser.add_argument('--trends', action='store_true', help='分析价值趋势')

    args = parser.parse_args()

    engine = EvolutionValueTrackingLoopEngine()

    if args.status:
        result = engine.get_status()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.dashboard:
        result = engine.get_dashboard()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.track is not None:
        result = engine.track_value_implementation(args.track)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.quantify:
        result = engine.quantify_value_contribution()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.decision:
        result = engine.value_driven_decision(args.decision)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.optimize:
        result = engine.value_based_loop_optimization()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.trends:
        result = engine.analyze_value_trends()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        # 默认显示仪表盘
        result = engine.get_dashboard()
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()