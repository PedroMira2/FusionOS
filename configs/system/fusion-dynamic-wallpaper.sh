#!/usr/bin/env bash
# ==============================================================================
# FusionOS Dynamic Wallpaper Engine
# Alternância automática e suave de papel de parede Dia / Noite para Plasma Wayland
# ==============================================================================

set -euo pipefail

WALLPAPER_DIR="/usr/share/backgrounds/fusionos"
DAY_WALLPAPER="${WALLPAPER_DIR}/fusionos-wallpaper.png"
NIGHT_WALLPAPER="${WALLPAPER_DIR}/fusionos-wallpaper.png"

# Se houver variantes separadas dia/noite, utilize-as
if [[ -f "${WALLPAPER_DIR}/fusionos-day.png" ]]; then
    DAY_WALLPAPER="${WALLPAPER_DIR}/fusionos-day.png"
fi
if [[ -f "${WALLPAPER_DIR}/fusionos-night.png" ]]; then
    NIGHT_WALLPAPER="${WALLPAPER_DIR}/fusionos-night.png"
fi

MODE="${1:-auto}"

apply_wallpaper() {
    local target="$1"
    if [[ ! -f "$target" ]]; then
        echo "[FusionOS] Aviso: Papel de parede não encontrado: $target"
        return 0
    fi
    
    # 1. Utilizar comando oficial do Plasma se disponível
    if command -v plasma-apply-wallpaperimage &>/dev/null; then
        plasma-apply-wallpaperimage "$target" &>/dev/null || true
    fi

    # 2. Configurar plasma-org.kde.plasma.desktop-appletsrc caso esteja em headless
    local plasma_cfg="${HOME}/.config/plasma-org.kde.plasma.desktop-appletsrc"
    if [[ -f "$plasma_cfg" ]] && command -v kwriteconfig6 &>/dev/null; then
        kwriteconfig6 --file "$plasma_cfg" --group "Wallpaper" --group "org.kde.image" --group "General" --key "Image" "$target" || true
    fi
    echo "[FusionOS] Papel de parede aplicado: $target"
}

case "$MODE" in
    day)
        apply_wallpaper "$DAY_WALLPAPER"
        ;;
    night)
        apply_wallpaper "$NIGHT_WALLPAPER"
        ;;
    auto|*)
        HOUR=$(date +%H)
        # Horário diurno: 06h às 18h
        if (( 10#$HOUR >= 6 && 10#$HOUR < 18 )); then
            apply_wallpaper "$DAY_WALLPAPER"
        else
            apply_wallpaper "$NIGHT_WALLPAPER"
        fi
        ;;
esac
