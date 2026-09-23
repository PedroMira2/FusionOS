# FusionOS 🚀

> **O Sistema Operacional que une a elegância do macOS, a produtividade e compatibilidade do Windows, e a solidez e velocidade do Linux.**

[![Base](https://img.shields.io/badge/Base-Fedora%2040%2F41-0b57a4?logo=fedora)](https://fedoraproject.org)
[![Desktop](https://img.shields.io/badge/Desktop-KDE%20Plasma%206-1d99f3?logo=kde)](https://kde.org)
[![Display](https://img.shields.io/badge/Display-Wayland-red)]()
[![Audio](https://img.shields.io/badge/Audio-PipeWire%20Low%20Latency-blue)]()
[![Gaming](https://img.shields.io/badge/Gaming-Steam%20%7C%20Epic%20%7C%20Wine-black)]()

---

## 🌟 O que torna o FusionOS Único?

1. **Aparência Fluida no Estilo Mac (Padrão):**
   * Barra superior translúcida com relógio central e menu global.
   * Dock flutuante inferior com cantos arredondados e auto-ocultação inteligente.
   * Busca global **Spotlight** acionada por `Alt + Espaço`.
   * Gestos táteis 1:1 no touchpad (Wayland nativo).

2. **Chameleon Layout Engine (100% Moldável):**
   * Alterne em **1 clique** entre o **Modo Mac**, **Modo Windows 11** (com barra inferior centralizada e Menu Iniciar clássico) ou **Modo Gamer / Foco**.

3. **Compatibilidade Total com o Windows:**
   * **Execução com duplo clique em arquivos `.exe` e `.msi`** através do assistente gráfico integrado.
   * **Heroic Games Launcher** pré-instalado para suporte nativo à **Epic Games Store**, **GOG** e **Amazon Games**.
   * **Steam** pré-configurada com **Proton-GE** ativado.
   * **GameMode + MangoHud** para máxima taxa de quadros e baixa latência.

4. **Desempenho & Estabilidade de Servidor:**
   * Ocupa apenas **~900MB de RAM** em repouso.
   * **ZRAM com compressão ZSTD:** Comprime dados na memória para rodar suave em qualquer PC.
   * **Snapshots Btrfs no GRUB:** Restaure o sistema em 5 segundos caso algo dê errado.
   * **Zero telemetria, zero anúncios e zero bloatware.**

---

## 📂 Estrutura do Projeto

```text
HEAK/
├── configs/
│   ├── kde/                  # Atalhos globais, KWin blur e gestos
│   ├── layouts/              # Templates de layout (Mac, Windows 11, Gamer)
│   ├── system/               # Kernel sysctl, ZRAM ZSTD, PipeWire e GameMode
│   └── wine/                 # Handler gráfico e associações para .exe e .msi
├── scripts/
│   ├── fusion-setup.sh       # Instalador mestre automatizado
│   ├── fusion-switch-layout.sh # Alternador instantâneo de interface
│   ├── install-gaming-stack.sh # Epic, Steam, Wine, DXVK e Codecs
│   ├── optimize-system.sh    # Otimizações de latência, memória e Btrfs
│   └── build-iso.sh          # Compilador da imagem ISO bootável
├── kickstart/
│   └── fusionos-fedora.ks    # Manifesto Kickstart oficial para a ISO
├── docs/
│   ├── VALUE_PROPOSITION.md  # Por que seu cliente vai preferir o FusionOS
│   ├── BUILD_ISO.md          # Passo a passo de compilação da ISO
│   └── USER_GUIDE.md         # Manual do usuário final
└── README.md
```

---

## 🚀 Como Usar e Testar

### Opção 1: Aplicar em uma instalação limpa do Fedora KDE
Para transformar qualquer computador rodando Fedora 40/41 KDE no FusionOS em poucos minutos:
```bash
sudo ./scripts/fusion-setup.sh
```

### Opção 2: Compilar a Imagem ISO Oficial Bootável
Para gerar o arquivo `.iso` instalável e gravar em pendrive USB:
```bash
sudo ./scripts/build-iso.sh
```
A imagem resultante estará em `output/FusionOS-Live-x86_64.iso`.

---

## 📖 Documentação Detalhada
* [Por que o FusionOS supera Windows e Mac (Proposta de Valor)](docs/VALUE_PROPOSITION.md)
* [Guia Completo de Compilação da ISO](docs/BUILD_ISO.md)
* [Manual do Usuário e Atalhos](docs/USER_GUIDE.md)

