#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""进程列表/结束（Windows）。用法: process_tool.py list  |  process_tool.py kill <进程名或 PID>"""
import sys
import subprocess
import os


def _ensure_utf8_stdout():
    """避免打印含 Unicode 字符时在 GBK 控制台报错（如 process list 中的进程名）。"""
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8")
            except (OSError, AttributeError):
                pass


def _safe_print(s, stream=sys.stdout):
    """在 GBK 控制台下安全输出含 Unicode 的字符串（如 tasklist 中的进程名）。"""
    if not s:
        return
    try:
        print(s, file=stream)
    except UnicodeEncodeError:
        try:
            buf = stream.buffer if hasattr(stream, "buffer") else sys.stdout.buffer
            buf.write(s.encode("utf-8", errors="replace") + b"\n")
            buf.flush()
        except (AttributeError, OSError):
            pass


def main():
    _ensure_utf8_stdout()
    if sys.platform != "win32":
        print("Windows only", file=sys.stderr)
        sys.exit(1)
    if len(sys.argv) < 2:
        print("usage: process_tool.py list  |  process_tool.py kill <进程名或PID>", file=sys.stderr)
        sys.exit(1)
    cmd = sys.argv[1].lower()
    if cmd == "list":
        try:
            r = subprocess.run(["tasklist"], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=15)
            out = (r.stdout or r.stderr or "").strip()
            if out:
                _safe_print(out)
        except Exception as e:
            print(str(e), file=sys.stderr)
            sys.exit(1)
    elif cmd == "kill" and len(sys.argv) >= 3:
        target = sys.argv[2]
        try:
            if target.isdigit():
                r = subprocess.run(["taskkill", "/F", "/PID", target], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=10)
            else:
                r = subprocess.run(["taskkill", "/F", "/IM", target], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=10)
            if r.returncode != 0:
                print(r.stderr or r.stdout or "taskkill failed", file=sys.stderr)
                sys.exit(1)
        except Exception as e:
            print(str(e), file=sys.stderr)
            sys.exit(1)
    else:
        print("usage: process_tool.py list  |  process_tool.py kill <进程名或PID>", file=sys.stderr)
        sys.exit(1)
    return 0

if __name__ == "__main__":
    sys.exit(main())
