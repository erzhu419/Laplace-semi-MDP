#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

VENV="${LAPLACE_VENV:-$PWD/.venv-laplace}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
LOCK_PATH="${LAPLACE_SETUP_LOCK:-$VENV.setup.lock}"

check_python() {
  "$1" - <<'PY'
import importlib
import platform
import sys

mods = ["numpy", "scipy", "networkx", "matplotlib"]
versions = {}
for name in mods:
    module = importlib.import_module(name)
    versions[name] = getattr(module, "__version__", "unknown")

print("python", sys.version.replace("\n", " "))
print("platform", platform.platform())
for name, version in versions.items():
    print(name, version)
PY
}

if [ "${LAPLACE_USE_SYSTEM_PYTHON:-0}" = "1" ]; then
  check_python "$PYTHON_BIN"
  exit 0
fi

mkdir -p "$(dirname "$VENV")"
if command -v flock >/dev/null 2>&1; then
  exec 9>"$LOCK_PATH"
  flock 9
fi

if [ ! -d "$VENV" ]; then
  "$PYTHON_BIN" -m venv "$VENV"
fi

source "$VENV/bin/activate"

REQ_HASH="$(sha256sum requirements.txt | awk '{print $1}')"
REQ_MARKER="$VENV/.requirements.sha256"
INSTALLED_HASH=""
if [ -f "$REQ_MARKER" ]; then
  INSTALLED_HASH="$(cat "$REQ_MARKER")"
fi

if [ "${LAPLACE_FORCE_PIP_INSTALL:-0}" = "1" ] || [ "$REQ_HASH" != "$INSTALLED_HASH" ]; then
  python -m pip install --upgrade pip wheel
  python -m pip install -r requirements.txt
  printf '%s\n' "$REQ_HASH" > "$REQ_MARKER"
fi

check_python python
