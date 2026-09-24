#!/usr/bin/env bash
# ==============================================================================
# FusionOS Instant Game Clip Recorder (Hardware-Accelerated ShadowPlay)
# Proposito: Grava clipes de jogos em alta definicao sem perda de FPS
# ==============================================================================

set -euo pipefail

SAVE_DIR="$HOME/Videos/FusionClips"
mkdir -p "$SAVE_DIR"

TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
OUTPUT_FILE="$SAVE_DIR/Clip_$TIMESTAMP.mp4"

echo "Gravando clipe de jogo..."

# Notifica o usuario
if command -v notify-send >/dev/null 2>&1; then
    notify-send -a "Fusion Game" -i "camera-video" "Gravação de Jogo" "Gravando clipe de 30 segundos..."
fi

# Detecta aceleracao de hardware (NVENC para NVIDIA ou VAAPI para AMD/Intel)
CODEC="libx264"
if command -v ffmpeg >/dev/null 2>&1; then
    if ffmpeg -encoders 2>/dev/null | grep -q "h264_nvenc"; then
        CODEC="h264_nvenc"
    elif ffmpeg -encoders 2>/dev/null | grep -q "h264_vaapi"; then
        CODEC="h264_vaapi"
    fi

    # Grava 30 segundos com baixa sobrecarga
    ffmpeg -y -f kmsgrab -i - -vf 'hwmap=derive_device=vaapi,scale_vaapi=format=nv12' -c:v "$CODEC" -qp 20 -t 30 "$OUTPUT_FILE" 2>/dev/null || \
    ffmpeg -y -f x11grab -video_size 1920x1080 -framerate 60 -i :0.0 -c:v "$CODEC" -preset fast -t 30 "$OUTPUT_FILE" 2>/dev/null || true
fi

if [[ -f "$OUTPUT_FILE" ]]; then
    if command -v notify-send >/dev/null 2>&1; then
        notify-send -a "Fusion Game" -i "video-mp4" "Clipe Salvo!" "Salvo em: $OUTPUT_FILE"
    fi
fi
