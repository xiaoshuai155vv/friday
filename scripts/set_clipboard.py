import sys
import ctypes
import time

text = sys.argv[1] if len(sys.argv) > 1 else "Hello"

# Open clipboard
if ctypes.windll.user32.OpenClipboard(None):
    ctypes.windll.user32.EmptyClipboard()
    # Convert to UTF-16
    text_utf16 = text.encode('utf-16-le') + b'\x00\x00'
    hMem = ctypes.windll.kernel32.GlobalAlloc(0x0002, len(text_utf16))
    pMem = ctypes.windll.kernel32.GlobalLock(hMem)
    ctypes.memmove(pMem, text_utf16, len(text_utf16))
    ctypes.windll.kernel32.GlobalUnlock(hMem)
    ctypes.windll.user32.SetClipboardData(1, hMem)  # CF_UNICODETEXT
    ctypes.windll.user32.CloseClipboard()
    print("Clipboard set successfully")
else:
    print("Failed to open clipboard")