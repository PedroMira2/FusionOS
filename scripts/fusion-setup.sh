#!/usr/bin/env bash
# ==============================================================================
#           ███████╗██╗   ██╗███████╗██╗ ██████╗ ███╗   ██╗ ██████╗ ███████╗
#           ██╔════╝██║   ██║██╔════╝██║██╔═══██╗████╗  ██║██╔═══██╗██╔════╝
#           █████╗  ██║   ██║███████╗██║██║   ██║██╔██╗ ██║██║   ██║███████╗
#           ██╔══╝  ██║   ██║╚════██║██║██║   ██║██║╚██╗██║██║   ██║╚════██║
#           ██║     ╚██████╔╝███████║██║╚██████╔╝██║ ╚████║╚██████╔╝███████║
#           ╚═╝      ╚═════╝ ╚══════╝╚═╝ ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝ ╚══════╝
# ==============================================================================
# Instalador Mestre do FusionOS: O Melhor do Windows, Mac e Linux
# ==============================================================================

set -euo pipefail

CYAN='\033[0;36m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m'

clear
echo -e "${CYAN}${BOLD}"
echo "    ███████╗██╗   ██╗███████╗██╗ ██████╗ ███╗   ██╗ ██████╗ ███████╗"
echo "    ██╔════╝██║   ██║██╔════╝██║██╔═══██╗████╗  ██║██╔═══██╗██╔════╝"
echo "    █████╗  ██║   ██║███████╗██║██║   ██║██╔██╗ ██║██║   ██║███████╗"
echo "    ██╔══╝  ██║   ██║╚════██║██║██║   ██║██║╚██╗██║██║   ██║╚════██║"
echo "    ██║     ╚██████╔╝███████║██║╚██████╔╝██║ ╚████║╚██████╔╝███████║"
echo "    ╚═╝      ╚═════╝ ╚══════╝╚═╝ ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝ ╚══════╝"
echo -e "${NC}"
echo -e "${BLUE}${BOLD}   >>> Transformando o seu sistema no FusionOS Definitivo <<<${NC}\n"

if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}Erro: Execute este instalador com permissões de administrador (sudo ./fusion-setup.sh)${NC}"
   exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
TARGET_USER="${SUDO_USER:-$USER}"
TARGET_HOME=$(eval echo "~$TARGET_USER")

echo -e "${GREEN}Detectado usuário principal:${NC} ${BOLD}$TARGET_USER${NC} (Home: $TARGET_HOME)\n"

# 1. Atualizacao inicial rapida
echo -e "${YELLOW}[Passo 1/6] Atualizando indices do sistema...${NC}"
dnf check-update -y || true

# 2. Executa a Stack Gamer e Windows
echo -e "\n${YELLOW}[Passo 2/6] Configurando Compatibilidade Gamer & Windows (.exe, Epic, Steam)...${NC}"
bash "${ROOT_DIR}/scripts/install-gaming-stack.sh"

# 3. Executa Otimizacoes de Baixa Latencia e Estabilidade
echo -e "\n${YELLOW}[Passo 3/6] Aplicando Otimizacoes de Memoria ZRAM, Btrfs e PipeWire...${NC}"
bash "${ROOT_DIR}/scripts/optimize-system.sh"

# 4. Instalando Ambiente KDE Plasma 6 e Componentes Centrais
echo -e "\n${YELLOW}[Passo 4/6] Garantindo instalação do KDE Plasma 6, SDDM e Layouts...${NC}"
dnf install -y @kde-desktop plasma-workspace-wayland sddm || true
systemctl enable sddm || true

mkdir -p /usr/share/fusionos/layouts
mkdir -p /usr/share/backgrounds/fusionos/
cp -rf "${ROOT_DIR}/configs/layouts/"* /usr/share/fusionos/layouts/
cp -f "${ROOT_DIR}/assets/fusionos-logo.svg" /usr/share/backgrounds/fusionos/logo.svg

# Registra os binarios do sistema no PATH
install -m 755 "${ROOT_DIR}/scripts/fusion-switch-layout.sh" /usr/local/bin/fusion-switch-layout
install -m 644 "${ROOT_DIR}/configs/layouts/fusion-layout-switcher.desktop" /usr/share/applications/fusion-layout-switcher.desktop

# 5. Instalando Tipografia Nítida Estilo macOS
echo -e "\n${YELLOW}[Passo 5/6] Instalando e Otimizando Fontes (Renderizacao Mac)...${NC}"
dnf install -y rsms-inter-fonts google-noto-sans-fonts fira-code-fonts || true

# 6. Aplicando Perfil Visual Padrao (macOS Mode) e Atalhos
echo -e "\n${YELLOW}[Passo 6/6] Configurando Atalhos Globais e Aparencia Inicial...${NC}"
USER_KDE_CONFIG="${TARGET_HOME}/.config"
mkdir -p "${USER_KDE_CONFIG}"

# Atalhos de teclado (Win+E, Win+V, Alt+Espaço Spotlight)
cp -f "${ROOT_DIR}/configs/kde/kglobalshortcutsrc" "${USER_KDE_CONFIG}/kglobalshortcutsrc" || true
cp -f "${ROOT_DIR}/configs/kde/kwinrc" "${USER_KDE_CONFIG}/kwinrc" || true

# Garante que os arquivos pertencem ao usuario real
chown -R "${TARGET_USER}:${TARGET_USER}" "${USER_KDE_CONFIG}"

echo -e "\n${GREEN}${BOLD}======================================================${NC}"
echo -e "${GREEN}${BOLD}     ✔ Instalação do FusionOS Concluída com Sucesso!  ${NC}"
echo -e "${GREEN}${BOLD}======================================================${NC}"
echo -e "${CYAN}O que foi ativado para o seu cliente:${NC}"
echo -e "  1. ${BOLD}Compatibilidade Windows (.exe/.msi):${NC} Duplo clique assistido com Wine e Bottles."
echo -e "  2. ${BOLD}Plataformas de Jogos:${NC} Epic Games (Heroic Launcher) e Steam configuradas com Proton-GE."
echo -e "  3. ${BOLD}Chameleon Engine:${NC} Alterne entre estilo Mac, Windows 11 e Gamer pelo aplicativo 'Alternador de Estilo FusionOS'."
echo -e "  4. ${BOLD}Spotlight:${NC} Pressione ${BOLD}Alt + Espaço${NC} para busca global instantânea."
echo -e "  5. ${BOLD}Segurança à Prova de Falhas:${NC} Snapshots Btrfs no GRUB prontos para restauração em 5 segundos."
echo -e "\n${YELLOW}Recomendado reiniciar a máquina para carregar o novo kernel e serviços: ${BOLD}reboot${NC}\n"

