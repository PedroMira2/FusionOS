import sys
import paramiko

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.194.129', port=22, username='testes', password='Pedromira28@')

stdin, stdout, stderr = ssh.exec_command('which mkefiboot')
print(stdout.read().decode('utf-8', errors='replace'))

ssh.close()
