#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
跨模块状态共享总线 (Module Bus)

功能：
- 实现模块间的状态共享和数据传递
- 提供事件发布/订阅机制
- 支持模块间直接通信
- 记录跨模块通信历史

使用方式：
    from module_bus import ModuleBus

    bus = ModuleBus()
    bus.publish("user_action", {"action": "open_file", "target": "document.pdf"})
    bus.subscribe("user_action", callback_function)
    state = bus.get_shared_state("current_task")
"""

import json
import os
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Callable, Optional
from collections import defaultdict

# 项目路径
SCRIPT_DIR = Path(__file__).parent
RUNTIME_DIR = SCRIPT_DIR.parent / "runtime"
STATE_DIR = RUNTIME_DIR / "state"

# 确保目录存在
STATE_DIR.mkdir(parents=True, exist_ok=True)


class ModuleBus:
    """跨模块状态共享总线"""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        """单例模式，确保全局唯一实例"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._initialized = True
        self.shared_state = {}  # 共享状态存储
        self.subscribers = defaultdict(list)  # 事件订阅者
        self.event_history = []  # 事件历史
        self.state_file = STATE_DIR / "module_bus_state.json"
        self.history_file = STATE_DIR / "module_bus_history.json"

        # 加载已保存的状态
        self._load_state()

    def _load_state(self):
        """加载已保存的状态"""
        try:
            if self.state_file.exists():
                with open(self.state_file, "r", encoding="utf-8") as f:
                    self.shared_state = json.load(f)
        except Exception as e:
            print(f"[ModuleBus] 加载状态失败: {e}")
            self.shared_state = {}

    def _save_state(self):
        """保存状态到文件"""
        try:
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump(self.shared_state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[ModuleBus] 保存状态失败: {e}")

    def _load_history(self):
        """加载事件历史"""
        try:
            if self.history_file.exists():
                with open(self.history_file, "r", encoding="utf-8") as f:
                    self.event_history = json.load(f)
        except Exception as e:
            print(f"[ModuleBus] 加载历史失败: {e}")
            self.event_history = []

    def _save_history(self):
        """保存事件历史"""
        try:
            # 保留最近100条
            history = self.event_history[-100:]
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[ModuleBus] 保存历史失败: {e}")

    # ========== 状态管理 ==========

    def set_shared_state(self, key: str, value: Any, namespace: str = "global") -> None:
        """
        设置共享状态

        Args:
            key: 状态键
            value: 状态值
            namespace: 命名空间（默认 global）
        """
        full_key = f"{namespace}:{key}"
        self.shared_state[full_key] = {
            "value": value,
            "timestamp": datetime.now().isoformat(),
            "namespace": namespace
        }
        self._save_state()

    def get_shared_state(self, key: str, namespace: str = "global", default: Any = None) -> Any:
        """
        获取共享状态

        Args:
            key: 状态键
            namespace: 命名空间（默认 global）
            default: 默认值

        Returns:
            状态值或默认值
        """
        full_key = f"{namespace}:{key}"
        state = self.shared_state.get(full_key, {})
        return state.get("value", default)

    def get_all_states(self, namespace: str = None) -> Dict[str, Any]:
        """获取指定命名空间的所有状态"""
        if namespace:
            return {
                k.replace(f"{namespace}:", ""): v["value"]
                for k, v in self.shared_state.items()
                if k.startswith(f"{namespace}:")
            }
        return {k: v["value"] for k, v in self.shared_state.items()}

    def delete_shared_state(self, key: str, namespace: str = "global") -> bool:
        """删除共享状态"""
        full_key = f"{namespace}:{key}"
        if full_key in self.shared_state:
            del self.shared_state[full_key]
            self._save_state()
            return True
        return False

    # ========== 事件系统 ==========

    def publish(self, event_type: str, data: Any = None, source: str = "unknown") -> None:
        """
        发布事件

        Args:
            event_type: 事件类型
            data: 事件数据
            source: 事件来源
        """
        event = {
            "type": event_type,
            "data": data,
            "source": source,
            "timestamp": datetime.now().isoformat()
        }

        # 记录到历史
        self.event_history.append(event)
        self._save_history()

        # 通知订阅者
        if event_type in self.subscribers:
            for callback in self.subscribers[event_type]:
                try:
                    callback(event)
                except Exception as e:
                    print(f"[ModuleBus] 事件回调失败: {e}")

        # 也通知通配符订阅者
        if "*" in self.subscribers:
            for callback in self.subscribers["*"]:
                try:
                    callback(event)
                except Exception as e:
                    print(f"[ModuleBus] 通配符回调失败: {e}")

    def subscribe(self, event_type: str, callback: Callable[[Dict], None]) -> None:
        """
        订阅事件

        Args:
            event_type: 事件类型（使用 * 订阅所有事件）
            callback: 回调函数
        """
        self.subscribers[event_type].append(callback)

    def unsubscribe(self, event_type: str, callback: Callable[[Dict], None]) -> bool:
        """取消订阅"""
        if event_type in self.subscribers:
            try:
                self.subscribers[event_type].remove(callback)
                return True
            except ValueError:
                pass
        return False

    # ========== 模块间通信 ==========

    def send_to_module(self, target_module: str, message: Dict[str, Any]) -> None:
        """向指定模块发送消息"""
        self.publish(f"module:{target_module}", message, source="module_bus")

    def broadcast(self, message: Dict[str, Any], exclude: List[str] = None) -> None:
        """广播消息给所有模块"""
        exclude = exclude or []
        event = {
            "type": "broadcast",
            "message": message,
            "timestamp": datetime.now().isoformat()
        }

        for module_name in self.subscribers:
            if module_name.startswith("module:") and module_name.split(":")[1] not in exclude:
                self.publish(module_name, message, source="broadcast")

    # ========== 状态查询 ==========

    def get_event_history(self, event_type: str = None, limit: int = 20) -> List[Dict]:
        """获取事件历史"""
        if event_type:
            events = [e for e in self.event_history if e.get("type") == event_type]
        else:
            events = self.event_history

        return events[-limit:]

    def get_status(self) -> Dict[str, Any]:
        """获取总线状态"""
        return {
            "namespaces": list(set(v.get("namespace") for v in self.shared_state.values())),
            "state_count": len(self.shared_state),
            "subscriber_count": sum(len(v) for v in self.subscribers.values()),
            "event_count": len(self.event_history),
            "subscribed_events": list(self.subscribers.keys()),
            "timestamp": datetime.now().isoformat()
        }

    # ========== 集成到 do.py 的便捷方法 ==========

    def quick_set(self, key_value: str) -> bool:
        """
        快速设置状态（格式：key=value 或 namespace:key=value）

        Args:
            key_value: 键值对字符串

        Returns:
            是否成功
        """
        try:
            if ":" in key_value:
                parts = key_value.split(":", 1)
                namespace = parts[0]
                kv = parts[1].split("=", 1)
                if len(kv) == 2:
                    self.set_shared_state(kv[0], kv[1], namespace)
                    return True
            else:
                kv = key_value.split("=", 1)
                if len(kv) == 2:
                    self.set_shared_state(kv[0], kv[1])
                    return True
        except Exception as e:
            print(f"[ModuleBus] 快速设置失败: {e}")
        return False

    def quick_get(self, key: str, namespace: str = "global") -> Any:
        """快速获取状态"""
        return self.get_shared_state(key, namespace)


# ========== 命令行接口 ==========

def main():
    """命令行入口"""
    bus = ModuleBus()

    if len(sys.argv) < 2:
        print(json.dumps(bus.get_status(), ensure_ascii=False, indent=2))
        return

    command = sys.argv[1]

    if command == "status":
        print(json.dumps(bus.get_status(), ensure_ascii=False, indent=2))

    elif command == "set" and len(sys.argv) > 2:
        key = sys.argv[2]
        value = sys.argv[3] if len(sys.argv) > 3 else ""
        bus.set_shared_state(key, value)
        print(f"已设置 {key} = {value}")

    elif command == "get" and len(sys.argv) > 2:
        key = sys.argv[2]
        namespace = sys.argv[3] if len(sys.argv) > 3 else "global"
        value = bus.get_shared_state(key, namespace)
        print(f"{key} = {value}")

    elif command == "list":
        print(json.dumps(bus.get_all_states(), ensure_ascii=False, indent=2))

    elif command == "history" and len(sys.argv) > 2:
        event_type = sys.argv[2]
        limit = int(sys.argv[3]) if len(sys.argv) > 3 else 20
        print(json.dumps(bus.get_event_history(event_type, limit), ensure_ascii=False, indent=2))

    elif command in ["help", "-h", "--help"]:
        print("""
跨模块状态共享总线

用法:
  python module_bus.py [command] [args]

命令:
  status              显示总线状态
  set <key> [value]   设置共享状态
  get <key> [ns]      获取共享状态（默认命名空间 global）
  list                列出所有状态
  history <type> [n]  获取事件历史
  help                显示帮助
        """)

    else:
        # 尝试作为快速设置处理
        if "=" in command:
            bus.quick_set(command)
            print(f"已设置: {command}")
        else:
            print(f"未知命令: {command}")


if __name__ == "__main__":
    import sys
    main()