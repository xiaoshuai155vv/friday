#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环预警驱动策略调整与进化驾驶舱深度集成引擎
Evolution Warning Cockpit Integration Engine

在 round 466 完成的预警驱动自动策略调整引擎基础上：
1. 将预警驱动策略调整能力与进化驾驶舱深度集成
2. 实现可视化预警与策略调整过程
3. 实现预警数据实时推送到驾驶舱
4. 实现策略调整过程可视化展示

功能：
1. 预警数据实时推送到驾驶舱
2. 策略调整过程可视化
3. 调整效果对比展示
4. 预警趋势分析展示
5. 实时数据动态刷新

Version: 1.0.0

依赖：
- evolution_warning_driven_strategy_adjustment_engine.py (round 466)
- evolution_cockpit_engine.py (round 350)

作者：AI Evolution System
日期：2026-03-15
"""

import os
import sys
import json
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict

# 添加项目根目录到 Python 路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, SCRIPT_DIR)


def _safe_print(text: str):
    """安全打印，处理编码问题"""
    import re
    try:
        print(text)
    except UnicodeEncodeError:
        clean_text = re.sub(r'[^\x00-\x7F]+', '', text)
        print(clean_text)


class WarningCockpitIntegrationEngine:
    """预警驱动策略调整与进化驾驶舱深度集成引擎 v1.0.0"""

    def __init__(self, state_dir: str = "runtime/state"):
        self.version = "1.0.0"
        self.state_dir = Path(state_dir)
        self.project_root = PROJECT_ROOT
        self.scripts_dir = SCRIPT_DIR
        self.runtime_dir = Path(self.project_root) / "runtime"
        self.logs_dir = Path(self.project_root) / "runtime" / "logs"

        # 状态文件
        self.state_file = self.state_dir / "warning_cockpit_integration_state.json"
        self.history_file = self.state_dir / "warning_cockpit_integration_history.json"
        self.dashboard_file = self.state_dir / "warning_cockpit_dashboard_data.json"

        # 初始化目录
        self._ensure_directories()

        # 状态
        self.state = self._load_state()

        # 引擎实例
        self.warning_strategy_engine = None
        self.cockpit_engine = None
        self._initialize_engines()

        # 实时推送配置
        self.realtime_push_enabled = True
        self.push_interval = 5  # 秒
        self.push_thread = None
        self.stop_push = False

    def _ensure_directories(self):
        """确保必要的目录存在"""
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)

    def _initialize_engines(self):
        """初始化集成的引擎"""
        # 尝试导入预警驱动策略调整引擎
        try:
            sys.path.insert(0, self.scripts_dir)
            from evolution_warning_driven_strategy_adjustment_engine import WarningDrivenStrategyAdjustmentEngine
            self.warning_strategy_engine = WarningDrivenStrategyAdjustmentEngine(str(self.project_root))
            _safe_print("[预警驾驶舱集成] 预警驱动策略调整引擎已加载")
        except ImportError as e:
            _safe_print(f"[预警驾驶舱集成] 无法加载预警驱动策略调整引擎: {e}")
            self.warning_strategy_engine = None

        # 尝试导入进化驾驶舱引擎
        try:
            from evolution_cockpit_engine import EvolutionCockpitEngine
            self.cockpit_engine = EvolutionCockpitEngine()
            _safe_print("[预警驾驶舱集成] 进化驾驶舱引擎已加载")
        except ImportError as e:
            _safe_print(f"[预警驾驶舱集成] 无法加载进化驾驶舱引擎: {e}")
            self.cockpit_engine = None

    def _load_state(self) -> Dict[str, Any]:
        """加载状态"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                _safe_print(f"[预警驾驶舱集成] 状态加载失败: {e}")

        # 默认状态
        default_state = {
            "version": self.version,
            "initialized_at": datetime.now().isoformat(),
            "last_update": datetime.now().isoformat(),
            "integrated_engines": {
                "warning_strategy": False,
                "cockpit": False
            },
            "dashboard_data": {
                "realtime_warnings": [],
                "adjustment_process": [],
                "adjustment_comparison": {},
                "warning_trends": [],
                "health_metrics": {}
            },
            "realtime_push_enabled": True,
            "push_stats": {
                "total_pushes": 0,
                "last_push_time": None
            }
        }
        self._save_state(default_state)
        return default_state

    def _save_state(self, state: Dict[str, Any]):
        """保存状态"""
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            _safe_print(f"[预警驾驶舱集成] 状态保存失败: {e}")

    def get_status(self) -> Dict[str, Any]:
        """获取引擎状态"""
        warning_engine_status = {}
        if self.warning_strategy_engine:
            try:
                warning_engine_status = self.warning_strategy_engine.get_status()
            except Exception as e:
                warning_engine_status = {"error": str(e)}

        return {
            "version": self.version,
            "integrated_engines": {
                "warning_strategy": self.warning_strategy_engine is not None,
                "cockpit": self.cockpit_engine is not None
            },
            "warning_engine_status": warning_engine_status,
            "realtime_push_enabled": self.realtime_push_enabled,
            "realtime_push_active": self.push_thread is not None and self.push_thread.is_alive(),
            "dashboard_file_exists": self.dashboard_file.exists()
        }

    def get_dashboard_data(self) -> Dict[str, Any]:
        """获取驾驶舱展示数据"""
        dashboard_data = {
            "timestamp": datetime.now().isoformat(),
            "engine_status": self.get_status(),
            "realtime_warnings": [],
            "adjustment_process": [],
            "adjustment_comparison": {},
            "warning_trends": [],
            "health_metrics": {}
        }

        # 获取预警驱动策略调整引擎的数据
        if self.warning_strategy_engine:
            try:
                # 获取预警汇总
                warning_summary = self.warning_strategy_engine.get_warning_summary()
                dashboard_data["realtime_warnings"] = warning_summary.get("recent", [])

                # 获取调整汇总
                adjustment_summary = self.warning_strategy_engine.get_adjustment_summary()
                dashboard_data["adjustment_process"] = adjustment_summary.get("recent", [])

                # 获取驾驶舱数据
                cockpit_data = self.warning_strategy_engine.get_cockpit_data()
                dashboard_data["health_metrics"] = {
                    "warnings_total": warning_summary.get("total", 0),
                    "adjustments_total": adjustment_summary.get("total", 0),
                    "adjustment_success_rate": adjustment_summary.get("success_rate", 0),
                    "by_warning_level": warning_summary.get("by_level", {}),
                    "by_adjustment_type": adjustment_summary.get("by_type", {})
                }

                # 计算预警趋势（基于最近的数据）
                if warning_summary.get("total", 0) > 0:
                    dashboard_data["warning_trends"] = self._calculate_warning_trends(
                        warning_summary.get("recent", [])
                    )

                # 生成调整前后对比
                if adjustment_summary.get("recent"):
                    dashboard_data["adjustment_comparison"] = self._generate_adjustment_comparison(
                        adjustment_summary.get("recent", [])
                    )

            except Exception as e:
                _safe_print(f"[预警驾驶舱集成] 获取驾驶舱数据失败: {e}")
                dashboard_data["error"] = str(e)

        # 保存到 dashboard 文件
        self._save_dashboard_data(dashboard_data)

        return dashboard_data

    def _calculate_warning_trends(self, recent_warnings: List[Dict]) -> List[Dict]:
        """计算预警趋势"""
        trends = []
        if not recent_warnings:
            return trends

        # 按级别统计
        level_counts = defaultdict(int)
        for w in recent_warnings:
            level = w.get("level", "unknown")
            level_counts[level] += 1

        for level, count in level_counts.items():
            trends.append({
                "level": level,
                "count": count,
                "percentage": count / len(recent_warnings) * 100
            })

        return sorted(trends, key=lambda x: x["count"], reverse=True)

    def _generate_adjustment_comparison(self, recent_adjustments: List[Dict]) -> Dict[str, Any]:
        """生成调整前后对比"""
        if not recent_adjustments:
            return {}

        # 获取最新的调整记录
        latest = recent_adjustments[-1]
        changes = latest.get("changes", {})

        comparison = {
            "latest_adjustment": {
                "type": latest.get("adjustment_type", "unknown"),
                "timestamp": latest.get("timestamp", ""),
                "success": latest.get("success", False),
                "changes_count": len(changes)
            },
            "change_details": []
        }

        for param, change in changes.items():
            comparison["change_details"].append({
                "parameter": param,
                "old_value": change.get("old", "N/A"),
                "new_value": change.get("new", "N/A")
            })

        return comparison

    def _save_dashboard_data(self, data: Dict[str, Any]):
        """保存驾驶舱数据到文件"""
        try:
            self.dashboard_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.dashboard_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            _safe_print(f"[预警驾驶舱集成] 保存驾驶舱数据失败: {e}")

    def enable_realtime_push(self):
        """启用实时推送"""
        self.realtime_push_enabled = True
        self.state["realtime_push_enabled"] = True
        self._save_state(self.state)
        return {"success": True, "message": "实时推送已启用"}

    def disable_realtime_push(self):
        """禁用实时推送"""
        self.realtime_push_enabled = False
        self.state["realtime_push_enabled"] = False
        self._save_state(self.state)
        return {"success": True, "message": "实时推送已禁用"}

    def start_realtime_push(self):
        """启动实时推送"""
        if self.push_thread and self.push_thread.is_alive():
            return {"success": False, "message": "实时推送已在运行中"}

        self.stop_push = False
        self.push_thread = threading.Thread(target=self._realtime_push_loop, daemon=True)
        self.push_thread.start()
        return {"success": True, "message": "实时推送已启动"}

    def stop_realtime_push(self):
        """停止实时推送"""
        self.stop_push = True
        if self.push_thread:
            self.push_thread.join(timeout=2)
        return {"success": True, "message": "实时推送已停止"}

    def _realtime_push_loop(self):
        """实时推送循环"""
        while not self.stop_push and self.realtime_push_enabled:
            try:
                # 获取最新数据并保存
                dashboard_data = self.get_dashboard_data()

                # 更新推送统计
                self.state["push_stats"]["total_pushes"] += 1
                self.state["push_stats"]["last_push_time"] = datetime.now().isoformat()
                self._save_state(self.state)

            except Exception as e:
                _safe_print(f"[预警驾驶舱集成] 实时推送循环错误: {e}")

            time.sleep(self.push_interval)

    def test_integration(self) -> Dict[str, Any]:
        """测试集成功能"""
        result = {
            "success": False,
            "tests": {}
        }

        # 测试1：获取状态
        try:
            status = self.get_status()
            result["tests"]["get_status"] = "pass"
            result["tests"]["status_detail"] = status
        except Exception as e:
            result["tests"]["get_status"] = f"fail: {e}"

        # 测试2：获取驾驶舱数据
        try:
            dashboard = self.get_dashboard_data()
            result["tests"]["get_dashboard_data"] = "pass"
            result["tests"]["dashboard_keys"] = list(dashboard.keys())
        except Exception as e:
            result["tests"]["get_dashboard_data"] = f"fail: {e}"

        # 测试3：生成测试预警
        if self.warning_strategy_engine:
            try:
                test_result = self.warning_strategy_engine.test_warning_trigger()
                result["tests"]["test_warning_trigger"] = "pass" if test_result.get("success") else "fail"
            except Exception as e:
                result["tests"]["test_warning_trigger"] = f"fail: {e}"

        # 判断整体成功
        result["success"] = all(
            "fail" not in str(v).lower() for v in result["tests"].values()
            if isinstance(v, str)
        )

        return result


# 命令行接口
def main():
    import argparse
    parser = argparse.ArgumentParser(
        description='预警驱动策略调整与进化驾驶舱深度集成引擎'
    )
    parser.add_argument(
        'command', nargs='?', default='status',
        choices=['status', 'dashboard', 'enable-push', 'disable-push', 'start-push', 'stop-push', 'test'],
        help='要执行的命令'
    )
    parser.add_argument('--json', action='store_true', help='输出 JSON 格式')

    args = parser.parse_args()

    engine = WarningCockpitIntegrationEngine()

    if args.command == 'status':
        result = engine.get_status()
    elif args.command == 'dashboard':
        result = engine.get_dashboard_data()
    elif args.command == 'enable-push':
        result = engine.enable_realtime_push()
    elif args.command == 'disable-push':
        result = engine.disable_realtime_push()
    elif args.command == 'start-push':
        result = engine.start_realtime_push()
    elif args.command == 'stop-push':
        result = engine.stop_realtime_push()
    elif args.command == 'test':
        result = engine.test_integration()
    else:
        result = {'error': f'未知命令: {args.command}'}

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        if args.command == 'status':
            print(f"=== 预警驾驶舱集成引擎 v{result['version']} ===")
            print(f"集成引擎状态:")
            print(f"  - 预警驱动策略调整: {'已加载' if result['integrated_engines']['warning_strategy'] else '未加载'}")
            print(f"  - 进化驾驶舱: {'已加载' if result['integrated_engines']['cockpit'] else '未加载'}")
            print(f"实时推送: {'启用' if result['realtime_push_enabled'] else '禁用'}")
            print(f"推送线程: {'运行中' if result.get('realtime_push_active') else '未运行'}")
            print(f"驾驶舱数据文件: {'存在' if result.get('dashboard_file_exists') else '不存在'}")
        elif args.command == 'dashboard':
            print("=== 驾驶舱数据 ===")
            print(f"时间戳: {result.get('timestamp', 'N/A')}")
            print(f"实时预警数: {len(result.get('realtime_warnings', []))}")
            print(f"调整记录数: {len(result.get('adjustment_process', []))}")
            print(f"健康指标: {result.get('health_metrics', {})}")
            print(f"预警趋势: {result.get('warning_trends', [])}")
        else:
            if 'success' in result:
                print(f"结果: {result.get('message', '执行成功' if result['success'] else '执行失败')}")
            elif 'error' in result:
                print(f"错误: {result['error']}")
            else:
                print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()