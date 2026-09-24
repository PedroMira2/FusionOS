import time
import os
import sys
import paramiko

VM_IP = "192.168.194.131"
VM_PORT = 22
VM_USER = "testes"
VM_PASS = "Pedromira28@"
LOCAL_ISO = r"C:\Users\pedro\Desktop\HEAK\FusionOS-Live-x86_64.iso"
REMOTE_ISO = "/home/testes/FusionOS/output/FusionOS-Live-x86_64.iso"

print(f"[*] Tentando conectar a {VM_USER}@{VM_IP}...")
for attempt in range(1, 30):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(VM_IP, port=VM_PORT, username=VM_USER, password=VM_PASS, timeout=5)
        print("[+] Conectado via SSH!")
        
        # Garante permissão de leitura
        ssh.exec_command(f"echo {VM_PASS} | sudo -S chmod 644 {REMOTE_ISO}")
        time.sleep(1)
        
        sftp = ssh.open_sftp()
        print(f"[*] Verificando tamanho do arquivo na VM...")
        stat = sftp.stat(REMOTE_ISO)
        size_gb = stat.st_size / (1024 * 1024 * 1024)
        print(f"[+] Arquivo encontrado: {REMOTE_ISO} ({size_gb:.2f} GB)")
        
        print(f"[*] Baixando para {LOCAL_ISO}...")
        
        def progress(transferred, total):
            pct = (transferred / total) * 100
            sys.stdout.write(f"\rProgresso: {pct:.1f}% ({transferred / (1024*1024):.1f} MB / {total / (1024*1024):.1f} MB)")
            sys.stdout.flush()

        sftp.get(REMOTE_ISO, LOCAL_ISO, callback=progress)
        sftp.close()
        ssh.close()
        print("\n[✔] SUCESSO! A ISO do FusionOS foi transferida para C:\\Users\\pedro\\Desktop\\HEAK\\FusionOS-Live-x86_64.iso!")
        sys.exit(0)
    except Exception as e:
        time.sleep(2)

print("\n[-] Não foi possível conectar ao SSH ainda.")
sys.exit(1)
