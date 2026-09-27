import hashlib
import os
import time
from datetime import datetime

# Appends timestamped events to both console and audit.log
def log_event(status, path):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] {status}: {path}"
    print(entry)
    with open("audit.log", "a") as f:
        f.write(entry + "\n")

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
    log_event("BASELINE", "baseline.txt written successfully")

def check_integrity(target_dir="target"):
    if not os.path.exists("baseline.txt"):
        log_event("ERROR", "No baseline found. Create one first.")
        return
    with open("baseline.txt", "r") as f:
        baseline = dict(line.strip().split("|") for line in f)

    for path, base_hash in baseline.items():
        curr_hash = calculate_hash(path)
        if curr_hash is None:
            log_event("DELETED", path)
        elif curr_hash != base_hash:
            log_event("TAMPERED", path)
        else:
            log_event("INTACT", path)

    for filename in os.listdir(target_dir):
        path = os.path.join(target_dir, filename)
        if os.path.isfile(path) and path not in baseline:
            log_event("UNTRACKED", path)

def monitor(target_dir="target", interval=3):
    print(f"[*] Monitoring '{target_dir}' every {interval}s (Ctrl+C to quit)...")
    try:
        while True:
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