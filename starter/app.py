from flask import Flask, render_template, jsonify, request
import sudoku_logic

app = Flask(__name__)

# Keep a simple in-memory store for current puzzle and solution
CURRENT = {
    'puzzle': None,
    'solution': None,
    'difficulty': 'medium',
    'clues': 35
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/new')
def new_game():
    difficulty = sudoku_logic.normalize_difficulty(request.args.get('difficulty'))
    clues_param = request.args.get('clues')

    if clues_param is None:
        clues = sudoku_logic.get_clues_for_difficulty(difficulty)
    else:
        try:
            clues = int(clues_param)
        except (TypeError, ValueError):
            clues = sudoku_logic.get_clues_for_difficulty(difficulty)

    puzzle, solution = sudoku_logic.generate_puzzle(clues)
    CURRENT['puzzle'] = puzzle
    CURRENT['solution'] = solution
    CURRENT['difficulty'] = difficulty
    CURRENT['clues'] = clues
    return jsonify({'puzzle': puzzle, 'difficulty': difficulty, 'clues': clues})

@app.route('/check', methods=['POST'])
def check_solution():
    data = request.json
    board = data.get('board')
    solution = CURRENT.get('solution')
    if solution is None:
        return jsonify({'error': 'No game in progress'}), 400
    if not isinstance(board, list):
        return jsonify({'error': 'Invalid board data'}), 400
    incorrect = []
    for i in range(sudoku_logic.SIZE):
        for j in range(sudoku_logic.SIZE):
            if board[i][j] != solution[i][j]:
                incorrect.append([i, j])

    conflicts = sudoku_logic.find_conflicts(board)
    solved = not incorrect and not any(cell == 0 for row in board for cell in row)

    if solved:
        message = 'Congratulations! You solved the puzzle correctly.'
    elif incorrect:
        message = 'Some cells are incorrect.'
    else:
        message = 'Your current entries are valid so far.'

    return jsonify({'incorrect': incorrect, 'conflicts': conflicts, 'solved': solved, 'message': message})

@app.route('/hint', methods=['POST'])
def hint():
    data = request.json
    board = data.get('board')
    solution = CURRENT.get('solution')
    if solution is None:
        return jsonify({'error': 'No game in progress'}), 400
    if not isinstance(board, list):
        return jsonify({'error': 'Invalid board data'}), 400

    empty_cells = []
    for i in range(sudoku_logic.SIZE):
        for j in range(sudoku_logic.SIZE):
            if i < len(board) and j < len(board[i]) and board[i][j] == 0:
                empty_cells.append((i, j))

    if not empty_cells:
        return jsonify({'error': 'No empty cell left'}), 400

    row, col = empty_cells[0]
    return jsonify({'row': row, 'col': col, 'value': solution[row][col]})

if __name__ == '__main__':
    app.run(debug=True)
