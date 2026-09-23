import socket
import concurrent.futures

def check_ip(ip):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.3)
    try:
        if s.connect_ex((ip, 22)) == 0:
            s.close()
            return ip
    except Exception:
        pass
    s.close()
    return None

ips = [f"192.168.194.{i}" for i in range(2, 255)] + [f"192.168.137.{i}" for i in range(2, 255)]

with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
    results = executor.map(check_ip, ips)
    for r in results:
        if r:
            print(f"FOUND: {r}", flush=True)

