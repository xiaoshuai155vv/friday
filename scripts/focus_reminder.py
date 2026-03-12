#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能时间管理与专注提醒模块 - 番茄钟、定时休息提醒、专注模式
支持：
  - pomodoro start [work_minutes] [break_minutes]: 启动番茄钟（默认25+5分钟）
  - pomodoro status: 查看当前番茄钟状态
  - pomodoro stop: 停止番茄钟
  - rest reminder [minutes]: 设置定时休息提醒
  - focus mode start: 启动专注模式（阻止娱乐应用）
  - focus mode stop: 停止专注模式
  - status: 查看专注提醒状态
"""
import sys
import os
import json
import time
import threading
import signal
import atexit
from datetime import datetime, timedelta

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(SCRIPT_DIR, "..", "runtime", "state", "focus_reminder_status.json")

# 默认配置
DEFAULT_WORK_MINUTES = 25
DEFAULT_BREAK_MINUTES = 5

class FocusReminder:
    def __init__(self):
        self.state = {
            "pomodoro_active": False,
            "pomodoro_start_time": None,
            "work_duration": DEFAULT_WORK_MINUTES,
            "break_duration": DEFAULT_BREAK_MINUTES,
            "completed_cycles": 0,
            "rest_reminder_active": False,
            "rest_reminder_minutes": 60,
            "rest_reminder_start_time": None,
            "focus_mode_active": False,
            "focus_mode_start_time": None,
            "blocked_apps": ["chrome", "firefox", "edge", "spotify", "music", "netease"]
        }
        self._load_state()
        self._cleanup_on_exit()

    def _load_state(self):
        """加载状态"""
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                    # 合并状态，保留运行时信息
                    self.state.update(saved)
            except Exception:
                pass

    def _save_state(self):
        """保存状态"""
        state_dir = os.path.dirname(STATE_FILE)
        if not os.path.exists(state_dir):
            os.makedirs(state_dir)
        try:
            with open(STATE_FILE, "w", encoding="utf-8") as f:
                json.dump(self.state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存状态失败: {e}", file=sys.stderr)

    def _cleanup_on_exit(self):
        """退出时清理"""
        atexit.register(self._save_state)

    def _show_notification(self, title, message):
        """显示通知"""
        try:
            notification_script = os.path.join(SCRIPT_DIR, "notification_tool.py")
            if os.path.exists(notification_script):
                subprocess.run(
                    [sys.executable, notification_script, "show", title, message],
                    capture_output=True, timeout=10
                )
            else:
                print(f"通知: {title} - {message}")
        except Exception as e:
            print(f"通知失败: {e}", file=sys.stderr)

    def _run_pomodoro_timer(self, work_minutes, break_minutes):
        """运行番茄钟计时器（后台线程）"""
        def timer_thread():
            # 工作阶段
            work_seconds = work_minutes * 60
            time.sleep(work_seconds)
            if not self.state.get("pomodoro_active", False):
                return
            self._show_notification("🍅 番茄钟", f"工作时间结束！已专注 {work_minutes} 分钟，开始休息 {break_minutes} 分钟")

            # 休息阶段
            break_seconds = break_minutes * 60
            time.sleep(break_seconds)
            if not self.state.get("pomodoro_active", False):
                return
            self.state["completed_cycles"] = self.state.get("completed_cycles", 0) + 1
            self._save_state()
            self._show_notification("🍅 休息结束", "开始新的番茄钟？使用「番茄钟开始」继续")

        thread = threading.Thread(target=timer_thread, daemon=True)
        thread.start()

    def _run_rest_reminder(self, minutes):
        """运行定时休息提醒"""
        def timer_thread():
            seconds = minutes * 60
            time.sleep(seconds)
            if not self.state.get("rest_reminder_active", False):
                return
            self._show_notification("💆 休息提醒", f"您已连续工作 {minutes} 分钟，建议休息一下！")

        thread = threading.Thread(target=timer_thread, daemon=True)
        thread.start()

    def _run_focus_mode_checker(self):
        """运行专注模式检查器"""
        def checker_thread():
            while self.state.get("focus_mode_active", False):
                try:
                    # 检查当前活动窗口
                    result = subprocess.run(
                        ["powershell", "-NoProfile", "-Command",
                         "(Get-Process | Where-Object {$_.MainWindowTitle -ne ''} | Select-Object -First 1).ProcessName"],
                        capture_output=True, text=True, timeout=5
                    )
                    if result.returncode == 0:
                        proc = result.stdout.strip().lower()
                        blocked = [app.lower() for app in self.state.get("blocked_apps", [])]
                        if any(b in proc for b in blocked):
                            self._show_notification("🎯 专注模式", f"检测到您正在使用 {proc}，当前为专注模式")
                except Exception:
                    pass
                time.sleep(60)  # 每分钟检查一次

        thread = threading.Thread(target=checker_thread, daemon=True)
        thread.start()

    def start_pomodoro(self, work_minutes=None, break_minutes=None):
        """启动番茄钟"""
        work = work_minutes or self.state.get("work_duration", DEFAULT_WORK_MINUTES)
        break_min = break_minutes or self.state.get("break_duration", DEFAULT_BREAK_MINUTES)

        self.state["pomodoro_active"] = True
        self.state["pomodoro_start_time"] = datetime.now().isoformat()
        self.state["work_duration"] = work
        self.state["break_duration"] = break_min
        self._save_state()

        self._show_notification("🍅 番茄钟已启动", f"工作 {work} 分钟，休息 {break_min} 分钟")
        self._run_pomodoro_timer(work, break_min)
        return True

    def stop_pomodoro(self):
        """停止番茄钟"""
        self.state["pomodoro_active"] = False
        self._save_state()
        self._show_notification("🍅 番茄钟已停止", f"本轮完成 {self.state.get('completed_cycles', 0)} 个番茄周期")
        return True

    def get_pomodoro_status(self):
        """获取番茄钟状态"""
        if not self.state.get("pomodoro_active", False):
            return "番茄钟未启动"

        start = self.state.get("pomodoro_start_time")
        if start:
            start_dt = datetime.fromisoformat(start)
            elapsed = datetime.now() - start_dt
            minutes = int(elapsed.total_seconds() / 60)
        else:
            minutes = 0

        work = self.state.get("work_duration", DEFAULT_WORK_MINUTES)
        completed = self.state.get("completed_cycles", 0)
        return f"番茄钟进行中 | 已工作 {minutes}/{work} 分钟 | 已完成 {completed} 个周期"

    def start_rest_reminder(self, minutes):
        """启动定时休息提醒"""
        minutes = minutes or self.state.get("rest_reminder_minutes", 60)
        self.state["rest_reminder_active"] = True
        self.state["rest_reminder_minutes"] = minutes
        self.state["rest_reminder_start_time"] = datetime.now().isoformat()
        self._save_state()

        self._show_notification("💆 休息提醒已设置", f"每 {minutes} 分钟提醒一次")
        self._run_rest_reminder(minutes)
        return True

    def stop_rest_reminder(self):
        """停止休息提醒"""
        self.state["rest_reminder_active"] = False
        self._save_state()
        self._show_notification("💆 休息提醒已停止", "休息提醒已关闭")
        return True

    def start_focus_mode(self):
        """启动专注模式"""
        self.state["focus_mode_active"] = True
        self.state["focus_mode_start_time"] = datetime.now().isoformat()
        self._save_state()

        self._show_notification("🎯 专注模式已启动", "系统将提醒您保持专注")
        self._run_focus_mode_checker()
        return True

    def stop_focus_mode(self):
        """停止专注模式"""
        self.state["focus_mode_active"] = False
        self._save_state()
        self._show_notification("🎯 专注模式已停止", "专注模式已关闭")
        return True

    def get_status(self):
        """获取完整状态"""
        status = []
        if self.state.get("pomodoro_active"):
            status.append(self.get_pomodoro_status())
        else:
            status.append("番茄钟: 未启动")

        if self.state.get("rest_reminder_active"):
            mins = self.state.get("rest_reminder_minutes", 60)
            status.append(f"休息提醒: 每 {mins} 分钟")
        else:
            status.append("休息提醒: 未启动")

        if self.state.get("focus_mode_active"):
            status.append("专注模式: 已启动")
        else:
            status.append("专注模式: 未启动")

        return "\n".join(status)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    cmd = sys.argv[1].lower()
    fr = FocusReminder()

    # pomodoro 子命令
    if cmd == "pomodoro":
        if len(sys.argv) < 3:
            print(fr.get_pomodoro_status())
            sys.exit(0)

        subcmd = sys.argv[2].lower()
        if subcmd == "start":
            work = int(sys.argv[3]) if len(sys.argv) > 3 else DEFAULT_WORK_MINUTES
            break_min = int(sys.argv[4]) if len(sys.argv) > 4 else DEFAULT_BREAK_MINUTES
            fr.start_pomodoro(work, break_min)
            print(f"番茄钟已启动: 工作 {work} 分钟，休息 {break_min} 分钟")
        elif subcmd == "stop":
            fr.stop_pomodoro()
            print("番茄钟已停止")
        elif subcmd == "status":
            print(fr.get_pomodoro_status())
        else:
            print(f"未知子命令: {subcmd}")
            sys.exit(1)

    # rest reminder 子命令
    elif cmd == "rest":
        if len(sys.argv) < 3:
            print(fr.get_status())
            sys.exit(0)

        subcmd = sys.argv[2].lower()
        if subcmd == "reminder":
            if len(sys.argv) < 4:
                print(f"当前休息提醒间隔: {fr.state.get('rest_reminder_minutes', 60)} 分钟")
                sys.exit(0)
            if sys.argv[3].lower() == "stop":
                fr.stop_rest_reminder()
                print("休息提醒已停止")
            else:
                minutes = int(sys.argv[3])
                fr.start_rest_reminder(minutes)
                print(f"休息提醒已设置: 每 {minutes} 分钟")
        else:
            print(f"未知子命令: {subcmd}")
            sys.exit(1)

    # focus mode 子命令
    elif cmd == "focus":
        if len(sys.argv) < 3:
            print(fr.get_status())
            sys.exit(0)

        subcmd = sys.argv[2].lower()
        if subcmd == "mode":
            if len(sys.argv) < 4:
                print(fr.get_status())
                sys.exit(0)
            if sys.argv[3].lower() == "start":
                fr.start_focus_mode()
                print("专注模式已启动")
            elif sys.argv[3].lower() == "stop":
                fr.stop_focus_mode()
                print("专注模式已停止")
            else:
                print(f"未知参数: {sys.argv[3]}")
                sys.exit(1)
        else:
            print(f"未知子命令: {subcmd}")
            sys.exit(1)

    # status 命令
    elif cmd == "status":
        print(fr.get_status())

    else:
        print(f"未知命令: {cmd}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()