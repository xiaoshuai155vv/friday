#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用 PyQt5 直接打开摄像头并显示预览窗口（不依赖系统相机应用）。
依赖: PyQt5（且需 QtMultimedia）。
用法: python camera_qt.py [--close-after N]  （N 秒后自动关闭，用于自拍截图后关窗）
"""
import sys
import os
import argparse

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# 便携 Python 或重装后 Qt 可能找不到 platform 插件，需显式指定路径
if "QT_QPA_PLATFORM_PLUGIN_PATH" not in os.environ:
    try:
        import PyQt5
        _qt_plugins = os.path.join(os.path.dirname(PyQt5.__file__), "Qt5", "plugins", "platforms")
        if os.path.isdir(_qt_plugins):
            os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = os.path.abspath(_qt_plugins)
    except Exception:
        pass


def main():
    try:
        from PyQt5.QtWidgets import QApplication, QMainWindow
        from PyQt5.QtMultimedia import QCamera, QCameraInfo
        from PyQt5.QtMultimediaWidgets import QCameraViewfinder
        from PyQt5.QtCore import Qt, QTimer
    except ImportError as e:
        print("camera_qt 需要 PyQt5 与 QtMultimedia:", e, file=sys.stderr)
        sys.exit(1)
    ap = argparse.ArgumentParser()
    ap.add_argument("--close-after", type=float, default=0, help="N 秒后自动关闭窗口（自拍流程用）")
    args = ap.parse_args()
    app = QApplication(sys.argv)
    cam = None
    info = QCameraInfo.defaultCamera()
    if info and not info.isNull():
        try:
            cam = QCamera(info)
        except Exception:
            cam = None
    if cam is None:
        available = QCameraInfo.availableCameras()
        if available:
            try:
                cam = QCamera(available[0])
            except Exception:
                cam = None
    if cam is None:
        print("未检测到可用摄像头", file=sys.stderr)
        sys.exit(1)
    vf = QCameraViewfinder()
    cam.setViewfinder(vf)
    win = QMainWindow()
    win.setWindowTitle("星期五 · 摄像头")
    win.setCentralWidget(vf)
    win.setMinimumSize(640, 480)
    win.resize(640, 480)
    win.show()
    win.raise_()
    win.activateWindow()
    if sys.platform == "win32":
        try:
            import ctypes
            hwnd = int(win.winId())
            ctypes.windll.user32.SetForegroundWindow(hwnd)
        except Exception:
            pass
    cam.start()
    if args.close_after > 0:
        def close_all():
            try:
                cam.stop()
            except Exception:
                pass
            win.close()
            app.quit()
        QTimer.singleShot(int(args.close_after * 1000), close_all)
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
