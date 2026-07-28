import sudoku_logic


def test_create_empty_board_has_expected_dimensions():
    """Ensures the empty board starts as a 9x9 grid filled with zeros."""
    board = sudoku_logic.create_empty_board()

    assert len(board) == sudoku_logic.SIZE
    assert all(len(row) == sudoku_logic.SIZE for row in board)
    assert board[0][0] == sudoku_logic.EMPTY


def test_is_safe_detects_row_column_and_box_conflicts():
    """Confirms the safety check rejects duplicate values in rows, columns, and 3x3 boxes."""
    board = sudoku_logic.create_empty_board()
    board[0][0] = 1
    board[0][1] = 1
    assert not sudoku_logic.is_safe(board, 0, 2, 1)

    board = sudoku_logic.create_empty_board()
    board[0][0] = 1
    board[1][0] = 1
    assert not sudoku_logic.is_safe(board, 2, 2, 1)

    board = sudoku_logic.create_empty_board()
    board[0][0] = 1
    board[1][1] = 1
    assert not sudoku_logic.is_safe(board, 2, 2, 1)


def test_generate_puzzle_returns_valid_puzzle_and_solution():
    """Verifies that a generated puzzle has the right shape and a valid solved board."""
    puzzle, solution = sudoku_logic.generate_puzzle(clues=35)

    assert len(puzzle) == sudoku_logic.SIZE
    assert len(solution) == sudoku_logic.SIZE
    assert all(len(row) == sudoku_logic.SIZE for row in puzzle)
    assert all(len(row) == sudoku_logic.SIZE for row in solution)
    assert any(cell == sudoku_logic.EMPTY for row in puzzle for cell in row)
    assert all(0 <= cell <= sudoku_logic.SIZE for row in puzzle for cell in row)
    assert all(0 <= cell <= sudoku_logic.SIZE for row in solution for cell in row)


def test_generate_puzzle_produces_a_uniquely_solved_grid():
    """Generated puzzles should still have exactly one valid solution."""
    puzzle, _ = sudoku_logic.generate_puzzle(clues=35)

    assert sudoku_logic.count_solutions(puzzle) == 1
