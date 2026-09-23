import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.194.129', port=22, username='testes', password='Pedromira28@')

cmd = 'echo Pedromira28@ | sudo -S tail -n 20 /home/testes/FusionOS/output/anaconda/packaging.log 2>/dev/null || echo Pedromira28@ | sudo -S tail -n 20 /tmp/packaging.log'

stdin, stdout, stderr = ssh.exec_command(cmd)
print(stdout.read().decode('utf-8', errors='replace'))
ssh.close()
