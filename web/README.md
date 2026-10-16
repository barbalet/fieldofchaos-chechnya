# Field of Chaos browser skirmish

A playable static browser game using the existing Gold C rules compiled to genuine WebAssembly. Includes a selectable Autopilot that plays both sides with paced actions and can be disabled mid-turn to take control, a 3-vs-3 battle, computer opponent, shared-device two-player mode, movement/pathfinding, blocking terrain, cover, ranged fire, wounds/incapacitation, ammunition, reloads, first aid, victory and browser-local saves.

## Play locally

From the repository root: `python3 -m http.server 8080`, then open http://localhost:8080. The root `index.html` opens `web/index.html`, which loads the game assets from `web/dist/`. You can also serve just the website with `python3 -m http.server 8080 --directory web`, or run `python3 -m http.server 8080` from inside `web/`. A precompiled `dist/game.wasm` is included. No server-side application or npm packages are required.

Use an HTTP server: opening HTML directly with `file://` cannot reliably load the WASM module.

## Rebuild

Run `./build.sh`. Set `WASM_CC` and `WASM_LD` to your LLVM clang and wasm-ld executables if they differ from the defaults. Requires a clang with wasm32 support and lld. The tiny freestanding runtime supplies only memset and strcmp; no imported JavaScript rules or WASI runtime are used.

`engine/vendor` snapshots the C library from the fieldofchaos submodule so hosting can build without recursively fetching it. Update all three files together when syncing rules. The original rules are unchanged; `engine/game.c` implements the skirmish orchestration.

## Scope and adaptations

One cell = two tabletop inches. Each unit gets one circular-range, straight-line move and one action per patrol turn; movement uses Euclidean distance without rounding away partial cells (rifle: 1.5-cell radius, carbine: 2.5-cell radius), with ruins and standing units blocking the route and diagonal corner crossings; weapon range uses Chebyshev distance, sight uses a grid ray. Every unit has Firearm Basic/Advanced, Close Combat and First Aid, default wound pools, a rifle or carbine, 10 loaded rounds and 3 spare clips. Ranged attacks use the Gold library's single attack resolution, including its two-round expenditure for advanced rifle/carbine use. No historical claims or campaign simulation are made.

Supported rules: Gold firearm range/skills/cover, ammunition, movement restrictions, seven hit locations, wound effects, healing. Not implemented: grenade, shotgun, melee, called head shots, special foes, character creation or campaign progression. Hotseat is shared-device multiplayer; remote network multiplayer is not implemented. Saves persist units and turn metadata; future random rolls are reseeded on page load rather than replaying an exact RNG stream.

## Checks

`node autopilot-tests.mjs` verifies both-side play, stopping, rapid toggles, reset cancellation and victory shutdown using the real WASM engine with a controlled timer queue.

`node tests.mjs` exercises the compiled WASM module, terrain/path movement, turn restrictions, range/sight, ammunition, combat and victory. The upstream Gold C suite runs with `make -C ../fieldofchaos/src test`.
