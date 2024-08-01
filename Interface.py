import time
import re
from Server import start
import socket
import json
import subprocess
import platform
from pathlib import Path
import ssl


def is_valid_ip(ip):
    pattern = re.compile(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$")
    if pattern.match(ip):
        return all(0 <= int(num) <= 255 for num in ip.split('.'))
    return False


def client_run():
    # Get the base directory of the script
    base_dir = Path(__file__).resolve().parent
    # Define the Client.py path
    clientpy_path = base_dir / 'Client.py'
    
    # Determine the operating system
    os_name = platform.system()

    try:
        if os_name == "Windows":
            subprocess.Popen(['start', 'cmd.exe', '/k', 'python', str(clientpy_path)], shell=True)
        elif os_name == 'Darwin':  # macOS
            script = f"""
            tell application "Terminal"
                do script "cd {base_dir} && python3 {clientpy_path}"
            end tell
            """
            subprocess.Popen(['osascript', '-e', script])
        elif os_name == 'Linux':  # Linux (including Linux Mint)
            subprocess.Popen(['gnome-terminal', '--', 'bash', '-c', f'python3 {clientpy_path}'])
        else:
            raise OSError(f"Unsupported operating system: {os_name}")
    except Exception as e:
        print(f"⚠️ An error occurred:{e}")


def Input():
    while True:
        try:
            IP_Address = input("🌐 Enter the Server IP: ")
            if is_valid_ip(IP_Address):
                with open('config.json', 'w') as f:
                    data['SERVER_IP'] = IP_Address
                    json.dump(data, f)
                break
            else:
                print("❌ Invalid IP address. Please enter a valid IP address.")
        except ValueError:
            print("❌ Invalid IP address. Please enter a valid IP address.")
    while True:
        try:
            PORT = int(input("🔌 Enter the Server PORT: "))
            if 1 <= PORT <= 65535:
                with open('config.json', 'w') as f:
                    data['PORT'] = PORT
                    json.dump(data, f)
                break
            else:
                print("❌ Invalid port. Please enter a number between 1 and 65535.")
        except ValueError:
            print("❌ Invalid port. Please enter a valid number.")
    return IP_Address, PORT


if __name__ == '__main__':
    
    with open('config.json') as f:
        data = json.load(f)

    Prefix = data['PREFIX']
    PORT = data['PORT']
    IP_Address = data['SERVER_IP']

    print("\n---🍁 WELCOME TO TERMICHAT 🍁 ---\n") 

    try:
        while True:
            print(f"{Prefix}start_server : 🌐 to start the Server\n{Prefix}start_client : 🖥️  to join server\n{Prefix}exit : 🚪 to exit the menu\n")
            choice = input("Enter your choice: ")
            
            if all (character in choice for character in [Prefix, 'start_server']):
                
                IP_Address, PORT = Input()
                ADDR = (IP_Address, PORT)
                server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                # SSL context
                context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
                context.load_cert_chain(certfile='server.crt', keyfile='server.key')
                
                # Wrap socket
                server = context.wrap_socket(server, server_side=True)
                
                server.bind(ADDR)
                start(server, ADDR, IP_Address, PORT)
                time.sleep(2)
                break;
            
            elif all (character in choice for character in [Prefix, 'start_client']):
                Input()
                client_run()
                break;
            elif all (character in choice for character in [Prefix, 'exit']):
                print("👋 Exiting...")
                exit()
            else:
                print("⚠️ Invalid Input!")
        
    except KeyboardInterrupt:
        print("👋 Exiting...")