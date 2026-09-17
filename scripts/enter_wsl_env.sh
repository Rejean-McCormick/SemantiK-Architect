#!/usr/bin/env bash
set +e
set -o pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
cd "$REPO_DIR" || exit 1

echo "=================================================="
echo "SemantiK Architect runtime shell"
echo "PWD=$(pwd)"
echo "WSL=$(uname -a)"
echo "=================================================="

if [[ ! -f "manage.py" ]]; then
  echo "ERROR: manage.py not found in repo root: $(pwd)"
  exec bash -li
fi

export PIP_DISABLE_PIP_VERSION_CHECK=1
export PYTHONDONTWRITEBYTECODE=1

VENV=""
if [[ -f ".venv/bin/activate" ]]; then
  VENV=".venv"
elif [[ -f "venv/bin/activate" ]]; then
  VENV="venv"
fi

if [[ -z "$VENV" ]]; then
  echo ""
  echo "[bootstrap] No virtual environment found."
  if command -v uv >/dev/null 2>&1; then
    echo "[bootstrap] Creating .venv with uv"
    uv venv .venv || { echo "ERROR: uv venv failed."; exec bash -li; }
    VENV=".venv"
  elif command -v python3 >/dev/null 2>&1; then
    echo "[bootstrap] Creating .venv with python3"
    python3 -m venv .venv || { echo "ERROR: python3 -m venv failed."; exec bash -li; }
    VENV=".venv"
  else
    echo "ERROR: neither uv nor python3 is available in WSL."
    exec bash -li
  fi
fi

# shellcheck disable=SC1090
source "${VENV}/bin/activate"

echo ""
echo "VENV_OK=${VIRTUAL_ENV}"
echo "PY=$(command -v python)"
python -V 2>/dev/null || true

echo ""
echo "[check] runtime packages"
python -c 'import importlib.util as u; mods=("pgf","fastapi","uvicorn"); missing=[m for m in mods if u.find_spec(m) is None]; print("CHECK_OK" if not missing else "MISSING=" + ",".join(missing))'

echo ""
echo "[check] PGF deployment"
python manage.py doctor

echo ""
echo "Useful commands:"
echo "  python manage.py doctor"
echo "  python manage.py serve --reload"
echo ""
echo "Grammar authoring/compilation is intentionally not available here."
echo "Supply runtime/semantik_architect.pgf or set PGF_PATH."
echo ""

exec bash -li
