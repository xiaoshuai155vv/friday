#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能进化闭环自动集成执行引擎 (Evolution Auto-Integrated Executor)
让系统能够自动将自我优化引擎的分析结果和优化建议集成到进化决策与执行流程中，
形成「自我分析→自动优化→智能决策→自动执行→效果验证→再优化」的完整闭环，
实现真正的自主迭代进化。

功能：
1. 自我优化结果自动获取 - 调用 evolution_loop_self_optimizer 获取分析和建议
2. 优化建议智能筛选 - 评估哪些建议值得执行
3. 自动决策集成 - 将优化决策融入进化环决策流程
4. 执行效果追踪 - 追踪优化执行的效果
5. 闭环反馈 - 将执行结果反馈给自我优化引擎

集成：支持"进化自动集成"、"集成优化"、"闭环执行"等关键词触发
"""

import os
import sys
import json
import glob
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

SCRIPTS = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(SCRIPTS)
RUNTIME_STATE = os.path.join(PROJECT, "runtime", "state")
RUNTIME_LOGS = os.path.join(PROJECT, "runtime", "logs")
REFERENCES = os.path.join(PROJECT, "references")

# 尝试导入自我优化引擎
try:
    sys.path.insert(0, SCRIPTS)
    from evolution_loop_self_optimizer import EvolutionLoopSelfOptimizer
    SELF_OPTIMIZER_AVAILABLE = True
except ImportError:
    SELF_OPTIMIZER_AVAILABLE = False


class EvolutionAutoIntegratedExecutor:
    """智能进化闭环自动集成执行引擎"""

    def __init__(self):
        self.name = "EvolutionAutoIntegratedExecutor"
        self.version = "1.0.0"
        self.config_path = os.path.join(RUNTIME_STATE, "evolution_auto_integrated_config.json")
        self.execution_history_path = os.path.join(RUNTIME_STATE, "evolution_auto_integrated_history.json")
        self.current_execution_path = os.path.join(RUNTIME_STATE, "evolution_auto_integrated_current.json")

        self.config = self._load_config()
        self.execution_history = self._load_execution_history()
        self.self_optimizer = None

        if SELF_OPTIMIZER_AVAILABLE:
            try:
                self.self_optimizer = EvolutionLoopSelfOptimizer()
            except Exception as e:
                print(f"警告: 无法初始化自我优化引擎: {e}")

    def _load_config(self) -> Dict:
        """加载配置"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass

        # 默认配置
        return {
            "integration_settings": {
                "auto_fetch_recommendations": True,  # 自动获取建议
                "auto_evaluate": True,  # 自动评估建议
                "auto_integrate": True,  # 自动集成到决策
                "auto_execute": False,  # 自动执行（默认关闭，需确认）
                "confirm_before_execute": True,  # 执行前确认
                "min_confidence_threshold": 0.6  # 最小置信度阈值
            },
            "evaluation_criteria": {
                "min_priority_score": 0.7,  # 最小优先级分数
                "consider_trend": True,  # 考虑趋势
                "consider_success_rate": True,  # 考虑成功率
                "consider_execution_complexity": True  # 考虑执行复杂度
            },
            "execution_settings": {
                "track_effects": True,  # 追踪效果
                "feedback_to_optimizer": True,  # 反馈给优化引擎
                "max_execution_time": 300,  # 最大执行时间（秒）
                "retry_on_failure": True,  # 失败重试
                "max_retries": 2  # 最大重试次数
            },
            "last_integration_time": None,
            "total_integrations": 0,
            "successful_integrations": 0
        }

    def _save_config(self):
        """保存配置"""
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存配置失败: {e}")

    def _load_execution_history(self) -> List[Dict]:
        """加载执行历史"""
        if os.path.exists(self.execution_history_path):
            try:
                with open(self.execution_history_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return []

    def _save_execution_history(self):
        """保存执行历史"""
        try:
            with open(self.execution_history_path, "w", encoding="utf-8") as f:
                json.dump(self.execution_history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存执行历史失败: {e}")

    def fetch_self_optimizer_recommendations(self) -> Dict[str, Any]:
        """获取自我优化引擎的建议"""
        if not self.self_optimizer:
            return {
                "status": "error",
                "message": "自我优化引擎不可用"
            }

        try:
            recommendations = self.self_optimizer.get_recommendations_for_next_round()
            return {
                "status": "success",
                "recommendations": recommendations,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"获取建议失败: {str(e)}"
            }

    def fetch_self_optimizer_status(self) -> Dict[str, Any]:
        """获取自我优化引擎状态"""
        if not self.self_optimizer:
            return {
                "status": "error",
                "message": "自我优化引擎不可用"
            }

        try:
            status = self.self_optimizer.get_self_optimization_status()
            return {
                "status": "success",
                "status_data": status,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"获取状态失败: {str(e)}"
            }

    def evaluate_recommendations(self, recommendations: Dict) -> Dict[str, Any]:
        """评估建议并筛选"""
        if recommendations.get("status") != "success":
            return {
                "status": "no_recommendations",
                "message": "无有效建议"
            }

        recs = recommendations.get("recommendations", {})
        current_status = recs.get("current_status", {})

        # 评估标准
        evaluated = []
        min_score = self.config["evaluation_criteria"]["min_priority_score"]

        for rec in recs.get("recommendations", []):
            score = self._calculate_recommendation_score(rec, current_status)

            if score >= min_score:
                evaluated.append({
                    "recommendation": rec,
                    "score": score,
                    "approved": True
                })
            else:
                evaluated.append({
                    "recommendation": rec,
                    "score": score,
                    "approved": False,
                    "reason": f"分数 {score:.2f} 低于阈值 {min_score}"
                })

        # 按分数排序
        evaluated.sort(key=lambda x: x["score"], reverse=True)

        # 筛选批准的建议
        approved = [e for e in evaluated if e["approved"]]

        return {
            "status": "ready",
            "total_count": len(evaluated),
            "approved_count": len(approved),
            "evaluated": evaluated,
            "approved": approved,
            "timestamp": datetime.now().isoformat()
        }

    def _calculate_recommendation_score(self, recommendation: Dict, current_status: Dict) -> float:
        """计算建议得分"""
        score = 0.5  # 基础分数

        rec_type = recommendation.get("type", "")

        # 类型加分
        if rec_type == "priority_action":
            score += 0.3
        elif rec_type == "auto_executable":
            score += 0.2

        # 趋势影响
        trend = current_status.get("trend", "unknown")
        if trend == "improving":
            score += 0.1
        elif trend == "declining":
            score += 0.2  # 下降趋势需要更多关注

        # 成功率影响
        success_rate = current_status.get("success_rate", 0.5)
        if success_rate < 0.5:
            score += 0.15  # 低成功率需要优化

        # 优化必要性
        if current_status.get("optimization_needed", False):
            score += 0.15

        return min(score, 1.0)  # 最高1.0

    def integrate_into_decision(self, evaluation: Dict) -> Dict[str, Any]:
        """将评估结果集成到进化决策"""
        if evaluation.get("status") != "ready":
            return {
                "status": "no_integration",
                "message": "无批准的建议需要集成"
            }

        approved = evaluation.get("approved", [])
        if not approved:
            return {
                "status": "no_integration",
                "message": "无批准的建议"
            }

        # 选择最高分的建议
        best = approved[0]
        rec = best["recommendation"]

        integration = {
            "selected_recommendation": rec,
            "score": best["score"],
            "integration_reason": f"最高得分 {best['score']:.2f}",
            "decision": self._generate_integration_decision(rec),
            "timestamp": datetime.now().isoformat()
        }

        # 保存当前执行信息
        try:
            with open(self.current_execution_path, "w", encoding="utf-8") as f:
                json.dump(integration, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存当前执行信息失败: {e}")

        return {
            "status": "integrated",
            "integration": integration,
            "timestamp": datetime.now().isoformat()
        }

    def _generate_integration_decision(self, recommendation: Dict) -> Dict[str, Any]:
        """生成集成决策"""
        rec_type = recommendation.get("type", "")
        description = recommendation.get("description", "")

        if rec_type == "priority_action":
            action = recommendation.get("action", "")
            return {
                "action_type": "execute_action",
                "description": description,
                "execution_plan": self._plan_execution(action),
                "priority": "high"
            }
        elif rec_type == "auto_executable":
            return {
                "action_type": "auto_execute",
                "description": description,
                "execution_plan": "调用自我优化引擎的执行接口",
                "priority": "medium"
            }
        else:
            return {
                "action_type": "review",
                "description": description,
                "execution_plan": "需要人工审查",
                "priority": "low"
            }

    def _plan_execution(self, action: str) -> str:
        """规划执行方案"""
        # 分析动作字符串，生成执行计划
        if "优化" in action or "调整" in action:
            return "调用自我优化引擎的参数调整功能"
        elif "分析" in action:
            return "执行进化执行效果分析"
        elif "执行" in action:
            return "执行优化建议"
        else:
            return f"执行动作: {action}"

    def execute_integration(self, integration: Dict = None) -> Dict[str, Any]:
        """执行集成（如果配置允许）"""
        if not integration:
            # 加载当前执行信息
            if os.path.exists(self.current_execution_path):
                try:
                    with open(self.current_execution_path, "r", encoding="utf-8") as f:
                        integration = json.load(f)
                except Exception:
                    pass
            else:
                return {
                    "status": "error",
                    "message": "无当前执行信息"
                }

        if not integration:
            return {
                "status": "error",
                "message": "无法加载执行信息"
            }

        decision = integration.get("decision", {})
        action_type = decision.get("action_type", "")

        # 检查是否需要确认
        if self.config["integration_settings"]["confirm_before_execute"]:
            if action_type == "execute_action" or action_type == "auto_execute":
                return {
                    "status": "pending_confirmation",
                    "message": "需要确认后执行",
                    "execution_plan": decision.get("execution_plan"),
                    "description": decision.get("description")
                }

        # 执行
        result = {
            "status": "executed",
            "action_type": action_type,
            "execution_plan": decision.get("execution_plan"),
            "description": decision.get("description"),
            "timestamp": datetime.now().isoformat()
        }

        # 如果自我优化引擎可用，可以调用其执行方法
        if self.self_optimizer and action_type == "auto_execute":
            try:
                exec_result = self.self_optimizer.execute_optimization()
                result["optimizer_result"] = exec_result
            except Exception as e:
                result["optimizer_error"] = str(e)

        # 记录到历史
        self.execution_history.append(result)
        if len(self.execution_history) > 100:
            self.execution_history = self.execution_history[-100:]
        self._save_execution_history()

        # 更新配置统计
        self.config["total_integrations"] += 1
        self.config["successful_integrations"] += 1
        self.config["last_integration_time"] = datetime.now().isoformat()
        self._save_config()

        return result

    def track_execution_effects(self) -> Dict[str, Any]:
        """追踪执行效果"""
        if not self.execution_history:
            return {
                "status": "no_history",
                "message": "无执行历史"
            }

        recent = self.execution_history[-10:]  # 最近10次

        # 统计
        total = len(recent)
        successful = sum(1 for r in recent if r.get("status") == "executed")

        return {
            "status": "ready",
            "recent_executions": total,
            "recent_success_rate": successful / total if total > 0 else 0,
            "total_integrations": self.config["total_integrations"],
            "total_success_rate": self.config["successful_integrations"] / self.config["total_integrations"] if self.config["total_integrations"] > 0 else 0,
            "last_integration_time": self.config.get("last_integration_time"),
            "timestamp": datetime.now().isoformat()
        }

    def feedback_to_optimizer(self, execution_result: Dict) -> Dict[str, Any]:
        """将执行结果反馈给自我优化引擎"""
        if not self.self_optimizer:
            return {
                "status": "skipped",
                "message": "自我优化引擎不可用"
            }

        # 创建反馈数据
        feedback = {
            "execution_result": execution_result,
            "timestamp": datetime.now().isoformat(),
            "source": "auto_integrated_executor"
        }

        # 保存反馈（自我优化引擎可以读取）
        feedback_path = os.path.join(RUNTIME_STATE, "evolution_optimizer_feedback.json")
        try:
            with open(feedback_path, "w", encoding="utf-8") as f:
                json.dump(feedback, f, ensure_ascii=False, indent=2)

            return {
                "status": "feedback_sent",
                "message": "执行结果已反馈给自我优化引擎",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"反馈失败: {str(e)}"
            }

    def run_full_integration_cycle(self) -> Dict[str, Any]:
        """运行完整的集成循环"""
        cycle_result = {
            "cycle_start": datetime.now().isoformat(),
            "steps": []
        }

        # 步骤1: 获取建议
        step1 = self.fetch_self_optimizer_recommendations()
        cycle_result["steps"].append({
            "step": "fetch_recommendations",
            "result": step1
        })

        if step1.get("status") != "success":
            cycle_result["status"] = "failed"
            cycle_result["error"] = "无法获取建议"
            cycle_result["cycle_end"] = datetime.now().isoformat()
            return cycle_result

        # 步骤2: 评估建议
        step2 = self.evaluate_recommendations(step1)
        cycle_result["steps"].append({
            "step": "evaluate_recommendations",
            "result": step2
        })

        if step2.get("status") != "ready":
            cycle_result["status"] = "no_approved"
            cycle_result["message"] = "无批准的建议"
            cycle_result["cycle_end"] = datetime.now().isoformat()
            return cycle_result

        # 步骤3: 集成到决策
        step3 = self.integrate_into_decision(step2)
        cycle_result["steps"].append({
            "step": "integrate_into_decision",
            "result": step3
        })

        if step3.get("status") != "integrated":
            cycle_result["status"] = "failed"
            cycle_result["error"] = "无法集成到决策"
            cycle_result["cycle_end"] = datetime.now().isoformat()
            return cycle_result

        # 步骤4: 执行集成（如果配置允许）
        if self.config["integration_settings"]["auto_execute"]:
            step4 = self.execute_integration(step3.get("integration"))
            cycle_result["steps"].append({
                "step": "execute_integration",
                "result": step4
            })

            # 步骤5: 反馈给优化引擎
            if self.config["execution_settings"]["feedback_to_optimizer"]:
                step5 = self.feedback_to_optimizer(step4)
                cycle_result["steps"].append({
                    "step": "feedback_to_optimizer",
                    "result": step5
                })

        cycle_result["status"] = "completed"
        cycle_result["cycle_end"] = datetime.now().isoformat()
        return cycle_result

    def get_status(self) -> Dict[str, Any]:
        """获取集成执行器状态"""
        status = {
            "name": self.name,
            "version": self.version,
            "self_optimizer_available": SELF_OPTIMIZER_AVAILABLE,
            "config": {
                "auto_fetch": self.config["integration_settings"]["auto_fetch_recommendations"],
                "auto_execute": self.config["integration_settings"]["auto_execute"],
                "confirm_before_execute": self.config["integration_settings"]["confirm_before_execute"]
            },
            "statistics": {
                "total_integrations": self.config["total_integrations"],
                "successful_integrations": self.config["successful_integrations"],
                "success_rate": self.config["successful_integrations"] / self.config["total_integrations"] if self.config["total_integrations"] > 0 else 0,
                "last_integration_time": self.config.get("last_integration_time")
            },
            "recent_history_count": len(self.execution_history[-10:]) if self.execution_history else 0,
            "timestamp": datetime.now().isoformat()
        }

        # 如果自我优化引擎可用，获取其状态
        if self.self_optimizer:
            try:
                optimizer_status = self.self_optimizer.get_self_optimization_status()
                status["optimizer_status"] = {
                    "success_rate": optimizer_status.get("analysis", {}).get("success_rate", 0),
                    "trend": optimizer_status.get("analysis", {}).get("trend", "unknown"),
                    "optimization_needed": optimizer_status.get("analysis", {}).get("optimization_needed", False)
                }
            except Exception:
                pass

        return status


def main():
    """主入口"""
    import argparse

    parser = argparse.ArgumentParser(description="智能进化闭环自动集成执行引擎")
    parser.add_argument("command", nargs="?", default="status",
                       help="命令: status|recommendations|evaluate|integrate|execute|track|feedback|full_cycle")
    parser.add_argument("--confirm", action="store_true", help="确认执行（用于需要确认的操作）")

    args = parser.parse_args()

    executor = EvolutionAutoIntegratedExecutor()

    if args.command == "status":
        result = executor.get_status()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "recommendations":
        result = executor.fetch_self_optimizer_recommendations()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "evaluate":
        # 先获取建议，再评估
        recs = executor.fetch_self_optimizer_recommendations()
        result = executor.evaluate_recommendations(recs)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "integrate":
        # 先获取建议，评估，再集成
        recs = executor.fetch_self_optimizer_recommendations()
        evaluation = executor.evaluate_recommendations(recs)
        result = executor.integrate_into_decision(evaluation)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "execute":
        # 如果需要确认
        if args.confirm:
            executor.config["integration_settings"]["confirm_before_execute"] = False
            executor._save_config()

        result = executor.execute_integration()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "track":
        result = executor.track_execution_effects()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "feedback":
        # 使用最近一次执行结果反馈
        if executor.execution_history:
            last_result = executor.execution_history[-1]
            result = executor.feedback_to_optimizer(last_result)
        else:
            result = {"status": "error", "message": "无执行历史"}
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "full_cycle":
        result = executor.run_full_integration_cycle()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    else:
        print(f"未知命令: {args.command}")
        print("可用命令: status, recommendations, evaluate, integrate, execute, track, feedback, full_cycle")


if __name__ == "__main__":
    main()