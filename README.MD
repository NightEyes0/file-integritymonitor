# Host-Based File Integrity Monitor (FIM)

A lightweight, real-time File Integrity Monitoring utility built with Python. Designed to detect unauthorized file tampering, backdoor drops, and deletions across sensitive directories using streaming SHA-256 cryptographic hashing.

## Core Capabilities
* **Streaming Cryptographic Hashing:** Processes files in 64KB chunks via `hashlib.sha256` to maintain a constant $O(1)$ memory footprint, safely scanning files of any size.
* **Tamper & Deletion Detection:** Compares active file states against an established baseline file signature record (`baseline.txt`).
* **Untracked File Detection:** Identifies unbaselined files and potential adversary persistence artifacts (e.g., webshells, scripts).
* **State Caching & Deduplication:** Tracks file lifecycle transitions to suppress redundant alert spam and combat alert fatigue.
* **Persistent Forensic Logging:** Formats and writes all security events with ISO timestamps (`YYYY-MM-DD HH:MM:SS`) to both stdout and a persistent `audit.log`.

## Detection Lifecycle
| State | Trigger Condition |
|---|---|
| `INTACT` | File hash matches recorded baseline checksum |
| `TAMPERED` | File hash differs from recorded baseline checksum |
| `DELETED` | Baseline file record is missing from filesystem |
| `UNTRACKED`| Discovered file not documented in baseline signature |

## Usage

### 1. Initialize Baseline
Generate cryptographic signatures for all target assets:
```bash
python fim.py
# Select Option 1