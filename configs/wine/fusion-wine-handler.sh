#!/usr/bin/env bash
# ==============================================================================
# FusionOS - Windows Application Handler (.exe / .msi)
# Proposito: Oferece experiencia de duplo clique nativa para programas do Windows
# ==============================================================================

set -euo pipefail

FILE_PATH="${1:-}"

if [[ -z "$FILE_PATH" || ! -f "$FILE_PATH" ]]; then
    if command -v kdialog >/dev/null 2>&1; then
        kdialog --title "FusionOS Windows Runner" --error "Nenhum arquivo executavel (.exe/.msi) selecionado."
    elif command -v zenity >/dev/null 2>&1; then
        zenity --error --title="FusionOS Windows Runner" --text="Nenhum arquivo executavel (.exe/.msi) selecionado."
    fi
    exit 1
fi

BASENAME=$(basename "$FILE_PATH")

# Verifica se o Wine ou Bottles estao instalados
if ! command -v wine >/dev/null 2>&1 && ! flatpak list | grep -q "com.usebottles.bottles"; then
    if command -v kdialog >/dev/null 2>&1; then
        kdialog --title "FusionOS Compatibility Layer" --yesno \
            "O suporte a programas do Windows (.exe) ainda nao foi instalado.\nDeseja instalar o pacote completo de compatibilidade agora?"
        if [[ $? -eq 0 ]]; then
            pkexec dnf install -y wine winetricks bottles || flatpak install -y flathub com.usebottles.bottles
        else
            exit 0
        fi
    fi
fi

# Caixa de dialogo para o usuario escolher o modo de execucao
CHOICE=""
if command -v kdialog >/dev/null 2>&1; then
    CHOICE=$(kdialog --title "FusionOS Windows Launcher - $BASENAME" \
        --radiolist "Como deseja executar '$BASENAME'?" \
        1 "Executar com Wine Direto (Mais rapido e simples)" on \
        2 "Abrir no Bottles (Ambiente isolado em container - Seguro)" off \
        3 "Abrir no Heroic Games (Se for instalador de jogos Epic/GOG)" off 2>/dev/null)
elif command -v zenity >/dev/null 2>&1; then
    CHOICE=$(zenity --list --radiolist --title="FusionOS Windows Launcher - $BASENAME" \
        --column="Selecionar" --column="ID" --column="Opcao" \
        TRUE 1 "Executar com Wine Direto (Mais rapido e simples)" \
        FALSE 2 "Abrir no Bottles (Ambiente isolado em container - Seguro)" \
        FALSE 3 "Abrir no Heroic Games (Se for instalador de jogos Epic/GOG)" 2>/dev/null)
else
    # Fallback sem GUI
    CHOICE="1"
fi

case "$CHOICE" in
    1|"1")
        # Cria prefixo padrao de 64-bit se nao existir
        export WINEPREFIX="${HOME}/.wine"
        export WINEARCH="win64"
        export DXVK_HUD=0
        notify-send "FusionOS" "Iniciando $BASENAME com Wine..." --icon=application-x-ms-dos-executable 2>/dev/null || true
        wine "$FILE_PATH" &
        ;;
    2|"2")
        notify-send "FusionOS" "Encaminhando $BASENAME para o Bottles..." --icon=com.usebottles.bottles 2>/dev/null || true
        if flatpak list | grep -q "com.usebottles.bottles"; then
            flatpak run com.usebottles.bottles -e "$FILE_PATH" &
        elif command -v bottles >/dev/null 2>&1; then
            bottles -e "$FILE_PATH" &
        else
            wine "$FILE_PATH" &
        fi
        ;;
    3|"3")
        notify-send "FusionOS" "Abrindo Heroic Games Launcher..." --icon=com.heroicgameslauncher.hgl 2>/dev/null || true
        if flatpak list | grep -q "com.heroicgameslauncher.hgl"; then
            flatpak run com.heroicgameslauncher.hgl &
        elif command -v heroic >/dev/null 2>&1; then
            heroic &
        else
            wine "$FILE_PATH" &
        fi
        ;;
    *)
        exit 0
        ;;
esac

