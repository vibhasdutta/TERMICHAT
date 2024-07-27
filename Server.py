import threading
import datetime
import socket

def handle_client(connection,addr,ADDR):

    username_length = int(connection.recv(4).decode('utf-8'))
    prefix_length = int(connection.recv(4).decode('utf-8'))

    UserName = connection.recv(username_length).decode('utf-8')
    ClientPrefix = connection.recv(prefix_length).decode('utf-8')

    print(f"[{UserName}:{addr}] Connected to the Server[{ADDR}]!")
    connected=True
    while connected:
        try:
            message_length=connection.recv(64).decode('utf-8')
            if message_length:
                
                try:
                    message_length = int(message_length)
                except ValueError:
                    print(f"Invalid message length received: {message_length}")
                    continue
                
                message=connection.recv(message_length).decode('utf-8')
                
                if all (character in message for character in [ClientPrefix,'exit']):
                    connected=False
                    print(f"[{UserName}:{addr} ] Disconnected from the Server[{ADDR}]!")
                    
                elif all (character in message for character in [ClientPrefix,'online']):
                    print(f"[ONlINE CONNECTION] : {threading.active_count()-1}")
                
                else:
                    print(f"[{UserName}] : {message}")
                
                connection.send(f"Sent:{message}".encode('utf-8')) # USER CAN SEE THE MESSAGE SENT BY HIM/HER
        
        except Exception as e:
            print(f"[{UserName}:{addr}] Disconnected from the Server[{ADDR}]!")
            #print(f"[ERROR] : {e}")
            break
    connection.close()

def start(server,ADDR,Ip_Address,PORT):

    x=datetime.datetime.now()
    print(f"[TIME:{x.strftime('%I:%M %p')}][STARTING] Server is starting at {Ip_Address}:{PORT}")
    server.listen()
    print(f"[LISTENING] Server is listening on {Ip_Address}")
    
    from Interface import client_run
    client_run()

    while True:
        connection,addr=server.accept()
        thread=threading.Thread(target=handle_client,args=(connection,addr,ADDR))
        thread.start()
        print(f"[ONlINE CONNECTION] : {threading.active_count()-1}")
