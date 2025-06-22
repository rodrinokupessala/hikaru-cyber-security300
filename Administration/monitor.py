import subprocess
from rich.console import Console
from rich.table import Table
import re

console = Console()

PADROES_ALTOS = ['cmd=', 'bash', 'eval', 'system(', 'powershell', 'base64', 'nc ', 'wget', 'curl', 'python -c']
PADROES_MEDIOS = ['User-Agent:', 'Suspicious', 'Content-Type: application/x-www-form-urlencoded']

def classificar_payload(payload):
    for padrao in PADROES_ALTOS:
        if padrao.lower() in payload.lower():
            return "ALTO"
    for padrao in PADROES_MEDIOS:
        if padrao.lower() in payload.lower():
            return "MÉDIO"
    return "BAIXO"

def monitorar():
    console.print("[bold cyan]📡 Monitor de Rede com Classificação de Risco[/bold cyan]")
    console.print("🔐 Requer root. Pressione Ctrl+C para parar.\n")

    try:
        comando = ["sudo", "tcpdump", "-nAl", "-i", "any", "tcp"]
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
                        tabela.add_row(src, dst, porta, risco, buffer_pacote[:50].replace("\n", " ") + "...")
                        console.print(tabela)
                buffer_pacote = ""
            else:
                buffer_pacote += linha
    except KeyboardInterrupt:
        console.print("\n[bold red]🛑 Monitoramento encerrado pelo usuário.[/bold red]")
    except Exception as e:
        console.print(f"[bold red]Erro:[/bold red] {e}")

if __name__ == "__main__":
    monitorar()
