import os

from pynput.keyboard import Controller as KeyboardController, Key,KeyCode
from pynput.mouse import Button, Controller as MouseController
import socket
import threading



def create_client(ip = "127.0.0.1",port = 1337):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create TCP Socket object
    client_socket.connect((ip, port))
    print("Client connected")
    return client_socket


def keyboard_clicker_thread(client_socket,exit_df = os._exit):
    try:
        keyboard = KeyboardController()
        socket_file = client_socket.makefile("r", encoding="utf-8")
        while True:
            key = socket_file.readline()
            if not key:
                break
            key = key.rstrip("\n")
            key_arr = key.split(":")

            if key_arr[0] == "CHAR":
                key = key_arr[1]

            elif key_arr[0] == "SPECIAL":
                key = getattr(Key, key_arr[1])

            elif key_arr[0] == "VK":
                key = KeyCode.from_vk(int(key_arr[1]))

            keyboard.press(key)
    except ConnectionError:
        print("Client disconnected")
        exit_df(0) 
    except ConnectionResetError:
        print("Client disconnected")
        exit_df(0) 

def mouse_handeler_thread(client_socket,exit_df = os._exit):
    try:
        mouse = MouseController()
        socket_file = client_socket.makefile("r", encoding="utf-8")
        while True:
            message = socket_file.readline()
            if not message:
                break
            message = message.strip()
            mouse_moves(mouse,message)
    except ConnectionError:
        print("Client disconnected")
        exit_df(0)
    except ConnectionResetError:
        print("Client disconnected")
        exit_df(0) 


def mouse_moves(mouse,message):
    message = message.split(",")
    if("move" == message[0]):
        mouse.move(float(message[1]), float(message[2]))

    elif("click" == message[0]):
        mouse.move(float(message[1]), float(message[2]))
        if (message[4] == "True"):
            mouse.press(getattr(Button,message[3]))
        else:
            mouse.release(getattr(Button,message[3]))

    elif("scroll" == message[0]):
        mouse.move(float(message[1]), float(message[2]))
        mouse.scroll(float(message[3]), float(message[4]))




if __name__ == "__main__":
    ip = input("Enter controller ip: ")
    with create_client(ip) as client_socket0:
        with create_client(ip) as client_socket1:
            thread_keyboard = threading.Thread(target= keyboard_clicker_thread,args=(client_socket0,),daemon=True,)
            thread_keyboard.start()

            thread_mouse = threading.Thread(target= mouse_handeler_thread,args=(client_socket1,),daemon=True,)
            thread_mouse.start()

            thread_mouse.join()
            thread_keyboard.join()
    
