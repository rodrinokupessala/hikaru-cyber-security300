import os
from pathlib import Path

def load_signatures(path):
    with open(path, encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def scan_file(file_path, signatures):
    try:
        with open(file_path, encoding="utf-8", errors="ignore") as f:
            content = f.read()
            for sig in signatures:
                if sig.lower() in content.lower():
                    print(f"🚨 VIRUS DETECTED: '{sig}' found in {file_path}")
                    return True
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")
    return False

def scan_directory(directory, signatures):
    print(f"🔎 Scanning directory: {directory}")
    directory = Path(directory)
    for file_path in directory.rglob("*"):
        if file_path.is_file():
            scan_file(file_path, signatures)

if __name__ == "__main__":
    signatures_path = "virus_signatures.txt"
    target_dir = "scan_targets"

    if not Path(signatures_path).exists():
        print("⚠️ Signature file not found.")
        exit(1)

    signatures = load_signatures(signatures_path)
    scan_directory(target_dir, signatures)
