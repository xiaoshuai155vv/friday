#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
剪贴板历史管理模块 - 记录、查看、恢复和清除剪贴板历史
支持文本类型的剪贴板内容历史管理
"""
import sys
import os
import json
import time
from datetime import datetime

if sys.platform != "win32":
    sys.exit(1)

# 导入剪贴板工具的函数
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from clipboard_tool import get_clipboard_text, set_clipboard_text
except ImportError:
    # 内联复制必要函数以确保独立运行
    import ctypes
    from ctypes import wintypes

    u = ctypes.windll.user32
    k = ctypes.windll.kernel32
    CF_UNICODETEXT = 13
    GMEM_MOVEABLE = 0x0002

    def get_clipboard_text():
        if not u.OpenClipboard(None):
            return None
        try:
            h = u.GetClipboardData(CF_UNICODETEXT)
            if not h:
                return None
            p = k.GlobalLock(h)
            if not p:
                return None
            try:
                n = 0
                while (ctypes.c_ushort * 1).from_address(p + n * 2)[0]:
                    n += 1
                if n == 0:
                    return ""
                buf = (ctypes.c_ushort * (n + 1)).from_address(p)
                return "".join(chr(buf[i]) for i in range(n))
            finally:
                k.GlobalUnlock(h)
        finally:
            u.CloseClipboard()

    def set_clipboard_text(text):
        if not isinstance(text, str):
            text = str(text)
        if not u.OpenClipboard(None):
            return False
        u.EmptyClipboard()
        try:
            nul = "\u0000"
            data = (text + nul).encode("utf-16-le")
            n = len(data)
            h = k.GlobalAlloc(GMEM_MOVEABLE, n)
            if not h:
                return False
            p = k.GlobalLock(h)
            if not p:
                k.GlobalFree(h)
                return False
            ctypes.memmove(p, data, n)
            k.GlobalUnlock(h)
            u.SetClipboardData(CF_UNICODETEXT, h)
            return True
        finally:
            u.CloseClipboard()

# 历史记录存储文件
HISTORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "runtime", "state", "clipboard_history.json")
MAX_HISTORY = 50  # 最多保存50条历史记录


def load_history():
    """加载历史记录"""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []


def save_history(history):
    """保存历史记录"""
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def add_to_history(text):
    """添加剪贴板内容到历史记录"""
    if not text or not text.strip():
        return False

    history = load_history()

    # 检查是否已存在相同内容（避免重复）
    for item in history:
        if item.get("content") == text:
            # 将已存在的项移到最前面
            history.remove(item)
            break

    # 添加新记录
    new_item = {
        "content": text,
        "timestamp": datetime.now().isoformat(),
        "preview": text[:50] + "..." if len(text) > 50 else text
    }
    history.insert(0, new_item)

    # 限制历史记录数量
    if len(history) > MAX_HISTORY:
        history = history[:MAX_HISTORY]

    save_history(history)
    return True


def list_history(limit=10):
    """列出历史记录"""
    history = load_history()
    if not history:
        print("剪贴板历史为空")
        return []

    print(f"剪贴板历史记录 (共 {len(history)} 条):")
    print("-" * 60)

    for i, item in enumerate(history[:limit]):
        timestamp = item.get("timestamp", "")
        preview = item.get("preview", "")
        print(f"{i+1}. [{timestamp[:19]}] {preview}")

    return history[:limit]


def restore_history(index):
    """恢复指定历史项到剪贴板"""
    history = load_history()

    if index < 0 or index >= len(history):
        print(f"错误：无效的索引 {index+1}，历史记录共有 {len(history)} 条")
        return False

    item = history[index]
    content = item.get("content", "")

    if set_clipboard_text(content):
        print(f"已恢复第 {index+1} 条到剪贴板")
        return True
    else:
        print("恢复剪贴板失败")
        return False


def clear_history():
    """清除所有历史记录"""
    save_history([])
    print("剪贴板历史已清除")
    return True


def get_current_clipboard():
    """获取当前剪贴板内容并添加到历史"""
    text = get_clipboard_text()
    if text and text.strip():
        if add_to_history(text):
            print(f"已将当前剪贴板内容添加到历史记录")
            return True
    return False


def main():
    if len(sys.argv) < 2:
        print("""clipboard_history - 剪贴板历史管理工具

用法:
  python clipboard_history.py add          - 添加当前剪贴板内容到历史
  python clipboard_history.py list [n]    - 查看历史记录 (默认显示10条)
  python clipboard_history.py restore n   - 恢复第n条历史到剪贴板
  python clipboard_history.py clear       - 清除所有历史记录
  python clipboard_history.py get          - 获取当前剪贴板内容
        """)
        sys.exit(1)

    cmd = sys.argv[1].lower()

    if cmd == "add":
        if get_current_clipboard():
            sys.exit(0)
        else:
            print("当前剪贴板为空或添加失败")
            sys.exit(1)

    elif cmd == "list":
        limit = 10
        if len(sys.argv) >= 3:
            try:
                limit = int(sys.argv[2])
            except ValueError:
                print("错误：limit 必须是数字")
                sys.exit(1)
        list_history(limit)

    elif cmd == "restore":
        if len(sys.argv) < 3:
            print("用法: clipboard_history.py restore <索引>")
            sys.exit(1)
        try:
            index = int(sys.argv[2]) - 1  # 转换为0-based
        except ValueError:
            print("错误：索引必须是数字")
            sys.exit(1)
        if not restore_history(index):
            sys.exit(1)

    elif cmd == "clear":
        clear_history()

    elif cmd == "get":
        text = get_clipboard_text()
        if text:
            print(text)
        else:
            print("剪贴板为空")

    else:
        print(f"未知命令: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()