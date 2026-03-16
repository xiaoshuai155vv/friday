#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM-OS 文件管理器 - 提供文件浏览、搜索、操作等能力

本模块提供类似 Windows 资源管理器的文件管理能力，包括：
- 目录浏览与导航
- 文件搜索
- 文件操作（复制、粘贴、重命名、删除、新建）
- 文件详情查看
- 磁盘空间查看

版本: 1.0.0
依赖: os, shutil, pathlib, subprocess
"""

import os
import sys
import json
import shutil
import argparse
from pathlib import Path
from datetime import datetime


def list_directory(path=None, show_hidden=False, sort_by="name"):
    """
    列出目录内容

    Args:
        path: 目录路径，默认当前目录
        show_hidden: 是否显示隐藏文件
        sort_by: 排序方式 (name, size, date, type)

    Returns:
        JSON 格式的目录内容列表
    """
    if path is None:
        path = os.getcwd()

    path = Path(path).resolve()

    if not path.exists():
        return json.dumps({"error": f"路径不存在: {path}"}, ensure_ascii=False)

    if not path.is_dir():
        return json.dumps({"error": f"不是目录: {path}"}, ensure_ascii=False)

    try:
        items = []
        for item in path.iterdir():
            # 跳过隐藏文件（如果不需要显示）
            if not show_hidden and item.name.startswith('.'):
                continue

            try:
                stat = item.stat()
                item_info = {
                    "name": item.name,
                    "type": "directory" if item.is_dir() else "file",
                    "size": stat.st_size if item.is_file() else 0,
                    "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                    "path": str(item)
                }
                items.append(item_info)
            except (PermissionError, OSError):
                continue

        # 排序
        if sort_by == "name":
            items.sort(key=lambda x: (x["type"], x["name"].lower()))
        elif sort_by == "size":
            items.sort(key=lambda x: (x["type"], -x["size"]))
        elif sort_by == "date":
            items.sort(key=lambda x: (x["type"], x["modified"]))
        elif sort_by == "type":
            items.sort(key=lambda x: (x["type"], x.get("suffix", "")))

        return json.dumps({
            "path": str(path),
            "parent": str(path.parent),
            "items": items,
            "total": len(items)
        }, ensure_ascii=False, indent=2)

    except Exception as e:
        return json.dumps({"error": f"列出目录失败: {str(e)}"}, ensure_ascii=False)


def search_files(path, pattern, recursive=False, max_results=100):
    """
    搜索文件

    Args:
        path: 搜索起始路径
        pattern: 搜索模式（支持通配符）
        recursive: 是否递归搜索子目录
        max_results: 最大结果数量

    Returns:
        JSON 格式的搜索结果
    """
    path = Path(path).resolve()

    if not path.exists():
        return json.dumps({"error": f"搜索路径不存在: {path}"}, ensure_ascii=False)

    try:
        results = []

        if recursive:
            # 递归搜索
            for item in path.rglob(pattern):
                if len(results) >= max_results:
                    break
                try:
                    stat = item.stat()
                    results.append({
                        "name": item.name,
                        "type": "directory" if item.is_dir() else "file",
                        "size": stat.st_size if item.is_file() else 0,
                        "path": str(item)
                    })
                except (PermissionError, OSError):
                    continue
        else:
            # 仅当前目录
            for item in path.glob(pattern):
                if len(results) >= max_results:
                    break
                try:
                    stat = item.stat()
                    results.append({
                        "name": item.name,
                        "type": "directory" if item.is_dir() else "file",
                        "size": stat.st_size if item.is_file() else 0,
                        "path": str(item)
                    })
                except (PermissionError, OSError):
                    continue

        return json.dumps({
            "pattern": pattern,
            "path": str(path),
            "recursive": recursive,
            "results": results,
            "total": len(results)
        }, ensure_ascii=False, indent=2)

    except Exception as e:
        return json.dumps({"error": f"搜索失败: {str(e)}"}, ensure_ascii=False)


def get_file_info(path):
    """
    获取文件/目录详细信息

    Args:
        path: 文件或目录路径

    Returns:
        JSON 格式的详细信息
    """
    path = Path(path).resolve()

    if not path.exists():
        return json.dumps({"error": f"路径不存在: {path}"}, ensure_ascii=False)

    try:
        stat = path.stat()

        info = {
            "name": path.name,
            "type": "directory" if path.is_dir() else "file",
            "path": str(path),
            "parent": str(path.parent),
            "size": stat.st_size,
            "size_formatted": format_size(stat.st_size),
            "created": datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d %H:%M:%S"),
            "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
            "accessed": datetime.fromtimestamp(stat.st_atime).strftime("%Y-%m-%d %H:%M:%S"),
        }

        # 如果是文件，尝试获取扩展名
        if path.is_file():
            info["extension"] = path.suffix

        return json.dumps(info, ensure_ascii=False, indent=2)

    except Exception as e:
        return json.dumps({"error": f"获取信息失败: {str(e)}"}, ensure_ascii=False)


def copy_file(source, destination, overwrite=False):
    """
    复制文件或目录

    Args:
        source: 源路径
        destination: 目标路径
        overwrite: 是否覆盖已存在的文件

    Returns:
        JSON 格式的执行结果
    """
    source = Path(source).resolve()
    destination = Path(destination).resolve()

    if not source.exists():
        return json.dumps({"error": f"源路径不存在: {source}"}, ensure_ascii=False)

    try:
        if destination.exists() and not overwrite:
            return json.dumps({"error": f"目标已存在: {destination}"}, ensure_ascii=False)

        if source.is_dir():
            if destination.exists() and destination.is_dir():
                # 目录复制到已存在的目录中
                dest_path = destination / source.name
            else:
                dest_path = destination

            if dest_path.exists() and not overwrite:
                return json.dumps({"error": f"目标目录已存在: {dest_path}"}, ensure_ascii=False)

            shutil.copytree(source, dest_path, dirs_exist_ok=overwrite)
            action = "copied"
        else:
            # 确保目标目录存在
            destination.parent.mkdir(parents=True, exist_ok=True)

            if destination.is_dir():
                dest_path = destination / source.name
            else:
                dest_path = destination

            shutil.copy2(source, dest_path)
            action = "copied"

        return json.dumps({
            "action": action,
            "source": str(source),
            "destination": str(dest_path),
            "success": True
        }, ensure_ascii=False)

    except Exception as e:
        return json.dumps({"error": f"复制失败: {str(e)}"}, ensure_ascii=False)


def move_file(source, destination, overwrite=False):
    """
    移动/重命名文件或目录

    Args:
        source: 源路径
        destination: 目标路径
        overwrite: 是否覆盖已存在的文件

    Returns:
        JSON 格式的执行结果
    """
    source = Path(source).resolve()
    destination = Path(destination).resolve()

    if not source.exists():
        return json.dumps({"error": f"源路径不存在: {source}"}, ensure_ascii=False)

    try:
        if destination.exists() and not overwrite:
            return json.dumps({"error": f"目标已存在: {destination}"}, ensure_ascii=False)

        # 确保目标父目录存在
        destination.parent.mkdir(parents=True, exist_ok=True)

        shutil.move(str(source), str(destination))
        action = "moved" if source != destination.parent else "renamed"

        return json.dumps({
            "action": action,
            "source": str(source),
            "destination": str(destination),
            "success": True
        }, ensure_ascii=False)

    except Exception as e:
        return json.dumps({"error": f"移动失败: {str(e)}"}, ensure_ascii=False)


def delete_file(path, recursive=False):
    """
    删除文件或目录

    Args:
        path: 要删除的路径
        recursive: 是否递归删除目录

    Returns:
        JSON 格式的执行结果
    """
    path = Path(path).resolve()

    if not path.exists():
        return json.dumps({"error": f"路径不存在: {path}"}, ensure_ascii=False)

    try:
        if path.is_dir():
            if recursive:
                shutil.rmtree(path)
                action = "deleted_recursive"
            else:
                path.rmdir()
                action = "deleted_empty"
        else:
            path.unlink()
            action = "deleted"

        return json.dumps({
            "action": action,
            "path": str(path),
            "success": True
        }, ensure_ascii=False)

    except Exception as e:
        return json.dumps({"error": f"删除失败: {str(e)}"}, ensure_ascii=False)


def create_file(path, content="", is_directory=False):
    """
    新建文件或目录

    Args:
        path: 新建路径
        content: 文件内容（仅对文件有效）
        is_directory: 是否创建目录

    Returns:
        JSON 格式的执行结果
    """
    path = Path(path).resolve()

    try:
        if is_directory:
            path.mkdir(parents=True, exist_ok=False)
            action = "directory_created"
        else:
            # 确保父目录存在
            path.parent.mkdir(parents=True, exist_ok=True)
            # 创建文件并写入内容
            path.write_text(content, encoding='utf-8')
            action = "file_created"

        return json.dumps({
            "action": action,
            "path": str(path),
            "success": True
        }, ensure_ascii=False)

    except FileExistsError:
        return json.dumps({"error": f"路径已存在: {path}"}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": f"创建失败: {str(e)}"}, ensure_ascii=False)


def get_disk_usage(path=None):
    """
    获取磁盘使用情况

    Args:
        path: 路径，默认当前盘符

    Returns:
        JSON 格式的磁盘使用信息
    """
    if path is None:
        path = os.getcwd()

    path = Path(path).resolve()

    try:
        # 获取磁盘总空间和可用空间
        stat = shutil.disk_usage(path)

        return json.dumps({
            "path": str(path),
            "total": stat.total,
            "total_formatted": format_size(stat.total),
            "used": stat.used,
            "used_formatted": format_size(stat.used),
            "free": stat.free,
            "free_formatted": format_size(stat.free),
            "percent": round(stat.used / stat.total * 100, 1)
        }, ensure_ascii=False, indent=2)

    except Exception as e:
        return json.dumps({"error": f"获取磁盘信息失败: {str(e)}"}, ensure_ascii=False)


def format_size(size):
    """格式化文件大小"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} PB"


def get_quick_access():
    """
    获取快速访问位置（用户主目录、桌面、下载等）

    Returns:
        JSON 格式的快速访问位置列表
    """
    home = Path.home()

    locations = [
        {"name": "用户主目录", "path": str(home), "icon": "home"},
        {"name": "桌面", "path": str(home / "Desktop"), "icon": "desktop"},
        {"name": "下载", "path": str(home / "Downloads"), "icon": "download"},
        {"name": "文档", "path": str(home / "Documents"), "icon": "document"},
        {"name": "图片", "path": str(home / "Pictures"), "icon": "picture"},
        {"name": "音乐", "path": str(home / "Music"), "icon": "music"},
        {"name": "视频", "path": str(home / "Videos"), "icon": "video"},
    ]

    # 添加 Windows 特定位置
    if sys.platform == "win32":
        # 添加快速访问（如果存在）
        quick_access = home / "AppData" / "Roaming" / "Microsoft" / "Windows" / "Recent"
        if quick_access.exists():
            locations.append({
                "name": "最近访问",
                "path": str(quick_access),
                "icon": "clock"
            })

    return json.dumps({
        "locations": locations,
        "platform": sys.platform
    }, ensure_ascii=False, indent=2)


def main():
    """命令行入口"""
    import io
    # 设置标准输出编码为 UTF-8
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

    parser = argparse.ArgumentParser(description="LLM-OS 文件管理器")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # list 命令
    list_parser = subparsers.add_parser("list", help="列出目录内容")
    list_parser.add_argument("path", nargs="?", default=None, help="目录路径")
    list_parser.add_argument("--hidden", action="store_true", help="显示隐藏文件")
    list_parser.add_argument("--sort", choices=["name", "size", "date", "type"], default="name", help="排序方式")

    # search 命令
    search_parser = subparsers.add_parser("search", help="搜索文件")
    search_parser.add_argument("path", nargs="?", default=".", help="搜索起始路径")
    search_parser.add_argument("pattern", help="搜索模式")
    search_parser.add_argument("-r", "--recursive", action="store_true", help="递归搜索")
    search_parser.add_argument("-m", "--max", type=int, default=100, help="最大结果数")

    # info 命令
    info_parser = subparsers.add_parser("info", help="获取文件信息")
    info_parser.add_argument("path", help="文件或目录路径")

    # copy 命令
    copy_parser = subparsers.add_parser("copy", help="复制文件或目录")
    copy_parser.add_argument("source", help="源路径")
    copy_parser.add_argument("destination", help="目标路径")
    copy_parser.add_argument("-f", "--force", action="store_true", help="覆盖已存在的文件")

    # move 命令
    move_parser = subparsers.add_parser("move", help="移动/重命名文件或目录")
    move_parser.add_argument("source", help="源路径")
    move_parser.add_argument("destination", help="目标路径")
    move_parser.add_argument("-f", "--force", action="store_true", help="覆盖已存在的文件")

    # delete 命令
    delete_parser = subparsers.add_parser("delete", help="删除文件或目录")
    delete_parser.add_argument("path", help="要删除的路径")
    delete_parser.add_argument("-r", "--recursive", action="store_true", help="递归删除目录")

    # create 命令
    create_parser = subparsers.add_parser("create", help="新建文件或目录")
    create_parser.add_argument("path", help="新建路径")
    create_parser.add_argument("-d", "--directory", action="store_true", help="创建目录")
    create_parser.add_argument("-c", "--content", default="", help="文件内容")

    # disk 命令
    disk_parser = subparsers.add_parser("disk", help="获取磁盘使用情况")
    disk_parser.add_argument("path", nargs="?", default=None, help="路径")

    # quick 命令
    subparsers.add_parser("quick", help="获取快速访问位置")

    args = parser.parse_args()

    # 执行对应命令
    if args.command == "list":
        print(list_directory(args.path, args.hidden, args.sort))
    elif args.command == "search":
        print(search_files(args.path, args.pattern, args.recursive, args.max))
    elif args.command == "info":
        print(get_file_info(args.path))
    elif args.command == "copy":
        print(copy_file(args.source, args.destination, args.force))
    elif args.command == "move":
        print(move_file(args.source, args.destination, args.force))
    elif args.command == "delete":
        print(delete_file(args.path, args.recursive))
    elif args.command == "create":
        print(create_file(args.path, args.content, args.directory))
    elif args.command == "disk":
        print(get_disk_usage(args.path))
    elif args.command == "quick":
        print(get_quick_access())
    else:
        parser.print_help()


if __name__ == "__main__":
    main()