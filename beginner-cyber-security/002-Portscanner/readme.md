# 🔍 Advanced Port Scanner (Python - Cross Platform)

A fast, flexible, and powerful **port scanning tool** written in Python.  
Works on **Windows**, **Linux**, **macOS**, **WSL**, and **Termux (Android)**.

---

## ⚙️ Features

- ✅ TCP and UDP scanning
- ✅ Banner grabbing (for identifying services)
- ✅ Manual or automatic port range
- ✅ Firewall bypass (via Nmap or internal slow stealth mode)
- ✅ Multi-threaded and customizable
- ✅ CLI interface with argparse
- ✅ Lightweight and portable

---

## 📦 Installation

```bash
git clone https://github.com/your-username/advanced-port-scanner.git
cd advanced-port-scanner
pip install colorama
```

Optional: To use Nmap-based stealth mode, install Nmap:

Linux / Termux: sudo apt install nmap or pkg install nmap

macOS (Homebrew): brew install nmap

Windows: Download Nmap and add it to PATH

🧪 Usage
Run the scanner from terminal:

bash
Copiar
Editar
python scanner.py -t <target> [options]
✅ Options
Option Description
-t, --target Target IP or hostname (required)
-s, --scan-type Scan type: tcp or udp (default: tcp)
-p, --ports Ports to scan (e.g. 22,80,443 or 20-100)
-b, --banner Enable banner grabbing (TCP only)
--firewall-bypass Use Nmap or slow internal scan for stealth
--threads Number of threads (default: 100)
--timeout Timeout per socket in seconds (default: 1.5)
--delay Delay between scans (useful for stealth mode)

💻 Examples

# Scan TCP ports 20–100 with banner grabbing

```bash
python scanner.py -t scanme.nmap.org -s tcp -p 20-100 -b
```

# Scan top common UDP ports

```bash
python scanner.py -t 192.168.1.1 -s udp
```

# Firewall bypass using Nmap

```bash
python scanner.py -t example.com --firewall-bypass
```

# Slow stealth scan without Nmap

```bash
python scanner.py -t 10.10.10.10 -p 1-1024 --firewall-bypass --delay 0.5
```

## 🎥 Demo

```bash
python scanner.py -t scanme.nmap.org -s tcp -p 22,80,443 -b
```

```
[+] Scanning scanme.nmap.org (TCP) | Ports: 3 | Threads: 100

[+] TCP 22 OPEN - Banner: SSH-2.0-OpenSSH_6.6.1p1 Ubuntu-2ubuntu2.13
[+] TCP 80 OPEN - Banner: HTTP/1.1 403 Forbidden
[!] TCP 443 error: [WinError 10061] No connection could be made...

[✓] Scan completed
```

🔐 Legal Disclaimer
⚠️ This tool is for educational and authorized testing purposes only.
Scanning systems without explicit permission is illegal and unethical.

👤 Author
Developer: [Your Name or GitHub Username]
🎯 Part of the Hikaru Cyber Security 300 project

📄 License
MIT License — free to use, modify, and distribute.

📂 Project Structure
bash
Copiar
Editar
advanced-port-scanner/
├── scanner.py # Main Python script
├── README.md # Documentation (this file)
├── LICENSE # MIT License
└── requirements.txt # Python dependencies
🌱 Future Features
