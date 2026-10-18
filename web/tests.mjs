import {readFile} from 'node:fs/promises';
import assert from 'node:assert/strict';
const {instance}=await WebAssembly.instantiate(await readFile(new URL('./dist/game.wasm',import.meta.url)),{}),e=instance.exports;
const count=e.unit_count(),size=e.patrol_size();
const stride=e.save_size()/count,base=e.save_ptr(),view=new DataView(e.memory.buffer),xOffset=stride-28;
const position=(i,x,y)=>{view.setInt32(base+i*stride+xOffset,x,true);view.setInt32(base+i*stride+xOffset+4,y,true)};
const ammo=(i,rounds,clips=0)=>{view.setInt32(base+i*stride+xOffset-8,rounds,true);view.setInt32(base+i*stride+xOffset-12,clips,true);assert.equal(e.state(i,5),rounds)};
e.start(123);assert.equal(count,10);assert.equal(size,5);
for(let side=0;side<2;side++){
 const b=side*size;assert.equal(e.state(b+3,9),4);assert.equal(e.state(b+4,9),0);
 assert.equal(e.unit_skill(b+4,17),1);assert.equal(e.unit_skill(b+1,16),1);assert.equal(e.unit_skill(b+2,13),1);
}
for(let i=0;i<count;i++)assert(e.movement_range_inches(i)/2>3);
assert.equal(e.can_move(0,5,3),1);assert.equal(e.can_move(0,6,2),0);
assert.equal(e.can_move(5,20,1),0);assert.equal(e.can_move(0,-1,0),0);
assert.equal(e.move_unit(0,3,2),1);assert.equal(e.move_unit(0,4,2),0);
e.start(123);position(1,7,3);assert.equal(e.can_move(1,9,3),0,'Ruins block routes');
position(0,7,2);assert.equal(e.can_move(0,8,1),0,'No diagonal corner cutting');
e.start(123);assert.equal(e.can_move(1,6,0),0);assert.equal(e.can_run(1,6,0),1);assert.equal(e.run_unit(1,6,0),1);
assert.equal(e.state(1,3),1);assert.equal(e.state(1,4),1);assert.equal(e.state(1,27),2);
assert.equal(e.reload(1),0);assert.equal(e.can_attack(1,5),0);e.end_turn();assert.equal(e.state(1,27),2);e.end_turn();assert.equal(e.state(1,27),0);
e.start(123);position(5,6,1);assert.equal(e.focused_attack(0,5),1);assert.equal(e.state(0,31),1);assert.equal(e.state(0,5),8);assert.equal(e.can_move(0,3,1),0);
e.start(123);position(5,6,1);assert.equal(e.move_unit(0,3,1),1);assert.equal(e.can_focus_attack(0,5),0);assert.equal(e.attack(0,5),1);
e.start(123);position(4,3,13);position(9,8,13);assert.equal(e.can_attack(4,9),0);position(9,9,13);
assert.equal(e.focused_attack(4,9),1);assert.equal(e.state(4,5),9);assert.equal(e.state(0,31),2);assert.equal(e.state(0,30),5);
e.start(123);position(3,3,10);position(8,6,10);ammo(3,2);assert.equal(e.can_attack(3,8),0);ammo(3,3);assert.equal(e.attack(3,8),1);assert.equal(e.state(3,5),0);
// Running targets lose two incoming attack dice; ordinary movers lose one.
for(const run of [false,true]){
 e.start(123);position(0,3,1);position(5,6,1);e.end_turn();
 assert.equal(run?e.run_unit(5,6,3):e.move_unit(5,6,3),1);e.end_turn();
 assert.equal(e.attack(0,5),1);assert.equal(e.state(0,30),run?1:2);
}
e.start(123);for(let i=0;i<count;i++)ammo(i,0);ammo(9,1);assert.equal(e.ammunition_exhausted(),0);ammo(9,0);ammo(3,2);assert.equal(e.ammunition_exhausted(),1);
console.log('WASM checks passed: five-person rosters, skills, circular movement, running, focus, sniper minimum range, SMG ammo, movement penalties and draw detection.');
