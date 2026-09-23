#!/usr/bin/env bash
# ==============================================================================
# FusionOS - System Optimization & Stability Engine
# Proposito: Aplica ZRAM (ZSTD), tuning de kernel, baixa latencia de audio e Btrfs
# ==============================================================================

set -euo pipefail

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}======================================================${NC}"
echo -e "${BLUE}     FusionOS - Otimização de Sistema & Estabilidade  ${NC}"
echo -e "${BLUE}======================================================${NC}"

if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}Este script precisa ser executado como root (ou via sudo).${NC}"
   exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo -e "\n${YELLOW}[1/5] Aplicando Ajustes de Kernel de Baixa Latencia (Sysctl)...${NC}"
install -m 644 "${ROOT_DIR}/configs/system/99-fusion-performance.conf" /etc/sysctl.d/99-fusion-performance.conf
sysctl --system >/dev/null 2>&1 || true

echo -e "\n${YELLOW}[2/5] Configurando ZRAM de Alta Compressao (ZSTD)...${NC}"
dnf install -y zram-generator-defaults zram-generator || true
install -m 644 "${ROOT_DIR}/configs/system/zram-generator.conf" /etc/systemd/zram-generator.conf
systemctl daemon-reload
systemctl restart systemd-zram-setup@zram0.service || true

echo -e "\n${YELLOW}[3/5] Configurando Audio de Baixa Latencia Estilo macOS (PipeWire)...${NC}"
mkdir -p /etc/pipewire/pipewire.conf.d/
install -m 644 "${ROOT_DIR}/configs/system/pipewire-lowlatency.conf" /etc/pipewire/pipewire.conf.d/99-lowlatency.conf
systemctl --user --global restart pipewire pipewire-pulse wireplumber 2>/dev/null || true

echo -e "\n${YELLOW}[4/5] Configurando Sistema de Restauracao 'A Prova de Falhas' (Btrfs Snapshots)...${NC}"
dnf install -y snapper btrfs-assistant grub-btrfs inotify-tools || true

# Configura Snapper na particao raiz se estiver em Btrfs
if findmnt -n -o FSTYPE / | grep -q "btrfs"; then
    if ! snapper list-configs | grep -q "root"; then
        snapper -c root create-config / || true
        # Limita snapshots para nao lotar o disco
        sed -i 's/NUMBER_LIMIT="50"/NUMBER_LIMIT="10"/' /etc/snapper/configs/root || true
        sed -i 's/NUMBER_LIMIT_IMPORTANT="10"/NUMBER_LIMIT_IMPORTANT="5"/' /etc/snapper/configs/root || true
    fi
    systemctl enable --now snapper-timeline.timer snapper-cleanup.timer || true
    systemctl enable --now grub-btrfsd || true
    echo -e "${GREEN}✔ Pontos de restauracao Btrfs ativados no menu de boot.${NC}"
else
    echo -e "${YELLOW}Aviso: A particao raiz nao e Btrfs. Snapshots avancados foram ignorados.${NC}"
fi

echo -e "\n${YELLOW}[5/5] Ajustes de SSD e Limpeza de Logs do Sistema...${NC}"
systemctl enable --now fstrim.timer || true

# Limita o journald a 200MB maximo para nao acumular lixo
mkdir -p /etc/systemd/journald.conf.d/
cat <<EOF > /etc/systemd/journald.conf.d/size-limit.conf
[Journal]
SystemMaxUse=200M
EOF
systemctl restart systemd-journald || true

echo -e "\n${GREEN}✔ Sistema otimizado com sucesso!${NC}"

