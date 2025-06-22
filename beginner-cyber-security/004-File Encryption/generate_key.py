from cryptography.fernet import Fernet
import os

# File name for the key
KEY_FILE = "secret.key"

# Generate and save the key
def generate_key():
    if os.path.exists(KEY_FILE):
        print(f"[!] Key already exists at '{KEY_FILE}'.")
    else:
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as key_file:
            key_file.write(key)
        print(f"[+] Key generated and saved to '{KEY_FILE}'.")

if __name__ == "__main__":
    generate_key()
