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
        HOTKEY_ID_FULL = 9001
        HOTKEY_ID_REGION = 9002
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


def _format_evolution_status_line():
    """格式化为过程·结果弹框首行：最近进化环请求: 成功/超时/失败 (HH:MM)。"""
    status, at, msg = load_evolution_last_status()
    if not status:
        return None
    t = _format_log_time(at) if at else ""
    if status == "ok":
        return "最近进化环请求: 成功 (本轮已完成)" + (" " + t if t else "")
    if status == "timeout":
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
        # 不再清空结果区，只在按钮上显示执行中
        self._exec_btn.setText("执行中…")
        self._exec_btn.setEnabled(False)
        QApplication.processEvents()
        try:
            r = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=90)
            out = (r.stdout or "").strip()
            err = (r.stderr or "").strip()
            if r.returncode != 0:
                out = "错误: " + (err or str(r.returncode))
            self._call_history.append({"q": q[:50], "out": out, "mode": "coords" if is_coords else "proxy"})
            lines = []
            for h in reversed(self._call_history[-10:]):
                lines.append("【%s】%s" % (h["mode"], h["q"]))
                lines.append(h["out"])
                lines.append("—")
            self._result_label.setText("\n".join(lines) if lines else out)
            sb = self._result_scroll.verticalScrollBar()
            sb.setValue(sb.maximum())
        except Exception as e:
            self._result_label.setText("异常: " + str(e))
        finally:
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
            proc = subprocess.run(
                cmd,
                cwd=ROOT,
                capture_output=True,
                text=True,
                timeout=320,
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
        # 动画
        self._angle = 0.0
        self._pulse = 0.0
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
        self._hint = QLabel("双击 · 查看过程", self)
        self._hint.setAlignment(Qt.AlignCenter)
        self._hint.setStyleSheet(
            "color: rgb(255,180,60); font-size: 10px; font-weight: 500; background: transparent;"
        )
        self._hint.setGeometry(0, CENTER + 36, SIZE, 18)
        self._stuck_edge = None
        self._onecall_dialog = None
        # 应用级快捷键（本应用前台时有效）
        s1 = QShortcut(QKeySequence("Ctrl+Shift+S"), self)
        s1.setContext(Qt.ApplicationShortcut)
        s1.activated.connect(self._on_shortcut_full_screenshot)
        s2 = QShortcut(QKeySequence("Ctrl+Shift+Q"), self)
        s2.setContext(Qt.ApplicationShortcut)
        s2.activated.connect(self._on_shortcut_region_capture)
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
        self._hint.setText("双击 · 查看过程")
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
            if not self._stuck_edge and self._drag_start is not None:
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
            self._drag_start = None

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
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
        menu.addSeparator()
        evolution_act = QAction("提交一轮进化环", self)
        evolution_act.triggered.connect(lambda: self._trigger_evolution_loop(None))
        menu.addAction(evolution_act)
        auto_evolution_act = QAction("开启自动进化环" if not self._auto_evolution_enabled else "关闭自动进化环", self)
        auto_evolution_act.triggered.connect(self._toggle_auto_evolution)
        menu.addAction(auto_evolution_act)
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
                if 0 < elapsed < 900:  # 15 分钟内
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
        self._phase.setText("进化环提交中…")
        tray = getattr(self, "_tray", None)
        if tray and hasattr(tray, "showMessage"):
            tray.showMessage("Friday", "已向 Claude Code 提交一轮进化环，请稍候。", QSystemTrayIcon.Information, 3000)

    def _schedule_auto_evolution(self):
        """定时触发一轮进化环（仅当已开启自动进化环且当前无任务时）。"""
        if not getattr(self, "_auto_evolution_enabled", False):
            return
        if self._evolution_worker is not None and self._evolution_worker.isRunning():
            QTimer.singleShot(10000, self._schedule_auto_evolution)
            return
        # 若上一轮刚超时，本轮自动跳过，避免 CC 侧多会话堆积
        status, at, _ = load_evolution_last_status()
        if status == "timeout" and at:
            try:
                from datetime import datetime, timezone
                s = at.replace("Z", "+00:00")
                dt = datetime.fromisoformat(s)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                elapsed = (datetime.now(timezone.utc) - dt).total_seconds()
                if 0 < elapsed < 900:
                    QTimer.singleShot(60000, self._schedule_auto_evolution)  # 1 分钟后再检查
                    return
            except Exception:
                pass
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
        self._phase.setText("自动进化环提交中…")
        tray = getattr(self, "_tray", None)
        if tray and hasattr(tray, "showMessage"):
            tray.showMessage("Friday", "自动进化环已提交（已带上一轮上下文，减少重复）。", QSystemTrayIcon.Information, 3000)
        QTimer.singleShot(interval * 1000, self._schedule_auto_evolution)

    def _toggle_auto_evolution(self):
        """开启/关闭自动进化环：定时触发没在工作的 CC 执行进化。"""
        self._auto_evolution_enabled = not self._auto_evolution_enabled
        tray = getattr(self, "_tray", None)
        if self._auto_evolution_enabled:
            if tray and hasattr(tray, "showMessage"):
                tray.showMessage("Friday", "已开启自动进化环，将按配置间隔定时提交进化任务。", QSystemTrayIcon.Information, 4000)
            QTimer.singleShot(2000, self._schedule_auto_evolution)
        else:
            if tray and hasattr(tray, "showMessage"):
                tray.showMessage("Friday", "已关闭自动进化环。", QSystemTrayIcon.Information, 2000)

    def _on_evolution_finished(self, ok, result):
        self._evolution_worker = None
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
        tray = getattr(self, "_tray", None)
        if tray and hasattr(tray, "showMessage"):
            if ok:
                tray.showMessage("Friday", "本轮进化环已完成。", QSystemTrayIcon.Information, 4000)
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

    def _tick(self):
        self._angle += 1.2
        if self._angle >= 360:
            self._angle -= 360
        self._pulse += 0.04
        if self._pulse >= 6.28318:
            self._pulse -= 6.28318
        self.update()

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
