import os
import io
import csv
import time
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
    CACHE_TTL_SECONDS = 24 * 60 * 60  # 24 hours

    def __init__(self, dir_path, auth_key_path, yara_rules_path=None, cache_file_path=None):
        self.dir_path = dir_path
        self.auth_key = get_auth_key(auth_key_path)
        
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.cache_file_path = cache_file_path or os.path.join(base_dir, "cached_hashes.txt")
        
        # Load hashes from local cache if valid, otherwise download fresh list
        self.known_hashes = self.get_hashlist()
        self.yara_rules = self.load_yara_rules(yara_rules_path)

    def is_cache_valid(self):
        if not os.path.exists(self.cache_file_path):
            return False
        
        file_age = time.time() - os.path.getmtime(self.cache_file_path)
        return file_age < self.CACHE_TTL_SECONDS

    def load_hashes_from_cache(self):
        print(f"Loading cached hashes from '{self.cache_file_path}'...")
        with open(self.cache_file_path, "r", encoding="utf-8") as f:
            hashes = {line.strip() for line in f if line.strip()}
        print(f"Loaded {len(hashes)} cached hashes.")
        return hashes

    def save_hashes_to_cache(self, hashes):
        try:
            with open(self.cache_file_path, "w", encoding="utf-8") as f:
                f.write("\n".join(hashes))
            print(f"Saved {len(hashes)} hashes to local cache.")
        except OSError as e:
            print(f"Warning: Could not save hash cache: {e}")

    def get_hashlist(self):
        if self.is_cache_valid():
            return self.load_hashes_from_cache()
        
        hashes = self.download_new_hashlist()
        if hashes:
            self.save_hashes_to_cache(hashes)
        elif os.path.exists(self.cache_file_path):
            # Fallback to expired cache if download fails
            print("Download failed. Falling back to expired local cache...")
            return self.load_hashes_from_cache()
        return hashes

    def download_new_hashlist(self):
        url = f"https://mb-api.abuse.ch/v2/files/exports/{self.auth_key}/full.csv.zip"
        print("Cache missing or older than 24h. Downloading latest hashes from MalwareBazaar...")
        
        try:
            response = requests.get(url, timeout=30)
            print(f"Status Code: {response.status_code}")

            if response.status_code == 200:
                with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                    file_name = z.namelist()[0]
                    content = z.read(file_name).decode("utf-8", errors="ignore")

                    hashes = set()
                    lines = (line for line in content.splitlines() if not line.startswith("#"))
                    reader = csv.reader(lines)
                    
                    for row in reader:
                        if len(row) > 1:
                            sha256_hash = row[1].strip().strip('"').lower()
                            if len(sha256_hash) == 64:
                                hashes.add(sha256_hash)

                    print(f"Total unique SHA256 hashes downloaded: {len(hashes)}")
                    return hashes
            else:
                print("Download error:", response.text)
        except requests.RequestException as e:
            print(f"Network error while downloading hashes: {e}")

        return set()

    def load_yara_rules(self, rules_path):
        if not rules_path or not YARA_AVAILABLE:
            return None

        if os.path.isfile(rules_path):
            print(f"Compiling YARA rules from '{rules_path}'...")
            return yara.compile(filepath=rules_path)

        if os.path.isdir(rules_path):
            rule_files = {}
            for root, _, files in os.walk(rules_path):
                for file in files:
                    if file.endswith((".yar", ".yara")):
                        full_path = os.path.join(root, file)
                        namespace = os.path.relpath(full_path, rules_path)
                        rule_files[namespace] = full_path

            if rule_files:
                print(f"Compiling {len(rule_files)} YARA rule files...")
                return yara.compile(filepaths=rule_files)

        print(f"Warning: No valid YARA rules found at '{rules_path}'.")
        return None

    def get_hash_file(self, file_path):
        sha256 = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
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
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
    TARGET_DIR = "C:\\Users\\hyani\\Downloads\\try"
    AUTH_KEY_FILE = os.path.join(BASE_DIR, "auth_key2.txt")
    YARA_FILE = os.path.join(BASE_DIR, "yara-rules-core.yar")

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