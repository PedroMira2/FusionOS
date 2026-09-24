#!/usr/bin/env python3
"""
FusionOS - Comprehensive Project Validator & Test Suite
Validates file integrity, syntax, line endings, Kickstart completeness,
desktop entries, and all 20 advanced roadmap features.
"""

import os
import sys
import subprocess
import py_compile
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

print("=" * 65)
print("     FUSIONOS - SUITE DE VALIDAÇÃO E TESTES AUTOMATIZADOS")
print("=" * 65)

errors = []
passed = 0

def check(condition, message):
    global passed
    if condition:
        print(f"  [PASS] {message}")
        passed += 1
    else:
        print(f"  [FAIL] {message}")
        errors.append(message)

# 1. Integridade das Pastas
required_dirs = [
    "configs/kde", "configs/layouts", "configs/system", "configs/wine",
    "configs/gaming", "configs/security", "configs/audio", "configs/sounds",
    "scripts", "kickstart", "docs", "assets", "assets/icons/fusion-glyphs"
]
for d in required_dirs:
    check((ROOT_DIR / d).is_dir(), f"Diretório essencial existe: {d}")

# 2. Finais de Linha Unix (LF puro em todos os arquivos de configuração e scripts)
text_files = (
    list(ROOT_DIR.rglob("*.sh")) + list(ROOT_DIR.rglob("*.js")) +
    list(ROOT_DIR.rglob("*.ks")) + list(ROOT_DIR.rglob("*.conf")) +
    list(ROOT_DIR.rglob("*.desktop")) + list(ROOT_DIR.rglob("*.service")) +
    list(ROOT_DIR.rglob("*.timer")) + list(ROOT_DIR.rglob("*.rules"))
)
for tf in text_files:
    content = tf.read_bytes()
    rel = tf.relative_to(ROOT_DIR)
    check(b"\r\n" not in content, f"Final de linha Unix (LF puro): {rel}")

# 3. Compilação e Sintaxe de TODOS os arquivos Python
py_files = list(ROOT_DIR.rglob("*.py"))
for pf in py_files:
    rel = pf.relative_to(ROOT_DIR)
    try:
        py_compile.compile(str(pf), doraise=True)
        check(True, f"Sintaxe Python válida (py_compile): {rel}")
    except Exception as e:
        check(False, f"Erro de sintaxe Python em {rel}: {e}")

# 4. Scripts JavaScript do Plasma 6 via Node.js
js_files = list((ROOT_DIR / "configs" / "layouts").glob("*.js"))
for jf in js_files:
    rel = jf.relative_to(ROOT_DIR)
    res = subprocess.run(["node", "--check", str(jf)], capture_output=True, text=True)
    check(res.returncode == 0, f"Sintaxe JS válida (node --check): {rel}")

# 5. Validação de Scripts Bash
sh_files = list(ROOT_DIR.rglob("*.sh"))
for sf in sh_files:
    rel = sf.relative_to(ROOT_DIR)
    content = sf.read_text(encoding="utf-8")
    check(content.startswith("#!/"), f"Shebang válido: {rel}")
    if sf.name != "fusion-profile.sh":
        check("set -e" in content, f"Tratamento de erro (set -e): {rel}")

# 6. Validação do Kickstart
ks_file = ROOT_DIR / "kickstart" / "fusionos-fedora.ks"
ks_content = ks_file.read_text(encoding="utf-8")
check("%packages" in ks_content, "Kickstart contém bloco %packages")
check("%post" in ks_content, "Kickstart contém bloco %post")
check("%end" in ks_content, "Kickstart contém finalizadores %end")
check("@kde-desktop" in ks_content, "Kickstart seleciona KDE Plasma 6")
check("wine" in ks_content and "steam" in ks_content, "Kickstart inclui stack gamer (Wine/Steam)")
check("fusion-switch-layout" in ks_content, "Kickstart tem Chameleon Layout Engine embutido")
check("fusion-gamebar" in ks_content, "Kickstart inclui Fusion Game Bar no %post")
check("fusion-runner-hub" in ks_content, "Kickstart inclui Fusion Runner Hub no %post")
check("fusion-quicklook" in ks_content, "Kickstart inclui QuickLook no %post")
check("fusion-control-center" in ks_content, "Kickstart inclui Control Center no %post")
check("fusion-vault" in ks_content, "Kickstart inclui Fusion Vault no %post")
check("fusion-shield" in ks_content, "Kickstart inclui Fusion Shield no %post")
check("fusion-permissions" in ks_content, "Kickstart inclui Flatpak Permissions no %post")
check("fusion-time-capsule" in ks_content, "Kickstart inclui Time Capsule no %post")
check("fusion-battery-switch" in ks_content, "Kickstart inclui Battery Switcher no %post")
check("fusion-auto-update" in ks_content, "Kickstart inclui Silent Updates no %post")

# 7. Validação de Arquivos .desktop
desktop_files = list(ROOT_DIR.rglob("*.desktop"))
for df in desktop_files:
    rel = df.relative_to(ROOT_DIR)
    content = df.read_text(encoding="utf-8")
    check("[Desktop Entry]" in content, f"Desktop Entry presente: {rel}")
    check("Type=" in content, f"Campo Type= presente: {rel}")
    check("Exec=" in content, f"Campo Exec= presente: {rel}")

# 8. Branding e Identidade Visual (Logos e Animação)
check((ROOT_DIR / "assets" / "fusionos-logo.svg").is_file(), "Logotipo oficial SVG existe")
check((ROOT_DIR / "assets" / "fusionos-boot-animation.svg").is_file(), "Animação de boot SVG existe")
check((ROOT_DIR / "configs" / "plymouth" / "fusionos.plymouth").is_file(), "Plymouth .plymouth presente")
check((ROOT_DIR / "configs" / "plymouth" / "fusionos.script").is_file(), "Plymouth .script presente")

# 9. Calamares Installer Branding & Slideshow
check((ROOT_DIR / "configs/calamares/branding/fusionos/branding.desc").is_file(), "Calamares branding.desc presente")
check((ROOT_DIR / "configs/calamares/branding/fusionos/slideshow.qml").is_file(), "Calamares slideshow.qml presente")
check((ROOT_DIR / "configs/calamares/settings.conf").is_file(), "Calamares settings.conf presente")

# 10. GRUB 2 Bootloader Theme
check((ROOT_DIR / "configs/grub/theme/theme.txt").is_file(), "Tema GRUB 2 theme.txt presente")
check((ROOT_DIR / "configs/grub/theme/background.svg").is_file(), "Fundo GRUB 2 background.svg presente")

# 11. GTK 3/4 e Konsole Theme
check((ROOT_DIR / "configs/gtk/gtk3-settings.ini").is_file(), "Tema GTK 3 presente")
check((ROOT_DIR / "configs/gtk/gtk4-settings.ini").is_file(), "Tema GTK 4 presente")
check((ROOT_DIR / "configs/konsole/FusionOS-Dark.colorscheme").is_file(), "Cores Konsole presentes")
check((ROOT_DIR / "configs/konsole/FusionOS.profile").is_file(), "Perfil Konsole presente")

# 12. Áudio Hi-Res 384kHz, Bluetooth e Dolby Atmos DSP
check((ROOT_DIR / "configs/system/pipewire-hires.conf").is_file(), "PipeWire Hi-Res 384kHz conf presente")
check((ROOT_DIR / "configs/system/wireplumber-bluetooth.conf").is_file(), "WirePlumber Bluetooth LDAC/aptX presente")
check((ROOT_DIR / "configs/audio/presets/FusionOS-Dolby-Spatial.json").is_file(), "Preset Dolby Spatial 3D presente")
check((ROOT_DIR / "configs/audio/presets/FusionOS-Super-Bass.json").is_file(), "Preset Super Bass presente")
check((ROOT_DIR / "configs/audio/presets/FusionOS-Cinema-3D.json").is_file(), "Preset Cinema 3D presente")
check((ROOT_DIR / "configs/audio/fusion-audio-service.sh").is_file(), "Serviço fusion-audio-service.sh presente")
check((ROOT_DIR / "configs/audio/fusion-sound-gui.py").is_file(), "Central gráfica fusion-sound-gui.py presente")

# 13. Tema Sonoro Acústico
sound_dir = ROOT_DIR / "configs/sounds/fusionos"
check((sound_dir / "index.theme").is_file(), "Arquivo index.theme sonoro presente")
check((sound_dir / "stereo/desktop-login.wav").is_file(), "Som desktop-login.wav presente")
check((sound_dir / "stereo/message-new-instant.wav").is_file(), "Som message-new-instant.wav presente")
check((sound_dir / "stereo/device-added.wav").is_file(), "Som device-added.wav presente")
check((sound_dir / "stereo/device-removed.wav").is_file(), "Som device-removed.wav presente")

# 14. Validação das 20 Melhorias do Roadmap:
# Grupo 1: Jogos
check((ROOT_DIR / "configs/gaming/fusion-gamebar.py").is_file(), "Item 1: Game Bar GUI presente")
check((ROOT_DIR / "configs/gaming/fusion-gamebar.desktop").is_file(), "Item 1: Game Bar Desktop Entry presente")
check((ROOT_DIR / "configs/gaming/fusion-clip-record.sh").is_file(), "Item 2: Clip Recorder script presente")
check((ROOT_DIR / "configs/gaming/fusion-runner-hub.py").is_file(), "Item 3: Fusion Runner Hub GUI presente")
check((ROOT_DIR / "configs/gaming/fusion-runner-hub.desktop").is_file(), "Item 3: Fusion Runner Hub Desktop Entry presente")

kwinrc_content = (ROOT_DIR / "configs/kde/kwinrc").read_text(encoding="utf-8")
check("AdaptiveSync=always" in kwinrc_content and "AllowTearing=true" in kwinrc_content, "Item 4: Auto-VRR & Low Latency configurado no kwinrc")

# Grupo 2: Produtividade
check((ROOT_DIR / "configs/system/fusion-quicklook.py").is_file(), "Item 5: QuickLook GUI presente")
check((ROOT_DIR / "configs/system/fusion-quicklook.desktop").is_file(), "Item 5: QuickLook Desktop Entry presente")
check("[ElectricBorders]" in kwinrc_content and "TopLeft=Overview" in kwinrc_content, "Item 6: Hot Corners configurado no kwinrc")
check((ROOT_DIR / "configs/kde/klipperrc").is_file(), "Item 7: ClipVault klipperrc presente")
check("MaxClipItems=50" in (ROOT_DIR / "configs/kde/klipperrc").read_text(encoding="utf-8"), "Item 7: ClipVault 50 itens configurado")
check("WindowSnapZone=12" in kwinrc_content and "BorderSnapZone=12" in kwinrc_content, "Item 8: Smart Window Snapping configurado")

# Grupo 3: Design & UI
check((ROOT_DIR / "configs/system/fusion-dynamic-wallpaper.sh").is_file(), "Item 9: Dynamic Wallpaper script presente")
check((ROOT_DIR / "configs/system/fusion-dynamic-wallpaper.service").is_file(), "Item 9: Dynamic Wallpaper service presente")
check((ROOT_DIR / "configs/system/fusion-dynamic-wallpaper.timer").is_file(), "Item 9: Dynamic Wallpaper timer presente")
check((ROOT_DIR / "configs/system/fusion-control-center.py").is_file(), "Item 10: Control Center GUI presente")
check((ROOT_DIR / "configs/system/fusion-control-center.desktop").is_file(), "Item 10: Control Center Desktop Entry presente")

glyph_icons = list((ROOT_DIR / "assets/icons/fusion-glyphs/scalable/apps").glob("*.svg"))
check(len(glyph_icons) >= 10, f"Item 11: Fusion Glyphs contém {len(glyph_icons)} ícones SVG escaláveis")
check((ROOT_DIR / "assets/icons/fusion-glyphs/index.theme").is_file(), "Item 11: Fusion Glyphs index.theme presente")

check((ROOT_DIR / "configs/system/fusion-focus-mode.sh").is_file(), "Item 12: Focus Mode script presente")
check((ROOT_DIR / "configs/system/fusion-focus-mode.desktop").is_file(), "Item 12: Focus Mode Desktop Entry presente")

# Grupo 4: Segurança & Privacidade
check((ROOT_DIR / "configs/security/fusion-vault.sh").is_file(), "Item 13: Fusion Vault script presente")
check((ROOT_DIR / "configs/security/fusion-vault-gui.py").is_file(), "Item 13: Fusion Vault GUI presente")
check((ROOT_DIR / "configs/security/fusion-vault.desktop").is_file(), "Item 13: Fusion Vault Desktop Entry presente")

check((ROOT_DIR / "configs/security/fusion-shield.py").is_file(), "Item 14: Fusion Shield GUI presente")
check((ROOT_DIR / "configs/security/fusion-shield.desktop").is_file(), "Item 14: Fusion Shield Desktop Entry presente")

check((ROOT_DIR / "configs/security/fusion-permissions.py").is_file(), "Item 15: Flatpak Permissions GUI presente")
check((ROOT_DIR / "configs/security/fusion-permissions.desktop").is_file(), "Item 15: Flatpak Permissions Desktop Entry presente")

check((ROOT_DIR / "configs/security/fusion-time-capsule.sh").is_file(), "Item 16: Time Capsule script presente")
check((ROOT_DIR / "configs/security/fusion-time-capsule-gui.py").is_file(), "Item 16: Time Capsule GUI presente")
check((ROOT_DIR / "configs/security/fusion-time-capsule.desktop").is_file(), "Item 16: Time Capsule Desktop Entry presente")

# Grupo 5: Sistema & Hardware
check((ROOT_DIR / "configs/system/fusion-battery-switch.sh").is_file(), "Item 17: Battery Switcher script presente")
check((ROOT_DIR / "configs/system/99-fusion-battery.rules").is_file(), "Item 17: Battery Switcher udev rule presente")

check((ROOT_DIR / "configs/system/fusion-focus-scheduler.sh").is_file(), "Item 18: Focus Scheduler script presente")
check((ROOT_DIR / "configs/system/fusion-focus-scheduler.service").is_file(), "Item 18: Focus Scheduler service presente")

check("[NightColor]" in kwinrc_content and "NightTemperature=3800" in kwinrc_content, "Item 19: Night Light 3800K configurado no kwinrc")

check((ROOT_DIR / "configs/system/fusion-auto-update.sh").is_file(), "Item 20: Auto Update script presente")
check((ROOT_DIR / "configs/system/fusion-auto-update.service").is_file(), "Item 20: Auto Update service presente")
check((ROOT_DIR / "configs/system/fusion-auto-update.timer").is_file(), "Item 20: Auto Update timer presente")

# Grupo 6: Pro Suite (Flagship Additions)
check((ROOT_DIR / "configs/audio/fusion-crisp-mic.sh").is_file(), "Pro 1: Crisp Mic script presente")
check((ROOT_DIR / "configs/audio/pipewire-crisp-mic.conf").is_file(), "Pro 1: Crisp Mic PipeWire conf presente")
autoeq_profiles = list((ROOT_DIR / "configs/audio/eq-profiles").glob("*.json"))
check(len(autoeq_profiles) >= 6, f"Pro 2: AutoEQ contém {len(autoeq_profiles)} perfis de fones de ouvido")

check((ROOT_DIR / "configs/system/fusion-lens.py").is_file(), "Pro 3: Fusion Lens OCR GUI presente")
check((ROOT_DIR / "configs/system/fusion-lens.desktop").is_file(), "Pro 3: Fusion Lens Desktop Entry presente")

check((ROOT_DIR / "configs/system/fusion-color-picker.py").is_file(), "Pro 4: Color Picker GUI presente")
check((ROOT_DIR / "configs/system/fusion-color-picker.desktop").is_file(), "Pro 4: Color Picker Desktop Entry presente")

check((ROOT_DIR / "configs/system/fusion-cloud-connect.sh").is_file(), "Pro 5: Cloud Connect script presente")
check((ROOT_DIR / "configs/system/fusion-cloud-connect.py").is_file(), "Pro 5: Cloud Connect GUI presente")
check((ROOT_DIR / "configs/system/fusion-cloud-connect.desktop").is_file(), "Pro 5: Cloud Connect Desktop Entry presente")

check((ROOT_DIR / "configs/software/fusion-software-hub.py").is_file(), "Pro 6: Software Hub GUI presente")
check((ROOT_DIR / "configs/software/fusion-software-hub.desktop").is_file(), "Pro 6: Software Hub Desktop Entry presente")

check((ROOT_DIR / "configs/system/fusion-waydroid-setup.sh").is_file(), "Pro 7: Android Subsystem script presente")
check((ROOT_DIR / "configs/system/fusion-waydroid-gui.py").is_file(), "Pro 7: Android Subsystem GUI presente")
check((ROOT_DIR / "configs/system/fusion-waydroid.desktop").is_file(), "Pro 7: Android Subsystem Desktop Entry presente")

check((ROOT_DIR / "configs/system/fusion-hdr-assistant.py").is_file(), "Pro 8: HDR Studio GUI presente")
check((ROOT_DIR / "configs/system/fusion-hdr-assistant.desktop").is_file(), "Pro 8: HDR Studio Desktop Entry presente")

check((ROOT_DIR / "configs/system/fusion-cast.py").is_file(), "Pro 9: Fusion Cast GUI presente")
check((ROOT_DIR / "configs/system/fusion-cast.desktop").is_file(), "Pro 9: Fusion Cast Desktop Entry presente")

check((ROOT_DIR / "configs/system/fusion-devbox.py").is_file(), "Pro 10: Fusion DevBox GUI presente")
check((ROOT_DIR / "configs/system/fusion-devbox.desktop").is_file(), "Pro 10: Fusion DevBox Desktop Entry presente")

check((ROOT_DIR / "configs/kde/yakuakerc").is_file(), "Pro 11: Yakuake Quake HUD terminal conf presente")
check(len(glyph_icons) >= 20, f"Ícones Fusion Glyphs expandidos para {len(glyph_icons)} SVGs")

# Grupo 7: Otimizações Extremas & 4 Modos Dedicados
power_sh = (ROOT_DIR / "configs/system/fusion-power-mode.sh").read_text(encoding="utf-8")
for m in ["powersave", "multitask", "performance", "gaming"]:
    check(m in power_sh, f"Perfil de energia dedicado presente: {m}")

check((ROOT_DIR / "configs/wine/dxvk.conf").is_file(), "DXVK config presente")
check("dxvk.enableAsync = true" in (ROOT_DIR / "configs/wine/dxvk.conf").read_text(encoding="utf-8"), "DXVK compilação assíncrona ativa (Zero Stutter)")

check((ROOT_DIR / "configs/system/60-fusion-iosched.rules").is_file(), "Regras udev de scheduler I/O para NVMe/SSDs presentes")
check((ROOT_DIR / "configs/system/fusion-speed.conf").is_file(), "Configuração systemd de boot/shutdown instantâneo presente")
check((ROOT_DIR / "configs/system/fusion-environment.conf").is_file(), "Variáveis globais de aceleração e Wayland nativo presentes")
check((ROOT_DIR / "configs/system/99-fusion-limits.conf").is_file(), "Limites de processo expandidos (nofile 1048576) presentes")

check((ROOT_DIR / "configs/system/fusion-turbo-gui.py").is_file(), "Fusion Turbo Center GUI presente")
check((ROOT_DIR / "configs/system/fusion-turbo.desktop").is_file(), "Fusion Turbo Center Desktop Entry presente")

print("\n" + "=" * 65)
print(f"RESULTADO: {passed} testes passaram | {len(errors)} falhas")
print("=" * 65)

if errors:
    print("\nFalhas encontradas:")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)
else:
    print("\n[SUCESSO] TODAS AS MELHORIAS E OTIMIZACOES FORAM VALIDADAS COM 0 ERROS!")
    sys.exit(0)
