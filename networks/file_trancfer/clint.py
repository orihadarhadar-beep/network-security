import socket
server_ip = "127.0.0.1"
server_port = 3000


def send_file(file_path, server_ip, server_port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((server_ip, server_port))
            file_name = file_path.split("\\")[-1]
            if len(file_name) > 255:
                file_name = file_name[:255]  # Truncate to 255 characters if necessary
            s.sendall(file_name.encode())  # Send the name
            rec = s.recv(1024)  
            while rec != b"ACK":
                chunk = s.recv(1024)
                if not chunk:
                    break
                rec += chunk

            
            if rec != b"ACK":
                print("Did not receive ACK from server. Aborting file transfer.")
                return

            with open(file_path, 'rb') as file:
                while True:
                    data = file.read(1024)
                    if not data:
                        break
                    s.sendall(data)
            
            print(f"File '{file_path}' sent successfully to {server_ip}:{server_port}.")
    
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
    except Exception as e:
        print(f"An error occurred while sending the file: {e}")

if __name__ == "__main__":
    file_path = input("Enter the path of the file to send: ")
    send_file(file_path, server_ip, server_port)
