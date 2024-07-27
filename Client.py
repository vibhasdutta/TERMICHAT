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

check = input("Do you want to change the Settings?[Y/N]:")
if check.lower()=='y':
    with open('config.json','w') as f:
        data['USER_NAME'] = input("Enter the User Name:")
        data['PREFIX'] = input("Enter the Prefix:")
        json.dump(data,f)
else:
    with open('config.json','w') as f:
        data['USER_NAME'] = data.get('USER_NAME', socket.gethostname())
        data['PREFIX'] = data.get('PREFIX', 'default_prefix')
        json.dump(data,f)

PORT = data['PORT']
CLIENT_IP = data['SERVER_IP']
UserName = data['USER_NAME']
ClientPrefix = data['PREFIX']


try:
    ADDR=(CLIENT_IP,PORT)

    client=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    client.connect(ADDR)

    client.send(f"{len(UserName):04}".encode('utf-8'))
    client.send(f"{len(ClientPrefix):04}".encode('utf-8'))

    client.send(UserName.encode('utf-8'))
    client.send(ClientPrefix.encode('utf-8'))

except Exception as e:
    print(f"ERROR : {e}")
    exit()

while True:
    
    try:
        try:
            message=input("Enter message:")
        except KeyboardInterrupt as e:
            send(f"{ClientPrefix}exit")

        
        if all (character in message for character in [ClientPrefix,'help']):
            print(f"{ClientPrefix}online : To check the number of online connections\n{ClientPrefix}exit : To exit the chat")
        
        elif all (character in message for character in [ClientPrefix,'exit']):
            break
        
        else:
            send(message)

    except ConnectionResetError:
        print(f"Connection was closed by the Server[{ADDR}]!")
        break
    except ConnectionAbortedError:
        print(f"Connection was closed by the Server[{ADDR}]!")
        break
    
    
