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

# Scans directory and writes file signatures to baseline.txt
def create_baseline(target_dir="target"):
    with open("baseline.txt", "w") as f:
        for filename in os.listdir(target_dir):
            path = os.path.join(target_dir, filename)
            if os.path.isfile(path):
                f.write(f"{path}|{calculate_hash(path)}\n")
    print("[+] Baseline created in baseline.txt")

#  Automatically prepares a target directory and records baseline
if __name__ == "__main__":
    if not os.path.exists("target"):
        os.makedirs("target")
    create_baseline()