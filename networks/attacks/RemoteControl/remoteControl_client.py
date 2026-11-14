import socket
import threading
from mouse_and_keyboard.agent import keyboard_clicker_thread, mouse_handeler_thread
from screen.agent import client_screen_thread


def create_client(ip = "127.0.0.1",port = 1337):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create TCP Socket object
    client_socket.connect((ip, port))
    print("Client connected")
    return client_socket





if __name__ == "__main__":
    ip = input("Enter controller ip: ")
    with create_client(ip) as client_socket0:
        with create_client(ip) as client_socket1:
            with create_client(ip) as client_socket2:
                thread_keyboard = threading.Thread(target= keyboard_clicker_thread,args=(client_socket0,),daemon=True,)
                thread_keyboard.start()

                thread_mouse = threading.Thread(target= mouse_handeler_thread,args=(client_socket1,),daemon=True,)
                thread_mouse.start()

                thread_screen = threading.Thread(target=client_screen_thread,args=(client_socket2,),daemon=True,)
                thread_screen.start()

                while (thread_keyboard.is_alive() and thread_mouse.is_alive() and thread_screen.is_alive()):
                        thread_screen.join(timeout=0.5)