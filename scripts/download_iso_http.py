import urllib.request
import sys
import time

URL = "http://192.168.194.131:8000/FusionOS-Live-x86_64.iso"
DEST = r"C:\Users\pedro\Desktop\HEAK\FusionOS-Live-x86_64.iso"

print(f"[*] Aguardando servidor na VM ({URL})...")
connected = False
for _ in range(60):
    try:
        req = urllib.request.Request(URL, method='HEAD')
        with urllib.request.urlopen(req, timeout=2) as resp:
            size_mb = int(resp.headers.get('Content-Length', 0)) / (1024 * 1024)
            print(f"[+] Conectado com sucesso! Tamanho da ISO: {size_mb:.1f} MB")
            connected = True
            break
    except Exception:
        time.sleep(1)

if not connected:
    print("[-] Servidor ainda não iniciado na VM.")
    sys.exit(1)

print(f"[*] Baixando {URL} para {DEST}...")

def reporthook(block_num, block_size, total_size):
    downloaded = block_num * block_size
    if total_size > 0:
        percent = min(100.0, (downloaded / total_size) * 100)
        mb_down = downloaded / (1024 * 1024)
        mb_tot = total_size / (1024 * 1024)
        sys.stdout.write(f"\rBaixando ISO: {percent:.1f}% ({mb_down:.1f} MB / {mb_tot:.1f} MB)")
        sys.stdout.flush()

urllib.request.urlretrieve(URL, DEST, reporthook)
print("\n[✔] DOWNLOAD CONCLUÍDO! A ISO está salva em:")
print(f"    {DEST}")

