#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自包含键盘工具（Windows ctypes）。key <vk> 单键按下并释放；keys <vk1> [vk2...] 组合键。
VK 为十进制虚拟键码，如 13=Enter 27=Esc 112=F1。type "text" 为输入字符串（ASCII/常见键）。
"""
import sys
if sys.platform != "win32":
    sys.exit(1)
import ctypes
u = ctypes.windll.user32
KEYEVENTF_KEYUP = 0x0002

# 常用字符到 VK 的映射（仅部分，可扩展）
CH_TO_VK = {}
for c in "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ":
    CH_TO_VK[c] = ord(c.upper())
for c, vk in [(" ", 0x20), ("\n", 0x0D), ("\t", 0x09), ("-", 0xBD), ("=", 0xBB), (".", 0xBE), (",", 0xBC), ("/", 0xBF), (";", 0xBA), ("'", 0xDE), ("[", 0xDB), ("]", 0xDD), ("\\", 0xDC), ("`", 0xC0)]:
    CH_TO_VK[c] = vk

def key_down(vk): u.keybd_event(vk, 0, 0, 0)
def key_up(vk):   u.keybd_event(vk, 0, KEYEVENTF_KEYUP, 0)
def tap(vk): key_down(vk); key_up(vk)

def main():
    if len(sys.argv) < 2:
        print("usage: key <vk>  |  keys <vk1> [vk2 ...]  |  type \"text\"", file=sys.stderr)
        sys.exit(1)
    cmd = sys.argv[1].lower()
    if cmd == "type" and len(sys.argv) >= 3:
        text = sys.argv[2]
        for c in text:
            vk = CH_TO_VK.get(c)
            if vk is not None:
                tap(vk)
            else:
                tap(0x20)  # fallback space
    elif cmd == "key" and len(sys.argv) >= 3:
        tap(int(sys.argv[2]))
    elif cmd == "keys" and len(sys.argv) >= 3:
        vks = [int(x, 0) for x in sys.argv[2:]]  # 0 allows 0x13
        for vk in vks:
            key_down(vk)
        for vk in reversed(vks):
            key_up(vk)
    else:
        print("usage: key <vk>  |  keys <vk1> [vk2 ...]  |  type \"text\"", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
