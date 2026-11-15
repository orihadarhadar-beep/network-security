
import os
import socket
import ssl

SERVER_IP = "127.0.0.1"
SERVER_PORT = 8080

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CERT_FILE = os.path.join(BASE_DIR, "server.crt")
KEY_FILE = os.path.join(BASE_DIR, "server.key")
KEYS_DIR = os.path.join(BASE_DIR, "keys")
def generate_new_key(client_ip):
    random_key = os.urandom(32)
    with open(f"{KEYS_DIR}\\{client_ip}", "wb") as key_file:
        key_file.write(random_key)
    return random_key


def read_existing_key(client_ip):
    with open(f"{KEYS_DIR}\\{client_ip}", "rb") as key_file:
        key = key_file.read()
        return key


def wrap_socket(sock, server_side=True, certfile=None, keyfile=None):
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    if certfile and keyfile:
        context.load_cert_chain(certfile=certfile, keyfile=keyfile)
    return context.wrap_socket(sock, server_side=server_side)


def main(mood = generate_new_key):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((SERVER_IP,SERVER_PORT) )
    sock.listen(1)

    print("Server is listening")
    while True:
        connection, address = sock.accept()
        ssl_connection = wrap_socket(connection, server_side=True, certfile=CERT_FILE, keyfile=KEY_FILE)
        ip, port = ssl_connection.getpeername()
        random_key = mood(ip)
        ssl_connection.sendall(random_key)

if __name__ == "__main__":
    read_mood = input("Do you want to send exist key?(y/n)")
    if read_mood == "y":
        main(read_existing_key)
    else:
        main()
