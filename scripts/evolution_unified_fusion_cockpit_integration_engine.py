#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景统一智能体融合引擎与进化驾驶舱深度集成引擎

将 round 393 的统一智能体融合引擎与 round 350 的进化驾驶舱深度集成，
实现可视化的融合状态监控，让用户能够在驾驶舱中直观地看到统一智能体的运行状态。

功能：
1. 融合状态实时监控与可视化
2. 融合引擎与驾驶舱数据互通
3. 融合历史趋势分析
4. 融合引擎健康度监控
5. 一键启动/停止融合引擎
6. 融合状态告警与自动处理

Version: 1.0.0

依赖：
- evolution_unified_intelligent_body_fusion_engine.py (round 393)
- evolution_cockpit_engine.py (round 350)
"""

import os
import sys
import json
import time
import threading
from datetime import datetime
from typing import Dict, List, Any, Optional

# 添加 scripts 目录到 Python 路径
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPTS_DIR)
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# 导入依赖引擎
try:
    from evolution_unified_intelligent_body_fusion_engine import EvolutionUnifiedIntelligentBodyFusionEngine
except ImportError:
    EvolutionUnifiedIntelligentBodyFusionEngine = None

try:
    from evolution_cockpit_engine import EvolutionCockpitEngine
except ImportError:
    EvolutionCockpitEngine = None


class EvolutionUnifiedFusionCockpitIntegrationEngine:
    """统一智能体融合引擎与进化驾驶舱深度集成引擎"""

    VERSION = "1.0.0"

    def __init__(self):
        self.name = "统一智能体融合驾驶舱集成引擎"
        self.description = "统一智能体融合引擎与进化驾驶舱深度集成，实现可视化融合状态监控"

        # 初始化引擎
        self.fusion_engine = None
        self.cockpit_engine = None
        self._init_engines()

        # 配置
        self.config = {
            'integration_enabled': True,
            'auto_monitor': True,
            'monitor_interval': 60,  # 监控间隔（秒）
            'health_check_enabled': True,
            'alert_threshold': 30,   # 告警阈值（融合分数低于此值告警）
            'auto_recovery_enabled': True,
        }

        # 状态
        self.state_file = "runtime/state/unified_fusion_cockpit_state.json"
        self.state = self._load_state()

        # 监控线程
        self.monitor_thread = None
        self.stop_monitor = False

    def _init_engines(self):
        """初始化引擎"""
        if EvolutionUnifiedIntelligentBodyFusionEngine:
            try:
                self.fusion_engine = EvolutionUnifiedIntelligentBodyFusionEngine()
                print(f"[{self.name}] 统一智能体融合引擎已加载")
            except Exception as e:
                print(f"[{self.name}] 加载统一智能体融合引擎失败: {e}")
        else:
            print(f"[{self.name}] 统一智能体融合引擎模块未找到")

        if EvolutionCockpitEngine:
            try:
                self.cockpit_engine = EvolutionCockpitEngine()
                print(f"[{self.name}] 进化驾驶舱引擎已加载")
            except Exception as e:
                print(f"[{self.name}] 加载进化驾驶舱引擎失败: {e}")
        else:
            print(f"[{self.name}] 进化驾驶舱引擎模块未找到")

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
            'last_fusion_score': 0,
            'monitoring_active': False,
            'alert_history': [],
            'fusion_engine_enabled': True,
            'cockpit_integration_active': False,
        }

    def _save_state(self):
        """保存状态"""
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2)

    def get_fusion_status(self) -> Dict:
        """获取融合引擎状态"""
        if not self.fusion_engine:
            return {'error': '融合引擎未加载'}

        try:
            status = self.fusion_engine.get_status()
            return status
        except Exception as e:
            return {'error': str(e)}

    def get_cockpit_status(self) -> Dict:
        """获取驾驶舱状态"""
        if not self.cockpit_engine:
            return {'error': '驾驶舱引擎未加载'}

        try:
            # 简化驾驶舱状态获取
            return {
                'engine': 'EvolutionCockpitEngine',
                'version': self.cockpit_engine.version,
                'running': self.cockpit_engine.running,
                'auto_mode': self.cockpit_engine.auto_mode,
            }
        except Exception as e:
            return {'error': str(e)}

    def get_integrated_status(self) -> Dict:
        """获取集成状态"""
        fusion_status = self.get_fusion_status()
        cockpit_status = self.get_cockpit_status()

        # 计算健康分数
        health_score = 100
        if 'error' not in fusion_status:
            fusion_score = fusion_status.get('last_fusion_score', 0)
            health_score = min(100, fusion_score + 20)  # 基础分加融合分数
        else:
            health_score = 50

        return {
            'timestamp': datetime.now().isoformat(),
            'integration_cycle': self.state['integration_cycle_count'],
            'fusion_engine': {
                'loaded': self.fusion_engine is not None,
                'enabled': self.state.get('fusion_engine_enabled', True),
                'status': fusion_status,
            },
            'cockpit_engine': {
                'loaded': self.cockpit_engine is not None,
                'active': self.state.get('cockpit_integration_active', False),
                'status': cockpit_status,
            },
            'health_score': health_score,
            'monitoring_active': self.state.get('monitoring_active', False),
            'config': self.config,
        }

    def run_full_integration_cycle(self) -> Dict:
        """运行完整的集成循环"""
        print(f"\n[{self.name}] 开始执行集成循环...")

        # 获取融合引擎状态
        fusion_status = self.get_fusion_status()
        print(f"[1/3] 融合引擎状态: {'正常' if 'error' not in fusion_status else '异常'}")

        # 获取驾驶舱状态
        cockpit_status = self.get_cockpit_status()
        print(f"[2/3] 驾驶舱状态: {'正常' if 'error' not in cockpit_status else '异常'}")

        # 计算健康分数
        integrated_status = self.get_integrated_status()
        health_score = integrated_status['health_score']

        # 更新状态
        self.state['integration_cycle_count'] += 1
        self.state['last_integration_timestamp'] = datetime.now().isoformat()
        self.state['last_fusion_score'] = fusion_status.get('last_fusion_score', 0)
        self._save_state()

        # 检查告警
        if health_score < self.config['alert_threshold']:
            self._handle_alert(health_score)

        summary = {
            'timestamp': datetime.now().isoformat(),
            'integration_cycle': self.state['integration_cycle_count'],
            'health_score': health_score,
            'fusion_status': fusion_status,
            'cockpit_status': cockpit_status,
            'conclusion': '集成循环完成'
        }

        print(f"\n[{self.name}] 集成循环执行完成")
        print(f"  健康分数: {health_score}")
        print(f"  融合分数: {self.state['last_fusion_score']}")

        return summary

    def _handle_alert(self, score: float):
        """处理告警"""
        alert = {
            'timestamp': datetime.now().isoformat(),
            'score': score,
            'threshold': self.config['alert_threshold'],
            'message': f'融合健康分数 {score} 低于阈值 {self.config["alert_threshold"]}'
        }

        self.state['alert_history'].append(alert)
        self.state['alert_history'] = self.state['alert_history'][-20:]  # 保留最近20条
        self._save_state()

        print(f"[{self.name}] 警告: {alert['message']}")

    def start_monitoring(self):
        """启动监控"""
        if self.monitor_thread and self.monitor_thread.is_alive():
            print(f"[{self.name}] 监控已在运行中")
            return

        self.stop_monitor = False
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        self.state['monitoring_active'] = True
        self._save_state()
        print(f"[{self.name}] 监控已启动")

    def stop_monitoring(self):
        """停止监控"""
        self.stop_monitor = True
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        self.state['monitoring_active'] = False
        self._save_state()
        print(f"[{self.name}] 监控已停止")

    def _monitor_loop(self):
        """监控循环"""
        while not self.stop_monitor:
            try:
                self.run_full_integration_cycle()
            except Exception as e:
                print(f"[{self.name}] 监控循环异常: {e}")

            time.sleep(self.config['monitor_interval'])

    def enable_fusion_engine(self):
        """启用融合引擎"""
        if self.fusion_engine:
            self.fusion_engine.enable()
            self.state['fusion_engine_enabled'] = True
            self._save_state()

    def disable_fusion_engine(self):
        """禁用融合引擎"""
        if self.fusion_engine:
            self.fusion_engine.disable()
            self.state['fusion_engine_enabled'] = False
            self._save_state()

    def get_fusion_history(self) -> List[Dict]:
        """获取融合历史"""
        if self.fusion_engine:
            return self.fusion_engine.get_fusion_history()
        return []

    def get_alert_history(self) -> List[Dict]:
        """获取告警历史"""
        return self.state.get('alert_history', [])

    def get_status(self) -> Dict:
        """获取状态"""
        return self.get_integrated_status()


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='统一智能体融合驾驶舱集成引擎')
    parser.add_argument('command', nargs='?', default='status',
                       choices=['status', 'full_cycle', 'fusion_status', 'cockpit_status',
                               'history', 'alerts', 'start_monitor', 'stop_monitor',
                               'enable_fusion', 'disable_fusion'],
                       help='命令')

    args = parser.parse_args()

    engine = EvolutionUnifiedFusionCockpitIntegrationEngine()

    if args.command == 'status':
        result = engine.get_status()
        print("\n=== 统一智能体融合驾驶舱集成引擎状态 ===")
        print(f"引擎: {result.get('timestamp', '')}")
        print(f"健康分数: {result.get('health_score', 0)}")
        print(f"融合引擎已加载: {result.get('fusion_engine', {}).get('loaded', False)}")
        print(f"驾驶舱引擎已加载: {result.get('cockpit_engine', {}).get('loaded', False)}")
        print(f"监控状态: {'运行中' if result.get('monitoring_active') else '已停止'}")

    elif args.command == 'full_cycle':
        result = engine.run_full_integration_cycle()
        print("\n=== 完整集成循环结果 ===")
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == 'fusion_status':
        result = engine.get_fusion_status()
        print("\n=== 融合引擎状态 ===")
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == 'cockpit_status':
        result = engine.get_cockpit_status()
        print("\n=== 驾驶舱状态 ===")
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == 'history':
        result = engine.get_fusion_history()
        print("\n=== 融合历史 ===")
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == 'alerts':
        result = engine.get_alert_history()
        print("\n=== 告警历史 ===")
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == 'start_monitor':
        engine.start_monitoring()

    elif args.command == 'stop_monitor':
        engine.stop_monitoring()

    elif args.command == 'enable_fusion':
        engine.enable_fusion_engine()

    elif args.command == 'disable_fusion':
        engine.disable_fusion_engine()


if __name__ == "__main__":
    main()