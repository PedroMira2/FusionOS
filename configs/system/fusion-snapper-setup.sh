#!/usr/bin/env bash
# ==============================================================================
# FusionOS - Provisionador do Btrfs Time Machine & GRUB Snapshots
# ==============================================================================

set -euo pipefail

# Verifica se o sistema raiz e Btrfs
ROOT_FSTYPE=$(findmnt -n -o FSTYPE / 2>/dev/null || echo "unknown")
if [[ "$ROOT_FSTYPE" != "btrfs" ]]; then
    echo "[AVISO] O sistema raiz nao e Btrfs. Snapshots no GRUB estao desativados."
    exit 0
fi

echo "Configurando o FusionOS Btrfs Time Machine..."

# Configura o Snapper para a raiz
if ! snapper list-configs 2>/dev/null | grep -q "root"; then
    snapper -c root create-config / || true
fi

# Aplica a politica de retencao personalizada do FusionOS
if [[ -f "/usr/share/fusionos/repo/configs/system/snapper-root.conf" ]]; then
    cp "/usr/share/fusionos/repo/configs/system/snapper-root.conf" /etc/snapper/configs/root
elif [[ -f "/etc/snapper/configs/root" ]]; then
    sed -i 's/^NUMBER_LIMIT=.*/NUMBER_LIMIT="10"/' /etc/snapper/configs/root
    sed -i 's/^TIMELINE_LIMIT_HOURLY=.*/TIMELINE_LIMIT_HOURLY="5"/' /etc/snapper/configs/root
fi

# Ativa os servicos de limpeza automatica do Snapper
systemctl enable --now snapper-timeline.timer 2>/dev/null || true
systemctl enable --now snapper-cleanup.timer 2>/dev/null || true

# Configura o grub-btrfs para gerar entradas de boot para cada snapshot
if command -v grub-btrfs >/dev/null 2>&1; then
    grub-btrfs /boot/grub2/grub.cfg 2>/dev/null || true
    systemctl enable --now grub-btrfsd.service 2>/dev/null || true
fi

echo "[SUCESSO] FusionOS Time Machine ativo com snapshots no GRUB!"
