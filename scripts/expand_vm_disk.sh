#!/usr/bin/env bash
# Script para expandir a partição raiz automaticamente no Fedora (Suporta Btrfs, Ext4, XFS e LVM)
set -e
set -x

echo "Instalando ferramentas de expansão..."
sudo dnf install -y cloud-utils-growpart lvm2

ROOT_PART=$(df / --output=source | tail -n 1)

if [[ "$ROOT_PART" == /dev/mapper/* ]]; then
    echo "LVM detectado. Tentando expandir Physical Volume..."
    # Pega o primeiro PV associado
    PV_PATH=$(sudo pvs --noheadings -o pv_name | tr -d ' ' | head -n 1)
    PARENT_DISK=$(lsblk -no pkname "$PV_PATH")
    CLEAN_NAME=$(basename "$PV_PATH")
    PART_NUM=$(echo "$CLEAN_NAME" | grep -o '[0-9]*$')
    
    echo "Expandindo partição /dev/$PARENT_DISK numero $PART_NUM..."
    sudo growpart "/dev/$PARENT_DISK" "$PART_NUM" || true
    
    sudo pvresize "$PV_PATH"
    sudo lvextend -l +100%FREE "$ROOT_PART"
    sudo xfs_growfs / || sudo resize2fs / || sudo btrfs filesystem resize max /
else
    CLEAN_NAME=$(basename "$ROOT_PART")
    PARENT_DISK=$(lsblk -no pkname "$ROOT_PART")
    
    if [ -n "$PARENT_DISK" ]; then
        PART_NUM=$(echo "$CLEAN_NAME" | grep -o '[0-9]*$')
        echo "Expandindo partição /dev/$PARENT_DISK numero $PART_NUM..."
        sudo growpart "/dev/$PARENT_DISK" "$PART_NUM" || true
        
        # Redimensiona o sistema de arquivos 
        sudo btrfs filesystem resize max / || sudo xfs_growfs / || sudo resize2fs "$ROOT_PART"
    else
        echo "Não foi possível detectar o disco físico automaticamente."
        lsblk
    fi
fi

echo "=================================================="
echo "Expansão concluída! Novo tamanho do disco:"
df -h /
echo "=================================================="
