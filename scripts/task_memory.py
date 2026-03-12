#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能任务记忆与预测中心
实现跨模块任务追踪、用户意图预测和主动任务规划
"""

import sys
import os
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from collections import defaultdict

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# 从现有模块导入所需功能
from context_memory import ContextMemory
from user_behavior_learner import UserBehaviorLearner
from task_execution_strategy import TaskExecutionStrategy
from system_health_check import SystemHealthCheck

class TaskMemory:
    """智能任务记忆与预测中心"""

    def __init__(self, storage_path="runtime/state/task_memory.json"):
        """
        初始化任务记忆中心

        Args:
            storage_path: 存储任务记忆的文件路径
        """
        self.storage_path = storage_path
        self.context_memory = ContextMemory()
        self.behavior_learner = UserBehaviorLearner()
        self.strategy_engine = TaskExecutionStrategy()
        self.health_checker = SystemHealthCheck()

        # 加载已有任务记忆
        self.tasks = self._load_tasks()

    def _load_tasks(self) -> Dict:
        """从文件加载任务记忆"""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载任务记忆失败: {e}")
                return {}
        return {}

    def _save_tasks(self):
        """保存任务记忆到文件"""
        try:
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(self.tasks, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存任务记忆失败: {e}")

    def record_task(self, task_id: str, task_info: Dict[str, Any]):
        """
        记录任务执行信息

        Args:
            task_id: 任务唯一标识
            task_info: 任务详细信息
        """
        self.tasks[task_id] = {
            "id": task_id,
            "timestamp": datetime.now().isoformat(),
            "info": task_info,
            "status": "completed"  # 可以是 pending/completed/failed
        }
        self._save_tasks()

        # 同时记录到用户行为学习模块
        self.behavior_learner.record_behavior(task_info.get('intent', ''), task_info)

    def get_task_history(self, limit: int = 10) -> List[Dict]:
        """
        获取任务历史记录

        Args:
            limit: 返回记录数量限制

        Returns:
            任务历史列表
        """
        # 按时间排序并返回最新记录
        sorted_tasks = sorted(self.tasks.values(),
                            key=lambda x: x['timestamp'],
                            reverse=True)
        return sorted_tasks[:limit]

    def predict_user_intent(self, context: str = "") -> Dict[str, Any]:
        """
        预测用户意图

        Args:
            context: 当前上下文信息

        Returns:
            预测结果，包含意图和建议
        """
        # 获取上下文信息
        context_data = self.context_memory.get_context(context) if context else {}

        # 从用户行为学习中获取偏好
        user_preferences = self.behavior_learner.get_user_preferences()

        # 从系统健康状态获取当前状态
        health_status = self.health_checker.check_health()

        # 综合分析预测用户意图
        predicted_intent = {
            "context": context_data,
            "preferences": user_preferences,
            "health_status": health_status,
            "predicted_intent": self._analyze_intent(context_data, user_preferences, health_status),
            "suggestions": self._generate_suggestions(context_data, user_preferences, health_status)
        }

        return predicted_intent

    def _analyze_intent(self, context_data: Dict, user_preferences: Dict, health_status: Dict) -> str:
        """
        分析用户意图

        Args:
            context_data: 上下文数据
            user_preferences: 用户偏好
            health_status: 系统健康状态

        Returns:
            预测的用户意图
        """
        # 基于当前上下文和用户偏好进行简单分析
        if health_status.get('cpu_usage', 0) > 80:
            return "系统负载高，建议执行轻量级任务"
        elif context_data.get('time_of_day') == 'morning':
            return "早晨时段，可能需要处理工作相关任务"
        elif context_data.get('time_of_day') == 'evening':
            return "晚间时段，可能需要休闲娱乐或总结任务"
        else:
            return "根据用户行为模式，建议执行常规任务"

    def _generate_suggestions(self, context_data: Dict, user_preferences: Dict, health_status: Dict) -> List[str]:
        """
        生成任务建议

        Args:
            context_data: 上下文数据
            user_preferences: 用户偏好
            health_status: 系统健康状态

        Returns:
            建议列表
        """
        suggestions = []

        # 基于健康状态的建议
        if health_status.get('cpu_usage', 0) > 80:
            suggestions.append("当前CPU使用率较高，建议执行轻量级任务")
        if health_status.get('memory_usage', 0) > 80:
            suggestions.append("当前内存使用率较高，建议清理内存或执行优化任务")

        # 基于用户偏好的建议
        if user_preferences.get('preferred_activities'):
            activities = user_preferences['preferred_activities']
            suggestions.extend([f"根据您的偏好，可执行 {act} 类型任务" for act in activities[:2]])

        # 基于时间的建议
        time_of_day = context_data.get('time_of_day')
        if time_of_day == 'morning':
            suggestions.append("上午时段，建议处理重要或紧急任务")
        elif time_of_day == 'afternoon':
            suggestions.append("下午时段，适合处理中等复杂度任务")
        elif time_of_day == 'evening':
            suggestions.append("晚上时段，适合轻松娱乐或总结回顾")

        return suggestions[:3]  # 返回最多3个建议

    def plan_active_task(self, context: str = "") -> Dict[str, Any]:
        """
        主动规划任务

        Args:
            context: 当前上下文

        Returns:
            主动规划结果
        """
        # 预测用户意图
        intent_prediction = self.predict_user_intent(context)

        # 基于预测结果生成主动任务规划
        active_plan = {
            "timestamp": datetime.now().isoformat(),
            "context": context,
            "intent_prediction": intent_prediction,
            "suggested_tasks": self._generate_active_tasks(intent_prediction),
            "priority": self._calculate_priority(intent_prediction)
        }

        return active_plan

    def _generate_active_tasks(self, intent_prediction: Dict) -> List[Dict]:
        """
        根据意图预测生成主动任务

        Args:
            intent_prediction: 意图预测结果

        Returns:
            任务列表
        """
        tasks = []
        suggestions = intent_prediction.get('suggestions', [])

        # 基于建议生成任务
        for i, suggestion in enumerate(suggestions):
            tasks.append({
                "id": f"auto_task_{i}",
                "description": suggestion,
                "priority": "medium",
                "estimated_time": "5-10分钟",
                "category": "suggestion"
            })

        # 添加一些基础任务建议
        if len(tasks) == 0:
            tasks.append({
                "id": "auto_task_0",
                "description": "执行常规任务",
                "priority": "low",
                "estimated_time": "1-5分钟",
                "category": "general"
            })

        return tasks

    def _calculate_priority(self, intent_prediction: Dict) -> str:
        """
        计算任务优先级

        Args:
            intent_prediction: 意图预测结果

        Returns:
            优先级字符串
        """
        # 简单的优先级判断逻辑
        health_status = intent_prediction.get('health_status', {})
        cpu_usage = health_status.get('cpu_usage', 0)
        memory_usage = health_status.get('memory_usage', 0)

        if cpu_usage > 80 or memory_usage > 80:
            return "high"
        elif cpu_usage > 60 or memory_usage > 60:
            return "medium"
        else:
            return "low"

    def get_statistics(self) -> Dict[str, Any]:
        """
        获取任务统计信息

        Returns:
            统计信息
        """
        total_tasks = len(self.tasks)
        completed_tasks = sum(1 for t in self.tasks.values() if t.get('status') == 'completed')
        failed_tasks = sum(1 for t in self.tasks.values() if t.get('status') == 'failed')

        # 按意图分类统计
        intent_counts = defaultdict(int)
        for task in self.tasks.values():
            intent = task.get('info', {}).get('intent', 'unknown')
            intent_counts[intent] += 1

        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "failed_tasks": failed_tasks,
            "completion_rate": completed_tasks / total_tasks if total_tasks > 0 else 0,
            "intent_distribution": dict(intent_counts)
        }

def main():
    """主函数 - 用于测试"""
    # 创建任务记忆实例
    task_memory = TaskMemory()

    # 测试记录任务
    task_memory.record_task("test_task_001", {
        "intent": "查看邮件",
        "duration": "30秒",
        "success": True
    })

    # 测试获取历史
    history = task_memory.get_task_history(5)
    print("任务历史:", history)

    # 测试意图预测
    prediction = task_memory.predict_user_intent("办公时间")
    print("意图预测:", prediction)

    # 测试主动规划
    plan = task_memory.plan_active_task("上午工作时间")
    print("主动规划:", plan)

    # 测试统计
    stats = task_memory.get_statistics()
    print("统计信息:", stats)

if __name__ == "__main__":
    main()