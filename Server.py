# ─────────────────────────────────────────────
# TermiChat Server — Version 1.0
# Author: VibhasDutta
# Date Updated: 2025-06-01
# ─────────────────────────────────────────────
import threading
import datetime
import socket

Clients = {}
UserNames = {}
Bans = set()
Admins = set()

Muted = set()  # For muted users
MessageQueue = []  # For scheduled messages: list of tuples (send_time, target_conn, message)

def send_private_message(sender_conn, recipient_username, message, timestamp):
    for conn, full_username in UserNames.items():
        if full_username.split(':')[0] == recipient_username:
            conn.send(f"[DM][{timestamp.strftime('%I:%M %p')}][{UserNames[sender_conn]}] {message}".encode('utf-8'))
            sender_conn.send(f"[DM to {recipient_username}] {message}".encode('utf-8'))
            return
    sender_conn.send("⚠️ User not found.".encode('utf-8'))

def broadcast(message):
    for client in Clients:
        try:
            client.send(message.encode('utf-8'))
        except:
            Clients.pop(client, None)
            UserNames.pop(client, None)
            if client in Admins:
                Admins.remove(client)

def handle_admin_command(command, connection, timestamp):
    try:
        admin_username = UserNames.get(connection, None)

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
                if index < 0 or index >= len(banned_users):
                    connection.send("❌ Invalid index.".encode('utf-8'))
                    return
                unbanned_user = banned_users[index]
                if unbanned_user == admin_username:
                    connection.send("⚠️ You cannot unban yourself.".encode('utf-8'))
                    return
                Bans.remove(unbanned_user)
                broadcast(f"🔓 [{timestamp.strftime('%I:%M %p')}] {unbanned_user} has been unbanned.")

        elif command == "banlist":
            if not Bans:
                connection.send("⛔ No clients are banned.".encode('utf-8'))
            else:
                for user in Bans:
                    connection.send(f"🔸 {user}".encode('utf-8'))

        elif command == "ban":
            users = [(conn, name) for conn, name in UserNames.items() if conn != connection and conn not in Admins]
            if not users:
                connection.send("⚠️ No users to ban (cannot ban yourself or other admins).".encode('utf-8'))
                return
            for i, (conn, name) in enumerate(users):
                connection.send(f"🔹[{i}] {name}".encode('utf-8'))
            connection.send("Enter index to ban: ".encode('utf-8'))
            index_length = int(connection.recv(4).decode('utf-8'))
            index = int(connection.recv(index_length).decode('utf-8'))
            if index < 0 or index >= len(users):
                connection.send("❌ Invalid index.".encode('utf-8'))
                return
            target_conn, banned_user = users[index]
            Bans.add(banned_user)
            target_conn.close()
            broadcast(f"🚫 [{timestamp.strftime('%I:%M %p')}] {banned_user} has been banned.")

        elif command == "kick":
            users = [(conn, name) for conn, name in UserNames.items() if conn != connection and conn not in Admins]
            if not users:
                connection.send("⚠️ No users to kick (cannot kick yourself or other admins).".encode('utf-8'))
                return
            for i, (conn, name) in enumerate(users):
                connection.send(f"🔹[{i}] {name}".encode('utf-8'))
            connection.send("Enter index to kick: ".encode('utf-8'))
            index_length = int(connection.recv(4).decode('utf-8'))
            index = int(connection.recv(index_length).decode('utf-8'))
            if index < 0 or index >= len(users):
                connection.send("❌ Invalid index.".encode('utf-8'))
                return
            kicked_conn, kicked_user = users[index]
            kicked_conn.close()
            broadcast(f"👢 [{timestamp.strftime('%I:%M %p')}] {kicked_user} has been kicked.")

        elif command == "mute":
            users = [(conn, name) for conn, name in UserNames.items() if conn != connection and conn not in Admins]
            if not users:
                connection.send("⚠️ No users to mute (cannot mute yourself or other admins).".encode('utf-8'))
                return
            for i, (conn, name) in enumerate(users):
                connection.send(f"🔹[{i}] {name}".encode('utf-8'))
            connection.send("Enter index to mute: ".encode('utf-8'))
            index_length = int(connection.recv(4).decode('utf-8'))
            index = int(connection.recv(index_length).decode('utf-8'))
            if index < 0 or index >= len(users):
                connection.send("❌ Invalid index.".encode('utf-8'))
                return
            target_conn, muted_user = users[index]
            Muted.add(target_conn)
            broadcast(f"🔇 [{timestamp.strftime('%I:%M %p')}] {muted_user} has been muted.")

        elif command == "unmute":
            if not Muted:
                connection.send("⛔ No users are muted.".encode('utf-8'))
                return
            muted_list = [(conn, UserNames[conn]) for conn in Muted]
            for i, (_, name) in enumerate(muted_list):
                connection.send(f"🔸[{i}] {name}".encode('utf-8'))
            connection.send("Enter index to unmute: ".encode('utf-8'))
            index_length = int(connection.recv(4).decode('utf-8'))
            index = int(connection.recv(index_length).decode('utf-8'))
            if index < 0 or index >= len(muted_list):
                connection.send("❌ Invalid index.".encode('utf-8'))
                return
            unmute_conn, unmute_user = muted_list[index]
            Muted.remove(unmute_conn)
            broadcast(f"🔊 [{timestamp.strftime('%I:%M %p')}] {unmute_user} has been unmuted.")

        elif command == "announce":
            connection.send("Enter announcement message: ".encode('utf-8'))
            msg_len = int(connection.recv(4).decode('utf-8'))
            message = connection.recv(msg_len).decode('utf-8')
            broadcast(f"📢 [Announcement {timestamp.strftime('%I:%M %p')}] {message}")

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
                for client in Clients:
                    if client != conn:  # Don't send message back to the sender
                        try:
                            client.send(f"💠 [{timestamp.strftime('%I:%M %p')}][{full_username}] | {msg}".encode('utf-8'))
                        except:
                            Clients.pop(client, None)
                            UserNames.pop(client, None)
                            if client in Admins:
                                Admins.remove(client)

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
    while True:
        server_pass = input("🔒 Enter server password: ")
        if len(server_pass) < 9:
            print("❗ Password must be at least 9 characters long.\n")
            continue
        else:
            break
    while True:
        admin_pass = input("👑 Enter admin password: ")
        if len(admin_pass) < 9:
            print("❗ Password must be at least 9 characters long.\n")
            continue
        else:
            break
    print(f"🕒 Server starting on {IP}:{PORT}...")
    server.listen()
    print(f"🔊 Listening on {IP}:{PORT}")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr, ADDR, server_pass, admin_pass))
        thread.start()
