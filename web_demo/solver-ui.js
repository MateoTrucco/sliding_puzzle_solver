import { bootPython, parsePythonJson } from './pyodide-helper.js';

let py;
let board = [1, 2, 3, 4, 5, 6, 7, 8, 0];
let moves = [];
let manualMoves = 0;
const boardEl = document.querySelector('#board');
const out = document.querySelector('#output');
const solveButton = document.querySelector('#solve');
const animateButton = document.querySelector('#animate');
const stepButton = document.querySelector('#step');
let language = localStorage.getItem('mateo-ui-language') || (navigator.language.toLowerCase().startsWith('es') ? 'es' : 'en');
const t = (en, es) => language === 'es' ? es : en;

function draw() {
  boardEl.innerHTML = board.map((value, index) => `<button type="button" class="tile ${value === 0 ? 'blank' : ''}" data-index="${index}" ${value === 0 ? 'disabled' : ''} aria-label="${value === 0 ? 'Empty space' : `Tile ${value}`}">${value || ''}</button>`).join('');
}

async function init() {
  py = await bootPython(['solver.py']);
  solveButton.disabled = false;
  draw();
  out.textContent = t('Ready. Move a tile, shuffle the board or analyze the current state.','Listo. Mové una ficha, mezclá el tablero o analizá el estado actual.');
}

function neighbors(current) {
  const blank = current.indexOf(0);
  const row = Math.floor(blank / 3);
  const column = blank % 3;
  const options = [];
  for (const [rowDelta, columnDelta] of [[0, -1], [0, 1], [-1, 0], [1, 0]]) {
    const nextRow = row + rowDelta;
    const nextColumn = column + columnDelta;
    if (nextRow >= 0 && nextRow < 3 && nextColumn >= 0 && nextColumn < 3) {
      const next = [...current];
      const target = nextRow * 3 + nextColumn;
      [next[blank], next[target]] = [next[target], next[blank]];
      options.push(next);
    }
  }
  return options;
}

function shuffle() {
  const depth = Number(document.querySelector('#difficulty').value);
  for (let index = 0; index < depth; index += 1) {
    const options = neighbors(board);
    board = options[Math.floor(Math.random() * options.length)];
  }
  moves = [];
  manualMoves = 0;
  animateButton.disabled = true;
  stepButton.disabled = true;
  document.querySelector('#solverMetrics').innerHTML = '';
  draw();
  out.textContent = t(`Solvable board generated with ${depth} valid random moves.`,`Tablero resoluble generado con ${depth} movimientos aleatorios válidos.`);
}

function solve() {
  if (!py) return;
  py.globals.set('demo_board', board);
  const raw = py.runPython(`import json\nfrom solver import solve\nr=solve(list(demo_board))\njson.dumps({'status':r.status,'moves':list(r.moves),'explored':r.explored,'message':r.message})`);
  const data = parsePythonJson(raw);
  moves = data.moves;
  out.textContent = `${data.message}\n${t('Status','Estado')}: ${data.status}\n${t('Explored states','Estados explorados')}: ${data.explored}\n${t('Moves','Movimientos')}: ${moves.join(' ') || t('(none)','(ninguno)')}`;
  document.querySelector('#solverMetrics').innerHTML = `<div class="metric"><strong>${moves.length}</strong><small>${t('Optimal moves','Movimientos óptimos')}</small></div><div class="metric"><strong>${data.explored}</strong><small>${t('States explored','Estados explorados')}</small></div><div class="metric"><strong>${manualMoves}</strong><small>${t('Manual moves','Movimientos manuales')}</small></div>`;
  animateButton.disabled = !moves.length;
  stepButton.disabled = !moves.length;
}

function applyNext() {
  if (!moves.length) return;
  const move = moves.shift();
  py.globals.set('demo_board', board);
  py.globals.set('demo_move', move);
  board = parsePythonJson(py.runPython(`import json\nfrom solver import apply_move\njson.dumps(list(apply_move(tuple(demo_board),demo_move)))`));
  draw();
  stepButton.disabled = !moves.length;
  animateButton.disabled = !moves.length;
}

async function animate() {
  animateButton.disabled = true;
  stepButton.disabled = true;
  while (moves.length) {
    applyNext();
    await new Promise((resolve) => setTimeout(resolve, 190));
  }
  out.textContent += `\n${t('Animation complete.','Animación completa.')}`;
}

boardEl.addEventListener('click', (event) => {
  const tile = event.target.closest('[data-index]');
  if (!tile || tile.disabled) return;
  const index = Number(tile.dataset.index);
  const blank = board.indexOf(0);
  const distance = Math.abs(Math.floor(index / 3) - Math.floor(blank / 3)) + Math.abs(index % 3 - blank % 3);
  if (distance !== 1) return;
  [board[index], board[blank]] = [board[blank], board[index]];
  manualMoves += 1;
  moves = [];
  animateButton.disabled = true;
  stepButton.disabled = true;
  draw();
  out.textContent = t(`Manual move ${manualMoves}.`,`Movimiento manual ${manualMoves}.`);
});

solveButton.disabled = true;
draw();
document.querySelector('#shuffle').addEventListener('click', shuffle);
solveButton.addEventListener('click', solve);
document.querySelector('#reset').addEventListener('click', () => {
  board = [1, 2, 3, 4, 5, 6, 7, 8, 0];
  moves = [];
  manualMoves = 0;
  draw();
  out.textContent = t('Reset to solved state.','Reiniciado al estado resuelto.');
  animateButton.disabled = true;
  stepButton.disabled = true;
  document.querySelector('#solverMetrics').innerHTML = '';
});
animateButton.addEventListener('click', animate);
stepButton.addEventListener('click', applyNext);
init().catch(() => {});
document.addEventListener('mt:language', (event) => { language = event.detail.language; });
