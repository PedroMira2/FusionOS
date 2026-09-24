#!/usr/bin/env bash
# ==============================================================================
# FusionOS Focus Mode (Modo Foco / Não Perturbe)
# Silenciamento inteligente de notificações e alertas sonoros durante trabalho/jogos
# ==============================================================================

set -euo pipefail

STATE_FILE="/tmp/fusion-focus-mode.active"
ACTION="${1:-toggle}"

is_active() {
    [[ -f "$STATE_FILE" ]]
}

enable_focus() {
    touch "$STATE_FILE"
    
    # 1. Inibir notificações no KDE Plasma via D-Bus
    if command -v qdbus6 &>/dev/null; then
        qdbus6 org.freedesktop.Notifications /org/freedesktop/Notifications SetInhibited true 2>/dev/null || true
    elif command -v gdbus &>/dev/null; then
        gdbus call --session --dest org.freedesktop.Notifications \
            --object-path /org/freedesktop/Notifications \
            --method org.freedesktop.Notifications.Inhibit \
            "FusionOS" "Modo Foco Ativado" "{}" 2>/dev/null || true
    fi

    # 2. Notificação breve de confirmação
    if command -v notify-send &>/dev/null; then
        notify-send -a "FusionOS" -i preferences-desktop-notification-bell \
            "Modo Foco Ativado" "Notificações e sons secundários silenciados." -t 2500 2>/dev/null || true
    fi
    echo "[FusionOS] Modo Foco ATIVADO."
}

disable_focus() {
    rm -f "$STATE_FILE"

    # 1. Desinibir notificações
    if command -v qdbus6 &>/dev/null; then
        qdbus6 org.freedesktop.Notifications /org/freedesktop/Notifications SetInhibited false 2>/dev/null || true
    fi

    if command -v notify-send &>/dev/null; then
        notify-send -a "FusionOS" -i preferences-desktop-notification-bell \
            "Modo Foco Desativado" "Notificações restauradas normalmente." -t 2500 2>/dev/null || true
    fi
    echo "[FusionOS] Modo Foco DESATIVADO."
}

case "$ACTION" in
    on|enable)
        enable_focus
        ;;
    off|disable)
        disable_focus
        ;;
    toggle)
        if is_active; then
            disable_focus
        else
            enable_focus
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
