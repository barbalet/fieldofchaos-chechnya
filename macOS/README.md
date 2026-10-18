# Field of Chaos for macOS

Native SwiftUI application for macOS 14 or later. It links the existing C Gold rules and skirmish engine directly; no browser, WASM runtime, network connection or third-party dependencies are required. This is a macOS app, not a Mac Catalyst target.

## Build and run

Install Xcode with its command-line tools selected. From the repository root:

```sh
./macOS/build-app.sh
open "macOS/build/Field of Chaos.app"
```

The script builds the host architecture (Apple Silicon or Intel) and creates a locally ad-hoc-signed `.app`. Distribution to other machines requires appropriate Developer ID signing and notarization. You can also open the root `Package.swift` in Xcode and run the `FieldOfChaos` executable scheme, or use `swift run FieldOfChaos`.

## Play

Click a friendly marker to select a unit. Choose Move, Run, Fire, Focused shot or First aid, then click a cell or target. Movement uses the full C allowance as a true-distance circle (eight inches / four cells for a rifle, ten inches / five cells for a carbine; all healthy agents have a radius greater than three cells, with leg injuries reducing movement). The dashed circle shows the geometric range; blue outlines show unobstructed destinations. Ruins and standing units block the straight route, including diagonal corner crossings. Orange outlines show valid attack targets. Each unit gets one move and one action per patrol turn. Reload and clear-jam actions use the same C engine as the website. End the patrol turn to give the other side control.

Enable **Autopilot · AI plays both patrols** to watch both sides play, one unit every 0.7 seconds. Disable it whenever you want to take over the current patrol. Existing moves, ammunition, wounds and spent actions remain unchanged. Autopilot stops at victory or a draw when every surviving unit has insufficient loaded ammunition to fire and no spare clips. A draw ends the operation; start a new operation to play again. It remains selected when starting a new operation, so the new battle starts automatically. The **Computer opponent** switch controls South when autopilot is off; turn it off for shared-device two-player play.

This shares the browser skirmish's scope and adaptations: 5-vs-5, grid movement, terrain, range, cover, firearm attacks, seven wound locations, first aid, ammunition and incapacitation victory. Grenades, shotguns, melee, called head shots, special foes, campaigns and character creation are not exposed. Native save/resume is not yet implemented. Loadouts and skills match the browser version; roles now have distinct skills.

## Patrols, skills and action choices

Each side has five people: a Rifleman, Scout, Medic, SMG gunner and Sniper. The character panel shows the actual skills assigned to the selected person. All have Firearm Basic; riflemen, SMG gunners and snipers also have Firearm Advanced. Scouts and SMG gunners have Running. Medics have First Aid and Paramedic. Snipers have the scenario-specific Sniper Training skill.

- **Move:** normal circular movement, preserving the action for firing or treatment.
- **Run:** a 50% larger movement radius, or double radius with Running; spends both movement and the action, so it cannot follow an attack or be followed by one. Healthy normal radii are 4 cells for riflemen/snipers, 5 for scouts/medics and 6 for SMG gunners. Leg injuries still reduce movement.
- **Fire:** ordinary Gold ranged attack; normal movement is allowed before or after it.
- **Focused shot:** available only before moving. Adds one aiming die and spends both the action and movement. Sniper Training adds a second aiming die. Focus is a scenario adaptation, not Gold's separate called-head-shot mechanic.
- **First aid / Reload:** spend the action; medics use their Paramedic skill for treatment. A jam must be cleared before shooting again.

Gold target-movement modifiers now apply: a moving target subtracts one attack die, and a running target subtracts two. A target's movement state lasts through the opposing patrol's turn. Sniper rifles cannot shoot under 12 inches and consume one round per attack. Advanced rifles consume two rounds, basic carbines one, and SMGs three. Draw detection accounts for those different costs.

The AI uses running to close long distances, focused shots when stationary, and withdrawal when a sniper is inside minimum range. These choices, focus bonuses, the extra Sniper Training skill and expanded grid movement are explicit skirmish adaptations. The upstream Gold C rules library remains unchanged.

## Architecture and validation

The root Swift package compiles `web/engine/game.c` and `web/engine/vendor/fieldofchaosgold.c` once as a native C target. `web/engine/nativeinclude/CFieldOfChaos.h` exposes the skirmish calls. The shared snapshot pointer is pointer-width-safe for native and WASM builds; native save/resume is still not exposed in the interface. The SwiftUI model runs only on the main actor; one cancellable task drives AI. Only one battle window is provided because the C engine maintains one global game state.

Run `swift test` for native movement, turn ownership, AI control of both patrols, and timer cancellation/reset tests. `node web/tests.mjs` and `node web/autopilot-tests.mjs` verify the existing WASM artifact. The native UI's Field manual explains play and the rules adaptations.
