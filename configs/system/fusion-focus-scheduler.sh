#!/usr/bin/env bash
# ==============================================================================
# FusionOS Window Focus CPU Priority Scheduler
# Prioriza dinamicamente a CPU e o subsistema de I/O da janela em foco ativo
# ==============================================================================

set -euo pipefail

PREV_PID=""

cleanup() {
    if [[ -n "$PREV_PID" ]]; then
        renice -n 0 -p "$PREV_PID" &>/dev/null || true
    fi
    exit 0
}

trap cleanup SIGINT SIGTERM

get_focused_pid() {
    # 1. Tentar via kdotool se disponível
    if command -v kdotool &>/dev/null; then
        local win
        win="$(kdotool getactivewindow 2>/dev/null || true)"
        if [[ -n "$win" ]]; then
            kdotool getwindowpid "$win" 2>/dev/null || true
            return
        fi
    fi

    # 2. Tentar via qdbus KWin script
    if command -v qdbus6 &>/dev/null; then
        # Leitura rápida de processo ativo via KWin
        local active_name
        active_name="$(qdbus6 org.kde.KWin /KWin org.kde.KWin.activeWindow 2>/dev/null || true)"
        if [[ -n "$active_name" && "$active_name" != "0" ]]; then
            pgrep -f "$active_name" 2>/dev/null | head -n1 || true
            return
        fi
    fi

    # 3. Fallback xdotool caso em sessão Xwayland
    if command -v xdotool &>/dev/null; then
        local xwin
        xwin="$(xdotool getactivewindow 2>/dev/null || true)"
        if [[ -n "$xwin" ]]; then
            xdotool getwindowpid "$xwin" 2>/dev/null || true
            return
        fi
    fi
}

echo "[FusionOS Focus Scheduler] Monitor de prioridade de janelas iniciado."

while true; do
    ACTIVE_PID="$(get_focused_pid || true)"
    
    if [[ -n "$ACTIVE_PID" && "$ACTIVE_PID" =~ ^[0-9]+$ && "$ACTIVE_PID" -gt 1 ]]; then
        if [[ "$ACTIVE_PID" != "$PREV_PID" ]]; then
            # Restaura processo anterior para nice normal (0)
            if [[ -n "$PREV_PID" ]]; then
                renice -n 0 -p "$PREV_PID" &>/dev/null || true
            fi
            
            # Prioriza processo focado: nice -5 e alta prioridade de I/O (classe 2, nível 0)
            renice -n -5 -p "$ACTIVE_PID" &>/dev/null || true
            if command -v ionice &>/dev/null; then
                ionice -c 2 -n 0 -p "$ACTIVE_PID" &>/dev/null || true
            fi
            
            PREV_PID="$ACTIVE_PID"
        fi
    fi
    
    sleep 2
done
