# Field of Chaos — Chechnya

The `fieldofchaos/` submodule contains the Field of Chaos Gold C rules library.

The playable WebAssembly browser skirmish is in [`web/`](web/README.md). It supports an AI opponent, shared-device two-player play, terrain, ranged combat, wounds, healing and save/resume.

To play locally:

```sh
python3 -m http.server 8080 --directory web/dist
```

Open http://localhost:8080. See the web README and in-game field manual for rules adaptations and current scope.

## Native macOS app

A SwiftUI macOS application using the same C engine is available in [`macOS/`](macOS/README.md), including selectable autopilot for both patrols. Build with `./macOS/build-app.sh`, then open `macOS/build/Field of Chaos.app`. Requires macOS 14+ and Xcode.
