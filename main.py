"""Interactive 8-puzzle with an A* solution visualizer."""

from __future__ import annotations

import random
import threading
import time
import tkinter as tk

from base_functions import c, enable_high_dpi
from solver import GOAL, Board, Move, SolveResult, apply_move, neighbors, solve
from ui_theme import apply_theme


class PuzzleApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Sliding Puzzle Solver")
        self.root.geometry("620x520")
        self.root.minsize(520, 470)
        self.colors = apply_theme(root, "#2563eb")
        enable_high_dpi(root)

        self.board: Board = GOAL
        self.solution: tuple[Move, ...] = ()
        self.solution_index = 0
        self.solving = False
        self.animating = False
        self.tile_buttons: list[tk.Button] = []

        self._build_ui()
        self.shuffle(30)

    def _build_ui(self) -> None:
        title = tk.Label(
            self.root,
            text="8-Puzzle A* Solver",
            font=("Segoe UI", 22, "bold"),
            bg=self.colors["bg"],
            fg=self.colors["ink"],
        )
        title.pack(pady=(18, 4))
        tk.Label(
            self.root,
            text="Move tiles yourself, shuffle a valid board, or let A* find the shortest path.",
            font=("Segoe UI", 10),
            bg=self.colors["bg"],
            fg=self.colors["muted"],
        ).pack(pady=(0, 12))

        body = tk.Frame(self.root, bg=self.colors["bg"])
        body.pack(fill="both", expand=True, padx=22, pady=8)
        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, weight=1)

        grid = tk.Frame(body, bg=self.colors["line"], bd=0, highlightthickness=0)
        grid.grid(row=0, column=0, rowspan=2, padx=(0, 18), sticky="nsew")
        for row in range(3):
            grid.rowconfigure(row, weight=1)
            grid.columnconfigure(row, weight=1)

        for index in range(9):
            button = tk.Button(
                grid,
                font=("Segoe UI", 24, "bold"),
                command=lambda tile=index: self.move_tile(tile),
                bd=0,
                relief="flat",
                cursor="hand2",
            )
            button.grid(row=index // 3, column=index % 3, padx=4, pady=4, sticky="nsew")
            self.tile_buttons.append(button)

        controls = tk.Frame(body, bg=self.colors["bg"])
        controls.grid(row=0, column=1, sticky="new")
        controls.columnconfigure(0, weight=1)

        self.solve_button = self._button(controls, "Solve", self.solve_async, self.colors["accent"])
        self.step_button = self._button(controls, "Next step", self.step_solution, "#f59e0b")
        self.animate_button = self._button(controls, "Animate", self.animate_solution, "#0ea5e9")
        self.shuffle_button = self._button(controls, "Shuffle", lambda: self.shuffle(50), "#7c3aed")
        self.reset_button = self._button(controls, "Reset", self.reset, self.colors["soft"])

        self.status = tk.Label(
            body,
            text="",
            justify="left",
            anchor="nw",
            wraplength=250,
            font=("Segoe UI", 11),
            bg=self.colors["card"],
            fg=self.colors["ink"],
            padx=14,
            pady=14,
            bd=0,
            relief="flat",
            highlightthickness=1,
            highlightbackground=self.colors["line"],
        )
        self.status.grid(row=1, column=1, sticky="nsew", pady=(12, 0))

        self._render()

    def _button(self, parent: tk.Widget, text: str, command, background: str) -> tk.Button:
        button = tk.Button(
            parent,
            text=text,
            command=command,
            font=("Segoe UI", 11, "bold"),
            bg=background,
            fg="#ffffff" if background != self.colors["soft"] else self.colors["ink"],
            activebackground=self.colors["card"],
            cursor="hand2",
            padx=10,
            pady=8,
        )
        button.pack(fill="x", pady=4)
        return button

    def _render(self) -> None:
        for index, value in enumerate(self.board):
            button = self.tile_buttons[index]
            if value == 0:
                button.configure(text="", state="disabled", bg=self.colors["soft"], relief="flat")
            else:
                button.configure(text=str(value), state="normal", bg=self.colors["card"], fg=self.colors["ink"], relief="flat")

    def _clear_solution(self) -> None:
        self.solution = ()
        self.solution_index = 0
        self.animating = False

    def move_tile(self, tile_index: int) -> None:
        if self.solving or self.animating:
            return
        blank_index = self.board.index(0)
        tile_row, tile_column = divmod(tile_index, 3)
        blank_row, blank_column = divmod(blank_index, 3)
        if abs(tile_row - blank_row) + abs(tile_column - blank_column) != 1:
            return

        move: Move
        if tile_row == blank_row and tile_column < blank_column:
            move = "L"
        elif tile_row == blank_row:
            move = "R"
        elif tile_row < blank_row:
            move = "U"
        else:
            move = "D"
        self.board = apply_move(self.board, move)
        self._clear_solution()
        self.status.configure(text="Manual move. Press Solve to calculate a new path.")
        self._render()

    def shuffle(self, steps: int = 40) -> None:
        if self.solving:
            return
        board = GOAL
        previous: Board | None = None
        for _ in range(max(1, steps)):
            options = [candidate for _move, candidate in neighbors(board) if candidate != previous]
            previous, board = board, random.choice(options)
        self.board = board
        self._clear_solution()
        self.status.configure(text="Valid shuffled board ready.")
        self._render()

    def reset(self) -> None:
        if self.solving:
            return
        self.board = GOAL
        self._clear_solution()
        self.status.configure(text="The puzzle is already solved.")
        self._render()

    def _set_controls_enabled(self, enabled: bool) -> None:
        state = "normal" if enabled else "disabled"
        for button in (
            self.solve_button,
            self.step_button,
            self.animate_button,
            self.shuffle_button,
            self.reset_button,
        ):
            button.configure(state=state)

    def solve_async(self) -> None:
        if self.solving or self.animating:
            return
        self.solving = True
        self._set_controls_enabled(False)
        self.status.configure(text="Solving with A*…")
        board_snapshot = self.board
        started = time.perf_counter()

        def worker() -> None:
            result = solve(board_snapshot)
            elapsed = time.perf_counter() - started
            self.root.after(0, lambda: self._handle_result(board_snapshot, result, elapsed))

        threading.Thread(target=worker, daemon=True).start()

    def _handle_result(self, board_snapshot: Board, result: SolveResult, elapsed: float) -> None:
        self.solving = False
        self._set_controls_enabled(True)
        if board_snapshot != self.board:
            self.status.configure(text="The board changed before the solver finished. Solve again.")
            return

        self.solution = result.moves
        self.solution_index = 0
        if result.status == "solved":
            preview = " ".join(result.moves[:30])
            suffix = " …" if len(result.moves) > 30 else ""
            self.status.configure(
                text=(
                    f"{result.message}\n"
                    f"Explored states: {result.explored}\n"
                    f"Time: {elapsed:.4f} s\n"
                    f"Moves: {preview}{suffix}"
                )
            )
        else:
            self.status.configure(text=result.message)

    def step_solution(self) -> None:
        if self.solving or self.animating:
            return
        if self.solution_index >= len(self.solution):
            if self.board == GOAL:
                self.status.configure(text="Solution complete.")
            else:
                self.status.configure(text="Press Solve before stepping through a solution.")
            return
        self.board = apply_move(self.board, self.solution[self.solution_index])
        self.solution_index += 1
        self._render()
        remaining = len(self.solution) - self.solution_index
        self.status.configure(text=f"Applied step {self.solution_index}. Remaining: {remaining}.")

    def animate_solution(self) -> None:
        if self.solving or self.animating:
            return
        if not self.solution or self.solution_index >= len(self.solution):
            self.status.configure(text="Press Solve before starting the animation.")
            return
        self.animating = True
        self._set_controls_enabled(False)
        self._animate_next()

    def _animate_next(self) -> None:
        if self.solution_index >= len(self.solution):
            self.animating = False
            self._set_controls_enabled(True)
            self.status.configure(text="Solution complete.")
            return
        self.board = apply_move(self.board, self.solution[self.solution_index])
        self.solution_index += 1
        self._render()
        self.status.configure(
            text=f"Animating step {self.solution_index} of {len(self.solution)}…"
        )
        self.root.after(220, self._animate_next)


def main() -> None:
    root = tk.Tk()
    PuzzleApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
