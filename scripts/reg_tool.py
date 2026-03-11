#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
注册表读写（Windows winreg）。get/set 支持 REG_SZ、REG_DWORD。
用法: reg_tool.py get HKCU "Software\\MyApp" ValueName
      reg_tool.py set HKCU "Software\\MyApp" ValueName sz "内容"  |  set ... ValueName dword 1
根键: HKCU(HKEY_CURRENT_USER), HKLM(HKEY_LOCAL_MACHINE), HKCR, HKU, HKCC
"""
import sys
if sys.platform != "win32":
    sys.exit(1)
import winreg

ROOTS = {
    "HKCU": winreg.HKEY_CURRENT_USER,
    "HKLM": winreg.HKEY_LOCAL_MACHINE,
    "HKCR": winreg.HKEY_CLASSES_ROOT,
    "HKU": winreg.HKEY_USERS,
    "HKCC": winreg.HKEY_CURRENT_CONFIG,
}

def main():
    if len(sys.argv) < 2:
        print("usage: reg_tool get <root> <key_path> [value_name]  |  set <root> <key_path> <value_name> sz|dword <value>", file=sys.stderr)
        sys.exit(1)
    cmd = sys.argv[1].lower()
    if cmd == "get":
        if len(sys.argv) < 4:
            print("usage: reg_tool get <root> <key_path> [value_name]", file=sys.stderr)
            sys.exit(1)
        root_name = sys.argv[2].upper()
        key_path = sys.argv[3]
        value_name = sys.argv[4] if len(sys.argv) > 4 else None  # default value
        if root_name not in ROOTS:
            print("root must be HKCU|HKLM|HKCR|HKU|HKCC", file=sys.stderr)
            sys.exit(1)
        try:
            key = winreg.OpenKey(ROOTS[root_name], key_path, 0, winreg.KEY_READ)
            try:
                val, typ = winreg.QueryValueEx(key, value_name or "")
                if typ == winreg.REG_DWORD:
                    print(val)
                else:
                    print(val)
            finally:
                winreg.CloseKey(key)
        except FileNotFoundError:
            print("", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(str(e), file=sys.stderr)
            sys.exit(1)
    elif cmd == "set":
        if len(sys.argv) < 6:
            print("usage: reg_tool set <root> <key_path> <value_name> sz|dword <value>", file=sys.stderr)
            sys.exit(1)
        root_name = sys.argv[2].upper()
        key_path = sys.argv[3]
        value_name = sys.argv[4]
        typ_str = sys.argv[5].lower()
        value = " ".join(sys.argv[6:]) if len(sys.argv) > 6 else ""
        if root_name not in ROOTS:
            print("root must be HKCU|HKLM|HKCR|HKU|HKCC", file=sys.stderr)
            sys.exit(1)
        try:
            key = winreg.CreateKey(ROOTS[root_name], key_path)
            try:
                if typ_str == "dword":
                    winreg.SetValueEx(key, value_name, 0, winreg.REG_DWORD, int(value))
                else:
                    winreg.SetValueEx(key, value_name, 0, winreg.REG_SZ, value)
            finally:
                winreg.CloseKey(key)
        except Exception as e:
            print(str(e), file=sys.stderr)
            sys.exit(1)
    else:
        print("usage: reg_tool get|set ...", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
