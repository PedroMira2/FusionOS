#!/usr/bin/env bash
# ==============================================================================
# FusionOS - ISO Image Builder
# Proposito: Compila a imagem ISO bootavel a partir do Kickstart via livemedia-creator
# ==============================================================================

set -euo pipefail

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}======================================================${NC}"
echo -e "${BLUE}        FusionOS - Compilador de Imagem ISO Bootavel  ${NC}"
echo -e "${BLUE}======================================================${NC}"

if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}Erro: Este script exige privilégios de root para montar imagens e chroot.${NC}"
   echo "Execute: sudo ./build-iso.sh"
   exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
KS_FILE="${ROOT_DIR}/kickstart/fusionos-fedora.ks"
OUTPUT_DIR="${ROOT_DIR}/output"

# Verifica se o arquivo kickstart existe
if [[ ! -f "$KS_FILE" ]]; then
    echo -e "${RED}Erro: Arquivo kickstart não encontrado em $KS_FILE${NC}"
    exit 1
fi

# Verifica ferramentas de compilação
if ! command -v livemedia-creator >/dev/null 2>&1; then
    echo -e "${YELLOW}Ferramenta 'livemedia-creator' não encontrada. Instalando dependências (lorax)...${NC}"
    dnf install -y lorax pykickstart
fi

echo -e "${YELLOW}Validando sintaxe do arquivo Kickstart...${NC}"
ksvalidator "$KS_FILE"
echo -e "${GREEN}✔ Kickstart válido!${NC}"

rm -rf "$OUTPUT_DIR"

FEDORA_VER=$(rpm -E %fedora 2>/dev/null || echo "40")
if [[ -z "$FEDORA_VER" || "$FEDORA_VER" == "%fedora" ]]; then
    FEDORA_VER="40"
fi

echo -e "\n${YELLOW}Iniciando a compilação da ISO do FusionOS (Fedora ${FEDORA_VER})...${NC}"
livemedia-creator \
    --ks="$KS_FILE" \
    --no-virt \
    --make-iso \
    --project="FusionOS-x86_64" \
    --releasever="$FEDORA_VER" \
    --volid="FusionOS_Live" \
    --iso-name="FusionOS-Live-x86_64.iso" \
    --resultdir="$OUTPUT_DIR"

echo -e "\n${GREEN}✔ Compilação concluída com sucesso!${NC}"
echo -e "${GREEN}A ISO foi gerada em: ${OUTPUT_DIR}/FusionOS-Live-x86_64.iso${NC}"
echo -e "Você já pode gravar esta imagem em um pendrive usando o BalenaEtcher ou Rufus."

