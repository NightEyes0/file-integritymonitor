import hashlib
import os
import time

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

def check_integrity(target_dir="target"):
    if not os.path.exists("baseline.txt"):
        print("[-] Error: No baseline found. Create one first.")
        return
    with open("baseline.txt", "r") as f:
        baseline = dict(line.strip().split("|") for line in f)

    for path, base_hash in baseline.items():
        curr_hash = calculate_hash(path)
        if curr_hash is None:
            print(f"[!] DELETED: {path}")
        elif curr_hash != base_hash:
            print(f"[!] TAMPERED: {path}")
        else:
            print(f"[+] INTACT: {path}")

    for filename in os.listdir(target_dir):
        path = os.path.join(target_dir, filename)
        if os.path.isfile(path) and path not in baseline:
            print(f"[!] NEW/UNTRACKED: {path}")

# Continuous polling loop with graceful shutdown
def monitor(target_dir="target", interval=3):
    print(f"[*] Monitoring '{target_dir}' every {interval}s (Ctrl+C to quit)...")
    try:
        while True:
            print("--- Scan Cycle ---")
            check_integrity(target_dir)
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\n[-] Monitoring stopped.")

if __name__ == "__main__":
    choice = input("Select mode - (1) Baseline, (2) Verify, (3) Live Monitor: ").strip()
    if choice == "1":
        create_baseline()
    elif choice == "2":
        check_integrity()
    else:
        monitor()