#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环跨引擎知识蒸馏与自主优化引擎
version 1.0.0

功能：
1. 从70+引擎历史运行数据中提取成功模式
2. 实现核心知识结构化，形成可复用的进化智慧库
3. 实现自主优化决策，将蒸馏知识应用到进化方向选择中
4. 与进化驾驶舱深度集成，可视化知识蒸馏过程

作者：AI Evolution System
日期：2026-03-15
"""

import os
import json
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter
import hashlib
import subprocess
import sys

# 尝试导入相关引擎
try:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from evolution_value_emergence_closed_loop_engine import EvolutionValueEmergenceClosedLoopEngine
    CLOSED_LOOP_ENGINE_AVAILABLE = True
except ImportError:
    CLOSED_LOOP_ENGINE_AVAILABLE = False


class EvolutionKnowledgeDistillationEngine:
    """跨引擎知识蒸馏与自主优化引擎"""

    def __init__(self, base_path: str = None):
        self.base_path = base_path or os.path.dirname(os.path.abspath(__file__))
        self.runtime_path = os.path.join(os.path.dirname(self.base_path), 'runtime')
        self.state_path = os.path.join(self.runtime_path, 'state')
        self.logs_path = os.path.join(self.runtime_path, 'logs')

        # 初始化闭环引擎
        self.closed_loop_engine = None
        if CLOSED_LOOP_ENGINE_AVAILABLE:
            try:
                self.closed_loop_engine = EvolutionValueEmergenceClosedLoopEngine(self.base_path)
            except Exception:
                pass

        # 知识蒸馏数据
        self.engine_history = {}  # 引擎历史运行数据
        self.success_patterns = {}  # 成功模式
        self.wisdom_library = {}  # 进化智慧库
        self.optimization_decisions = []  # 优化决策记录

        # 蒸馏配置
        self.config = {
            'distillation_enabled': True,
            'pattern_min_samples': 3,
            'wisdom_update_interval': 10,  # 轮次
            'auto_optimization': True,
            'cross_engine_analysis': True,
            'similarity_threshold': 0.7,
        }

        # 加载已有数据
        self._load_data()

    def _load_data(self):
        """加载历史数据"""
        # 加载引擎历史
        history_file = os.path.join(self.state_path, 'evolution_engine_history.json')
        if os.path.exists(history_file):
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    self.engine_history = json.load(f)
            except Exception:
                pass

        # 加载成功模式
        patterns_file = os.path.join(self.state_path, 'evolution_success_patterns.json')
        if os.path.exists(patterns_file):
            try:
                with open(patterns_file, 'r', encoding='utf-8') as f:
                    self.success_patterns = json.load(f)
            except Exception:
                pass

        # 加载智慧库
        wisdom_file = os.path.join(self.state_path, 'evolution_wisdom_library.json')
        if os.path.exists(wisdom_file):
            try:
                with open(wisdom_file, 'r', encoding='utf-8') as f:
                    self.wisdom_library = json.load(f)
            except Exception:
                pass

    def _save_data(self):
        """保存数据到文件"""
        os.makedirs(self.state_path, exist_ok=True)

        # 保存引擎历史
        history_file = os.path.join(self.state_path, 'evolution_engine_history.json')
        try:
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(self.engine_history, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

        # 保存成功模式
        patterns_file = os.path.join(self.state_path, 'evolution_success_patterns.json')
        try:
            with open(patterns_file, 'w', encoding='utf-8') as f:
                json.dump(self.success_patterns, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

        # 保存智慧库
        wisdom_file = os.path.join(self.state_path, 'evolution_wisdom_library.json')
        try:
            with open(wisdom_file, 'w', encoding='utf-8') as f:
                json.dump(self.wisdom_library, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def initialize(self) -> Dict[str, Any]:
        """初始化引擎"""
        status = {
            'status': 'initialized',
            'timestamp': datetime.now().isoformat(),
            'engine_history_count': len(self.engine_history),
            'success_patterns_count': len(self.success_patterns),
            'wisdom_library_count': len(self.wisdom_library),
            'closed_loop_engine_loaded': self.closed_loop_engine is not None,
        }

        # 尝试初始化闭环引擎
        if self.closed_loop_engine:
            try:
                init_result = self.closed_loop_engine.initialize()
                status['closed_loop_init'] = init_result
            except Exception as e:
                status['closed_loop_error'] = str(e)

        return status

    def get_status(self) -> Dict[str, Any]:
        """获取引擎状态"""
        return {
            'initialized': True,
            'engine_history_count': len(self.engine_history),
            'success_patterns_count': len(self.success_patterns),
            'wisdom_library_count': len(self.wisdom_library),
            'optimization_decisions_count': len(self.optimization_decisions),
            'config': self.config,
            'closed_loop_engine_available': CLOSED_LOOP_ENGINE_AVAILABLE,
        }

    def collect_engine_history(self, round_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        收集引擎历史运行数据

        从进化环的运行数据中提取有价值的信息，包括：
        - 引擎执行结果
        - 执行效率
        - 价值实现情况
        - 决策质量
        """
        engine_name = round_data.get('engine_name', 'unknown')
        execution_result = round_data.get('execution_result', {})

        if engine_name not in self.engine_history:
            self.engine_history[engine_name] = {
                'rounds': [],
                'success_count': 0,
                'failure_count': 0,
                'total_rounds': 0,
                'first_seen': datetime.now().isoformat(),
            }

        history_entry = {
            'round': round_data.get('round', 0),
            'timestamp': datetime.now().isoformat(),
            'success': execution_result.get('success', False),
            'efficiency': execution_result.get('efficiency', 0.0),
            'value_achieved': execution_result.get('value_achieved', 0.0),
            'decision_quality': execution_result.get('decision_quality', 0.0),
            'execution_time': execution_result.get('execution_time', 0),
            'features': round_data.get('features', []),
        }

        self.engine_history[engine_name]['rounds'].append(history_entry)
        self.engine_history[engine_name]['total_rounds'] += 1

        if execution_result.get('success', False):
            self.engine_history[engine_name]['success_count'] += 1
        else:
            self.engine_history[engine_name]['failure_count'] += 1

        self._save_data()

        return {
            'success': True,
            'engine_name': engine_name,
            'total_history': self.engine_history[engine_name]['total_rounds'],
        }

    def extract_success_patterns(self, engine_name: str = None) -> Dict[str, Any]:
        """
        提取成功模式

        分析引擎历史数据，提取成功执行的模式特征：
        - 时间模式（何时执行更容易成功）
        - 特征组合（哪些功能组合效果最好）
        - 上下文模式（什么情况下适合执行）
        """
        patterns = {}

        engines_to_analyze = [engine_name] if engine_name else list(self.engine_history.keys())

        for eng in engines_to_analyze:
            if eng not in self.engine_history:
                continue

            history = self.engine_history[eng]
            rounds_data = history.get('rounds', [])

            if len(rounds_data) < self.config['pattern_min_samples']:
                continue

            # 分析成功案例
            success_rounds = [r for r in rounds_data if r.get('success', False)]

            if not success_rounds:
                continue

            # 提取特征模式
            feature_counter = Counter()
            for r in success_rounds:
                features = r.get('features', [])
                for f in features:
                    feature_counter[f] += 1

            # 提取效率模式
            avg_efficiency = sum(r.get('efficiency', 0) for r in success_rounds) / len(success_rounds)

            # 提取价值模式
            avg_value = sum(r.get('value_achieved', 0) for r in success_rounds) / len(success_rounds)

            # 提取决策质量模式
            avg_decision = sum(r.get('decision_quality', 0) for r in success_rounds) / len(success_rounds)

            patterns[eng] = {
                'success_rate': len(success_rounds) / len(rounds_data),
                'top_features': [f for f, _ in feature_counter.most_common(5)],
                'avg_efficiency': avg_efficiency,
                'avg_value': avg_value,
                'avg_decision_quality': avg_decision,
                'sample_count': len(success_rounds),
                'analyzed_at': datetime.now().isoformat(),
            }

        self.success_patterns.update(patterns)
        self._save_data()

        return {
            'success': True,
            'patterns_extracted': len(patterns),
            'engines_analyzed': engines_to_analyze,
        }

    def build_wisdom_library(self) -> Dict[str, Any]:
        """
        构建进化智慧库

        将提取的成功模式结构化为可复用的智慧：
        - 最佳实践总结
        - 决策规则
        - 优化建议
        - 跨引擎知识关联
        """
        wisdom = {
            'best_practices': [],
            'decision_rules': [],
            'optimization_suggestions': [],
            'cross_engine_insights': [],
            'updated_at': datetime.now().isoformat(),
        }

        # 从成功模式构建最佳实践
        for eng, pattern in self.success_patterns.items():
            if pattern.get('success_rate', 0) >= 0.7:  # 70%+ 成功率
                wisdom['best_practices'].append({
                    'engine': eng,
                    'success_rate': pattern['success_rate'],
                    'recommended_features': pattern.get('top_features', []),
                    'efficiency_benchmark': pattern.get('avg_efficiency', 0),
                    'value_benchmark': pattern.get('avg_value', 0),
                })

        # 从决策质量构建决策规则
        high_quality_patterns = [
            p for p in self.success_patterns.values()
            if p.get('avg_decision_quality', 0) >= 0.7
        ]

        if high_quality_patterns:
            wisdom['decision_rules'] = [
                {
                    'condition': 'success_rate >= 0.7 AND decision_quality >= 0.7',
                    'action': 'recommend_engine',
                    'engines': [p.get('engine', 'unknown') for p in high_quality_patterns],
                }
            ]

        # 生成优化建议
        for eng, pattern in self.success_patterns.items():
            if pattern.get('success_rate', 0) < 0.5:
                wisdom['optimization_suggestions'].append({
                    'engine': eng,
                    'issue': f"success_rate={pattern.get('success_rate', 0):.2f} (低于50%)",
                    'suggestion': '分析失败原因，考虑功能简化或跳过',
                })

        # 跨引擎洞察
        if len(self.success_patterns) >= 2:
            wisdom['cross_engine_insights'].append({
                'type': 'multi_engine_collaboration',
                'observation': f"已分析 {len(self.success_patterns)} 个引擎的成功模式",
                'recommendation': '可考虑跨引擎协同优化',
            })

        self.wisdom_library = wisdom
        self._save_data()

        return {
            'success': True,
            'wisdom_built': True,
            'best_practices_count': len(wisdom['best_practices']),
            'optimization_suggestions_count': len(wisdom['optimization_suggestions']),
        }

    def get_optimization_recommendation(self, current_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        获取优化建议

        基于蒸馏的智慧库，为当前进化提供优化建议：
        - 推荐使用的引擎
        - 建议避免的引擎
        - 优化方向
        """
        recommendations = {
            'recommended_engines': [],
            'engines_to_avoid': [],
            'optimization_directions': [],
            'reasoning': [],
        }

        context = current_context or {}

        # 基于最佳实践推荐引擎
        best_practices = self.wisdom_library.get('best_practices', [])
        for practice in best_practices:
            if practice.get('success_rate', 0) >= 0.8:  # 80%+ 成功率
                recommendations['recommended_engines'].append({
                    'engine': practice['engine'],
                    'confidence': practice['success_rate'],
                    'reason': f"success_rate={practice['success_rate']:.0%}",
                })

        # 基于优化建议识别需要避免的引擎
        suggestions = self.wisdom_library.get('optimization_suggestions', [])
        for suggestion in suggestions:
            recommendations['engines_to_avoid'].append({
                'engine': suggestion['engine'],
                'reason': suggestion['suggestion'],
            })

        # 生成优化方向
        for practice in best_practices[:3]:  # 前3个最佳实践
            recommendations['optimization_directions'].append({
                'direction': f"use_{practice['engine']}",
                'expected_benefit': f"efficiency +{practice.get('efficiency_benchmark', 0):.0%}",
            })

        # 添加推理过程
        if recommendations['recommended_engines']:
            recommendations['reasoning'].append(
                f"基于 {len(self.wisdom_library.get('best_practices', []))} 个最佳实践分析"
            )

        # 记录决策
        decision_record = {
            'timestamp': datetime.now().isoformat(),
            'context': context,
            'recommendations': recommendations,
        }
        self.optimization_decisions.append(decision_record)

        return recommendations

    def run_distillation_cycle(self, round_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        运行完整的知识蒸馏周期

        1. 收集本轮数据
        2. 提取模式
        3. 更新智慧库
        4. 生成优化建议
        """
        results = {
            'timestamp': datetime.now().isoformat(),
            'steps': [],
        }

        # 步骤1: 收集数据
        collection_result = self.collect_engine_history(round_data)
        results['steps'].append({'step': 'collection', 'result': collection_result})

        # 步骤2: 提取模式
        extraction_result = self.extract_success_patterns()
        results['steps'].append({'step': 'extraction', 'result': extraction_result})

        # 步骤3: 更新智慧库
        if len(self.engine_history) >= self.config['wisdom_update_interval']:
            wisdom_result = self.build_wisdom_library()
            results['steps'].append({'step': 'wisdom', 'result': wisdom_result})

        # 步骤4: 生成建议
        recommendation = self.get_optimization_recommendation(round_data)
        results['steps'].append({'step': 'recommendation', 'result': recommendation})
        results['recommendations'] = recommendation

        results['success'] = True
        return results


def main():
    """主函数：用于命令行测试"""
    import argparse

    parser = argparse.ArgumentParser(description='跨引擎知识蒸馏与自主优化引擎')
    parser.add_argument('command', choices=['status', 'initialize', 'collect', 'extract', 'wisdom', 'recommend', 'cycle'],
                        help='要执行的命令')
    parser.add_argument('--engine', type=str, help='引擎名称')
    parser.add_argument('--round', type=int, help='轮次')
    parser.add_argument('--success', type=bool, default=True, help='是否成功')
    parser.add_argument('--efficiency', type=float, default=0.8, help='效率')
    parser.add_argument('--value', type=float, default=0.7, help='价值')
    parser.add_argument('--quality', type=float, default=0.75, help='决策质量')

    args = parser.parse_args()

    engine = EvolutionKnowledgeDistillationEngine()

    if args.command == 'status':
        print(json.dumps(engine.get_status(), ensure_ascii=False, indent=2))

    elif args.command == 'initialize':
        result = engine.initialize()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == 'collect':
        if not args.engine or not args.round:
            print("错误：需要指定 --engine 和 --round")
            sys.exit(1)
        round_data = {
            'engine_name': args.engine,
            'round': args.round,
            'execution_result': {
                'success': args.success,
                'efficiency': args.efficiency,
                'value_achieved': args.value,
                'decision_quality': args.quality,
            }
        }
        result = engine.collect_engine_history(round_data)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == 'extract':
        result = engine.extract_success_patterns(args.engine)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == 'wisdom':
        result = engine.build_wisdom_library()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == 'recommend':
        result = engine.get_optimization_recommendation()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == 'cycle':
        if not args.engine or not args.round:
            print("错误：需要指定 --engine 和 --round")
            sys.exit(1)
        round_data = {
            'engine_name': args.engine,
            'round': args.round,
            'execution_result': {
                'success': args.success,
                'efficiency': args.efficiency,
                'value_achieved': args.value,
                'decision_quality': args.quality,
            }
        }
        result = engine.run_distillation_cycle(round_data)
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()