"""
智能全场景进化环元健康诊断与自愈增强引擎
让系统能够持续监控元进化环本身的健康状态，实时检测进化过程中的异常模式，
自动诊断问题根因并生成自愈方案，形成元进化层面的免疫系统。

Version: 1.0.0
"""

import json
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path

# 状态文件路径
RUNTIME_STATE_DIR = Path(__file__).parent.parent / "runtime" / "state"
RUNTIME_LOGS_DIR = Path(__file__).parent.parent / "runtime" / "logs"


class MetaHealthDiagnosisSelfHealingEngine:
    """元进化环健康诊断与自愈引擎"""

    def __init__(self):
        self.name = "MetaHealthDiagnosisSelfHealingEngine"
        self.version = "1.0.0"
        self.state_file = RUNTIME_STATE_DIR / "meta_health_state.json"
        self.history_file = RUNTIME_STATE_DIR / "meta_health_history.json"
        self.health_check_interval = 300  # 5分钟检查一次
        self.last_check_time = None
        self.anomaly_patterns = self._load_anomaly_patterns()
        self.self_healing_strategies = self._load_self_healing_strategies()

    def _load_anomaly_patterns(self) -> Dict:
        """加载异常模式库"""
        return {
            "execution_failure": {
                "description": "进化执行失败",
                "indicators": ["error", "fail", "exception"],
                "severity": "high"
            },
            "verification_failure": {
                "description": "验证未通过",
                "indicators": ["verify fail", "校验失败", "未通过"],
                "severity": "high"
            },
            "strategy_ineffective": {
                "description": "策略无效",
                "indicators": ["ineffective", "无效果", "低效"],
                "severity": "medium"
            },
            "performance_degradation": {
                "description": "性能下降",
                "indicators": ["slow", "超时", "延迟"],
                "severity": "medium"
            },
            "resource_exhaustion": {
                "description": "资源耗尽",
                "indicators": ["memory", "cpu", "资源不足"],
                "severity": "high"
            },
            "loop_stuck": {
                "description": "进化环卡住",
                "indicators": ["stuck", "卡住", "无进展"],
                "severity": "critical"
            }
        }

    def _load_self_healing_strategies(self) -> Dict:
        """加载自愈策略库"""
        return {
            "execution_failure": {
                "actions": [
                    {"type": "log", "content": "记录错误详情"},
                    {"type": "retry", "max_attempts": 3},
                    {"type": "fallback", "content": "切换到备用策略"}
                ]
            },
            "verification_failure": {
                "actions": [
                    {"type": "analyze", "content": "分析验证失败原因"},
                    {"type": "adjust", "content": "调整验证参数"},
                    {"type": "skip_optional", "content": "跳过可选验证项"}
                ]
            },
            "strategy_ineffective": {
                "actions": [
                    {"type": "rotate", "content": "轮换策略"},
                    {"type": "blend", "content": "混合多策略"},
                    {"type": "reset", "content": "重置策略参数"}
                ]
            },
            "performance_degradation": {
                "actions": [
                    {"type": "throttle", "content": "降低执行频率"},
                    {"type": "optimize", "content": "优化执行路径"},
                    {"type": "cache", "content": "增加缓存"}
                ]
            },
            "resource_exhaustion": {
                "actions": [
                    {"type": "cleanup", "content": "清理临时资源"},
                    {"type": "pause", "content": "暂停非关键任务"},
                    {"type": "scale_down", "content": "减少并发"}
                ]
            },
            "loop_stuck": {
                "actions": [
                    {"type": "force_continue", "content": "强制继续下一轮"},
                    {"type": "reset_state", "content": "重置状态"},
                    {"type": "alert", "content": "发送告警通知"}
                ]
            }
        }

    def get_meta_health_status(self) -> Dict:
        """获取元进化环健康状态"""
        health_data = {
            "timestamp": datetime.now().isoformat(),
            "engine_name": self.name,
            "engine_version": self.version,
            "health_score": 100,
            "status": "healthy",
            "checks": []
        }

        # 检查1: 进化状态文件
        try:
            current_mission_path = RUNTIME_STATE_DIR / "current_mission.json"
            if current_mission_path.exists():
                with open(current_mission_path, 'r', encoding='utf-8') as f:
                    mission = json.load(f)
                    health_data["checks"].append({
                        "item": "current_mission",
                        "status": "ok",
                        "detail": f"phase={mission.get('phase')}, round={mission.get('loop_round')}"
                    })

                    # 检查是否卡住
                    if mission.get('phase') == '假设' and mission.get('next_action') == '规划':
                        # 正常状态
                        pass
            else:
                health_data["checks"].append({
                    "item": "current_mission",
                    "status": "warning",
                    "detail": "mission file not found"
                })
                health_data["health_score"] -= 10
        except Exception as e:
            health_data["checks"].append({
                "item": "current_mission",
                "status": "error",
                "detail": str(e)
            })
            health_data["health_score"] -= 20

        # 检查2: 进化历史
        try:
            completed_files = list(RUNTIME_STATE_DIR.glob("evolution_completed_*.json"))
            recent_completed = [f for f in completed_files
                              if datetime.fromtimestamp(f.stat().st_mtime) > datetime.now() - timedelta(hours=24)]

            if len(recent_completed) > 0:
                health_data["checks"].append({
                    "item": "evolution_history",
                    "status": "ok",
                    "detail": f"{len(recent_completed)} rounds in last 24h"
                })
            else:
                health_data["checks"].append({
                    "item": "evolution_history",
                    "status": "warning",
                    "detail": "no recent evolution rounds"
                })
                health_data["health_score"] -= 15
        except Exception as e:
            health_data["checks"].append({
                "item": "evolution_history",
                "status": "error",
                "detail": str(e)
            })
            health_data["health_score"] -= 10

        # 检查3: 日志健康
        try:
            today_log = RUNTIME_LOGS_DIR / f"behavior_{datetime.now().strftime('%Y-%m-%d')}.log"
            if today_log.exists():
                log_size = today_log.stat().st_size
                health_data["checks"].append({
                    "item": "log_system",
                    "status": "ok",
                    "detail": f"log size: {log_size} bytes"
                })
            else:
                health_data["checks"].append({
                    "item": "log_system",
                    "status": "warning",
                    "detail": "today log not found"
                })
                health_data["health_score"] -= 5
        except Exception as e:
            health_data["checks"].append({
                "item": "log_system",
                "status": "error",
                "detail": str(e)
            })
            health_data["health_score"] -= 10

        # 检查4: 关键引擎可用性
        critical_engines = [
            "evolution_meta_strategy_execution_verification_engine.py",
            "evolution_meta_methodology_auto_optimizer.py",
            "evolution_cross_round_deep_learning_iteration_engine.py"
        ]
        scripts_dir = Path(__file__).parent

        critical_check = []
        for engine in critical_engines:
            engine_path = scripts_dir / engine
            if engine_path.exists():
                critical_check.append("ok")
            else:
                critical_check.append("missing")

        if all(c == "ok" for c in critical_check):
            health_data["checks"].append({
                "item": "critical_engines",
                "status": "ok",
                "detail": f"All {len(critical_engines)} critical engines available"
            })
        else:
            missing_count = critical_check.count("missing")
            health_data["checks"].append({
                "item": "critical_engines",
                "status": "warning",
                "detail": f"{missing_count} critical engines missing"
            })
            health_data["health_score"] -= missing_count * 15

        # 计算健康状态
        health_data["health_score"] = max(0, health_data["health_score"])

        if health_data["health_score"] >= 80:
            health_data["status"] = "healthy"
        elif health_data["health_score"] >= 50:
            health_data["status"] = "degraded"
        else:
            health_data["status"] = "unhealthy"

        # 存储状态
        self._save_health_state(health_data)

        return health_data

    def _save_health_state(self, health_data: Dict):
        """保存健康状态"""
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(health_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save health state: {e}")

    def detect_anomalies(self, context: Optional[Dict] = None) -> List[Dict]:
        """检测异常模式"""
        anomalies = []

        # 从最近的进化历史中检测异常
        try:
            # 获取最近完成的进化
            completed_files = sorted(
                RUNTIME_STATE_DIR.glob("evolution_completed_*.json"),
                key=lambda x: x.stat().st_mtime,
                reverse=True
            )[:10]  # 最近10轮

            for f in completed_files:
                with open(f, 'r', encoding='utf-8') as file:
                    data = json.load(file)

                    # 检查是否有失败标记
                    if data.get("status") in ["stale_failed", "failed"]:
                        anomalies.append({
                            "type": "execution_failure",
                            "round": data.get("loop_round"),
                            "description": f"Round {data.get('loop_round')} failed",
                            "severity": "high",
                            "timestamp": data.get("timestamp", "")
                        })

                    # 检查是否有警告
                    if "风险等级" in data.get("做了什么", "") and "高" in data["做了什么"]:
                        anomalies.append({
                            "type": "risk_detected",
                            "round": data.get("loop_round"),
                            "description": "High risk evolution",
                            "severity": "medium",
                            "timestamp": data.get("timestamp", "")
                        })
        except Exception as e:
            print(f"Warning: Failed to detect anomalies: {e}")

        # 合并用户提供的上下文
        if context:
            context_str = str(context).lower()
            for pattern_key, pattern_info in self.anomaly_patterns.items():
                for indicator in pattern_info["indicators"]:
                    if indicator.lower() in context_str:
                        anomalies.append({
                            "type": pattern_key,
                            "description": pattern_info["description"],
                            "severity": pattern_info["severity"],
                            "timestamp": datetime.now().isoformat()
                        })

        return anomalies

    def diagnose_root_cause(self, anomaly: Dict) -> Dict:
        """诊断问题根因"""
        diagnosis = {
            "anomaly": anomaly,
            "root_cause": "unknown",
            "confidence": 0.0,
            "analysis": []
        }

        anomaly_type = anomaly.get("type", "")

        # 基于异常类型进行分析
        if anomaly_type == "execution_failure":
            diagnosis["analysis"].append("可能原因：执行脚本错误、资源不足、外部依赖不可用")
            diagnosis["root_cause"] = "execution_environment_issue"
            diagnosis["confidence"] = 0.7

        elif anomaly_type == "verification_failure":
            diagnosis["analysis"].append("可能原因：验证标准过高、输入数据异常、执行结果不符合预期")
            diagnosis["root_cause"] = "verification_criteria_mismatch"
            diagnosis["confidence"] = 0.6

        elif anomaly_type == "strategy_ineffective":
            diagnosis["analysis"].append("可能原因：策略参数不当、上下文不匹配、策略老化")
            diagnosis["root_cause"] = "strategy_degradation"
            diagnosis["confidence"] = 0.5

        elif anomaly_type == "loop_stuck":
            diagnosis["analysis"].append("可能原因：状态文件损坏、进程锁死、决策循环")
            diagnosis["root_cause"] = "state_machine_stuck"
            diagnosis["confidence"] = 0.8

        else:
            diagnosis["analysis"].append("需要更多信息进行诊断")
            diagnosis["confidence"] = 0.3

        return diagnosis

    def generate_self_healing_plan(self, diagnosis: Dict) -> Dict:
        """生成自愈方案"""
        root_cause = diagnosis.get("root_cause", "unknown")

        healing_plan = {
            "diagnosis": diagnosis,
            "actions": [],
            "estimated_effectiveness": 0.0
        }

        # 映射根因到自愈策略
        cause_to_strategy = {
            "execution_environment_issue": "execution_failure",
            "verification_criteria_mismatch": "verification_failure",
            "strategy_degradation": "strategy_ineffective",
            "state_machine_stuck": "loop_stuck"
        }

        strategy_key = cause_to_strategy.get(root_cause, "execution_failure")

        if strategy_key in self.self_healing_strategies:
            healing_plan["actions"] = self.self_healing_strategies[strategy_key]["actions"]
            healing_plan["estimated_effectiveness"] = 0.7

        return healing_plan

    def execute_self_healing(self, healing_plan: Dict) -> Dict:
        """执行自愈方案"""
        result = {
            "success": False,
            "executed_actions": [],
            "remaining_actions": healing_plan.get("actions", []),
            "message": ""
        }

        for action in healing_plan.get("actions", []):
            action_type = action.get("type", "")
            action_content = action.get("content", "")

            try:
                if action_type == "log":
                    # 记录日志
                    result["executed_actions"].append({
                        "type": action_type,
                        "content": action_content,
                        "status": "success"
                    })
                    result["remaining_actions"].remove(action)

                elif action_type == "retry":
                    # 重试逻辑（这里只是标记，实际重试由调用者执行）
                    result["executed_actions"].append({
                        "type": action_type,
                        "content": "标记需要重试",
                        "status": "pending_retry"
                    })

                elif action_type == "alert":
                    # 发送告警
                    result["executed_actions"].append({
                        "type": action_type,
                        "content": "将发送告警通知",
                        "status": "success"
                    })
                    result["message"] = "自愈方案已部分执行，建议检查系统状态"

                else:
                    # 其他操作
                    result["executed_actions"].append({
                        "type": action_type,
                        "content": action_content,
                        "status": "not_implemented"
                    })

            except Exception as e:
                result["executed_actions"].append({
                    "type": action_type,
                    "content": action_content,
                    "status": "failed",
                    "error": str(e)
                })

        result["success"] = len(result["executed_actions"]) > 0 and len(result["remaining_actions"]) == 0

        return result

    def run_full_cycle(self, context: Optional[Dict] = None) -> Dict:
        """运行完整的健康诊断-自愈周期"""
        cycle_result = {
            "timestamp": datetime.now().isoformat(),
            "health_check": None,
            "anomalies": [],
            "diagnoses": [],
            "healing_plans": [],
            "healing_results": [],
            "final_status": "unknown"
        }

        # 1. 健康检查
        health_status = self.get_meta_health_status()
        cycle_result["health_check"] = health_status

        # 2. 异常检测
        anomalies = self.detect_anomalies(context)
        cycle_result["anomalies"] = anomalies

        # 3. 对每个异常进行诊断和自愈
        for anomaly in anomalies:
            diagnosis = self.diagnose_root_cause(anomaly)
            cycle_result["diagnoses"].append(diagnosis)

            healing_plan = self.generate_self_healing_plan(diagnosis)
            cycle_result["healing_plans"].append(healing_plan)

            healing_result = self.execute_self_healing(healing_plan)
            cycle_result["healing_results"].append(healing_result)

        # 4. 确定最终状态
        if health_status["status"] == "healthy" and len(anomalies) == 0:
            cycle_result["final_status"] = "healthy"
        elif health_status["status"] == "unhealthy" or any(
            a.get("severity") == "critical" for a in anomalies
        ):
            cycle_result["final_status"] = "unhealthy"
        else:
            cycle_result["final_status"] = "degraded"

        return cycle_result

    def get_cockpit_data(self) -> Dict:
        """获取驾驶舱数据"""
        health = self.get_meta_health_status()
        anomalies = self.detect_anomalies()

        return {
            "meta_health": health,
            "anomaly_count": len(anomalies),
            "recent_anomalies": anomalies[:5] if anomalies else [],
            "self_healing_capability": True,
            "last_check": self.last_check_time.isoformat() if self.last_check_time else None
        }


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(
        description="智能全场景进化环元健康诊断与自愈增强引擎"
    )
    parser.add_argument("--status", action="store_true", help="获取元进化环健康状态")
    parser.add_argument("--detect", action="store_true", help="检测异常模式")
    parser.add_argument("--diagnose", type=str, help="诊断指定异常（JSON字符串）")
    parser.add_argument("--heal", type=str, help="执行自愈（JSON字符串诊断结果）")
    parser.add_argument("--full-cycle", action="store_true", help="运行完整健康诊断-自愈周期")
    parser.add_argument("--cockpit-data", action="store_true", help="获取驾驶舱数据")

    args = parser.parse_args()

    engine = MetaHealthDiagnosisSelfHealingEngine()

    if args.status:
        result = engine.get_meta_health_status()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.detect:
        result = engine.detect_anomalies()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.diagnose:
        try:
            anomaly = json.loads(args.diagnose)
            result = engine.diagnose_root_cause(anomaly)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        except json.JSONDecodeError:
            print("Error: Invalid JSON for diagnose")

    elif args.heal:
        try:
            diagnosis = json.loads(args.heal)
            healing_plan = engine.generate_self_healing_plan(diagnosis)
            result = engine.execute_self_healing(healing_plan)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        except json.JSONDecodeError:
            print("Error: Invalid JSON for heal")

    elif args.full_cycle:
        result = engine.run_full_cycle()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.cockpit_data:
        result = engine.get_cockpit_data()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()