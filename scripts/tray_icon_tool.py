# -*- coding: utf-8 -*-
"""
系统托盘图标交互工具
实现对系统托盘图标的点击、右键菜单操作等
"""
import sys
import ctypes
import time
from typing import List, Dict, Optional, Tuple

# Windows API
user32 = ctypes.windll.user32
shell32 = ctypes.windll.shell32

# 定义结构体
class RECT(ctypes.Structure):
    _fields_ = [("left", ctypes.c_long),
                ("top", ctypes.c_long),
                ("right", ctypes.c_long),
                ("bottom", ctypes.c_long)]

class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long),
                ("y", ctypes.c_long)]


def find_tray_window() -> Optional[int]:
    """查找系统托盘窗口句柄"""
    # 查找系统托盘窗口 (Shell_TrayWnd)
    hwnd = user32.FindWindowW(u"Shell_TrayWnd", None)
    if not hwnd:
        return None

    # 查找托盘中的通知区域 (NotifyIconOverflowWindow)
    overflow_hwnd = user32.FindWindowW(u"NotifyIconOverflowWindow", None)

    return hwnd, overflow_hwnd if overflow_hwnd else None


def get_tray_icons() -> List[Dict]:
    """获取系统托盘图标列表"""
    icons = []

    # 查找托盘窗口
    tray_result = find_tray_window()
    if not tray_result:
        return [{"error": "未找到系统托盘窗口"}]

    hwnd, overflow_hwnd = tray_result

    # 遍历托盘窗口的子窗口
    def enum_tray_children(hwnd):
        result = []
        # 查找 ToolbarWindow32 类（托盘图标通常是 Toolbar）
        child = user32.FindWindowExW(hwnd, 0, u"ToolbarWindow32", None)
        while child:
            # 获取窗口位置
            rect = RECT()
            user32.GetWindowRect(child, ctypes.byref(rect))

            # 获取窗口标题（工具提示）
            length = user32.GetWindowTextLengthW(child)
            if length > 0:
                buff = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(child, buff, length + 1)
                title = buff.value
            else:
                title = ""

            # 获取进程信息
            pid = ctypes.c_ulong()
            user32.GetWindowThreadProcessId(child, ctypes.byref(pid))

            result.append({
                "hwnd": child,
                "title": title,
                "rect": {
                    "left": rect.left,
                    "top": rect.top,
                    "right": rect.right,
                    "bottom": rect.bottom
                },
                "pid": pid.value
            })

            # 继续查找下一个
            child = user32.FindWindowExW(hwnd, child, u"ToolbarWindow32", None)

        return result

    # 枚举主托盘图标
    icons.extend(enum_tray_children(hwnd))

    # 如果有溢出窗口，也枚举
    if overflow_hwnd:
        icons.extend(enum_tray_children(overflow_hwnd))

    if not icons:
        return [{"error": "未找到托盘图标"}]

    # 简化返回结果
    return [{"index": i, "title": icon.get("title", "Unknown"), "pid": icon.get("pid", 0)}
            for i, icon in enumerate(icons) if "error" not in icon]


def click_tray_icon(icon_index: int = 0) -> Dict:
    """点击指定索引的托盘图标（模拟左键点击图标区域）"""
    tray_result = find_tray_window()
    if not tray_result:
        return {"success": False, "error": "未找到系统托盘窗口"}

    hwnd, overflow_hwnd = tray_result

    # 尝试点击主托盘
    def try_click(hwnd):
        # 查找 ToolbarWindow32
        toolbar = user32.FindWindowExW(hwnd, 0, u"ToolbarWindow32", None)
        if not toolbar:
            return False

        # 获取工具栏信息
        # 由于托盘图标的精确位置需要通过消息获取，这里使用近似方法
        # 发送鼠标点击消息到托盘区域

        # 获取托盘窗口的位置
        rect = RECT()
        user32.GetWindowRect(hwnd, ctypes.byref(rect))

        # 计算图标大致位置（托盘通常在右下角）
        # 这是一个简化实现，实际位置需要更精确的获取
        x = rect.left + 20 + icon_index * 20
        y = rect.top + 10

        # 发送鼠标点击
        # WM_LBUTTONDOWN
        user32.PostMessageW(hwnd, 0x0201, 0, y << 16 | x)  # MK_LBUTTON + coordinates
        time.sleep(0.05)
        # WM_LBUTTONUP
        user32.PostMessageW(hwnd, 0x0202, 0, y << 16 | x)

        return True

    if try_click(hwnd):
        return {"success": True, "action": "clicked", "icon_index": icon_index}

    # 尝试溢出窗口
    if overflow_hwnd and try_click(overflow_hwnd):
        return {"success": True, "action": "clicked", "icon_index": icon_index}

    return {"success": False, "error": "点击托盘图标失败"}


def right_click_tray_icon(icon_index: int = 0) -> Dict:
    """右键点击指定索引的托盘图标（弹出右键菜单）"""
    tray_result = find_tray_window()
    if not tray_result:
        return {"success": False, "error": "未找到系统托盘窗口"}

    hwnd, overflow_hwnd = tray_result

    # 类似于左键点击，但发送右键消息
    def try_right_click(hwnd):
        rect = RECT()
        user32.GetWindowRect(hwnd, ctypes.byref(rect))

        x = rect.left + 20 + icon_index * 20
        y = rect.top + 10

        # WM_RBUTTONDOWN
        user32.PostMessageW(hwnd, 0x0204, 0, y << 16 | x)  # MK_RBUTTON
        time.sleep(0.05)
        # WM_RBUTTONUP
        user32.PostMessageW(hwnd, 0x0205, 0, y << 16 | x)

        return True

    if try_right_click(hwnd):
        return {"success": True, "action": "right_clicked", "icon_index": icon_index}

    if overflow_hwnd and try_right_click(overflow_hwnd):
        return {"success": True, "action": "right_clicked", "icon_index": icon_index}

    return {"success": False, "error": "右键点击托盘图标失败"}


def click_by_title(title: str, button: str = "left") -> Dict:
    """根据图标标题（工具提示）点击托盘图标"""
    icons = get_tray_icons()

    # 过滤掉 error 项
    valid_icons = [i for i in icons if "error" not in i]

    # 查找匹配的图标
    for icon in valid_icons:
        if title.lower() in icon.get("title", "").lower():
            action = right_click_tray_icon if button == "right" else click_tray_icon
            result = action(icon["index"])
            result["matched_title"] = icon.get("title", "")
            return result

    return {"success": False, "error": f"未找到标题包含 '{title}' 的托盘图标"}


def get_tray_info() -> Dict:
    """获取系统托盘的详细信息"""
    tray_result = find_tray_window()
    if not tray_result:
        return {"success": False, "error": "未找到系统托盘窗口"}

    hwnd, overflow_hwnd = tray_result

    def get_window_info(hwnd):
        rect = RECT()
        user32.GetWindowRect(hwnd, ctypes.byref(rect))

        # 获取类名
        class_name = ctypes.create_unicode_buffer(256)
        user32.GetClassNameW(hwnd, class_name, 256)

        # 获取窗口标题
        title_len = user32.GetWindowTextLengthW(hwnd)
        title = ctypes.create_unicode_buffer(title_len + 1) if title_len > 0 else None
        if title:
            user32.GetWindowTextW(hwnd, title, title_len + 1)

        return {
            "class_name": class_name.value,
            "title": title.value if title else "",
            "rect": {
                "left": rect.left,
                "top": rect.top,
                "right": rect.right,
                "bottom": rect.bottom,
                "width": rect.right - rect.left,
                "height": rect.bottom - rect.top
            }
        }

    info = {
        "success": True,
        "tray_window": get_window_info(hwnd),
        "icons": get_tray_icons()
    }

    if overflow_hwnd:
        info["overflow_window"] = get_window_info(overflow_hwnd)

    return info


def main():
    """主函数：处理命令行参数"""
    if len(sys.argv) < 2:
        print("系统托盘图标交互工具")
        print("用法:")
        print("  python tray_icon_tool.py list              # 列出托盘图标")
        print("  python tray_icon_tool.py click [index]     # 点击托盘图标(默认索引0)")
        print("  python tray_icon_tool.py right-click [index]  # 右键点击托盘图标")
        print("  python tray_icon_tool.py click-title \"标题\"  # 根据标题点击托盘图标")
        print("  python tray_icon_tool.py right-click-title \"标题\"  # 根据标题右键点击")
        print("  python tray_icon_tool.py info              # 获取托盘详细信息")
        return

    command = sys.argv[1].lower()

    if command == "list":
        icons = get_tray_icons()
        print("系统托盘图标列表:")
        for icon in icons:
            if "error" in icon:
                print(f"  错误: {icon['error']}")
            else:
                print(f"  [{icon['index']}] {icon['title']} (PID: {icon['pid']})")

    elif command == "click":
        index = int(sys.argv[2]) if len(sys.argv) > 2 else 0
        result = click_tray_icon(index)
        print(result)

    elif command == "right-click":
        index = int(sys.argv[2]) if len(sys.argv) > 2 else 0
        result = right_click_tray_icon(index)
        print(result)

    elif command == "click-title":
        if len(sys.argv) < 3:
            print("请指定图标标题")
            return
        title = sys.argv[2]
        result = click_by_title(title, "left")
        print(result)

    elif command == "right-click-title":
        if len(sys.argv) < 3:
            print("请指定图标标题")
            return
        title = sys.argv[2]
        result = click_by_title(title, "right")
        print(result)

    elif command == "info":
        info = get_tray_info()
        import json
        print(json.dumps(info, ensure_ascii=False, indent=2))

    else:
        print(f"未知命令: {command}")


if __name__ == "__main__":
    main()