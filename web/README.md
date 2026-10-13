# Field of Chaos browser skirmish

A playable static browser game using the existing Gold C rules compiled to genuine WebAssembly. Includes a selectable Autopilot that plays both sides with paced actions and can be disabled mid-turn to take control, a 3-vs-3 battle, computer opponent, shared-device two-player mode, movement/pathfinding, blocking terrain, cover, ranged fire, wounds/incapacitation, ammunition, reloads, first aid, victory and browser-local saves.

## Play locally

From this directory: `python3 -m http.server 8080 --directory dist`, then open http://localhost:8080. A precompiled `dist/game.wasm` is included. No server-side application or npm packages are required.

## Rebuild

Run `./build.sh`. Set `WASM_CC` and `WASM_LD` to your LLVM clang and wasm-ld executables if they differ from the defaults. Requires a clang with wasm32 support and lld. The tiny freestanding runtime supplies only memset and strcmp; no imported JavaScript rules or WASI runtime are used.

`engine/vendor` snapshots the C library from the fieldofchaos submodule so hosting can build without recursively fetching it. Update all three files together when syncing rules. The original rules are unchanged; `engine/game.c` implements the skirmish orchestration.

## Scope and adaptations

One cell = two tabletop inches. Each unit gets one orthogonal path-based move and one action per patrol turn; range uses Chebyshev distance, sight uses a grid ray. Every unit has Firearm Basic/Advanced, Close Combat and First Aid, default wound pools, a rifle or carbine, 10 loaded rounds and 3 spare clips. Ranged attacks use the Gold library's single attack resolution, including its two-round expenditure for advanced rifle/carbine use. No historical claims or campaign simulation are made.

Supported rules: Gold firearm range/skills/cover, ammunition, movement restrictions, seven hit locations, wound effects, healing. Not implemented: grenade, shotgun, melee, called head shots, special foes, character creation or campaign progression. Hotseat is shared-device multiplayer; remote network multiplayer is not implemented. Saves persist units and turn metadata; future random rolls are reseeded on page load rather than replaying an exact RNG stream.

## Checks

`node autopilot-tests.mjs` verifies both-side play, stopping, rapid toggles, reset cancellation and victory shutdown using the real WASM engine with a controlled timer queue.

`node tests.mjs` exercises the compiled WASM module, terrain/path movement, turn restrictions, range/sight, ammunition, combat and victory. The upstream Gold C suite runs with `make -C ../fieldofchaos/src test`.
