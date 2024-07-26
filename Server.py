import socket
import threading
import os
import dotenv
dotenv.load_dotenv()
import datetime

def handle_client(connection,addr,UserName,Prefix,ADDR):
    print(f"[{UserName}:{addr}] Connected to the Server[{ADDR}]!")
    connected=True
    while connected:
        try:
            message_length=connection.recv(64).decode('utf-8')
            if message_length:
                message_length=int(message_length)
                message=connection.recv(message_length).decode('utf-8')
                
                if all (character in message for character in [Prefix,'exit']):
                    connected=False
                    print(f"[{UserName}:{addr} ] Disconnected from the Server[{ADDR}]!")
                    
                elif all (character in message for character in [Prefix,'online']):
                    print(f"[ONlINE CONNECTION] : {threading.active_count()-1}")
                else:
                    print(f"[{UserName}] : {message}")
                connection.send(f"Sent:{message}".encode('utf-8')) # USER CAN SEE THE MESSAGE SENT BY HIM/HER
        except Exception:
            print(f"[{UserName}:{addr}] Disconnected from the Server[{ADDR}]!")
            break
    connection.close()

def start(UserName,Prefix,server,ADDR):
    x=datetime.datetime.now()
    print(f"[TIME:{x.strftime('%I:%M %p')}][STARTING] Server is starting at {os.getenv('SERVER_IP')}:{os.getenv('PORT')}")
    server.listen()
    print(f"[LISTENING] Server is listening on {os.getenv('SERVER_IP')}")
    
    from Interface import client_run
    client_run()

    while True:
        connection,addr=server.accept()
        thread=threading.Thread(target=handle_client,args=(connection,addr,UserName,Prefix,ADDR))
        thread.start()
        print(f"[ONlINE CONNECTION] : {threading.active_count()-1}")



