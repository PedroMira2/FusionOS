#!/usr/bin/env bash
# ==============================================================================
# FusionOS Shell Integration & Aliases
# ==============================================================================

# Executar Fastfetch apenas em sessoes interativas do terminal
if [[ $- == *i* ]] && command -v fastfetch >/dev/null 2>&1; then
    fastfetch --config /etc/fastfetch/config.jsonc 2>/dev/null || fastfetch
fi

# Atalhos uteis do FusionOS
alias fusion-info="fastfetch"
alias fusion-update="sudo dnf upgrade --refresh -y && flatpak update -y"
alias fusion-layout="fusion-switch-layout"
alias fusion-wine="fusion-wine-handler"
