#!/usr/bin/env bash
# ==============================================================================
# FusionOS - Chameleon Layout Switcher
# Proposito: Permite alternar instantaneamente entre layout Mac, Windows 11 e Gamer
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="/usr/share/fusionos/layouts"
if [[ ! -d "$SCRIPT_DIR" ]]; then
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../configs/layouts" && pwd)"
fi

TARGET_MODE="${1:-}"

if [[ -z "$TARGET_MODE" ]]; then
    if command -v kdialog >/dev/null 2>&1; then
        TARGET_MODE=$(kdialog --title "FusionOS - Personalizar Layout" \
            --radiolist "Escolha a aparencia que mais combina com seu estilo:" \
            "macos" "Estilo Mac (Barra Superior + Dock Flutuante Translúcido)" on \
            "win11" "Estilo Windows 11 (Barra de Tarefas Centralizada Familiar)" off \
            "gamer" "Estilo Gamer / Foco (Ultra Imersivo com Auto-Ocultação)" off 2>/dev/null)
    elif command -v zenity >/dev/null 2>&1; then
        TARGET_MODE=$(zenity --list --radiolist --title="FusionOS - Personalizar Layout" \
            --column="Selecionar" --column="ID" --column="Estilo" \
            TRUE "macos" "Estilo Mac (Barra Superior + Dock Flutuante)" \
            FALSE "win11" "Estilo Windows 11 (Barra Centralizada)" \
            FALSE "gamer" "Estilo Gamer / Foco (Imersao Total)" 2>/dev/null)
    else
        echo "Uso: $0 [macos|win11|gamer]"
        exit 1
    fi
fi

if [[ -z "$TARGET_MODE" ]]; then
    exit 0
fi

LAYOUT_FILE=""
MODE_NAME=""

case "$TARGET_MODE" in
    macos)
        LAYOUT_FILE="${SCRIPT_DIR}/layout-macos.js"
        MODE_NAME="macOS (Barra Superior + Dock)"
        ;;
    win11)
        LAYOUT_FILE="${SCRIPT_DIR}/layout-win11.js"
        MODE_NAME="Windows 11 (Barra Centralizada)"
        ;;
    gamer)
        LAYOUT_FILE="${SCRIPT_DIR}/layout-gamer.js"
        MODE_NAME="Gamer & Foco (Imersivo)"
        ;;
    *)
        echo "Opcao invalida: $TARGET_MODE"
        exit 1
        ;;
esac

if [[ ! -f "$LAYOUT_FILE" ]]; then
    echo "Erro: Arquivo de layout $LAYOUT_FILE nao encontrado."
    exit 1
fi

JS_CODE=$(cat "$LAYOUT_FILE")

# Executa o script diretamente na instancia ativa do PlasmaShell via DBus
if command -v qdbus-qt6 >/dev/null 2>&1; then
    qdbus-qt6 org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript "$JS_CODE" >/dev/null 2>&1 || true
elif command -v qdbus >/dev/null 2>&1; then
    qdbus org.kde.plasmashell /PlasmaShell evaluateScript "$JS_CODE" >/dev/null 2>&1 || true
fi

notify-send "FusionOS" "Layout alterado com sucesso para: $MODE_NAME" --icon=preferences-desktop-theme 2>/dev/null || true

