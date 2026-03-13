#!/usr/bin/env python3
"""
智能用户意图自动补全与增强引擎
Intelligent User Intent Auto-Completion & Enhancement Engine

让系统能够理解模糊/不完整的用户输入，主动补全意图并推荐最可能的操作。
当用户输入不完整时（如"帮我处理一下那个"），系统能够：
1. 分析上下文（历史对话、当前场景、系统状态）
2. 预测用户可能的完整意图
3. 主动询问确认或自动执行最可能的操作

这是"超越用户"的能力——用户不需要精确表达需求，系统能理解模糊意图。
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

# 路径配置
SCRIPT_DIR = Path(__file__).parent
RUNTIME_STATE = SCRIPT_DIR.parent / "runtime" / "state"
RUNTIME_LOGS = SCRIPT_DIR.parent / "runtime" / "logs"
PLANS_DIR = SCRIPT_DIR.parent / "assets" / "plans"


class IntentCompletionEngine:
    """智能用户意图自动补全与增强引擎"""

    def __init__(self):
        self.history_file = RUNTIME_STATE / "intent_completion_history.json"
        self.context_file = RUNTIME_STATE / "conversation_context.json"
        self.completions = self._load_history()

    def _load_history(self):
        """加载历史补全记录"""
        if self.history_file.exists():
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return {"completions": [], "last_updated": None}
        return {"completions": [], "last_updated": None}

    def _save_history(self):
        """保存历史补全记录"""
        self.completions["last_updated"] = datetime.now().isoformat()
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(self.completions, f, ensure_ascii=False, indent=2)

    def _load_context(self):
        """加载会话上下文"""
        if self.context_file.exists():
            try:
                with open(self.context_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def _analyze_input_clarity(self, user_input: str) -> dict:
        """分析输入的清晰度"""
        user_input = user_input.strip()
        clarity_score = 1.0  # 默认完整
        ambiguity_flags = []

        # 检测模糊指代词
        vague_patterns = [
            (r"^(那个|这个|它|这个|那个东西|这个文件|那个文件)$", "指代词"),
            (r"^(帮我|帮我处理|帮我做|帮我看下)$", "动作不完整"),
            (r"^(刚才|之前|上次|之前那个)$", "时间指代不明确"),
            (r"^(什么|哪个|怎么|为什么)$", "信息缺失"),
            (r"^(等一下|先|先看看|先处理)$", "意图不明确"),
        ]

        for pattern, flag in vague_patterns:
            if re.search(pattern, user_input):
                ambiguity_flags.append(flag)
                clarity_score -= 0.3

        # 检测过短输入
        if len(user_input) < 4:
            clarity_score -= 0.2
            ambiguity_flags.append("输入过短")

        # 检测无动词输入
        if not re.search(r"(帮|做|处理|看|找|开|关|发|写|整理|查|执行|运行|启动|关闭)", user_input):
            clarity_score -= 0.3
            ambiguity_flags.append("缺少动作动词")

        clarity_score = max(0.0, min(1.0, clarity_score))

        return {
            "clarity_score": clarity_score,
            "is_ambiguous": clarity_score < 0.7,
            "ambiguity_flags": ambiguity_flags,
            "original_input": user_input
        }

    def _get_recent_context(self) -> dict:
        """获取最近对话上下文"""
        context = self._load_context()
        recent_file = RUNTIME_STATE / "recent_logs.json"

        if recent_file.exists():
            try:
                with open(recent_file, "r", encoding="utf-8") as f:
                    recent_data = json.load(f)
                    recent_entries = recent_data.get("entries", [])[-5:]  # 最近5条
                    context["recent_conversations"] = [
                        {
                            "time": e.get("time", ""),
                            "desc": e.get("desc", ""),
                            "mission": e.get("mission", "")
                        }
                        for e in recent_entries
                    ]
            except:
                pass

        return context

    def _predict_intent(self, user_input: str, context: dict) -> list:
        """预测用户可能的意图"""
        predictions = []
        user_input = user_input.lower()

        # 基于关键词和上下文预测
        intent_templates = [
            # 文件相关
            ("文件", ["打开", "查看", "整理", "发送"], "打开或处理文件"),
            ("文档", ["打开", "编辑", "整理"], "处理文档"),
            ("图片", ["查看", "整理", "发送"], "处理图片"),

            # 应用相关
            ("开.*", ["打开", "启动", "运行"], "打开应用程序"),
            ("浏览器", ["打开", "浏览"], "打开浏览器"),
            ("微信", ["打开", "发消息"], "打开微信"),

            # 系统相关
            ("截", ["截图", "截屏"], "截取屏幕"),
            ("音量", ["调整", "设置", "静音"], "调整音量"),
            ("亮度", ["调整", "设置"], "调整屏幕亮度"),

            # 任务相关
            ("整理", ["整理", "归类"], "整理文件"),
            ("发送", ["发送", "发"], "发送消息或文件"),
        ]

        for pattern, actions, description in intent_templates:
            if re.search(pattern, user_input):
                predictions.append({
                    "intent": description,
                    "confidence": 0.7,
                    "suggested_actions": actions
                })

        # 基于最近上下文补充预测
        recent_convs = context.get("recent_conversations", [])
        if recent_convs:
            # 根据最近的操作推断当前意图
            for conv in recent_convs[:3]:
                desc = conv.get("desc", "")
                if "打开" in desc:
                    predictions.append({
                        "intent": "继续之前的操作",
                        "confidence": 0.4,
                        "suggested_actions": ["重新打开", "继续"]
                    })
                    break

        # 按置信度排序
        predictions.sort(key=lambda x: x["confidence"], reverse=True)
        return predictions[:3]  # 最多返回3个预测

    def _generate_completion_suggestion(self, analysis: dict, predictions: list) -> dict:
        """生成补全建议"""
        if not analysis["is_ambiguous"]:
            return {
                "type": "clear",
                "message": "输入清晰，无需补全",
                "original_input": analysis["original_input"]
            }

        if not predictions:
            return {
                "type": "cannot_complete",
                "message": "无法理解您的意图，请补充更多信息",
                "original_input": analysis["original_input"]
            }

        # 生成多选项建议
        suggestions = []
        for i, pred in enumerate(predictions):
            suggestions.append({
                "index": i + 1,
                "intent": pred["intent"],
                "confidence": f"{pred['confidence']*100:.0f}%",
                "actions": pred["suggested_actions"]
            })

        return {
            "type": "suggestions",
            "message": f"检测到您输入不完整，可能意图：",
            "original_input": analysis["original_input"],
            "ambiguity_flags": analysis["ambiguity_flags"],
            "suggestions": suggestions,
            "auto_action": predictions[0] if predictions[0]["confidence"] > 0.6 else None
        }

    def complete(self, user_input: str, auto_execute: bool = False) -> dict:
        """
        补全用户意图

        Args:
            user_input: 用户的原始输入
            auto_execute: 是否自动执行最可能的操作

        Returns:
            补全结果和建议
        """
        # 分析输入清晰度
        analysis = self._analyze_input_clarity(user_input)

        # 获取上下文
        context = self._get_recent_context()

        # 预测意图
        predictions = self._predict_intent(user_input, context)

        # 生成建议
        suggestion = self._generate_completion_suggestion(analysis, predictions)

        # 记录补全历史
        completion_record = {
            "timestamp": datetime.now().isoformat(),
            "original_input": user_input,
            "analysis": analysis,
            "predictions": predictions,
            "suggestion_type": suggestion["type"]
        }
        self.completions["completions"].append(completion_record)
        # 保留最近20条
        self.completions["completions"] = self.completions["completions"][-20:]
        self._save_history()

        # 添加上下文到返回结果
        suggestion["context"] = {
            "recent_count": len(context.get("recent_conversations", []))
        }

        return suggestion

    def status(self) -> dict:
        """获取引擎状态"""
        return {
            "engine": "Intent Completion Engine",
            "version": "1.0",
            "total_completions": len(self.completions.get("completions", [])),
            "last_updated": self.completions.get("last_updated"),
            "capabilities": [
                "模糊输入分析",
                "意图预测",
                "上下文感知",
                "自动补全建议",
                "多选项推荐"
            ]
        }

    def clear_history(self) -> dict:
        """清除历史记录"""
        self.completions = {"completions": [], "last_updated": None}
        self._save_history()
        return {"status": "success", "message": "历史记录已清除"}


def main():
    """CLI 入口"""
    import argparse
    parser = argparse.ArgumentParser(description="智能用户意图自动补全引擎")
    parser.add_argument("action", nargs="?", default="status",
                        help="操作: status, complete, clear")
    parser.add_argument("--input", "-i", type=str, default="",
                        help="要补全的用户输入")
    parser.add_argument("--auto", "-a", action="store_true",
                        help="自动执行最可能的操作")

    args = parser.parse_args()
    engine = IntentCompletionEngine()

    if args.action == "status":
        result = engine.status()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.action == "complete":
        if not args.input:
            print("错误: 请提供要补全的输入 (-i/--input)")
            return
        result = engine.complete(args.input, args.auto)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.action == "clear":
        result = engine.clear_history()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"未知操作: {args.action}")
        print("可用操作: status, complete, clear")


if __name__ == "__main__":
    main()