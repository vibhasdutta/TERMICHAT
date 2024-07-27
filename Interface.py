import time
import subprocess
from Server import start
import socket
import json
import platform
from pathlib import Path

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

    with open('config.json','w') as f:
        data['USER_NAME'] = socket.gethostname()
        json.dump(data,f)

    print("Welcome to the TERMICHAT!")

    print("Do you want to Host or Connect the SERVER?[H/C]")
    while True:
        choice=input("Enter your choice:")
        if choice.lower()=='h':
            with open('config.json','w') as f:
                data['SERVER_IP'] = socket.gethostbyname(socket.gethostname())
                data['PORT'] = int(input("Enter the Server PORT:"))
                json.dump(data,f)
            break;
        elif choice.lower()=='c':
            with open('config.json','w') as f:
                data['SERVER_IP'] = input("Enter the Server IP:")
                data['PORT'] = int(input("Enter the Server PORT:"))
                json.dump(data,f)
            break;
        else:
            print("Invalid Choice!")
        
    while True:
        try:
            
            Prefix = data['PREFIX']
            UserName = data['USER_NAME']
            PORT = data['PORT']
            IP_Address = data['SERVER_IP']


            print(f"\nEnter {Prefix}start_server : to start the Server \n{Prefix}settings : to set prefix and username \n{Prefix}exit : to exit the chat\n")
            choice=input("Enter your choice:")
            
            if all (character in choice for character in [Prefix,'start_server']):
                ADDR=(IP_Address,PORT)
                server=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                server.bind(ADDR)

                start(UserName,Prefix,server,ADDR,IP_Address,PORT)
                time.sleep(2)
            
            elif all (character in choice for character in [Prefix,'settings']):
                    
                    print("Enter the following details:")
                    Prefix=input("Enter the Prefix:")
                    UserName=input("Enter the UserName:")
                    with open('config.json','w') as f:
                        data['PREFIX'] = Prefix
                        data['USER_NAME'] = UserName
                        json.dump(data,f)
                    print("Settings Updated!")
                    
            elif all (character in choice for character in [Prefix,'exit']):
                
                print("Exiting...")
            
            else:
                
                print("Invalid Input!")
        
        except KeyboardInterrupt:
            print("Exiting...")
            break
