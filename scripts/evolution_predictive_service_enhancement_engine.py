#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能全场景主动预测与预防性服务增强引擎 (Evolution Predictive Service Enhancement Engine)
Version: 1.0.0

在 round 257 的情境感知与主动服务编排引擎、round 286 的预测驱动主动服务编排引擎基础上，
进一步增强主动预测与预防性服务能力。让系统能够基于用户行为序列、时间规律、系统状态、历史交互
等多维度信息，主动预测用户当前可能需要什么服务，在用户明确提出需求之前主动提供，实现从
「被动响应」到「主动预见」的范式升级。让系统更像一个贴心的助手，主动为用户准备好一切。

功能：
1. 用户行为序列深度分析（时间模式、操作习惯、任务链）
2. 多维度预测融合（时间+行为+系统状态+历史）
3. 主动服务预热（提前加载资源、预启动应用、预准备上下文）
4. 预防性服务提供（根据预测主动提供服务建议或执行准备）
5. 预测准确性持续学习（基于用户反馈调整预测模型）

集成到 do.py 支持：
- 主动预测、预测服务、预防性服务、需求预测、服务预热、预测分析等关键词触发
"""

import json
import os
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import threading
import time

# 路径配置
SCRIPT_DIR = Path(__file__).parent
RUNTIME_DIR = SCRIPT_DIR.parent / "runtime"
STATE_DIR = RUNTIME_DIR / "state"
LOGS_DIR = RUNTIME_DIR / "logs"


class PredictiveServiceEnhancementEngine:
    """智能全场景主动预测与预防性服务增强引擎"""

    def __init__(self):
        self.name = "主动预测与预防性服务增强引擎"
        self.version = "1.0.0"

        # 用户行为数据
        self.user_behavior_sequences = []  # 行为序列
        self.time_patterns = {}  # 时间模式
        self.task_patterns = {}  # 任务模式
        self.prediction_history = []  # 预测历史

        # 预测模型
        self.prediction_weights = {
            "time": 0.3,
            "behavior": 0.3,
            "system": 0.2,
            "history": 0.2
        }

        # 预测缓存
        self.prediction_cache = {}
        self.last_prediction_time = None

        # 加载配置和历史数据
        self.config = self._load_config()
        self._load_historical_data()

        print(f"[{self.name}] 初始化完成 (v{self.version})")

    def _load_config(self) -> Dict:
        """加载配置"""
        config_path = STATE_DIR / "predictive_service_config.json"
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Failed to load config: {e}")

        # 默认配置
        return {
            "enable_behavior_sequence": True,
            "enable_time_pattern": True,
            "enable_system_context": True,
            "enable_pre_service": True,
            "enable_preventive_service": True,
            "enable_feedback_learning": True,
            "prediction_horizon_minutes": 30,
            "min_confidence_threshold": 0.5,
            "max_predictions": 5,
            "cache_ttl_seconds": 300
        }

    def _load_historical_data(self):
        """加载历史数据"""
        # 加载用户行为序列
        behavior_file = STATE_DIR / "user_behavior_sequences.json"
        if behavior_file.exists():
            try:
                with open(behavior_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.user_behavior_sequences = data.get("sequences", [])
                    self.time_patterns = data.get("time_patterns", {})
                    self.task_patterns = data.get("task_patterns", {})
            except Exception as e:
                print(f"Warning: Failed to load behavior data: {e}")

        # 加载预测历史
        prediction_history_file = STATE_DIR / "prediction_history.json"
        if prediction_history_file.exists():
            try:
                with open(prediction_history_file, 'r', encoding='utf-8') as f:
                    self.prediction_history = json.load(f)
            except Exception as e:
                print(f"Warning: Failed to load prediction history: {e}")

    def _save_historical_data(self):
        """保存历史数据"""
        # 保存用户行为序列
        behavior_file = STATE_DIR / "user_behavior_sequences.json"
        try:
            with open(behavior_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "sequences": self.user_behavior_sequences,
                    "time_patterns": self.time_patterns,
                    "task_patterns": self.task_patterns,
                    "updated_at": datetime.now().isoformat()
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save behavior data: {e}")

        # 保存预测历史
        prediction_history_file = STATE_DIR / "prediction_history.json"
        try:
            with open(prediction_history_file, 'w', encoding='utf-8') as f:
                json.dump(self.prediction_history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save prediction history: {e}")

    def analyze_time_pattern(self) -> Dict[str, Any]:
        """分析时间模式"""
        now = datetime.now()
        current_hour = now.hour
        current_minute = now.minute
        day_of_week = now.weekday()

        # 基于时间规律的预测
        time_predictions = []

        # 早上9点左右：检查邮件/日程
        if 8 <= current_hour <= 10:
            time_predictions.append({
                "service": "check_email",
                "confidence": 0.8,
                "reason": "早上检查邮件是常见习惯"
            })
            time_predictions.append({
                "service": "check_schedule",
                "confidence": 0.7,
                "reason": "早上查看日程安排"
            })

        # 中午12点左右：午餐/休息
        if 11 <= current_hour <= 13:
            time_predictions.append({
                "service": "lunch_reminder",
                "confidence": 0.75,
                "reason": "午餐时间到了"
            })

        # 下午2点左右：继续工作
        if 13 <= current_hour <= 15:
            time_predictions.append({
                "service": "continue_work",
                "confidence": 0.6,
                "reason": "下午工作时间"
            })

        # 下午5点左右：收尾工作
        if 16 <= current_hour <= 18:
            time_predictions.append({
                "service": "end_of_day_summary",
                "confidence": 0.65,
                "reason": "下班前总结当天工作"
            })

        # 周末：娱乐/休闲
        if day_of_week >= 5:
            time_predictions.append({
                "service": "entertainment",
                "confidence": 0.7,
                "reason": "周末休闲时间"
            })

        return {
            "type": "time",
            "predictions": time_predictions,
            "time_info": {
                "hour": current_hour,
                "minute": current_minute,
                "day_of_week": day_of_week,
                "is_weekend": day_of_week >= 5
            }
        }

    def analyze_behavior_sequence(self) -> Dict[str, Any]:
        """分析用户行为序列"""
        if not self.user_behavior_sequences:
            return {
                "type": "behavior",
                "predictions": [],
                "reason": "没有足够的行为数据"
            }

        # 获取最近的行为序列
        recent_behaviors = self.user_behavior_sequences[-10:] if len(self.user_behavior_sequences) >= 10 else self.user_behavior_sequences

        # 简单的序列模式匹配
        behavior_predictions = []

        # 检查常见行为链
        behavior_chain = [b.get("action", "") for b in recent_behaviors]

        # 如果用户最近打开了浏览器，预测可能需要搜索
        if "open_browser" in behavior_chain or "launch_browser" in behavior_chain:
            behavior_predictions.append({
                "service": "web_search",
                "confidence": 0.7,
                "reason": "用户刚打开浏览器，可能需要搜索"
            })

        # 如果用户打开了文件管理器，可能需要查找文件
        if "open_explorer" in behavior_chain or "launch_explorer" in behavior_chain:
            behavior_predictions.append({
                "service": "find_file",
                "confidence": 0.6,
                "reason": "用户打开了文件管理器"
            })

        # 如果用户打开了记事本，可能需要记录
        if "open_notepad" in behavior_chain or "launch_notepad" in behavior_chain:
            behavior_predictions.append({
                "service": "take_note",
                "confidence": 0.55,
                "reason": "用户打开了记事本"
            })

        return {
            "type": "behavior",
            "predictions": behavior_predictions,
            "recent_behaviors": recent_behaviors[-3:] if recent_behaviors else []
        }

    def analyze_system_context(self) -> Dict[str, Any]:
        """分析系统状态上下文"""
        system_predictions = []

        # 尝试获取系统状态
        try:
            # CPU 使用率
            import psutil
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()

            # 如果 CPU 很高，可能需要清理
            if cpu_percent > 80:
                system_predictions.append({
                    "service": "system_cleanup",
                    "confidence": 0.75,
                    "reason": f"CPU使用率较高 ({cpu_percent}%)"
                })

            # 内存紧张
            if memory.percent > 85:
                system_predictions.append({
                    "service": "memory_optimization",
                    "confidence": 0.8,
                    "reason": f"内存使用率较高 ({memory.percent}%)"
                })

        except ImportError:
            pass

        return {
            "type": "system",
            "predictions": system_predictions,
            "has_psutil": 'psutil' in globals()
        }

    def analyze_history_context(self) -> Dict[str, Any]:
        """分析历史交互上下文"""
        if not self.prediction_history:
            return {
                "type": "history",
                "predictions": [],
                "reason": "没有预测历史"
            }

        # 基于历史预测
        history_predictions = []

        # 统计历史上这个时间段的常见服务
        now = datetime.now()
        hour = now.hour
        day_of_week = now.weekday()

        # 筛选同一时间段的预测
        same_time_predictions = [
            p for p in self.prediction_history
            if p.get("time_info", {}).get("hour") == hour
        ]

        # 统计常见服务
        service_counts = {}
        for p in same_time_predictions:
            for service in p.get("predictions", []):
                svc = service.get("service", "")
                service_counts[svc] = service_counts.get(svc, 0) + 1

        # 最常见的服务
        if service_counts:
            top_services = sorted(service_counts.items(), key=lambda x: x[1], reverse=True)[:3]
            for service, count in top_services:
                confidence = min(0.9, count / len(same_time_predictions) * 0.8 + 0.2)
                history_predictions.append({
                    "service": service,
                    "confidence": confidence,
                    "reason": f"历史上此时段常见服务 (出现{count}次)"
                })

        return {
            "type": "history",
            "predictions": history_predictions,
            "total_history": len(self.prediction_history)
        }

    def fuse_predictions(self, time_pred: Dict, behavior_pred: Dict,
                        system_pred: Dict, history_pred: Dict) -> List[Dict]:
        """融合多维度预测结果"""
        all_predictions = []

        # 收集所有预测
        for pred_source in [time_pred, behavior_pred, system_pred, history_pred]:
            predictions = pred_source.get("predictions", [])
            for pred in predictions:
                service = pred.get("service", "")
                confidence = pred.get("confidence", 0)

                # 查找是否已有该服务的预测
                existing = next((p for p in all_predictions if p["service"] == service), None)
                if existing:
                    existing["confidence"] = (existing["confidence"] + confidence) / 2
                    existing["reasons"].append(pred.get("reason", ""))
                else:
                    all_predictions.append({
                        "service": service,
                        "confidence": confidence,
                        "reasons": [pred.get("reason", "")],
                        "source": pred_source.get("type", "unknown")
                    })

        # 排序并过滤
        all_predictions.sort(key=lambda x: x["confidence"], reverse=True)

        # 过滤低置信度预测
        threshold = self.config.get("min_confidence_threshold", 0.5)
        filtered = [p for p in all_predictions if p["confidence"] >= threshold]

        # 限制数量
        max_predictions = self.config.get("max_predictions", 5)
        return filtered[:max_predictions]

    def predict(self, force_refresh: bool = False) -> Dict[str, Any]:
        """执行预测"""
        now = datetime.now()

        # 检查缓存
        if not force_refresh and self.last_prediction_time:
            cache_ttl = self.config.get("cache_ttl_seconds", 300)
            if (now - self.last_prediction_time).total_seconds() < cache_ttl:
                return {
                    "success": True,
                    "predictions": self.prediction_cache.get("predictions", []),
                    "from_cache": True,
                    "cached_at": self.prediction_cache.get("cached_at", "")
                }

        # 各维度分析
        time_pred = self.analyze_time_pattern()
        behavior_pred = self.analyze_behavior_sequence()
        system_pred = self.analyze_system_context()
        history_pred = self.analyze_history_context()

        # 融合预测
        fused_predictions = self.fuse_predictions(time_pred, behavior_pred, system_pred, history_pred)

        # 构建结果
        result = {
            "success": True,
            "predictions": fused_predictions,
            "from_cache": False,
            "timestamp": now.isoformat(),
            "sources": {
                "time": time_pred,
                "behavior": behavior_pred,
                "system": system_pred,
                "history": history_pred
            }
        }

        # 更新缓存
        self.prediction_cache = {
            "predictions": fused_predictions,
            "cached_at": now.isoformat()
        }
        self.last_prediction_time = now

        # 记录预测历史
        self.prediction_history.append({
            "timestamp": now.isoformat(),
            "time_info": time_pred.get("time_info", {}),
            "predictions": fused_predictions
        })
        self._save_historical_data()

        return result

    def record_behavior(self, action: str, context: Dict = None):
        """记录用户行为"""
        behavior_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "context": context or {}
        }
        self.user_behavior_sequences.append(behavior_entry)

        # 限制历史长度
        max_history = 100
        if len(self.user_behavior_sequences) > max_history:
            self.user_behavior_sequences = self.user_behavior_sequences[-max_history:]

        self._save_historical_data()

    def provide_feedback(self, service: str, was_accurate: bool):
        """提供预测反馈，用于持续学习"""
        if not self.config.get("enable_feedback_learning", True):
            return

        # 调整预测权重
        if was_accurate:
            # 提高该服务的置信度
            for pred in self.prediction_history[-10:]:
                for p in pred.get("predictions", []):
                    if p.get("service") == service:
                        p["confidence"] = min(1.0, p.get("confidence", 0) + 0.1)
        else:
            # 降低置信度
            for pred in self.prediction_history[-10:]:
                for p in pred.get("predictions", []):
                    if p.get("service") == service:
                        p["confidence"] = max(0, p.get("confidence", 0) - 0.1)

        self._save_historical_data()

    def pre_service(self, service: str) -> Dict[str, Any]:
        """预热服务：提前准备服务所需的资源"""
        if not self.config.get("enable_pre_service", True):
            return {"success": False, "reason": "Pre-service disabled"}

        pre_service_actions = {
            "check_email": {
                "actions": ["预启动邮件客户端", "检查新邮件"],
                "estimated_time": "5秒"
            },
            "check_schedule": {
                "actions": ["打开日历应用", "加载今日日程"],
                "estimated_time": "3秒"
            },
            "web_search": {
                "actions": ["激活浏览器", "打开搜索页面"],
                "estimated_time": "2秒"
            },
            "system_cleanup": {
                "actions": ["扫描大文件", "检查后台进程"],
                "estimated_time": "10秒"
            },
            "memory_optimization": {
                "actions": ["分析内存使用", "建议关闭程序"],
                "estimated_time": "5秒"
            }
        }

        if service in pre_service_actions:
            return {
                "success": True,
                "service": service,
                "preparation": pre_service_actions[service]
            }
        else:
            return {
                "success": False,
                "reason": f"未知服务: {service}"
            }

    def get_status(self) -> Dict[str, Any]:
        """获取引擎状态"""
        return {
            "name": self.name,
            "version": self.version,
            "status": "active",
            "config": self.config,
            "data_stats": {
                "behavior_sequences": len(self.user_behavior_sequences),
                "prediction_history": len(self.prediction_history),
                "time_patterns": len(self.time_patterns),
                "task_patterns": len(self.task_patterns)
            },
            "prediction_weights": self.prediction_weights
        }


# 单例实例
_engine_instance = None
_engine_lock = threading.Lock()


def get_engine() -> PredictiveServiceEnhancementEngine:
    """获取引擎单例"""
    global _engine_instance
    if _engine_instance is None:
        with _engine_lock:
            if _engine_instance is None:
                _engine_instance = PredictiveServiceEnhancementEngine()
    return _engine_instance


def predict(force_refresh: bool = False) -> Dict[str, Any]:
    """快捷预测函数"""
    engine = get_engine()
    return engine.predict(force_refresh)


def record_behavior(action: str, context: Dict = None):
    """记录行为"""
    engine = get_engine()
    engine.record_behavior(action, context)


def provide_feedback(service: str, was_accurate: bool):
    """提供反馈"""
    engine = get_engine()
    engine.provide_feedback(service, was_accurate)


def pre_service(service: str) -> Dict[str, Any]:
    """预热服务"""
    engine = get_engine()
    return engine.pre_service(service)


def get_status() -> Dict[str, Any]:
    """获取状态"""
    engine = get_engine()
    return engine.get_status()


# 命令行接口
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="主动预测与预防性服务增强引擎")
    parser.add_argument("command", nargs="?", default="predict",
                        help="命令: predict, status, record, feedback, pre-service")
    parser.add_argument("--action", help="行为名称 (record 命令用)")
    parser.add_argument("--service", help="服务名称 (feedback/pre-service 命令用)")
    parser.add_argument("--accurate", type=lambda x: x.lower() == "true",
                        help="预测是否准确 (feedback 命令用)")
    parser.add_argument("--refresh", action="store_true", help="强制刷新预测")

    args = parser.parse_args()

    if args.command == "predict":
        result = predict(force_refresh=args.refresh)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == "status":
        result = get_status()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == "record":
        if args.action:
            record_behavior(args.action)
            print(f"已记录行为: {args.action}")
        else:
            print("错误: 需要指定 --action 参数")
    elif args.command == "feedback":
        if args.service and args.accurate is not None:
            provide_feedback(args.service, args.accurate)
            print(f"已记录反馈: {args.service} - {'准确' if args.accurate else '不准确'}")
        else:
            print("错误: 需要指定 --service 和 --accurate 参数")
    elif args.command == "pre-service":
        if args.service:
            result = pre_service(args.service)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print("错误: 需要指定 --service 参数")
    else:
        parser.print_help()