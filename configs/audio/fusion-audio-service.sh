#!/usr/bin/env bash
# ==============================================================================
# FusionOS Audio Engine Service (Dolby Atmos & Hi-Res DSP Initializer)
# Proposito: Inicia o processamento DSP em segundo plano de forma silenciosa
# ==============================================================================

set -euo pipefail

PRESETS_DIR="$HOME/.config/easyeffects/output"
mkdir -p "$PRESETS_DIR"

# Copia os presets de fábrica do FusionOS para o usuário
SYSTEM_PRESETS="/usr/share/fusionos/audio/presets"
if [[ -d "$SYSTEM_PRESETS" ]]; then
    cp -u "$SYSTEM_PRESETS"/*.json "$PRESETS_DIR/" 2>/dev/null || true
fi

# Se easyeffects estiver instalado, inicia como serviço em segundo plano
if command -v easyeffects >/dev/null 2>&1; then
    # Inicia como servico headless se ainda nao estiver rodando
    if ! pgrep -x "easyeffects" >/dev/null 2>&1; then
        easyeffects --gapplication-service &
        sleep 1
        # Carrega o perfil Dolby 3D Spatial por padrão
        easyeffects -l "FusionOS-Dolby-Spatial" 2>/dev/null || true
    fi
fi
