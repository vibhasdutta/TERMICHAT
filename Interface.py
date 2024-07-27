import time
import subprocess
from Server import start
import socket
import json


def client_run():
    from pathlib import Path
        # Get the base directory of the script
    base_dir = Path(__file__).resolve().parent

    # Define the TERMICHAT directory
    termichat_dir = base_dir / 'Client.py'
    subprocess.Popen(['start', 'cmd', '/k', 'python',termichat_dir], shell=True)


if __name__ == '__main__':
    
    with open('config.json') as f:
        data = json.load(f)

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

            with open('config.json') as f:
                    data = json.load(f)

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
                    IP_Address=input("Enter the IP Address:")
                    PORT=int(input("Enter the PORT:"))
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
