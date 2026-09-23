import sys
import paramiko

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.194.129', port=22, username='testes', password='Pedromira28@')

def run(cmd):
    print(f"=== {cmd} ===")
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print(stdout.read().decode('utf-8', errors='replace'))

run("df -h /")
run("free -h")
run("ps aux | grep -E 'mksquashfs|xorriso|livemedia' | grep -v grep")
run("ls -lh /var/tmp/lmc-work-1ukzc811/images/ 2>/dev/null")
run("ls -lh /home/testes/FusionOS/output/ 2>/dev/null")

ssh.close()
