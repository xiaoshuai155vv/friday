#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""文档快速预览模块（QuickLook风格）。用法: python quick_look.py <文件路径> [行数限制]

支持预览常见文件类型：txt, json, md, py, js, html, css, xml, yaml, csv, log 等
无需打开完整应用，直接在终端显示文件内容预览。
"""
import sys
import os
import json
import re
from pathlib import Path

# 默认预览行数
DEFAULT_LINES = 100
MAX_LINE_LENGTH = 500  # 单行最大字符数

# 文件类型与预览方式映射
PREVIEW_HANDLERS = {
    '.txt': 'text',
    '.log': 'text',
    '.md': 'markdown',
    '.json': 'json',
    '.py': 'code',
    '.js': 'code',
    '.ts': 'code',
    '.html': 'code',
    '.css': 'code',
    '.xml': 'code',
    '.yaml': 'code',
    '.yml': 'code',
    '.csv': 'csv',
    '.sh': 'code',
    '.bat': 'code',
    '.cmd': 'code',
    '.sql': 'code',
    '.c': 'code',
    '.cpp': 'code',
    '.java': 'code',
    '.go': 'code',
    '.rs': 'code',
    '.swift': 'code',
    '.kt': 'code',
    '.rb': 'code',
    '.php': 'code',
    '.lua': 'code',
    '.ps1': 'code',
}

def get_file_type(path):
    """根据文件扩展名确定文件类型"""
    ext = Path(path).suffix.lower()
    return PREVIEW_HANDLERS.get(ext, 'text')

def truncate_line(line, max_len=MAX_LINE_LENGTH):
    """截断过长的行"""
    line = line.rstrip('\n\r')
    if len(line) > max_len:
        return line[:max_len] + " ..."
    return line

def preview_text(lines, file_path):
    """预览纯文本文件"""
    print(f"=== 文本预览: {os.path.abspath(file_path)} ===")
    print(f"=== 总行数: {len(lines)} ===\n")
    for i, line in enumerate(lines, 1):
        print(f"{i:4d}: {truncate_line(line)}")

def preview_markdown(lines, file_path):
    """预览 Markdown 文件，突出标题"""
    print(f"=== Markdown 预览: {os.path.abspath(file_path)} ===")
    print(f"=== 总行数: {len(lines)} ===\n")
    for i, line in enumerate(lines, 1):
        line = line.rstrip('\n\r')
        # 突出标题行
        if line.startswith('#'):
            print(f"\n{i:4d}: {line}")
        elif line.strip().startswith('```'):
            print(f"{i:4d}: {line[:80]}")
        else:
            print(f"{i:4d}: {truncate_line(line)}")

def preview_json(lines, file_path):
    """预览 JSON 文件，格式化输出"""
    print(f"=== JSON 预览: {os.path.abspath(file_path)} ===\n")
    content = ''.join(lines)
    try:
        data = json.loads(content)
        # 格式化输出，限制深度
        formatted = json.dumps(data, indent=2, ensure_ascii=False, default=str)
        # 限制输出行数
        formatted_lines = formatted.split('\n')[:DEFAULT_LINES]
        for i, line in enumerate(formatted_lines, 1):
            print(f"{i:4d}: {line[:MAX_LINE_LENGTH]}")
        if len(formatted.split('\n')) > DEFAULT_LINES:
            print(f"\n... (共 {len(formatted.split(chr(10)))} 行，仅显示前 {DEFAULT_LINES} 行)")
    except json.JSONDecodeError as e:
        print(f"JSON 解析错误: {e}")
        print("尝试作为纯文本显示:")
        for i, line in enumerate(lines[:DEFAULT_LINES], 1):
            print(f"{i:4d}: {truncate_line(line)}")

def preview_code(lines, file_path):
    """预览代码文件，突出注释和字符串"""
    print(f"=== 代码预览: {os.path.abspath(file_path)} ===")
    print(f"=== 总行数: {len(lines)} ===\n")
    for i, line in enumerate(lines, 1):
        line = line.rstrip('\n\r')
        # 突出函数定义
        if re.match(r'^\s*(def|class|function|func|public|private|protected)\s+', line):
            print(f"\n{i:4d}: {line}")
        elif line.strip().startswith('#') or line.strip().startswith('//'):
            print(f"{i:4d}: {line}")  # 注释
        else:
            print(f"{i:4d}: {truncate_line(line)}")

def preview_csv(lines, file_path):
    """预览 CSV 文件，以表格形式展示"""
    print(f"=== CSV 预览: {os.path.abspath(file_path)} ===")
    print(f"=== 总行数: {len(lines)} ===\n")
    # 读取前几行作为表头
    sample_lines = lines[:min(10, len(lines))]
    for i, line in enumerate(sample_lines, 1):
        fields = line.strip().split(',')
        print(f"行{i:2d}: {' | '.join(fields[:10])}")  # 限制显示前10列
    if len(lines) > 10:
        print(f"\n... (共 {len(lines)} 行，仅显示前 10 行)")

def preview_file(file_path, max_lines=None):
    """预览文件主函数"""
    if max_lines is None:
        max_lines = DEFAULT_LINES

    # 检查文件是否存在
    if not os.path.exists(file_path):
        print(f"错误: 文件不存在 - {file_path}", file=sys.stderr)
        return False

    if not os.path.isfile(file_path):
        print(f"错误: 不是有效文件 - {file_path}", file=sys.stderr)
        return False

    # 读取文件
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except UnicodeDecodeError:
        # 尝试其他编码
        try:
            with open(file_path, 'r', encoding='gbk') as f:
                lines = f.readlines()
        except Exception as e:
            print(f"错误: 无法读取文件 - {e}", file=sys.stderr)
            return False
    except Exception as e:
        print(f"错误: 读取文件失败 - {e}", file=sys.stderr)
        return False

    # 文件为空
    if not lines:
        print(f"文件为空: {file_path}")
        return True

    # 根据文件类型选择预览方式
    file_type = get_file_type(file_path)

    # 截取需要显示的行数
    display_lines = lines[:max_lines]

    if file_type == 'markdown':
        preview_markdown(display_lines, file_path)
    elif file_type == 'json':
        preview_json(display_lines, file_path)
    elif file_type == 'code':
        preview_code(display_lines, file_path)
    elif file_type == 'csv':
        preview_csv(display_lines, file_path)
    else:
        preview_text(display_lines, file_path)

    # 提示是否还有更多内容
    if len(lines) > max_lines:
        print(f"\n=== 还有 {len(lines) - max_lines} 行未显示 ===")
        print(f"使用 'python quick_look.py {file_path} {len(lines)}' 查看全部")

    return True

def main():
    if len(sys.argv) < 2:
        print("用法: python quick_look.py <文件路径> [行数限制]", file=sys.stderr)
        print("示例:", file=sys.stderr)
        print("  python quick_look.py test.txt", file=sys.stderr)
        print("  python quick_look.py data.json 50", file=sys.stderr)
        print("  python quick_look.py readme.md", file=sys.stderr)
        sys.exit(1)

    file_path = sys.argv[1]
    max_lines = int(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_LINES

    success = preview_file(file_path, max_lines)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    sys.exit(main())