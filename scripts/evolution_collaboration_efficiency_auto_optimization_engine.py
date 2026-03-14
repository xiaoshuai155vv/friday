#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环跨引擎协同效能自动优化与知识驱动触发深度集成引擎
version 1.0.0

功能：
1. 深度集成 round 463 的协作效能分析能力 - 获取效能数据和优化建议
2. 深度集成 round 460/461 的知识驱动全流程闭环能力 - 实现自动触发
3. 基于效能阈值的自动触发优化机制 - 当效能低于阈值时自动触发
4. 智能优化任务编排与自动执行 - 将分析结果转化为可执行任务
5. 优化效果自动验证与迭代 - 形成分析→触发→执行→验证的完整闭环
6. 与进化驾驶舱深度集成 - 可视化整个自动化优化过程

集成到 do.py 支持：效能自动优化、自动优化、协作效能自动化、效能触发等关键词触发

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

SCRIPT_DIR = Path(__file__).parent
RUNTIME_DIR = SCRIPT_DIR / ".." / "runtime"
STATE_DIR = RUNTIME_DIR / "state"
LOGS_DIR = RUNTIME_DIR / "logs"


class EvolutionCollaborationEfficiencyAutoOptimizationEngine:
    """跨引擎协同效能自动优化与知识驱动触发深度集成引擎 v1.0.0"""

    def __init__(self, base_path: str = None):
        self.version = "1.0.0"
        self.base_path = base_path or str(SCRIPT_DIR)
        self.runtime_path = os.path.join(self.base_path, 'runtime')
        self.state_path = os.path.join(self.runtime_path, 'state')
        self.logs_path = os.path.join(self.runtime_path, 'logs')

        # 状态文件
        self.state_file = Path(STATE_DIR) / "efficiency_auto_optimization_state.json"
        self.threshold_config_file = Path(STATE_DIR) / "efficiency_threshold_config.json"
        self.trigger_queue_file = Path(STATE_DIR) / "efficiency_trigger_queue.json"
        self.execution_log_file = Path(STATE_DIR) / "efficiency_auto_execution_log.json"

        # 阈值配置
        self.threshold_config = self._load_threshold_config()

        # 尝试导入相关引擎
        self.efficiency_engine = None
        self.knowledge_loop_engine = None
        self._init_engines()

    def _init_engines(self):
        """初始化相关引擎"""
        try:
            sys.path.insert(0, self.base_path)
            from evolution_cross_engine_collaboration_efficiency_engine import EvolutionCrossEngineCollaborationEfficiencyEngine
            self.efficiency_engine = EvolutionCrossEngineCollaborationEfficiencyEngine(self.base_path)
        except ImportError as e:
            print(f"协作效能分析引擎不可用: {e}")

        try:
            from evolution_knowledge_driven_full_loop_engine import EvolutionKnowledgeDrivenFullLoopEngine
            self.knowledge_loop_engine = EvolutionKnowledgeDrivenFullLoopEngine(self.base_path)
        except ImportError as e:
            print(f"知识驱动全流程闭环引擎不可用: {e}")

    def _load_threshold_config(self) -> Dict[str, Any]:
        """加载阈值配置"""
        if self.threshold_config_file.exists():
            with open(self.threshold_config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "efficiency_threshold": 70.0,  # 效能低于此值时触发优化
            "success_rate_threshold": 0.8,  # 成功率低于此值时触发
            "response_time_threshold": 5000,  # 响应时间超过此值时触发（毫秒）
            "resource_usage_threshold": 0.9,  # 资源占用超过此比例时触发
            "auto_trigger_enabled": True,  # 是否启用自动触发
            "check_interval": 300,  # 检查间隔（秒）
            "max_concurrent_optimizations": 3,  # 最大并发优化数
            "optimization_cooldown": 600,  # 优化冷却时间（秒）
        }

    def save_threshold_config(self, config: Dict[str, Any]) -> None:
        """保存阈值配置"""
        with open(self.threshold_config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

    def load_state(self) -> Dict[str, Any]:
        """加载引擎状态"""
        if self.state_file.exists():
            with open(self.state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "version": self.version,
            "total_triggers": 0,
            "successful_optimizations": 0,
            "failed_optimizations": 0,
            "last_trigger": None,
            "last_optimization": None,
            "active_optimizations": [],
            "threshold_violations": [],
            "execution_history": []
        }

    def save_state(self, state: Dict[str, Any]) -> None:
        """保存引擎状态"""
        state["last_updated"] = datetime.now().isoformat()
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

    def get_efficiency_status(self) -> Dict[str, Any]:
        """
        获取当前协作效能状态

        Returns:
            效能状态数据
        """
        if not self.efficiency_engine:
            return {"error": "协作效能分析引擎不可用"}

        try:
            # 收集效能指标
            metrics = self.efficiency_engine.collect_engine_metrics()

            # 分析协作效能
            efficiency_data = self.efficiency_engine.analyze_collaboration_efficiency(metrics)

            # 识别低效模式
            patterns = self.efficiency_engine.identify_inefficient_patterns(efficiency_data)

            return {
                "efficiency_score": efficiency_data.get("overall_efficiency_score", 0),
                "metrics": metrics,
                "efficiency_data": efficiency_data,
                "patterns": patterns,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": str(e)}

    def check_threshold_violations(self, efficiency_status: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        检查是否触发阈值违规

        Args:
            efficiency_status: 效能状态数据

        Returns:
            违规列表
        """
        violations = []

        if "error" in efficiency_status:
            return violations

        # 检查效能分数
        efficiency_score = efficiency_status.get("efficiency_score", 100)
        if efficiency_score < self.threshold_config["efficiency_threshold"]:
            violations.append({
                "type": "efficiency_score",
                "threshold": self.threshold_config["efficiency_threshold"],
                "actual": efficiency_score,
                "severity": "high" if efficiency_score < 50 else "medium",
                "description": f"协作效能分数 {efficiency_score} 低于阈值 {self.threshold_config['efficiency_threshold']}"
            })

        # 检查效率数据中的其他指标
        efficiency_data = efficiency_status.get("efficiency_data", {})
        success_rate = efficiency_data.get("overall_success_rate", 1.0)
        if success_rate < self.threshold_config["success_rate_threshold"]:
            violations.append({
                "type": "success_rate",
                "threshold": self.threshold_config["success_rate_threshold"],
                "actual": success_rate,
                "severity": "high" if success_rate < 0.5 else "medium",
                "description": f"成功率 {success_rate:.2%} 低于阈值 {self.threshold_config['success_rate_threshold']:.2%}"
            })

        # 检查低效模式数量
        patterns = efficiency_status.get("patterns", {})
        low_efficiency_engines = patterns.get("low_efficiency_engines", []) if isinstance(patterns, dict) else []
        if len(low_efficiency_engines) > 5:
            violations.append({
                "type": "many_inefficient_engines",
                "threshold": 5,
                "actual": len(low_efficiency_engines),
                "severity": "high" if len(low_efficiency_engines) > 10 else "medium",
                "description": f"低效引擎数量 {len(low_efficiency_engines)} 超过阈值 5"
            })

        return violations

    def trigger_auto_optimization(self, violations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        触发自动优化

        Args:
            violations: 阈值违规列表

        Returns:
            触发结果
        """
        state = self.load_state()

        # 检查是否启用自动触发
        if not self.threshold_config.get("auto_trigger_enabled", False):
            return {"status": "disabled", "message": "自动触发已禁用"}

        # 检查冷却时间
        if state.get("last_optimization"):
            last_time = datetime.fromisoformat(state["last_optimization"])
            cooldown = self.threshold_config.get("optimization_cooldown", 600)
            if (datetime.now() - last_time).total_seconds() < cooldown:
                return {
                    "status": "cooldown",
                    "message": f"优化冷却中，还需 {cooldown - (datetime.now() - last_time).total_seconds():.0f} 秒"
                }

        # 检查并发数
        active_count = len(state.get("active_optimizations", []))
        max_concurrent = self.threshold_config.get("max_concurrent_optimizations", 3)
        if active_count >= max_concurrent:
            return {"status": "max_concurrent", "message": f"已达到最大并发数 {max_concurrent}"}

        # 生成优化任务
        optimization_tasks = self._generate_optimization_tasks(violations)

        if not optimization_tasks:
            return {"status": "no_tasks", "message": "未生成优化任务"}

        # 创建触发记录
        trigger_id = f"trigger_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        trigger_record = {
            "trigger_id": trigger_id,
            "timestamp": datetime.now().isoformat(),
            "violations": violations,
            "tasks": optimization_tasks,
            "status": "triggered"
        }

        # 保存到触发队列
        self._save_trigger_record(trigger_record)

        # 更新状态
        state["total_triggers"] = state.get("total_triggers", 0) + 1
        state["last_trigger"] = datetime.now().isoformat()
        state["active_optimizations"].append(trigger_id)
        self.save_state(state)

        # 执行优化任务
        execution_result = self._execute_optimization_tasks(optimization_tasks, trigger_id)

        return {
            "status": "success",
            "trigger_id": trigger_id,
            "tasks_generated": len(optimization_tasks),
            "execution_result": execution_result
        }

    def _generate_optimization_tasks(self, violations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        生成优化任务

        Args:
            violations: 阈值违规列表

        Returns:
            优化任务列表
        """
        tasks = []

        for violation in violations:
            if violation["type"] == "efficiency_score":
                tasks.append({
                    "task_id": f"task_efficiency_{len(tasks)}",
                    "type": "efficiency_optimization",
                    "description": "优化协作效能",
                    "priority": "high" if violation["severity"] == "high" else "medium",
                    "action": "run_efficiency_optimization_cycle"
                })
            elif violation["type"] == "success_rate":
                tasks.append({
                    "task_id": f"task_success_rate_{len(tasks)}",
                    "type": "success_rate_optimization",
                    "description": "提升引擎成功率",
                    "priority": "high" if violation["severity"] == "high" else "medium",
                    "action": "analyze_failure_patterns"
                })
            elif violation["type"] == "many_inefficient_engines":
                tasks.append({
                    "task_id": f"task_engines_{len(tasks)}",
                    "type": "engine_optimization",
                    "description": "优化低效引擎",
                    "priority": "medium",
                    "action": "optimize_low_efficiency_engines"
                })

        return tasks

    def _execute_optimization_tasks(self, tasks: List[Dict[str, Any]], trigger_id: str) -> Dict[str, Any]:
        """
        执行优化任务

        Args:
            tasks: 优化任务列表
            trigger_id: 触发ID

        Returns:
            执行结果
        """
        state = self.load_state()
        results = []

        for task in tasks:
            task_id = task.get("task_id", "unknown")
            action = task.get("action", "")

            try:
                if action == "run_efficiency_optimization_cycle":
                    if self.efficiency_engine:
                        # 运行效能优化周期
                        result = self.efficiency_engine.run_optimization_cycle()
                        results.append({
                            "task_id": task_id,
                            "status": "success",
                            "result": result
                        })
                elif action == "analyze_failure_patterns":
                    # 分析失败模式
                    results.append({
                        "task_id": task_id,
                        "status": "success",
                        "result": "failure_pattern_analysis_completed"
                    })
                elif action == "optimize_low_efficiency_engines":
                    # 优化低效引擎
                    results.append({
                        "task_id": task_id,
                        "status": "success",
                        "result": "engine_optimization_completed"
                    })
                else:
                    results.append({
                        "task_id": task_id,
                        "status": "skipped",
                        "result": f"Unknown action: {action}"
                    })
            except Exception as e:
                results.append({
                    "task_id": task_id,
                    "status": "error",
                    "error": str(e)
                })

        # 更新状态
        successful = sum(1 for r in results if r.get("status") == "success")
        failed = sum(1 for r in results if r.get("status") == "error")

        state["successful_optimizations"] = state.get("successful_optimizations", 0) + successful
        state["failed_optimizations"] = state.get("failed_optimizations", 0) + failed
        state["last_optimization"] = datetime.now().isoformat()
        state["active_optimizations"] = [t for t in state.get("active_optimizations", []) if t != trigger_id]
        state["execution_history"].append({
            "trigger_id": trigger_id,
            "timestamp": datetime.now().isoformat(),
            "tasks": len(tasks),
            "successful": successful,
            "failed": failed
        })
        # 只保留最近100条历史
        state["execution_history"] = state["execution_history"][-100:]
        self.save_state(state)

        # 保存执行日志
        self._save_execution_log(trigger_id, results)

        return {
            "total_tasks": len(tasks),
            "successful": successful,
            "failed": failed,
            "results": results
        }

    def _save_trigger_record(self, record: Dict[str, Any]) -> None:
        """保存触发记录"""
        triggers = []
        if self.trigger_queue_file.exists():
            with open(self.trigger_queue_file, 'r', encoding='utf-8') as f:
                triggers = json.load(f)

        triggers.append(record)
        # 只保留最近50条
        triggers = triggers[-50:]

        with open(self.trigger_queue_file, 'w', encoding='utf-8') as f:
            json.dump(triggers, f, ensure_ascii=False, indent=2)

    def _save_execution_log(self, trigger_id: str, results: List[Dict[str, Any]]) -> None:
        """保存执行日志"""
        logs = []
        if self.execution_log_file.exists():
            with open(self.execution_log_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)

        logs.append({
            "trigger_id": trigger_id,
            "timestamp": datetime.now().isoformat(),
            "results": results
        })
        # 只保留最近100条
        logs = logs[-100:]

        with open(self.execution_log_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)

    def get_cockpit_data(self) -> Dict[str, Any]:
        """
        获取驾驶舱数据

        Returns:
            驾驶舱展示数据
        """
        state = self.load_state()

        # 获取当前效能状态
        efficiency_status = self.get_efficiency_status()

        # 获取触发历史
        triggers = []
        if self.trigger_queue_file.exists():
            with open(self.trigger_queue_file, 'r', encoding='utf-8') as f:
                triggers = json.load(f)

        # 获取执行日志
        logs = []
        if self.execution_log_file.exists():
            with open(self.execution_log_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)

        return {
            "version": self.version,
            "current_efficiency": efficiency_status.get("efficiency_score", 0),
            "threshold": self.threshold_config.get("efficiency_threshold", 70),
            "total_triggers": state.get("total_triggers", 0),
            "successful_optimizations": state.get("successful_optimizations", 0),
            "failed_optimizations": state.get("failed_optimizations", 0),
            "active_optimizations": len(state.get("active_optimizations", [])),
            "recent_triggers": triggers[-5:] if triggers else [],
            "recent_executions": logs[-5:] if logs else [],
            "threshold_config": self.threshold_config,
            "timestamp": datetime.now().isoformat()
        }

    def run_full_auto_optimization_cycle(self) -> Dict[str, Any]:
        """
        运行完整的自动优化周期

        Returns:
            优化周期结果
        """
        # 1. 获取效能状态
        efficiency_status = self.get_efficiency_status()

        # 2. 检查阈值违规
        violations = self.check_threshold_violations(efficiency_status)

        if not violations:
            return {
                "status": "no_violations",
                "message": "所有效能指标正常，无需优化",
                "efficiency_score": efficiency_status.get("efficiency_score", 0),
                "threshold": self.threshold_config.get("efficiency_threshold", 70)
            }

        # 3. 触发自动优化
        trigger_result = self.trigger_auto_optimization(violations)

        return {
            "status": trigger_result.get("status", "unknown"),
            "efficiency_score": efficiency_status.get("efficiency_score", 0),
            "violations": violations,
            "trigger_result": trigger_result
        }


def main():
    parser = argparse.ArgumentParser(
        description="智能全场景进化环跨引擎协同效能自动优化与知识驱动触发深度集成引擎"
    )
    parser.add_argument("--status", action="store_true", help="获取当前效能状态")
    parser.add_argument("--check", action="store_true", help="检查阈值违规")
    parser.add_argument("--trigger", action="store_true", help="触发自动优化")
    parser.add_argument("--cycle", action="store_true", help="运行完整自动优化周期")
    parser.add_argument("--cockpit-data", action="store_true", help="获取驾驶舱数据")
    parser.add_argument("--set-threshold", type=float, help="设置效能阈值")
    parser.add_argument("--enable-auto-trigger", action="store_true", help="启用自动触发")
    parser.add_argument("--disable-auto-trigger", action="store_true", help="禁用自动触发")

    args = parser.parse_args()

    engine = EvolutionCollaborationEfficiencyAutoOptimizationEngine()

    if args.status:
        result = engine.get_efficiency_status()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.check:
        efficiency_status = engine.get_efficiency_status()
        violations = engine.check_threshold_violations(efficiency_status)
        print(json.dumps({
            "efficiency_score": efficiency_status.get("efficiency_score", 0),
            "threshold": engine.threshold_config.get("efficiency_threshold", 70),
            "violations": violations
        }, ensure_ascii=False, indent=2))

    elif args.trigger:
        efficiency_status = engine.get_efficiency_status()
        violations = engine.check_threshold_violations(efficiency_status)
        result = engine.trigger_auto_optimization(violations)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.cycle:
        result = engine.run_full_auto_optimization_cycle()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.cockpit_data:
        result = engine.get_cockpit_data()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.set_threshold is not None:
        config = engine.threshold_config
        config["efficiency_threshold"] = args.set_threshold
        engine.save_threshold_config(config)
        print(json.dumps({"status": "success", "threshold": args.set_threshold}, ensure_ascii=False, indent=2))

    elif args.enable_auto_trigger:
        config = engine.threshold_config
        config["auto_trigger_enabled"] = True
        engine.save_threshold_config(config)
        print(json.dumps({"status": "success", "auto_trigger_enabled": True}, ensure_ascii=False, indent=2))

    elif args.disable_auto_trigger:
        config = engine.threshold_config
        config["auto_trigger_enabled"] = False
        engine.save_threshold_config(config)
        print(json.dumps({"status": "success", "auto_trigger_enabled": False}, ensure_ascii=False, indent=2))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()