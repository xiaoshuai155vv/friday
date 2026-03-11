#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
异常预测预防机制 - 基于历史失败和执行策略分析，预测潜在错误并提供预防建议

功能：
1. 解析 failures.md 历史失败模式
2. 分析 task_strategy_history.json 策略执行历史
3. 基于失败模式建立预测规则
4. 在执行任务前预测潜在风险并提供预防措施
"""

import os
import re
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
RUNTIME_STATE = PROJECT_ROOT / "runtime" / "state"
REFERENCES = PROJECT_ROOT / "references"


class FailurePredictor:
    """异常预测器"""

    def __init__(self):
        self.failure_patterns = []
        self.strategy_history = []
        self.prediction_rules = []
        self._load_data()

    def _load_data(self):
        """加载失败历史和策略历史"""
        # 加载 failures.md
        failures_path = REFERENCES / "failures.md"
        if failures_path.exists():
            self.failure_patterns = self._parse_failures(failures_path)

        # 加载策略历史
        strategy_history_path = RUNTIME_STATE / "task_strategy_history.json"
        if strategy_history_path.exists():
            with open(strategy_history_path, "r", encoding="utf-8") as f:
                self.strategy_history = json.load(f)

    def _parse_failures(self, path: Path) -> List[Dict[str, Any]]:
        """解析 failures.md"""
        patterns = []
        try:
            content = path.read_text(encoding="utf-8")
            # 匹配格式：- YYYY-MM-DD：问题描述 → 原因分析 → 下次如何避免
            # 也匹配纯文本描述
            lines = content.split("\n")
            for line in lines:
                line = line.strip()
                if line.startswith("- ") and "：" in line:
                    # 提取日期和描述
                    match = re.match(r"- (\d{4}-\d{2}-\d{2})：(.+)", line)
                    if match:
                        date_str, desc = match.groups()
                        patterns.append({
                            "date": date_str,
                            "description": desc,
                            "keywords": self._extract_keywords(desc)
                        })
        except Exception as e:
            print(f"Warning: Failed to parse failures.md: {e}")
        return patterns

    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        keywords = []
        # 常见错误类型关键词
        error_types = [
            "vision", "坐标", "超时", "失败", "错误", "异常",
            "激活", "窗口", "截图", "剪贴板", "权限", "进程",
            "模块", "找不到", "无法", "中断", "崩溃"
        ]
        text_lower = text.lower()
        for kw in error_types:
            if kw in text_lower:
                keywords.append(kw)
        return keywords

    def _build_prediction_rules(self):
        """基于失败模式建立预测规则"""
        rules = []

        # 统计关键词频率
        keyword_freq = {}
        for fp in self.failure_patterns:
            for kw in fp.get("keywords", []):
                keyword_freq[kw] = keyword_freq.get(kw, 0) + 1

        # 基于高频关键词建立规则
        high_freq_keywords = [kw for kw, cnt in keyword_freq.items() if cnt >= 2]

        for kw in high_freq_keywords:
            if kw in ["vision", "坐标"]:
                rules.append({
                    "trigger": "vision_coords",
                    "risk": "坐标偏移或识别错误",
                    "prevention": [
                        "检查 vision_coords_offset 配置",
                        "使用 click_verify 验证坐标",
                        "考虑添加固定偏移"
                    ]
                })
            elif kw in ["激活", "窗口"]:
                rules.append({
                    "trigger": "window_activate",
                    "risk": "窗口激活失败",
                    "prevention": [
                        "使用 activate_process 而非 activate 标题",
                        "添加重试逻辑和等待时间",
                        "检查窗口是否最小化"
                    ]
                })
            elif kw in ["超时", "失败"]:
                rules.append({
                    "trigger": "vision/screenshot",
                    "risk": "操作超时或失败",
                    "prevention": [
                        "增加等待时间",
                        "添加重试机制",
                        "检查网络/环境状态"
                    ]
                })
            elif kw in ["剪贴板"]:
                rules.append({
                    "trigger": "clipboard",
                    "risk": "剪贴板操作失败",
                    "prevention": [
                        "使用 keyboard_tool type 替代",
                        "使用 paste 组合键"
                    ]
                })

        # 基于策略历史建立规则
        if self.strategy_history:
            # 分析失败率高的步骤类型
            step_failures = {}
            for record in self.strategy_history:
                step_type = record.get("step_type", "unknown")
                success = record.get("success", True)
                if not success:
                    step_failures[step_type] = step_failures.get(step_type, 0) + 1

            for step_type, count in step_failures.items():
                if count >= 2:
                    rules.append({
                        "trigger": step_type,
                        "risk": f"{step_type} 执行失败率较高",
                        "prevention": [
                            f"为 {step_type} 步骤增加重试次数",
                            f"为 {step_type} 步骤增加等待时间",
                            f"考虑使用备用方案"
                        ]
                    })

        self.prediction_rules = rules
        return rules

    def predict(self, step_type: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        预测指定步骤类型的潜在风险

        Args:
            step_type: 步骤类型 (e.g., "vision", "click", "activate")
            context: 额外上下文信息

        Returns:
            预测结果包含风险描述和预防建议
        """
        if not self.prediction_rules:
            self._build_prediction_rules()

        # 匹配相关规则
        matched_rules = []
        step_type_lower = step_type.lower()

        for rule in self.prediction_rules:
            trigger = rule.get("trigger", "").lower()
            if trigger in step_type_lower or step_type_lower in trigger:
                matched_rules.append(rule)

        if not matched_rules:
            return {
                "step_type": step_type,
                "risk_level": "low",
                "risks": [],
                "preventions": ["无已知风险"]
            }

        return {
            "step_type": step_type,
            "risk_level": "medium" if len(matched_rules) <= 2 else "high",
            "risks": [rule.get("risk", "") for rule in matched_rules],
            "preventions": self._deduplicate_preventions(matched_rules)
        }

    def _deduplicate_preventions(self, rules: List[Dict]) -> List[str]:
        """去重预防建议"""
        preventions = []
        seen = set()
        for rule in rules:
            for p in rule.get("prevention", []):
                if p not in seen:
                    seen.add(p)
                    preventions.append(p)
        return preventions

    def get_all_predictions(self) -> Dict[str, Any]:
        """获取所有预测规则"""
        if not self.prediction_rules:
            self._build_prediction_rules()
        return {
            "generated_at": datetime.now().isoformat(),
            "total_patterns": len(self.failure_patterns),
            "total_rules": len(self.prediction_rules),
            "rules": self.prediction_rules
        }

    def save_predictions(self, output_path: Optional[Path] = None):
        """保存预测规则到文件"""
        if output_path is None:
            output_path = RUNTIME_STATE / "failure_predictions.json"

        predictions = self.get_all_predictions()
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(predictions, f, ensure_ascii=False, indent=2)

        return output_path


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(
        description="异常预测预防机制 - 基于历史失败和执行策略分析"
    )
    parser.add_argument(
        "--predict", "-p",
        help="预测指定步骤类型的风险 (e.g., vision, click, activate)"
    )
    parser.add_argument(
        "--context", "-c",
        help="额外上下文 JSON (e.g., '{\"app\": \"ihaier\"}')"
    )
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="列出所有预测规则"
    )
    parser.add_argument(
        "--save", "-s",
        action="store_true",
        help="保存预测规则到 runtime/state/failure_predictions.json"
    )

    args = parser.parse_args()

    predictor = FailurePredictor()

    if args.list:
        # 列出所有预测规则
        predictions = predictor.get_all_predictions()
        print(json.dumps(predictions, ensure_ascii=False, indent=2))

    elif args.predict:
        # 预测指定步骤类型
        context = None
        if args.context:
            try:
                context = json.loads(args.context)
            except json.JSONDecodeError:
                print(f"Error: Invalid JSON context: {args.context}")
                sys.exit(1)

        result = predictor.predict(args.predict, context)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.save:
        # 保存预测规则
        output_path = predictor.save_predictions()
        print(f"Predictions saved to: {output_path}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()