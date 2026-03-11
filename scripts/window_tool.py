#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
窗口前后台（Windows ctypes）。
- activate <标题>：按窗口标题匹配并置前；pid <标题>：输出该标题对应窗口的进程 PID。
- activate_process <进程名>：按进程列表中的进程名找 PID，再激活该进程的主窗口。
- activate_pid <PID>：激活指定 PID 的进程所属的第一个可见窗口。
- maximize <标题>：按窗口标题查找并最大化该窗口（ShowWindow SW_MAXIMIZE），便于后续截图/多模态时避免背景干扰。
- maximize_process <进程名>：按进程名找到主窗口并最大化。
用法: window_tool.py activate "记事本"  |  window_tool.py activate_process ihaier  |  window_tool.py maximize "办公平台"
"""
import sys
import subprocess
import re
if sys.platform != "win32":
    sys.exit(1)
import ctypes
from ctypes import wintypes

u = ctypes.windll.user32
WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

# 找到的窗口句柄与搜索串（回调用）
_found_hwnd = None
_search_title = ""
_search_pid = None

def _enum_callback(hwnd, lparam):
    global _found_hwnd
    length = u.GetWindowTextLengthW(hwnd) + 1
    if length <= 1:
        return True
    buf = ctypes.create_unicode_buffer(length)
    u.GetWindowTextW(hwnd, buf, length)
    title = buf.value or ""
    if _search_title and _search_title in title.lower():
        _found_hwnd = hwnd
        return False  # 停止枚举
    return True

def _enum_callback_by_pid(hwnd, lparam):
    global _found_hwnd, _search_pid
    if not u.IsWindowVisible(hwnd):
        return True
    pid = get_window_process_id(hwnd)
    if pid == _search_pid:
        _found_hwnd = hwnd
        return False
    return True

def find_hwnd_by_title(partial_title):
    """按部分标题查找第一个匹配窗口的 HWND，未找到返回 None。"""
    global _found_hwnd, _search_title
    _found_hwnd = None
    _search_title = (partial_title or "").strip().lower()
    if not _search_title:
        return None
    u.EnumWindows.argtypes = [WNDENUMPROC, wintypes.LPARAM]
    u.EnumWindows(WNDENUMPROC(_enum_callback), 0)
    return _found_hwnd

def find_hwnd_by_pid(pid):
    """按进程 PID 查找该进程下第一个可见窗口的 HWND，未找到返回 None。"""
    global _found_hwnd, _search_pid
    _found_hwnd = None
    _search_pid = int(pid) if pid is not None else 0
    if _search_pid <= 0:
        return None
    u.EnumWindows.argtypes = [WNDENUMPROC, wintypes.LPARAM]
    u.EnumWindows(WNDENUMPROC(_enum_callback_by_pid), 0)
    return _found_hwnd

def get_window_process_id(hwnd):
    """返回窗口所属进程 PID。"""
    pid = wintypes.DWORD()
    u.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    return pid.value

def get_pids_by_process_name(partial_name):
    """通过 tasklist 按进程名（如 ihaier、iHaier2.0）匹配，返回 PID 列表。匹配忽略大小写（包含/前缀）。"""
    name = (partial_name or "").strip().lower()
    if not name:
        return []
    try:
        r = subprocess.run(
            ["tasklist", "/FO", "CSV", "/NH"],
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=15
        )
        out = (r.stdout or "").strip()
    except Exception:
        return []
    pids = []
    for line in out.splitlines():
        # CSV: "Image Name","PID","Session Name",...；进程名统一转小写后包含/前缀匹配
        parts = re.findall(r'"([^"]*)"', line)
        if len(parts) >= 2:
            image_name = (parts[0] or "").strip().lower()
            if name in image_name or image_name.startswith(name):
                try:
                    pids.append(int(parts[1].replace(",", "").strip()))
                except ValueError:
                    pass
    return pids

SW_MAXIMIZE = 3
SW_RESTORE = 9

def activate_by_title(partial_title):
    """将标题包含 partial_title 的窗口激活到前台。返回是否成功。"""
    hwnd = find_hwnd_by_title(partial_title)
    if hwnd is None:
        return False
    if u.IsIconic(hwnd):
        u.ShowWindow(hwnd, SW_RESTORE)
    if u.SetForegroundWindow(hwnd) != 0:
        return True
    return _set_foreground_with_attach(hwnd)


def maximize_by_title(partial_title):
    """将标题包含 partial_title 的窗口最大化。返回是否成功。"""
    hwnd = find_hwnd_by_title(partial_title)
    if hwnd is None:
        return False
    if u.IsIconic(hwnd):
        u.ShowWindow(hwnd, SW_RESTORE)
    u.ShowWindow(hwnd, SW_MAXIMIZE)
    return True


def maximize_by_process(partial_name):
    """按进程名找到主窗口并最大化。优先标题含「办公平台」的窗口。"""
    hwnd = find_hwnd_by_title(partial_name)
    if hwnd is not None:
        if u.IsIconic(hwnd):
            u.ShowWindow(hwnd, SW_RESTORE)
        u.ShowWindow(hwnd, SW_MAXIMIZE)
        return True
    pids = get_pids_by_process_name(partial_name)
    if not pids:
        return False
    candidates = _collect_visible_windows_by_pids(pids)
    candidates.sort(key=lambda item: (0 if "办公平台" in (item[1] or "") else (1 if "办公" in (item[1] or "") else 2), item[1] or ""))
    for hwnd, _ in candidates:
        if u.IsIconic(hwnd):
            u.ShowWindow(hwnd, SW_RESTORE)
        u.ShowWindow(hwnd, SW_MAXIMIZE)
        return True
    return False

def _collect_visible_windows_by_pids(pids):
    """收集多个 PID 下所有可见窗口的 (hwnd, title)。用于多进程应用（如 iHaier）优先激活主窗口。"""
    result = []
    pids_set = set(int(x) for x in pids if x is not None and int(x) > 0)

    def _enum(hwnd, lparam):
        if not u.IsWindowVisible(hwnd):
            return True
        pid = get_window_process_id(hwnd)
        if pid not in pids_set:
            return True
        length = u.GetWindowTextLengthW(hwnd) + 1
        if length <= 1:
            result.append((hwnd, ""))
            return True
        buf = ctypes.create_unicode_buffer(length)
        u.GetWindowTextW(hwnd, buf, length)
        result.append((hwnd, (buf.value or "").strip()))
        return True

    u.EnumWindows(WNDENUMPROC(_enum), 0)
    return result


def _set_foreground_with_attach(hwnd):
    """尝试 AttachThreadInput + BringWindowToTop + SetForegroundWindow，提高 Electron 等窗口激活成功率。"""
    if u.SetForegroundWindow(hwnd) != 0:
        return True
    kernel32 = ctypes.windll.kernel32
    cur_thread = kernel32.GetCurrentThreadId()
    fore_hwnd = u.GetForegroundWindow()
    if fore_hwnd and fore_hwnd != hwnd:
        fore_thread = u.GetWindowThreadProcessId(fore_hwnd, None)
        if u.AttachThreadInput(cur_thread, fore_thread, True):
            u.BringWindowToTop(hwnd)
            u.ShowWindow(hwnd, 9)
            u.SetForegroundWindow(hwnd)
            u.AttachThreadInput(cur_thread, fore_thread, False)
            return u.GetForegroundWindow() == hwnd
    return False


def activate_by_pid(pid):
    """将指定 PID 的进程所属的第一个可见窗口激活到前台。返回是否成功。"""
    hwnd = find_hwnd_by_pid(pid)
    if hwnd is None:
        return False
    if u.IsIconic(hwnd):
        u.ShowWindow(hwnd, 9)  # SW_RESTORE
    if u.SetForegroundWindow(hwnd) != 0:
        return True
    return _set_foreground_with_attach(hwnd)


def activate_by_process(partial_name):
    """按进程名在进程列表中查找 PID，再激活该进程的窗口。先标题再进程名；多进程时优先激活标题含「办公平台」的主窗口。"""
    if activate_by_title(partial_name):
        return True
    pids = get_pids_by_process_name(partial_name)
    if not pids:
        return False
    # 多进程应用（如 iHaier2.0 有多个进程）：收集所有可见窗口，优先标题含「办公平台」或「办公」的主窗口
    candidates = _collect_visible_windows_by_pids(pids)
    # 优先：标题含「办公平台」> 含「办公」> 其他非空标题 > 空标题
    def _key(item):
        hwnd, title = item
        if "办公平台" in title:
            return (0, title)
        if "办公" in title:
            return (1, title)
        if title:
            return (2, title)
        return (3, title)

    candidates.sort(key=_key)
    for hwnd, title in candidates:
        if u.IsIconic(hwnd):
            u.ShowWindow(hwnd, SW_RESTORE)
        if u.SetForegroundWindow(hwnd) != 0:
            return True
        if _set_foreground_with_attach(hwnd):
            return True
    return False


def _ensure_utf8_stdout():
    """避免打印时在 GBK 控制台报 UnicodeEncodeError（如含中文的 usage）。"""
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8")
            except (OSError, AttributeError):
                pass


def main():
    _ensure_utf8_stdout()
    if len(sys.argv) < 3:
        print('usage: window_tool.py activate "标题"  |  activate_process <进程名>  |  maximize "标题"  |  maximize_process <进程名>  |  pid "标题"', file=sys.stderr)
        sys.exit(1)
    cmd = sys.argv[1].lower()
    arg = sys.argv[2]
    if cmd == "maximize":
        if maximize_by_title(arg):
            print("OK")
        else:
            print("No matching window for maximize", file=sys.stderr)
            sys.exit(1)
    elif cmd == "maximize_process":
        if maximize_by_process(arg):
            print("OK")
        else:
            print("No matching process/window for maximize", file=sys.stderr)
            sys.exit(1)
    elif cmd == "activate":
        if activate_by_title(arg):
            print("OK")
        else:
            print("No matching window or SetForegroundWindow failed", file=sys.stderr)
            sys.exit(1)
    elif cmd == "activate_process":
        if activate_by_process(arg):
            print("OK")
        else:
            print("No matching process/window or SetForegroundWindow failed", file=sys.stderr)
            sys.exit(1)
    elif cmd == "activate_pid":
        try:
            pid = int(arg)
            if activate_by_pid(pid):
                print("OK")
            else:
                print("No window for PID or SetForegroundWindow failed", file=sys.stderr)
                sys.exit(1)
        except ValueError:
            print("activate_pid requires a numeric PID", file=sys.stderr)
            sys.exit(1)
    elif cmd == "pid":
        hwnd = find_hwnd_by_title(arg)
        if hwnd is not None:
            print(get_window_process_id(hwnd))
        else:
            print("0")
            sys.exit(1)
    else:
        print('usage: window_tool.py activate "标题"  |  activate_process <进程名>  |  maximize "标题"  |  maximize_process <进程名>  |  pid "标题"', file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
