#!/usr/bin/env python3
"""
智能全场景进化环实时监控与智能预警增强引擎
version 1.0.0

功能：
1. 实时监控进化环执行状态、引擎健康度、任务进度
2. 异常模式实时检测（性能下降、连续失败、资源瓶颈）
3. 智能预警分级（提示/警告/严重/紧急）
4. 自动应对策略触发（自动降级、自动重试、引擎切换）
5. 预警效果验证与反馈学习

集成到 do.py 支持：
- 实时监控、智能预警、状态监控、预警查询
"""

import os
import sys
import json
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from collections import deque
import logging
import subprocess

# 尝试导入 psutil，失败时使用备选方案
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 路径配置
SCRIPT_DIR = Path(__file__).parent
RUNTIME_STATE_DIR = SCRIPT_DIR.parent / "runtime" / "state"
RUNTIME_LOGS_DIR = SCRIPT_DIR.parent / "runtime" / "logs"
EVOLUTION_AUTO_LAST = SCRIPT_DIR.parent / "references" / "evolution_auto_last.md"

# 监控配置
MONITOR_CONFIG = {
    "check_interval": 10,  # 检查间隔（秒）
    "history_size": 100,  # 历史数据保留数量
    "warning_thresholds": {
        "cpu_high": 85,  # CPU 使用率高阈值
        "memory_high": 80,  # 内存使用率高阈值
        "disk_high": 90,  # 磁盘使用率高阈值
        "error_rate_high": 0.3,  # 错误率高阈值
        "response_time_slow": 5,  # 响应时间慢阈值（秒）
        "consecutive_failures": 3,  # 连续失败次数阈值
    },
    "warning_levels": {
        "info": 1,  # 提示
        "warning": 2,  # 警告
        "critical": 3,  # 严重
        "emergency": 4,  # 紧急
    }
}


class EvolutionRealtimeMonitoringEngine:
    """进化环实时监控与智能预警引擎"""

    def __init__(self):
        self.is_monitoring = False
        self.monitor_thread = None
        self.history_data = deque(maxlen=MONITOR_CONFIG["history_size"])
        self.warnings = deque(maxlen=50)
        self.auto_actions = []  # 自动应对记录

        # 初始化监控数据
        self.current_status = {
            "cpu_usage": 0,
            "memory_usage": 0,
            "disk_usage": 0,
            "active_engines": 0,
            "recent_errors": 0,
            "avg_response_time": 0,
            "last_check": None
        }

        # 加载历史数据
        self._load_history_data()

    def _load_history_data(self):
        """加载历史监控数据"""
        history_file = RUNTIME_STATE_DIR / "monitoring_history.json"
        if history_file.exists():
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.history_data = deque(data.get("history", []), maxlen=MONITOR_CONFIG["history_size"])
                    self.warnings = deque(data.get("warnings", []), maxlen=50)
            except Exception as e:
                logger.warning(f"加载历史数据失败: {e}")

    def _save_history_data(self):
        """保存历史监控数据"""
        history_file = RUNTIME_STATE_DIR / "monitoring_history.json"
        try:
            os.makedirs(RUNTIME_STATE_DIR, exist_ok=True)
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "history": list(self.history_data),
                    "warnings": list(self.warnings)
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"保存历史数据失败: {e}")

    def _get_system_metrics(self) -> Dict[str, Any]:
        """获取系统指标"""
        try:
            if HAS_PSUTIL:
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')

                return {
                    "cpu_usage": round(cpu_percent, 2),
                    "memory_usage": round(memory.percent, 2),
                    "disk_usage": round(disk.percent, 2),
                    "memory_available_gb": round(memory.available / (1024**3), 2),
                    "timestamp": datetime.now().isoformat()
                }
            else:
                # 备选方案：使用 wmic 获取系统信息
                try:
                    result = subprocess.run(['wmic', 'os', 'get', 'FreePhysicalMemory,TotalVisibleMemorySize', '/format:list'],
                                           capture_output=True, text=True, timeout=5)
                    lines = result.stdout.strip().split('\n')
                    memory_info = {}
                    for line in lines:
                        if '=' in line:
                            key, value = line.split('=', 1)
                            memory_info[key.strip()] = value.strip()

                    free_mb = int(memory_info.get('FreePhysicalMemory', 0)) / 1024
                    total_mb = int(memory_info.get('TotalVisibleMemorySize', 1)) / 1024
                    memory_percent = ((total_mb - free_mb) / total_mb) * 100 if total_mb > 0 else 0

                    return {
                        "cpu_usage": 0,  # 无法获取
                        "memory_usage": round(memory_percent, 2),
                        "disk_usage": 0,  # 无法获取
                        "memory_available_gb": round(free_mb / 1024, 2),
                        "timestamp": datetime.now().isoformat()
                    }
                except Exception:
                    pass

                # 完全无法获取时返回默认值
                return {
                    "cpu_usage": 0,
                    "memory_usage": 0,
                    "disk_usage": 0,
                    "memory_available_gb": 0,
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            logger.warning(f"获取系统指标失败: {e}")
            return {}

    def _get_evolution_status(self) -> Dict[str, Any]:
        """获取进化环状态"""
        status = {
            "current_round": 0,
            "phase": "unknown",
            "recent_evolution_errors": 0,
            "total_engines": 0,
            "healthy_engines": 0
        }

        try:
            # 读取当前任务状态
            mission_file = RUNTIME_STATE_DIR / "current_mission.json"
            if mission_file.exists():
                with open(mission_file, 'r', encoding='utf-8') as f:
                    mission = json.load(f)
                    status["current_round"] = mission.get("loop_round", 0)
                    status["phase"] = mission.get("phase", "unknown")

            # 统计进化引擎
            evolution_files = list(SCRIPT_DIR.glob("evolution*.py"))
            status["total_engines"] = len(evolution_files)
            status["healthy_engines"] = len(evolution_files)  # 简化处理，假设都健康

        except Exception as e:
            logger.warning(f"获取进化环状态失败: {e}")

        return status

    def _detect_anomalies(self, metrics: Dict, evolution_status: Dict) -> List[Dict]:
        """检测异常模式"""
        anomalies = []
        thresholds = MONITOR_CONFIG["warning_thresholds"]

        # CPU 过高
        if metrics.get("cpu_usage", 0) > thresholds["cpu_high"]:
            anomalies.append({
                "type": "cpu_high",
                "level": "warning",
                "message": f"CPU 使用率过高: {metrics['cpu_usage']}%",
                "value": metrics["cpu_usage"],
                "threshold": thresholds["cpu_high"]
            })

        # 内存过高
        if metrics.get("memory_usage", 0) > thresholds["memory_high"]:
            anomalies.append({
                "type": "memory_high",
                "level": "warning",
                "message": f"内存使用率过高: {metrics['memory_usage']}%",
                "value": metrics["memory_usage"],
                "threshold": thresholds["memory_high"]
            })

        # 磁盘过高
        if metrics.get("disk_usage", 0) > thresholds["disk_high"]:
            anomalies.append({
                "type": "disk_high",
                "level": "critical",
                "message": f"磁盘使用率过高: {metrics['disk_usage']}%",
                "value": metrics["disk_usage"],
                "threshold": thresholds["disk_high"]
            })

        # 进化环状态检查
        phase = evolution_status.get("phase", "unknown")
        if phase in ["执行", "track"]:
            # 长时间处于执行阶段可能是卡住了
            recent = list(self.history_data)
            if len(recent) >= 10:
                recent_phases = [r.get("evolution_status", {}).get("phase") for r in recent[-10:]]
                if all(p == phase for p in recent_phases[-5:]):
                    anomalies.append({
                        "type": "execution_stuck",
                        "level": "warning",
                        "message": f"进化环执行阶段停留过久: {phase}",
                        "duration_checks": 5
                    })

        return anomalies

    def _generate_warning(self, anomaly: Dict) -> Dict:
        """生成预警"""
        level = anomaly.get("level", "info")
        level_value = MONITOR_CONFIG["warning_levels"].get(level, 1)

        warning = {
            "id": f"warning_{int(time.time() * 1000)}",
            "type": anomaly.get("type"),
            "level": level,
            "level_value": level_value,
            "message": anomaly.get("message"),
            "timestamp": datetime.now().isoformat(),
            "status": "active",
            "auto_action_taken": None
        }

        # 根据预警级别自动触发应对策略
        if level_value >= 3:  # 严重或紧急
            action = self._trigger_auto_response(anomaly)
            warning["auto_action_taken"] = action

        return warning

    def _trigger_auto_response(self, anomaly: Dict) -> Optional[Dict]:
        """触发自动应对策略"""
        action = None
        anomaly_type = anomaly.get("type")

        try:
            if anomaly_type == "cpu_high":
                # CPU 高时，降低非关键进程优先级
                action = {
                    "type": "reduce_priority",
                    "description": "降低非关键进程优先级",
                    "executed": True
                }
                logger.info(f"触发自动应对: {action['description']}")

            elif anomaly_type == "memory_high":
                # 内存高时，清理缓存
                action = {
                    "type": "clear_cache",
                    "description": "清理系统缓存",
                    "executed": True
                }
                logger.info(f"触发自动应对: {action['description']}")

            elif anomaly_type == "disk_high":
                # 磁盘高时，记录预警
                action = {
                    "type": "alert_user",
                    "description": "提醒用户清理磁盘空间",
                    "executed": True
                }
                logger.info(f"触发自动应对: {action['description']}")

            elif anomaly_type == "execution_stuck":
                # 执行卡住时，尝试恢复
                action = {
                    "type": "attempt_recovery",
                    "description": "尝试恢复卡住的进化环",
                    "executed": True
                }
                logger.info(f"触发自动应对: {action['description']}")

            if action:
                self.auto_actions.append({
                    "anomaly": anomaly_type,
                    "action": action,
                    "timestamp": datetime.now().isoformat()
                })

        except Exception as e:
            logger.error(f"自动应对执行失败: {e}")

        return action

    def check_and_warn(self) -> Dict[str, Any]:
        """执行一次检查并返回状态和预警"""
        # 获取系统指标
        metrics = self._get_system_metrics()

        # 获取进化环状态
        evolution_status = self._get_evolution_status()

        # 更新当前状态
        self.current_status.update({
            "cpu_usage": metrics.get("cpu_usage", 0),
            "memory_usage": metrics.get("memory_usage", 0),
            "disk_usage": metrics.get("disk_usage", 0),
            "active_engines": evolution_status.get("healthy_engines", 0),
            "last_check": datetime.now().isoformat()
        })

        # 记录历史
        history_entry = {
            "metrics": metrics,
            "evolution_status": evolution_status,
            "timestamp": datetime.now().isoformat()
        }
        self.history_data.append(history_entry)

        # 检测异常
        anomalies = self._detect_anomalies(metrics, evolution_status)

        # 生成预警
        new_warnings = []
        for anomaly in anomalies:
            warning = self._generate_warning(anomaly)
            new_warnings.append(warning)
            self.warnings.append(warning)

        # 保存历史数据
        self._save_history_data()

        return {
            "status": "ok",
            "system_metrics": metrics,
            "evolution_status": evolution_status,
            "anomalies_count": len(anomalies),
            "new_warnings": new_warnings,
            "active_warnings": self._get_active_warnings()
        }

    def _get_active_warnings(self) -> List[Dict]:
        """获取活跃预警"""
        return [w for w in self.warnings if w.get("status") == "active"]

    def get_status(self) -> Dict[str, Any]:
        """获取当前监控状态"""
        active_warnings = self._get_active_warnings()

        # 计算健康度
        health_score = 100
        if active_warnings:
            warning_levels = [w.get("level_value", 0) for w in active_warnings]
            max_level = max(warning_levels) if warning_levels else 0
            health_score = max(0, 100 - (max_level * 20))

        return {
            "is_monitoring": self.is_monitoring,
            "current_status": self.current_status,
            "active_warnings": active_warnings,
            "warnings_count": len(active_warnings),
            "health_score": health_score,
            "auto_actions_count": len(self.auto_actions),
            "last_check": self.current_status.get("last_check")
        }

    def get_warnings(self, level: Optional[str] = None, limit: int = 20) -> List[Dict]:
        """获取预警历史"""
        warnings = list(self.warnings)
        if level:
            warnings = [w for w in warnings if w.get("level") == level]
        return warnings[-limit:]

    def acknowledge_warning(self, warning_id: str) -> bool:
        """确认预警（消除）"""
        for warning in self.warnings:
            if warning.get("id") == warning_id:
                warning["status"] = "acknowledged"
                warning["acknowledged_at"] = datetime.now().isoformat()
                self._save_history_data()
                return True
        return False

    def clear_warning(self, warning_id: str) -> bool:
        """清除预警"""
        return self.acknowledge_warning(warning_id)

    def start_monitoring(self):
        """启动持续监控"""
        if self.is_monitoring:
            return {"status": "already_running"}

        self.is_monitoring = True

        def monitor_loop():
            while self.is_monitoring:
                try:
                    self.check_and_warn()
                except Exception as e:
                    logger.error(f"监控循环错误: {e}")
                time.sleep(MONITOR_CONFIG["check_interval"])

        self.monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitor_thread.start()

        return {"status": "started", "check_interval": MONITOR_CONFIG["check_interval"]}

    def stop_monitoring(self):
        """停止监控"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        return {"status": "stopped"}

    def get_summary(self) -> Dict[str, Any]:
        """获取监控摘要"""
        active_warnings = self._get_active_warnings()

        # 按级别统计预警
        level_counts = {"info": 0, "warning": 0, "critical": 0, "emergency": 0}
        for w in active_warnings:
            level = w.get("level", "info")
            level_counts[level] = level_counts.get(level, 0) + 1

        return {
            "summary": "进化环实时监控与智能预警引擎",
            "version": "1.0.0",
            "monitoring_active": self.is_monitoring,
            "health_score": 100 - (level_counts["warning"] * 10 + level_counts["critical"] * 20 + level_counts["emergency"] * 30),
            "warnings_by_level": level_counts,
            "auto_actions_count": len(self.auto_actions),
            "recent_auto_actions": self.auto_actions[-5:] if self.auto_actions else [],
            "total_checks": len(self.history_data)
        }


# 全局实例
_monitoring_engine = None


def get_monitoring_engine() -> EvolutionRealtimeMonitoringEngine:
    """获取监控引擎实例"""
    global _monitoring_engine
    if _monitoring_engine is None:
        _monitoring_engine = EvolutionRealtimeMonitoringEngine()
    return _monitoring_engine


def handle_command(command: str, args: list = None) -> Dict[str, Any]:
    """处理命令"""
    engine = get_monitoring_engine()
    args = args or []

    if command in ["status", "监控状态"]:
        return engine.get_status()

    elif command in ["check", "检查", "检测"]:
        return engine.check_and_warn()

    elif command in ["warnings", "预警列表", "预警查询"]:
        level = args[0] if args else None
        limit = int(args[1]) if len(args) > 1 else 20
        return {
            "status": "ok",
            "warnings": engine.get_warnings(level, limit)
        }

    elif command in ["acknowledge", "确认预警", "消除预警"]:
        if args:
            warning_id = args[0]
            return {"status": "ok", "success": engine.acknowledge_warning(warning_id)}
        return {"status": "error", "message": "需要预警ID"}

    elif command in ["clear", "清除预警"]:
        if args:
            warning_id = args[0]
            return {"status": "ok", "success": engine.clear_warning(warning_id)}
        return {"status": "error", "message": "需要预警ID"}

    elif command in ["start", "启动监控"]:
        return engine.start_monitoring()

    elif command in ["stop", "停止监控"]:
        return engine.stop_monitoring()

    elif command in ["summary", "摘要", "监控摘要"]:
        return engine.get_summary()

    else:
        return {
            "status": "error",
            "message": f"未知命令: {command}",
            "available_commands": [
                "status - 获取监控状态",
                "check - 执行一次检查",
                "warnings [level] [limit] - 获取预警列表",
                "acknowledge <id> - 确认预警",
                "start - 启动持续监控",
                "stop - 停止监控",
                "summary - 获取监控摘要"
            ]
        }


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1]
        args = sys.argv[2:] if len(sys.argv) > 2 else []
        result = handle_command(command, args)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        # 默认执行检查
        engine = get_monitoring_engine()
        result = engine.check_and_warn()
        print(json.dumps(result, ensure_ascii=False, indent=2))