import copy
import random

SIZE = 9
EMPTY = 0
DIFFICULTY_SETTINGS = {
    'easy': 44,
    'medium': 35,
    'hard': 30,
}


def deep_copy(board):
    return copy.deepcopy(board)

def create_empty_board():
    return [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]


def normalize_difficulty(difficulty):
    if difficulty is None:
        return 'medium'
    normalized = str(difficulty).strip().lower()
    return normalized if normalized in DIFFICULTY_SETTINGS else 'medium'


def get_clues_for_difficulty(difficulty):
    normalized = normalize_difficulty(difficulty)
    return DIFFICULTY_SETTINGS[normalized]


def find_conflicts(board):
    conflicts = set()

    for row in range(SIZE):
        seen = {}
        for col in range(SIZE):
            value = board[row][col]
            if value == EMPTY:
                continue
            if value in seen:
                conflicts.add((row, seen[value]))
                conflicts.add((row, col))
            else:
                seen[value] = col

    for col in range(SIZE):
        seen = {}
        for row in range(SIZE):
            value = board[row][col]
            if value == EMPTY:
                continue
            if value in seen:
                conflicts.add((seen[value], col))
                conflicts.add((row, col))
            else:
                seen[value] = row

    for box_row in range(0, SIZE, 3):
        for box_col in range(0, SIZE, 3):
            seen = {}
            for row in range(box_row, box_row + 3):
                for col in range(box_col, box_col + 3):
                    value = board[row][col]
                    if value == EMPTY:
                        continue
                    if value in seen:
                        conflicts.add(seen[value])
                        conflicts.add((row, col))
                    else:
                        seen[value] = (row, col)

    return [(row, col) for row, col in conflicts]


def is_safe(board, row, col, num):
    # Check row and column
    for x in range(SIZE):
        if board[row][x] == num or board[x][col] == num:
            return False
    # Check 3x3 box
    start_row = row - row % 3
    start_col = col - col % 3
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False
    return True

def fill_board(board):
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                possible = list(range(1, SIZE + 1))
                random.shuffle(possible)
                for candidate in possible:
                    if is_safe(board, row, col, candidate):
                        board[row][col] = candidate
                        if fill_board(board):
                            return True
                        board[row][col] = EMPTY
                return False
    return True

def find_empty_cell(board):
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                return row, col
    return None


def count_solutions(board, limit=2):
    empty_cell = find_empty_cell(board)
    if empty_cell is None:
        return 1

    row, col = empty_cell
    possible = list(range(1, SIZE + 1))
    random.shuffle(possible)

    solutions = 0
    for num in possible:
        if is_safe(board, row, col, num):
            board[row][col] = num
            solutions += count_solutions(board, limit)
            board[row][col] = EMPTY
            if solutions >= limit:
                return solutions

    return solutions


def remove_cells(board, clues):
    target_removals = max(0, SIZE * SIZE - clues)
    cells = [(row, col) for row in range(SIZE) for col in range(SIZE)]
    random.shuffle(cells)

    removed = 0
    for row, col in cells:
        if removed >= target_removals:
            break
        if board[row][col] == EMPTY:
            continue

        original_value = board[row][col]
        board[row][col] = EMPTY
        if count_solutions(board, limit=2) != 1:
            board[row][col] = original_value
        else:
            removed += 1


def generate_puzzle(clues=35):
    board = create_empty_board()
    fill_board(board)
    solution = deep_copy(board)
    remove_cells(board, clues)
    puzzle = deep_copy(board)
    return puzzle, solution
