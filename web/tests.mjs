import {readFile} from 'node:fs/promises';
import assert from 'node:assert/strict';
const {instance}=await WebAssembly.instantiate(await readFile(new URL('./dist/game.wasm',import.meta.url)),{}),e=instance.exports;
e.start(123);assert.equal(e.state(0,20),0);assert.equal(e.state(0,8),13);assert.equal(e.move_unit(3,20,3),0);assert.equal(e.move_unit(0,7,3),0);assert.equal(e.move_unit(0,3,3),1);assert.equal(e.move_unit(0,4,3),0);assert.equal(e.move_unit(1,-1,7),0);assert.equal(e.terrain(8,3),2);assert.equal(e.terrain(5,10),1);assert.equal(e.can_attack(0,1),0);assert.equal(e.can_attack(0,3),0);
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

// Circular movement gives all healthy agents a radius greater than 3, rather than flooring
// to cells or counting Manhattan/diagonal steps.
e.start(123);
assert.equal(e.movement_range_inches(0),8);
for(let i=0;i<6;i++)assert(e.movement_range_inches(i)/2>3);
assert.equal(e.can_move(0,5,5),1); // sqrt(13) cells fits a 4-cell radius
assert.equal(e.can_move(0,7,3),0); // 10 inches, outside the 8-inch rifle radius
assert.equal(e.can_move(1,4,8),1); // sqrt(5) cells = 4.47 inches
assert.equal(e.can_move(1,6,11),0); // sqrt(32) cells exceeds the 5-cell carbine radius
const position=(unit,x,y)=>{view.setInt32(base+unit*stride+xOffset,x,true);view.setInt32(base+unit*stride+xOffset+4,y,true)};
position(1,7,3);
assert.equal(e.can_move(1,9,3),0,'No movement through a ruin');
position(0,7,2);
assert.equal(e.can_move(0,8,1),0,'No diagonal corner cutting beside a ruin');
e.start(123);position(1,1,3);
assert.equal(e.can_move(1,2,4),0,'A standing unit blocks a diagonal corner');
console.log('Circular movement checks passed: fractional-cell radii, diagonal distances, blocked routes and corners.');

e.start(123);
assert.equal(e.state(0,10),4);assert.equal(e.state(1,10),5);
// Leg injuries retain their normal movement penalties at the larger scale.
view.setInt32(base+stride-40,0,true);
assert.equal(e.movement_range_inches(0),4);
view.setInt32(base+stride-36,0,true);
assert.equal(e.movement_range_inches(0),0);
