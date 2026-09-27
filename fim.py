import hashlib
import os

def calculate_hash(filepath):
    sha256 = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            while chunk := f.read(65536):
                sha256.update(chunk)
        return sha256.hexdigest()
    except FileNotFoundError:
        return None

def create_baseline(target_dir="target"):
    with open("baseline.txt", "w") as f:
        for filename in os.listdir(target_dir):
            path = os.path.join(target_dir, filename)
            if os.path.isfile(path):
                f.write(f"{path}|{calculate_hash(path)}\n")
    print("[+] Baseline created in baseline.txt")

# Compares live file hashes against recorded baseline
def check_integrity():
    if not os.path.exists("baseline.txt"):
        print("[-] Error: No baseline found. Create one first.")
        return
    with open("baseline.txt", "r") as f:
        for line in f:
            path, base_hash = line.strip().split("|")
            curr_hash = calculate_hash(path)
            if curr_hash is None:
                print(f"[!] DELETED: {path}")
            elif curr_hash != base_hash:
                print(f"[!] TAMPERED: {path}")
            else:
                print(f"[+] INTACT: {path}")
