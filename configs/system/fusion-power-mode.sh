#!/usr/bin/env bash
# ==============================================================================
# FusionOS Extreme Power & Performance Profile Engine
# Perfis dedicados: Economia, Multitarefas, Desempenho Máximo e Jogos Extremo
# ==============================================================================

set -euo pipefail

TARGET_MODE="${1:-}"

if [[ -z "$TARGET_MODE" ]]; then
    GUI_APP="/usr/local/bin/fusion-power-gui.py"
    if [[ ! -f "$GUI_APP" ]]; then
        GUI_APP="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/fusion-power-gui.py"
    fi

    if [[ -n "${DISPLAY:-}" || -n "${WAYLAND_DISPLAY:-}" ]] && [[ -f "$GUI_APP" ]] && command -v python3 >/dev/null 2>&1; then
        exec python3 "$GUI_APP"
    else
        echo "Uso: $0 [powersave|multitask|performance|gaming]"
        exit 1
    fi
fi

set_cpu_governor() {
    local gov="$1"
    for g in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do
        [[ -f "$g" ]] && echo "$gov" | sudo tee "$g" >/dev/null 2>&1 || true
    done
}

set_energy_pref() {
    local pref="$1"
    for p in /sys/devices/system/cpu/cpu*/cpufreq/energy_performance_preference; do
        [[ -f "$p" ]] && echo "$pref" | sudo tee "$p" >/dev/null 2>&1 || true
    done
}

case "$TARGET_MODE" in
    powersave|eco|quiet|battery)
        echo "[FusionOS] Ativando Modo Economia de Energia..."
        if command -v powerprofilesctl >/dev/null 2>&1; then
            powerprofilesctl set power-saver 2>/dev/null || true
        fi
        set_cpu_governor "powersave"
        set_energy_pref "power"
        
        # Ativar economia PCIe e áudio
        echo "1" | sudo tee /sys/module/snd_hda_intel/parameters/power_save >/dev/null 2>&1 || true
        
        TITLE="Modo Economia de Energia Ativado"
        DESC="Frequências de clock contidas e foco máximo na autonomia da bateria."
        ICON="battery-charging"
        ;;

    multitask|balanced|work|dev)
        echo "[FusionOS] Ativando Modo Multitarefas..."
        if command -v powerprofilesctl >/dev/null 2>&1; then
            powerprofilesctl set balanced 2>/dev/null || true
        fi
        set_cpu_governor "schedutil"
        set_energy_pref "balance_performance"
        
        # Priorizar cache de I/O e multithreading simultâneo
        sudo sysctl -w vm.vfs_cache_pressure=50 >/dev/null 2>&1 || true
        
        TITLE="Modo Multitarefas Ativado"
        DESC="Equilíbrio ideal entre núcleos para compilação, navegação pesada e produtividade."
        ICON="preferences-system-power"
        ;;

    performance|max|turbo)
        echo "[FusionOS] Ativando Modo Desempenho Máximo..."
        if command -v powerprofilesctl >/dev/null 2>&1; then
            powerprofilesctl set performance 2>/dev/null || true
        fi
        set_cpu_governor "performance"
        set_energy_pref "performance"
        
        # Desativar economia de energia em placas de vídeo e barramentos
        if [[ -f /sys/class/drm/card0/device/power_dpm_force_performance_level ]]; then
            echo "high" | sudo tee /sys/class/drm/card0/device/power_dpm_force_performance_level >/dev/null 2>&1 || true
        fi

        TITLE="Modo Desempenho Máximo Ativado"
        DESC="Todos os núcleos de CPU e GPU destravados no clock máximo de pico."
        ICON="applications-utilities"
        ;;

    gaming|game|ultra|fps)
        echo "[FusionOS] Ativando Modo Jogos Extremo (Ultra Low Latency)..."
        if command -v powerprofilesctl >/dev/null 2>&1; then
            powerprofilesctl set performance 2>/dev/null || true
        fi
        set_cpu_governor "performance"
        set_energy_pref "performance"
        
        # Iniciar GameMode daemon
        if command -v gamemoded >/dev/null 2>&1; then
            gamemoded -r 2>/dev/null || true
        fi

        # Elevar prioridade do compositor e GPU
        if [[ -f /sys/class/drm/card0/device/power_dpm_force_performance_level ]]; then
            echo "manual" | sudo tee /sys/class/drm/card0/device/power_dpm_force_performance_level >/dev/null 2>&1 || true
        fi

        TITLE="Modo Jogos Extremo Ativado"
        DESC="GameMode, latência mínima de quadros (VRR) e prioridade total para a GPU."
        ICON="applications-games"
        ;;

    *)
        echo "Opção inválida: $TARGET_MODE (use: powersave, multitask, performance, gaming)"
        exit 1
        ;;
esac

# Envia notificação visual na área de trabalho
if command -v notify-send >/dev/null 2>&1 && [[ -n "${DISPLAY:-}" || -n "${WAYLAND_DISPLAY:-}" ]]; then
    notify-send -a "FusionOS Energia & Desempenho" -i "$ICON" "$TITLE" "$DESC" -t 3000 || true
fi

echo "[SUCESSO] $TITLE: $DESC"
