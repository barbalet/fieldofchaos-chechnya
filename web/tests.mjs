import {readFile} from 'node:fs/promises';
import assert from 'node:assert/strict';
const {instance}=await WebAssembly.instantiate(await readFile(new URL('./dist/game.wasm',import.meta.url)),{}),e=instance.exports;
e.start(123);assert.equal(e.state(0,20),0);assert.equal(e.state(0,8),13);assert.equal(e.move_unit(3,20,3),0);assert.equal(e.move_unit(0,4,3),0);assert.equal(e.move_unit(0,3,3),1);assert.equal(e.move_unit(0,4,3),0);assert.equal(e.move_unit(1,-1,7),0);assert.equal(e.terrain(8,3),2);assert.equal(e.terrain(5,10),1);assert.equal(e.can_attack(0,1),0);assert.equal(e.can_attack(0,3),0);
e.end_turn();assert.equal(e.state(0,20),1);assert.equal(e.state(0,3),0);e.end_turn();assert.equal(e.state(0,21),2);
// Position through the save interface to test deterministic close-range combat.
e.start(456);const bytes=new Uint8Array(e.memory.buffer,e.save_ptr(),e.save_size());const saved=bytes.slice();assert(e.save_size()%6===0);const stride=e.save_size()/6;const view=new DataView(e.memory.buffer);const base=e.save_ptr();
// x and y are followed by four turn integers at the end of each Unit.
const xOffset=stride-20;view.setInt32(base+xOffset,3,true);view.setInt32(base+xOffset+4,3,true);view.setInt32(base+3*stride+xOffset,5,true);view.setInt32(base+3*stride+xOffset+4,3,true);
assert.equal(e.can_attack(0,3),1);assert.equal(e.attack(0,3),1);assert.equal(e.state(0,5),8);assert.equal(e.attack(0,3),0);assert(e.state(0,23)>0);assert.equal(e.state(0,24),4);
bytes.set(saved);e.restore_meta(0,1);assert.equal(e.state(0,0),2);assert.equal(e.state(0,5),10);
// Repeated attacks use real wounds and eventually incapacitate the target.
view.setInt32(base+xOffset,3,true);view.setInt32(base+xOffset+4,3,true);view.setInt32(base+3*stride+xOffset,5,true);view.setInt32(base+3*stride+xOffset+4,3,true);
for(let n=0;n<150&&e.alive(3);n++){if(e.state(0,5)<2)e.reload(0);else e.attack(0,3);e.end_turn();e.end_turn()}
assert.equal(e.alive(3),0);assert.equal(e.can_attack(0,3),0);
console.log('WASM checks passed: initialization, terrain, path limits, ownership, turns, range, combat, ammunition, save restoration and incapacitation.');
