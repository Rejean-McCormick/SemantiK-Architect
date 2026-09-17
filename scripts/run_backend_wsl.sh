#!/usr/bin/env bash
# Runtime API launcher for WSL. SemantiK Architect consumes an existing PGF;
# this script does not compile grammar sources or start background workers.

set +e
set -o pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
cd "$REPO_DIR" || exit 1

TS="$(date +%Y%m%d_%H%M%S)"
mkdir -p logs
LOGFILE="logs/backend_${TS}.log"
exec > >(tee -a "$LOGFILE") 2>&1

echo "SemantiK Architect runtime API"
echo "PWD=$(pwd)"
echo "Log=${REPO_DIR}/${LOGFILE}"

VENV=""
if [[ -f ".venv/bin/activate" ]]; then
  VENV=".venv"
elif [[ -f "venv/bin/activate" ]]; then
  VENV="venv"
fi

if [[ -n "$VENV" ]]; then
  # shellcheck disable=SC1090
  source "${VENV}/bin/activate"
  echo "VENV_OK=${VIRTUAL_ENV}"
else
  echo "VENV_MISSING: create .venv or venv before starting the API."
fi

export PGF_PATH="${PGF_PATH:-${REPO_DIR}/runtime/semantik_architect.pgf}"

echo ""
echo "Preflight:"
python3 manage.py doctor
STATUS=$?
if [[ $STATUS -ne 0 ]]; then
  echo "Runtime is not ready. Supply a precompiled PGF and the pgf Python package."
  exec bash -li
fi

echo ""
echo "Running: python3 manage.py serve --host 0.0.0.0 --port 8000"
PYTHONUNBUFFERED=1 python3 -u manage.py serve --host 0.0.0.0 --port 8000
STATUS=$?
echo "API exit code: ${STATUS}"

echo ""
echo "Dropping into an interactive shell."
exec bash -li
