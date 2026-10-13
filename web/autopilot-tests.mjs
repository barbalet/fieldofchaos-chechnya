import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import vm from 'node:vm';
const wasm=await readFile(new URL('./dist/game.wasm',import.meta.url));
const {instance}=await WebAssembly.instantiate(wasm,{}),engine=instance.exports;
class Element {
 constructor(){this.children=[];this.checked=false;this.disabled=false;this.value='';this.textContent='';this.classList={add(){},toggle(){}}}
 append(e){this.children.push(e)} prepend(e){this.children.unshift(e)} replaceChildren(){this.children=[]} setAttribute(){}
}
const elements=new Map(),get=id=>{if(!elements.has(id))elements.set(id,new Element());return elements.get(id)};
get('mode').value='local';const timers=[];
const context=vm.createContext({document:{getElementById:get,createElement:()=>new Element(),querySelectorAll:()=>[]},crypto:{getRandomValues:a=>{a[0]=123;return a}},WebAssembly:{instantiate:async()=>({instance})},Uint8Array,Uint32Array,fetch:async()=>({ok:true,arrayBuffer:async()=>wasm}),setTimeout:fn=>timers.push(fn)});
await vm.runInContext(`(async()=>{${await readFile(new URL('./dist/game.js',import.meta.url),'utf8')} })()`,context);
const tick=async()=>{const fn=timers.shift();if(fn)fn();await Promise.resolve();await Promise.resolve()};
const snapshot=()=>Array.from(new Uint8Array(engine.memory.buffer,engine.save_ptr(),engine.save_size()));
assert.equal(get('autopilot').disabled,false);
get('autopilot').checked=true;get('autopilot').onchange();
for(let n=0;n<50&&engine.state(0,21)<2;n++)await tick();
assert(engine.state(0,21)>=2,'autopilot must play both sides');assert(get('log').children.some(x=>x.textContent.startsWith('North ·')&&x.textContent.includes('advanced')));assert(get('log').children.some(x=>x.textContent.startsWith('South ·')&&x.textContent.includes('advanced')));
get('autopilot').checked=false;get('autopilot').onchange();const stopped=snapshot(),round=engine.state(0,21),side=engine.state(0,20);for(let n=0;n<10;n++)await tick();assert.deepEqual(snapshot(),stopped);assert.equal(engine.state(0,21),round);assert.equal(engine.state(0,20),side);assert.equal(get('end').disabled,false);
// Rapid off/on and reset while a timer is pending cannot let old loops mutate a new battle.
get('autopilot').checked=true;get('autopilot').onchange();get('autopilot').checked=false;get('autopilot').onchange();get('autopilot').checked=true;get('autopilot').onchange();get('new').onclick();for(let n=0;n<25;n++)await tick();assert(engine.state(0,21)>=1);assert(get('log').children.some(x=>x.textContent.includes('advanced')));
// A finished battle automatically clears the toggle.
const stride=engine.save_size()/6,view=new DataView(engine.memory.buffer);for(let i=3;i<6;i++)view.setInt32(engine.save_ptr()+i*stride+stride-60,0,true);engine.restore_meta(engine.state(0,20),engine.state(0,21));assert.equal(engine.state(0,22),0);for(let n=0;n<10;n++)await tick();assert.equal(get('autopilot').checked,false);assert.equal(get('end').disabled,true);
console.log('Autopilot checks passed: both sides advance, disabling stops pending actions, rapid toggles/reset cancel old loops, and victory stops autopilot.');
