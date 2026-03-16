#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM-OS 系统设置智能控制模块

提供系统设置的智能控制能力，让用户可以通过自然语言或命令直接调整系统设置，
而无需打开系统设置界面。

功能：
- 亮度调节（基于 brightness_tool）
- 音量控制（基于 volume_tool/keyboard_tool）
- 电源管理（基于 power_tool）
- 深色模式切换（通过注册表）
- 飞行模式控制（通过 netsh）
- 屏幕缩放比例控制
- 壁纸更换

版本: 1.0.0
依赖: brightness_tool, volume_tool, keyboard_tool, power_tool, reg_tool, wallpaper_tool
"""

import os
import sys
import subprocess
import ctypes
import json
import argparse
import time
from pathlib import Path

# 脚本目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def get_brightness():
    """获取当前屏幕亮度"""
    brightness_tool = os.path.join(SCRIPT_DIR, "brightness_tool.py")
    result = subprocess.run(
        [sys.executable, brightness_tool, "get"],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    )
    return result.stdout.strip()


def set_brightness(value):
    """设置屏幕亮度 (0-100)"""
    brightness_tool = os.path.join(SCRIPT_DIR, "brightness_tool.py")
    result = subprocess.run(
        [sys.executable, brightness_tool, "set", str(value)],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    )
    if result.returncode == 0:
        return f"屏幕亮度已设置为 {value}%"
    return f"设置亮度失败: {result.stderr}"


def adjust_brightness(delta):
    """调整屏幕亮度（相对值）"""
    # 先获取当前亮度
    current = get_brightness()
    try:
        # 尝试解析输出
        if "当前亮度" in current or "Brightness" in current:
            # 从输出中提取数值
            import re
            match = re.search(r'(\d+)', current)
            if match:
                current_val = int(match.group(1))
            else:
                current_val = 50
        else:
            current_val = 50
    except:
        current_val = 50

    new_val = max(0, min(100, current_val + delta))
    return set_brightness(new_val)


def get_volume():
    """获取当前音量"""
    volume_tool = os.path.join(SCRIPT_DIR, "volume_tool.py")
    result = subprocess.run(
        [sys.executable, volume_tool, "get"],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    )
    return result.stdout.strip()


def set_volume(value):
    """设置音量 (0-100)"""
    volume_tool = os.path.join(SCRIPT_DIR, "volume_tool.py")
    result = subprocess.run(
        [sys.executable, volume_tool, "set", str(value)],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    )
    if result.returncode == 0:
        return f"音量已设置为 {value}%"
    return f"设置音量失败: {result.stderr}"


def adjust_volume(delta):
    """调整音量（相对值）"""
    current = get_volume()
    try:
        import re
        match = re.search(r'(\d+)', current)
        if match:
            current_val = int(match.group(1))
        else:
            current_val = 50
    except:
        current_val = 50

    new_val = max(0, min(100, current_val + delta))
    return set_volume(new_val)


def mute_volume():
    """静音"""
    keyboard_tool = os.path.join(SCRIPT_DIR, "keyboard_tool.py")
    result = subprocess.run(
        [sys.executable, keyboard_tool, "key", "173"],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    )
    return "已静音" if result.returncode == 0 else f"静音失败: {result.stderr}"


def get_battery_status():
    """获取电池状态"""
    try:
        import subprocess
        result = subprocess.run(
            ["wmic", "Battery", "get", "EstimatedChargeRemaining,EstimatedRunTime,Status", "/Format:List"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        return result.stdout
    except Exception as e:
        return f"获取电池状态失败: {e}"


def get_power_plan():
    """获取当前电源计划"""
    try:
        result = subprocess.run(
            ["powercfg", "/getactivescheme"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        return result.stdout
    except Exception as e:
        return f"获取电源计划失败: {e}"


def set_power_plan(plan_type):
    """设置电源计划

    plan_type: 'balanced' (平衡), 'power_saver' (节能), 'high_performance' (高性能)
    """
    plan_map = {
        'balanced': '381b4222-f694-41f0-9685-ff5bb260df2e',
        'power_saver': 'a1841308-3541-4fab-bc81-f71556f20b4a',
        'high_performance': '8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c'
    }

    guid = plan_map.get(plan_type.lower())
    if not guid:
        return f"未知电源计划类型: {plan_type}，可用: balanced, power_saver, high_performance"

    try:
        result = subprocess.run(
            ["powercfg", "/setactive", guid],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        if result.returncode == 0:
            plan_names = {
                'balanced': '平衡',
                'power_saver': '节能',
                'high_performance': '高性能'
            }
            return f"电源计划已切换为: {plan_names.get(plan_type, plan_type)}"
        return f"设置电源计划失败: {result.stderr}"
    except Exception as e:
        return f"设置电源计划失败: {e}"


def get_dark_mode_status():
    """获取深色模式状态"""
    try:
        reg_tool = os.path.join(SCRIPT_DIR, "reg_tool.py")
        result = subprocess.run(
            [sys.executable, reg_tool, "get", "HKCU",
             "Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize",
             "AppsUseLightTheme"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        output = result.stdout.strip()
        if "0" in output:
            return "深色模式: 已开启"
        elif "1" in output:
            return "深色模式: 已关闭"
        return "深色模式: 未知"
    except Exception as e:
        return f"获取深色模式状态失败: {e}"


def set_dark_mode(enabled):
    """设置深色模式"""
    value = 0 if enabled else 1
    try:
        reg_tool = os.path.join(SCRIPT_DIR, "reg_tool.py")
        result = subprocess.run(
            [sys.executable, reg_tool, "set", "HKCU",
             "Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize",
             "AppsUseLightTheme", "REG_DWORD", str(value)],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        if result.returncode == 0:
            mode = "开启" if enabled else "关闭"
            return f"深色模式已{mode}"
        return f"设置深色模式失败: {result.stderr}"
    except Exception as e:
        return f"设置深色模式失败: {e}"


def toggle_dark_mode():
    """切换深色模式"""
    status = get_dark_mode_status()
    if "已开启" in status:
        return set_dark_mode(False)
    else:
        return set_dark_mode(True)


def get_airplane_mode():
    """获取飞行模式状态"""
    try:
        # 使用 netsh 检查无线状态
        result = subprocess.run(
            ["netsh", "wlan", "show", "interfaces"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        if "connected" in result.stdout.lower():
            return "飞行模式: 已关闭 (WiFi 已连接)"
        else:
            return "飞行模式: 已开启 (WiFi 未连接)"
    except Exception as e:
        return f"获取飞行模式状态失败: {e}"


def set_airplane_mode(enabled):
    """设置飞行模式"""
    # Windows 飞行模式控制较为复杂，这里提供一个简化的实现
    try:
        if enabled:
            # 禁用无线网卡
            result = subprocess.run(
                ["netsh", "interface", "set", "interface", "Wi-Fi", "disable"],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            if result.returncode == 0:
                return "飞行模式已开启"
            return f"开启飞行模式失败: {result.stderr}"
        else:
            # 启用无线网卡
            result = subprocess.run(
                ["netsh", "interface", "set", "interface", "Wi-Fi", "enable"],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            if result.returncode == 0:
                return "飞行模式已关闭"
            return f"关闭飞行模式失败: {result.stderr}"
    except Exception as e:
        return f"设置飞行模式失败: {e}"


def get_display_scale():
    """获取显示缩放比例"""
    try:
        # 使用 PowerShell 获取 DPI 设置
        ps_script = '''
        Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
public class DPI {
    [DllImport("user32.dll", SetLastError = true)]
    public static extern int GetDpiForSystem();
}
"@
$DPI = [DPI]::GetDpiForSystem()
$Scale = [Math]::Round($DPI / 96.0 * 100)
Write-Output "Scale: $Scale%"
'''
        result = subprocess.run(
            ["powershell", "-Command", ps_script],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        return result.stdout.strip()
    except Exception as e:
        return f"获取显示缩放比例失败: {e}"


def set_display_scale(scale):
    """设置显示缩放比例（仅支持部分系统）"""
    # 注意：修改系统 DPI 需要管理员权限且需要重启explorer
    return "设置显示缩放需要管理员权限且需要重启explorer，建议通过系统设置手动修改"


def get_wallpaper():
    """获取当前壁纸路径"""
    try:
        reg_tool = os.path.join(SCRIPT_DIR, "reg_tool.py")
        result = subprocess.run(
            [sys.executable, reg_tool, "get", "HKCU",
             "Control Panel\\Desktop", "Wallpaper"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        return result.stdout.strip()
    except Exception as e:
        return f"获取壁纸失败: {e}"


def set_wallpaper(image_path):
    """设置壁纸"""
    if not os.path.exists(image_path):
        return f"文件不存在: {image_path}"

    try:
        # 使用 SystemParametersInfo 设置壁纸
        SPI_SETDESKWALLPAPER = 0x0014
        SPIF_UPDATEINIFILE = 0x01
        SPIF_SENDCHANGE = 0x02

        # 将路径转换为 Windows 格式
        abs_path = os.path.abspath(image_path).replace('/', '\\')

        # 使用 PowerShell 设置壁纸
        ps_script = f'''
Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
public class Wallpaper {{
    [DllImport("user32.dll", CharSet = CharSet.Auto)]
    public static extern int SystemParametersInfo(int uAction, int uParam, string lpvParam, int fuWinIni);
}}
"@
$result = [Wallpaper]::SystemParametersInfo(0x0014, 0, "{abs_path}", 0x01 -bor 0x02)
if ($result -eq 0) {{ Write-Output "FAILED" }} else {{ Write-Output "SUCCESS" }}
'''
        result = subprocess.run(
            ["powershell", "-Command", ps_script],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        if "SUCCESS" in result.stdout:
            return f"壁纸已设置为: {image_path}"
        return f"设置壁纸失败: {result.stderr}"
    except Exception as e:
        return f"设置壁纸失败: {e}"


def get_system_settings():
    """获取所有系统设置概览"""
    settings = {}
    settings["brightness"] = get_brightness()
    settings["volume"] = get_volume()
    settings["battery"] = get_battery_status()
    settings["power_plan"] = get_power_plan()
    settings["dark_mode"] = get_dark_mode_status()
    settings["airplane_mode"] = get_airplane_mode()
    settings["display_scale"] = get_display_scale()
    settings["wallpaper"] = get_wallpaper()

    return json.dumps(settings, ensure_ascii=False, indent=2)


def list_settings_commands():
    """列出所有可用的设置命令"""
    commands = """
LLM-OS 系统设置智能控制
=========================

可用命令:
  --brightness get              获取当前亮度
  --brightness set <0-100>      设置亮度
  --brightness up               增加亮度
  --brightness down             减少亮度

  --volume get                  获取当前音量
  --volume set <0-100>          设置音量
  --volume up                   增加音量
  --volume down                 减少音量
  --volume mute                 静音

  --battery status              获取电池状态

  --power plan                  获取当前电源计划
  --power set <plan>            设置电源计划
                                可用: balanced(平衡), power_saver(节能), high_performance(高性能)

  --dark-mode status            获取深色模式状态
  --dark-mode on                开启深色模式
  --dark-mode off               关闭深色模式
  --dark-mode toggle            切换深色模式

  --airplane-mode status        获取飞行模式状态
  --airplane-mode on            开启飞行模式
  --airplane-mode off           关闭飞行模式

  --scale status                获取显示缩放比例

  --wallpaper get               获取当前壁纸
  --wallpaper set <path>        设置壁纸

  --all                         获取所有设置概览

示例:
  python llm_os_settings.py --brightness set 80
  python llm_os_settings.py --volume up
  python llm_os_settings.py --dark-mode on
  python llm_os_settings.py --power set power_saver
"""
    return commands


def main():
    parser = argparse.ArgumentParser(
        description='LLM-OS 系统设置智能控制',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=list_settings_commands()
    )

    # 亮度控制
    parser.add_argument('--brightness', nargs='?', const='status',
                        help='亮度控制: get, set <0-100>, up, down')

    # 音量控制
    parser.add_argument('--volume', nargs='?', const='status',
                        help='音量控制: get, set <0-100>, up, down, mute')

    # 电池状态
    parser.add_argument('--battery', nargs='?', const='status',
                        help='电池状态: status')

    # 电源管理
    parser.add_argument('--power', nargs='+', help='电源管理: plan, set <plan>')

    # 深色模式
    parser.add_argument('--dark-mode', nargs='*',
                        help='深色模式: status, on, off, toggle')

    # 飞行模式
    parser.add_argument('--airplane-mode', nargs='*',
                        help='飞行模式: status, on, off')

    # 显示缩放
    parser.add_argument('--scale', nargs='?', const='status',
                        help='显示缩放: status')

    # 壁纸
    parser.add_argument('--wallpaper', nargs='+', help='壁纸: get, set <path>')

    # 所有设置概览
    parser.add_argument('--all', action='store_true',
                        help='获取所有设置概览')

    # 列出命令帮助
    parser.add_argument('--help-commands', action='store_true',
                        help='列出所有命令')

    args = parser.parse_args()

    # 如果没有参数，显示帮助
    if len(sys.argv) == 1:
        print(list_settings_commands())
        return

    # 亮度控制
    if args.brightness is not None:
        action = args.brightness
        if action == 'status' or action == 'get':
            print(get_brightness())
        elif action == 'up':
            print(adjust_brightness(10))
        elif action == 'down':
            print(adjust_brightness(-10))
        elif action.isdigit():
            print(set_brightness(int(action)))
        else:
            print(f"未知亮度操作: {action}")
            print("可用: get, set <0-100>, up, down")

    # 音量控制
    elif args.volume is not None:
        action = args.volume
        if action == 'status' or action == 'get':
            print(get_volume())
        elif action == 'up':
            print(adjust_volume(10))
        elif action == 'down':
            print(adjust_volume(-10))
        elif action == 'mute':
            print(mute_volume())
        elif action.isdigit():
            print(set_volume(int(action)))
        else:
            print(f"未知音量操作: {action}")
            print("可用: get, set <0-100>, up, down, mute")

    # 电池状态
    elif args.battery is not None:
        print(get_battery_status())

    # 电源管理
    elif args.power is not None:
        if args.power[0] == 'plan':
            print(get_power_plan())
        elif args.power[0] == 'set' and len(args.power) > 1:
            print(set_power_plan(args.power[1]))
        else:
            print("可用: power plan, power set <plan>")

    # 深色模式
    elif args.dark_mode is not None:
        if not args.dark_mode or args.dark_mode[0] == 'status':
            print(get_dark_mode_status())
        elif args.dark_mode[0] == 'on':
            print(set_dark_mode(True))
        elif args.dark_mode[0] == 'off':
            print(set_dark_mode(False))
        elif args.dark_mode[0] == 'toggle':
            print(toggle_dark_mode())
        else:
            print("可用: dark-mode status/on/off/toggle")

    # 飞行模式
    elif args.airplane_mode is not None:
        if not args.airplane_mode or args.airplane_mode[0] == 'status':
            print(get_airplane_mode())
        elif args.airplane_mode[0] == 'on':
            print(set_airplane_mode(True))
        elif args.airplane_mode[0] == 'off':
            print(set_airplane_mode(False))
        else:
            print("可用: airplane-mode status/on/off")

    # 显示缩放
    elif args.scale is not None:
        if args.scale == 'status':
            print(get_display_scale())
        else:
            print("可用: --scale status")

    # 壁纸
    elif args.wallpaper is not None:
        if args.wallpaper[0] == 'get':
            print(get_wallpaper())
        elif args.wallpaper[0] == 'set' and len(args.wallpaper) > 1:
            print(set_wallpaper(args.wallpaper[1]))
        else:
            print("可用: --wallpaper get, --wallpaper set <path>")

    # 所有设置概览
    elif args.all:
        print(get_system_settings())

    # 帮助
    elif args.help_commands:
        print(list_settings_commands())


if __name__ == "__main__":
    main()