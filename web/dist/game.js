const $ = id => document.getElementById(id);
const names = ['North · 01 / Rifleman', 'North · 02 / Scout', 'North · 03 / Medic', 'South · 01 / Rifleman', 'South · 02 / Scout', 'South · 03 / Medic'];
const locations = ['Left leg', 'Right leg', 'Chest', 'Abdomen', 'Left arm', 'Right arm', 'Head'];
let e, selected = -1, action = 'move', busy = false, generation = 0, reportedFinish = false;
const s = (i, key) => e.state(i, key);
const friendly = i => Math.floor(i / 3) === s(0, 20);
const draw = () => s(0, 22) < 0 && !Array.from({length: 6}, (_, i) => i).some(i => s(i, 2) && (s(i, 5) >= 2 || s(i, 6) > 0));
const finished = () => s(0, 22) >= 0 || draw();
const active = () => selected >= 0 && s(selected, 2) && friendly(selected) && !finished() && !busy;
function log(text) {
    const li = document.createElement('li');
    li.textContent = text;
    $('log').prepend(li);
    while ($('log').children.length > 150) $('log').lastElementChild.remove();
}
function finishIfNeeded() {
    if (!finished()) return;
    busy = false;
    $('autopilot').checked = false;
    if (!reportedFinish) {
        generation++;
        reportedFinish = true;
        log(draw() ? 'Draw: both patrols are out of ammunition. Operation complete.' : 'Operation complete. Autopilot stopped.');
    }
}
function movementCircle() {
    if (!active() || action !== 'move') return;
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('class', 'range-overlay');
    svg.setAttribute('viewBox', '0 0 24 16');
    svg.setAttribute('preserveAspectRatio', 'none');
    svg.setAttribute('aria-hidden', 'true');
    const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    circle.setAttribute('cx', s(selected, 0) + 0.5);
    circle.setAttribute('cy', s(selected, 1) + 0.5);
    circle.setAttribute('r', e.movement_range_inches(selected) / 2);
    svg.append(circle);
    $('board').append(svg);
}
function render() {
    finishIfNeeded();
    const side = s(0, 20), win = s(0, 22);
    $('turn').textContent = draw() ? 'Draw · ammunition exhausted' : win >= 0 ? `${win ? 'South' : 'North'} patrol wins` : `Round ${s(0, 21)} / ${side ? 'South' : 'North'} patrol`;
    $('phase').textContent = finished() ? 'Operation complete' : busy ? ($('autopilot').checked ? 'Autopilot / AI controls both patrols' : 'Computer patrol is moving…') : 'Operation: Street crossing';
    $('board').replaceChildren();
    for (let y = 0; y < 16; y++) for (let x = 0; x < 24; x++) {
        let i = -1;
        for (let n = 0; n < 6; n++) if (s(n, 0) === x && s(n, 1) === y && s(n, 2)) { i = n; break; }
        const cell = document.createElement('button'), terrain = e.terrain(x, y);
        cell.className = 'cell';
        if (terrain) cell.classList.add(terrain === 2 ? 'ruin' : 'rubble');
        if (i >= 0) {
            cell.classList.add('unit');
            if (i >= 3) cell.classList.add('enemy');
            if (i === selected) cell.classList.add('selected');
            const text = document.createElement('span'); text.textContent = i % 3 + 1; cell.append(text);
        }
        if (active() && action === 'move' && e.can_move(selected, x, y)) cell.classList.add('reachable');
        if (active() && action === 'fire' && i >= 0 && e.can_attack(selected, i)) cell.classList.add('target');
        cell.setAttribute('aria-label', `Column ${x + 1}, row ${y + 1}, ${terrain === 2 ? 'ruins' : terrain ? 'rubble' : 'street'}${i >= 0 ? ', ' + names[i] : ''}`);
        cell.onclick = () => click(x, y, i);
        $('board').append(cell);
    }
    movementCircle();
    $('unitname').textContent = selected >= 0 ? names[selected] : 'Select a unit';
    $('unitinfo').textContent = selected >= 0 ? `${s(selected, 9) === 1 ? 'Rifle' : 'Carbine'} · ${s(selected, 5)}/10 rounds · ${s(selected, 6)} spare clips\n${s(selected, 2) ? `${s(selected, 3) ? 'Moved' : 'Move ready'} / ${s(selected, 4) ? 'Action used' : 'Action ready'}` : 'Incapacitated'}${s(selected, 7) ? ' / JAMMED' : ''}` : 'Choose a marker from the active patrol.';
    $('wounds').replaceChildren();
    if (selected >= 0) locations.forEach((name, k) => { const span = document.createElement('span'); span.textContent = `${name} ${s(selected, 11 + k)}`; $('wounds').append(span); });
    ['move', 'fire', 'heal', 'reload'].forEach(id => {
        $(id).disabled = !active() || (id === 'move' ? s(selected, 3) : s(selected, 4));
        $(id).classList.toggle('active', id === action);
    });
    $('end').disabled = busy || finished();
    $('autopilot').disabled = finished();
    $('hint').textContent = finished() ? 'Operation complete. Start a new operation to play again.' : busy ? ($('autopilot').checked ? 'Watching the battle. Disable Autopilot to take control.' : 'Resolving the opposing patrol’s turn.') : action === 'move' ? 'Choose a highlighted destination inside the circle. Ruins and units block the straight route.' : action === 'fire' ? 'Choose an orange highlighted opposing unit.' : 'Choose yourself or an adjacent ally for first aid.';
}
function click(x, y, i) {
    if (busy || finished()) return;
    if (active() && action === 'heal' && i >= 0 && friendly(i) && e.heal(selected, i)) {
        log(`${names[selected]}: first aid ${s(0, 26) ? 'restored ' + locations[s(0, 25)] : 'failed'} (${s(0, 23)} vs ${s(0, 24)}).`); render(); return;
    }
    if (i >= 0 && friendly(i)) { selected = i; render(); return; }
    if (!active()) return;
    if (action === 'move' && e.move_unit(selected, x, y)) log(`${names[selected]} moved to ${x + 1}, ${y + 1}.`);
    else if (action === 'fire' && i >= 0 && e.attack(selected, i)) report(selected, i);
    else { $('hint').textContent = 'That action is unavailable. Select a highlighted cell or valid target.'; return; }
    render();
}
function report(i, j) {
    log(`${names[i]} → ${names[j]}: ${s(0, 23)} vs ${s(0, 24)}. ${s(0, 26) ? 'Hit: ' + locations[s(0, 25)] + '.' : 'Miss.'}${s(i, 7) ? ' Weapon jammed.' : ''}${!s(j, 2) ? ' Target incapacitated.' : ''}`);
}
function reset() {
    generation++; busy = false; reportedFinish = false;
    e.start(crypto.getRandomValues(new Uint32Array(1))[0]); selected = 0; action = 'move';
    $('log').replaceChildren(); log('Operation started. Eliminate the opposing patrol.'); render(); scheduleAI();
}
const pause = () => new Promise(resolve => setTimeout(resolve, 700));
function scheduleAI() {
    if (finished()) { render(); return; }
    if (!busy && ($('autopilot').checked || ($('mode').value === 'ai' && s(0, 20) === 1))) void ai();
}
function takeControl() {
    generation++; busy = false;
    selected = Array.from({length: 3}, (_, k) => s(0, 20) * 3 + k).find(i => s(i, 2)) ?? -1;
    render();
}
// Match the Mac AI's Euclidean target ordering and weighted eight-way
// terrain distances. Actual movement legality is always checked by C.
function approachMap(target) {
    const distances = Array(384).fill(1000), queue = [s(target, 1) * 24 + s(target, 0)];
    distances[queue[0]] = 0;
    for (let h = 0; h < queue.length; h++) {
        const cell = queue[h], x = cell % 24, y = Math.floor(cell / 24);
        for (const [dx, dy] of [[1,0],[-1,0],[0,1],[0,-1],[1,1],[1,-1],[-1,1],[-1,-1]]) {
            const nx = x + dx, ny = y + dy;
            if (e.terrain(nx, ny) === 2 || (dx && dy && (e.terrain(nx, y) === 2 || e.terrain(x, ny) === 2))) continue;
            const next = ny * 24 + nx, cost = dx && dy ? Math.SQRT2 : 1;
            if (distances[next] > distances[cell] + cost + 0.000001) { distances[next] = distances[cell] + cost; queue.push(next); }
        }
    }
    return distances;
}
function stepAI(i) {
    selected = i;
    if (s(i, 2)) {
        const distance = j => (s(i, 0) - s(j, 0)) ** 2 + (s(i, 1) - s(j, 1)) ** 2;
        const enemies = Array.from({length: 6}, (_, j) => j).filter(j => Math.floor(j / 3) !== s(0, 20) && s(j, 2)).sort((a, b) => distance(a) - distance(b));
        if (!s(i, 4) && (s(i, 7) || s(i, 5) < 2)) if (e.reload(i)) log(`${names[i]} serviced its weapon.`);
        if (enemies.length && !enemies.some(j => e.can_attack(i, j))) {
            const distances = approachMap(enemies[0]); let best = -1, score = 1000;
            for (let cell = 0; cell < 384; cell++) if (e.can_move(i, cell % 24, Math.floor(cell / 24)) && distances[cell] < score) { best = cell; score = distances[cell]; }
            if (best >= 0 && e.move_unit(i, best % 24, Math.floor(best / 24))) log(`${names[i]} advanced.`);
        }
        const target = enemies.find(j => e.can_attack(i, j));
        if (target !== undefined) { if (e.attack(i, target)) report(i, target); }
        else if (e.heal(i, i)) log(`${names[i]}: first aid ${s(0, 26) ? 'restored ' + locations[s(0, 25)] : 'failed'}.`);
    }
    if (i % 3 === 2 && s(0, 22) < 0) { e.end_turn(); log('Patrol turn ended.'); }
    render();
}
async function ai() {
    if (busy || finished()) return;
    busy = true; const run = generation; render();
    do {
        const start = s(0, 20) * 3;
        for (let i = start; i < start + 3; i++) {
            await pause();
            if (run !== generation || finished()) { if (finished()) render(); return; }
            stepAI(i);
            if (finished()) return;
        }
    } while ($('autopilot').checked);
    busy = false;
    selected = Array.from({length: 3}, (_, k) => s(0, 20) * 3 + k).find(i => s(i, 2)) ?? -1;
    render(); scheduleAI();
}
$('autopilot').onchange = () => {
    if ($('autopilot').checked) { log('Autopilot enabled. AI controls both patrols.'); scheduleAI(); }
    else { takeControl(); log('Autopilot disabled. You control the current patrol.'); }
};
$('end').onclick = () => { if (busy || finished()) return; e.end_turn(); selected = -1; log('Patrol turn ended.'); render(); scheduleAI(); };
['move', 'fire', 'heal'].forEach(id => $(id).onclick = () => { action = id; render(); });
$('reload').onclick = () => { if (!active()) return; if (e.reload(selected)) { log(`${names[selected]} reloaded or cleared a jam.`); render(); } else $('hint').textContent = 'No spare clips available.'; };
$('new').onclick = reset;
$('mode').onchange = () => { takeControl(); scheduleAI(); };
$('help').onclick = () => $('manual').showModal();
$('save').onclick = () => {
    try {
        if (busy) { log('Wait until the computer turn ends before saving.'); return; }
        const data = {version: 1, bytes: Array.from(new Uint8Array(e.memory.buffer, e.save_ptr(), e.save_size())), side: s(0, 20), round: s(0, 21), mode: $('mode').value};
        localStorage.setItem('foc-save', JSON.stringify(data)); log('Operation saved on this browser.');
    } catch { log('This browser could not store the save.'); }
};
$('resume').onclick = () => {
    try {
        const data = JSON.parse(localStorage.getItem('foc-save'));
        if (!data || data.version !== 1 || data.bytes.length !== e.save_size() || ![0, 1].includes(data.side) || !Number.isInteger(data.round) || data.round < 1) throw Error();
        generation++; busy = false; reportedFinish = false;
        new Uint8Array(e.memory.buffer, e.save_ptr(), e.save_size()).set(data.bytes); e.restore_meta(data.side, data.round);
        $('mode').value = data.mode; selected = -1; log('Saved operation resumed.'); render(); scheduleAI();
    } catch { log('No compatible saved operation found.'); }
};
try {
    const response = await fetch('game.wasm'); if (!response.ok) throw Error(`HTTP ${response.status}`);
    const result = await WebAssembly.instantiate(await response.arrayBuffer(), {});
    e = result.instance.exports; reset(); $('engine').textContent = 'WASM ACTIVE';
} catch (err) {
    $('turn').textContent = 'Engine unavailable'; $('hint').textContent = 'Serve this folder over HTTP to load game.wasm. ' + err.message;
    document.querySelectorAll('button:not(#help), #autopilot').forEach(control => control.disabled = true);
}
