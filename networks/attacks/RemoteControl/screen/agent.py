import io
import os
import socket
import struct
import time
import pyautogui


def create_client(ip = "127.0.0.1",port = 1337):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create TCP Socket object
    client_socket.connect((ip, port))
    print("Client connected")
    return client_socket


def client_screen_thread(client_socket,exit_df = os._exit):
    try:
        while True:
            screenshot = pyautogui.screenshot()

            # Encode the frame
            frame_buffer = io.BytesIO()
            screenshot.save(frame_buffer, format="JPEG")
            frame_data = frame_buffer.getvalue()

            # Send the size of the frame
            frame_size = len(frame_data)
            client_socket.sendall(struct.pack(">L", frame_size))

            # Send the frame
            client_socket.sendall(frame_data)
            time.sleep(0.1)
    except ConnectionError:
        print("Client disconnected")
        exit_df(0)
    except ConnectionResetError:
        print("Client disconnected")
        exit_df(0)  


if __name__ == "__main__":
    client_socket =  create_client()
    client_screen_thread(client_socket)
