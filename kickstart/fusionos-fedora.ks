# ==============================================================================
# FusionOS Live ISO Kickstart Specification (Fedora 40/41 KDE Base)
# Proposito: Define todos os pacotes, repositorios e configuracoes para gerar a ISO
# 100% Auto-contido e pronto para o livemedia-creator
# ==============================================================================

# Informacoes Basicas e Localizacao
lang pt_BR.UTF-8
keyboard br-abnt2
timezone America/Sao_Paulo --utc
selinux --enforcing
firewall --enabled --service=mdns

# Autenticacao e Bootloader Obrigatorios
rootpw --lock
bootloader --location=none
zerombr
clearpart --all

# Particionamento do Sistema Live
part / --size 12288 --fstype ext4

# Repositorios Oficiais do Fedora e RPM Fusion (usando $releasever dinâmico)
url --url="https://dl.fedoraproject.org/pub/fedora/linux/releases/$releasever/Everything/x86_64/os/" --mirrorlist="https://mirrors.fedoraproject.org/mirrorlist?repo=fedora-$releasever&arch=x86_64"
repo --name=fedora --mirrorlist="https://mirrors.fedoraproject.org/mirrorlist?repo=fedora-$releasever&arch=x86_64"
repo --name=updates --mirrorlist="https://mirrors.fedoraproject.org/mirrorlist?repo=updates-released-f$releasever&arch=x86_64"
repo --name=rpmfusion-free --mirrorlist="https://mirrors.rpmfusion.org/mirrorlist?repo=free-fedora-$releasever&arch=x86_64"
repo --name=rpmfusion-free-updates --mirrorlist="https://mirrors.rpmfusion.org/mirrorlist?repo=free-fedora-updates-released-f$releasever&arch=x86_64"
repo --name=rpmfusion-nonfree --mirrorlist="https://mirrors.rpmfusion.org/mirrorlist?repo=nonfree-fedora-$releasever&arch=x86_64"
repo --name=rpmfusion-nonfree-updates --mirrorlist="https://mirrors.rpmfusion.org/mirrorlist?repo=nonfree-fedora-updates-released-f$releasever&arch=x86_64"

# Selecao de Pacotes da Imagem
%packages
# 0. Bootloader, Kernel e Suporte Live Obrigatorios
kernel
kernel-modules
dracut-live
dracut-config-generic
grub2-efi-x64
shim-x64
grub2-pc
grub2-pc-modules
grub2-tools
grub2-tools-extra
isolinux
syslinux

# 1. Base KDE Plasma 6
@kde-desktop
@multimedia
plasma-desktop
plasma-workspace
plasma-workspace-wayland
kwin
kwin-wayland
dolphin
konsole
krunner
kdialog
zenity

# 2. Fontes e Renderizacao de Nivel Superior
rsms-inter-fonts
google-noto-sans-fonts
fira-code-fonts

# 3. Audio Studio-Grade e Codecs
pipewire
pipewire-pulseaudio
pipewire-alsa
wireplumber
gstreamer1-plugins-good
gstreamer1-plugins-bad-freeworld
gstreamer1-plugins-ugly
gstreamer1-libav
ffmpeg

# 4. Compatibilidade Gamer & Windows
wine
winetricks
steam
gamemode
mangohud
vulkan-loader
mesa-vulkan-drivers
mesa-va-drivers

# 5. Sistema e Resiliencia
snapper
btrfs-assistant
zram-generator
flatpak
liveusb-creator
calamares

# Remocoes para manter o sistema limpo e leve (zero bloatware)
-gnome-boxes
-kmail
-korganizer
-kaddressbook
%end

# Configuracoes de Pos-Instalacao do Live Environment
%post
# 1. Habilita Flathub Oficial Completo
flatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo

# 2. Ativa o servico de ZRAM
systemctl enable systemd-zram-setup@zram0.service

# 3. Otimizacoes de kernel de baixa latencia e jogos no Live System
cat <<'EOF' > /etc/sysctl.d/99-fusion-performance.conf
vm.max_map_count = 2147483642
vm.swappiness = 10
vm.vfs_cache_pressure = 50
vm.dirty_background_ratio = 5
vm.dirty_ratio = 10
fs.file-max = 2097152
fs.inotify.max_user_watches = 524288
net.core.default_qdisc = cake
net.ipv4.tcp_congestion_control = bbr
net.ipv4.tcp_fastopen = 3
EOF

# 4. Audio de Baixa Latencia PipeWire
mkdir -p /etc/pipewire/pipewire.conf.d/
cat <<'EOF' > /etc/pipewire/pipewire.conf.d/99-lowlatency.conf
context.properties = {
    default.clock.rate          = 48000
    default.clock.allowed-rates = [ 44100 48000 88200 96000 192000 ]
    default.clock.quantum       = 256
    default.clock.min-quantum   = 64
    default.clock.max-quantum   = 1024
}
EOF

# 5. Criando Diretorios do FusionOS
mkdir -p /usr/share/fusionos/layouts
mkdir -p /usr/local/bin

# 6. Injetando Layouts Plasma 6 (Mac, Windows 11 e Gamer)
cat <<'EOF' > /usr/share/fusionos/layouts/layout-macos.js
var allPanels = panels();
for (var i = 0; i < allPanels.length; i++) {
    allPanels[i].remove();
}
var topBar = new Panel();
topBar.location = "top";
topBar.height = 28;
topBar.alignment = "center";
topBar.floating = false;
topBar.addWidget("org.kde.plasma.kickoff");
topBar.addWidget("org.kde.plasma.appmenu");
topBar.addWidget("org.kde.plasma.panelspacer");
var clock = topBar.addWidget("org.kde.plasma.digitalclock");
clock.currentConfigGroup = ["Appearance"];
clock.writeConfig("showDate", "true");
clock.writeConfig("dateFormat", "shortDate");
topBar.addWidget("org.kde.plasma.panelspacer");
topBar.addWidget("org.kde.plasma.systemtray");

var dock = new Panel();
dock.location = "bottom";
dock.height = 54;
dock.alignment = "center";
dock.floating = true;
dock.hiding = "windowscover";
var taskManager = dock.addWidget("org.kde.plasma.icontasks");
taskManager.currentConfigGroup = ["General"];
taskManager.writeConfig("launchers", [
    "applications:org.kde.dolphin.desktop",
    "applications:org.mozilla.firefox.desktop",
    "applications:com.heroicgameslauncher.hgl.desktop",
    "applications:steam.desktop",
    "applications:org.kde.discover.desktop",
    "applications:org.kde.konsole.desktop",
    "applications:fusion-layout-switcher.desktop"
]);
dock.addWidget("org.kde.plasma.trash");
EOF

cat <<'EOF' > /usr/share/fusionos/layouts/layout-win11.js
var allPanels = panels();
for (var i = 0; i < allPanels.length; i++) {
    allPanels[i].remove();
}
var winPanel = new Panel();
winPanel.location = "bottom";
winPanel.height = 44;
winPanel.floating = true;
winPanel.addWidget("org.kde.plasma.panelspacer");
winPanel.addWidget("org.kde.plasma.kickoff");
winPanel.addWidget("org.kde.plasma.krunner");
winPanel.addWidget("org.kde.plasma.pager");
var taskManager = winPanel.addWidget("org.kde.plasma.icontasks");
taskManager.currentConfigGroup = ["General"];
taskManager.writeConfig("launchers", [
    "applications:org.kde.dolphin.desktop",
    "applications:org.mozilla.firefox.desktop",
    "applications:com.heroicgameslauncher.hgl.desktop",
    "applications:steam.desktop",
    "applications:org.kde.discover.desktop",
    "applications:org.kde.konsole.desktop",
    "applications:fusion-layout-switcher.desktop"
]);
winPanel.addWidget("org.kde.plasma.panelspacer");
winPanel.addWidget("org.kde.plasma.systemtray");
var clock = winPanel.addWidget("org.kde.plasma.digitalclock");
clock.currentConfigGroup = ["Appearance"];
clock.writeConfig("showDate", "true");
clock.writeConfig("dateFormat", "shortDate");
winPanel.addWidget("org.kde.plasma.showdesktop");
EOF

cat <<'EOF' > /usr/share/fusionos/layouts/layout-gamer.js
var allPanels = panels();
for (var i = 0; i < allPanels.length; i++) {
    allPanels[i].remove();
}
var gamerDock = new Panel();
gamerDock.location = "bottom";
gamerDock.height = 42;
gamerDock.alignment = "center";
gamerDock.floating = true;
gamerDock.hiding = "autohide";
var taskManager = gamerDock.addWidget("org.kde.plasma.icontasks");
taskManager.currentConfigGroup = ["General"];
taskManager.writeConfig("launchers", [
    "applications:com.heroicgameslauncher.hgl.desktop",
    "applications:steam.desktop",
    "applications:org.mozilla.firefox.desktop",
    "applications:org.kde.dolphin.desktop",
    "applications:fusion-layout-switcher.desktop"
]);
gamerDock.addWidget("org.kde.plasma.systemtray");
EOF

# 7. Injetando o Alternador de Layout
cat <<'EOF' > /usr/local/bin/fusion-switch-layout
#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="/usr/share/fusionos/layouts"
TARGET_MODE="${1:-}"
if [[ -z "$TARGET_MODE" ]]; then
    if command -v kdialog >/dev/null 2>&1; then
        TARGET_MODE=$(kdialog --title "FusionOS - Personalizar Layout" \
            --radiolist "Escolha a aparencia que mais combina com seu estilo:" \
            "macos" "Estilo Mac (Barra Superior + Dock Flutuante Translúcido)" on \
            "win11" "Estilo Windows 11 (Barra de Tarefas Centralizada Familiar)" off \
            "gamer" "Estilo Gamer / Foco (Ultra Imersivo com Auto-Ocultação)" off 2>/dev/null)
    elif command -v zenity >/dev/null 2>&1; then
        TARGET_MODE=$(zenity --list --radiolist --title="FusionOS - Personalizar Layout" \
            --column="Selecionar" --column="ID" --column="Estilo" \
            TRUE "macos" "Estilo Mac (Barra Superior + Dock Flutuante)" \
            FALSE "win11" "Estilo Windows 11 (Barra Centralizada)" \
            FALSE "gamer" "Estilo Gamer / Foco (Imersao Total)" 2>/dev/null)
    else
        exit 1
    fi
fi
[[ -z "$TARGET_MODE" ]] && exit 0
LAYOUT_FILE="${SCRIPT_DIR}/layout-${TARGET_MODE}.js"
[[ ! -f "$LAYOUT_FILE" ]] && exit 1
JS_CODE=$(cat "$LAYOUT_FILE")
if command -v qdbus-qt6 >/dev/null 2>&1; then
    qdbus-qt6 org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript "$JS_CODE" >/dev/null 2>&1 || true
elif command -v qdbus >/dev/null 2>&1; then
    qdbus org.kde.plasmashell /PlasmaShell evaluateScript "$JS_CODE" >/dev/null 2>&1 || true
fi
notify-send "FusionOS" "Layout alterado com sucesso!" --icon=preferences-desktop-theme 2>/dev/null || true
EOF
chmod +x /usr/local/bin/fusion-switch-layout

# 8. Injetando o Handler de Aplicativos Windows (.exe / .msi)
cat <<'EOF' > /usr/local/bin/fusion-wine-handler
#!/usr/bin/env bash
set -euo pipefail
FILE_PATH="${1:-}"
[[ -z "$FILE_PATH" || ! -f "$FILE_PATH" ]] && exit 1
BASENAME=$(basename "$FILE_PATH")
CHOICE=""
if command -v kdialog >/dev/null 2>&1; then
    CHOICE=$(kdialog --title "FusionOS Windows Launcher - $BASENAME" \
        --radiolist "Como deseja executar '$BASENAME'?" \
        1 "Executar com Wine Direto (Mais rapido e simples)" on \
        2 "Abrir no Bottles (Ambiente isolado em container - Seguro)" off \
        3 "Abrir no Heroic Games (Se for instalador de jogos Epic/GOG)" off 2>/dev/null)
else
    CHOICE="1"
fi
case "$CHOICE" in
    1|"1")
        export WINEPREFIX="${HOME}/.wine"
        export WINEARCH="win64"
        wine "$FILE_PATH" &
        ;;
    2|"2")
        flatpak run com.usebottles.bottles -e "$FILE_PATH" 2>/dev/null || wine "$FILE_PATH" &
        ;;
    3|"3")
        flatpak run com.heroicgameslauncher.hgl 2>/dev/null || wine "$FILE_PATH" &
        ;;
    *)
        exit 0
        ;;
esac
EOF
chmod +x /usr/local/bin/fusion-wine-handler

# 9. Injetando Desktop Launchers
cat <<'EOF' > /usr/share/applications/fusion-layout-switcher.desktop
[Desktop Entry]
Type=Application
Name=FusionOS Layout Switcher
Name[pt_BR]=Alternador de Estilo FusionOS
Comment=Mude instantaneamente entre estilo Mac, Windows 11 e Gamer
Exec=/usr/local/bin/fusion-switch-layout
Icon=preferences-desktop-theme
Terminal=false
Categories=Settings;DesktopSettings;Qt;KDE;
StartupNotify=true
EOF

cat <<'EOF' > /usr/share/applications/fusion-exe-runner.desktop
[Desktop Entry]
Type=Application
Name=FusionOS Windows App Launcher
Name[pt_BR]=Executador de Aplicativos Windows do FusionOS
Comment=Execute programas e instaladores do Windows (.exe / .msi)
Exec=/usr/local/bin/fusion-wine-handler %f
Icon=application-x-ms-dos-executable
Terminal=false
MimeType=application/x-ms-dos-executable;application/x-msdownload;application/x-msi;
Categories=Utility;System;
StartupNotify=true
EOF
update-desktop-database /usr/share/applications || true

# 10. Cria o usuario padrao Live com privilegios
useradd -m -c "FusionOS Live User" -G wheel liveuser
passwd -d liveuser >/dev/null

# 11. Habilita o login automatico no SDDM
cat <<'EOF' > /etc/sddm.conf.d/autologin.conf
[Autologin]
User=liveuser
Session=plasmawayland
EOF

# 12. Pre-configura atalhos (Win+E, Win+V, Alt+Espaco) para o liveuser
mkdir -p /home/liveuser/.config
cat <<'EOF' > /home/liveuser/.config/kglobalshortcutsrc
[krunner.desktop]
_k_friendly_name=Busca Global Spotlight
run-command=Alt+Space; Meta+Space

[org.kde.dolphin.desktop]
_k_friendly_name=Explorador de Arquivos
_launch=Meta+E

[kded6]
_k_friendly_name=Daemon do KDE
show-on-mouse-pos=Meta+V

[kwin]
_k_friendly_name=Gerenciador de Janelas KWin
Overview=Meta+Tab
Window Quick Tile Left=Meta+Left
Window Quick Tile Right=Meta+Right
Window Maximize=Meta+Up
Window Minimize=Meta+Down
Walk Through Windows=Alt+Tab
Lock Session=Meta+L
EOF

chown -R liveuser:liveuser /home/liveuser

echo "FusionOS Kickstart Post-Install 100% Configurado!"
%end
