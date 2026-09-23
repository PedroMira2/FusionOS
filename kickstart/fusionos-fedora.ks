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
repo --name=rpmfusion-free-updates --metalink="https://mirrors.rpmfusion.org/metalink?repo=free-fedora-updates-released-f41&arch=x86_64"
repo --name=rpmfusion-nonfree --metalink="https://mirrors.rpmfusion.org/metalink?repo=nonfree-fedora-41&arch=x86_64"
repo --name=rpmfusion-nonfree-updates --metalink="https://mirrors.rpmfusion.org/metalink?repo=nonfree-fedora-updates-released-f41&arch=x86_64"

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


# Configuracoes Internas do Live OS
%post
# 1. Privilégios e Usuario Live (CRÍTICO: sudo sem senha)
useradd -m -c "FusionOS Live User" -G wheel liveuser
passwd -d liveuser >/dev/null
echo "liveuser ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/liveuser
chmod 0440 /etc/sudoers.d/liveuser

# 2. SDDM Autologin
mkdir -p /etc/sddm.conf.d
cat <<'EOF' > /etc/sddm.conf.d/autologin.conf
[Autologin]
User=liveuser
Session=plasmawayland
EOF
systemctl enable sddm
systemctl set-default graphical.target

# 3. Flathub
flatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo

# 4. Configurar Plymouth (Animação de Boot Premium)
mkdir -p /usr/share/plymouth/themes/fusionos
cp -r /usr/share/fusionos/repo/configs/plymouth/* /usr/share/plymouth/themes/fusionos/ 2>/dev/null || true
cp /usr/share/fusionos/repo/assets/fusionos-logo.svg /usr/share/plymouth/themes/fusionos/ 2>/dev/null || true
if command -v rsvg-convert >/dev/null 2>&1; then
    rsvg-convert -w 256 -h 256 /usr/share/fusionos/repo/assets/fusionos-logo.svg -o /usr/share/plymouth/themes/fusionos/logo.png 2>/dev/null || true
fi
plymouth-set-default-theme fusionos || true

# 5. Configurar Wallpaper e Atalhos Globais
mkdir -p /usr/share/wallpapers/FusionOS/contents/images
cp /usr/share/fusionos/repo/assets/fusionos-logo.svg /usr/share/wallpapers/FusionOS/contents/images/1920x1080.svg 2>/dev/null || true
cat <<'EOF' > /usr/share/wallpapers/FusionOS/metadata.desktop
[Desktop Entry]
Name=FusionOS Default
X-KDE-PluginInfo-Name=FusionOS
X-KDE-PluginInfo-Author=FusionOS Team
X-KDE-PluginInfo-License=GPLv3
EOF
mkdir -p /usr/share/plasma/shells/org.kde.plasma.desktop/contents/updates/
cat <<'EOF' > /usr/share/plasma/shells/org.kde.plasma.desktop/contents/updates/99-fusion-wallpaper.js
var desktops = desktops();
for (var i = 0; i < desktops.length; i++) {
    desktops[i].wallpaperPlugin = "org.kde.image";
    desktops[i].currentConfigGroup = ["Wallpaper", "org.kde.image", "General"];
    desktops[i].writeConfig("Image", "file:///usr/share/wallpapers/FusionOS/contents/images/1920x1080.svg");
    desktops[i].writeConfig("FillMode", "2");
}
EOF

mkdir -p /home/liveuser/.config
cp /usr/share/fusionos/repo/configs/kde/kglobalshortcutsrc /home/liveuser/.config/ 2>/dev/null || true

# 6. Integrar Scripts do Sistema (Onboarding, Wine Handler, Layouts)
cp /usr/share/fusionos/repo/configs/onboarding/fusion-welcome.py /usr/local/bin/ 2>/dev/null || true
chmod +x /usr/local/bin/fusion-welcome.py 2>/dev/null || true

cp /usr/share/fusionos/repo/configs/wine/fusion-wine-handler.sh /usr/local/bin/fusion-wine-handler 2>/dev/null || true
chmod +x /usr/local/bin/fusion-wine-handler 2>/dev/null || true

cp /usr/share/fusionos/repo/scripts/fusion-switch-layout.sh /usr/local/bin/fusion-switch-layout 2>/dev/null || true
chmod +x /usr/local/bin/fusion-switch-layout 2>/dev/null || true

mkdir -p /usr/share/fusionos/layouts
cp -r /usr/share/fusionos/repo/configs/layouts/*.js /usr/share/fusionos/layouts/ 2>/dev/null || true

mkdir -p /usr/share/applications
cp /usr/share/fusionos/repo/configs/layouts/fusion-layout-switcher.desktop /usr/share/applications/ 2>/dev/null || true
cp /usr/share/fusionos/repo/configs/wine/fusion-exe-runner.desktop /usr/share/applications/ 2>/dev/null || true
update-desktop-database /usr/share/applications || true

# 7. Criar Atalhos na Área de Trabalho do Live User
mkdir -p /home/liveuser/Desktop
mkdir -p /home/liveuser/.config/autostart

cat <<'EOF' > /home/liveuser/Desktop/fusion-welcome.desktop
[Desktop Entry]
Name=Fusion OS Welcome
Comment=Configure o seu sistema
Exec=/usr/local/bin/fusion-welcome.py
Icon=preferences-desktop
Terminal=false
Type=Application
EOF

cat <<'EOF' > /home/liveuser/Desktop/install-fusionos.desktop
[Desktop Entry]
Name=Instalar Fusion OS
Comment=Instalar o sistema no disco
Exec=sudo calamares
Icon=drive-harddisk
Terminal=false
Type=Application
EOF

cp /home/liveuser/Desktop/fusion-welcome.desktop /home/liveuser/.config/autostart/
chmod +x /home/liveuser/Desktop/*.desktop
chown -R liveuser:liveuser /home/liveuser

# 8. Rebranding para Fusion OS
cat <<'EOF' > /etc/os-release
NAME="Fusion OS"
VERSION="1.0"
ID=fusionos
ID_LIKE=fedora
VERSION_ID="1.0"
PRETTY_NAME="Fusion OS 1.0"
ANSI_COLOR="0;38;2;60;108;231"
LOGO=fusionos-logo
EOF

echo "FusionOS Kickstart 100% Configurado e Limpo!"
%end
