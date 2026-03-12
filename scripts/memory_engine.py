#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
智能记忆系统
让星期五能够跨会话持久化存储和检索用户偏好、重要信息、历史交互，
实现真正的个性化记忆助手。

功能：
- 用户偏好记忆：记住用户的长期偏好设置
- 重要信息存储：存储用户重要的个人信息和事项
- 交互历史记录：记录用户交互的上下文和历史
- 记忆检索与应用：支持基于关键词的检索和智能应用

用法:
  python memory_engine.py store "<类型>" "<内容>" [--meta "<元数据>"]
  python memory_engine.py retrieve "<关键词>"
  python memory_engine.py search "<关键词>"
  python memory_engine.py list [--type "<类型>"]
  python memory_engine.py delete "<ID>"
  python memory_engine.py stats
"""

import argparse
import json
import os
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from collections import defaultdict

# 路径配置
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
STATE_DIR = os.path.join(PROJECT_ROOT, "runtime", "state")
MEMORY_FILE = os.path.join(STATE_DIR, "memory_store.json")


def ensure_dir():
    """确保目录存在"""
    os.makedirs(STATE_DIR, exist_ok=True)


def load_memory():
    """加载记忆存储"""
    ensure_dir()
    if not os.path.exists(MEMORY_FILE):
        return {"memories": [], "last_updated": None}
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"memories": [], "last_updated": None}


def save_memory(data):
    """保存记忆存储"""
    ensure_dir()
    data["last_updated"] = datetime.now(timezone.utc).isoformat()
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


class MemoryEntry:
    """记忆条目"""

    def __init__(self, id: str, content: str, memory_type: str, meta: Dict[str, Any] = None):
        self.id = id
        self.content = content
        self.memory_type = memory_type
        self.meta = meta or {}
        self.timestamp = datetime.now(timezone.utc).isoformat()

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "content": self.content,
            "type": self.memory_type,
            "meta": self.meta,
            "timestamp": self.timestamp
        }

    @classmethod
    def from_dict(cls, data):
        """从字典创建记忆条目"""
        return cls(
            id=data["id"],
            content=data["content"],
            memory_type=data["type"],
            meta=data.get("meta", {})
        )


def store_memory(memory_type: str, content: str, meta: Dict[str, Any] = None) -> Dict[str, Any]:
    """存储新的记忆"""
    data = load_memory()

    # 生成唯一ID
    import uuid
    entry_id = str(uuid.uuid4())

    # 创建记忆条目
    entry = MemoryEntry(entry_id, content, memory_type, meta)

    # 添加到存储中
    data["memories"].append(entry.to_dict())

    # 保持最近1000条记忆
    data["memories"] = data["memories"][-1000:]

    save_memory(data)

    return entry.to_dict()


def retrieve_memory(keyword: str) -> List[Dict[str, Any]]:
    """根据关键词检索记忆"""
    data = load_memory()
    results = []

    # 搜索所有记忆条目
    for entry in data["memories"]:
        if keyword.lower() in entry["content"].lower() or \
           (entry.get("meta") and keyword.lower() in str(entry["meta"]).lower()):
            results.append(entry)

    # 按时间倒序排列
    results.sort(key=lambda x: x["timestamp"], reverse=True)
    return results


def search_memory(keyword: str, memory_type: str = None) -> List[Dict[str, Any]]:
    """高级搜索记忆"""
    data = load_memory()
    results = []

    for entry in data["memories"]:
        # 检查类型过滤
        if memory_type and entry["type"] != memory_type:
            continue

        # 检查关键词
        if keyword.lower() in entry["content"].lower() or \
           (entry.get("meta") and keyword.lower() in str(entry["meta"]).lower()):
            results.append(entry)

    # 按时间倒序排列
    results.sort(key=lambda x: x["timestamp"], reverse=True)
    return results


def list_memories(memory_type: str = None, limit: int = 100) -> List[Dict[str, Any]]:
    """列出记忆条目"""
    data = load_memory()

    # 如果指定了类型，过滤类型
    if memory_type:
        filtered = [entry for entry in data["memories"] if entry["type"] == memory_type]
    else:
        filtered = data["memories"]

    # 按时间倒序排列并限制数量
    filtered.sort(key=lambda x: x["timestamp"], reverse=True)
    return filtered[:limit]


def delete_memory(memory_id: str) -> Dict[str, Any]:
    """删除指定ID的记忆"""
    data = load_memory()

    # 查找并删除
    original_count = len(data["memories"])
    data["memories"] = [entry for entry in data["memories"] if entry["id"] != memory_id]

    if len(data["memories"]) < original_count:
        save_memory(data)
        return {"status": "deleted", "message": f"记忆已删除 (ID: {memory_id})"}
    else:
        return {"status": "not_found", "message": f"未找到ID为 {memory_id} 的记忆"}


def get_stats() -> Dict[str, Any]:
    """获取记忆统计信息"""
    data = load_memory()

    # 按类型统计
    type_count = defaultdict(int)
    for entry in data["memories"]:
        type_count[entry["type"]] += 1

    return {
        "total_memories": len(data["memories"]),
        "memory_types": dict(type_count),
        "last_updated": data["last_updated"]
    }


def main():
    parser = argparse.ArgumentParser(description="智能记忆系统")
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # store 命令
    store_parser = subparsers.add_parser("store", help="存储新的记忆")
    store_parser.add_argument("type", help="记忆类型")
    store_parser.add_argument("content", help="记忆内容")
    store_parser.add_argument("--meta", help="元数据 (JSON格式)")

    # retrieve 命令
    retrieve_parser = subparsers.add_parser("retrieve", help="根据关键词检索记忆")
    retrieve_parser.add_argument("keyword", help="检索关键词")

    # search 命令
    search_parser = subparsers.add_parser("search", help="搜索记忆")
    search_parser.add_argument("keyword", help="搜索关键词")
    search_parser.add_argument("--type", help="记忆类型过滤")

    # list 命令
    list_parser = subparsers.add_parser("list", help="列出记忆")
    list_parser.add_argument("--type", help="记忆类型过滤")
    list_parser.add_argument("--limit", type=int, default=100, help="限制数量")

    # delete 命令
    delete_parser = subparsers.add_parser("delete", help="删除记忆")
    delete_parser.add_argument("id", help="记忆ID")

    # stats 命令
    subparsers.add_parser("stats", help="获取统计信息")

    args = parser.parse_args()

    if args.command == "store":
        meta = json.loads(args.meta) if args.meta else None
        result = store_memory(args.type, args.content, meta)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "retrieve":
        result = retrieve_memory(args.keyword)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "search":
        result = search_memory(args.keyword, args.type)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "list":
        result = list_memories(args.type, args.limit)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "delete":
        result = delete_memory(args.id)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "stats":
        result = get_stats()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()