import socket
import time

def check_vm():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    try:
        s.connect(('192.168.194.129', 22))
        s.close()
        return True
    except Exception:
        return False

print("VM status:", check_vm())

