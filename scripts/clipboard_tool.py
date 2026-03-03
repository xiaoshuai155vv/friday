#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自包含剪贴板工具（Windows ctypes）。get/set 文本；image_get <路径> 将剪贴板图片存为 BMP；image_set <路径> 从 BMP 文件写入剪贴板。
"""
import sys
import os
if sys.platform != "win32":
    sys.exit(1)
import ctypes
from ctypes import wintypes

u = ctypes.windll.user32
k = ctypes.windll.kernel32
CF_UNICODETEXT = 13
CF_DIB = 8
GMEM_MOVEABLE = 0x0002

def get_clipboard_text():
    if not u.OpenClipboard(None):
        return None
    try:
        h = u.GetClipboardData(CF_UNICODETEXT)
        if not h:
            return None
        p = k.GlobalLock(h)
        if not p:
            return None
        try:
            n = 0
            while (ctypes.c_ushort * 1).from_address(p + n * 2)[0]:
                n += 1
            if n == 0:
                return ""
            buf = (ctypes.c_ushort * (n + 1)).from_address(p)
            return "".join(chr(buf[i]) for i in range(n))
        finally:
            k.GlobalUnlock(h)
    finally:
        u.CloseClipboard()

def set_clipboard_text(text):
    if not isinstance(text, str):
        text = str(text)
    if not u.OpenClipboard(None):
        return False
    u.EmptyClipboard()
    try:
        nul = "\u0000"
        data = (text + nul).encode("utf-16-le")
        n = len(data)
        h = k.GlobalAlloc(GMEM_MOVEABLE, n)
        if not h:
            return False
        p = k.GlobalLock(h)
        if not p:
            k.GlobalFree(h)
            return False
        ctypes.memmove(p, data, n)
        k.GlobalUnlock(h)
        u.SetClipboardData(CF_UNICODETEXT, h)
        return True
    finally:
        u.CloseClipboard()

def image_get(path):
    """将剪贴板中的图片（CF_DIB）保存为 BMP 文件。返回是否成功。"""
    if not u.OpenClipboard(None):
        return False
    try:
        h = u.GetClipboardData(CF_DIB)
        if not h:
            return False
        p = k.GlobalLock(h)
        if not p:
            return False
        try:
            dib_size = k.GlobalSize(h)
            # BITMAPINFOHEADER at p: biBitCount at offset 12
            bi_bit_count = ctypes.c_uint16.from_address(p + 12).value if dib_size >= 14 else 24
            color_entries = 0 if bi_bit_count > 8 else (2 ** bi_bit_count)
            color_table_size = color_entries * 4
            off_bits = 14 + 40 + color_table_size
            file_size = 14 + dib_size
            with open(path, "wb") as f:
                # BITMAPFILEHEADER
                f.write(b"BM")
                f.write(ctypes.c_uint32(file_size).value.to_bytes(4, "little"))
                f.write(ctypes.c_uint16(0).value.to_bytes(2, "little"))
                f.write(ctypes.c_uint16(0).value.to_bytes(2, "little"))
                f.write(ctypes.c_uint32(off_bits).value.to_bytes(4, "little"))
                f.write(ctypes.string_at(p, dib_size))
            return True
        finally:
            k.GlobalUnlock(h)
    finally:
        u.CloseClipboard()

def image_set(path):
    """将 BMP 文件内容（去掉 14 字节文件头）以 CF_DIB 形式写入剪贴板。返回是否成功。"""
    if not os.path.isfile(path):
        return False
    with open(path, "rb") as f:
        raw = f.read()
    if len(raw) < 14 + 4 or raw[:2] != b"BM":
        return False
    dib = raw[14:]
    n = len(dib)
    h = k.GlobalAlloc(GMEM_MOVEABLE, n)
    if not h:
        return False
    p = k.GlobalLock(h)
    if not p:
        k.GlobalFree(h)
        return False
    ctypes.memmove(p, dib, n)
    k.GlobalUnlock(h)
    if not u.OpenClipboard(None):
        k.GlobalFree(h)
        return False
    u.EmptyClipboard()
    try:
        u.SetClipboardData(CF_DIB, h)
        return True
    except Exception:
        k.GlobalFree(h)
        return False
    finally:
        u.CloseClipboard()

def main():
    if len(sys.argv) < 2:
        print("usage: get | set \"text\" | image_get <path> | image_set <path>", file=sys.stderr)
        sys.exit(1)
    cmd = sys.argv[1].lower()
    if cmd == "get":
        t = get_clipboard_text()
        if t is not None:
            print(t)
        else:
            print("", end="")
    elif cmd == "set" and len(sys.argv) >= 3:
        text = sys.argv[2]
        if not set_clipboard_text(text):
            print("SetClipboardData failed", file=sys.stderr)
            sys.exit(1)
    elif cmd == "image_get" and len(sys.argv) >= 3:
        if not image_get(sys.argv[2]):
            print("image_get failed", file=sys.stderr)
            sys.exit(1)
    elif cmd == "image_set" and len(sys.argv) >= 3:
        if not image_set(sys.argv[2]):
            print("image_set failed", file=sys.stderr)
            sys.exit(1)
    else:
        print("usage: get | set \"text\" | image_get <path> | image_set <path>", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
