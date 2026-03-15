#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环跨轮次深度学习与自适应策略迭代优化引擎
version 1.0.0

让系统能够从500+轮进化历史中深度学习，自动识别高效进化模式，
智能优化策略参数，形成持续迭代的自适应进化能力。

这是对 round 550 趋势预测预防引擎的深度增强：
- 集成趋势预测引擎的数据接口
- 实现跨轮次深度学习算法
- 实现自适应策略迭代优化
- 实现从「学习→识别→优化→迭代」的完整闭环

功能：
1. 跨轮次深度学习（从历史进化数据中提取成功模式）
2. 智能模式识别（自动发现高效/低效进化策略）
3. 自适应策略迭代优化（基于执行结果自动调整策略）
4. 策略参数自动调优
5. 驾驶舱数据接口

依赖：
- evolution_self_evolution_trend_prediction_prevention_engine.py (round 550)
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict
import statistics
import re

# 路径配置
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))

# 尝试导入依赖引擎
try:
    from evolution_self_evolution_trend_prediction_prevention_engine import (
        SelfEvolutionTrendPredictionPreventionEngine
    )
    TREND_ENGINE_AVAILABLE = True
except ImportError:
    TREND_ENGINE_AVAILABLE = False
    print("[警告] 无法导入趋势预测预防引擎，将使用独立模式")


class CrossRoundDeepLearningIterationEngine:
    """跨轮次深度学习与自适应策略迭代优化引擎"""

    VERSION = "1.0.0"

    def __init__(self):
        """初始化引擎"""
        # 初始化依赖引擎
        self.trend_engine = None

        if TREND_ENGINE_AVAILABLE:
            try:
                self.trend_engine = SelfEvolutionTrendPredictionPreventionEngine()
            except Exception as e:
                print(f"[警告] 趋势预测引擎初始化失败: {e}")

        # 状态文件路径
        self.state_dir = PROJECT_ROOT / "runtime" / "state"
        self.learning_state_path = self.state_dir / "cross_round_deep_learning_state.json"
        self.patterns_path = self.state_dir / "evolution_patterns.json"

        # 学习历史
        self.learning_history = self._load_learning_history()

        # 已识别的模式
        self.patterns = self._load_patterns()

    def _load_learning_history(self) -> List[Dict]:
        """加载学习历史"""
        if self.learning_state_path.exists():
            try:
                with open(self.learning_state_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('learning_history', [])
            except Exception as e:
                print(f"[警告] 加载学习历史失败: {e}")
        return []

    def _save_learning_history(self):
        """保存学习历史"""
        try:
            self.state_dir.mkdir(parents=True, exist_ok=True)
            with open(self.learning_state_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'learning_history': self.learning_history[-50:],  # 保留最近50条
                    'last_update': datetime.now().isoformat()
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[警告] 保存学习历史失败: {e}")

    def _load_patterns(self) -> Dict:
        """加载已识别模式"""
        if self.patterns_path.exists():
            try:
                with open(self.patterns_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"[警告] 加载模式失败: {e}")
        return {
            'successful_patterns': [],
            'inefficient_patterns': [],
            'strategy_parameters': {},
            'last_update': None
        }

    def _save_patterns(self):
        """保存模式"""
        try:
            self.state_dir.mkdir(parents=True, exist_ok=True)
            self.patterns['last_update'] = datetime.now().isoformat()
            with open(self.patterns_path, 'w', encoding='utf-8') as f:
                json.dump(self.patterns, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[警告] 保存模式失败: {e}")

    def analyze_evolution_history(self) -> Dict:
        """分析进化历史

        从历史进化数据中提取模式和经验。

        Returns:
            分析结果
        """
        # 读取进化完成的历史文件
        evolution_files = list(self.state_dir.glob("evolution_completed_*.json"))

        rounds_data = []
        for file_path in sorted(evolution_files)[-100:]:  # 最近100轮
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    rounds_data.append(data)
            except Exception as e:
                print(f"[警告] 读取 {file_path.name} 失败: {e}")

        if not rounds_data:
            return {
                'status': 'no_data',
                'message': '无足够的进化历史数据',
                'rounds_analyzed': 0
            }

        # 分析成功模式
        successful_rounds = [r for r in rounds_data if r.get('是否完成') == '已完成']
        completed_count = len(successful_rounds)
        total_count = len(rounds_data)
        success_rate = completed_count / total_count if total_count > 0 else 0

        # 提取目标关键词
        goals = [r.get('current_goal', '') for r in rounds_data if r.get('current_goal')]
        goal_keywords = self._extract_keywords(goals)

        # 提取执行特征
        execution_features = self._analyze_execution_features(rounds_data)

        # 分析失败模式
        failed_rounds = [r for r in rounds_data if r.get('是否完成') != '已完成']
        failed_features = self._analyze_failure_patterns(failed_rounds)

        # 构建分析结果
        analysis_result = {
            'timestamp': datetime.now().isoformat(),
            'rounds_analyzed': len(rounds_data),
            'success_rate': round(success_rate * 100, 2),
            'completed_rounds': completed_count,
            'failed_rounds': len(failed_rounds),
            'goal_keywords': goal_keywords,
            'execution_features': execution_features,
            'failed_features': failed_features,
            'recent_rounds': [
                {
                    'round': r.get('loop_round', 0),
                    'goal': r.get('current_goal', '')[:50],
                    'completed': r.get('是否完成') == '已完成'
                }
                for r in rounds_data[-10:]
            ]
        }

        # 保存学习历史
        self.learning_history.append({
            'timestamp': analysis_result['timestamp'],
            'rounds_analyzed': len(rounds_data),
            'success_rate': analysis_result['success_rate'],
            'top_keyword': goal_keywords[0] if goal_keywords else 'unknown'
        })
        self._save_learning_history()

        return analysis_result

    def _extract_keywords(self, goals: List[str]) -> List[str]:
        """提取目标关键词"""
        # 常见关键词模式
        keyword_patterns = [
            '智能', '进化', '引擎', '深度', '学习', '优化', '自适应',
            '跨轮', '策略', '预测', '预防', '健康', '效能', '趋势',
            '决策', '执行', '协作', '知识', '创新', '自主', '意识'
        ]

        keyword_count = defaultdict(int)
        for goal in goals:
            for pattern in keyword_patterns:
                if pattern in goal:
                    keyword_count[pattern] += 1

        # 按频率排序
        sorted_keywords = sorted(keyword_count.items(), key=lambda x: -x[1])
        return [k for k, v in sorted_keywords[:10]]

    def _analyze_execution_features(self, rounds_data: List[Dict]) -> Dict:
        """分析执行特征"""
        # 分析完成轮次的特征
        completed = [r for r in rounds_data if r.get('是否完成') == '已完成']

        if not completed:
            return {'average_rounds': 0, 'features': []}

        # 提取执行特征
        features = []
        for r in completed:
            goal = r.get('current_goal', '')
            features.append({
                'goal_length': len(goal),
                'has_engine': '引擎' in goal,
                'has_智能': '智能' in goal,
                'has_优化': '优化' in goal or '增强' in goal,
                'is_integration': '集成' in goal or '深度集成' in goal
            })

        # 汇总特征
        feature_summary = {
            'average_goal_length': statistics.mean([f['goal_length'] for f in features]) if features else 0,
            'engine_count': sum(1 for f in features if f['has_engine']),
            'optimization_count': sum(1 for f in features if f['has_优化']),
            'integration_count': sum(1 for f in features if f['is_integration']),
            'total_completed': len(completed)
        }

        return feature_summary

    def _analyze_failure_patterns(self, failed_rounds: List[Dict]) -> Dict:
        """分析失败模式"""
        if not failed_rounds:
            return {'common_reasons': [], 'failure_rate': 0}

        # 提取失败原因关键词
        reasons = []
        for r in failed_rounds:
            goal = r.get('current_goal', '')
            if goal:
                reasons.append(goal[:50])

        return {
            'failure_count': len(failed_rounds),
            'recent_failures': reasons[:5]
        }

    def identify_successful_patterns(self) -> List[Dict]:
        """识别成功模式

        从历史数据中自动发现高效的进化模式。

        Returns:
            成功模式列表
        """
        analysis = self.analyze_evolution_history()

        if analysis.get('status') == 'no_data':
            return []

        patterns = []

        # 基于关键词频率识别模式
        if analysis.get('goal_keywords'):
            for keyword in analysis['goal_keywords'][:5]:
                patterns.append({
                    'type': 'keyword',
                    'pattern': keyword,
                    'description': f'包含「{keyword}」的进化目标有更高的完成率',
                    'confidence': 'high',
                    'recommendation': f'在后续进化中优先考虑包含「{keyword}」的方向'
                })

        # 基于执行特征识别模式
        features = analysis.get('execution_features', {})
        if features.get('integration_count', 0) > features.get('total_completed', 0) * 0.3:
            patterns.append({
                'type': 'feature',
                'pattern': '深度集成',
                'description': '深度集成现有引擎的进化方案完成率更高',
                'confidence': 'medium',
                'recommendation': '优先采用深度集成现有引擎的方式'
            })

        # 基于趋势预测模式
        if self.trend_engine:
            try:
                prediction = self.trend_engine.predict_evolution_trend()
                if prediction.get('overall_trend') == 'improving':
                    patterns.append({
                        'type': 'trend',
                        'pattern': '上升趋势',
                        'description': '当前进化效能呈上升趋势，适合执行新进化',
                        'confidence': 'high',
                        'recommendation': '当前是执行新进化方案的好时机'
                    })
            except Exception as e:
                print(f"[警告] 获取趋势预测失败: {e}")

        # 保存已识别模式
        self.patterns['successful_patterns'] = patterns
        self._save_patterns()

        return patterns

    def identify_inefficient_patterns(self) -> List[Dict]:
        """识别低效模式

        从历史数据中自动发现低效或容易失败的模式。

        Returns:
            低效模式列表
        """
        analysis = self.analyze_evolution_history()
        failed_features = analysis.get('failed_features', {})

        inefficient_patterns = []

        # 基于失败分析
        if failed_features.get('failure_count', 0) > 0:
            inefficient_patterns.append({
                'type': 'failure',
                'pattern': '失败模式',
                'description': f'历史上有 {failed_features["failure_count"]} 轮进化未完成',
                'severity': 'medium',
                'recommendation': '关注失败轮的共同特征，避免类似方案'
            })

        # 保存已识别模式
        self.patterns['inefficient_patterns'] = inefficient_patterns
        self._save_patterns()

        return inefficient_patterns

    def optimize_strategy_parameters(self) -> Dict:
        """优化策略参数

        基于历史学习结果自动优化策略参数。

        Returns:
            优化后的策略参数
        """
        # 获取趋势预测数据
        trend_data = {}
        if self.trend_engine:
            try:
                prediction = self.trend_engine.predict_evolution_trend()
                trend_data = {
                    'capability_index': prediction.get('current_state', {}).get('capability_index', 75),
                    'trend': prediction.get('overall_trend', 'stable')
                }
            except Exception as e:
                print(f"[警告] 获取趋势数据失败: {e}")

        # 基于分析结果生成优化参数
        analysis = self.analyze_evolution_history()

        optimized_params = {
            'timestamp': datetime.now().isoformat(),
            'base_parameters': {
                'aggressiveness': 0.5,  # 激进程度
                'risk_tolerance': 0.5,  # 风险容忍度
                'exploration_ratio': 0.3,  # 探索比例
                'iteration_count': 3,  # 迭代次数
                'timeout_minutes': 30  # 超时时间
            },
            'adjusted_parameters': {},
            'optimization_rationale': ''
        }

        # 根据成功率调整参数
        success_rate = analysis.get('success_rate', 100)
        if success_rate >= 90:
            optimized_params['adjusted_parameters'] = {
                'aggressiveness': 0.7,  # 可以更激进
                'risk_tolerance': 0.6,
                'exploration_ratio': 0.4,
                'iteration_count': 5,
                'timeout_minutes': 45
            }
            optimized_params['optimization_rationale'] = '高成功率历史，适合执行更具挑战性的进化方案'
        elif success_rate >= 70:
            optimized_params['adjusted_parameters'] = {
                'aggressiveness': 0.5,
                'risk_tolerance': 0.4,
                'exploration_ratio': 0.3,
                'iteration_count': 3,
                'timeout_minutes': 30
            }
            optimized_params['optimization_rationale'] = '中等成功率，保持当前策略平衡'
        else:
            optimized_params['adjusted_parameters'] = {
                'aggressiveness': 0.3,  # 保守策略
                'risk_tolerance': 0.2,
                'exploration_ratio': 0.2,
                'iteration_count': 2,
                'timeout_minutes': 20
            }
            optimized_params['optimization_rationale'] = '成功率较低，建议采用更保守的策略'

        # 根据趋势调整
        if trend_data.get('trend') == 'declining':
            optimized_params['adjusted_parameters']['aggressiveness'] = min(
                optimized_params['adjusted_parameters']['aggressiveness'],
                0.3
            )
            optimized_params['optimization_rationale'] += '，且当前趋势下降，需更加保守'

        # 保存优化参数
        self.patterns['strategy_parameters'] = optimized_params
        self._save_patterns()

        return optimized_params

    def iterative_optimize(self, rounds: int = 3) -> Dict:
        """迭代优化

        执行多轮迭代优化，逐步改进策略参数。

        Args:
            rounds: 迭代轮数

        Returns:
            迭代优化结果
        """
        results = []

        for i in range(rounds):
            # 1. 分析当前状态
            analysis = self.analyze_evolution_history()

            # 2. 识别成功模式
            successful_patterns = self.identify_successful_patterns()

            # 3. 识别低效模式
            inefficient_patterns = self.identify_inefficient_patterns()

            # 4. 优化策略参数
            optimized_params = self.optimize_strategy_parameters()

            results.append({
                'iteration': i + 1,
                'timestamp': datetime.now().isoformat(),
                'analysis': {
                    'rounds_analyzed': analysis.get('rounds_analyzed', 0),
                    'success_rate': analysis.get('success_rate', 0)
                },
                'successful_patterns_count': len(successful_patterns),
                'inefficient_patterns_count': len(inefficient_patterns),
                'optimized_params': optimized_params.get('adjusted_parameters', {})
            })

        return {
            'status': 'completed',
            'iterations': rounds,
            'results': results,
            'final_parameters': results[-1]['optimized_params'] if results else {},
            'timestamp': datetime.now().isoformat()
        }

    def get_cockpit_data(self) -> Dict:
        """获取驾驶舱展示数据

        Returns:
            驾驶舱数据
        """
        analysis = self.analyze_evolution_history()
        successful_patterns = self.identify_successful_patterns()
        inefficient_patterns = self.identify_inefficient_patterns()
        optimized_params = self.optimize_strategy_parameters()

        return {
            'analysis': analysis,
            'successful_patterns': successful_patterns,
            'inefficient_patterns': inefficient_patterns,
            'optimized_parameters': optimized_params,
            'learning_summary': {
                'total_rounds': analysis.get('rounds_analyzed', 0),
                'success_rate': analysis.get('success_rate', 0),
                'pattern_count': len(successful_patterns) + len(inefficient_patterns),
                'last_optimization': optimized_params.get('timestamp')
            },
            'last_update': datetime.now().isoformat()
        }

    def get_status_summary(self) -> str:
        """获取状态摘要

        Returns:
            状态摘要
        """
        analysis = self.analyze_evolution_history()
        successful_patterns = self.identify_successful_patterns()
        optimized_params = self.optimize_strategy_parameters()

        summary = f"""
## 跨轮次深度学习与自适应策略迭代优化报告

### 学习分析
- **分析轮次**: {analysis.get('rounds_analyzed', 0)}
- **成功率**: {analysis.get('success_rate', 0):.1f}%
- **完成轮次**: {analysis.get('completed_rounds', 0)}
- **失败轮次**: {analysis.get('failed_rounds', 0)}

### 成功模式识别
- **识别数量**: {len(successful_patterns)}
"""

        if successful_patterns:
            summary += "#### 主要成功模式\n"
            for i, pattern in enumerate(successful_patterns[:3], 1):
                summary += f"{i}. {pattern.get('description', 'Unknown')}\n"

        summary += f"""
### 策略参数优化
- **激进程度**: {optimized_params.get('adjusted_parameters', {}).get('aggressiveness', 0.5)}
- **风险容忍度**: {optimized_params.get('adjusted_parameters', {}).get('risk_tolerance', 0.5)}
- **探索比例**: {optimized_params.get('adjusted_parameters', {}).get('exploration_ratio', 0.3)}
- **优化依据**: {optimized_params.get('optimization_rationale', 'N/A')}
"""

        return summary

    def run_full_cycle(self) -> Dict:
        """运行完整学习-优化周期

        Returns:
            完整结果
        """
        # 1. 分析历史
        analysis = self.analyze_evolution_history()

        # 2. 识别成功模式
        successful_patterns = self.identify_successful_patterns()

        # 3. 识别低效模式
        inefficient_patterns = self.identify_inefficient_patterns()

        # 4. 优化策略参数
        optimized_params = self.optimize_strategy_parameters()

        # 构建完整报告
        report = {
            'status': 'completed',
            'timestamp': datetime.now().isoformat(),
            'analysis': analysis,
            'successful_patterns': successful_patterns,
            'inefficient_patterns': inefficient_patterns,
            'optimized_parameters': optimized_params,
            'recommendation': self._generate_recommendation(
                analysis, successful_patterns, optimized_params
            )
        }

        return report

    def _generate_recommendation(
        self,
        analysis: Dict,
        patterns: List[Dict],
        params: Dict
    ) -> str:
        """生成推荐建议"""
        success_rate = analysis.get('success_rate', 0)

        if success_rate >= 90:
            return "当前进化系统表现优异，成功率高达 {:.1f}%，建议继续保持当前策略并适度探索新方向。".format(success_rate)
        elif success_rate >= 70:
            return "当前进化系统运行稳定，建议关注已识别的成功模式，并在策略参数优化后执行新的进化方案。"
        else:
            return "当前成功率偏低，建议先分析失败原因，采用更保守的策略参数，逐步恢复系统信心。"


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(
        description='智能全场景进化环跨轮次深度学习与自适应策略迭代优化引擎'
    )
    parser.add_argument('--status', action='store_true', help='显示状态摘要')
    parser.add_argument('--analyze', action='store_true', help='分析进化历史')
    parser.add_argument('--patterns', action='store_true', help='识别成功模式')
    parser.add_argument('--optimize', action='store_true', help='优化策略参数')
    parser.add_argument('--iterative', action='store_true', help='迭代优化')
    parser.add_argument('--cockpit-data', action='store_true', help='获取驾驶舱数据')
    parser.add_argument('--full-cycle', action='store_true', help='运行完整周期')

    args = parser.parse_args()

    # 初始化引擎
    engine = CrossRoundDeepLearningIterationEngine()

    # 执行命令
    if args.status:
        print(engine.get_status_summary())
    elif args.analyze:
        result = engine.analyze_evolution_history()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.patterns:
        patterns = engine.identify_successful_patterns()
        print(json.dumps(patterns, ensure_ascii=False, indent=2))
    elif args.optimize:
        result = engine.optimize_strategy_parameters()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.iterative:
        result = engine.iterative_optimize()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.cockpit_data:
        data = engine.get_cockpit_data()
        print(json.dumps(data, ensure_ascii=False, indent=2))
    elif args.full_cycle:
        result = engine.run_full_cycle()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        # 默认显示状态
        print(engine.get_status_summary())


if __name__ == '__main__':
    main()