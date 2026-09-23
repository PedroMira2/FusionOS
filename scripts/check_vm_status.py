import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.194.129', port=22, username='testes', password='Pedromira28@', timeout=10)

def run(cmd):
    print(f"=== {cmd} ===")
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print(stdout.read().decode('utf-8', errors='ignore'))
    err = stderr.read().decode('utf-8', errors='ignore')
    if err:
        print("[STDERR]", err)

# Kill hung anaconda processes
run("echo Pedromira28@ | sudo -S killall -9 anaconda livemedia-creator 2>/dev/null; sleep 2")
run("echo Pedromira28@ | sudo -S umount -f /mnt/sysroot 2>/dev/null; echo Pedromira28@ | sudo -S losetup -D 2>/dev/null")
run("echo Pedromira28@ | sudo -S rm -rf /home/testes/FusionOS/output /var/tmp/dnf* /tmp/dnf* /tmp/lmc* /run/anaconda.pid 2>/dev/null")
run("df -h /")

ssh.close()

