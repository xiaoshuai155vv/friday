# -*- coding: utf-8 -*-
"""
音量工具：get 读当前档位（0~10），set 设档位。
不依赖 pycaw（你本机 COM 会崩溃），set 优先 nircmd，否则用键盘音量加/减模拟。
"""
import os
import sys
import subprocess

SCRIPTS = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(SCRIPTS)


def _nircmd_set(level):
    """level 0~100，与扬声器托盘 0~100 一致（6=6%，60=60%）"""
    level = max(0, min(100, int(level)))
    lev = level / 100.0
    vol16 = max(0, min(0xFFFF, int(round(lev * 0xFFFF))))
    nircmd = os.path.join(SCRIPTS, "nircmd.exe")
    if not os.path.isfile(nircmd):
        nircmd = "nircmd"
    try:
        r = subprocess.run(
            [nircmd, "setvolume", "0", str(vol16), str(vol16)],
            capture_output=True,
            timeout=5,
            cwd=PROJECT,
        )
        return r.returncode == 0
    except FileNotFoundError:
        return False
    except Exception:
        return False


def _keyboard_set(level):
    """先快速减到很低再快速加到目标（每步约 2%），间隔很短几乎无感。"""
    try:
        import ctypes
        import time
        VK_UP, VK_DOWN = 0xAF, 0xAE
        KEYUP = 0x0002
        u = ctypes.windll.user32
        level = max(0, min(100, int(level)))
        # 极短间隔，避免漏键又尽量快
        gap = 0.003
        for _ in range(50):
            u.keybd_event(VK_DOWN, 0, 0, 0)
            u.keybd_event(VK_DOWN, 0, KEYUP, 0)
            time.sleep(gap)
        steps_up = max(0, min(50, (level + 1) // 2))
        for _ in range(steps_up):
            u.keybd_event(VK_UP, 0, 0, 0)
            u.keybd_event(VK_UP, 0, KEYUP, 0)
            time.sleep(gap)
        return True
    except Exception:
        return False


def _get_pycaw():
    """子进程调 pycaw 读音量，避免本进程崩溃"""
    code = (
        "from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume\n"
        "from comtypes import CLSCTX_ALL\n"
        "vol = AudioUtilities.GetSpeakers().Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)\n"
        "print(round(vol.GetMasterVolumeLevelScalar() * 100))\n"
    )
    try:
        r = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            timeout=5,
            cwd=SCRIPTS,
        )
        if r.returncode == 0 and r.stdout.strip().isdigit():
            return int(r.stdout.strip())
    except Exception:
        pass
    return None


def main():
    if len(sys.argv) < 2:
        print("用法: volume_tool.py get | set <0-100>")
        return
    cmd = sys.argv[1].lower()
    if cmd == "get":
        v = _get_pycaw()
        if v is not None:
            print(v)
        else:
            print("?", flush=True)
        return
    if cmd == "set" and len(sys.argv) >= 3:
        try:
            level = int(sys.argv[2])
        except ValueError:
            level = 50
        level = max(0, min(100, level))
        # 仅用键盘模拟，不依赖 nircmd
        if _keyboard_set(level):
            print("ok", level, "(keyboard 约 %s%%)" % level)
        else:
            print("err", file=sys.stderr)
        return
        print("用法: volume_tool.py get | set <0-100>")


if __name__ == "__main__":
    main()
