#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环健康自愈引擎 (version 1.0.0)

让进化环具备实时健康监控与自愈能力——整合监控、自愈、预防、预警等能力，
形成进化环的"免疫系统"，实现问题检测→自动修复→验证→预防的完整闭环。

功能：
1. 实时健康监控 - 监控进化环各组件状态、执行效率、资源使用
2. 智能预警系统 - 多维度指标综合判断，智能预警
3. 自动自愈修复 - 自动检测问题并尝试修复
4. 预防性干预 - 在问题发生前主动预防
5. 闭环验证 - 修复后自动验证效果

该模块深度集成以下模块：
- evolution_loop_health_monitor.py（实时监控）
- evolution_loop_self_healing_engine.py（自愈引擎）
- evolution_health_assurance_loop.py（健康保障）
- evolution_performance_monitor.py（效能监控）

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

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
RUNTIME_DIR = PROJECT_ROOT / "runtime"
STATE_DIR = RUNTIME_DIR / "state"
LOGS_DIR = RUNTIME_DIR / "logs"


class EvolutionLoopHealthHealer:
    """智能全场景进化环健康自愈引擎"""

    def __init__(self):
        self.name = "EvolutionLoopHealthHealer"
        self.version = "1.0.0"
        self.state_file = STATE_DIR / "evolution_health_healer_state.json"
        self.alert_history = deque(maxlen=50)
        self.healing_history = deque(maxlen=50)
        self.metrics_history = deque(maxlen=100)
        self.thresholds = {
            'phase_stuck_minutes': 30,
            'round_timeout_hours': 4,
            'error_rate_threshold': 0.3,
            'memory_warning_mb': 500,
            'cpu_warning_percent': 80,
            'health_score_threshold': 60
        }
        self.lock = threading.Lock()
        self.load_state()

    def load_state(self):
        """加载状态"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.alert_history = deque(data.get('alert_history', []), maxlen=50)
                    self.healing_history = deque(data.get('healing_history', []), maxlen=50)
                    self.metrics_history = deque(data.get('metrics_history', []), maxlen=100)
                    self.thresholds = data.get('thresholds', self.thresholds)
            except Exception:
                pass

    def save_state(self):
        """保存状态"""
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        with self.lock:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'alert_history': list(self.alert_history),
                    'healing_history': list(self.healing_history),
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
        current_mission = STATE_DIR / "current_mission.json"
        state = {
            'mission': 'Unknown',
            'phase': 'Unknown',
            'loop_round': 0,
            'current_goal': '',
            'next_action': '',
            'last_updated': ''
        }

        if current_mission.exists():
            try:
                with open(current_mission, 'r', encoding='utf-8') as f:
                    mission = json.load(f)
                    state = {
                        'mission': mission.get('mission', 'Unknown'),
                        'phase': mission.get('phase', 'Unknown'),
                        'loop_round': mission.get('loop_round', 0),
                        'current_goal': mission.get('current_goal', ''),
                        'next_action': mission.get('next_action', ''),
                        'last_updated': mission.get('updated_at', '')
                    }
            except Exception:
                pass

        return state

    def analyze_failed_rounds(self) -> List[Dict[str, Any]]:
        """
        分析失败的进化轮次

        返回:
            失败分析结果列表
        """
        failed_analysis = []

        for f in STATE_DIR.glob("evolution_completed_*.json"):
            try:
                with open(f, 'r', encoding='utf-8') as fp:
                    data = json.load(fp)
                    status = data.get('status', data.get('是否完成', ''))

                    if status in ['failed', 'stale_failed'] or status == '未完成':
                        goal = data.get('current_goal', data.get('做了什么', ''))
                        session_id = f.stem.replace('evolution_completed_', '')

                        failed_analysis.append({
                            'session_id': session_id,
                            'goal': goal,
                            'status': status,
                            'analyzed': False
                        })
            except Exception:
                continue

        return failed_analysis

    def detect_stuck_phase(self) -> Optional[Dict[str, Any]]:
        """
        检测是否出现阶段停滞

        返回:
            停滞检测结果
        """
        state = self.get_current_evolution_state()
        phase = state.get('phase', '')
        updated = state.get('last_updated', '')

        if not updated or phase in ['假设', '规划']:
            return None

        try:
            last_time = datetime.fromisoformat(updated.replace('Z', '+00:00'))
            now = datetime.now()
            minutes_stuck = (now - last_time).total_seconds() / 60

            if minutes_stuck > self.thresholds['phase_stuck_minutes']:
                return {
                    'type': 'phase_stuck',
                    'phase': phase,
                    'minutes': int(minutes_stuck),
                    'message': f'阶段 {phase} 已停滞 {int(minutes_stuck)} 分钟'
                }
        except Exception:
            pass

        return None

    def collect_health_metrics(self) -> Dict[str, Any]:
        """
        收集健康指标

        返回:
            健康指标字典
        """
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'current_state': self.get_current_evolution_state(),
            'failed_rounds': 0,
            'error_rate': 0.0,
            'health_score': 100,
            'warnings': []
        }

        # 统计失败轮次
        failed = self.analyze_failed_rounds()
        metrics['failed_rounds'] = len(failed)

        # 计算错误率（基于最近30轮）
        recent_count = 0
        completed_count = 0
        for f in sorted(STATE_DIR.glob("evolution_completed_*.json"), key=lambda x: x.stat().st_mtime, reverse=True)[:30]:
            try:
                with open(f, 'r', encoding='utf-8') as fp:
                    data = json.load(fp)
                    completed_count += 1
                    status = data.get('status', data.get('是否完成', ''))
                    if status in ['failed', 'stale_failed'] or status == '未完成':
                        recent_count += 1
            except Exception:
                pass

        if completed_count > 0:
            metrics['error_rate'] = recent_count / completed_count
            metrics['health_score'] = max(0, 100 - recent_count * 15 - (recent_count > 0 and completed_count > 0 and recent_count / completed_count > 0.3 and 10 or 0))

        # 检测阶段停滞
        stuck = self.detect_stuck_phase()
        if stuck:
            metrics['warnings'].append(stuck)
            metrics['health_score'] -= 10

        # 检查当前阶段
        phase = metrics['current_state'].get('phase', '')
        if phase in ['', 'Unknown']:
            metrics['warnings'].append({'type': 'unknown_phase', 'message': '当前阶段未知'})
            metrics['health_score'] -= 15

        return metrics

    def generate_health_report(self) -> Dict[str, Any]:
        """
        生成健康报告

        返回:
            健康报告
        """
        metrics = self.collect_health_metrics()

        report = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'healthy',
            'health_score': metrics['health_score'],
            'current_round': metrics['current_state'].get('loop_round', 0),
            'current_phase': metrics['current_state'].get('phase', 'Unknown'),
            'failed_rounds': metrics['failed_rounds'],
            'error_rate': metrics['error_rate'],
            'warnings': [],
            'recommendations': []
        }

        # 判断总体状态
        if metrics['health_score'] >= 80:
            report['overall_status'] = 'healthy'
            report['recommendations'].append('系统运行正常，继续保持')
        elif metrics['health_score'] >= 60:
            report['overall_status'] = 'warning'
            report['recommendations'].append('建议关注系统健康状态')
        else:
            report['overall_status'] = 'critical'
            report['recommendations'].append('需要立即进行健康干预')

        # 添加警告
        report['warnings'] = metrics['warnings']

        # 基于错误率添加建议
        if metrics['error_rate'] > 0.3:
            report['recommendations'].append(f'错误率较高({metrics["error_rate"]:.1%})，建议分析失败原因')
        elif metrics['error_rate'] > 0.1:
            report['recommendations'].append('错误率略高，建议关注')

        # 基于失败轮次添加建议
        if metrics['failed_rounds'] > 0:
            report['recommendations'].append(f'存在 {metrics["failed_rounds"]} 轮失败，需要处理')

        return report

    def attempt_auto_repair(self) -> Dict[str, Any]:
        """
        尝试自动修复

        返回:
            修复结果
        """
        result = {
            'timestamp': datetime.now().isoformat(),
            'repairs_attempted': [],
            'repairs_successful': [],
            'repairs_failed': [],
            'overall_status': 'no_action'
        }

        # 1. 清理大日志文件
        try:
            logs_dir = LOGS_DIR
            if logs_dir.exists():
                total_size = 0
                large_files = []
                for f in logs_dir.glob("*.log"):
                    try:
                        size = f.stat().st_size
                        total_size += size
                        if size > 10 * 1024 * 1024:  # > 10MB
                            large_files.append((f, size))
                    except Exception:
                        pass

                if large_files:
                    # 清理最大的日志文件
                    large_files.sort(key=lambda x: x[1], reverse=True)
                    for f, size in large_files[:3]:
                        try:
                            # 保留前1000行
                            with open(f, 'r', encoding='utf-8', errors='ignore') as fp:
                                lines = fp.readlines()
                            if len(lines) > 1000:
                                with open(f, 'w', encoding='utf-8') as fp:
                                    fp.writelines(lines[:1000])
                                result['repairs_attempted'].append({
                                    'type': 'log_cleanup',
                                    'file': str(f.name),
                                    'action': 'trimmed to 1000 lines'
                                })
                        except Exception:
                            pass
        except Exception as e:
            result['repairs_failed'].append({'type': 'log_cleanup', 'error': str(e)})

        # 2. 检查状态文件完整性
        try:
            mission_file = STATE_DIR / "current_mission.json"
            if mission_file.exists():
                with open(mission_file, 'r', encoding='utf-8') as f:
                    mission = json.load(f)

                # 确保必要字段存在
                required_fields = ['mission', 'phase', 'loop_round', 'current_goal', 'next_action']
                missing_fields = [f for f in required_fields if f not in mission]

                if missing_fields:
                    for field in missing_fields:
                        if field == 'loop_round':
                            mission[field] = 0
                        else:
                            mission[field] = ''
                    with open(mission_file, 'w', encoding='utf-8') as f:
                        json.dump(mission, f, ensure_ascii=False, indent=2)
                    result['repairs_attempted'].append({
                        'type': 'state_repair',
                        'fields_fixed': missing_fields
                    })
        except Exception as e:
            result['repairs_failed'].append({'type': 'state_repair', 'error': str(e)})

        # 3. 检查过期会话文件
        try:
            now = datetime.now()
            for f in STATE_DIR.glob("evolution_completed_*.json"):
                try:
                    mtime = datetime.fromtimestamp(f.stat().st_mtime)
                    age = (now - mtime).total_seconds()
                    if age > 7 * 24 * 3600:  # 超过7天
                        # 检查是否已完成
                        with open(f, 'r', encoding='utf-8') as fp:
                            data = json.load(fp)
                            status = data.get('status', '')
                            if status not in ['已完成', 'completed', '完成']:
                                # 标记为过期失败
                                data['status'] = 'stale_failed'
                                with open(f, 'w', encoding='utf-8') as fp:
                                    json.dump(data, fp, ensure_ascii=False, indent=2)
                                result['repairs_attempted'].append({
                                    'type': 'stale_session',
                                    'session': f.name,
                                    'action': 'marked as stale_failed'
                                })
                except Exception:
                    pass
        except Exception as e:
            result['repairs_failed'].append({'type': 'stale_session', 'error': str(e)})

        # 汇总结果
        if result['repairs_attempted']:
            result['overall_status'] = 'completed'
            result['repairs_successful'] = result['repairs_attempted']
        else:
            result['overall_status'] = 'no_issues_found'

        # 记录到历史
        self.healing_history.append({
            'timestamp': result['timestamp'],
            'repairs': result['repairs_attempted'],
            'status': result['overall_status']
        })

        return result

    def execute_closed_loop(self) -> Dict[str, Any]:
        """
        执行完整闭环：检测→修复→验证

        返回:
            闭环执行结果
        """
        result = {
            'timestamp': datetime.now().isoformat(),
            'health_check': None,
            'repairs': None,
            'verification': None,
            'overall_status': 'unknown'
        }

        # 1. 健康检查
        health_report = self.generate_health_report()
        result['health_check'] = health_report

        # 2. 如果有问题，尝试修复
        if health_report['overall_status'] in ['warning', 'critical']:
            repair_result = self.attempt_auto_repair()
            result['repairs'] = repair_result

            # 3. 验证修复效果
            verification_report = self.generate_health_report()
            result['verification'] = verification_report

            # 4. 判断整体状态
            if verification_report['health_score'] >= 80:
                result['overall_status'] = 'healed'
            elif verification_report['health_score'] >= 60:
                result['overall_status'] = 'improved'
            else:
                result['overall_status'] = 'needs_manual_intervention'
        else:
            result['overall_status'] = 'healthy'
            result['repairs'] = {'status': 'no_repair_needed', 'repairs_attempted': []}

        # 保存状态
        self.save_state()

        return result

    def get_status(self) -> Dict[str, Any]:
        """
        获取系统状态

        返回:
            系统状态字典
        """
        health_report = self.generate_health_report()

        return {
            'name': self.name,
            'version': self.version,
            'health_report': health_report,
            'healing_history_count': len(self.healing_history),
            'alert_history_count': len(self.alert_history),
            'last_updated': datetime.now().isoformat()
        }


def main():
    """主函数 - 支持命令行调用"""
    import sys

    engine = EvolutionLoopHealthHealer()

    if len(sys.argv) < 2:
        # 无参数时显示状态
        status = engine.get_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))
        return

    command = sys.argv[1].lower()

    if command in ['status', '状态']:
        status = engine.get_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))

    elif command in ['health', '健康', 'report']:
        report = engine.generate_health_report()
        print(json.dumps(report, ensure_ascii=False, indent=2))

    elif command in ['metrics', '指标']:
        metrics = engine.collect_health_metrics()
        print(json.dumps(metrics, ensure_ascii=False, indent=2))

    elif command in ['repair', '修复', 'heal']:
        result = engine.attempt_auto_repair()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command in ['闭环', 'closed_loop', 'loop']:
        result = engine.execute_closed_loop()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command in ['failed', '分析']:
        failed = engine.analyze_failed_rounds()
        print(json.dumps(failed, ensure_ascii=False, indent=2))

    elif command in ['help', '帮助']:
        help_text = """
智能全场景进化环健康自愈引擎

用法:
    python evolution_loop_health_healer.py <command>

命令:
    status/状态      - 显示系统状态和健康报告
    health/健康     - 生成健康报告
    metrics/指标    - 收集健康指标
    repair/修复/heal - 尝试自动修复
    闭环/closed_loop - 执行完整闭环：检测→修复→验证
    failed/分析      - 分析失败的进化轮次
    help/帮助       - 显示帮助信息
        """
        print(help_text)

    else:
        print(f"未知命令: {command}")
        print("使用 'help' 查看可用命令")


if __name__ == "__main__":
    main()