import sys
import os
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
ssh.connect(VM_IP, port=VM_PORT, username=VM_USER, password=VM_PASS, timeout=30)
print("[+] Conectado com sucesso à VM!")

remote_iso = "/home/testes/FusionOS/output/FusionOS-Live-x86_64.iso"
local_iso = r"C:\Users\pedro\Desktop\HEAK\FusionOS-Live-x86_64.iso"

# Adjust permissions on VM so sftp user can read
ssh.exec_command('echo Pedromira28@ | sudo -S chmod 644 /home/testes/FusionOS/output/FusionOS-Live-x86_64.iso')
time.sleep(1)

sftp = ssh.open_sftp()
stat = sftp.stat(remote_iso)
total_size = stat.st_size
print(f"[*] Tamanho do arquivo ISO na VM: {total_size / (1024*1024):.2f} MB ({total_size / (1024*1024*1024):.2f} GB)")
print(f"[*] Baixando para {local_iso}...")

last_print = time.time()
def progress(transferred, total):
    global last_print
    if time.time() - last_print > 3:
        percent = (transferred / total) * 100
        mb_transferred = transferred / (1024 * 1024)
        mb_total = total / (1024 * 1024)
        print(f"    [SFTP] Baixado: {mb_transferred:.1f} MB / {mb_total:.1f} MB ({percent:.1f}%)")
        last_print = time.time()

sftp.get(remote_iso, local_iso, callback=progress)
sftp.close()
ssh.close()

if os.path.exists(local_iso):
    local_size = os.path.getsize(local_iso)
    print(f"[✔] ISO baixada com sucesso! Tamanho final: {local_size / (1024*1024*1024):.2f} GB")
else:
    print("[X] Erro: arquivo local nao encontrado apos download.")
