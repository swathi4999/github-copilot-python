import app as app_module
import sudoku_logic


def test_index_route_renders_html_page(client):
    """The home page should respond with HTML content successfully."""
    response = client.get("/")

    assert response.status_code == 200
    assert response.content_type.startswith("text/html")


def test_new_game_route_returns_puzzle_and_stores_state(client):
    """The /new route should create a puzzle and remember it for later checks."""
    response = client.get("/new?clues=35")

    assert response.status_code == 200
    payload = response.get_json()
    assert isinstance(payload["puzzle"], list)
    assert len(payload["puzzle"]) == sudoku_logic.SIZE
    assert app_module.CURRENT["puzzle"] is not None
    assert app_module.CURRENT["solution"] is not None


def test_check_solution_route_reports_incorrect_cells(client):
    """The /check route should identify cells that differ from the stored solution."""
    client.get("/new?clues=35")
    solution = app_module.CURRENT["solution"]
    wrong_board = sudoku_logic.deep_copy(solution)
    wrong_board[0][0] = 1 if wrong_board[0][0] != 1 else 2

    response = client.post("/check", json={"board": wrong_board})

    assert response.status_code == 200
    payload = response.get_json()
    assert [0, 0] in payload["incorrect"]
    assert payload["solved"] is False
    assert payload["message"] == "Some cells are incorrect."


def test_check_solution_route_reports_solved_game(client):
    """The /check route should report a solved puzzle and return a congratulatory message."""
    client.get("/new?clues=35")
    solution = app_module.CURRENT["solution"]

    response = client.post("/check", json={"board": solution})

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["incorrect"] == []
    assert payload["conflicts"] == []
    assert payload["solved"] is True
    assert payload["message"] == "Congratulations! You solved the puzzle correctly."


def test_new_game_route_supports_named_difficulties(client):
    """The /new route should map difficulty labels to the expected number of clues."""
    response = client.get("/new?difficulty=easy")

    assert response.status_code == 200
    puzzle = response.get_json()["puzzle"]
    clues = sum(cell != 0 for row in puzzle for cell in row)
    assert clues == 44


def test_hint_route_returns_one_hint_for_active_game(client):
    """The /hint route should return a valid empty cell from the current puzzle."""
    client.get("/new?clues=35")
    puzzle = app_module.CURRENT["puzzle"]

    response = client.post("/hint", json={"board": puzzle})

    assert response.status_code == 200
    payload = response.get_json()
    assert "row" in payload and "col" in payload and "value" in payload
    row, col, value = payload["row"], payload["col"], payload["value"]
    assert puzzle[row][col] == 0
    assert value == app_module.CURRENT["solution"][row][col]


def test_check_solution_route_requires_active_game(client):
    """The /check route should return an error when no game has been started."""
    response = client.post("/check", json={"board": []})

    assert response.status_code == 400
    assert response.get_json()["error"] == "No game in progress"


def test_index_route_contains_leaderboard_section(client):
    """The landing page should include the leaderboard and player controls."""
    response = client.get("/")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert 'id="leaderboard"' in html
    assert 'id="player-name"' in html
    assert 'id="difficulty"' in html
