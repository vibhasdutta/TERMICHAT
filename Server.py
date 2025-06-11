# ─────────────────────────────────────────────
# TermiChat Server — Version 1.0 (Fixed)
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

def send_private_message(sender_conn, recipient_username, message, timestamp):
    for conn, full_username in UserNames.items():
        if full_username.split(':')[0] == recipient_username:
            conn.send(f"[DM][{timestamp.strftime('%I:%M %p')}][{UserNames[sender_conn]}] {message}".encode('utf-8'))
            sender_conn.send(f"[DM to {recipient_username}] {message}".encode('utf-8'))
            return
    sender_conn.send("⚠️ User not found.".encode('utf-8'))

def broadcast(message):
    # Create a copy of the clients list to avoid iteration issues
    clients_copy = list(Clients.keys())
    clients_to_remove = []
    
    for client in clients_copy:
        try:
            client.send(message.encode('utf-8'))
        except:
            clients_to_remove.append(client)
    
    # Remove disconnected clients after iteration
    for client in clients_to_remove:
        cleanup_client(client)

def cleanup_client(client):
    """Safely remove a client from all collections"""
    if client in Clients:
        Clients.pop(client, None)
    if client in UserNames:
        UserNames.pop(client, None)
    if client in Admins:
        Admins.remove(client)
    if client in Muted:
        Muted.remove(client)

def recv_all(conn, n):
    """Ensure n bytes are received."""
    data = b''
    while len(data) < n:
        packet = conn.recv(n - len(data))
        if not packet:
            raise ConnectionError("Client disconnected unexpectedly.")
        data += packet
    return data

def handle_admin_command(command, connection, timestamp):
    try:
        admin_username = UserNames.get(connection, None)
        connection.settimeout(10.0)  # Prevent infinite wait

        def get_index():
            index_length = int(recv_all(connection, 4).decode('utf-8'))
            index = int(recv_all(connection, index_length).decode('utf-8'))
            return index

        if command == "unban":
            if not Bans:
                connection.send("⛔ No clients are banned.".encode('utf-8'))
                return
            banned_users = list(Bans)
            for i, user in enumerate(banned_users):
                connection.send(f"🔸[{i}] {user}".encode('utf-8'))
            connection.send("Enter index to unban: ".encode('utf-8'))
            index = get_index()
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

        elif command in {"ban", "kick", "mute"}:
            users = [(conn, name) for conn, name in UserNames.items() if conn != connection and conn not in Admins]
            if not users:
                connection.send(f"⚠️ No users to {command} (cannot target yourself or other admins).".encode('utf-8'))
                return
            for i, (conn, name) in enumerate(users):
                connection.send(f"🔹[{i}] {name}".encode('utf-8'))
            connection.send(f"Enter index to {command}: ".encode('utf-8'))
            index = get_index()
            if index < 0 or index >= len(users):
                connection.send("❌ Invalid index.".encode('utf-8'))
                return
            target_conn, target_user = users[index]

            if command == "ban":
                Bans.add(target_user)
                broadcast(f"🚫 [{timestamp.strftime('%I:%M %p')}] {target_user} has been banned.")
                cleanup_client(target_conn)  # Clean up first
                target_conn.close()  # Then close connection
            elif command == "kick":
                broadcast(f"👢 [{timestamp.strftime('%I:%M %p')}] {target_user} has been kicked.")
                cleanup_client(target_conn)  # Clean up first
                target_conn.close()  # Then close connection
            elif command == "mute":
                Muted.add(target_conn)
                broadcast(f"🔇 [{timestamp.strftime('%I:%M %p')}] {target_user} has been muted.")

        elif command == "unmute":
            if not Muted:
                connection.send("⛔ No users are muted.".encode('utf-8'))
                return
            muted_list = [(conn, UserNames.get(conn, "Unknown")) for conn in Muted]
            for i, (_, name) in enumerate(muted_list):
                connection.send(f"🔸[{i}] {name}".encode('utf-8'))
            connection.send("Enter index to unmute: ".encode('utf-8'))
            index = get_index()
            if index < 0 or index >= len(muted_list):
                connection.send("❌ Invalid index.".encode('utf-8'))
                return
            unmute_conn, unmute_user = muted_list[index]
            Muted.remove(unmute_conn)
            broadcast(f"🔊 [{timestamp.strftime('%I:%M %p')}] {unmute_user} has been unmuted.")

        elif command == "announce":
            connection.send("Enter announcement message: ".encode('utf-8'))
            msg_len = int(recv_all(connection, 4).decode('utf-8'))
            message = recv_all(connection, msg_len).decode('utf-8')
            broadcast(f"📢 [Announcement {timestamp.strftime('%I:%M %p')}] {message}")

    except (ValueError, IndexError, ConnectionError) as e:
        connection.send(f"⚠️ Error: {str(e)}".encode('utf-8'))
    except Exception as e:
        connection.send(f"⚠️ Unexpected error: {str(e)}".encode('utf-8'))
    finally:
        connection.settimeout(None)

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
        if conn in Admins:
            broadcast(f"👑 [{timestamp.strftime('%I:%M %p')}][ADMIN: {full_username}] has joined the server.")
        else:
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
            
            # Check if user is muted before processing regular messages
            if conn in Muted and not msg.startswith(prefix):
                conn.send("🔇 You are muted and cannot send messages.".encode('utf-8'))
                continue
                
            if msg.startswith(prefix):
                command = msg[len(prefix):].strip().split()[0]
                if command in ["ban", "unban", "banlist", "kick", "mute", "unmute", "announce"]:
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
                
                # Create a copy of clients to avoid iteration issues
                clients_copy = list(Clients.keys())
                clients_to_remove = []
                
                for client in clients_copy:
                    if client != conn:  # Don't send message back to the sender
                        try:
                            client.send(f"💠 [{timestamp.strftime('%I:%M %p')}][{full_username}] | {msg}".encode('utf-8'))
                        except:
                            clients_to_remove.append(client)
                
                # Remove disconnected clients after iteration
                for client in clients_to_remove:
                    cleanup_client(client)

    except Exception as e:
        print(f"❌ Disconnected: {addr}, Error: {e}")
    finally:
        cleanup_client(conn)
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

if __name__ == "__main__":
    IP_Address = '127.0.0.1'
    PORT = 1234
    ADDR = (IP_Address, PORT)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    start(server, ADDR, IP_Address, PORT)