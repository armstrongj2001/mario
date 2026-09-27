#!/usr/bin/env bash
# POSIX compatibility launcher. Windows runs: py -3 scripts/install.py
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$SCRIPT_DIR/install.py" "$@"
