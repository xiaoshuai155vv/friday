#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
智能错误模式学习与主动防御引擎
让系统能够从执行历史和错误日志中自动学习错误模式，
预测可能发生的错误，并主动实施预防措施。

区别于：
- self_healing_engine: 问题后修复
- predictive_prevention_engine: 预测问题
- 本引擎：主动防御 - 在错误发生前就从历史中学习模式并预防

功能：
- 错误模式学习：从执行历史、错误日志中学习错误模式
- 错误预测：预测可能发生的错误
- 主动防御：在错误发生前实施预防措施
- 防御策略管理：管理主动防御策略

用法:
  python error_pattern_learning_engine.py learn [--history-lines N]
  python error_pattern_learning_engine.py predict
  python error_pattern_learning_engine.py defend [--apply]
  python error_pattern_learning_engine.py patterns
  python error_pattern_learning_engine.py status
  python error_pattern_learning_engine.py defense-config
  python error_pattern_learning_engine.py add-pattern "<错误类型>" "<模式>" "<防御策略>"
"""

import argparse
import json
import os
import re
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from collections import defaultdict, Counter

# 路径配置
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
STATE_DIR = os.path.join(PROJECT_ROOT, "runtime", "state")
LOGS_DIR = os.path.join(PROJECT_ROOT, "runtime", "logs")
PATTERN_FILE = os.path.join(STATE_DIR, "error_patterns.json")
DEFENSE_CONFIG_FILE = os.path.join(STATE_DIR, "defense_config.json")
PREDICTION_FILE = os.path.join(STATE_DIR, "error_predictions.json")


def ensure_dir():
    """确保目录存在"""
    os.makedirs(STATE_DIR, exist_ok=True)
    os.makedirs(LOGS_DIR, exist_ok=True)


def load_json_file(filepath: str, default: Any = None) -> Any:
    """加载 JSON 文件"""
    ensure_dir()
    if not os.path.exists(filepath):
        return default if default is not None else {}
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default if default is not None else {}


def save_json_file(filepath: str, data: Any):
    """保存 JSON 文件"""
    ensure_dir()
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


class ErrorPattern:
    """错误模式"""

    def __init__(self, pattern_id: str, error_type: str, pattern: str,
                 frequency: int = 0, severity: str = "info",
                 related_operations: List[str] = None,
                 prevention_hint: str = ""):
        self.id = pattern_id
        self.error_type = error_type
        self.pattern = pattern  # 正则表达式模式
        self.frequency = frequency
        self.severity = severity  # critical, warning, info
        self.related_operations = related_operations or []
        self.prevention_hint = prevention_hint
        self.first_seen = datetime.now(timezone.utc).isoformat()
        self.last_seen = datetime.now(timezone.utc).isoformat()

    def to_dict(self):
        return {
            "id": self.id,
            "error_type": self.error_type,
            "pattern": self.pattern,
            "frequency": self.frequency,
            "severity": self.severity,
            "related_operations": self.related_operations,
            "prevention_hint": self.prevention_hint,
            "first_seen": self.first_seen,
            "last_seen": self.last_seen
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'ErrorPattern':
        obj = cls(
            data.get("id", ""),
            data.get("error_type", ""),
            data.get("pattern", ""),
            data.get("frequency", 0),
            data.get("severity", "info"),
            data.get("related_operations", []),
            data.get("prevention_hint", "")
        )
        obj.first_seen = data.get("first_seen", obj.first_seen)
        obj.last_seen = data.get("last_seen", obj.last_seen)
        return obj


class DefenseStrategy:
    """防御策略"""

    def __init__(self, strategy_id: str, name: str, description: str,
                 trigger_patterns: List[str] = None,
                 actions: List[Dict] = None,
                 enabled: bool = True):
        self.id = strategy_id
        self.name = name
        self.description = description
        self.trigger_patterns = trigger_patterns or []
        self.actions = actions or []  # [{"type": "check", "target": "..."}, {"type": "warn", "message": "..."}]
        self.enabled = enabled
        self.last_triggered = None
        self.trigger_count = 0

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "trigger_patterns": self.trigger_patterns,
            "actions": self.actions,
            "enabled": self.enabled,
            "last_triggered": self.last_triggered,
            "trigger_count": self.trigger_count
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'DefenseStrategy':
        obj = cls(
            data.get("id", ""),
            data.get("name", ""),
            data.get("description", ""),
            data.get("trigger_patterns", []),
            data.get("actions", []),
            data.get("enabled", True)
        )
        obj.last_triggered = data.get("last_triggered")
        obj.trigger_count = data.get("trigger_count", 0)
        return obj


class ErrorPrediction:
    """错误预测"""

    def __init__(self, prediction_id: str, predicted_error: str,
                 confidence: float, context: Dict = None,
                 recommended_action: str = ""):
        self.id = prediction_id
        self.predicted_error = predicted_error
        self.confidence = confidence  # 0-1
        self.context = context or {}
        self.recommended_action = recommended_action
        self.created_at = datetime.now(timezone.utc).isoformat()
        self.actual_occurred = None  # 是否实际发生

    def to_dict(self):
        return {
            "id": self.id,
            "predicted_error": self.predicted_error,
            "confidence": self.confidence,
            "context": self.context,
            "recommended_action": self.recommended_action,
            "created_at": self.created_at,
            "actual_occurred": self.actual_occurred
        }


class ErrorPatternLearningEngine:
    """智能错误模式学习与主动防御引擎"""

    # 预定义的常见错误模式
    DEFAULT_PATTERNS = [
        {
            "id": "clipboard_fail",
            "error_type": "clipboard_error",
            "pattern": r"SetClipboardData|Cannot open clipboard",
            "frequency": 0,
            "severity": "warning",
            "related_operations": ["clipboard_tool", "type"],
            "prevention_hint": "剪贴板操作在远程会话中可能失败，建议使用 keyboard_tool type 替代"
        },
        {
            "id": "vision_timeout",
            "error_type": "vision_timeout",
            "pattern": r"vision.*timeout|Vision.*failed",
            "frequency": 0,
            "severity": "warning",
            "related_operations": ["vision_proxy", "screenshot"],
            "prevention_hint": "视觉分析可能超时，建议设置较短超时或跳过视觉步骤"
        },
        {
            "id": "window_not_found",
            "error_type": "window_error",
            "pattern": r"窗口未找到|cannot find window|no such window",
            "frequency": 0,
            "severity": "warning",
            "related_operations": ["window_tool", "activate"],
            "prevention_hint": "窗口激活前应先检查窗口是否存在"
        },
        {
            "id": "process_not_ready",
            "error_type": "process_error",
            "pattern": r"进程.*未就绪|process.*not ready",
            "frequency": 0,
            "severity": "info",
            "related_operations": ["launch", "activate_process"],
            "prevention_hint": "进程启动后应等待足够时间再操作"
        },
        {
            "id": "unicode_error",
            "error_type": "encoding_error",
            "pattern": r"UnicodeEncodeError|gbk.*can't encode",
            "frequency": 0,
            "severity": "warning",
            "related_operations": ["print", "process_tool"],
            "prevention_hint": "处理包含中文的输出时使用安全的编码方式"
        }
    ]

    # 预定义的防御策略
    DEFAULT_DEFENSES = [
        {
            "id": "clipboard_defense",
            "name": "剪贴板防御",
            "description": "检测到剪贴板操作时，优先使用 keyboard_tool type",
            "trigger_patterns": ["clipboard", "paste"],
            "actions": [
                {"type": "check", "target": "session_type"},
                {"type": "warn", "message": "建议使用 keyboard_tool type 替代剪贴板操作"}
            ],
            "enabled": True
        },
        {
            "id": "vision_timeout_defense",
            "name": "视觉超时防御",
            "description": "视觉操作前检查 API 配置",
            "trigger_patterns": ["vision", "screenshot"],
            "actions": [
                {"type": "check", "target": "vision_config"},
                {"type": "warn", "message": "视觉功能可能超时，请设置合理超时时间"}
            ],
            "enabled": True
        },
        {
            "id": "window_activate_defense",
            "name": "窗口激活防御",
            "description": "窗口操作前检查窗口状态",
            "trigger_patterns": ["activate", "window"],
            "actions": [
                {"type": "check", "target": "window_exists"},
                {"type": "warn", "message": "窗口可能不存在，建议先列出窗口列表"}
            ],
            "enabled": True
        }
    ]

    def __init__(self):
        self.patterns = self._load_patterns()
        self.defenses = self._load_defenses()
        self.predictions = []

    def _load_patterns(self) -> Dict[str, ErrorPattern]:
        """加载错误模式"""
        data = load_json_file(PATTERN_FILE, {"patterns": []})
        return {p["id"]: ErrorPattern.from_dict(p) for p in data.get("patterns", [])}

    def _save_patterns(self):
        """保存错误模式"""
        data = {"patterns": [p.to_dict() for p in self.patterns.values()]}
        save_json_file(PATTERN_FILE, data)

    def _load_defenses(self) -> Dict[str, DefenseStrategy]:
        """加载防御策略"""
        data = load_json_file(DEFENSE_CONFIG_FILE, {"defenses": []})
        if not data.get("defenses"):
            # 初始化默认防御策略
            data = {"defenses": self.DEFAULT_DEFENSES}
            save_json_file(DEFENSE_CONFIG_FILE, data)
        return {d["id"]: DefenseStrategy.from_dict(d) for d in data.get("defenses", [])}

    def _save_defenses(self):
        """保存防御策略"""
        data = {"defenses": [d.to_dict() for d in self.defenses.values()]}
        save_json_file(DEFENSE_CONFIG_FILE, data)

    def learn_from_history(self, history_lines: int = 100) -> Dict[str, Any]:
        """从执行历史学习错误模式"""
        results = {
            "new_patterns_found": 0,
            "patterns_updated": 0,
            "errors_analyzed": 0,
            "summary": ""
        }

        # 读取最近的日志文件
        log_files = []
        if os.path.exists(LOGS_DIR):
            for f in os.listdir(LOGS_DIR):
                if f.startswith("behavior_") and f.endswith(".log"):
                    log_files.append(os.path.join(LOGS_DIR, f))

        # 收集所有错误信息
        error_patterns = defaultdict(list)
        for log_file in sorted(log_files, key=os.path.getmtime, reverse=True)[:3]:
            try:
                with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
                    lines = f.readlines()
                    for line in lines[-history_lines:]:
                        results["errors_analyzed"] += 1
                        # 查找错误关键词
                        error_keywords = ["error", "fail", "exception", "timeout", "cannot", "unable"]
                        line_lower = line.lower()
                        for keyword in error_keywords:
                            if keyword in line_lower:
                                # 提取错误上下文
                                error_patterns[keyword].append(line.strip())
                                break
            except Exception:
                continue

        # 分析错误模式并更新
        for error_type, contexts in error_patterns.items():
            if len(contexts) >= 2:  # 至少出现2次
                # 检查是否已存在
                existing = None
                for pid, pattern in self.patterns.items():
                    if pattern.error_type == error_type:
                        existing = pattern
                        break

                if existing:
                    # 更新已有模式
                    existing.frequency += len(contexts)
                    existing.last_seen = datetime.now(timezone.utc).isoformat()
                    results["patterns_updated"] += 1
                else:
                    # 创建新模式
                    new_pattern = ErrorPattern(
                        pattern_id=f"{error_type}_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
                        error_type=error_type,
                        pattern=f"{error_type}.*",
                        frequency=len(contexts),
                        severity="warning",
                        related_operations=[],
                        prevention_hint=f"从历史中学习到 {error_type} 类型错误"
                    )
                    self.patterns[new_pattern.id] = new_pattern
                    results["new_patterns_found"] += 1

        self._save_patterns()
        results["summary"] = f"分析了 {results['errors_analyzed']} 条日志，发现 {results['new_patterns_found']} 个新模式，更新了 {results['patterns_updated']} 个已有模式"
        return results

    def predict_errors(self, current_context: Dict = None) -> List[ErrorPrediction]:
        """预测可能发生的错误"""
        predictions = []
        context = current_context or {}

        # 基于已学习的模式进行预测
        for pattern in self.patterns.values():
            if pattern.frequency >= 2:  # 至少出现2次
                # 计算置信度（基于频率）
                confidence = min(0.9, pattern.frequency / 10.0)

                if confidence > 0.3:  # 阈值
                    prediction = ErrorPrediction(
                        prediction_id=f"pred_{pattern.id}_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
                        predicted_error=pattern.error_type,
                        confidence=confidence,
                        context=context,
                        recommended_action=pattern.prevention_hint
                    )
                    predictions.append(prediction)

        # 按置信度排序
        predictions.sort(key=lambda x: x.confidence, reverse=True)

        # 保存预测结果
        self.predictions = predictions
        save_json_file(PREDICTION_FILE, {
            "predictions": [p.to_dict() for p in predictions],
            "generated_at": datetime.now(timezone.utc).isoformat()
        })

        return predictions[:5]  # 最多返回5个预测

    def get_patterns(self) -> List[Dict]:
        """获取所有错误模式"""
        return [p.to_dict() for p in self.patterns.values()]

    def get_defenses(self) -> List[Dict]:
        """获取所有防御策略"""
        return [d.to_dict() for d in self.defenses.values()]

    def add_pattern(self, error_type: str, pattern: str, prevention_hint: str = "") -> Dict:
        """添加新的错误模式"""
        pattern_id = f"{error_type}_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
        new_pattern = ErrorPattern(
            pattern_id=pattern_id,
            error_type=error_type,
            pattern=pattern,
            frequency=1,
            severity="info",
            prevention_hint=prevention_hint
        )
        self.patterns[pattern_id] = new_pattern
        self._save_patterns()
        return {"status": "success", "pattern_id": pattern_id}

    def add_defense(self, name: str, description: str, trigger_patterns: List[str],
                   actions: List[Dict]) -> Dict:
        """添加新的防御策略"""
        strategy_id = f"defense_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
        new_defense = DefenseStrategy(
            strategy_id=strategy_id,
            name=name,
            description=description,
            trigger_patterns=trigger_patterns,
            actions=actions
        )
        self.defenses[strategy_id] = new_defense
        self._save_defenses()
        return {"status": "success", "defense_id": strategy_id}

    def apply_defense(self, context: Dict) -> List[Dict]:
        """应用防御策略"""
        applied = []
        current_operation = context.get("operation", "").lower()

        for defense in self.defenses.values():
            if not defense.enabled:
                continue

            # 检查是否应该触发
            for trigger in defense.trigger_patterns:
                if trigger.lower() in current_operation:
                    # 执行防御动作
                    for action in defense.actions:
                        applied.append({
                            "defense": defense.name,
                            "action": action
                        })
                    defense.last_triggered = datetime.now(timezone.utc).isoformat()
                    defense.trigger_count += 1
                    break

        self._save_defenses()
        return applied

    def get_status(self) -> Dict:
        """获取引擎状态"""
        return {
            "total_patterns": len(self.patterns),
            "total_defenses": len(self.defenses),
            "enabled_defenses": sum(1 for d in self.defenses.values() if d.enabled),
            "patterns_by_severity": {
                "critical": sum(1 for p in self.patterns.values() if p.severity == "critical"),
                "warning": sum(1 for p in self.patterns.values() if p.severity == "warning"),
                "info": sum(1 for p in self.patterns.values() if p.severity == "info")
            },
            "most_common_errors": [
                {"type": p.error_type, "frequency": p.frequency}
                for p in sorted(self.patterns.values(), key=lambda x: x.frequency, reverse=True)[:5]
            ]
        }


def main():
    parser = argparse.ArgumentParser(
        description="智能错误模式学习与主动防御引擎",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python error_pattern_learning_engine.py learn --history-lines 200
  python error_pattern_learning_engine.py predict
  python error_pattern_learning_engine.py patterns
  python error_pattern_learning_engine.py defense-config
  python error_pattern_learning_engine.py status
  python error_pattern_learning_engine.py add-pattern "custom_error" "custom.*pattern" "预防建议"
        """
    )
    parser.add_argument("command", choices=["learn", "predict", "patterns", "defense-config", "status", "add-pattern"],
                       help="要执行的命令")
    parser.add_argument("--history-lines", type=int, default=100, help="分析的历史日志行数")
    parser.add_argument("--apply", action="store_true", help="应用防御策略")
    parser.add_argument("--pattern-type", help="添加模式时的错误类型")
    parser.add_argument("--pattern", help="添加模式时的正则表达式")
    parser.add_argument("--hint", help="添加模式时的预防建议")

    args = parser.parse_args()
    engine = ErrorPatternLearningEngine()

    if args.command == "learn":
        result = engine.learn_from_history(args.history_lines)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "predict":
        predictions = engine.predict_errors()
        print(json.dumps({
            "predictions": [p.to_dict() for p in predictions],
            "count": len(predictions)
        }, ensure_ascii=False, indent=2))

    elif args.command == "patterns":
        patterns = engine.get_patterns()
        print(json.dumps({"patterns": patterns, "count": len(patterns)}, ensure_ascii=False, indent=2))

    elif args.command == "defense-config":
        defenses = engine.get_defenses()
        print(json.dumps({"defenses": defenses, "count": len(defenses)}, ensure_ascii=False, indent=2))

    elif args.command == "status":
        status = engine.get_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))

    elif args.command == "add-pattern":
        if not args.pattern_type or not args.pattern:
            print("错误: 需要提供 --pattern-type 和 --pattern 参数")
            return
        result = engine.add_pattern(args.pattern_type, args.pattern, args.hint or "")
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()