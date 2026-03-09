#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
获取 Windows 已安装应用列表。从注册表 Uninstall 键读取 DisplayName。
用法: installed_apps_tool.py [--json] [--simple]
  --json: 输出 JSON 数组（含 name, version, publisher）
  --simple: 每行一个应用名（默认）
"""
import sys
import json

if sys.platform != "win32":
    print("Windows only", file=sys.stderr)
    sys.exit(1)

import winreg

UNINSTALL_PATHS = [
    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
    (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
]


def _read_key(hkey, path, name, default=None):
    try:
        k = winreg.OpenKey(hkey, path, 0, winreg.KEY_READ)
        try:
            val, _ = winreg.QueryValueEx(k, name)
            return val
        finally:
            winreg.CloseKey(k)
    except (FileNotFoundError, OSError):
        pass
    return default


def list_installed_apps():
    seen = set()
    apps = []
    for hkey, base_path in UNINSTALL_PATHS:
        try:
            key = winreg.OpenKey(hkey, base_path, 0, winreg.KEY_READ)
            try:
                i = 0
                while True:
                    try:
                        subkey_name = winreg.EnumKey(key, i)
                        i += 1
                    except OSError:
                        break
                    subpath = base_path + "\\" + subkey_name
                    display_name = _read_key(hkey, subpath, "DisplayName")
                    if not display_name or not display_name.strip():
                        continue
                    # 跳过系统组件、更新补丁等
                    if _read_key(hkey, subpath, "SystemComponent"):
                        continue
                    if _read_key(hkey, subpath, "ParentKeyName"):
                        continue
                    display_name = display_name.strip()
                    if display_name in seen:
                        continue
                    seen.add(display_name)
                    version = _read_key(hkey, subpath, "DisplayVersion") or ""
                    publisher = _read_key(hkey, subpath, "Publisher") or ""
                    apps.append({
                        "name": display_name,
                        "version": version,
                        "publisher": publisher,
                    })
            finally:
                winreg.CloseKey(key)
        except (FileNotFoundError, OSError):
            continue
    apps.sort(key=lambda x: x["name"].lower())
    return apps


def _ensure_utf8():
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            try:
                s.reconfigure(encoding="utf-8")
            except (OSError, AttributeError):
                pass


def main():
    _ensure_utf8()
    json_out = "--json" in sys.argv
    simple = "--simple" in sys.argv or (not json_out and len(sys.argv) == 1)
    apps = list_installed_apps()
    if json_out:
        print(json.dumps(apps, ensure_ascii=False, indent=0))
    else:
        for a in apps:
            print(a["name"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
