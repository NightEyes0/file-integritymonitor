import hashlib
import hmac
import os
import time
from datetime import datetime

SECRET_KEY = b"fim_super_secret_key_2026"

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

# NEW: Calculates HMAC-SHA256 signature for baseline file verification
def compute_baseline_hmac():
    if not os.path.exists("baseline.txt"):
        return ""
    with open("baseline.txt", "rb") as f:
        return hmac.new(SECRET_KEY, f.read(), hashlib.sha256).hexdigest()

def create_baseline(target_dir="target"):
    with open("baseline.txt", "w") as f:
        for root, _, files in os.walk(target_dir):
            for filename in files:
                path = os.path.join(root, filename)
                f.write(f"{path}|{calculate_hash(path)}\n")
    # NEW: Sign the generated baseline
    with open("baseline.sig", "w") as f:
        f.write(compute_baseline_hmac())
    log_event("BASELINE", "baseline.txt and baseline.sig generated")

def check_integrity(target_dir="target", state_cache=None):
    if not os.path.exists("baseline.txt") or not os.path.exists("baseline.sig"):
        log_event("ERROR", "Missing baseline or signature file. Create baseline first.")
        return

    # NEW: Validate HMAC signature before trusting baseline data
    with open("baseline.sig", "r") as f:
        recorded_sig = f.read().strip()
    if not hmac.compare_digest(compute_baseline_hmac(), recorded_sig):
        log_event("CRITICAL", "BASELINE POISONED! Signature mismatch on baseline.txt")
        return

    with open("baseline.txt", "r") as f:
        baseline = dict(line.strip().split("|") for line in f if "|" in line)

    for path, base_hash in baseline.items():
        curr_hash = calculate_hash(path)
        status = "DELETED" if curr_hash is None else ("TAMPERED" if curr_hash != base_hash else "INTACT")
        if state_cache is None or state_cache.get(path) != status:
            log_event(status, path)
            if state_cache is not None:
                state_cache[path] = status

    for root, _, files in os.walk(target_dir):
        for filename in files:
            path = os.path.join(root, filename)
            if path not in baseline and (state_cache is None or state_cache.get(path) != "UNTRACKED"):
                log_event("UNTRACKED", path)
                if state_cache is not None:
                    state_cache[path] = "UNTRACKED"

def monitor(target_dir="target", interval=3):
    print(f"[*] Monitoring '{target_dir}' recursively every {interval}s (Ctrl+C to quit)...")
    state_cache = {}
    try:
        while True:
            check_integrity(target_dir, state_cache)
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