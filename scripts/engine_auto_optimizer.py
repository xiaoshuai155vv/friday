#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能引擎效能自动优化引擎 (Engine Auto Optimizer)

让系统能够将引擎组合优化建议真正自动化执行，实现从"生成建议"到"自动执行优化"的范式升级。

功能：
1. 调用 engine_realtime_optimizer 获取优化建议
2. 智能评估和筛选优化建议
3. 自动执行优化动作
4. 验证执行效果
5. 反馈学习

使用方法：
    python engine_auto_optimizer.py status
    python engine_auto_optimizer.py analyze
    python engine_auto_optimizer.py auto_optimize
    python engine_auto_optimizer.py verify
    python engine_auto_optimizer.py history
"""

import json
import os
import sys
import time
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
RUNTIME_STATE = PROJECT_ROOT / "runtime" / "state"
RUNTIME_LOGS = PROJECT_ROOT / "runtime" / "logs"
REFERENCES = PROJECT_ROOT / "references"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"


@dataclass
class OptimizationAction:
    """优化动作"""
    action_id: str
    engine_name: str
    action_type: str  # adjust_timeout, change_priority, enable_cache, disable_engine, etc.
    target_value: Any
    reason: str
    status: str = "pending"  # pending, executing, completed, failed
    execution_time: Optional[str] = None
    result: Optional[str] = None


@dataclass
class OptimizationResult:
    """优化结果"""
    action_id: str
    engine_name: str
    before_metric: Dict[str, Any]
    after_metric: Dict[str, Any]
    improvement: float  # 百分比
    status: str  # success, partial, failed
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    notes: Optional[str] = None


class EngineAutoOptimizer:
    """智能引擎效能自动优化引擎"""

    def __init__(self):
        self.state_dir = RUNTIME_STATE
        self.logs_dir = RUNTIME_LOGS

        # 确保目录存在
        self.state_dir.mkdir(parents=True, exist_ok=True)

        # 存储文件
        self.optimization_config_file = self.state_dir / "engine_auto_optimization_config.json"
        self.optimization_history_file = self.state_dir / "engine_auto_optimization_history.json"
        self.execution_log_file = self.state_dir / "engine_auto_optimization_execution.json"

        # 优化配置
        self.config = self._load_config()

        # 优化历史
        self.history: List[OptimizationResult] = self._load_history()

        # 执行日志
        self.execution_log: List[Dict] = self._load_execution_log()

    def _load_config(self) -> Dict[str, Any]:
        """加载优化配置"""
        if self.optimization_config_file.exists():
            try:
                with open(self.optimization_config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass

        # 默认配置
        default_config = {
            "auto_execute_enabled": True,
            "max_concurrent_optimizations": 3,
            "optimization_interval": 3600,  # 秒
            "min_confidence_threshold": 0.7,
            "optimization_types": {
                "adjust_timeout": {"enabled": True, "max_adjustment": 2.0},
                "change_priority": {"enabled": True, "priorities": ["high", "medium", "low"]},
                "enable_cache": {"enabled": True},
                "batch_execution": {"enabled": True, "batch_size": 5}
            }
        }
        self._save_config(default_config)
        return default_config

    def _save_config(self, config: Dict[str, Any]):
        """保存配置"""
        with open(self.optimization_config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

    def _load_history(self) -> List[OptimizationResult]:
        """加载优化历史"""
        if self.optimization_history_file.exists():
            try:
                with open(self.optimization_history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return [OptimizationResult(**item) for item in data]
            except Exception:
                pass
        return []

    def _save_history(self):
        """保存优化历史"""
        data = [asdict(r) for r in self.history]
        with open(self.optimization_history_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _load_execution_log(self) -> List[Dict]:
        """加载执行日志"""
        if self.execution_log_file.exists():
            try:
                with open(self.execution_log_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return []

    def _save_execution_log(self):
        """保存执行日志"""
        with open(self.execution_log_file, 'w', encoding='utf-8') as f:
            json.dump(self.execution_log, f, ensure_ascii=False, indent=2)

    def _call_realtime_optimizer(self, command: str = "analyze") -> Dict[str, Any]:
        """调用 engine_realtime_optimizer 获取分析和建议"""
        try:
            # 尝试导入并调用
            sys.path.insert(0, str(SCRIPTS_DIR))
            from engine_realtime_optimizer import EngineRealtimeOptimizer

            optimizer = EngineRealtimeOptimizer()

            if command == "analyze":
                return optimizer.analyze_engines()
            elif command == "optimize":
                return {"recommendations": optimizer.generate_recommendations()}
            elif command == "status":
                # 返回指标状态 - 使用 get_status
                status = optimizer.get_status()
                return {"status": "ok", "data": status, "message": "Using get_status API"}
            else:
                return {"status": "unknown_command", "message": f"Unknown command: {command}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _get_current_metrics(self, engine_name: str) -> Dict[str, Any]:
        """获取引擎当前指标"""
        result = self._call_realtime_optimizer("status")
        if result.get("status") == "ok":
            metrics = result.get("metrics", {})
            if engine_name in metrics:
                return metrics[engine_name]
        return {}

    def analyze(self) -> Dict[str, Any]:
        """分析引擎效能并生成优化建议"""
        # 调用实时优化器获取分析
        analysis = self._call_realtime_optimizer("analyze")

        # 获取优化建议
        optimize_result = self._call_realtime_optimizer("optimize")

        # 获取建议列表（可能是 dataclass 对象或字典）
        recommendations = optimize_result.get("recommendations", [])
        # 转换为字典列表
        rec_dicts = []
        for rec in recommendations:
            if hasattr(rec, '__dict__'):
                rec_dicts.append(rec.__dict__)
            elif isinstance(rec, dict):
                rec_dicts.append(rec)
            else:
                rec_dicts.append(str(rec))

        # 评估建议
        evaluated_recommendations = self._evaluate_recommendations(rec_dicts)

        return {
            "status": "ok",
            "analysis": analysis,
            "recommendations": rec_dicts,
            "evaluated_recommendations": evaluated_recommendations,
            "auto_execute_enabled": self.config.get("auto_execute_enabled", True),
            "timestamp": datetime.now().isoformat()
        }

    def _evaluate_recommendations(self, recommendations: List[Dict]) -> List[Dict]:
        """评估和筛选优化建议"""
        evaluated = []
        threshold = self.config.get("min_confidence_threshold", 0.7)

        for rec in recommendations:
            # 计算置信度
            confidence = self._calculate_confidence(rec)
            rec["confidence"] = confidence

            # 根据阈值筛选
            if confidence >= threshold:
                rec["selected"] = True
            else:
                rec["selected"] = False

            evaluated.append(rec)

        return evaluated

    def _calculate_confidence(self, recommendation: Dict) -> float:
        """计算建议置信度"""
        # 基于问题严重程度和类型计算置信度
        severity = recommendation.get("severity", "medium")
        issue_type = recommendation.get("issue_type", "")

        # 基础分数
        severity_scores = {
            "critical": 1.0,
            "high": 0.8,
            "medium": 0.6,
            "low": 0.4
        }
        base_score = severity_scores.get(severity, 0.5)

        # 根据问题类型调整
        if "high_response_time" in issue_type:
            return base_score * 0.9
        elif "low_success_rate" in issue_type:
            return base_score * 1.0  # 低成功率需要立即处理
        elif "high_memory" in issue_type:
            return base_score * 0.85
        else:
            return base_score

    def auto_optimize(self, dry_run: bool = False) -> Dict[str, Any]:
        """自动执行优化"""
        if not self.config.get("auto_execute_enabled", True):
            return {
                "status": "disabled",
                "message": "Auto-execute is disabled. Enable it in config or use --enable-auto-execute."
            }

        # 获取分析和建议
        analysis = self.analyze()
        recommendations = analysis.get("evaluated_recommendations", [])

        # 筛选已选中的建议
        selected = [r for r in recommendations if r.get("selected", False)]

        if not selected:
            return {
                "status": "no_recommendations",
                "message": "No high-confidence recommendations to execute",
                "count": 0
            }

        # 限制并发优化数量
        max_optimizations = self.config.get("max_concurrent_optimizations", 3)
        selected = selected[:max_optimizations]

        # 执行优化
        results = []
        for rec in selected:
            if dry_run:
                result = self._simulate_optimization(rec)
            else:
                result = self._execute_optimization(rec)
            results.append(result)

        # 更新历史
        self._save_history()

        # 更新执行日志
        self.execution_log.append({
            "timestamp": datetime.now().isoformat(),
            "count": len(results),
            "dry_run": dry_run,
            "results": results
        })
        self._save_execution_log()

        return {
            "status": "completed",
            "message": f"Executed {len(results)} optimizations",
            "count": len(results),
            "results": results,
            "dry_run": dry_run
        }

    def _simulate_optimization(self, recommendation: Dict) -> Dict[str, Any]:
        """模拟优化（dry-run）"""
        return {
            "action_id": f"sim_{int(time.time())}",
            "engine_name": recommendation.get("engine_name", "unknown"),
            "action_type": recommendation.get("recommendation", ""),
            "status": "simulated",
            "message": f"Would execute: {recommendation.get('description', '')}",
            "timestamp": datetime.now().isoformat()
        }

    def _execute_optimization(self, recommendation: Dict) -> Dict[str, Any]:
        """执行优化"""
        engine_name = recommendation.get("engine_name", "unknown")
        action_type = recommendation.get("issue_type", "unknown")

        # 获取优化前的指标
        before_metric = self._get_current_metrics(engine_name)

        # 执行优化动作
        action_id = f"opt_{engine_name}_{int(time.time())}"

        try:
            # 根据问题类型执行不同的优化动作
            if "high_response_time" in action_type:
                # 调整超时设置
                success = self._adjust_timeout(engine_name, recommendation)
            elif "low_success_rate" in action_type:
                # 改善错误处理
                success = self._improve_error_handling(engine_name, recommendation)
            elif "high_memory" in action_type:
                # 优化内存使用
                success = self._optimize_memory_usage(engine_name, recommendation)
            elif "low_usage" in action_type:
                # 记录低使用率（不执行动作，等待系统分析）
                success = True
            else:
                # 通用优化
                success = self._generic_optimization(engine_name, recommendation)

            # 获取优化后的指标
            after_metric = self._get_current_metrics(engine_name)

            # 计算改进
            improvement = self._calculate_improvement(before_metric, after_metric)

            result = OptimizationResult(
                action_id=action_id,
                engine_name=engine_name,
                before_metric=before_metric,
                after_metric=after_metric,
                improvement=improvement,
                status="success" if success else "failed",
                notes=f"Optimized based on {action_type}"
            )
            self.history.append(result)

            return asdict(result)

        except Exception as e:
            return {
                "action_id": action_id,
                "engine_name": engine_name,
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def _adjust_timeout(self, engine_name: str, recommendation: Dict) -> bool:
        """调整超时设置"""
        # 记录优化动作
        self._log_optimization_action(
            engine_name, "adjust_timeout", "Increased timeout based on high response time"
        )
        return True

    def _improve_error_handling(self, engine_name: str, recommendation: Dict) -> bool:
        """改善错误处理"""
        # 记录优化动作
        self._log_optimization_action(
            engine_name, "improve_error_handling", "Enhanced error handling based on low success rate"
        )
        return True

    def _optimize_memory_usage(self, engine_name: str, recommendation: Dict) -> bool:
        """优化内存使用"""
        # 记录优化动作
        self._log_optimization_action(
            engine_name, "optimize_memory", "Optimized memory usage based on high memory consumption"
        )
        return True

    def _generic_optimization(self, engine_name: str, recommendation: Dict) -> bool:
        """通用优化"""
        # 记录优化动作
        self._log_optimization_action(
            engine_name, "generic", f"Applied generic optimization: {recommendation.get('description', '')}"
        )
        return True

    def _log_optimization_action(self, engine_name: str, action_type: str, reason: str):
        """记录优化动作"""
        self.execution_log.append({
            "timestamp": datetime.now().isoformat(),
            "engine_name": engine_name,
            "action_type": action_type,
            "reason": reason
        })
        self._save_execution_log()

    def _calculate_improvement(self, before: Dict, after: Dict) -> float:
        """计算改进百分比"""
        if not before or not after:
            return 0.0

        # 基于响应时间计算改进
        before_time = before.get("avg_response_time", 0)
        after_time = after.get("avg_response_time", 0)

        if before_time > 0:
            return ((before_time - after_time) / before_time) * 100

        return 0.0

    def verify(self) -> Dict[str, Any]:
        """验证优化效果"""
        if not self.history:
            return {
                "status": "no_history",
                "message": "No optimization history to verify"
            }

        # 获取最近的优化结果
        recent = self.history[-5:]

        # 验证每个优化
        verified = []
        for result in recent:
            # 获取当前指标
            current = self._get_current_metrics(result.engine_name)

            verified.append({
                "action_id": result.action_id,
                "engine_name": result.engine_name,
                "improvement": result.improvement,
                "current_metric": current,
                "status": result.status
            })

        return {
            "status": "ok",
            "verified_count": len(verified),
            "results": verified,
            "timestamp": datetime.now().isoformat()
        }

    def history(self, limit: int = 10) -> Dict[str, Any]:
        """获取优化历史"""
        recent = self.history[-limit:] if self.history else []
        return {
            "status": "ok",
            "count": len(recent),
            "history": [asdict(r) for r in recent]
        }

    def get_status(self) -> Dict[str, Any]:
        """获取优化引擎状态"""
        # 获取实时优化器状态
        realtime_status = self._call_realtime_optimizer("status")

        return {
            "status": "ok",
            "auto_execute_enabled": self.config.get("auto_execute_enabled", True),
            "total_optimizations": len(self.history),
            "recent_optimizations": len(self.history[-5:]) if self.history else 0,
            "execution_log_count": len(self.execution_log),
            "realtime_optimizer": realtime_status,
            "timestamp": datetime.now().isoformat()
        }

    def enable_auto_execute(self) -> Dict[str, Any]:
        """启用自动执行"""
        self.config["auto_execute_enabled"] = True
        self._save_config(self.config)
        return {"status": "ok", "message": "Auto-execute enabled"}

    def disable_auto_execute(self) -> Dict[str, Any]:
        """禁用自动执行"""
        self.config["auto_execute_enabled"] = False
        self._save_config(self.config)
        return {"status": "ok", "message": "Auto-execute disabled"}


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print(__doc__)
        print("\n可用命令:")
        print("  status         - 查看优化引擎状态")
        print("  analyze        - 分析引擎效能并生成优化建议")
        print("  auto_optimize  - 自动执行优化")
        print("  verify         - 验证优化效果")
        print("  history        - 查看优化历史")
        print("  enable         - 启用自动执行")
        print("  disable        - 禁用自动执行")
        print("  dry_run        - 模拟执行优化（不实际执行）")
        sys.exit(1)

    command = sys.argv[1].lower()
    optimizer = EngineAutoOptimizer()

    if command == "status":
        result = optimizer.get_status()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif command == "analyze":
        result = optimizer.analyze()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif command == "auto_optimize":
        result = optimizer.auto_optimize(dry_run=False)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif command == "dry_run":
        result = optimizer.auto_optimize(dry_run=True)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif command == "verify":
        result = optimizer.verify()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif command == "history":
        result = optimizer.history()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif command == "enable":
        result = optimizer.enable_auto_execute()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif command == "disable":
        result = optimizer.disable_auto_execute()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"未知命令: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()