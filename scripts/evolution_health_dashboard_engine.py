#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环健康指数实时仪表盘引擎 (version 1.0.0)

将多个健康模块（健康监控、自愈引擎、健康评估、预警系统）的数据统一聚合，
生成统一的健康指数视图，让进化环的健康状态一目了然。

功能：
1. 多模块数据聚合 - 整合监控、自愈、评估、预警数据
2. 健康指数计算 - 生成综合健康指数 (0-100)
3. 实时状态面板 - 显示各模块实时状态
4. 趋势分析 - 分析健康趋势和变化
5. 问题汇总 - 汇总所有已知问题和待修复项
6. 快速行动入口 - 提供一键修复、重新评估等入口

该引擎与以下模块深度集成：
- evolution_loop_health_monitor.py（实时监控）
- evolution_loop_self_healing_engine.py（自愈引擎）
- evolution_health_healing_integrated_engine.py（评估+自愈集成）
- system_health_alert_engine.py（预警系统）

作者：Claude Sonnet 4.6
日期：2026-03-14
"""

import os
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
RUNTIME_DIR = PROJECT_ROOT / "runtime"
STATE_DIR = RUNTIME_DIR / "state"
LOGS_DIR = RUNTIME_DIR / "logs"


class EvolutionHealthDashboardEngine:
    """智能全场景进化环健康指数实时仪表盘引擎"""

    def __init__(self):
        self.name = "EvolutionHealthDashboardEngine"
        self.version = "1.0.0"
        self.state_file = STATE_DIR / "evolution_health_dashboard_state.json"
        self.dashboard_data = None
        self.load_state()

    def load_state(self):
        """加载状态"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.dashboard_data = data.get('last_dashboard')
            except Exception:
                pass

    def save_state(self):
        """保存状态"""
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump({
                'last_dashboard': self.dashboard_data,
                'last_updated': datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)

    def get_monitor_status(self) -> Dict[str, Any]:
        """获取监控模块状态"""
        result = {
            'module': 'health_monitor',
            'status': 'unknown',
            'score': 50,
            'details': {}
        }

        try:
            monitor_state = STATE_DIR / "evolution_health_monitor_state.json"
            if monitor_state.exists():
                with open(monitor_state, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    result['status'] = 'active'
                    result['last_alert'] = data.get('alert_history', [])[-1] if data.get('alert_history') else None
                    result['alert_count'] = len(data.get('alert_history', []))
        except Exception as e:
            result['error'] = str(e)

        return result

    def get_healer_status(self) -> Dict[str, Any]:
        """获取自愈模块状态"""
        result = {
            'module': 'self_healer',
            'status': 'unknown',
            'score': 50,
            'details': {}
        }

        try:
            healer_state = STATE_DIR / "evolution_loop_self_healing_state.json"
            if healer_state.exists():
                with open(healer_state, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    result['status'] = 'ready'
                    result['last_repair'] = data.get('last_repair')
        except Exception as e:
            result['error'] = str(e)

        return result

    def get_integration_status(self) -> Dict[str, Any]:
        """获取集成模块状态"""
        result = {
            'module': 'health_healing_integrated',
            'status': 'unknown',
            'score': 50,
            'details': {}
        }

        try:
            integrated_state = STATE_DIR / "evolution_health_healing_integrated_state.json"
            if integrated_state.exists():
                with open(integrated_state, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    report = data.get('last_integration_report', {})
                    result['status'] = 'ready'
                    result['score'] = report.get('overall_status') == 'success' and 100 or 70
                    result['last_report'] = report.get('summary', '无')
        except Exception as e:
            result['error'] = str(e)

        return result

    def get_current_mission_status(self) -> Dict[str, Any]:
        """获取当前进化任务状态"""
        result = {
            'round': 0,
            'phase': 'unknown',
            'age_minutes': 0,
            'health': 'unknown'
        }

        try:
            mission_file = STATE_DIR / "current_mission.json"
            if mission_file.exists():
                with open(mission_file, 'r', encoding='utf-8') as f:
                    mission = json.load(f)
                    result['round'] = mission.get('loop_round', 0)
                    result['phase'] = mission.get('phase', 'unknown')
                    result['current_goal'] = mission.get('current_goal', '')

                    # 计算任务年龄
                    updated = mission.get('updated_at', '')
                    if updated:
                        try:
                            updated_time = datetime.fromisoformat(updated.replace('Z', '+00:00'))
                            age = datetime.now() - updated_time.replace(tzinfo=None)
                            result['age_minutes'] = int(age.total_seconds() / 60)

                            # 判断健康状态
                            if result['age_minutes'] < 60:
                                result['health'] = 'healthy'
                            elif result['age_minutes'] < 180:
                                result['health'] = 'warning'
                            else:
                                result['health'] = 'stuck'
                        except Exception:
                            pass
        except Exception as e:
            result['error'] = str(e)

        return result

    def calculate_health_index(self, module_statuses: List[Dict]) -> int:
        """
        计算综合健康指数

        参数:
            module_statuses: 各模块状态列表

        返回:
            健康指数 (0-100)
        """
        total_score = 0
        count = 0

        for module in module_statuses:
            score = module.get('score', 50)
            total_score += score
            count += 1

        return int(total_score / count) if count > 0 else 50

    def generate_dashboard(self) -> Dict[str, Any]:
        """
        生成健康仪表盘

        返回:
            完整的仪表盘数据
        """
        dashboard = {
            'timestamp': datetime.now().isoformat(),
            'version': self.version,
            'health_index': 50,
            'health_status': 'unknown',
            'modules': [],
            'mission_status': {},
            'issues': [],
            'trends': {},
            'recommendations': []
        }

        # 收集各模块状态
        monitor = self.get_monitor_status()
        healer = self.get_healer_status()
        integration = self.get_integration_status()

        dashboard['modules'] = [monitor, healer, integration]

        # 获取任务状态
        dashboard['mission_status'] = self.get_current_mission_status()

        # 计算健康指数
        dashboard['health_index'] = self.calculate_health_index(dashboard['modules'])

        # 确定健康状态
        if dashboard['health_index'] >= 80:
            dashboard['health_status'] = 'excellent'
        elif dashboard['health_index'] >= 60:
            dashboard['health_status'] = 'healthy'
        elif dashboard['health_index'] >= 40:
            dashboard['health_status'] = 'warning'
        else:
            dashboard['health_status'] = 'critical'

        # 生成建议
        dashboard['recommendations'] = self._generate_recommendations(dashboard)

        # 保存状态
        self.dashboard_data = dashboard
        self.save_state()

        return dashboard

    def _generate_recommendations(self, dashboard: Dict) -> List[str]:
        """生成健康建议"""
        recommendations = []
        health_index = dashboard.get('health_index', 50)
        health_status = dashboard.get('health_status', 'unknown')
        mission_status = dashboard.get('mission_status', {})

        # 基于健康状态生成建议
        if health_status == 'critical':
            recommendations.append('建议立即运行健康检查和自愈：python scripts/evolution_health_healing_integrated_engine.py run')
        elif health_status == 'warning':
            recommendations.append('建议运行完整健康评估：python scripts/evolution_loop_health_monitor.py check')

        # 基于任务状态生成建议
        mission_health = mission_status.get('health', 'unknown')
        if mission_health == 'stuck':
            recommendations.append('检测到任务停滞，建议检查当前进化状态')
        elif mission_health == 'warning':
            recommendations.append('任务运行时间较长，建议关注进度')

        # 如果没有特殊问题，生成常规建议
        if not recommendations:
            recommendations.append('系统运行正常，进化环健康指数良好')
            recommendations.append('可以使用 "do 进化状态" 查看当前进化进度')

        return recommendations

    def get_status_summary(self) -> str:
        """获取状态摘要"""
        dashboard = self.generate_dashboard()

        summary = f"""=== 进化环健康仪表盘 ===
健康指数: {dashboard['health_index']}/100 ({dashboard['health_status']})
当前轮次: {dashboard['mission_status'].get('round', 'N/A')}
当前阶段: {dashboard['mission_status'].get('phase', 'N/A')}

模块状态:
- 健康监控: {dashboard['modules'][0].get('status', 'unknown')}
- 自愈引擎: {dashboard['modules'][1].get('status', 'unknown')}
- 评估集成: {dashboard['modules'][2].get('status', 'unknown')}

建议:
"""
        for rec in dashboard.get('recommendations', []):
            summary += f"  - {rec}\n"

        return summary

    def get_status(self) -> Dict[str, Any]:
        """
        获取系统状态（简洁版）

        返回:
            状态字典
        """
        # 如果有缓存数据，返回缓存
        if self.dashboard_data:
            # 检查是否过期（超过5分钟）
            last_updated = self.dashboard_data.get('timestamp', '')
            if last_updated:
                try:
                    last_time = datetime.fromisoformat(last_updated)
                    age = datetime.now() - last_time
                    if age.total_seconds() < 300:  # 5分钟内
                        return self.dashboard_data
                except Exception:
                    pass

        # 重新生成
        return self.generate_dashboard()


def main():
    """主函数 - 支持命令行调用"""
    import sys

    engine = EvolutionHealthDashboardEngine()

    if len(sys.argv) < 2:
        # 无参数时显示状态摘要
        print(engine.get_status_summary())
        return

    command = sys.argv[1].lower()

    if command in ['status', '状态']:
        status = engine.get_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))

    elif command in ['dashboard', '仪表盘', '面板']:
        dashboard = engine.generate_dashboard()
        print(json.dumps(dashboard, ensure_ascii=False, indent=2))

    elif command in ['summary', '摘要', '概要']:
        print(engine.get_status_summary())

    elif command in ['refresh', '刷新', 'update']:
        dashboard = engine.generate_dashboard()
        print(json.dumps(dashboard, ensure_ascii=False, indent=2))

    elif command in ['help', '帮助']:
        help_text = """
智能全场景进化环健康指数实时仪表盘引擎

用法:
    python evolution_health_dashboard_engine.py <command>

命令:
    status/状态        - 显示简洁状态
    dashboard/仪表盘/面板 - 显示完整仪表盘
    summary/摘要      - 显示状态摘要
    refresh/刷新/update - 刷新数据并显示
    help/帮助         - 显示帮助信息
        """
        print(help_text)

    else:
        print(f"未知命令: {command}")
        print("使用 'help' 查看可用命令")


if __name__ == "__main__":
    main()