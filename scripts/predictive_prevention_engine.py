#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主动预测与预防引擎 (Predictive Prevention Engine)

功能：整合自愈、情境感知、学习引擎，实现问题发生前主动发现并预防。
核心能力：
1. 主动问题检测 - 主动扫描系统状态，提前发现问题
2. 用户需求预测 - 基于情境和历史预测用户可能的需求
3. 预防性优化建议 - 基于学习的历史模式提供预防建议
4. 主动预警机制 - 在问题发生前发出预警并提供解决方案

集成：
- self_healing_engine: 问题诊断能力
- context_awareness_engine: 情境感知能力
- adaptive_learning_engine: 学习适应能力
"""

import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

# 路径处理
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, SCRIPT_DIR)  # 添加 scripts 目录
sys.path.insert(0, PROJECT_ROOT)

# 导入主动通知引擎和决策编排中心
try:
    from proactive_notification_engine import ProactiveNotificationEngine
    NOTIFICATION_ENGINE_AVAILABLE = True
except ImportError:
    NOTIFICATION_ENGINE_AVAILABLE = False

try:
    # 动态导入决策编排中心
    from importlib.util import spec_from_file_location, module_from_spec
    decision_file = os.path.join(SCRIPT_DIR, "decision_orchestrator.py")
    if os.path.exists(decision_file):
        spec = spec_from_file_location("decision_orchestrator", decision_file)
        if spec and spec.loader:
            decision_module = module_from_spec(spec)
            sys.modules['decision_orchestrator'] = decision_module
            spec.loader.exec_module(decision_module)
            DecisionOrchestrator = decision_module.DecisionOrchestrator
            DECISION_ORCHESTRATOR_AVAILABLE = True
    else:
        DECISION_ORCHESTRATOR_AVAILABLE = False
except Exception as e:
    DECISION_ORCHESTRATOR_AVAILABLE = False


class PredictivePreventionEngine:
    """主动预测与预防引擎"""

    def __init__(self):
        self.name = "Predictive Prevention Engine"
        self.version = "1.0.0"
        self.state_file = os.path.join(PROJECT_ROOT, "runtime", "state", "predictive_prevention_state.json")
        self.predictions_file = os.path.join(PROJECT_ROOT, "runtime", "state", "predictions.json")

        # 内置问题模式库
        self.problem_patterns = {
            "high_memory": {
                "threshold": 85,  # 内存使用率超过85%
                "description": "内存使用率过高",
                "prevention": "关闭不必要的后台程序，清理内存"
            },
            "high_cpu": {
                "threshold": 90,  # CPU使用率超过90%
                "description": "CPU负载过高",
                "prevention": "降低高负载进程优先级或关闭"
            },
            "disk_low": {
                "threshold": 90,  # 磁盘使用率超过90%
                "description": "磁盘空间不足",
                "prevention": "清理临时文件，删除不必要的文件"
            },
            "process_not_responding": {
                "threshold": 3,  # 无响应进程数超过3
                "description": "存在无响应的进程",
                "prevention": "结束无响应进程"
            },
            "network_unstable": {
                "threshold": 2,  # 网络断开次数
                "description": "网络连接不稳定",
                "prevention": "检查网络设备，重置网络适配器"
            }
        }

        # 用户行为预测模式
        self.behavior_patterns = {
            "morning_routine": {
                "time_range": (7, 9),
                "description": "早晨常规操作",
                "typical_actions": ["打开邮件", "查看日历", "启动工作应用"]
            },
            "meeting_time": {
                "time_range": (10, 11),
                "description": "会议时间",
                "typical_actions": ["打开视频会议", "准备文档"]
            },
            "afternoon_work": {
                "time_range": (14, 17),
                "description": "下午工作时间",
                "typical_actions": ["文档处理", "数据整理"]
            },
            "end_of_day": {
                "time_range": (18, 19),
                "description": "下班时间",
                "typical_actions": ["保存文件", "整理桌面", "关闭应用"]
            }
        }

        self._load_state()

    def _load_state(self):
        """加载状态"""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    self.state = json.load(f)
            except Exception:
                self.state = {"scans": [], "predictions": [], "alerts": []}
        else:
            self.state = {"scans": [], "predictions": [], "alerts": []}

    def _save_state(self):
        """保存状态"""
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2)

    def _get_system_metrics(self) -> Dict[str, Any]:
        """获取系统指标"""
        import psutil

        metrics = {}
        try:
            # 内存
            mem = psutil.virtual_memory()
            metrics["memory_percent"] = mem.percent
            metrics["memory_available"] = mem.available / (1024**3)  # GB

            # CPU
            metrics["cpu_percent"] = psutil.cpu_percent(interval=1)

            # 磁盘
            disk = psutil.disk_usage('/')
            metrics["disk_percent"] = disk.percent
            metrics["disk_free"] = disk.free / (1024**3)  # GB

            # 进程
            metrics["processes"] = len(psutil.pids())
            metrics["processes_not_responding"] = 0  # 需要窗口系统

            # 网络
            net = psutil.net_connections()
            metrics["network_active"] = len(net)

        except Exception as e:
            metrics["error"] = str(e)

        return metrics

    def scan_and_predict(self) -> Dict[str, Any]:
        """主动扫描并预测问题

        Returns:
            扫描结果和预测
        """
        result = {
            "timestamp": datetime.now().isoformat(),
            "system_metrics": {},
            "detected_issues": [],
            "risk_level": "low",  # low, medium, high, critical
            "predictions": [],
            "prevention_suggestions": []
        }

        # 获取系统指标
        try:
            result["system_metrics"] = self._get_system_metrics()
        except ImportError:
            result["system_metrics"] = {"error": "psutil not available, using basic metrics"}
            result["system_metrics"] = self._get_basic_metrics()
        except Exception as e:
            result["system_metrics"] = {"error": str(e)}

        # 检测问题
        issues = self._detect_issues(result["system_metrics"])
        result["detected_issues"] = issues
        result["risk_level"] = self._calculate_risk_level(issues)

        # 预测
        predictions = self._predict_user_needs()
        result["predictions"] = predictions

        # 预防建议
        suggestions = self._generate_prevention_suggestions(issues)
        result["prevention_suggestions"] = suggestions

        # 保存状态
        self.state["scans"].append({
            "timestamp": result["timestamp"],
            "risk_level": result["risk_level"],
            "issues_count": len(issues)
        })
        # 只保留最近20条记录
        self.state["scans"] = self.state["scans"][-20:]
        self._save_state()

        # 保存预测
        self._save_predictions(result)

        return result

    def _get_basic_metrics(self) -> Dict[str, Any]:
        """获取基础系统指标（无psutil时）"""
        import subprocess

        metrics = {}
        try:
            # Windows: wmic memory
            output = subprocess.check_output(
                "wmic OS get FreePhysicalMemory,TotalVisibleMemorySize /Value",
                shell=True, stderr=subprocess.DEVNULL, text=True
            )
            lines = output.strip().split('\n')
            for line in lines:
                if '=' in line:
                    key, value = line.split('=', 1)
                    if 'Free' in key:
                        metrics["memory_free"] = int(value) / 1024
                    elif 'Total' in key:
                        metrics["memory_total"] = int(value) / 1024

            if "memory_free" in metrics and "memory_total" in metrics:
                metrics["memory_percent"] = (
                    (metrics["memory_total"] - metrics["memory_free"]) / metrics["memory_total"] * 100
                )

        except Exception:
            pass

        return metrics

    def _detect_issues(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """检测潜在问题"""
        issues = []

        # 内存问题
        if "memory_percent" in metrics:
            if metrics["memory_percent"] >= self.problem_patterns["high_memory"]["threshold"]:
                issues.append({
                    "type": "high_memory",
                    "severity": "high" if metrics["memory_percent"] > 90 else "medium",
                    "description": self.problem_patterns["high_memory"]["description"],
                    "current_value": f"{metrics['memory_percent']:.1f}%",
                    "threshold": f"{self.problem_patterns['high_memory']['threshold']}%",
                    "prevention": self.problem_patterns["high_memory"]["prevention"]
                })

        # CPU问题
        if "cpu_percent" in metrics:
            if metrics["cpu_percent"] >= self.problem_patterns["high_cpu"]["threshold"]:
                issues.append({
                    "type": "high_cpu",
                    "severity": "high" if metrics["cpu_percent"] > 95 else "medium",
                    "description": self.problem_patterns["high_cpu"]["description"],
                    "current_value": f"{metrics['cpu_percent']:.1f}%",
                    "threshold": f"{self.problem_patterns['high_cpu']['threshold']}%",
                    "prevention": self.problem_patterns["high_cpu"]["prevention"]
                })

        # 磁盘问题
        if "disk_percent" in metrics:
            if metrics["disk_percent"] >= self.problem_patterns["disk_low"]["threshold"]:
                issues.append({
                    "type": "disk_low",
                    "severity": "critical" if metrics["disk_percent"] > 95 else "high",
                    "description": self.problem_patterns["disk_low"]["description"],
                    "current_value": f"{metrics['disk_percent']:.1f}%",
                    "threshold": f"{self.problem_patterns['disk_low']['threshold']}%",
                    "prevention": self.problem_patterns["disk_low"]["prevention"]
                })

        return issues

    def _calculate_risk_level(self, issues: List[Dict[str, Any]]) -> str:
        """计算风险等级"""
        if not issues:
            return "low"

        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for issue in issues:
            sev = issue.get("severity", "low")
            severity_counts[sev] = severity_counts.get(sev, 0) + 1

        if severity_counts["critical"] > 0:
            return "critical"
        elif severity_counts["high"] > 1:
            return "critical"
        elif severity_counts["high"] > 0:
            return "high"
        elif severity_counts["medium"] > 0:
            return "medium"
        else:
            return "low"

    def _predict_user_needs(self) -> List[Dict[str, Any]]:
        """预测用户需求"""
        predictions = []
        now = datetime.now()
        current_hour = now.hour

        # 基于时间模式预测
        for pattern_name, pattern_info in self.behavior_patterns.items():
            time_range = pattern_info["time_range"]
            if time_range[0] <= current_hour < time_range[1]:
                predictions.append({
                    "type": "time_based",
                    "pattern": pattern_name,
                    "description": pattern_info["description"],
                    "suggested_actions": pattern_info["typical_actions"],
                    "confidence": 0.8
                })

        # 基于星期几预测
        weekday = now.weekday()
        if weekday < 5:  # 工作日
            predictions.append({
                "type": "day_based",
                "pattern": "workday",
                "description": "工作日模式",
                "suggested_actions": ["检查邮件", "查看今日日程", "准备会议材料"],
                "confidence": 0.7
            })
        else:  # 周末
            predictions.append({
                "type": "day_based",
                "pattern": "weekend",
                "description": "周末模式",
                "suggested_actions": ["整理文件", "学习新技能", "放松娱乐"],
                "confidence": 0.7
            })

        return predictions

    def _generate_prevention_suggestions(
        self, issues: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """生成预防建议"""
        suggestions = []

        # 基于问题生成建议
        for issue in issues:
            suggestions.append({
                "issue_type": issue.get("type"),
                "severity": issue.get("severity"),
                "suggestion": issue.get("prevention"),
                "action_type": "immediate" if issue.get("severity") in ["critical", "high"] else "scheduled"
            })

        # 基于时间生成预防建议
        now = datetime.now()
        current_hour = now.hour

        if 8 <= current_hour <= 9:
            suggestions.append({
                "issue_type": "productivity",
                "severity": "low",
                "suggestion": "早晨是高效工作时段，建议先处理重要任务",
                "action_type": "scheduled"
            })
        elif 14 <= current_hour <= 15:
            suggestions.append({
                "issue_type": "energy",
                "severity": "low",
                "suggestion": "下午容易疲劳，建议短暂休息后继续工作",
                "action_type": "scheduled"
            })

        # 如果没有特殊问题，添加一般性建议
        if not suggestions:
            suggestions.append({
                "issue_type": "general",
                "severity": "low",
                "suggestion": "系统运行正常，建议保持当前状态",
                "action_type": "none"
            })

        return suggestions

    def _save_predictions(self, result: Dict[str, Any]):
        """保存预测结果"""
        os.makedirs(os.path.dirname(self.predictions_file), exist_ok=True)

        predictions_data = {
            "last_update": result["timestamp"],
            "risk_level": result["risk_level"],
            "detected_issues": result["detected_issues"],
            "predictions": result["predictions"],
            "suggestions": result["prevention_suggestions"]
        }

        try:
            with open(self.predictions_file, 'w', encoding='utf-8') as f:
                json.dump(predictions_data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def get_preventive_report(self) -> str:
        """获取预防性报告"""
        result = self.scan_and_predict()

        report_lines = [
            "=" * 50,
            f"主动预测与预防报告 - {result['timestamp']}",
            "=" * 50,
            "",
            f"风险等级: {result['risk_level'].upper()}",
            ""
        ]

        # 系统指标
        if result["system_metrics"]:
            report_lines.append("【系统状态】")
            metrics = result["system_metrics"]
            if "memory_percent" in metrics:
                report_lines.append(f"  内存使用: {metrics['memory_percent']:.1f}%")
            if "cpu_percent" in metrics:
                report_lines.append(f"  CPU使用: {metrics['cpu_percent']:.1f}%")
            if "disk_percent" in metrics:
                report_lines.append(f"  磁盘使用: {metrics['disk_percent']:.1f}%")
            report_lines.append("")

        # 检测到的问题
        if result["detected_issues"]:
            report_lines.append("【检测到的问题】")
            for issue in result["detected_issues"]:
                report_lines.append(f"  [{issue['severity'].upper()}] {issue['description']}")
                report_lines.append(f"    当前值: {issue['current_value']}")
                report_lines.append(f"    建议: {issue['prevention']}")
            report_lines.append("")
        else:
            report_lines.append("【系统状态】未检测到问题，系统运行正常")
            report_lines.append("")

        # 预测
        if result["predictions"]:
            report_lines.append("【用户需求预测】")
            for pred in result["predictions"]:
                report_lines.append(f"  {pred['description']} (置信度: {pred['confidence']:.0%})")
            report_lines.append("")

        # 建议
        if result["prevention_suggestions"]:
            report_lines.append("【预防建议】")
            for suggestion in result["prevention_suggestions"]:
                if suggestion["action_type"] != "none":
                    report_lines.append(f"  [{suggestion['action_type']}] {suggestion['suggestion']}")
            report_lines.append("")

        report_lines.append("=" * 50)

        return "\n".join(report_lines)

    def get_alert(self) -> Optional[Dict[str, Any]]:
        """获取当前预警信息"""
        result = self.scan_and_predict()

        if result["risk_level"] in ["critical", "high"]:
            return {
                "level": result["risk_level"],
                "timestamp": result["timestamp"],
                "issues": result["detected_issues"],
                "suggestions": result["prevention_suggestions"]
            }

        return None

    def send_alert_notification(self, force: bool = False) -> Dict[str, Any]:
        """发送预警通知到用户

        当检测到高风险时，自动通过主动通知引擎发送预警通知

        Args:
            force: 是否强制发送（即使没有高风险）

        Returns:
            发送结果
        """
        result = {
            "success": False,
            "alert_sent": False,
            "message": ""
        }

        # 获取预警信息
        alert = self.get_alert()

        if not alert and not force:
            result["message"] = "当前无高风险预警，无需发送通知"
            return result

        if not NOTIFICATION_ENGINE_AVAILABLE:
            result["message"] = "主动通知引擎不可用"
            return result

        try:
            # 创建通知引擎实例
            notification_engine = ProactiveNotificationEngine()

            # 构建通知内容
            if alert:
                level_text = "紧急" if alert["level"] == "critical" else "高风险"
                title = f"⚠️ 系统{level_text}预警"

                # 构建消息内容
                issues_text = []
                for issue in alert.get("issues", []):
                    issues_text.append(f"• {issue.get('description', '未知问题')}: {issue.get('current_value', 'N/A')}")

                suggestions_text = []
                for suggestion in alert.get("suggestions", []):
                    if suggestion.get("action_type") == "immediate":
                        suggestions_text.append(f"• {suggestion.get('suggestion', '无')}")

                content_lines = [title, ""]
                if issues_text:
                    content_lines.append("检测到以下问题:")
                    content_lines.extend(issues_text)
                    content_lines.append("")
                if suggestions_text:
                    content_lines.append("建议立即处理:")
                    content_lines.extend(suggestions_text)

                content = "\n".join(content_lines)

                # 发送通知，优先级根据风险等级
                priority = 5 if alert["level"] == "critical" else 4

                notification_id = notification_engine.add_notification(
                    notification_type="alert",
                    content=content,
                    priority=priority,
                    metadata={
                        "alert_level": alert["level"],
                        "issues_count": len(alert.get("issues", [])),
                        "source": "predictive_prevention_engine"
                    }
                )

                result["success"] = True
                result["alert_sent"] = True
                result["message"] = f"预警通知已发送 (ID: {notification_id})"
                result["notification_id"] = notification_id

            elif force:
                # 强制发送时，发送系统正常通知
                notification_id = notification_engine.add_notification(
                    notification_type="system",
                    content="系统检测完成，当前无高风险预警。系统运行正常。",
                    priority=1,
                    metadata={"source": "predictive_prevention_engine"}
                )
                result["success"] = True
                result["message"] = f"系统状态通知已发送 (ID: {notification_id})"

        except Exception as e:
            result["message"] = f"发送预警通知失败: {str(e)}"

        return result

    def auto_trigger_decision(self, auto_execute: bool = False) -> Dict[str, Any]:
        """自动触发决策编排中心

        当检测到高风险问题时，自动触发决策编排中心进行分析和修复决策。
        这是「预测→决策→执行→通知」自动化闭环的关键环节。

        Args:
            auto_execute: 是否自动执行修复（需要决策编排中心支持）

        Returns:
            触发决策编排的结果
        """
        result = {
            "success": False,
            "triggered": False,
            "decision_result": None,
            "message": ""
        }

        # 先进行系统扫描
        scan_result = self.scan_and_predict()

        # 检查是否需要触发决策
        if scan_result["risk_level"] not in ["critical", "high"]:
            result["message"] = "系统风险等级低，无需触发决策编排"
            return result

        if not DECISION_ORCHESTRATOR_AVAILABLE:
            result["message"] = "决策编排中心不可用，仅发送预警通知"
            # 降级为仅发送通知
            notify_result = self.send_alert_notification(force=True)
            result["notification_sent"] = notify_result.get("alert_sent", False)
            return result

        try:
            # 创建决策编排中心实例
            orchestrator = DecisionOrchestrator()

            # 构建触发上下文
            context = f"系统检测到{scan_result['risk_level']}风险，检测到{len(scan_result['detected_issues'])}个问题，需要诊断和修复"

            # 调用决策编排中心
            # 检查是否有自动化修复能力
            if auto_execute and hasattr(orchestrator, 'execute_auto_remediation'):
                decision_result = orchestrator.execute_auto_remediation(scan_result)
            else:
                # 仅获取预测服务（分析+建议）
                decision_result = orchestrator.get_predictive_service()

            result["success"] = True
            result["triggered"] = True
            result["decision_result"] = decision_result
            result["risk_level"] = scan_result["risk_level"]
            result["issues_count"] = len(scan_result["detected_issues"])
            result["message"] = f"已触发决策编排中心，风险等级: {scan_result['risk_level']}"

            # 同时发送预警通知
            notify_result = self.send_alert_notification(force=True)
            result["notification_sent"] = notify_result.get("alert_sent", False)

        except Exception as e:
            result["message"] = f"触发决策编排失败: {str(e)}"

        # 保存触发历史
        self.state["alerts"].append({
            "timestamp": datetime.now().isoformat(),
            "triggered": result["triggered"],
            "risk_level": scan_result.get("risk_level"),
            "auto_execute": auto_execute
        })
        self._save_state()

        return result


def main():
    """主函数"""
    engine = PredictivePreventionEngine()

    # 解析命令行参数
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command in ["scan", "predict", "检测", "预测"]:
            result = engine.scan_and_predict()
            print(json.dumps(result, ensure_ascii=False, indent=2))

        elif command in ["report", "报告"]:
            print(engine.get_preventive_report())

        elif command in ["alert", "预警"]:
            alert = engine.get_alert()
            if alert:
                print(json.dumps(alert, ensure_ascii=False, indent=2))
            else:
                print(json.dumps({"status": "no_alert", "message": "当前无预警"}, ensure_ascii=False, indent=2))

        elif command in ["notify", "通知", "发送预警", "send_alert"]:
            # 发送预警通知
            force = len(sys.argv) > 2 and sys.argv[2].lower() in ["--force", "-f", "force"]
            result = engine.send_alert_notification(force=force)
            print(json.dumps(result, ensure_ascii=False, indent=2))

        elif command in ["auto", "自动", "auto_trigger", "自动触发"]:
            # 自动触发决策编排
            auto_execute = len(sys.argv) > 2 and sys.argv[2].lower() in ["--auto", "-a", "auto", "execute"]
            result = engine.auto_trigger_decision(auto_execute=auto_execute)
            print(json.dumps(result, ensure_ascii=False, indent=2))

        else:
            # 默认显示报告
            print(engine.get_preventive_report())
    else:
        # 默认显示报告
        print(engine.get_preventive_report())


if __name__ == "__main__":
    main()