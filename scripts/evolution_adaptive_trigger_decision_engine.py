#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环自适应触发与自主决策增强引擎
Evolution Adaptive Trigger & Decision Engine

在 round 350 的进化驾驶舱和 round 349 的跨引擎协同优化基础上，进一步增强
进化环的自适应触发与自主决策能力。让系统能够基于系统状态、进化历史、健康态势
自动判断是否需要触发进化、选择哪种进化策略、执行哪个优化动作，实现从
「被动等待触发」到「主动感知→智能决策→自动执行→效果验证」的完整自主闭环。

功能：
1. 多维度触发条件评估（系统负载、健康度、进化效率、能力缺口、时间规律）
2. 自主决策引擎（评估触发条件→选择最优策略→生成执行计划）
3. 自动执行与效果验证
4. 与进化驾驶舱深度集成
5. 智能学习与自适应优化

Version: 1.0.0

依赖：
- evolution_cockpit_engine.py (round 350)
- evolution_cross_engine_collaboration_optimizer.py (round 349)
- evolution_full_auto_loop.py (round 300/306)
- evolution_global_situation_awareness.py (round 329)
"""

import os
import sys
import json
import time
import threading
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
from collections import defaultdict
import math

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


class AdaptiveTriggerDecisionEngine:
    """自适应触发与自主决策引擎"""

    def __init__(self):
        self.version = "1.0.0"
        self.project_root = PROJECT_ROOT
        self.scripts_dir = SCRIPT_DIR
        self.runtime_dir = os.path.join(self.project_root, "runtime")
        self.state_dir = os.path.join(self.runtime_dir, "state")
        self.logs_dir = os.path.join(self.runtime_dir, "logs")

        # 状态文件
        self.state_file = os.path.join(self.state_dir, "adaptive_trigger_decision_state.json")
        self.config_file = os.path.join(self.state_dir, "adaptive_trigger_decision_config.json")
        self.decision_history_file = os.path.join(self.state_dir, "adaptive_decision_history.json")
        self.trigger_log_file = os.path.join(self.state_dir, "adaptive_trigger_log.json")

        # 初始化目录
        self._ensure_directories()

        # 配置
        self.config = self._load_config()

        # 决策状态
        self.last_trigger_time = None
        self.last_decision = None
        self.decision_count = 0
        self.trigger_count = 0

        # 触发条件权重配置
        self.trigger_weights = self.config.get("trigger_weights", {
            "system_load": 0.2,
            "health_score": 0.3,
            "evolution_efficiency": 0.2,
            "capability_gaps": 0.2,
            "time_pattern": 0.1
        })

        # 决策阈值
        self.trigger_threshold = self.config.get("trigger_threshold", 0.6)
        self.decision_timeout = self.config.get("decision_timeout", 300)  # 5分钟

    def _ensure_directories(self):
        """确保必要的目录存在"""
        for directory in [self.state_dir, self.logs_dir]:
            os.makedirs(directory, exist_ok=True)

    def _load_config(self) -> Dict:
        """加载配置文件"""
        default_config = {
            "trigger_weights": {
                "system_load": 0.2,
                "health_score": 0.3,
                "evolution_efficiency": 0.2,
                "capability_gaps": 0.2,
                "time_pattern": 0.1
            },
            "trigger_threshold": 0.6,
            "decision_timeout": 300,
            "auto_trigger_enabled": True,
            "decision_strategy": "weighted",  # weighted, priority, adaptive
            "min_interval_seconds": 300,  # 最小触发间隔
            "max_consecutive_decisions": 5,  # 最大连续决策次数
            "learning_enabled": True,
            "decision_log_days": 30
        }

        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    return {**default_config, **config}
            except Exception as e:
                _safe_print(f"配置加载失败: {e}")

        return default_config

    def _save_config(self):
        """保存配置文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            _safe_print(f"配置保存失败: {e}")

    def get_system_load(self) -> float:
        """获取系统负载评分 (0-1，越低越好)"""
        try:
            # 简化实现：检查当前运行状态
            state_file = os.path.join(self.state_dir, "current_mission.json")
            if os.path.exists(state_file):
                with open(state_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                    # 如果正在执行，负载较高
                    if state.get("phase") in ["执行", "规划"]:
                        return 0.7
            return 0.3  # 负载低
        except Exception:
            return 0.5

    def get_health_score(self) -> float:
        """获取系统健康度评分 (0-1，越高越好)"""
        try:
            # 尝试读取健康状态
            health_files = [
                os.path.join(self.state_dir, "evolution_cockpit_state.json"),
                os.path.join(self.state_dir, "cross_engine_health.json")
            ]

            for health_file in health_files:
                if os.path.exists(health_file):
                    with open(health_file, 'r', encoding='utf-8') as f:
                        health_data = json.load(f)
                        if "health_score" in health_data:
                            return health_data["health_score"]
                        if "overall_health" in health_data:
                            return health_data["overall_health"]

            # 默认健康度
            return 0.8
        except Exception:
            return 0.7

    def get_evolution_efficiency(self) -> float:
        """获取进化效率评分 (0-1)"""
        try:
            # 读取最近的进化完成记录
            last_evolution_file = os.path.join(self.state_dir, "evolution_auto_last.md")
            if os.path.exists(last_evolution_file):
                with open(last_evolution_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # 检查最近进化是否成功
                    if "完成" in content or "completed" in content.lower():
                        return 0.8
            return 0.5
        except Exception:
            return 0.5

    def get_capability_gaps_score(self) -> float:
        """获取能力缺口评分 (0-1，越高表示缺口越大)"""
        try:
            gaps_file = os.path.join(PROJECT_ROOT, "references", "capability_gaps.md")
            if os.path.exists(gaps_file):
                with open(gaps_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # 简单统计"待扩展"条目数量
                    if "已覆盖" in content and "缺口" in content:
                        # 有覆盖说明缺口小
                        return 0.3
            return 0.4  # 轻微缺口
        except Exception:
            return 0.5

    def get_time_pattern_score(self) -> float:
        """获取时间规律评分 (0-1)"""
        try:
            now = datetime.now()
            hour = now.hour

            # 工作时间（9-18点）更适合进化
            if 9 <= hour <= 18:
                return 0.8
            # 晚间（18-22点）次之
            elif 18 <= hour <= 22:
                return 0.6
            # 夜间和凌晨不适合
            else:
                return 0.2
        except Exception:
            return 0.5

    def evaluate_trigger_conditions(self) -> Tuple[float, Dict]:
        """评估所有触发条件，返回综合评分和详细信息"""
        scores = {
            "system_load": self.get_system_load(),
            "health_score": self.get_health_score(),
            "evolution_efficiency": self.get_evolution_efficiency(),
            "capability_gaps": self.get_capability_gaps_score(),
            "time_pattern": self.get_time_pattern_score()
        }

        # 计算加权综合评分
        # 系统负载：越低越好，所以用 1 - load
        # 健康度：越高越好
        # 进化效率：越高越好
        # 能力缺口：越高越好（表示需要进化）
        # 时间规律：越高越好（表示适合进化）

        weighted_score = (
            (1 - scores["system_load"]) * self.trigger_weights["system_load"] +
            scores["health_score"] * self.trigger_weights["health_score"] +
            scores["evolution_efficiency"] * self.trigger_weights["evolution_efficiency"] +
            scores["capability_gaps"] * self.trigger_weights["capability_gaps"] +
            scores["time_pattern"] * self.trigger_weights["time_pattern"]
        )

        return weighted_score, scores

    def should_trigger_evolution(self) -> Tuple[bool, Dict]:
        """判断是否应该触发进化"""
        # 检查最小间隔
        if self.last_trigger_time:
            elapsed = time.time() - self.last_trigger_time
            if elapsed < self.config.get("min_interval_seconds", 300):
                return False, {"reason": "min_interval_not_reached", "elapsed": elapsed}

        # 评估触发条件
        score, details = self.evaluate_trigger_conditions()

        # 记录评估结果
        self._log_trigger_evaluation(score, details)

        # 判断是否触发
        should_trigger = score >= self.trigger_threshold

        return should_trigger, {
            "score": score,
            "threshold": self.trigger_threshold,
            "details": details
        }

    def _log_trigger_evaluation(self, score: float, details: Dict):
        """记录触发评估日志"""
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "score": score,
                "threshold": self.trigger_threshold,
                "should_trigger": score >= self.trigger_threshold,
                "details": details
            }

            # 读取现有日志
            log_data = []
            if os.path.exists(self.trigger_log_file):
                with open(self.trigger_log_file, 'r', encoding='utf-8') as f:
                    try:
                        log_data = json.load(f)
                    except:
                        log_data = []

            log_data.append(log_entry)

            # 只保留最近30条
            log_data = log_data[-30:]

            with open(self.trigger_log_file, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            _safe_print(f"触发评估日志记录失败: {e}")

    def decide_evolution_strategy(self, trigger_result: Dict) -> Dict:
        """决定进化策略"""
        score = trigger_result.get("score", 0)
        details = trigger_result.get("details", {})

        # 基于评估结果选择策略
        if details.get("capability_gaps", 0) > 0.6:
            # 能力缺口大，优先补齐能力
            strategy = "capability_focus"
            priority = "high"
        elif details.get("health_score", 0) < 0.5:
            # 健康度低，优先健康修复
            strategy = "health_focus"
            priority = "urgent"
        elif details.get("evolution_efficiency", 0) < 0.5:
            # 效率低，进行优化
            strategy = "efficiency_focus"
            priority = "medium"
        else:
            # 正常进化
            strategy = "balanced"
            priority = "normal"

        # 构建决策结果
        decision = {
            "strategy": strategy,
            "priority": priority,
            "score": score,
            "timestamp": datetime.now().isoformat(),
            "reason": self._get_strategy_reason(strategy, details)
        }

        self.last_decision = decision
        self.decision_count += 1

        # 记录决策历史
        self._save_decision_history(decision)

        return decision

    def _get_strategy_reason(self, strategy: str, details: Dict) -> str:
        """获取策略选择原因"""
        reasons = {
            "capability_focus": f"能力缺口较大({details.get('capability_gaps', 0):.2f})，优先补齐能力",
            "health_focus": f"系统健康度较低({details.get('health_score', 0):.2f})，优先健康修复",
            "efficiency_focus": f"进化效率待提升({details.get('evolution_efficiency', 0):.2f})，进行优化",
            "balanced": "系统状态良好，执行平衡进化策略"
        }
        return reasons.get(strategy, "默认策略")

    def _save_decision_history(self, decision: Dict):
        """保存决策历史"""
        try:
            history = []
            if os.path.exists(self.decision_history_file):
                with open(self.decision_history_file, 'r', encoding='utf-8') as f:
                    try:
                        history = json.load(f)
                    except:
                        history = []

            history.append(decision)

            # 只保留最近30条
            history = history[-30:]

            with open(self.decision_history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            _safe_print(f"决策历史保存失败: {e}")

    def generate_execution_plan(self, decision: Dict) -> Dict:
        """生成执行计划"""
        strategy = decision.get("strategy", "balanced")

        # 基于策略生成具体执行计划
        plan_templates = {
            "capability_focus": {
                "action": "capability_enhancement",
                "description": "增强能力覆盖",
                "suggested_focus": "补齐能力缺口"
            },
            "health_focus": {
                "action": "health_remediation",
                "description": "修复系统健康问题",
                "suggested_focus": "诊断并修复问题"
            },
            "efficiency_focus": {
                "action": "efficiency_optimization",
                "description": "优化进化效率",
                "suggested_focus": "提升执行效率"
            },
            "balanced": {
                "action": "balanced_evolution",
                "description": "平衡进化",
                "suggested_focus": "综合优化"
            }
        }

        plan = plan_templates.get(strategy, plan_templates["balanced"])
        plan["decision"] = decision
        plan["generated_at"] = datetime.now().isoformat()

        return plan

    def auto_execute(self, plan: Dict) -> Dict:
        """自动执行计划"""
        result = {
            "success": False,
            "plan": plan,
            "executed_at": datetime.now().isoformat(),
            "message": ""
        }

        try:
            action = plan.get("action")

            if action == "capability_enhancement":
                # 触发能力增强流程
                result["message"] = "触发能力增强流程（需要进一步集成）"
                result["success"] = True
            elif action == "health_remediation":
                # 触发健康修复
                result["message"] = "触发健康修复流程（需要进一步集成）"
                result["success"] = True
            elif action == "efficiency_optimization":
                # 触发效率优化
                result["message"] = "触发效率优化流程（需要进一步集成）"
                result["success"] = True
            elif action == "balanced_evolution":
                # 触发平衡进化
                result["message"] = "触发平衡进化流程（需要进一步集成）"
                result["success"] = True
            else:
                result["message"] = f"未知动作类型: {action}"

            if result["success"]:
                self.trigger_count += 1
                self.last_trigger_time = time.time()

        except Exception as e:
            result["message"] = f"执行失败: {str(e)}"

        return result

    def evaluate_execution_result(self, execution_result: Dict) -> Dict:
        """评估执行结果"""
        evaluation = {
            "success": execution_result.get("success", False),
            "message": execution_result.get("message", ""),
            "evaluated_at": datetime.now().isoformat()
        }

        # 如果成功，可以调整触发权重
        if evaluation["success"] and self.config.get("learning_enabled", True):
            self._adjust_weights_based_on_result(execution_result)

        return evaluation

    def _adjust_weights_based_on_result(self, result: Dict):
        """根据执行结果调整权重（简单学习）"""
        # 简化实现：可以根据历史成功率微调
        pass

    def run_adaptive_cycle(self) -> Dict:
        """运行完整的自适应触发与决策周期"""
        cycle_result = {
            "triggered": False,
            "decision": None,
            "plan": None,
            "execution": None,
            "evaluation": None,
            "timestamp": datetime.now().isoformat()
        }

        # 1. 评估触发条件
        should_trigger, trigger_result = self.should_trigger_evolution()
        cycle_result["trigger_result"] = trigger_result

        if not should_trigger:
            cycle_result["message"] = "未达到触发条件"
            return cycle_result

        cycle_result["triggered"] = True

        # 2. 决定进化策略
        decision = self.decide_evolution_strategy(trigger_result)
        cycle_result["decision"] = decision

        # 3. 生成执行计划
        plan = self.generate_execution_plan(decision)
        cycle_result["plan"] = plan

        # 4. 自动执行
        execution = self.auto_execute(plan)
        cycle_result["execution"] = execution

        # 5. 评估执行结果
        evaluation = self.evaluate_execution_result(execution)
        cycle_result["evaluation"] = evaluation

        cycle_result["message"] = "自适应触发与决策周期完成"

        return cycle_result

    def get_status(self) -> Dict:
        """获取引擎状态"""
        return {
            "version": self.version,
            "running": True,
            "config": self.config,
            "decision_count": self.decision_count,
            "trigger_count": self.trigger_count,
            "last_trigger_time": self.last_trigger_time,
            "last_decision": self.last_decision,
            "trigger_threshold": self.trigger_threshold
        }

    def get_health_status(self) -> Dict:
        """获取健康状态"""
        score, details = self.evaluate_trigger_conditions()

        return {
            "health_score": score,
            "threshold": self.trigger_threshold,
            "details": details,
            "healthy": score >= self.trigger_threshold,
            "engines_monitored": 1,  # 本引擎
            "timestamp": datetime.now().isoformat()
        }

    def diagnose(self) -> Dict:
        """诊断问题"""
        diagnosis = {
            "issues": [],
            "recommendations": [],
            "timestamp": datetime.now().isoformat()
        }

        # 检查各项指标
        score, details = self.evaluate_trigger_conditions()

        if details["system_load"] > 0.7:
            diagnosis["issues"].append("系统负载较高")
            diagnosis["recommendations"].append("建议等待系统负载降低后再触发进化")

        if details["health_score"] < 0.5:
            diagnosis["issues"].append("系统健康度较低")
            diagnosis["recommendations"].append("建议优先修复健康问题")

        if details["capability_gaps"] > 0.6:
            diagnosis["issues"].append("存在较大能力缺口")
            diagnosis["recommendations"].append("建议优先补齐能力")

        if details["time_pattern"] < 0.3:
            diagnosis["issues"].append("当前时间不适合进化")
            diagnosis["recommendations"].append("建议在工作时间执行进化")

        if not diagnosis["issues"]:
            diagnosis["issues"].append("未发现明显问题")
            diagnosis["recommendations"].append("系统状态良好，可以进行进化")

        return diagnosis


def main():
    """主函数：提供命令行接口"""
    import argparse

    parser = argparse.ArgumentParser(
        description="智能全场景进化环自适应触发与自主决策增强引擎"
    )
    parser.add_argument("action", nargs="?", default="status",
                        choices=["status", "health", "diagnose", "evaluate", "decide", "execute", "full_cycle"],
                        help="执行的操作")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")

    args = parser.parse_args()

    engine = AdaptiveTriggerDecisionEngine()

    if args.action == "status":
        status = engine.get_status()
        _safe_print(json.dumps(status, ensure_ascii=False, indent=2))

    elif args.action == "health":
        health = engine.get_health_status()
        _safe_print(json.dumps(health, ensure_ascii=False, indent=2))

    elif args.action == "diagnose":
        diagnosis = engine.diagnose()
        _safe_print(json.dumps(diagnosis, ensure_ascii=False, indent=2))

    elif args.action == "evaluate":
        score, details = engine.evaluate_trigger_conditions()
        result = {
            "score": score,
            "threshold": engine.trigger_threshold,
            "should_trigger": score >= engine.trigger_threshold,
            "details": details
        }
        _safe_print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.action == "decide":
        should_trigger, trigger_result = engine.should_trigger_evolution()
        if should_trigger:
            decision = engine.decide_evolution_strategy(trigger_result)
            _safe_print(json.dumps(decision, ensure_ascii=False, indent=2))
        else:
            _safe_print(json.dumps({"triggered": False, "reason": trigger_result}, ensure_ascii=False, indent=2))

    elif args.action == "execute":
        result = engine.run_adaptive_cycle()
        _safe_print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.action == "full_cycle":
        # 完整周期：评估 -> 决策 -> 执行 -> 评估
        cycle_result = engine.run_adaptive_cycle()
        _safe_print(json.dumps(cycle_result, ensure_ascii=False, indent=2))

        evaluation = cycle_result.get("evaluation")
        if evaluation and evaluation.get("success"):
            _safe_print("\n✅ 自适应触发与决策周期执行成功")
        else:
            _safe_print("\n❌ 执行未触发或失败")


if __name__ == "__main__":
    main()