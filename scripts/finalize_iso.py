import sys
import paramiko

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.194.129', port=22, username='testes', password='Pedromira28@', timeout=30)

def run(cmd):
    print(f"=== {cmd} ===")
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print("[STDERR]", err)
    return out

# 1. Free space by removing the 8GB uncompressed disk image (squashfs is already made!)
run("echo Pedromira28@ | sudo -S rm -f /home/testes/FusionOS/output/lmc-disk-*.img")
run("df -h /")

# 2. Setup EFI/BOOT and efiboot.img
setup_efi_cmd = """echo Pedromira28@ | sudo -S bash -c '
set -e
WORK="/var/tmp/lmc-work-1ukzc811"
mkdir -p "$WORK/EFI/BOOT/fonts"
cp -v /boot/efi/EFI/BOOT/BOOTX64.EFI "$WORK/EFI/BOOT/"
cp -v /boot/efi/EFI/BOOT/fbx64.efi "$WORK/EFI/BOOT/"
cp -v /boot/efi/EFI/fedora/gcdx64.efi "$WORK/EFI/BOOT/grubx64.efi"
cp -v /boot/grub2/fonts/unicode.pf2 "$WORK/EFI/BOOT/fonts/"
cp -v "$WORK/boot/grub2/grub.cfg" "$WORK/EFI/BOOT/grub.cfg"
mkefiboot --label=ANACONDA "$WORK/EFI/BOOT" "$WORK/images/efiboot.img"
ls -lh "$WORK/images/efiboot.img"
'"""
run(setup_efi_cmd)

# 3. Run xorrisofs to generate the bootable ISO
xorriso_cmd = """echo Pedromira28@ | sudo -S bash -c '
set -e
WORK="/var/tmp/lmc-work-1ukzc811"
OUTPUT="/home/testes/FusionOS/output/FusionOS-Live-x86_64.iso"
mkdir -p /home/testes/FusionOS/output

xorrisofs -o "$OUTPUT" \
   -R -J -V "FusionOS_Live" \
   --grub2-mbr /usr/lib/grub/i386-pc/boot_hybrid.img \
   -partition_offset 16 \
   -appended_part_as_gpt \
   -append_partition 2 C12A7328-F81F-11D2-BA4B-00A0C93EC93B "$WORK/images/efiboot.img" \
   -iso_mbr_part_type EBD0A0A2-B9E5-4433-87C0-68B6B72699C7 \
   -c boot.cat --boot-catalog-hide \
   -b images/eltorito.img \
   -no-emul-boot -boot-load-size 4 -boot-info-table --grub2-boot-info \
   -eltorito-alt-boot \
   -e "--interval:appended_partition_2:all::" -no-emul-boot \
   -graft-points \
   images/pxeboot="$WORK/images/pxeboot" \
   LiveOS="$WORK/LiveOS" \
   Fedora-Legal-README.txt="$WORK/Fedora-Legal-README.txt" \
   LICENSE="$WORK/LICENSE" \
   boot/grub2="$WORK/boot/grub2" \
   boot/grub2/i386-pc=/usr/lib/grub/i386-pc \
   images/eltorito.img="$WORK/images/eltorito.img" \
   EFI/BOOT="$WORK/EFI/BOOT"

ls -lh "$OUTPUT"
'"""
run(xorriso_cmd)

ssh.close()
