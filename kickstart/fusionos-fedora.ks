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
network --bootproto=dhcp --device=link --activate

# Autenticacao e Bootloader Obrigatorios
rootpw --lock
bootloader --location=none
zerombr
clearpart --all

# Particionamento do Sistema Live (11GB)
part / --size 11000 --fstype ext4

# Repositorios Oficiais do Fedora 41
url --metalink="https://mirrors.fedoraproject.org/metalink?repo=fedora-41&arch=x86_64"
repo --name=fedora --metalink="https://mirrors.fedoraproject.org/metalink?repo=fedora-41&arch=x86_64"
repo --name=updates --metalink="https://mirrors.fedoraproject.org/metalink?repo=updates-released-f41&arch=x86_64"
repo --name=rpmfusion-free --metalink="https://mirrors.rpmfusion.org/metalink?repo=free-fedora-41&arch=x86_64"
repo --name=rpmfusion-free-updates --metalink="https://mirrors.rpmfusion.org/metalink?repo=free-fedora-updates-released-41&arch=x86_64"
repo --name=rpmfusion-nonfree --metalink="https://mirrors.rpmfusion.org/metalink?repo=nonfree-fedora-41&arch=x86_64"
repo --name=rpmfusion-nonfree-updates --metalink="https://mirrors.rpmfusion.org/metalink?repo=nonfree-fedora-updates-released-41&arch=x86_64"

# Selecao de Pacotes
%packages --ignoremissing
# 0. Base
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
syslinux

# 1. Desktop & UI
@kde-desktop
@multimedia
plasma-desktop
plasma-workspace
plasma-workspace-wayland
sddm
sddm-wayland-plasma
sddm-kcm
kwin
kwin-wayland
dolphin
konsole
krunner
kdialog
zenity

# 2. Branding & Live Environment
python3-pyqt6
python3-pip
plymouth
plymouth-plugin-script
plymouth-theme-spinner
grub2-efi-x64-cdboot
librsvg2-tools
calamares

# 3. Audio & Fonts
rsms-inter-fonts
google-noto-sans-fonts
fira-code-fonts
pipewire
pipewire-pulseaudio
pipewire-alsa
wireplumber
gstreamer1-plugins-good
gstreamer1-plugins-bad-freeworld
gstreamer1-plugins-ugly
gstreamer1-libav
ffmpeg

# 4. System & Compatibility
wine
winetricks
steam
gamemode
mangohud
vulkan-loader
mesa-vulkan-drivers
mesa-va-drivers
snapper
btrfs-assistant
zram-generator
flatpak

# Remocoes de Bloatware
-gnome-boxes
-kmail
-korganizer
-kaddressbook
-plasma-desktop-doc
-gawk-all-langpacks
-qcom-wwan-firmware
-nxpwireless-firmware
-tiwilink-firmware
-cirrus-audio-firmware
-mellanox-firmware
-dracut-config-rescue

# 5. UI Premium & Redesign Components
kvantum
kvantum-qt5
# Fontes premium
rsms-inter-fonts
google-noto-sans-fonts
google-noto-emoji-fonts
fira-code-fonts
# Suporte a SDDM theme QML
qt6-qtdeclarative
qt6-qtquickcontrols2
# Blur e efeitos Wayland
qt5-qtgraphicaleffects
# KDE extras para dock flutuante
plasma-systemmonitor
kde-gtk-config
breeze-gtk
klassy
# Ferramentas de aparência e terminal
plasma-lookandfeel-tools
fastfetch

# 6. Audio Hi-Res, Bluetooth Destravado, Hardware & Performance
pciutils
power-profiles-daemon
python3-dnf-plugin-snapper
libcanberra
sound-theme-freedesktop
easyeffects
pipewire-codec-aptx
libfreeaptx
kde-connect
kde-connect-libs
brightnessctl
wf-recorder
rsync
gocryptfs
rclone
yakuake
tesseract
tesseract-langpack-por
tesseract-langpack-eng
%end


# Copiar arquivos do repositório host para dentro da ISO
%post --nochroot
echo "Sincronizando arquivos do repositorio para dentro da ISO..."
if [ -d "/home/testes/FusionOS" ]; then
    REPO="/home/testes/FusionOS"
elif [ -n "$GITHUB_WORKSPACE" ]; then
    REPO="$GITHUB_WORKSPACE"
else
    REPO=$(pwd)
fi
mkdir -p $INSTALL_ROOT/usr/share/fusionos/repo
cp -r $REPO/configs $INSTALL_ROOT/usr/share/fusionos/repo/ || true
cp -r $REPO/assets $INSTALL_ROOT/usr/share/fusionos/repo/ || true
cp -r $REPO/scripts $INSTALL_ROOT/usr/share/fusionos/repo/ || true
%end


# Configuracoes Internas do Live OS - REDESIGN PREMIUM
%post
# ==================================================================
# 1. Utilizador Live e Permissoes (CRITICO: sudo sem senha)
# ==================================================================
useradd -m -c "FusionOS Live User" -G wheel liveuser
passwd -d liveuser >/dev/null
echo "liveuser ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/liveuser
chmod 0440 /etc/sudoers.d/liveuser

# ==================================================================
# 2. SDDM - Autologin + Tema FusionOS Premium
# ==================================================================
mkdir -p /etc/sddm.conf.d

cat <<'EOF' > /etc/sddm.conf.d/fusionos.conf
[Autologin]
User=liveuser
Session=plasmawayland

[Theme]
Current=fusionos-login
Font=Inter

[General]
DisplayServer=wayland
GreetDelay=0
EOF

# Instalar tema SDDM
mkdir -p /usr/share/sddm/themes/fusionos-login
cp -r /usr/share/fusionos/repo/configs/sddm/fusionos-login/* /usr/share/sddm/themes/fusionos-login/ 2>/dev/null || true

systemctl enable sddm
systemctl set-default graphical.target

# ==================================================================
# 3. Flathub (repositorio de apps)
# ==================================================================
flatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo

# ==================================================================
# 4. Plymouth - Animacao de Boot Premium FusionOS
# ==================================================================
mkdir -p /usr/share/plymouth/themes/fusionos
cp -r /usr/share/fusionos/repo/configs/plymouth/* /usr/share/plymouth/themes/fusionos/ 2>/dev/null || true
cp /usr/share/fusionos/repo/assets/fusionos-logo.svg /usr/share/plymouth/themes/fusionos/ 2>/dev/null || true

# Converter SVG para PNG (logo quadrado para Plymouth)
if command -v rsvg-convert >/dev/null 2>&1; then
    rsvg-convert -w 256 -h 256 \
        /usr/share/fusionos/repo/assets/fusionos-logo.svg \
        -o /usr/share/plymouth/themes/fusionos/logo.png 2>/dev/null || true
fi
plymouth-set-default-theme fusionos 2>/dev/null || true

# ==================================================================
# 5. KDE Plasma - Tema de Cores, Fontes e Aparencia Premium
# ==================================================================
LIVE_HOME="/home/liveuser"
mkdir -p $LIVE_HOME/.config $LIVE_HOME/.local/share/color-schemes

# Esquema de cores FusionOS Dark
cp /usr/share/fusionos/repo/configs/kde/FusionOS-Dark.colors \
   $LIVE_HOME/.local/share/color-schemes/ 2>/dev/null || true
cp /usr/share/fusionos/repo/configs/kde/FusionOS-Dark.colors \
   /usr/share/color-schemes/ 2>/dev/null || true

# Configuracoes globais KDE (fontes Inter, tema, animacoes)
cp /usr/share/fusionos/repo/configs/kde/kdeglobals \
   $LIVE_HOME/.config/kdeglobals 2>/dev/null || true

# Configuracoes Kwin (cantos arredondados, blur, animacoes)
cp /usr/share/fusionos/repo/configs/kde/kwinrc \
   $LIVE_HOME/.config/kwinrc 2>/dev/null || true

# Atalhos globais KDE
cp /usr/share/fusionos/repo/configs/kde/kglobalshortcutsrc \
   $LIVE_HOME/.config/ 2>/dev/null || true

# Look and Feel base: Breeze Dark (sera sobreposto pelo FusionOS)
mkdir -p $LIVE_HOME/.config/plasma-workspace/env/
cat <<'EOF' > $LIVE_HOME/.config/plasma-workspace/env/fusion-theme.sh
#!/bin/bash
# Aplicar tema FusionOS ao iniciar sessao Plasma
if command -v plasma-apply-colorscheme >/dev/null 2>&1; then
    plasma-apply-colorscheme FusionOS-Dark 2>/dev/null || true
fi
if command -v plasma-apply-lookandfeel >/dev/null 2>&1; then
    plasma-apply-lookandfeel org.kde.breezedark.desktop 2>/dev/null || true
fi
EOF
chmod +x $LIVE_HOME/.config/plasma-workspace/env/fusion-theme.sh

# ==================================================================
# 6. Wallpaper FusionOS Premium (SVG dinamico)
# ==================================================================
mkdir -p /usr/share/wallpapers/FusionOS/contents/images

# Gerar wallpaper dark gradiente inline
cat <<'SVGEOF' > /usr/share/wallpapers/FusionOS/contents/images/1920x1080.svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1920 1080">
  <defs>
    <radialGradient id="bg" cx="50%" cy="50%" r="75%">
      <stop offset="0%" stop-color="#1A1D27"/>
      <stop offset="60%" stop-color="#111420"/>
      <stop offset="100%" stop-color="#0D0F1A"/>
    </radialGradient>
    <radialGradient id="glow1" cx="30%" cy="60%" r="40%">
      <stop offset="0%" stop-color="#5B8BFF" stop-opacity="0.08"/>
      <stop offset="100%" stop-color="#5B8BFF" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="glow2" cx="75%" cy="35%" r="35%">
      <stop offset="0%" stop-color="#8B5CF6" stop-opacity="0.07"/>
      <stop offset="100%" stop-color="#8B5CF6" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <rect width="1920" height="1080" fill="url(#bg)"/>
  <rect width="1920" height="1080" fill="url(#glow1)"/>
  <rect width="1920" height="1080" fill="url(#glow2)"/>
</svg>
SVGEOF

cat <<'EOF' > /usr/share/wallpapers/FusionOS/metadata.desktop
[Desktop Entry]
Name=FusionOS Dark
Name[pt_BR]=FusionOS Dark
X-KDE-PluginInfo-Name=FusionOS
X-KDE-PluginInfo-Author=FusionOS Team
X-KDE-PluginInfo-License=GPLv3
X-KDE-PluginInfo-Category=Dark
EOF

# Configurar wallpaper via script Plasma
mkdir -p /usr/share/plasma/shells/org.kde.plasma.desktop/contents/updates/
cat <<'EOF' > /usr/share/plasma/shells/org.kde.plasma.desktop/contents/updates/99-fusionos-wallpaper.js
var desktops = desktops();
for (var i = 0; i < desktops.length; i++) {
    desktops[i].wallpaperPlugin = "org.kde.image";
    desktops[i].currentConfigGroup = ["Wallpaper", "org.kde.image", "General"];
    desktops[i].writeConfig("Image", "file:///usr/share/wallpapers/FusionOS/contents/images/1920x1080.svg");
    desktops[i].writeConfig("FillMode", "2");
    desktops[i].writeConfig("Color", "13,15,26");
}
EOF

# ==================================================================
# 7. Painel Plasma Flutuante
# ==================================================================
mkdir -p $LIVE_HOME/.config/plasma-org.kde.plasma.desktop-appletsrc.d/

# Configurar painel via script de inicializacao
cat <<'EOF' > /usr/share/plasma/shells/org.kde.plasma.desktop/contents/updates/98-fusionos-panel.js
// Configurar painel FusionOS flutuante
var panels = panels();
if (panels.length > 0) {
    var panel = panels[0];
    panel.floating = true;
    panel.height = 52;
    panel.alignment = "center";
    panel.panelOpacity = 2; // Translucent
}
EOF

# ==================================================================
# 8. Integracao de Scripts do Sistema
# ==================================================================
cp /usr/share/fusionos/repo/configs/onboarding/fusion-welcome.py \
   /usr/local/bin/ 2>/dev/null || true
chmod +x /usr/local/bin/fusion-welcome.py 2>/dev/null || true

cp /usr/share/fusionos/repo/configs/wine/fusion-wine-handler.sh \
   /usr/local/bin/fusion-wine-handler 2>/dev/null || true
chmod +x /usr/local/bin/fusion-wine-handler 2>/dev/null || true

cp /usr/share/fusionos/repo/scripts/fusion-switch-layout.sh \
   /usr/local/bin/fusion-switch-layout 2>/dev/null || true
chmod +x /usr/local/bin/fusion-switch-layout 2>/dev/null || true

mkdir -p /usr/share/fusionos/layouts
cp -r /usr/share/fusionos/repo/configs/layouts/*.js \
   /usr/share/fusionos/layouts/ 2>/dev/null || true
cp /usr/share/fusionos/repo/configs/layouts/fusion-layout-gui.py \
   /usr/share/fusionos/layouts/ 2>/dev/null || true
chmod +x /usr/share/fusionos/layouts/fusion-layout-gui.py 2>/dev/null || true

mkdir -p /usr/share/applications
cp /usr/share/fusionos/repo/configs/layouts/fusion-layout-switcher.desktop \
   /usr/share/applications/ 2>/dev/null || true
cp /usr/share/fusionos/repo/configs/wine/fusion-exe-runner.desktop \
   /usr/share/applications/ 2>/dev/null || true

# ==================================================================
# 9. Calamares - Instalador com Branding e Slideshow FusionOS
# ==================================================================
mkdir -p /usr/share/calamares/branding/fusionos /etc/calamares
cp -r /usr/share/fusionos/repo/configs/calamares/branding/fusionos/* \
   /usr/share/calamares/branding/fusionos/ 2>/dev/null || true
cp /usr/share/fusionos/repo/configs/calamares/settings.conf \
   /etc/calamares/settings.conf 2>/dev/null || true

if command -v rsvg-convert >/dev/null 2>&1; then
    rsvg-convert -w 128 -h 128 /usr/share/fusionos/repo/assets/fusionos-logo.svg \
        -o /usr/share/calamares/branding/fusionos/logo.png 2>/dev/null || true
    rsvg-convert -w 256 -h 256 /usr/share/fusionos/repo/assets/fusionos-logo.svg \
        -o /usr/share/calamares/branding/fusionos/welcome.png 2>/dev/null || true
fi

# ==================================================================
# 10. Bootloader GRUB 2 - Tema Premium
# ==================================================================
mkdir -p /boot/grub2/themes/fusionos
cp -r /usr/share/fusionos/repo/configs/grub/theme/* \
   /boot/grub2/themes/fusionos/ 2>/dev/null || true

if command -v rsvg-convert >/dev/null 2>&1; then
    rsvg-convert -w 1920 -h 1080 /usr/share/fusionos/repo/configs/grub/theme/background.svg \
        -o /boot/grub2/themes/fusionos/background.png 2>/dev/null || true
fi

if [ -f /etc/default/grub ]; then
    sed -i '/^GRUB_THEME=/d' /etc/default/grub 2>/dev/null || true
    echo 'GRUB_THEME="/boot/grub2/themes/fusionos/theme.txt"' >> /etc/default/grub
fi

# ==================================================================
# 11. GTK 3, GTK 4 & Konsole - Consistencia Dark em Todos os Apps
# ==================================================================
mkdir -p $LIVE_HOME/.config/gtk-3.0 $LIVE_HOME/.config/gtk-4.0
mkdir -p /etc/skel/.config/gtk-3.0 /etc/skel/.config/gtk-4.0

cp /usr/share/fusionos/repo/configs/gtk/gtk3-settings.ini $LIVE_HOME/.config/gtk-3.0/settings.ini 2>/dev/null || true
cp /usr/share/fusionos/repo/configs/gtk/gtk4-settings.ini $LIVE_HOME/.config/gtk-4.0/settings.ini 2>/dev/null || true
cp /usr/share/fusionos/repo/configs/gtk/gtk3-settings.ini /etc/skel/.config/gtk-3.0/settings.ini 2>/dev/null || true
cp /usr/share/fusionos/repo/configs/gtk/gtk4-settings.ini /etc/skel/.config/gtk-4.0/settings.ini 2>/dev/null || true

mkdir -p $LIVE_HOME/.local/share/konsole /usr/share/konsole
cp /usr/share/fusionos/repo/configs/konsole/FusionOS-Dark.colorscheme $LIVE_HOME/.local/share/konsole/ 2>/dev/null || true
cp /usr/share/fusionos/repo/configs/konsole/FusionOS.profile $LIVE_HOME/.local/share/konsole/ 2>/dev/null || true
cp /usr/share/fusionos/repo/configs/konsole/FusionOS-Dark.colorscheme /usr/share/konsole/ 2>/dev/null || true
cp /usr/share/fusionos/repo/configs/konsole/FusionOS.profile /usr/share/konsole/ 2>/dev/null || true

cat <<'EOF' > $LIVE_HOME/.config/konsolerc
[Desktop Entry]
DefaultProfile=FusionOS.profile
EOF

# ==================================================================
# 12. Fastfetch e Integracao de Terminal
# ==================================================================
mkdir -p /etc/fastfetch
cp /usr/share/fusionos/repo/configs/fastfetch/config.jsonc /etc/fastfetch/config.jsonc 2>/dev/null || true
cp /usr/share/fusionos/repo/configs/system/fusion-profile.sh /etc/profile.d/fusion-profile.sh 2>/dev/null || true
chmod +x /etc/profile.d/fusion-profile.sh 2>/dev/null || true

# ==================================================================
# 13. Btrfs Time Machine & Snapper
# ==================================================================
mkdir -p /etc/snapper/configs
cp /usr/share/fusionos/repo/configs/system/snapper-root.conf /etc/snapper/configs/root 2>/dev/null || true
cp /usr/share/fusionos/repo/configs/system/fusion-snapper-setup.sh /usr/local/bin/fusion-snapper-setup 2>/dev/null || true
chmod +x /usr/local/bin/fusion-snapper-setup 2>/dev/null || true

# ==================================================================
# 14. Perfis de Energia e Desempenho (Fusion Power Profiles)
# ==================================================================
cp /usr/share/fusionos/repo/configs/system/fusion-power-mode.sh /usr/local/bin/fusion-power-mode 2>/dev/null || true
chmod +x /usr/local/bin/fusion-power-mode 2>/dev/null || true
cp /usr/share/fusionos/repo/configs/system/fusion-power-gui.py /usr/local/bin/fusion-power-gui.py 2>/dev/null || true
chmod +x /usr/local/bin/fusion-power-gui.py 2>/dev/null || true
cp /usr/share/fusionos/repo/configs/system/fusion-power-mode.desktop /usr/share/applications/ 2>/dev/null || true

# ==================================================================
# 15. Assistente de Drivers e Hardware (NVIDIA / Wi-Fi)
# ==================================================================
cp /usr/share/fusionos/repo/configs/system/fusion-hardware-assistant.sh /usr/local/bin/fusion-hardware-assistant 2>/dev/null || true
chmod +x /usr/local/bin/fusion-hardware-assistant 2>/dev/null || true
cp /usr/share/fusionos/repo/configs/system/fusion-hardware-gui.py /usr/local/bin/fusion-hardware-gui.py 2>/dev/null || true
chmod +x /usr/local/bin/fusion-hardware-gui.py 2>/dev/null || true
cp /usr/share/fusionos/repo/configs/system/fusion-hardware-assistant.desktop /usr/share/applications/ 2>/dev/null || true

# ==================================================================
# 16. Identidade Sonora FusionOS (Sound Theme Acustico)
# ==================================================================
mkdir -p /usr/share/sounds/fusionos
cp -r /usr/share/fusionos/repo/configs/sounds/fusionos/* /usr/share/sounds/fusionos/ 2>/dev/null || true

mkdir -p $LIVE_HOME/.config/autostart
cat <<'EOF' > $LIVE_HOME/.config/autostart/fusion-sound.desktop
[Desktop Entry]
Name=FusionOS Startup Sound
Comment=Som de boas-vindas do FusionOS
Exec=sh -c 'sleep 2 && (paplay /usr/share/sounds/fusionos/stereo/desktop-login.wav 2>/dev/null || pw-play /usr/share/sounds/fusionos/stereo/desktop-login.wav 2>/dev/null || true)'
Terminal=false
Type=Application
StartupNotify=false
EOF

# ==================================================================
# 17. Motor de Audio Hi-Res, Dolby 3D & Bluetooth Destravado
# ==================================================================
mkdir -p /etc/pipewire/pipewire.conf.d /etc/wireplumber/wireplumber.conf.d
cp /usr/share/fusionos/repo/configs/system/pipewire-hires.conf /etc/pipewire/pipewire.conf.d/ 2>/dev/null || true
cp /usr/share/fusionos/repo/configs/system/wireplumber-bluetooth.conf /etc/wireplumber/wireplumber.conf.d/ 2>/dev/null || true

mkdir -p /usr/share/fusionos/audio/presets
cp -r /usr/share/fusionos/repo/configs/audio/presets/* /usr/share/fusionos/audio/presets/ 2>/dev/null || true
cp /usr/share/fusionos/repo/configs/audio/fusion-audio-service.sh /usr/local/bin/fusion-audio-service 2>/dev/null || true
chmod +x /usr/local/bin/fusion-audio-service 2>/dev/null || true
cp /usr/share/fusionos/repo/configs/audio/fusion-sound-gui.py /usr/local/bin/fusion-sound-gui.py 2>/dev/null || true
chmod +x /usr/local/bin/fusion-sound-gui.py 2>/dev/null || true
cp /usr/share/fusionos/repo/configs/audio/fusion-sound-control.desktop /usr/share/applications/ 2>/dev/null || true

cat <<'EOF' > $LIVE_HOME/.config/autostart/fusion-audio-service.desktop
[Desktop Entry]
Name=FusionOS Audio Service
Comment=Motor de áudio Dolby 3D e DSP do FusionOS
Exec=/usr/local/bin/fusion-audio-service
Terminal=false
Type=Application
StartupNotify=false
EOF

# ==================================================================
# 18. Area de Trabalho (Desktop) - Atalhos Premium
# ==================================================================
mkdir -p $LIVE_HOME/Desktop

cat <<'EOF' > $LIVE_HOME/Desktop/fusion-welcome.desktop
[Desktop Entry]
Name=FusionOS Welcome
Name[pt_BR]=Bem-vindo ao FusionOS
Comment=Configure o seu sistema FusionOS
Comment[pt_BR]=Configure o seu sistema FusionOS
Exec=/usr/local/bin/fusion-welcome.py
Icon=preferences-desktop
Terminal=false
Type=Application
StartupNotify=true
EOF

cat <<'EOF' > $LIVE_HOME/Desktop/install-fusionos.desktop
[Desktop Entry]
Name=Install FusionOS
Name[pt_BR]=Instalar FusionOS
Comment=Install the system to your disk permanently
Comment[pt_BR]=Instalar o sistema no disco permanentemente
Exec=sudo calamares
Icon=drive-harddisk
Terminal=false
Type=Application
StartupNotify=true
EOF

cp $LIVE_HOME/Desktop/fusion-welcome.desktop \
   $LIVE_HOME/.config/autostart/
chmod +x $LIVE_HOME/Desktop/*.desktop
chown -R liveuser:liveuser $LIVE_HOME
update-desktop-database /usr/share/applications || true

# ==================================================================
# 20. Spotlight HUD (KRunner)
# ==================================================================
cp /usr/share/fusionos/repo/configs/kde/krunnerrc $LIVE_HOME/.config/krunnerrc 2>/dev/null || true
cp /usr/share/fusionos/repo/configs/kde/krunnerrc /etc/skel/.config/krunnerrc 2>/dev/null || true

# ==================================================================
# 21. Gestos Mac no Touchpad (Natural Scrolling & 1:1 Gestures)
# ==================================================================
cp /usr/share/fusionos/repo/configs/kde/touchpadrc $LIVE_HOME/.config/touchpadrc 2>/dev/null || true
cp /usr/share/fusionos/repo/configs/kde/touchpadrc /etc/skel/.config/touchpadrc 2>/dev/null || true

# ==================================================================
# 22. Fusion Connect (Integracao com Celular)
# ==================================================================
cp /usr/share/fusionos/repo/configs/system/fusion-connect-setup.sh /usr/local/bin/fusion-connect-setup 2>/dev/null || true
chmod +x /usr/local/bin/fusion-connect-setup 2>/dev/null || true
cp /usr/share/fusionos/repo/configs/system/fusion-connect.desktop /usr/share/applications/ 2>/dev/null || true

# ==================================================================
# 23. AdBlock e DNS-over-TLS Criptografado
# ==================================================================
mkdir -p /etc/systemd/resolved.conf.d
cp /usr/share/fusionos/repo/configs/system/resolved-privacy.conf /etc/systemd/resolved.conf.d/privacy.conf 2>/dev/null || true
systemctl enable systemd-resolved 2>/dev/null || true

# ==================================================================
# 24. Fusion Cleaner & Otimizador de Sistema
# ==================================================================
cp /usr/share/fusionos/repo/configs/system/fusion-cleaner.sh /usr/local/bin/fusion-cleaner 2>/dev/null || true
chmod +x /usr/local/bin/fusion-cleaner 2>/dev/null || true
cp /usr/share/fusionos/repo/configs/system/fusion-cleaner-gui.py /usr/local/bin/fusion-cleaner-gui.py 2>/dev/null || true
chmod +x /usr/local/bin/fusion-cleaner-gui.py 2>/dev/null || true
cp /usr/share/fusionos/repo/configs/system/fusion-cleaner.desktop /usr/share/applications/ 2>/dev/null || true

# ==================================================================
# 25. Gaming Suite (Game Bar, Clip Recorder, Runner Hub)
# ==================================================================
cp /usr/share/fusionos/repo/configs/gaming/fusion-gamebar.py /usr/local/bin/fusion-gamebar 2>/dev/null || true
chmod +x /usr/local/bin/fusion-gamebar 2>/dev/null || true
cp /usr/share/fusionos/repo/configs/gaming/fusion-clip-record.sh /usr/local/bin/fusion-clip-record 2>/dev/null || true
chmod +x /usr/local/bin/fusion-clip-record 2>/dev/null || true
cp /usr/share/fusionos/repo/configs/gaming/fusion-runner-hub.py /usr/local/bin/fusion-runner-hub 2>/dev/null || true
chmod +x /usr/local/bin/fusion-runner-hub 2>/dev/null || true
cp /usr/share/fusionos/repo/configs/gaming/*.desktop /usr/share/applications/ 2>/dev/null || true

# ==================================================================
# 26. Produtividade (QuickLook & ClipVault)
# ==================================================================
cp /usr/share/fusionos/repo/configs/system/fusion-quicklook.py /usr/local/bin/fusion-quicklook 2>/dev/null || true
chmod +x /usr/local/bin/fusion-quicklook 2>/dev/null || true
cp /usr/share/fusionos/repo/configs/system/fusion-quicklook.desktop /usr/share/applications/ 2>/dev/null || true
cp /usr/share/fusionos/repo/configs/kde/klipperrc $LIVE_HOME/.config/klipperrc 2>/dev/null || true
cp /usr/share/fusionos/repo/configs/kde/klipperrc /etc/skel/.config/klipperrc 2>/dev/null || true

# ==================================================================
# 27. Design & UI (Dynamic Wallpaper, Control Center, Focus Mode, Glyphs)
# ==================================================================
cp /usr/share/fusionos/repo/configs/system/fusion-dynamic-wallpaper.sh /usr/local/bin/fusion-dynamic-wallpaper 2>/dev/null || true
chmod +x /usr/local/bin/fusion-dynamic-wallpaper 2>/dev/null || true
mkdir -p /etc/systemd/user
cp /usr/share/fusionos/repo/configs/system/fusion-dynamic-wallpaper.service /etc/systemd/user/ 2>/dev/null || true
cp /usr/share/fusionos/repo/configs/system/fusion-dynamic-wallpaper.timer /etc/systemd/user/ 2>/dev/null || true

cp /usr/share/fusionos/repo/configs/system/fusion-control-center.py /usr/local/bin/fusion-control-center 2>/dev/null || true
chmod +x /usr/local/bin/fusion-control-center 2>/dev/null || true
cp /usr/share/fusionos/repo/configs/system/fusion-control-center.desktop /usr/share/applications/ 2>/dev/null || true

cp /usr/share/fusionos/repo/configs/system/fusion-focus-mode.sh /usr/local/bin/fusion-focus-mode 2>/dev/null || true
chmod +x /usr/local/bin/fusion-focus-mode 2>/dev/null || true
cp /usr/share/fusionos/repo/configs/system/fusion-focus-mode.desktop /usr/share/applications/ 2>/dev/null || true

mkdir -p /usr/share/icons/fusion-glyphs
cp -r /usr/share/fusionos/repo/assets/icons/fusion-glyphs/* /usr/share/icons/fusion-glyphs/ 2>/dev/null || true
gtk-update-icon-cache /usr/share/icons/fusion-glyphs 2>/dev/null || true

# ==================================================================
# 28. Seguranca & Privacidade (Vault, Shield, Permissions, Time Capsule)
# ==================================================================
cp /usr/share/fusionos/repo/configs/security/fusion-vault.sh /usr/local/bin/fusion-vault 2>/dev/null || true
chmod +x /usr/local/bin/fusion-vault 2>/dev/null || true
cp /usr/share/fusionos/repo/configs/security/fusion-vault-gui.py /usr/local/bin/fusion-vault-gui 2>/dev/null || true
chmod +x /usr/local/bin/fusion-vault-gui 2>/dev/null || true
cp /usr/share/fusionos/repo/configs/security/fusion-vault.desktop /usr/share/applications/ 2>/dev/null || true

cp /usr/share/fusionos/repo/configs/security/fusion-shield.py /usr/local/bin/fusion-shield 2>/dev/null || true
chmod +x /usr/local/bin/fusion-shield 2>/dev/null || true
cp /usr/share/fusionos/repo/configs/security/fusion-shield.desktop /usr/share/applications/ 2>/dev/null || true

cp /usr/share/fusionos/repo/configs/security/fusion-permissions.py /usr/local/bin/fusion-permissions 2>/dev/null || true
chmod +x /usr/local/bin/fusion-permissions 2>/dev/null || true
cp /usr/share/fusionos/repo/configs/security/fusion-permissions.desktop /usr/share/applications/ 2>/dev/null || true

cp /usr/share/fusionos/repo/configs/security/fusion-time-capsule.sh /usr/local/bin/fusion-time-capsule 2>/dev/null || true
chmod +x /usr/local/bin/fusion-time-capsule 2>/dev/null || true
cp /usr/share/fusionos/repo/configs/security/fusion-time-capsule-gui.py /usr/local/bin/fusion-time-capsule-gui 2>/dev/null || true
chmod +x /usr/local/bin/fusion-time-capsule-gui 2>/dev/null || true
cp /usr/share/fusionos/repo/configs/security/fusion-time-capsule.desktop /usr/share/applications/ 2>/dev/null || true

# ==================================================================
# 29. Hardware & Otimizacoes de Fundo (Battery Switcher, Scheduler, Updates)
# ==================================================================
cp /usr/share/fusionos/repo/configs/system/fusion-battery-switch.sh /usr/local/bin/fusion-battery-switch 2>/dev/null || true
chmod +x /usr/local/bin/fusion-battery-switch 2>/dev/null || true
mkdir -p /etc/udev/rules.d
cp /usr/share/fusionos/repo/configs/system/99-fusion-battery.rules /etc/udev/rules.d/ 2>/dev/null || true

cp /usr/share/fusionos/repo/configs/system/fusion-focus-scheduler.sh /usr/local/bin/fusion-focus-scheduler 2>/dev/null || true
chmod +x /usr/local/bin/fusion-focus-scheduler 2>/dev/null || true
cp /usr/share/fusionos/repo/configs/system/fusion-focus-scheduler.service /etc/systemd/user/ 2>/dev/null || true

cp /usr/share/fusionos/repo/configs/system/fusion-auto-update.sh /usr/local/bin/fusion-auto-update 2>/dev/null || true
chmod +x /usr/local/bin/fusion-auto-update 2>/dev/null || true
cp /usr/share/fusionos/repo/configs/system/fusion-auto-update.service /etc/systemd/system/ 2>/dev/null || true
cp /usr/share/fusionos/repo/configs/system/fusion-auto-update.timer /etc/systemd/system/ 2>/dev/null || true
systemctl enable fusion-auto-update.timer 2>/dev/null || true

# ==================================================================
# 30. Pro Suite (Crisp Mic, AutoEQ, Lens OCR, Color Picker, Cloud, Hub, Waydroid, HDR, Cast, DevBox, Quake HUD)
# ==================================================================
cp /usr/share/fusionos/repo/configs/audio/fusion-crisp-mic.sh /usr/local/bin/fusion-crisp-mic 2>/dev/null || true
chmod +x /usr/local/bin/fusion-crisp-mic 2>/dev/null || true
mkdir -p /usr/share/fusionos/audio/eq-profiles
cp -r /usr/share/fusionos/repo/configs/audio/eq-profiles/* /usr/share/fusionos/audio/eq-profiles/ 2>/dev/null || true
cp /usr/share/fusionos/repo/configs/audio/pipewire-crisp-mic.conf /usr/share/fusionos/audio/ 2>/dev/null || true

cp /usr/share/fusionos/repo/configs/system/fusion-lens.py /usr/local/bin/fusion-lens 2>/dev/null || true
chmod +x /usr/local/bin/fusion-lens 2>/dev/null || true
cp /usr/share/fusionos/repo/configs/system/fusion-lens.desktop /usr/share/applications/ 2>/dev/null || true

cp /usr/share/fusionos/repo/configs/system/fusion-color-picker.py /usr/local/bin/fusion-color-picker 2>/dev/null || true
chmod +x /usr/local/bin/fusion-color-picker 2>/dev/null || true
cp /usr/share/fusionos/repo/configs/system/fusion-color-picker.desktop /usr/share/applications/ 2>/dev/null || true

cp /usr/share/fusionos/repo/configs/system/fusion-cloud-connect.sh /usr/local/bin/fusion-cloud-connect 2>/dev/null || true
chmod +x /usr/local/bin/fusion-cloud-connect 2>/dev/null || true
cp /usr/share/fusionos/repo/configs/system/fusion-cloud-connect.py /usr/local/bin/fusion-cloud-connect-gui 2>/dev/null || true
chmod +x /usr/local/bin/fusion-cloud-connect-gui 2>/dev/null || true
cp /usr/share/fusionos/repo/configs/system/fusion-cloud-connect.desktop /usr/share/applications/ 2>/dev/null || true

cp /usr/share/fusionos/repo/configs/software/fusion-software-hub.py /usr/local/bin/fusion-software-hub 2>/dev/null || true
chmod +x /usr/local/bin/fusion-software-hub 2>/dev/null || true
cp /usr/share/fusionos/repo/configs/software/fusion-software-hub.desktop /usr/share/applications/ 2>/dev/null || true

cp /usr/share/fusionos/repo/configs/system/fusion-waydroid-setup.sh /usr/local/bin/fusion-waydroid-setup 2>/dev/null || true
chmod +x /usr/local/bin/fusion-waydroid-setup 2>/dev/null || true
cp /usr/share/fusionos/repo/configs/system/fusion-waydroid-gui.py /usr/local/bin/fusion-waydroid-gui 2>/dev/null || true
chmod +x /usr/local/bin/fusion-waydroid-gui 2>/dev/null || true
cp /usr/share/fusionos/repo/configs/system/fusion-waydroid.desktop /usr/share/applications/ 2>/dev/null || true

cp /usr/share/fusionos/repo/configs/system/fusion-hdr-assistant.py /usr/local/bin/fusion-hdr-assistant 2>/dev/null || true
chmod +x /usr/local/bin/fusion-hdr-assistant 2>/dev/null || true
cp /usr/share/fusionos/repo/configs/system/fusion-hdr-assistant.desktop /usr/share/applications/ 2>/dev/null || true

cp /usr/share/fusionos/repo/configs/system/fusion-cast.py /usr/local/bin/fusion-cast 2>/dev/null || true
chmod +x /usr/local/bin/fusion-cast 2>/dev/null || true
cp /usr/share/fusionos/repo/configs/system/fusion-cast.desktop /usr/share/applications/ 2>/dev/null || true

cp /usr/share/fusionos/repo/configs/system/fusion-devbox.py /usr/local/bin/fusion-devbox 2>/dev/null || true
chmod +x /usr/local/bin/fusion-devbox 2>/dev/null || true
cp /usr/share/fusionos/repo/configs/system/fusion-devbox.desktop /usr/share/applications/ 2>/dev/null || true

cp /usr/share/fusionos/repo/configs/kde/yakuakerc $LIVE_HOME/.config/yakuakerc 2>/dev/null || true
cp /usr/share/fusionos/repo/configs/kde/yakuakerc /etc/skel/.config/yakuakerc 2>/dev/null || true

# Garantir symlinks universais em /usr/bin/ para todos os binarios em /usr/local/bin/
for bin in /usr/local/bin/fusion-*; do
    if [ -x "$bin" ]; then
        ln -sf "$bin" "/usr/bin/$(basename "$bin")" 2>/dev/null || true
    fi
done

# ==================================================================
# 31. Rebranding OS (Zero Fedora)
# ==================================================================
cat <<'EOF' > /etc/os-release
NAME="FusionOS"
VERSION="1.0 (Noble)"
ID=fusionos
ID_LIKE=linux
VERSION_ID="1.0"
PRETTY_NAME="FusionOS 1.0 Noble"
ANSI_COLOR="0;38;2;91;139;255"
LOGO=fusionos-logo
HOME_URL="https://github.com/PedroMira2/FusionOS"
DOCUMENTATION_URL="https://github.com/PedroMira2/FusionOS/wiki"
BUG_REPORT_URL="https://github.com/PedroMira2/FusionOS/issues"
EOF

# Hostname exclusivo
echo "fusionos" > /etc/hostname

echo ""
echo "======================================================"
echo "  FusionOS 1.0 Noble - Kickstart 100% Configurado!"
echo "======================================================"
%end
