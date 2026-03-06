#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通过 PowerShell 设置剪贴板文本（在 ctypes SetClipboardData 失败的环境如远程会话中更易成功）。
用法: python set_clipboard_ps.py "要写入的内容"
"""
import sys
import os
import subprocess
import tempfile

def main():
    if len(sys.argv) < 2:
        print("usage: set_clipboard_ps.py <text>", file=sys.stderr)
        sys.exit(1)
    text = sys.argv[1]
    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as f:
            f.write(text)
            path = f.name
        try:
            # Use -File so $args[0] is the path; path is passed as single argument (handles spaces)
            ps_script = "Set-Clipboard -Value (Get-Content -LiteralPath $args[0] -Encoding UTF8 -Raw)"
            with tempfile.NamedTemporaryFile(mode="w", suffix=".ps1", delete=False, encoding="utf-8") as psf:
                psf.write(ps_script)
                ps_path = psf.name
            try:
                cmd = [
                    "powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", ps_path, path,
                ]
                r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=10)
            finally:
                try:
                    os.unlink(ps_path)
                except OSError:
                    pass
            if r.returncode != 0:
                print(r.stderr or "PowerShell Set-Clipboard failed", file=sys.stderr)
                sys.exit(1)
        finally:
            try:
                os.unlink(path)
            except OSError:
                pass
    except Exception as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
