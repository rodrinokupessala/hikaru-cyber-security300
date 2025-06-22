import subprocess
from rich.console import Console
from rich.table import Table
import re
import socket

console = Console()

PADROES_ALTOS = ['cmd=', 'bash', 'eval', 'system(', 'powershell', 'base64', 'nc ', 'wget', 'curl', 'python -c']
PADROES_MEDIOS = ['User-Agent:', 'Suspicious', 'Content-Type: application/x-www-form-urlencoded']

def get_ip_local():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_local = s.getsockname()[0]
        s.close()
        return ip_local
    except:
        return "127.0.0.1"

def classificar_payload(payload):
    for padrao in PADROES_ALTOS:
        if padrao.lower() in payload.lower():
            return "ALTO"
    for padrao in PADROES_MEDIOS:
        if padrao.lower() in payload.lower():
            return "MÉDIO"
    return "BAIXO"

def monitorar(ip_servidor, ip_local):
    console.print(f"[bold cyan]📡 SOC em {ip_local} monitorando tráfego de entrada para o servidor {ip_servidor}[/bold cyan]")
    console.print("🔐 Requer root. Pressione Ctrl+C para parar.\n")

    try:
        comando = ["sudo", "tcpdump", "-nAl", "-i", "any", f"dst host {ip_servidor} and tcp"]
        proc = subprocess.Popen(comando, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)

        buffer_pacote = ""
        for linha in proc.stdout:
            if linha.strip() == "":
                if buffer_pacote:
                    risco = classificar_payload(buffer_pacote)
                    origem = re.search(r'IP ([\d\.]+)', buffer_pacote)
                    destino = re.search(r'> ([\d\.]+)\.(\d+):', buffer_pacote)
                    if origem and destino:
                        src = origem.group(1)
                        dst = destino.group(1)
                        porta = destino.group(2)

                        tabela = Table(show_lines=True)
                        tabela.add_column("Origem", style="green")
                        tabela.add_column("Destino", style="cyan")
                        tabela.add_column("Porta", style="magenta")
                        tabela.add_column("Risco", style="bold red")
                        tabela.add_column("Indício", style="yellow")

                        tabela.add_row(src, dst, porta, risco, buffer_pacote[:60].replace("\n", " ") + "...")
                        console.print(tabela)
                buffer_pacote = ""
            else:
                buffer_pacote += linha

    except KeyboardInterrupt:
        console.print("\n[bold red]🛑 Monitoramento encerrado pelo usuário.[/bold red]")
    except Exception as e:
        console.print(f"[bold red]Erro:[/bold red] {e}")

if __name__ == "__main__":
    ip_local = get_ip_local()
    console.print(f"[bold green]IP local do SOC detectado automaticamente:[/bold green] {ip_local}")
    ip_servidor = input("Digite o IP do servidor a monitorar (ex: 172.18.96.1): ").strip()
    monitorar(ip_servidor, ip_local)
