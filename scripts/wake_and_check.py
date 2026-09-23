import sys
import paramiko

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

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

# Disable sleep / screen blanking permanently so screen stays active
run("echo Pedromira28@ | sudo -S systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target")

# Simulate user activity to wake up screen
run("gsettings set org.gnome.desktop.session idle-delay 0 2>/dev/null; gsettings set org.gnome.settings-daemon.plugins.power sleep-inactive-ac-type 'nothing' 2>/dev/null")

# Check running processes
run("ps aux | grep -E 'build-iso|livemedia|anaconda|lorax' | grep -v grep")
run("uptime")

ssh.close()
