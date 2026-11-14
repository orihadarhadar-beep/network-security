import os
from pynput.keyboard import Listener as KeyboardListener
from pynput.keyboard import  Key
from pynput.mouse import Button,Listener as MouseListener
import socket
import threading




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


def safe_send(sock, message, exit_fn=os._exit):
    try:
        sock.sendall(message)
    except (ConnectionError, ConnectionResetError, BrokenPipeError, OSError):
        print("Client disconnected")
        exit_fn(0)


def mouse_lisener_thread(client_socket,exit_df = os._exit):
    try:
        def on_move(x, y):
            message = f"move,{x},{y}\n"
            safe_send(client_socket,message.encode(),exit_df)

        def on_click(x, y, button, pressed):
            message = f"click,{x},{y},{button.name},{pressed}\n"
            safe_send(client_socket,message.encode(),exit_df)

        def on_scroll(x, y, dx, dy):
            message = f"scroll,{x},{y},{dx},{dy}\n"
            safe_send(client_socket,message.encode(),exit_df)


        with MouseListener(on_click=on_click, on_scroll=on_scroll,on_move=on_move) as listener:
            listener.join()
    except ConnectionError:
        print("Client disconnected")
        exit_df(0)
    except ConnectionResetError:
        print("Client disconnected")
        exit_df(0)  



def keyboard_lisener_thread(client_socket,exit_df = os._exit):
    try:
        def send_keyboard_click(key):

            if key == Key.esc:
                print("got esc------")
                try:
                    client_socket.close()
                except Exception:
                    pass
                exit_df(0)


            if hasattr(key, "char") and key.char is not None:
                # Ignore ASCII control characters (like Ctrl+M -> '\r') since Ctrl itself is sent separately
                if ord(key.char) < 32:
                    return
                key_str = f"CHAR:{key.char}\n"
            elif hasattr(key, "name"):
                key_str = f"SPECIAL:{key.name}\n"
            else:
                key_str = f"VK:{key.vk}\n"
            
            client_socket.send(key_str.encode())


        with KeyboardListener(on_press=send_keyboard_click) as listener:
            listener.join()
    except ConnectionError:
        print("Client disconnected")
        exit_df(0) 
    except ConnectionResetError:
        print("Client disconnected")
        exit_df(0)  


def main(server_socket):    
    client_socket = accept_client(server_socket)
    thread_keyboard = threading.Thread(target= keyboard_lisener_thread, args=(client_socket,),daemon=True,)
    thread_keyboard.start()

    client_socket = accept_client(server_socket)
    thread_mouse = threading.Thread(target= mouse_lisener_thread, args=(client_socket,),daemon=True,)
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
    
