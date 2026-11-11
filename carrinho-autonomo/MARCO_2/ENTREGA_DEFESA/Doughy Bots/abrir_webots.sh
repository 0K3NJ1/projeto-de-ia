#!/usr/bin/env bash
# Abre somente o mundo interativo deste pacote, usando o Webots R2025a.
set -eu

pacote="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
projeto="$(cd "$pacote/../../.." && pwd)"
webots_home="${WEBOTS_HOME:-$HOME/.local/opt/webots-R2025a}"

if [ ! -x "$webots_home/webots" ]; then
  printf 'Webots R2025a não encontrado em %s\n' "$webots_home" >&2
  exit 1
fi

# O runtime.ini usa python3. No computador do grupo, priorizamos o ambiente
# virtual já configurado; em outra máquina, vale o Python do PATH.
if [ -x "$projeto/.venv/bin/python3" ]; then
  export PATH="$projeto/.venv/bin:$PATH"
fi
export WEBOTS_HOME="$webots_home"
export MPLCONFIGDIR="$pacote/.cache/matplotlib"
mkdir -p "$MPLCONFIGDIR"

# Os pesos do Qwen não entram no Git. Se já existirem na raiz local, um link
# permite reaproveitá-los sem copiar quase 3 GB para a pasta de apresentação.
if [ -d "$projeto/.cache/huggingface" ] && [ ! -e "$pacote/.cache/huggingface" ]; then
  ln -s "$projeto/.cache/huggingface" "$pacote/.cache/huggingface"
fi

exec "$webots_home/webots" "$@" "$pacote/worlds/etapa3_buscas.wbt"
