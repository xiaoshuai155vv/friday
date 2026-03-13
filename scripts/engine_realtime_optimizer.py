#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能引擎组合实时监控与自适应优化引擎

让系统能够实时监控70+引擎的使用效果，基于性能指标自动识别优化机会，
生成动态优化建议，实现从静态组合到自适应动态组合的范式升级。

功能：
1. 引擎使用实时监控（调用频率、响应时间、内存占用、成功率）
2. 基于指标的动态优化建议生成
3. 引擎组合效果分析
4. 自适应优化策略推荐

使用方法：
    python engine_realtime_optimizer.py status
    python engine_realtime_optimizer.py analyze
    python engine_realtime_optimizer.py optimize
    python engine_realtime_optimizer.py monitor
"""

import json
import os
import sys
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict, deque
from dataclasses import dataclass, field, asdict

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
RUNTIME_STATE = PROJECT_ROOT / "runtime" / "state"
RUNTIME_LOGS = PROJECT_ROOT / "runtime" / "logs"
REFERENCES = PROJECT_ROOT / "references"


@dataclass
class EngineMetrics:
    """引擎性能指标"""
    engine_name: str
    call_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    total_response_time: float = 0.0  # 毫秒
    avg_response_time: float = 0.0
    memory_usage: float = 0.0  # MB
    peak_memory: float = 0.0
    last_call_time: Optional[str] = None
    first_call_time: Optional[str] = None

    @property
    def success_rate(self) -> float:
        if self.call_count == 0:
            return 0.0
        return self.success_count / self.call_count * 100

    @property
    def failure_rate(self) -> float:
        return 100 - self.success_rate


@dataclass
class OptimizationRecommendation:
    """优化建议"""
    engine_name: str
    issue_type: str  # high_response_time, low_usage, high_memory, low_success_rate, etc.
    severity: str  # critical, high, medium, low
    description: str
    recommendation: str
    expected_improvement: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class EngineRealtimeOptimizer:
    """智能引擎组合实时监控与自适应优化引擎"""

    def __init__(self):
        self.state_dir = RUNTIME_STATE
        self.logs_dir = RUNTIME_LOGS
        self.references_dir = REFERENCES

        # 确保目录存在
        self.state_dir.mkdir(parents=True, exist_ok=True)

        # 引擎性能数据存储
        self.metrics_file = self.state_dir / "engine_realtime_metrics.json"
        self.optimization_file = self.state_dir / "engine_optimization_recommendations.json"
        self.history_file = self.state_dir / "engine_optimization_history.json"

        # 实时指标缓存
        self.metrics: Dict[str, EngineMetrics] = {}
        self.recommendations: List[OptimizationRecommendation] = []

        # 监控状态
        self.monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None

        # 阈值配置
        self.thresholds = {
            "response_time_high": 5000,  # 毫秒
            "response_time_medium": 2000,
            "memory_high": 500,  # MB
            "memory_medium": 200,
            "success_rate_low": 70,  # 百分比
            "usage_low": 5,  # 调用次数阈值
        }

        # 加载现有数据
        self._load_metrics()
        self._load_recommendations()

    def _load_metrics(self) -> None:
        """加载引擎性能数据"""
        if self.metrics_file.exists():
            try:
                with open(self.metrics_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for eng_name, eng_data in data.get('engines', {}).items():
                        self.metrics[eng_name] = EngineMetrics(**eng_data)
            except Exception as e:
                print(f"加载引擎性能数据失败: {e}")

    def _save_metrics(self) -> None:
        """保存引擎性能数据"""
        try:
            data = {
                'timestamp': datetime.now().isoformat(),
                'engines': {name: asdict(metrics) for name, metrics in self.metrics.items()}
            }
            with open(self.metrics_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存引擎性能数据失败: {e}")

    def _load_recommendations(self) -> None:
        """加载优化建议"""
        if self.optimization_file.exists():
            try:
                with open(self.optimization_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for rec_data in data.get('recommendations', []):
                        self.recommendations.append(OptimizationRecommendation(**rec_data))
            except Exception as e:
                print(f"加载优化建议失败: {e}")

    def _save_recommendations(self) -> None:
        """保存优化建议"""
        try:
            data = {
                'timestamp': datetime.now().isoformat(),
                'recommendations': [asdict(rec) for rec in self.recommendations]
            }
            with open(self.optimization_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存优化建议失败: {e}")

    def record_engine_call(self, engine_name: str, response_time: float = 0,
                          success: bool = True, memory_usage: float = 0) -> None:
        """记录引擎调用

        Args:
            engine_name: 引擎名称
            response_time: 响应时间（毫秒）
            success: 是否成功
            memory_usage: 内存占用（MB）
        """
        if engine_name not in self.metrics:
            self.metrics[engine_name] = EngineMetrics(engine_name=engine_name)

        metrics = self.metrics[engine_name]
        metrics.call_count += 1

        if success:
            metrics.success_count += 1
        else:
            metrics.failure_count += 1

        metrics.total_response_time += response_time
        metrics.avg_response_time = metrics.total_response_time / metrics.call_count

        if memory_usage > 0:
            metrics.memory_usage = memory_usage
            if memory_usage > metrics.peak_memory:
                metrics.peak_memory = memory_usage

        metrics.last_call_time = datetime.now().isoformat()
        if metrics.first_call_time is None:
            metrics.first_call_time = metrics.last_call_time

        # 自动保存
        self._save_metrics()

    def analyze_engines(self) -> Dict[str, Any]:
        """分析所有引擎的性能指标"""
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'total_engines': len(self.metrics),
            'engine_analysis': [],
            'summary': {
                'total_calls': 0,
                'total_successes': 0,
                'total_failures': 0,
                'avg_success_rate': 0,
                'avg_response_time': 0,
                'high_memory_engines': [],
                'slow_engines': [],
                'low_usage_engines': [],
                'low_success_engines': []
            }
        }

        total_calls = 0
        total_successes = 0
        total_failures = 0
        total_response_time = 0

        for engine_name, metrics in self.metrics.items():
            total_calls += metrics.call_count
            total_successes += metrics.success_count
            total_failures += metrics.failure_count
            total_response_time += metrics.total_response_time

            # 分析单个引擎
            eng_analysis = {
                'engine_name': engine_name,
                'call_count': metrics.call_count,
                'success_rate': round(metrics.success_rate, 2),
                'failure_rate': round(metrics.failure_rate, 2),
                'avg_response_time': round(metrics.avg_response_time, 2),
                'peak_memory': round(metrics.peak_memory, 2),
                'issues': []
            }

            # 检测问题
            if metrics.avg_response_time > self.thresholds['response_time_high']:
                eng_analysis['issues'].append('high_response_time')
                analysis['summary']['slow_engines'].append(engine_name)

            if metrics.peak_memory > self.thresholds['memory_high']:
                eng_analysis['issues'].append('high_memory')
                analysis['summary']['high_memory_engines'].append(engine_name)

            if metrics.call_count < self.thresholds['usage_low']:
                eng_analysis['issues'].append('low_usage')
                analysis['summary']['low_usage_engines'].append(engine_name)

            if metrics.success_rate < self.thresholds['success_rate_low']:
                eng_analysis['issues'].append('low_success_rate')
                analysis['summary']['low_success_engines'].append(engine_name)

            analysis['engine_analysis'].append(eng_analysis)

        # 计算汇总
        if total_calls > 0:
            analysis['summary']['total_calls'] = total_calls
            analysis['summary']['total_successes'] = total_successes
            analysis['summary']['total_failures'] = total_failures
            analysis['summary']['avg_success_rate'] = round(total_successes / total_calls * 100, 2)

        if len(self.metrics) > 0:
            analysis['summary']['avg_response_time'] = round(total_response_time / total_calls, 2) if total_calls > 0 else 0

        return analysis

    def generate_recommendations(self) -> List[OptimizationRecommendation]:
        """生成优化建议"""
        self.recommendations.clear()

        analysis = self.analyze_engines()

        # 处理慢引擎
        for engine_name in analysis['summary'].get('slow_engines', []):
            metrics = self.metrics.get(engine_name)
            if metrics:
                self.recommendations.append(OptimizationRecommendation(
                    engine_name=engine_name,
                    issue_type='high_response_time',
                    severity='high' if metrics.avg_response_time > self.thresholds['response_time_high'] else 'medium',
                    description=f"引擎 '{engine_name}' 平均响应时间 {metrics.avg_response_time:.2f}ms，超过阈值",
                    recommendation=f"建议优化 {engine_name} 的执行逻辑，考虑添加缓存或并行处理",
                    expected_improvement="响应时间降低 30-50%"
                ))

        # 处理高内存引擎
        for engine_name in analysis['summary'].get('high_memory_engines', []):
            metrics = self.metrics.get(engine_name)
            if metrics:
                self.recommendations.append(OptimizationRecommendation(
                    engine_name=engine_name,
                    issue_type='high_memory',
                    severity='critical' if metrics.peak_memory > self.thresholds['memory_high'] else 'high',
                    description=f"引擎 '{engine_name}' 峰值内存 {metrics.peak_memory:.2f}MB，超过阈值",
                    recommendation=f"建议优化 {engine_name} 的内存使用，释放不必要的资源",
                    expected_improvement="内存使用降低 20-40%"
                ))

        # 处理低使用率引擎
        for engine_name in analysis['summary'].get('low_usage_engines', []):
            metrics = self.metrics.get(engine_name)
            if metrics:
                self.recommendations.append(OptimizationRecommendation(
                    engine_name=engine_name,
                    issue_type='low_usage',
                    severity='low',
                    description=f"引擎 '{engine_name}' 调用次数仅 {metrics.call_count} 次，使用率低",
                    recommendation=f"建议推广 {engine_name} 的使用场景，或评估是否需要",
                    expected_improvement="提高引擎利用率，发挥系统能力"
                ))

        # 处理低成功率引擎
        for engine_name in analysis['summary'].get('low_success_engines', []):
            metrics = self.metrics.get(engine_name)
            if metrics:
                self.recommendations.append(OptimizationRecommendation(
                    engine_name=engine_name,
                    issue_type='low_success_rate',
                    severity='critical',
                    description=f"引擎 '{engine_name}' 成功率仅 {metrics.success_rate:.2f}%，低于阈值",
                    recommendation=f"建议立即修复 {engine_name} 的问题，检查错误日志并优化",
                    expected_improvement="成功率提升至 90%+"
                ))

        # 如果没有明显问题，生成正面反馈
        if not self.recommendations:
            self.recommendations.append(OptimizationRecommendation(
                engine_name='system',
                issue_type='all_engines_healthy',
                severity='low',
                description="所有引擎运行状态良好，未检测到明显问题",
                recommendation="继续保持当前运行状态，定期进行健康检查",
                expected_improvement="系统稳定运行"
            ))

        # 保存建议
        self._save_recommendations()

        return self.recommendations

    def get_engine_combination_analysis(self) -> Dict[str, Any]:
        """分析引擎组合效果"""
        # 尝试从引擎协作跟踪数据中获取组合信息
        collab_file = self.state_dir / "engine_collaboration_tracking.json"
        combo_analysis = {
            'timestamp': datetime.now().isoformat(),
            'engine_count': len(self.metrics),
            'active_engines': [],
            'idle_engines': [],
            'recommendations': []
        }

        # 分类引擎
        for engine_name, metrics in self.metrics.items():
            if metrics.call_count > 10:
                combo_analysis['active_engines'].append({
                    'name': engine_name,
                    'calls': metrics.call_count,
                    'success_rate': round(metrics.success_rate, 2)
                })
            else:
                combo_analysis['idle_engines'].append({
                    'name': engine_name,
                    'calls': metrics.call_count
                })

        # 生成组合建议
        if len(combo_analysis['active_engines']) < len(self.metrics) * 0.3:
            combo_analysis['recommendations'].append({
                'type': 'low_utilization',
                'message': '系统中有较多引擎未被充分利用，建议扩展使用场景或整合低利用率引擎'
            })

        return combo_analysis

    def get_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        return {
            'timestamp': datetime.now().isoformat(),
            'monitoring': self.monitoring,
            'total_engines_tracked': len(self.metrics),
            'total_recommendations': len(self.recommendations),
            'thresholds': self.thresholds
        }

    def start_monitoring(self) -> None:
        """启动实时监控"""
        if not self.monitoring:
            self.monitoring = True

            def monitor_loop():
                while self.monitoring:
                    # 收集当前进程信息（如果 psutil 可用）
                    if PSUTIL_AVAILABLE:
                        try:
                            process = psutil.Process()
                        except:
                            pass
                    time.sleep(60)  # 每分钟检查一次

            self.monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
            self.monitor_thread.start()
            print("实时监控已启动")

    def stop_monitoring(self) -> None:
        """停止实时监控"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
        print("实时监控已停止")

    def export_optimization_history(self) -> None:
        """导出优化历史"""
        try:
            history = {
                'timestamp': datetime.now().isoformat(),
                'engines': {name: asdict(metrics) for name, metrics in self.metrics.items()},
                'recommendations': [asdict(rec) for rec in self.recommendations]
            }

            # 读取历史
            history_data = []
            if self.history_file.exists():
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    history_data = json.load(f)

            # 添加新记录
            history_data.append(history)

            # 只保留最近100条
            history_data = history_data[-100:]

            # 保存
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history_data, f, ensure_ascii=False, indent=2)

            print(f"优化历史已保存，共 {len(history_data)} 条记录")
        except Exception as e:
            print(f"保存优化历史失败: {e}")

    def demo_with_sample_data(self) -> None:
        """使用示例数据演示功能"""
        sample_engines = [
            ('window_tool', 156, 150, 6, 3200, 45.6),
            ('mouse_tool', 234, 230, 4, 1800, 23.4),
            ('keyboard_tool', 189, 185, 4, 2100, 18.9),
            ('vision_proxy', 78, 70, 8, 8500, 128.5),
            ('screenshot_tool', 145, 143, 2, 1200, 35.2),
            ('process_tool', 67, 60, 7, 5600, 89.3),
            ('file_tool', 89, 85, 4, 3200, 56.7),
            ('notification_tool', 45, 45, 0, 800, 12.3),
            ('clipboard_tool', 123, 120, 3, 950, 15.8),
            ('power_tool', 12, 12, 0, 600, 8.9),
        ]

        for eng_name, calls, successes, failures, resp_time, mem in sample_engines:
            metrics = EngineMetrics(engine_name=eng_name)
            metrics.call_count = calls
            metrics.success_count = successes
            metrics.failure_count = failures
            metrics.total_response_time = resp_time
            metrics.avg_response_time = resp_time / calls
            metrics.peak_memory = mem
            metrics.first_call_time = datetime.now().isoformat()
            metrics.last_call_time = datetime.now().isoformat()
            self.metrics[eng_name] = metrics

        self._save_metrics()
        print("已加载示例数据")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='智能引擎组合实时监控与自适应优化引擎')
    parser.add_argument('command', choices=['status', 'analyze', 'optimize', 'monitor', 'demo', 'combo'],
                       help='命令')
    parser.add_argument('--demo', action='store_true', help='使用示例数据')

    args = parser.parse_args()

    optimizer = EngineRealtimeOptimizer()

    if args.command == 'status':
        status = optimizer.get_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))

    elif args.command == 'demo':
        optimizer.demo_with_sample_data()
        print("示例数据已加载")

    elif args.command == 'analyze':
        analysis = optimizer.analyze_engines()
        print(json.dumps(analysis, ensure_ascii=False, indent=2))

    elif args.command == 'optimize':
        recommendations = optimizer.generate_recommendations()
        print(f"生成了 {len(recommendations)} 条优化建议:")
        for i, rec in enumerate(recommendations, 1):
            print(f"\n[{i}] {rec.engine_name} - {rec.severity.upper()}")
            print(f"    问题: {rec.description}")
            print(f"    建议: {rec.recommendation}")
            print(f"    预期: {rec.expected_improvement}")

    elif args.command == 'combo':
        combo = optimizer.get_engine_combination_analysis()
        print(json.dumps(combo, ensure_ascii=False, indent=2))

    elif args.command == 'monitor':
        if optimizer.monitoring:
            optimizer.stop_monitoring()
        else:
            optimizer.start_monitoring()


if __name__ == '__main__':
    main()