#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM-OS 剪贴板管理器模块 - 提供智能剪贴板管理能力

本模块提供类似剪贴板增强工具的功能：
- 剪贴板历史记录（自动保存复制内容）
- 剪贴板历史搜索
- 常用内容收藏
- 一键粘贴历史内容

版本: 1.0.0
依赖: clipboard_tool, json, os
"""

import os
import sys
import json
import time
import shutil
from datetime import datetime
from pathlib import Path

# 脚本目录和状态目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "runtime", "state")
CLIPBOARD_HISTORY_FILE = os.path.join(STATE_DIR, "clipboard_history.json")
CLIPBOARD_FAVORITES_FILE = os.path.join(STATE_DIR, "clipboard_favorites.json")

# 默认配置
DEFAULT_MAX_HISTORY = 100  # 默认保存100条历史
MAX_CONTENT_LENGTH = 10000  # 单条内容最大长度


def load_history():
    """加载剪贴板历史"""
    if os.path.exists(CLIPBOARD_HISTORY_FILE):
        try:
            with open(CLIPBOARD_HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []


def save_history(history):
    """保存剪贴板历史"""
    try:
        os.makedirs(os.path.dirname(CLIPBOARD_HISTORY_FILE), exist_ok=True)
        with open(CLIPBOARD_HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
        return True
    except IOError:
        return False


def load_favorites():
    """加载收藏内容"""
    if os.path.exists(CLIPBOARD_FAVORITES_FILE):
        try:
            with open(CLIPBOARD_FAVORITES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []


def save_favorites(favorites):
    """保存收藏内容"""
    try:
        os.makedirs(os.path.dirname(CLIPBOARD_FAVORITES_FILE), exist_ok=True)
        with open(CLIPBOARD_FAVORITES_FILE, 'w', encoding='utf-8') as f:
            json.dump(favorites, f, ensure_ascii=False, indent=2)
        return True
    except IOError:
        return False


def add_to_history(content, content_type="text"):
    """添加内容到历史记录"""
    if not content or not content.strip():
        return False

    # 限制内容长度
    if len(content) > MAX_CONTENT_LENGTH:
        content = content[:MAX_CONTENT_LENGTH] + "...[内容过长已截断]"

    history = load_history()

    # 检查是否与最近一条重复
    if history and history[0].get('content') == content:
        return False  # 重复内容不重复添加

    # 创建新条目
    entry = {
        'id': int(time.time() * 1000),
        'content': content,
        'type': content_type,
        'timestamp': datetime.now().isoformat(),
        'preview': content[:100] + ("..." if len(content) > 100 else "")
    }

    # 添加到开头
    history.insert(0, entry)

    # 限制历史长度
    if len(history) > DEFAULT_MAX_HISTORY:
        history = history[:DEFAULT_MAX_HISTORY]

    return save_history(history)


def get_history(limit=None, search=None):
    """获取剪贴板历史"""
    history = load_history()

    # 搜索过滤
    if search:
        search_lower = search.lower()
        history = [h for h in history if search_lower in h.get('content', '').lower()]

    # 数量限制
    if limit:
        history = history[:limit]

    return history


def clear_history():
    """清空剪贴板历史"""
    return save_history([])


def add_favorite(content, name=None, tags=None):
    """添加内容到收藏"""
    if not content or not content.strip():
        return False

    # 限制内容长度
    if len(content) > MAX_CONTENT_LENGTH:
        content = content[:MAX_CONTENT_LENGTH] + "...[内容过长已截断]"

    favorites = load_favorites()

    # 检查是否已收藏
    for fav in favorites:
        if fav.get('content') == content:
            return False  # 已收藏

    # 创建收藏条目
    entry = {
        'id': int(time.time() * 1000),
        'content': content,
        'name': name or f"收藏 {len(favorites) + 1}",
        'tags': tags or [],
        'created_at': datetime.now().isoformat()
    }

    favorites.append(entry)
    return save_favorites(favorites)


def remove_favorite(favorite_id):
    """移除收藏"""
    favorites = load_favorites()
    favorites = [f for f in favorites if f.get('id') != favorite_id]
    return save_favorites(favorites)


def get_favorites(search=None):
    """获取收藏列表"""
    favorites = load_favorites()

    # 搜索过滤
    if search:
        search_lower = search.lower()
        favorites = [f for f in favorites
                     if search_lower in f.get('content', '').lower()
                     or search_lower in f.get('name', '').lower()
                     or any(search_lower in tag.lower() for tag in f.get('tags', []))]

    return favorites


def format_history(history, show_preview=True):
    """格式化历史列表为可读格式"""
    if not history:
        return "暂无剪贴板历史"

    lines = ["=== 剪贴板历史 ==="]
    for i, entry in enumerate(history, 1):
        timestamp = entry.get('timestamp', '')[:19]
        content_type = entry.get('type', 'text')
        preview = entry.get('preview', entry.get('content', '')[:50])

        lines.append(f"{i}. [{content_type}] {timestamp}")
        if show_preview:
            lines.append(f"   {preview}")
        lines.append("")

    return '\n'.join(lines)


def format_favorites(favorites):
    """格式化收藏列表为可读格式"""
    if not favorites:
        return "暂无收藏内容"

    lines = ["=== 收藏内容 ==="]
    for i, fav in enumerate(favorites, 1):
        name = fav.get('name', '未命名')
        tags = fav.get('tags', [])
        created = fav.get('created_at', '')[:19]
        preview = fav.get('content', '')[:50] + ("..." if len(fav.get('content', '')) > 50 else "")

        tags_str = f" [{', '.join(tags)}]" if tags else ""
        lines.append(f"{i}. {name}{tags_str} - {created}")
        lines.append(f"   {preview}")
        lines.append("")

    return '\n'.join(lines)


def copy_to_clipboard(content):
    """复制内容到剪贴板（使用 clipboard_tool）"""
    clipboard_tool = os.path.join(SCRIPT_DIR, "clipboard_tool.py")

    # 尝试使用 clipboard_tool
    if os.path.exists(clipboard_tool):
        result = subprocess.run(
            [sys.executable, clipboard_tool, "set", content],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        return result.returncode == 0

    # 使用 PowerShell 后备
    try:
        subprocess.run(
            ["powershell", "-Command", f"Set-Clipboard -Value '{content}'"],
            capture_output=True,
            timeout=5
        )
        return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def main():
    import argparse
    import io

    # 设置标准输出编码
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

    parser = argparse.ArgumentParser(
        description="LLM-OS 剪贴板管理器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python llm_os_clipboard_manager.py --history                      # 查看历史记录
  python llm_os_clipboard_manager.py --history 10                  # 查看最近10条
  python llm_os_clipboard_manager.py --search "关键词"            # 搜索历史
  python llm_os_clipboard_manager.py --add-favorite "内容"        # 收藏内容
  python llm_os_clipboard_manager.py --favorites                   # 查看收藏
  python llm_os_clipboard_manager.py --copy 5                      # 复制第5条历史
  python llm_os_clipboard_manager.py --clear                       # 清空历史
        """
    )

    parser.add_argument("--history", "-hl", nargs='?', const=-1, type=int, metavar="[N]",
                       help="查看剪贴板历史（可选指定数量）")
    parser.add_argument("--search", "-s", type=str, metavar="关键词",
                       help="搜索剪贴板历史")
    parser.add_argument("--favorites", "-f", action="store_true",
                       help="查看收藏内容")
    parser.add_argument("--add-favorite", "-af", type=str, metavar="内容",
                       help="添加收藏")
    parser.add_argument("--remove-favorite", "-rf", type=int, metavar="ID",
                       help="移除收藏（指定ID）")
    parser.add_argument("--copy", "-c", type=int, metavar="N",
                       help="复制第N条历史到剪贴板")
    parser.add_argument("--clear", "-cl", action="store_true",
                       help="清空剪贴板历史")
    parser.add_argument("--json", "-j", action="store_true",
                       help="输出 JSON 格式")
    parser.add_argument("--version", "-v", action="store_true",
                       help="显示版本信息")

    args = parser.parse_args()

    # 显示版本
    if args.version:
        print("LLM-OS 剪贴板管理器 version 1.0.0")
        return

    # 如果没有参数，显示帮助
    if len(sys.argv) == 1:
        parser.print_help()
        return

    # 查看历史
    if args.history is not None:
        limit = args.history if args.history > 0 else None
        history = get_history(limit=limit, search=args.search)
        if args.json:
            print(json.dumps(history, ensure_ascii=False, indent=2))
        else:
            print(format_history(history))

    # 查看收藏
    if args.favorites:
        favorites = get_favorites(search=args.search)
        if args.json:
            print(json.dumps(favorites, ensure_ascii=False, indent=2))
        else:
            print(format_favorites(favorites))

    # 添加收藏
    if args.add_favorite:
        if add_favorite(args.add_favorite):
            print(f"✓ 已添加收藏: {args.add_favorite[:50]}...")
        else:
            print("✗ 收藏失败（可能已存在）")

    # 移除收藏
    if args.remove_favorite:
        if remove_favorite(args.remove_favorite):
            print(f"✓ 已移除收藏 ID: {args.remove_favorite}")
        else:
            print(f"✗ 移除失败，ID {args.remove_favorite} 不存在")

    # 复制历史
    if args.copy:
        history = get_history(limit=args.copy)
        if 0 < args.copy <= len(history):
            content = history[args.copy - 1].get('content', '')
            if copy_to_clipboard(content):
                print(f"✓ 已复制第 {args.copy} 条到剪贴板")
            else:
                print("✗ 复制到剪贴板失败")
        else:
            print(f"✗ 无第 {args.copy} 条历史记录")

    # 清空历史
    if args.clear:
        if clear_history():
            print("✓ 已清空剪贴板历史")
        else:
            print("✗ 清空失败")


if __name__ == "__main__":
    main()