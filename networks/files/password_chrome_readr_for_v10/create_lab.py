import os
import json
import base64
import sqlite3
import win32crypt
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

def setup_lab():
    master_key = get_random_bytes(32)

    encrypted_key_dpapi = win32crypt.CryptProtectData(master_key, None, None, None, None, 0)
    key_with_prefix = b"DPAPI" + encrypted_key_dpapi
    b64_key = base64.b64encode(key_with_prefix).decode("utf-8")

    local_state_data = {
        "os_crypt": {
            "encrypted_key": b64_key
        }
    }
    with open("mock_local_state.json", "w", encoding="utf-8") as f:
        json.dump(local_state_data, f, indent=4)

    db_name = "mock_login_data.db"
    if os.path.exists(db_name):
        os.remove(db_name)

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE logins (
            origin_url TEXT,
            username_value TEXT,
            password_value BLOB
        )
    """)

    dummy_entries = [
        ("https://example-bank.local", "student_user", "MySecretPass123!"),
        ("https://university-portal.local", "cyber_learner", "P@ssw0rd2026"),
        ("https://test-mail.local", "admin@lab.local", "AdminLab#99")
    ]

    for url, user, plain_password in dummy_entries:
        iv = get_random_bytes(12)  
        cipher = AES.new(master_key, AES.MODE_GCM, iv)
        ciphertext, tag = cipher.encrypt_and_digest(plain_password.encode("utf-8"))

        encrypted_blob = b"v10" + iv + ciphertext + tag
        cursor.execute("INSERT INTO logins VALUES (?, ?, ?)", (url, user, encrypted_blob))

    conn.commit()
    conn.close()
    print("[+] Lab environment created successfully!")
    print("[+] Created files: 'mock_local_state.json' and 'mock_login_data.db'")

if __name__ == "__main__":
    setup_lab()
