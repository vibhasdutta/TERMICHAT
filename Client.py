# ─────────────────────────────────────────────
# TermiChat Server — Version 1.0
# Author: VibhasDutta
# Date Updated: 2025-06-01
# ─────────────────────────────────────────────
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
    print(r"""
 _       __     __                             ______         ______                    _ ________          __ 
| |     / /__  / /________  ____ ___  ___     /_  __/___     /_  __/__  _________ ___  (_) ____/ /_  ____ _/ /_
| | /| / / _ \/ / ___/ __ \/ __ `__ \/ _ \     / / / __ \     / / / _ \/ ___/ __ `__ \/ / /   / __ \/ __ `/ __/
| |/ |/ /  __/ / /__/ /_/ / / / / / /  __/    / / / /_/ /    / / /  __/ /  / / / / / / / /___/ / / / /_/ / /_  
|__/|__/\___/_/\___/\____/_/ /_/ /_/\___/    /_/  \____/    /_/  \___/_/  /_/ /_/ /_/_/\____/_/ /_/\__,_/\__/  

TermiChat Client — Version 1.0 | Author: VibhasDutta | Updated: 2025-06-01
""")
    print(f"⚙️---CURRENT SETTINGS---⚙️\n🌐 SERVER IP: {CLIENT_IP}\n🔌 PORT: {PORT}\n👤 USER NAME: {UserName}\n🏷️ PREFIX: {ClientPrefix}\n\n")

    check = input("❓ Do you want to change the Settings? [Yes/No]: ")
    if check.lower() == 'yes':
        check = input("🔧 What do you want to change? [USERNAME/PREFIX]: ")

        if check.lower() == 'username':
            UserName = input("👤 Enter the User Name: ")
        elif check.lower() == 'prefix':
            ClientPrefix = input("🏷️ Enter the Prefix: ")
        else:
            print("⚠️ Invalid Input!\n")

        with open('config.json', 'w') as f:
            data['USER_NAME'] = UserName
            data['PREFIX'] = ClientPrefix
            json.dump(data, f)
    else:
        with open('config.json', 'w') as f:
            data['USER_NAME'] = data.get('USER_NAME', socket.gethostname())
            data['PREFIX'] = data.get('PREFIX', '!')
            data['PORT'] = data.get('PORT', 8080)
            json.dump(data, f)

    ADDR = (CLIENT_IP, PORT)

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)

    client.send(f"{len(UserName):04}".encode('utf-8'))
    client.send(UserName.encode('utf-8'))
    client.send(f"{len(ClientPrefix):04}".encode('utf-8'))
    client.send(ClientPrefix.encode('utf-8'))

    BanVerify = int(client.recv(4).decode('utf-8'))
    BanVerify = client.recv(BanVerify).decode('utf-8')
    if BanVerify == 'you are banned':
        print(f"🚫You are banned from the server {ADDR}\n")
        exit()

    Server_PASS_Try = 0
    while True:
        if Server_PASS_Try == 3:
            UserVerify = 'Too many attempts!'
            client.send(f"{len(UserVerify):04}".encode('utf-8'))
            client.send(UserVerify.encode('utf-8'))
            print("⚠️ Too many attempts! Exiting...\n")
            exit()

        Server_password = input("🔒 Enter the Server Password: ")
        if len(Server_password) < 9:
            print("❗ Password must be at least 9 characters long.\n")
            continue

        client.send(f"{len(Server_password):04}".encode('utf-8'))
        client.send(Server_password.encode('utf-8'))

        UserVerify = int(client.recv(4).decode('utf-8'))
        UserVerify = client.recv(UserVerify).decode('utf-8')

        if UserVerify == 'access denied':
            print("🚫 Access Denied!\n")
            Server_PASS_Try += 1
        else:
            print("✅ Access Granted!\n")
            break

    AdminVerify = int(client.recv(4).decode('utf-8'))
    AdminVerify = client.recv(AdminVerify).decode('utf-8')

    if AdminVerify == 'admin?':
        check = input("👑 Are you an Admin! [Yes/No]: ")
        client.send(f"{len(check):04}".encode('utf-8'))
        client.send(check.encode('utf-8'))

        if check.lower() == 'yes':
            Admin_PASS_Try = 0
            while Admin_PASS_Try < 3:
                AdminPassword = input("Enter the Admin Password: ")
                if len(AdminPassword) < 9:
                    print("❗ Password must be at least 9 characters long.\n")
                    continue

                client.send(f"{len(AdminPassword):04}".encode('utf-8'))
                client.send(AdminPassword.encode('utf-8'))

                response_length = int(client.recv(4).decode('utf-8'))
                AdminVerify = client.recv(response_length).decode('utf-8')

                if AdminVerify == 'access denied':
                    Admin_PASS_Try += 1
                    print("🚫 Access Denied!\n")
                else:
                    print("✅ Access Granted!\n")
                    break
            else:
                print("⚠️ Too many attempts! Exiting...\n")
                exit()

except KeyboardInterrupt:
    print("Keyboard Interrupt!")
    exit()
except Exception as e:
    print(f"⚠️ [ERROR] : {e}\n")
    exit()


def send(msg):
    message = msg.encode('utf-8')
    msg_length = len(message)
    send_length = str(msg_length).encode('utf-8')
    send_length += b' ' * (64 - len(send_length))
    client.send(send_length)
    client.send(message)


def receive():
    try:
        while True:
            message = client.recv(2048).decode('utf-8')
            if message == f"[200]Exit":
                print("❌ You are disconnected from the server!\n")
                break
            else:
                print(f"{message}\n")
    except Exception as e:
        print(f"🔒 Connection was closed by the Server [{ADDR}]!\n")
        print(f"⚠️ [ERROR] : {e}\n")


def main():
    
    while True:
        try:
            message = input()
            cmd = message.strip().lower()

            if cmd.startswith(f"{ClientPrefix}help"):
                print(f"""
🟢 {ClientPrefix}online: Check online members
👑 {ClientPrefix}adminlist: Show all Admins
🚫 {ClientPrefix}ban: Ban Member (Admin only)
✅ {ClientPrefix}unban: Unban Member (Admin only)
📋 {ClientPrefix}banlist: Show Banned Members (Admin only)
🔇 {ClientPrefix}mute: Mute Member (Admin only)
🔊 {ClientPrefix}unmute: Unmute Member (Admin only)
📢 {ClientPrefix}announce: Server-wide message (Admin only)
👢 {ClientPrefix}kick: Kick Member (Admin only)
🌐 {ClientPrefix}serverinfo: Server info
🚪 {ClientPrefix}exit: Exit chat
""")

            elif cmd.startswith(f"{ClientPrefix}exit"):
                send(f"{ClientPrefix}exit")
                break

            elif cmd in [f"{ClientPrefix}banlist", f"{ClientPrefix}adminlist",
                         f"{ClientPrefix}serverinfo", f"{ClientPrefix}online"]:
                send(message)

            elif cmd.startswith(f"{ClientPrefix}unban"):
                send(f"{ClientPrefix}unban")
                index = input("🔢 Enter index to unban: ")
                client.send(f"{len(index):04}".encode('utf-8'))
                client.send(index.encode('utf-8'))

            elif cmd.startswith(f"{ClientPrefix}ban") and not cmd.startswith(f"{ClientPrefix}unban"):
                send(f"{ClientPrefix}ban")
                index = input("🔢 Enter index to ban: ")
                client.send(f"{len(index):04}".encode('utf-8'))
                client.send(index.encode('utf-8'))

            elif cmd.startswith(f"{ClientPrefix}kick"):
                send(f"{ClientPrefix}kick")
                index = input("🔢 Enter index to kick: ")
                client.send(f"{len(index):04}".encode('utf-8'))
                client.send(index.encode('utf-8'))

            elif cmd.startswith(f"{ClientPrefix}mute"):
                send(f"{ClientPrefix}mute")
                index = input("🔢 Enter index to mute: ")
                client.send(f"{len(index):04}".encode('utf-8'))
                client.send(index.encode('utf-8'))

            elif cmd.startswith(f"{ClientPrefix}unmute"):
                send(f"{ClientPrefix}unmute")
                index = input("🔢 Enter index to unmute: ")
                client.send(f"{len(index):04}".encode('utf-8'))
                client.send(index.encode('utf-8'))

            elif cmd.startswith(f"{ClientPrefix}announce"):
                send(f"{ClientPrefix}announce")
                announcement = input("📢 Enter announcement message: ")
                client.send(f"{len(announcement):04}".encode('utf-8'))
                client.send(announcement.encode('utf-8'))

            else:
                send(message)

        except Exception as e:
            print(f"⚠️ Error: {e}\n")
            break

try:
    threading.Thread(target=receive).start()
    threading.Thread(target=main).start()
except Exception as e:
    print(f"⚠️ [Thread Error] : {e}")
    exit()
