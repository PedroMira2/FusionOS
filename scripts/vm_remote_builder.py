import sys
import os
import time
import paramiko

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

VM_IP = "192.168.194.131"
VM_PORT = 22
VM_USER = "testes"
VM_PASS = os.environ.get("VM_PASS", "Pedromira28@")

print(f"[*] Conectando a {VM_USER}@{VM_IP}...")
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(VM_IP, port=VM_PORT, username=VM_USER, password=VM_PASS, timeout=15)
print("[+] Conectado com sucesso à VM!")

local_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sftp = ssh.open_sftp()
print(f"[*] Sincronizando kickstart e scripts diretamente via SFTP...")
files_to_sync = [
    ("kickstart/fusionos-fedora.ks", "/home/testes/FusionOS/kickstart/fusionos-fedora.ks"),
    ("scripts/build-iso.sh", "/home/testes/FusionOS/scripts/build-iso.sh"),
    ("scripts/fusion-setup.sh", "/home/testes/FusionOS/scripts/fusion-setup.sh"),
]
for rel_local, remote_path in files_to_sync:
    local_path = os.path.join(local_root, rel_local.replace("/", os.sep))
    if os.path.exists(local_path):
        try:
            sftp.put(local_path, remote_path)
            print(f"    -> Enviado: {rel_local}")
        except Exception as e:
            print(f"    -> Erro ao enviar {rel_local}: {e}")
sftp.close()

cmd = "cd ~/FusionOS && git pull origin main && echo 'Pedromira28@' | sudo -S rm -rf output /var/tmp/dnf* /tmp/dnf* /run/anaconda.pid && echo 'Pedromira28@' | sudo -S bash scripts/build-iso.sh"
print(f"[*] Executando comando na VM:\n    {cmd}\n" + "=" * 60)

stdin, stdout, stderr = ssh.exec_command(cmd, get_pty=True)

while True:
    line = stdout.readline()
    if not line:
        break
    sys.stdout.write(line)
    sys.stdout.flush()

exit_code = stdout.channel.recv_exit_status()
print("=" * 60)
print(f"[*] Processo finalizado na VM com código: {exit_code}")

if exit_code == 0:
    print("[*] Baixando a ISO gerada da VM para C:\\Users\\pedro\\Desktop\\HEAK\\FusionOS-Live-x86_64.iso...")
    sftp = ssh.open_sftp()
    remote_iso = "/home/testes/FusionOS/output/FusionOS-Live-x86_64.iso"
    local_iso = r"C:\Users\pedro\Desktop\HEAK\FusionOS-Live-x86_64.iso"
    sftp.get(remote_iso, local_iso)
    sftp.close()
    print("[✔] ISO baixada com sucesso para a pasta do Windows! Pronta para gravar no pendrive com Rufus ou BalenaEtcher.")

ssh.close()
sys.exit(exit_code)
