import time
import subprocess
from Server import start
import socket
import json
import platform
from pathlib import Path
import re

def is_valid_ip(ip):
    pattern = re.compile(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$")
    if pattern.match(ip):
        return all(0 <= int(num) <= 255 for num in ip.split('.'))
    return False



def client_run():
    # Get the base directory of the script
    base_dir = Path(__file__).resolve().parent
    # Define the TERMICHAT directory
    termichat_dir = base_dir / 'Client.py'
    
    # Determine the operating system
    os_name = platform.system()

    if os_name == "Windows":
        subprocess.Popen(['start', 'cmd.exe', '/k', 'python', str(termichat_dir)], shell=True)
    elif os_name == "Darwin":  # macOS
        subprocess.Popen(['osascript', '-e', f'tell application "Terminal" to do script "python {termichat_dir}"'])
    elif os_name == "Linux":
        try:
            subprocess.Popen(['x-terminal-emulator', '-e', 'python', str(termichat_dir)])
        except FileNotFoundError:
            subprocess.Popen(['gnome-terminal', '--', 'python', str(termichat_dir)])
    else:
        raise OSError("Unsupported operating system")


if __name__ == '__main__':
    
    with open('config.json') as f:
        data = json.load(f)

    Prefix = data['PREFIX']
    PORT = data['PORT']
    IP_Address = data['SERVER_IP']

    print("Welcome to the TERMICHAT!") 

    while True:
        print("Do you want to Host or Connect the SERVER?[H/C]")
        choice=input("Enter your choice:")
        
        if choice.lower()=='h':
            
            IP_Address = socket.gethostbyname(socket.gethostname())
            while True:
                try:
                    port_number = int(input("Enter the Server PORT:"))
                    if 1 <= port_number <= 65535:
                        with open('config.json','w') as f:
                            data['PORT'] = port_number
                            json.dump(data,f)
                        break
                    else:
                        print("Invalid port. Please enter a number between 1 and 65535.")
                except ValueError:
                    print("Invalid port. Please enter a valid number.")
            break;
        
        elif choice.lower()=='c':
            while True:
                try:
                    ip_address = input("Enter the Server IP:")
                    if is_valid_ip(ip_address):
                        with open('config.json','w') as f:
                            data['IP'] = ip_address
                            json.dump(data,f)
                        break
                    else:
                        print("Invalid IP address. Please enter a valid IP address.")
                except ValueError:
                    print("Invalid IP address. Please enter a valid IP address.")

            while True:
                try:
                    port_number = int(input("Enter the Server PORT:"))
                    if 1 <= port_number <= 65535:
                        with open('config.json','w') as f:
                            data['PORT'] = port_number
                            json.dump(data,f)
                        break
                    else:
                        print("Invalid port. Please enter a number between 1 and 65535.")
                except ValueError:
                    print("Invalid port. Please enter a valid number.")
            break;
        
    while True:
        try:
            print(f"\nEnter {Prefix}start_server : to start the Server \n {Prefix}start_client : to join server \n{Prefix}exit : to exit the menu\n")
            choice=input("Enter your choice:")
            
            if all (character in choice for character in [Prefix,'start_server']):
                ADDR=(IP_Address,PORT)
                server=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                server.bind(ADDR)

                start(server,ADDR,IP_Address,PORT)
                time.sleep(2)

            elif all (character in choice for character in [Prefix,'start_client']):   
                
                client_run()    
                time.sleep(2) 
            
            elif all (character in choice for character in [Prefix,'exit']):
                
                print("Exiting...")
                exit()
            
            else:
                
                print("Invalid Input!")
        
        except KeyboardInterrupt:
            print("Exiting...")
            break
