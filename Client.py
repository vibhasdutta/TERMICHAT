import socket
import threading
import os
import dotenv
import time
dotenv.load_dotenv()

def send(msg):
    message=msg.encode('utf-8')
    msg_length=len(message)
    send_length=str(msg_length).encode('utf-8')
    send_length+=b' '*(64-len(send_length))
    client.send(send_length)
    client.send(message)
    print(client.recv(2048).decode('utf-8'))


UserName = os.getenv('USER_NAME')
Prefix = os.getenv('Prefix')
PORT = int(os.getenv('PORT'))

if os.getenv('HOSTING_ON')=='True':
    CLIENT_IP = socket.gethostbyname(socket.gethostname())
else:
    CLIENT_IP = os.getenv('SERVER_IP')
    
ADDR=(CLIENT_IP,PORT)
client=socket.socket(socket.AF_INET,socket.SOCK_STREAM)

try:
    client.connect(ADDR)
except OSError:
    print("THE SEVRER IP OR PORT IS INVALID!")
    exit()

while True:
    
    try:
        message=input("Enter message:")
        if all (character in message for character in [Prefix,'help']):
            print(f"{Prefix}online : To check the number of online connections\n{Prefix}exit : To exit the chat")
        elif all (character in message for character in [Prefix,'exit']):
            break
        else:
            send(message)
    except ConnectionResetError:
        print(f"Connection was closed by the Server[{ADDR}]!")
        break
    except KeyboardInterrupt:
        send(f"{Prefix}exit")
        break
    