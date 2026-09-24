#!/usr/bin/env bash
# ==============================================================================
# FusionOS Silent Background Update Engine
# Atualizações automáticas invisíveis de segurança e flatpaks sem travar o sistema
# ==============================================================================

set -euo pipefail

LOG_FILE="/var/log/fusion-update.log"
mkdir -p "$(dirname "$LOG_FILE")" 2>/dev/null || true

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [Fusion Auto-Update] $*" | tee -a "$LOG_FILE" 2>/dev/null || echo "$*"
}

log "Iniciando verificação silenciosa de atualizações..."

# 1. Atualizar repositórios e baixar pacotes DNF em background com prioridade mínima (idle)
if command -v dnf &>/dev/null; then
    log "Baixando pacotes de sistema em segundo plano (--downloadonly)..."
    nice -n 19 ionice -c 3 dnf upgrade --downloadonly -y --refresh &>> "$LOG_FILE" || true
fi

# 2. Atualizar Flatpaks silenciosamente em segundo plano
if command -v flatpak &>/dev/null; then
    log "Atualizando aplicativos Flatpak de forma não-interativa..."
    nice -n 19 ionice -c 3 flatpak update -y --noninteractive &>> "$LOG_FILE" || true
fi

log "Ciclo de atualização em segundo plano concluído com sucesso."
