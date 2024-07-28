import socket
import json
import threading
import time


try:    

    with open('config.json') as f:
        data = json.load(f)

    PORT = data['PORT']
    CLIENT_IP = data['SERVER_IP']
    UserName = data['USER_NAME']
    ClientPrefix = data['PREFIX']

    check = input("Do you want to change the Settings?[Y/N]:")
    if check.lower()=='y':
        check=input("what do you want to change?[USERNAME/PREFIX]:")
        
        if check.lower()=='username':
            UserName = input("Enter the User Name:")
        elif check.lower()=='prefix':
            ClientPrefix = input("Enter the Prefix:")
        else:
            print("Invalid Input!")

        
        with open('config.json','w') as f:
            data['USER_NAME'] = UserName
            data['PREFIX'] = ClientPrefix
            json.dump(data,f)
    else:
        with open('config.json','w') as f:
            data['USER_NAME'] = data.get('USER_NAME', socket.gethostname())
            data['PREFIX'] = data.get('PREFIX', 'default_prefix')
            data['PORT'] = data.get('PORT', 8080)
            json.dump(data,f)

    while True:
        Server_password=input("Enter the Server Password:")
        if len(Server_password) <= 8:
            print("Password must be at least 8 characters long.")
            pass
        else:
            break


    ADDR=(CLIENT_IP,PORT)
    client=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    client.connect(ADDR)
    client.send(f"{len(UserName):04}".encode('utf-8'))
    client.send(UserName.encode('utf-8'))
    client.send(f"{len(ClientPrefix):04}".encode('utf-8'))
    client.send(ClientPrefix.encode('utf-8'))
    
    client.send(f"{len(Server_password):04}".encode('utf-8'))
    client.send(Server_password.encode('utf-8'))
    text = int(client.recv(4).decode('utf-8'))
    text = client.recv(text).decode('utf-8')
    if text == 'access denied':
        print("Access Denied!")
        exit()  
    else:
        print("Access Granted!")
except KeyboardInterrupt:
    print("Keyboard Interrupt!")
    exit()        
except Exception as e:
    print(f"ERROR : {e}")
    exit()





def send(msg):
    message=msg.encode('utf-8')
    msg_length=len(message)
    send_length=str(msg_length).encode('utf-8')
    send_length+=b' '*(64-len(send_length))
    client.send(send_length)
    client.send(message)

def receive():
    try:
        while True:
            print(client.recv(2048).decode('utf-8'))  
    except Exception as e:
        print(f"ERROR : {e}")



def main():
    while True:
        try:

                message=input()
            
                if all (character in message for character in [ClientPrefix,'help']):
                    print(f"{ClientPrefix}online : To check the number of online connections\n{ClientPrefix}exit : To exit the chat")
            
                elif all (character in message for character in [ClientPrefix,'exit']):
                    send(f"{ClientPrefix}exit")
                    break
            
                else:
                    send(message)
        except KeyboardInterrupt:
            print("Keyboard Interrupt!")
            break            
        
        except ConnectionResetError:
            print(f"Connection was closed by the Server[{ADDR}]!")
            break
        except ConnectionAbortedError:
            print(f"Connection was closed by the Server[{ADDR}]!")
            break

thread1 = threading.Thread(target=receive)
thread1.start()
thread2 = threading.Thread(target=main)
thread2.start()


