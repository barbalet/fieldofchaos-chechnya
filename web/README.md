# Field of Chaos browser skirmish

A playable static browser game using the existing Gold C rules compiled to genuine WebAssembly. Includes a selectable Autopilot that plays both sides with paced actions and can be disabled mid-turn to take control, a 5-vs-5 battle, computer opponent, shared-device two-player mode, movement/pathfinding, blocking terrain, cover, ranged fire, wounds/incapacitation, ammunition, reloads, first aid, victory and browser-local saves.

## Play locally

From the repository root: `python3 -m http.server 8080`, then open http://localhost:8080. The root `index.html` opens `web/index.html`, which loads the game assets from `web/dist/`. You can also serve just the website with `python3 -m http.server 8080 --directory web`, or run `python3 -m http.server 8080` from inside `web/`. A precompiled `dist/game.wasm` is included. No server-side application or npm packages are required.

Use an HTTP server: opening HTML directly with `file://` cannot reliably load the WASM module.

## Rebuild

Run `./build.sh`. Set `WASM_CC` and `WASM_LD` to your LLVM clang and wasm-ld executables if they differ from the defaults. Requires a clang with wasm32 support and lld. The tiny freestanding runtime supplies only memset and strcmp; no imported JavaScript rules or WASI runtime are used.

`engine/vendor` snapshots the C library from the fieldofchaos submodule so hosting can build without recursively fetching it. Update all three files together when syncing rules. The original rules are unchanged; `engine/game.c` implements the skirmish orchestration.

## Mac version parity

The browser uses the same C circular movement rules as the native Mac app and displays the same dashed range circle. AI uses Euclidean target ordering and weighted eight-way terrain distances, and acts once per unit every 0.7 seconds. Autopilot controls both patrols; turning it off returns manual control without resetting spent actions. Both versions stop on victory or an ammunition-exhaustion draw. A draw ends the operation and cannot restart until a new battle begins. Browser save/resume remains available, including completed battles.

## Scope and adaptations

One cell = two tabletop inches. Each unit gets one circular-range, straight-line move and one action per patrol turn; movement uses Euclidean distance without rounding away partial cells (rifle: 4-cell radius, carbine: 5-cell radius; all healthy agents have a radius greater than 3 cells, with leg injuries reducing movement), with ruins and standing units blocking the route and diagonal corner crossings; weapon range uses Chebyshev distance, sight uses a grid ray. Each character starts with default wound pools, 10 loaded rounds and 3 spare clips. Skills and weapon-specific costs are listed below. No historical claims or campaign simulation are made.

Supported rules: Gold firearm range/skills/cover, ammunition, movement restrictions, seven hit locations, wound effects, healing. Not implemented: grenade, shotgun, melee, called head shots, special foes, character creation or campaign progression. Hotseat is shared-device multiplayer; remote network multiplayer is not implemented. Saves persist units and turn metadata; future random rolls are reseeded on page load rather than replaying an exact RNG stream.

## Patrols, skills and action choices

Each side has five people: a Rifleman, Scout, Medic, SMG gunner and Sniper. The character panel shows the actual skills assigned to the selected person. All have Firearm Basic; riflemen, SMG gunners and snipers also have Firearm Advanced. Scouts and SMG gunners have Running. Medics have First Aid and Paramedic. Snipers have the scenario-specific Sniper Training skill.

- **Move:** normal circular movement, preserving the action for firing or treatment.
- **Run:** a 50% larger movement radius, or double radius with Running; spends both movement and the action, so it cannot follow an attack or be followed by one. Healthy normal radii are 4 cells for riflemen/snipers, 5 for scouts/medics and 6 for SMG gunners. Leg injuries still reduce movement.
- **Fire:** ordinary Gold ranged attack; normal movement is allowed before or after it.
- **Focused shot:** available only before moving. Adds one aiming die and spends both the action and movement. Sniper Training adds a second aiming die. Focus is a scenario adaptation, not Gold's separate called-head-shot mechanic.
- **First aid / Reload:** spend the action; medics use their Paramedic skill for treatment. A jam must be cleared before shooting again.

Gold target-movement modifiers now apply: a moving target subtracts one attack die, and a running target subtracts two. A target's movement state lasts through the opposing patrol's turn. Sniper rifles cannot shoot under 12 inches and consume one round per attack. Advanced rifles consume two rounds, basic carbines one, and SMGs three. Draw detection accounts for those different costs.

The AI uses running to close long distances, focused shots when stationary, and withdrawal when a sniper is inside minimum range. These choices, focus bonuses, the extra Sniper Training skill and expanded grid movement are explicit skirmish adaptations. The upstream Gold C rules library remains unchanged.

Browser saves now use format v2 for the ten-person roster and action states. Old three-person saves are rejected with an incompatible-save message.

## Checks

`node autopilot-tests.mjs` verifies both-side play, stopping, rapid toggles, reset cancellation, victory/draw shutdown, circular overlays, and terminal save/resume using the real WASM engine with a controlled timer queue.

`node tests.mjs` exercises the compiled WASM module, terrain/path movement, turn restrictions, range/sight, ammunition, combat and victory. The upstream Gold C suite runs with `make -C ../fieldofchaos/src test`.
