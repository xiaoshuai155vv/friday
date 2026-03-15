#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景进化环跨引擎知识自动推荐与智能预测触发引擎
=============================================================
在 round 489 完成的跨引擎深度知识蒸馏与智能传承增强引擎基础上，
进一步增强知识自动推荐与智能预测触发能力。

让系统能够基于当前上下文主动推荐相关知识、预测用户潜在需求、
智能触发知识准备，实现从「被动响应查询」到「主动预测并推送」的范式升级。

功能：
1. 知识自动推荐增强 - 基于上下文、历史行为、实时状态
2. 用户需求智能预测 - 预测用户下一步可能需要的知识
3. 知识预触发与自动准备 - 提前加载可能需要的知识
4. 智能触发机制 - 条件满足时自动推送知识
5. 与进化驾驶舱深度集成
6. 集成到 do.py 支持知识推荐、智能预测、主动推送等关键词触发

version: 1.0.0
"""

import os
import sys
import json
import re
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
from collections import defaultdict
import threading

# 解决 Windows 控制台 Unicode 输出问题
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# 路径配置
BASE_DIR = Path(__file__).parent.parent
RUNTIME_DIR = BASE_DIR / "runtime"
STATE_DIR = RUNTIME_DIR / "state"
KNOWLEDGE_DIR = RUNTIME_DIR / "knowledge"
LOGS_DIR = RUNTIME_DIR / "logs"

# 存储文件路径
PREDICTION_HISTORY_FILE = STATE_DIR / "knowledge_prediction_history.json"
PREDICTION_MODEL_FILE = STATE_DIR / "knowledge_prediction_model.json"
PREPARE_QUEUE_FILE = STATE_DIR / "knowledge_prepare_queue.json"
TRIGGER_CONFIG_FILE = STATE_DIR / "knowledge_trigger_config.json"


def _safe_print(text: str):
    """安全打印"""
    try:
        print(text)
    except UnicodeEncodeError:
        clean_text = re.sub(r'[^\x00-\x7F]+', '', text)
        print(clean_text)


class KnowledgeProactiveRecommendationPredictionEngine:
    """跨引擎知识自动推荐与智能预测触发引擎"""

    def __init__(self):
        self.version = "1.0.0"
        self.engine_name = "跨引擎知识自动推荐与智能预测触发引擎"

        # 确保目录存在
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)

        # 加载数据
        self.prediction_history = self._load_prediction_history()
        self.prediction_model = self._load_prediction_model()
        self.prepare_queue = self._load_prepare_queue()
        self.trigger_config = self._load_trigger_config()

        # 知识缓存
        self.knowledge_cache = {}

        # 预测模式（从历史中学习）
        self.patterns = self._load_patterns()

        _safe_print(f"[{self.engine_name} v{self.version}] 初始化完成")

    def _load_prediction_history(self) -> Dict:
        """加载预测历史"""
        if PREDICTION_HISTORY_FILE.exists():
            try:
                with open(PREDICTION_HISTORY_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {"predictions": [], "feedback": []}
        return {"predictions": [], "feedback": []}

    def _save_prediction_history(self):
        """保存预测历史"""
        try:
            with open(PREDICTION_HISTORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.prediction_history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            _safe_print(f"[警告] 保存预测历史失败: {e}")

    def _load_prediction_model(self) -> Dict:
        """加载预测模型"""
        if PREDICTION_MODEL_FILE.exists():
            try:
                with open(PREDICTION_MODEL_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {"context_features": {}, "transition_probabilities": {}, "last_update": None}
        return {"context_features": {}, "transition_probabilities": {}, "last_update": None}

    def _save_prediction_model(self):
        """保存预测模型"""
        self.prediction_model["last_update"] = datetime.now().isoformat()
        try:
            with open(PREDICTION_MODEL_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.prediction_model, f, ensure_ascii=False, indent=2)
        except Exception as e:
            _safe_print(f"[警告] 保存预测模型失败: {e}")

    def _load_prepare_queue(self) -> List[Dict]:
        """加载预触发队列"""
        if PREPARE_QUEUE_FILE.exists():
            try:
                with open(PREPARE_QUEUE_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def _save_prepare_queue(self):
        """保存预触发队列"""
        try:
            with open(PREPARE_QUEUE_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.prepare_queue, f, ensure_ascii=False, indent=2)
        except Exception as e:
            _safe_print(f"[警告] 保存预触发队列失败: {e}")

    def _load_trigger_config(self) -> Dict:
        """加载触发配置"""
        if TRIGGER_CONFIG_FILE.exists():
            try:
                with open(TRIGGER_CONFIG_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return self._get_default_trigger_config()
        return self._get_default_trigger_config()

    def _get_default_trigger_config(self) -> Dict:
        """获取默认触发配置"""
        return {
            "enabled": True,
            "triggers": [
                {"type": "time_based", "interval_minutes": 30, "enabled": True},
                {"type": "context_change", "enabled": True},
                {"type": "pattern_detected", "confidence_threshold": 0.7, "enabled": True},
                {"type": "health_threshold", "threshold": 70, "enabled": True}
            ],
            "notification": {"enabled": True, "method": "log"},
            "last_update": datetime.now().isoformat()
        }

    def _load_patterns(self) -> Dict:
        """加载学习到的模式"""
        # 从预测模型中提取模式
        patterns = {
            "context_transitions": defaultdict(list),  # 上下文转换模式
            "knowledge_usage": defaultdict(int),  # 知识使用频率
            "time_based_patterns": defaultdict(list),  # 时间相关模式
            "sequence_patterns": defaultdict(list)  # 序列模式
        }

        # 从历史中学习模式
        for pred in self.prediction_history.get("predictions", [])[-100:]:  # 只看最近100条
            context = pred.get("context", {})
            timestamp = pred.get("timestamp", "")

            # 记录知识使用
            for kw in pred.get("recommended_keywords", []):
                patterns["knowledge_usage"][kw] += 1

            # 记录时间模式
            if timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    hour = dt.hour
                    patterns["time_based_patterns"][hour].append(pred.get("predicted_needs", []))
                except Exception:
                    pass

        return patterns

    def _get_current_context(self) -> Dict:
        """获取当前上下文"""
        context = {
            "timestamp": datetime.now().isoformat(),
            "hour": datetime.now().hour,
            "day_of_week": datetime.now().weekday()
        }

        # 尝试获取当前任务
        mission_file = STATE_DIR / "current_mission.json"
        if mission_file.exists():
            try:
                with open(mission_file, 'r', encoding='utf-8') as f:
                    mission = json.load(f)
                    context["current_mission"] = mission.get("mission", "")
                    context["current_goal"] = mission.get("current_goal", "")
                    context["phase"] = mission.get("phase", "")
            except Exception:
                pass

        # 尝试获取最近行为
        recent_logs_file = STATE_DIR / "recent_logs.json"
        if recent_logs_file.exists():
            try:
                with open(recent_logs_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
                    recent = logs.get("entries", [])[:5]
                    context["recent_activities"] = [e.get("desc", "")[:100] for e in recent]
            except Exception:
                pass

        # 尝试获取系统状态
        health_file = STATE_DIR / "health_status.json"
        if health_file.exists():
            try:
                with open(health_file, 'r', encoding='utf-8') as f:
                    health = json.load(f)
                    context["health_score"] = health.get("overall_score", 100)
            except Exception:
                pass

        return context

    def predict_user_needs(self, context: Optional[Dict] = None) -> Dict[str, Any]:
        """预测用户需求 - 基于当前上下文预测可能需要的知识"""
        print("\n=== 用户需求智能预测 ===")

        if context is None:
            context = self._get_current_context()

        predictions = {
            "timestamp": datetime.now().isoformat(),
            "context": context,
            "predicted_needs": [],
            "confidence_scores": {},
            "reasoning": []
        }

        # 1. 基于时间模式的预测
        hour = context.get("hour", 12)
        time_based_preds = self._predict_time_based(hour)
        predictions["predicted_needs"].extend(time_based_preds)
        if time_based_preds:
            predictions["reasoning"].append(f"基于时间模式({hour}点)预测")

        # 2. 基于当前任务的预测
        current_goal = context.get("current_goal", "")
        if current_goal and current_goal != "待确定":
            task_preds = self._predict_task_based(current_goal)
            predictions["predicted_needs"].extend(task_preds)
            if task_preds:
                predictions["reasoning"].append(f"基于当前任务「{current_goal[:20]}...」预测")

        # 3. 基于历史序列的预测
        sequence_preds = self._predict_sequence_based()
        predictions["predicted_needs"].extend(sequence_preds)
        if sequence_preds:
            predictions["reasoning"].append("基于历史行为序列预测")

        # 4. 基于健康状态的预测
        health_score = context.get("health_score", 100)
        if health_score < 80:
            predictions["predicted_needs"].append("health_optimization")
            predictions["reasoning"].append(f"基于健康状态({health_score})预测")

        # 去重并计算置信度
        unique_preds = list(set(predictions["predicted_needs"]))
        predictions["predicted_needs"] = unique_preds
        predictions["confidence_scores"] = {p: 0.7 + (0.1 * len(predictions["reasoning"]))
                                            for p in unique_preds}

        # 限制预测数量
        predictions["predicted_needs"] = predictions["predicted_needs"][:5]

        # 保存预测结果
        self.prediction_history["predictions"].append(predictions)
        if len(self.prediction_history["predictions"]) > 200:
            self.prediction_history["predictions"] = self.prediction_history["predictions"][-200:]
        self._save_prediction_history()

        print(f"预测到 {len(predictions['predicted_needs'])} 个潜在需求")
        for need in predictions["predicted_needs"]:
            conf = predictions["confidence_scores"].get(need, 0)
            print(f"  - {need}: {conf:.1%}")

        return predictions

    def _predict_time_based(self, hour: int) -> List[str]:
        """基于时间预测"""
        preds = []

        # 早晨：效能相关
        if 6 <= hour < 10:
            preds.extend(["efficiency", "productivity"])
        # 上午：决策相关
        elif 10 <= hour < 12:
            preds.extend(["decision", "strategy"])
        # 下午：执行相关
        elif 13 <= hour < 17:
            preds.extend(["execution", "optimization"])
        # 傍晚：反思相关
        elif 17 <= hour < 20:
            preds.extend(["reflection", "learning"])
        # 晚上：计划相关
        else:
            preds.extend(["planning", "strategy"])

        return preds

    def _predict_task_based(self, current_goal: str) -> List[str]:
        """基于当前任务预测"""
        preds = []
        goal_lower = current_goal.lower()

        if "知识" in goal_lower or "knowledge" in goal_lower:
            preds.extend(["knowledge_retrieval", "knowledge_recommendation"])
        elif "效能" in goal_lower or "efficiency" in goal_lower:
            preds.extend(["efficiency_optimization", "performance"])
        elif "决策" in goal_lower or "decision" in goal_lower:
            preds.extend(["decision_support", "strategy"])
        elif "优化" in goal_lower or "optimization" in goal_lower:
            preds.extend(["optimization_strategies", "best_practices"])
        elif "预测" in goal_lower or "prediction" in goal_lower:
            preds.extend(["prediction_methods", "analysis"])
        elif "健康" in goal_lower or "health" in goal_lower:
            preds.extend(["health_optimization", "maintenance"])
        else:
            preds.extend(["general_guidance", "best_practices"])

        return preds

    def _predict_sequence_based(self) -> List[str]:
        """基于历史序列预测"""
        # 简单实现：基于最近的知识使用模式预测
        recent_knowledge = self.patterns.get("knowledge_usage", {})

        if not recent_knowledge:
            return []

        # 找到最常用的知识类型
        sorted_knowledge = sorted(recent_knowledge.items(), key=lambda x: x[1], reverse=True)
        top_knowledge = [k for k, v in sorted_knowledge[:3]]

        # 推荐相关但未使用的
        related = {
            "efficiency": ["performance", "optimization"],
            "knowledge": ["learning", "reasoning"],
            "decision": ["strategy", "planning"],
            "optimization": ["efficiency", "improvement"]
        }

        preds = []
        for kw in top_knowledge:
            if kw in related:
                preds.extend(related[kw][:1])

        return preds

    def prepare_knowledge(self, predicted_needs: List[str]) -> Dict[str, Any]:
        """预触发知识准备 - 提前准备可能需要的知识"""
        print("\n=== 知识预触发准备 ===")

        prepare_result = {
            "timestamp": datetime.now().isoformat(),
            "predicted_needs": predicted_needs,
            "prepared_knowledge": [],
            "prepare_queue": []
        }

        knowledge_sources = {
            "efficiency": [
                "evolution_execution_efficiency_cockpit_integration_engine",
                "evolution_execution_trend_analysis_engine"
            ],
            "knowledge": [
                "evolution_knowledge_distillation_inheritance_engine",
                "evolution_cross_engine_knowledge_index_engine"
            ],
            "decision": [
                "evolution_decision_quality_evaluator",
                "evolution_strategy_intelligent_recommendation_engine"
            ],
            "optimization": [
                "evolution_methodology_auto_optimizer",
                "evolution_execution_strategy_self_optimizer"
            ],
            "prediction": [
                "evolution_trend_prediction_prevention_engine",
                "evolution_effectiveness_prediction_prevention_engine"
            ],
            "health": [
                "health_immunity_evolution_engine",
                "evolution_warning_intervention_deep_integration_engine"
            ],
            "planning": [
                "evolution_direction_discovery",
                "evolution_meta_pattern_discovery"
            ]
        }

        # 为每个预测需求准备知识
        for need in predicted_needs:
            if need in knowledge_sources:
                sources = knowledge_sources[need]
                for src in sources:
                    prepare_result["prepared_knowledge"].append({
                        "need": need,
                        "source": src,
                        "status": "ready"
                    })

                # 添加到预触发队列
                self.prepare_queue.append({
                    "need": need,
                    "sources": sources,
                    "timestamp": datetime.now().isoformat(),
                    "status": "pending"
                })

        # 限制队列长度
        if len(self.prepare_queue) > 50:
            self.prepare_queue = self.prepare_queue[-50:]
        self._save_prepare_queue()

        print(f"已为 {len(predicted_needs)} 个预测需求准备知识")
        print(f"预触发队列包含 {len(self.prepare_queue)} 项")

        return prepare_result

    def get_recommendations(self, context: Optional[Dict] = None, max_items: int = 5) -> Dict[str, Any]:
        """获取知识推荐 - 基于上下文和预测"""
        print("\n=== 智能知识推荐 ===")

        if context is None:
            context = self._get_current_context()

        # 先预测需求
        predictions = self.predict_user_needs(context)
        predicted_needs = predictions.get("predicted_needs", [])

        # 基于预测获取推荐
        recommendations = {
            "timestamp": datetime.now().isoformat(),
            "context_summary": {
                "hour": context.get("hour"),
                "mission": context.get("current_mission", ""),
                "phase": context.get("phase", "")
            },
            "predictions": predicted_needs,
            "recommendations": [],
            "trigger_actions": []
        }

        # 生成推荐
        knowledge_topics = {
            "efficiency": "进化效能分析 - 了解当前系统的执行效率优化空间",
            "knowledge": "知识蒸馏与传承 - 获取最新提炼的核心知识",
            "decision": "决策质量评估 - 分析进化决策的质量和效果",
            "optimization": "策略自动优化 - 获取优化建议和改进策略",
            "prediction": "趋势预测预防 - 查看效能趋势和预防性建议",
            "health": "健康预警与自愈 - 了解系统健康状态和预警",
            "planning": "进化方向发现 - 发现新的进化机会和方向",
            "general_guidance": "通用指导 - 获取最佳实践和通用建议"
        }

        for need in predicted_needs[:max_items]:
            if need in knowledge_topics:
                recommendations["recommendations"].append({
                    "topic": need,
                    "description": knowledge_topics[need],
                    "confidence": predictions.get("confidence_scores", {}).get(need, 0.5)
                })

        # 生成可触发的行动
        for rec in recommendations["recommendations"]:
            recommendations["trigger_actions"].append({
                "recommendation": rec["topic"],
                "action": f"do {rec['topic']}",
                "description": rec["description"]
            })

        print(f"生成了 {len(recommendations['recommendations'])} 条推荐")
        for rec in recommendations["recommendations"]:
            print(f"  - {rec['topic']}: {rec['description'][:40]}...")

        return recommendations

    def analyze_trigger_conditions(self) -> Dict[str, Any]:
        """分析触发条件"""
        print("\n=== 触发条件分析 ===")

        context = self._get_current_context()
        trigger_analysis = {
            "timestamp": datetime.now().isoformat(),
            "context": context,
            "trigger_results": [],
            "overall_status": "idle"
        }

        for trigger in self.trigger_config.get("triggers", []):
            if not trigger.get("enabled", True):
                continue

            trigger_type = trigger.get("type", "")
            result = {"type": trigger_type, "triggered": False, "reason": ""}

            if trigger_type == "time_based":
                interval = trigger.get("interval_minutes", 30)
                last_update = self.prediction_model.get("last_update")
                if last_update:
                    try:
                        last_time = datetime.fromisoformat(last_update.replace('Z', '+00:00'))
                        elapsed = (datetime.now() - last_time).total_seconds() / 60
                        if elapsed >= interval:
                            result["triggered"] = True
                            result["reason"] = f"距离上次预测已过 {elapsed:.0f} 分钟"
                    except Exception:
                        pass

            elif trigger_type == "context_change":
                # 检测上下文变化
                last_prediction = self.prediction_history.get("predictions", [])
                if last_prediction:
                    last = last_prediction[-1]
                    last_context = last.get("context", {})
                    if last_context.get("phase") != context.get("phase"):
                        result["triggered"] = True
                        result["reason"] = f"阶段从 {last_context.get('phase')} 变为 {context.get('phase')}"

            elif trigger_type == "health_threshold":
                threshold = trigger.get("threshold", 70)
                health_score = context.get("health_score", 100)
                if health_score < threshold:
                    result["triggered"] = True
                    result["reason"] = f"健康分 {health_score} 低于阈值 {threshold}"

            trigger_analysis["trigger_results"].append(result)

        # 判断是否需要触发
        triggered_count = sum(1 for r in trigger_analysis["trigger_results"] if r["triggered"])
        if triggered_count > 0:
            trigger_analysis["overall_status"] = "triggered"
            print(f"检测到 {triggered_count} 个触发条件满足")
        else:
            print("未检测到触发条件")

        return trigger_analysis

    def auto_trigger_recommendation(self) -> Dict[str, Any]:
        """自动触发推荐"""
        print("\n=== 自动触发推荐 ===")

        # 分析触发条件
        analysis = self.analyze_trigger_conditions()

        if analysis.get("overall_status") != "triggered":
            print("无需触发推荐")
            return {"status": "no_trigger", "message": "未满足触发条件"}

        # 满足条件，执行预测和推荐
        context = self._get_current_context()
        predictions = self.predict_user_needs(context)
        recommendations = self.get_recommendations(context)

        # 预触发知识准备
        prepare_result = self.prepare_knowledge(predictions.get("predicted_needs", []))

        result = {
            "timestamp": datetime.now().isoformat(),
            "status": "triggered",
            "trigger_reasons": [r["reason"] for r in analysis["trigger_results"] if r["triggered"]],
            "predictions": predictions,
            "recommendations": recommendations,
            "preparation": prepare_result
        }

        print(f"自动触发成功，推荐了 {len(recommendations.get('recommendations', []))} 条知识")

        return result

    def get_cockpit_data(self) -> Dict[str, Any]:
        """获取驾驶舱数据"""
        print("\n=== 驾驶舱数据 ===")

        # 收集统计数据
        stats = {
            "total_predictions": len(self.prediction_history.get("predictions", [])),
            "prepare_queue_size": len(self.prepare_queue),
            "patterns_learned": len(self.patterns.get("knowledge_usage", {})),
            "trigger_config": self.trigger_config.get("triggers", [])
        }

        # 最近预测
        recent_predictions = self.prediction_history.get("predictions", [])[-10:]

        cockpit_data = {
            "timestamp": datetime.now().isoformat(),
            "engine_name": self.engine_name,
            "version": self.version,
            "statistics": stats,
            "recent_predictions": recent_predictions,
            "trigger_status": self.trigger_config.get("enabled", True),
            "prepare_queue": self.prepare_queue[-5:]  # 最近5条
        }

        print(f"统计数据: {stats}")

        return cockpit_data

    def run_full_cycle(self) -> Dict[str, Any]:
        """运行完整循环"""
        print("\n" + "="*60)
        print(f"[{self.engine_name}] 完整循环开始")
        print("="*60)

        # 1. 自动触发检测
        trigger_result = self.auto_trigger_recommendation()

        # 2. 获取推荐
        if trigger_result.get("status") != "triggered":
            context = self._get_current_context()
            recommendations = self.get_recommendations(context)
        else:
            recommendations = trigger_result.get("recommendations", {})

        # 3. 驾驶舱数据
        cockpit_data = self.get_cockpit_data()

        result = {
            "timestamp": datetime.now().isoformat(),
            "trigger_result": trigger_result,
            "recommendations": recommendations,
            "cockpit_data": cockpit_data
        }

        print("\n" + "="*60)
        print(f"[{self.engine_name}] 完整循环完成")
        print("="*60)

        return result


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(
        description="智能全场景进化环跨引擎知识自动推荐与智能预测触发引擎"
    )
    parser.add_argument("--predict", action="store_true", help="预测用户需求")
    parser.add_argument("--recommend", action="store_true", help="获取知识推荐")
    parser.add_argument("--prepare", action="store_true", help="预触发知识准备")
    parser.add_argument("--trigger", action="store_true", help="自动触发推荐")
    parser.add_argument("--analyze-triggers", action="store_true", help="分析触发条件")
    parser.add_argument("--cycle", action="store_true", help="运行完整循环")
    parser.add_argument("--cockpit-data", action="store_true", help="获取驾驶舱数据")
    parser.add_argument("--status", action="store_true", help="显示状态")

    args = parser.parse_args()

    engine = KnowledgeProactiveRecommendationPredictionEngine()

    if args.predict:
        result = engine.predict_user_needs()
        print("\n=== 预测结果 ===")
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.prepare:
        # 需要先预测
        predictions = engine.predict_user_needs()
        result = engine.prepare_knowledge(predictions.get("predicted_needs", []))
        print("\n=== 准备结果 ===")
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.recommend:
        result = engine.get_recommendations()
        print("\n=== 推荐结果 ===")
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.analyze_triggers:
        result = engine.analyze_trigger_conditions()
        print("\n=== 触发条件分析 ===")
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.trigger:
        result = engine.auto_trigger_recommendation()
        print("\n=== 自动触发结果 ===")
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.cycle:
        result = engine.run_full_cycle()
        print("\n=== 完整循环结果 ===")
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.cockpit_data:
        result = engine.get_cockpit_data()
        print("\n=== 驾驶舱数据 ===")
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.status:
        print(f"\n=== {engine.engine_name} ===")
        print(f"版本: {engine.version}")
        print(f"预测历史: {len(engine.prediction_history.get('predictions', []))} 条")
        print(f"预触发队列: {len(engine.prepare_queue)} 项")
        print(f"学习模式: {len(engine.patterns.get('knowledge_usage', {}))} 个")
        print(f"触发配置: {'启用' if engine.trigger_config.get('enabled') else '禁用'}")

    else:
        # 默认显示状态
        print(f"\n=== {engine.engine_name} v{engine.version} ===")
        print("使用 --help 查看可用选项")
        print(f"\n预测历史: {len(engine.prediction_history.get('predictions', []))} 条")
        print(f"预触发队列: {len(engine.prepare_queue)} 项")


if __name__ == "__main__":
    main()