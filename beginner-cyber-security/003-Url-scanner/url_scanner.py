import requests
from bs4 import BeautifulSoup
import sys
import time
import socket
import ssl
from urllib.parse import urlparse
from colorama import Fore, Style

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

def get_ssl_info(domain):
    context = ssl.create_default_context()
    try:
        with socket.create_connection((domain, 443), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                return {
                    'subject': dict(x[0] for x in cert['subject']),
                    'issuer': dict(x[0] for x in cert['issuer']),
                    'valid_from': cert['notBefore'],
                    'valid_until': cert['notAfter'],
                }
    except Exception as e:
        return {"error": str(e)}

def scan_url(url):
    print(f"{Fore.CYAN}Scanning {url}{Style.RESET_ALL}")
    parsed = urlparse(url)
    domain = parsed.netloc or parsed.path

    try:
        start = time.time()
        response = requests.get(url, headers=headers, timeout=10, allow_redirects=True, verify=True)
        duration = round((time.time() - start), 2)

        # Status
        print(f"{Fore.GREEN}[+] Status Code: {response.status_code}{Style.RESET_ALL}")
        print(f"[+] Redirected To: {response.url}" if response.url != url else "[+] No Redirect")

        # SSL Certificate Info
        ssl_info = get_ssl_info(domain)
        if "error" not in ssl_info:
            print(f"{Fore.YELLOW}[+] SSL Certificate Info:")
            print(f"    Subject: {ssl_info['subject'].get('commonName')}")
            print(f"    Issuer: {ssl_info['issuer'].get('commonName')}")
            print(f"    Valid From: {ssl_info['valid_from']}")
            print(f"    Valid Until: {ssl_info['valid_until']}")
        else:
            print(f"{Fore.RED}[!] SSL Info Error: {ssl_info['error']}{Style.RESET_ALL}")

        # Title Extraction
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.title.string.strip() if soup.title else 'N/A'
        print(f"{Fore.BLUE}[+] Page Title: {title}{Style.RESET_ALL}")

        # Timing
        print(f"[+] Response Time: {duration}s")

        # Basic Vulnerability Patterns
        if "admin" in response.text.lower():
            print(f"{Fore.RED}[!] Warning: Found 'admin' in page content!{Style.RESET_ALL}")

        if "index of /" in response.text.lower():
            print(f"{Fore.RED}[!] Directory listing enabled!{Style.RESET_ALL}")

    except requests.exceptions.RequestException as e:
        print(f"{Fore.RED}[!] Error: {e}{Style.RESET_ALL}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python url_scanner.py <https://target-url>")
        sys.exit(1)

    target_url = sys.argv[1]
    scan_url(target_url)
