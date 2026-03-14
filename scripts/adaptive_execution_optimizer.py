#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景执行自适应优化引擎 (Adaptive Execution Optimizer)

让系统能够实时分析执行效果、自动调整执行参数、优化执行路径，实现真正的自适应执行闭环。

功能：
1. 实时执行效果分析（分析执行时间、成功率、资源使用）
2. 自动执行参数调优（超时、重试、并发数、引擎选择）
3. 执行路径优化（发现更高效的执行方式）
4. 自适应学习（从历史执行中学习最佳策略）
5. 闭环反馈（将优化结果应用到后续执行）

使用方法：
    python adaptive_execution_optimizer.py analyze
    python adaptive_execution_optimizer.py optimize
    python adaptive_execution_optimizer.py status
    python adaptive_execution_optimizer.py apply
"""

import json
import os
import sys
import time
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from collections import defaultdict

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
RUNTIME_STATE = PROJECT_ROOT / "runtime" / "state"
RUNTIME_LOGS = PROJECT_ROOT / "runtime" / "logs"
REFERENCES = PROJECT_ROOT / "references"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"


@dataclass
class ExecutionRecord:
    """执行记录"""
    record_id: str
    task_type: str  # run_plan, workflow, scenario, etc.
    start_time: str
    end_time: Optional[str] = None
    duration: Optional[float] = None  # 秒
    status: str = "running"  # running, success, failed, timeout
    engine_used: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@dataclass
class OptimizationSuggestion:
    """优化建议"""
    suggestion_id: str
    task_type: str
    parameter_name: str
    current_value: Any
    suggested_value: Any
    reason: str
    expected_improvement: float  # 预期改善百分比
    confidence: float  # 置信度 0-1
    status: str = "pending"  # pending, applied, rejected
    applied_at: Optional[str] = None


class AdaptiveExecutionOptimizer:
    """智能全场景执行自适应优化引擎"""

    def __init__(self):
        self.state_dir = RUNTIME_STATE
        self.logs_dir = RUNTIME_LOGS

        # 确保目录存在
        self.state_dir.mkdir(parents=True, exist_ok=True)

        # 存储文件
        self.execution_records_file = self.state_dir / "adaptive_execution_records.json"
        self.optimization_suggestions_file = self.state_dir / "adaptive_execution_suggestions.json"
        self.optimization_config_file = self.state_dir / "adaptive_execution_config.json"

        # 执行记录
        self.execution_records: List[ExecutionRecord] = self._load_records()

        # 优化建议
        self.suggestions: List[OptimizationSuggestion] = self._load_suggestions()

        # 配置
        self.config = self._load_config()

    def _load_records(self) -> List[ExecutionRecord]:
        """加载执行记录"""
        if self.execution_records_file.exists():
            try:
                with open(self.execution_records_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return [ExecutionRecord(**r) for r in data]
            except Exception:
                pass
        return []

    def _save_records(self):
        """保存执行记录"""
        try:
            with open(self.execution_records_file, 'w', encoding='utf-8') as f:
                json.dump([asdict(r) for r in self.execution_records[-1000:]], f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存执行记录失败: {e}")

    def _load_suggestions(self) -> List[OptimizationSuggestion]:
        """加载优化建议"""
        if self.optimization_suggestions_file.exists():
            try:
                with open(self.optimization_suggestions_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return [OptimizationSuggestion(**s) for s in data]
            except Exception:
                pass
        return []

    def _save_suggestions(self):
        """保存优化建议"""
        try:
            with open(self.optimization_suggestions_file, 'w', encoding='utf-8') as f:
                json.dump([asdict(s) for s in self.suggestions[-100:]], f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存优化建议失败: {e}")

    def _load_config(self) -> Dict[str, Any]:
        """加载配置"""
        if self.optimization_config_file.exists():
            try:
                with open(self.optimization_config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass

        # 默认配置
        return {
            "enabled": True,
            "auto_apply": False,
            "min_samples_for_optimization": 5,  # 最少样本数才开始优化
            "max_history_size": 1000,
            "parameters": {
                "timeout": {
                    "default": 30,
                    "min": 5,
                    "max": 300,
                    "adjustment_factor": 0.8  # 成功执行的时间 * factor 作为超时
                },
                "retry": {
                    "default": 3,
                    "min": 0,
                    "max": 10
                },
                "concurrency": {
                    "default": 1,
                    "min": 1,
                    "max": 10
                }
            },
            "task_type_overrides": {}  # 特定任务类型的配置
        }

    def _save_config(self):
        """保存配置"""
        try:
            with open(self.optimization_config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存配置失败: {e}")

    def record_execution(self, task_type: str, engine_used: str, parameters: Dict[str, Any],
                        status: str = "success", result: Optional[Dict] = None,
                        error: Optional[str] = None, duration: Optional[float] = None):
        """记录执行结果"""
        record = ExecutionRecord(
            record_id=f"exec_{int(time.time() * 1000)}",
            task_type=task_type,
            start_time=datetime.now().isoformat(),
            end_time=datetime.now().isoformat() if status != "running" else None,
            duration=duration,
            status=status,
            engine_used=engine_used,
            parameters=parameters,
            result=result,
            error=error
        )
        self.execution_records.append(record)
        self._save_records()

        # 分析并生成优化建议
        self._analyze_and_suggest(record)

    def _analyze_and_suggest(self, record: ExecutionRecord):
        """分析执行记录并生成优化建议"""
        # 收集同类任务的历史记录
        task_records = [r for r in self.execution_records if r.task_type == record.task_type]

        if len(task_records) < self.config.get("min_samples_for_optimization", 5):
            return

        # 分析超时参数
        self._analyze_timeout(task_records)

        # 分析重试参数
        self._analyze_retry(task_records)

    def _analyze_timeout(self, records: List[ExecutionRecord]):
        """分析超时参数"""
        successful_records = [r for r in records if r.status == "success" and r.duration is not None]

        if not successful_records:
            return

        # 计算平均成功执行时间
        avg_duration = sum(r.duration for r in successful_records) / len(successful_records)

        # 计算最大成功执行时间
        max_duration = max(r.duration for r in successful_records)

        # 建议超时时间 = 最大成功时间 * factor
        suggested_timeout = int(max_duration * self.config["parameters"]["timeout"]["adjustment_factor"])
        suggested_timeout = max(
            self.config["parameters"]["timeout"]["min"],
            min(suggested_timeout, self.config["parameters"]["timeout"]["max"])
        )

        # 检查是否已有类似建议
        task_type = records[0].task_type
        existing = [s for s in self.suggestions if s.task_type == task_type and s.parameter_name == "timeout"]

        if not existing or existing[0].suggested_value != suggested_timeout:
            suggestion = OptimizationSuggestion(
                suggestion_id=f"suggest_{int(time.time() * 1000)}",
                task_type=task_type,
                parameter_name="timeout",
                current_value=self.config["parameters"]["timeout"]["default"],
                suggested_value=suggested_timeout,
                reason=f"基于 {len(successful_records)} 次成功执行分析，平均执行时间 {avg_duration:.2f}秒，最大 {max_duration:.2f}秒",
                expected_improvement=10.0,
                confidence=0.8
            )
            self.suggestions.append(suggestion)
            self._save_suggestions()

    def _analyze_retry(self, records: List[ExecutionRecord]):
        """分析重试参数"""
        failed_with_retry = [r for r in records if r.status == "failed" and r.parameters.get("retry", 0) > 0]
        failed_without_retry = [r for r in records if r.status == "failed" and r.parameters.get("retry", 0) == 0]

        # 如果有重试但仍失败，可能是重试次数不够
        if failed_with_retry and len(records) >= 10:
            current_retry = self.config["parameters"]["retry"]["default"]
            suggested_retry = min(current_retry + 1, self.config["parameters"]["retry"]["max"])

            task_type = records[0].task_type
            existing = [s for s in self.suggestions if s.task_type == task_type and s.parameter_name == "retry"]

            if not existing:
                suggestion = OptimizationSuggestion(
                    suggestion_id=f"suggest_{int(time.time() * 1000)}",
                    task_type=task_type,
                    parameter_name="retry",
                    current_value=current_retry,
                    suggested_value=suggested_retry,
                    reason=f"检测到 {len(failed_with_retry)} 次失败后重试仍然失败，建议增加重试次数",
                    expected_improvement=5.0,
                    confidence=0.6
                )
                self.suggestions.append(suggestion)
                self._save_suggestions()

    def analyze(self) -> Dict[str, Any]:
        """分析执行效果并生成报告"""
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "total_records": len(self.execution_records),
            "task_types": {},
            "overall_stats": {
                "success_rate": 0.0,
                "avg_duration": 0.0,
                "total_duration": 0.0
            },
            "optimization_opportunities": []
        }

        if not self.execution_records:
            return analysis

        # 按任务类型统计
        task_stats = defaultdict(lambda: {"total": 0, "success": 0, "failed": 0, "timeout": 0, "durations": []})

        for record in self.execution_records:
            task_stats[record.task_type]["total"] += 1
            if record.status == "success":
                task_stats[record.task_type]["success"] += 1
            elif record.status == "failed":
                task_stats[record.task_type]["failed"] += 1
            elif record.status == "timeout":
                task_stats[record.task_type]["timeout"] += 1

            if record.duration:
                task_stats[record.task_type]["durations"].append(record.duration)

        # 计算统计数据
        total_success = sum(s["success"] for s in task_stats.values())
        total_failed = sum(s["failed"] for s in task_stats.values())
        total_timeout = sum(s["timeout"] for s in task_stats.values())

        analysis["overall_stats"]["success_rate"] = total_success / len(self.execution_records) if self.execution_records else 0
        analysis["overall_stats"]["total_duration"] = sum(
            sum(s["durations"]) for s in task_stats.values()
        )

        for task_type, stats in task_stats.items():
            if stats["durations"]:
                avg_dur = sum(stats["durations"]) / len(stats["durations"])
            else:
                avg_dur = 0

            analysis["task_types"][task_type] = {
                "total": stats["total"],
                "success": stats["success"],
                "failed": stats["failed"],
                "timeout": stats["timeout"],
                "success_rate": stats["success"] / stats["total"] if stats["total"] > 0 else 0,
                "avg_duration": avg_dur
            }

        # 识别优化机会
        for task_type, stats in task_stats.items():
            if stats["failed"] > 0:
                analysis["optimization_opportunities"].append({
                    "task_type": task_type,
                    "issue": "存在失败记录",
                    "suggestion": "增加错误处理和重试机制"
                })

            if stats["timeout"] > 0:
                analysis["optimization_opportunities"].append({
                    "task_type": task_type,
                    "issue": "存在超时",
                    "suggestion": "增加超时时间或优化执行逻辑"
                })

        return analysis

    def get_suggestions(self, task_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """获取优化建议"""
        suggestions = self.suggestions

        if task_type:
            suggestions = [s for s in suggestions if s.task_type == task_type]

        # 只返回待应用的建议
        pending = [s for s in suggestions if s.status == "pending"]

        return [
            {
                "suggestion_id": s.suggestion_id,
                "task_type": s.task_type,
                "parameter_name": s.parameter_name,
                "current_value": s.current_value,
                "suggested_value": s.suggested_value,
                "reason": s.reason,
                "expected_improvement": s.expected_improvement,
                "confidence": s.confidence
            }
            for s in pending
        ]

    def apply_suggestion(self, suggestion_id: str) -> bool:
        """应用优化建议"""
        for suggestion in self.suggestions:
            if suggestion.suggestion_id == suggestion_id:
                # 更新配置
                task_type = suggestion.task_type
                param_name = suggestion.parameter_name

                if task_type not in self.config["task_type_overrides"]:
                    self.config["task_type_overrides"][task_type] = {}

                self.config["task_type_overrides"][task_type][param_name] = suggestion.suggested_value

                # 标记建议为已应用
                suggestion.status = "applied"
                suggestion.applied_at = datetime.now().isoformat()

                self._save_config()
                self._save_suggestions()

                return True

        return False

    def auto_optimize(self) -> Dict[str, Any]:
        """自动应用优化建议"""
        result = {
            "applied": [],
            "skipped": [],
            "failed": []
        }

        pending = [s for s in self.suggestions if s.status == "pending"]

        for suggestion in pending:
            # 只自动应用高置信度的建议
            if suggestion.confidence >= 0.7:
                if self.apply_suggestion(suggestion.suggestion_id):
                    result["applied"].append({
                        "suggestion_id": suggestion.suggestion_id,
                        "task_type": suggestion.task_type,
                        "parameter": suggestion.parameter_name,
                        "new_value": suggestion.suggested_value
                    })
                else:
                    result["failed"].append(suggestion.suggestion_id)
            else:
                result["skipped"].append(suggestion.suggestion_id)

        return result

    def get_optimized_parameters(self, task_type: str) -> Dict[str, Any]:
        """获取优化后的参数"""
        default_params = self.config["parameters"].copy()

        # 检查是否有任务类型特定的覆盖
        if task_type in self.config["task_type_overrides"]:
            default_params.update(self.config["task_type_overrides"][task_type])

        return default_params

    def status(self) -> Dict[str, Any]:
        """获取优化器状态"""
        return {
            "enabled": self.config["enabled"],
            "total_records": len(self.execution_records),
            "total_suggestions": len(self.suggestions),
            "pending_suggestions": len([s for s in self.suggestions if s.status == "pending"]),
            "applied_suggestions": len([s for s in self.suggestions if s.status == "applied"]),
            "task_types": list(set(r.task_type for r in self.execution_records))
        }


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    command = sys.argv[1].lower()
    optimizer = AdaptiveExecutionOptimizer()

    if command == "analyze":
        result = optimizer.analyze()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "optimize" or command == "auto_optimize":
        result = optimizer.auto_optimize()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "status":
        result = optimizer.status()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "suggestions":
        task_type = sys.argv[2] if len(sys.argv) > 2 else None
        result = optimizer.get_suggestions(task_type)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "apply":
        if len(sys.argv) > 2:
            suggestion_id = sys.argv[2]
            success = optimizer.apply_suggestion(suggestion_id)
            print(f"应用建议: {'成功' if success else '失败'}")
        else:
            print("用法: python adaptive_execution_optimizer.py apply <suggestion_id>")

    elif command == "params":
        if len(sys.argv) > 2:
            task_type = sys.argv[2]
            result = optimizer.get_optimized_parameters(task_type)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print("用法: python adaptive_execution_optimizer.py params <task_type>")

    else:
        print(f"未知命令: {command}")
        print(__doc__)


if __name__ == "__main__":
    main()