import socket
import threading
from queue import Queue
import subprocess
import platform
import shutil
from colorama import Fore, init

init(autoreset=True)

# Global settings
THREADS = 100
TIMEOUT = 1.5
queue = Queue()
print_lock = threading.Lock()


def banner_grab(ip, port):
    try:
        with socket.create_connection((ip, port), timeout=TIMEOUT) as s:
            s.sendall(b'HEAD / HTTP/1.0\r\n\r\n')
            return s.recv(1024).decode(errors='ignore').strip()
    except Exception:
        return None


def tcp_scan(ip, port, banner_option):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(TIMEOUT)
            result = s.connect_ex((ip, port))
            if result == 0:
                with print_lock:
                    print(f"{Fore.GREEN}[+] TCP {port} OPEN", end="")
                    if banner_option:
                        banner = banner_grab(ip, port)
                        if banner:
                            print(f" - {Fore.YELLOW}Banner: {banner}")
                        else:
                            print()
                    else:
                        print()
    except Exception as e:
        with print_lock:
            print(f"{Fore.RED}[!] Error on TCP {port}: {e}")


def udp_scan(ip, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.settimeout(TIMEOUT)
            s.sendto(b'', (ip, port))
            try:
                data, _ = s.recvfrom(1024)
                with print_lock:
                    print(f"{Fore.GREEN}[+] UDP {port} responded: {data.decode(errors='ignore')}")
            except socket.timeout:
                with print_lock:
                    print(f"{Fore.YELLOW}[?] UDP {port} open|filtered (no response)")
    except Exception as e:
        with print_lock:
            print(f"{Fore.RED}[!] Error on UDP {port}: {e}")


def worker(scan_type, ip, banner_option):
    while True:
        port = queue.get()
        if scan_type == 'tcp':
            tcp_scan(ip, port, banner_option)
        elif scan_type == 'udp':
            udp_scan(ip, port)
        queue.task_done()


def nmap_check():
    return shutil.which("nmap") is not None


def nmap_scan(ip):
    if not nmap_check():
        print(f"{Fore.RED}[!] Nmap is not installed or not in PATH.")
        return
    print(f"{Fore.CYAN}[*] Running OS fingerprint & service detection via Nmap...\n")
    try:
        output = subprocess.check_output(["nmap", "-O", "-sV", ip], stderr=subprocess.STDOUT)
        print(output.decode())
    except subprocess.CalledProcessError as e:
        print(f"{Fore.RED}[!] Nmap error:\n{e.output.decode()}")


def main():
    print(f"{Fore.CYAN}== Advanced Cross-Platform Port Scanner ==")
    target = input("Enter target IP or hostname: ").strip()
    scan_type = input("Scan type (tcp/udp): ").strip().lower()
    banner_option = input("Enable banner grabbing? (yes/no): ").strip().lower() == 'yes'

    try:
        port_start = int(input("Start port: "))
        port_end = int(input("End port: "))
    except ValueError:
        print(f"{Fore.RED}[!] Invalid port range input.")
        return

    print(f"\n{Fore.CYAN}[*] Scanning {target} [{scan_type.upper()}] from port {port_start} to {port_end}\n")

    for _ in range(THREADS):
        t = threading.Thread(target=worker, args=(scan_type, target, banner_option), daemon=True)
        t.start()

    for port in range(port_start, port_end + 1):
        queue.put(port)

    queue.join()

    if input("\nRun Nmap OS & service detection? (yes/no): ").strip().lower() == 'yes':
        nmap_scan(target)

    print(f"\n{Fore.GREEN}[✓] Scan completed.\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}[!] Interrupted by user. Exiting.")
