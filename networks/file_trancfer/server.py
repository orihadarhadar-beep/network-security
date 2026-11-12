import os
import socket

SERVER_IP = "127.0.0.1" 
SERVER_PORT = 3000
SAVE_PATH = r"C:\\Users\\hyani\\Downloads\\t1"



def start_server(save_dir, server_ip, server_port):
    os.makedirs(save_dir, exist_ok=True)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((server_ip, server_port))
        s.listen(5) 
        print(f"Server listening on {server_ip}:{server_port}...")

        while True:
            try:
                conn, addr = s.accept()
                with conn:
                    file_name = conn.recv(1024)
                    full_path = os.path.join(save_dir, os.path.basename(file_name.decode()))
                    conn.sendall(b"ACK")  # Acknowledge receipt of the file name
                    with open(full_path, "wb") as f:
                        while True:
                            data = conn.recv(1024)
                            if not data:
                                break
                            f.write(data)
                    print(f"File '{file_name.decode()}' saved to '{full_path}'.")
            except Exception as e:
                print(f"Error accepting connection: {e}")
                continue
                 
                


if __name__ == "__main__":
    start_server(SAVE_PATH, SERVER_IP, SERVER_PORT)
