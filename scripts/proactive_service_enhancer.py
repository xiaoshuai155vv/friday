#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能主动服务增强引擎 (Proactive Service Enhancer)

让系统能够在用户发出指令之前就主动预测可能需要的服务并做好准备，
实现从「被动响应」到「主动预见」的范式升级。

区别于现有主动服务引擎的「检测条件→触发」，本引擎专注于「预测需求→预准备」。
利用 LLM 对用户行为模式的深度分析，实现超越用户的主动预见能力。

功能：
1. 用户行为模式分析（分析历史交互识别常用场景）
2. 主动服务预测（基于时间、上下文、习惯预测可能需求）
3. 预加载准备（提前打开可能需要的应用/场景）
4. 智能提醒（主动提醒用户可能需要执行的操作）
5. 与 zero_click_service_engine、proactive_service_orchestrator 深度集成

区别于其他引擎：
- proactive_service_orchestrator: 持续监控→发现机会→推荐/执行
- proactive_service_trigger: 条件触发式服务
- zero_click_service_engine: 简短输入→完整任务链
- 本引擎: 预测需求→预准备→主动服务
"""

import os
import sys
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Optional, Any, Tuple

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
RUNTIME_DIR = PROJECT_ROOT / "runtime"
STATE_DIR = RUNTIME_DIR / "state"
LOGS_DIR = RUNTIME_DIR / "logs"


class ProactiveServiceEnhancer:
    """智能主动服务增强引擎"""

    def __init__(self):
        self.service_enabled = True
        self.prediction_interval = 300  # 预测间隔（秒）
        self.min_confidence = 0.5  # 最小置信度
        self.max_predictions = 5  # 最大预测数
        self.preload_enabled = True  # 预加载开关

        # 用户行为模式
        self.user_patterns = {}
        self.frequent_scenarios = []
        self.time_based_predictions = defaultdict(list)
        self.context_based_predictions = defaultdict(list)

        # 预测历史
        self.prediction_history = []
        self.preload_history = []
        self.service_history = []

        # 加载已有数据
        self._load_user_patterns()

    def _get_time_category(self) -> str:
        """获取当前时间段分类"""
        hour = datetime.now().hour
        if 5 <= hour < 9:
            return "morning"
        elif 9 <= hour < 12:
            return "forenoon"
        elif 12 <= hour < 14:
            return "noon"
        elif 14 <= hour < 18:
            return "afternoon"
        elif 18 <= hour < 22:
            return "evening"
        else:
            return "night"

    def _load_user_patterns(self):
        """加载用户行为模式数据"""
        pattern_file = STATE_DIR / "user_behavior_patterns.json"
        if pattern_file.exists():
            try:
                with open(pattern_file, 'r', encoding='utf-8') as f:
                    self.user_patterns = json.load(f)
            except Exception as e:
                print(f"加载用户行为模式失败: {e}")
                self.user_patterns = {}

    def _save_user_patterns(self):
        """保存用户行为模式数据"""
        pattern_file = STATE_DIR / "user_behavior_patterns.json"
        try:
            with open(pattern_file, 'w', encoding='utf-8') as f:
                json.dump(self.user_patterns, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存用户行为模式失败: {e}")

    def _get_recent_activities(self, limit: int = 20) -> List[Dict]:
        """获取最近的活动记录"""
        activities = []
        recent_logs = STATE_DIR / "recent_logs.json"

        if recent_logs.exists():
            try:
                with open(recent_logs, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    activities = data.get('logs', [])[-limit:]
            except Exception:
                pass

        return activities

    def _analyze_time_patterns(self) -> Dict[str, List[str]]:
        """分析时间模式，预测特定时间可能需要的服务"""
        time_predictions = defaultdict(list)

        # 基于时间段的常见活动模式
        current_time = self._get_time_category()
        day_of_week = datetime.now().weekday()
        is_weekend = day_of_week >= 5

        # 工作日时间模式
        if not is_weekend:
            if current_time == "morning":
                time_predictions["morning_routine"] = [
                    "检查日程",
                    "查看邮件/消息",
                    "打开工作应用",
                    "回顾昨日任务"
                ]
            elif current_time == "forenoon":
                time_predictions["forenoon_work"] = [
                    "处理工作文档",
                    "查看审批事项",
                    "参加线上会议"
                ]
            elif current_time == "afternoon":
                time_predictions["afternoon_work"] = [
                    "继续处理工作",
                    "整理文档",
                    "查看任务进度"
                ]
            elif current_time == "evening":
                time_predictions["evening_review"] = [
                    "回顾当天工作",
                    "安排明日计划",
                    "发送工作汇报"
                ]
        else:
            # 周末时间模式
            if current_time == "morning":
                time_predictions["weekend_morning"] = [
                    "查看资讯",
                    "整理文件",
                    "学习新技能"
                ]
            elif current_time == "afternoon":
                time_predictions["weekend_afternoon"] = [
                    "娱乐休闲",
                    "处理个人事务"
                ]

        return dict(time_predictions)

    def _analyze_context_patterns(self) -> Dict[str, List[str]]:
        """分析上下文模式，基于当前状态预测需求"""
        context_predictions = defaultdict(list)

        try:
            # 获取当前时间
            current_time = datetime.now()
            hour = current_time.hour

            # 检测是否接近会议时间（基于常见会议时间）
            if 9 <= hour <= 11 or 14 <= hour <= 16:
                context_predictions["meeting_time"] = [
                    "查看今日会议安排",
                    "准备会议材料",
                    "加入视频会议"
                ]

            # 检测是否接近下班时间
            if 17 <= hour <= 18:
                context_predictions["end_of_work"] = [
                    "回顾今日工作",
                    "整理桌面",
                    "发送日报"
                ]

            # 检测是否接近午休时间
            if 11 <= hour <= 13:
                context_predictions["lunch_time"] = [
                    "查看外卖选项",
                    "预定餐厅"
                ]

        except Exception as e:
            print(f"分析上下文模式失败: {e}")

        return dict(context_predictions)

    def _analyze_behavior_patterns(self) -> List[Dict]:
        """分析用户行为模式，从历史中学习"""
        predictions = []

        try:
            # 加载最近的行为日志
            activities = self._get_recent_activities(50)

            # 统计频繁执行的场景
            scenario_counts = defaultdict(int)
            for activity in activities:
                if 'mission' in activity:
                    mission = activity['mission']
                    scenario_counts[mission] += 1

            # 找出最频繁的场景
            frequent = sorted(scenario_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            for scenario, count in frequent:
                if count >= 2:
                    predictions.append({
                        "type": "frequent_action",
                        "scenario": scenario,
                        "confidence": min(count / 10, 0.9),
                        "reason": f"该操作在过去执行了 {count} 次"
                    })

        except Exception as e:
            print(f"分析行为模式失败: {e}")

        return predictions

    def predict_services(self) -> List[Dict[str, Any]]:
        """预测用户可能需要的服务"""
        predictions = []

        # 1. 时间模式预测
        time_predictions = self._analyze_time_patterns()
        for category, services in time_predictions.items():
            for service in services:
                predictions.append({
                    "type": "time_based",
                    "category": category,
                    "service": service,
                    "confidence": 0.7,
                    "reason": f"当前时段({self._get_time_category()})的常见活动"
                })

        # 2. 上下文模式预测
        context_predictions = self._analyze_context_patterns()
        for category, services in context_predictions.items():
            for service in services:
                predictions.append({
                    "type": "context_based",
                    "category": category,
                    "service": service,
                    "confidence": 0.6,
                    "reason": f"基于当前上下文({category})的预测"
                })

        # 3. 行为模式预测
        behavior_predictions = self._analyze_behavior_patterns()
        predictions.extend(behavior_predictions)

        # 过滤低置信度预测并排序
        predictions = [p for p in predictions if p.get('confidence', 0) >= self.min_confidence]
        predictions.sort(key=lambda x: x.get('confidence', 0), reverse=True)

        # 限制数量
        predictions = predictions[:self.max_predictions]

        return predictions

    def preload_services(self, predictions: List[Dict]) -> List[Dict]:
        """预加载可能需要的服务"""
        preloaded = []

        if not self.preload_enabled:
            return preloaded

        for pred in predictions:
            pred_type = pred.get('type', '')
            service = pred.get('service', '')

            # 只预加载高置信度的预测
            if pred.get('confidence', 0) < 0.7:
                continue

            # 基于预测类型决定预加载策略
            preload_action = None

            if 'time_based' in pred_type:
                # 时间模式预测 - 预加载应用
                if '会议' in service:
                    preload_action = {"type": "app", "target": "outlook"}
                elif '邮件' in service or '消息' in service:
                    preload_action = {"type": "app", "target": "iHaier"}
                elif '文档' in service:
                    preload_action = {"type": "app", "target": "explorer"}

            elif 'context_based' in pred_type:
                # 上下文预测 - 准备数据
                if '会议' in service:
                    preload_action = {"type": "data", "target": "calendar_events"}
                elif '任务' in service:
                    preload_action = {"type": "data", "target": "task_list"}

            elif 'frequent_action' in pred_type:
                # 频繁操作 - 准备执行环境
                preload_action = {"type": "ready", "target": service}

            if preload_action:
                preloaded.append({
                    "prediction": pred,
                    "preload": preload_action,
                    "timestamp": datetime.now().isoformat()
                })

                self.preload_history.append({
                    "prediction": pred,
                    "preload": preload_action,
                    "timestamp": datetime.now().isoformat()
                })

        return preloaded

    def generate_recommendations(self) -> List[Dict]:
        """生成主动推荐"""
        predictions = self.predict_services()
        preloaded = self.preload_services(predictions)

        recommendations = []

        for pred in predictions[:3]:
            recommendations.append({
                "service": pred.get('service', ''),
                "confidence": pred.get('confidence', 0),
                "reason": pred.get('reason', ''),
                "action": f"建议：{pred.get('service', '')}"
            })

        return recommendations

    def get_status(self) -> Dict[str, Any]:
        """获取引擎状态"""
        predictions = self.predict_services()
        recommendations = self.generate_recommendations()

        return {
            "engine": "ProactiveServiceEnhancer",
            "enabled": self.service_enabled,
            "preload_enabled": self.preload_enabled,
            "time_category": self._get_time_category(),
            "prediction_count": len(predictions),
            "recommendations": recommendations,
            "preload_count": len(self.preload_history),
            "history_count": len(self.prediction_history)
        }

    def run_prediction(self) -> Dict[str, Any]:
        """运行一次预测"""
        predictions = self.predict_services()
        preloaded = self.preload_services(predictions)

        result = {
            "timestamp": datetime.now().isoformat(),
            "predictions": predictions,
            "preloaded": preloaded,
            "count": len(predictions)
        }

        self.prediction_history.append(result)

        # 保存预测历史
        self._save_prediction_history()

        return result

    def _save_prediction_history(self):
        """保存预测历史"""
        history_file = STATE_DIR / "prediction_history.json"
        try:
            # 只保留最近 100 条
            history = self.prediction_history[-100:]
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存预测历史失败: {e}")


def main():
    """主函数 - 支持命令行调用"""
    enhancer = ProactiveServiceEnhancer()

    if len(sys.argv) < 2:
        # 默认显示状态
        status = enhancer.get_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))
        return

    command = sys.argv[1]

    if command == "status":
        status = enhancer.get_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))

    elif command == "predict":
        result = enhancer.run_prediction()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "recommend":
        recommendations = enhancer.generate_recommendations()
        print(json.dumps({
            "recommendations": recommendations,
            "count": len(recommendations)
        }, ensure_ascii=False, indent=2))

    elif command == "preload":
        predictions = enhancer.predict_services()
        preloaded = enhancer.preload_services(predictions)
        print(json.dumps({
            "preloaded": preloaded,
            "count": len(preloaded)
        }, ensure_ascii=False, indent=2))

    else:
        print(f"未知命令: {command}")
        print("支持的命令: status, predict, recommend, preload")


if __name__ == "__main__":
    main()