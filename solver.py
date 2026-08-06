"""A* solver for the classic 8-puzzle."""

from __future__ import annotations

from dataclasses import dataclass
from heapq import heappop, heappush
from itertools import count
from typing import Iterable, Literal

Board = tuple[int, ...]
Move = Literal["L", "R", "U", "D"]
GOAL: Board = (1, 2, 3, 4, 5, 6, 7, 8, 0)
MOVE_DELTAS: dict[Move, tuple[int, int]] = {
    "L": (0, -1),
    "R": (0, 1),
    "U": (-1, 0),
    "D": (1, 0),
}


@dataclass(frozen=True)
class SolveResult:
    status: Literal["solved", "already_solved", "unsolvable", "invalid"]
    moves: tuple[Move, ...] = ()
    explored: int = 0
    message: str = ""


def normalize_board(board: Iterable[int] | Iterable[Iterable[int]]) -> Board:
    """Return a flat immutable board and reject malformed inputs."""

    values = list(board)
    if len(values) == 3 and all(not isinstance(item, int) for item in values):
        flattened: list[int] = []
        for row in values:
            row_values = list(row)  # type: ignore[arg-type]
            if len(row_values) != 3:
                raise ValueError("each row must contain exactly three values")
            flattened.extend(row_values)
        values = flattened

    if len(values) != 9 or any(isinstance(value, bool) or not isinstance(value, int) for value in values):
        raise ValueError("board must contain exactly nine integers")
    board_tuple = tuple(values)  # type: ignore[arg-type]
    if set(board_tuple) != set(range(9)):
        raise ValueError("board must contain each number from 0 to 8 exactly once")
    return board_tuple


def is_solvable(board: Board) -> bool:
    """Return whether a valid 3×3 board can reach the goal state."""

    numbers = [value for value in board if value != 0]
    inversions = sum(
        1
        for index, left in enumerate(numbers)
        for right in numbers[index + 1 :]
        if left > right
    )
    return inversions % 2 == 0


def manhattan_distance(board: Board) -> int:
    distance = 0
    for index, value in enumerate(board):
        if value == 0:
            continue
        goal_index = value - 1
        row, column = divmod(index, 3)
        goal_row, goal_column = divmod(goal_index, 3)
        distance += abs(row - goal_row) + abs(column - goal_column)
    return distance


def neighbors(board: Board) -> list[tuple[Move, Board]]:
    blank_index = board.index(0)
    row, column = divmod(blank_index, 3)
    candidates: list[tuple[Move, Board]] = []
    for move, (row_delta, column_delta) in MOVE_DELTAS.items():
        new_row, new_column = row + row_delta, column + column_delta
        if not (0 <= new_row < 3 and 0 <= new_column < 3):
            continue
        target_index = new_row * 3 + new_column
        mutable = list(board)
        mutable[blank_index], mutable[target_index] = mutable[target_index], mutable[blank_index]
        candidates.append((move, tuple(mutable)))
    return candidates


def apply_move(board: Board, move: Move) -> Board:
    for candidate_move, candidate_board in neighbors(board):
        if candidate_move == move:
            return candidate_board
    raise ValueError(f"move {move!r} is not valid for this board")


def solve(board: Iterable[int] | Iterable[Iterable[int]]) -> SolveResult:
    """Solve a board with A* and return an explicit status."""

    try:
        start = normalize_board(board)
    except ValueError as exc:
        return SolveResult("invalid", message=str(exc))

    if start == GOAL:
        return SolveResult("already_solved", message="The puzzle is already solved.")
    if not is_solvable(start):
        return SolveResult("unsolvable", message="This arrangement is not solvable.")

    sequence = count()
    frontier: list[tuple[int, int, int, Board, tuple[Move, ...]]] = []
    heappush(frontier, (manhattan_distance(start), 0, next(sequence), start, ()))
    best_cost: dict[Board, int] = {start: 0}
    explored = 0

    while frontier:
        _priority, cost, _order, current, path = heappop(frontier)
        if cost != best_cost.get(current):
            continue
        explored += 1
        if current == GOAL:
            return SolveResult("solved", path, explored, f"Solved in {len(path)} moves.")

        next_cost = cost + 1
        for move, candidate in neighbors(current):
            if next_cost >= best_cost.get(candidate, 10**9):
                continue
            best_cost[candidate] = next_cost
            next_path = path + (move,)
            priority = next_cost + manhattan_distance(candidate)
            heappush(frontier, (priority, next_cost, next(sequence), candidate, next_path))

    return SolveResult("unsolvable", explored=explored, message="No solution was found.")
