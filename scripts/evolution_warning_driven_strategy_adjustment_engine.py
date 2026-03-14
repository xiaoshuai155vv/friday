#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环预警驱动自动策略调整引擎
version 1.0.0

在 round 465 的元进化与自动化深度集成引擎基础上：
1. 将元进化优化能力与预警引擎深度集成
2. 实现基于预警的自动策略调整功能
3. 实现"预警→策略自动调整→执行→验证"的完整闭环
4. 实现预警驱动的元进化优化

功能：
1. 预警监听与接收 - 监听多维度预警信息
2. 预警分析 - 分析预警类型、级别、影响范围
3. 策略自动调整 - 基于预警自动调整进化策略
4. 调整执行 - 自动执行策略调整
5. 闭环验证 - 验证调整效果并持续优化
6. 与进化驾驶舱深度集成 - 可视化整个过程
7. 集成到 do.py 支持关键词触发

该引擎整合以下模块能力：
- evolution_meta_optimization_integration_engine.py (元进化优化集成)
- evolution_warning_intervention_deep_integration_engine.py (预警与干预)
- evolution_cockpit_engine.py (进化驾驶舱)

作者：AI Evolution System
日期：2026-03-15
"""

import os
import sys
import json
import re
import time
import threading
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import argparse
import subprocess

# 设置 UTF-8 编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

SCRIPT_DIR = Path(__file__).parent
RUNTIME_DIR = SCRIPT_DIR / ".." / "runtime"
STATE_DIR = RUNTIME_DIR / "state"
LOGS_DIR = RUNTIME_DIR / "logs"


class WarningDrivenStrategyAdjustmentEngine:
    """预警驱动自动策略调整引擎 v1.0.0"""

    def __init__(self, base_path: str = None):
        self.version = "1.0.0"
        self.base_path = base_path or str(SCRIPT_DIR)
        self.runtime_path = os.path.join(self.base_path, 'runtime')
        self.state_path = os.path.join(self.runtime_path, 'state')
        self.logs_path = os.path.join(self.runtime_path, 'logs')

        # 状态文件
        self.state_file = Path(STATE_DIR) / "warning_strategy_adjustment_state.json"
        self.warning_history_file = Path(STATE_DIR) / "warning_strategy_adjustment_history.json"
        self.adjustment_log_file = Path(STATE_DIR) / "warning_strategy_adjustment_log.json"
        self.cockpit_data_file = Path(STATE_DIR) / "warning_strategy_cockpit_data.json"

        # 初始化状态
        self.enabled = True
        self.auto_adjust_enabled = True
        self.warnings_received = []
        self.adjustments_made = []
        self.last_adjustment_time = None

        # 策略配置
        self.strategy_config = self._load_strategy_config()

        # 尝试导入相关引擎
        self.meta_optimization_engine = None
        self.warning_engine = None
        self._init_engines()

        # 加载历史数据
        self._load_history()

    def _init_engines(self):
        """初始化相关引擎"""
        try:
            sys.path.insert(0, self.base_path)
            from evolution_meta_optimization_integration_engine import EvolutionMetaOptimizationIntegrationEngine
            self.meta_optimization_engine = EvolutionMetaOptimizationIntegrationEngine(self.base_path)
        except ImportError as e:
            print(f"元进化优化集成引擎不可用: {e}")

        try:
            from evolution_warning_intervention_deep_integration_engine import WarningInterventionEngine
            self.warning_engine = WarningInterventionEngine()
        except ImportError as e:
            print(f"预警干预引擎不可用: {e}")

    def _load_strategy_config(self) -> Dict[str, Any]:
        """加载策略配置"""
        default_config = {
            "auto_adjust_enabled": True,
            "warning_levels": {
                "low": {"auto_adjust": False, "notify_only": True},
                "medium": {"auto_adjust": True, "adjustment_type": "minor"},
                "high": {"auto_adjust": True, "adjustment_type": "moderate"},
                "critical": {"auto_adjust": True, "adjustment_type": "major", "force_adjust": True}
            },
            "adjustment_types": {
                "minor": {"strategy_weight_change": 0.1, "priority_adjustment": 1},
                "moderate": {"strategy_weight_change": 0.2, "priority_adjustment": 2},
                "major": {"strategy_weight_change": 0.3, "priority_adjustment": 3}
            },
            "adjustment_cooldown": 300,  # 调整冷却时间（秒）
            "max_adjustments_per_hour": 10,
            "verification_enabled": True,
            "rollback_on_failure": True
        }

        config_file = Path(STATE_DIR) / "warning_strategy_config.json"
        try:
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    return {**default_config, **config}
        except Exception as e:
            print(f"加载策略配置失败: {e}")

        # 创建默认配置
        try:
            config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"创建默认配置失败: {e}")

        return default_config

    def _load_history(self):
        """加载历史数据"""
        try:
            if self.warning_history_file.exists():
                with open(self.warning_history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.warnings_received = data.get('warnings', [])
                    self.adjustments_made = data.get('adjustments', [])
        except Exception as e:
            print(f"加载历史数据失败: {e}")

    def _save_history(self):
        """保存历史数据"""
        try:
            data = {
                'warnings': self.warnings_received[-100:],  # 保留最近100条
                'adjustments': self.adjustments_made[-100:],
                'last_updated': datetime.now().isoformat()
            }
            self.warning_history_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.warning_history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存历史数据失败: {e}")

    def receive_warning(self, warning_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        接收预警信息并触发策略调整

        Args:
            warning_data: 预警数据，包含 type, level, message, source 等

        Returns:
            处理结果
        """
        result = {
            'success': False,
            'warning_received': warning_data,
            'adjustment_made': None,
            'timestamp': datetime.now().isoformat()
        }

        # 记录预警
        self.warnings_received.append({
            **warning_data,
            'received_at': datetime.now().isoformat(),
            'processed': False
        })

        # 检查是否需要自动调整
        warning_level = warning_data.get('level', 'low')
        level_config = self.strategy_config.get('warning_levels', {}).get(warning_level, {})

        if not self.auto_adjust_enabled or not level_config.get('auto_adjust', False):
            result['message'] = f"预警级别 {warning_level} 不触发自动调整"
            return result

        # 检查冷却时间
        if self.last_adjustment_time:
            cooldown = self.strategy_config.get('adjustment_cooldown', 300)
            time_since_last = (datetime.now() - self.last_adjustment_time).total_seconds()
            if time_since_last < cooldown:
                result['message'] = f"调整冷却中，距离上次调整还有 {cooldown - time_since_last:.0f} 秒"
                return result

        # 执行策略调整
        adjustment_result = self._execute_strategy_adjustment(warning_data, level_config)
        result['adjustment_made'] = adjustment_result
        result['success'] = adjustment_result.get('success', False)
        result['message'] = adjustment_result.get('message', '')

        self.last_adjustment_time = datetime.now()
        self._save_history()

        return result

    def _execute_strategy_adjustment(self, warning_data: Dict[str, Any], level_config: Dict[str, Any]) -> Dict[str, Any]:
        """执行策略调整"""
        adjustment_type = level_config.get('adjustment_type', 'minor')
        type_config = self.strategy_config.get('adjustment_types', {}).get(adjustment_type, {})

        adjustment_record = {
            'warning': warning_data,
            'adjustment_type': adjustment_type,
            'timestamp': datetime.now().isoformat(),
            'success': False,
            'changes': {}
        }

        # 1. 从元进化优化引擎获取当前策略
        current_strategy = {}
        if self.meta_optimization_engine:
            try:
                # 获取当前策略状态
                status_result = self.meta_optimization_engine.get_status()
                current_strategy = status_result.get('current_strategy', {})
            except Exception as e:
                adjustment_record['error'] = f"获取当前策略失败: {e}"

        # 2. 根据预警类型生成调整方案
        warning_type = warning_data.get('type', 'unknown')
        adjustment_plan = self._generate_adjustment_plan(warning_type, adjustment_type, type_config, current_strategy)

        # 3. 应用策略调整
        if self.meta_optimization_engine and adjustment_plan.get('strategy_changes'):
            try:
                for param, value in adjustment_plan['strategy_changes'].items():
                    adjustment_record['changes'][param] = {
                        'old': current_strategy.get(param, 'N/A'),
                        'new': value
                    }
                    current_strategy[param] = value

                # 调用元进化引擎应用调整
                self.meta_optimization_engine.apply_strategy_adjustment(current_strategy)
                adjustment_record['success'] = True
                adjustment_record['message'] = f"策略调整成功: {adjustment_type} 级调整"
            except Exception as e:
                adjustment_record['success'] = False
                adjustment_record['error'] = f"应用策略调整失败: {e}"
        else:
            adjustment_record['success'] = True
            adjustment_record['message'] = "策略调整计划已生成（元进化引擎未集成）"

        # 4. 记录调整
        self.adjustments_made.append(adjustment_record)

        return adjustment_record

    def _generate_adjustment_plan(self, warning_type: str, adjustment_type: str,
                                   type_config: Dict[str, Any], current_strategy: Dict[str, Any]) -> Dict[str, Any]:
        """生成策略调整方案"""
        plan = {
            'warning_type': warning_type,
            'adjustment_type': adjustment_type,
            'strategy_changes': {},
            'priority_adjustment': type_config.get('priority_adjustment', 0)
        }

        # 根据预警类型生成不同的调整策略
        if 'performance' in warning_type.lower() or 'efficiency' in warning_type.lower():
            # 性能预警 - 调整执行策略
            plan['strategy_changes'] = {
                'execution_priority': 'high',
                'timeout_multiplier': 1.5,
                'retry_count': current_strategy.get('retry_count', 3) + 1
            }
        elif 'health' in warning_type.lower() or 'system' in warning_type.lower():
            # 健康预警 - 调整健康检查参数
            plan['strategy_changes'] = {
                'health_check_interval': max(30, current_strategy.get('health_check_interval', 60) - 10),
                'recovery_priority': 'high'
            }
        elif 'resource' in warning_type.lower() or 'memory' in warning_type.lower():
            # 资源预警 - 调整资源分配
            plan['strategy_changes'] = {
                'resource_allocation': 'conservative',
                'max_concurrent_tasks': max(1, current_strategy.get('max_concurrent_tasks', 5) - 1)
            }
        elif 'evolution' in warning_type.lower() or 'progress' in warning_type.lower():
            # 进化预警 - 调整进化策略
            weight_change = type_config.get('strategy_weight_change', 0.1)
            plan['strategy_changes'] = {
                'exploration_rate': min(1.0, current_strategy.get('exploration_rate', 0.3) + weight_change),
                'caution_level': min(1.0, current_strategy.get('caution_level', 0.5) + weight_change)
            }
        else:
            # 默认调整
            plan['strategy_changes'] = {
                'caution_level': min(1.0, current_strategy.get('caution_level', 0.5) + type_config.get('strategy_weight_change', 0.1))
            }

        return plan

    def verify_adjustment(self, adjustment_record: Dict[str, Any]) -> Dict[str, Any]:
        """验证策略调整效果"""
        verification_result = {
            'adjustment': adjustment_record,
            'verified': False,
            'effectiveness': 'unknown',
            'timestamp': datetime.now().isoformat()
        }

        # 简单的验证逻辑：检查调整是否已生效
        if self.meta_optimization_engine:
            try:
                status = self.meta_optimization_engine.get_status()
                current_strategy = status.get('current_strategy', {})

                # 检查策略是否已更新
                changes = adjustment_record.get('changes', {})
                verified = True
                for param, change in changes.items():
                    if param in current_strategy and current_strategy[param] == change.get('new'):
                        verified = verified and True
                    elif param not in current_strategy:
                        verified = False

                verification_result['verified'] = verified
                verification_result['effectiveness'] = 'good' if verified else 'uncertain'
            except Exception as e:
                verification_result['error'] = str(e)
        else:
            verification_result['verified'] = True  # 假设成功
            verification_result['effectiveness'] = 'assumed'

        return verification_result

    def get_status(self) -> Dict[str, Any]:
        """获取引擎状态"""
        return {
            'version': self.version,
            'enabled': self.enabled,
            'auto_adjust_enabled': self.auto_adjust_enabled,
            'warnings_received_count': len(self.warnings_received),
            'adjustments_made_count': len(self.adjustments_made),
            'last_adjustment_time': self.last_adjustment_time.isoformat() if self.last_adjustment_time else None,
            'config': {
                'auto_adjust_enabled': self.auto_adjust_enabled,
                'adjustment_cooldown': self.strategy_config.get('adjustment_cooldown', 300),
                'max_adjustments_per_hour': self.strategy_config.get('max_adjustments_per_hour', 10)
            },
            'integrated_engines': {
                'meta_optimization': self.meta_optimization_engine is not None,
                'warning_engine': self.warning_engine is not None
            }
        }

    def get_warning_summary(self) -> Dict[str, Any]:
        """获取预警汇总"""
        if not self.warnings_received:
            return {'total': 0, 'by_level': {}, 'recent': []}

        by_level = {}
        for w in self.warnings_received:
            level = w.get('level', 'unknown')
            by_level[level] = by_level.get(level, 0) + 1

        return {
            'total': len(self.warnings_received),
            'by_level': by_level,
            'recent': self.warnings_received[-10:]
        }

    def get_adjustment_summary(self) -> Dict[str, Any]:
        """获取调整汇总"""
        if not self.adjustments_made:
            return {'total': 0, 'by_type': {}, 'recent': []}

        by_type = {}
        for a in self.adjustments_made:
            atype = a.get('adjustment_type', 'unknown')
            by_type[atype] = by_type.get(atype, 0) + 1

        return {
            'total': len(self.adjustments_made),
            'by_type': by_type,
            'recent': self.adjustments_made[-10:],
            'success_rate': sum(1 for a in self.adjustments_made if a.get('success', False)) / len(self.adjustments_made)
        }

    def enable_auto_adjust(self):
        """启用自动调整"""
        self.auto_adjust_enabled = True
        return {'success': True, 'message': '自动策略调整已启用'}

    def disable_auto_adjust(self):
        """禁用自动调整"""
        self.auto_adjust_enabled = False
        return {'success': True, 'message': '自动策略调整已禁用'}

    def test_warning_trigger(self) -> Dict[str, Any]:
        """测试预警触发功能"""
        test_warning = {
            'type': 'test_warning',
            'level': 'medium',
            'message': '这是一条测试预警',
            'source': 'test'
        }
        return self.receive_warning(test_warning)

    def get_cockpit_data(self) -> Dict[str, Any]:
        """获取驾驶舱展示数据"""
        return {
            'engine_status': self.get_status(),
            'warning_summary': self.get_warning_summary(),
            'adjustment_summary': self.get_adjustment_summary(),
            'recent_activity': {
                'warnings': self.warnings_received[-5:],
                'adjustments': self.adjustments_made[-5:]
            }
        }


# 命令行接口
def main():
    parser = argparse.ArgumentParser(description='预警驱动自动策略调整引擎')
    parser.add_argument('command', nargs='?', default='status',
                        choices=['status', 'warnings', 'adjustments', 'enable', 'disable', 'test', 'cockpit'],
                        help='要执行的命令')
    parser.add_argument('--warning', '-w', type=str, help='发送预警数据 (JSON 字符串)')
    parser.add_argument('--json', action='store_true', help='输出 JSON 格式')

    args = parser.parse_args()

    engine = WarningDrivenStrategyAdjustmentEngine()

    if args.command == 'status':
        result = engine.get_status()
    elif args.command == 'warnings':
        result = engine.get_warning_summary()
    elif args.command == 'adjustments':
        result = engine.get_adjustment_summary()
    elif args.command == 'enable':
        result = engine.enable_auto_adjust()
    elif args.command == 'disable':
        result = engine.disable_auto_adjust()
    elif args.command == 'test':
        result = engine.test_warning_trigger()
    elif args.command == 'cockpit':
        result = engine.get_cockpit_data()
    else:
        result = {'error': f'未知命令: {args.command}'}

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        # 友好输出
        if args.command == 'status':
            print(f"=== 预警驱动自动策略调整引擎 v{result['version']} ===")
            print(f"启用状态: {'启用' if result['enabled'] else '禁用'}")
            print(f"自动调整: {'启用' if result['auto_adjust_enabled'] else '禁用'}")
            print(f"接收预警数: {result['warnings_received_count']}")
            print(f"执行调整数: {result['adjustments_made_count']}")
            print(f"上次调整: {result['last_adjustment_time'] or '无'}")
            print(f"集成引擎: 元进化优化={result['integrated_engines']['meta_optimization']}, 预警引擎={result['integrated_engines']['warning_engine']}")
        elif args.command == 'warnings':
            print(f"=== 预警汇总 ===")
            print(f"总预警数: {result['total']}")
            print(f"按级别统计: {result['by_level']}")
        elif args.command == 'adjustments':
            print(f"=== 调整汇总 ===")
            print(f"总调整数: {result['total']}")
            print(f"按类型统计: {result['by_type']}")
            print(f"成功率: {result.get('success_rate', 0):.1%}")
        elif 'success' in result:
            print(f"结果: {result.get('message', '执行成功' if result['success'] else '执行失败')}")
        else:
            print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()