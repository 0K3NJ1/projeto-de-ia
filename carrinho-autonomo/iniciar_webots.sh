#!/usr/bin/env bash
set -eu

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
webots_home="${WEBOTS_HOME:-/home/arthur/.local/opt/webots-R2025a}"
if [ ! -x "$webots_home/webots" ]; then
  printf 'Webots R2025a não encontrado em %s\n' "$webots_home" >&2
  exit 1
fi
if [ ! -x "$project_root/.venv/bin/python" ]; then
  printf 'Ambiente Python do projeto não encontrado em %s/.venv\n' "$project_root" >&2
  exit 1
fi

export WEBOTS_HOME="$webots_home"
export PATH="$project_root/.venv/bin:$PATH"
export MPLCONFIGDIR="$project_root/.cache/matplotlib"
mkdir -p "$MPLCONFIGDIR"
exec "$webots_home/webots" "$@" "$project_root/worlds/etapa3_buscas.wbt"
