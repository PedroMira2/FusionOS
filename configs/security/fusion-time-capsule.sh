#!/usr/bin/env bash
# ==============================================================================
# FusionOS Time Capsule Engine
# Sistema de backup incremental e snapshots estilo Apple Time Machine
# ==============================================================================

set -euo pipefail

BACKUP_ROOT="${FUSION_BACKUP_DEST:-/var/fusion-backups/${USER}}"
SOURCE_DIR="${HOME}"
ACTION="${1:-list}"

mkdir -p "$BACKUP_ROOT" 2>/dev/null || true

create_backup() {
    local timestamp
    timestamp="$(date +%Y-%m-%d_%H-%M-%S)"
    local target_dir="${BACKUP_ROOT}/snapshot_${timestamp}"
    local latest_link="${BACKUP_ROOT}/latest"

    echo "[Fusion Time Capsule] Iniciando backup incremental de ${SOURCE_DIR}..."

    local link_arg=""
    if [[ -d "$latest_link" ]]; then
        link_arg="--link-dest=${latest_link}"
    fi

    # Executa rsync com preservação total de atributos e hardlinks para deduplicação
    rsync -aAX --delete \
        --exclude='.cache' \
        --exclude='.local/share/Trash' \
        --exclude='Downloads' \
        --exclude='node_modules' \
        $link_arg \
        "${SOURCE_DIR}/" "${target_dir}/"

    # Atualiza symlink do latest
    rm -f "$latest_link"
    ln -s "${target_dir}" "$latest_link"

    echo "[Fusion Time Capsule] Backup concluído com sucesso: snapshot_${timestamp}"
    
    if command -v notify-send &>/dev/null; then
        notify-send -a "FusionOS" -i document-save \
            "Time Capsule Concluído" "Ponto de restauração salvo: snapshot_${timestamp}" -t 3000 || true
    fi
}

list_backups() {
    echo "[Fusion Time Capsule] Pontos de restauração disponíveis:"
    if [[ -d "$BACKUP_ROOT" ]]; then
        find "$BACKUP_ROOT" -maxdepth 1 -name "snapshot_*" -type d | sort -r | while read -r d; do
            local base
            base="$(basename "$d")"
            local size
            size="$(du -sh "$d" 2>/dev/null | cut -f1)"
            echo "• ${base} (${size})"
        done
    fi
}

case "$ACTION" in
    backup|create)
        create_backup
        ;;
    list)
        list_backups
        ;;
    *)
        echo "Uso: $0 {create|list}"
        exit 1
        ;;
esac
