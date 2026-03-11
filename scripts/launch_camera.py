#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
打开系统默认摄像头应用（Windows）。

优先级：1) 环境变量 CAMERA_APP_PATH 或 FRIDAY_CAMERA_EXE 指定的 exe；2) explorer shell:AppsFolder 启动 UWP 相机；3) **PyQt5 直接打开摄像头**（camera_qt.py，项目已集成 Qt，无白框）；4) microsoft.windows.camera: 协议（未安装系统相机时会弹白框）。

若本机未安装 Windows 相机且商店不可用，会优先用 Qt 摄像头窗口；若需指定第三方 exe 可设置 CAMERA_APP_PATH。
用法: python launch_camera.py
"""
import sys
import subprocess
import os
import time

def main():
    if sys.platform != "win32":
        print("Windows only", file=sys.stderr)
        sys.exit(1)
    flags = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
    # 0) 若用户已配置第三方相机 exe
    camera_exe = os.environ.get("CAMERA_APP_PATH") or os.environ.get("FRIDAY_CAMERA_EXE")
    if camera_exe and os.path.isfile(camera_exe):
        try:
            subprocess.Popen([camera_exe], creationflags=flags)
            print("OK")
            return
        except Exception:
            pass
    # 1) 优先用 PyQt5 直接打开摄像头（本机无 Windows 相机时 explorer 会“成功”但不出窗口，故 Qt 放前面）
    close_after = 0
    if "--close-after" in sys.argv:
        try:
            i = sys.argv.index("--close-after")
            if i + 1 < len(sys.argv):
                close_after = float(sys.argv[i + 1])
        except (ValueError, IndexError):
            pass
    camera_qt = os.path.join(os.path.dirname(__file__), "camera_qt.py")
    if os.path.isfile(camera_qt):
        try:
            # 用 pythonw 启动 GUI，避免控制台干扰；无 pythonw 则用 python
            py_dir = os.path.dirname(sys.executable)
            pythonw = os.path.join(py_dir, "pythonw.exe")
            interp = pythonw if os.path.isfile(pythonw) else sys.executable
            cmd = [interp, camera_qt]
            if close_after > 0:
                cmd.extend(["--close-after", str(close_after)])
            p = subprocess.Popen(
                cmd,
                cwd=os.path.dirname(os.path.dirname(camera_qt)),
                creationflags=0,
                env={**os.environ, "PYTHONIOENCODING": "utf-8"},
            )
            time.sleep(2.0)
            if p.poll() is None:
                print("OK")
                return
            # camera_qt 已退出，打印 stderr 便于排查（若之前有 capture）
        except Exception:
            pass
    # 2) explorer shell:AppsFolder 启动 Windows 相机 UWP
    aumids = [
        "Microsoft.WindowsCamera_8wekyb3d8bbwe!App",
        "Microsoft.WindowsCamera_8wekyb3d8bbwe!Microsoft.WindowsCamera",
    ]
    for aumid in aumids:
        try:
            subprocess.Popen(
                ["explorer.exe", "shell:AppsFolder\\" + aumid],
                creationflags=flags,
            )
            print("OK")
            return
        except (FileNotFoundError, OSError, Exception):
            continue
    # 3) 最后回退：protocol（未安装系统相机时会弹白框）
    try:
        subprocess.Popen("start microsoft.windows.camera:", shell=True, creationflags=flags)
    except Exception:
        try:
            os.startfile("microsoft.windows.camera:")
        except Exception:
            subprocess.run(["cmd", "/c", "start", "microsoft.windows.camera:"], creationflags=flags)
    print("OK")

if __name__ == "__main__":
    main()
