import psutil
import re
import time
from pathlib import Path

SIGNATURE_FILE = "process_signatures.txt"
CHECK_INTERVAL = 0.5  # segundos

def load_signatures(path):
    signatures = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "::" not in line:
                print(f"⚠️ Invalid signature format: {line}")
                continue
            name, pattern = map(str.strip, line.split("::", 1))
            signatures.append({"name": name, "pattern": pattern})
    return signatures

def check_new_processes(seen_pids, signatures):
    current_pids = set()
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            pid = proc.info['pid']
            current_pids.add(pid)

            if pid not in seen_pids:
                cmdline = " ".join(proc.info['cmdline']) if proc.info['cmdline'] else ""
                for sig in signatures:
                    if re.search(sig["pattern"], cmdline, re.IGNORECASE):
                        print(f"\n🚨 Signature matched: {sig['name']}")
                        print(f"    PID: {pid}, Name: {proc.info['name']}")
                        print(f"    Command Line: {cmdline}\n")

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    seen_pids.clear()
    seen_pids.update(current_pids)

def wait_for_signature_file(path):
    print(f"🕒 Waiting for signature file: {path} ...")
    while not Path(path).exists():
        time.sleep(1)
    print("✅ Signature file found.\n")

if __name__ == "__main__":
    seen_pids = set()

    try:
        if not Path(SIGNATURE_FILE).exists():
            wait_for_signature_file(SIGNATURE_FILE)

        signatures = load_signatures(SIGNATURE_FILE)

        print("🛡️ Process monitor started. Waiting for new processes... (Press Ctrl+C to stop)\n")
        seen_pids.update(p.info['pid'] for p in psutil.process_iter(['pid']))

        while True:
            check_new_processes(seen_pids, signatures)
            time.sleep(CHECK_INTERVAL)

    except KeyboardInterrupt:
        print("\n🛑 Monitoring stopped by user.")
