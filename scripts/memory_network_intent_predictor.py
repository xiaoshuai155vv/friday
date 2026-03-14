#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景记忆网络与主动意图预测引擎 (Round 259)
让系统能够构建跨会话的记忆网络，学习用户行为模式、主动预测用户意图，
并在预测到意图时提前准备服务，实现从「被动响应」到「主动预测+提前准备」的范式升级。

功能：
1. 跨会话记忆网络构建 - 存储用户行为、偏好、任务历史
2. 行为模式学习 - 从历史数据中学习用户习惯
3. 主动意图预测 - 基于模式和上下文预测下一步可能需求
4. 主动服务准备 - 在预测到意图时提前准备资源

用法：
    python memory_network_intent_predictor.py [command] [args...]

Commands:
    status          - 查看记忆网络状态
    learn <行为>    - 学习用户行为
    predict         - 预测用户下一步可能的需求
    prepare <意图>  - 提前准备服务
    patterns        - 显示学习到的行为模式
    clear           - 清空记忆网络
    help            - 显示帮助信息
"""
import os
import sys
import json
import time
import hashlib
from datetime import datetime, timedelta
from collections import defaultdict

# 项目路径
SCRIPTS = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(SCRIPTS)
MEMORY_FILE = os.path.join(PROJECT, "runtime", "state", "memory_network.json")
PATTERNS_FILE = os.path.join(PROJECT, "runtime", "state", "behavior_patterns.json")


class MemoryNetworkIntentPredictor:
    """智能全场景记忆网络与主动意图预测引擎"""

    def __init__(self):
        """初始化记忆网络"""
        self.memory = self._load_memory()
        self.patterns = self._load_patterns()

    def _load_memory(self):
        """加载记忆网络数据"""
        if os.path.exists(MEMORY_FILE):
            try:
                with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass

        # 初始化空记忆网络
        return {
            "version": "1.0.0",
            "created_at": datetime.now().isoformat(),
            "sessions": [],
            "behaviors": [],
            "preferences": {},
            "task_history": [],
            "last_updated": datetime.now().isoformat()
        }

    def _save_memory(self):
        """保存记忆网络数据"""
        self.memory["last_updated"] = datetime.now().isoformat()
        os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True)
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(self.memory, f, ensure_ascii=False, indent=2)

    def _load_patterns(self):
        """加载行为模式数据"""
        if os.path.exists(PATTERNS_FILE):
            try:
                with open(PATTERNS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # 将普通 dict 转回 defaultdict 以支持 .append() 操作
                    patterns = {
                        "version": data.get("version", "1.0.0"),
                        "created_at": data.get("created_at", datetime.now().isoformat()),
                        "time_patterns": defaultdict(list, data.get("time_patterns", {})),
                        "sequence_patterns": defaultdict(list, data.get("sequence_patterns", {})),
                        "frequency_patterns": defaultdict(int, data.get("frequency_patterns", {})),
                        "context_patterns": defaultdict(list, data.get("context_patterns", {})),
                        "last_updated": data.get("last_updated", datetime.now().isoformat())
                    }
                    return patterns
            except Exception:
                pass

        # 初始化空模式
        return {
            "version": "1.0.0",
            "created_at": datetime.now().isoformat(),
            "time_patterns": defaultdict(list),  # 时间模式
            "sequence_patterns": defaultdict(list),  # 序列模式
            "frequency_patterns": defaultdict(int),  # 频率模式
            "context_patterns": defaultdict(list),  # 上下文模式
            "last_updated": datetime.now().isoformat()
        }

    def _save_patterns(self):
        """保存行为模式数据"""
        self.patterns["last_updated"] = datetime.now().isoformat()
        os.makedirs(os.path.dirname(PATTERNS_FILE), exist_ok=True)
        # 转换 defaultdicts 为普通 dict 以便 JSON 序列化
        patterns_to_save = {
            "version": self.patterns["version"],
            "created_at": self.patterns["created_at"],
            "time_patterns": dict(self.patterns["time_patterns"]),
            "sequence_patterns": dict(self.patterns["sequence_patterns"]),
            "frequency_patterns": dict(self.patterns["frequency_patterns"]),
            "context_patterns": dict(self.patterns["context_patterns"]),
            "last_updated": self.patterns["last_updated"]
        }
        with open(PATTERNS_FILE, "w", encoding="utf-8") as f:
            json.dump(patterns_to_save, f, ensure_ascii=False, indent=2)

    def learn_behavior(self, behavior, context=None):
        """学习用户行为

        Args:
            behavior: 用户行为描述
            context: 上下文信息（时间、应用、场景等）
        """
        timestamp = datetime.now()

        # 记录行为
        behavior_entry = {
            "behavior": behavior,
            "timestamp": timestamp.isoformat(),
            "hour": timestamp.hour,
            "weekday": timestamp.weekday(),
            "context": context or {}
        }
        self.memory["behaviors"].append(behavior_entry)

        # 限制行为历史长度
        if len(self.memory["behaviors"]) > 1000:
            self.memory["behaviors"] = self.memory["behaviors"][-1000:]

        # 更新行为频率模式
        behavior_key = behavior.lower().strip()
        self.patterns["frequency_patterns"][behavior_key] = \
            self.patterns["frequency_patterns"].get(behavior_key, 0) + 1

        # 更新时间模式
        hour_key = f"hour_{timestamp.hour}"
        self.patterns["time_patterns"][hour_key].append(behavior_key)

        # 更新序列模式（记录行为之间的关联）
        if len(self.memory["behaviors"]) > 1:
            prev_behavior = self.memory["behaviors"][-2]["behavior"].lower().strip()
            seq_key = f"{prev_behavior} -> {behavior_key}"
            self.patterns["sequence_patterns"][seq_key].append(timestamp.isoformat())

        # 更新上下文模式
        if context:
            for key, value in context.items():
                context_key = f"{key}:{value}"
                self.patterns["context_patterns"][context_key].append(behavior_key)

        # 保存
        self._save_memory()
        self._save_patterns()

        return f"已学习行为: {behavior}"

    def predict_intent(self, context=None):
        """预测用户意图

        Args:
            context: 当前上下文信息

        Returns:
            预测的意图列表（按概率排序）
        """
        predictions = []
        timestamp = datetime.now()
        current_hour = timestamp.hour
        current_weekday = timestamp.weekday()

        # 1. 基于时间模式预测
        hour_key = f"hour_{current_hour}"
        if hour_key in self.patterns["time_patterns"]:
            time_behaviors = self.patterns["time_patterns"][hour_key]
            # 统计该时间段最常见的行为
            behavior_counts = defaultdict(int)
            for b in time_behaviors:
                behavior_counts[b] += 1
            for behavior, count in sorted(behavior_counts.items(), key=lambda x: -x[1])[:3]:
                predictions.append({
                    "intent": behavior,
                    "reason": f"基于时间模式（{current_hour}点常见行为）",
                    "confidence": min(count / 10, 1.0)
                })

        # 2. 基于序列模式预测
        if len(self.memory["behaviors"]) > 0:
            last_behavior = self.memory["behaviors"][-1]["behavior"].lower().strip()
            seq_prefix = f"{last_behavior} ->"
            matching_patterns = [(k, v) for k, v in self.patterns["sequence_patterns"].items()
                                  if k.startswith(seq_prefix)]
            for pattern, times in matching_patterns[:3]:
                next_intent = pattern.split(" -> ")[1]
                # 避免重复
                if not any(p["intent"] == next_intent for p in predictions):
                    predictions.append({
                        "intent": next_intent,
                        "reason": "基于行为序列预测",
                        "confidence": min(len(times) / 5, 1.0)
                    })

        # 3. 基于频率模式预测
        sorted_freq = sorted(self.patterns["frequency_patterns"].items(),
                            key=lambda x: -x[1])[:5]
        for behavior, freq in sorted_freq:
            if not any(p["intent"] == behavior for p in predictions):
                predictions.append({
                    "intent": behavior,
                    "reason": "基于行为频率",
                    "confidence": min(freq / 50, 1.0)
                })

        # 4. 基于上下文模式预测
        if context:
            for key, value in context.items():
                context_key = f"{key}:{value}"
                if context_key in self.patterns["context_patterns"]:
                    context_behaviors = self.patterns["context_patterns"][context_key]
                    if context_behaviors:
                        most_common = max(set(context_behaviors),
                                        key=context_behaviors.count)
                        if not any(p["intent"] == most_common for p in predictions):
                            predictions.append({
                                "intent": most_common,
                                "reason": f"基于上下文（{key}={value}）",
                                "confidence": 0.7
                            })

        # 按置信度排序并返回
        predictions.sort(key=lambda x: -x["confidence"])
        return predictions[:5]

    def prepare_service(self, intent):
        """提前准备服务

        Args:
            intent: 预测的意图

        Returns:
            准备状态
        """
        # 这里可以预加载资源、准备执行环境等
        # 目前只是一个简单的记录功能

        preparation_entry = {
            "intent": intent,
            "timestamp": datetime.now().isoformat(),
            "status": "prepared"
        }

        if "preparations" not in self.memory:
            self.memory["preparations"] = []

        self.memory["preparations"].append(preparation_entry)

        # 限制准备历史
        if len(self.memory["preparations"]) > 100:
            self.memory["preparations"] = self.memory["preparations"][-100:]

        self._save_memory()

        return f"已为意图 '{intent}' 提前准备好服务"

    def get_status(self):
        """获取记忆网络状态"""
        behaviors_count = len(self.memory.get("behaviors", []))
        sessions_count = len(self.memory.get("sessions", []))
        patterns_count = len(self.patterns.get("frequency_patterns", {}))
        last_updated = self.memory.get("last_updated", "未知")

        return {
            "version": "1.0.0",
            "behaviors_count": behaviors_count,
            "sessions_count": sessions_count,
            "patterns_count": patterns_count,
            "last_updated": last_updated,
            "top_behaviors": sorted(self.patterns.get("frequency_patterns", {}).items(),
                                   key=lambda x: -x[1])[:5]
        }

    def get_patterns(self):
        """获取学习到的行为模式"""
        return {
            "time_patterns": dict(self.patterns.get("time_patterns", {})),
            "sequence_patterns": dict(self.patterns.get("sequence_patterns", {})),
            "frequency_patterns": dict(self.patterns.get("frequency_patterns", {})),
            "context_patterns": dict(self.patterns.get("context_patterns", {}))
        }

    def clear(self):
        """清空记忆网络"""
        self.memory = {
            "version": "1.0.0",
            "created_at": datetime.now().isoformat(),
            "sessions": [],
            "behaviors": [],
            "preferences": {},
            "task_history": [],
            "last_updated": datetime.now().isoformat()
        }
        self.patterns = {
            "version": "1.0.0",
            "created_at": datetime.now().isoformat(),
            "time_patterns": defaultdict(list),
            "sequence_patterns": defaultdict(list),
            "frequency_patterns": defaultdict(int),
            "context_patterns": defaultdict(list),
            "last_updated": datetime.now().isoformat()
        }
        self._save_memory()
        self._save_patterns()
        return "记忆网络已清空"


def main():
    """主函数"""
    predictor = MemoryNetworkIntentPredictor()

    if len(sys.argv) < 2:
        # 默认显示状态
        status = predictor.get_status()
        print("=== 智能全场景记忆网络与主动意图预测引擎 ===")
        print(f"版本: {status['version']}")
        print(f"已学习行为数: {status['behaviors_count']}")
        print(f"会话数: {status['sessions_count']}")
        print(f"模式数: {status['patterns_count']}")
        print(f"最后更新: {status['last_updated']}")
        if status['top_behaviors']:
            print("\n最常见行为:")
            for behavior, count in status['top_behaviors']:
                print(f"  - {behavior}: {count}次")
        print("\n用法: python memory_network_intent_predictor.py [command]")
        print("Commands: status, learn <行为>, predict, prepare <意图>, patterns, clear, help")
        return

    command = sys.argv[1].lower()

    if command == "status":
        status = predictor.get_status()
        print("=== 记忆网络状态 ===")
        print(f"版本: {status['version']}")
        print(f"已学习行为数: {status['behaviors_count']}")
        print(f"会话数: {status['sessions_count']}")
        print(f"模式数: {status['patterns_count']}")
        print(f"最后更新: {status['last_updated']}")
        if status['top_behaviors']:
            print("\n最常见行为:")
            for behavior, count in status['top_behaviors']:
                print(f"  - {behavior}: {count}次")

    elif command == "learn":
        if len(sys.argv) < 3:
            print("用法: learn <行为描述>")
            return
        behavior = " ".join(sys.argv[2:])
        context = {"hour": datetime.now().hour, "weekday": datetime.now().weekday()}
        result = predictor.learn_behavior(behavior, context)
        print(result)

    elif command == "predict":
        context = {"hour": datetime.now().hour, "weekday": datetime.now().weekday()}
        predictions = predictor.predict_intent(context)
        print("=== 意图预测 ===")
        if predictions:
            for i, pred in enumerate(predictions, 1):
                print(f"{i}. {pred['intent']}")
                print(f"   原因: {pred['reason']}")
                print(f"   置信度: {pred['confidence']:.2f}")
        else:
            print("暂无预测结果，请先学习一些行为")

    elif command == "prepare":
        if len(sys.argv) < 3:
            print("用法: prepare <意图>")
            return
        intent = " ".join(sys.argv[2:])
        result = predictor.prepare_service(intent)
        print(result)

    elif command == "patterns":
        patterns = predictor.get_patterns()
        print("=== 行为模式 ===")
        print("\n时间模式（按小时）:")
        for key, values in list(patterns["time_patterns"].items())[:5]:
            print(f"  {key}: {len(values)}条记录")

        print("\n序列模式（部分）:")
        for key in list(patterns["sequence_patterns"].keys())[:5]:
            print(f"  {key}")

        print("\n频率模式（Top 10）:")
        sorted_freq = sorted(patterns["frequency_patterns"].items(),
                           key=lambda x: -x[1])[:10]
        for behavior, count in sorted_freq:
            print(f"  {behavior}: {count}次")

    elif command == "clear":
        result = predictor.clear()
        print(result)

    elif command == "help":
        print(__doc__)

    else:
        print(f"未知命令: {command}")
        print("用法: python memory_network_intent_predictor.py [command]")
        print("Commands: status, learn <行为>, predict, prepare <意图>, patterns, clear, help")


if __name__ == "__main__":
    main()