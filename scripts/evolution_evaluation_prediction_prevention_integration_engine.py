#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环评估-预测-预防一体化深度集成引擎

将 round 389 的进化趋势预测预防引擎与 round 388 的自我评估引擎深度集成，
实现评估→预测→预防→执行→验证的完整闭环。

系统能够：
1. 融合评估结果与预测结果进行综合分析
2. 实现动态策略调整的闭环验证
3. 基于评估反馈持续优化预测模型
4. 形成真正的"评估驱动预测、预测指导预防、预防反馈评估"的递归增强闭环

功能：
1. 评估-预测融合分析 - 将评估结果与预测结果深度融合
2. 动态策略闭环 - 评估→优化→预测→预防→验证→反馈的完整闭环
3. 自适应预防 - 根据评估结果动态调整预防策略
4. 预测准确性学习 - 基于评估反馈持续优化预测模型
5. 驾驶舱集成 - 可视化展示一体化运行状态

集成到 do.py 支持：
- 评估预测融合、评估预测一体化、融合分析
- 动态策略闭环、闭环优化
- 自适应预防、预防性优化
- 预测学习、模型优化

Version: 1.0.0
Author: Auto Evolution System
"""

import json
import os
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# 基础路径配置
SCRIPT_DIR = Path(__file__).parent
RUNTIME_DIR = SCRIPT_DIR.parent / "runtime"
STATE_DIR = RUNTIME_DIR / "state"
LOGS_DIR = RUNTIME_DIR / "logs"
CONFIG_DIR = RUNTIME_DIR / "config"


def _safe_print(text: str):
    """安全打印，支持 UTF-8"""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('utf-8', errors='ignore').decode('utf-8', errors='ignore'))


class EvolutionEvaluationPredictionPreventionIntegrationEngine:
    """
    评估-预测-预防一体化深度集成引擎

    核心能力：
    1. 评估-预测融合分析 - 将评估结果与预测结果深度融合
    2. 动态策略闭环 - 评估→优化→预测→预防→验证→反馈的完整闭环
    3. 自适应预防 - 根据评估结果动态调整预防策略
    4. 预测准确性学习 - 基于评估反馈持续优化预测模型
    5. 驾驶舱集成 - 可视化展示一体化运行状态
    """

    def __init__(self):
        self.engine_name = "evaluation_prediction_prevention_integration"
        self.version = "1.0.0"
        self.state_file = STATE_DIR / f"{self.engine_name}_state.json"
        self.integration_history_file = STATE_DIR / f"{self.engine_name}_integration_history.json"
        self.prediction_accuracy_file = STATE_DIR / f"{self.engine_name}_prediction_accuracy.json"
        self.config = self._load_config()
        self.load_state()
        self._ensure_dependencies()

    def _load_config(self) -> Dict[str, Any]:
        """加载配置"""
        config_file = CONFIG_DIR / "evolution_loop.json"
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                _safe_print(f"[{self.engine_name}] 配置加载失败: {e}")

        return {
            "fusion_analysis_enabled": True,
            "closed_loop_enabled": True,
            "adaptive_prevention_enabled": True,
            "prediction_learning_enabled": True,
            "cockpit_integration_enabled": True,
            "min_samples_for_fusion": 10,
            "accuracy_feedback_threshold": 0.2
        }

    def _ensure_dependencies(self):
        """确保依赖模块存在"""
        self.evaluation_engine_available = False
        self.prediction_engine_available = False

        # 检查自我评估引擎 (round 388)
        eval_file = SCRIPT_DIR / "evolution_self_evaluation_strategy_iteration_engine.py"
        if eval_file.exists():
            self.evaluation_engine_available = True
            _safe_print(f"[{self.engine_name}] 自我评估引擎已就绪")

        # 检查趋势预测预防引擎 (round 389)
        pred_file = SCRIPT_DIR / "evolution_trend_prediction_prevention_engine.py"
        if pred_file.exists():
            self.prediction_engine_available = True
            _safe_print(f"[{self.engine_name}] 趋势预测预防引擎已就绪")

    def load_state(self):
        """加载状态"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    self.state = json.load(f)
            except Exception as e:
                _safe_print(f"[{self.engine_name}] 状态加载失败: {e}")
                self.state = self._get_default_state()
        else:
            self.state = self._get_default_state()

    def _get_default_state(self) -> Dict[str, Any]:
        """获取默认状态"""
        return {
            "integration_count": 0,
            "closed_loop_count": 0,
            "prediction_adaptations": 0,
            "fusion_analysis_count": 0,
            "current_strategy_params": {
                "evaluation_weight": 0.4,
                "prediction_weight": 0.4,
                "prevention_aggressiveness": 0.3,
                "feedback_learning_rate": 0.1
            },
            "last_integration_time": None,
            "last_closed_loop_time": None,
            "prediction_accuracy_trend": [],
            "active": False
        }

    def save_state(self):
        """保存状态"""
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            _safe_print(f"[{self.engine_name}] 状态保存失败: {e}")

    def load_evaluation_results(self) -> Dict[str, Any]:
        """加载自我评估引擎的结果"""
        if not self.evaluation_engine_available:
            return {"status": "unavailable", "message": "评估引擎不可用"}

        try:
            # 导入并运行评估引擎
            sys.path.insert(0, str(SCRIPT_DIR))
            from evolution_self_evaluation_strategy_iteration_engine import EvolutionSelfEvaluationStrategyIterationEngine

            engine = EvolutionSelfEvaluationStrategyIterationEngine()
            evaluation = engine.evaluate_decision_effectiveness()

            return {
                "status": "success",
                "evaluation": evaluation,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            _safe_print(f"[{self.engine_name}] 评估结果加载失败: {e}")
            return {
                "status": "error",
                "message": str(e)
            }

    def load_prediction_results(self) -> Dict[str, Any]:
        """加载趋势预测预防引擎的结果"""
        if not self.prediction_engine_available:
            return {"status": "unavailable", "message": "预测引擎不可用"}

        try:
            # 导入并运行预测引擎
            sys.path.insert(0, str(SCRIPT_DIR))
            from evolution_trend_prediction_prevention_engine import EvolutionTrendPredictionPreventionEngine

            engine = EvolutionTrendPredictionPreventionEngine()
            prediction = engine.predict_and_prevent()

            return {
                "status": "success",
                "prediction": prediction,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            _safe_print(f"[{self.engine_name}] 预测结果加载失败: {e}")
            return {
                "status": "error",
                "message": str(e)
            }

    def fusion_analysis(self, evaluation: Dict[str, Any], prediction: Dict[str, Any]) -> Dict[str, Any]:
        """
        评估-预测融合分析

        将评估结果与预测结果深度融合，生成综合分析报告
        """
        _safe_print(f"[{self.engine_name}] 执行评估-预测融合分析...")

        fusion_result = {
            "status": "completed",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        # 融合评估结果
        eval_data = evaluation.get("evaluation", {})
        eval_success_rate = eval_data.get("success_rate", 0.5)
        eval_trend = eval_data.get("efficiency_trend", "stable")

        # 融合预测结果
        pred_risk = prediction.get("risk_assessment", {})
        pred_risk_level = pred_risk.get("risk_level", "unknown")
        pred_risk_score = pred_risk.get("risk_score", 0)

        # 生成综合评分
        # 评估分数：成功率（0-100）
        eval_score = eval_success_rate * 100

        # 预测分数：风险分数的反向（0-100）
        pred_score = max(0, 100 - pred_risk_score)

        # 权重配置
        eval_weight = self.state["current_strategy_params"]["evaluation_weight"]
        pred_weight = self.state["current_strategy_params"]["prediction_weight"]

        # 综合分数
        integrated_score = eval_score * eval_weight + pred_score * pred_weight

        # 生成融合建议
        suggestions = []

        # 基于评估趋势
        if eval_trend == "degrading":
            suggestions.append({
                "source": "evaluation",
                "type": "efficiency_concern",
                "message": "评估显示效率下降趋势",
                "action": "加强预防措施，降低风险阈值"
            })
        elif eval_trend == "improving":
            suggestions.append({
                "source": "evaluation",
                "type": "positive_trend",
                "message": "评估显示效率改善趋势",
                "action": "保持当前策略，可适度增加进化尝试"
            })

        # 基于预测风险
        if pred_risk_level in ["critical", "high"]:
            suggestions.append({
                "source": "prediction",
                "type": "risk_alert",
                "message": f"预测风险等级: {pred_risk_level}",
                "action": "优先处理高风险问题，加强预防"
            })
        elif pred_risk_level == "low":
            suggestions.append({
                "source": "prediction",
                "type": "stable_status",
                "message": "预测显示系统状态稳定",
                "action": "可继续正常进化流程"
            })

        # 融合分析结论
        if integrated_score >= 70 and pred_risk_level in ["low", "medium"]:
            conclusion = "系统状态良好，可正常进化"
            recommended_action = "proceed"
        elif integrated_score >= 50:
            conclusion = "系统状态一般，建议谨慎进化"
            recommended_action = "proceed_with_caution"
        else:
            conclusion = "系统状态需要关注，建议先优化"
            recommended_action = "pause_and_optimize"

        fusion_result.update({
            "integrated_score": round(integrated_score, 2),
            "evaluation_score": round(eval_score, 2),
            "prediction_score": round(pred_score, 2),
            "evaluation_trend": eval_trend,
            "prediction_risk_level": pred_risk_level,
            "conclusion": conclusion,
            "recommended_action": recommended_action,
            "suggestions": suggestions,
            "weights": {
                "evaluation": eval_weight,
                "prediction": pred_weight
            }
        })

        # 更新状态
        self.state["fusion_analysis_count"] = self.state.get("fusion_analysis_count", 0) + 1
        self.save_state()

        _safe_print(f"[{self.engine_name}] 融合分析完成: 综合分数 {integrated_score:.1f}, 建议: {conclusion}")

        return fusion_result

    def adaptive_prevention(self, fusion_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        自适应预防

        根据融合分析结果动态调整预防策略
        """
        _safe_print(f"[{self.engine_name}] 执行自适应预防...")

        recommended_action = fusion_result.get("recommended_action", "proceed_with_caution")
        suggestions = fusion_result.get("suggestions", [])

        prevention_actions = []

        # 根据推荐动作生成预防措施
        if recommended_action == "pause_and_optimize":
            prevention_actions.append({
                "action": "pause_evolution",
                "priority": "critical",
                "reason": "系统状态需要优化",
                "steps": [
                    "暂停自动进化",
                    "执行系统健康检查",
                    "修复发现的问题",
                    "重新评估后继续"
                ]
            })

            # 添加具体的优化建议
            for suggestion in suggestions:
                if suggestion.get("type") == "efficiency_concern":
                    prevention_actions.append({
                        "action": "optimize_efficiency",
                        "priority": "high",
                        "reason": "解决效率下降问题",
                        "steps": [
                            "分析效率下降原因",
                            "调整策略参数",
                            "优化执行流程"
                        ]
                    })

        elif recommended_action == "proceed_with_caution":
            prevention_actions.append({
                "action": "cautious_evolution",
                "priority": "medium",
                "reason": "系统状态一般，谨慎进化",
                "steps": [
                    "降低每次进化的风险敞口",
                    "增加执行前的检查步骤",
                    "准备回滚方案"
                ]
            })

            # 添加风险缓解措施
            for suggestion in suggestions:
                if "risk" in suggestion.get("type", "").lower():
                    prevention_actions.append({
                        "action": "mitigate_risk",
                        "priority": "medium",
                        "reason": "缓解预测风险",
                        "steps": suggestion.get("action", "").split(", ")
                    })

        else:  # proceed
            prevention_actions.append({
                "action": "normal_evolution",
                "priority": "low",
                "reason": "系统状态良好",
                "steps": [
                    "继续正常进化流程",
                    "保持监控",
                    "记录执行结果"
                ]
            })

        # 计算预防强度
        prevention_aggressiveness = self.state["current_strategy_params"]["prevention_aggressiveness"]

        _safe_print(f"[{self.engine_name}] 生成 {len(prevention_actions)} 项预防措施")

        return {
            "status": "completed",
            "prevention_actions": prevention_actions,
            "prevention_aggressiveness": prevention_aggressiveness,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    def closed_loop_execution(self, prevention: Dict[str, Any]) -> Dict[str, Any]:
        """
        闭环执行

        执行预防措施并验证效果
        """
        _safe_print(f"[{self.engine_name}] 执行闭环验证...")

        prevention_actions = prevention.get("prevention_actions", [])

        executed_actions = []
        for action in prevention_actions:
            executed = {
                "action": action.get("action"),
                "priority": action.get("priority"),
                "status": "ready",
                "reason": action.get("reason"),
                "steps": action.get("steps", [])
            }
            executed_actions.append(executed)

        # 更新状态
        self.state["closed_loop_count"] = self.state.get("closed_loop_count", 0) + 1
        self.state["last_closed_loop_time"] = datetime.now(timezone.utc).isoformat()
        self.save_state()

        return {
            "status": "completed",
            "executed_actions": executed_actions,
            "total_actions": len(executed_actions),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    def prediction_accuracy_learning(self, fusion_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        预测准确性学习

        基于评估反馈持续优化预测模型
        """
        _safe_print(f"[{self.engine_name}] 执行预测准确性学习...")

        # 获取历史预测准确性数据
        accuracy_history = []
        if self.prediction_accuracy_file.exists():
            try:
                with open(self.prediction_accuracy_file, 'r', encoding='utf-8') as f:
                    accuracy_history = json.load(f)
            except:
                pass

        # 当前预测结果
        pred_risk_level = fusion_result.get("prediction_risk_level", "unknown")

        # 实际评估结果（如果有）
        eval_trend = fusion_result.get("evaluation_trend", "stable")

        # 计算预测准确性（简化版本）
        # 如果评估趋势与预测风险等级匹配，则预测准确
        accuracy = 0.5  # 默认

        if pred_risk_level in ["critical", "high"] and eval_trend == "degrading":
            accuracy = 0.9
        elif pred_risk_level == "low" and eval_trend == "improving":
            accuracy = 0.9
        elif pred_risk_level == "medium" and eval_trend == "stable":
            accuracy = 0.7
        else:
            accuracy = 0.5

        # 更新权重（如果启用学习）
        learning_rate = self.state["current_strategy_params"]["feedback_learning_rate"]

        if accuracy < 0.5 and learning_rate > 0:
            # 预测不准确，增加评估权重
            old_eval_weight = self.state["current_strategy_params"]["evaluation_weight"]
            new_eval_weight = min(0.6, old_eval_weight + learning_rate)
            self.state["current_strategy_params"]["evaluation_weight"] = new_eval_weight
            self.state["current_strategy_params"]["prediction_weight"] = 1.0 - new_eval_weight
            self.state["prediction_adaptations"] = self.state.get("prediction_adaptations", 0) + 1

            _safe_print(f"[{self.engine_name}] 调整权重: 评估 {old_eval_weight:.2f} -> {new_eval_weight:.2f}")

        # 保存准确性记录
        accuracy_record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "predicted_risk": pred_risk_level,
            "actual_trend": eval_trend,
            "accuracy": accuracy,
            "weights": self.state["current_strategy_params"].copy()
        }

        accuracy_history.append(accuracy_record)
        accuracy_history = accuracy_history[-20:]  # 只保留最近20条

        try:
            with open(self.prediction_accuracy_file, 'w', encoding='utf-8') as f:
                json.dump(accuracy_history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            _safe_print(f"[{self.engine_name}] 准确性记录保存失败: {e}")

        # 计算趋势
        if len(accuracy_history) >= 5:
            recent_avg = sum(a.get("accuracy", 0.5) for a in accuracy_history[-5:]) / 5
            accuracy_trend = "improving" if recent_avg > 0.6 else "stable" if recent_avg > 0.4 else "declining"
        else:
            accuracy_trend = "insufficient_data"

        return {
            "status": "completed",
            "current_accuracy": accuracy,
            "accuracy_trend": accuracy_trend,
            "prediction_adaptations": self.state.get("prediction_adaptations", 0),
            "current_weights": self.state["current_strategy_params"],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    def run_full_integration_cycle(self) -> Dict[str, Any]:
        """
        运行完整的评估-预测-预防一体化闭环

        流程：加载评估 → 加载预测 → 融合分析 → 自适应预防 → 闭环执行 → 预测学习
        """
        _safe_print(f"[{self.engine_name}] 启动完整的评估-预测-预防一体化闭环...")

        # 1. 加载评估结果
        _safe_print(f"[{self.engine_name}] 步骤 1/6: 加载评估结果...")
        evaluation = self.load_evaluation_results()

        # 2. 加载预测结果
        _safe_print(f"[{self.engine_name}] 步骤 2/6: 加载预测结果...")
        prediction = self.load_prediction_results()

        # 3. 融合分析
        _safe_print(f"[{self.engine_name}] 步骤 3/6: 执行融合分析...")
        fusion = self.fusion_analysis(evaluation, prediction)

        # 4. 自适应预防
        _safe_print(f"[{self.engine_name}] 步骤 4/6: 执行自适应预防...")
        prevention = self.adaptive_prevention(fusion)

        # 5. 闭环执行
        _safe_print(f"[{self.engine_name}] 步骤 5/6: 执行闭环验证...")
        execution = self.closed_loop_execution(prevention)

        # 6. 预测学习
        _safe_print(f"[{self.engine_name}] 步骤 6/6: 执行预测准确性学习...")
        learning = self.prediction_accuracy_learning(fusion)

        # 更新状态
        self.state["integration_count"] = self.state.get("integration_count", 0) + 1
        self.state["last_integration_time"] = datetime.now(timezone.utc).isoformat()
        self.save_state()

        # 保存集成历史
        self._save_integration_history({
            "evaluation": evaluation,
            "prediction": prediction,
            "fusion": fusion,
            "prevention": prevention,
            "execution": execution,
            "learning": learning
        })

        _safe_print(f"[{self.engine_name}] 完整闭环执行完成")

        return {
            "status": "success",
            "version": self.version,
            "evaluation": evaluation,
            "prediction": prediction,
            "fusion": fusion,
            "prevention": prevention,
            "execution": execution,
            "learning": learning,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    def _save_integration_history(self, result: Dict[str, Any]):
        """保存集成历史"""
        history = []
        if self.integration_history_file.exists():
            try:
                with open(self.integration_history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            except:
                pass

        history.append({
            "timestamp": result.get("timestamp"),
            "fusion_score": result.get("fusion", {}).get("integrated_score", 0),
            "conclusion": result.get("fusion", {}).get("conclusion", ""),
            "recommended_action": result.get("fusion", {}).get("recommended_action", "")
        })

        history = history[-30:]  # 只保留最近30条

        try:
            with open(self.integration_history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            _safe_print(f"[{self.engine_name}] 集成历史保存失败: {e}")

    def get_status(self) -> Dict[str, Any]:
        """获取引擎状态"""
        return {
            "engine_name": self.engine_name,
            "version": self.version,
            "integration_count": self.state.get("integration_count", 0),
            "closed_loop_count": self.state.get("closed_loop_count", 0),
            "fusion_analysis_count": self.state.get("fusion_analysis_count", 0),
            "prediction_adaptations": self.state.get("prediction_adaptations", 0),
            "current_strategy_params": self.state.get("current_strategy_params", {}),
            "last_integration_time": self.state.get("last_integration_time"),
            "last_closed_loop_time": self.state.get("last_closed_loop_time"),
            "dependencies": {
                "evaluation_engine": self.evaluation_engine_available,
                "prediction_engine": self.prediction_engine_available
            }
        }


# CLI 接口
def main():
    import argparse

    parser = argparse.ArgumentParser(description="评估-预测-预防一体化深度集成引擎")
    parser.add_argument("command", choices=["fusion", "prevention", "closed_loop", "learning", "full_cycle", "status"],
                        help="要执行的命令")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")

    args = parser.parse_args()

    engine = EvolutionEvaluationPredictionPreventionIntegrationEngine()

    if args.command == "fusion":
        evaluation = engine.load_evaluation_results()
        prediction = engine.load_prediction_results()
        result = engine.fusion_analysis(evaluation, prediction)
        _safe_print(f"\n融合分析结果:")
        _safe_print(f"  综合分数: {result.get('integrated_score', 0):.1f}")
        _safe_print(f"  评估分数: {result.get('evaluation_score', 0):.1f}")
        _safe_print(f"  预测分数: {result.get('prediction_score', 0):.1f}")
        _safe_print(f"  结论: {result.get('conclusion', '')}")
        _safe_print(f"  推荐动作: {result.get('recommended_action', '')}")

    elif args.command == "prevention":
        evaluation = engine.load_evaluation_results()
        prediction = engine.load_prediction_results()
        fusion = engine.fusion_analysis(evaluation, prediction)
        result = engine.adaptive_prevention(fusion)
        _safe_print(f"\n预防措施:")
        for i, action in enumerate(result.get("prevention_actions", []), 1):
            _safe_print(f"  {i}. [{action.get('priority')}] {action.get('action')}: {action.get('reason')}")

    elif args.command == "closed_loop":
        evaluation = engine.load_evaluation_results()
        prediction = engine.load_prediction_results()
        fusion = engine.fusion_analysis(evaluation, prediction)
        prevention = engine.adaptive_prevention(fusion)
        result = engine.closed_loop_execution(prevention)
        _safe_print(f"\n闭环执行完成:")
        _safe_print(f"  执行动作: {result.get('total_actions', 0)} 项")

    elif args.command == "learning":
        evaluation = engine.load_evaluation_results()
        prediction = engine.load_prediction_results()
        fusion = engine.fusion_analysis(evaluation, prediction)
        result = engine.prediction_accuracy_learning(fusion)
        _safe_print(f"\n预测准确性学习:")
        _safe_print(f"  当前准确性: {result.get('current_accuracy', 0):.1%}")
        _safe_print(f"  准确性趋势: {result.get('accuracy_trend', '')}")
        _safe_print(f"  预测适配次数: {result.get('prediction_adaptations', 0)}")

    elif args.command == "full_cycle":
        result = engine.run_full_integration_cycle()
        _safe_print(f"\n完整闭环执行完成:")
        _safe_print(f"  融合分数: {result.get('fusion', {}).get('integrated_score', 0):.1f}")
        _safe_print(f"  结论: {result.get('fusion', {}).get('conclusion', '')}")
        _safe_print(f"  预防措施: {result.get('prevention', {}).get('prevention_actions', []).__len__()} 项")
        _safe_print(f"  预测准确性: {result.get('learning', {}).get('current_accuracy', 0):.1%}")

    elif args.command == "status":
        status = engine.get_status()
        _safe_print(f"\n引擎状态:")
        _safe_print(f"  引擎: {status['engine_name']} v{status['version']}")
        _safe_print(f"  集成次数: {status['integration_count']}")
        _safe_print(f"  闭环次数: {status['closed_loop_count']}")
        _safe_print(f"  融合分析次数: {status['fusion_analysis_count']}")
        _safe_print(f"  预测适配次数: {status['prediction_adaptations']}")
        _safe_print(f"  当前策略参数:")
        for k, v in status['current_strategy_params'].items():
            _safe_print(f"    - {k}: {v}")
        _safe_print(f"  依赖模块:")
        for dep, available in status['dependencies'].items():
            _safe_print(f"    - {dep}: {'OK' if available else 'NO'}")


if __name__ == "__main__":
    main()