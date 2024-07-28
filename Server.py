import threading
import datetime
import socket

Clients = []
UserNames = []
Bans = []
Admin = []

def broadcast(message):
    for client in Clients:
        client.send(f"{message}".encode('utf-8'))

def handle_admin_command(command, user,message,connection,ClientPrefix,x):

            if command.startswith("unban"):
                if len(Bans) == 0:
                    connection.send("No clients are banned.".encode('utf-8'))
                else:
                    for ban in Bans:
                        index = Bans.index(ban)
                        connection.send(f"[{index}][{UserNames[index]}]".encode('utf-8'))
                    try:
                        connection.send("Enter the index of the client you want to unban or Press Enter to Exit".encode('utf-8'))
                        try:
                            UnbanIndex_length = int(connection.recv(4).decode('utf-8'))
                            UnbanIndex = int(connection.recv(UnbanIndex_length).decode('utf-8'))
                        except ValueError:
                            print("Invalid Input!")
                            
                        UnbanClient = Bans[UnbanIndex]
                        Bans.remove(UnbanClient)
                        print(f"[{x.strftime('%I:%M %p')}][{UserNames[UnbanIndex]}] has been unbanned.")
                        broadcast(f"[{x.strftime('%I:%M %p')}][{UserNames[UnbanIndex]}] has been unbanned.")
                    except Exception as e:
                        print(f"[ERROR] : {e}".encode('utf-8'))
            
            elif command.startswith("banlist"):
                if len(Bans) == 0:
                    connection.send("No clients are banned.".encode('utf-8'))
                else:    
                    for ban in Bans:
                        index = Bans.index(ban)
                        connection.send(f"[{index}][{UserNames[index]}]".encode('utf-8'))
            
            elif command.startswith("ban"):
                for client in Clients:
                    index = Clients.index(client)
                    connection.send(f"[{index}][{UserNames[index]}]".encode('utf-8'))
                try:
                    connection.send("Enter the index of the client you want to ban or Press Enter to Exit".encode('utf-8'))
                    try:
                        BanIndex_length = int(connection.recv(4).decode('utf-8'))
                        BanIndex = int(connection.recv(BanIndex_length).decode('utf-8'))
                    except ValueError:
                        print("Invalid Input!")
                        
                    BanClient = Clients[BanIndex]
                    BanClient.close()
                    print(f"[{x.strftime('%I:%M %p')}][{UserNames[BanIndex]}] has been banned.")
                    broadcast(f"[{x.strftime('%I:%M %p')}][{UserNames[BanIndex]}] has been banned.")
                    Bans.append(Clients[BanIndex])
                except Exception as e:
                    print(f"[ERROR] : {e}".encode('utf-8'))
            elif  command.startswith("adminlist"):
                for admin in Admin:
                    index = Admin.index(admin)
                    connection.send(f"[{index}][{UserNames[index]}]".encode('utf-8'))

            elif command.startswith("kick"):
                for client in Clients:
                    index = Clients.index(client)
                    connection.send(f"{index} : {UserNames[index]}".encode('utf-8'))
                try:
                    connection.send("Enter the index of the client you want to kick or Press Enter to Exit ".encode('utf-8'))
                    try:
                        KickIndex_length = int(connection.recv(4).decode('utf-8'))
                        KickIndex = int(connection.recv(KickIndex_length).decode('utf-8'))
                        KickClient = Clients[KickIndex]
                        KickClient.close()
                    except ValueError:
                        print("Invalid Input!")
                        
                    print(f"[{x.strftime('%I:%M %p')}][{UserNames[KickIndex]}] has been kicked.")
                    broadcast(f"[{x.strftime('%I:%M %p')}][{UserNames[KickIndex]}] has been kicked.")
                except Exception as e:
                    connection.send(f"[ERROR] : {e}".encode('utf-8'))

def handle_client(connection,addr,ADDR,SERVER_PASSWORD,ADMIN_PASSWORD,UserName,ClientPrefix):
    
    try:
        x=datetime.datetime.now()

        if connection in Bans:
            BanText = "you are banned"
            connection.send(f"{len(BanText):04}".encode('utf-8'))
            connection.send(BanText.encode('utf-8'))
            print(f"[{x.strftime('%I:%M %p')}][{UserName}:{addr}] was trying to connect to the server[{ADDR}] but is banned!")
            UserNames.remove(f"{UserName}:{addr}")
            Clients.remove(connection)
            connection.close()
            return
        else:
            BanText = "you are not banned"
            connection.send(f"{len(BanText):04}".encode('utf-8'))
            connection.send(BanText.encode('utf-8'))

        while True:
            password_length = int(connection.recv(4).decode('utf-8'))
            password = connection.recv(password_length).decode('utf-8')
            
            
            if password != SERVER_PASSWORD:
                Invatext = "access denied"
                connection.send(f"{len(Invatext):04}".encode('utf-8'))
                connection.send(Invatext.encode('utf-8'))
                print(f"[{x.strftime('%I:%M %p')}][{UserName}:{addr}] was trying to connect to the server[{ADDR}] but access denied!")
                UserNames.remove(f"{UserName}:{addr}")
                Clients.remove(connection)
                connection.close()
                return
            elif password == 'Too many attempts!':
                UserNames.remove(f"{UserName}:{addr}")
                print(f"[{x.strftime('%I:%M %p')}][{UserName}:{addr}] was trying to connect to the server[{ADDR}] but too many attempts!")
                Clients.remove(connection)
                connection.close()
                return
            else:
                acctext = "access granted"
                connection.send(f"{len(acctext):04}".encode('utf-8'))
                connection.send(acctext.encode('utf-8'))
                break

        AdminVerify = "admin?"
        connection.send(f"{len(AdminVerify):04}".encode('utf-8'))
        connection.send(AdminVerify.encode('utf-8'))

        AdminVerify = connection.recv(4).decode('utf-8')
        AdminVerify = connection.recv(int(AdminVerify)).decode('utf-8')

        if AdminVerify.lower() == 'yes':
            while True:
                AdminPassword_length = int(connection.recv(4).decode('utf-8'))
                AdminPassword = connection.recv(AdminPassword_length).decode('utf-8')
                if AdminPassword == ADMIN_PASSWORD:
                    AdminVerify = "access granted"
                    connection.send(f"{len(AdminVerify):04}".encode('utf-8'))
                    connection.send(AdminVerify.encode('utf-8'))
                    connection.send("Welcome Admin!".encode('utf-8'))
                    print(f"[{x.strftime('%I:%M %p')}][{UserName}:{addr}] Join as Admin!")
                    Admin.append(connection)
                    break
                elif AdminPassword != ADMIN_PASSWORD:
                    AdminVerify = "access denied"
                    connection.send(f"{len(AdminVerify):04}".encode('utf-8'))
                    connection.send(AdminVerify.encode('utf-8'))
                    print(f"[{x.strftime('%I:%M %p')}][{UserName}:{addr}] was trying to connect to the server[{ADDR}] but access denied!")
                elif AdminPassword == 'Too many attempts!':
                    UserNames.remove(f"{UserName}:{addr}")
                    print(f"[{x.strftime('%I:%M %p')}][{UserName}:{addr}] was trying to connect to the server as Admin [{ADDR}] but too many attempts!")
                    Clients.remove(connection)
                    connection.close()

    except Exception as e:
        print(f"[ERROR] : {e}")
        return 
    print(f"[{x.strftime('%I:%M %p')}][{UserName}:{addr}] Connected to the Server[{ADDR}]!")
    broadcast(f"[{x.strftime('%I:%M %p')}][{UserName}:{addr}] Connected to the Server[{ADDR}]!")

    connected=True
    

    while connected:
        x=datetime.datetime.now()
        try:
            message_length=connection.recv(64).decode('utf-8')
            if message_length:
                
                try:
                    message_length = int(message_length)
                except ValueError:
                    print(f"Invalid message length received: {message_length}")
                    break
                
                message=connection.recv(message_length).decode('utf-8')

                if message.startswith(ClientPrefix):
                    command = message[1:]
                    if command.split()[0] in ["ban", "unban", "banlist", "kick"]:
                        if connection in Admin:
                            handle_admin_command(command, UserName,message,connection,ClientPrefix,x)
                        else:
                            connection.send("You do not have permission to execute this command.".encode('utf-8'))
                    
                    elif all (character in message for character in [ClientPrefix,'exit']):
                        connected=False
                        print(f"[{x.strftime('%I:%M %p')}][{UserName}:{addr}] Disconnected from the Server[{ADDR}]!")
                        broadcast(f"[{x.strftime('%I:%M %p')}][{UserName}:{addr}] Disconnected from the Server[{ADDR}]!")

                    elif all (character in message for character in [ClientPrefix,'online']):
                        connection.send(f"[ONlINE CONNECTION] : {threading.active_count()-1}".encode('utf-8'))
                        for i in UserNames:
                            connection.send(f"[{i}]".encode('utf-8'))
                else:
                    print(f"[{x.strftime('%I:%M %p')}:{UserName}] | {message}")
                    broadcast(f"[{x.strftime('%I:%M %p')}:{UserName}] | {message}")

                    # connection.send(f"Sent:{message}".encode('utf-8'))  #USER CAN SEE THE MESSAGE SENT BY HIM/HER
        
        except Exception as e:
            print(f"[{x.strftime('%I:%M %p')}][{UserName}:{addr}] Disconneted from the Server[{ADDR}]!")
            print(f"[ERROR] : {e}")
            break

    if len(Admin) != 0:
        Admin.remove(connection)

    UserNames.remove(f"{UserName}:{addr}")
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

    while True:
        ADMIN_PASSWORD = input("Enter the admin password: ")
        if len(ADMIN_PASSWORD) <= 8:
            print("Password must be at least 8 characters long.")
            pass
        else:
            break
        
        

       
    x=datetime.datetime.now()
    print(f"[TIME:{x.strftime('%I:%M %p')}][STARTING] Server is starting at {Ip_Address}:{PORT}")
    server.listen()
    print(f"[LISTENING] Server is Online and listening! on {Ip_Address}")
    
    from Interface import client_run
    client_run()

    while True:
        connection,addr=server.accept()

        username_length = int(connection.recv(4).decode('utf-8'))
        UserName = connection.recv(username_length).decode('utf-8')
        UserNames.append(f"{UserName}:{addr}")

        prefix_length = int(connection.recv(4).decode('utf-8'))
        ClientPrefix = connection.recv(prefix_length).decode('utf-8')
    
        Clients.append(connection)
        
        thread=threading.Thread(target=handle_client,args=(connection,addr,ADDR,SERVER_PASSWORD,ADMIN_PASSWORD,UserName,ClientPrefix))
        thread.start()
        # print(f"[ONlINE CONNECTION] : {threading.active_count()-1}")