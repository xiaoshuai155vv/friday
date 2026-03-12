#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能主动通知引擎
让系统能够主动向用户推送有价值的信息和建议，实现从被动响应到主动服务的进化
"""

import json
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import threading
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 通知存储路径
NOTIFICATION_DB_PATH = os.path.join(os.path.dirname(__file__), "..", "runtime", "state", "notifications.json")


class ProactiveNotificationEngine:
    """主动通知引擎类"""

    def __init__(self):
        """初始化主动通知引擎"""
        self.notifications = self._load_notifications()
        self.running = False

    def _load_notifications(self) -> List[Dict]:
        """加载通知数据"""
        try:
            if os.path.exists(NOTIFICATION_DB_PATH):
                with open(NOTIFICATION_DB_PATH, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return []
        except Exception as e:
            logger.error(f"加载通知数据失败: {e}")
            return []

    def _save_notifications(self):
        """保存通知数据"""
        try:
            os.makedirs(os.path.dirname(NOTIFICATION_DB_PATH), exist_ok=True)
            with open(NOTIFICATION_DB_PATH, 'w', encoding='utf-8') as f:
                json.dump(self.notifications, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存通知数据失败: {e}")

    def add_notification(self, notification_type: str, content: str, trigger_time: Optional[str] = None,
                       priority: int = 1, metadata: Optional[Dict] = None) -> str:
        """
        添加一个通知

        Args:
            notification_type: 通知类型 (reminder, recommendation, habit)
            content: 通知内容
            trigger_time: 触发时间 (ISO格式) 如果为None则立即触发
            priority: 优先级 (1-5, 5最高)
            metadata: 元数据

        Returns:
            通知ID
        """
        notification_id = f"notif_{int(time.time())}"

        notification = {
            "id": notification_id,
            "type": notification_type,
            "content": content,
            "trigger_time": trigger_time,
            "priority": priority,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {},
            "read": False
        }

        self.notifications.append(notification)
        self._save_notifications()
        logger.info(f"添加通知: {notification_id} - {content}")
        return notification_id

    def get_unread_notifications(self) -> List[Dict]:
        """获取未读通知"""
        return [n for n in self.notifications if not n.get('read', False)]

    def mark_as_read(self, notification_id: str):
        """标记通知为已读"""
        for notification in self.notifications:
            if notification.get('id') == notification_id:
                notification['read'] = True
                self._save_notifications()
                logger.info(f"标记通知为已读: {notification_id}")
                break

    def check_and_send_notifications(self):
        """检查并发送到期的通知"""
        now = datetime.now()
        unread_notifications = self.get_unread_notifications()

        for notification in unread_notifications:
            trigger_time_str = notification.get('trigger_time')
            if trigger_time_str:
                try:
                    trigger_time = datetime.fromisoformat(trigger_time_str.replace('Z', '+00:00'))
                    if now >= trigger_time:
                        # 发送通知（这里只是模拟）
                        logger.info(f"发送通知: {notification['content']}")
                        self.mark_as_read(notification['id'])
                except Exception as e:
                    logger.error(f"处理通知时间失败 {notification['id']}: {e}")

    def schedule_reminder(self, content: str, minutes_delay: int = 5, priority: int = 3) -> str:
        """
        安排一个提醒

        Args:
            content: 提醒内容
            minutes_delay: 延迟分钟数
            priority: 优先级

        Returns:
            通知ID
        """
        trigger_time = datetime.now() + timedelta(minutes=minutes_delay)
        trigger_time_str = trigger_time.isoformat()

        return self.add_notification(
            notification_type="reminder",
            content=content,
            trigger_time=trigger_time_str,
            priority=priority,
            metadata={"delay_minutes": minutes_delay}
        )

    def get_recommendations(self, user_context: Dict = None) -> List[str]:
        """
        根据用户上下文生成推荐

        Args:
            user_context: 用户上下文信息

        Returns:
            推荐列表
        """
        recommendations = []

        # 基于时间的推荐
        current_hour = datetime.now().hour
        if 9 <= current_hour <= 12:
            recommendations.append("上午好！今天是工作日，记得安排好一天的工作计划哦")
        elif 12 <= current_hour <= 18:
            recommendations.append("下午好！工作间隙记得适当休息一下")
        elif 18 <= current_hour <= 22:
            recommendations.append("晚上好！一天辛苦了，可以考虑放松一下")

        # 基于用户习惯的推荐（这里简化处理）
        if user_context and user_context.get('last_activity'):
            last_activity = user_context['last_activity']
            if last_activity == 'work':
                recommendations.append("工作一段时间了，建议起身活动一下")
            elif last_activity == 'break':
                recommendations.append("休息时间到了，可以考虑继续工作或放松")

        return recommendations

    def send_recommendation(self, content: str, priority: int = 2) -> str:
        """
        发送推荐通知

        Args:
            content: 推荐内容
            priority: 优先级

        Returns:
            通知ID
        """
        return self.add_notification(
            notification_type="recommendation",
            content=content,
            priority=priority
        )

    def send_habit_reminder(self, habit_name: str, frequency: str = "daily") -> str:
        """
        发送习惯提醒

        Args:
            habit_name: 习惯名称
            frequency: 频率 (daily, weekly, monthly)

        Returns:
            通知ID
        """
        content = f"提醒：该进行'{habit_name}'习惯训练了"
        if frequency == "weekly":
            content += " (每周提醒)"
        elif frequency == "monthly":
            content += " (每月提醒)"

        return self.add_notification(
            notification_type="habit",
            content=content,
            priority=2
        )

    def get_notification_stats(self) -> Dict:
        """获取通知统计信息"""
        total = len(self.notifications)
        unread = len(self.get_unread_notifications())
        by_type = {}
        for n in self.notifications:
            n_type = n.get('type', 'unknown')
            by_type[n_type] = by_type.get(n_type, 0) + 1

        return {
            "total": total,
            "unread": unread,
            "by_type": by_type
        }

    def clear_old_notifications(self, days_old: int = 30):
        """清理旧的通知"""
        cutoff_date = datetime.now() - timedelta(days=days_old)
        old_notifications = []
        new_notifications = []

        for notification in self.notifications:
            timestamp_str = notification.get('timestamp', '')
            try:
                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                if timestamp < cutoff_date:
                    old_notifications.append(notification)
                else:
                    new_notifications.append(notification)
            except Exception:
                new_notifications.append(notification)

        self.notifications = new_notifications
        self._save_notifications()
        logger.info(f"清理了 {len(old_notifications)} 条旧通知")


def main():
    """主函数 - 用于测试"""
    engine = ProactiveNotificationEngine()

    # 测试添加通知
    print("=== 测试主动通知引擎 ===")

    # 添加提醒
    reminder_id = engine.schedule_reminder("开会时间快到了", 2)
    print(f"添加提醒: {reminder_id}")

    # 添加推荐
    rec_id = engine.send_recommendation("今天天气不错，适合出去走走")
    print(f"添加推荐: {rec_id}")

    # 添加习惯提醒
    habit_id = engine.send_habit_reminder("每天喝水", "daily")
    print(f"添加习惯提醒: {habit_id}")

    # 显示通知统计
    stats = engine.get_notification_stats()
    print(f"通知统计: {stats}")

    # 显示未读通知
    unread = engine.get_unread_notifications()
    print(f"未读通知: {len(unread)} 条")

    # 检查通知
    engine.check_and_send_notifications()

    print("测试完成")


if __name__ == "__main__":
    main()