#!/usr/bin/env bash
# ==============================================================================
# FusionOS System Cleaner & Disk Optimizer
# Proposito: Limpeza profunda de caches, logs antigos e runtimes orfaos com 1 clique
# ==============================================================================

set -euo pipefail

# Se chamado sem argumentos na sessao grafica, abre a interface GUI
if [[ -n "${DISPLAY:-}" || -n "${WAYLAND_DISPLAY:-}" ]] && [[ "${1:-}" != "--cli" ]]; then
    GUI_APP="/usr/local/bin/fusion-cleaner-gui.py"
    if [[ ! -f "$GUI_APP" ]]; then
        GUI_APP="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/fusion-cleaner-gui.py"
    fi
    if [[ -f "$GUI_APP" ]] && command -v python3 >/dev/null 2>&1; then
        exec python3 "$GUI_APP"
    fi
fi

echo "Iniciando otimizacao e limpeza do FusionOS..."

# Mede espaco livre inicial em MB
INITIAL_FREE=$(df -m / | awk 'NR==2 {print $4}')

# 1. Remove runtimes Flatpak nao utilizados
if command -v flatpak >/dev/null 2>&1; then
    echo "Limpando runtimes Flatpak orfaos..."
    flatpak uninstall --unused -y 2>/dev/null || true
fi

# 2. Limpa cache de pacotes DNF
if command -v dnf >/dev/null 2>&1; then
    echo "Limpando cache de pacotes DNF..."
    sudo dnf clean all 2>/dev/null || true
fi

# 3. Compacta logs antigos do systemd
if command -v journalctl >/dev/null 2>&1; then
    echo "Compactando logs do sistema..."
    sudo journalctl --vacuum-size=100M 2>/dev/null || true
fi

# 4. Limpa caches de miniaturas e temporarios do usuario
echo "Limpando arquivos temporarios e miniaturas..."
rm -rf ~/.cache/thumbnails/* 2>/dev/null || true
rm -rf /var/tmp/lmc-* 2>/dev/null || true

# Mede espaco livre final
FINAL_FREE=$(df -m / | awk 'NR==2 {print $4}')
FREED=$((FINAL_FREE - INITIAL_FREE))
if (( FREED < 0 )); then FREED=0; fi

MSG="Limpeza concluida! ${FREED} MB de espaco recuperados no SSD."
echo "[SUCESSO] $MSG"

if command -v notify-send >/dev/null 2>&1 && [[ -n "${DISPLAY:-}" || -n "${WAYLAND_DISPLAY:-}" ]]; then
    notify-send -a "Fusion Cleaner" -i "drive-harddisk" "FusionOS Otimizado" "$MSG"
fi
