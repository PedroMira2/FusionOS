#!/usr/bin/env bash
# ==============================================================================
# FusionOS Power & Performance Profile Manager
# Proposito: Alternar instantaneamente entre perfis de consumo e jogos
# ==============================================================================

set -euo pipefail

TARGET_MODE="${1:-}"

if [[ -z "$TARGET_MODE" ]]; then
    # Se chamado sem argumentos no ambiente grafico, abre a interface GUI
    GUI_APP="/usr/local/bin/fusion-power-gui.py"
    if [[ ! -f "$GUI_APP" ]]; then
        GUI_APP="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/fusion-power-gui.py"
    fi

    if [[ -n "${DISPLAY:-}" || -n "${WAYLAND_DISPLAY:-}" ]] && [[ -f "$GUI_APP" ]] && command -v python3 >/dev/null 2>&1; then
        exec python3 "$GUI_APP"
    else
        echo "Uso: $0 [powersave|balanced|performance]"
        exit 1
    fi
fi

case "$TARGET_MODE" in
    powersave|eco|quiet)
        echo "Ativando Modo Silencioso / Economico..."
        if command -v powerprofilesctl >/dev/null 2>&1; then
            powerprofilesctl set power-saver 2>/dev/null || true
        fi
        for gov in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do
            [[ -f "$gov" ]] && echo "powersave" | sudo tee "$gov" >/dev/null 2>&1 || true
        done
        TITLE="Modo Silencioso Ativado"
        DESC="Frequencias de CPU reduzidas para maxima autonomia e silencio."
        ICON="battery-charging"
        ;;

    balanced|default|auto)
        echo "Ativando Modo Equilibrado..."
        if command -v powerprofilesctl >/dev/null 2>&1; then
            powerprofilesctl set balanced 2>/dev/null || true
        fi
        for gov in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do
            [[ -f "$gov" ]] && echo "schedutil" | sudo tee "$gov" >/dev/null 2>&1 || true
        done
        TITLE="Modo Equilibrado Ativado"
        DESC="Desempenho fluido e dinamico de acordo com a demanda."
        ICON="preferences-system-power"
        ;;

    performance|game|ultra)
        echo "Ativando Modo Performance / Gamer..."
        if command -v powerprofilesctl >/dev/null 2>&1; then
            powerprofilesctl set performance 2>/dev/null || true
        fi
        for gov in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do
            [[ -f "$gov" ]] && echo "performance" | sudo tee "$gov" >/dev/null 2>&1 || true
        done
        if command -v gamemoded >/dev/null 2>&1; then
            gamemoded -r 2>/dev/null || true
        fi
        TITLE="Modo Performance & Jogos Ativado"
        DESC="Clocks maximos desbloqueados e GameMode pronto."
        ICON="applications-games"
        ;;

    *)
        echo "Opcao invalida: $TARGET_MODE (use: powersave, balanced, performance)"
        exit 1
        ;;
esac

# Envia notificacao visual na area de trabalho
if command -v notify-send >/dev/null 2>&1 && [[ -n "${DISPLAY:-}" || -n "${WAYLAND_DISPLAY:-}" ]]; then
    notify-send -a "FusionOS Performance" -i "$ICON" "$TITLE" "$DESC"
fi

echo "[SUCESSO] $TITLE: $DESC"
