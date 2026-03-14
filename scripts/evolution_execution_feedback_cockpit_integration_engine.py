#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环执行效果实时反馈与进化驾驶舱深度集成引擎
Evolution Execution Feedback Cockpit Integration Engine

将 round 418/419 的策略反馈调整能力、round 425 的趋势分析能力与进化驾驶舱（round 350）深度集成，实现：
1. 驾驶舱实时显示策略执行效果
2. 反馈调整状态可视化
3. 智能推荐优化建议展示
4. 跨引擎数据共享与状态同步
5. 执行效果驱动的推荐优化
6. 进化趋势预测与驾驶舱集成（round 426 增强）

功能：
1. 执行效果实时监控
2. 反馈状态驾驶舱可视化
3. 策略调整建议展示
4. 执行趋势分析
5. 智能预警
6. 趋势预测驾驶舱可视化（新增）
7. 实时数据推送与动态刷新（新增）
8. 多维度效果指标展示（增强）

Version: 1.1.0

依赖：
- evolution_cockpit_engine.py (round 350)
- evolution_strategy_feedback_adjustment_engine.py (round 418)
- evolution_strategy_recommendation_feedback_integration_engine.py (round 419)
- evolution_execution_trend_analysis_engine.py (round 425)
"""

import os
import sys
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from collections import defaultdict
import threading

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


class ExecutionFeedbackCockpitIntegrationEngine:
    """进化环执行效果反馈与驾驶舱深度集成引擎"""

    def __init__(self, state_dir: str = "runtime/state"):
        self.version = "1.1.0"
        self.state_dir = Path(state_dir)
        self.project_root = PROJECT_ROOT
        self.scripts_dir = SCRIPT_DIR
        self.runtime_dir = Path(self.project_root) / "runtime"
        self.logs_dir = Path(self.project_root) / "runtime" / "logs"

        # 状态文件
        self.state_file = self.state_dir / "execution_feedback_cockpit_state.json"
        self.history_file = self.state_dir / "execution_feedback_cockpit_history.json"

        # 初始化目录
        self._ensure_directories()

        # 状态
        self.state = self._load_state()

        # 引擎实例
        self.cockpit_engine = None
        self.feedback_engine = None
        self.trend_engine = None  # round 425 新增
        self._initialize_engines()

    def _ensure_directories(self):
        """确保必要的目录存在"""
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)

    def _initialize_engines(self):
        """初始化集成的引擎"""
        # 尝试导入进化驾驶舱引擎
        try:
            from evolution_cockpit_engine import EvolutionCockpitEngine
            self.cockpit_engine = EvolutionCockpitEngine()
            _safe_print("[反馈驾驶舱集成] 进化驾驶舱引擎已加载")
        except ImportError as e:
            _safe_print(f"[反馈驾驶舱集成] 无法加载进化驾驶舱引擎: {e}")
            self.cockpit_engine = None

        # 尝试导入策略反馈调整引擎
        try:
            from evolution_strategy_feedback_adjustment_engine import StrategyFeedbackAdjustmentEngine
            self.feedback_engine = StrategyFeedbackAdjustmentEngine(state_dir=str(self.state_dir))
            _safe_print("[反馈驾驶舱集成] 策略反馈调整引擎已加载")
        except ImportError as e:
            _safe_print(f"[反馈驾驶舱集成] 无法加载策略反馈调整引擎: {e}")
            self.feedback_engine = None

        # round 425 新增：尝试导入趋势分析引擎
        try:
            from evolution_execution_trend_analysis_engine import EvolutionExecutionTrendAnalysisEngine
            self.trend_engine = EvolutionExecutionTrendAnalysisEngine()
            _safe_print("[反馈驾驶舱集成] 进化趋势分析引擎已加载 (round 425)")
        except ImportError as e:
            _safe_print(f"[反馈驾驶舱集成] 无法加载进化趋势分析引擎: {e}")
            self.trend_engine = None

    def _load_state(self) -> Dict[str, Any]:
        """加载状态"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                _safe_print(f"[反馈驾驶舱集成] 状态加载失败: {e}")

        # 默认状态
        default_state = {
            "version": self.version,
            "initialized_at": datetime.now().isoformat(),
            "last_update": datetime.now().isoformat(),
            "integrated_engines": {
                "cockpit": False,
                "feedback": False,
                "trend": False  # round 425 新增
            },
            "execution_tracking": {},
            "feedback_history": [],
            "dashboard_data": {
                "realtime_metrics": {},
                "adjustment_status": {},
                "optimization_suggestions": [],
                "execution_trends": [],
                "trend_predictions": {},  # round 426 新增：趋势预测数据
                "realtime_push_enabled": True  # round 426 新增：实时推送开关
            },
            "statistics": {
                "total_executions": 0,
                "total_adjustments": 0,
                "average_deviation": 0.0,
                "optimization_count": 0,
                "trend_predictions_count": 0  # round 426 新增
            }
        }

        self._save_state(default_state)
        return default_state

    def _save_state(self, state: Dict):
        """保存状态"""
        try:
            state["last_update"] = datetime.now().isoformat()
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
        except Exception as e:
            _safe_print(f"[反馈驾驶舱集成] 状态保存失败: {e}")

    def track_execution_effect(self, strategy_name: str, execution_data: Dict[str, Any]) -> Dict[str, Any]:
        """跟踪策略执行效果并同步到驾驶舱"""
        result = {
            "status": "success",
            "strategy_name": strategy_name,
            "tracked_at": datetime.now().isoformat(),
            "dashboard_update": False,
            "feedback_update": False
        }

        try:
            # 更新执行跟踪记录
            if strategy_name not in self.state["execution_tracking"]:
                self.state["execution_tracking"][strategy_name] = {
                    "executions": [],
                    "total_runs": 0,
                    "last_execution": None
                }

            execution_record = {
                "timestamp": datetime.now().isoformat(),
                "data": execution_data,
                "metrics": execution_data.get("metrics", {})
            }

            self.state["execution_tracking"][strategy_name]["executions"].append(execution_record)
            self.state["execution_tracking"][strategy_name]["total_runs"] += 1
            self.state["execution_tracking"][strategy_name]["last_execution"] = datetime.now().isoformat()

            # 更新统计
            self.state["statistics"]["total_executions"] += 1

            # 如果有反馈引擎，也更新反馈数据
            if self.feedback_engine:
                try:
                    feedback_result = self.feedback_engine.track_execution(strategy_name, execution_data)
                    result["feedback_update"] = True
                    result["feedback_data"] = feedback_result
                except Exception as e:
                    _safe_print(f"[反馈驾驶舱集成] 反馈引擎更新失败: {e}")

            # 更新驾驶舱数据
            self._update_dashboard_data(strategy_name, execution_data)

            # 保存状态
            self._save_state(self.state)

            result["dashboard_update"] = True
            result["execution_id"] = len(self.state["execution_tracking"][strategy_name]["executions"]) - 1

        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
            _safe_print(f"[反馈驾驶舱集成] 执行效果跟踪失败: {e}")

        return result

    def _update_dashboard_data(self, strategy_name: str, execution_data: Dict[str, Any]):
        """更新驾驶舱数据"""
        # 更新实时指标
        metrics = execution_data.get("metrics", {})
        self.state["dashboard_data"]["realtime_metrics"][strategy_name] = {
            "timestamp": datetime.now().isoformat(),
            "success_rate": metrics.get("success_rate", 0),
            "efficiency": metrics.get("efficiency", 0),
            "deviation": metrics.get("deviation", 0),
            "execution_time": metrics.get("execution_time", 0)
        }

        # 更新执行趋势
        trend_entry = {
            "timestamp": datetime.now().isoformat(),
            "strategy": strategy_name,
            "metrics": metrics
        }
        self.state["dashboard_data"]["execution_trends"].append(trend_entry)

        # 限制趋势数据量
        max_trends = 100
        if len(self.state["dashboard_data"]["execution_trends"]) > max_trends:
            self.state["dashboard_data"]["execution_trends"] = \
                self.state["dashboard_data"]["execution_trends"][-max_trends:]

    def get_adjustment_status(self, strategy_name: Optional[str] = None) -> Dict[str, Any]:
        """获取反馈调整状态"""
        status = {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "strategies": {}
        }

        if strategy_name:
            # 获取特定策略的调整状态
            if strategy_name in self.state["execution_tracking"]:
                tracking = self.state["execution_tracking"][strategy_name]
                status["strategies"][strategy_name] = {
                    "total_runs": tracking["total_runs"],
                    "last_execution": tracking.get("last_execution"),
                    "dashboard_metrics": self.state["dashboard_data"]["realtime_metrics"].get(strategy_name, {}),
                    "adjustment_pending": self._check_adjustment_pending(strategy_name)
                }
        else:
            # 获取所有策略的调整状态
            for strat, tracking in self.state["execution_tracking"].items():
                status["strategies"][strat] = {
                    "total_runs": tracking["total_runs"],
                    "last_execution": tracking.get("last_execution"),
                    "dashboard_metrics": self.state["dashboard_data"]["realtime_metrics"].get(strat, {}),
                    "adjustment_pending": self._check_adjustment_pending(strat)
                }

        return status

    def _check_adjustment_pending(self, strategy_name: str) -> bool:
        """检查是否需要调整"""
        if strategy_name not in self.state["execution_tracking"]:
            return False

        tracking = self.state["execution_tracking"][strategy_name]
        executions = tracking.get("executions", [])

        if len(executions) < 2:
            return False

        # 检查最近执行的偏差
        recent_executions = executions[-5:]
        deviations = [e.get("data", {}).get("metrics", {}).get("deviation", 0) for e in recent_executions]

        # 如果平均偏差超过阈值，建议调整
        if deviations:
            avg_deviation = sum(deviations) / len(deviations)
            return avg_deviation > 0.15  # 15% 偏差阈值

        return False

    def generate_optimization_suggestions(self, strategy_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """生成优化建议"""
        suggestions = []

        # 分析执行数据生成建议
        if strategy_name and strategy_name in self.state["execution_tracking"]:
            tracking = self.state["execution_tracking"][strategy_name]
            executions = tracking.get("executions", [])

            if len(executions) >= 3:
                # 分析执行效率趋势
                recent_metrics = [e.get("data", {}).get("metrics", {}) for e in executions[-5:]]

                # 检查是否有性能下降
                if len(recent_metrics) >= 2:
                    recent_efficiency = recent_metrics[-1].get("efficiency", 0)
                    older_efficiency = recent_metrics[0].get("efficiency", 0)

                    if recent_efficiency < older_efficiency * 0.8:
                        suggestions.append({
                            "type": "efficiency_degradation",
                            "strategy": strategy_name,
                            "message": f"策略 {strategy_name} 效率下降了 {((older_efficiency - recent_efficiency) / older_efficiency * 100):.1f}%",
                            "recommendation": "建议调整策略参数或重新评估执行方案",
                            "priority": "high"
                        })

                # 检查执行时间趋势
                exec_times = [m.get("execution_time", 0) for m in recent_metrics if m.get("execution_time")]
                if len(exec_times) >= 2 and exec_times[-1] > exec_times[0] * 1.5:
                    suggestions.append({
                        "type": "execution_time_increase",
                        "strategy": strategy_name,
                        "message": f"策略 {strategy_name} 执行时间增加了",
                        "recommendation": "建议优化执行流程或增加并行处理",
                        "priority": "medium"
                    })

        # 检查整体统计
        stats = self.state["statistics"]
        if stats["total_executions"] > 0:
            avg_dev = stats.get("average_deviation", 0)
            if avg_dev > 0.2:
                suggestions.append({
                    "type": "high_deviation",
                    "strategy": "global",
                    "message": f"整体策略偏差偏高 ({avg_dev*100:.1f}%)",
                    "recommendation": "建议重新校准策略评估模型",
                    "priority": "high"
                })

        # 更新状态中的建议
        self.state["dashboard_data"]["optimization_suggestions"] = suggestions

        return suggestions

    def get_dashboard_integration_data(self) -> Dict[str, Any]:
        """获取驾驶舱集成数据"""
        # 获取趋势分析数据（round 425 新增）
        trend_data = {}
        if self.trend_engine:
            try:
                trend_status = self.trend_engine.get_status()
                trend_data = {
                    "available": True,
                    "status": trend_status.get("status", "unknown"),
                    "overall_health": trend_status.get("overall_health", "unknown"),
                    "total_history_rounds": trend_status.get("total_history_rounds", 0)
                }
                # 获取预测数据
                try:
                    analysis_result = self.trend_engine.analyze_and_predict()
                    if analysis_result.get("status") == "success":
                        trend_data["predictions"] = analysis_result.get("predictions", {})
                        trend_data["trends"] = analysis_result.get("trends", {})
                        trend_data["optimization_suggestions"] = analysis_result.get("optimization_suggestions", [])
                except Exception as e:
                    _safe_print(f"[反馈驾驶舱集成] 获取趋势分析失败: {e}")
            except Exception as e:
                _safe_print(f"[反馈驾驶舱集成] 获取趋势引擎状态失败: {e}")

        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "version": self.version,
            "engines_status": {
                "cockpit": self.cockpit_engine is not None,
                "feedback": self.feedback_engine is not None,
                "trend": self.trend_engine is not None  # round 426 新增
            },
            "realtime_metrics": self.state["dashboard_data"]["realtime_metrics"],
            "adjustment_status": self.get_adjustment_status()["strategies"],
            "optimization_suggestions": self.state["dashboard_data"]["optimization_suggestions"],
            "execution_trends": self.state["dashboard_data"]["execution_trends"][-20:],  # 最近20条
            "trend_analysis": trend_data,  # round 426 新增
            "realtime_push_enabled": self.state["dashboard_data"].get("realtime_push_enabled", True),  # round 426 新增
            "statistics": self.state["statistics"]
        }

    def get_trend_predictions_for_cockpit(self) -> Dict[str, Any]:
        """获取趋势预测数据用于驾驶舱展示（round 426 新增）"""
        result = {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "trend_predictions": {},
            "realtime_update": True
        }

        if not self.trend_engine:
            result["status"] = "no_trend_engine"
            return result

        try:
            # 获取状态
            status = self.trend_engine.get_status()
            result["trend_predictions"]["status"] = status.get("status", "unknown")
            result["trend_predictions"]["overall_health"] = status.get("overall_health", "unknown")
            result["trend_predictions"]["total_rounds"] = status.get("total_history_rounds", 0)

            # 获取分析结果
            analysis = self.trend_engine.analyze_and_predict()
            if analysis.get("status") == "success":
                result["trend_predictions"]["predictions"] = analysis.get("predictions", {})
                result["trend_predictions"]["trends"] = analysis.get("trends", {})
                result["trend_predictions"]["recommendations"] = analysis.get("optimization_suggestions", [])

            # 更新本地状态
            self.state["dashboard_data"]["trend_predictions"] = result["trend_predictions"]
            self.state["statistics"]["trend_predictions_count"] += 1
            self._save_state(self.state)

        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
            _safe_print(f"[反馈驾驶舱集成] 获取趋势预测失败: {e}")

        return result

    def enable_realtime_push(self, enabled: bool = True):
        """启用/禁用实时推送（round 426 新增）"""
        self.state["dashboard_data"]["realtime_push_enabled"] = enabled
        self._save_state(self.state)
        _safe_print(f"[反馈驾驶舱集成] 实时推送已{'启用' if enabled else '禁用'}")

    def execute_full_integration_loop(self, strategy_name: str, execution_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行完整的集成闭环：跟踪→反馈→分析→建议→驾驶舱更新"""
        result = {
            "status": "success",
            "strategy_name": strategy_name,
            "timestamp": datetime.now().isoformat(),
            "steps": {}
        }

        try:
            # 步骤1: 跟踪执行效果
            track_result = self.track_execution_effect(strategy_name, execution_data)
            result["steps"]["tracking"] = track_result

            # 步骤2: 获取调整状态
            adjustment_status = self.get_adjustment_status(strategy_name)
            result["steps"]["adjustment_status"] = adjustment_status

            # 步骤3: 生成优化建议
            suggestions = self.generate_optimization_suggestions(strategy_name)
            result["steps"]["suggestions"] = suggestions

            # 步骤4: 如果有驾驶舱引擎，同步数据
            if self.cockpit_engine:
                try:
                    # 获取驾驶舱数据并合并
                    cockpit_data = self.cockpit_engine.get_dashboard_data() if hasattr(self.cockpit_engine, 'get_dashboard_data') else {}
                    result["steps"]["cockpit_sync"] = {"status": "success", "data": cockpit_data}
                except Exception as e:
                    result["steps"]["cockpit_sync"] = {"status": "error", "error": str(e)}

            # 步骤5: 如果有反馈引擎，执行反馈闭环
            if self.feedback_engine:
                try:
                    feedback_loop = self.feedback_engine.execute_full_loop(strategy_name, execution_data)
                    result["steps"]["feedback_loop"] = feedback_loop
                except Exception as e:
                    result["steps"]["feedback_loop"] = {"status": "error", "error": str(e)}

            result["completed"] = True

        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
            _safe_print(f"[反馈驾驶舱集成] 完整集成闭环执行失败: {e}")

        return result

    def get_status(self) -> Dict[str, Any]:
        """获取引擎状态"""
        return {
            "status": "running",
            "version": self.version,
            "initialized_at": self.state.get("initialized_at"),
            "last_update": self.state.get("last_update"),
            "engines_status": {
                "cockpit": self.cockpit_engine is not None,
                "feedback": self.feedback_engine is not None,
                "trend": self.trend_engine is not None  # round 426 新增
            },
            "statistics": self.state["statistics"],
            "tracked_strategies": list(self.state["execution_tracking"].keys()),
            "realtime_push": self.state["dashboard_data"].get("realtime_push_enabled", True)  # round 426 新增
        }

    def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        health = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "checks": {}
        }

        # 检查引擎状态
        health["checks"]["cockpit_engine"] = "ok" if self.cockpit_engine else "not_loaded"
        health["checks"]["feedback_engine"] = "ok" if self.feedback_engine else "not_loaded"
        health["checks"]["trend_engine"] = "ok" if self.trend_engine else "not_loaded"  # round 426 新增

        # 检查状态文件
        health["checks"]["state_file"] = "ok" if self.state_file.exists() else "missing"

        # 检查目录
        health["checks"]["state_dir"] = "ok" if self.state_dir.exists() else "missing"

        # 统计健康状态
        if health["checks"]["cockpit_engine"] == "not_loaded" or health["checks"]["feedback_engine"] == "not_loaded":
            health["status"] = "degraded"

        return health


def main():
    """主函数 - 用于命令行调用"""
    import argparse

    parser = argparse.ArgumentParser(description="进化环执行效果反馈与驾驶舱深度集成引擎 (v1.1.0)")
    parser.add_argument("command", choices=["track", "status", "adjustments", "suggestions", "dashboard", "health", "loop", "trend_predictions", "enable_push", "disable_push"],
                        help="要执行的命令")
    parser.add_argument("--strategy", type=str, help="策略名称")
    parser.add_argument("--data", type=str, help="执行数据 (JSON 字符串)")
    parser.add_argument("--state-dir", type=str, default="runtime/state", help="状态目录")

    args = parser.parse_args()

    # 初始化引擎
    engine = ExecutionFeedbackCockpitIntegrationEngine(state_dir=args.state_dir)

    if args.command == "track":
        if not args.strategy or not args.data:
            print("错误: track 命令需要 --strategy 和 --data 参数")
            return

        try:
            execution_data = json.loads(args.data)
        except json.JSONDecodeError:
            print("错误: --data 必须是有效的 JSON 字符串")
            return

        result = engine.track_execution_effect(args.strategy, execution_data)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif args.command == "status":
        result = engine.get_status()
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif args.command == "adjustments":
        result = engine.get_adjustment_status(args.strategy)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif args.command == "suggestions":
        result = engine.generate_optimization_suggestions(args.strategy)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif args.command == "dashboard":
        result = engine.get_dashboard_integration_data()
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif args.command == "health":
        result = engine.health_check()
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif args.command == "loop":
        if not args.strategy or not args.data:
            print("错误: loop 命令需要 --strategy 和 --data 参数")
            return

        try:
            execution_data = json.loads(args.data)
        except json.JSONDecodeError:
            print("错误: --data 必须是有效的 JSON 字符串")
            return

        result = engine.execute_full_integration_loop(args.strategy, execution_data)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif args.command == "trend_predictions":
        # round 426 新增：获取趋势预测数据
        result = engine.get_trend_predictions_for_cockpit()
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif args.command == "enable_push":
        # round 426 新增：启用实时推送
        engine.enable_realtime_push(True)
        print(json.dumps({"status": "success", "message": "实时推送已启用"}, indent=2, ensure_ascii=False))

    elif args.command == "disable_push":
        # round 426 新增：禁用实时推送
        engine.enable_realtime_push(False)
        print(json.dumps({"status": "success", "message": "实时推送已禁用"}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()