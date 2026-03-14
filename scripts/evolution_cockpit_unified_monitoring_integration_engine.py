#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环统一监控数据与进化驾驶舱深度集成引擎（Round 396）

将 round 395 的统一监控数据（健康分数、预警、可视化数据）与进化驾驶舱深度集成，
在驾驶舱中实现统一的监控视图展示。系统能够：
1. 在驾驶舱中展示统一健康分数
2. 展示融合监控与系统监控的综合状态
3. 展示实时预警信息
4. 提供一键集成触发和状态查询

集成：evolution_cockpit_engine.py + evolution_realtime_monitoring_fusion_integration_engine.py

Version: 1.0.0
"""

import os
import sys
import json
import subprocess
import time
from datetime import datetime
from typing import Dict, List, Any, Optional

# 项目根目录
PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT)

SCRIPTS = os.path.join(PROJECT, "scripts")

try:
    from scripts.evolution_cockpit_engine import EvolutionCockpitEngine
except ImportError:
    # 尝试相对导入
    try:
        from evolution_cockpit_engine import EvolutionCockpitEngine
    except ImportError:
        EvolutionCockpitEngine = None


class EvolutionCockpitUnifiedMonitoringIntegrationEngine:
    """进化驾驶舱统一监控集成引擎"""

    VERSION = "1.0.0"
    name = "进化驾驶舱统一监控集成"

    def __init__(self):
        self.cockpit = None
        self.monitoring = None
        self.state = {
            'integration_active': False,
            'last_integration_timestamp': None,
            'integration_count': 0,
            'last_unified_health_score': 0,
            'last_cockpit_health': 0,
        }
        self._load_engines()

    def _load_engines(self):
        """加载驾驶舱和监控引擎"""
        # 加载进化驾驶舱
        if EvolutionCockpitEngine:
            try:
                self.cockpit = EvolutionCockpitEngine()
            except Exception as e:
                print(f"[驾驶舱集成] 加载进化驾驶舱失败: {e}")
                self.cockpit = None
        else:
            print(f"[驾驶舱集成] 无法导入 EvolutionCockpitEngine")

        # 加载融合监控引擎
        try:
            # 动态导入融合监控引擎
            monitoring_module_path = os.path.join(SCRIPTS, "evolution_realtime_monitoring_fusion_integration_engine.py")
            if os.path.exists(monitoring_module_path):
                import importlib.util
                spec = importlib.util.spec_from_file_location(
                    "evolution_realtime_monitoring_fusion_integration_engine",
                    monitoring_module_path
                )
                monitoring_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(monitoring_module)

                if hasattr(monitoring_module, 'get_integration_engine'):
                    self.monitoring = monitoring_module.get_integration_engine()
                    print(f"[驾驶舱集成] 融合监控引擎加载成功")
                else:
                    print(f"[驾驶舱集成] 融合监控引擎未找到 get_integration_engine")
            else:
                print(f"[驾驶舱集成] 融合监控引擎文件不存在")
        except Exception as e:
            print(f"[驾驶舱集成] 加载融合监控引擎失败: {e}")
            self.monitoring = None

    def get_integrated_status(self) -> Dict[str, Any]:
        """获取集成状态"""
        cockpit_status = {}
        monitoring_status = {}

        # 获取驾驶舱状态
        if self.cockpit:
            try:
                cockpit_status = {
                    'loaded': True,
                    'running': self.cockpit.running,
                    'auto_mode': self.cockpit.auto_mode,
                    'current_round': self.cockpit.current_evolution_round,
                    'version': self.cockpit.version,
                }
            except Exception as e:
                cockpit_status = {
                    'loaded': False,
                    'error': str(e)
                }
        else:
            cockpit_status = {'loaded': False}

        # 获取融合监控状态
        if self.monitoring:
            try:
                monitoring_status = self.monitoring.get_unified_status()
                monitoring_status['loaded'] = True
            except Exception as e:
                monitoring_status = {
                    'loaded': False,
                    'error': str(e)
                }
        else:
            monitoring_status = {'loaded': False}

        # 计算集成健康度
        integrated_health = 0
        if cockpit_status.get('loaded'):
            integrated_health += 50
        if monitoring_status.get('loaded'):
            integrated_health += 50

        # 统一健康分数
        unified_health = monitoring_status.get('unified_health_score', 0)

        return {
            'timestamp': datetime.now().isoformat(),
            'integration_active': self.state['integration_active'],
            'integration_count': self.state['integration_count'],
            'integrated_health': integrated_health,
            'unified_health_score': unified_health,
            'cockpit': cockpit_status,
            'monitoring': monitoring_status,
        }

    def get_dashboard_data(self) -> Dict[str, Any]:
        """获取驾驶舱统一监控仪表盘数据"""
        integrated_status = self.get_integrated_status()

        # 获取更详细的监控数据
        monitoring_data = {}
        if self.monitoring:
            try:
                monitoring_data = {
                    'unified_status': self.monitoring.get_unified_status(),
                    'visualization': self.monitoring.get_visualization_data(),
                    'warnings': self.monitoring.get_warning_history(10),
                }
            except Exception as e:
                monitoring_data = {'error': str(e)}

        # 获取驾驶舱数据
        cockpit_data = {}
        if self.cockpit:
            try:
                cockpit_data = self.cockpit.get_dashboard_data()
            except Exception as e:
                cockpit_data = {'error': str(e)}

        return {
            'timestamp': datetime.now().isoformat(),
            'version': self.VERSION,
            'integrated': integrated_status,
            'monitoring': monitoring_data,
            'cockpit': cockpit_data,
            'unified_dashboard': {
                'health_score': integrated_status.get('unified_health_score', 0),
                'integration_health': integrated_status.get('integrated_health', 0),
                'cockpit_running': integrated_status.get('cockpit', {}).get('running', False),
                'monitoring_active': integrated_status.get('monitoring', {}).get('monitoring_active', False),
                'warnings_count': len(monitoring_data.get('warnings', [])),
            }
        }

    def run_integration_cycle(self) -> Dict[str, Any]:
        """运行集成循环"""
        print(f"\n[{self.name}] 开始执行集成循环...")

        # 获取集成状态
        status = self.get_integrated_status()
        print(f"[1/3] 集成状态: 健康度 {status.get('integrated_health')}%")

        # 获取统一监控状态
        monitoring_status = status.get('monitoring', {})
        unified_score = monitoring_status.get('unified_health_score', 0)
        print(f"[2/3] 统一健康分数: {unified_score}")

        # 获取驾驶舱状态
        cockpit_status = status.get('cockpit', {})
        print(f"[3/3] 驾驶舱运行: {'是' if cockpit_status.get('running') else '否'}")

        # 更新状态
        self.state['integration_active'] = True
        self.state['last_integration_timestamp'] = datetime.now().isoformat()
        self.state['integration_count'] += 1
        self.state['last_unified_health_score'] = unified_score

        summary = {
            'timestamp': datetime.now().isoformat(),
            'integration_count': self.state['integration_count'],
            'integrated_health': status.get('integrated_health', 0),
            'unified_health_score': unified_score,
            'cockpit_running': cockpit_status.get('running', False),
            'monitoring_active': monitoring_status.get('monitoring_active', False),
            'conclusion': '集成循环完成'
        }

        print(f"\n[{self.name}] 集成循环执行完成")
        print(f"  集成健康度: {status.get('integrated_health')}%")
        print(f"  统一健康分数: {unified_score}")
        print(f"  驾驶舱运行: {'是' if cockpit_status.get('running') else '否'}")

        return summary

    def status(self) -> str:
        """获取状态摘要"""
        status = self.get_integrated_status()

        lines = [
            f"=== 进化驾驶舱统一监控集成状态 (v{self.VERSION}) ===",
            f"集成状态: {'活跃' if status.get('integration_active') else '未激活'}",
            f"集成次数: {status.get('integration_count', 0)}",
            f"集成健康度: {status.get('integrated_health', 0)}%",
            f"统一健康分数: {status.get('unified_health_score', 0)}",
            f"",
            f"--- 组件状态 ---",
            f"驾驶舱: {'已加载' if status.get('cockpit', {}).get('loaded') else '未加载'}",
            f"融合监控: {'已加载' if status.get('monitoring', {}).get('loaded') else '未加载'}",
        ]

        cockpit = status.get('cockpit', {})
        if cockpit.get('loaded'):
            lines.append(f"驾驶舱运行: {'是' if cockpit.get('running') else '否'}")
            lines.append(f"自动模式: {'启用' if cockpit.get('auto_mode') else '禁用'}")
            lines.append(f"当前轮次: {cockpit.get('current_round')}")

        monitoring = status.get('monitoring', {})
        if monitoring.get('loaded'):
            lines.append(f"监控激活: {'是' if monitoring.get('monitoring_active') else '否'}")
            lines.append(f"预警数量: {monitoring.get('warnings_count', 0)}")

        return "\n".join(lines)


def get_integration_engine() -> EvolutionCockpitUnifiedMonitoringIntegrationEngine:
    """获取集成引擎实例"""
    return EvolutionCockpitUnifiedMonitoringIntegrationEngine()


def main():
    """主函数"""
    engine = get_integration_engine()

    # 解析命令
    if len(sys.argv) < 2:
        cmd = "status"
    else:
        cmd = sys.argv[1]

    if cmd == "status":
        print(engine.status())
    elif cmd == "integrated_status":
        status = engine.get_integrated_status()
        print(json.dumps(status, indent=2, ensure_ascii=False))
    elif cmd == "dashboard":
        data = engine.get_dashboard_data()
        print(json.dumps(data, indent=2, ensure_ascii=False))
    elif cmd == "run_cycle":
        result = engine.run_integration_cycle()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif cmd in ["help", "-h", "--help"]:
        print(f"""
智能全场景进化环统一监控数据与进化驾驶舱深度集成引擎 (v{engine.VERSION})

用法:
  python evolution_cockpit_unified_monitoring_integration_engine.py <命令>

命令:
  status          - 显示集成状态
  integrated_status - 显示集成详细状态
  dashboard       - 显示驾驶舱统一监控仪表盘
  run_cycle       - 运行集成循环
  help            - 显示帮助

示例:
  python evolution_cockpit_unified_monitoring_integration_engine.py status
  python evolution_cockpit_unified_monitoring_integration_engine.py dashboard
        """)
    else:
        print(f"未知命令: {cmd}")
        print("使用 'help' 查看可用命令")
        sys.exit(1)


if __name__ == "__main__":
    main()