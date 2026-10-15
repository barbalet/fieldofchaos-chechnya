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

Click a friendly marker to select a unit. Choose Move, Fire or First aid, then click a cell or target. Blue outlines show available moves; orange outlines show valid targets. Each unit gets one move and one action per patrol turn. Reload and clear-jam actions use the same C engine as the website. End the patrol turn to give the other side control.

Enable **Autopilot · AI plays both patrols** to watch both sides play, one unit every 0.7 seconds. Disable it whenever you want to take over the current patrol. Existing moves, ammunition, wounds and spent actions remain unchanged. Autopilot stops at victory or a draw when every surviving unit has insufficient loaded ammunition to fire and no spare clips. A draw ends the operation; start a new operation to play again. It remains selected when starting a new operation, so the new battle starts automatically. The **Computer opponent** switch controls South when autopilot is off; turn it off for shared-device two-player play.

This shares the browser skirmish's scope and adaptations: 3-vs-3, grid movement, terrain, range, cover, firearm attacks, seven wound locations, first aid, ammunition and incapacitation victory. Grenades, shotguns, melee, called head shots, special foes, campaigns and character creation are not exposed. Native save/resume is not yet implemented. All units have the same skill loadout as the web version. UI labels such as Scout and Medic are identifiers, not different skill classes.

## Architecture and validation

The root Swift package compiles `web/engine/game.c` and `web/engine/vendor/fieldofchaosgold.c` once as a native C target. `web/engine/nativeinclude/CFieldOfChaos.h` exposes the skirmish calls. It deliberately omits WASM's 32-bit save-pointer API. The SwiftUI model runs only on the main actor; one cancellable task drives AI. Only one battle window is provided because the C engine maintains one global game state.

Run `swift test` for native movement, turn ownership, AI control of both patrols, and timer cancellation/reset tests. `node web/tests.mjs` and `node web/autopilot-tests.mjs` verify the existing WASM artifact. The native UI's Field manual explains play and the rules adaptations.
