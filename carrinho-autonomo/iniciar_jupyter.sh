#!/usr/bin/env bash
set -eu

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ ! -x "$project_root/.venv/bin/jupyter" ]; then
  printf 'Jupyter não encontrado no ambiente Python em %s/.venv\n' "$project_root" >&2
  exit 1
fi

export MPLCONFIGDIR="$project_root/.cache/matplotlib"
mkdir -p "$MPLCONFIGDIR"
cd "$project_root"
exec "$project_root/.venv/bin/jupyter" lab "$@"
