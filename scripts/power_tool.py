#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
电源/睡眠控制（Windows）。
prevent_sleep [秒数]：在指定秒数内阻止系统休眠与关闭显示器；0 表示持续直到进程结束。
sleep：进入睡眠；hibernate：进入休眠。
shutdown [秒]：关机，默认立即；reboot [秒]：重启，默认立即。使用 shutdown.exe。
"""
import sys
import time
import subprocess
if sys.platform != "win32":
    sys.exit(1)
import ctypes

k = ctypes.windll.kernel32
ES_CONTINUOUS = 0x80000000
ES_SYSTEM_REQUIRED = 0x00000001
ES_DISPLAY_REQUIRED = 0x00000002

def prevent_sleep(seconds=0):
    k.SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED)
    if seconds > 0:
        try:
            time.sleep(seconds)
        finally:
            k.SetThreadExecutionState(ES_CONTINUOUS)
    else:
        try:
            while True:
                time.sleep(3600)
        except KeyboardInterrupt:
            k.SetThreadExecutionState(ES_CONTINUOUS)

def do_sleep():
    """进入睡眠（挂起）。"""
    return ctypes.windll.powrprof.SetSuspendState(0, 1, 0) != 0

def do_hibernate():
    """进入休眠。"""
    return ctypes.windll.powrprof.SetSuspendState(1, 1, 0) != 0

def do_shutdown(delay_sec=0):
    """关机。delay_sec 后执行。"""
    subprocess.run(["shutdown", "/s", "/t", str(int(delay_sec))], check=False)

def do_reboot(delay_sec=0):
    """重启。delay_sec 后执行。"""
    subprocess.run(["shutdown", "/r", "/t", str(int(delay_sec))], check=False)

def main():
    if len(sys.argv) < 2:
        print("usage: power_tool.py prevent_sleep [seconds] | sleep | hibernate | shutdown [sec] | reboot [sec]", file=sys.stderr)
        sys.exit(1)
    cmd = sys.argv[1].lower()
    if cmd == "prevent_sleep":
        sec = 0
        if len(sys.argv) >= 3:
            try:
                sec = float(sys.argv[2])
            except ValueError:
                pass
        prevent_sleep(sec)
        return 0
    if cmd == "sleep":
        if not do_sleep():
            print("SetSuspendState(sleep) failed", file=sys.stderr)
            sys.exit(1)
        return 0
    if cmd == "hibernate":
        if not do_hibernate():
            print("SetSuspendState(hibernate) failed", file=sys.stderr)
            sys.exit(1)
        return 0
    if cmd == "shutdown":
        delay = 0
        if len(sys.argv) >= 3:
            try:
                delay = max(0, int(float(sys.argv[2])))
            except ValueError:
                pass
        do_shutdown(delay)
        return 0
    if cmd == "reboot":
        delay = 0
        if len(sys.argv) >= 3:
            try:
                delay = max(0, int(float(sys.argv[2])))
            except ValueError:
                pass
        do_reboot(delay)
        return 0
    print("usage: power_tool.py prevent_sleep [seconds] | sleep | hibernate | shutdown [sec] | reboot [sec]", file=sys.stderr)
    sys.exit(1)

if __name__ == "__main__":
    sys.exit(main())
