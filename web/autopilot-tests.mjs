import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import vm from 'node:vm';
const wasm=await readFile(new URL('./dist/game.wasm',import.meta.url));
const {instance}=await WebAssembly.instantiate(wasm,{}),engine=instance.exports;
class Element {
 constructor(){this.children=[];this.checked=false;this.disabled=false;this.value='';this.textContent='';this.attributes={};this.classList={add(){},toggle(){}}}
 append(e){e.parent=this;this.children.push(e)} prepend(e){e.parent=this;this.children.unshift(e)} remove(){this.parent.children=this.parent.children.filter(x=>x!==this)} replaceChildren(){this.children=[]} setAttribute(key,value){this.attributes[key]=String(value)}
 get lastElementChild(){return this.children.at(-1)}
}
const elements=new Map(),get=id=>{if(!elements.has(id))elements.set(id,new Element());return elements.get(id)};
get('mode').value='local';const timers=[];let seed=123;const saves=new Map();
const context=vm.createContext({document:{getElementById:get,createElement:()=>new Element(),createElementNS:()=>new Element(),querySelectorAll:()=>[]},crypto:{getRandomValues:a=>{a[0]=seed;return a}},WebAssembly:{instantiate:async()=>({instance})},Uint8Array,Uint32Array,fetch:async()=>({ok:true,arrayBuffer:async()=>wasm}),setTimeout:fn=>timers.push(fn),localStorage:{setItem:(key,value)=>saves.set(key,value),getItem:key=>saves.get(key)}});
await vm.runInContext(`(async()=>{${await readFile(new URL('./dist/game.js',import.meta.url),'utf8')} })()`,context);
const tick=async()=>{const fn=timers.shift();if(fn)fn();await Promise.resolve();await Promise.resolve()};
const snapshot=()=>Array.from(new Uint8Array(engine.memory.buffer,engine.save_ptr(),engine.save_size()));
assert.equal(get('autopilot').disabled,false);
const radius=()=>get('board').children.find(x=>x.attributes.class==='range-overlay')?.children[0].attributes.r;
assert.equal(radius(),'1.5');
get('board').children[7*24+2].onclick();
assert.equal(radius(),'2.5');
get('new').onclick();
get('autopilot').checked=true;get('autopilot').onchange();
for(let n=0;n<50&&engine.state(0,21)<2;n++)await tick();
assert(engine.state(0,21)>=2,'autopilot must play both sides');assert(get('log').children.some(x=>x.textContent.startsWith('North ·')&&x.textContent.includes('advanced')));assert(get('log').children.some(x=>x.textContent.startsWith('South ·')&&x.textContent.includes('advanced')));
get('autopilot').checked=false;get('autopilot').onchange();const stopped=snapshot(),round=engine.state(0,21),side=engine.state(0,20);for(let n=0;n<10;n++)await tick();assert.deepEqual(snapshot(),stopped);assert.equal(engine.state(0,21),round);assert.equal(engine.state(0,20),side);assert.equal(get('end').disabled,false);
// Rapid off/on and reset while a timer is pending cannot let old loops mutate a new battle.
get('autopilot').checked=true;get('autopilot').onchange();get('autopilot').checked=false;get('autopilot').onchange();get('autopilot').checked=true;get('autopilot').onchange();get('new').onclick();for(let n=0;n<25;n++)await tick();assert(engine.state(0,21)>=1);assert(get('log').children.some(x=>x.textContent.includes('advanced')));
// A finished battle automatically clears the toggle.
const stride=engine.save_size()/6,view=new DataView(engine.memory.buffer);for(let i=3;i<6;i++)view.setInt32(engine.save_ptr()+i*stride+stride-60,0,true);engine.restore_meta(engine.state(0,20),engine.state(0,21));assert.equal(engine.state(0,22),0);for(let n=0;n<10;n++)await tick();assert.equal(get('autopilot').checked,false);assert.equal(get('end').disabled,true);
console.log('Autopilot checks passed: both sides advance, disabling stops pending actions, rapid toggles/reset cancel old loops, and victory stops autopilot.');

// Match the Mac regression battle, including exhaustion and terminal controls.
seed=253;get('new').onclick();get('autopilot').checked=true;get('autopilot').onchange();
let oneSideEmpty=false;
for(let n=0;n<1200&&get('autopilot').checked;n++){
 const empty=[0,1].map(side=>![0,1,2].some(k=>{const i=side*3+k;return engine.state(i,2)&&(engine.state(i,5)>=2||engine.state(i,6)>0)}));
 if(empty[0]!==empty[1]&&engine.state(0,22)<0){oneSideEmpty=true;assert(!get('turn').textContent.includes('Draw'));}
 await tick();
}
assert(oneSideEmpty,'One empty patrol must not end the game prematurely');
assert.equal(engine.state(0,22),-1);
assert.equal(get('turn').textContent,'Draw · ammunition exhausted');
assert.equal(get('autopilot').checked,false);assert.equal(get('end').disabled,true);
assert(get('log').children.some(x=>x.textContent.includes('both patrols are out of ammunition')));
const drawn=snapshot(),drawnRound=engine.state(0,21);
get('autopilot').checked=true;get('autopilot').onchange();get('end').onclick();
for(let n=0;n<10;n++)await tick();
assert.deepEqual(snapshot(),drawn);assert.equal(engine.state(0,21),drawnRound);
assert.equal(get('autopilot').checked,false);
get('save').onclick();seed=123;get('new').onclick();assert.equal(get('end').disabled,false);
get('resume').onclick();assert.equal(get('turn').textContent,'Draw · ammunition exhausted');
assert.equal(get('end').disabled,true);assert.deepEqual(snapshot(),drawn);
console.log('Mac parity checks passed: circular overlays, ammunition draw, no premature draw, terminal controls and save/resume.');
