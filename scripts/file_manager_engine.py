#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
智能文件管理引擎
让星期五能够自动按类型/时间整理文件，提供文件搜索、分析、智能分类功能
"""
import os
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any


class FileManagerEngine:
    """智能文件管理引擎"""

    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.project_root = os.path.dirname(self.base_dir)

        # 文件类型映射
        self.file_types = {
            'images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg', '.ico'],
            'videos': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm'],
            'audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a'],
            'documents': ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt', '.md', '.rtf'],
            'archives': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'],
            'code': ['.py', '.js', '.html', '.css', '.java', '.cpp', '.c', '.go', '.rs', '.ts', '.json', '.xml', '.yaml', '.yml'],
            'executables': ['.exe', '.dll', '.msi', '.bat', '.cmd', '.ps1']
        }

    def get_file_type(self, filename: str) -> str:
        """获取文件类型分类"""
        ext = Path(filename).suffix.lower()
        for category, extensions in self.file_types.items():
            if ext in extensions:
                return category
        return 'other'

    def search_files(self, directory: str, pattern: str = None,
                     file_type: str = None, min_size: int = None,
                     max_size: int = None, modified_after: str = None,
                     modified_before: str = None, recursive: bool = True) -> Dict[str, Any]:
        """
        搜索文件

        Args:
            directory: 搜索目录
            pattern: 文件名模式（支持通配符）
            file_type: 文件类型（images/videos/audio/documents/archives/code）
            min_size: 最小文件大小（字节）
            max_size: 最大文件大小（字节）
            modified_after: 修改时间之后（ISO格式）
            modified_before: 修改时间之前（ISO格式）
            recursive: 是否递归搜索

        Returns:
            搜索结果字典
        """
        results = {
            'directory': directory,
            'pattern': pattern,
            'file_type': file_type,
            'total_found': 0,
            'files': []
        }

        if not os.path.exists(directory):
            results['error'] = f"Directory not found: {directory}"
            return results

        # 解析时间
        time_after = None
        time_before = None
        if modified_after:
            try:
                time_after = datetime.fromisoformat(modified_after.replace('Z', '+00:00'))
            except:
                pass
        if modified_before:
            try:
                time_before = datetime.fromisoformat(modified_before.replace('Z', '+00:00'))
            except:
                pass

        try:
            if recursive:
                for root, dirs, files in os.walk(directory):
                    for filename in files:
                        if self._matches_criteria(filename, os.path.join(root, filename),
                                                   pattern, file_type, min_size, max_size,
                                                   time_after, time_before):
                            file_path = os.path.join(root, filename)
                            results['files'].append(self._get_file_info(file_path))
            else:
                for filename in os.listdir(directory):
                    file_path = os.path.join(directory, filename)
                    if os.path.isfile(file_path):
                        if self._matches_criteria(filename, file_path, pattern, file_type,
                                                  min_size, max_size, time_after, time_before):
                            results['files'].append(self._get_file_info(file_path))

            results['total_found'] = len(results['files'])
        except Exception as e:
            results['error'] = str(e)

        return results

    def _matches_criteria(self, filename: str, file_path: str, pattern: str,
                         file_type: str, min_size: int, max_size: int,
                         time_after: datetime, time_before: datetime) -> bool:
        """检查文件是否匹配条件"""
        # 名称模式匹配
        if pattern:
            import fnmatch
            if not fnmatch.fnmatch(filename.lower(), pattern.lower()):
                return False

        # 文件类型匹配
        if file_type:
            if self.get_file_type(filename) != file_type:
                return False

        # 文件大小匹配
        try:
            size = os.path.getsize(file_path)
            if min_size and size < min_size:
                return False
            if max_size and size > max_size:
                return False
        except:
            pass

        # 修改时间匹配
        try:
            mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
            if time_after and mtime < time_after:
                return False
            if time_before and mtime > time_before:
                return False
        except:
            pass

        return True

    def _get_file_info(self, file_path: str) -> Dict[str, Any]:
        """获取文件信息"""
        try:
            stat = os.stat(file_path)
            return {
                'name': os.path.basename(file_path),
                'path': file_path,
                'size': stat.st_size,
                'size_human': self._format_size(stat.st_size),
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'type': self.get_file_type(os.path.basename(file_path)),
                'extension': Path(file_path).suffix.lower()
            }
        except Exception as e:
            return {
                'name': os.path.basename(file_path),
                'path': file_path,
                'error': str(e)
            }

    def _format_size(self, size: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} PB"

    def analyze_directory(self, directory: str, recursive: bool = True) -> Dict[str, Any]:
        """
        分析目录

        Args:
            directory: 要分析的目录
            recursive: 是否递归分析

        Returns:
            目录分析结果
        """
        result = {
            'directory': directory,
            'total_files': 0,
            'total_size': 0,
            'total_size_human': '0 B',
            'by_type': {},
            'largest_files': [],
            'recent_files': []
        }

        if not os.path.exists(directory):
            result['error'] = f"Directory not found: {directory}"
            return result

        files_info = []

        try:
            if recursive:
                for root, dirs, files in os.walk(directory):
                    for filename in files:
                        file_path = os.path.join(root, filename)
                        try:
                            stat = os.stat(file_path)
                            files_info.append({
                                'name': filename,
                                'path': file_path,
                                'size': stat.st_size,
                                'modified': stat.st_mtime,
                                'type': self.get_file_type(filename)
                            })
                        except:
                            pass
            else:
                for filename in os.listdir(directory):
                    file_path = os.path.join(directory, filename)
                    if os.path.isfile(file_path):
                        try:
                            stat = os.stat(file_path)
                            files_info.append({
                                'name': filename,
                                'path': file_path,
                                'size': stat.st_size,
                                'modified': stat.st_mtime,
                                'type': self.get_file_type(filename)
                            })
                        except:
                            pass

            result['total_files'] = len(files_info)

            # 按类型统计
            for f in files_info:
                ftype = f['type']
                if ftype not in result['by_type']:
                    result['by_type'][ftype] = {'count': 0, 'size': 0}
                result['by_type'][ftype]['count'] += 1
                result['by_type'][ftype]['size'] += f['size']
                result['total_size'] += f['size']

            # 格式化类型大小
            for ftype in result['by_type']:
                result['by_type'][ftype]['size_human'] = self._format_size(
                    result['by_type'][ftype]['size']
                )

            result['total_size_human'] = self._format_size(result['total_size'])

            # 最大文件
            sorted_by_size = sorted(files_info, key=lambda x: x['size'], reverse=True)
            result['largest_files'] = [
                {
                    'name': f['name'],
                    'path': f['path'],
                    'size': f['size'],
                    'size_human': self._format_size(f['size'])
                }
                for f in sorted_by_size[:10]
            ]

            # 最近文件
            sorted_by_time = sorted(files_info, key=lambda x: x['modified'], reverse=True)
            result['recent_files'] = [
                {
                    'name': f['name'],
                    'path': f['path'],
                    'modified': datetime.fromtimestamp(f['modified']).isoformat()
                }
                for f in sorted_by_time[:10]
            ]

        except Exception as e:
            result['error'] = str(e)

        return result

    def organize_files(self, source_dir: str, target_dir: str = None,
                       mode: str = 'by_type', create_subdirs: bool = True) -> Dict[str, Any]:
        """
        整理文件

        Args:
            source_dir: 源目录
            target_dir: 目标目录（默认为源目录下的 organized）
            mode: 整理模式（by_type/by_date/by_size）
            create_subdirs: 是否创建子目录

        Returns:
            整理结果
        """
        if target_dir is None:
            target_dir = os.path.join(source_dir, 'organized')

        result = {
            'source': source_dir,
            'target': target_dir,
            'mode': mode,
            'moved': [],
            'errors': []
        }

        if not os.path.exists(source_dir):
            result['error'] = f"Source directory not found: {source_dir}"
            return result

        try:
            os.makedirs(target_dir, exist_ok=True)

            for filename in os.listdir(source_dir):
                source_path = os.path.join(source_dir, filename)

                if not os.path.isfile(source_path):
                    continue

                # 计算目标路径
                if mode == 'by_type':
                    file_type = self.get_file_type(filename)
                    subdir = file_type if create_subdirs else ''
                elif mode == 'by_date':
                    mtime = os.path.getmtime(source_path)
                    date_str = datetime.fromtimestamp(mtime).strftime('%Y-%m')
                    subdir = date_str if create_subdirs else ''
                elif mode == 'by_size':
                    size = os.path.getsize(source_path)
                    if size < 1024 * 1024:  # < 1MB
                        subdir = 'small'
                    elif size < 100 * 1024 * 1024:  # < 100MB
                        subdir = 'medium'
                    else:
                        subdir = 'large'
                else:
                    subdir = ''

                # 创建子目录
                if subdir:
                    target_subdir = os.path.join(target_dir, subdir)
                    os.makedirs(target_subdir, exist_ok=True)
                    target_path = os.path.join(target_subdir, filename)
                else:
                    target_path = os.path.join(target_dir, filename)

                # 处理文件名冲突
                if os.path.exists(target_path):
                    base, ext = os.path.splitext(filename)
                    counter = 1
                    while os.path.exists(target_path):
                        target_path = os.path.join(
                            os.path.dirname(target_path),
                            f"{base}_{counter}{ext}"
                        )
                        counter += 1

                # 移动文件
                try:
                    shutil.move(source_path, target_path)
                    result['moved'].append({
                        'from': source_path,
                        'to': target_path,
                        'category': subdir
                    })
                except Exception as e:
                    result['errors'].append({
                        'file': source_path,
                        'error': str(e)
                    })

        except Exception as e:
            result['error'] = str(e)

        return result


def handle_request(intent: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    处理文件管理请求

    Args:
        intent: 意图（search/analyze/organize）
        params: 参数

    Returns:
        处理结果
    """
    engine = FileManagerEngine()

    if intent == 'search':
        return engine.search_files(
            directory=params.get('directory', os.getcwd()),
            pattern=params.get('pattern'),
            file_type=params.get('file_type'),
            min_size=params.get('min_size'),
            max_size=params.get('max_size'),
            modified_after=params.get('modified_after'),
            modified_before=params.get('modified_before'),
            recursive=params.get('recursive', True)
        )
    elif intent == 'analyze':
        return engine.analyze_directory(
            directory=params.get('directory', os.getcwd()),
            recursive=params.get('recursive', True)
        )
    elif intent == 'organize':
        return engine.organize_files(
            source_dir=params.get('source_dir', os.getcwd()),
            target_dir=params.get('target_dir'),
            mode=params.get('mode', 'by_type'),
            create_subdirs=params.get('create_subdirs', True)
        )
    else:
        return {'error': f'Unknown intent: {intent}'}


if __name__ == '__main__':
    import sys
    import argparse

    parser = argparse.ArgumentParser(description='智能文件管理引擎')
    parser.add_argument('command', choices=['search', 'analyze', 'organize'],
                        help='要执行的命令')
    parser.add_argument('--directory', '-d', default='.', help='目录路径')
    parser.add_argument('--pattern', '-p', help='文件名模式')
    parser.add_argument('--type', '-t', help='文件类型')
    parser.add_argument('--mode', '-m', default='by_type', choices=['by_type', 'by_date', 'by_size'],
                        help='整理模式')
    parser.add_argument('--output', '-o', help='输出文件路径（JSON）')

    args = parser.parse_args()

    params = {'directory': args.directory}

    if args.pattern:
        params['pattern'] = args.pattern
    if args.type:
        params['file_type'] = args.type

    if args.command == 'search':
        result = handle_request('search', params)
    elif args.command == 'analyze':
        result = handle_request('analyze', params)
    else:
        result = handle_request('organize', {'source_dir': args.directory, 'mode': args.mode})

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"结果已保存到: {args.output}")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))