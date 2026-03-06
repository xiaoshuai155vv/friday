#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自包含键盘工具（Windows ctypes）。
- key <vk>：单键；keys <vk1> [vk2...]：组合键（VK 十进制，如 17 75 = Ctrl+K）。
- shortcut <组合名>：常用组合，如 shortcut ctrl+k、shortcut ctrl+c、shortcut ctrl+v（Ctrl=17, Alt=18, Shift=16, Win=91；字母 K=75, C=67, V=86 等）。
- type "text"：输入字符串，支持 ASCII 与中文/Unicode（非 ASCII 用 SendInput KEYEVENTF_UNICODE）。
"""
import sys
if sys.platform != "win32":
    sys.exit(1)
import ctypes
from ctypes import wintypes
u = ctypes.windll.user32
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_UNICODE = 0x0004

# 常用组合键名 -> [vk1, vk2, ...]（小写，如 "ctrl+k"）
SHORTCUT_VKS = {
    "ctrl+k": [0x11, 0x4B], "ctrl+c": [0x11, 0x43], "ctrl+v": [0x11, 0x56], "ctrl+a": [0x11, 0x41],
    "ctrl+x": [0x11, 0x58], "ctrl+z": [0x11, 0x5A], "ctrl+s": [0x11, 0x53], "ctrl+f": [0x11, 0x46],
    "alt+tab": [0x12, 0x09], "alt+f4": [0x12, 0x73], "enter": [0x0D], "esc": [0x1B],
}

# 常用字符到 VK 的映射（仅部分，可扩展）
CH_TO_VK = {}
for c in "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ":
    CH_TO_VK[c] = ord(c.upper())
for c, vk in [(" ", 0x20), ("\n", 0x0D), ("\t", 0x09), ("-", 0xBD), ("=", 0xBB), (".", 0xBE), (",", 0xBC), ("/", 0xBF), (";", 0xBA), ("'", 0xDE), ("[", 0xDB), ("]", 0xDD), ("\\", 0xDC), ("`", 0xC0)]:
    CH_TO_VK[c] = vk

# SendInput 用于 Unicode 输入（中文等）
ULONG_PTR = ctypes.c_size_t

class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]

class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", wintypes.LONG), ("dy", wintypes.LONG), ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD), ("time", wintypes.DWORD), ("dwExtraInfo", ULONG_PTR),
    ]

class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [
        ("uMsg", wintypes.DWORD), ("wParamL", wintypes.WORD), ("wParamH", wintypes.WORD),
    ]

class INPUT_UNION(ctypes.Union):
    _fields_ = [("mi", MOUSEINPUT), ("ki", KEYBDINPUT), ("hi", HARDWAREINPUT)]

class INPUT(ctypes.Structure):
    _fields_ = [("type", wintypes.DWORD), ("union", INPUT_UNION)]

INPUT_KEYBOARD = 1
u.SendInput.argtypes = [wintypes.UINT, ctypes.POINTER(INPUT), ctypes.c_int]
u.SendInput.restype = wintypes.UINT

def send_unicode_char(code: int) -> None:
    """Send one Unicode code point (BMP or surrogate) via SendInput."""
    inp = INPUT()
    inp.type = INPUT_KEYBOARD
    inp.union.ki.wVk = 0
    inp.union.ki.wScan = code & 0xFFFF
    inp.union.ki.dwFlags = KEYEVENTF_UNICODE
    inp.union.ki.time = 0
    inp.union.ki.dwExtraInfo = 0
    u.SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT))
    inp.union.ki.dwFlags = KEYEVENTF_UNICODE | KEYEVENTF_KEYUP
    u.SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT))

def type_unicode(text: str) -> None:
    """Input string using Unicode events (supports Chinese and any BMP character)."""
    for c in text:
        cp = ord(c)
        if cp <= 0xFFFF:
            send_unicode_char(cp)
        else:
            # Supplementary plane: UTF-16 surrogate pair
            cp -= 0x10000
            high = 0xD800 + (cp >> 10)
            low = 0xDC00 + (cp & 0x3FF)
            send_unicode_char(high)
            send_unicode_char(low)

def key_down(vk): u.keybd_event(vk, 0, 0, 0)
def key_up(vk):   u.keybd_event(vk, 0, KEYEVENTF_KEYUP, 0)
def tap(vk): key_down(vk); key_up(vk)

def main():
    if len(sys.argv) < 2:
        print("usage: key <vk>  |  keys <vk1> [vk2...]  |  shortcut <组合>  |  type \"text\" (ASCII+中文)", file=sys.stderr)
        sys.exit(1)
    cmd = sys.argv[1].lower()
    if cmd == "type" and len(sys.argv) >= 3:
        text = sys.argv[2]
        for c in text:
            vk = CH_TO_VK.get(c)
            if vk is not None:
                tap(vk)
            else:
                type_unicode(c)
    elif cmd == "shortcut" and len(sys.argv) >= 3:
        name = sys.argv[2].lower().replace(" ", "").replace("-", "+")
        vks = SHORTCUT_VKS.get(name)
        if not vks:
            print("unknown shortcut: %s (e.g. ctrl+k, ctrl+c, ctrl+v, alt+tab)", file=sys.stderr)
            sys.exit(1)
        for vk in vks:
            key_down(vk)
        for vk in reversed(vks):
            key_up(vk)
    elif cmd == "key" and len(sys.argv) >= 3:
        tap(int(sys.argv[2]))
    elif cmd == "keys" and len(sys.argv) >= 3:
        vks = [int(x, 0) for x in sys.argv[2:]]  # 0 allows 0x13
        for vk in vks:
            key_down(vk)
        for vk in reversed(vks):
            key_up(vk)
    else:
        print("usage: key <vk>  |  keys <vk1> [vk2...]  |  shortcut ctrl+k  |  type \"text\" (支持中文)", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
