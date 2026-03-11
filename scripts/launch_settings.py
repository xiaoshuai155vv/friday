#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""打开 Windows 设置。用法: python launch_settings.py [设置页，如 display、notifications]"""
import sys
import subprocess
import os

def main():
    page = sys.argv[1] if len(sys.argv) > 1 else ""
    uri = "ms-settings:"
    if page == "display" or page == "显示":
        uri = "ms-settings:display"
    elif page == "notifications" or page == "通知":
        uri = "ms-settings:notifications"
    elif page:
        uri = "ms-settings:" + page
    try:
        subprocess.Popen("start " + uri, shell=True)
    except Exception:
        try:
            os.startfile(uri)
        except Exception:
            subprocess.run(
                ["cmd", "/c", "start", uri],
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, "CREATE_NO_WINDOW") else 0,
            )
    print("OK")

if __name__ == "__main__":
    main()
