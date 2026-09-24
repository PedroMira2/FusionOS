#!/usr/bin/env bash
# ==============================================================================
# Fusion Connect Setup (KDE Connect Integration)
# Proposito: Configura firewall e servico para integracao perfeita com celulares
# ==============================================================================

set -euo pipefail

echo "Configurando Fusion Connect (Pareamento com Celular)..."

# Libera portas do KDE Connect no firewall se o firewalld estiver ativo
if command -v firewall-cmd >/dev/null 2>&1 && systemctl is-active --quiet firewalld; then
    firewall-cmd --permanent --add-service=kde-connect 2>/dev/null || true
    firewall-cmd --reload 2>/dev/null || true
fi

# Inicializa o servico do KDE Connect em segundo plano para o usuario
if command -v kdeconnectd >/dev/null 2>&1; then
    if ! pgrep -x "kdeconnectd" >/dev/null 2>&1; then
        /usr/libexec/kdeconnectd &
    fi
fi

echo "[SUCESSO] Fusion Connect pronto para pareamento via Wi-Fi!"
