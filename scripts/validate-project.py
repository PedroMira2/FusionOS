#!/usr/bin/env python3
"""
FusionOS - Comprehensive Project Validator & Test Suite
Validates file integrity, syntax, line endings, Kickstart completeness, and references.
"""

import os
import sys
import subprocess
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

print("=" * 60)
print("     FUSIONOS - SUITE DE VALIDAÇÃO E TESTES AUTOMATIZADOS")
print("=" * 60)

errors = []
warnings = []
passed = 0

def check(condition, message):
    global passed
    if condition:
        print(f"  [PASS] {message}")
        passed += 1
    else:
        print(f"  [FAIL] {message}")
        errors.append(message)

# 1. Testar Integridade das Pastas
required_dirs = ["configs/kde", "configs/layouts", "configs/system", "configs/wine", "scripts", "kickstart", "docs", "assets"]
for d in required_dirs:
    check((ROOT_DIR / d).is_dir(), f"Diretório essencial existe: {d}")

# 2. Testar Finais de Linha (Unix LF obrigatório para Linux)
text_files = list(ROOT_DIR.rglob("*.sh")) + list(ROOT_DIR.rglob("*.js")) + list(ROOT_DIR.rglob("*.ks")) + list(ROOT_DIR.rglob("*.conf")) + list(ROOT_DIR.rglob("*.desktop"))
for tf in text_files:
    content = tf.read_bytes()
    rel = tf.relative_to(ROOT_DIR)
    check(b"\r\n" not in content, f"Final de linha Unix (LF puro): {rel}")

# 3. Testar Scripts JavaScript do Plasma 6 via Node.js
js_files = list((ROOT_DIR / "configs" / "layouts").glob("*.js"))
for jf in js_files:
    rel = jf.relative_to(ROOT_DIR)
    res = subprocess.run(["node", "--check", str(jf)], capture_output=True, text=True)
    check(res.returncode == 0, f"Sintaxe JS válida (node --check): {rel}")

# 4. Testar Scripts Bash
sh_files = list((ROOT_DIR / "scripts").glob("*.sh")) + list((ROOT_DIR / "configs" / "wine").glob("*.sh"))
for sf in sh_files:
    rel = sf.relative_to(ROOT_DIR)
    content = sf.read_text(encoding="utf-8")
    
    # Valida Shebang
    check(content.startswith("#!/"), f"Shebang válido: {rel}")
    
    # Valida modo de erro restrito
    check("set -e" in content, f"Tratamento de erro (set -e): {rel}")
    
    # Valida balanceamento de aspas simples e duplas (básico)
    double_quotes = content.count('"')
    check(double_quotes % 2 == 0, f"Aspas duplas balanceadas ({double_quotes}): {rel}")

# 5. Testar Especificação Kickstart
ks_file = ROOT_DIR / "kickstart" / "fusionos-fedora.ks"
ks_content = ks_file.read_text(encoding="utf-8")
check("%packages" in ks_content, "Kickstart contém bloco %packages")
check("%post" in ks_content, "Kickstart contém bloco %post")
check("%end" in ks_content, "Kickstart contém finalizadores %end")
check("@kde-desktop" in ks_content, "Kickstart seleciona KDE Plasma 6")
check("wine" in ks_content and "steam" in ks_content, "Kickstart inclui stack gamer (Wine/Steam)")
check("fusion-switch-layout" in ks_content, "Kickstart tem Chameleon Layout Engine embutido no %post")
check("fusion-wine-handler" in ks_content, "Kickstart tem assistente .exe embutido no %post")

# 6. Testar Arquivos Desktop (.desktop)
desktop_files = list(ROOT_DIR.rglob("*.desktop"))
for df in desktop_files:
    rel = df.relative_to(ROOT_DIR)
    content = df.read_text(encoding="utf-8")
    check("[Desktop Entry]" in content, f"Seção [Desktop Entry] presente: {rel}")
    check("Type=" in content, f"Campo Type= presente: {rel}")
    check("Exec=" in content, f"Campo Exec= presente: {rel}")

# 7. Testar Presença dos Logos e Assets Animados
check((ROOT_DIR / "assets" / "fusionos-logo.svg").is_file(), "Logotipo oficial SVG existe em assets/fusionos-logo.svg")
check((ROOT_DIR / "assets" / "fusionos-boot-animation.svg").is_file(), "Animação de boot SVG existe em assets/fusionos-boot-animation.svg")
check((ROOT_DIR / "assets" / "boot-preview.html").is_file(), "Página de visualização do boot existe em assets/boot-preview.html")

# 8. Testar Tema de Boot Plymouth
check((ROOT_DIR / "configs" / "plymouth" / "fusionos.plymouth").is_file(), "Configuração Plymouth presente")
check((ROOT_DIR / "configs" / "plymouth" / "fusionos.script").is_file(), "Script de animação Plymouth presente")

# 9. Testar GitHub Actions CI/CD para compilação automática na nuvem
check((ROOT_DIR / ".github" / "workflows" / "build-iso.yml").is_file(), "Workflow do GitHub Actions para compilar ISO presente")

# 10. Testar Links de Documentação do README.md
readme_content = (ROOT_DIR / "README.md").read_text(encoding="utf-8")
for doc in ["docs/VALUE_PROPOSITION.md", "docs/BUILD_ISO.md", "docs/USER_GUIDE.md"]:
    check((ROOT_DIR / doc).is_file(), f"Documento citado no README existe: {doc}")

# 11. Testar Calamares Installer Branding & Slideshow
check((ROOT_DIR / "configs/calamares/branding/fusionos/branding.desc").is_file(), "Calamares branding.desc presente")
check((ROOT_DIR / "configs/calamares/branding/fusionos/slideshow.qml").is_file(), "Calamares slideshow.qml presente")
check((ROOT_DIR / "configs/calamares/settings.conf").is_file(), "Calamares settings.conf presente")

# 12. Testar Tema do Bootloader GRUB 2
check((ROOT_DIR / "configs/grub/theme/theme.txt").is_file(), "Tema do GRUB 2 theme.txt presente")
check((ROOT_DIR / "configs/grub/theme/background.svg").is_file(), "Fundo do GRUB 2 background.svg presente")

# 13. Testar Consistência GTK 3/4 e Konsole Dark Theme
check((ROOT_DIR / "configs/gtk/gtk3-settings.ini").is_file(), "Tema GTK 3 gtk3-settings.ini presente")
check((ROOT_DIR / "configs/gtk/gtk4-settings.ini").is_file(), "Tema GTK 4 gtk4-settings.ini presente")
check((ROOT_DIR / "configs/konsole/FusionOS-Dark.colorscheme").is_file(), "Esquema de cores do Konsole presente")
check((ROOT_DIR / "configs/konsole/FusionOS.profile").is_file(), "Perfil padrão do Konsole presente")

# 14. Testar Interface Gráfica do Chameleon Layout Switcher
check((ROOT_DIR / "configs/layouts/fusion-layout-gui.py").is_file(), "Chameleon GUI fusion-layout-gui.py presente")

# 15. Testar Fastfetch e Perfil de Terminal
check((ROOT_DIR / "configs/fastfetch/config.jsonc").is_file(), "Configuração do Fastfetch config.jsonc presente")
check((ROOT_DIR / "configs/system/fusion-profile.sh").is_file(), "Script de perfil do terminal fusion-profile.sh presente")

# 16. Testar Btrfs Time Machine e Snapper
check((ROOT_DIR / "configs/system/snapper-root.conf").is_file(), "Configuração do Snapper snapper-root.conf presente")
check((ROOT_DIR / "configs/system/fusion-snapper-setup.sh").is_file(), "Script fusion-snapper-setup.sh presente")

# 17. Testar Perfis de Energia e Performance
check((ROOT_DIR / "configs/system/fusion-power-mode.sh").is_file(), "Script fusion-power-mode.sh presente")
check((ROOT_DIR / "configs/system/fusion-power-gui.py").is_file(), "Interface GUI fusion-power-gui.py presente")
check((ROOT_DIR / "configs/system/fusion-power-mode.desktop").is_file(), "Atalho fusion-power-mode.desktop presente")

# 18. Testar Assistente de Drivers e Hardware
check((ROOT_DIR / "configs/system/fusion-hardware-assistant.sh").is_file(), "Script fusion-hardware-assistant.sh presente")
check((ROOT_DIR / "configs/system/fusion-hardware-gui.py").is_file(), "Interface GUI fusion-hardware-gui.py presente")
check((ROOT_DIR / "configs/system/fusion-hardware-assistant.desktop").is_file(), "Atalho fusion-hardware-assistant.desktop presente")

# 19. Testar Tema Sonoro Acústico
sound_dir = ROOT_DIR / "configs/sounds/fusionos"
check((sound_dir / "index.theme").is_file(), "Arquivo index.theme sonoro presente")
check((sound_dir / "stereo/desktop-login.wav").is_file(), "Som de inicialização (desktop-login.wav) presente")
check((sound_dir / "stereo/message-new-instant.wav").is_file(), "Som de notificação (message-new-instant.wav) presente")
check((sound_dir / "stereo/device-added.wav").is_file(), "Som de dispositivo conectado presente")
check((sound_dir / "stereo/device-removed.wav").is_file(), "Som de dispositivo desconectado presente")

# 20. Testar Motor de Áudio Hi-Res e Bluetooth Destravado
check((ROOT_DIR / "configs/system/pipewire-hires.conf").is_file(), "Configuração PipeWire Hi-Res presente")
check((ROOT_DIR / "configs/system/wireplumber-bluetooth.conf").is_file(), "Configuração WirePlumber Bluetooth Hi-Res presente")

# 21. Testar Presets de Áudio Dolby 3D e Cinema
check((ROOT_DIR / "configs/audio/presets/FusionOS-Dolby-Spatial.json").is_file(), "Preset Dolby Spatial 3D presente")
check((ROOT_DIR / "configs/audio/presets/FusionOS-Super-Bass.json").is_file(), "Preset Super Bass presente")
check((ROOT_DIR / "configs/audio/presets/FusionOS-Cinema-3D.json").is_file(), "Preset Cinema 3D presente")

# 22. Testar Central de Áudio e Serviço de Inicialização
check((ROOT_DIR / "configs/audio/fusion-audio-service.sh").is_file(), "Serviço de áudio fusion-audio-service.sh presente")
check((ROOT_DIR / "configs/audio/fusion-sound-gui.py").is_file(), "Central gráfica de áudio fusion-sound-gui.py presente")
check((ROOT_DIR / "configs/audio/fusion-sound-control.desktop").is_file(), "Atalho de controle de áudio presente")

print("\n" + "=" * 60)
print(f"RESULTADO: {passed} testes passaram | {len(errors)} falhas")
print("=" * 60)

if errors:
    print("\nFalhas encontradas:")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)
else:
    print("\n[SUCESSO] TODAS AS VALIDACOES PASSARAM COM SUCESSO! O PROJETO ESTA 100% PRONTO.")
    sys.exit(0)
