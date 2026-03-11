#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""简单文件读写与列目录。用法: read <路径> | write <路径> [内容] | list <目录>"""
import sys
import os

def main():
    if len(sys.argv) < 2:
        print("用法: file_tool.py read <路径> | write <路径> [内容] | list <目录>", file=sys.stderr)
        sys.exit(1)
    cmd = sys.argv[1].lower()
    if cmd == "list":
        path = sys.argv[2] if len(sys.argv) > 2 else "."
        try:
            d = os.path.abspath(path)
            for name in sorted(os.listdir(d)):
                p = os.path.join(d, name)
                tag = "D" if os.path.isdir(p) else "F"
                print(tag, name)
        except Exception as e:
            print(str(e), file=sys.stderr)
            sys.exit(1)
        return 0
    if len(sys.argv) < 3:
        print("用法: file_tool.py read <路径> | write <路径> [内容] | list <目录>", file=sys.stderr)
        sys.exit(1)
    path = sys.argv[2]
    if cmd == "read":
        try:
            with open(path, "r", encoding="utf-8") as f:
                print(f.read(), end="")
        except Exception as e:
            print(str(e), file=sys.stderr)
            sys.exit(1)
    elif cmd == "write":
        content = " ".join(sys.argv[3:]) if len(sys.argv) > 3 else ""
        try:
            os.makedirs(os.path.dirname(os.path.abspath(path)) or ".", exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception as e:
            print(str(e), file=sys.stderr)
            sys.exit(1)
    else:
        print("用法: file_tool.py read <路径>  |  file_tool.py write <路径> [内容]", file=sys.stderr)
        sys.exit(1)
    return 0

if __name__ == "__main__":
    sys.exit(main())
