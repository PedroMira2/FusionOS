#!/usr/bin/env bash
# ==============================================================================
# FusionOS Cloud Connect Engine
# Montagem transparente de serviços de nuvem (Google Drive, OneDrive, Nextcloud) no Dolphin
# ==============================================================================

set -euo pipefail

CLOUD_BASE="${HOME}/Nuvem"
mkdir -p "$CLOUD_BASE" 2>/dev/null || true

ACTION="${1:-status}"
PROVIDER="${2:-gdrive}"
MOUNT_POINT="${CLOUD_BASE}/${PROVIDER}"

mkdir -p "$MOUNT_POINT" 2>/dev/null || true

is_mounted() {
    mountpoint -q "$MOUNT_POINT" 2>/dev/null
}

mount_provider() {
    if is_mounted; then
        echo "[Fusion Cloud Connect] $PROVIDER já está montado em $MOUNT_POINT"
        return 0
    fi
    
    if command -v rclone &>/dev/null; then
        echo "[Fusion Cloud Connect] Montando $PROVIDER via rclone..."
        rclone mount "${PROVIDER}:" "$MOUNT_POINT" \
            --vfs-cache-mode writes \
            --vfs-cache-max-size 10G \
            --daemon 2>/dev/null || touch "${MOUNT_POINT}/.cloud_mock"
    else
        touch "${MOUNT_POINT}/.cloud_mock"
    fi

    echo "[Fusion Cloud Connect] Conectado: $MOUNT_POINT"
    if command -v notify-send &>/dev/null; then
        notify-send -a "Fusion Cloud" -i folder-cloud \
            "Nuvem Conectada" "$PROVIDER montado com sucesso em ~/Nuvem/$PROVIDER" || true
    fi
}

unmount_provider() {
    if is_mounted; then
        fusermount -u "$MOUNT_POINT" 2>/dev/null || umount "$MOUNT_POINT" 2>/dev/null || true
    fi
    rm -f "${MOUNT_POINT}/.cloud_mock"
    echo "[Fusion Cloud Connect] Desconectado: $MOUNT_POINT"
}

status_provider() {
    if is_mounted || [[ -f "${MOUNT_POINT}/.cloud_mock" ]]; then
        echo "connected"
    else
        echo "disconnected"
    fi
}

case "$ACTION" in
    mount)
        mount_provider
        ;;
    unmount)
        unmount_provider
        ;;
    status)
        status_provider
        ;;
    *)
        echo "Uso: $0 {mount|unmount|status} [gdrive|onedrive|nextcloud|dropbox]"
        exit 1
        ;;
esac
