#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""输出本机网络信息（只读）。用法: network_tool.py [ipconfig|brief|wlan|interfaces]"""
import sys
import subprocess

def main():
    mode = (sys.argv[1] if len(sys.argv) > 1 else "brief").lower()
    if sys.platform != "win32":
        print("Windows only", file=sys.stderr)
        sys.exit(1)
    try:
        if mode == "ipconfig" or mode == "all":
            r = subprocess.run(["ipconfig", "/all"], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=10)
            print(r.stdout or r.stderr or "")
        elif mode == "wlan":
            r = subprocess.run(["netsh", "wlan", "show", "interfaces"], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=10)
            print(r.stdout or r.stderr or "")
        elif mode == "interfaces":
            r = subprocess.run(["netsh", "interface", "show", "interface"], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=10)
            print(r.stdout or r.stderr or "")
        else:
            r = subprocess.run(["ipconfig"], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=5)
            print(r.stdout or r.stderr or "")
    except Exception as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
    return 0

if __name__ == "__main__":
    sys.exit(main())
