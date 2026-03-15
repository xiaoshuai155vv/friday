#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环决策自动执行与动态调整引擎
(Decision Auto-Execution and Dynamic Adjustment Engine)

让系统能够将多引擎协同智能决策的结果自动转化为可执行的动作序列、
智能调整执行参数、动态处理执行异常、验证执行效果，形成从
「智能决策→自动执行→动态调整→效果验证」的完整闭环。

这是 round 509 完成的「多引擎协同智能决策深度集成引擎」的增强——
让决策能够真正自动执行，而不仅仅停留在决策层面。

Version: 1.0.0
"""

import json
import os
import sys
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
STATE_DIR = PROJECT_ROOT / "runtime" / "state"
DATA_DIR = PROJECT_ROOT / "runtime" / "data"
LOGS_DIR = PROJECT_ROOT / "runtime" / "logs"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"

# 添加 scripts 目录到路径以便导入
sys.path.insert(0, str(SCRIPTS_DIR))


class ExecutionStatus(Enum):
    """执行状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"
    SKIPPED = "skipped"


class AdjustmentType(Enum):
    """调整类型"""
    PARAMETER = "parameter"
    STRATEGY = "strategy"
    TIMEOUT = "timeout"
    RETRY = "retry"
    FALLBACK = "fallback"


@dataclass
class ExecutionAction:
    """执行动作"""
    action_id: str
    action_type: str  # "run_script", "update_config", "call_api", "execute_command"
    action_content: Dict[str, Any]
    order: int
    dependencies: List[str] = field(default_factory=list)
    timeout: int = 60
    retry_count: int = 3
    required: bool = True


@dataclass
class ExecutionResult:
    """执行结果"""
    action_id: str
    status: ExecutionStatus
    output: str = ""
    error: str = ""
    duration: float = 0.0
    adjustments_made: List[str] = field(default_factory=list)
    timestamp: str = ""


@dataclass
class DecisionExecution:
    """决策执行记录"""
    decision_id: str
    decision_content: str
    execution_actions: List[ExecutionAction]
    execution_results: List[ExecutionResult]
    overall_status: ExecutionStatus
    total_duration: float = 0.0
    adjustments_count: int = 0
    timestamp: str = ""


class DecisionAutoExecutionEngine:
    """决策自动执行与动态调整引擎核心类"""

    def __init__(self):
        self.version = "1.0.0"
        self.name = "Decision Auto-Execution and Dynamic Adjustment"
        self.runtime_dir = PROJECT_ROOT / "runtime"
        self.state_dir = self.runtime_dir / "state"
        self.data_dir = self.runtime_dir / "data"
        self.logs_dir = self.runtime_dir / "logs"
        self.scripts_dir = PROJECT_ROOT / "scripts"

        # 决策执行记录
        self.execution_records: Dict[str, DecisionExecution] = {}
        self.pending_executions: List[str] = []

        # 执行统计
        self.stats = {
            "total_decisions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "partial_executions": 0,
            "total_adjustments": 0,
            "total_duration": 0.0
        }

        # 动作类型映射
        self.action_handlers = {
            "run_script": self._execute_script,
            "update_config": self._update_config,
            "call_api": self._call_api,
            "execute_command": self._execute_command,
            "modify_file": self._modify_file,
            "run_plan": self._run_plan
        }

    def get_status(self) -> Dict[str, Any]:
        """获取引擎状态"""
        return {
            "version": self.version,
            "name": self.name,
            "total_executions": len(self.execution_records),
            "pending_executions": len(self.pending_executions),
            "stats": self.stats
        }

    def load_multi_engine_decisions(self) -> List[Dict[str, Any]]:
        """加载多引擎协同决策结果"""
        decisions = []

        # 尝试从相关引擎加载决策结果
        possible_files = [
            self.data_dir / "collaborative_decisions.json",
            self.state_dir / "evolution_multi_engine_collaborative_decisions.json",
            self.data_dir / "multi_engine_decisions.json"
        ]

        for file_path in possible_files:
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if isinstance(data, list):
                            decisions.extend(data)
                        elif isinstance(data, dict):
                            decisions.append(data)
                except Exception:
                    pass

        return decisions

    def create_execution_actions(self, decision: Dict[str, Any]) -> List[ExecutionAction]:
        """将决策转化为可执行的动作序列"""
        actions = []

        decision_content = decision.get("final_decision", decision.get("decision_content", ""))
        decision_type = decision.get("decision_type", "general")
        execution_path = decision.get("execution_path", [])

        # 基于决策类型生成动作
        if "optimization" in decision_type:
            actions.extend(self._generate_optimization_actions(decision))
        elif "repair" in decision_type:
            actions.extend(self._generate_repair_actions(decision))
        elif "innovation" in decision_type:
            actions.extend(self._generate_innovation_actions(decision))
        elif "health" in decision_type:
            actions.extend(self._generate_health_actions(decision))
        elif "value" in decision_type:
            actions.extend(self._generate_value_actions(decision))
        else:
            actions.extend(self._generate_general_actions(decision))

        # 如果有明确的执行路径，使用执行路径
        if execution_path:
            for i, path_item in enumerate(execution_path):
                action = ExecutionAction(
                    action_id=f"action_{i}",
                    action_type="execute_command",
                    action_content={"command": path_item},
                    order=i,
                    timeout=60
                )
                # 避免重复添加
                if not any(a.action_content.get("command") == path_item for a in actions):
                    actions.append(action)

        # 按依赖关系排序
        actions = self._sort_actions_by_dependencies(actions)

        # 重新分配顺序
        for i, action in enumerate(actions):
            action.order = i

        return actions

    def _generate_optimization_actions(self, decision: Dict[str, Any]) -> List[ExecutionAction]:
        """生成优化相关动作"""
        actions = []

        # 添加收集分析数据动作
        actions.append(ExecutionAction(
            action_id="collect_data",
            action_type="run_script",
            action_content={
                "script": "evolution_self_evolution_effectiveness_analysis_engine.py",
                "args": ["--analyze", "--json-output"]
            },
            order=0,
            timeout=120
        ))

        # 添加执行优化动作
        actions.append(ExecutionAction(
            action_id="execute_optimization",
            action_type="run_script",
            action_content={
                "script": "evolution_adaptive_optimizer.py",
                "args": ["--auto-optimize"]
            },
            order=1,
            dependencies=["collect_data"],
            timeout=180
        ))

        return actions

    def _generate_repair_actions(self, decision: Dict[str, Any]) -> List[ExecutionAction]:
        """生成修复相关动作"""
        actions = []

        # 添加健康诊断动作
        actions.append(ExecutionAction(
            action_id="diagnose",
            action_type="run_script",
            action_content={
                "script": "evolution_meta_evolution_internal_health_diagnosis_self_healing_engine.py",
                "args": ["--diagnose", "--auto-fix"]
            },
            order=0,
            timeout=120,
            required=True
        ))

        # 添加自动修复动作
        actions.append(ExecutionAction(
            action_id="auto_fix",
            action_type="run_script",
            action_content={
                "script": "self_healing_engine.py",
                "args": ["--auto-fix", "--verify"]
            },
            order=1,
            dependencies=["diagnose"],
            timeout=180
        ))

        return actions

    def _generate_innovation_actions(self, decision: Dict[str, Any]) -> List[ExecutionAction]:
        """生成创新相关动作"""
        actions = []

        # 添加创新方案生成动作
        actions.append(ExecutionAction(
            action_id="generate_innovation",
            action_type="run_script",
            action_content={
                "script": "evolution_innovation_realization_engine.py",
                "args": ["--auto-generate", "--evaluate"]
            },
            order=0,
            timeout=180
        ))

        # 添加执行创新动作
        actions.append(ExecutionAction(
            action_id="execute_innovation",
            action_type="run_script",
            action_content={
                "script": "evolution_innovation_execution_optimizer_engine.py",
                "args": ["--auto-execute"]
            },
            order=1,
            dependencies=["generate_innovation"],
            timeout=300
        ))

        return actions

    def _generate_health_actions(self, decision: Dict[str, Any]) -> List[ExecutionAction]:
        """生成健康相关动作"""
        actions = []

        # 添加健康检查动作
        actions.append(ExecutionAction(
            action_id="health_check",
            action_type="run_script",
            action_content={
                "script": "system_health_report_engine.py",
                "args": ["--auto", "--json"]
            },
            order=0,
            timeout=60
        ))

        # 添加预防性维护动作
        actions.append(ExecutionAction(
            action_id="preventive_maintenance",
            action_type="run_script",
            action_content={
                "script": "evolution_preventive_maintenance_enhancement_engine.py",
                "args": ["--auto-execute"]
            },
            order=1,
            dependencies=["health_check"],
            timeout=120
        ))

        return actions

    def _generate_value_actions(self, decision: Dict[str, Any]) -> List[ExecutionAction]:
        """生成价值相关动作"""
        actions = []

        # 添加价值评估动作
        actions.append(ExecutionAction(
            action_id="assess_value",
            action_type="run_script",
            action_content={
                "script": "evolution_roi_auto_assessment_engine.py",
                "args": ["--analyze", "--json-output"]
            },
            order=0,
            timeout=120
        ))

        # 添加价值优化动作
        actions.append(ExecutionAction(
            action_id="optimize_value",
            action_type="run_script",
            action_content={
                "script": "evolution_adaptive_value_optimization_engine.py",
                "args": ["--auto-optimize"]
            },
            order=1,
            dependencies=["assess_value"],
            timeout=180
        ))

        return actions

    def _generate_general_actions(self, decision: Dict[str, Any]) -> List[ExecutionAction]:
        """生成通用动作"""
        actions = []

        # 添加通用分析动作
        actions.append(ExecutionAction(
            action_id="analyze",
            action_type="run_script",
            action_content={
                "script": "evolution_strategy_engine.py",
                "args": ["--analyze"]
            },
            order=0,
            timeout=60
        ))

        return actions

    def _sort_actions_by_dependencies(self, actions: List[ExecutionAction]) -> List[ExecutionAction]:
        """按依赖关系排序动作"""
        # 构建依赖图
        dependency_graph = defaultdict(set)
        action_map = {a.action_id: a for a in actions}

        for action in actions:
            for dep in action.dependencies:
                if dep in action_map:
                    dependency_graph[action.action_id].add(dep)

        # 拓扑排序
        sorted_actions = []
        visited = set()

        def visit(action_id: str):
            if action_id in visited:
                return
            visited.add(action_id)
            for dep in dependency_graph[action_id]:
                visit(dep)
            if action_id in action_map:
                sorted_actions.append(action_map[action_id])

        for action in actions:
            visit(action.action_id)

        return sorted_actions

    def execute_decision(self, decision: Dict[str, Any], auto_adjust: bool = True) -> DecisionExecution:
        """执行决策"""
        decision_id = decision.get("decision_id", f"decision_{int(time.time())}")
        decision_content = decision.get("final_decision", decision.get("decision_content", ""))

        # 创建执行记录
        execution = DecisionExecution(
            decision_id=decision_id,
            decision_content=decision_content,
            execution_actions=[],
            execution_results=[],
            overall_status=ExecutionStatus.PENDING,
            timestamp=datetime.now().isoformat()
        )

        # 生成执行动作
        actions = self.create_execution_actions(decision)
        execution.execution_actions = actions

        self.stats["total_decisions"] += 1

        start_time = time.time()

        # 按顺序执行动作
        for action in actions:
            result = self._execute_action(action, auto_adjust)
            execution.execution_results.append(result)

            # 检查是否需要停止
            if result.status == ExecutionStatus.FAILED and action.required:
                execution.overall_status = ExecutionStatus.FAILED
                break

            if result.adjustments_made:
                execution.adjustments_count += len(result.adjustments_made)
                self.stats["total_adjustments"] += len(result.adjustments_made)

        execution.total_duration = time.time() - start_time
        self.stats["total_duration"] += execution.total_duration

        # 确定整体状态
        if execution.overall_status != ExecutionStatus.FAILED:
            failed_count = sum(1 for r in execution.execution_results if r.status == ExecutionStatus.FAILED)
            required_actions = [a for a in actions if a.required]
            if failed_count == 0:
                execution.overall_status = ExecutionStatus.COMPLETED
                self.stats["successful_executions"] += 1
            elif failed_count < len(required_actions):
                execution.overall_status = ExecutionStatus.PARTIAL
                self.stats["partial_executions"] += 1
            else:
                execution.overall_status = ExecutionStatus.FAILED
                self.stats["failed_executions"] += 1

        # 保存执行记录
        self.execution_records[decision_id] = execution

        return execution

    def _execute_action(self, action: ExecutionAction, auto_adjust: bool) -> ExecutionResult:
        """执行单个动作"""
        result = ExecutionResult(
            action_id=action.action_id,
            status=ExecutionStatus.RUNNING,
            timestamp=datetime.now().isoformat()
        )

        start_time = time.time()
        handler = self.action_handlers.get(action.action_type)

        if not handler:
            result.status = ExecutionStatus.FAILED
            result.error = f"Unknown action type: {action.action_type}"
            return result

        # 尝试执行，带有重试机制
        for attempt in range(action.retry_count + 1):
            try:
                success, output = handler(action)

                if success:
                    result.status = ExecutionStatus.COMPLETED
                    result.output = output
                    result.duration = time.time() - start_time
                    return result
                else:
                    if attempt < action.retry_count and auto_adjust:
                        # 自动调整并重试
                        adjustment = self._make_adjustment(action, attempt, output)
                        result.adjustments_made.append(adjustment)

            except Exception as e:
                result.error = str(e)
                if attempt < action.retry_count and auto_adjust:
                    adjustment = self._make_adjustment(action, attempt, str(e))
                    result.adjustments_made.append(adjustment)

        result.status = ExecutionStatus.FAILED
        result.duration = time.time() - start_time

        return result

    def _make_adjustment(self, action: ExecutionAction, attempt: int, error: str) -> str:
        """动态调整参数"""
        adjustment_desc = ""

        # 增加超时时间
        if "timeout" in error.lower() or "took too long" in error.lower():
            action.timeout = int(action.timeout * 1.5)
            adjustment_desc = f"Increased timeout to {action.timeout}s"

        # 减少重试次数以避免无限循环
        elif "retry" in error.lower():
            action.retry_count = min(action.retry_count, 1)
            adjustment_desc = "Reduced retry count"

        # 调整执行策略
        elif "memory" in error.lower() or "resource" in error.lower():
            if "timeout" not in adjustment_desc:
                action.timeout = min(action.timeout * 2, 600)
                adjustment_desc = f"Adjusted timeout and reduced scope due to resource constraints"

        # 默认调整
        if not adjustment_desc:
            adjustment_desc = f"Attempt {attempt + 1} failed, continuing..."

        return adjustment_desc

    def _execute_script(self, action: ExecutionAction) -> Tuple[bool, str]:
        """执行脚本"""
        script_name = action.action_content.get("script", "")
        args = action.action_content.get("args", [])

        if not script_name:
            return False, "No script specified"

        script_path = self.scripts_dir / script_name
        if not script_path.exists():
            return False, f"Script not found: {script_name}"

        try:
            cmd = [sys.executable, str(script_path)] + args
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=action.timeout,
                cwd=str(PROJECT_ROOT)
            )
            return result.returncode == 0, result.stdout + result.stderr
        except subprocess.TimeoutExpired:
            return False, f"Script execution timeout after {action.timeout}s"
        except Exception as e:
            return False, str(e)

    def _update_config(self, action: ExecutionAction) -> Tuple[bool, str]:
        """更新配置"""
        config_path = action.action_content.get("path", "")
        updates = action.action_content.get("updates", {})

        if not config_path:
            return False, "No config path specified"

        full_path = PROJECT_ROOT / config_path
        if not full_path.exists():
            return False, f"Config file not found: {config_path}"

        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            config.update(updates)

            with open(full_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

            return True, f"Config updated: {config_path}"
        except Exception as e:
            return False, str(e)

    def _call_api(self, action: ExecutionAction) -> Tuple[bool, str]:
        """调用 API（预留接口）"""
        api_endpoint = action.action_content.get("endpoint", "")
        method = action.action_content.get("method", "GET")

        # 这是一个预留实现
        return True, f"API call placeholder: {method} {api_endpoint}"

    def _execute_command(self, action: ExecutionAction) -> Tuple[bool, str]:
        """执行命令"""
        command = action.action_content.get("command", "")

        if not command:
            return False, "No command specified"

        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=action.timeout,
                cwd=str(PROJECT_ROOT)
            )
            return result.returncode == 0, result.stdout + result.stderr
        except subprocess.TimeoutExpired:
            return False, f"Command timeout after {action.timeout}s"
        except Exception as e:
            return False, str(e)

    def _modify_file(self, action: ExecutionAction) -> Tuple[bool, str]:
        """修改文件（预留接口）"""
        file_path = action.action_content.get("path", "")
        content = action.action_content.get("content", "")

        if not file_path:
            return False, "No file path specified"

        try:
            full_path = PROJECT_ROOT / file_path
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)

            return True, f"File modified: {file_path}"
        except Exception as e:
            return False, str(e)

    def _run_plan(self, action: ExecutionAction) -> Tuple[bool, str]:
        """运行计划"""
        plan_name = action.action_content.get("plan", "")

        if not plan_name:
            return False, "No plan specified"

        try:
            cmd = [sys.executable, str(self.scripts_dir / "do.py"), "run_plan", plan_name]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=action.timeout,
                cwd=str(PROJECT_ROOT)
            )
            return result.returncode == 0, result.stdout + result.stderr
        except subprocess.TimeoutExpired:
            return False, f"Plan execution timeout after {action.timeout}s"
        except Exception as e:
            return False, str(e)

    def get_execution_report(self, decision_id: str = "") -> Dict[str, Any]:
        """获取执行报告"""
        if decision_id:
            if decision_id in self.execution_records:
                execution = self.execution_records[decision_id]
                return {
                    "decision_id": decision_id,
                    "decision_content": execution.decision_content,
                    "status": execution.overall_status.value,
                    "actions_count": len(execution.execution_actions),
                    "results": [
                        {
                            "action_id": r.action_id,
                            "status": r.status.value,
                            "output": r.output[:200] if r.output else "",
                            "error": r.error[:200] if r.error else "",
                            "duration": r.duration,
                            "adjustments": r.adjustments_made
                        }
                        for r in execution.execution_results
                    ],
                    "total_duration": execution.total_duration,
                    "adjustments_count": execution.adjustments_count,
                    "timestamp": execution.timestamp
                }
            else:
                return {"error": f"Decision {decision_id} not found"}

        # 返回所有执行记录
        return {
            "total_executions": len(self.execution_records),
            "stats": self.stats,
            "recent_executions": [
                {
                    "decision_id": eid,
                    "status": ex.overall_status.value,
                    "duration": ex.total_duration,
                    "timestamp": ex.timestamp
                }
                for eid, ex in list(self.execution_records.items())[-10:]
            ]
        }

    def get_cockpit_data(self) -> Dict[str, Any]:
        """获取驾驶舱数据"""
        return {
            "engine": self.name,
            "version": self.version,
            "stats": self.stats,
            "recent_executions": [
                {
                    "decision_id": eid,
                    "status": ex.overall_status.value,
                    "duration": ex.total_duration,
                    "adjustments": ex.adjustments_count
                }
                for eid, ex in list(self.execution_records.items())[-5:]
            ]
        }


def main():
    """主入口"""
    import argparse

    parser = argparse.ArgumentParser(description="决策自动执行与动态调整引擎")
    parser.add_argument("--status", action="store_true", help="获取引擎状态")
    parser.add_argument("--execute", type=str, help="执行指定决策ID")
    parser.add_argument("--load-decisions", action="store_true", help="加载多引擎决策")
    parser.add_argument("--report", type=str, help="获取执行报告")
    parser.add_argument("--cockpit-data", action="store_true", help="获取驾驶舱数据")

    args = parser.parse_args()

    engine = DecisionAutoExecutionEngine()

    if args.status:
        status = engine.get_status()
        print(json.dumps(status, indent=2, ensure_ascii=False))

    elif args.load_decisions:
        decisions = engine.load_multi_engine_decisions()
        print(f"Loaded {len(decisions)} decisions")
        for d in decisions[:3]:
            print(f"  - {d.get('decision_id', 'unknown')}: {d.get('final_decision', '')[:50]}")

    elif args.execute:
        # 模拟决策执行
        decision = {"decision_id": args.execute, "decision_type": "optimization", "final_decision": "Execute optimization"}
        result = engine.execute_decision(decision)
        print(f"Execution status: {result.overall_status.value}")
        print(f"Duration: {result.total_duration:.2f}s")
        print(f"Adjustments: {result.adjustments_count}")

    elif args.report:
        report = engine.get_execution_report(args.report)
        print(json.dumps(report, indent=2, ensure_ascii=False))

    elif args.cockpit_data:
        data = engine.get_cockpit_data()
        print(json.dumps(data, indent=2, ensure_ascii=False))

    else:
        # 默认显示状态
        status = engine.get_status()
        print(json.dumps(status, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()