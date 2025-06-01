# ─────────────────────────────────────────────
# TermiChat Server — Version 1.0
# Author: VibhasDutta
# Date Updated: 2025-06-01
# ─────────────────────────────────────────────
import time
import re
import socket
import json
import subprocess
import platform
from pathlib import Path


def is_valid_ip(ip):
    pattern = re.compile(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$")
    if pattern.match(ip):
        return all(0 <= int(num) <= 255 for num in ip.split('.'))
    return False


def update_config(new_data):
    try:
        with open('config.json', 'r') as f:
            data = json.load(f)
    except:
        data = {}

    data.update(new_data)
    with open('config.json', 'w') as f:
        json.dump(data, f, indent=4)


def client_run():
    base_dir = Path(__file__).resolve().parent
    clientpy_path = base_dir / 'Client.py'
    os_name = platform.system()
def client_run_gui():
    base_dir = Path(__file__).resolve().parent
    clientpy_path = base_dir / 'client_gui.py'
    os_name = platform.system()

    try:
        if os_name == "Windows":
            subprocess.Popen(['start', 'cmd.exe', '/k', 'python', str(clientpy_path)], shell=True)
        elif os_name == 'Darwin':
            script = f"""
            tell application \"Terminal\"
                do script \"cd {base_dir} && python3 {clientpy_path}\"
            end tell
            """
            subprocess.Popen(['osascript', '-e', script])
        elif os_name == 'Linux':
            subprocess.Popen(['gnome-terminal', '--', 'bash', '-c', f'python3 {clientpy_path}'])
        else:
            raise OSError(f"Unsupported OS: {os_name}")
    except Exception as e:
        print(f"⚠️ Error launching client: {e}")


def Input():
    while True:
        IP_Address = input("🌐 Enter the Server IP: ")
        if is_valid_ip(IP_Address):
            break
        else:
            print("❌ Invalid IP. Try again.")

    while True:
        try:
            PORT = int(input("🔌 Enter the Server PORT: "))
            if 1 <= PORT <= 65535:
                break
            else:
                print("❌ Port must be between 1 and 65535.")
        except ValueError:
            print("❌ Invalid input. Port must be a number.")

    update_config({"SERVER_IP": IP_Address, "PORT": PORT})
    return IP_Address, PORT


if __name__ == '__main__':
    try:
        with open('config.json') as f:
            data = json.load(f)
    except:
        data = {"PREFIX": "!", "PORT": 8080, "SERVER_IP": "127.0.0.1"}

    Prefix = data.get('PREFIX', '!')
    PORT = data.get('PORT', 8080)
    IP_Address = data.get('SERVER_IP', '127.0.0.1')

    print(r"""
 _       __     __                             ______         ______                    _ ________          __ 
| |     / /__  / /________  ____ ___  ___     /_  __/___     /_  __/__  _________ ___  (_) ____/ /_  ____ _/ /_
| | /| / / _ \/ / ___/ __ \/ __ `__ \/ _ \     / / / __ \     / / / _ \/ ___/ __ `__ \/ / /   / __ \/ __ `/ __/
| |/ |/ /  __/ / /__/ /_/ / / / / / /  __/    / / / /_/ /    / / /  __/ /  / / / / / / / /___/ / / / /_/ / /_  
|__/|__/\___/_/\___/\____/_/ /_/ /_/\___/    /_/  \____/    /_/  \___/_/  /_/ /_/ /_/_/\____/_/ /_/\__,_/\__/  

TermiChat Client — Version 1.0 | Author: VibhasDutta | Updated: 2025-06-01
""")

    try:
        while True:
            print(f"{Prefix}start_server : 🌐 Start the Server\n{Prefix}start_client_cli \n{Prefix}start_client_gui: 🖥️ \n{Prefix}exit : 🚪 Exit Menu\n")
            choice = input("Enter your choice: ")

            if choice.startswith(f"{Prefix}start_server"):
                IP_Address, PORT = Input()
                ADDR = (IP_Address, PORT)
                server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server.bind(ADDR)

                from Server import start
                start(server, ADDR, IP_Address, PORT)
                break

            elif choice.startswith(f"{Prefix}start_client_cli"):
                Input()
                client_run()
                break
            elif choice.startswith(f"{Prefix}start_client_gui"):
                client_run_gui()
                break
            elif choice.startswith(f"{Prefix}exit"):
                print("👋 Exiting...")
                exit()

            else:
                print("⚠️ Invalid input. Try again.")

    except KeyboardInterrupt:
        print("👋 Exiting...")
