import socket
import json

def send(msg):
    message=msg.encode('utf-8')
    msg_length=len(message)
    send_length=str(msg_length).encode('utf-8')
    send_length+=b' '*(64-len(send_length))
    client.send(send_length)
    client.send(message)
    print(client.recv(2048).decode('utf-8'))

with open('config.json') as f:
    data = json.load(f)

Prefix = data['PREFIX']
PORT = data['PORT']
CLIENT_IP = socket.gethostbyname(socket.gethostname())
ADDR=(CLIENT_IP,PORT)
client=socket.socket(socket.AF_INET,socket.SOCK_STREAM)

try:
    client.connect(ADDR)
except socket.error as e:
    print(f"THE SEVRER IP OR PORT IS INVALID! or {e}")
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
    
