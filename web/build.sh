#!/bin/sh
set -eu
cd "$(dirname "$0")"
CC=${WASM_CC:-/usr/local/Cellar/llvm/18.1.5/bin/clang}
LD=${WASM_LD:-/usr/local/Cellar/llvm/18.1.5/bin/wasm-ld}
"$CC" --target=wasm32 -std=c11 -O2 -nostdlib -fno-builtin -Iengine/include -Iengine/vendor -c engine/vendor/fieldofchaosgold.c -o /tmp/foc-rules.o
"$CC" --target=wasm32 -std=c11 -O2 -nostdlib -fno-builtin -Iengine/include -Iengine/vendor -c engine/runtime.c -o /tmp/foc-runtime.o
"$CC" --target=wasm32 -std=c11 -O2 -nostdlib -fno-builtin -Iengine/include -Iengine/vendor -c engine/game.c -o /tmp/foc-game.o
"$LD" --no-entry --export-all /tmp/foc-rules.o /tmp/foc-runtime.o /tmp/foc-game.o -o dist/game.wasm
