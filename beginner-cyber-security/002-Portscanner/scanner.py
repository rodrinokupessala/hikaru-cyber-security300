#!/usr/bin/env python3
import argparse
import socket
import threading
import time
import random
import shutil
import subprocess
from queue import Queue
from colorama import init, Fore

init(autoreset=True)

# ---------- Global settings ----------
COMMON_PORTS = [21, 22, 23, 25, 53, 80, 110, 135, 139, 143, 443, 445, 993, 995,
                1433, 1521, 1723, 3306, 3389, 5060, 5900, 8080, 8443]

THREADS = 100
TIMEOUT = 1.5
SRC_PORT = 53
queue = Queue()
lock = threading.Lock()

# ---------- Banner grabbing ----------
def banner_grab(ip, port):
    try:
        with socket.create_connection((ip, port), timeout=TIMEOUT) as s:
            s.sendall(b'HEAD / HTTP/1.0\r\n\r\n')
            return s.recv(1024).decode(errors='ignore').strip()
    except Exception:
        return None

# ---------- TCP and UDP scan ----------
def tcp_scan(ip, port, banners, bypass):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(TIMEOUT)
            if bypass:
                try: s.bind(('', SRC_PORT))
                except: pass
            r = s.connect_ex((ip, port))
            if r == 0:
                with lock:
                    print(f"{Fore.GREEN}[+] TCP {port} OPEN", end="")
                    if banners:
                        b = banner_grab(ip, port)
                        print(f" - {Fore.YELLOW}{b}" if b else "")
                    else: print()
    except Exception as e:
        with lock:
            print(f"{Fore.RED}[!] TCP {port} error: {e}")

def udp_scan(ip, port, bypass):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.settimeout(TIMEOUT + 1)
            if bypass:
                try: s.bind(('', SRC_PORT))
                except: pass
            s.sendto(b'', (ip, port))
            try:
                d, _ = s.recvfrom(512)
                with lock:
                    print(f"{Fore.GREEN}[+] UDP {port} responded ({len(d)} bytes)")
            except socket.timeout:
                with lock:
                    print(f"{Fore.YELLOW}[?] UDP {port} open|filtered")
    except Exception as e:
        with lock:
            print(f"{Fore.RED}[!] UDP {port} error: {e}")

def worker(ip, scan_type, banners, bypass, delay):
    while True:
        port = queue.get()
        if scan_type == 'tcp':
            tcp_scan(ip, port, banners, bypass)
        else:
            udp_scan(ip, port, bypass)
        queue.task_done()
        if delay:
            time.sleep(delay)

# ---------- Nmap helper ----------
def nmap_available():
    return shutil.which("nmap") is not None

def nmap_stealth(ip, ports, scan_type):
    if not nmap_available():
        print(f"{Fore.RED}[!] Nmap not found; fallback to internal scan.")
        return
    port_arg = ','.join(map(str, ports))
    nmap_cmd = ["nmap", "-Pn", "-T2", "--source-port", "53", "-f", "-p", port_arg,
                "-sS" if scan_type == "tcp" else "-sU", ip]
    print(f"{Fore.CYAN}[*] Nmap stealth scan:\n{' '.join(nmap_cmd)}\n")
    try:
        out = subprocess.check_output(nmap_cmd, stderr=subprocess.STDOUT)
        print(out.decode(errors="ignore"))

    except subprocess.CalledProcessError as e:
        print(e.output.decode())

# ---------- Port parsing ----------
def parse_ports(arg: str, default_udp=False):
    if arg:
        parts = arg.split(',')
        out = []
        for p in parts:
            if '-' in p:
                a, b = map(int, p.split('-'))
                out.extend(range(a, b + 1))
            else:
                out.append(int(p))
        return sorted(set(out))
    return COMMON_PORTS if not default_udp else [53, 67, 68, 123, 161, 500]

# ---------- Main ----------
def main():
    global THREADS, TIMEOUT

    parser = argparse.ArgumentParser(
        description="Advanced Port Scanner (TCP/UDP) with firewall bypass")
    parser.add_argument("-t", "--target", required=True, help="Target IP or hostname")
    parser.add_argument("-s", "--scan-type", choices=['tcp', 'udp'], default='tcp',
                        help="Scan type: tcp or udp (default: tcp)")
    parser.add_argument("-p", "--ports",
                        help="Ports: '22,80,443' or range '20-443'. Defaults to top ports")
    parser.add_argument("-b", "--banner", action="store_true", help="Enable banner grabbing (TCP only)")
    parser.add_argument("--firewall-bypass", action="store_true",
                        help="Attempt stealth scan via Nmap or internal bypass")
    parser.add_argument("--threads", type=int, default=THREADS,
                        help="Number of threads (default: 100)")
    parser.add_argument("--timeout", type=float, default=TIMEOUT,
                        help="Socket timeout in seconds (default: 1.5)")
    parser.add_argument("--delay", type=float, default=0.0,
                        help="Delay between scans (default: 0.0)")

    args = parser.parse_args()

    THREADS = args.threads
    TIMEOUT = args.timeout

    ports = parse_ports(args.ports, default_udp=(args.scan_type == 'udp'))

    if args.firewall_bypass and nmap_available():
        nmap_stealth(args.target, ports, args.scan_type)
        return

    if args.firewall_bypass:
        random.shuffle(ports)
        if args.delay == 0.0:
            args.delay = 0.25  # slow down scan to reduce detection

    print(f"{Fore.CYAN}[+] Scanning {args.target} ({args.scan_type.upper()}) "
          f"| Ports: {len(ports)} | Threads: {THREADS}")

    for _ in range(THREADS):
        threading.Thread(
            target=worker,
            args=(args.target, args.scan_type, args.banner, args.firewall_bypass, args.delay),
            daemon=True
        ).start()

    for port in ports:
        queue.put(port)
    queue.join()
    print(f"\n{Fore.GREEN}[✓] Scan completed\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}[!] Interrupted by user. Exiting.")
