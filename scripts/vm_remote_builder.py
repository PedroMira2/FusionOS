import sys
import time
import paramiko

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

VM_IP = "192.168.194.129"
VM_PORT = 22
VM_USER = "testes"
VM_PASS = "Pedromira28@"

print(f"[*] Conectando a {VM_USER}@{VM_IP}...")
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(VM_IP, port=VM_PORT, username=VM_USER, password=VM_PASS, timeout=15)
print("[+] Conectado com sucesso à VM!")

cmd = "cd ~/FusionOS && git fetch origin && git reset --hard origin/main && chmod +x scripts/*.sh configs/wine/*.sh && echo 'Pedromira28@' | sudo -S ./scripts/build-iso.sh"
print(f"[*] Executando comando na VM:\n    {cmd}\n" + "=" * 60)

stdin, stdout, stderr = ssh.exec_command(cmd, get_pty=True)

# Loop de leitura em tempo real
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
