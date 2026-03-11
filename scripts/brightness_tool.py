# -*- coding: utf-8 -*-
"""
亮度工具：get 读当前亮度（0~100），set 设亮度。
Windows 下用 WMI WmiMonitorBrightness / WmiMonitorBrightnessMethods，仅对笔记本内置屏通常有效。
"""
import sys


def _wmi_get():
    try:
        import subprocess
        ps = r"""
$g = Get-CimInstance -Namespace root/WMI -ClassName WmiMonitorBrightness -ErrorAction SilentlyContinue
if ($g) { $g[0].CurrentBrightness } else { '' }
"""
        r = subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps],
            capture_output=True,
            text=True,
            timeout=5,
        )
        s = (r.stdout or "").strip()
        if s.isdigit():
            return int(s)
    except Exception:
        pass
    return None


def _wmi_set(level_0_100):
    """level 0~100，WmiSetBrightness(亮度, 超时秒)"""
    level = max(0, min(100, int(level_0_100)))
    try:
        import subprocess
        # 用 Invoke-CimMethod 更稳，部分机型需管理员权限
        ps = r"""
$m = Get-CimInstance -Namespace root/WMI -ClassName WmiMonitorBrightnessMethods -ErrorAction SilentlyContinue
if ($m) { Invoke-CimMethod -InputObject $m[0] -MethodName WmiSetBrightness -Arguments @{Brightness=%d; Timeout=0} } else { $null }
""" % level
        r = subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps],
            capture_output=True,
            text=True,
            timeout=10,
        )
        # Invoke-CimMethod 成功时 ReturnValue 常为 0
        return r.returncode == 0
    except Exception:
        return False


def main():
    if len(sys.argv) < 2:
        print("用法: brightness_tool.py get | set <0-100>")
        return
    cmd = sys.argv[1].lower()
    if cmd == "get":
        v = _wmi_get()
        print(v if v is not None else "?")
        return
    if cmd == "set" and len(sys.argv) >= 3:
        try:
            level = int(sys.argv[2])
        except ValueError:
            level = 50
        if _wmi_set(level):
            print("ok", level)
        else:
            print("err: WMI 不可用或本机不支持（多为笔记本内置屏）", file=sys.stderr)
        return
    print("用法: brightness_tool.py get | set <0-100>")


if __name__ == "__main__":
    main()
