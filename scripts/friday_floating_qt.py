#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
原生 GUI 悬浮球：圆形、无边框、透明或深色底、置顶。
不依赖 WebView，用 PyQt5 绘制网格球 + 圆环 + 光球 + 文案。
依赖: pip install PyQt5
"""
import sys
import os
import json
import glob
import time
import subprocess
import ctypes
import ctypes.wintypes
from datetime import datetime
from math import pi, cos, sin

# Windows 全局热键（仅 win32）
if sys.platform == "win32":
    try:
        user32 = ctypes.windll.user32
        MOD_NOREPEAT = 0x4000
        MOD_ALT = 0x0001
        MOD_CONTROL = 0x0002
        MOD_SHIFT = 0x0004
        WM_HOTKEY = 0x0312
        VK_S = 0x53
        VK_Q = 0x51
        VK_V = 0x56
        HOTKEY_ID_FULL = 9001
        HOTKEY_ID_REGION = 9002
        HOTKEY_ID_VOICE = 9003
        _win_RegisterHotKey = user32.RegisterHotKey
        _win_RegisterHotKey.argtypes = [ctypes.wintypes.HWND, ctypes.c_int, ctypes.c_uint, ctypes.c_uint]
        _win_RegisterHotKey.restype = ctypes.wintypes.BOOL
        _win_UnregisterHotKey = user32.UnregisterHotKey
        _win_UnregisterHotKey.argtypes = [ctypes.wintypes.HWND, ctypes.c_int]
        _win_UnregisterHotKey.restype = ctypes.wintypes.BOOL
        HAS_GLOBAL_HOTKEY = True
    except Exception:
        HAS_GLOBAL_HOTKEY = False
else:
    HAS_GLOBAL_HOTKEY = False

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SCRIPTS = os.path.join(ROOT, "scripts")
STATE_FILE = os.path.join(ROOT, "runtime", "state", "current_mission.json")
RECENT_LOGS_FILE = os.path.join(ROOT, "runtime", "state", "recent_logs.json")
EVOLUTION_LAST_STATUS_FILE = os.path.join(ROOT, "runtime", "state", "evolution_last_status.json")
EVOLUTION_SESSION_PENDING = os.path.join(ROOT, "runtime", "state", "evolution_session_pending.json")
LOG_DIR = os.path.join(ROOT, "runtime", "logs")
ONECALL_LOG_FILE = os.path.join(LOG_DIR, "onecall.log")
SCREENSHOTS_DIR = os.path.join(ROOT, "runtime", "screenshots")


def _onecall_log(msg):
    """框选/剪贴板/预览相关日志，便于排查。"""
    try:
        os.makedirs(LOG_DIR, exist_ok=True)
        with open(ONECALL_LOG_FILE, "a", encoding="utf-8") as f:
            f.write("%s\t%s\n" % (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), msg))
            f.flush()
    except Exception:
        pass


def _latest_region_bmp(max_age_seconds=120):
    """取最近生成的框选图 onecall_region_*.bmp，若超过 max_age_seconds 秒则返回 None。"""
    try:
        os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
        now = datetime.now()
        best_path, best_mtime = None, 0
        for name in os.listdir(SCREENSHOTS_DIR):
            if name.startswith("onecall_region_") and name.lower().endswith(".bmp"):
                path = os.path.join(SCREENSHOTS_DIR, name)
                if not os.path.isfile(path):
                    continue
                mtime = os.path.getmtime(path)
                if (now.timestamp() - mtime) <= max_age_seconds and mtime > best_mtime:
                    best_path, best_mtime = path, mtime
        return best_path
    except Exception:
        return None
SIZE = 300
CENTER = SIZE // 2
EDGE_MARGIN = 12
EDGE_STICK_W = 36

# 尝试导入 PyQt5
try:
    from PyQt5.QtWidgets import (
        QApplication, QWidget, QLabel, QSystemTrayIcon,
        QMenu, QAction, QDesktopWidget, QScrollArea,
        QPushButton, QVBoxLayout, QHBoxLayout, QFrame,
        QPlainTextEdit, QComboBox, QShortcut, QFileDialog, QInputDialog,
    )
    from PyQt5.QtCore import Qt, QTimer, QPoint, QRect, QEvent, QThread, pyqtSignal
    from PyQt5.QtGui import (
        QPainter, QColor, QPen, QBrush, QRadialGradient,
        QPainterPath, QFont, QLinearGradient, QRegion, QIcon, QPixmap, QKeySequence, QWheelEvent, QKeyEvent,
    )
    HAS_QT = True
except ImportError:
    HAS_QT = False


def load_state():
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"mission": "—", "phase": "—", "loop_round": 0}


def load_recent_output(max_entries=6):
    """最近几条行为日志，用于显示节点/输出（滑动区多行）"""
    try:
        if os.path.isfile(RECENT_LOGS_FILE):
            with open(RECENT_LOGS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            entries = data.get("entries") or []
            return entries[-max_entries:] if len(entries) >= max_entries else entries
    except Exception:
        pass
    return []


def can_submit_evolution():
    """上一轮会话是否已完成（evolution_completed_<session_id>.json 已存在）。未完成则不可提交下一轮，避免多会话堆积。若超过 30 分钟仍未完成则标记为失败并允许下一轮。"""
    try:
        if not os.path.isfile(EVOLUTION_SESSION_PENDING):
            return True
        with open(EVOLUTION_SESSION_PENDING, "r", encoding="utf-8") as f:
            d = json.load(f)
        sid = (d.get("session_id") or "").strip()
        if not sid:
            return True
        completed = os.path.join(ROOT, "runtime", "state", "evolution_completed_%s.json" % sid)
        if os.path.isfile(completed):
            return True
        started_at = d.get("started_at", "")
        if started_at:
            try:
                from datetime import datetime, timezone
                s = started_at.replace("Z", "+00:00")
                dt = datetime.fromisoformat(s)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                elapsed = (datetime.now(timezone.utc) - dt).total_seconds()
                if elapsed > 1800:
                    os.makedirs(os.path.dirname(completed), exist_ok=True)
                    with open(completed, "w", encoding="utf-8") as f:
                        json.dump({
                            "session_id": sid,
                            "status": "stale_failed",
                            "message": "超过30分钟未完成，标记为失败",
                            "started_at": started_at,
                        }, f, ensure_ascii=False, indent=2)
                    return True
            except Exception:
                pass
        return False
    except Exception:
        return True


def load_evolution_last_status():
    """读最近一次进化环请求状态，用于过程·结果展示与防重复提示。"""
    try:
        if os.path.isfile(EVOLUTION_LAST_STATUS_FILE):
            with open(EVOLUTION_LAST_STATUS_FILE, "r", encoding="utf-8") as f:
                d = json.load(f)
            return d.get("status"), d.get("at", ""), d.get("message", "")
    except Exception:
        pass
    return None, "", ""


def _cc_completed_after_timeout(timeout_at_iso):
    """启发式：timeout 后若 behavior 日志出现 decide，则认为 CC 已完成该轮。"""
    try:
        from datetime import timezone

        s = (timeout_at_iso or "").strip().replace("Z", "+00:00")
        t0 = datetime.fromisoformat(s)
        if t0.tzinfo is None:
            t0 = t0.replace(tzinfo=timezone.utc)

        pattern = os.path.join(LOG_DIR, "behavior_*.log")
        files = sorted(glob.glob(pattern))
        if not files:
            return False
        # 只看最近 2 个文件的末尾，避免扫描过大
        for path in reversed(files[-2:]):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    lines = f.readlines()[-400:]
                for line in reversed(lines):
                    line = (line or "").strip()
                    if not line:
                        continue
                    parts = line.split("\t", 5)
                    if len(parts) < 2:
                        continue
                    ts, phase = parts[0], parts[1]
                    if phase != "decide":
                        continue
                    try:
                        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                        if dt.tzinfo is None:
                            dt = dt.replace(tzinfo=timezone.utc)
                        if dt > t0:
                            return True
                    except Exception:
                        continue
            except Exception:
                continue
    except Exception:
        return False
    return False


def _format_evolution_status_line():
    """格式化为过程·结果弹框首行：最近进化环请求: 成功/超时/失败 (HH:MM)。首行固定为「上次请求状态」，不按时间与下方日志混排。"""
    status, at, msg = load_evolution_last_status()
    if not status:
        return None
    t = _format_log_time(at) if at else ""
    if status == "ok":
        return "最近进化环请求: 成功 (本轮已完成)" + (" " + t if t else "")
    if status == "timeout":
        # 若下方日志中已有超时之后的 decide，说明 CC 已跑完，首行提示可清除超时状态，避免误解「一直是最上面」
        if at and _cc_completed_after_timeout(at):
            return "最近进化环请求: 超时(" + t + ")，下方日志显示本轮已完成 — 可右键「清除超时状态」更新"
        return "最近进化环请求: 超时 " + (t + " — CC 可能仍在执行，请勿急于再提交" if t else "— CC 可能仍在执行，请勿急于再提交")
    return "最近进化环请求: 失败 " + (t + " " + (msg or "")[:30] if t or msg else "")


def _format_log_time(iso_ts):
    """将 behavior_log 的 ISO 时间戳格式化为本地简短时间 [HH:MM:SS] 或 [MM-DD HH:MM]"""
    if not iso_ts or not iso_ts.strip():
        return ""
    try:
        from datetime import datetime
        s = iso_ts.strip()
        if "T" in s:
            dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
            try:
                local = dt.astimezone()
            except Exception:
                local = dt
            return local.strftime("%H:%M:%S")
        return s[:19] if len(s) >= 19 else s
    except Exception:
        return iso_ts[:12] if len(iso_ts) > 12 else iso_ts


def load_recent_output_all(max_entries=80):
    """弹框用：直接从 runtime/logs/behavior_*.log 读最近条目，与当前进程同源，不依赖 recent_logs.json"""
    rows = []
    try:
        pattern = os.path.join(LOG_DIR, "behavior_*.log")
        files = sorted(glob.glob(pattern))  # 日期升序，先旧后新
        for path in files:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        parts = line.split("\t", 5)
                        if len(parts) >= 3:
                            rows.append({
                                "ts": parts[0],
                                "phase": parts[1],
                                "desc": parts[2],
                            })
            except Exception:
                continue
        return rows[-max_entries:] if rows else []
    except Exception:
        pass
    return []


# 弹框尺寸（放大以便阅读，行距与字体在 FridayLogDialog 内设置）
LOG_DIALOG_W = 560
LOG_DIALOG_H = 680


class FridayLogDialog(QWidget):
    """过程/结果弹框，风格与悬浮球一致：深色透明、琥珀色"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Friday 过程")
        self.setFixedSize(LOG_DIALOG_W, LOG_DIALOG_H)
        self.setWindowFlags(
            Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
            | Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self._drag_start = None
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(12)
        title = QLabel("过程 · 结果")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(
            "color: rgb(255,200,80); font-size: 16px; letter-spacing: 4px; font-weight: 600; background: transparent;"
        )
        layout.addWidget(title)
        sub = QLabel("首行 = 最近请求状态（固定置顶），以下 = 行为日志（倒序）")
        sub.setStyleSheet("color: rgb(200,170,90); font-size: 11px; background: transparent;")
        layout.addWidget(sub)
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QScrollArea.NoFrame)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._scroll.setStyleSheet(
            "QScrollArea { background: rgba(65,65,80,0.95); border: 1px solid rgb(255,170,50); border-radius: 8px; }"
            "QScrollBar:vertical { width: 10px; background: rgba(45,45,55,0.95); border: none; border-radius: 4px; margin: 0; }"
            "QScrollBar::handle:vertical { background: rgb(255,170,50); border-radius: 4px; min-height: 28px; }"
            "QScrollBar::handle:vertical:hover { background: rgb(255,195,80); }"
            "QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }"
        )
        self._log_label = QLabel("—")
        self._log_label.setWordWrap(True)
        self._log_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self._log_label.setStyleSheet(
            "color: rgb(255,210,100); font-size: 14px; font-weight: 500; background: transparent; padding: 12px;"
        )
        self._log_label.setMinimumWidth(LOG_DIALOG_W - 60)
        self._log_label.setMinimumHeight(320)
        font = self._log_label.font()
        font.setPointSize(13)
        font.setStyleHint(font.SansSerif)
        self._log_label.setFont(font)
        self._scroll.setWidget(self._log_label)
        layout.addWidget(self._scroll, 1)
        close_btn = QPushButton("关闭")
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setStyleSheet(
            "QPushButton { color: rgb(255,200,80); background: rgba(255,170,50,0.2); "
            "border: 1px solid rgb(255,170,50); border-radius: 6px; padding: 6px 20px; font-weight: 600; }"
            "QPushButton:hover { background: rgba(255,170,50,0.35); }"
        )
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn, 0, Qt.AlignCenter)
        self._refresh()
        self._refresh_timer = QTimer(self)
        self._refresh_timer.timeout.connect(self._refresh)
        self._refresh_timer.start(10000)

    def _refresh(self):
        # 首行：最近进化环请求状态（成功/超时/失败），便于判断上一轮是否完成
        evolution_line = _format_evolution_status_line()
        entries = load_recent_output_all(80)
        lines = []
        if evolution_line:
            lines.append(evolution_line)
        for e in reversed(entries):
            ts = _format_log_time(e.get("ts") or "")
            ph = (e.get("phase") or "").strip()
            desc = (e.get("desc") or "").strip()
            if desc:
                prefix = ("[" + ts + "] ") if ts else ""
                lines.append(prefix + ph + " · " + desc)
        self._log_label.setText("\n\n".join(lines) if lines else "—")

    def showEvent(self, event):
        super().showEvent(event)
        self._refresh()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        p.setPen(QPen(QColor(255, 180, 50, 220), 1))
        p.setBrush(QColor(58, 58, 72, 252))
        p.drawRoundedRect(1, 1, LOG_DIALOG_W - 2, LOG_DIALOG_H - 2, 12, 12)
        p.end()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_start = event.globalPos() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if getattr(self, "_drag_start", None) is not None and event.buttons() & Qt.LeftButton:
            self.move(event.globalPos() - self._drag_start)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_start = None


# OneCall 多模态对话框尺寸（放大、更亮）
ONECALL_W = 520
ONECALL_H = 720
ONECALL_BAR_H = 36


def _bmp_size(bmp_path):
    """读取 BMP 宽高，失败返回 (None, None)。"""
    try:
        with open(bmp_path, "rb") as f:
            head = f.read(54)
        if len(head) < 54 or head[:2] != b"BM":
            return None, None
        w_full = int.from_bytes(head[18:22], "little")
        h_full_raw = int.from_bytes(head[22:26], "little")
        h_full = -h_full_raw if h_full_raw < 0 else h_full_raw
        return w_full, h_full
    except Exception:
        return None, None


def _crop_bmp(src_path, x1, y1, w, h, out_path):
    """从 BMP 裁剪区域并保存。24 位 BMP，支持 top-down(biHeight<0) 和 bottom-up。坐标自动钳位到图像内。"""
    try:
        with open(src_path, "rb") as f:
            data = bytearray(f.read())
        if len(data) < 54 or data[:2] != b"BM":
            _onecall_log("crop_bmp_fail header len=%s head2=%s" % (len(data), data[:2] if len(data) >= 2 else b""))
            return False
        px_offset = int.from_bytes(data[10:14], "little")
        w_full = int.from_bytes(data[18:22], "little")
        h_full_raw = int.from_bytes(data[22:26], "little")
        top_down = h_full_raw < 0
        h_full = -h_full_raw if top_down else h_full_raw
        # 钳位到图像范围内，避免越界导致裁剪失败
        x1 = max(0, min(x1, w_full - 1))
        y1 = max(0, min(y1, h_full - 1))
        w = max(1, min(w, w_full - x1))
        h = max(1, min(h, h_full - y1))
        row_full = ((w_full * 3 + 3) // 4) * 4
        row_out = ((w * 3 + 3) // 4) * 4
        raw_out = 54 + row_out * h
        out = bytearray(54)
        out[:14] = data[:14]
        out[2:6] = (raw_out + 14).to_bytes(4, "little")
        out[14:54] = data[14:54]
        out[18:22] = w.to_bytes(4, "little")
        out[22:26] = (-h).to_bytes(4, "little", signed=True)
        out[34:38] = (row_out * h).to_bytes(4, "little")
        for yy in range(h):
            sy = (y1 + yy) if top_down else (h_full - 1 - (y1 + yy))
            src_start = px_offset + sy * row_full + x1 * 3
            out.extend(data[src_start : src_start + w * 3])
            out.extend(b"\x00" * (row_out - w * 3))
        with open(out_path, "wb") as f:
            f.write(out)
        _onecall_log("crop_bmp_ok out=%s" % out_path)
        return True
    except Exception as e:
        _onecall_log("crop_bmp_exception %s" % repr(e))
        return False


class RegionCaptureOverlay(QWidget):
    """全屏半透明 overlay，拖拽框选区域后从预截图中裁剪。"""
    def __init__(self, full_bmp_path=None, parent=None, on_result=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self._start = None
        self._rect = None
        self._full_bmp = full_bmp_path
        self._result_path = None
        self._on_result = on_result

    def showEvent(self, event):
        super().showEvent(event)
        self._start = None
        self._rect = None
        self._result_path = None
        screen = QDesktopWidget().screenGeometry()
        self.setGeometry(0, 0, screen.width(), screen.height())

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._start = event.pos()
            self._rect = QRect(self._start, self._start)

    def mouseMoveEvent(self, event):
        if self._start is not None and event.buttons() & Qt.LeftButton:
            self._rect = QRect(self._start, event.pos()).normalized()
            self.update()

    def mouseReleaseEvent(self, event):
        ok = event.button() == Qt.LeftButton and self._start is not None and self._rect and self._full_bmp and os.path.isfile(self._full_bmp)
        _onecall_log("overlay_release ok=%s start=%s rect=%s file=%s" % (
            ok, self._start is not None, self._rect.width() if self._rect else 0, os.path.isfile(self._full_bmp) if self._full_bmp else False
        ))
        if ok:
            r = self._rect
            if r.width() >= 10 and r.height() >= 10:
                # 按截图实际尺寸映射 overlay 坐标，避免 DPI/分辨率不一致导致裁剪错位或失败
                w_bmp, h_bmp = _bmp_size(self._full_bmp)
                ow, oh = max(1, self.width()), max(1, self.height())
                if w_bmp is not None and h_bmp is not None:
                    x1 = int(r.x() * w_bmp / ow)
                    y1 = int(r.y() * h_bmp / oh)
                    w = max(1, int(r.width() * w_bmp / ow))
                    h = max(1, int(r.height() * h_bmp / oh))
                else:
                    x1, y1 = r.x(), r.y()
                    w, h = max(1, r.width()), max(1, r.height())
                _onecall_log("overlay_crop_params w_bmp=%s h_bmp=%s ow=%s oh=%s x1=%s y1=%s w=%s h=%s" % (w_bmp, h_bmp, ow, oh, x1, y1, w, h))
                out = os.path.join(SCREENSHOTS_DIR, "onecall_region_%s.bmp" % datetime.now().strftime("%Y%m%d_%H%M%S"))
                crop_ok = _crop_bmp(self._full_bmp, x1, y1, w, h, out)
                if crop_ok:
                    self._result_path = out
                    _onecall_log("region_crop_ok path=%s" % out)
                    try:
                        pm = QPixmap(out)
                        if not pm.isNull():
                            QApplication.clipboard().setPixmap(pm)
                            _onecall_log("clipboard_set_pixmap ok size=%dx%d" % (pm.width(), pm.height()))
                        else:
                            _onecall_log("clipboard_skip pixmap_is_null")
                    except Exception as e:
                        _onecall_log("clipboard_set_error %s" % repr(e))
                else:
                    _onecall_log("region_crop_bmp_returned_false")
            else:
                _onecall_log("region_crop_fail rect_small w=%s h=%s" % (r.width(), r.height()))
            if self._on_result:
                try:
                    self._on_result(self._result_path)
                except Exception:
                    pass
            self._start = None
            self._rect = None
            self.close()
        else:
            _onecall_log("region_cancel no_rect_or_no_file")
            if self._on_result:
                try:
                    self._on_result(None)
                except Exception:
                    pass
            self._start = None
            self._rect = None
            self.close()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        p.fillRect(self.rect(), QColor(0, 0, 0, 100))
        if self._rect and self._rect.isValid():
            p.setCompositionMode(QPainter.CompositionMode_Clear)
            p.fillRect(self._rect, Qt.transparent)
            p.setCompositionMode(QPainter.CompositionMode_SourceOver)
            p.setPen(QPen(QColor(255, 180, 50), 2, Qt.DashLine))
            p.setBrush(Qt.NoBrush)
            p.drawRect(self._rect)
        p.end()


class ImagePreviewWindow(QWidget):
    """图片预览窗口：支持 +/- 与滚轮缩放"""
    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self._image_path = image_path
        self._pixmap = QPixmap(image_path)
        self._scale = 1.0
        self.setWindowTitle("图片预览")
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Tool | Qt.Window)
        layout = QVBoxLayout(self)
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(False)
        self._scroll.setAlignment(Qt.AlignCenter)
        self._scroll.setStyleSheet("QScrollArea { background: rgb(55,55,70); border: none; }")
        self._img_label = QLabel()
        self._img_label.setAlignment(Qt.AlignCenter)
        self._img_label.setStyleSheet("background: transparent;")
        self._img_label.setScaledContents(False)
        self._scroll.setWidget(self._img_label)
        layout.addWidget(self._scroll, 1)
        hint = QLabel("滚轮或 +/- 键缩放")
        hint.setStyleSheet("color: rgb(200,180,100); font-size: 11px;")
        layout.addWidget(hint, 0, Qt.AlignCenter)
        close_btn = QPushButton("关闭")
        close_btn.setStyleSheet("QPushButton { color: rgb(255,200,80); background: rgba(255,170,50,0.2); border: 1px solid rgb(255,170,50); padding: 6px 20px; }")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
        self.setStyleSheet("background: rgb(55,55,70);")
        self.resize(820, 640)
        self._apply_zoom()

    def _apply_zoom(self):
        if self._pixmap.isNull():
            return
        w, h = self._pixmap.width(), self._pixmap.height()
        sw, sh = int(w * self._scale), int(h * self._scale)
        scaled = self._pixmap.scaled(sw, sh, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self._img_label.setPixmap(scaled)
        self._img_label.setMinimumSize(scaled.size())
        self._img_label.resize(scaled.size())

    def _zoom_in(self):
        self._scale = min(5.0, self._scale * 1.15)
        self._apply_zoom()

    def _zoom_out(self):
        self._scale = max(0.15, self._scale / 1.15)
        self._apply_zoom()

    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            self._zoom_in()
        else:
            self._zoom_out()

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Plus, Qt.Key_Equal):
            self._zoom_in()
        elif event.key() == Qt.Key_Minus:
            self._zoom_out()
        else:
            super().keyPressEvent(event)


class OneCallWorker(QThread):
    """后台执行 vision 调用，不阻塞主线程，便于悬浮球显示等待动画。"""
    finished_signal = pyqtSignal(bool, str, str, int)

    def __init__(self, script_path, args, cwd):
        super().__init__()
        self._script_path = script_path
        self._args = args
        self._cwd = cwd

    def run(self):
        try:
            r = subprocess.run(
                self._args,
                cwd=self._cwd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=90,
            )
            out = (r.stdout or "").strip()
            err = (r.stderr or "").strip()
            self.finished_signal.emit(r.returncode == 0, out, err, r.returncode)
        except subprocess.TimeoutExpired:
            self.finished_signal.emit(False, "", "timeout", -1)
        except Exception as e:
            self.finished_signal.emit(False, "", str(e), -1)


class FridayMultimodalDialog(QWidget):
    """OneCall 多模态：输入语料 + 图片，调用 vision_proxy/vision_coords，结果可滚动；可收起为小条。"""
    def __init__(self, ball, parent=None):
        super().__init__(parent)
        self._ball = ball
        self._collapsed = False
        self._image_path = None
        self._call_history = []
        self.setWindowTitle("Friday OneCall")
        self.setFixedSize(ONECALL_W, ONECALL_H)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self._drag_start = None
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(12)
        title_row = QHBoxLayout()
        ss = "color: rgb(255,210,90); font-size: 15px; font-weight: 600; background: transparent;"
        title = QLabel("OneCall · 多模态")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(ss + " letter-spacing: 3px;")
        title_row.addWidget(title, 1)
        self._close_btn = QPushButton("✕")
        self._close_btn.setFixedSize(28, 28)
        self._close_btn.setCursor(Qt.PointingHandCursor)
        self._close_btn.setStyleSheet(
            "QPushButton { color: rgb(255,200,80); background: transparent; border: none; font-size: 16px; font-weight: bold; }"
            "QPushButton:hover { color: rgb(255,100,80); background: rgba(255,80,60,0.2); border-radius: 4px; }"
        )
        self._close_btn.clicked.connect(self.close)
        title_row.addWidget(self._close_btn, 0, Qt.AlignRight | Qt.AlignTop)
        layout.addLayout(title_row)
        # 快捷键已移至 FridayBall 应用级，任意位置可用
        self._content_frame = QFrame()
        self._content_frame.setStyleSheet("background: transparent;")
        content_layout = QVBoxLayout(self._content_frame)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(12)
        btn_ss = (
            "QPushButton { color: rgb(255,210,90); background: rgba(255,180,60,0.25); "
            "border: 1px solid rgb(255,170,50); border-radius: 6px; padding: 6px 14px; font-weight: 600; font-size: 13px; }"
            "QPushButton:hover { background: rgba(255,170,50,0.4); }"
            "QPushButton:disabled { color: rgb(150,130,70); border-color: rgb(120,100,50); }"
        )
        input_label = QLabel("语料 / 问题")
        input_label.setStyleSheet("color: rgb(255,200,80); font-size: 13px;")
        content_layout.addWidget(input_label)
        self._input = QPlainTextEdit()
        self._input.setPlaceholderText("输入要问图片的问题，如：描述图中内容")
        self._input.setMaximumHeight(88)
        self._input.setStyleSheet(
            "QPlainTextEdit { background: rgba(65,65,80,0.95); color: rgb(255,220,110); "
            "border: 1px solid rgb(255,170,50); border-radius: 8px; padding: 8px; font-size: 14px; }"
        )
        self._input.installEventFilter(self)
        content_layout.addWidget(self._input)
        img_row = QHBoxLayout()
        self._img_btn_full = QPushButton("全屏截图 (Ctrl+Shift+S)")
        self._img_btn_full.setCursor(Qt.PointingHandCursor)
        self._img_btn_full.setStyleSheet(btn_ss)
        self._img_btn_full.clicked.connect(self._do_full_screenshot)
        self._img_btn_region = QPushButton("框选区域 (Ctrl+Shift+Q)")
        self._img_btn_region.setCursor(Qt.PointingHandCursor)
        self._img_btn_region.setStyleSheet(btn_ss)
        self._img_btn_region.clicked.connect(self._do_region_capture)
        self._img_btn_upload = QPushButton("上传图片")
        self._img_btn_upload.setCursor(Qt.PointingHandCursor)
        self._img_btn_upload.setStyleSheet(btn_ss)
        self._img_btn_upload.clicked.connect(self._do_upload_image)
        self._img_status = QLabel("未选择图片")
        self._img_status.setStyleSheet("color: rgb(220,190,80); font-size: 12px;")
        img_row.addWidget(self._img_btn_full)
        img_row.addWidget(self._img_btn_region)
        img_row.addWidget(self._img_btn_upload)
        img_row.addStretch()
        img_row.addWidget(self._img_status)
        content_layout.addLayout(img_row)
        self._preview_btn = QPushButton("点击预览图片")
        self._preview_btn.setCursor(Qt.PointingHandCursor)
        self._preview_btn.setMinimumHeight(100)
        self._preview_btn.setStyleSheet(
            "QPushButton { color: rgb(200,180,100); background: rgba(65,65,80,0.95); "
            "border: 1px dashed rgb(255,170,50); border-radius: 8px; font-size: 13px; }"
            "QPushButton:hover { background: rgba(75,75,90,0.95); color: rgb(255,200,100); }"
        )
        self._preview_btn.clicked.connect(self._show_preview)
        self._preview_btn.setEnabled(False)
        content_layout.addWidget(self._preview_btn)
        mode_row = QHBoxLayout()
        mode_row.addWidget(QLabel("模式:"))
        self._mode = QComboBox()
        self._mode.addItems(["看图理解 (vision_proxy)", "获取坐标 (vision_coords)"])
        self._mode.setMinimumWidth(220)
        self._mode.setStyleSheet(
            "QComboBox { background: rgba(55,55,70,0.95); color: rgb(255,220,90); font-size: 13px; "
            "border: 1px solid rgb(255,170,50); border-radius: 6px; padding: 6px 10px; min-height: 20px; }"
            "QComboBox QAbstractItemView { color: rgb(255,220,90); background: rgb(55,55,70); selection-background-color: rgb(80,70,50); }"
            "QComboBox::drop-down { border: none; }"
        )
        mode_row.addWidget(self._mode, 1)
        content_layout.addLayout(mode_row)
        self._exec_btn = QPushButton("执行 OneCall")
        self._exec_btn.setCursor(Qt.PointingHandCursor)
        self._exec_btn.setStyleSheet(btn_ss)
        self._exec_btn.clicked.connect(self._do_call)
        content_layout.addWidget(self._exec_btn)
        result_label = QLabel("结果")
        result_label.setStyleSheet("color: rgb(255,200,80); font-size: 13px;")
        content_layout.addWidget(result_label)
        self._result_scroll = QScrollArea()
        self._result_scroll.setWidgetResizable(True)
        self._result_scroll.setFrameShape(QScrollArea.NoFrame)
        self._result_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._result_scroll.setStyleSheet(
            "QScrollArea { background: rgba(65,65,80,0.95); border: 1px solid rgb(255,170,50); border-radius: 8px; min-height: 280px; }"
            "QScrollBar:vertical { width: 10px; background: rgba(45,45,55,0.95); border-radius: 5px; }"
            "QScrollBar::handle:vertical { background: rgb(255,170,50); border-radius: 5px; min-height: 30px; }"
        )
        self._result_label = QLabel("—")
        self._result_label.setWordWrap(True)
        self._result_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self._result_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self._result_label.setStyleSheet("color: rgb(255,215,100); font-size: 13px; padding: 10px; background: transparent; line-height: 1.4;")
        self._result_label.setMinimumWidth(ONECALL_W - 50)
        self._result_scroll.setWidget(self._result_label)
        content_layout.addWidget(self._result_scroll, 1)
        bot_row = QHBoxLayout()
        self._collapse_btn = QPushButton("收起")
        self._collapse_btn.setCursor(Qt.PointingHandCursor)
        self._collapse_btn.setStyleSheet(btn_ss)
        self._collapse_btn.clicked.connect(self._toggle_collapse)
        close_btn = QPushButton("关闭")
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setStyleSheet(btn_ss)
        close_btn.clicked.connect(self.close)
        bot_row.addWidget(self._collapse_btn)
        bot_row.addWidget(close_btn)
        content_layout.addLayout(bot_row)
        layout.addWidget(self._content_frame, 1)
        self._bar_frame = QFrame()
        self._bar_frame.setStyleSheet("background: transparent;")
        self._bar_frame.setFixedHeight(ONECALL_BAR_H)
        bar_layout = QVBoxLayout(self._bar_frame)
        bar_layout.setContentsMargins(0, 0, 0, 0)
        self._bar_btn = QPushButton("OneCall · 点击展开")
        self._bar_btn.setFlat(True)
        self._bar_btn.setCursor(Qt.PointingHandCursor)
        self._bar_btn.setStyleSheet(
            "QPushButton { color: rgb(255,200,80); background: transparent; border: none; font-size: 11px; }"
            "QPushButton:hover { color: rgb(255,220,100); }"
        )
        self._bar_btn.clicked.connect(self._toggle_collapse)
        bar_layout.addWidget(self._bar_btn)
        layout.addWidget(self._bar_frame)
        self._bar_frame.hide()

    def eventFilter(self, obj, event):
        if obj is self._input and event.type() == QEvent.KeyPress and event.key() == Qt.Key_V and (event.modifiers() & Qt.ControlModifier):
            if not QApplication.clipboard().pixmap().isNull():
                if self._set_image_from_clipboard("已选: 粘贴"):
                    return True
        return super().eventFilter(obj, event)

    def _toggle_collapse(self):
        self._collapsed = not self._collapsed
        if self._collapsed:
            self.setFixedHeight(60)
            self._content_frame.hide()
            self._collapse_btn.setText("展开")
            self._bar_frame.show()
            last = (self._call_history[-1]["out"][:60] + "…") if self._call_history else "—"
            self._bar_btn.setText("OneCall · 最近: %s" % last)
        else:
            self.setFixedHeight(ONECALL_H)
            self._content_frame.show()
            self._collapse_btn.setText("收起")
            self._bar_frame.hide()

    def _update_preview(self, path):
        """预览区显示的是本地保存的截图（全屏或框选保存到 runtime/screenshots），非剪贴板。"""
        if path and os.path.isfile(path):
            pm = QPixmap(path)
            if not pm.isNull():
                thumb = pm.scaled(160, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self._preview_btn.setIcon(QIcon(thumb))
                self._preview_btn.setIconSize(thumb.size())
                self._preview_btn.setText(" 点击查看大图")
                self._preview_btn.setToolTip("本地保存的截图，点击查看大图")
            self._preview_btn.setEnabled(True)
        else:
            self._preview_btn.setIcon(QIcon())
            self._preview_btn.setText("点击预览图片")
            self._preview_btn.setToolTip("")
            self._preview_btn.setEnabled(False)

    def _show_preview(self):
        if not self._image_path or not os.path.isfile(self._image_path):
            return
        if getattr(self, "_preview_win", None) and self._preview_win.isVisible():
            self._preview_win.raise_()
            self._preview_win.activateWindow()
            return
        self._preview_win = ImagePreviewWindow(self._image_path)
        self._preview_win.show()
        self._preview_win.raise_()
        self._preview_win.activateWindow()

    def _do_full_screenshot(self):
        os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
        path = os.path.join(SCREENSHOTS_DIR, "onecall_full_%s.bmp" % datetime.now().strftime("%Y%m%d_%H%M%S"))
        r = subprocess.run([sys.executable, os.path.join(SCRIPTS, "screenshot_tool.py"), path], cwd=ROOT, capture_output=True, timeout=10)
        if r.returncode == 0 and os.path.isfile(path):
            self._image_path = path
            self._img_status.setText("已选: 全屏")
            try:
                pm = QPixmap(path)
                if not pm.isNull():
                    QApplication.clipboard().setPixmap(pm)
            except Exception:
                pass
            self._update_preview(path)

    def _do_upload_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "选择图片", "", "图片 (*.png *.jpg *.jpeg *.bmp *.gif);;全部 (*.*)"
        )
        if not path or not os.path.isfile(path):
            return
        try:
            import shutil
            os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
            ext = os.path.splitext(path)[1].lower() or ".png"
            dest = os.path.join(SCREENSHOTS_DIR, "onecall_upload_%s%s" % (datetime.now().strftime("%Y%m%d_%H%M%S"), ext))
            shutil.copy2(path, dest)
            self._image_path = dest
            self._img_status.setText("已选: 上传")
            pm = QPixmap(dest)
            if not pm.isNull():
                QApplication.clipboard().setPixmap(pm)
            self._update_preview(dest)
            self._preview_btn.setEnabled(True)
        except Exception:
            pass

    def _do_region_capture(self):
        self.hide()
        QTimer.singleShot(300, self._show_region_overlay)

    def _show_region_overlay(self):
        os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
        full_path = os.path.join(SCREENSHOTS_DIR, "onecall_capture_%s.bmp" % datetime.now().strftime("%Y%m%d_%H%M%S"))
        r = subprocess.run([sys.executable, os.path.join(SCRIPTS, "screenshot_tool.py"), full_path], cwd=ROOT, capture_output=True, timeout=10)
        if r.returncode != 0 or not os.path.isfile(full_path):
            self._img_status.setText("截图失败")
            self.show()
            return
        # 回调由对话框在显示后从文件设剪贴板（overlay 关闭后设剪贴板会丢）
        ball = getattr(self, "_ball", None)
        def on_result(path):
            target = getattr(ball, "_onecall_dialog", None) if ball else self
            if target is None:
                target = self
            _onecall_log("on_result_called path=%s" % repr(path))
            QTimer.singleShot(80, lambda p=path, t=target: t._on_region_done(p))
        overlay = RegionCaptureOverlay(full_path, None, on_result=on_result)
        overlay.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Window)
        self._region_overlay = overlay
        screen = QDesktopWidget().screenGeometry()
        overlay.setGeometry(screen)
        overlay.show()
        QApplication.processEvents()
        overlay.raise_()
        overlay.activateWindow()

    def _set_image_from_clipboard(self, status_label="已选: 粘贴"):
        """从剪贴板取图并写入预览（剪贴板中转，不依赖路径传递）。"""
        try:
            pm = QApplication.clipboard().pixmap()
            if pm.isNull():
                _onecall_log("clipboard_read pixmap_is_null")
                return False
            _onecall_log("clipboard_read ok size=%dx%d" % (pm.width(), pm.height()))
            os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
            path = os.path.join(SCREENSHOTS_DIR, "onecall_paste_%s.png" % datetime.now().strftime("%Y%m%d_%H%M%S"))
            if pm.save(path, "PNG"):
                self._image_path = path
                self._img_status.setText(status_label)
                self._update_preview(path)
                self._preview_btn.setEnabled(True)
                _onecall_log("preview_from_clipboard ok path=%s" % path)
                return True
            _onecall_log("preview_from_clipboard save_fail path=%s" % path)
        except Exception as e:
            _onecall_log("preview_from_clipboard error %s" % repr(e))
        return False

    def _on_region_done(self, path):
        # 先展开，再解析 path（回调可能丢 path，用最近框选文件兜底）
        if getattr(self, "_collapsed", False):
            self._collapsed = False
            self.setFixedHeight(ONECALL_H)
            self._content_frame.show()
            if hasattr(self, "_collapse_btn"):
                self._collapse_btn.setText("收起")
            if hasattr(self, "_bar_frame"):
                self._bar_frame.hide()
        if path:
            path = os.path.abspath(path)
        if not path or not os.path.isfile(path):
            path = _latest_region_bmp()
            if path:
                _onecall_log("on_region_done used_fallback_path path=%s" % path)
        if self._set_image_from_clipboard("已选: 框选"):
            _onecall_log("on_region_done used_clipboard")
        elif path and os.path.isfile(path):
            self._image_path = path
            self._img_status.setText("已选: 框选")
            self._update_preview(self._image_path)
            self._preview_btn.setEnabled(True)
            _onecall_log("on_region_done used_path path=%s" % self._image_path)
        else:
            _onecall_log("on_region_done no_image path=%s fallback=%s" % (repr(path), _latest_region_bmp()))
            self._img_status.setText("未选择图片")
        self.show()
        self.raise_()
        self.activateWindow()
        QApplication.processEvents()
        # 窗口已显示后再设剪贴板，避免 overlay 关闭导致剪贴板被清空（由前台窗口持有）
        if getattr(self, "_image_path", None) and os.path.isfile(self._image_path):
            try:
                pm = QPixmap(self._image_path)
                if not pm.isNull():
                    QApplication.clipboard().setPixmap(pm)
                    _onecall_log("on_region_done set_clipboard_after_show ok")
                else:
                    _onecall_log("on_region_done set_clipboard_skip pixmap_null")
            except Exception as e:
                _onecall_log("on_region_done set_clipboard_error %s" % repr(e))
        self._preview_btn.repaint()
        QApplication.processEvents()

    def _do_call(self):
        if not self._image_path or not os.path.isfile(self._image_path):
            self._result_label.setText("请先选择图片（全屏或框选）")
            return
        q = self._input.toPlainText().strip()
        if not q:
            self._result_label.setText("请输入问题")
            return
        is_coords = "坐标" in self._mode.currentText()
        script = "vision_coords.py" if is_coords else "vision_proxy.py"
        args = [sys.executable, os.path.join(SCRIPTS, script), self._image_path, q]
        self._exec_btn.setText("执行中…")
        self._exec_btn.setEnabled(False)
        self._onecall_pending_q = q
        self._onecall_pending_coords = is_coords
        if self._ball and hasattr(self._ball, "_set_spinning"):
            self._ball._set_spinning(True)
        self._onecall_worker = OneCallWorker(os.path.join(SCRIPTS, script), args, ROOT)
        self._onecall_worker.finished_signal.connect(self._on_onecall_finished)
        self._onecall_worker.start()

    def _on_onecall_finished(self, ok, out, err, returncode):
        self._onecall_worker = None
        if self._ball and hasattr(self._ball, "_set_spinning"):
            self._ball._set_spinning(False)
        q = getattr(self, "_onecall_pending_q", "")
        is_coords = getattr(self, "_onecall_pending_coords", False)
        if not ok and out == "":
            out = "错误: " + (err or str(returncode))
        self._call_history.append({"q": q[:50], "out": out, "mode": "coords" if is_coords else "proxy"})
        lines = []
        for h in reversed(self._call_history[-10:]):
            lines.append("【%s】%s" % (h["mode"], h["q"]))
            lines.append(h["out"])
            lines.append("—")
        self._result_label.setText("\n".join(lines) if lines else out)
        sb = self._result_scroll.verticalScrollBar()
        sb.setValue(sb.maximum())
        if hasattr(self, "_exec_btn") and self._exec_btn:
            self._exec_btn.setText("执行 OneCall")
            self._exec_btn.setEnabled(True)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        p.setPen(QPen(QColor(255, 180, 50, 220), 1))
        p.setBrush(QColor(58, 58, 72, 252))
        p.drawRoundedRect(1, 1, self.width() - 2, self.height() - 2, 12, 12)
        p.end()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_start = event.globalPos() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if getattr(self, "_drag_start", None) is not None and event.buttons() & Qt.LeftButton:
            self.move(event.globalPos() - self._drag_start)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_start = None


class VoiceVisionFallbackWorker(QThread):
    """do.py 失败时：截图 + vision_proxy 多模态兜底"""
    finished_signal = pyqtSignal(str)

    def __init__(self, user_text):
        super().__init__()
        self._user_text = user_text

    def run(self):
        try:
            import tempfile
            bmp = os.path.join(tempfile.gettempdir(), "friday_voice_fallback.bmp")
            r1 = subprocess.run(
                [sys.executable, os.path.join(SCRIPTS, "screenshot_tool.py"), bmp],
                cwd=ROOT, capture_output=True, text=True, timeout=10
            )
            if r1.returncode != 0 or not os.path.isfile(bmp):
                self.finished_signal.emit("截图失败")
                return
            r2 = subprocess.run(
                [sys.executable, os.path.join(SCRIPTS, "vision_proxy.py"), bmp, self._user_text],
                cwd=ROOT, capture_output=True, text=True, timeout=60, encoding="utf-8", errors="replace"
            )
            out = (r2.stdout or "").strip()
            if out:
                self.finished_signal.emit(out[:300])
            else:
                self.finished_signal.emit("多模态未返回结果")
        except Exception as e:
            self.finished_signal.emit("多模态异常: " + str(e)[:80])


class VoiceAsrWorker(QThread):
    """后台线程：讯飞 ASR 录音识别，支持提前结束。"""
    partial_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(str)

    def __init__(self, stop_event, duration_sec=60):
        super().__init__()
        self._stop = stop_event
        self._duration = duration_sec

    def run(self):
        try:
            sys.path.insert(0, SCRIPTS)
            from xunfei_asr_service import record_and_recognize, is_configured, HAS_SOUNDDEVICE, HAS_WEBSOCKET
            if not is_configured() or not HAS_WEBSOCKET or not HAS_SOUNDDEVICE:
                self.finished_signal.emit("")
                return
            text = record_and_recognize(
                duration_sec=self._duration,
                on_partial=lambda t: self.partial_signal.emit(t),
                stop_event=self._stop,
            )
            self.finished_signal.emit(text or "")
        except Exception as e:
            self.finished_signal.emit("")


# 语音聊天框尺寸（屏幕中央透明 chat，放大以便多轮对话）
VOICE_OVERLAY_W = 560
VOICE_OVERLAY_H = 520


class VoiceOverlayWidget(QWidget):
    """屏幕中央透明 chat 框：用户与 AI(CC) 的语音文字对话"""
    def __init__(self, ball, parent=None):
        super().__init__(parent)
        self._ball = ball
        self._stop_event = None
        self.setWindowTitle("Friday 语音")
        self.setFixedSize(VOICE_OVERLAY_W, VOICE_OVERLAY_H)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self._drag_start = None
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(8)
        self._status = QLabel("◉ 正在听…")
        self._status.setWordWrap(True)
        self._status.setAlignment(Qt.AlignCenter)
        self._status.setStyleSheet(
            "color: rgb(255,235,140); font-size: 12px; font-weight: 600; "
            "background: transparent; letter-spacing: 2px; "
            "text-shadow: 0 0 12px rgba(255,200,80,0.8);"
        )
        layout.addWidget(self._status, 0)
        self._text = QLabel("")
        self._text.setWordWrap(True)
        self._text.setAlignment(Qt.AlignCenter)
        self._text.setStyleSheet(
            "color: rgb(255,220,100); font-size: 14px; font-weight: 600; "
            "background: transparent; letter-spacing: 2px; line-height: 1.4; "
            "text-shadow: 0 0 14px rgba(255,180,50,0.7);"
        )
        layout.addWidget(self._text, 0)
        self._chat = QPlainTextEdit()
        self._chat.setReadOnly(True)
        self._chat.setFrameShape(QFrame.NoFrame)
        self._chat.setMinimumHeight(280)
        self._chat.setStyleSheet(
            "QPlainTextEdit { color: rgb(200,220,240); font-size: 13px; "
            "background: transparent; border: none; "
            "selection-background-color: rgba(255,170,50,0.3); }"
        )
        self._chat.setPlaceholderText("你与 CC 的语音对话将显示在这里…")
        layout.addWidget(self._chat, 1)
        btn_row = QHBoxLayout()
        self._stop_btn = QPushButton("结束 (Esc)")
        self._stop_btn.setCursor(Qt.PointingHandCursor)
        self._stop_btn.setFocusPolicy(Qt.StrongFocus)
        self._stop_btn.setFixedHeight(32)
        self._stop_btn.setMinimumWidth(100)
        self._stop_btn.setStyleSheet(
            "QPushButton { color: rgb(255,200,80); background: rgba(255,170,50,0.15); "
            "border: 1px solid rgb(255,170,50); border-radius: 4px; font-weight: 600; font-size: 12px; }"
            "QPushButton:hover { background: rgba(255,170,50,0.35); }"
        )
        self._stop_btn.clicked.connect(self._on_stop)
        self._continue_btn = QPushButton("继续说话")
        self._continue_btn.setCursor(Qt.PointingHandCursor)
        self._continue_btn.setFixedHeight(32)
        self._continue_btn.setMinimumWidth(90)
        self._continue_btn.setStyleSheet(
            "QPushButton { color: rgb(180,220,255); background: rgba(100,150,200,0.2); "
            "border: 1px solid rgb(100,150,200); border-radius: 4px; font-weight: 600; font-size: 12px; }"
            "QPushButton:hover { background: rgba(100,150,200,0.35); }"
        )
        self._continue_btn.clicked.connect(self._on_continue)
        btn_row.addStretch()
        btn_row.addWidget(self._continue_btn)
        btn_row.addWidget(self._stop_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)
        esc = QShortcut(QKeySequence(Qt.Key_Escape), self)
        esc.activated.connect(self._on_stop)

    def _on_continue(self):
        if self._ball and hasattr(self._ball, "_start_voice_from_ball"):
            self._ball._start_voice_from_ball()

    def _on_stop(self):
        e = getattr(self, "_stop_event", None)
        if e:
            e.set()
        self.hide()

    def set_listening(self):
        self._status.setText("◉ 正在听…")
        self._text.setText("")

    def set_partial(self, text):
        self._status.setText("◉ 识别中")
        self._text.setText(text[:80] + ("…" if len(text) > 80 else ""))

    def set_final(self, text):
        self._status.setText("你说")
        self._text.setText(text[:100] + ("…" if len(text) > 100 else ""))
        if text and text.strip():
            self._chat.appendPlainText("你: " + text.strip())
            self._scroll_chat_to_bottom()

    def set_response(self, text):
        if text and text.strip():
            self._chat.appendPlainText("CC: " + text.strip())
            self._scroll_chat_to_bottom()

    def _scroll_chat_to_bottom(self):
        sb = self._chat.verticalScrollBar()
        if sb:
            sb.setValue(sb.maximum())

    def set_error(self, msg):
        self._status.setText("")
        self._text.setText(msg[:70] if msg else "")

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        p.setRenderHint(QPainter.SmoothPixmapTransform, True)
        # 玻璃质感：高透明、渐变、细描边
        r = self.rect().adjusted(1, 1, -1, -1)
        grad = QLinearGradient(0, 0, 0, self.height())
        grad.setColorAt(0, QColor(100, 130, 180, 85))
        grad.setColorAt(0.5, QColor(60, 85, 130, 65))
        grad.setColorAt(1, QColor(40, 60, 100, 75))
        p.setBrush(grad)
        p.setPen(QPen(QColor(255, 255, 255, 90), 1))
        p.drawRoundedRect(r, 14, 14)
        # 玻璃高光边
        p.setPen(QPen(QColor(255, 255, 255, 45), 1))
        p.setBrush(Qt.NoBrush)
        p.drawRoundedRect(r.adjusted(2, 2, -2, -2), 12, 12)
        p.end()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            child = self.childAt(event.pos())
            if child in (self._stop_btn, self._continue_btn):
                event.ignore()
                return
            self._drag_start = event.globalPos() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if getattr(self, "_drag_start", None) is not None and event.buttons() & Qt.LeftButton:
            self.move(event.globalPos() - self._drag_start)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_start = None

    def showEvent(self, event):
        super().showEvent(event)
        self.activateWindow()
        self.raise_()


class FridayVoiceDialog(QWidget):
    """语音浮层：录音→识别→调用 do.py，电脑端以快捷键/点击触发。"""
    def __init__(self, ball, parent=None):
        super().__init__(parent)
        self._ball = ball
        self.setWindowTitle("Friday 语音")
        self.setFixedSize(420, 280)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self._drag_start = None
        self._asr_worker = None
        self._stop_event = None
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(12)
        title = QLabel("语音 · Ctrl+Shift+V")
        title.setStyleSheet("color: rgb(255,210,90); font-size: 14px; font-weight: 600; background: transparent;")
        layout.addWidget(title)
        self._status = QLabel("点击「开始录音」或按 Ctrl+Shift+V")
        self._status.setWordWrap(True)
        self._status.setStyleSheet("color: rgb(255,220,110); font-size: 13px; padding: 8px; background: rgba(65,65,80,0.95); border-radius: 8px; min-height: 80px;")
        layout.addWidget(self._status, 1)
        btn_ss = (
            "QPushButton { color: rgb(255,210,90); background: rgba(255,180,60,0.25); "
            "border: 1px solid rgb(255,170,50); border-radius: 6px; padding: 8px 16px; font-weight: 600; }"
            "QPushButton:hover { background: rgba(255,170,50,0.4); }"
            "QPushButton:disabled { color: rgb(150,130,70); }"
        )
        self._start_btn = QPushButton("开始录音")
        self._start_btn.setCursor(Qt.PointingHandCursor)
        self._start_btn.setStyleSheet(btn_ss)
        self._start_btn.clicked.connect(self._on_start)
        self._stop_btn = QPushButton("结束")
        self._stop_btn.setCursor(Qt.PointingHandCursor)
        self._stop_btn.setStyleSheet(btn_ss)
        self._stop_btn.clicked.connect(self._on_stop)
        self._stop_btn.setEnabled(False)
        row = QHBoxLayout()
        row.addWidget(self._start_btn)
        row.addWidget(self._stop_btn)
        layout.addLayout(row)
        close_btn = QPushButton("关闭")
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setStyleSheet(btn_ss)
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn, 0, Qt.AlignCenter)

    def _on_start(self):
        sys.path.insert(0, SCRIPTS)
        try:
            from xunfei_config_loader import is_configured
            from xunfei_asr_service import HAS_SOUNDDEVICE, HAS_WEBSOCKET
        except Exception:
            self._status.setText("讯飞语音未配置或依赖缺失。请复制 config/xunfei_config.example.json 到 runtime/config/xunfei_config.json 并填入密钥，安装: pip install websocket-client sounddevice numpy")
            return
        if not is_configured():
            self._status.setText("请配置讯飞 API：复制 config/xunfei_config.example.json 到 runtime/config/xunfei_config.json 并填入 app_id、api_key、api_secret")
            return
        if not HAS_SOUNDDEVICE or not HAS_WEBSOCKET:
            self._status.setText("请安装: pip install websocket-client sounddevice numpy")
            return
        self._stop_event = __import__("threading").Event()
        self._start_btn.setEnabled(False)
        self._stop_btn.setEnabled(True)
        self._status.setText("正在录音… 说完后点击「结束」")
        self._asr_worker = VoiceAsrWorker(self._stop_event, duration_sec=60)
        self._asr_worker.partial_signal.connect(self._on_partial)
        self._asr_worker.finished_signal.connect(self._on_finished)
        self._asr_worker.start()

    def _on_partial(self, text):
        if text:
            self._status.setText("识别中: " + (text[:80] + "…" if len(text) > 80 else text))

    def _on_stop(self):
        if self._stop_event:
            self._stop_event.set()
        self._stop_btn.setEnabled(False)
        self._status.setText("正在识别…")

    def _on_finished(self, text):
        self._asr_worker = None
        self._start_btn.setEnabled(True)
        self._stop_btn.setEnabled(False)
        if not text or not text.strip():
            self._status.setText("未识别到内容，请重试。")
            return
        self._status.setText("已识别: " + text[:100] + ("…" if len(text) > 100 else ""))
        # 调用 do.py
        try:
            r = subprocess.run(
                [sys.executable, os.path.join(SCRIPTS, "do.py"), text.strip()],
                cwd=ROOT,
                capture_output=True,
                text=True,
                timeout=120,
                encoding="utf-8",
                errors="replace",
            )
            out = (r.stdout or "").strip()[:200]
            if out:
                self._status.setText("执行结果: " + out)
        except Exception as e:
            self._status.setText("执行异常: " + str(e)[:80])

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        p.setPen(QPen(QColor(255, 180, 50, 220), 1))
        p.setBrush(QColor(58, 58, 72, 252))
        p.drawRoundedRect(1, 1, self.width() - 2, self.height() - 2, 12, 12)
        p.end()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_start = event.globalPos() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if getattr(self, "_drag_start", None) is not None and event.buttons() & Qt.LeftButton:
            self.move(event.globalPos() - self._drag_start)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_start = None


class EvolutionLoopWorker(QThread):
    """后台线程：调用 evolution_loop_client 向 CCR 提交一轮进化环，不阻塞悬浮球。"""
    finished_signal = pyqtSignal(bool, object)

    def __init__(self, parent=None, user_hint=None, auto_evolution=False):
        super().__init__(parent)
        self._user_hint = (user_hint or "").strip()
        self._auto_evolution = bool(auto_evolution)

    def run(self):
        hint_file = None
        try:
            cmd = [
                sys.executable,
                os.path.join(SCRIPTS, "evolution_loop_client.py"),
                "--once",
            ]
            if self._auto_evolution:
                cmd.append("--auto-evolution")
            if self._user_hint:
                config_dir = os.path.join(ROOT, "runtime", "config")
                os.makedirs(config_dir, exist_ok=True)
                hint_file = os.path.join(config_dir, "evolution_user_hint.txt")
                try:
                    with open(hint_file, "w", encoding="utf-8") as f:
                        f.write(self._user_hint)
                    cmd.extend(["--user-hint-file", hint_file])
                except Exception:
                    pass
            # 子进程超时须 >= evolution_loop_client 内 HTTP 等待时间，否则 client 未返回就被 kill，状态一直为 timeout
            sub_timeout = 380
            try:
                cfg_path = os.path.join(ROOT, "runtime", "config", "evolution_loop.json")
                if os.path.isfile(cfg_path):
                    with open(cfg_path, "r", encoding="utf-8") as f:
                        cfg = json.load(f)
                    req_t = max(60, int(cfg.get("request_timeout_seconds") or 300))
                    sub_timeout = req_t + 120
            except Exception:
                pass
            proc = subprocess.run(
                cmd,
                cwd=ROOT,
                capture_output=True,
                text=True,
                timeout=sub_timeout,
                encoding="utf-8",
                errors="replace",
            )
            ok = proc.returncode == 0
            result = {"stdout": proc.stdout or "", "stderr": proc.stderr or ""}
            self.finished_signal.emit(ok, result)
        except subprocess.TimeoutExpired:
            self.finished_signal.emit(False, {"error": "timeout"})
        except Exception as e:
            self.finished_signal.emit(False, {"error": str(e)})
        finally:
            if hint_file and os.path.isfile(hint_file):
                try:
                    os.remove(hint_file)
                except Exception:
                    pass


class FridayBall(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Friday")
        self.setFixedSize(SIZE, SIZE)
        self.setWindowFlags(
            Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
            | Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_ShowWithoutActivating, True)
        self._drag_start = None  # 左键拖拽移动
        # 圆形裁剪
        self.setMask(QRegion(0, 0, SIZE, SIZE, QRegion.Ellipse))
        # 动画：平时不转，仅等待时转（进化环、OneCall 等）
        self._angle = 0.0
        self._pulse = 0.0
        self._spinning = False
        self._state = load_state()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(50)
        self._state_timer = QTimer(self)
        self._state_timer.timeout.connect(self._load_state)
        self._state_timer.start(1000)
        self._evolution_worker = None
        self._auto_evolution_enabled = False
        self._title = QLabel("FRIDAY", self)
        self._title.setAlignment(Qt.AlignCenter)
        self._title.setStyleSheet(
            "color: rgb(255,200,80); font-size: 16px; letter-spacing: 5px; font-weight: 600; background: transparent;"
        )
        self._title.setGeometry(0, CENTER - 58, SIZE, 26)
        self._phase = QLabel("", self)
        self._phase.setAlignment(Qt.AlignCenter)
        self._phase.setStyleSheet(
            "color: rgb(255,200,80); font-size: 13px; font-weight: 500; background: rgba(255,180,50,0.25); "
            "border: 1px solid rgb(255,170,40); border-radius: 999px; padding: 3px 10px;"
        )
        self._phase.setGeometry(0, CENTER - 30, SIZE, 24)
        self._mission = QLabel("", self)
        self._mission.setAlignment(Qt.AlignCenter)
        self._mission.setWordWrap(True)
        self._mission.setStyleSheet(
            "color: rgb(255,210,100); font-size: 13px; font-weight: 500; background: transparent;"
        )
        self._mission.setGeometry(12, CENTER - 4, SIZE - 24, 24)
        # 底部：轮次 + 双击提示（过程/结果改由弹框展示）
        self._round = QLabel("", self)
        self._round.setAlignment(Qt.AlignCenter)
        self._round.setStyleSheet(
            "color: rgb(240,185,70); font-size: 12px; font-weight: 500; background: transparent;"
        )
        self._round.setGeometry(0, CENTER + 14, SIZE, 20)
        self._hint = QLabel("单击语音 · 双击过程", self)
        self._hint.setAlignment(Qt.AlignCenter)
        self._hint.setStyleSheet(
            "color: rgb(255,180,60); font-size: 10px; font-weight: 500; background: transparent;"
        )
        self._hint.setGeometry(0, CENTER + 36, SIZE, 18)
        # 自动进化环：下一次倒计时 + 上一轮完成状态（轻量展示）
        self._auto_info = QLabel("", self)
        self._auto_info.setAlignment(Qt.AlignCenter)
        self._auto_info.setStyleSheet(
            "color: rgb(235,190,85); font-size: 10px; font-weight: 500; background: transparent;"
        )
        self._auto_info.setGeometry(0, CENTER + 54, SIZE, 16)
        self._next_auto_at = None  # epoch seconds
        self._last_auto_ui_sec = 0
        self._stuck_edge = None
        self._onecall_dialog = None
        self._voice_overlay = None
        self._voice_asr_worker = None
        self._voice_stop_event = None
        self._press_pos = None
        self._click_timer = QTimer(self)
        self._click_timer.setSingleShot(True)
        self._click_timer.timeout.connect(self._start_voice_from_ball)
        # 应用级快捷键（本应用前台时有效）
        s1 = QShortcut(QKeySequence("Ctrl+Shift+S"), self)
        s1.setContext(Qt.ApplicationShortcut)
        s1.activated.connect(self._on_shortcut_full_screenshot)
        s2 = QShortcut(QKeySequence("Ctrl+Shift+Q"), self)
        s2.setContext(Qt.ApplicationShortcut)
        s2.activated.connect(self._on_shortcut_region_capture)
        s3 = QShortcut(QKeySequence("Ctrl+Shift+V"), self)
        s3.setContext(Qt.ApplicationShortcut)
        s3.activated.connect(self._on_shortcut_voice)
        self._voice_dialog = None
        self._apply_state()
        # Windows 全局热键（其他应用前台时也能响应）
        if HAS_GLOBAL_HOTKEY:
            QTimer.singleShot(400, self._register_global_hotkeys)

    def _stick_to_edge(self, pos):
        """拖拽释放时若靠近屏幕边缘则吸附，只露出 EDGE_STICK_W 宽条。"""
        screen = QDesktopWidget().availableGeometry()
        x, y = pos.x(), pos.y()
        margin = EDGE_MARGIN
        if x >= screen.width() - SIZE - margin:
            return ("right", screen.width() - EDGE_STICK_W, y)
        if x <= margin:
            return ("left", 0, y)
        if y >= screen.height() - SIZE - margin:
            return ("bottom", x, screen.height() - EDGE_STICK_W)
        if y <= margin:
            return ("top", x, 0)
        return None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._press_pos = event.globalPos()
            if self._stuck_edge:
                self._unstick()
            else:
                self._drag_start = event.globalPos() - self.frameGeometry().topLeft()

    def _unstick(self):
        self._stuck_edge = None
        self.setFixedSize(SIZE, SIZE)
        self.setMask(QRegion(0, 0, SIZE, SIZE, QRegion.Ellipse))
        self._title.show()
        self._phase.show()
        self._mission.show()
        self._round.show()
        self._hint.show()
        self._auto_info.show()
        self._hint.setText("单击语音 · 双击过程")
        self._hint.setGeometry(0, CENTER + 36, SIZE, 18)
        screen = QDesktopWidget().availableGeometry()
        x = min(max(self.x(), 0), screen.width() - SIZE)
        y = min(max(self.y(), 0), screen.height() - SIZE)
        self.move(x, y)

    def mouseMoveEvent(self, event):
        if self._stuck_edge:
            return
        if self._drag_start is not None and event.buttons() & Qt.LeftButton:
            self.move(event.globalPos() - self._drag_start)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            # 区分点击与拖拽：位移 < 8px 视为点击
            is_click = (
                self._press_pos is not None
                and (event.globalPos() - self._press_pos).manhattanLength() < 8
            )
            self._press_pos = None
            if not self._stuck_edge and self._drag_start is not None:
                if is_click:
                    self._on_ball_clicked()
                else:
                    stick = self._stick_to_edge(self.pos())
                    if stick:
                        edge, nx, ny = stick
                        self._stuck_edge = edge
                        self.setFixedSize(EDGE_STICK_W, EDGE_STICK_W)
                        self.setMask(QRegion(0, 0, EDGE_STICK_W, EDGE_STICK_W, QRegion.Ellipse))
                        self.move(nx, ny)
                        self._title.hide()
                        self._phase.hide()
                        self._mission.hide()
                        self._round.hide()
                        self._hint.hide()
                        self._auto_info.hide()
            self._drag_start = None

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._click_timer.stop()
            d = FridayLogDialog(self)
            d.move(self._dialog_pos(LOG_DIALOG_W, LOG_DIALOG_H))
            d.show()

    def _dialog_pos(self, w, h):
        """弹框位置：尽量在球下方，不超出屏幕"""
        screen = QDesktopWidget().availableGeometry()
        g = self.frameGeometry()
        cx = g.x() + (g.width() - w) // 2
        cy = g.y() + g.height() + 8
        if cy + h > screen.bottom():
            cy = g.y() - h - 8
        if cx < screen.left():
            cx = screen.left()
        if cx + w > screen.right():
            cx = screen.right() - w
        return QPoint(cx, cy)

    def _show_onecall(self):
        if self._onecall_dialog is None or not self._onecall_dialog.isVisible():
            self._onecall_dialog = FridayMultimodalDialog(self)
        self._onecall_dialog.move(self._dialog_pos(ONECALL_W, ONECALL_H))
        self._onecall_dialog.show()
        self._onecall_dialog.raise_()
        self._onecall_dialog.activateWindow()

    def _on_ball_clicked(self):
        """左键单击悬浮球：延迟判定，避免与双击冲突；单击=语音，双击=日志"""
        self._click_timer.start(220)

    def _start_voice_from_ball(self):
        """开始语音：显示浮层、启动 ASR、网格旋转"""
        if self._voice_asr_worker is not None and self._voice_asr_worker.isRunning():
            return
        sys.path.insert(0, SCRIPTS)
        try:
            from xunfei_config_loader import is_configured
            from xunfei_asr_service import HAS_SOUNDDEVICE, HAS_WEBSOCKET
        except Exception:
            tray = getattr(self, "_tray", None)
            if tray and hasattr(tray, "showMessage"):
                tray.showMessage("Friday", "讯飞语音未配置或依赖缺失。pip install websocket-client sounddevice numpy", QSystemTrayIcon.Warning, 4000)
            return
        if not is_configured():
            tray = getattr(self, "_tray", None)
            if tray and hasattr(tray, "showMessage"):
                tray.showMessage("Friday", "请配置讯飞 API：复制 config/xunfei_config.example.json 到 runtime/config/xunfei_config.json", QSystemTrayIcon.Warning, 4000)
            return
        if not HAS_SOUNDDEVICE or not HAS_WEBSOCKET:
            tray = getattr(self, "_tray", None)
            if tray and hasattr(tray, "showMessage"):
                tray.showMessage("Friday", "请安装: pip install websocket-client sounddevice numpy", QSystemTrayIcon.Warning, 4000)
            return
        self._voice_stop_event = __import__("threading").Event()
        if self._voice_overlay is None or not self._voice_overlay.isVisible():
            self._voice_overlay = VoiceOverlayWidget(self)
        self._voice_overlay._stop_event = self._voice_stop_event
        self._voice_overlay.set_listening()
        self._voice_overlay.activateWindow()
        self._voice_overlay.raise_()
        screen = QDesktopWidget().availableGeometry()
        ox = screen.center().x() - VOICE_OVERLAY_W // 2
        oy = screen.center().y() - VOICE_OVERLAY_H // 2
        self._voice_overlay.move(max(screen.left(), min(ox, screen.right() - VOICE_OVERLAY_W)),
                                max(screen.top(), min(oy, screen.bottom() - VOICE_OVERLAY_H)))
        self._voice_overlay.show()
        self._voice_overlay.raise_()
        self._set_spinning(True)
        self._voice_asr_worker = VoiceAsrWorker(self._voice_stop_event, duration_sec=60)
        self._voice_asr_worker.partial_signal.connect(self._on_voice_partial)
        self._voice_asr_worker.finished_signal.connect(self._on_voice_finished)
        self._voice_asr_worker.start()

    def _on_voice_partial(self, text):
        if self._voice_overlay and self._voice_overlay.isVisible():
            self._voice_overlay.set_partial(text)

    def _auto_restart_voice(self):
        """AI 返回后自动开始下一轮录音，无需点击"""
        if self._voice_overlay and self._voice_overlay.isVisible():
            QTimer.singleShot(400, self._start_voice_from_ball)

    def _on_voice_finished(self, text):
        self._voice_asr_worker = None
        self._set_spinning(False)
        if not self._voice_overlay or not self._voice_overlay.isVisible():
            return
        if not text or not text.strip():
            self._voice_overlay.set_error("未识别到内容")
            self._auto_restart_voice()
            return
        self._voice_overlay.set_final(text)
        try:
            r = subprocess.run(
                [sys.executable, os.path.join(SCRIPTS, "do.py"), text.strip()],
                cwd=ROOT,
                capture_output=True,
                text=True,
                timeout=120,
                encoding="utf-8",
                errors="replace",
            )
            out = (r.stdout or "").strip()
            if out:
                self._voice_overlay.set_response(out[:300])
                self._auto_restart_voice()
            elif r.returncode != 0:
                self._voice_overlay.set_response("do.py 执行失败，尝试多模态…")
                self._voice_overlay._continue_btn.setEnabled(False)
                self._voice_vision_worker = VoiceVisionFallbackWorker(text.strip())
                self._voice_vision_worker.finished_signal.connect(self._on_voice_vision_finished)
                self._voice_vision_worker.start()
            else:
                self._voice_overlay.set_response("执行完成")
                self._auto_restart_voice()
        except Exception as e:
            self._voice_overlay.set_response("执行异常: " + str(e)[:80])
            self._auto_restart_voice()

    def _on_voice_vision_finished(self, result):
        self._voice_vision_worker = None
        if self._voice_overlay and self._voice_overlay.isVisible():
            self._voice_overlay.set_response(result)
            self._voice_overlay._continue_btn.setEnabled(True)
            self._auto_restart_voice()

    def _show_voice(self):
        """快捷键/菜单：同左键点击，打开浮层并开始录音"""
        self._start_voice_from_ball()

    def _on_shortcut_voice(self):
        self._show_voice()

    def _on_shortcut_full_screenshot(self):
        self._show_onecall()
        QTimer.singleShot(120, self._trigger_full_screenshot)

    def _trigger_full_screenshot(self):
        if self._onecall_dialog and self._onecall_dialog.isVisible():
            self._onecall_dialog._do_full_screenshot()

    def _on_shortcut_region_capture(self):
        self._show_onecall()
        QTimer.singleShot(120, self._trigger_region_capture)

    def _trigger_region_capture(self):
        if self._onecall_dialog and self._onecall_dialog.isVisible():
            self._onecall_dialog._do_region_capture()

    def _register_global_hotkeys(self):
        if not HAS_GLOBAL_HOTKEY:
            return
        try:
            hwnd = int(self.winId())
            mod = MOD_CONTROL | MOD_SHIFT
            if _win_RegisterHotKey(hwnd, HOTKEY_ID_FULL, mod, VK_S):
                pass
            if _win_RegisterHotKey(hwnd, HOTKEY_ID_REGION, mod, VK_Q):
                pass
            if _win_RegisterHotKey(hwnd, HOTKEY_ID_VOICE, mod, VK_V):
                pass
        except Exception:
            pass

    def nativeEvent(self, eventType, message):
        if HAS_GLOBAL_HOTKEY and eventType in (b"windows_generic_MSG", b"windows_dispatcher_MSG") and message:
            try:
                try:
                    ptr_val = int(message)
                except (TypeError, ValueError):
                    ptr_val = getattr(message, "value", None) or getattr(message, "as_c_void_p", lambda: None)()
                    ptr_val = getattr(ptr_val, "value", ptr_val) if ptr_val is not None else 0
                if not ptr_val:
                    return super().nativeEvent(eventType, message)
                class MSG(ctypes.Structure):
                    _fields_ = [
                        ("hwnd", ctypes.wintypes.HWND),
                        ("message", ctypes.c_uint),
                        ("wParam", ctypes.wintypes.WPARAM),
                        ("lParam", ctypes.wintypes.LPARAM),
                        ("time", ctypes.c_ulong),
                        ("pt", ctypes.wintypes.POINT),
                    ]
                ptr = ctypes.c_void_p(ptr_val)
                msg = ctypes.cast(ptr, ctypes.POINTER(MSG)).contents
                if msg.message == WM_HOTKEY:
                    if msg.wParam == HOTKEY_ID_FULL:
                        QTimer.singleShot(0, self._on_shortcut_full_screenshot)
                        return True, 0
                    if msg.wParam == HOTKEY_ID_REGION:
                        QTimer.singleShot(0, self._on_shortcut_region_capture)
                        return True
                    if msg.wParam == HOTKEY_ID_VOICE:
                        QTimer.singleShot(0, self._on_shortcut_voice)
                        return True, 0
            except Exception:
                pass
        return super().nativeEvent(eventType, message)

    def closeEvent(self, event):
        if HAS_GLOBAL_HOTKEY:
            try:
                hwnd = int(self.winId())
                _win_UnregisterHotKey(hwnd, HOTKEY_ID_FULL)
                _win_UnregisterHotKey(hwnd, HOTKEY_ID_REGION)
                _win_UnregisterHotKey(hwnd, HOTKEY_ID_VOICE)
            except Exception:
                pass
        super().closeEvent(event)

    def contextMenuEvent(self, event):
        """窗口内右键弹出菜单"""
        menu = QMenu(self)
        proc_act = QAction("过程 · 结果", self)
        proc_act.triggered.connect(self._show_log_dialog)
        menu.addAction(proc_act)
        onecall_act = QAction("OneCall · 多模态", self)
        onecall_act.triggered.connect(self._show_onecall)
        menu.addAction(onecall_act)
        voice_act = QAction("开始语音 (Ctrl+Shift+V)", self)
        voice_act.triggered.connect(self._show_voice)
        menu.addAction(voice_act)
        menu.addSeparator()
        evolution_act = QAction("提交一轮进化环", self)
        evolution_act.triggered.connect(lambda: self._trigger_evolution_loop(None))
        menu.addAction(evolution_act)
        auto_evolution_act = QAction("开启自动进化环" if not self._auto_evolution_enabled else "关闭自动进化环", self)
        auto_evolution_act.triggered.connect(self._toggle_auto_evolution)
        menu.addAction(auto_evolution_act)
        ack_act = QAction("清除进化环超时状态（CC 已跑完时）", self)
        ack_act.triggered.connect(self._ack_evolution_timeout)
        menu.addAction(ack_act)
        menu.addSeparator()
        quit_act = QAction("退出", self)
        quit_act.triggered.connect(self._quit_app)
        menu.addAction(quit_act)
        menu.exec_(event.globalPos())

    def _show_log_dialog(self):
        d = FridayLogDialog(self)
        d.move(self._dialog_pos(LOG_DIALOG_W, LOG_DIALOG_H))
        d.show()

    def _trigger_evolution_loop(self, user_hint=None):
        """提交一轮进化环：可选用户补充需求，在后台线程调用 CCR /api/agent，不阻塞 UI。"""
        if self._evolution_worker is not None and self._evolution_worker.isRunning():
            tray = getattr(self, "_tray", None)
            if tray and hasattr(tray, "showMessage"):
                tray.showMessage("Friday", "上一轮进化环仍在请求中，请稍候。", QSystemTrayIcon.Warning, 3000)
            return
        if not can_submit_evolution():
            tray = getattr(self, "_tray", None)
            if tray and hasattr(tray, "showMessage"):
                tray.showMessage("Friday", "上一轮会话尚未完成（evolution_completed 未写入），请等待完成后再提交。", QSystemTrayIcon.Warning, 5000)
            return
        # 若上一轮刚超时，提示 CC 可能仍在执行，避免误开新会话
        status, at, _ = load_evolution_last_status()
        if status == "timeout" and at:
            try:
                from datetime import datetime, timezone
                s = at.replace("Z", "+00:00")
                dt = datetime.fromisoformat(s)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                elapsed = (datetime.now(timezone.utc) - dt).total_seconds()
                if 0 < elapsed < 300:  # 5 分钟内不提交，避免 CC 侧多会话
                    tray = getattr(self, "_tray", None)
                    if tray and hasattr(tray, "showMessage"):
                        tray.showMessage("Friday", "上一轮请求已超时，CC 可能仍在执行；若现在提交会开启新会话。", QSystemTrayIcon.Warning, 5000)
            except Exception:
                pass
        if user_hint is None:
            text, ok = QInputDialog.getText(
                self,
                "进化环",
                "本轮补充需求（可选，留空则完全按 workflow 自主假设）：",
            )
            if not ok:
                return
            user_hint = (text or "").strip()
        self._evolution_worker = EvolutionLoopWorker(self, user_hint=user_hint or None)
        self._evolution_worker.finished_signal.connect(self._on_evolution_finished)
        self._evolution_worker.start()
        self._set_spinning(True)
        self._phase.setText("进化环提交中…")
        tray = getattr(self, "_tray", None)
        if tray and hasattr(tray, "showMessage"):
            tray.showMessage("Friday", "已向 Claude Code 提交一轮进化环，请稍候。", QSystemTrayIcon.Information, 3000)

    def _schedule_auto_evolution(self):
        """定时触发一轮进化环（仅当已开启自动进化环且当前无任务时）。"""
        if not getattr(self, "_auto_evolution_enabled", False):
            return
        if self._evolution_worker is not None and self._evolution_worker.isRunning():
            # 当前仍在执行：仅做“检查”调度，不改写 _next_auto_at，倒计时继续指向“下次触发”时间（到 0 后保持 00:00）
            QTimer.singleShot(10000, self._schedule_auto_evolution)
            return
        if not can_submit_evolution():
            QTimer.singleShot(60000, self._schedule_auto_evolution)
            self._next_auto_at = time.time() + 60
            return
        # 若上一轮刚超时，5 分钟内每分钟检查一次；若发现下方日志已有 decide（CC 已跑完）则提前结束冷却并提交下一轮
        status, at, _ = load_evolution_last_status()
        if status == "timeout" and at:
            try:
                from datetime import datetime, timezone
                s = at.replace("Z", "+00:00")
                dt = datetime.fromisoformat(s)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                elapsed = (datetime.now(timezone.utc) - dt).total_seconds()
                if 0 < elapsed < 300:
                    if _cc_completed_after_timeout(at):
                        try:
                            os.makedirs(os.path.dirname(EVOLUTION_LAST_STATUS_FILE), exist_ok=True)
                            with open(EVOLUTION_LAST_STATUS_FILE, "w", encoding="utf-8") as f:
                                json.dump({
                                    "status": "ok",
                                    "at": datetime.now(timezone.utc).isoformat(),
                                    "message": "auto_reconcile: decide_seen_after_timeout",
                                }, f, ensure_ascii=False, indent=2)
                        except Exception:
                            pass
                        # 不 return，继续往下发起下一轮
                    else:
                        QTimer.singleShot(60000, self._schedule_auto_evolution)
                        self._next_auto_at = time.time() + 60
                        return
            except Exception:
                pass
        # 每次设定下一轮时从配置文件读取间隔（非启动时读一次），0 表示默认 300 秒
        config_path = os.path.join(ROOT, "runtime", "config", "evolution_loop.json")
        interval = 300
        try:
            if os.path.isfile(config_path):
                with open(config_path, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                interval = max(60, int(cfg.get("auto_interval_seconds") or 300))
        except Exception:
            pass
        # 自动进化环带 --auto-evolution：客户端会拼上一轮 track/decide 与已完成项，减少重复
        self._evolution_worker = EvolutionLoopWorker(self, user_hint=None, auto_evolution=True)
        self._evolution_worker.finished_signal.connect(self._on_evolution_finished)
        self._evolution_worker.start()
        self._set_spinning(True)
        self._phase.setText("自动进化环提交中…")
        tray = getattr(self, "_tray", None)
        if tray and hasattr(tray, "showMessage"):
            tray.showMessage("Friday", "【自动进化】已提交一轮；倒计时为下次循环触发时间。", QSystemTrayIcon.Information, 3000)
        QTimer.singleShot(interval * 1000, self._schedule_auto_evolution)
        self._next_auto_at = time.time() + interval

    def _ack_evolution_timeout(self):
        """上一轮 HTTP 超时但 CC 已在后台跑完时，清除 evolution_last_status 的 timeout，自动环可立即再提交。"""
        try:
            r = subprocess.run(
                [sys.executable, os.path.join(SCRIPTS, "evolution_loop_client.py"), "--ack-complete"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                timeout=15,
                encoding="utf-8",
                errors="replace",
            )
            tray = getattr(self, "_tray", None)
            if r.returncode == 0 and tray and hasattr(tray, "showMessage"):
                tray.showMessage("Friday", "已清除超时状态；自动进化环可正常继续提交。", QSystemTrayIcon.Information, 4000)
            elif tray and hasattr(tray, "showMessage"):
                tray.showMessage("Friday", "清除失败，可手动运行: python scripts/evolution_loop_client.py --ack-complete", QSystemTrayIcon.Warning, 5000)
        except Exception as e:
            tray = getattr(self, "_tray", None)
            if tray and hasattr(tray, "showMessage"):
                tray.showMessage("Friday", "清除超时状态异常: %s" % str(e)[:60], QSystemTrayIcon.Warning, 4000)

    def _toggle_auto_evolution(self):
        """开启/关闭自动进化环：定时触发没在工作的 CC 执行进化。"""
        self._auto_evolution_enabled = not self._auto_evolution_enabled
        tray = getattr(self, "_tray", None)
        if self._auto_evolution_enabled:
            if tray and hasattr(tray, "showMessage"):
                tray.showMessage("Friday", "已开启自动进化环；倒计时为下次触发时间（首轮约 2 秒后提交）。", QSystemTrayIcon.Information, 4000)
            QTimer.singleShot(2000, self._schedule_auto_evolution)
            self._next_auto_at = time.time() + 2
        else:
            if tray and hasattr(tray, "showMessage"):
                tray.showMessage("Friday", "已关闭自动进化环。", QSystemTrayIcon.Information, 2000)
            self._next_auto_at = None

    def _on_evolution_finished(self, ok, result):
        self._evolution_worker = None
        self._set_spinning(False)
        err = result.get("error") or ""
        stderr = (result.get("stderr") or "").lower()
        is_timeout = (
            err == "timeout"
            or "timed out" in str(err).lower()
            or "timed out" in stderr
            or (not ok and "timeout" in stderr)
        )
        # 写入最近状态（含 worker 侧超时，因客户端被 kill 时不会写）
        try:
            from datetime import datetime, timezone
            os.makedirs(os.path.dirname(EVOLUTION_LAST_STATUS_FILE), exist_ok=True)
            status = "ok" if ok else ("timeout" if is_timeout else "error")
            with open(EVOLUTION_LAST_STATUS_FILE, "w", encoding="utf-8") as f:
                json.dump({
                    "status": status,
                    "at": datetime.now(timezone.utc).isoformat(),
                    "message": (err or result.get("stderr") or "")[:200],
                }, f, ensure_ascii=False, indent=2)
        except Exception:
            pass
        self._load_state()
        # 自动进化开启时：下一轮在 interval 秒后触发（设定倒计时并真正预约下一轮，否则只靠 10s 轮询会过早触发）
        if getattr(self, "_auto_evolution_enabled", False):
            interval = 300
            try:
                cfg_path = os.path.join(ROOT, "runtime", "config", "evolution_loop.json")
                if os.path.isfile(cfg_path):
                    with open(cfg_path, "r", encoding="utf-8") as f:
                        interval = max(60, int(json.load(f).get("auto_interval_seconds") or 300))
            except Exception:
                pass
            self._next_auto_at = time.time() + interval
            QTimer.singleShot(interval * 1000, self._schedule_auto_evolution)
        tray = getattr(self, "_tray", None)
        if tray and hasattr(tray, "showMessage"):
            if ok:
                tray.showMessage("Friday", "【自动进化】本轮已完成；下一轮将按间隔倒计时触发。", QSystemTrayIcon.Information, 4000)
            elif is_timeout:
                tray.showMessage("Friday", "进化环请求超时，CC 可能仍在执行，请勿急于再提交。", QSystemTrayIcon.Warning, 6000)
            else:
                err_display = err or (result.get("stderr") or "")[:80]
                tray.showMessage("Friday", "进化环失败: %s" % err_display, QSystemTrayIcon.Warning, 5000)

    def _quit_app(self):
        QApplication.quit()

    def _load_state(self):
        self._state = load_state()
        self._apply_state()

    def _apply_state(self):
        s = self._state
        self._phase.setText((s.get("phase") or "—").strip())
        mission = (s.get("mission") or "—").strip()
        if len(mission) > 24:
            mission = mission[:22] + "…"
        self._mission.setText(mission)
        r = s.get("loop_round") or 0
        self._round.setText("第 {} 轮".format(r) if r > 0 else "")
        self._title.setText("FRIDAY")
        self._update_auto_info(force=True)

    def _set_spinning(self, on):
        """控制悬浮球是否旋转：仅等待时转（进化环、OneCall 等）。"""
        self._spinning = bool(on)

    def _tick(self):
        if self._spinning:
            self._angle += 1.2
            if self._angle >= 360:
                self._angle -= 360
            self._pulse += 0.04
            if self._pulse >= 6.28318:
                self._pulse -= 6.28318
        self._update_auto_info()
        self.update()

    def _update_auto_info(self, force=False):
        """悬浮球底部小字：自动进化倒计时 + 上一轮状态（每秒刷新一次即可）。"""
        try:
            now = int(time.time())
            if not force and now == getattr(self, "_last_auto_ui_sec", 0):
                return
            self._last_auto_ui_sec = now
            # CC 是否仍在执行：以当前 worker 线程是否在跑为准
            is_running = bool(self._evolution_worker is not None and self._evolution_worker.isRunning())
            status, _, _ = load_evolution_last_status()
            if is_running:
                status_txt = "上轮:进行中"
            else:
                status_txt = "上轮:—"
                if status == "ok":
                    status_txt = "上轮:完成"
                elif status == "timeout":
                    status_txt = "上轮:超时"
                elif status == "error":
                    status_txt = "上轮:失败"

            if getattr(self, "_auto_evolution_enabled", False):
                if is_running:
                    # 运行中仍显示“下次触发”倒计时（到 0 后显示 00:00），不改为 10s 回跳
                    if self._next_auto_at:
                        left = int(max(0, self._next_auto_at - time.time()))
                        mm, ss = left // 60, left % 60
                        self._auto_info.setText("AUTO %02d:%02d | %s" % (mm, ss, status_txt))
                    else:
                        self._auto_info.setText("AUTO 运行中 | %s" % status_txt)
                elif self._next_auto_at:
                    left = int(max(0, self._next_auto_at - time.time()))
                    mm = left // 60
                    ss = left % 60
                    self._auto_info.setText("AUTO %02d:%02d | %s" % (mm, ss, status_txt))
                else:
                    self._auto_info.setText("AUTO --:-- | %s" % status_txt)
            else:
                self._auto_info.setText(status_txt)
        except Exception:
            pass

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        p.setRenderHint(QPainter.SmoothPixmapTransform, True)
        if self._stuck_edge:
            self._paint_stuck(p)
            return
        cx, cy = CENTER, CENTER
        # 薄纱透明底
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(255, 255, 255, 28))
        p.drawEllipse(0, 0, SIZE, SIZE)
        p.setBrush(Qt.NoBrush)
        R = int(SIZE * 0.38)
        base = int(SIZE * 0.22)
        # 贾维斯/星期五 HUD 风：金/琥珀细线网格+圆环
        pen_grid = QPen(QColor(255, 195, 70, 200))
        pen_grid.setWidth(1)
        p.setPen(pen_grid)
        for layer in range(2):
            p.save()
            p.translate(cx, cy)
            p.rotate(self._angle + (90 * layer))
            p.translate(-cx, -cy)
            for i in range(16):
                a = i * pi / 8
                dx, dy = R * cos(a), R * sin(a)
                p.drawLine(cx, cy, int(cx + dx), int(cy + dy))
            for r in [R * 0.35, R * 0.65, R]:
                p.drawEllipse(int(cx - r), int(cy - r), int(2 * r), int(2 * r))
            p.restore()
        pen_ring = QPen(QColor(255, 180, 50, 240))
        pen_ring.setWidth(1)
        p.setPen(pen_ring)
        for r, dr in [(base, 0), (base + 35, 5), (base + 70, -5)]:
            p.save()
            p.translate(cx, cy)
            p.rotate(self._angle + dr)
            p.translate(-cx, -cy)
            p.drawEllipse(cx - r, cy - r, r * 2, r * 2)
            p.restore()
        rad = int(SIZE * 0.12) + int(3 * (0.5 + 0.5 * cos(self._pulse)))
        grad = QRadialGradient(cx, cy, rad)
        grad.setColorAt(0, QColor(255, 210, 90, 240))
        grad.setColorAt(0.5, QColor(255, 170, 40, 180))
        grad.setColorAt(1, QColor(220, 140, 20, 100))
        p.setPen(Qt.NoPen)
        p.setBrush(grad)
        p.drawEllipse(int(cx - rad), int(cy - rad), int(rad * 2), int(rad * 2))
        p.end()

    def _paint_stuck(self, p):
        """吸边时绘制中号黄色半圆，根据边去掉一侧"""
        w, h = self.width(), self.height()
        r = min(w, h) * 0.45
        cx, cy = w / 2, h / 2
        path = QPainterPath()
        edge = self._stuck_edge or "right"
        if edge == "right":
            path.arcMoveTo(cx - r, cy - r, r * 2, r * 2, 90)
            path.arcTo(cx - r, cy - r, r * 2, r * 2, 90, 180)
        elif edge == "left":
            path.arcMoveTo(cx - r, cy - r, r * 2, r * 2, 270)
            path.arcTo(cx - r, cy - r, r * 2, r * 2, 270, 180)
        elif edge == "top":
            path.arcMoveTo(cx - r, cy - r, r * 2, r * 2, 180)
            path.arcTo(cx - r, cy - r, r * 2, r * 2, 180, 180)
        else:
            path.arcMoveTo(cx - r, cy - r, r * 2, r * 2, 0)
            path.arcTo(cx - r, cy - r, r * 2, r * 2, 0, 180)
        path.closeSubpath()
        p.setPen(Qt.NoPen)
        grad = QRadialGradient(cx, cy, r)
        grad.setColorAt(0, QColor(255, 220, 100, 240))
        grad.setColorAt(1, QColor(255, 170, 50, 200))
        p.setBrush(grad)
        p.drawPath(path)


def make_tray_icon():
    """贾维斯/星期五风：金/琥珀色圆点"""
    pm = QPixmap(24, 24)
    pm.fill(QColor(0, 0, 0, 0))
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing, True)
    p.setBrush(QColor(255, 195, 70, 240))
    p.setPen(Qt.NoPen)
    p.drawEllipse(2, 2, 20, 20)
    p.end()
    return QIcon(pm)


def main():
    if not HAS_QT:
        print("请安装 PyQt5: pip install PyQt5")
        sys.exit(1)
    os.chdir(ROOT)
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    w = FridayBall()
    # 托盘图标 + 右键菜单（退出）
    tray = QSystemTrayIcon(w)
    w._tray = tray
    tray.setIcon(make_tray_icon())
    tray.setToolTip("Friday 悬浮球 · 左键拖动 · 拖到边缘吸附 · 双击过程 · 右键 OneCall/退出")
    tray_menu = QMenu()
    quit_act = QAction("退出", tray)
    quit_act.triggered.connect(app.quit)
    tray_menu.addAction(quit_act)
    tray.setContextMenu(tray_menu)
    tray.show()
    # 居中
    screen = QDesktopWidget().availableGeometry()
    x = (screen.width() - SIZE) // 2
    y = (screen.height() - SIZE) // 2
    w.move(x, y)
    w.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
