#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环价值-涌现闭环增强引擎
version 1.0.0

功能：
1. 收集价值实现引擎的执行结果和价值追踪数据
2. 分析假设执行成功/失败模式
3. 将分析结果反馈到涌现发现引擎
4. 实现完整的"假设→执行→价值实现→反馈→新假设"递归增强闭环
5. 与进化驾驶舱深度集成

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

# 尝试导入价值实现引擎和涌现发现引擎
try:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from evolution_hypothesis_execution_engine import EvolutionHypothesisExecutionEngine
    EXECUTION_ENGINE_AVAILABLE = True
except ImportError:
    EXECUTION_ENGINE_AVAILABLE = False

try:
    from evolution_emergence_discovery_innovation_engine import EvolutionEmergenceDiscoveryInnovationEngine
    EMERGENCE_ENGINE_AVAILABLE = True
except ImportError:
    EMERGENCE_ENGINE_AVAILABLE = False


class EvolutionValueEmergenceClosedLoopEngine:
    """价值-涌现闭环增强引擎"""

    def __init__(self, base_path: str = None):
        self.base_path = base_path or os.path.dirname(os.path.abspath(__file__))
        self.runtime_path = os.path.join(os.path.dirname(self.base_path), 'runtime')
        self.state_path = os.path.join(self.runtime_path, 'state')
        self.logs_path = os.path.join(self.runtime_path, 'logs')
        self.capabilities_path = os.path.join(os.path.dirname(self.base_path), 'references', 'capabilities.md')

        # 初始化价值实现引擎
        self.execution_engine = None
        if EXECUTION_ENGINE_AVAILABLE:
            try:
                self.execution_engine = EvolutionHypothesisExecutionEngine(self.base_path)
            except Exception:
                pass

        # 初始化涌现发现引擎
        self.emergence_engine = None
        if EMERGENCE_ENGINE_AVAILABLE:
            try:
                self.emergence_engine = EvolutionEmergenceDiscoveryInnovationEngine(self.base_path)
            except Exception:
                pass

        # 闭环数据
        self.feedback_data = []
        self.closed_loop_history = []
        self.optimization_patterns = {}

        # 闭环配置
        self.config = {
            'feedback_enabled': True,
            'auto_optimization': True,
            'pattern_learning': True,
            'min_samples_for_pattern': 3,
            'value_threshold': 0.6,
            'success_threshold': 0.7,
        }

    def initialize(self) -> Dict[str, Any]:
        """初始化引擎"""
        # 初始化价值执行引擎
        execution_status = None
        if self.execution_engine:
            try:
                execution_status = self.execution_engine.initialize()
            except Exception as e:
                execution_status = {'status': 'error', 'message': str(e)}

        # 初始化涌现发现引擎
        emergence_status = None
        if self.emergence_engine:
            try:
                emergence_status = self.emergence_engine.initialize()
            except Exception as e:
                emergence_status = {'status': 'error', 'message': str(e)}

        # 加载历史闭环数据
        self._load_closed_loop_history()

        result = {
            'status': 'success',
            'message': '价值-涌现闭环增强引擎初始化成功',
            'version': '1.0.0',
            'capabilities': [
                '价值数据收集',
                '执行结果分析',
                '闭环反馈',
                '模式学习',
                '优化建议生成',
                '递归增强'
            ],
            'execution_engine_status': execution_status,
            'emergence_engine_status': emergence_status,
            'loaded_data': {
                'closed_loop_history_count': len(self.closed_loop_history),
                'feedback_data_count': len(self.feedback_data),
                'optimization_patterns_count': len(self.optimization_patterns)
            }
        }
        return result

    def _load_closed_loop_history(self) -> List[Dict]:
        """加载历史闭环数据"""
        history = []
        history_file = os.path.join(self.state_path, 'value_emergence_closed_loop_history.json')
        if os.path.exists(history_file):
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
                    self.closed_loop_history = history
            except Exception:
                pass
        return history

    def _save_closed_loop_history(self):
        """保存闭环历史"""
        history_file = os.path.join(self.state_path, 'value_emergence_closed_loop_history.json')
        try:
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(self.closed_loop_history, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def collect_value_data(self) -> Dict[str, Any]:
        """收集价值实现数据"""
        value_data = {
            'timestamp': datetime.now().isoformat(),
            'execution_results': [],
            'value_metrics': {},
            'status': 'collected'
        }

        # 从价值实现引擎获取数据
        if self.execution_engine:
            try:
                # 获取执行历史
                if hasattr(self.execution_engine, 'execution_history'):
                    value_data['execution_results'] = self.execution_engine.execution_history

                # 获取价值追踪数据
                if hasattr(self.execution_engine, 'value_tracking'):
                    value_data['value_metrics'] = self.execution_engine.value_tracking
            except Exception as e:
                value_data['error'] = str(e)

        # 从已完成进化记录中收集
        try:
            state_files = []
            if os.path.exists(self.state_path):
                for f in os.listdir(self.state_path):
                    if f.startswith('evolution_completed_') and f.endswith('.json'):
                        state_files.append(f)

            recent_files = sorted(state_files, reverse=True)[:10]  # 取最近10个
            for f in recent_files:
                try:
                    with open(os.path.join(self.state_path, f), 'r', encoding='utf-8') as fp:
                        data = json.load(fp)
                        if 'execution_results' not in value_data:
                            value_data['execution_results'] = []
                        value_data['execution_results'].append({
                            'round': data.get('loop_round', 'unknown'),
                            'goal': data.get('current_goal', ''),
                            'completed': data.get('completed', False),
                            'result': data.get('result', {})
                        })
                except Exception:
                    pass
        except Exception as e:
            value_data['collection_error'] = str(e)

        self.feedback_data.append(value_data)
        return value_data

    def analyze_execution_patterns(self, value_data: Dict) -> Dict[str, Any]:
        """分析执行模式"""
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'patterns': {},
            'success_factors': [],
            'failure_factors': [],
            'value_insights': [],
            'recommendations': []
        }

        execution_results = value_data.get('execution_results', [])

        if not execution_results:
            return analysis

        # 分析成功模式
        successful = [r for r in execution_results if r.get('completed', False)]
        failed = [r for r in execution_results if not r.get('completed', False)]

        if successful:
            analysis['success_factors'].append({
                'count': len(successful),
                'total': len(execution_results),
                'rate': len(successful) / len(execution_results) if execution_results else 0,
                'sample_goals': [r.get('goal', '')[:50] for r in successful[:3]]
            })

        if failed:
            analysis['failure_factors'].append({
                'count': len(failed),
                'sample_goals': [r.get('goal', '')[:50] for r in failed[:3]]
            })

        # 提取价值指标分析
        value_metrics = value_data.get('value_metrics', {})
        if value_metrics:
            avg_value = sum(v.get('value', 0) for v in value_metrics.values()) / len(value_metrics) if value_metrics else 0
            analysis['value_insights'].append({
                'average_value': avg_value,
                'metrics_count': len(value_metrics)
            })

        # 生成优化建议
        if len(successful) / len(execution_results) < self.config['success_threshold'] if execution_results else False:
            analysis['recommendations'].append('执行成功率偏低，建议调整假设生成策略')

        if analysis.get('value_insights'):
            if analysis['value_insights'][0]['average_value'] < self.config['value_threshold']:
                analysis['recommendations'].append('价值实现不足，建议优化假设的可执行性')

        return analysis

    def generate_feedback(self, analysis: Dict) -> Dict[str, Any]:
        """生成反馈数据"""
        feedback = {
            'timestamp': datetime.now().isoformat(),
            'analysis': analysis,
            'optimization_hints': [],
            'hypothesis_adjustments': [],
            'status': 'generated'
        }

        # 基于分析生成优化提示
        success_factors = analysis.get('success_factors', [])
        if success_factors:
            rate = success_factors[0].get('rate', 0)
            if rate > 0.8:
                feedback['optimization_hints'].append('高成功率假设特征：可作为后续假设生成的参考')
            elif rate < 0.5:
                feedback['optimization_hints'].append('低成功率假设特征：需要调整假设生成策略')

        failure_factors = analysis.get('failure_factors', [])
        if failure_factors:
            feedback['optimization_hints'].append('识别到失败模式：需要在假设生成时规避')

        recommendations = analysis.get('recommendations', [])
        for rec in recommendations:
            feedback['hypothesis_adjustments'].append({
                'type': 'recommendation',
                'content': rec
            })

        # 学习优化模式
        if self.config['pattern_learning']:
            self._learn_optimization_patterns(analysis)

        return feedback

    def _learn_optimization_patterns(self, analysis: Dict):
        """学习优化模式"""
        success_factors = analysis.get('success_factors', [])
        failure_factors = analysis.get('failure_factors', [])

        if success_factors:
            key = 'success_patterns'
            if key not in self.optimization_patterns:
                self.optimization_patterns[key] = []
            self.optimization_patterns[key].append({
                'timestamp': datetime.now().isoformat(),
                'rate': success_factors[0].get('rate', 0),
                'sample_goals': success_factors[0].get('sample_goals', [])
            })

        if failure_factors:
            key = 'failure_patterns'
            if key not in self.optimization_patterns:
                self.optimization_patterns[key] = []
            self.optimization_patterns[key].append({
                'timestamp': datetime.now().isoformat(),
                'sample_goals': failure_factors[0].get('sample_goals', [])
            })

    def send_feedback_to_emergence(self, feedback: Dict) -> Dict[str, Any]:
        """将反馈发送到涌现发现引擎"""
        result = {
            'timestamp': datetime.now().isoformat(),
            'feedback_sent': False,
            'emergence_response': None,
            'status': 'pending'
        }

        if not self.emergence_engine:
            result['error'] = '涌现发现引擎未初始化'
            return result

        try:
            # 调用涌现发现引擎的反馈接口
            if hasattr(self.emergence_engine, 'receive_feedback'):
                response = self.emergence_engine.receive_feedback(feedback)
                result['feedback_sent'] = True
                result['emergence_response'] = response
            elif hasattr(self.emergence_engine, 'update_from_execution'):
                # 备用接口
                response = self.emergence_engine.update_from_execution(feedback)
                result['feedback_sent'] = True
                result['emergence_response'] = response
            else:
                # 尝试通过加载数据的方式传递反馈
                feedback_file = os.path.join(self.state_path, 'execution_feedback_for_emergence.json')
                with open(feedback_file, 'w', encoding='utf-8') as f:
                    json.dump(feedback, f, ensure_ascii=False, indent=2)
                result['feedback_sent'] = True
                result['message'] = '反馈已写入文件，涌现引擎可读取'
        except Exception as e:
            result['error'] = str(e)

        result['status'] = 'completed' if result['feedback_sent'] else 'failed'
        return result

    def execute_closed_loop(self) -> Dict[str, Any]:
        """执行完整的闭环流程"""
        loop_result = {
            'timestamp': datetime.now().isoformat(),
            'steps': {},
            'status': 'in_progress'
        }

        # 步骤1: 收集价值数据
        step1 = self.collect_value_data()
        loop_result['steps']['collect_value_data'] = {
            'status': 'success' if step1.get('status') == 'collected' else 'failed',
            'data': step1
        }

        # 步骤2: 分析执行模式
        step2 = self.analyze_execution_patterns(step1)
        loop_result['steps']['analyze_patterns'] = {
            'status': 'success',
            'analysis': step2
        }

        # 步骤3: 生成反馈
        step3 = self.generate_feedback(step2)
        loop_result['steps']['generate_feedback'] = {
            'status': 'success',
            'feedback': step3
        }

        # 步骤4: 发送到涌现引擎
        step4 = self.send_feedback_to_emergence(step3)
        loop_result['steps']['send_to_emergence'] = step4

        # 记录闭环历史
        self.closed_loop_history.append(loop_result)
        self._save_closed_loop_history()

        loop_result['status'] = 'completed'
        return loop_result

    def get_status(self) -> Dict[str, Any]:
        """获取引擎状态"""
        return {
            'status': 'running',
            'version': '1.0.0',
            'engines': {
                'execution_engine': self.execution_engine is not None,
                'emergence_engine': self.emergence_engine is not None
            },
            'data': {
                'feedback_data_count': len(self.feedback_data),
                'closed_loop_history_count': len(self.closed_loop_history),
                'optimization_patterns_count': len(self.optimization_patterns)
            },
            'config': self.config
        }

    def get_optimization_suggestions(self) -> List[str]:
        """获取优化建议"""
        suggestions = []

        if not self.closed_loop_history:
            return ['暂无足够数据生成优化建议，请先执行闭环']

        # 基于历史闭环数据分析
        recent_loops = self.closed_loop_history[-5:]  # 最近5次闭环
        success_count = 0

        for loop in recent_loops:
            steps = loop.get('steps', {})
            send_step = steps.get('send_to_emergence', {})
            if send_step.get('feedback_sent'):
                success_count += 1

        if success_count == len(recent_loops):
            suggestions.append('闭环执行成功率很高，系统运行良好')
        elif success_count > 0:
            suggestions.append(f'闭环执行成功率: {success_count}/{len(recent_loops)}，建议检查未成功的环节')

        # 基于优化模式生成建议
        if 'success_patterns' in self.optimization_patterns:
            patterns = self.optimization_patterns['success_patterns']
            if len(patterns) >= self.config['min_samples_for_pattern']:
                suggestions.append('已学习到成功模式，可用于优化后续假设生成')

        if 'failure_patterns' in self.optimization_patterns:
            suggestions.append('已识别失败模式，建议在假设生成时规避')

        return suggestions


def main():
    """主函数，支持命令行调用"""
    import argparse

    parser = argparse.ArgumentParser(description='智能全场景进化环价值-涌现闭环增强引擎')
    parser.add_argument('command', nargs='?', default='status',
                       help='命令: status, initialize, collect, analyze, feedback, closed_loop, suggestions')
    parser.add_argument('--verbose', '-v', action='store_true', help='详细输出')

    args = parser.parse_args()

    engine = EvolutionValueEmergenceClosedLoopEngine()

    if args.command == 'status':
        result = engine.get_status()
    elif args.command == 'initialize':
        result = engine.initialize()
    elif args.command == 'collect':
        result = engine.collect_value_data()
    elif args.command == 'analyze':
        value_data = engine.collect_value_data()
        result = engine.analyze_execution_patterns(value_data)
    elif args.command == 'feedback':
        value_data = engine.collect_value_data()
        analysis = engine.analyze_execution_patterns(value_data)
        result = engine.generate_feedback(analysis)
    elif args.command == 'closed_loop':
        result = engine.execute_closed_loop()
    elif args.command == 'suggestions':
        result = {'suggestions': engine.get_optimization_suggestions()}
    else:
        result = {'error': f'未知命令: {args.command}'}

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()