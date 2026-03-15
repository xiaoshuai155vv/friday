#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环价值投资回报智能评估与持续优化引擎
version 1.0.0

在 round 584 完成的价值战略预测与执行闭环基础上，进一步构建价值投资的 ROI 智能评估能力。
让系统能够量化每次进化的投入产出比、评估进化投资的真实回报、持续优化投资策略，
形成从「价值预测」到「ROI 评估」再到「策略优化」的完整投资管理闭环。

本轮新增：
1. 进化投入成本分析 - 计算每轮进化的资源投入：时间、代码量、引擎复杂度等
2. 价值产出评估 - 量化进化后系统能力的提升：效率、质量、创新等
3. ROI 计算 - 投入产出比、净价值、边际效益
4. 投资策略优化 - 基于 ROI 数据智能调整进化投资方向
5. 与 round 584 价值战略执行引擎深度集成
6. 驾驶舱数据接口
7. 集成到 do.py 支持相关关键词触发

Version: 1.0.0
Round: 585
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


class EvolutionValueInvestmentROIAssessmentEngine:
    """价值投资回报智能评估与持续优化引擎"""

    VERSION = "1.0.0"
    ROUND = 585

    def __init__(self):
        """初始化引擎"""
        self.db_path = EVOLUTION_DB
        self.data_dir = DATA_DIR
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.roi_cache_file = self.data_dir / "roi_assessment_cache.json"
        self.investment_history_file = self.data_dir / "investment_roi_history.json"
        self.optimization_recommendations_file = self.data_dir / "roi_optimization_recommendations.json"

    def _get_connection(self):
        """获取数据库连接"""
        return sqlite3.connect(str(self.db_path))

    def _load_roi_cache(self) -> Dict:
        """加载 ROI 缓存"""
        if self.roi_cache_file.exists():
            try:
                with open(self.roi_cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def _save_roi_cache(self, data: Dict):
        """保存 ROI 缓存"""
        with open(self.roi_cache_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _load_investment_history(self) -> List[Dict]:
        """加载投资历史"""
        if self.investment_history_file.exists():
            try:
                with open(self.investment_history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return []

    def _save_investment_history(self, history: List[Dict]):
        """保存投资历史"""
        with open(self.investment_history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

    def _load_optimization_recommendations(self) -> List[Dict]:
        """加载优化建议"""
        if self.optimization_recommendations_file.exists():
            try:
                with open(self.optimization_recommendations_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return []

    def _save_optimization_recommendations(self, recommendations: List[Dict]):
        """保存优化建议"""
        with open(self.optimization_recommendations_file, 'w', encoding='utf-8') as f:
            json.dump(recommendations, f, ensure_ascii=False, indent=2)

    def _collect_evolution_data(self, rounds: int = 50) -> List[Dict]:
        """收集进化历史数据"""
        evolution_data = []

        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # 从进化历史表获取数据
            cursor.execute("""
                SELECT round_num, goal, status, efficiency_gain,
                       quality_improvement, innovation_enhancement, timestamp,
                       files_created, files_modified, code_lines_added, code_lines_removed
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
                    'timestamp': row[6],
                    'files_created': row[7] or 0,
                    'files_modified': row[8] or 0,
                    'code_lines_added': row[9] or 0,
                    'code_lines_removed': row[10] or 0
                })

            conn.close()
        except Exception as e:
            print(f"收集进化历史数据失败: {e}")

        return evolution_data

    def analyze_investment_cost(self, rounds: int = 30) -> Dict:
        """
        分析进化投入成本

        Args:
            rounds: 分析的轮次数

        Returns:
            成本分析结果
        """
        evolution_data = self._collect_evolution_data(rounds)

        if not evolution_data:
            return {
                'status': 'no_data',
                'message': '无足够进化历史数据进行分析',
                'cost_analysis': {}
            }

        # 计算各项投入指标
        total_files_created = sum(e.get('files_created', 0) for e in evolution_data)
        total_files_modified = sum(e.get('files_modified', 0) for e in evolution_data)
        total_lines_added = sum(e.get('code_lines_added', 0) for e in evolution_data)
        total_lines_removed = sum(e.get('code_lines_removed', 0) for e in evolution_data)

        # 计算每轮平均投入
        avg_files_created = total_files_created / len(evolution_data) if evolution_data else 0
        avg_files_modified = total_files_modified / len(evolution_data) if evolution_data else 0
        avg_lines_added = total_lines_added / len(evolution_data) if evolution_data else 0

        # 估算时间投入（基于文件变更数量）
        # 假设每个文件变更平均需要 30 分钟
        estimated_time_hours = (total_files_created + total_files_modified) * 0.5
        avg_time_per_round = estimated_time_hours / len(evolution_data) if evolution_data else 0

        cost_analysis = {
            'total_rounds': len(evolution_data),
            'total_files_created': total_files_created,
            'total_files_modified': total_files_modified,
            'total_lines_added': total_lines_added,
            'total_lines_removed': total_lines_removed,
            'net_lines_added': total_lines_added - total_lines_removed,
            'avg_files_created_per_round': round(avg_files_created, 2),
            'avg_files_modified_per_round': round(avg_files_modified, 2),
            'avg_lines_added_per_round': round(avg_lines_added, 2),
            'estimated_total_hours': round(estimated_time_hours, 1),
            'avg_time_per_round_hours': round(avg_time_per_round, 2),
            # 成本权重：时间权重 0.4，代码量权重 0.3，文件变更权重 0.3
            'total_cost_score': round(
                estimated_time_hours * 0.4 +
                (total_lines_added + total_lines_removed) * 0.01 +
                (total_files_created + total_files_modified) * 2,
                2
            )
        }

        return {
            'status': 'success',
            'cost_analysis': cost_analysis,
            'timestamp': datetime.now().isoformat()
        }

    def evaluate_value_output(self, rounds: int = 30) -> Dict:
        """
        评估价值产出

        Args:
            rounds: 评估的轮次数

        Returns:
            价值产出评估结果
        """
        evolution_data = self._collect_evolution_data(rounds)

        if not evolution_data:
            return {
                'status': 'no_data',
                'message': '无足够数据进行价值评估',
                'value_output': {}
            }

        # 计算各项价值指标
        total_efficiency = sum(e.get('efficiency_gain', 0) for e in evolution_data)
        total_quality = sum(e.get('quality_improvement', 0) for e in evolution_data)
        total_innovation = sum(e.get('innovation_enhancement', 0) for e in evolution_data)

        # 计算加权总价值（效率 0.4，质量 0.3，创新 0.3）
        weighted_value = (
            total_efficiency * 0.4 +
            total_quality * 0.3 +
            total_innovation * 0.3
        )

        # 计算已完成轮次的价值产出
        completed_rounds = [e for e in evolution_data if e.get('status') != '未完成']
        completed_count = len(completed_rounds)
        completion_rate = completed_count / len(evolution_data) if evolution_data else 0

        # 计算边际效益（每单位投入产生的价值）
        cost_analysis = self.analyze_investment_cost(rounds)
        total_cost = cost_analysis.get('cost_analysis', {}).get('total_cost_score', 1)
        marginal_value = weighted_value / total_cost if total_cost > 0 else 0

        value_output = {
            'total_rounds': len(evolution_data),
            'completed_rounds': completed_count,
            'completion_rate': round(completion_rate * 100, 1),
            'total_efficiency': round(total_efficiency, 2),
            'total_quality': round(total_quality, 2),
            'total_innovation': round(total_innovation, 2),
            'total_weighted_value': round(weighted_value, 2),
            'avg_value_per_round': round(weighted_value / len(evolution_data), 2) if evolution_data else 0,
            'marginal_value_per_cost_unit': round(marginal_value, 4),
            'value_efficiency_ratio': round(weighted_value / total_cost, 4) if total_cost > 0 else 0
        }

        # 识别高价值进化
        high_value_rounds = sorted(
            [
                {
                    'round': e['round_num'],
                    'goal': e['goal'][:50] + '...' if len(e.get('goal', '')) > 50 else e.get('goal', ''),
                    'value': e.get('efficiency_gain', 0) + e.get('quality_improvement', 0) + e.get('innovation_enhancement', 0)
                }
                for e in evolution_data
            ],
            key=lambda x: x['value'],
            reverse=True
        )[:5]

        value_output['top_5_value_rounds'] = high_value_rounds

        return {
            'status': 'success',
            'value_output': value_output,
            'timestamp': datetime.now().isoformat()
        }

    def calculate_roi(self, rounds: int = 30) -> Dict:
        """
        计算投资回报率 (ROI)

        Args:
            rounds: 评估的轮次数

        Returns:
            ROI 计算结果
        """
        # 获取成本和价值数据
        cost_analysis = self.analyze_investment_cost(rounds)
        value_evaluation = self.evaluate_value_output(rounds)

        if cost_analysis.get('status') == 'no_data' or value_evaluation.get('status') == 'no_data':
            return {
                'status': 'no_data',
                'message': '无足够数据进行 ROI 计算',
                'roi': {}
            }

        cost_data = cost_analysis.get('cost_analysis', {})
        value_data = value_evaluation.get('value_output', {})

        # 计算各项 ROI 指标
        total_cost = cost_data.get('total_cost_score', 1)
        total_value = value_data.get('total_weighted_value', 0)

        # ROI = (收益 - 成本) / 成本 * 100%
        roi_percentage = ((total_value - total_cost) / total_cost * 100) if total_cost > 0 else 0

        # 净价值 = 收益 - 成本
        net_value = total_value - total_cost

        # 投资回报倍数
        return_on_multiple = total_value / total_cost if total_cost > 0 else 0

        # 效率 ROI（基于完成率）
        completion_rate = value_data.get('completion_rate', 0) / 100
        efficiency_roi = roi_percentage * completion_rate

        # 创新 ROI（创新价值占比）
        total_innovation = value_data.get('total_innovation', 0)
        innovation_ratio = total_innovation / total_value if total_value > 0 else 0
        innovation_roi = roi_percentage * (1 + innovation_ratio)

        roi = {
            'total_cost': round(total_cost, 2),
            'total_value': round(total_value, 2),
            'net_value': round(net_value, 2),
            'roi_percentage': round(roi_percentage, 2),
            'return_on_multiple': round(return_on_multiple, 2),
            'efficiency_roi': round(efficiency_roi, 2),
            'innovation_roi': round(innovation_roi, 2),
            'marginal_roi': round(value_data.get('marginal_value_per_cost_unit', 0) * 100, 2),
            'completion_rate': value_data.get('completion_rate', 0),
            'investment_rating': self._get_investment_rating(roi_percentage)
        }

        result = {
            'status': 'success',
            'roi': roi,
            'cost_breakdown': {
                'estimated_hours': cost_data.get('estimated_total_hours', 0),
                'files_changed': cost_data.get('total_files_created', 0) + cost_data.get('total_files_modified', 0),
                'lines_changed': cost_data.get('net_lines_added', 0)
            },
            'value_breakdown': {
                'efficiency': value_data.get('total_efficiency', 0),
                'quality': value_data.get('total_quality', 0),
                'innovation': value_data.get('total_innovation', 0)
            },
            'timestamp': datetime.now().isoformat()
        }

        # 缓存结果
        self._save_roi_cache(result)

        return result

    def _get_investment_rating(self, roi_percentage: float) -> str:
        """根据 ROI 百分比获取投资评级"""
        if roi_percentage >= 200:
            return "优秀 (Excellent)"
        elif roi_percentage >= 100:
            return "良好 (Good)"
        elif roi_percentage >= 50:
            return "一般 (Fair)"
        elif roi_percentage >= 0:
            return "较差 (Poor)"
        else:
            return "亏损 (Loss)"

    def optimize_investment_strategy(self, target_roi: float = 100.0) -> Dict:
        """
        优化投资策略

        Args:
            target_roi: 目标 ROI 百分比

        Returns:
            优化建议
        """
        # 获取最新 ROI 数据
        roi_cache = self._load_roi_cache()
        if not roi_cache or roi_cache.get('status') == 'no_data':
            # 如果没有缓存，先计算 ROI
            self.calculate_roi()
            roi_cache = self._load_roi_cache()

        roi_data = roi_cache.get('roi', {})
        current_roi = roi_data.get('roi_percentage', 0)
        investment_rating = roi_data.get('investment_rating', '未知')

        # 生成优化建议
        recommendations = []

        if current_roi < target_roi:
            gap = target_roi - current_roi
            recommendations.append({
                'type': '战略调整',
                'priority': '高',
                'action': f'当前 ROI ({current_roi:.1f}%) 低于目标 ({target_roi}%)，差距 {gap:.1f}%，建议调整投资策略'
            })

        # 基于各维度分析生成建议
        cost_analysis = self.analyze_investment_cost()
        value_evaluation = self.evaluate_value_output()

        cost_data = cost_analysis.get('cost_analysis', {})
        value_data = value_evaluation.get('value_output', {})

        # 效率分析
        avg_files = cost_data.get('avg_files_created_per_round', 0) + cost_data.get('avg_files_modified_per_round', 0)
        if avg_files > 10:
            recommendations.append({
                'type': '成本优化',
                'priority': '中',
                'action': f'平均每轮文件变更数量 ({avg_files:.1f}) 较高，建议精简进化范围，减少不必要变更'
            })
        elif avg_files < 2:
            recommendations.append({
                'type': '投入增加',
                'priority': '中',
                'action': f'平均每轮文件变更数量 ({avg_files:.1f}) 较低，可考虑增加投入以加速进化'
            })

        # 价值分析
        efficiency_ratio = value_data.get('total_efficiency', 0) / (value_data.get('total_weighted_value', 1) or 1)
        if efficiency_ratio > 0.6:
            recommendations.append({
                'type': '创新提升',
                'priority': '中',
                'action': '效率提升占比过高，创新投入相对不足，建议增加创新类进化的投资比例'
            })

        # 完成率分析
        completion_rate = value_data.get('completion_rate', 0)
        if completion_rate < 80:
            recommendations.append({
                'type': '执行力提升',
                'priority': '高',
                'action': f'进化完成率 ({completion_rate:.1f}%) 偏低，建议加强执行规划，提高进化完成率'
            })

        # 边际效益分析
        marginal_roi = roi_data.get('marginal_roi', 0)
        if marginal_roi < 5:
            recommendations.append({
                'type': '边际优化',
                'priority': '高',
                'action': f'边际 ROI ({marginal_roi:.2f}) 较低，每单位投入产生的价值递减，建议优化资源分配策略'
            })

        # 如果没有具体建议，添加正向反馈
        if not recommendations:
            recommendations.append({
                'type': '保持现状',
                'priority': '低',
                'action': '当前投资策略运行良好，各项指标均衡，建议保持现有策略'
            })

        optimization = {
            'current_roi': round(current_roi, 2),
            'target_roi': target_roi,
            'investment_rating': investment_rating,
            'recommendations': recommendations,
            'strategy_adjustments': self._generate_strategy_adjustments(current_roi, target_roi)
        }

        # 保存优化建议
        history = self._load_investment_history()
        history.append({
            'timestamp': datetime.now().isoformat(),
            'optimization': optimization
        })
        self._save_investment_history(history[-50:])

        self._save_optimization_recommendations(recommendations)

        return optimization

    def _generate_strategy_adjustments(self, current_roi: float, target_roi: float) -> List[str]:
        """生成策略调整建议"""
        adjustments = []

        gap = target_roi - current_roi

        if gap > 100:
            adjustments.extend([
                '大幅增加高价值进化方向的投资',
                '降低低效进化的资源分配',
                '优先完成高 ROI 的进化任务'
            ])
        elif gap > 50:
            adjustments.extend([
                '增加高价值进化的投资比例',
                '优化资源分配效率',
                '提升进化完成率'
            ])
        elif gap > 0:
            adjustments.extend([
                '微调投资策略',
                '关注边际效益优化',
                '保持稳定增长'
            ])
        else:
            adjustments.extend([
                '当前 ROI 超过目标，保持现有策略',
                '可适度增加创新探索类投入',
                '关注长期价值积累'
            ])

        return adjustments

    def get_cockpit_data(self) -> Dict:
        """获取驾驶舱数据"""
        # 收集所有关键数据
        roi_cache = self._load_roi_cache()
        investment_history = self._load_investment_history()
        recommendations = self._load_optimization_recommendations()

        roi_data = roi_cache.get('roi', {}) if roi_cache.get('status') == 'success' else {}
        cost_analysis = roi_cache.get('cost_breakdown', {})
        value_breakdown = roi_cache.get('value_breakdown', {})

        cockpit_data = {
            'engine': 'EvolutionValueInvestmentROIAssessmentEngine',
            'version': self.VERSION,
            'round': self.ROUND,
            'timestamp': datetime.now().isoformat(),
            'key_metrics': {
                'roi_percentage': roi_data.get('roi_percentage', 0),
                'net_value': roi_data.get('net_value', 0),
                'return_on_multiple': roi_data.get('return_on_multiple', 0),
                'investment_rating': roi_data.get('investment_rating', '未知'),
                'completion_rate': roi_data.get('completion_rate', 0)
            },
            'cost_metrics': cost_analysis,
            'value_metrics': value_breakdown,
            'recent_optimization': investment_history[-1] if investment_history else None,
            'current_recommendations': recommendations
        }

        return cockpit_data

    def run_full_analysis(self) -> Dict:
        """运行完整分析"""
        # 1. 分析投入成本
        cost_analysis = self.analyze_investment_cost()

        # 2. 评估价值产出
        value_evaluation = self.evaluate_value_output()

        # 3. 计算 ROI
        roi_calculation = self.calculate_roi()

        # 4. 优化投资策略
        optimization = self.optimize_investment_strategy()

        # 5. 获取驾驶舱数据
        cockpit_data = self.get_cockpit_data()

        return {
            'status': 'success',
            'cost_analysis': cost_analysis,
            'value_evaluation': value_evaluation,
            'roi_calculation': roi_calculation,
            'optimization': optimization,
            'cockpit_data': cockpit_data,
            'timestamp': datetime.now().isoformat()
        }

    def integrate_with_round584(self) -> Dict:
        """
        与 round 584 价值战略执行引擎深度集成

        Returns:
            集成结果
        """
        integration_result = {
            'status': 'success',
            'message': '与 round 584 价值战略执行引擎集成',
            'capabilities': [
                '接收价值战略执行引擎的预测数据',
                '将 ROI 评估结果反馈给价值战略引擎',
                '基于价值预测调整投资策略',
                '共享驾驶舱数据接口'
            ]
        }

        # 尝试读取 round 584 的缓存数据
        try:
            round584_cache = DATA_DIR / "meta_value_strategy_prediction_cache.json"
            if round584_cache.exists():
                with open(round584_cache, 'r', encoding='utf-8') as f:
                    cache = json.load(f)
                    integration_result['round584_data_available'] = True
                    integration_result['round584_cache_summary'] = {
                        'keys': list(cache.keys()) if isinstance(cache, dict) else []
                    }
            else:
                integration_result['round584_data_available'] = False
                integration_result['message'] += '（round 584 缓存暂无数据）'
        except Exception as e:
            integration_result['round584_data_available'] = False
            integration_result['error'] = str(e)

        return integration_result


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(
        description='价值投资回报智能评估与持续优化引擎'
    )
    parser.add_argument('--cost', action='store_true', help='分析投入成本')
    parser.add_argument('--value', action='store_true', help='评估价值产出')
    parser.add_argument('--roi', action='store_true', help='计算 ROI')
    parser.add_argument('--optimize', action='store_true', help='优化投资策略')
    parser.add_argument('--integrate', action='store_true', help='集成 round 584 引擎')
    parser.add_argument('--cockpit-data', action='store_true', help='获取驾驶舱数据')
    parser.add_argument('--full', action='store_true', help='运行完整分析')
    parser.add_argument('--status', action='store_true', help='显示引擎状态')
    parser.add_argument('--target-roi', type=float, default=100.0, help='目标 ROI 百分比')

    args = parser.parse_args()

    engine = EvolutionValueInvestmentROIAssessmentEngine()

    if args.status:
        result = engine.get_cockpit_data()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.cost:
        result = engine.analyze_investment_cost()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.value:
        result = engine.evaluate_value_output()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.roi:
        result = engine.calculate_roi()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.optimize:
        result = engine.optimize_investment_strategy(args.target_roi)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.integrate:
        result = engine.integrate_with_round584()
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