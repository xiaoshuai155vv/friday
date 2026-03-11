#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows 10+ Toast 通知。show "标题" "正文" 或 show "正文"（无标题）。
依赖系统 Toast，无额外 pip 包；若失败可尝试 pip install win10toast。
"""
import sys
import subprocess
import os

def show_toast_powershell(title, body):
    """通过 PowerShell 调用 WinRT Toast（Win10+）。正文通过参数传入。"""
    text = body or title or "FRIDAY"
    ps = (
        "& { $msg=$args[0]; "
        "$t=[Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText01); "
        "$t.GetElementsByTagName('text').Item(0).AppendChild($t.CreateTextNode($msg))|Out-Null; "
        "[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier('FRIDAY').Show([Windows.UI.Notifications.ToastNotification]::new($t)) }"
    )
    try:
        r = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps, text],
            capture_output=True, text=True, timeout=8
        )
        return r.returncode == 0
    except Exception:
        return False

def main():
    if len(sys.argv) < 2 or sys.argv[1].lower() != "show":
        print('usage: notification_tool.py show "正文"  |  show "标题" "正文"', file=sys.stderr)
        sys.exit(1)
    if len(sys.argv) >= 4:
        title = sys.argv[2]
        body = " ".join(sys.argv[3:])
    elif len(sys.argv) >= 3:
        title = ""
        body = " ".join(sys.argv[2:])
    else:
        body = "FRIDAY"
        title = ""
    if sys.platform != "win32":
        print("Windows only", file=sys.stderr)
        sys.exit(1)
    try:
        if show_toast_powershell(title, body):
            return 0
    except Exception:
        pass
    # 回退：仅打印，便于调试
    print("Toast may require Win10+ or run: pip install win10toast", file=sys.stderr)
    sys.exit(1)

if __name__ == "__main__":
    sys.exit(main())
