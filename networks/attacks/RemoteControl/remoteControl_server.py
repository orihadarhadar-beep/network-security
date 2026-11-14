
import os
import socket
import threading
from mouse_and_keyboard.controller import keyboard_lisener_thread,mouse_lisener_thread
from screen.controller import server_screen_thread, exit_df


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

    

def main(server_socket):    
    client_socket = accept_client(server_socket)
    thread_keyboard = threading.Thread(target= keyboard_lisener_thread, args=(client_socket,exit_df),daemon=True,)
    thread_keyboard.start()

    client_socket = accept_client(server_socket)
    thread_mouse = threading.Thread(target= mouse_lisener_thread, args=(client_socket,),daemon=True,)
    thread_mouse.start()

    client_socket = accept_client(server_socket)
    thread_screen = threading.Thread(target= server_screen_thread, args=(client_socket,),daemon=True,)
    thread_screen.start()
   
    while (thread_keyboard.is_alive() and thread_mouse.is_alive() and thread_screen.is_alive()):
        thread_screen.join(timeout=0.5)



if __name__ == "__main__":
    server_socket = create_server()
    try:
        main(server_socket)
    except KeyboardInterrupt:
        print("Ctrl+C detected - shutting down server...")
        server_socket.close()
        os._exit(0)
    