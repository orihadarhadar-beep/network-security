import os
from pynput.keyboard import Listener as KeyboardListener
from pynput.keyboard import  Key
from pynput.mouse import Button,Listener as MouseListener
import socket
import threading




def create_server():
    server_socket = socket.socket(
        socket.AF_INET, socket.SOCK_STREAM
    )  # Create TCP Socket object
    server_socket.bind(("127.0.0.1", 8080))  # Define the IP + Port for the server
    server_socket.listen(
        5
    )  # Define maximum amount of connections waiting to be accepted
    print(f"Listening for new connections")
    return server_socket


def accept_client(server_socket):
    client_socket, client_address = server_socket.accept()
    print(f"Connection established with {client_address}")
    return client_socket



def mouse_thread(client_socket):
    try:
        def on_move(x, y):
            message = f"move,{x},{y}\n"
            client_socket.send(message.encode())

        def on_click(x, y, button, pressed):
            message = f"click,{x},{y},{button.name},{pressed}\n"
            client_socket.send(message.encode())

        def on_scroll(x, y, dx, dy):
            message = f"scroll,{x},{y},{dx},{dy}\n"
            client_socket.send(message.encode())


        with MouseListener(on_click=on_click, on_scroll=on_scroll,on_move=on_move) as listener:
            listener.join()
    except Exception as e:
        print(f"Eror :{e}")



def keyboard_lisener_thread(client_socket):
    try:
        def send_keyboard_click(key):
            if key == Key.esc:
                print("got esc------")
                client_socket.close()
                os._exit(0)
            if hasattr(key, "char") and key.char is not None:
                key_str = f"CHAR:{key.char}\n"
            elif hasattr(key, "name"):
                key_str = f"SPECIAL:{key.name}\n"
            else:
                key_str = f"VK:{key.vk}\n"
            
            client_socket.send(key_str.encode())
            print(f"Sent key: {key}")

        with KeyboardListener(on_press=send_keyboard_click) as listener:
            listener.join()
    except Exception as e:
        print(f"Eror :{e}")


def main(server_socket):    
    client_socket = accept_client(server_socket)
    thread_keyboard = threading.Thread(target= keyboard_lisener_thread, args=(client_socket,))
    thread_keyboard.start()

    client_socket = accept_client(server_socket)
    thread_mouse = threading.Thread(target= mouse_thread, args=(client_socket,))
    thread_mouse.start()

    thread_keyboard.join()
    thread_mouse.join()


if __name__ == "__main__":
    server_socket = create_server()
    while True:
        try:
            main(server_socket)
        except Exception as e:
            print(f"Eror: {e}")
    
