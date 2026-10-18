#!/bin/sh
set -eu
cd "$(dirname "$0")"
CC=${WASM_CC:-/usr/local/Cellar/llvm/18.1.5/bin/clang}
LD=${WASM_LD:-/usr/local/Cellar/llvm/18.1.5/bin/wasm-ld}
"$CC" --target=wasm32 -std=c11 -O2 -nostdlib -fno-builtin -Iengine/include -Iengine/vendor -c engine/vendor/fieldofchaosgold.c -o /tmp/foc-rules.o
"$CC" --target=wasm32 -std=c11 -O2 -nostdlib -fno-builtin -Iengine/include -Iengine/vendor -c engine/runtime.c -o /tmp/foc-runtime.o
"$CC" --target=wasm32 -std=c11 -O2 -nostdlib -fno-builtin -Iengine/include -Iengine/vendor -c engine/game.c -o /tmp/foc-game.o
"$LD" --no-entry --export-all /tmp/foc-rules.o /tmp/foc-runtime.o /tmp/foc-game.o -o dist/game.wasm

# Version dependent assets so browsers cannot reuse an older patrol roster.
# Keep the website-root entry point synchronized with the deployable HTML.
python3 - <<'PY'
from hashlib import sha256
from pathlib import Path
import re

wasm_version = sha256(Path("dist/game.wasm").read_bytes()).hexdigest()[:16]
script_path = Path("dist/game.js")
script = re.sub(r"fetch\('game\.wasm(?:\?v=[a-f0-9]+)?'\)",
                f"fetch('game.wasm?v={wasm_version}')", script_path.read_text())
script_path.write_text(script)
script_version = sha256(script.encode()).hexdigest()[:16]
html_path = Path("dist/index.html")
html = re.sub(r'src="game\.js(?:\?v=[a-f0-9]+)?"',
              f'src="game.js?v={script_version}"', html_path.read_text())
html_path.write_text(html)
Path("index.html").write_text(html.replace("<head>", '<head><base href="./dist/">', 1))
PY
