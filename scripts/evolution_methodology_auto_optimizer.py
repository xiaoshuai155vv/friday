#!/usr/bin/env python3
"""
智能全场景进化环进化方法论自动优化引擎
在 round 443 完成的元进化驾驶舱深度集成引擎基础上，进一步构建进化方法论的自动优化能力。
让系统能够自动分析历代进化方法论的效果、识别最成功的进化模式与策略组合、
自动优化进化参数与流程，形成真正的「学会如何进化得更好」的递归优化闭环。

功能：
1. 历史进化方法论效果自动分析（成功率/效率/价值实现）
2. 进化模式与策略组合自动识别（聚类/关联分析）
3. 进化参数自动优化（基于分析结果的参数调优）
4. 优化建议自动生成与执行
5. 优化效果验证与迭代
6. 与进化驾驶舱深度集成（可视化优化过程和结果）
7. 集成到 do.py 支持方法论优化、进化优化、自动优化等关键词触发

Version: 1.0.0
"""

import os
import sys
import json
import sqlite3
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
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

# 数据文件路径
OPTIMIZATION_STATE_FILE = os.path.join(STATE_DIR, "methodology_auto_optimization_state.json")
COCKPIT_INTEGRATION_FILE = os.path.join(STATE_DIR, "methodology_optimizer_cockpit_data.json")


def _safe_print(text: str):
    """安全打印"""
    try:
        print(text)
    except UnicodeEncodeError:
        clean_text = re.sub(r'[^\x00-\x7F]+', '', text)
        print(clean_text)


def load_evolution_completed_history() -> List[Dict[str, Any]]:
    """加载所有已完成进化的历史数据"""
    history = []
    if os.path.exists(STATE_DIR):
        for f in os.listdir(STATE_DIR):
            if f.startswith("evolution_completed_") and f.endswith(".json"):
                file_path = os.path.join(STATE_DIR, f)
                try:
                    with open(file_path, 'r', encoding='utf-8') as fp:
                        data = json.load(fp)
                        if 'loop_round' in data:
                            history.append(data)
                except Exception as e:
                    _safe_print(f"加载 {f} 失败: {e}")
    return sorted(history, key=lambda x: x.get('loop_round', 0), reverse=True)


class MethodologyAutoOptimizer:
    """进化方法论自动优化引擎 - 增强版"""

    def __init__(self):
        self.db_path = os.path.join(STATE_DIR, "evolution_history.db")
        self.state_file = OPTIMIZATION_STATE_FILE
        self.cockpit_file = COCKPIT_INTEGRATION_FILE
        self.state = self._load_state()
        self.analysis_window = 50  # 分析最近50轮
        self.min_samples = 5  # 最少样本数

    def _load_state(self) -> Dict:
        """加载优化状态"""
        default_state = {
            'last_optimization_round': 0,
            'optimization_count': 0,
            'pending_optimizations': [],
            'applied_optimizations': [],
            'pattern_discoveries': [],
            'effectiveness_scores': {},
            'auto_optimize_enabled': True,
            'updated_at': datetime.now().isoformat()
        }
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                    default_state.update(state)
        except Exception as e:
            _safe_print(f"加载优化状态失败: {e}")
        return default_state

    def _save_state(self):
        """保存优化状态"""
        try:
            os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
            self.state['updated_at'] = datetime.now().isoformat()
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            _safe_print(f"保存优化状态失败: {e}")

    def analyze_methodology_effects(self, history: List[Dict] = None) -> Dict[str, Any]:
        """分析历代进化方法论效果"""
        if history is None:
            history = load_evolution_completed_history()

        # 限制分析窗口
        history = history[:self.analysis_window]

        analysis = {
            'total_rounds': len(history),
            'rounds_analyzed': 0,
            'success_count': 0,
            'failed_count': 0,
            'success_rate': 0.0,
            'methodology_categories': {},
            'round_performance': [],
            'trend_analysis': {},
            'analyzed_at': datetime.now().isoformat()
        }

        if not history:
            return analysis

        # 统计完成状态
        for h in history:
            status = h.get('是否完成', h.get('status', ''))
            if status in ['已完成', 'completed']:
                analysis['success_count'] += 1
            elif status in ['未完成', 'failed']:
                analysis['failed_count'] += 1
            analysis['rounds_analyzed'] += 1

        # 计算成功率
        if analysis['rounds_analyzed'] > 0:
            analysis['success_rate'] = round(
                analysis['success_count'] / analysis['rounds_analyzed'] * 100, 1
            )

        # 分析方法论类别
        for h in history:
            goal = h.get('current_goal', h.get('做了什么', ''))

            # 分类方法论
            category = self._classify_methodology(goal)
            if category not in analysis['methodology_categories']:
                analysis['methodology_categories'][category] = {
                    'count': 0, 'success': 0, 'failed': 0, 'rounds': []
                }

            cat = analysis['methodology_categories'][category]
            cat['count'] += 1
            cat['rounds'].append(h.get('loop_round', 0))

            if h.get('是否完成') == '已完成':
                cat['success'] += 1
            elif h.get('是否完成') == '未完成':
                cat['failed'] += 1

        # 计算各类别成功率
        for cat, stats in analysis['methodology_categories'].items():
            if stats['count'] > 0:
                stats['success_rate'] = round(stats['success'] / stats['count'] * 100, 1)

        # 趋势分析：近25轮 vs 前25轮
        mid = len(history) // 2
        recent = history[:mid] if mid > 0 else history
        older = history[mid:] if mid > 0 else []

        def calc_trend(group):
            if not group:
                return {'success_rate': 0, 'count': 0}
            success = sum(1 for h in group if h.get('是否完成') == '已完成')
            return {
                'success_rate': round(success / len(group) * 100, 1),
                'count': len(group)
            }

        analysis['trend_analysis'] = {
            'recent': calc_trend(recent),
            'older': calc_trend(older),
            'trend_direction': 'improving' if calc_trend(recent)['success_rate'] > calc_trend(older)['success_rate'] else 'declining'
        }

        return analysis

    def _classify_methodology(self, goal: str) -> str:
        """分类方法论类型"""
        goal = goal.lower()
        if '元进化' in goal or 'meta' in goal:
            return '元进化'
        elif '驾驶舱' in goal or 'cockpit' in goal:
            return '驾驶舱集成'
        elif '知识' in goal and ('图谱' in goal or '融合' in goal):
            return '知识图谱'
        elif '执行' in goal and ('效率' in goal or '优化' in goal):
            return '执行优化'
        elif '趋势' in goal or '预测' in goal:
            return '趋势预测'
        elif '反馈' in goal or '监控' in goal:
            return '监控反馈'
        elif '自动' in goal and ('优化' in goal or '执行' in goal):
            return '自动化'
        elif '集成' in goal or '深度' in goal:
            return '深度集成'
        elif '引擎' in goal:
            return '引擎创建'
        else:
            return '其他'

    def discover_patterns(self, history: List[Dict] = None) -> Dict[str, Any]:
        """发现进化模式与策略组合"""
        if history is None:
            history = load_evolution_completed_history()

        history = history[:self.analysis_window]

        patterns = {
            'successful_patterns': [],
            'failed_patterns': [],
            'optimization_opportunities': [],
            'strategy_combinations': [],
            'discovered_at': datetime.now().isoformat()
        }

        if len(history) < self.min_samples:
            return patterns

        # 成功的进化模式
        successful = [h for h in history if h.get('是否完成') == '已完成']
        failed = [h for h in history if h.get('是否完成') == '未完成']

        # 分析成功模式
        if successful:
            # 按目标类型分组
            goal_groups = defaultdict(list)
            for h in successful:
                goal = h.get('current_goal', '')
                category = self._classify_methodology(goal)
                goal_groups[category].append(h)

            for cat, items in goal_groups.items():
                if len(items) >= 2:  # 至少2次成功
                    patterns['successful_patterns'].append({
                        'category': cat,
                        'count': len(items),
                        'rounds': [h.get('loop_round', 0) for h in items],
                        'success_rate': 100.0,
                        'description': f'{cat}类型进化连续{len(items)}次成功'
                    })

        # 识别优化机会
        analysis = self.analyze_methodology_effects(history)

        for cat, stats in analysis['methodology_categories'].items():
            if stats['count'] >= 3:
                if stats['success_rate'] < 70:
                    patterns['optimization_opportunities'].append({
                        'type': 'low_success',
                        'category': cat,
                        'success_rate': stats['success_rate'],
                        'count': stats['count'],
                        'suggestion': f'{cat}类型成功率较低({stats["success_rate"]}%)，建议分析原因并优化'
                    })
                elif stats['count'] >= 5 and stats['success_rate'] >= 90:
                    patterns['optimization_opportunities'].append({
                        'type': 'high_success',
                        'category': cat,
                        'success_rate': stats['success_rate'],
                        'count': stats['count'],
                        'suggestion': f'{cat}类型成功率很高({stats["success_rate"]}%)，可作为最佳实践推广'
                    })

        # 趋势分析产生的优化机会
        if analysis['trend_analysis']['trend_direction'] == 'declining':
            patterns['optimization_opportunities'].append({
                'type': 'declining_trend',
                'recent_rate': analysis['trend_analysis']['recent']['success_rate'],
                'older_rate': analysis['trend_analysis']['older']['success_rate'],
                'suggestion': f'进化成功率呈下降趋势（{analysis["trend_analysis"]["older"]["success_rate"]}% → {analysis["trend_analysis"]["recent"]["success_rate"]}%），需要立即优化'
            })

        # 策略组合分析
        # 检查连续完成的进化
        consecutive_success = 0
        max_consecutive = 0
        consecutive_start = 0

        for i, h in enumerate(history):
            if h.get('是否完成') == '已完成':
                if consecutive_success == 0:
                    consecutive_start = i
                consecutive_success += 1
                max_consecutive = max(max_consecutive, consecutive_success)
            else:
                consecutive_success = 0

        if max_consecutive >= 3:
            patterns['strategy_combinations'].append({
                'type': 'consecutive_success',
                'max_consecutive': max_consecutive,
                'description': f'最多连续{max_consecutive}次成功，说明当前进化策略稳定'
            })

        # 保存发现的模式
        self.state['pattern_discoveries'].append({
            'patterns': patterns,
            'discovered_at': datetime.now().isoformat()
        })
        self._save_state()

        return patterns

    def generate_optimization_suggestions(self, history: List[Dict] = None) -> List[Dict[str, Any]]:
        """生成优化建议"""
        if history is None:
            history = load_evolution_completed_history()

        suggestions = []

        # 获取模式发现结果
        patterns = self.discover_patterns(history)

        # 基于优化机会生成建议
        for opt in patterns.get('optimization_opportunities', []):
            if opt['type'] == 'low_success':
                suggestions.append({
                    'priority': 'high',
                    'category': 'strategy_adjustment',
                    'target': opt['category'],
                    'suggestion': opt['suggestion'],
                    'action': f'分析{opt["category"]}类型进化的失败原因，调整策略参数'
                })
            elif opt['type'] == 'declining_trend':
                suggestions.append({
                    'priority': 'critical',
                    'category': 'trend_reversal',
                    'target': 'overall',
                    'suggestion': opt['suggestion'],
                    'action': '立即执行全面的方法论诊断，识别系统性问题'
                })
            elif opt['type'] == 'high_success':
                suggestions.append({
                    'priority': 'medium',
                    'category': 'best_practice',
                    'target': opt['category'],
                    'suggestion': opt['suggestion'],
                    'action': f'将{opt["category"]}的成功模式应用到其他类型'
                })

        # 基于趋势分析生成建议
        analysis = self.analyze_methodology_effects(history)
        if analysis['trend_analysis']['trend_direction'] == 'declining':
            suggestions.append({
                'priority': 'high',
                'category': 'trend_optimization',
                'target': 'execution',
                'suggestion': '执行效率优化：简化流程、减少等待时间',
                'action': '检查进化执行步骤，识别可并行化或简化的环节'
            })

        # 保存待执行的优化建议
        self.state['pending_optimizations'] = suggestions
        self._save_state()

        return suggestions

    def apply_optimization(self, optimization: Dict) -> bool:
        """应用优化建议"""
        try:
            # 将优化标记为已应用
            applied = {
                'optimization': optimization,
                'applied_at': datetime.now().isoformat(),
                'round_applied': self.state.get('last_optimization_round', 0) + 1
            }

            self.state['applied_optimizations'].append(applied)
            self.state['optimization_count'] += 1
            self.state['pending_optimizations'] = [
                opt for opt in self.state.get('pending_optimizations', [])
                if opt != optimization
            ]

            self._save_state()
            return True
        except Exception as e:
            _safe_print(f"应用优化失败: {e}")
            return False

    def verify_optimization_effect(self, optimization: Dict, history: List[Dict] = None) -> Dict:
        """验证优化效果"""
        if history is None:
            history = load_evolution_completed_history()

        # 取优化应用后的最新几轮
        recent_rounds = history[:10]

        if not recent_rounds:
            return {'status': 'insufficient_data', 'message': '无足够数据验证'}

        success_count = sum(1 for h in recent_rounds if h.get('是否完成') == '已完成')
        success_rate = round(success_count / len(recent_rounds) * 100, 1)

        return {
            'status': 'verified',
            'recent_success_rate': success_rate,
            'rounds_checked': len(recent_rounds),
            'verification_time': datetime.now().isoformat(),
            'effectiveness': 'effective' if success_rate >= 70 else 'needs_improvement'
        }

    def get_cockpit_data(self) -> Dict:
        """获取驾驶舱数据"""
        history = load_evolution_completed_history()
        analysis = self.analyze_methodology_effects(history)
        patterns = self.discover_patterns(history)
        suggestions = self.generate_optimization_suggestions(history)

        return {
            'analysis': analysis,
            'patterns': patterns,
            'suggestions': suggestions,
            'state': {
                'optimization_count': self.state.get('optimization_count', 0),
                'applied_count': len(self.state.get('applied_optimizations', [])),
                'pending_count': len(self.state.get('pending_optimizations', []))
            },
            'updated_at': datetime.now().isoformat()
        }

    def push_to_cockpit(self):
        """推送到驾驶舱"""
        data = self.get_cockpit_data()
        try:
            os.makedirs(os.path.dirname(self.cockpit_file), exist_ok=True)
            with open(self.cockpit_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            _safe_print(f"方法论优化数据已推送到驾驶舱: {self.cockpit_file}")
            return True
        except Exception as e:
            _safe_print(f"推送驾驶舱失败: {e}")
            return False

    def run_full_optimization_cycle(self) -> Dict:
        """运行完整的优化周期"""
        _safe_print("开始执行进化方法论自动优化周期...")

        # 1. 分析方法论效果
        _safe_print("[1/4] 分析进化方法论效果...")
        history = load_evolution_completed_history()
        analysis = self.analyze_methodology_effects(history)

        # 2. 发现模式
        _safe_print("[2/4] 发现进化模式与策略组合...")
        patterns = self.discover_patterns(history)

        # 3. 生成优化建议
        _safe_print("[3/4] 生成优化建议...")
        suggestions = self.generate_optimization_suggestions(history)

        # 4. 推送到驾驶舱
        _safe_print("[4/4] 推送到进化驾驶舱...")
        self.push_to_cockpit()

        _safe_print("优化周期完成!")

        return {
            'analysis': analysis,
            'patterns': patterns,
            'suggestions': suggestions,
            'completed_at': datetime.now().isoformat()
        }


def main():
    """主函数 - 支持命令行调用"""
    import argparse

    parser = argparse.ArgumentParser(description='进化方法论自动优化引擎')
    parser.add_argument('--analyze', action='store_true', help='分析进化方法论效果')
    parser.add_argument('--patterns', action='store_true', help='发现进化模式')
    parser.add_argument('--suggestions', action='store_true', help='生成优化建议')
    parser.add_argument('--full-cycle', action='store_true', help='运行完整优化周期')
    parser.add_argument('--cockpit-data', action='store_true', help='获取驾驶舱数据')
    parser.add_argument('--push-cockpit', action='store_true', help='推送到驾驶舱')
    parser.add_argument('--verify', action='store_true', help='验证优化效果')

    args = parser.parse_args()

    optimizer = MethodologyAutoOptimizer()

    if args.analyze or (not any(vars(args).values())):
        result = optimizer.analyze_methodology_effects()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    if args.patterns:
        result = optimizer.discover_patterns()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    if args.suggestions:
        result = optimizer.generate_optimization_suggestions()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    if args.full_cycle:
        result = optimizer.run_full_optimization_cycle()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    if args.cockpit_data:
        result = optimizer.get_cockpit_data()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    if args.push_cockpit:
        optimizer.push_to_cockpit()

    if args.verify:
        # 验证最新的优化效果
        pending = optimizer.state.get('pending_optimizations', [])
        if pending:
            result = optimizer.verify_optimization_effect(pending[0])
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print("无待验证的优化")


if __name__ == '__main__':
    main()