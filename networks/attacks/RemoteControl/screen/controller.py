import io
import os
import socket
import struct
import cv2
import numpy as np
from PIL import Image

SIZE_BITS = 4
ESC_KEY_ASCII = 27
def create_server(port = 1337):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("0.0.0.0", port)) 
    server_socket.listen(5) 
    print(f"Listening for new connections")
    return server_socket


def accept_client(server_socket):
    client_socket, client_address = server_socket.accept()
    print(f"Connection established with {client_address}")
    return client_socket


def get_data(client_socket,size):
    data = b""
    while len(data) < size:
        chunk = client_socket.recv(size - len(data))
        if not chunk:
            raise ConnectionError("")
        data += chunk

    return data


def exit_df(num=0):
    print("end the pro")
    cv2.waitKey(0)
    os._exit(num)


def server_screen_thread(client_socket):
    try:
        while True:
            size = get_data(client_socket,SIZE_BITS)
            frame_size = struct.unpack(">L", size)[0]

            data = get_data(client_socket,frame_size)
            frame_data = io.BytesIO(data)


            pil_image = Image.open(frame_data)
            frame = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

            cv2.imshow("Remote Screen", frame)

            if cv2.waitKey(1) & 0xFF == ESC_KEY_ASCII:
                exit_df()
    except ConnectionError:
        print("Client disconnected")
        exit_df()
    except ConnectionResetError:
        print("Client disconnected")
        exit_df()    


if __name__ == "__main__":
    server_socket =  create_server()
    client_socket = accept_client(server_socket)
    server_screen_thread(client_socket)