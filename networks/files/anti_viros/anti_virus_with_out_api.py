import os
import io
import csv
import hashlib
import zipfile
import requests

try:
    import yara
    YARA_AVAILABLE = True
except Exception as e:
    print(f"Warning: YARA could not be loaded ({e}). Running in Hash-only mode.")
    YARA_AVAILABLE = False


def get_auth_key(auth_key_path):
    with open(auth_key_path, "r", encoding="utf-8") as key_file:
        return key_file.read().strip()


class AntiVirus:
    def __init__(self, dir_path, auth_key_path, yara_rules_path=None):
        self.dir_path = dir_path
        self.auth_key = get_auth_key(auth_key_path)
        # Download the hash database once upon initialization
        self.known_hashes = self.get_new_hashlist()
        self.yara_rules = self.load_yara_rules(yara_rules_path)

    def load_yara_rules(self, rules_path):
        if not rules_path or not YARA_AVAILABLE:
            return None
        if os.path.exists(rules_path):
            return yara.compile(filepath=rules_path)
        print(f"Warning: YARA rules file '{rules_path}' not found.")
        return None

    def get_new_hashlist(self):
        url = f"https://mb-api.abuse.ch/v2/files/exports/{self.auth_key}/full.csv.zip"
        print("Downloading latest malware hashes from MalwareBazaar...")
        
        try:
            response = requests.get(url, timeout=30)
            print(f"Status Code: {response.status_code}")

            if response.status_code == 200:
                with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                    file_name = z.namelist()[0]
                    content = z.read(file_name).decode("utf-8", errors="ignore")

                    # Use a set for O(1) lookup speed
                    hashes = set()
                    lines = (line for line in content.splitlines() if not line.startswith("#"))
                    reader = csv.reader(lines)
                    
                    for row in reader:
                        # In MalwareBazaar full.csv, column index 1 is sha256_hash
                        if len(row) > 1:
                            sha256_hash = row[1].strip().strip('"').lower()
                            if len(sha256_hash) == 64:
                                hashes.add(sha256_hash)

                    print(f"Total unique SHA256 hashes loaded: {len(hashes)}")
                    return hashes
            else:
                print("Download error:", response.text)
        except requests.RequestException as e:
            print(f"Network error while downloading hashes: {e}")

        return set()

    def get_hash_file(self, file_path):
        sha256 = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                # Read in 64KB chunks to support large files efficiently
                for chunk in iter(lambda: f.read(65536), b""):
                    sha256.update(chunk)
            return sha256.hexdigest().lower()
        except OSError as e:
            print(f"Could not read file '{file_path}' for hashing: {e}")
            return None

    def check_yara_rules(self, file_path):
        if not self.yara_rules:
            return False
        try:
            matches = self.yara_rules.match(file_path)
            if matches:
                print(f"[YARA MATCH] {file_path} matched rules: {matches}")
                return True
        except Exception as e:
            print(f"Error scanning '{file_path}' with YARA: {e}")
        return False

    def scan_file(self, file_path):
        # 1. Hash check
        file_hash = self.get_hash_file(file_path)
        if file_hash and file_hash in self.known_hashes:
            print(f"[HASH MATCH] {file_path} is a known malware!")
            return True

        # 2. YARA rules check
        if self.check_yara_rules(file_path):
            return True

        return False

    def scan_dir(self, path=None):
        viruses = []
        if path is None:
            path = self.dir_path

        try:
            items = os.listdir(path)
            if not items:
                return viruses

            for item in items:
                item_path = os.path.join(path, item)
                if os.path.isfile(item_path):
                    if self.scan_file(item_path):
                        viruses.append(item_path)
                elif os.path.isdir(item_path):
                    viruses.extend(self.scan_dir(item_path))

        except FileNotFoundError:
            print(f"Error: The directory '{path}' does not exist.")
        except PermissionError:
            print(f"Error: Permission denied accessing '{path}'.")
        except OSError as e:
            print(f"Error: Could not access '{path}': {e}")

        return viruses


if __name__ == "__main__":
    TARGET_DIR = "C:\\Users\\hyani\\Downloads\\try"
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    AUTH_KEY_FILE = os.path.join(BASE_DIR, "auth_key.txt")
    YARA_FILE = os.path.join(BASE_DIR, "yara-forge-rules-core.yar") # Optional: pass None if you don't have a YARA file yet

    scanner = AntiVirus(dir_path=TARGET_DIR, auth_key_path=AUTH_KEY_FILE, yara_rules_path=YARA_FILE)
    
    print(f"\nStarting scan on '{TARGET_DIR}'...")
    detected_viruses = scanner.scan_dir()

    print("\n--- Scan Complete ---")
    if detected_viruses:
        print(f"Found {len(detected_viruses)} malicious file(s):")
        for virus in detected_viruses:
            print(f" - {virus}")
    else:
        print("No threats detected.")