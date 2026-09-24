#!/usr/bin/env bash
# ==============================================================================
# FusionOS Waydroid Subsystem Engine
# Subsistema Android com aceleração gráfica 3D e integração com desktop Wayland
# ==============================================================================

set -euo pipefail

ACTION="${1:-status}"

is_running() {
    if command -v waydroid &>/dev/null; then
        waydroid status 2>/dev/null | grep -q "RUNNING"
    else
        false
    fi
}

start_android() {
    echo "[Fusion Android Engine] Inicializando subsistema Android..."
    if command -v waydroid &>/dev/null; then
        systemctl start waydroid-container 2>/dev/null || true
        waydroid session start &>/dev/null &
        waydroid prop set persist.waydroid.multi_windows true 2>/dev/null || true
    fi
    echo "[Fusion Android Engine] Android pronto para uso."
    if command -v notify-send &>/dev/null; then
        notify-send -a "FusionOS" -i smartphone \
            "Android Subsystem Pronto" "Aplicativos Android podem ser executados como janelas nativas." || true
    fi
}

stop_android() {
    echo "[Fusion Android Engine] Encerrando subsistema Android..."
    if command -v waydroid &>/dev/null; then
        waydroid session stop 2>/dev/null || true
        systemctl stop waydroid-container 2>/dev/null || true
    fi
    echo "[Fusion Android Engine] Android encerrado."
}

case "$ACTION" in
    start)
        start_android
        ;;
    stop)
        stop_android
        ;;
    status)
        if is_running; then
            echo "running"
        else
            echo "stopped"
        fi
        ;;
    *)
        echo "Uso: $0 {start|stop|status}"
        exit 1
        ;;
esac
