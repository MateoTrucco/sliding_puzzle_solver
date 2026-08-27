import {bootPython,parsePythonJson} from './pyodide-helper.js';
let py,board=[1,2,3,4,5,6,7,8,0],moves=[];const boardEl=document.querySelector('#board'),out=document.querySelector('#output'),solveBtn=document.querySelector('#solve'),animateBtn=document.querySelector('#animate');
function draw(){boardEl.innerHTML=board.map(v=>`<div class="tile ${v===0?'blank':''}">${v||''}</div>`).join('');}
async function init(){py=await bootPython(['solver.py']);solveBtn.disabled=false;draw();out.textContent='Ready. Shuffle the board or solve the current state.';}
function neighborsJS(b){const z=b.indexOf(0),r=Math.floor(z/3),c=z%3,res=[];for(const [dr,dc] of [[0,-1],[0,1],[-1,0],[1,0]]){const nr=r+dr,nc=c+dc;if(nr>=0&&nr<3&&nc>=0&&nc<3){const n=[...b],i=nr*3+nc;[n[z],n[i]]=[n[i],n[z]];res.push(n)}}return res;}
function shuffle(){for(let i=0;i<28;i++){const opts=neighborsJS(board);board=opts[Math.floor(Math.random()*opts.length)]}moves=[];animateBtn.disabled=true;draw();out.textContent='Solvable board generated with valid moves.';}
function solve(){if(!py)return;py.globals.set('demo_board',board);const raw=py.runPython(`import json
from solver import solve
r=solve(list(demo_board))
json.dumps({'status':r.status,'moves':list(r.moves),'explored':r.explored,'message':r.message})`);const data=parsePythonJson(raw);moves=data.moves;out.textContent=`${data.message}
Status: ${data.status}
Explored states: ${data.explored}
Moves: ${moves.join(' ')||'(none)'}`;animateBtn.disabled=!moves.length;}
async function animate(){animateBtn.disabled=true;for(const move of moves){py.globals.set('demo_board',board);py.globals.set('demo_move',move);board=parsePythonJson(py.runPython(`import json
from solver import apply_move
json.dumps(list(apply_move(tuple(demo_board),demo_move)))`));draw();await new Promise(r=>setTimeout(r,220));}moves=[];out.textContent+='
Animation complete.';}
solveBtn.disabled=true;draw();document.querySelector('#shuffle').addEventListener('click',shuffle);solveBtn.addEventListener('click',solve);document.querySelector('#reset').addEventListener('click',()=>{board=[1,2,3,4,5,6,7,8,0];moves=[];draw();out.textContent='Reset to solved state.';animateBtn.disabled=true});animateBtn.addEventListener('click',animate);init().catch(()=>{});
