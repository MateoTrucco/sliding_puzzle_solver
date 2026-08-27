"""Shared Tkinter helpers used by the small desktop projects.

The module intentionally stays dependency-free so each project can be run with a
standard Python installation that includes Tkinter.
"""

from __future__ import annotations

import platform
import time
import tkinter as tk
from collections.abc import Callable
from typing import Any

COLORS = {
    "surface": "#f5f7fa",
    "accent": "#ff6f61",
    "background": "#f5f7fa",
    "text": "#1a1a1d",
    "white": "#ffffff",
    "success": "#4caf50",
    "danger": "#f36b61",
    "warning": "#ffeb3b",
    "info": "#2196f3",
    "purple": "#691ee9",
}

# Backwards-compatible aliases used by the original projects.
c = {
    "-": COLORS["surface"],
    "+": COLORS["accent"],
    "++": COLORS["background"],
    "b": COLORS["text"],
    "w": COLORS["white"],
    "g": COLORS["success"],
    "r": COLORS["danger"],
    "y": COLORS["warning"],
    "blu": COLORS["info"],
    "m": COLORS["purple"],
}


def enable_high_dpi(root: tk.Misc | None = None) -> None:
    """Enable high-DPI support where the platform exposes it.

    On Windows, process DPI awareness must be configured before creating the
    main window. On Linux/macOS, an existing Tk root may be supplied to adjust
    Tk scaling without creating a hidden extra window.
    """

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


def wait(seconds: float = 0.5) -> None:
    """Pause the current thread.

    Avoid calling this from Tkinter callbacks because it blocks the interface.
    Prefer ``widget.after(...)`` for GUI delays.
    """

    if seconds < 0:
        raise ValueError("seconds must be non-negative")
    time.sleep(seconds)


def _parse_geometry(winsize: str) -> tuple[int, int] | None:
    if winsize in {"", "auto"}:
        return None
    try:
        width_text, height_text = winsize.lower().split("x", maxsplit=1)
        width, height = int(width_text), int(height_text)
    except (ValueError, AttributeError) as exc:
        raise ValueError("winsize must use the format 'WIDTHxHEIGHT', '', or 'auto'") from exc
    if width <= 0 or height <= 0:
        raise ValueError("window dimensions must be positive")
    return width, height


def make_screen(
    title: str = "Title",
    winsize: str = "580x450",
    minsize_x: int = 400,
    minsize_y: int = 250,
    bg_body: str = c["++"],
    bg_int: str = c["-"],
    fg_int: str = c["b"],
    bg_button: str = c["+"],
    fg_button: str = c["b"],
    label_font: tuple[Any, ...] = ("Arial", 16, "bold"),
    input_font: tuple[Any, ...] = ("Arial", 14),
    output_font: tuple[Any, ...] = ("Courier", 12, "bold"),
    button_font: tuple[Any, ...] = ("Arial", 14, "bold"),
    button_text: str = "PLAY",
    button_command: Callable[[], Any] | None = None,
    use_title: bool = True,
    use_input: bool = True,
    use_button: bool = True,
    use_loading_bar: bool = True,
    use_output: bool = True,
    loading_duration: int = 600,
    loading_steps: int = 24,
) -> dict[str, Any]:
    """Create a reusable Tkinter layout and return its widgets/helpers."""

    if minsize_x <= 0 or minsize_y <= 0:
        raise ValueError("minimum window dimensions must be positive")
    if loading_duration < 0:
        raise ValueError("loading_duration must be non-negative")
    if loading_steps <= 0:
        raise ValueError("loading_steps must be greater than zero")

    window = tk.Tk()
    enable_high_dpi(window)
    window.title(title)
    window.configure(bg=bg_body)
    window.columnconfigure(0, weight=1)

    dimensions = _parse_geometry(winsize)
    if dimensions is not None:
        width, height = dimensions
        window.geometry(f"{width}x{height}")
        window.minsize(minsize_x, minsize_y)
    else:
        window.update_idletasks()
        window.minsize(minsize_x, minsize_y)

    next_row = 0
    ui: dict[str, Any] = {"window": window}

    if use_title:
        title_label = tk.Label(
            window,
            text=title,
            font=label_font,
            bg=bg_int,
            fg=fg_int,
            borderwidth=2,
            relief="solid",
        )
        title_label.grid(row=next_row, column=0, padx=10, pady=(10, 5), sticky="ew")
        ui["title_label"] = title_label
        next_row += 1

    if use_input:
        input_text = tk.Entry(
            window,
            font=input_font,
            bg=bg_int,
            fg=fg_int,
            borderwidth=2,
            relief="solid",
        )
        input_text.grid(row=next_row, column=0, padx=10, pady=5, sticky="ew", ipady=5)
        ui["input_text"] = input_text
        next_row += 1

    def finish_action() -> None:
        if "input_text" in ui:
            ui["input_text"].configure(state="normal")
        if "action_button" in ui:
            ui["action_button"].configure(state="normal")
        if button_command is not None:
            button_command()

    def animate_loading_bar(step: int = 0) -> None:
        interval = max(1, loading_duration // loading_steps) if loading_duration else 1
        percentage = step / loading_steps
        if percentage <= 0.3:
            color = c["r"]
        elif percentage <= 0.6:
            color = c["y"]
        elif percentage <= 0.9:
            color = c["blu"]
        else:
            color = c["m"]

        bar_width = 30
        filled = round(bar_width * percentage)
        ui["loading_label"].configure(text="█" * filled + "░" * (bar_width - filled), fg=color)

        if step < loading_steps:
            window.after(interval, animate_loading_bar, step + 1)
        else:
            ui["loading_label"].configure(text="")
            finish_action()

    def on_click() -> None:
        if use_loading_bar:
            if "input_text" in ui:
                ui["input_text"].configure(state="disabled")
            ui["action_button"].configure(state="disabled")
            animate_loading_bar()
        else:
            finish_action()

    if use_button:
        action_button = tk.Button(
            window,
            text=button_text,
            command=on_click,
            font=button_font,
            bg=bg_button,
            fg=fg_button,
            borderwidth=2,
            relief="raised",
            cursor="hand2",
            activebackground=bg_int,
            activeforeground=fg_int,
        )
        action_button.grid(row=next_row, column=0, padx=80, pady=5, sticky="ew")
        ui["action_button"] = action_button
        next_row += 1

    if use_loading_bar:
        loading_label = tk.Label(
            window,
            text="",
            font=("Courier", 10),
            bg=bg_body,
            fg=fg_int,
            anchor="center",
        )
        loading_label.grid(row=next_row, column=0, padx=20, pady=5, sticky="ew")
        ui["loading_label"] = loading_label
        next_row += 1

    if use_output:
        output_frame = tk.Frame(window, bg=bg_body, borderwidth=2, relief="solid")
        output_frame.grid(row=next_row, column=0, padx=10, pady=10, sticky="nsew")
        window.rowconfigure(next_row, weight=1)
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)

        output_canvas = tk.Canvas(output_frame, bg=bg_int, highlightthickness=0)
        output_scrollbar = tk.Scrollbar(output_frame, orient="vertical", command=output_canvas.yview)
        output_scrollable_frame = tk.Frame(output_canvas, bg=bg_int)
        canvas_item = output_canvas.create_window((0, 0), window=output_scrollable_frame, anchor="nw")

        output_scrollable_frame.bind(
            "<Configure>",
            lambda _event: output_canvas.configure(scrollregion=output_canvas.bbox("all")),
        )
        output_canvas.bind(
            "<Configure>",
            lambda event: output_canvas.itemconfigure(canvas_item, width=event.width),
        )
        output_canvas.configure(yscrollcommand=output_scrollbar.set)
        output_canvas.grid(row=0, column=0, sticky="nsew")
        output_scrollbar.grid(row=0, column=1, sticky="ns")

        output_label = tk.Label(
            output_scrollable_frame,
            text="",
            font=output_font,
            bg=bg_int,
            fg=fg_int,
            anchor="center",
            justify="center",
            wraplength=540,
            padx=10,
            pady=10,
        )
        output_label.pack(fill="both", expand=True)
        ui.update(
            {
                "output_frame": output_frame,
                "output_canvas": output_canvas,
                "output_label": output_label,
            }
        )

        def write_output(text: object, clear: bool = True) -> None:
            new_text = str(text)
            if not clear and output_label.cget("text"):
                new_text = f"{output_label.cget('text')}{new_text}"
            output_label.configure(text=new_text)

        def clear_output() -> None:
            output_label.configure(text="")

        def update_output_wrap(event: tk.Event[Any] | None = None) -> None:
            width = event.width if event is not None else window.winfo_width()
            output_label.configure(wraplength=max(120, min(width - 60, 900)))

        window.bind("<Configure>", update_output_wrap, add="+")
        ui["write_output"] = write_output
        ui["clear_output"] = clear_output
        next_row += 1

    next_row_ref = [next_row]

    def add_element(
        kind: str = "label",
        text: str = "",
        font: tuple[Any, ...] = ("Arial", 12),
        row: int | None = None,
        col: int = 0,
        rowspan: int | str | None = None,
        colspan: int | str | None = None,
        padx: int | tuple[int, int] = 10,
        pady: int | tuple[int, int] = 5,
        sticky: str | None = "nsew",
        weight: int = 0,
        anchor: str = "w",
        **kwargs: Any,
    ) -> tk.Widget:
        """Add a label, button, or entry to the main window grid."""

        if row is None:
            row = next_row_ref[0]
            next_row_ref[0] += 1

        resolved_colspan = max(window.grid_size()[0], 1) if colspan == "all" else int(colspan or 1)
        resolved_rowspan = max(window.grid_size()[1], 1) if rowspan == "all" else int(rowspan or 1)
        resolved_sticky = "" if sticky is None else ("nsew" if sticky == "all" else sticky)
        kind = kind.lower()

        common = {"font": font, "borderwidth": 2}
        if kind == "label":
            widget: tk.Widget = tk.Label(
                window,
                text=text,
                anchor=anchor,
                bg=kwargs.pop("bg", bg_int),
                fg=kwargs.pop("fg", fg_int),
                relief=kwargs.pop("relief", "solid"),
                **common,
                **kwargs,
            )
        elif kind == "button":
            widget = tk.Button(
                window,
                text=text,
                bg=kwargs.pop("bg", bg_button),
                fg=kwargs.pop("fg", fg_button),
                activebackground=kwargs.pop("active_bg", bg_int),
                activeforeground=kwargs.pop("active_fg", fg_int),
                relief=kwargs.pop("relief", "raised"),
                cursor=kwargs.pop("cursor", "hand2"),
                **common,
                **kwargs,
            )
        elif kind == "entry":
            widget = tk.Entry(
                window,
                bg=kwargs.pop("bg", bg_int),
                fg=kwargs.pop("fg", fg_int),
                relief=kwargs.pop("relief", "solid"),
                **common,
                **kwargs,
            )
        else:
            raise ValueError(f"unknown element kind: {kind}")

        widget.grid(
            row=row,
            column=col,
            columnspan=resolved_colspan,
            rowspan=resolved_rowspan,
            padx=padx,
            pady=pady,
            sticky=resolved_sticky,
        )
        window.columnconfigure(col, weight=weight)
        window.rowconfigure(row, weight=weight)
        return widget

    ui["add_element"] = add_element
    return ui
