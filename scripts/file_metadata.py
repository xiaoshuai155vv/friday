#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件元数据管理模块
提供文件元数据提取、标签管理、智能分类等功能
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path

# 添加项目路径以便导入其他模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 元数据存储文件路径
METADATA_FILE = os.path.join(os.path.dirname(__file__), "..", "runtime", "state", "file_metadata.json")
TAGS_FILE = os.path.join(os.path.dirname(__file__), "..", "runtime", "state", "file_tags.json")

def get_file_metadata(file_path):
    """
    获取文件元数据

    Args:
        file_path (str): 文件路径

    Returns:
        dict: 文件元数据信息
    """
    try:
        stat = os.stat(file_path)

        # 获取文件基本信息
        metadata = {
            "path": file_path,
            "name": os.path.basename(file_path),
            "size": stat.st_size,
            "created_time": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "accessed_time": datetime.fromtimestamp(stat.st_atime).isoformat(),
            "is_directory": os.path.isdir(file_path),
            "extension": os.path.splitext(file_path)[1].lower() if not os.path.isdir(file_path) else ""
        }

        # 如果是文件，添加更多详细信息
        if not metadata["is_directory"]:
            # 根据文件扩展名判断类型
            file_type_map = {
                '.txt': '文本文件',
                '.md': 'Markdown文件',
                '.py': 'Python脚本',
                '.js': 'JavaScript文件',
                '.html': 'HTML文件',
                '.css': 'CSS样式文件',
                '.json': 'JSON文件',
                '.xml': 'XML文件',
                '.csv': 'CSV文件',
                '.pdf': 'PDF文档',
                '.doc': 'Word文档',
                '.docx': 'Word文档',
                '.xls': 'Excel表格',
                '.xlsx': 'Excel表格',
                '.ppt': 'PowerPoint演示',
                '.pptx': 'PowerPoint演示',
                '.jpg': 'JPEG图片',
                '.jpeg': 'JPEG图片',
                '.png': 'PNG图片',
                '.gif': 'GIF动画',
                '.bmp': '位图图片',
                '.mp3': 'MP3音频',
                '.wav': 'WAV音频',
                '.mp4': 'MP4视频',
                '.avi': 'AVI视频',
                '.mov': 'MOV视频',
                '.exe': 'Windows可执行程序',
                '.dll': 'Windows动态链接库',
                '.zip': 'ZIP压缩包',
                '.rar': 'RAR压缩包'
            }

            metadata["type"] = file_type_map.get(metadata["extension"], "未知文件类型")

        return metadata
    except Exception as e:
        return {"error": f"获取元数据失败: {str(e)}"}

def add_file_tag(file_path, tag):
    """
    为文件添加标签

    Args:
        file_path (str): 文件路径
        tag (str): 标签名称

    Returns:
        bool: 是否成功
    """
    try:
        # 读取现有标签
        tags_data = {}
        if os.path.exists(TAGS_FILE):
            with open(TAGS_FILE, 'r', encoding='utf-8') as f:
                tags_data = json.load(f)

        # 添加标签
        if file_path not in tags_data:
            tags_data[file_path] = []

        if tag not in tags_data[file_path]:
            tags_data[file_path].append(tag)

        # 保存标签
        with open(TAGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(tags_data, f, ensure_ascii=False, indent=2)

        return True
    except Exception as e:
        print(f"添加标签失败: {str(e)}", file=sys.stderr)
        return False

def get_file_tags(file_path):
    """
    获取文件的所有标签

    Args:
        file_path (str): 文件路径

    Returns:
        list: 标签列表
    """
    try:
        tags_data = {}
        if os.path.exists(TAGS_FILE):
            with open(TAGS_FILE, 'r', encoding='utf-8') as f:
                tags_data = json.load(f)

        return tags_data.get(file_path, [])
    except Exception as e:
        print(f"获取标签失败: {str(e)}", file=sys.stderr)
        return []

def remove_file_tag(file_path, tag):
    """
    移除文件标签

    Args:
        file_path (str): 文件路径
        tag (str): 标签名称

    Returns:
        bool: 是否成功
    """
    try:
        tags_data = {}
        if os.path.exists(TAGS_FILE):
            with open(TAGS_FILE, 'r', encoding='utf-8') as f:
                tags_data = json.load(f)

        if file_path in tags_data and tag in tags_data[file_path]:
            tags_data[file_path].remove(tag)

            # 如果没有标签了，删除该文件记录
            if not tags_data[file_path]:
                del tags_data[file_path]

            # 保存标签
            with open(TAGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(tags_data, f, ensure_ascii=False, indent=2)

            return True
        return False
    except Exception as e:
        print(f"移除标签失败: {str(e)}", file=sys.stderr)
        return False

def search_files_by_tag(tag):
    """
    根据标签搜索文件

    Args:
        tag (str): 标签名称

    Returns:
        list: 匹配的文件路径列表
    """
    try:
        tags_data = {}
        if os.path.exists(TAGS_FILE):
            with open(TAGS_FILE, 'r', encoding='utf-8') as f:
                tags_data = json.load(f)

        matched_files = []
        for file_path, tags in tags_data.items():
            if tag in tags:
                matched_files.append(file_path)

        return matched_files
    except Exception as e:
        print(f"搜索标签失败: {str(e)}", file=sys.stderr)
        return []

def classify_file(file_path):
    """
    根据文件特征进行智能分类

    Args:
        file_path (str): 文件路径

    Returns:
        list: 分类标签列表
    """
    try:
        metadata = get_file_metadata(file_path)
        classifications = []

        # 根据文件类型分类
        if metadata.get("type"):
            classifications.append(metadata["type"])

        # 根据文件大小分类
        size = metadata.get("size", 0)
        if size < 1024:  # 小于1KB
            classifications.append("小型文件")
        elif size < 1024 * 1024:  # 小于1MB
            classifications.append("中型文件")
        else:  # 大于等于1MB
            classifications.append("大型文件")

        # 根据创建时间分类（最近一个月）
        created_time = metadata.get("created_time")
        if created_time:
            try:
                created_dt = datetime.fromisoformat(created_time.replace('Z', '+00:00'))
                days_diff = (datetime.now() - created_dt).days
                if days_diff <= 30:
                    classifications.append("近期文件")
                elif days_diff <= 90:
                    classifications.append("中期文件")
                else:
                    classifications.append("历史文件")
            except:
                pass

        # 根据文件扩展名分类
        ext = metadata.get("extension", "")
        if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
            classifications.append("图像文件")
        elif ext in ['.mp3', '.wav', '.flac']:
            classifications.append("音频文件")
        elif ext in ['.mp4', '.avi', '.mov']:
            classifications.append("视频文件")
        elif ext in ['.pdf', '.doc', '.docx', '.xls', '.xlsx']:
            classifications.append("办公文档")
        elif ext in ['.py', '.js', '.html', '.css']:
            classifications.append("代码文件")

        return classifications
    except Exception as e:
        print(f"文件分类失败: {str(e)}", file=sys.stderr)
        return []

def list_all_tags():
    """
    列出所有标签

    Returns:
        list: 所有标签列表
    """
    try:
        tags_data = {}
        if os.path.exists(TAGS_FILE):
            with open(TAGS_FILE, 'r', encoding='utf-8') as f:
                tags_data = json.load(f)

        all_tags = set()
        for tags in tags_data.values():
            all_tags.update(tags)

        return list(all_tags)
    except Exception as e:
        print(f"列出标签失败: {str(e)}", file=sys.stderr)
        return []

def main():
    """
    主函数 - 用于命令行测试
    """
    if len(sys.argv) < 2:
        print("用法: python file_metadata.py <命令> [参数...]")
        print("命令:")
        print("  metadata <文件路径>       - 获取文件元数据")
        print("  add-tag <文件路径> <标签> - 添加文件标签")
        print("  get-tags <文件路径>       - 获取文件标签")
        print("  remove-tag <文件路径> <标签> - 移除文件标签")
        print("  search-tag <标签>         - 搜索带标签的文件")
        print("  classify <文件路径>       - 智能分类文件")
        print("  list-tags                 - 列出所有标签")
        return

    command = sys.argv[1]

    if command == "metadata":
        if len(sys.argv) < 3:
            print("请提供文件路径")
            return
        file_path = sys.argv[2]
        metadata = get_file_metadata(file_path)
        print(json.dumps(metadata, ensure_ascii=False, indent=2))

    elif command == "add-tag":
        if len(sys.argv) < 4:
            print("请提供文件路径和标签")
            return
        file_path = sys.argv[2]
        tag = sys.argv[3]
        success = add_file_tag(file_path, tag)
        print(f"标签添加{'成功' if success else '失败'}")

    elif command == "get-tags":
        if len(sys.argv) < 3:
            print("请提供文件路径")
            return
        file_path = sys.argv[2]
        tags = get_file_tags(file_path)
        print(json.dumps(tags, ensure_ascii=False, indent=2))

    elif command == "remove-tag":
        if len(sys.argv) < 4:
            print("请提供文件路径和标签")
            return
        file_path = sys.argv[2]
        tag = sys.argv[3]
        success = remove_file_tag(file_path, tag)
        print(f"标签移除{'成功' if success else '失败'}")

    elif command == "search-tag":
        if len(sys.argv) < 3:
            print("请提供标签")
            return
        tag = sys.argv[2]
        files = search_files_by_tag(tag)
        print(json.dumps(files, ensure_ascii=False, indent=2))

    elif command == "classify":
        if len(sys.argv) < 3:
            print("请提供文件路径")
            return
        file_path = sys.argv[2]
        classifications = classify_file(file_path)
        print(json.dumps(classifications, ensure_ascii=False, indent=2))

    elif command == "list-tags":
        tags = list_all_tags()
        print(json.dumps(tags, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()