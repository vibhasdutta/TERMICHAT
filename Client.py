import socket
import json
import threading

try:    

    with open('config.json') as f:
        data = json.load(f)

    PORT = data['PORT']
    CLIENT_IP = data['SERVER_IP']
    UserName = data['USER_NAME']
    ClientPrefix = data['PREFIX']

    print(f"---CURRENTSETTINGS---\nSERVER_IP : {CLIENT_IP}\nPORT : {PORT}\nUSER_NAME : {UserName}\nPREFIX : {ClientPrefix}")
    
    check = input("Do you want to change the Settings?[Yes/No]:")
    if check.lower()=='yes':
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
            data['PREFIX'] = data.get('PREFIX', '!')
            data['PORT'] = data.get('PORT', 8080)
            json.dump(data,f)


    ADDR=(CLIENT_IP,PORT)
    client=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    client.connect(ADDR)
    client.send(f"{len(UserName):04}".encode('utf-8'))
    client.send(UserName.encode('utf-8'))
    client.send(f"{len(ClientPrefix):04}".encode('utf-8'))
    client.send(ClientPrefix.encode('utf-8'))

    BanVerify = int(client.recv(4).decode('utf-8')) 
    BanVerify = client.recv(BanVerify).decode('utf-8')
    if BanVerify == 'you are banned':
        print(f"You are banned! frome the server {ADDR}")
        exit()
    

    Server_PASS_Try = 0
    while True:
        if Server_PASS_Try == 3:
            UserVerify = 'Too many attempts!'
            client.send(f"{len(UserVerify):04}".encode('utf-8'))
            client.send(UserVerify.encode('utf-8'))
            print("Too many attempts! Exiting...")
            exit()

        while True:
            Server_password=input("Enter the Server Password:")
            if len(Server_password) <= 8:
                print("Password must be at least 8 characters long.")
                pass
            else:
                break
        
        client.send(f"{len(Server_password):04}".encode('utf-8'))
        client.send(Server_password.encode('utf-8'))

        UserVerify = int(client.recv(4).decode('utf-8'))
        UserVerify = client.recv(UserVerify).decode('utf-8')

        if UserVerify == 'you are banned':
            print(f"You are banned! frome the server {ADDR}")
            exit()
        elif UserVerify == 'access denied':
            print("Access Denied!")
            Server_PASS_Try += 1 
            pass
        else:
            print("Access Granted!")
            break


    AdminVerify = int(client.recv(4).decode('utf-8'))
    AdminVerify = client.recv(AdminVerify).decode('utf-8')

    if AdminVerify == 'admin?':
        check = input("You are an Admin![Yes/No]:")
        client.send(f"{len(check):04}".encode('utf-8'))
        client.send(check.encode('utf-8'))
        if check.lower() == 'yes':
            
            Admin_PASS_Try = 0
            while True:

                if Admin_PASS_Try == 3:
                    AdminVerfiy = 'Too many attempts!'
                    client.send(f"{len(AdminVerify):04}".encode('utf-8'))
                    client.send(AdminVerify.encode('utf-8'))
                    print("Too many attempts! Exiting...")
                    exit()

                while True:
                    AdminVerify = input("Enter the Admin Password:")
                    if len(AdminVerify) <= 8:
                        print("Password must be at least 8 characters long.")
                        pass
                    else:
                        break
                    
                client.send(f"{len(AdminVerify):04}".encode('utf-8'))
                client.send(AdminVerify.encode('utf-8'))

                AdminVerify = int(client.recv(4).decode('utf-8'))
                AdminVerify = client.recv(AdminVerify).decode('utf-8')
                
                if AdminVerify == 'access denied':
                    Admin_PASS_Try += 1
                    print("Access Denied!")
                else:
                    break
                    
        
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
                try:
                    message=input()
                except EOFError:
                    print("EXITING...")
                    break
            
                if all (character in message for character in [ClientPrefix,'help']):
                    print(f"{ClientPrefix}online : To check the number of online Members\n{ClientPrefix}adminlist : To Show all Admin Online!\n{ClientPrefix}ban : To Ban a Member(ADMIN ONLY)\n{ClientPrefix}unban : To UnBan a Member(ADMIN ONLY)\n{ClientPrefix}banlist : To check list of Ban a Members(ADMIN ONLY)\n{ClientPrefix}kick : To Kick a Member(ADMIN ONLY)\n{ClientPrefix}exit : To exit the chat")

                elif all (character in message for character in [ClientPrefix,'exit']):
                    send(f"{ClientPrefix}exit")
                    break
                elif all (character in message for character in [ClientPrefix,'banlist']):
                    send(f"{ClientPrefix}banlist")

                elif all (character in message for character in [ClientPrefix,'unban']):
                    send(f"{ClientPrefix}unban")
                    try:
                        index = (input())
                        client.send(f"{len(index):04}".encode('utf-8'))
                        client.send(index.encode('utf-8'))
                    except ValueError:
                        print("Invalid Input!")
                    except KeyboardInterrupt:
                        print("Keyboard Interrupt!")
                    
                elif all (character in message for character in [ClientPrefix,'kick']):
                    send(f"{ClientPrefix}kick")
                    try:
                        index = (input())
                        client.send(f"{len(index):04}".encode('utf-8'))
                        client.send(index.encode('utf-8'))
                    except ValueError:
                        print("Invalid Input!")
                    except KeyboardInterrupt:
                        print("Keyboard Interrupt!")

                elif all (character in message for character in [ClientPrefix,'ban']) and not all (character in message for character in [ClientPrefix,'unban']):
                    send(f"{ClientPrefix}ban")
                    try:
                        index = (input())
                        client.send(f"{len(index):04}".encode('utf-8'))
                        client.send(index.encode('utf-8'))
                    except ValueError:
                        print("Invalid Input!")
                    except KeyboardInterrupt:
                        print("Keyboard Interrupt!")
                    
                else:
                    send(message)

        except ConnectionResetError:
            print(f"Connection was closed by the Server[{ADDR}]!")
            break
        except ConnectionAbortedError:
            print(f"Connection was closed by the Server[{ADDR}]!")
            break
try:
    thread1 = threading.Thread(target=receive)
    thread1.start()
    thread2 = threading.Thread(target=main)
    thread2.start()
except Exception as e:
    exit()
