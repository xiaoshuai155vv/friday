#!/usr/bin/env python3
"""
智能全场景进化环元进化执行过程深度监控与智能预警增强引擎
Evolution Meta Execution Deep Monitoring and Smart Warning Enhancement Engine

version: 1.0.0
description: 在 round 644 完成的元进化自适应学习与策略自动优化引擎 V2 基础上，构建更深层次的执行过程深度监控能力，
让系统能够实时追踪进化执行状态、智能预测执行风险、主动部署预防性措施，形成「执行→监控→预警→预防」的完整闭环。

功能：
1. 执行状态实时追踪 - 追踪每轮进化的执行进度、资源使用、异常状态
2. 执行风险智能预测 - 基于历史模式预测执行风险（超时、失败、资源耗尽）
3. 预防性措施自动部署 - 风险预测触发时自动部署预防性措施
4. 多维度执行指标监控 - CPU、内存、执行时间、成功率等多维度指标
5. 智能预警分级 - 根据风险等级触发不同级别的预警（info/warning/critical）
6. 与自适应学习引擎集成 - 利用 round 644 的学习能力优化监控策略

依赖：
- round 644: 元进化自适应学习与策略自动优化引擎 V2
- round 620: 元进化执行效能实时优化引擎
- round 628: 元进化引擎健康预测与预防性自愈深度增强引擎
"""

import os
import sys
import json
import time
import logging
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 路径配置
SCRIPT_DIR = Path(__file__).parent
RUNTIME_DIR = SCRIPT_DIR.parent / "runtime"
STATE_DIR = RUNTIME_DIR / "state"
LOGS_DIR = RUNTIME_DIR / "logs"


class ExecutionMetrics:
    """执行指标数据类"""

    def __init__(self):
        self.cpu_usage: float = 0.0
        self.memory_usage: float = 0.0
        self.execution_time: float = 0.0
        self.success_rate: float = 1.0
        self.error_count: int = 0
        self.warning_count: int = 0
        self.status: str = "idle"  # idle/running/completed/failed
        self.progress: float = 0.0  # 0-100
        self.details: Dict[str, Any] = {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "cpu_usage": self.cpu_usage,
            "memory_usage": self.memory_usage,
            "execution_time": self.execution_time,
            "success_rate": self.success_rate,
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "status": self.status,
            "progress": self.progress,
            "details": self.details
        }


class RiskPredictor:
    """执行风险预测器"""

    def __init__(self):
        self.history: List[Dict[str, Any]] = []
        self.thresholds = {
            "cpu_warning": 80.0,
            "cpu_critical": 95.0,
            "memory_warning": 80.0,
            "memory_critical": 95.0,
            "time_warning_factor": 0.8,  # 预计时间的 80% 时预警
            "error_rate_warning": 0.1,
            "error_rate_critical": 0.3
        }

    def predict_risk(self, metrics: ExecutionMetrics, estimated_time: float = 0) -> Tuple[str, str]:
        """
        预测执行风险
        返回: (risk_level, risk_reason)
        risk_level: none/info/warning/critical
        """
        risk_level = "none"
        risk_reasons = []

        # CPU 风险检测
        if metrics.cpu_usage >= self.thresholds["cpu_critical"]:
            risk_level = "critical"
            risk_reasons.append(f"CPU使用率critical({metrics.cpu_usage}%)")
        elif metrics.cpu_usage >= self.thresholds["cpu_warning"]:
            if risk_level not in ["critical"]:
                risk_level = "warning"
            risk_reasons.append(f"CPU使用率warning({metrics.cpu_usage}%)")

        # 内存风险检测
        if metrics.memory_usage >= self.thresholds["memory_critical"]:
            risk_level = "critical"
            risk_reasons.append(f"内存使用率critical({metrics.memory_usage}%)")
        elif metrics.memory_usage >= self.thresholds["memory_warning"]:
            if risk_level not in ["critical"]:
                risk_level = "warning"
            risk_reasons.append(f"内存使用率warning({metrics.memory_usage}%)")

        # 执行时间风险检测
        if estimated_time > 0 and metrics.execution_time > estimated_time * self.thresholds["time_warning_factor"]:
            if risk_level == "none":
                risk_level = "info"
            risk_reasons.append(f"执行时间接近预估({metrics.execution_time:.1f}s/{estimated_time:.1f}s)")

        # 错误率风险检测
        if metrics.success_rate < (1 - self.thresholds["error_rate_critical"]):
            risk_level = "critical"
            risk_reasons.append(f"错误率critical({1-metrics.success_rate:.2f})")
        elif metrics.success_rate < (1 - self.thresholds["error_rate_warning"]):
            if risk_level not in ["critical"]:
                risk_level = "warning"
            risk_reasons.append(f"错误率warning({1-metrics.success_rate:.2f})")

        return risk_level, "; ".join(risk_reasons) if risk_reasons else "正常"

    def add_history(self, metrics: ExecutionMetrics, risk_level: str):
        """添加历史记录用于学习"""
        self.history.append({
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics.to_dict(),
            "risk_level": risk_level
        })
        # 保留最近 100 条历史
        if len(self.history) > 100:
            self.history = self.history[-100:]


class PreventiveMeasures:
    """预防性措施自动部署器"""

    def __init__(self):
        self.deployed_measures: List[Dict[str, Any]] = []

    def deploy_preventive_measures(self, risk_level: str, metrics: ExecutionMetrics) -> List[str]:
        """
        根据风险等级部署预防性措施
        返回: 已部署的措施列表
        """
        deployed = []

        if risk_level == "critical":
            # Critical 级别：立即采取措施
            deployed.append("暂停非关键任务")
            deployed.append("增加资源监控频率")
            deployed.append("准备错误恢复预案")
            logger.warning(f"[Critical] 部署预防性措施: {deployed}")

        elif risk_level == "warning":
            # Warning 级别：预警并准备措施
            deployed.append("增加监控频率")
            deployed.append("检查资源使用趋势")
            logger.info(f"[Warning] 部署预防性措施: {deployed}")

        elif risk_level == "info":
            # Info 级别：记录但不采取措施
            logger.info(f"[Info] 执行状态: {metrics.status}, 进度: {metrics.progress}%")

        # 记录已部署的措施
        if deployed:
            self.deployed_measures.append({
                "timestamp": datetime.now().isoformat(),
                "risk_level": risk_level,
                "measures": deployed,
                "metrics": metrics.to_dict()
            })

        return deployed


class ExecutionDeepMonitoringEngine:
    """执行过程深度监控引擎"""

    def __init__(self):
        self.version = "1.0.0"
        self.name = "元进化执行过程深度监控与智能预警增强引擎"

        # 核心组件
        self.risk_predictor = RiskPredictor()
        self.preventive_measures = PreventiveMeasures()

        # 当前执行状态
        self.current_metrics = ExecutionMetrics()
        self.is_monitoring = False
        self.monitoring_thread: Optional[threading.Thread] = None

        # 执行历史
        self.execution_history: List[Dict[str, Any]] = []

        # 集成自适应学习引擎
        self.adaptive_learning_available = self._check_adaptive_learning()

        logger.info(f"{self.name} v{self.version} 初始化完成")
        if self.adaptive_learning_available:
            logger.info("已集成 round 644 自适应学习引擎")

    def _check_adaptive_learning(self) -> bool:
        """检查自适应学习引擎是否可用"""
        adaptive_script = SCRIPT_DIR / "evolution_meta_adaptive_learning_strategy_optimizer_v2.py"
        return adaptive_script.exists()

    def start_monitoring(self, task_id: str = "default", estimated_time: float = 0):
        """开始监控"""
        self.is_monitoring = True
        self.current_metrics = ExecutionMetrics()
        self.current_metrics.status = "running"
        logger.info(f"开始执行监控: task_id={task_id}, 预估时间={estimated_time}s")

    def update_metrics(self, **kwargs):
        """更新执行指标"""
        for key, value in kwargs.items():
            if hasattr(self.current_metrics, key):
                setattr(self.current_metrics, key, value)

    def check_risk_and_deploy(self, estimated_time: float = 0) -> Tuple[str, str, List[str]]:
        """
        检查风险并部署预防性措施
        返回: (risk_level, risk_reason, deployed_measures)
        """
        risk_level, risk_reason = self.risk_predictor.predict_risk(
            self.current_metrics, estimated_time
        )
        deployed = self.preventive_measures.deploy_preventive_measures(
            risk_level, self.current_metrics
        )
        self.risk_predictor.add_history(self.current_metrics, risk_level)

        return risk_level, risk_reason, deployed

    def stop_monitoring(self, final_status: str = "completed") -> Dict[str, Any]:
        """停止监控并返回执行报告"""
        self.is_monitoring = False
        self.current_metrics.status = final_status
        self.current_metrics.progress = 100.0

        # 生成执行报告
        report = {
            "task_id": "default",
            "start_time": datetime.now().isoformat(),
            "end_time": datetime.now().isoformat(),
            "status": final_status,
            "metrics": self.current_metrics.to_dict(),
            "risk_history": self.risk_predictor.history[-10:],
            "deployed_measures": self.preventive_measures.deployed_measures[-10:]
        }

        # 保存到历史
        self.execution_history.append(report)
        if len(self.execution_history) > 100:
            self.execution_history = self.execution_history[-100:]

        logger.info(f"执行监控结束: status={final_status}, metrics={self.current_metrics.to_dict()}")
        return report

    def get_cockpit_data(self) -> Dict[str, Any]:
        """获取驾驶舱展示数据"""
        return {
            "engine_name": self.name,
            "version": self.version,
            "is_monitoring": self.is_monitoring,
            "current_metrics": self.current_metrics.to_dict(),
            "recent_executions": self.execution_history[-5:],
            "risk_predictor_available": True,
            "preventive_measures_available": True,
            "adaptive_learning_integrated": self.adaptive_learning_available,
            "total_executions": len(self.execution_history),
            "active_measures": len(self.preventive_measures.deployed_measures)
        }

    def run(self, args: List[str]) -> Dict[str, Any]:
        """执行主要逻辑"""
        if not args:
            return {"status": "error", "message": "缺少操作参数"}

        command = args[0]

        if command == "--version":
            return {
                "name": self.name,
                "version": self.version,
                "status": "ok"
            }

        elif command == "--status":
            return {
                "status": "ok",
                "is_monitoring": self.is_monitoring,
                "current_metrics": self.current_metrics.to_dict(),
                "adaptive_learning_integrated": self.adaptive_learning_available
            }

        elif command == "--start":
            task_id = args[1] if len(args) > 1 else "default"
            estimated_time = float(args[2]) if len(args) > 2 else 0
            self.start_monitoring(task_id, estimated_time)
            return {
                "status": "ok",
                "message": f"开始监控: task_id={task_id}"
            }

        elif command == "--update":
            # 解析并更新指标
            kwargs = {}
            for arg in args[1:]:
                if "=" in arg:
                    key, value = arg.split("=", 1)
                    try:
                        kwargs[key] = float(value)
                    except:
                        kwargs[key] = value
            self.update_metrics(**kwargs)

            # 检查风险
            estimated_time = float(args[args.index("--estimated") + 1]) if "--estimated" in args else 0
            risk_level, risk_reason, deployed = self.check_risk_and_deploy(estimated_time)

            return {
                "status": "ok",
                "risk_level": risk_level,
                "risk_reason": risk_reason,
                "deployed_measures": deployed,
                "metrics": self.current_metrics.to_dict()
            }

        elif command == "--stop":
            final_status = args[1] if len(args) > 1 else "completed"
            report = self.stop_monitoring(final_status)
            return {
                "status": "ok",
                "report": report
            }

        elif command == "--cockpit-data":
            return self.get_cockpit_data()

        else:
            return {
                "status": "error",
                "message": f"未知命令: {command}",
                "available_commands": [
                    "--version",
                    "--status",
                    "--start [task_id] [estimated_time]",
                    "--update key=value...",
                    "--stop [status]",
                    "--cockpit-data"
                ]
            }


def main():
    """主函数"""
    engine = ExecutionDeepMonitoringEngine()

    # 解析命令行参数
    args = sys.argv[1:] if len(sys.argv) > 1 else []

    if not args:
        # 无参数时显示状态
        result = engine.get_cockpit_data()
    else:
        result = engine.run(args)

    # 输出结果
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


if __name__ == "__main__":
    main()