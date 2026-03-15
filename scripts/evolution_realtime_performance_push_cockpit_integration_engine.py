#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环效能实时数据推送与驾驶舱智能预警深度集成引擎
(Realtime Performance Push & Cockpit Smart Warning Integration Engine)

在 round 481 完成的自我进化效能深度分析与自适应优化引擎基础上，
进一步增强效能分析的实时数据推送能力，将效能分析结果与进化驾驶舱深度集成，
实现自动刷新和智能预警功能。

让系统能够实时推送效能数据到驾驶舱、实现数据自动刷新、
基于阈值的智能预警、预警阈值动态调整，形成完整的
「实时数据推送 → 自动刷新 → 智能预警 → 自动干预」的闭环。

Version: 1.0.0
"""

import json
import os
import sys
import time
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from collections import deque
import statistics

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
STATE_DIR = PROJECT_ROOT / "runtime" / "state"
DATA_DIR = PROJECT_ROOT / "runtime" / "data"
LOGS_DIR = PROJECT_ROOT / "runtime" / "logs"

# 添加 scripts 目录到路径以便导入
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

# 尝试导入效能分析引擎
try:
    from evolution_self_evolution_effectiveness_analysis_engine import (
        SelfEvolutionEffectivenessAnalysisEngine
    )
    EFFECTIVENESS_ENGINE_AVAILABLE = True
except ImportError:
    EFFECTIVENESS_ENGINE_AVAILABLE = False


class RealtimePerformancePushCockpitIntegrationEngine:
    """效能实时数据推送与驾驶舱智能预警深度集成引擎核心类"""

    def __init__(self):
        self.version = "1.0.0"
        self.name = "Realtime Performance Push & Cockpit Integration Engine"
        self.runtime_dir = PROJECT_ROOT / "runtime"
        self.state_dir = self.runtime_dir / "state"
        self.data_dir = self.runtime_dir / "data"

        # 数据文件路径
        self.config_file = self.data_dir / "realtime_performance_push_config.json"
        self.realtime_data_file = self.data_dir / "realtime_performance_data.json"
        self.warning_history_file = self.data_dir / "warning_history.json"
        self.auto_refresh_state_file = self.data_dir / "auto_refresh_state.json"

        # 实时数据缓存
        self._realtime_cache = {}
        self._cache_last_update = None
        self._push_callbacks = []

        # 预警状态
        self._active_warnings = []
        self._warning_history = deque(maxlen=100)  # 保留最近100条预警

        # 自动刷新线程
        self._auto_refresh_thread = None
        self._auto_refresh_running = False
        self._refresh_interval = 300  # 默认5分钟刷新一次

        # 效能分析引擎实例
        self._effectiveness_engine = None
        if EFFECTIVENESS_ENGINE_AVAILABLE:
            self._effectiveness_engine = SelfEvolutionEffectivenessAnalysisEngine()

        self._ensure_directories()
        self._initialize_data()

    def _ensure_directories(self):
        """确保必要的目录存在"""
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def _initialize_data(self):
        """初始化数据文件"""
        if not self.config_file.exists():
            default_config = {
                "push_enabled": True,
                "auto_refresh": {
                    "enabled": True,
                    "interval_seconds": 300,  # 5分钟
                    "real_time_mode": False  # True 为实时模式（需要额外依赖）
                },
                "warning": {
                    "enabled": True,
                    "thresholds": {
                        "success_rate_warning": 0.7,
                        "success_rate_critical": 0.5,
                        "baseline_pass_rate_warning": 0.8,
                        "baseline_pass_rate_critical": 0.6,
                        "execution_time_warning": 180,  # 秒
                        "execution_time_critical": 300,
                        "consecutive_failures_warning": 3,
                        "consecutive_failures_critical": 5
                    },
                    "dynamic_adjustment": {
                        "enabled": True,
                        "adjustment_factor": 0.05,  # 每次调整5%
                        "min_samples": 10  # 至少10个样本才调整
                    },
                    "notification": {
                        "console": True,
                        "log_file": True,
                        "state_file": True
                    }
                },
                "cockpit_integration": {
                    "enable_auto_refresh": True,
                    "data_refresh_endpoint": "/api/performance/realtime",
                    "warning_endpoint": "/api/performance/warnings",
                    "push_mode": "polling"  # polling 或 websocket（需要额外依赖）
                }
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, ensure_ascii=False, indent=2)

        if not self.realtime_data_file.exists():
            with open(self.realtime_data_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "last_update": None,
                    "data": {},
                    "refresh_count": 0
                }, f, ensure_ascii=False, indent=2)

        if not self.warning_history_file.exists():
            with open(self.warning_history_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "warnings": [],
                    "total_count": 0
                }, f, ensure_ascii=False, indent=2)

        if not self.auto_refresh_state_file.exists():
            with open(self.auto_refresh_state_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "running": False,
                    "last_refresh": None,
                    "next_refresh": None,
                    "refresh_count": 0
                }, f, ensure_ascii=False, indent=2)

    def _load_config(self) -> Dict:
        """加载配置"""
        with open(self.config_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def collect_realtime_data(self) -> Dict[str, Any]:
        """收集实时效能数据"""
        print("[效能实时推送] 收集实时效能数据...")

        realtime_data = {
            "collection_time": datetime.now().isoformat(),
            "effectiveness_data": None,
            "warnings": [],
            "metrics": {}
        }

        # 收集效能分析数据
        if self._effectiveness_engine:
            try:
                effectiveness = self._effectiveness_engine.collect_effectiveness_data()
                realtime_data["effectiveness_data"] = effectiveness.get("summary", {})

                # 提取关键指标
                summary = effectiveness.get("summary", {})
                realtime_data["metrics"] = {
                    "total_rounds": summary.get("total_rounds", 0),
                    "completed_rounds": summary.get("completed_rounds", 0),
                    "success_rate": summary.get("success_rate", 0),
                    "baseline_pass_rate": summary.get("baseline_pass_rate", 0),
                    "targeted_pass_rate": summary.get("targeted_pass_rate", 0)
                }
            except Exception as e:
                print(f"  警告：收集效能数据失败: {e}")
                realtime_data["error"] = str(e)

        # 执行智能预警检查
        warnings = self.check_warnings(realtime_data.get("metrics", {}))
        realtime_data["warnings"] = warnings

        # 更新缓存
        self._realtime_cache = realtime_data
        self._cache_last_update = datetime.now()

        # 保存到文件
        with open(self.realtime_data_file, 'w', encoding='utf-8') as f:
            json.dump({
                "last_update": realtime_data["collection_time"],
                "data": realtime_data,
                "refresh_count": self._get_refresh_count() + 1
            }, f, ensure_ascii=False, indent=2)

        print(f"[效能实时推送] 数据收集完成 - 刷新次数: {self._get_refresh_count() + 1}")
        if warnings:
            print(f"  发现 {len(warnings)} 个预警")

        return realtime_data

    def _get_refresh_count(self) -> int:
        """获取刷新次数"""
        try:
            with open(self.realtime_data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("refresh_count", 0)
        except:
            return 0

    def check_warnings(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """智能预警检查"""
        config = self._load_config()
        warning_config = config.get("warning", {})
        thresholds = warning_config.get("thresholds", {})

        warnings = []

        # 检查成功率
        success_rate = metrics.get("success_rate", 1.0)
        if success_rate < thresholds.get("success_rate_critical", 0.5):
            warnings.append({
                "type": "success_rate",
                "severity": "critical",
                "message": f"进化成功率严重偏低: {success_rate:.1%}",
                "value": success_rate,
                "threshold": thresholds.get("success_rate_critical", 0.5),
                "timestamp": datetime.now().isoformat(),
                "action_required": True
            })
        elif success_rate < thresholds.get("success_rate_warning", 0.7):
            warnings.append({
                "type": "success_rate",
                "severity": "warning",
                "message": f"进化成功率偏低: {success_rate:.1%}",
                "value": success_rate,
                "threshold": thresholds.get("success_rate_warning", 0.7),
                "timestamp": datetime.now().isoformat(),
                "action_required": True
            })

        # 检查基线通过率
        baseline_pass_rate = metrics.get("baseline_pass_rate", 1.0)
        if baseline_pass_rate < thresholds.get("baseline_pass_rate_critical", 0.6):
            warnings.append({
                "type": "baseline_pass_rate",
                "severity": "critical",
                "message": f"基线通过率严重偏低: {baseline_pass_rate:.1%}",
                "value": baseline_pass_rate,
                "threshold": thresholds.get("baseline_pass_rate_critical", 0.6),
                "timestamp": datetime.now().isoformat(),
                "action_required": True
            })
        elif baseline_pass_rate < thresholds.get("baseline_pass_rate_warning", 0.8):
            warnings.append({
                "type": "baseline_pass_rate",
                "severity": "warning",
                "message": f"基线通过率偏低: {baseline_pass_rate:.1%}",
                "value": baseline_pass_rate,
                "threshold": thresholds.get("baseline_pass_rate_warning", 0.8),
                "timestamp": datetime.now().isoformat(),
                "action_required": True
            })

        # 检查是否有连续失败（需要分析历史数据）
        consecutive_failures = self._check_consecutive_failures()
        if consecutive_failures >= thresholds.get("consecutive_failures_critical", 5):
            warnings.append({
                "type": "consecutive_failures",
                "severity": "critical",
                "message": f"连续 {consecutive_failures} 轮进化失败",
                "value": consecutive_failures,
                "threshold": thresholds.get("consecutive_failures_critical", 5),
                "timestamp": datetime.now().isoformat(),
                "action_required": True
            })
        elif consecutive_failures >= thresholds.get("consecutive_failures_warning", 3):
            warnings.append({
                "type": "consecutive_failures",
                "severity": "warning",
                "message": f"连续 {consecutive_failures} 轮进化未完成",
                "value": consecutive_failures,
                "threshold": thresholds.get("consecutive_failures_warning", 3),
                "timestamp": datetime.now().isoformat(),
                "action_required": True
            })

        # 保存预警历史
        if warnings:
            self._save_warning_history(warnings)

        # 更新活动预警
        self._active_warnings = warnings

        return warnings

    def _check_consecutive_failures(self) -> int:
        """检查连续失败次数"""
        try:
            # 读取最近的进化完成状态
            completed_files = sorted(
                self.state_dir.glob("evolution_completed_*.json"),
                key=lambda x: x.name,
                reverse=True
            )[:10]  # 检查最近10轮

            consecutive_failures = 0
            for file in completed_files:
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        status = data.get("status", "").lower()
                        if "未完成" in status or "failed" in status or "incomplete" in status:
                            consecutive_failures += 1
                        else:
                            break  # 遇到成功的就停止
                except:
                    continue

            return consecutive_failures
        except:
            return 0

    def _save_warning_history(self, warnings: List[Dict]):
        """保存预警历史"""
        try:
            with open(self.warning_history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)

            existing_warnings = history.get("warnings", [])
            existing_warnings.extend(warnings)

            # 保留最近100条
            existing_warnings = existing_warnings[-100:]

            history["warnings"] = existing_warnings
            history["total_count"] = len(existing_warnings)

            with open(self.warning_history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"  警告：保存预警历史失败: {e}")

    def adjust_warning_thresholds_dynamically(self) -> Dict[str, Any]:
        """动态调整预警阈值"""
        config = self._load_config()
        dynamic_config = config.get("warning", {}).get("dynamic_adjustment", {})

        if not dynamic_config.get("enabled", False):
            return {"status": "disabled", "message": "动态调整已禁用"}

        print("[效能实时推送] 动态调整预警阈值...")

        adjustment_result = {
            "adjustment_time": datetime.now().isoformat(),
            "adjustments": [],
            "current_thresholds": config.get("warning", {}).get("thresholds", {})
        }

        # 读取预警历史进行分析
        try:
            with open(self.warning_history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)

            warnings = history.get("warnings", [])

            if len(warnings) < dynamic_config.get("min_samples", 10):
                adjustment_result["message"] = f"样本不足 ({len(warnings)}/{dynamic_config.get('min_samples', 10)})，跳过调整"
                return adjustment_result

            # 分析预警模式
            warning_types = {}
            for w in warnings:
                w_type = w.get("type", "unknown")
                if w_type not in warning_types:
                    warning_types[w_type] = []
                warning_types[w_type].append(w)

            # 根据预警频率调整阈值
            adjustment_factor = dynamic_config.get("adjustment_factor", 0.05)
            current_thresholds = config.get("warning", {}).get("thresholds", {})

            for w_type, type_warnings in warning_types.items():
                if len(type_warnings) >= dynamic_config.get("min_samples", 10):
                    # 频繁预警，考虑调整阈值
                    if w_type == "success_rate":
                        current_thresholds["success_rate_warning"] = min(
                            0.95,
                            current_thresholds.get("success_rate_warning", 0.7) + adjustment_factor
                        )
                        current_thresholds["success_rate_critical"] = min(
                            0.85,
                            current_thresholds.get("success_rate_critical", 0.5) + adjustment_factor
                        )
                        adjustment_result["adjustments"].append({
                            "type": w_type,
                            "action": "increased",
                            "factor": adjustment_factor
                        })

            # 保存更新后的配置
            if "warning" not in config:
                config["warning"] = {}
            config["warning"]["thresholds"] = current_thresholds

            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)

            adjustment_result["current_thresholds"] = current_thresholds
            adjustment_result["message"] = f"完成 {len(adjustment_result['adjustments'])} 项调整"

            print(f"[效能实时推送] 阈值调整完成 - {len(adjustment_result['adjustments'])} 项调整")

        except Exception as e:
            adjustment_result["error"] = str(e)
            adjustment_result["message"] = f"调整失败: {e}"

        return adjustment_result

    def start_auto_refresh(self, interval_seconds: Optional[int] = None):
        """启动自动刷新"""
        config = self._load_config()
        refresh_config = config.get("auto_refresh", {})

        if interval_seconds is None:
            interval_seconds = refresh_config.get("interval_seconds", 300)

        self._refresh_interval = interval_seconds

        if self._auto_refresh_running:
            print("[效能实时推送] 自动刷新已在运行中")
            return

        self._auto_refresh_running = True
        self._auto_refresh_thread = threading.Thread(
            target=self._auto_refresh_loop,
            daemon=True
        )
        self._auto_refresh_thread.start()

        # 更新状态文件
        with open(self.auto_refresh_state_file, 'w', encoding='utf-8') as f:
            json.dump({
                "running": True,
                "last_refresh": None,
                "next_refresh": datetime.now().isoformat(),
                "interval_seconds": interval_seconds,
                "refresh_count": 0
            }, f, ensure_ascii=False, indent=2)

        print(f"[效能实时推送] 自动刷新已启动 - 间隔: {interval_seconds}秒")

    def stop_auto_refresh(self):
        """停止自动刷新"""
        self._auto_refresh_running = False

        # 更新状态文件
        with open(self.auto_refresh_state_file, 'w', encoding='utf-8') as f:
            json.dump({
                "running": False,
                "last_refresh": datetime.now().isoformat(),
                "next_refresh": None,
                "refresh_count": self._get_refresh_count()
            }, f, ensure_ascii=False, indent=2)

        print("[效能实时推送] 自动刷新已停止")

    def _auto_refresh_loop(self):
        """自动刷新循环"""
        while self._auto_refresh_running:
            try:
                # 收集实时数据
                self.collect_realtime_data()

                # 检查预警
                if self._active_warnings:
                    print(f"[效能实时推送] 当前有 {len(self._active_warnings)} 个活动预警")

                # 更新状态文件
                with open(self.auto_refresh_state_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        "running": True,
                        "last_refresh": datetime.now().isoformat(),
                        "next_refresh": datetime.now().isoformat(),
                        "interval_seconds": self._refresh_interval,
                        "refresh_count": self._get_refresh_count()
                    }, f, ensure_ascii=False, indent=2)

                # 调用推送回调
                for callback in self._push_callbacks:
                    try:
                        callback(self._realtime_cache)
                    except Exception as e:
                        print(f"  警告：推送回调失败: {e}")

            except Exception as e:
                print(f"[效能实时推送] 自动刷新错误: {e}")

            # 等待下一个刷新周期
            for _ in range(self._refresh_interval):
                if not self._auto_refresh_running:
                    break
                time.sleep(1)

    def register_push_callback(self, callback: Callable):
        """注册推送回调"""
        self._push_callbacks.append(callback)
        print(f"[效能实时推送] 已注册推送回调: {callback.__name__}")

    def get_cockpit_data(self) -> Dict[str, Any]:
        """获取驾驶舱展示数据"""
        print("[效能实时推送] 生成驾驶舱数据...")

        # 收集实时数据
        realtime_data = self.collect_realtime_data()

        # 读取自动刷新状态
        auto_refresh_state = {}
        if self.auto_refresh_state_file.exists():
            with open(self.auto_refresh_state_file, 'r', encoding='utf-8') as f:
                auto_refresh_state = json.load(f)

        # 读取预警历史
        warning_history = {}
        if self.warning_history_file.exists():
            with open(self.warning_history_file, 'r', encoding='utf-8') as f:
                warning_history = json.load(f)

        cockpit_data = {
            "engine": self.name,
            "version": self.version,
            "collection_time": datetime.now().isoformat(),
            "realtime_metrics": realtime_data.get("metrics", {}),
            "active_warnings": self._active_warnings,
            "warning_count": len(self._active_warnings),
            "auto_refresh": {
                "running": auto_refresh_state.get("running", False),
                "interval_seconds": auto_refresh_state.get("interval_seconds", 300),
                "refresh_count": auto_refresh_state.get("refresh_count", 0),
                "last_refresh": auto_refresh_state.get("last_refresh")
            },
            "historical_warnings": {
                "total": warning_history.get("total_count", 0),
                "recent": warning_history.get("warnings", [])[-10:]
            },
            "thresholds": self._load_config().get("warning", {}).get("thresholds", {}),
            "realtime_data_url": str(self.realtime_data_file),
            "warning_history_url": str(self.warning_history_file)
        }

        print("[效能实时推送] 驾驶舱数据生成完成")
        return cockpit_data

    def run_full_integration(self) -> Dict[str, Any]:
        """运行完整集成"""
        print("="*60)
        print("[效能实时推送与驾驶舱集成引擎] 开始运行...")
        print("="*60)

        result = {
            "engine": self.name,
            "version": self.version,
            "execution_time": datetime.now().isoformat(),
            "steps": {}
        }

        # 步骤1: 收集实时数据
        print("\n[步骤1] 收集实时效能数据...")
        realtime_data = self.collect_realtime_data()
        result["steps"]["data_collection"] = {
            "status": "completed",
            "metrics_collected": len(realtime_data.get("metrics", {}))
        }

        # 步骤2: 预警检查
        print("\n[步骤2] 智能预警检查...")
        warnings = realtime_data.get("warnings", [])
        result["steps"]["warning_check"] = {
            "status": "completed",
            "warnings_found": len(warnings)
        }
        for w in warnings:
            print(f"  - [{w.get('severity').upper()}] {w.get('message')}")

        # 步骤3: 动态阈值调整
        print("\n[步骤3] 动态阈值调整（如启用）...")
        threshold_adjustment = self.adjust_warning_thresholds_dynamically()
        result["steps"]["threshold_adjustment"] = {
            "status": "completed",
            "adjustments": len(threshold_adjustment.get("adjustments", []))
        }

        # 步骤4: 驾驶舱数据
        print("\n[步骤4] 生成驾驶舱数据...")
        cockpit_data = self.get_cockpit_data()
        result["steps"]["cockpit_data"] = {
            "status": "completed",
            "auto_refresh_running": cockpit_data.get("auto_refresh", {}).get("running", False)
        }

        print("\n" + "="*60)
        print("[效能实时推送与驾驶舱集成引擎] 运行完成!")
        print("="*60)

        return result


def main():
    """主函数 - 命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(
        description="智能全场景进化环效能实时数据推送与驾驶舱智能预警深度集成引擎"
    )
    parser.add_argument("--status", action="store_true", help="查看引擎状态")
    parser.add_argument("--collect", action="store_true", help="收集实时数据")
    parser.add_argument("--check-warnings", action="store_true", help="检查预警")
    parser.add_argument("--adjust-thresholds", action="store_true", help="动态调整阈值")
    parser.add_argument("--start-auto-refresh", action="store_true", help="启动自动刷新")
    parser.add_argument("--stop-auto-refresh", action="store_true", help="停止自动刷新")
    parser.add_argument("--run", action="store_true", help="运行完整集成")
    parser.add_argument("--cockpit-data", action="store_true", help="获取驾驶舱数据")
    parser.add_argument("--interval", type=int, default=300, help="自动刷新间隔（秒）")

    args = parser.parse_args()

    engine = RealtimePerformancePushCockpitIntegrationEngine()

    if args.status:
        config = engine._load_config()
        print(f"引擎版本: {engine.version}")
        print(f"推送启用: {config.get('push_enabled', True)}")
        print(f"自动刷新: {config.get('auto_refresh', {}).get('enabled', True)}")
        print(f"预警启用: {config.get('warning', {}).get('enabled', True)}")

        # 显示自动刷新状态
        if Path(engine.auto_refresh_state_file).exists():
            with open(engine.auto_refresh_state_file, 'r', encoding='utf-8') as f:
                state = json.load(f)
                print(f"自动刷新运行中: {state.get('running', False)}")
                print(f"刷新次数: {state.get('refresh_count', 0)}")

    elif args.collect:
        result = engine.collect_realtime_data()
        print(f"\n实时指标: {result.get('metrics', {})}")
        if result.get("warnings"):
            print(f"\n预警:")
            for w in result["warnings"]:
                print(f"  - [{w.get('severity')}] {w.get('message')}")

    elif args.check_warnings:
        metrics = engine.collect_realtime_data().get("metrics", {})
        warnings = engine.check_warnings(metrics)
        print(f"\n预警数量: {len(warnings)}")
        for w in warnings:
            print(f"  - [{w.get('severity')}] {w.get('message')}")

    elif args.adjust_thresholds:
        result = engine.adjust_warning_thresholds_dynamically()
        print(f"\n调整结果: {result.get('message')}")
        if result.get("adjustments"):
            print("调整详情:")
            for adj in result["adjustments"]:
                print(f"  - {adj.get('type')}: {adj.get('action')}")

    elif args.start_auto_refresh:
        engine.start_auto_refresh(args.interval)
        print(f"自动刷新已启动，间隔: {args.interval}秒")

    elif args.stop_auto_refresh:
        engine.stop_auto_refresh()
        print("自动刷新已停止")

    elif args.run:
        result = engine.run_full_integration()
        print(f"\n执行时间: {result.get('execution_time')}")
        print(f"收集指标: {result['steps']['data_collection']['metrics_collected']}")
        print(f"发现预警: {result['steps']['warning_check']['warnings_found']}")
        print(f"阈值调整: {result['steps']['threshold_adjustment']['adjustments']}")

    elif args.cockpit_data:
        data = engine.get_cockpit_data()
        print(json.dumps(data, ensure_ascii=False, indent=2))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()