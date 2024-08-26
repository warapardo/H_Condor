import nmap
import paramiko
import time


def scan_range(ip_range, port):
   nm = nmap.PortScanner()
   open_hosts = []  # Lista para armazenar IPs com a porta aberta
  
   try:
       # Realiza o escaneamento da faixa de IPs para a porta específica
       nm.scan(hosts=ip_range, arguments=f'-T4 -p {port}')
      
       # Verifica e coleta os IPs com a porta aberta
       for host in nm.all_hosts():
           print(f'Host: {host} ({nm[host].hostname()})')
           print(f'Estado: {nm[host].state()}')
          
           # Verifica o estado da porta para cada protocolo
           for protocol in nm[host].all_protocols():
               port_state = nm[host][protocol].get(int(port), {'state': 'closed or filtered'})
               if port_state["state"] == 'open':
                   open_hosts.append(host)
               print(f'Port: {port}\tState: {port_state["state"]}')
              
           print('-' * 60)
  
   except nmap.nmap.PortScannerError as e:
       print(f'Erro do Nmap: {e}')
   except Exception as e:
       print(f'Erro durante o escaneamento: {e}')
  
   return open_hosts


def check_service_and_execute_commands(host, ssh_user, ssh_password, port, check_command, commands):
   try:
       # Estabelece a conexão SSH
       ssh = paramiko.SSHClient()
       ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
      
       # Conecta na porta especificada
       ssh.connect(host, username=ssh_user, password=ssh_password, port=port)
      
       # Testa a conectividade SSH antes de tentar executar comandos
       try:
           print(f'Conectando via SSH a {host} na porta {port}...')
           stdin, stdout, stderr = ssh.exec_command(check_command)
           service_status = stdout.read().decode().strip()
           if(service_status == 'active'):
               print(f'\033[32m{service_status}\033[0m')
           elif(service_status == 'inactive'):
               print(f'\033[91m{service_status}\033[0m')
          
          


          
           # Se o serviço não estiver rodando, executa os comandos fornecidos
           if 'inactive' in service_status:
               print(f'O serviço não está rodando em {host}. Executando comandos...')
               for command in commands:
                   print(f'Executando comando: {command}')
                   stdin, stdout, stderr = ssh.exec_command(command)
                   print(f'Saída: {stdout.read().decode().strip()}')
                   print(f'Erro: {stderr.read().decode().strip()}')
                   time.sleep(10)  # Delay de 10 segundos entre os comandos
           else:
               print(f'O serviço está rodando em {host}.')
      
       except paramiko.SSHException as e:
           print(f'Erro ao executar comandos em {host}: {e}')
       finally:
           ssh.close()
  
   except paramiko.SSHException as e:
       print(f'\033[91m Erro SSH em {host}: {e}\033[0m')
   except Exception as e:
       print(f'Erro ao conectar em {host}: {e}')


if __name__ == '__main__':
   ip_range = '143.106.244.1/24'  # Substitua pela faixa de IP que você deseja escanear
   port = 22000 
   ssh_user = 'root' 
   ssh_password = 'rmrs@)!(' 
   check_command = 'systemctl is-active condor.service'  # Comando para verificar se o serviço está rodando
   commands = [
   'curl -fsSL https://get.htcondor.org | sudo GET_HTCONDOR_PASSWORD="htcondor_password" /bin/bash -s -- --no-dry-run --execute 143.106.243.252',
   'scp -o port=22000 lmp_serial $maq:/usr/local/bin/',
   'scp -o port=22000 49-common.config $maq:/etc/condor/config.d/',
   'ssh -p 22000 $maq "apt-get install -y build-essential cmake git libfftw3-dev"',
   'ssh -p 22000 $maq "systemctl restart condor.service"',
   'ssh -p 22000 $maq "systemctl enable condor.service"',
   'ssh -p 22000 $maq "systemctl start condor.service"',
   ]
  
   open_hosts = scan_range(ip_range, port)
  
   # Verifica e executa comandos nos IPs com a porta aberta
   for host in open_hosts:
       check_service_and_execute_commands(host, ssh_user, ssh_password, port, check_command, commands)



