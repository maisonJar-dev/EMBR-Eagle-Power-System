#!/usr/bin/env sh

set -eu

if command -v pio >/dev/null 2>&1; then
    PIO="$(command -v pio)"
elif [ -x "$HOME/.platformio/penv/bin/pio" ]; then
    # The VS Code PlatformIO extension installs Core here on Linux and macOS.
    PIO="$HOME/.platformio/penv/bin/pio"
else
    printf '%s\n' \
        "PlatformIO Core was not found." \
        "Install the VS Code PlatformIO IDE extension, restart VS Code, and rerun:" \
        "  ./scripts/bootstrap.sh"
    exit 1
fi

printf 'Using %s\n' "$PIO"
"$PIO" project init --ide vscode --environment uno
"$PIO" run --target compiledb
"$PIO" run

printf '%s\n' \
    "" \
    "Setup complete." \
    "If VS Code still shows stale diagnostics, run Developer: Reload Window."
