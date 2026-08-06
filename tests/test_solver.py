from solver import GOAL, apply_move, is_solvable, manhattan_distance, normalize_board, solve


def test_normalize_nested_board():
    assert normalize_board(((1, 2, 3), (4, 5, 6), (7, 8, 0))) == GOAL


def test_invalid_board_is_reported():
    result = solve((0, 0, 0, 0, 0, 0, 0, 0, 0))
    assert result.status == "invalid"


def test_already_solved_is_distinct():
    result = solve(GOAL)
    assert result.status == "already_solved"
    assert result.moves == ()


def test_one_move_solution():
    board = (1, 2, 3, 4, 5, 6, 7, 0, 8)
    result = solve(board)
    assert result.status == "solved"
    assert result.moves == ("R",)
    assert apply_move(board, result.moves[0]) == GOAL


def test_unsolvable_board():
    board = (1, 2, 3, 4, 5, 6, 8, 7, 0)
    assert not is_solvable(board)
    assert solve(board).status == "unsolvable"


def test_known_hard_board_uses_optimal_31_moves():
    board = (8, 6, 7, 2, 5, 4, 3, 0, 1)
    result = solve(board)
    assert result.status == "solved"
    assert len(result.moves) == 31


def test_goal_has_zero_manhattan_distance():
    assert manhattan_distance(GOAL) == 0

def test_boolean_tile_is_rejected():
    result = solve((True, 2, 3, 4, 5, 6, 7, 8, 0))
    assert result.status == "invalid"

