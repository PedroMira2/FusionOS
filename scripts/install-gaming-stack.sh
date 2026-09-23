#!/usr/bin/env bash
# ==============================================================================
# FusionOS - Gaming & Windows Apps Installation Engine
# Proposito: Instala e configura Epic Games (Heroic), Steam (Proton), Wine e Codecs
# ==============================================================================

set -euo pipefail

# Cores para o terminal
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}======================================================${NC}"
echo -e "${BLUE}   FusionOS - Configuração da Stack Gamer & Windows   ${NC}"
echo -e "${BLUE}======================================================${NC}"

if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}Este script precisa ser executado como root (ou via sudo).${NC}"
   exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo -e "\n${YELLOW}[1/6] Habilitando Repositorios Essenciais (RPM Fusion & Flathub)...${NC}"
dnf install -y \
    https://mirrors.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm \
    https://mirrors.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-$(rpm -E %fedora).noarch.rpm || true

dnf config-manager --enable fedora-cisco-openh264 -y || true

# Configura Flathub Oficial Completo
flatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo

echo -e "\n${YELLOW}[2/6] Instalando Codecs de Video/Audio e Suporte Grafico Completo...${NC}"
dnf swap -y ffmpeg-free ffmpeg --allowerasing || true
dnf install -y --allowerasing --skip-unavailable \
    gstreamer1-plugins-bad-freeworld \
    gstreamer1-plugins-ugly \
    gstreamer1-plugin-openh264 \
    gstreamer1-libav \
    ffmpeg \
    mesa-va-drivers \
    vulkan-loader \
    vulkan-tools || true

echo -e "\n${YELLOW}[3/6] Instalando Camada de Compatibilidade Windows (Wine, DXVK, Vulkan)...${NC}"
dnf install -y --allowerasing --skip-unavailable \
    wine \
    winetricks \
    gamemode \
    mangohud \
    zenity \
    kdialog || true

echo -e "\n${YELLOW}[4/6] Instalando Plataformas de Jogos (Epic Games, Steam, Bottles)...${NC}"
# Instala Steam via DNF para maxima integracao de drivers
dnf install -y steam || true

# Instala Heroic Games Launcher (Epic Games + GOG + Amazon) e Bottles via Flatpak
flatpak install -y flathub \
    com.heroicgameslauncher.hgl \
    com.usebottles.bottles \
    net.davidotek.pupgui2 # ProtonUp-Qt (Gerenciador de Proton-GE)

echo -e "\n${YELLOW}[5/6] Instalando o Assistente de Executaveis (.exe / .msi)...${NC}"
# Copia o script handler e a associacao MIME
install -m 755 "${ROOT_DIR}/configs/wine/fusion-wine-handler.sh" /usr/local/bin/fusion-wine-handler
install -m 644 "${ROOT_DIR}/configs/wine/fusion-exe-runner.desktop" /usr/share/applications/fusion-exe-runner.desktop

# Associa tipos MIME de executaveis Windows
update-desktop-database /usr/share/applications || true

echo -e "\n${YELLOW}[6/6] Otimizando GameMode e Prioridades de Jogos...${NC}"
install -m 644 "${ROOT_DIR}/configs/system/gamemode.ini" /etc/gamemode.ini

echo -e "\n${GREEN}✔ Stack Gamer e Compatibilidade com Windows configurada com sucesso!${NC}"

