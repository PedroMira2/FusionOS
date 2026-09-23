import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.194.131', port=22, username='testes', password='Pedromira28@')

cmd = """
echo "=== PROCESSES ==="
ps aux | grep -E "anaconda|livemedia|dnf|lorax" | grep -v grep

echo "=== DISK USAGE ==="
df -h /

echo "=== ANACONDA / PROGRAM LOGS ==="
tail -n 25 /tmp/program.log 2>/dev/null || tail -n 25 /home/testes/FusionOS/program.log 2>/dev/null

echo "=== LAST LOG FROM LIVEMEDIA ==="
tail -n 20 /tmp/livemedia.log 2>/dev/null || tail -n 20 /home/testes/FusionOS/livemedia.log 2>/dev/null
"""

stdin, stdout, stderr = ssh.exec_command(cmd)
print(stdout.read().decode('utf-8', errors='replace'))
ssh.close()
