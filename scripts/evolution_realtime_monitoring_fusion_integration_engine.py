#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环实时监控与融合状态深度集成引擎

将 round 394 的融合驾驶舱监控数据与 round 362 的进化环实时监控引擎深度集成，
实现统一的监控视图和丰富的可视化展示能力。

功能：
1. 统一监控数据源（融合状态 + 实时监控）
2. 融合状态与系统健康联动分析
3. 跨引擎健康态势统一感知
4. 智能预警融合（同时考虑融合分数和系统指标）
5. 统一可视化展示
6. 端到端状态闭环

Version: 1.0.0

依赖：
- evolution_unified_fusion_cockpit_integration_engine.py (round 394)
- evolution_realtime_monitoring_warning_engine.py (round 362)
"""

import os
import sys
import json
import time
import threading
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from collections import deque

# 添加 scripts 目录到 Python 路径
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPTS_DIR)
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# 导入依赖引擎
try:
    from evolution_unified_fusion_cockpit_integration_engine import EvolutionUnifiedFusionCockpitIntegrationEngine
except ImportError:
    EvolutionUnifiedFusionCockpitIntegrationEngine = None

try:
    from evolution_realtime_monitoring_warning_engine import EvolutionRealtimeMonitoringEngine
except ImportError:
    EvolutionRealtimeMonitoringEngine = None


class EvolutionRealtimeMonitoringFusionIntegrationEngine:
    """进化环实时监控与融合状态深度集成引擎"""

    VERSION = "1.0.0"

    def __init__(self):
        self.name = "进化环实时监控与融合状态深度集成引擎"
        self.description = "深度集成实时监控与融合驾驶舱，提供统一监控视图和丰富可视化"

        # 初始化引擎
        self.fusion_integration_engine = None
        self.monitoring_engine = None
        self._init_engines()

        # 配置
        self.config = {
            'integration_enabled': True,
            'auto_monitor': True,
            'monitor_interval': 30,  # 监控间隔（秒）
            'health_check_enabled': True,
            'unified_warning_enabled': True,  # 统一预警
            'visualization_data_enabled': True,  # 可视化数据
            'alert_threshold': {
                'fusion_score_low': 50,     # 融合分数低于此值告警
                'system_health_low': 60,    # 系统健康度低于此值告警
                'combined_health_low': 55, # 综合健康度低于此值告警
            }
        }

        # 状态
        self.state_file = "runtime/state/realtime_monitoring_fusion_state.json"
        self.state = self._load_state()

        # 监控线程
        self.monitor_thread = None
        self.stop_monitor = False

        # 统一监控数据缓存
        self.unified_data_cache = deque(maxlen=100)
        self.unified_warnings = deque(maxlen=50)

    def _init_engines(self):
        """初始化引擎"""
        # 融合驾驶舱集成引擎
        if EvolutionUnifiedFusionCockpitIntegrationEngine:
            try:
                self.fusion_integration_engine = EvolutionUnifiedFusionCockpitIntegrationEngine()
                print(f"[{self.name}] 融合驾驶舱集成引擎已加载")
            except Exception as e:
                print(f"[{self.name}] 加载融合驾驶舱集成引擎失败: {e}")
        else:
            print(f"[{self.name}] 融合驾驶舱集成引擎模块未找到")

        # 实时监控引擎
        try:
            self.monitoring_engine = EvolutionRealtimeMonitoringEngine()
            print(f"[{self.name}] 实时监控引擎已加载")
        except Exception as e:
            print(f"[{self.name}] 加载实时监控引擎失败: {e}")
            # 如果无法导入，则使用备用实现
            self.monitoring_engine = self._create_backup_monitoring()

    def _create_backup_monitoring(self):
        """创建备用监控实现"""
        class BackupMonitoring:
            def __init__(self):
                self.is_monitoring = False

            def get_status(self):
                return {
                    'is_monitoring': False,
                    'current_status': {},
                    'active_warnings': [],
                    'warnings_count': 0,
                    'health_score': 0,
                }

            def check_and_warn(self):
                return {
                    'status': 'ok',
                    'system_metrics': {},
                    'evolution_status': {},
                    'anomalies_count': 0,
                    'new_warnings': [],
                    'active_warnings': []
                }

        return BackupMonitoring()

    def _load_state(self) -> Dict:
        """加载状态"""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"[{self.name}] 加载状态失败: {e}")

        return {
            'integration_cycle_count': 0,
            'last_integration_timestamp': '',
            'last_unified_health_score': 0,
            'last_fusion_health_score': 0,
            'last_system_health_score': 0,
            'monitoring_active': False,
            'unified_warning_history': [],
            'visualization_data_history': [],
        }

    def _save_state(self):
        """保存状态"""
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2)

    def get_fusion_status(self) -> Dict:
        """获取融合状态"""
        if not self.fusion_integration_engine:
            return {'error': '融合集成引擎未加载', 'loaded': False}

        try:
            status = self.fusion_integration_engine.get_integrated_status()
            return {
                'loaded': True,
                'health_score': status.get('health_score', 0),
                'fusion_engine': status.get('fusion_engine', {}),
                'cockpit_engine': status.get('cockpit_engine', {}),
                'monitoring_active': status.get('monitoring_active', False),
                'integration_cycle': status.get('integration_cycle', 0),
            }
        except Exception as e:
            return {'error': str(e), 'loaded': False}

    def get_monitoring_status(self) -> Dict:
        """获取实时监控状态"""
        if not self.monitoring_engine:
            return {'error': '监控引擎未加载', 'loaded': False}

        try:
            status = self.monitoring_engine.get_status()
            return {
                'loaded': True,
                'is_monitoring': status.get('is_monitoring', False),
                'health_score': status.get('health_score', 0),
                'system_metrics': status.get('current_status', {}),
                'warnings_count': status.get('warnings_count', 0),
                'active_warnings': status.get('active_warnings', []),
            }
        except Exception as e:
            return {'error': str(e), 'loaded': False}

    def calculate_unified_health_score(self, fusion_status: Dict, monitoring_status: Dict) -> Tuple[float, Dict]:
        """计算统一健康分数"""
        fusion_score = fusion_status.get('health_score', 0) if fusion_status.get('loaded') else 50
        system_score = monitoring_status.get('health_score', 0) if monitoring_status.get('loaded') else 50

        # 加权计算综合健康分数
        # 融合引擎权重稍高，因为是本轮重点
        unified_score = (fusion_score * 0.55) + (system_score * 0.45)

        # 考虑加载状态
        if not fusion_status.get('loaded', False):
            unified_score *= 0.7
        if not monitoring_status.get('loaded', False):
            unified_score *= 0.7

        details = {
            'fusion_health_score': fusion_score,
            'system_health_score': system_score,
            'fusion_loaded': fusion_status.get('loaded', False),
            'monitoring_loaded': monitoring_status.get('loaded', False),
            'calculation_method': 'weighted_average (fusion=0.55, system=0.45)',
        }

        return round(unified_score, 2), details

    def generate_unified_warnings(self, fusion_status: Dict, monitoring_status: Dict, unified_score: float) -> List[Dict]:
        """生成统一预警"""
        warnings = []
        thresholds = self.config['alert_threshold']

        # 融合分数预警
        if fusion_status.get('loaded') and fusion_status.get('health_score', 100) < thresholds['fusion_score_low']:
            warnings.append({
                'type': 'fusion_health_low',
                'level': 'warning',
                'message': f"融合引擎健康分数过低: {fusion_status.get('health_score')}",
                'source': 'fusion_integration',
                'timestamp': datetime.now().isoformat(),
            })

        # 系统健康预警
        if monitoring_status.get('loaded') and monitoring_status.get('health_score', 100) < thresholds['system_health_low']:
            warnings.append({
                'type': 'system_health_low',
                'level': 'warning',
                'message': f"系统健康分数过低: {monitoring_status.get('health_score')}",
                'source': 'monitoring',
                'timestamp': datetime.now().isoformat(),
            })

        # 综合健康预警
        if unified_score < thresholds['combined_health_low']:
            warnings.append({
                'type': 'unified_health_low',
                'level': 'critical',
                'message': f"综合健康分数过低: {unified_score}，需要关注融合引擎和系统监控状态",
                'source': 'unified_integration',
                'timestamp': datetime.now().isoformat(),
            })

        # 实时监控预警传递
        if monitoring_status.get('loaded'):
            active_warnings = monitoring_status.get('active_warnings', [])
            for w in active_warnings:
                if w.get('level') in ['critical', 'emergency']:
                    warnings.append({
                        'type': f"system_{w.get('type', 'warning')}",
                        'level': w.get('level', 'warning'),
                        'message': f"系统预警: {w.get('message', '')}",
                        'source': 'monitoring',
                        'timestamp': datetime.now().isoformat(),
                    })

        return warnings

    def get_unified_status(self) -> Dict:
        """获取统一状态"""
        fusion_status = self.get_fusion_status()
        monitoring_status = self.get_monitoring_status()

        # 计算统一健康分数
        unified_score, health_details = self.calculate_unified_health_score(fusion_status, monitoring_status)

        # 生成统一预警
        unified_warnings = self.generate_unified_warnings(fusion_status, monitoring_status, unified_score)

        # 系统指标
        system_metrics = {}
        if monitoring_status.get('loaded'):
            system_metrics = monitoring_status.get('system_metrics', {})

        return {
            'timestamp': datetime.now().isoformat(),
            'integration_cycle': self.state['integration_cycle_count'],
            'unified_health_score': unified_score,
            'health_details': health_details,
            'fusion_status': {
                'loaded': fusion_status.get('loaded', False),
                'health_score': fusion_status.get('health_score', 0),
                'integration_cycle': fusion_status.get('integration_cycle', 0),
                'monitoring_active': fusion_status.get('monitoring_active', False),
            },
            'monitoring_status': {
                'loaded': monitoring_status.get('loaded', False),
                'health_score': monitoring_status.get('health_score', 0),
                'is_monitoring': monitoring_status.get('is_monitoring', False),
                'warnings_count': monitoring_status.get('warnings_count', 0),
            },
            'system_metrics': system_metrics,
            'unified_warnings': unified_warnings,
            'warnings_count': len(unified_warnings),
            'monitoring_active': self.state.get('monitoring_active', False),
            'config': self.config,
        }

    def run_full_integration_cycle(self) -> Dict:
        """运行完整的集成循环"""
        print(f"\n[{self.name}] 开始执行集成循环...")

        # 获取融合状态
        fusion_status = self.get_fusion_status()
        print(f"[1/4] 融合状态: {'已加载' if fusion_status.get('loaded') else '未加载'}")

        # 获取监控状态
        monitoring_status = self.get_monitoring_status()
        print(f"[2/4] 监控状态: {'已加载' if monitoring_status.get('loaded') else '未加载'}")

        # 计算统一健康分数
        unified_score, health_details = self.calculate_unified_health_score(fusion_status, monitoring_status)
        print(f"[3/4] 综合健康分数: {unified_score}")

        # 生成统一预警
        unified_warnings = self.generate_unified_warnings(fusion_status, monitoring_status, unified_score)
        print(f"[4/4] 统一预警数量: {len(unified_warnings)}")

        # 更新状态
        self.state['integration_cycle_count'] += 1
        self.state['last_integration_timestamp'] = datetime.now().isoformat()
        self.state['last_unified_health_score'] = unified_score
        self.state['last_fusion_health_score'] = health_details.get('fusion_health_score', 0)
        self.state['last_system_health_score'] = health_details.get('system_health_score', 0)

        # 保存预警历史
        if unified_warnings:
            self.state['unified_warning_history'].extend(unified_warnings)
            self.state['unified_warning_history'] = self.state['unified_warning_history'][-30:]

        self._save_state()

        # 缓存统一数据
        unified_data = {
            'timestamp': datetime.now().isoformat(),
            'unified_health_score': unified_score,
            'fusion_status': fusion_status,
            'monitoring_status': monitoring_status,
            'warnings': unified_warnings,
        }
        self.unified_data_cache.append(unified_data)

        summary = {
            'timestamp': datetime.now().isoformat(),
            'integration_cycle': self.state['integration_cycle_count'],
            'unified_health_score': unified_score,
            'health_details': health_details,
            'unified_warnings_count': len(unified_warnings),
            'unified_warnings': unified_warnings,
            'conclusion': '集成循环完成'
        }

        print(f"\n[{self.name}] 集成循环执行完成")
        print(f"  综合健康分数: {unified_score}")
        print(f"  融合健康分数: {health_details.get('fusion_health_score', 0)}")
        print(f"  系统健康分数: {health_details.get('system_health_score', 0)}")
        if unified_warnings:
            print(f"  预警信息:")
            for w in unified_warnings:
                print(f"    - [{w.get('level')}] {w.get('message')}")

        return summary

    def get_visualization_data(self) -> Dict:
        """获取可视化数据"""
        # 历史趋势数据
        history_data = list(self.unified_data_cache)

        # 预警趋势
        warning_trends = []
        for data in history_data:
            warning_trends.append({
                'timestamp': data.get('timestamp'),
                'warnings_count': len(data.get('warnings', [])),
                'health_score': data.get('unified_health_score'),
            })

        # 当前状态
        current_status = self.get_unified_status()

        # 健康分数趋势
        health_trend = []
        if len(history_data) >= 2:
            # 计算趋势
            recent_scores = [d.get('unified_health_score', 0) for d in history_data[-10:]]
            avg_score = sum(recent_scores) / len(recent_scores) if recent_scores else 0
            trend_direction = "stable"
            if len(recent_scores) >= 2:
                if recent_scores[-1] > recent_scores[0]:
                    trend_direction = "improving"
                elif recent_scores[-1] < recent_scores[0]:
                    trend_direction = "declining"

            health_trend = {
                'direction': trend_direction,
                'average': round(avg_score, 2),
                'current': recent_scores[-1] if recent_scores else 0,
                'samples': len(recent_scores),
            }

        return {
            'timestamp': datetime.now().isoformat(),
            'current_status': {
                'health_score': current_status.get('unified_health_score'),
                'warnings_count': current_status.get('warnings_count'),
                'fusion_health': current_status.get('fusion_status', {}).get('health_score'),
                'system_health': current_status.get('monitoring_status', {}).get('health_score'),
            },
            'health_trend': health_trend,
            'warning_trends': warning_trends[-20:] if warning_trends else [],
            'history_samples': len(history_data),
        }

    def start_monitoring(self):
        """启动监控"""
        if self.monitor_thread and self.monitor_thread.is_alive():
            print(f"[{self.name}] 监控已在运行中")
            return {'status': 'already_running'}

        self.stop_monitor = False
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        self.state['monitoring_active'] = True
        self._save_state()
        print(f"[{self.name}] 监控已启动")
        return {'status': 'started', 'interval': self.config['monitor_interval']}

    def stop_monitoring(self):
        """停止监控"""
        self.stop_monitor = True
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        self.state['monitoring_active'] = False
        self._save_state()
        print(f"[{self.name}] 监控已停止")
        return {'status': 'stopped'}

    def _monitor_loop(self):
        """监控循环"""
        while not self.stop_monitor:
            try:
                self.run_full_integration_cycle()
            except Exception as e:
                print(f"[{self.name}] 监控循环异常: {e}")

            time.sleep(self.config['monitor_interval'])

    def get_warning_history(self, limit: int = 20) -> List[Dict]:
        """获取预警历史"""
        history = self.state.get('unified_warning_history', [])
        return history[-limit:]

    def get_status(self) -> Dict:
        """获取状态"""
        return self.get_unified_status()

    def check(self) -> Dict:
        """执行一次检查"""
        return self.run_full_integration_cycle()


# 全局实例
_integration_engine = None


def get_integration_engine() -> EvolutionRealtimeMonitoringFusionIntegrationEngine:
    """获取集成引擎实例"""
    global _integration_engine
    if _integration_engine is None:
        _integration_engine = EvolutionRealtimeMonitoringFusionIntegrationEngine()
    return _integration_engine


def handle_command(command: str, args: list = None) -> Dict[str, Any]:
    """处理命令"""
    engine = get_integration_engine()
    args = args or []

    if command in ["status", "状态", "融合监控状态"]:
        return engine.get_status()

    elif command in ["check", "检查", "检测", "融合监控检测"]:
        return engine.check()

    elif command in ["visualization", "可视化", "可视化数据"]:
        return engine.get_visualization_data()

    elif command in ["warnings", "预警", "预警列表"]:
        limit = int(args[0]) if args and args[0].isdigit() else 20
        return {
            "status": "ok",
            "warnings": engine.get_warning_history(limit)
        }

    elif command in ["fusion_status", "融合状态"]:
        return engine.get_fusion_status()

    elif command in ["monitoring_status", "监控状态"]:
        return engine.get_monitoring_status()

    elif command in ["start", "启动", "启动监控"]:
        return engine.start_monitoring()

    elif command in ["stop", "停止", "停止监控"]:
        return engine.stop_monitoring()

    elif command in ["summary", "摘要"]:
        return {
            "status": "ok",
            "version": EvolutionRealtimeMonitoringFusionIntegrationEngine.VERSION,
            "monitoring_active": engine.state.get('monitoring_active', False),
            "integration_cycles": engine.state.get('integration_cycle_count', 0),
            "health_score": engine.get_unified_status().get('unified_health_score', 0),
        }

    else:
        return {
            "status": "error",
            "message": f"未知命令: {command}",
            "available_commands": [
                "status - 获取融合监控状态",
                "check - 执行一次融合监控检测",
                "visualization - 获取可视化数据",
                "warnings [limit] - 获取预警列表",
                "fusion_status - 获取融合状态",
                "monitoring_status - 获取监控状态",
                "start - 启动持续监控",
                "stop - 停止监控",
                "summary - 获取摘要"
            ]
        }


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='进化环实时监控与融合状态深度集成引擎')
    parser.add_argument('command', nargs='?', default='status',
                       choices=['status', 'check', 'visualization', 'warnings',
                               'fusion_status', 'monitoring_status',
                               'start', 'stop', 'summary'],
                       help='命令')

    args = parser.parse_args()

    engine = get_integration_engine()

    if args.command == 'status':
        result = engine.get_status()
        print("\n=== 进化环实时监控与融合状态深度集成引擎状态 ===")
        print(f"综合健康分数: {result.get('unified_health_score', 0)}")
        print(f"融合健康分数: {result.get('fusion_status', {}).get('health_score', 0)}")
        print(f"系统健康分数: {result.get('monitoring_status', {}).get('health_score', 0)}")
        print(f"预警数量: {result.get('warnings_count', 0)}")
        print(f"监控状态: {'运行中' if result.get('monitoring_active') else '已停止'}")

    elif args.command == 'check':
        result = engine.check()
        print("\n=== 融合监控检测结果 ===")
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == 'visualization':
        result = engine.get_visualization_data()
        print("\n=== 可视化数据 ===")
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == 'warnings':
        result = engine.get_warning_history()
        print("\n=== 预警历史 ===")
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == 'fusion_status':
        result = engine.get_fusion_status()
        print("\n=== 融合状态 ===")
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == 'monitoring_status':
        result = engine.get_monitoring_status()
        print("\n=== 监控状态 ===")
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == 'start':
        result = engine.start_monitoring()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == 'stop':
        result = engine.stop_monitoring()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == 'summary':
        result = handle_command('summary')
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()