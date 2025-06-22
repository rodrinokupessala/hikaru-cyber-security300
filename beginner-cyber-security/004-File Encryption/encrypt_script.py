import os
from cryptography.fernet import Fernet

KEY_FILE = "secret.key"
SAMPLE_FILE = "example.txt"

# Load the previously generated key
def load_key():
    if not os.path.exists(KEY_FILE):
        raise FileNotFoundError(f"[!] The key file '{KEY_FILE}' was not found. Generate it first using generate_key.py.")
    return open(KEY_FILE, "rb").read()

# Encrypt a file
def encrypt_file(file_name, key):
    # Create file if it doesn't exist
    if not os.path.exists(file_name):
        print(f"[!] File '{file_name}' not found. Creating a sample...")
        with open(file_name, "w") as f:
            f.write("This is a sample text to encrypt.")
    fernet = Fernet(key)
    with open(file_name, "rb") as file:
        data = file.read()
    encrypted = fernet.encrypt(data)
    with open(file_name + ".enc", "wb") as file:
        file.write(encrypted)
    print(f"[+] Encrypted file saved as '{file_name}.enc'.")

# Decrypt a file
def decrypt_file(encrypted_file_name, key):
    if not os.path.exists(encrypted_file_name):
        print(f"[!] Encrypted file '{encrypted_file_name}' not found.")
        return
    fernet = Fernet(key)
    with open(encrypted_file_name, "rb") as file:
        encrypted_data = file.read()
    decrypted = fernet.decrypt(encrypted_data)
    output_file = "dec_" + encrypted_file_name.replace(".enc", "")
    with open(output_file, "wb") as file:
        file.write(decrypted)
    print(f"[+] Decrypted file saved as '{output_file}'.")

# Main logic
if __name__ == "__main__":
    key = load_key()

    # Encrypt
    encrypt_file(SAMPLE_FILE, key)

    # Decrypt
    decrypt_file(SAMPLE_FILE + ".enc", key)
