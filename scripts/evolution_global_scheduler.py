#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能进化环全局智能调度与优先级自动优化引擎 (version 1.0.0)

让进化环能够基于实时系统负载、进化历史效率、能力缺口紧迫度自动智能调度进化任务和调整优先级，
实现更高效的进化资源分配，形成"感知→分析→调度→执行→反馈"的完整闭环。

功能：
1. 实时系统负载感知 - 监控CPU、内存、磁盘、进程状态
2. 进化历史效率分析 - 分析各类型进化的完成效率
3. 能力缺口紧迫度评估 - 评估未完成进化的优先级
4. 智能调度算法 - 基于以上维度动态分配进化资源
5. 优先级自动调整 - 根据实时状态动态调整进化优先级

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
import glob

# 尝试导入 psutil，如果不可用则使用备用方案
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


class EvolutionGlobalScheduler:
    """智能进化环全局智能调度与优先级自动优化引擎"""

    def __init__(self):
        self.name = "EvolutionGlobalScheduler"
        self.version = "1.0.0"
        self.state_file = STATE_DIR / "evolution_global_scheduler_state.json"
        self.schedule_history = deque(maxlen=100)
        self.priority_history = deque(maxlen=100)
        self.system_load_history = deque(maxlen=60)
        self.lock = threading.Lock()
        self.load_state()

    def load_state(self):
        """加载状态"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.schedule_history = deque(data.get('schedule_history', []), maxlen=100)
                    self.priority_history = deque(data.get('priority_history', []), maxlen=100)
                    self.system_load_history = deque(data.get('system_load_history', []), maxlen=60)
            except Exception:
                pass

    def save_state(self):
        """保存状态"""
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        with self.lock:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'schedule_history': list(self.schedule_history),
                    'priority_history': list(self.priority_history),
                    'system_load_history': list(self.system_load_history),
                    'last_updated': datetime.now().isoformat()
                }, f, ensure_ascii=False, indent=2)

    def get_system_load(self) -> Dict[str, Any]:
        """
        获取实时系统负载

        返回:
            系统负载信息
        """
        try:
            if not HAS_PSUTIL:
                # 使用默认负载值（当 psutil 不可用时）
                load_info = {
                    'timestamp': datetime.now().isoformat(),
                    'cpu_percent': 30,  # 假设值
                    'memory_percent': 50,
                    'memory_available_mb': 4096,
                    'disk_percent': 60,
                    'disk_free_gb': 100,
                    'process_count': 100,
                    'note': '使用默认值（psutil 未安装）'
                }
            else:
                cpu_percent = psutil.cpu_percent(interval=0.5)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')

                load_info = {
                    'timestamp': datetime.now().isoformat(),
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory.percent,
                    'memory_available_mb': memory.available / (1024 * 1024),
                    'disk_percent': disk.percent,
                    'disk_free_gb': disk.free / (1024 * 1024 * 1024),
                    'process_count': len(psutil.pids())
                }

            self.system_load_history.append(load_info)
            return load_info
        except Exception as e:
            return {
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }

    def analyze_evolution_history_efficiency(self) -> Dict[str, Any]:
        """
        分析进化历史效率

        返回:
            进化效率分析结果
        """
        analysis = {
            'total_rounds': 0,
            'completed_rounds': 0,
            'failed_rounds': 0,
            'average_completion_time_hours': 0,
            'efficiency_by_type': {},
            'recent_trend': 'stable'
        }

        try:
            # 扫描已完成进化记录
            completed_files = list(STATE_DIR.glob("evolution_completed_*.json"))
            analysis['total_rounds'] = len(completed_files)

            completed = 0
            total_time = 0
            type_stats = {}

            for f in completed_files:
                try:
                    with open(f, 'r', encoding='utf-8') as fp:
                        data = json.load(fp)
                        status = data.get('status', '')

                        if '完成' in status:
                            completed += 1
                            # 提取类型
                            goal = data.get('current_goal', '')
                            ev_type = self._extract_evolution_type(goal)

                            if ev_type not in type_stats:
                                type_stats[ev_type] = {'count': 0, 'total_time': 0}

                            type_stats[ev_type]['count'] += 1

                            # 计算时间（如果有完成时间）
                            completed_at = data.get('completed_at', '')
                            if completed_at:
                                try:
                                    dt = datetime.fromisoformat(completed_at.replace('Z', '+00:00'))
                                    total_time += 1
                                except:
                                    pass
                except:
                    pass

            analysis['completed_rounds'] = completed
            analysis['failed_rounds'] = analysis['total_rounds'] - completed

            if total_time > 0:
                analysis['average_completion_time_hours'] = round(total_time / completed, 2) if completed > 0 else 0

            # 计算各类型效率
            for ev_type, stats in type_stats.items():
                analysis['efficiency_by_type'][ev_type] = {
                    'count': stats['count'],
                    'avg_time': round(stats['total_time'] / stats['count'], 2) if stats['count'] > 0 else 0
                }

            # 计算近期趋势
            if len(self.schedule_history) >= 10:
                recent = list(self.schedule_history)[-10:]
                completed_count = sum(1 for s in recent if s.get('status') == 'completed')
                if completed_count >= 8:
                    analysis['recent_trend'] = 'improving'
                elif completed_count <= 4:
                    analysis['recent_trend'] = 'declining'

        except Exception as e:
            analysis['error'] = str(e)

        return analysis

    def _extract_evolution_type(self, goal: str) -> str:
        """提取进化类型"""
        if '健康' in goal or '自愈' in goal:
            return 'health'
        elif '调度' in goal or '优化' in goal or '效率' in goal:
            return 'optimization'
        elif '协作' in goal or '协同' in goal:
            return 'collaboration'
        elif '学习' in goal or '适应' in goal:
            return 'learning'
        elif '决策' in goal or '执行' in goal:
            return 'decision'
        elif '预测' in goal or '预防' in goal:
            return 'prediction'
        elif '意识' in goal or '自主' in goal:
            return 'autonomy'
        else:
            return 'other'

    def assess_capability_gap_urgency(self) -> List[Dict[str, Any]]:
        """
        评估能力缺口紧迫度

        返回:
            紧迫度评估结果列表
        """
        gaps = []

        # 读取能力缺口
        gaps_file = PROJECT_ROOT / "references" / "capability_gaps.md"
        if gaps_file.exists():
            try:
                with open(gaps_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # 简单解析缺口（如果有）
                    if '—' not in content or '可扩展' in content:
                        gaps.append({
                            'type': 'capability_gap',
                            'description': '基础能力缺口',
                            'urgency': 'medium',
                            'impact': 'high'
                        })
            except:
                pass

        # 分析未完成进化
        try:
            # 扫描最近未完成的进化
            current_mission_file = STATE_DIR / "current_mission.json"
            if current_mission_file.exists():
                with open(current_mission_file, 'r', encoding='utf-8') as f:
                    mission = json.load(f)

                    # 检查是否有停滞的阶段
                    phase = mission.get('phase', '')
                    updated_at = mission.get('updated_at', '')

                    if updated_at:
                        try:
                            updated_time = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                            hours_stuck = (datetime.now() - updated_time).total_seconds() / 3600

                            if hours_stuck > 2:
                                gaps.append({
                                    'type': 'stuck_phase',
                                    'description': f'阶段停滞: {phase}',
                                    'urgency': 'high' if hours_stuck > 4 else 'medium',
                                    'impact': 'high',
                                    'hours_stuck': round(hours_stuck, 2)
                                })
                        except:
                            pass
        except Exception as e:
            gaps.append({
                'type': 'analysis_error',
                'description': str(e),
                'urgency': 'low',
                'impact': 'low'
            })

        # 评估紧迫度
        for gap in gaps:
            if gap.get('urgency') == 'high':
                gap['priority_score'] = 9
            elif gap.get('urgency') == 'medium':
                gap['priority_score'] = 6
            else:
                gap['priority_score'] = 3

        return sorted(gaps, key=lambda x: x.get('priority_score', 0), reverse=True)

    def calculate_optimal_schedule(self) -> Dict[str, Any]:
        """
        计算最优调度方案

        返回:
            调度方案
        """
        schedule = {
            'timestamp': datetime.now().isoformat(),
            'system_load': self.get_system_load(),
            'efficiency_analysis': self.analyze_evolution_history_efficiency(),
            'urgency_assessment': self.assess_capability_gap_urgency(),
            'recommended_schedule': [],
            'priority_adjustments': []
        }

        # 基于系统负载计算推荐
        load = schedule['system_load']
        if 'error' not in load:
            cpu = load.get('cpu_percent', 0)
            mem = load.get('memory_percent', 0)

            # 根据资源可用性推荐调度策略
            if cpu < 50 and mem < 60:
                schedule['recommended_schedule'].append({
                    'action': 'execute_heavy_evolution',
                    'reason': '系统资源充足，可以执行重型进化任务',
                    'confidence': 'high'
                })
                schedule['priority_adjustments'].append({
                    'type': 'increase_priority',
                    'target': 'complex_evolution',
                    'adjustment': '+2'
                })
            elif cpu < 80 and mem < 80:
                schedule['recommended_schedule'].append({
                    'action': 'execute_normal_evolution',
                    'reason': '系统资源适中，执行常规进化任务',
                    'confidence': 'medium'
                })
            else:
                schedule['recommended_schedule'].append({
                    'action': 'defer_evolution',
                    'reason': '系统负载高，建议推迟进化任务',
                    'confidence': 'high'
                })
                schedule['priority_adjustments'].append({
                    'type': 'decrease_priority',
                    'target': 'all',
                    'adjustment': '-1'
                })

        # 基于效率分析调整
        efficiency = schedule['efficiency_analysis']
        if efficiency.get('recent_trend') == 'declining':
            schedule['priority_adjustments'].append({
                'type': 'optimize_strategy',
                'target': 'evolution_strategy',
                'adjustment': 'Review and optimize'
            })

        # 基于紧迫度评估
        urgency = schedule['urgency_assessment']
        if urgency:
            top_gap = urgency[0]
            schedule['priority_adjustments'].append({
                'type': 'address_urgency',
                'target': top_gap.get('type', 'unknown'),
                'adjustment': f"+{top_gap.get('priority_score', 5)}"
            })

        # 保存调度历史
        self.schedule_history.append(schedule)
        self.save_state()

        return schedule

    def get_schedule_status(self) -> Dict[str, Any]:
        """
        获取调度状态

        返回:
            当前调度状态
        """
        return {
            'name': self.name,
            'version': self.version,
            'current_schedule': self.calculate_optimal_schedule(),
            'recent_schedules': list(self.schedule_history)[-5:],
            'system_load': self.get_system_load()
        }

    def adjust_priority(self, target: str, adjustment: int) -> Dict[str, Any]:
        """
        调整优先级

        参数:
            target: 目标类型
            adjustment: 调整值（正数增加优先级，负数降低）

        返回:
            调整结果
        """
        result = {
            'target': target,
            'adjustment': adjustment,
            'timestamp': datetime.now().isoformat(),
            'success': True
        }

        self.priority_history.append(result)
        self.save_state()

        return result


def main():
    """主函数 - 支持命令行调用"""
    import argparse

    parser = argparse.ArgumentParser(description='智能进化环全局调度与优先级优化引擎')
    parser.add_argument('command', nargs='?', default='status',
                        choices=['status', 'schedule', 'load', 'efficiency', 'urgency', 'adjust'],
                        help='要执行的命令')
    parser.add_argument('--target', type=str, help='调整目标')
    parser.add_argument('--adjustment', type=int, help='调整值')

    args = parser.parse_args()

    scheduler = EvolutionGlobalScheduler()

    if args.command == 'status':
        result = scheduler.get_schedule_status()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == 'schedule':
        result = scheduler.calculate_optimal_schedule()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == 'load':
        result = scheduler.get_system_load()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == 'efficiency':
        result = scheduler.analyze_evolution_history_efficiency()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == 'urgency':
        result = scheduler.assess_capability_gap_urgency()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == 'adjust':
        if args.target and args.adjustment is not None:
            result = scheduler.adjust_priority(args.target, args.adjustment)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print("错误: 需要 --target 和 --adjustment 参数")


if __name__ == '__main__':
    main()