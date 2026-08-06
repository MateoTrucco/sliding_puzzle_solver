"""Small Tkinter helpers used by the puzzle interface."""

from __future__ import annotations

import platform
import tkinter as tk

COLORS = {
    "surface": "#e2e8f0",
    "accent": "#94a3b8",
    "background": "#f8fafc",
    "text": "#111827",
    "white": "#ffffff",
    "success": "#22c55e",
    "danger": "#ef4444",
    "warning": "#f59e0b",
    "info": "#3b82f6",
}
c = {
    "-": COLORS["surface"], "+": COLORS["accent"], "++": COLORS["background"],
    "b": COLORS["text"], "w": COLORS["white"], "g": COLORS["success"],
    "r": COLORS["danger"], "y": COLORS["warning"], "blu": COLORS["info"],
}

def enable_high_dpi(root: tk.Misc | None = None) -> None:
    if platform.system() == "Windows":
        try:
            from ctypes import windll
            try:
                windll.shcore.SetProcessDpiAwareness(1)
            except (AttributeError, OSError):
                windll.user32.SetProcessDPIAware()
        except (AttributeError, OSError):
            return
    elif root is not None:
        try:
            root.tk.call("tk", "scaling", 1.5)
        except tk.TclError:
            return
