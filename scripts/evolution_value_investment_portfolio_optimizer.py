#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环元进化价值投资组合优化与风险对冲引擎
version 1.0.0

在 round 560 完成的元进化价值预测与预防性优化引擎基础上，构建价值投资组合优化能力。
让系统能够基于价值预测结果，智能分配进化投资、优化组合策略、构建风险对冲，
形成「预测→投资决策→组合优化→风险对冲→价值实现」的完整价值投资闭环。

本轮新增：
1. 进化投资组合分析 - 分析多轮进化的价值贡献、风险敞口、资源分配
2. 智能投资分配 - 基于价值预测和风险评估，智能分配进化投资比例
3. 组合策略优化 - 动态调整投资组合，实现风险收益最优
4. 风险对冲策略 - 构建风险对冲机制，降低低价值投资风险
5. 与 round 560 价值预测引擎深度集成
6. 驾驶舱数据接口

Version: 1.0.0
Round: 561
"""

import os
import json
import sqlite3
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import math

# 解决 Windows 控制台编码问题
import sys
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# 路径配置
SCRIPT_DIR = Path(__file__).parent
RUNTIME_STATE_DIR = SCRIPT_DIR.parent / "runtime" / "state"
DATA_DIR = SCRIPT_DIR.parent / "data"
EVOLUTION_DB = RUNTIME_STATE_DIR / "evolution_history.db"


class EvolutionValueInvestmentPortfolioOptimizer:
    """元进化价值投资组合优化与风险对冲引擎"""

    VERSION = "1.0.0"
    ROUND = 561

    def __init__(self):
        """初始化引擎"""
        self.db_path = EVOLUTION_DB
        self.data_dir = DATA_DIR
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.portfolio_cache_file = self.data_dir / "investment_portfolio_cache.json"
        self.allocation_history_file = self.data_dir / "investment_allocation_history.json"
        self.hedge_strategy_file = self.data_dir / "risk_hedge_strategy.json"
        self.performance_history_file = self.data_dir / "portfolio_performance_history.json"

    def _get_connection(self):
        """获取数据库连接"""
        return sqlite3.connect(str(self.db_path))

    def _load_portfolio_cache(self) -> Dict:
        """加载投资组合缓存"""
        if self.portfolio_cache_file.exists():
            try:
                with open(self.portfolio_cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def _save_portfolio_cache(self, data: Dict):
        """保存投资组合缓存"""
        with open(self.portfolio_cache_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _load_allocation_history(self) -> List[Dict]:
        """加载投资分配历史"""
        if self.allocation_history_file.exists():
            try:
                with open(self.allocation_history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return []

    def _save_allocation_history(self, history: List[Dict]):
        """保存投资分配历史"""
        with open(self.allocation_history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

    def _load_hedge_strategy(self) -> Dict:
        """加载风险对冲策略"""
        if self.hedge_strategy_file.exists():
            try:
                with open(self.hedge_strategy_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def _save_hedge_strategy(self, strategy: Dict):
        """保存风险对冲策略"""
        with open(self.hedge_strategy_file, 'w', encoding='utf-8') as f:
            json.dump(strategy, f, ensure_ascii=False, indent=2)

    def _load_performance_history(self) -> List[Dict]:
        """加载组合绩效历史"""
        if self.performance_history_file.exists():
            try:
                with open(self.performance_history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return []

    def _save_performance_history(self, history: List[Dict]):
        """保存组合绩效历史"""
        with open(self.performance_history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

    def _collect_evolution_data(self, rounds: int = 30) -> List[Dict]:
        """收集进化历史数据"""
        evolution_data = []

        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # 从进化历史表获取数据
            cursor.execute("""
                SELECT round_num, goal, status, efficiency_gain,
                       quality_improvement, innovation_enhancement, timestamp
                FROM evolution_history
                ORDER BY round_num DESC
                LIMIT ?
            """, (rounds,))

            rows = cursor.fetchall()
            for row in rows:
                evolution_data.append({
                    'round_num': row[0],
                    'goal': row[1],
                    'status': row[2],
                    'efficiency_gain': row[3] or 0.0,
                    'quality_improvement': row[4] or 0.0,
                    'innovation_enhancement': row[5] or 0.0,
                    'timestamp': row[6]
                })

            conn.close()
        except Exception as e:
            print(f"收集进化历史数据失败: {e}")

        return evolution_data

    def _collect_value_prediction_data(self, rounds: int = 20) -> List[Dict]:
        """收集价值预测数据（从 round 560 的预测缓存）"""
        prediction_data = []

        try:
            # 尝试从 round 560 的预测缓存读取
            prediction_cache = SCRIPT_DIR.parent / "data" / "meta_value_prediction_cache.json"
            if prediction_cache.exists():
                with open(prediction_cache, 'r', encoding='utf-8') as f:
                    cache = json.load(f)
                    if 'predictions' in cache:
                        prediction_data = cache['predictions']
        except Exception as e:
            print(f"收集价值预测数据失败: {e}")

        return prediction_data

    def analyze_portfolio(self, rounds: int = 30) -> Dict:
        """
        分析进化投资组合

        Args:
            rounds: 分析的轮次数

        Returns:
            投资组合分析结果
        """
        evolution_data = self._collect_evolution_data(rounds)
        value_predictions = self._collect_value_prediction_data(20)

        if not evolution_data:
            return {
                'status': 'no_data',
                'message': '无足够进化历史数据进行分析',
                'analysis': {}
            }

        # 计算各维度的统计指标
        efficiency_scores = [e['efficiency_gain'] for e in evolution_data]
        quality_scores = [e['quality_improvement'] for e in evolution_data]
        innovation_scores = [e['innovation_enhancement'] for e in evolution_data]

        analysis = {
            'total_rounds_analyzed': len(evolution_data),
            'avg_efficiency': sum(efficiency_scores) / len(efficiency_scores) if efficiency_scores else 0,
            'avg_quality': sum(quality_scores) / len(quality_scores) if quality_scores else 0,
            'avg_innovation': sum(innovation_scores) / len(innovation_scores) if innovation_scores else 0,
            'max_efficiency': max(efficiency_scores) if efficiency_scores else 0,
            'max_quality': max(quality_scores) if quality_scores else 0,
            'max_innovation': max(innovation_scores) if innovation_scores else 0,
            'min_efficiency': min(efficiency_scores) if efficiency_scores else 0,
            'min_quality': min(quality_scores) if quality_scores else 0,
            'min_innovation': min(innovation_scores) if innovation_scores else 0,
            'efficiency_std': self._calculate_std(efficiency_scores),
            'quality_std': self._calculate_std(quality_scores),
            'innovation_std': self._calculate_std(innovation_scores),
            'risk_exposure': self._calculate_risk_exposure(evolution_data),
            'value_contribution': self._calculate_value_contribution(evolution_data),
            'prediction_count': len(value_predictions)
        }

        # 识别高效和低效进化模式
        high_performers = [e for e in evolution_data
                          if e['efficiency_gain'] > analysis['avg_efficiency']]
        low_performers = [e for e in evolution_data
                         if e['efficiency_gain'] < analysis['avg_efficiency'] * 0.5]

        analysis['high_performer_count'] = len(high_performers)
        analysis['low_performer_count'] = len(low_performers)
        analysis['success_rate'] = len(high_performers) / len(evolution_data) if evolution_data else 0

        result = {
            'status': 'success',
            'analysis': analysis,
            'high_performers': high_performers[:5],
            'low_performers': low_performers[:5],
            'timestamp': datetime.now().isoformat()
        }

        # 缓存结果
        self._save_portfolio_cache(result)

        return result

    def _calculate_std(self, values: List[float]) -> float:
        """计算标准差"""
        if not values:
            return 0.0
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return math.sqrt(variance)

    def _calculate_risk_exposure(self, evolution_data: List[Dict]) -> float:
        """计算风险敞口"""
        if not evolution_data:
            return 0.0

        # 基于效率波动和失败率计算风险
        efficiency_scores = [e['efficiency_gain'] for e in evolution_data]
        std = self._calculate_std(efficiency_scores)
        failed_count = sum(1 for e in evolution_data if e.get('status') == '未完成')
        failure_rate = failed_count / len(evolution_data)

        # 风险敞口 = 波动率 * 0.6 + 失败率 * 0.4
        risk_exposure = std * 0.6 + failure_rate * 40

        return min(100, risk_exposure)

    def _calculate_value_contribution(self, evolution_data: List[Dict]) -> Dict:
        """计算各维度的价值贡献"""
        if not evolution_data:
            return {'efficiency': 0, 'quality': 0, 'innovation': 0, 'overall': 0}

        total_value = sum(
            e['efficiency_gain'] + e['quality_improvement'] + e['innovation_enhancement']
            for e in evolution_data
        )

        efficiency_sum = sum(e['efficiency_gain'] for e in evolution_data)
        quality_sum = sum(e['quality_improvement'] for e in evolution_data)
        innovation_sum = sum(e['innovation_enhancement'] for e in evolution_data)

        return {
            'efficiency': (efficiency_sum / total_value * 100) if total_value > 0 else 0,
            'quality': (quality_sum / total_value * 100) if total_value > 0 else 0,
            'innovation': (innovation_sum / total_value * 100) if total_value > 0 else 0,
            'overall': total_value / len(evolution_data) if evolution_data else 0
        }

    def calculate_allocation(self, total_budget: float = 100.0, risk_tolerance: str = 'medium') -> Dict:
        """
        计算智能投资分配

        Args:
            total_budget: 总投资预算
            risk_tolerance: 风险承受能力 (low/medium/high)

        Returns:
            投资分配建议
        """
        # 基于风险承受能力调整分配策略
        risk_multipliers = {
            'low': {'efficiency': 0.5, 'quality': 0.35, 'innovation': 0.15},
            'medium': {'efficiency': 0.35, 'quality': 0.35, 'innovation': 0.30},
            'high': {'efficiency': 0.25, 'quality': 0.30, 'innovation': 0.45}
        }

        multipliers = risk_multipliers.get(risk_tolerance, risk_multipliers['medium'])

        # 获取最新分析结果
        portfolio_cache = self._load_portfolio_cache()
        if portfolio_cache.get('status') == 'success':
            analysis = portfolio_cache.get('analysis', {})
            value_contribution = analysis.get('value_contribution', {})

            # 基于历史价值贡献调整分配
            efficiency_weight = (value_contribution.get('efficiency', 33) / 100) * multipliers['efficiency']
            quality_weight = (value_contribution.get('quality', 33) / 100) * multipliers['quality']
            innovation_weight = (value_contribution.get('innovation', 33) / 100) * multipliers['innovation']

            # 归一化
            total_weight = efficiency_weight + quality_weight + innovation_weight
            if total_weight > 0:
                efficiency_weight /= total_weight
                quality_weight /= total_weight
                innovation_weight /= total_weight
        else:
            # 使用默认分配
            efficiency_weight = multipliers['efficiency']
            quality_weight = multipliers['quality']
            innovation_weight = multipliers['innovation']

        allocation = {
            'efficiency': {
                'percentage': round(efficiency_weight * 100, 1),
                'budget': round(total_budget * efficiency_weight, 2),
                'rationale': '基于历史效率提升表现分配资源'
            },
            'quality': {
                'percentage': round(quality_weight * 100, 1),
                'budget': round(total_budget * quality_weight, 2),
                'rationale': '基于质量改进贡献分配资源'
            },
            'innovation': {
                'percentage': round(innovation_weight * 100, 1),
                'budget': round(total_budget * innovation_weight, 2),
                'rationale': '基于创新能力提升潜力分配资源'
            },
            'risk_tolerance': risk_tolerance,
            'total_budget': total_budget
        }

        # 记录分配历史
        history = self._load_allocation_history()
        history.append({
            'timestamp': datetime.now().isoformat(),
            'allocation': allocation,
            'risk_tolerance': risk_tolerance
        })
        # 保留最近 50 条
        self._save_allocation_history(history[-50:])

        return allocation

    def optimize_portfolio_strategy(self, target_return: float = 10.0) -> Dict:
        """
        优化组合策略

        Args:
            target_return: 目标收益率

        Returns:
            优化后的策略建议
        """
        # 获取分析数据
        portfolio_cache = self._load_portfolio_cache()
        analysis = portfolio_cache.get('analysis', {})

        if not analysis:
            # 如果没有缓存，先进行分析
            self.analyze_portfolio()
            portfolio_cache = self._load_portfolio_cache()
            analysis = portfolio_cache.get('analysis', {})

        risk_exposure = analysis.get('risk_exposure', 50)
        success_rate = analysis.get('success_rate', 0.5)

        # 基于目标收益率和当前风险敞口生成优化策略
        if risk_exposure > 70:
            strategy_type = '保守'
            adjustments = [
                '降低高风险进化方向的投资比例',
                '增加稳定收益类进化的权重',
                '加强预防性优化投入'
            ]
        elif risk_exposure > 40:
            strategy_type = '平衡'
            adjustments = [
                '保持现有风险水平',
                '优化资源配置效率',
                '适度增加创新投入'
            ]
        else:
            strategy_type = '激进'
            adjustments = [
                '增加高回报进化方向的投资',
                '提高创新和探索类进化的比例',
                '接受更高的风险以换取更高收益'
            ]

        strategy = {
            'strategy_type': strategy_type,
            'current_risk_exposure': round(risk_exposure, 1),
            'success_rate': round(success_rate * 100, 1),
            'target_return': target_return,
            'adjustments': adjustments,
            'rebalance建议': self._generate_rebalance_advice(analysis),
            'timestamp': datetime.now().isoformat()
        }

        return strategy

    def _generate_rebalance_advice(self, analysis: Dict) -> List[str]:
        """生成再平衡建议"""
        advice = []

        efficiency = analysis.get('avg_efficiency', 0)
        quality = analysis.get('avg_quality', 0)
        innovation = analysis.get('avg_innovation', 0)

        if efficiency < 5:
            advice.append('效率提升不足，建议增加效率优化类进化的投入')
        if quality < 5:
            advice.append('质量改进有限，建议加强质量保障相关进化')
        if innovation < 3:
            advice.append('创新能力有待提升，建议增加创新探索类进化的比例')

        efficiency_std = analysis.get('efficiency_std', 0)
        if efficiency_std > 10:
            advice.append('效率波动较大，建议增加稳定性优化')

        success_rate = analysis.get('success_rate', 0)
        if success_rate < 0.5:
            advice.append('成功率偏低，建议加强预防性分析和优化')

        if not advice:
            advice.append('各项指标均衡，建议保持当前策略')

        return advice

    def generate_hedge_strategy(self, portfolio_value: float = 100.0) -> Dict:
        """
        生成风险对冲策略

        Args:
            portfolio_value: 投资组合价值

        Returns:
            风险对冲策略
        """
        # 获取当前风险敞口
        portfolio_cache = self._load_portfolio_cache()
        analysis = portfolio_cache.get('analysis', {})
        risk_exposure = analysis.get('risk_exposure', 50)

        # 基于风险敞口生成对冲策略
        if risk_exposure < 30:
            hedge_level = '低'
            strategies = [
                {'type': '多元化', 'action': '保持投资多元化分散风险', 'allocation': '10%'},
                {'type': '预防性', 'action': '维持适度预防性投入', 'allocation': '5%'}
            ]
        elif risk_exposure < 60:
            hedge_level = '中'
            strategies = [
                {'type': '多元化', 'action': '增加投资多元化降低单一风险', 'allocation': '20%'},
                {'type': '预防性', 'action': '增加预防性优化投入', 'allocation': '10%'},
                {'type': '保险', 'action': '预留应急资源应对突发问题', 'allocation': '5%'}
            ]
        else:
            hedge_level = '高'
            strategies = [
                {'type': '多元化', 'action': '大幅增加投资多元化', 'allocation': '30%'},
                {'type': '预防性', 'action': '大幅增加预防性投入', 'allocation': '20%'},
                {'type': '保险', 'action': '预留充足应急资源', 'allocation': '15%'},
                {'type': '止损', 'action': '设置风险止损线', 'allocation': '5%'}
            ]

        hedge_strategy = {
            'hedge_level': hedge_level,
            'current_risk_exposure': round(risk_exposure, 1),
            'portfolio_value': portfolio_value,
            'strategies': strategies,
            'total_hedge_allocation': sum(float(s['allocation'].replace('%', '')) for s in strategies),
            'timestamp': datetime.now().isoformat()
        }

        # 保存对冲策略
        self._save_hedge_strategy(hedge_strategy)

        return hedge_strategy

    def get_portfolio_performance(self, rounds: int = 10) -> Dict:
        """
        获取投资组合绩效

        Args:
            rounds: 评估的轮次数

        Returns:
            绩效评估结果
        """
        evolution_data = self._collect_evolution_data(rounds)

        if not evolution_data:
            return {
                'status': 'no_data',
                'message': '无足够数据进行绩效评估'
            }

        # 计算各项指标
        total_efficiency = sum(e['efficiency_gain'] for e in evolution_data)
        total_quality = sum(e['quality_improvement'] for e in evolution_data)
        total_innovation = sum(e['innovation_enhancement'] for e in evolution_data)
        completed_rounds = sum(1 for e in evolution_data if e.get('status') != '未完成')

        performance = {
            'rounds_evaluated': len(evolution_data),
            'completed_rounds': completed_rounds,
            'completion_rate': completed_rounds / len(evolution_data),
            'total_value_generated': total_efficiency + total_quality + total_innovation,
            'avg_value_per_round': (total_efficiency + total_quality + total_innovation) / len(evolution_data),
            'efficiency_contribution': total_efficiency,
            'quality_contribution': total_quality,
            'innovation_contribution': total_innovation,
            'avg_efficiency': total_efficiency / len(evolution_data),
            'avg_quality': total_quality / len(evolution_data),
            'avg_innovation': total_innovation / len(evolution_data),
            'timestamp': datetime.now().isoformat()
        }

        # 记录绩效历史
        history = self._load_performance_history()
        history.append(performance)
        self._save_performance_history(history[-50:])

        return {
            'status': 'success',
            'performance': performance
        }

    def get_cockpit_data(self) -> Dict:
        """获取驾驶舱数据"""
        # 收集所有关键数据
        portfolio = self._load_portfolio_cache()
        allocation_history = self._load_allocation_history()
        hedge_strategy = self._load_hedge_strategy()
        performance_history = self._load_performance_history()

        # 获取最新的分析结果
        latest_analysis = portfolio.get('analysis', {}) if portfolio.get('status') == 'success' else {}

        cockpit_data = {
            'engine': 'EvolutionValueInvestmentPortfolioOptimizer',
            'version': self.VERSION,
            'round': self.ROUND,
            'timestamp': datetime.now().isoformat(),
            'portfolio_analysis': latest_analysis,
            'current_allocation': allocation_history[-1] if allocation_history else None,
            'hedge_strategy': hedge_strategy,
            'recent_performance': performance_history[-5:] if performance_history else [],
            'key_metrics': {
                'risk_exposure': latest_analysis.get('risk_exposure', 0),
                'success_rate': latest_analysis.get('success_rate', 0) * 100,
                'avg_value_per_round': latest_analysis.get('value_contribution', {}).get('overall', 0)
            }
        }

        return cockpit_data

    def run_full_analysis(self) -> Dict:
        """运行完整分析"""
        # 1. 分析投资组合
        portfolio_result = self.analyze_portfolio()

        # 2. 计算投资分配
        allocation = self.calculate_allocation()

        # 3. 优化组合策略
        strategy = self.optimize_portfolio_strategy()

        # 4. 生成风险对冲策略
        hedge = self.generate_hedge_strategy()

        # 5. 获取绩效评估
        performance = self.get_portfolio_performance()

        return {
            'status': 'success',
            'portfolio_analysis': portfolio_result,
            'investment_allocation': allocation,
            'portfolio_strategy': strategy,
            'hedge_strategy': hedge,
            'performance': performance,
            'cockpit_data': self.get_cockpit_data(),
            'timestamp': datetime.now().isoformat()
        }


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(
        description='元进化价值投资组合优化与风险对冲引擎'
    )
    parser.add_argument('--analyze', action='store_true', help='分析投资组合')
    parser.add_argument('--allocation', action='store_true', help='计算投资分配')
    parser.add_argument('--optimize', action='store_true', help='优化组合策略')
    parser.add_argument('--hedge', action='store_true', help='生成风险对冲策略')
    parser.add_argument('--performance', action='store_true', help='获取绩效评估')
    parser.add_argument('--cockpit-data', action='store_true', help='获取驾驶舱数据')
    parser.add_argument('--full', action='store_true', help='运行完整分析')
    parser.add_argument('--status', action='store_true', help='显示引擎状态')
    parser.add_argument('--risk-tolerance', default='medium', choices=['low', 'medium', 'high'],
                       help='风险承受能力')
    parser.add_argument('--budget', type=float, default=100.0, help='总投资预算')

    args = parser.parse_args()

    engine = EvolutionValueInvestmentPortfolioOptimizer()

    if args.status:
        result = engine.get_cockpit_data()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.analyze:
        result = engine.analyze_portfolio()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.allocation:
        result = engine.calculate_allocation(args.budget, args.risk_tolerance)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.optimize:
        result = engine.optimize_portfolio_strategy()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.hedge:
        result = engine.generate_hedge_strategy(args.budget)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.performance:
        result = engine.get_portfolio_performance()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.cockpit_data:
        result = engine.get_cockpit_data()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.full:
        result = engine.run_full_analysis()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        # 默认显示状态
        result = engine.get_cockpit_data()
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()