// Client-side rendering and interaction for the Flask-backed Sudoku
const SIZE = 9;
const LEADERBOARD_KEY = 'sudokuLeaderboard';
const DIFFICULTY_SETTINGS = {
  easy: 44,
  medium: 35,
  hard: 30,
};

let puzzle = [];
let startTime = null;
let hintsUsed = 0;
let currentDifficulty = 'medium';
let gameSolved = false;

function createBoardElement() {
  const boardDiv = document.getElementById('sudoku-board');
  boardDiv.innerHTML = '';
  for (let i = 0; i < SIZE; i++) {
    const rowDiv = document.createElement('div');
    rowDiv.className = 'sudoku-row';
    for (let j = 0; j < SIZE; j++) {
      const input = document.createElement('input');
      input.type = 'text';
      input.maxLength = 1;
      input.className = 'sudoku-cell';
      input.dataset.row = i;
      input.dataset.col = j;
      input.addEventListener('input', (e) => {
        if (gameSolved) {
          e.target.value = '';
          return;
        }

        const val = e.target.value.replace(/[^1-9]/g, '');
        e.target.value = val;
        const board = getBoardState();
        const conflicts = findBoardConflicts(board);
        updateBoardHighlights(conflicts);
      });
      rowDiv.appendChild(input);
    }
    boardDiv.appendChild(rowDiv);
  }
}

function setMessage(text, color = '#333') {
  const msg = document.getElementById('message');
  msg.style.color = color;
  msg.innerText = text;
}

function getElapsedSeconds() {
  if (!startTime) {
    return 0;
  }
  return Math.round((Date.now() - startTime) / 1000);
}

function updateStatus() {
  document.getElementById('time-elapsed').innerText = getElapsedSeconds();
  document.getElementById('hints-used').innerText = hintsUsed;
}

function getCellIndex(row, col) {
  return row * SIZE + col;
}

function findBoardConflicts(board) {
  const conflicts = new Set();

  for (let row = 0; row < SIZE; row++) {
    const seen = new Map();
    for (let col = 0; col < SIZE; col++) {
      const value = board[row][col];
      if (!value) {
        continue;
      }
      if (seen.has(value)) {
        conflicts.add(`${row}:${seen.get(value)}`);
        conflicts.add(`${row}:${col}`);
      } else {
        seen.set(value, col);
      }
    }
  }

  for (let col = 0; col < SIZE; col++) {
    const seen = new Map();
    for (let row = 0; row < SIZE; row++) {
      const value = board[row][col];
      if (!value) {
        continue;
      }
      if (seen.has(value)) {
        conflicts.add(`${seen.get(value)}:${col}`);
        conflicts.add(`${row}:${col}`);
      } else {
        seen.set(value, row);
      }
    }
  }

  for (let boxRow = 0; boxRow < SIZE; boxRow += 3) {
    for (let boxCol = 0; boxCol < SIZE; boxCol += 3) {
      const seen = new Map();
      for (let row = boxRow; row < boxRow + 3; row++) {
        for (let col = boxCol; col < boxCol + 3; col++) {
          const value = board[row][col];
          if (!value) {
            continue;
          }
          if (seen.has(value)) {
            conflicts.add(`${seen.get(value)}:${col}`);
            conflicts.add(`${row}:${col}`);
          } else {
            seen.set(value, `${row}:${col}`);
          }
        }
      }
    }
  }

  return Array.from(conflicts).map((entry) => {
    const [row, col] = entry.split(':').map(Number);
    return [row, col];
  });
}

function updateBoardHighlights(conflicts = [], incorrect = []) {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const conflictIndices = new Set(conflicts.map(([row, col]) => getCellIndex(row, col)));
  const incorrectIndices = new Set(incorrect.map(([row, col]) => getCellIndex(row, col)));

  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE; j++) {
      const idx = getCellIndex(i, j);
      const inp = inputs[idx];
      const isPrefilled = inp.disabled || puzzle[i][j] !== 0;
      let className = 'sudoku-cell';

      if (isPrefilled) {
        className += ' prefilled';
      }
      if (conflictIndices.has(idx)) {
        className += ' conflict';
      }
      if (incorrectIndices.has(idx) && !isPrefilled) {
        className += ' incorrect';
      }

      inp.className = className;
    }
  }
}

function renderPuzzle(puz) {
  puzzle = puz;
  createBoardElement();
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE; j++) {
      const idx = getCellIndex(i, j);
      const val = puzzle[i][j];
      const inp = inputs[idx];
      if (val !== 0) {
        inp.value = val;
        inp.disabled = true;
      } else {
        inp.value = '';
        inp.disabled = false;
      }
    }
  }
  updateBoardHighlights();
}

function loadLeaderboard() {
  const raw = localStorage.getItem(LEADERBOARD_KEY);
  try {
    const records = JSON.parse(raw);
    return Array.isArray(records) ? records : [];
  } catch {
    return [];
  }
}

function saveLeaderboard(records) {
  localStorage.setItem(LEADERBOARD_KEY, JSON.stringify(records));
}

function formatTime(seconds) {
  return `${seconds}s`;
}

function renderLeaderboard(records) {
  const body = document.querySelector('#leaderboard tbody');
  body.innerHTML = '';

  if (!records.length) {
    const emptyRow = document.createElement('tr');
    emptyRow.innerHTML = '<td colspan="5">No completed games yet.</td>';
    body.appendChild(emptyRow);
    return;
  }

  records.forEach((record, index) => {
    const row = document.createElement('tr');
    row.innerHTML = `
      <td>${index + 1}</td>
      <td>${record.name}</td>
      <td>${formatTime(record.time)}</td>
      <td>${record.difficulty}</td>
      <td>${record.hints}</td>
    `;
    body.appendChild(row);
  });
}

function addLeaderboardRecord(record) {
  const records = loadLeaderboard();
  records.push(record);
  records.sort((a, b) => a.time - b.time || a.hints - b.hints);
  const topRecords = records.slice(0, 10);
  saveLeaderboard(topRecords);
  renderLeaderboard(topRecords);
}

function getBoardState() {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const board = [];
  for (let i = 0; i < SIZE; i++) {
    board[i] = [];
    for (let j = 0; j < SIZE; j++) {
      const idx = getCellIndex(i, j);
      const val = inputs[idx].value;
      board[i][j] = val ? parseInt(val, 10) : 0;
    }
  }
  return board;
}

async function newGame() {
  const difficulty = document.getElementById('difficulty').value;
  const clues = DIFFICULTY_SETTINGS[difficulty] || DIFFICULTY_SETTINGS.medium;
  const res = await fetch(`/new?difficulty=${encodeURIComponent(difficulty)}&clues=${clues}`);
  const data = await res.json();
  renderPuzzle(data.puzzle);
  currentDifficulty = difficulty;
  startTime = Date.now();
  hintsUsed = 0;
  gameSolved = false;
  updateStatus();
  setMessage('');
}

async function requestHint() {
  if (gameSolved) {
    return;
  }

  const board = getBoardState();
  const res = await fetch('/hint', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board}),
  });
  const data = await res.json();
  if (data.error) {
    setMessage(data.error, '#d32f2f');
    return;
  }

  const rowIndex = data.row;
  const colIndex = data.col;
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const idx = rowIndex * SIZE + colIndex;
  const input = inputs[idx];
  input.value = data.value;
  input.disabled = true;
  input.classList.add('prefilled');

  hintsUsed += 1;
  updateStatus();
  updateBoardHighlights();
}

async function checkSolution() {
  const board = getBoardState();
  const res = await fetch('/check', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board}),
  });
  const data = await res.json();
  if (data.error) {
    setMessage(data.error, '#d32f2f');
    return;
  }

  const incorrect = data.incorrect || [];
  const conflicts = data.conflicts || [];
  updateBoardHighlights(conflicts, incorrect);

  if (data.solved) {
    gameSolved = true;
    const boardDiv = document.getElementById('sudoku-board');
    const inputs = boardDiv.getElementsByTagName('input');
    for (let idx = 0; idx < inputs.length; idx++) {
      const inp = inputs[idx];
      if (!inp.disabled) {
        inp.disabled = true;
      }
    }

    const elapsed = getElapsedSeconds();
    const name = document.getElementById('player-name').value.trim() || 'Anonymous';
    addLeaderboardRecord({
      name,
      time: elapsed,
      difficulty: currentDifficulty,
      hints: hintsUsed,
    });
    setMessage(`Congratulations! You solved it in ${elapsed}s.`, '#388e3c');
    return;
  }

  if (incorrect.length === 0) {
    setMessage('Your current entries are valid so far.', '#388e3c');
  } else {
    setMessage('Some cells are incorrect.', '#d32f2f');
  }
}

window.addEventListener('load', () => {
  document.getElementById('new-game').addEventListener('click', newGame);
  document.getElementById('hint-button').addEventListener('click', requestHint);
  document.getElementById('check-solution').addEventListener('click', checkSolution);
  renderLeaderboard(loadLeaderboard());
  newGame();
  setInterval(updateStatus, 1000);
});
