#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""统一入口：用户意图 → 执行对应脚本。用法: python do.py <意图> [参数...]"""
import sys
import os

# 诊断：无论 stdout 是否可见，都写文件 + stderr，便于确认是否执行到本脚本
try:
    _here = os.path.dirname(os.path.abspath(__file__))
    _debug_path = os.path.normpath(os.path.join(_here, "..", "vol_debug.txt"))
    with open(_debug_path, "w", encoding="utf-8") as _f:
        _f.write("do.py loaded argv=%r\n" % (sys.argv,))
except Exception:
    pass
try:
    sys.stderr.write("do.py stderr argv=%r\n" % (sys.argv,))
    sys.stderr.flush()
except Exception:
    pass
import subprocess

SCRIPTS = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(SCRIPTS)


def _launch_via_win_r(app_name):
    """Win+R 输入应用名回车，用于启动未在 do 中显式列出的应用。"""
    import time
    kbd = os.path.join(SCRIPTS, "keyboard_tool.py")
    subprocess.run([sys.executable, kbd, "keys", "91", "82"], cwd=PROJECT)  # Win+R
    time.sleep(0.5)
    subprocess.run([sys.executable, kbd, "type", app_name], cwd=PROJECT)
    time.sleep(0.3)
    subprocess.run([sys.executable, kbd, "key", "13"], cwd=PROJECT)  # Enter


def main():
    if len(sys.argv) < 2:
        print("用法: do.py 自拍|打开摄像头|截图|已安装应用|打开网易云音乐|...|剪贴板读|防休眠|...|run <脚本名> [参数...]", file=sys.stderr)
        sys.exit(1)
    intent = sys.argv[1].strip()
    if intent == "自拍":
        interp = os.environ.get("FRIDAY_INVOKER_PYTHON") or sys.executable
        subprocess.run([interp, os.path.join(SCRIPTS, "selfie.py")], cwd=PROJECT)
    elif intent == "打开摄像头":
        interp = os.environ.get("FRIDAY_INVOKER_PYTHON") or sys.executable
        subprocess.run([interp, os.path.join(SCRIPTS, "camera_qt.py")], cwd=PROJECT)
    elif intent in ("截图", "截屏"):
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "screenshot_tool.py")], cwd=PROJECT)
    elif intent == "打开浏览器":
        url = sys.argv[2] if len(sys.argv) > 2 else "https://www.bing.com"
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "launch_browser.py"), url], cwd=PROJECT)
    elif intent == "打开记事本":
        path = sys.argv[2] if len(sys.argv) > 2 else ""
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "launch_notepad.py")] + ([path] if path else []), cwd=PROJECT)
    elif intent == "打开文件管理器":
        path = sys.argv[2] if len(sys.argv) > 2 else ""
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "launch_explorer.py")] + ([path] if path else []), cwd=PROJECT)
    elif intent == "按回车":
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "keyboard_tool.py"), "key", "13"], cwd=PROJECT)
    elif intent in ("复制", "Ctrl+C"):
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "keyboard_tool.py"), "keys", "17", "67"], cwd=PROJECT)
    elif intent in ("粘贴", "Ctrl+V"):
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "keyboard_tool.py"), "keys", "17", "86"], cwd=PROJECT)
    elif intent in ("输入中文", "中文输入", "粘贴中文"):
        # 中文/Unicode：先写入剪贴板再 Ctrl+V 粘贴（避免 keyboard type 仅 ASCII）
        text = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""
        if text:
            subprocess.run([sys.executable, os.path.join(SCRIPTS, "clipboard_tool.py"), "set", text], cwd=PROJECT)
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "keyboard_tool.py"), "keys", "17", "86"], cwd=PROJECT)
    elif intent in ("进程列表", "任务列表"):
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "process_tool.py"), "list"], cwd=PROJECT)
    elif intent in ("结束进程", "kill"):
        name_or_pid = sys.argv[2] if len(sys.argv) > 2 else ""
        if name_or_pid:
            subprocess.run([sys.executable, os.path.join(SCRIPTS, "process_tool.py"), "kill", name_or_pid], cwd=PROJECT)
    elif intent in ("光标位置", "获取光标", "鼠标位置"):
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "mouse_tool.py"), "pos"], cwd=PROJECT)
    elif intent in ("打开闹钟", "闹钟"):
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "launch_clock.py")], cwd=PROJECT)
    elif intent in ("打开日历", "日历"):
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "launch_calendar.py")], cwd=PROJECT)
    elif intent in ("剪贴板读", "读剪贴板"):
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "clipboard_tool.py"), "get"], cwd=PROJECT)
    elif intent in ("剪贴板写", "写剪贴板"):
        text = sys.argv[2] if len(sys.argv) > 2 else ""
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "clipboard_tool.py"), "set", text], cwd=PROJECT)
    elif intent in ("剪贴板图片保存", "剪贴板图保存"):
        path = sys.argv[2] if len(sys.argv) > 2 else os.path.join(PROJECT, "screenshots", "clipboard_image.bmp")
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "clipboard_tool.py"), "image_get", path], cwd=PROJECT)
    elif intent in ("剪贴板图片写入", "剪贴板图写入"):
        path = sys.argv[2] if len(sys.argv) > 2 else ""
        if path:
            subprocess.run([sys.executable, os.path.join(SCRIPTS, "clipboard_tool.py"), "image_set", path], cwd=PROJECT)
    elif intent in ("窗口激活", "激活窗口", "前置窗口"):
        title = sys.argv[2] if len(sys.argv) > 2 else ""
        if title:
            subprocess.run([sys.executable, os.path.join(SCRIPTS, "window_tool.py"), "activate", title], cwd=PROJECT)
    elif intent in ("窗口PID", "按标题查PID"):
        title = sys.argv[2] if len(sys.argv) > 2 else ""
        if title:
            subprocess.run([sys.executable, os.path.join(SCRIPTS, "window_tool.py"), "pid", title], cwd=PROJECT)
    elif intent in ("结束窗口", "关闭窗口"):
        title = sys.argv[2] if len(sys.argv) > 2 else ""
        if title:
            r = subprocess.run([sys.executable, os.path.join(SCRIPTS, "window_tool.py"), "pid", title], cwd=PROJECT, capture_output=True, text=True)
            pid = (r.stdout or "").strip()
            if pid and pid != "0":
                subprocess.run([sys.executable, os.path.join(SCRIPTS, "process_tool.py"), "kill", pid], cwd=PROJECT)
    elif intent in ("睡眠", "进入睡眠", "sleep"):
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "power_tool.py"), "sleep"], cwd=PROJECT)
    elif intent in ("休眠", "进入休眠", "hibernate"):
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "power_tool.py"), "hibernate"], cwd=PROJECT)
    elif intent in ("关机", "关闭电脑", "shutdown"):
        delay = sys.argv[2] if len(sys.argv) > 2 else "0"
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "power_tool.py"), "shutdown", delay], cwd=PROJECT)
    elif intent in ("重启", "重新启动", "reboot"):
        delay = sys.argv[2] if len(sys.argv) > 2 else "0"
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "power_tool.py"), "reboot", delay], cwd=PROJECT)
    elif intent == "防休眠":
        sec = sys.argv[2] if len(sys.argv) > 2 else "0"
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "power_tool.py"), "prevent_sleep", sec], cwd=PROJECT)
    elif intent == "音量静音":
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "keyboard_tool.py"), "key", "173"], cwd=PROJECT)
    elif intent == "音量减":
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "keyboard_tool.py"), "key", "174"], cwd=PROJECT)
    elif intent == "音量增":
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "keyboard_tool.py"), "key", "175"], cwd=PROJECT)
    elif intent in ("打开运行", "运行", "Win+R"):
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "keyboard_tool.py"), "keys", "91", "82"], cwd=PROJECT)
    elif intent in ("打开设置", "设置"):
        page = sys.argv[2] if len(sys.argv) > 2 else ""
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "launch_settings.py")] + ([page] if page else []), cwd=PROJECT)
    elif intent in ("任务管理器", "打开任务管理器"):
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "launch_taskmgr.py")], cwd=PROJECT)
    elif intent in ("计算器", "打开计算器"):
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "launch_calc.py")], cwd=PROJECT)
    elif intent in ("打开网易云音乐", "网易云音乐", "云音乐"):
        _launch_via_win_r("CloudMusic")
    elif intent in ("打开QQ音乐", "QQ音乐"):
        _launch_via_win_r("QQMusic")
    elif intent in ("打开酷狗音乐", "酷狗音乐", "酷狗"):
        _launch_via_win_r("Kugou")
    elif intent in ("打开Spotify", "Spotify"):
        _launch_via_win_r("Spotify")
    elif intent in ("打开应用", "启动应用") and len(sys.argv) > 2:
        _launch_via_win_r(sys.argv[2])  # do.py 打开应用 CloudMusic
    elif intent in ("已安装应用", "应用列表", "列出应用", "installed_apps"):
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "installed_apps_tool.py")] + sys.argv[2:], cwd=PROJECT)
    elif intent in ("网络信息", "ipconfig", "网络"):
        mode = sys.argv[2] if len(sys.argv) > 2 else "brief"
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "network_tool.py"), mode], cwd=PROJECT)
    elif intent in ("WLAN", "无线网络", "WiFi"):
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "network_tool.py"), "wlan"], cwd=PROJECT)
    elif intent in ("网络接口", "网卡列表"):
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "network_tool.py"), "interfaces"], cwd=PROJECT)
    elif intent in ("音量值", "当前音量"):
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "volume_tool.py"), "get"], cwd=PROJECT)
    elif intent in ("音量加", "音量+"):
        n = 1
        if len(sys.argv) > 2:
            try:
                n = max(1, min(50, int(sys.argv[2])))
            except ValueError:
                pass
        try:
            import ctypes
            VK_VOLUME_UP = 0xAF
            KEYEVENTF_KEYUP = 0x0002
            u = ctypes.windll.user32
            for _ in range(n):
                u.keybd_event(VK_VOLUME_UP, 0, 0, 0)
                u.keybd_event(VK_VOLUME_UP, 0, KEYEVENTF_KEYUP, 0)
            sys.stderr.write("音量加 x%s\n" % n)
            sys.stderr.flush()
        except Exception as e:
            sys.stderr.write("err %s\n" % e)
            sys.stderr.flush()
    elif intent in ("音量减", "音量-"):
        n = 1
        if len(sys.argv) > 2:
            try:
                n = max(1, min(50, int(sys.argv[2])))
            except ValueError:
                pass
        try:
            import ctypes
            VK_VOLUME_DOWN = 0xAE
            KEYEVENTF_KEYUP = 0x0002
            u = ctypes.windll.user32
            for _ in range(n):
                u.keybd_event(VK_VOLUME_DOWN, 0, 0, 0)
                u.keybd_event(VK_VOLUME_DOWN, 0, KEYEVENTF_KEYUP, 0)
            sys.stderr.write("音量减 x%s\n" % n)
            sys.stderr.flush()
        except Exception as e:
            sys.stderr.write("err %s\n" % e)
            sys.stderr.flush()
    elif intent in ("设置音量", "音量设置"):
        vol = sys.argv[2] if len(sys.argv) > 2 else ""
        if vol:
            subprocess.run([sys.executable, os.path.join(SCRIPTS, "volume_tool.py"), "set", vol], cwd=PROJECT)
        else:
            sys.stderr.write("用法: do.py 设置音量 <0-100>\n")
            sys.stderr.flush()
    elif intent == "音量值":
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "volume_tool.py"), "get"], cwd=PROJECT)
    elif intent in ("设置亮度", "亮度"):
        # brightness_tool: get | set <0-100>
        if len(sys.argv) > 2 and sys.argv[2].isdigit():
            subprocess.run([sys.executable, os.path.join(SCRIPTS, "brightness_tool.py"), "set", sys.argv[2]], cwd=PROJECT)
        else:
            subprocess.run([sys.executable, os.path.join(SCRIPTS, "brightness_tool.py"), "get"], cwd=PROJECT)
    elif intent in ("亮度", "当前亮度"):
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "brightness_tool.py"), "get"], cwd=PROJECT)
    elif intent in ("设置亮度", "亮度设置"):
        val = sys.argv[2] if len(sys.argv) > 2 else ""
        if val:
            subprocess.run([sys.executable, os.path.join(SCRIPTS, "brightness_tool.py"), "set", val], cwd=PROJECT)
    elif intent in ("通知", "Toast", "弹窗通知"):
        msg = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "FRIDAY"
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "notification_tool.py"), "show", msg], cwd=PROJECT)
    elif intent in ("当前时间", "时间", "time"):
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "time_tool.py")], cwd=PROJECT)
    elif intent in ("主机名", "计算机名", "COMPUTERNAME"):
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "env_tool.py"), "COMPUTERNAME"], cwd=PROJECT)
    elif intent in ("用户名", "USERNAME"):
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "env_tool.py"), "USERNAME"], cwd=PROJECT)
    elif intent in ("列目录", "list_dir", "ls"):
        p = sys.argv[2] if len(sys.argv) > 2 else "."
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "file_tool.py"), "list", p], cwd=PROJECT)
    elif intent in ("读文件", "file_read"):
        p = sys.argv[2] if len(sys.argv) > 2 else ""
        if p:
            subprocess.run([sys.executable, os.path.join(SCRIPTS, "file_tool.py"), "read", p], cwd=PROJECT)
    elif intent in ("写文件", "file_write"):
        p = sys.argv[2] if len(sys.argv) > 2 else ""
        content = " ".join(sys.argv[3:]) if len(sys.argv) > 3 else ""
        if p:
            subprocess.run([sys.executable, os.path.join(SCRIPTS, "file_tool.py"), "write", p, content], cwd=PROJECT)
    elif intent == "run" or intent == "执行":
        if len(sys.argv) < 3:
            print("用法: do.py run <脚本名> [参数...]，如 do.py run screenshot_tool 路径", file=sys.stderr)
            sys.exit(1)
        name = sys.argv[2]
        if not name.endswith(".py"):
            name += ".py"
        path = os.path.join(SCRIPTS, name)
        if not os.path.isfile(path):
            print("脚本不存在:", path, file=sys.stderr)
            sys.exit(1)
        subprocess.run([sys.executable, path] + sys.argv[3:], cwd=PROJECT)
    else:
        print("未知意图:", intent, file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
