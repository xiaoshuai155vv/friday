#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环执行策略自优化与进化驾驶舱深度集成引擎
在 round 449 完成的执行策略自优化深度增强引擎基础上，进一步将自优化能力与进化驾驶舱深度集成。
让系统能够将策略优化过程和结果实时推送到驾驶舱，实现可视化展示和驾驶舱控制。

功能：
1. 集成 round 449 执行策略自优化引擎的数据收集能力
2. 实现优化数据的实时推送（将优化数据推送到驾驶舱可读取的位置）
3. 实现优化过程可视化（分析进度、模式识别、策略生成、执行状态、效果验证）
4. 实现驾驶舱控制接口（从驾驶舱触发优化、暂停、查看详情）
5. 实现优化效果对比可视化（优化前后指标对比图表数据）
6. 实现多维度优化指标展示（响应时间、成功率、资源使用、协作效率）
7. 实现优化历史与趋势分析（历史优化记录、效果趋势）
8. 集成到 do.py 支持驾驶舱优化、优化驾驶舱、优化集成等关键词触发

Version: 1.0.0

依赖：
- evolution_execution_strategy_self_optimizer.py (round 449)
- evolution_cockpit_engine.py (round 350)
"""

import os
import sys
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
from collections import defaultdict
import threading
import time

# 添加 scripts 目录到路径
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPTS_DIR)

# 项目目录
PROJECT_DIR = os.path.dirname(SCRIPTS_DIR)
RUNTIME_DIR = os.path.join(PROJECT_DIR, "runtime")
STATE_DIR = os.path.join(RUNTIME_DIR, "state")
LOGS_DIR = os.path.join(RUNTIME_DIR, "logs")

# 存储文件路径
COCKPIT_INTEGRATION_FILE = os.path.join(STATE_DIR, "strategy_cockpit_integration.json")
OPTIMIZATION_DATA_FILE = os.path.join(STATE_DIR, "execution_strategy_data.json")
OPTIMIZATION_RESULTS_FILE = os.path.join(STATE_DIR, "optimization_results.json")
COCKPIT_STATE_FILE = os.path.join(STATE_DIR, "evolution_cockpit_state.json")


def _safe_print(text: str):
    """安全打印"""
    try:
        print(text)
    except UnicodeEncodeError:
        clean_text = re.sub(r'[^\x00-\x7F]+', '', text)
        print(clean_text)


class StrategyCockpitIntegrationEngine:
    """执行策略自优化与进化驾驶舱深度集成引擎"""

    def __init__(self):
        self.version = "1.0.0"
        self.integration_data = self._load_integration_data()
        self.push_lock = threading.Lock()

        # 配置
        self.config = {
            'push_interval': 5,           # 推送间隔（秒）
            'max_history': 100,           # 最大历史记录数
            'enable_auto_push': True,     # 启用自动推送
        }

    def _load_integration_data(self) -> Dict:
        """加载集成数据"""
        default = {
            'last_push': None,
            'push_history': [],           # 推送历史
            'cockpit_status': {},         # 驾驶舱状态
            'optimization_summary': {},   # 优化摘要
            'visualization_data': {},     # 可视化数据
        }
        try:
            if os.path.exists(COCKPIT_INTEGRATION_FILE):
                with open(COCKPIT_INTEGRATION_FILE, 'r', encoding='utf-8') as f:
                    default.update(json.load(f))
        except Exception as e:
            _safe_print(f"加载集成数据失败: {e}")
        return default

    def _save_integration_data(self):
        """保存集成数据"""
        try:
            os.makedirs(os.path.dirname(COCKPIT_INTEGRATION_FILE), exist_ok=True)
            self.integration_data['last_push'] = datetime.now().isoformat()
            with open(COCKPIT_INTEGRATION_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.integration_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            _safe_print(f"保存集成数据失败: {e}")

    def _load_optimization_data(self) -> Dict:
        """加载优化数据"""
        data = {
            'executions': [],
            'statistics': {}
        }
        try:
            if os.path.exists(OPTIMIZATION_DATA_FILE):
                with open(OPTIMIZATION_DATA_FILE, 'r', encoding='utf-8') as f:
                    data.update(json.load(f))
        except Exception as e:
            _safe_print(f"加载优化数据失败: {e}")
        return data

    def _load_optimization_results(self) -> Dict:
        """加载优化结果"""
        data = {
            'results': []
        }
        try:
            if os.path.exists(OPTIMIZATION_RESULTS_FILE):
                with open(OPTIMIZATION_RESULTS_FILE, 'r', encoding='utf-8') as f:
                    data.update(json.load(f))
        except Exception as e:
            _safe_print(f"加载优化结果失败: {e}")
        return data

    def get_cockpit_status(self) -> Dict:
        """获取驾驶舱状态"""
        status = {
            'timestamp': datetime.now().isoformat(),
            'integration_active': True,
            'connected': False,
            'last_update': None
        }

        try:
            if os.path.exists(COCKPIT_STATE_FILE):
                with open(COCKPIT_STATE_FILE, 'r', encoding='utf-8') as f:
                    cockpit_state = json.load(f)
                    status['connected'] = True
                    status['last_update'] = cockpit_state.get('last_update')
                    status['running'] = cockpit_state.get('running', False)
                    status['auto_mode'] = cockpit_state.get('auto_mode', False)
        except Exception as e:
            _safe_print(f"获取驾驶舱状态失败: {e}")

        self.integration_data['cockpit_status'] = status
        return status

    def collect_optimization_summary(self) -> Dict:
        """收集优化摘要"""
        optimization_data = self._load_optimization_data()
        results_data = self._load_optimization_results()

        executions = optimization_data.get('executions', [])
        results = results_data.get('results', [])

        summary = {
            'timestamp': datetime.now().isoformat(),
            'total_executions': len(executions),
            'total_optimizations': len(results),
            'successful_optimizations': len([r for r in results if r.get('status') == 'success']),
            'failed_optimizations': len([r for r in results if r.get('status') == 'failed']),
        }

        # 计算成功率
        if summary['total_optimizations'] > 0:
            summary['success_rate'] = summary['successful_optimizations'] / summary['total_optimizations']
        else:
            summary['success_rate'] = 0

        # 执行统计
        if executions:
            durations = [e.get('duration', 0) for e in executions if 'duration' in e]
            if durations:
                summary['avg_duration'] = sum(durations) / len(durations)
                summary['max_duration'] = max(durations)

            success_count = sum(1 for e in executions if e.get('success', False))
            summary['execution_success_rate'] = success_count / len(executions) if executions else 0

        self.integration_data['optimization_summary'] = summary
        return summary

    def generate_visualization_data(self) -> Dict:
        """生成可视化数据"""
        optimization_data = self._load_optimization_data()
        results_data = self._load_optimization_results()

        executions = optimization_data.get('executions', [])
        results = results_data.get('results', [])

        viz_data = {
            'timestamp': datetime.now().isoformat(),
            'metrics': {},
            'trends': {},
            'comparison': {}
        }

        # 1. 响应时间趋势
        if len(executions) >= 2:
            recent_executions = executions[-20:]  # 最近20条
            durations = [e.get('duration', 0) for e in recent_executions if 'duration' in e]
            if durations:
                viz_data['trends']['response_time'] = {
                    'current': durations[-1] if durations else 0,
                    'average': sum(durations) / len(durations),
                    'min': min(durations),
                    'max': max(durations),
                    'history': durations
                }

        # 2. 成功率趋势
        if len(executions) >= 2:
            recent = executions[-20:]
            success_count = sum(1 for e in recent if e.get('success', False))
            viz_data['trends']['success_rate'] = {
                'current': success_count / len(recent) if recent else 0,
                'history': [1 if e.get('success', False) else 0 for e in recent]
            }

        # 3. 优化效果对比（优化前后）
        if results:
            # 取最近的优化结果
            recent_results = results[-5:]
            before_metrics = []
            after_metrics = []

            for r in recent_results:
                if 'before_metrics' in r and 'after_metrics' in r:
                    before_metrics.append(r['before_metrics'])
                    after_metrics.append(r['after_metrics'])

            if before_metrics and after_metrics:
                viz_data['comparison'] = {
                    'latest_before': before_metrics[-1] if before_metrics else {},
                    'latest_after': after_metrics[-1] if after_metrics else {},
                    'count': len(before_metrics)
                }

        # 4. 引擎执行分布
        engine_counts = defaultdict(int)
        for e in executions:
            engine_counts[e.get('engine', 'unknown')] += 1

        viz_data['metrics']['engine_distribution'] = dict(engine_counts)

        # 5. 低效模式分布
        patterns = []
        try:
            pattern_file = os.path.join(STATE_DIR, "execution_pattern_analysis.json")
            if os.path.exists(pattern_file):
                with open(pattern_file, 'r', encoding='utf-8') as f:
                    pattern_data = json.load(f)
                    patterns = pattern_data.get('patterns', [])
        except Exception:
            pass

        pattern_counts = defaultdict(int)
        for p in patterns:
            pattern_counts[p.get('pattern_type', 'unknown')] += 1

        viz_data['metrics']['pattern_distribution'] = dict(pattern_counts)

        self.integration_data['visualization_data'] = viz_data
        return viz_data

    def push_to_cockpit(self) -> Dict:
        """推送数据到驾驶舱"""
        with self.push_lock:
            push_result = {
                'timestamp': datetime.now().isoformat(),
                'status': 'success',
                'data_pushed': {}
            }

            try:
                # 1. 收集驾驶舱状态
                cockpit_status = self.get_cockpit_status()
                push_result['data_pushed']['cockpit_status'] = cockpit_status

                # 2. 收集优化摘要
                summary = self.collect_optimization_summary()
                push_result['data_pushed']['optimization_summary'] = summary

                # 3. 生成可视化数据
                viz_data = self.generate_visualization_data()
                push_result['data_pushed']['visualization_data'] = viz_data

                # 4. 保存推送历史
                self.integration_data['push_history'].append(push_result)
                if len(self.integration_data['push_history']) > self.config['max_history']:
                    self.integration_data['push_history'] = self.integration_data['push_history'][-self.config['max_history']:]

                self._save_integration_data()

            except Exception as e:
                push_result['status'] = 'failed'
                push_result['error'] = str(e)
                _safe_print(f"推送数据到驾驶舱失败: {e}")

            return push_result

    def trigger_optimization_from_cockpit(self, params: Dict = None) -> Dict:
        """从驾驶舱触发优化"""
        result = {
            'timestamp': datetime.now().isoformat(),
            'trigger_source': 'cockpit',
            'params': params or {}
        }

        try:
            # 导入执行策略自优化引擎
            try:
                from evolution_execution_strategy_self_optimizer import ExecutionStrategySelfOptimizer
                optimizer = ExecutionStrategySelfOptimizer()

                # 运行完整优化周期
                cycle_result = optimizer.run_full_optimization_cycle()

                result['status'] = 'success'
                result['optimization_result'] = {
                    'analysis_status': cycle_result.get('steps', {}).get('analysis', {}).get('status'),
                    'patterns_found': len(cycle_result.get('steps', {}).get('patterns', [])),
                    'strategies_generated': len(cycle_result.get('steps', {}).get('strategies', [])),
                    'execution_status': cycle_result.get('steps', {}).get('execution', {}).get('message', ''),
                    'verification_count': cycle_result.get('steps', {}).get('verification', {}).get('verified_count', 0)
                }

                # 推送更新后的数据到驾驶舱
                self.push_to_cockpit()

            except ImportError as e:
                result['status'] = 'failed'
                result['error'] = f"无法导入执行策略自优化引擎: {e}"

        except Exception as e:
            result['status'] = 'failed'
            result['error'] = str(e)
            _safe_print(f"从驾驶舱触发优化失败: {e}")

        return result

    def get_optimization_dashboard_data(self) -> Dict:
        """获取优化仪表盘数据（供驾驶舱调用）"""
        dashboard_data = {
            'timestamp': datetime.now().isoformat(),
            'summary': self.collect_optimization_summary(),
            'visualization': self.generate_visualization_data(),
            'cockpit_status': self.get_cockpit_status(),
            'quick_actions': {
                'trigger_optimization': True,
                'view_history': True,
                'view_trends': True,
                'view_comparison': True
            }
        }

        return dashboard_data

    def get_optimization_history(self, limit: int = 20) -> List[Dict]:
        """获取优化历史"""
        results_data = self._load_optimization_results()
        results = results_data.get('results', [])

        # 返回最近的记录
        return results[-limit:] if results else []

    def get_trend_analysis(self, metric: str = 'response_time', days: int = 7) -> Dict:
        """获取趋势分析"""
        optimization_data = self._load_optimization_data()
        executions = optimization_data.get('executions', [])

        # 过滤指定时间范围
        cutoff = datetime.now() - timedelta(days=days)
        recent_executions = []

        for e in executions:
            try:
                exec_time = datetime.fromisoformat(e.get('timestamp', ''))
                if exec_time >= cutoff:
                    recent_executions.append(e)
            except Exception:
                continue

        trend = {
            'metric': metric,
            'period_days': days,
            'data_points': len(recent_executions),
            'analysis': {}
        }

        if metric == 'response_time' and recent_executions:
            durations = [e.get('duration', 0) for e in recent_executions if 'duration' in e]
            if durations:
                # 将数据分成若干段分析趋势
                segment_size = max(1, len(durations) // 5)
                segments = [durations[i:i+segment_size] for i in range(0, len(durations), segment_size)]

                trend['analysis'] = {
                    'overall_avg': sum(durations) / len(durations),
                    'current_avg': sum(durations[-segment_size:]) / len(durations[-segment_size:]) if durations[-segment_size:] else 0,
                    'segments': [
                        {
                            'segment': i,
                            'avg': sum(s) / len(s) if s else 0,
                            'trend': 'up' if i > 0 and sum(s) / len(s) > sum(segments[i-1]) / len(segments[i-1]) else 'down'
                        }
                        for i, s in enumerate(segments) if s
                    ]
                }

        elif metric == 'success_rate' and recent_executions:
            success_values = [1 if e.get('success', False) else 0 for e in recent_executions]
            if success_values:
                segment_size = max(1, len(success_values) // 5)
                segments = [success_values[i:i+segment_size] for i in range(0, len(success_values), segment_size)]

                trend['analysis'] = {
                    'overall_rate': sum(success_values) / len(success_values),
                    'current_rate': sum(success_values[-segment_size:]) / len(success_values[-segment_size:]) if success_values[-segment_size:] else 0,
                    'segments': [
                        {
                            'segment': i,
                            'rate': sum(s) / len(s) if s else 0,
                            'trend': 'up' if i > 0 and sum(s) / len(s) > sum(segments[i-1]) / len(segments[i-1]) else 'down'
                        }
                        for i, s in enumerate(segments) if s
                    ]
                }

        return trend

    def run_continuous_integration(self, duration: int = 60):
        """运行持续集成（定期推送数据到驾驶舱）"""
        _safe_print(f"启动持续集成模式，运行时长: {duration}秒")
        start_time = time.time()

        while time.time() - start_time < duration:
            try:
                result = self.push_to_cockpit()
                if result.get('status') == 'success':
                    _safe_print(f"数据推送成功: {result.get('timestamp')}")
                else:
                    _safe_print(f"数据推送失败: {result.get('error')}")

                # 等待推送间隔
                time.sleep(self.config['push_interval'])

            except KeyboardInterrupt:
                _safe_print("手动停止持续集成")
                break
            except Exception as e:
                _safe_print(f"持续集成出错: {e}")
                time.sleep(self.config['push_interval'])

        _safe_print("持续集成模式结束")


def main():
    """主函数 - 支持命令行调用"""
    import argparse

    parser = argparse.ArgumentParser(
        description='智能全场景进化环执行策略自优化与进化驾驶舱深度集成引擎'
    )
    parser.add_argument('--push', action='store_true', help='推送数据到驾驶舱')
    parser.add_argument('--status', action='store_true', help='获取驾驶舱状态')
    parser.add_argument('--summary', action='store_true', help='获取优化摘要')
    parser.add_argument('--viz', action='store_true', help='获取可视化数据')
    parser.add_argument('--dashboard', action='store_true', help='获取仪表盘数据')
    parser.add_argument('--trigger', action='store_true', help='从驾驶舱触发优化')
    parser.add_argument('--history', action='store_true', help='获取优化历史')
    parser.add_argument('--trend', type=str, help='获取趋势分析 (response_time|success_rate)')
    parser.add_argument('--continuous', type=int, nargs='?', const=60, help='运行持续集成模式（默认60秒）')

    args = parser.parse_args()

    engine = StrategyCockpitIntegrationEngine()

    if args.status:
        # 获取驾驶舱状态
        status = engine.get_cockpit_status()
        _safe_print("=" * 50)
        _safe_print("驾驶舱状态：")
        _safe_print("=" * 50)
        for key, value in status.items():
            _safe_print(f"{key}: {value}")

    elif args.summary:
        # 获取优化摘要
        summary = engine.collect_optimization_summary()
        _safe_print("=" * 50)
        _safe_print("优化摘要：")
        _safe_print("=" * 50)
        for key, value in summary.items():
            _safe_print(f"{key}: {value}")

    elif args.viz:
        # 获取可视化数据
        viz = engine.generate_visualization_data()
        _safe_print("=" * 50)
        _safe_print("可视化数据：")
        _safe_print("=" * 50)
        print(json.dumps(viz, ensure_ascii=False, indent=2))

    elif args.dashboard:
        # 获取仪表盘数据
        dashboard = engine.get_optimization_dashboard_data()
        _safe_print("=" * 50)
        _safe_print("仪表盘数据：")
        _safe_print("=" * 50)
        print(json.dumps(dashboard, ensure_ascii=False, indent=2))

    elif args.trigger:
        # 从驾驶舱触发优化
        result = engine.trigger_optimization_from_cockpit()
        _safe_print("=" * 50)
        _safe_print("优化触发结果：")
        _safe_print("=" * 50)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.history:
        # 获取优化历史
        history = engine.get_optimization_history()
        _safe_print("=" * 50)
        _safe_print("优化历史：")
        _safe_print("=" * 50)
        for i, h in enumerate(history, 1):
            _safe_print(f"\n{i}. 策略ID: {h.get('strategy_id')}")
            _safe_print(f"   状态: {h.get('status')}")
            _safe_print(f"   时间: {h.get('timestamp')}")

    elif args.trend:
        # 获取趋势分析
        trend = engine.get_trend_analysis(args.trend)
        _safe_print("=" * 50)
        _safe_print(f"趋势分析 ({args.trend}):")
        _safe_print("=" * 50)
        print(json.dumps(trend, ensure_ascii=False, indent=2))

    elif args.continuous:
        # 运行持续集成模式
        engine.run_continuous_integration(args.continuous)

    elif args.push:
        # 推送数据到驾驶舱
        result = engine.push_to_cockpit()
        _safe_print("=" * 50)
        _safe_print("推送结果：")
        _safe_print("=" * 50)
        _safe_print(f"状态: {result.get('status')}")
        _safe_print(f"时间: {result.get('timestamp')}")
        if result.get('error'):
            _safe_print(f"错误: {result.get('error')}")

    else:
        # 默认：显示帮助
        parser.print_help()
        _safe_print("\n示例：")
        _safe_print("  python evolution_strategy_cockpit_integration_engine.py --status")
        _safe_print("  python evolution_strategy_cockpit_integration_engine.py --summary")
        _safe_print("  python evolution_strategy_cockpit_integration_engine.py --viz")
        _safe_print("  python evolution_strategy_cockpit_integration_engine.py --dashboard")
        _safe_print("  python evolution_strategy_cockpit_integration_engine.py --trigger")
        _safe_print("  python evolution_strategy_cockpit_integration_engine.py --history")
        _safe_print("  python evolution_strategy_cockpit_integration_engine.py --trend response_time")
        _safe_print("  python evolution_strategy_cockpit_integration_engine.py --push")
        _safe_print("  python evolution_strategy_cockpit_integration_engine.py --continuous 120")


if __name__ == '__main__':
    main()