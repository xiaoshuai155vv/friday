#!/usr/bin/env python3
"""
智能全场景进化方法论自动优化引擎与进化环深度集成引擎
将 round 345 的进化方法论优化引擎与进化环深度集成，
实现进化过程中的自动检测→分析→优化→执行→验证闭环，
让方法论优化能力能够在进化环执行过程中自动触发。

功能：
1. 自动检测进化环执行状态，判断是否需要触发优化
2. 与进化环深度集成，在适当条件下自动调用方法论优化引擎
3. 实现完整的「检测→分析→优化→执行→验证」闭环
4. 支持手动触发和自动触发两种模式
5. 与 do.py 深度集成，支持关键词触发
"""

import os
import sys
import json
import sqlite3
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

# 添加项目根目录到 Python 路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, SCRIPT_DIR)  # 添加 scripts 目录以便导入同目录模块

# 导入方法论优化引擎
try:
    from evolution_methodology_optimizer import EvolutionMethodologyOptimizer
except ImportError:
    EvolutionMethodologyOptimizer = None


def _safe_print(text: str):
    """安全打印，处理编码问题"""
    import re
    try:
        print(text)
    except UnicodeEncodeError:
        clean_text = re.sub(r'[^\x00-\x7F]+', '', text)
        print(clean_text)


class EvolutionMethodologyIntegration:
    """进化方法论优化引擎与进化环深度集成引擎"""

    def __init__(self):
        self.optimizer = EvolutionMethodologyOptimizer() if EvolutionMethodologyOptimizer else None
        self.db_path = os.path.join(PROJECT_ROOT, "runtime/state/evolution_history.db")
        self.state_path = os.path.join(PROJECT_ROOT, "runtime/state/methodology_integration_state.json")
        self.integration_config = self._load_config()
        self.last_optimization_round = 0

    def _load_config(self) -> Dict:
        """加载集成配置"""
        default_config = {
            'auto_trigger_enabled': True,  # 自动触发优化
            'optimization_interval': 10,  # 每10轮执行一次自动优化
            'low_success_rate_threshold': 0.7,  # 成功率低于70%时触发优化
            'high_failure_count_threshold': 3,  # 连续失败3次时触发优化
            'efficiency_degradation_threshold': 0.2,  # 效率下降20%时触发优化
            'check_on_evolution_end': True,  # 进化结束时检查
            'check_on_evolution_start': False,  # 进化开始时检查
            'auto_apply_optimizations': True,  # 自动应用优化
            'notify_on_optimization': True,  # 优化时通知
        }

        config_path = os.path.join(PROJECT_ROOT, "runtime/state/methodology_integration_config.json")
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    saved_config = json.load(f)
                    default_config.update(saved_config)
        except Exception as e:
            _safe_print(f"加载集成配置失败: {e}")

        return default_config

    def _save_config(self, config: Dict):
        """保存集成配置"""
        config_path = os.path.join(PROJECT_ROOT, "runtime/state/methodology_integration_config.json")
        try:
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            _safe_print(f"保存集成配置失败: {e}")

    def get_current_round(self) -> int:
        """获取当前进化轮次"""
        try:
            if os.path.exists(self.db_path):
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT MAX(round_number) FROM evolution_rounds")
                result = cursor.fetchone()
                conn.close()
                if result and result[0]:
                    return result[0]
        except Exception as e:
            _safe_print(f"获取当前轮次失败: {e}")
        return 0

    def get_recent_rounds_stats(self, count: int = 10) -> Dict:
        """获取最近N轮的统计信息"""
        stats = {
            'total': 0,
            'completed': 0,
            'failed': 0,
            'success_rate': 0.0,
            'avg_execution_time': 0.0,
            'consecutive_failures': 0,
            'rounds': []
        }

        try:
            if not os.path.exists(self.db_path):
                return stats

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 获取最近N轮数据
            cursor.execute("""
                SELECT round_number, status, execution_time, current_goal
                FROM evolution_rounds
                ORDER BY round_number DESC
                LIMIT ?
            """, (count,))

            rows = cursor.fetchall()
            stats['total'] = len(rows)

            for row in rows:
                round_num, status, exec_time, goal = row
                stats['rounds'].append({
                    'round': round_num,
                    'status': status,
                    'execution_time': exec_time,
                    'goal': goal
                })

                if status in ['已完成', 'success', 'completed']:
                    stats['completed'] += 1
                elif status in ['failed', '失败']:
                    stats['failed'] += 1

                if exec_time:
                    stats['avg_execution_time'] += exec_time

            # 计算成功率
            if stats['total'] > 0:
                stats['success_rate'] = stats['completed'] / stats['total']

            # 计算平均执行时间
            if stats['total'] > 0:
                stats['avg_execution_time'] = stats['avg_execution_time'] / stats['total']

            # 计算连续失败
            stats['consecutive_failures'] = self._count_consecutive_failures(rows)

            conn.close()

        except Exception as e:
            _safe_print(f"获取最近轮次统计失败: {e}")

        return stats

    def _count_consecutive_failures(self, rows: List[Tuple]) -> int:
        """计算连续失败次数"""
        consecutive = 0
        for row in rows:
            status = row[1]
            if status in ['failed', '失败']:
                consecutive += 1
            else:
                break
        return consecutive

    def calculate_efficiency_trend(self) -> float:
        """计算效率趋势（返回变化率）"""
        try:
            if not os.path.exists(self.db_path):
                return 0.0

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 获取前后各5轮的执行时间
            cursor.execute("""
                SELECT round_number, execution_time
                FROM evolution_rounds
                WHERE execution_time > 0
                ORDER BY round_number DESC
                LIMIT 20
            """)

            rows = cursor.fetchall()
            conn.close()

            if len(rows) < 10:
                return 0.0

            # 分为前后两半
            first_half = rows[len(rows)//2:]
            second_half = rows[:len(rows)//2]

            first_avg = sum(r[1] for r in first_half) / len(first_half) if first_half else 0
            second_avg = sum(r[1] for r in second_half) / len(second_half) if second_half else 0

            if first_avg == 0:
                return 0.0

            # 计算变化率
            trend = (second_avg - first_avg) / first_avg
            return trend

        except Exception as e:
            _safe_print(f"计算效率趋势失败: {e}")
            return 0.0

    def check_optimization_needed(self) -> Dict[str, Any]:
        """检查是否需要触发优化"""
        current_round = self.get_current_round()
        stats = self.get_recent_rounds_stats(10)
        efficiency_trend = self.calculate_efficiency_trend()

        triggers = []

        # 1. 检查是否达到优化间隔
        rounds_since_last = current_round - self.last_optimization_round
        if rounds_since_last >= self.integration_config.get('optimization_interval', 10):
            triggers.append({
                'type': 'interval',
                'reason': f'已达到{self.integration_config.get("optimization_interval", 10)}轮优化间隔',
                'severity': 'low'
            })

        # 2. 检查成功率是否过低
        success_rate = stats.get('success_rate', 1.0)
        threshold = self.integration_config.get('low_success_rate_threshold', 0.7)
        if success_rate < threshold:
            triggers.append({
                'type': 'low_success_rate',
                'reason': f'成功率过低 ({success_rate:.1%} < {threshold:.1%})',
                'severity': 'high'
            })

        # 3. 检查连续失败
        consecutive_failures = stats.get('consecutive_failures', 0)
        fail_threshold = self.integration_config.get('high_failure_count_threshold', 3)
        if consecutive_failures >= fail_threshold:
            triggers.append({
                'type': 'consecutive_failures',
                'reason': f'连续失败{consecutive_failures}次',
                'severity': 'high'
            })

        # 4. 检查效率是否下降
        efficiency_trend_threshold = self.integration_config.get('efficiency_degradation_threshold', 0.2)
        if efficiency_trend > efficiency_trend_threshold:
            triggers.append({
                'type': 'efficiency_degradation',
                'reason': f'执行效率下降 {efficiency_trend:.1%}',
                'severity': 'medium'
            })

        return {
            'optimization_needed': len(triggers) > 0,
            'triggers': triggers,
            'current_round': current_round,
            'rounds_since_last_optimization': rounds_since_last,
            'stats': stats,
            'efficiency_trend': efficiency_trend
        }

    def run_auto_optimization(self, force: bool = False) -> Dict[str, Any]:
        """运行自动优化"""
        _safe_print("=" * 60)
        _safe_print("进化方法论自动优化引擎（深度集成模式）")
        _safe_print("=" * 60)

        # 1. 检查是否需要优化
        _safe_print("\n[1/5] 检查是否需要触发优化...")
        check_result = self.check_optimization_needed()

        if not force and not check_result['optimization_needed']:
            _safe_print(f"    当前不需要触发优化")
            _safe_print(f"    距上次优化: {check_result['rounds_since_last_optimization']} 轮")
            _safe_print(f"    成功率: {check_result['stats'].get('success_rate', 0):.1%}")
            _safe_print(f"    效率趋势: {check_result['efficiency_trend']:.1%}")

            # 保存检查结果
            self._save_state({
                'last_check': datetime.now().isoformat(),
                'check_result': check_result,
                'auto_optimization_triggered': False
            })

            return {
                'status': 'skipped',
                'reason': 'no_optimization_needed',
                'check_result': check_result
            }

        # 2. 显示触发原因
        if check_result['triggers']:
            _safe_print(f"    检测到 {len(check_result['triggers'])} 个触发条件:")
            for trigger in check_result['triggers']:
                severity_emoji = '🔴' if trigger['severity'] == 'high' else '🟡' if trigger['severity'] == 'medium' else '🟢'
                _safe_print(f"    {severity_emoji} {trigger['type']}: {trigger['reason']}")

        # 3. 执行优化
        _safe_print("\n[2/5] 执行进化方法论优化...")

        if self.optimizer:
            # 保存优化前的分析结果作为基准
            previous_analysis = self.optimizer.analyze_evolution_history()

            # 执行完整优化周期
            optimization_result = self.optimizer.run_full_optimization_cycle()

            # 更新最后优化轮次
            self.last_optimization_round = self.get_current_round()

            # 4. 验证优化效果
            _safe_print("\n[3/5] 验证优化效果...")
            verification = self.optimizer.verify_optimization_effect(previous_analysis)

            _safe_print(f"    成功率变化: {verification['comparison'].get('success_rate_change', 0):+.1f}%")
            _safe_print(f"    平均时间变化: {verification['comparison'].get('avg_time_change', 0):+.1f}s")
            _safe_print(f"    整体改善: {'是' if verification.get('overall_improvement') else '否'}")

            # 5. 保存状态
            _safe_print("\n[4/5] 保存优化状态...")
            state = {
                'last_optimization': datetime.now().isoformat(),
                'last_optimization_round': self.last_optimization_round,
                'check_result': check_result,
                'optimization_result': {
                    'applied_count': optimization_result.get('applied', {}).get('applied_count', 0),
                    'patterns_count': len(optimization_result.get('patterns', []))
                },
                'verification': {
                    'overall_improvement': verification.get('overall_improvement', False),
                    'success_rate_change': verification['comparison'].get('success_rate_change', 0)
                }
            }
            self._save_state(state)

            _safe_print("\n[5/5] 优化完成!")
            _safe_print("=" * 60)

            return {
                'status': 'completed',
                'check_result': check_result,
                'optimization': optimization_result,
                'verification': verification
            }
        else:
            _safe_print("    错误: 无法加载方法论优化引擎模块")
            return {
                'status': 'failed',
                'error': 'optimizer_module_not_available'
            }

    def _save_state(self, state: Dict):
        """保存集成状态"""
        try:
            os.makedirs(os.path.dirname(self.state_path), exist_ok=True)
            with open(self.state_path, 'w', encoding='utf-8') as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            _safe_print(f"保存集成状态失败: {e}")

    def get_status(self) -> Dict:
        """获取集成引擎状态"""
        check_result = self.check_optimization_needed()

        state = {}
        if os.path.exists(self.state_path):
            try:
                with open(self.state_path, 'r', encoding='utf-8') as f:
                    state = json.load(f)
            except:
                pass

        return {
            'status': 'active',
            'auto_trigger_enabled': self.integration_config.get('auto_trigger_enabled', True),
            'optimization_needed': check_result['optimization_needed'],
            'triggers': check_result.get('triggers', []),
            'last_optimization': state.get('last_optimization'),
            'current_round': check_result['current_round'],
            'rounds_since_last_optimization': check_result['rounds_since_last_optimization'],
            'config': self.integration_config
        }

    def update_config(self, key: str, value: Any) -> Dict:
        """更新配置"""
        self.integration_config[key] = value
        self._save_config(self.integration_config)
        return {'status': 'updated', 'key': key, 'value': value}

    def trigger_after_evolution(self) -> Dict:
        """在进化环结束后触发检查（供进化环调用）"""
        if not self.integration_config.get('check_on_evolution_end', True):
            return {'status': 'disabled', 'reason': 'check_on_evolution_end is disabled'}

        return self.run_auto_optimization(force=False)

    def trigger_before_evolution(self) -> Dict:
        """在进化环开始前触发检查（供进化环调用）"""
        if not self.integration_config.get('check_on_evolution_start', False):
            return {'status': 'disabled', 'reason': 'check_on_evolution_start is disabled'}

        return self.run_auto_optimization(force=False)


def main():
    """主入口"""
    import argparse

    parser = argparse.ArgumentParser(description='智能进化方法论自动优化引擎（深度集成版）')
    parser.add_argument('command', nargs='?', default='status',
                        help='命令: status, check, optimize, auto, config')
    parser.add_argument('--force', action='store_true', help='强制执行优化')
    parser.add_argument('--set', nargs=2, metavar=('KEY', 'VALUE'), help='设置配置项')
    parser.add_argument('--enable', action='store_true', help='启用自动触发')
    parser.add_argument('--disable', action='store_true', help='禁用自动触发')

    args = parser.parse_args()

    integration = EvolutionMethodologyIntegration()

    if args.command == 'check' or args.command == 'analyze':
        # 仅检查是否需要优化
        result = integration.check_optimization_needed()
        print("\n优化检查结果:")
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == 'optimize' or args.command == 'run':
        # 执行优化
        result = integration.run_auto_optimization(force=args.force)
        print("\n优化执行结果:")
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == 'auto':
        # 自动模式：根据配置自动判断
        result = integration.run_auto_optimization(force=False)
        print("\n自动优化结果:")
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == 'config':
        # 显示/修改配置
        if args.set:
            key, value = args.set
            # 尝试转换值为适当类型
            if value.lower() in ['true', 'yes', '1']:
                value = True
            elif value.lower() in ['false', 'no', '0']:
                value = False
            elif value.isdigit():
                value = int(value)

            result = integration.update_config(key, value)
            print("\n配置更新结果:")
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            # 显示当前配置
            status = integration.get_status()
            print("\n当前配置:")
            print(json.dumps(status.get('config', {}), ensure_ascii=False, indent=2))

    elif args.command == 'enable':
        # 启用自动触发
        result = integration.update_config('auto_trigger_enabled', True)
        print("\n已启用自动触发")

    elif args.command == 'disable':
        # 禁用自动触发
        result = integration.update_config('auto_trigger_enabled', False)
        print("\n已禁用自动触发")

    else:
        # 默认显示状态
        status = integration.get_status()
        print("\n方法论集成引擎状态:")
        print(json.dumps(status, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()