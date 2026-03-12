#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
跨模块上下文共享与状态同步机制
实现模块间的状态共享和上下文传递，让各个智能模块可以协同工作
"""

import json
import time
import threading
from typing import Dict, Any, Optional
from pathlib import Path

# 上下文存储路径
CONTEXT_STORAGE_PATH = Path("runtime/state/context_bus_storage.json")

class ContextBus:
    """跨模块上下文总线"""

    def __init__(self):
        self._context = {}
        self._lock = threading.Lock()
        self._load_context()

    def _load_context(self):
        """从文件加载上下文"""
        try:
            if CONTEXT_STORAGE_PATH.exists():
                with open(CONTEXT_STORAGE_PATH, 'r', encoding='utf-8') as f:
                    self._context = json.load(f)
        except Exception as e:
            print(f"加载上下文失败: {e}")
            self._context = {}

    def _save_context(self):
        """保存上下文到文件"""
        try:
            with open(CONTEXT_STORAGE_PATH, 'w', encoding='utf-8') as f:
                json.dump(self._context, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存上下文失败: {e}")

    def set_context(self, key: str, value: Any, ttl: Optional[int] = None):
        """
        设置上下文值

        Args:
            key: 上下文键
            value: 上下文值
            ttl: 过期时间（秒），None表示永不过期
        """
        with self._lock:
            self._context[key] = {
                'value': value,
                'timestamp': time.time(),
                'ttl': ttl
            }
            self._save_context()

    def get_context(self, key: str, default: Any = None) -> Any:
        """
        获取上下文值

        Args:
            key: 上下文键
            default: 默认值

        Returns:
            上下文值或默认值
        """
        with self._lock:
            if key not in self._context:
                return default

            context_data = self._context[key]

            # 检查是否过期
            if context_data['ttl'] is not None:
                if time.time() - context_data['timestamp'] > context_data['ttl']:
                    del self._context[key]
                    self._save_context()
                    return default

            return context_data['value']

    def delete_context(self, key: str):
        """删除上下文"""
        with self._lock:
            if key in self._context:
                del self._context[key]
                self._save_context()

    def clear_expired(self):
        """清理过期上下文"""
        with self._lock:
            current_time = time.time()
            expired_keys = []

            for key, context_data in self._context.items():
                if context_data['ttl'] is not None:
                    if current_time - context_data['timestamp'] > context_data['ttl']:
                        expired_keys.append(key)

            for key in expired_keys:
                del self._context[key]

            self._save_context()

    def list_context(self) -> Dict[str, Any]:
        """列出所有上下文（不包含过期的）"""
        with self._lock:
            self.clear_expired()
            result = {}
            for key, context_data in self._context.items():
                result[key] = context_data['value']
            return result

    def get_context_info(self) -> Dict[str, Any]:
        """获取上下文信息"""
        with self._lock:
            self.clear_expired()
            result = {}
            for key, context_data in self._context.items():
                result[key] = {
                    'value': context_data['value'],
                    'timestamp': context_data['timestamp'],
                    'ttl': context_data['ttl'],
                    'expired': False if context_data['ttl'] is None else \
                        (time.time() - context_data['timestamp'] > context_data['ttl'])
                }
            return result

# 全局上下文总线实例
context_bus = ContextBus()

def set_context(key: str, value: Any, ttl: Optional[int] = None):
    """设置上下文值的便捷函数"""
    context_bus.set_context(key, value, ttl)

def get_context(key: str, default: Any = None) -> Any:
    """获取上下文值的便捷函数"""
    return context_bus.get_context(key, default)

def delete_context(key: str):
    """删除上下文的便捷函数"""
    context_bus.delete_context(key)

def list_context() -> Dict[str, Any]:
    """列出所有上下文的便捷函数"""
    return context_bus.list_context()

def get_context_info() -> Dict[str, Any]:
    """获取上下文信息的便捷函数"""
    return context_bus.get_context_info()

if __name__ == "__main__":
    # 测试代码
    print("测试跨模块上下文总线...")

    # 设置上下文
    set_context("user_name", "张三")
    set_context("last_action", "打开浏览器", ttl=60)  # 1分钟后过期

    # 获取上下文
    name = get_context("user_name")
    last_action = get_context("last_action")
    print(f"用户名: {name}")
    print(f"上次动作: {last_action}")

    # 列出所有上下文
    print("所有上下文:", list_context())

    # 获取上下文信息
    print("上下文详细信息:", get_context_info())

    print("测试完成!")