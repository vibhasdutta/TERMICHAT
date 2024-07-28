import threading
import datetime
import socket

Clients = []
def broadcast(message):
    for client in Clients:
        client.send(f"{message}".encode('utf-8'))

def handle_client(connection,addr,ADDR,SERVER_PASSWORD,UserName,ClientPrefix):

    try:
        # Receive the length of the password
        password_length = int(connection.recv(4).decode('utf-8'))
        password = connection.recv(password_length).decode('utf-8')
        
        if password != SERVER_PASSWORD:
            Invatext = "access denied"
            connection.send(f"{len(Invatext):04}".encode('utf-8'))
            connection.send(Invatext.encode('utf-8'))
            connection.close()
            return
        else:
            acctext = "access granted"
            connection.send(f"{len(acctext):04}".encode('utf-8'))
            connection.send(acctext.encode('utf-8'))

        

    except Exception as e:
        print(f"[ERROR] : {e}")
        return 

    broadcast(f"[{UserName}:{addr}] Connected to the Server[{ADDR}]!")
    connected=True
    while connected:
        try:
            message_length=connection.recv(64).decode('utf-8')
            if message_length:
                
                try:
                    message_length = int(message_length)
                except ValueError:
                    print(f"Invalid message length received: {message_length}")
                    break
                
                message=connection.recv(message_length).decode('utf-8')
                
                if all (character in message for character in [ClientPrefix,'exit']):
                    connected=False
                    print(f"[{UserName}:{addr} ] Disconnected from the Server[{ADDR}]!")
                    broadcast(f"[{UserName}:{addr} ] Disconnected from the Server[{ADDR}]!")
                    
                    
                elif all (character in message for character in [ClientPrefix,'online']):
                    connection.send(f"[ONlINE CONNECTION] : {threading.active_count()-1}".encode('utf-8'))
                
                else:
                    print(f"[{UserName}] : {message}")
                    broadcast(f"[{UserName}] : {message}")
                
                #connection.send(f"Sent:{message}".encode('utf-8')) # USER CAN SEE THE MESSAGE SENT BY HIM/HER
        
        except Exception as e:
            print(f"[{UserName}:{addr} ] Disconnected from the Server[{ADDR}]!")
            #print(f"[ERROR] : {e}")
            break

    Clients.remove(connection)
    connection.close()

def start(server,ADDR,Ip_Address,PORT):

    while True:
        SERVER_PASSWORD = input("Enter the server password: ")
        if len(SERVER_PASSWORD) <= 8:
            print("Password must be at least 8 characters long.")
            pass
        else:
            break
        
    x=datetime.datetime.now()
    print(f"[TIME:{x.strftime('%I:%M %p')}][STARTING] Server is starting at {Ip_Address}:{PORT}")
    server.listen()
    print(f"[LISTENING] Server is Online and listening! on {Ip_Address}")
    
    while True:
        connection,addr=server.accept()

        username_length = int(connection.recv(4).decode('utf-8'))
        UserName = connection.recv(username_length).decode('utf-8')

        prefix_length = int(connection.recv(4).decode('utf-8'))
        ClientPrefix = connection.recv(prefix_length).decode('utf-8')

        Clients.append(connection)

        thread=threading.Thread(target=handle_client,args=(connection,addr,ADDR,SERVER_PASSWORD,UserName,ClientPrefix))
        thread.start()
        # print(f"[ONlINE CONNECTION] : {threading.active_count()-1}")