#!/bin/bash
# ==============================================================================
# FusionOS Shell Profile
# Configurações de terminal interativo, aliases e exibição do Fastfetch
# ==============================================================================

# Executa apenas em sessões interativas
if [[ $- == *i* ]]; then
    if command -v fastfetch &>/dev/null; then
        fastfetch
    fi

    # Aliases úteis do FusionOS
    alias update="sudo dnf upgrade -y && flatpak update -y"
    alias cleaner="fusion-cleaner"
    alias gamebar="fusion-gamebar"
    alias control="fusion-control-center"
    alias vault="fusion-vault-gui"
    alias shield="fusion-shield"
fi
