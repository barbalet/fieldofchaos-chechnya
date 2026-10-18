import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import vm from 'node:vm';
const wasm=await readFile(new URL('./dist/game.wasm',import.meta.url));
const {instance}=await WebAssembly.instantiate(wasm,{}),engine=instance.exports;
class Element {
 constructor(){this.children=[];this.checked=false;this.disabled=false;this.value='';this.textContent='';this.attributes={};this.classList={add(){},toggle(){}}}
 append(e){e.parent=this;this.children.push(e)} prepend(e){e.parent=this;this.children.unshift(e)}
 remove(){this.parent.children=this.parent.children.filter(x=>x!==this)} replaceChildren(){this.children=[]}
 setAttribute(key,value){this.attributes[key]=String(value)} get lastElementChild(){return this.children.at(-1)}
}
const elements=new Map(),get=id=>{if(!elements.has(id))elements.set(id,new Element());return elements.get(id)};
get('mode').value='local';const timers=[],saves=new Map();let seed=123;
const context=vm.createContext({document:{getElementById:get,createElement:()=>new Element(),createElementNS:()=>new Element(),querySelectorAll:()=>[]},crypto:{getRandomValues:a=>{a[0]=seed;return a}},WebAssembly:{instantiate:async()=>({instance})},Uint8Array,Uint32Array,fetch:async()=>({ok:true,arrayBuffer:async()=>wasm}),setTimeout:fn=>timers.push(fn),localStorage:{setItem:(key,value)=>saves.set(key,value),getItem:key=>saves.get(key)}});
await vm.runInContext(`(async()=>{${await readFile(new URL('./dist/game.js',import.meta.url),'utf8')} })()`,context);
const tick=async()=>{const fn=timers.shift();if(fn)fn();await Promise.resolve();await Promise.resolve()};
const snapshot=()=>Array.from(new Uint8Array(engine.memory.buffer,engine.save_ptr(),engine.save_size()));
const radius=()=>get('board').children.find(x=>x.attributes.class==='range-overlay')?.children[0].attributes.r;
assert.equal(radius(),'4');assert(get('skills').textContent.includes('Firearm Advanced'));
get('board').children[13*24+2].onclick();assert(get('skills').textContent.includes('Sniper Training'));assert(get('unitinfo').textContent.includes('Sniper rifle'));
get('board').children[4*24+2].onclick();assert.equal(radius(),'5');get('run').onclick();assert.equal(radius(),'10');
get('board').children[6].onclick();assert.equal(engine.state(1,27),2);assert.equal(get('fire').disabled,true);
get('new').onclick();get('autopilot').checked=true;get('autopilot').onchange();
for(let n=0;n<50&&engine.state(0,21)<2;n++)await tick();assert(engine.state(0,21)>=2);
assert(get('log').children.some(x=>x.textContent.startsWith('North ·')));assert(get('log').children.some(x=>x.textContent.startsWith('South ·')));
get('autopilot').checked=false;get('autopilot').onchange();const stopped=snapshot();for(let n=0;n<10;n++)await tick();assert.deepEqual(snapshot(),stopped);assert.equal(get('end').disabled,false);
// Cancel old timers across rapid toggles and reset.
get('autopilot').checked=true;get('autopilot').onchange();get('autopilot').checked=false;get('autopilot').onchange();get('new').onclick();
const stride=engine.save_size()/10,base=engine.save_ptr(),view=new DataView(engine.memory.buffer);
const ammo=(i,rounds)=>{view.setInt32(base+i*stride+stride-36,rounds,true);view.setInt32(base+i*stride+stride-40,0,true)};
for(let i=0;i<10;i++)ammo(i,0);ammo(9,1);
get('move').onclick();assert.equal(get('end').disabled,false,'The sniper can fire one round');
ammo(9,0);ammo(0,2);view.setInt32(base+5*stride+stride-28,6,true);view.setInt32(base+5*stride+stride-24,1,true);
get('autopilot').checked=true;get('autopilot').onchange();for(let n=0;n<20&&get('autopilot').checked;n++)await tick();
assert.equal(get('turn').textContent,'Draw · ammunition exhausted');assert.equal(get('autopilot').checked,false);assert.equal(get('end').disabled,true);
const drawn=snapshot();get('autopilot').checked=true;get('autopilot').onchange();get('end').onclick();for(let n=0;n<10;n++)await tick();assert.deepEqual(snapshot(),drawn);
get('save').onclick();get('new').onclick();assert.equal(get('end').disabled,false);get('resume').onclick();assert.equal(get('turn').textContent,'Draw · ammunition exhausted');assert.deepEqual(snapshot(),drawn);
// Patrol victory includes all five opponents, not just the first three.
get('new').onclick();for(let i=5;i<10;i++)view.setInt32(base+i*stride+stride-68,0,true);engine.restore_meta(0,1);get('move').onclick();assert.equal(get('turn').textContent,'North patrol wins');
console.log('Browser checks passed: five-unit skill display, run circle/action cost, both-side AI, cancellation, weapon-aware draws, terminal save/resume and five-opponent victory.');
