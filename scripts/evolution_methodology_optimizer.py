#!/usr/bin/env python3
"""
智能全场景进化方法论自动优化引擎
基于 round 344 的创新实现深化引擎，进一步实现进化方法论的自动优化能力。
系统能够自动分析进化执行的历史数据，识别低效模式和优化机会，
动态调整进化策略参数，实现"进化→分析→优化→更高效进化"的递归优化闭环，
让系统真正学会"如何更好地进化"。

功能：
1. 进化历史数据自动分析（成功率、效率、资源消耗）
2. 低效模式识别（重复进化、资源浪费、策略失效）
3. 策略参数动态调整（优先级、执行顺序、资源分配）
4. 递归优化闭环（分析→优化→执行→验证→再分析）
5. 与 do.py 深度集成
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

# 添加项目根目录到 Python 路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, PROJECT_ROOT)


def _safe_print(text: str):
    """安全打印，处理编码问题"""
    try:
        print(text)
    except UnicodeEncodeError:
        clean_text = re.sub(r'[^\x00-\x7F]+', '', text)
        print(clean_text)


class EvolutionMethodologyOptimizer:
    """进化方法论自动优化引擎 - 自动分析进化数据，识别优化机会，动态调整策略"""

    def __init__(self):
        self.db_path = os.path.join(PROJECT_ROOT, "runtime/state/evolution_history.db")
        self.methodology_config_path = os.path.join(PROJECT_ROOT, "runtime/state/methodology_config.json")
        self.optimization_history_path = os.path.join(PROJECT_ROOT, "runtime/state/methodology_optimization_history.json")
        self.current_optimization = {}
        self.config = self._load_config()

    def _load_config(self) -> Dict:
        """加载方法论配置"""
        default_config = {
            'analysis_window': 50,  # 分析最近50轮
            'min_samples_for_analysis': 5,  # 最少5个样本才分析
            'low_efficiency_threshold': 0.6,  # 低效率阈值
            'high_success_threshold': 0.85,  # 高成功率阈值
            'auto_apply_optimizations': True,  # 自动应用优化
            'optimization_interval': 10,  # 每10轮执行一次优化
            'strategy_weights': {
                'health': 0.5,
                'intent': 0.5,
                'prediction': 0.5,
                'scheduling': 0.5,
                'collaboration': 0.5,
                'innovation': 0.5,
                'knowledge': 0.5,
                'efficiency': 0.5
            },
            'execution_priorities': {
                'critical': 1,
                'high': 2,
                'normal': 3,
                'low': 4
            },
            'resource_allocation': {
                'max_concurrent_evolution': 3,
                'time_per_evolution': 300,  # 秒
                'memory_limit_mb': 512
            }
        }

        try:
            if os.path.exists(self.methodology_config_path):
                with open(self.methodology_config_path, 'r', encoding='utf-8') as f:
                    saved_config = json.load(f)
                    default_config.update(saved_config)
        except Exception as e:
            _safe_print(f"加载方法论配置失败: {e}")

        return default_config

    def _save_config(self, config: Dict):
        """保存方法论配置"""
        try:
            os.makedirs(os.path.dirname(self.methodology_config_path), exist_ok=True)
            with open(self.methodology_config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            _safe_print(f"方法论配置已保存到 {self.methodology_config_path}")
        except Exception as e:
            _safe_print(f"保存方法论配置失败: {e}")

    def analyze_evolution_history(self) -> Dict:
        """分析进化历史数据"""
        analysis = {
            'total_rounds': 0,
            'completed_rounds': 0,
            'failed_rounds': 0,
            'avg_execution_time': 0,
            'success_rate': 0,
            'strategy_performance': {},
            'execution_trends': {},
            'analyzed_at': datetime.now().isoformat()
        }

        try:
            if not os.path.exists(self.db_path):
                return analysis

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 获取总体统计
            cursor.execute("""
                SELECT COUNT(*),
                       SUM(CASE WHEN status IN ('已完成', 'success', 'completed') THEN 1 ELSE 0 END),
                       SUM(CASE WHEN status IN ('failed', '失败') THEN 1 ELSE 0 END),
                       AVG(execution_time)
                FROM evolution_rounds
                WHERE round_number > (SELECT MAX(round_number) FROM evolution_rounds) - ?
            """, (self.config.get('analysis_window', 50),))

            row = cursor.fetchone()
            if row:
                analysis['total_rounds'] = row[0] or 0
                analysis['completed_rounds'] = row[1] or 0
                analysis['failed_rounds'] = row[2] or 0
                analysis['avg_execution_time'] = round(row[3] or 0, 2)

                if analysis['total_rounds'] > 0:
                    analysis['success_rate'] = round(
                        analysis['completed_rounds'] / analysis['total_rounds'] * 100, 1
                    )

            # 分析各策略类型的表现
            cursor.execute("""
                SELECT current_goal, status, execution_time, round_number
                FROM evolution_rounds
                WHERE round_number > (SELECT MAX(round_number) FROM evolution_rounds) - ?
                ORDER BY round_number DESC
            """, (self.config.get('analysis_window', 50),))

            strategy_stats = defaultdict(lambda: {
                'count': 0, 'success': 0, 'failed': 0, 'times': [], 'rounds': []
            })

            for row in cursor.fetchall():
                goal, status, exec_time, round_num = row
                strategy_type = self._classify_strategy(goal)

                if strategy_type:
                    stats = strategy_stats[strategy_type]
                    stats['count'] += 1
                    stats['rounds'].append(round_num)

                    if status in ['已完成', 'success', 'completed']:
                        stats['success'] += 1
                    elif status in ['failed', '失败']:
                        stats['failed'] += 1

                    if exec_time:
                        stats['times'].append(exec_time)

            # 计算各策略的详细性能
            for strategy_type, stats in strategy_stats.items():
                if stats['count'] > 0:
                    stats['success_rate'] = round(stats['success'] / stats['count'] * 100, 1)
                    stats['avg_time'] = round(sum(stats['times']) / len(stats['times']), 2) if stats['times'] else 0
                    stats['min_time'] = min(stats['times']) if stats['times'] else 0
                    stats['max_time'] = max(stats['times']) if stats['times'] else 0
                    # 计算时间趋势
                    if len(stats['rounds']) >= 3:
                        recent_avg = sum(stats['times'][:len(stats['times'])//2]) / (len(stats['times'])//2) if len(stats['times']) > 1 else 0
                        older_avg = sum(stats['times'][len(stats['times'])//2:]) / (len(stats['times']) - len(stats['times'])//2) if len(stats['times']) > 1 else 0
                        if older_avg > 0:
                            stats['time_trend'] = 'improving' if recent_avg < older_avg else 'degrading' if recent_avg > older_avg else 'stable'
                        else:
                            stats['time_trend'] = 'stable'
                    else:
                        stats['time_trend'] = 'insufficient_data'

                    del stats['times']  # 删除原始时间列表以减小输出
                    del stats['rounds']

            analysis['strategy_performance'] = dict(strategy_stats)

            # 计算整体执行趋势
            cursor.execute("""
                SELECT round_number, execution_time
                FROM evolution_rounds
                WHERE round_number > (SELECT MAX(round_number) FROM evolution_rounds) - ?
                AND execution_time > 0
                ORDER BY round_number ASC
            """, (self.config.get('analysis_window', 50),))

            time_rows = cursor.fetchall()
            if len(time_rows) >= 5:
                first_half = time_rows[:len(time_rows)//2]
                second_half = time_rows[len(time_rows)//2:]

                first_avg = sum(r[1] for r in first_half) / len(first_half)
                second_avg = sum(r[1] for r in second_half) / len(second_half)

                if second_avg < first_avg * 0.9:
                    analysis['execution_trends']['efficiency'] = 'improving'
                elif second_avg > first_avg * 1.1:
                    analysis['execution_trends']['efficiency'] = 'degrading'
                else:
                    analysis['execution_trends']['efficiency'] = 'stable'

            conn.close()

        except Exception as e:
            _safe_print(f"分析进化历史时出错: {e}")

        return analysis

    def _classify_strategy(self, goal: str) -> Optional[str]:
        """根据目标分类策略类型"""
        if not goal:
            return None

        goal_lower = goal.lower()

        if any(k in goal_lower for k in ['健康', '自愈', '自检', '诊断', '免疫', '防御']):
            return 'health'
        elif any(k in goal_lower for k in ['意图', '觉醒', '自主', '自主意识', '自主决策']):
            return 'intent'
        elif any(k in goal_lower for k in ['预测', '主动服务', '服务编排', '预防']):
            return 'prediction'
        elif any(k in goal_lower for k in ['调度', '优化', '资源', '负载', '均衡']):
            return 'scheduling'
        elif any(k in goal_lower for k in ['协作', '多智能体', '协同', '克隆', '分布式']):
            return 'collaboration'
        elif any(k in goal_lower for k in ['创新', '创造', '发现', '实现']):
            return 'innovation'
        elif any(k in goal_lower for k in ['知识', '学习', '传承', '推理']):
            return 'knowledge'
        elif any(k in goal_lower for k in ['效率', '效能', '监控', '性能']):
            return 'efficiency'
        elif any(k in goal_lower for k in ['方法论', '元', '优化']):
            return 'methodology'
        else:
            return 'other'

    def identify_low_efficiency_patterns(self, analysis: Dict) -> List[Dict]:
        """识别低效模式"""
        patterns = []

        strategy_perf = analysis.get('strategy_performance', {})

        # 1. 识别低成功率策略
        for strategy, data in strategy_perf.items():
            count = data.get('count', 0)
            success_rate = data.get('success_rate', 0)

            if count >= self.config.get('min_samples_for_analysis', 5):
                if success_rate < self.config.get('low_efficiency_threshold', 60):
                    patterns.append({
                        'type': 'low_success_rate',
                        'strategy': strategy,
                        'severity': 'high' if success_rate < 40 else 'medium',
                        'description': f'{strategy}策略成功率低({success_rate}%)，建议降低优先级或改进方法',
                        'data': data
                    })

        # 2. 识别执行时间退化
        for strategy, data in strategy_perf.items():
            trend = data.get('time_trend', 'insufficient_data')
            if trend == 'degrading':
                patterns.append({
                    'type': 'execution_time_degradation',
                    'strategy': strategy,
                    'severity': 'medium',
                    'description': f'{strategy}策略执行时间呈上升趋势，需优化执行效率',
                    'data': data
                })

        # 3. 识别高效率策略
        high_efficient = []
        for strategy, data in strategy_perf.items():
            count = data.get('count', 0)
            success_rate = data.get('success_rate', 0)
            avg_time = data.get('avg_time', 0)

            if count >= 3 and success_rate >= self.config.get('high_success_threshold', 85):
                high_efficient.append({
                    'strategy': strategy,
                    'success_rate': success_rate,
                    'avg_time': avg_time
                })

        if high_efficient:
            patterns.append({
                'type': 'high_efficiency_strategies',
                'severity': 'info',
                'description': f'发现{len(high_efficient)}个高效率策略，可增加其权重',
                'strategies': high_efficient
            })

        return patterns

    def generate_optimization_plan(self, analysis: Dict, patterns: List[Dict]) -> Dict:
        """生成优化方案"""
        plan = {
            'adjustments': [],
            'strategy_weight_updates': {},
            'execution_priority_updates': {},
            'resource_allocation_updates': {},
            'recommendations': []
        }

        # 1. 基于低效模式调整策略权重
        for pattern in patterns:
            if pattern['type'] == 'low_success_rate':
                strategy = pattern['strategy']
                current_weight = self.config.get('strategy_weights', {}).get(strategy, 0.5)

                # 降低低效策略的权重
                new_weight = max(0.2, current_weight - 0.2)
                plan['strategy_weight_updates'][strategy] = {
                    'current': current_weight,
                    'suggested': new_weight,
                    'reason': pattern['description']
                }

                plan['adjustments'].append({
                    'type': 'reduce_weight',
                    'target': f'strategy_weights.{strategy}',
                    'value': new_weight
                })

            elif pattern['type'] == 'high_efficiency_strategies':
                for hs in pattern.get('strategies', []):
                    strategy = hs['strategy']
                    current_weight = self.config.get('strategy_weights', {}).get(strategy, 0.5)

                    # 增加高效策略的权重
                    new_weight = min(0.9, current_weight + 0.15)
                    plan['strategy_weight_updates'][strategy] = {
                        'current': current_weight,
                        'suggested': new_weight,
                        'reason': f'{strategy}策略表现优秀(成功率{hs["success_rate"]}%)，建议增加权重'
                    }

                    plan['adjustments'].append({
                        'type': 'increase_weight',
                        'target': f'strategy_weights.{strategy}',
                        'value': new_weight
                    })

        # 2. 基于执行趋势调整资源配置
        efficiency_trend = analysis.get('execution_trends', {}).get('efficiency', 'stable')
        if efficiency_trend == 'degrading':
            # 执行效率下降，减少并发
            current_concurrent = self.config.get('resource_allocation', {}).get('max_concurrent_evolution', 3)
            new_concurrent = max(1, current_concurrent - 1)

            plan['resource_allocation_updates']['max_concurrent_evolution'] = {
                'current': current_concurrent,
                'suggested': new_concurrent,
                'reason': '执行效率下降，减少并发以提升稳定性'
            }

            plan['adjustments'].append({
                'type': 'reduce_concurrent',
                'target': 'resource_allocation.max_concurrent_evolution',
                'value': new_concurrent
            })

            plan['recommendations'].append('建议：降低并发数，提升每轮进化的专注度和成功率')

        elif efficiency_trend == 'improving':
            # 执行效率提升，可以尝试更激进的优化
            plan['recommendations'].append('执行效率持续改善，可尝试更激进的优化策略')

        # 3. 生成总体建议
        total_rounds = analysis.get('total_rounds', 0)
        success_rate = analysis.get('success_rate', 0)

        if total_rounds > 0:
            if success_rate >= 85:
                plan['recommendations'].append(f'整体成功率优秀({success_rate}%)，保持当前策略')
            elif success_rate >= 70:
                plan['recommendations'].append(f'整体成功率良好({success_rate}%)，建议微调权重')
            else:
                plan['recommendations'].append(f'整体成功率偏低({success_rate}%)，需全面审视进化策略')

        return plan

    def apply_optimizations(self, plan: Dict) -> Dict:
        """应用优化方案"""
        applied = []

        # 更新策略权重
        for strategy, update in plan.get('strategy_weight_updates', {}).items():
            if 'strategy_weights' not in self.config:
                self.config['strategy_weights'] = {}

            old_value = self.config['strategy_weights'].get(strategy, 0.5)
            self.config['strategy_weights'][strategy] = update['suggested']
            applied.append(f'策略权重 {strategy}: {old_value} -> {update["suggested"]}')

        # 更新资源配置
        for key, update in plan.get('resource_allocation_updates', {}).items():
            if 'resource_allocation' not in self.config:
                self.config['resource_allocation'] = {}

            old_value = self.config['resource_allocation'].get(key, 0)
            self.config['resource_allocation'][key] = update['suggested']
            applied.append(f'资源配置 {key}: {old_value} -> {update["suggested"]}')

        # 保存配置
        self._save_config(self.config)

        return {
            'applied_count': len(applied),
            'applied_items': applied,
            'plan': plan
        }

    def verify_optimization_effect(self, previous_analysis: Dict) -> Dict:
        """验证优化效果"""
        # 获取最新分析
        current_analysis = self.analyze_evolution_history()

        # 对比关键指标
        comparison = {
            'success_rate_change': current_analysis.get('success_rate', 0) - previous_analysis.get('success_rate', 0),
            'avg_time_change': current_analysis.get('avg_execution_time', 0) - previous_analysis.get('avg_execution_time', 0),
            'strategy_performance_changes': {}
        }

        # 对比各策略表现
        prev_strategies = previous_analysis.get('strategy_performance', {})
        curr_strategies = current_analysis.get('strategy_performance', {})

        for strategy in set(list(prev_strategies.keys()) + list(curr_strategies.keys())):
            prev_data = prev_strategies.get(strategy, {})
            curr_data = curr_strategies.get(strategy, {})

            comparison['strategy_performance_changes'][strategy] = {
                'success_rate_change': curr_data.get('success_rate', 0) - prev_data.get('success_rate', 0),
                'avg_time_change': curr_data.get('avg_time', 0) - prev_data.get('avg_time', 0)
            }

        return {
            'verified': True,
            'previous_analysis': previous_analysis,
            'current_analysis': current_analysis,
            'comparison': comparison,
            'overall_improvement': comparison['success_rate_change'] > 0 or comparison['avg_time_change'] < 0
        }

    def run_full_optimization_cycle(self) -> Dict:
        """执行完整的优化周期"""
        _safe_print("=" * 60)
        _safe_print("进化方法论自动优化引擎")
        _safe_print("=" * 60)

        # 1. 分析进化历史数据
        _safe_print("\n[1/5] 分析进化历史数据...")
        analysis = self.analyze_evolution_history()
        _safe_print(f"    分析了 {analysis['total_rounds']} 轮进化")
        _safe_print(f"    成功率: {analysis['success_rate']}%")
        _safe_print(f"    平均执行时间: {analysis['avg_execution_time']}s")

        # 2. 识别低效模式
        _safe_print("\n[2/5] 识别低效模式...")
        patterns = self.identify_low_efficiency_patterns(analysis)
        _safe_print(f"    发现 {len(patterns)} 个模式")

        for pattern in patterns:
            severity_emoji = '🔴' if pattern['severity'] == 'high' else '🟡' if pattern['severity'] == 'medium' else '🟢'
            _safe_print(f"    {severity_emoji} {pattern['type']}: {pattern['description']}")

        # 3. 生成优化方案
        _safe_print("\n[3/5] 生成优化方案...")
        plan = self.generate_optimization_plan(analysis, patterns)
        _safe_print(f"    生成了 {len(plan['adjustments'])} 条调整")

        for adj in plan['adjustments']:
            _safe_print(f"    - {adj['type']}: {adj['target']} = {adj['value']}")

        # 4. 应用优化
        _safe_print("\n[4/5] 应用优化...")
        result = self.apply_optimizations(plan)
        _safe_print(f"    已应用 {result['applied_count']} 条优化")

        # 5. 保存优化历史
        self._save_optimization_history(analysis, patterns, plan)

        # 6. 输出建议
        _safe_print("\n[5/5] 优化建议:")
        for rec in plan.get('recommendations', []):
            _safe_print(f"    💡 {rec}")

        _safe_print("\n" + "=" * 60)
        _safe_print("优化完成！")
        _safe_print("=" * 60)

        self.current_optimization = {
            'timestamp': datetime.now().isoformat(),
            'analysis': analysis,
            'patterns': patterns,
            'plan': plan,
            'applied': result
        }

        return self.current_optimization

    def _save_optimization_history(self, analysis: Dict, patterns: List[Dict], plan: Dict):
        """保存优化历史"""
        history = []

        try:
            if os.path.exists(self.optimization_history_path):
                with open(self.optimization_history_path, 'r', encoding='utf-8') as f:
                    history = json.load(f)
        except:
            pass

        history.append({
            'timestamp': datetime.now().isoformat(),
            'total_rounds': analysis.get('total_rounds', 0),
            'success_rate': analysis.get('success_rate', 0),
            'patterns_count': len(patterns),
            'adjustments_count': len(plan.get('adjustments', [])),
            'recommendations': plan.get('recommendations', [])
        })

        # 只保留最近20条
        history = history[-20:]

        try:
            os.makedirs(os.path.dirname(self.optimization_history_path), exist_ok=True)
            with open(self.optimization_history_path, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            _safe_print(f"保存优化历史失败: {e}")

    def get_status(self) -> Dict:
        """获取引擎状态"""
        return {
            'status': 'active',
            'config': self.config,
            'last_optimization': self.current_optimization if self.current_optimization else None
        }

    def get_recent_optimizations(self, limit: int = 5) -> List[Dict]:
        """获取最近的优化记录"""
        try:
            if os.path.exists(self.optimization_history_path):
                with open(self.optimization_history_path, 'r', encoding='utf-8') as f:
                    history = json.load(f)
                return history[-limit:]
        except:
            pass
        return []

    def analyze_and_report(self) -> Dict:
        """分析并生成报告（不自动应用优化）"""
        analysis = self.analyze_evolution_history()
        patterns = self.identify_low_efficiency_patterns(analysis)
        plan = self.generate_optimization_plan(analysis, patterns)

        return {
            'analysis': analysis,
            'patterns': patterns,
            'plan': plan,
            'generated_at': datetime.now().isoformat()
        }


def main():
    """主入口"""
    import argparse

    parser = argparse.ArgumentParser(description='智能进化方法论自动优化引擎')
    parser.add_argument('command', nargs='?', default='status',
                        help='命令: status, optimize, analyze, history, config')
    parser.add_argument('--optimize', action='store_true', help='执行完整优化')
    parser.add_argument('--analyze', action='store_true', help='仅分析并生成报告（不应用）')
    parser.add_argument('--history', action='store_true', help='查看优化历史')
    parser.add_argument('--config', action='store_true', help='查看当前配置')
    parser.add_argument('--limit', type=int, default=5, help='历史记录数量限制')

    args = parser.parse_args()

    optimizer = EvolutionMethodologyOptimizer()

    if args.optimize or args.command == 'optimize':
        result = optimizer.run_full_optimization_cycle()
        print("\n优化结果:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.analyze or args.command == 'analyze':
        result = optimizer.analyze_and_report()
        print("\n分析报告:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.history or args.command == 'history':
        history = optimizer.get_recent_optimizations(args.limit)
        print("\n优化历史:")
        print(json.dumps(history, ensure_ascii=False, indent=2))
    elif args.config or args.command == 'config':
        config = optimizer._load_config()
        print("\n当前方法论配置:")
        print(json.dumps(config, ensure_ascii=False, indent=2))
    else:
        # 默认显示状态
        status = optimizer.get_status()
        print("\n方法论优化引擎状态:")
        print(json.dumps(status, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()