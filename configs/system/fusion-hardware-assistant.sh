#!/usr/bin/env bash
# ==============================================================================
# FusionOS Hardware & Driver Assistant
# Proposito: Deteccao automatica de GPU NVIDIA, Wi-Fi e aceleração grafica
# ==============================================================================

set -euo pipefail

# Se chamado graficamente, abre a interface GUI
if [[ -n "${DISPLAY:-}" || -n "${WAYLAND_DISPLAY:-}" ]]; then
    GUI_APP="/usr/local/bin/fusion-hardware-gui.py"
    if [[ ! -f "$GUI_APP" ]]; then
        GUI_APP="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/fusion-hardware-gui.py"
    fi
    if [[ -f "$GUI_APP" ]] && command -v python3 >/dev/null 2>&1; then
        exec python3 "$GUI_APP"
    fi
fi

echo "=== FusionOS Hardware & Driver Check ==="

# 1. Deteccao de Placa de Video
GPU_INFO=$(lspci 2>/dev/null | grep -Ei "vga|3d|display" || echo "Desconhecida")
echo "GPU Detectada: $GPU_INFO"

if echo "$GPU_INFO" | grep -qi "nvidia"; then
    echo "[AVISO] Placa NVIDIA identificada!"
    if lsmod | grep -qi "nvidia"; then
        echo "[STATUS] Driver proprietario NVIDIA ja esta carregado e ativo."
    else
        echo "[ACAO NECESSARIA] Driver oficial NVIDIA recomendado para maximo desempenho."
        echo "Para instalar via terminal: sudo dnf install -y akmod-nvidia xorg-x11-drv-nvidia-cuda"
    fi
elif echo "$GPU_INFO" | grep -qi "amd\|radeon"; then
    echo "[STATUS] GPU AMD Radeon detectada. Drivers Mesa e RADV Vulkan nativos ativos."
elif echo "$GPU_INFO" | grep -qi "intel"; then
    echo "[STATUS] GPU Intel detectada. Drivers Mesa Iris/ANV Vulkan nativos ativos."
fi

# 2. Deteccao de Wi-Fi
WIFI_INFO=$(lspci 2>/dev/null | grep -Ei "network|wireless" || echo "Nenhum")
echo "Wi-Fi: $WIFI_INFO"
