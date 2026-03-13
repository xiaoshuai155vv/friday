#!/usr/bin/env python3
"""
智能意图深度推理引擎
让系统能够进行更深层次的用户意图推理，理解深层需求、隐含意图和上下文暗示。

功能：
1. 多层次意图分析（表层意图、深层意图、潜在意图）
2. 上下文感知推理
3. 历史行为分析
4. 隐含意图识别
5. 个性化意图预测
6. 意图置信度评估
"""

import json
import os
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path

# 路径配置
PROJECT_ROOT = Path(__file__).parent.parent
RUNTIME_STATE = PROJECT_ROOT / "runtime" / "state"
RECENT_LOGS = RUNTIME_STATE / "recent_logs.json"
SCENARIO_EXPERIENCES = RUNTIME_STATE / "scenario_experiences.json"
LONG_TERM_MEMORY = RUNTIME_STATE / "long_term_memory.json"


class IntentDeepReasoningEngine:
    """智能意图深度推理引擎"""

    def __init__(self):
        self.name = "IntentDeepReasoningEngine"
        self.version = "1.0.0"
        self.intent_hierarchy = {
            "表层意图": "用户直接表达的需求",
            "深层意图": "用户实际需要解决的问题",
            "潜在意图": "用户未明确表达但可能需要的内容"
        }
        self.reasoning_depth = 3  # 推理层级深度
        self.context_window = 10  # 上下文窗口大小

    def get_system_status(self) -> Dict[str, Any]:
        """获取引擎状态"""
        return {
            "name": self.name,
            "version": self.version,
            "status": "active",
            "capabilities": [
                "多层次意图分析",
                "上下文感知推理",
                "历史行为分析",
                "隐含意图识别",
                "个性化意图预测",
                "意图置信度评估"
            ],
            "config": {
                "reasoning_depth": self.reasoning_depth,
                "context_window": self.context_window
            }
        }

    def _load_recent_logs(self) -> List[Dict]:
        """加载最近的行为日志"""
        try:
            if RECENT_LOGS.exists():
                with open(RECENT_LOGS, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get("entries", [])[-self.context_window:]
        except Exception:
            pass
        return []

    def _load_scenario_experiences(self) -> List[Dict]:
        """加载场景经验"""
        try:
            if SCENARIO_EXPERIENCES.exists():
                with open(SCENARIO_EXPERIENCES, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get("entries", [])
        except Exception:
            pass
        return []

    def _load_long_term_memory(self) -> Dict:
        """加载长期记忆"""
        try:
            if LONG_TERM_MEMORY.exists():
                with open(LONG_TERM_MEMORY, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

    def _analyze_user_patterns(self, user_input: str, context: Dict) -> Dict:
        """分析用户行为模式"""
        patterns = {
            "time_pattern": None,
            "frequency_pattern": None,
            "sequence_pattern": None,
            "preference_pattern": None
        }

        # 分析时间模式
        recent_logs = self._load_recent_logs()
        if recent_logs:
            times = [entry.get("time", "") for entry in recent_logs]
            if times:
                patterns["time_pattern"] = "用户近期有活动记录"

        # 分析频率模式
        scenario_experiences = self._load_scenario_experiences()
        if scenario_experiences:
            scene_counts = {}
            for exp in scenario_experiences:
                scene = exp.get("scene", "unknown")
                scene_counts[scene] = scene_counts.get(scene, 0) + 1

            if scene_counts:
                most_common = max(scene_counts.items(), key=lambda x: x[1])
                patterns["frequency_pattern"] = f"用户最常使用场景: {most_common[0]}"

        # 分析序列模式
        if len(recent_logs) >= 2:
            patterns["sequence_pattern"] = "检测到用户行为序列模式"

        # 分析偏好模式
        long_term_memory = self._load_long_term_memory()
        if long_term_memory:
            habits = long_term_memory.get("habits", {})
            if habits:
                patterns["preference_pattern"] = f"用户习惯: {list(habits.keys())[:3]}"

        return patterns

    def _extract_implied_intent(self, user_input: str, surface_intent: str) -> List[str]:
        """提取隐含意图"""
        implied_intents = []

        # 基于关键词识别隐含意图
        implied_keywords = {
            "打开": ["需要查看内容", "需要操作界面", "需要启动应用"],
            "发送": ["需要编写内容", "需要选择接收人", "可能需要确认发送结果"],
            "查询": ["需要了解信息", "可能需要筛选结果", "可能需要导出结果"],
            "设置": ["需要自定义行为", "可能需要保存设置", "可能需要重启应用"],
            "整理": ["需要清理空间", "需要分类管理", "需要备份重要文件"]
        }

        for keyword, intents in implied_keywords.items():
            if keyword in user_input:
                implied_intents.extend(intents)

        # 基于深层意图推断隐含需求
        if surface_intent in ["文件管理", "文档处理"]:
            implied_intents.extend(["提高效率", "节省时间", "减少重复操作"])

        return list(set(implied_intents))[:3]  # 限制返回数量

    def _assess_confidence(self, surface_intent: str, deep_intent: str,
                          context: Dict, patterns: Dict) -> float:
        """评估意图置信度"""
        confidence = 0.5  # 基础置信度

        # 基于上下文丰富度调整
        if context.get("recent_action"):
            confidence += 0.1
        if context.get("time_of_day"):
            confidence += 0.05

        # 基于模式匹配调整
        if patterns.get("frequency_pattern"):
            confidence += 0.15
        if patterns.get("sequence_pattern"):
            confidence += 0.1

        # 基于历史行为调整
        if patterns.get("preference_pattern"):
            confidence += 0.1

        return min(confidence, 0.99)  # 最高不超过 0.99

    def _infer_deep_intent(self, user_input: str, surface_intent: str,
                           context: Dict, patterns: Dict) -> str:
        """推理深层意图"""
        # 深层意图通常与用户要解决的问题相关
        deep_intent_map = {
            "打开应用": "高效完成工作任务",
            "文件操作": "整理和管理工作资料",
            "发送消息": "沟通和协作",
            "查询信息": "获取所需知识或数据",
            "设置配置": "优化工作环境",
            "执行计划": "自动化完成任务"
        }

        # 基于上下文推断深层意图
        if context.get("recent_action"):
            recent = context.get("recent_action", "")
            if "任务" in recent:
                return "完成未完成任务"
            if "会议" in recent:
                return "跟进会议相关事项"

        # 基于用户模式推断
        if patterns.get("preference_pattern"):
            return "获得个性化服务"

        return deep_intent_map.get(surface_intent, "满足用户需求")

    def analyze_intent(self, user_input: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        分析用户意图（主方法）

        Args:
            user_input: 用户输入
            context: 上下文信息（可选）

        Returns:
            意图分析结果
        """
        if context is None:
            context = {}

        # 1. 提取表层意图（基于关键词）
        surface_intent = self._extract_surface_intent(user_input)

        # 2. 分析用户行为模式
        patterns = self._analyze_user_patterns(user_input, context)

        # 3. 推理深层意图
        deep_intent = self._infer_deep_intent(user_input, surface_intent, context, patterns)

        # 4. 提取隐含意图
        implied_intents = self._extract_implied_intent(user_input, surface_intent)

        # 5. 评估置信度
        confidence = self._assess_confidence(surface_intent, deep_intent, context, patterns)

        # 6. 生成推理链
        reasoning_chain = self._generate_reasoning_chain(
            user_input, surface_intent, deep_intent, implied_intents, patterns
        )

        # 7. 生成建议行动
        suggested_actions = self._generate_suggested_actions(
            surface_intent, deep_intent, implied_intents, context
        )

        return {
            "user_input": user_input,
            "surface_intent": surface_intent,
            "deep_intent": deep_intent,
            "implied_intents": implied_intents,
            "confidence": confidence,
            "reasoning_chain": reasoning_chain,
            "suggested_actions": suggested_actions,
            "context_used": {
                "recent_logs_count": len(self._load_recent_logs()),
                "scenario_experiences_count": len(self._load_scenario_experiences()),
                "patterns": patterns
            },
            "timestamp": datetime.now().isoformat()
        }

    def _extract_surface_intent(self, user_input: str) -> str:
        """提取表层意图"""
        # 基于关键词匹配
        keyword_intent_map = {
            "打开": "打开应用",
            "启动": "打开应用",
            "运行": "执行操作",
            "发送": "发送消息",
            "发": "发送消息",
            "查": "查询信息",
            "搜索": "查询信息",
            "找": "查询信息",
            "设置": "设置配置",
            "配置": "设置配置",
            "整理": "文件整理",
            "管理": "文件管理",
            "执行": "执行计划",
            "计划": "任务计划"
        }

        for keyword, intent in keyword_intent_map.items():
            if keyword in user_input:
                return intent

        return "通用操作"

    def _generate_reasoning_chain(self, user_input: str, surface_intent: str,
                                   deep_intent: str, implied_intents: List[str],
                                   patterns: Dict) -> List[str]:
        """生成推理链"""
        chain = [
            f"1. 用户输入: 「{user_input}」",
            f"2. 表层意图识别: {surface_intent}",
            f"3. 基于上下文分析用户行为模式...",
            f"4. 深层意图推理: {deep_intent}"
        ]

        if patterns.get("frequency_pattern"):
            chain.append(f"5. 频率模式: {patterns['frequency_pattern']}")

        if implied_intents:
            chain.append(f"6. 隐含意图: {', '.join(implied_intents[:2])}")

        chain.append(f"7. 综合推理置信度评估")

        return chain

    def _generate_suggested_actions(self, surface_intent: str, deep_intent: str,
                                    implied_intents: List[str], context: Dict) -> List[Dict]:
        """生成建议行动"""
        suggestions = []

        # 基于表层意图的建议
        intent_actions = {
            "打开应用": [
                {"action": "launch", "target": "应用启动", "priority": "high"},
                {"action": "maximize", "target": "窗口最大化", "priority": "medium"}
            ],
            "发送消息": [
                {"action": "prepare_content", "target": "准备消息内容", "priority": "high"},
                {"action": "select_recipient", "target": "选择接收人", "priority": "high"}
            ],
            "查询信息": [
                {"action": "search", "target": "执行搜索", "priority": "high"},
                {"action": "filter", "target": "筛选结果", "priority": "medium"}
            ],
            "文件整理": [
                {"action": "analyze", "target": "分析文件结构", "priority": "high"},
                {"action": "categorize", "target": "分类整理", "priority": "medium"}
            ]
        }

        suggestions.extend(intent_actions.get(surface_intent, []))

        # 基于隐含意图的建议
        for implied in implied_intents[:2]:
            suggestions.append({
                "action": "consider",
                "target": implied,
                "priority": "low"
            })

        return suggestions

    def predict_intent(self, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        预测用户可能的需求

        Args:
            context: 上下文信息

        Returns:
            预测结果
        """
        if context is None:
            context = {}

        predictions = []

        # 基于时间模式预测
        now = datetime.now()
        hour = now.hour

        if 9 <= hour < 12:
            predictions.append({
                "predicted_intent": "工作计划相关",
                "probability": 0.7,
                "reason": "用户通常在上午进行计划性工作"
            })
        elif 14 <= hour < 17:
            predictions.append({
                "predicted_intent": "执行任务相关",
                "probability": 0.65,
                "reason": "用户通常在下午执行任务"
            })

        # 基于近期行为预测
        recent_logs = self._load_recent_logs()
        if recent_logs:
            last_intent = recent_logs[-1].get("desc", "")[:50]
            predictions.append({
                "predicted_intent": "延续上次操作",
                "probability": 0.5,
                "reason": f"上次操作: {last_intent}"
            })

        # 基于场景经验预测
        scenario_experiences = self._load_scenario_experiences()
        if scenario_experiences:
            # 找到最近成功的场景
            success_scenes = [e for e in scenario_experiences if e.get("result") == "success"]
            if success_scenes:
                last_scene = success_scenes[-1].get("scene", "")
                predictions.append({
                    "predicted_intent": "可能重复使用",
                    "probability": 0.4,
                    "reason": f"上次成功场景: {last_scene}"
                })

        return {
            "predictions": predictions,
            "timestamp": now.isoformat()
        }

    def batch_analyze(self, user_inputs: List[str], context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        批量分析多个用户输入

        Args:
            user_inputs: 用户输入列表
            context: 上下文信息

        Returns:
            批量分析结果
        """
        results = []

        for user_input in user_inputs:
            result = self.analyze_intent(user_input, context)
            results.append(result)

        # 汇总分析
        summary = {
            "total_inputs": len(user_inputs),
            "surface_intents": {},
            "average_confidence": sum(r["confidence"] for r in results) / len(results) if results else 0,
            "common_implied_intents": []
        }

        # 统计表层意图分布
        for r in results:
            intent = r["surface_intent"]
            summary["surface_intents"][intent] = summary["surface_intents"].get(intent, 0) + 1

        return {
            "individual_results": results,
            "summary": summary,
            "timestamp": datetime.now().isoformat()
        }

    def get_insights(self) -> Dict[str, Any]:
        """获取意图推理洞察"""
        recent_logs = self._load_recent_logs()
        scenario_experiences = self._load_scenario_experiences()
        long_term_memory = self._load_long_term_memory()

        insights = {
            "user_behavior_summary": {
                "recent_activities": len(recent_logs),
                "successful_scenarios": len([e for e in scenario_experiences if e.get("result") == "success"]),
                "long_term_goals": len(long_term_memory.get("goals", []))
            },
            "intent_patterns": {
                "most_common_intent": "任务执行",
                "intent_complexity": "中等",
                "inferred_preference": "效率导向"
            },
            "recommendations": [
                "建议在用户提交任务后主动提供进度更新",
                "可以基于时间模式提前准备常用资源",
                "建议增加跨场景的上下文关联"
            ]
        }

        return insights


def main():
    """CLI 入口"""
    import sys

    engine = IntentDeepReasoningEngine()

    if len(sys.argv) < 2:
        # 默认显示状态
        print(json.dumps(engine.get_system_status(), ensure_ascii=False, indent=2))
        return

    command = sys.argv[1]

    if command == "status":
        print(json.dumps(engine.get_system_status(), ensure_ascii=False, indent=2))

    elif command == "analyze":
        # 分析用户输入
        user_input = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "帮我打开文件管理器"
        context = {}
        result = engine.analyze_intent(user_input, context)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "predict":
        # 预测用户需求
        context = {}
        result = engine.predict_intent(context)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "batch":
        # 批量分析
        user_inputs = sys.argv[2:] if len(sys.argv) > 2 else ["打开文件管理器", "发送消息", "整理文件"]
        result = engine.batch_analyze(user_inputs)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "insights":
        # 获取洞察
        result = engine.get_insights()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    else:
        print(f"未知命令: {command}")
        print("可用命令: status, analyze, predict, batch, insights")


if __name__ == "__main__":
    main()