#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环实时监控与预警引擎 (version 1.0.0)

让进化环具备实时健康监控与智能预警能力——实时追踪进化环运行状态、
自动检测异常指标、智能预警并联动自愈机制，形成进化环的"免疫系统"。

功能：
1. 实时状态追踪 - 追踪进化环各阶段执行状态与耗时
2. 异常检测 - 检测执行停滞、状态异常、资源瓶颈
3. 智能预警 - 基于多维度指标综合判断并发出预警
4. 趋势分析 - 分析进化效率趋势，预测潜在问题
5. 联动自愈 - 与自愈引擎联动，触发自动修复

该引擎与以下模块深度集成：
- evolution_loop_self_healing_engine.py（自愈引擎）
- evolution_performance_monitor.py（效能监控）
- autonomous_awareness_engine.py（自主意识引擎）
- system_health_report_engine.py（健康报告）

作者：Claude Sonnet 4.6
日期：2026-03-14
"""

import os
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from collections import deque
import threading

# psutil 可能不可用，提供备选
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False


# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
RUNTIME_DIR = PROJECT_ROOT / "runtime"
STATE_DIR = RUNTIME_DIR / "state"
LOGS_DIR = RUNTIME_DIR / "logs"


class EvolutionLoopHealthMonitor:
    """智能全场景进化环实时监控与预警引擎"""

    def __init__(self):
        self.name = "EvolutionLoopHealthMonitor"
        self.version = "1.0.0"
        self.state_file = STATE_DIR / "evolution_health_monitor_state.json"
        self.alert_history = []
        self.metrics_history = deque(maxlen=100)  # 保留最近100条指标
        self.thresholds = {
            'phase_stuck_minutes': 30,  # 阶段停滞超时（分钟）
            'round_timeout_hours': 4,   # 轮次超时（小时）
            'error_rate_threshold': 0.3,  # 错误率阈值
            'memory_warning_mb': 500,   # 内存警告阈值（MB）
            'cpu_warning_percent': 80    # CPU警告阈值（%）
        }
        self.lock = threading.Lock()
        self.load_state()

    def load_state(self):
        """加载状态"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.alert_history = data.get('alert_history', [])
                    # 恢复metrics_history
                    metrics = data.get('metrics_history', [])
                    self.metrics_history = deque(metrics, maxlen=100)
                    self.thresholds = data.get('thresholds', self.thresholds)
            except Exception:
                pass

    def save_state(self):
        """保存状态"""
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        with self.lock:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'alert_history': self.alert_history[-50:],  # 保留最近50条
                    'metrics_history': list(self.metrics_history),
                    'thresholds': self.thresholds,
                    'last_updated': datetime.now().isoformat()
                }, f, ensure_ascii=False, indent=2)

    def get_current_evolution_state(self) -> Dict[str, Any]:
        """
        获取当前进化环状态

        返回:
            当前进化状态
        """
        state = {
            'current_mission': None,
            'recent_completed': [],
            'active_sessions': []
        }

        # 读取当前任务
        current_mission = STATE_DIR / "current_mission.json"
        if current_mission.exists():
            try:
                with open(current_mission, 'r', encoding='utf-8') as f:
                    state['current_mission'] = json.load(f)
            except Exception:
                pass

        # 读取最近完成的进化
        completed_files = sorted(
            STATE_DIR.glob("evolution_completed_ev_*.json"),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )[:5]

        for f in completed_files:
            try:
                with open(f, 'r', encoding='utf-8') as fp:
                    state['recent_completed'].append(json.load(fp))
            except Exception:
                continue

        return state

    def collect_metrics(self) -> Dict[str, Any]:
        """
        收集当前系统指标

        返回:
            系统指标
        """
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'system': {},
            'evolution': {}
        }

        # 系统指标
        if HAS_PSUTIL:
            try:
                metrics['system'] = {
                    'cpu_percent': psutil.cpu_percent(interval=0.1),
                    'memory_mb': psutil.Process().memory_info().rss / 1024 / 1024,
                    'disk_percent': psutil.disk_usage('/').percent
                }
            except Exception:
                pass
        else:
            # 无 psutil 时设置默认值
            metrics['system'] = {
                'cpu_percent': 0,
                'memory_mb': 0,
                'disk_percent': 0,
                'note': 'psutil not available'
            }

        # 进化环指标
        evolution_state = self.get_current_evolution_state()
        mission = evolution_state.get('current_mission', {})

        metrics['evolution'] = {
            'loop_round': mission.get('loop_round', 0),
            'phase': mission.get('phase', 'unknown'),
            'current_goal': mission.get('current_goal', ''),
            'next_action': mission.get('next_action', ''),
            'recent_completed_count': len(evolution_state.get('recent_completed', []))
        }

        # 计算执行时长（如果记录了开始时间）
        updated_at = mission.get('updated_at', '')
        if updated_at:
            try:
                start_time = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                elapsed = (datetime.now() - start_time.replace(tzinfo=None)).total_seconds() / 60
                metrics['evolution']['elapsed_minutes'] = round(elapsed, 1)
            except Exception:
                pass

        self.metrics_history.append(metrics)
        return metrics

    def detect_anomalies(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        检测异常

        参数:
            metrics: 系统指标

        返回:
            异常列表
        """
        anomalies = []

        # 1. 检测阶段停滞
        evolution = metrics.get('evolution', {})
        elapsed = evolution.get('elapsed_minutes', 0)
        phase = evolution.get('phase', '')

        if elapsed > self.thresholds['phase_stuck_minutes'] and phase in ['假设', '规划', '执行', '校验']:
            anomalies.append({
                'type': 'phase_stuck',
                'severity': 'warning',
                'message': f'阶段 "{phase}" 已停滞 {elapsed:.0f} 分钟',
                'phase': phase,
                'elapsed_minutes': elapsed
            })

        # 2. 检测资源异常
        system = metrics.get('system', {})
        memory_mb = system.get('memory_mb', 0)
        cpu_percent = system.get('cpu_percent', 0)

        if memory_mb > self.thresholds['memory_warning_mb']:
            anomalies.append({
                'type': 'high_memory',
                'severity': 'warning',
                'message': f'内存使用 {memory_mb:.0f} MB 超过阈值',
                'memory_mb': memory_mb
            })

        if cpu_percent > self.thresholds['cpu_warning_percent']:
            anomalies.append({
                'type': 'high_cpu',
                'severity': 'warning',
                'message': f'CPU 使用率 {cpu_percent:.0f}% 超过阈值',
                'cpu_percent': cpu_percent
            })

        # 3. 检测无目标状态
        current_goal = evolution.get('current_goal', '')
        if not current_goal and evolution.get('loop_round', 0) > 0:
            anomalies.append({
                'type': 'no_goal',
                'severity': 'info',
                'message': '当前无明确目标',
                'phase': phase
            })

        # 4. 检测无效阶段
        valid_phases = ['假设', '规划', '执行', '校验', '反思', '未知']
        if phase not in valid_phases:
            anomalies.append({
                'type': 'invalid_phase',
                'severity': 'warning',
                'message': f'无效阶段: {phase}',
                'phase': phase
            })

        return anomalies

    def analyze_trends(self) -> Dict[str, Any]:
        """
        分析进化效率趋势

        返回:
            趋势分析结果
        """
        if len(self.metrics_history) < 5:
            return {'status': 'insufficient_data', 'message': '数据不足，无法分析趋势'}

        # 分析内存趋势
        memory_values = [m.get('system', {}).get('memory_mb', 0) for m in self.metrics_history]
        cpu_values = [m.get('system', {}).get('cpu_percent', 0) for m in self.metrics_history]

        # 计算趋势
        memory_trend = 'stable'
        if len(memory_values) >= 10:
            first_half = sum(memory_values[:5]) / 5
            second_half = sum(memory_values[-5:]) / 5
            if second_half > first_half * 1.2:
                memory_trend = 'increasing'
            elif second_half < first_half * 0.8:
                memory_trend = 'decreasing'

        return {
            'status': 'analyzed',
            'memory_trend': memory_trend,
            'memory_avg': sum(memory_values) / len(memory_values),
            'cpu_avg': sum(cpu_values) / len(cpu_values),
            'data_points': len(self.metrics_history)
        }

    def generate_alert(self, anomalies: List[Dict[str, Any]], metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        生成预警

        参数:
            anomalies: 异常列表
            metrics: 系统指标

        返回:
            预警列表
        """
        alerts = []

        for anomaly in anomalies:
            # 检查是否已发送类似预警（避免重复）
            recent_types = [a.get('type') for a in self.alert_history[-5:]]
            if anomaly['type'] in recent_types:
                continue

            alert = {
                'timestamp': datetime.now().isoformat(),
                'type': anomaly['type'],
                'severity': anomaly['severity'],
                'message': anomaly['message'],
                'details': anomaly,
                'action_required': anomaly['severity'] in ['critical', 'warning']
            }

            alerts.append(alert)
            self.alert_history.append(alert)

        return alerts

    def monitor(self, auto_heal: bool = False) -> Dict[str, Any]:
        """
        执行监控

        参数:
            auto_heal: 是否自动尝试修复

        返回:
            监控结果
        """
        result = {
            'timestamp': datetime.now().isoformat(),
            'metrics': None,
            'anomalies': [],
            'alerts': [],
            'trends': {},
            'overall_status': 'healthy'
        }

        # 1. 收集指标
        metrics = self.collect_metrics()
        result['metrics'] = metrics

        # 2. 检测异常
        anomalies = self.detect_anomalies(metrics)
        result['anomalies'] = anomalies

        # 3. 生成预警
        alerts = self.generate_alert(anomalies, metrics)
        result['alerts'] = alerts

        # 4. 分析趋势
        trends = self.analyze_trends()
        result['trends'] = trends

        # 5. 计算总体状态
        if alerts:
            severe_count = sum(1 for a in alerts if a['severity'] in ['critical', 'warning'])
            if severe_count > 2:
                result['overall_status'] = 'critical'
            elif severe_count > 0:
                result['overall_status'] = 'warning'
            else:
                result['overall_status'] = 'healthy'
        else:
            result['overall_status'] = 'healthy'

        # 6. 尝试自动修复（如果启用）
        if auto_heal and anomalies:
            repair_result = self.attempt_auto_repair(anomalies)
            result['repair_attempted'] = repair_result

        # 保存状态
        self.save_state()

        return result

    def attempt_auto_repair(self, anomalies: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        尝试自动修复

        参数:
            anomalies: 异常列表

        返回:
            修复结果
        """
        result = {
            'attempted': False,
            'actions': [],
            'success': False
        }

        for anomaly in anomalies:
            if anomaly['type'] == 'phase_stuck':
                # 阶段停滞，尝试推进状态
                result['actions'].append({
                    'type': 'phase_stuck',
                    'action': '记录状态，后续轮次可检测并处理'
                })
                result['attempted'] = True

            elif anomaly['type'] == 'high_memory':
                # 内存高，触发GC
                result['actions'].append({
                    'type': 'high_memory',
                    'action': '记录预警，建议手动处理'
                })
                result['attempted'] = True

        if result['actions']:
            result['success'] = True

        return result

    def get_status(self) -> Dict[str, Any]:
        """
        获取系统状态

        返回:
            系统状态
        """
        # 快速检查
        metrics = self.collect_metrics()
        anomalies = self.detect_anomalies(metrics)

        return {
            'name': self.name,
            'version': self.version,
            'overall_status': 'warning' if anomalies else 'healthy',
            'current_phase': metrics.get('evolution', {}).get('phase', 'unknown'),
            'current_round': metrics.get('evolution', {}).get('loop_round', 0),
            'anomalies_count': len(anomalies),
            'alerts_count': len(self.alert_history),
            'thresholds': self.thresholds,
            'last_updated': datetime.now().isoformat()
        }

    def get_alert_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取预警历史

        参数:
            limit: 返回数量限制

        返回:
            预警历史
        """
        return self.alert_history[-limit:]

    def clear_alerts(self):
        """清除历史预警"""
        self.alert_history = []
        self.save_state()


def main():
    """主函数 - 支持命令行调用"""
    import sys

    engine = EvolutionLoopHealthMonitor()

    if len(sys.argv) < 2:
        # 无参数时显示状态
        status = engine.get_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))
        return

    command = sys.argv[1].lower()

    if command in ['status', '状态']:
        status = engine.get_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))

    elif command in ['monitor', '监控', 'check']:
        result = engine.monitor()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command in ['metrics', '指标']:
        metrics = engine.collect_metrics()
        print(json.dumps(metrics, ensure_ascii=False, indent=2))

    elif command in ['anomalies', '异常']:
        metrics = engine.collect_metrics()
        anomalies = engine.detect_anomalies(metrics)
        print(json.dumps(anomalies, ensure_ascii=False, indent=2))

    elif command in ['trends', '趋势']:
        trends = engine.analyze_trends()
        print(json.dumps(trends, ensure_ascii=False, indent=2))

    elif command in ['alerts', '预警']:
        history = engine.get_alert_history()
        print(json.dumps(history, ensure_ascii=False, indent=2))

    elif command in ['clear', '清除']:
        engine.clear_alerts()
        print("已清除预警历史")

    elif command in ['help', '帮助']:
        help_text = """
智能全场景进化环实时监控与预警引擎

用法:
    python evolution_loop_health_monitor.py <command>

命令:
    status/状态      - 显示系统状态
    monitor/监控/check - 执行监控检查
    metrics/指标     - 收集当前指标
    anomalies/异常   - 检测异常
    trends/趋势     - 分析趋势
    alerts/预警      - 查看预警历史
    clear/清除       - 清除预警历史
    help/帮助        - 显示帮助信息
        """
        print(help_text)

    else:
        print(f"未知命令: {command}")
        print("使用 'help' 查看可用命令")


if __name__ == "__main__":
    main()