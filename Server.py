### Updated Server.py with Fixes ###
import threading
import datetime
import socket

Clients = {}
UserNames = {}
Bans = set()
Admins = set()

def broadcast(message):
    for client in Clients:
        try:
            client.send(message.encode('utf-8'))
        except:
            continue

def handle_admin_command(command, connection, timestamp):
    try:
        if command == "unban":
            if not Bans:
                connection.send("⛔ No clients are banned.".encode('utf-8'))
            else:
                banned_users = list(Bans)
                for i, user in enumerate(banned_users):
                    connection.send(f"🔸[{i}] {user}".encode('utf-8'))
                connection.send("Enter index to unban: ".encode('utf-8'))
                index_length = int(connection.recv(4).decode('utf-8'))
                index = int(connection.recv(index_length).decode('utf-8'))
                unbanned_user = banned_users[index]
                Bans.remove(unbanned_user)
                broadcast(f"🔓 [{timestamp.strftime('%I:%M %p')}] {unbanned_user} has been unbanned.")

        elif command == "banlist":
            if not Bans:
                connection.send("⛔ No clients are banned.".encode('utf-8'))
            else:
                for user in Bans:
                    connection.send(f"🔸 {user}".encode('utf-8'))

        elif command == "ban":
            users = list(UserNames.values())
            for i, name in enumerate(users):
                connection.send(f"🔹[{i}] {name}".encode('utf-8'))
            connection.send("Enter index to ban: ".encode('utf-8'))
            index_length = int(connection.recv(4).decode('utf-8'))
            index = int(connection.recv(index_length).decode('utf-8'))
            target_conn = list(UserNames.keys())[index]
            banned_user = UserNames[target_conn]
            Bans.add(banned_user)
            target_conn.close()
            broadcast(f"🚫 [{timestamp.strftime('%I:%M %p')}] {banned_user} has been banned.")

        elif command == "kick":
            users = list(UserNames.values())
            for i, name in enumerate(users):
                connection.send(f"🔹[{i}] {name}".encode('utf-8'))
            connection.send("Enter index to kick: ".encode('utf-8'))
            index_length = int(connection.recv(4).decode('utf-8'))
            index = int(connection.recv(index_length).decode('utf-8'))
            kicked_conn = list(UserNames.keys())[index]
            kicked_user = UserNames[kicked_conn]
            kicked_conn.close()
            broadcast(f"👢 [{timestamp.strftime('%I:%M %p')}] {kicked_user} has been kicked.")

    except Exception as e:
        connection.send(f"⚠️ Error: {e}".encode('utf-8'))

def handle_client(conn, addr, ADDR, server_pass, admin_pass):
    try:
        username_length = int(conn.recv(4).decode('utf-8'))
        username = conn.recv(username_length).decode('utf-8')

        prefix_length = int(conn.recv(4).decode('utf-8'))
        prefix = conn.recv(prefix_length).decode('utf-8')

        full_username = f"{username}:{addr}"

        if full_username in Bans:
            msg = "you are banned"
            conn.send(f"{len(msg):04}".encode('utf-8'))
            conn.send(msg.encode('utf-8'))
            conn.close()
            return

        msg = "you are not banned"
        conn.send(f"{len(msg):04}".encode('utf-8'))
        conn.send(msg.encode('utf-8'))

        while True:
            pw_len = int(conn.recv(4).decode('utf-8'))
            password = conn.recv(pw_len).decode('utf-8')
            if password == 'Too many attempts!':
                conn.close()
                return
            elif password != server_pass:
                msg = "access denied"
                conn.send(f"{len(msg):04}".encode('utf-8'))
                conn.send(msg.encode('utf-8'))
            else:
                msg = "access granted"
                conn.send(f"{len(msg):04}".encode('utf-8'))
                conn.send(msg.encode('utf-8'))
                break

        msg = "admin?"
        conn.send(f"{len(msg):04}".encode('utf-8'))
        conn.send(msg.encode('utf-8'))

        is_admin = conn.recv(int(conn.recv(4).decode('utf-8'))).decode('utf-8')

        if is_admin.lower() == 'yes':
            attempts = 0
            while attempts < 3:
                pw_len = int(conn.recv(4).decode('utf-8'))
                admin_pw = conn.recv(pw_len).decode('utf-8')
                if admin_pw == admin_pass:
                    msg = "access granted"
                    conn.send(f"{len(msg):04}".encode('utf-8'))
                    conn.send(msg.encode('utf-8'))
                    Admins.add(conn)
                    break
                else:
                    attempts += 1
                    msg = "access denied"
                    conn.send(f"{len(msg):04}".encode('utf-8'))
                    conn.send(msg.encode('utf-8'))
            if attempts == 3:
                conn.close()
                return
        else:
            conn.send("Welcome to the Server!".encode('utf-8'))

        Clients[conn] = username
        UserNames[conn] = full_username

        timestamp = datetime.datetime.now()
        print(f"🔗 [{timestamp.strftime('%I:%M %p')}][{full_username}] connected.")
        broadcast(f"🔗 [{timestamp.strftime('%I:%M %p')}][{full_username}] joined the server.")

        while True:
            msg_len = conn.recv(64).decode('utf-8')
            if not msg_len:
                break

            try:
                msg_len = int(msg_len.strip())
                msg = conn.recv(msg_len).decode('utf-8')
            except:
                break

            timestamp = datetime.datetime.now()
            if msg.startswith(prefix):
                command = msg[len(prefix):].strip().split()[0]
                if command in ["ban", "unban", "banlist", "kick"]:
                    if conn in Admins:
                        handle_admin_command(command, conn, timestamp)
                    else:
                        conn.send("🔒 You do not have permission to run this command.".encode('utf-8'))
                elif command == "serverinfo":
                    conn.send(f"🔗 Server Address: {ADDR}".encode('utf-8'))
                    conn.send(f"🟢 Online Users: {len(Clients)}".encode('utf-8'))
                    conn.send(f"👑 Admins Online: {len(Admins)}".encode('utf-8'))
                elif command == "adminlist":
                    if not Admins:
                        conn.send("⛔ No Admins are online.".encode('utf-8'))
                    else:
                        for i, admin_conn in enumerate(Admins):
                            conn.send(f"👑 [{i}] {UserNames[admin_conn]}".encode('utf-8'))
                elif command == "exit":
                    conn.send("[200]Exit".encode('utf-8'))
                    break
                elif command == "online":
                    conn.send(f"🟢 Online Users: {len(Clients)}".encode('utf-8'))
                    for user in UserNames.values():
                        conn.send(f"🔹 {user}".encode('utf-8'))
            else:
                print(f"💠 [{timestamp.strftime('%I:%M %p')}][{full_username}] | {msg}")
                broadcast(f"💠 [{timestamp.strftime('%I:%M %p')}][{full_username}] | {msg}")

    except Exception as e:
        print(f"❌ Disconnected: {addr}, Error: {e}")
    finally:
        if conn in Admins:
            Admins.remove(conn)
        if conn in Clients:
            Clients.pop(conn)
        if conn in UserNames:
            UserNames.pop(conn)
        conn.close()

def start(server, ADDR, IP, PORT):
    server_pass = input("🔒 Enter server password: ")
    admin_pass = input("👑 Enter admin password: ")

    print(f"🕒 Server starting on {IP}:{PORT}...")
    server.listen()
    print(f"🔊 Listening on {IP}:{PORT}")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr, ADDR, server_pass, admin_pass))
        thread.start()
