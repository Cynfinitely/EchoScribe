#!/usr/bin/env sh
# Python lint gate: ruff check on the given files, or all tracked Python files.
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

# No args: every tracked Python file, so local WIP that isn't committed can't
# fail a push (CI only sees tracked files either way).
if [ "$#" -eq 0 ]; then
  cd "$ROOT_DIR"
  # shellcheck disable=SC2046
  set -- $(git ls-files '*.py')
  [ "$#" -eq 0 ] && exit 0
fi

exec "$RUFF" check --config "$ROOT_DIR/ruff.toml" "$@"
