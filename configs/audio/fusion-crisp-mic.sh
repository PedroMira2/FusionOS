#!/usr/bin/env bash
# ==============================================================================
# FusionOS Crisp Mic CLI Controller
# Ativação/Desativação instantânea do cancelamento de ruído por IA no microfone
# ==============================================================================

set -euo pipefail

CONF_SOURCE="/usr/share/fusionos/audio/pipewire-crisp-mic.conf"
if [[ ! -f "$CONF_SOURCE" ]]; then
    CONF_SOURCE="$(dirname "$(realpath "$0")")/pipewire-crisp-mic.conf"
fi

USER_PIPEWIRE_DIR="${HOME}/.config/pipewire/pipewire.conf.d"
USER_TARGET="${USER_PIPEWIRE_DIR}/99-fusion-crisp-mic.conf"
ACTION="${1:-status}"

mkdir -p "$USER_PIPEWIRE_DIR" 2>/dev/null || true

is_active() {
    [[ -f "$USER_TARGET" ]]
}

enable_crisp_mic() {
    if [[ -f "$CONF_SOURCE" ]]; then
        cp "$CONF_SOURCE" "$USER_TARGET"
        systemctl --user restart pipewire wireplumber 2>/dev/null || true
        echo "[Fusion Crisp Mic] Cancelamento de ruído por IA ATIVADO."
        if command -v notify-send &>/dev/null; then
            notify-send -a "Fusion Áudio" -i audio-input-microphone \
                "Fusion Crisp Mic Ativado" "Voz isolada em tempo real por rede neural RNNoise." -t 2500 || true
        fi
    else
        echo "[Fusion Crisp Mic] Erro: Arquivo de configuração não encontrado: $CONF_SOURCE"
        exit 1
    fi
}

disable_crisp_mic() {
    rm -f "$USER_TARGET"
    systemctl --user restart pipewire wireplumber 2>/dev/null || true
    echo "[Fusion Crisp Mic] Cancelamento de ruído DESATIVADO."
    if command -v notify-send &>/dev/null; then
        notify-send -a "Fusion Áudio" -i audio-input-microphone \
            "Fusion Crisp Mic Desativado" "Microfone operando no modo padrão." -t 2500 || true
    fi
}

case "$ACTION" in
    on|enable)
        enable_crisp_mic
        ;;
    off|disable)
        disable_crisp_mic
        ;;
    toggle)
        if is_active; then
            disable_crisp_mic
        else
            enable_crisp_mic
        fi
        ;;
    status)
        if is_active; then
            echo "active"
        else
            echo "inactive"
        fi
        ;;
    *)
        echo "Uso: $0 {on|off|toggle|status}"
        exit 1
        ;;
esac
