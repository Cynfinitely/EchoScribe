#!/usr/bin/env sh
# Python lint gate: ruff check on the given files, or the whole repo.
# Hooks and GUI git clients run without the venv activated, so prefer the
# repo venv's ruff, then one on PATH. Config: ruff.toml.
set -eu

ROOT_DIR=$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)

if [ -x "$ROOT_DIR/venv/bin/ruff" ]; then
  RUFF="$ROOT_DIR/venv/bin/ruff"
elif command -v ruff >/dev/null 2>&1; then
  RUFF=ruff
else
  echo "❌ ruff not found. Install it: venv/bin/python3 -m pip install -r requirements-dev.txt"
  exit 1
fi

if [ "$#" -eq 0 ]; then
  set -- "$ROOT_DIR"
fi

exec "$RUFF" check --config "$ROOT_DIR/ruff.toml" "$@"
