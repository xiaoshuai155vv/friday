#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自包含全屏截图（Windows GDI），输出 BMP 到指定路径或默认 runtime/screenshots/ 目录。
用法: python screenshot_tool.py [out_path]
"""
import sys
import os
if sys.platform != "win32":
    sys.exit(1)
import ctypes
from ctypes import wintypes

u = ctypes.windll.user32
g = ctypes.windll.gdi32

SRCCOPY = 0x00CC0020
BI_RGB = 0
DIB_RGB_COLORS = 0

def main():
    out = sys.argv[1] if len(sys.argv) >= 2 else None
    if not out:
        base = os.path.join(os.path.dirname(__file__), "..", "runtime", "screenshots")
        os.makedirs(base, exist_ok=True)
        from datetime import datetime
        out = os.path.join(base, f"capture_{datetime.now().strftime('%Y%m%d_%H%M%S')}.bmp")

    w = u.GetSystemMetrics(0)
    h = u.GetSystemMetrics(1)
    hdc_screen = u.GetDC(0)
    hdc_mem = g.CreateCompatibleDC(hdc_screen)
    hbm = g.CreateCompatibleBitmap(hdc_screen, w, h)
    g.SelectObject(hdc_mem, hbm)
    g.BitBlt(hdc_mem, 0, 0, w, h, hdc_screen, 0, 0, SRCCOPY)

    class BITMAPINFOHEADER(ctypes.Structure):
        _fields_ = [
            ("biSize", wintypes.DWORD), ("biWidth", wintypes.LONG), ("biHeight", wintypes.LONG),
            ("biPlanes", wintypes.WORD), ("biBitCount", wintypes.WORD), ("biCompression", wintypes.DWORD),
            ("biSizeImage", wintypes.DWORD), ("biXPelsPerMeter", wintypes.LONG), ("biYPelsPerMeter", wintypes.LONG),
            ("biClrUsed", wintypes.DWORD), ("biClrImportant", wintypes.DWORD),
        ]
    bmi = BITMAPINFOHEADER()
    bmi.biSize = ctypes.sizeof(BITMAPINFOHEADER)
    bmi.biWidth = w
    bmi.biHeight = -h  # top-down
    bmi.biPlanes = 1
    bmi.biBitCount = 24
    bmi.biCompression = BI_RGB

    buf_size = w * h * 3
    buf = (ctypes.c_byte * buf_size)()
    g.GetDIBits(hdc_mem, hbm, 0, h, buf, ctypes.byref(bmi), DIB_RGB_COLORS)

    u.ReleaseDC(0, hdc_screen)
    g.DeleteObject(hbm)
    g.DeleteDC(hdc_mem)

    row = w * 3
    pad = (4 - (row % 4)) % 4
    stride = row + pad
    raw_size = stride * h
    file_size = 14 + 40 + raw_size
    with open(out, "wb") as f:
        f.write(b"BM")
        f.write(file_size.to_bytes(4, "little"))
        f.write((0).to_bytes(4, "little"))
        f.write((54).to_bytes(4, "little"))  # pixel offset
        f.write((40).to_bytes(4, "little"))  # DIB header size
        f.write(w.to_bytes(4, "little"))
        f.write(h.to_bytes(4, "little"))
        f.write((1).to_bytes(2, "little"))
        f.write((24).to_bytes(2, "little"))
        f.write((0).to_bytes(4, "little"))
        f.write((raw_size).to_bytes(4, "little"))
        f.write((0).to_bytes(4, "little") * 4)
        mv = memoryview(buf)
        for y in range(h - 1, -1, -1):
            f.write(mv[y * row : (y + 1) * row].tobytes())
            f.write(b"\x00" * pad)
    print(out)

if __name__ == "__main__":
    main()
