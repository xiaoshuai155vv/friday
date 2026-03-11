#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""输出环境/主机信息（只读）。用法: env_tool.py [COMPUTERNAME|USERNAME|all|EXPAND <路径>]"""
import sys
import os

def main():
    key = (sys.argv[1] if len(sys.argv) > 1 else "all").upper()
    if key == "EXPAND":
        if len(sys.argv) < 3:
            print("usage: env_tool.py EXPAND <含%VAR%的路径>", file=sys.stderr)
            sys.exit(1)
    if sys.platform != "win32":
        if key == "ALL":
            for k, v in sorted(os.environ.items()):
                print(k, "=", v)
        else:
            print(os.environ.get(key, ""))
        return 0
    env = os.environ
    if key == "COMPUTERNAME":
        print(env.get("COMPUTERNAME", ""))
    elif key == "USERNAME":
        print(env.get("USERNAME", ""))
    elif key == "ALL":
        for k in ["COMPUTERNAME", "USERNAME", "USERPROFILE", "APPDATA", "TEMP", "TMP"]:
            print(k, "=", env.get(k, ""))
    elif key == "EXPAND" and len(sys.argv) > 2:
        path = sys.argv[2]
        for k, v in env.items():
            path = path.replace("%" + k + "%", v).replace("%" + k.lower() + "%", v)
        print(path)
    else:
        print(env.get(key, ""))
    return 0

if __name__ == "__main__":
    sys.exit(main())
