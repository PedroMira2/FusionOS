#!/usr/bin/env bash
# ==============================================================================
# FusionOS Intelligent Battery Switcher
# Ajusta dinamicamente clocks da CPU, perfis de energia e indexação ao plugar/desplugar da tomada
# ==============================================================================

set -euo pipefail

EVENT="${1:-auto}"

detect_power() {
    # Procura adaptadores AC no sysfs
    for ac in /sys/class/power_supply/AC* /sys/class/power_supply/ADP*; do
        if [[ -f "${ac}/online" ]]; then
            if [[ "$(< "${ac}/online")" == "1" ]]; then
                echo "ac"
                return
            fi
        fi
    done
    echo "battery"
}

if [[ "$EVENT" == "auto" ]]; then
    EVENT="$(detect_power)"
fi

if [[ "$EVENT" == "battery" ]]; then
    echo "[FusionOS] Bateria detectada. Ativando perfil de economia inteligente..."
    
    # 1. Chamar motor de energia do FusionOS
    if [[ -x /usr/bin/fusion-power-mode ]]; then
        /usr/bin/fusion-power-mode powersave || true
    fi

    # 2. Suspender indexadores pesados em segundo plano para poupar ciclos de CPU
    if command -v balooctl6 &>/dev/null; then
        balooctl6 suspend &>/dev/null || true
    fi

    # 3. Notificar usuário suavemente
    if command -v notify-send &>/dev/null; then
        notify-send -a "FusionOS Energia" -i battery-low \
            "Modo Bateria Ativado" "Foco na autonomia: perfil econômico ativado." -t 2000 || true
    fi

elif [[ "$EVENT" == "ac" ]]; then
    echo "[FusionOS] Fonte de alimentação AC conectada. Restaurando potência máxima..."

    # 1. Chamar motor de energia
    if [[ -x /usr/bin/fusion-power-mode ]]; then
        /usr/bin/fusion-power-mode balanced || true
    fi

    # 2. Retomar indexadores
    if command -v balooctl6 &>/dev/null; then
        balooctl6 resume &>/dev/null || true
    fi

    # 3. Notificar usuário suavemente
    if command -v notify-send &>/dev/null; then
        notify-send -a "FusionOS Energia" -i battery-charging \
            "Conectado à Energia" "Desempenho total e aceleração ativados." -t 2000 || true
    fi
fi
