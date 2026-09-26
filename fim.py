import hashlib

def calculate_hash(filepath):
    sha256 = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            while chunk := f.read(65536):
                sha256.update(chunk)
        return sha256.hexdigest()
    except FileNotFoundError:
        return None

if __name__ == "__main__":
    print("File Integrity Monitor initialized.")