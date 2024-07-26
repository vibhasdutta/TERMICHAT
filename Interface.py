import dotenv
import os
import time
dotenv.load_dotenv()
import subprocess
from Server import start
import socket



def client_run():
    from pathlib import Path
        # Get the base directory of the script
    base_dir = Path(__file__).resolve().parent

    # Define the TERMICHAT directory
    termichat_dir = base_dir / 'Client.py'
    subprocess.Popen(['start', 'cmd', '/k', 'python',termichat_dir], shell=True)

if __name__ == '__main__':

    if os.getenv('user_name')=='your username'  or os.getenv('SERVER_IP')=='your ip or server ip' or os.getenv('PORT')=='your port':
        print("Please set the settings first!")
        time.sleep(2)
        print("Enter the following details:")
        IP_Address = input("Enter the IP Address:")
        PORT = int(input("Enter the PORT:"))
        Prefix = input("Enter the Prefix:")
        UserName = input("Enter the UserName:")
        os.putenv('USER_NAME',UserName)
        os.putenv('Prefix',Prefix)
        os.putenv('PORT',str(PORT))
        os.putenv('SERVER_IP',IP_Address)

    try:
        Prefix = os.getenv('Prefix')
        UserName = os.getenv('USER_NAME')
        PORT = int(os.getenv('PORT'))
        IP_Address = os.getenv('SERVER_IP')
        ADDR=(IP_Address,PORT)
        server=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        server.bind(ADDR)
    except Exception:
        print("The IP Address or PORT is invalid!")
        exit()


    print("Welcome to the TERMICHAT!")

    print("Do you want to Host or Connect the SERVER?[Y/N]")
    while True:
        choice=input("Enter your choice:")
        if choice.lower()=='y':
            IP_Address = socket.gethostbyname(socket.gethostname())
            os.putenv('HOSTING_ON','True')
            break;
        elif choice.lower()=='n':
            pass
        else:
            print("Invalid Choice!")
        

    while True:
        try:
            print(f"\nEnter {Prefix}start_server : to start the Server \n{Prefix}settings : to set server ip,port,prefix and username \n{Prefix}exit : to exit the chat\n")
            choice=input("Enter your choice:")
            
            if all (character in choice for character in [Prefix,'start_server']):

                start(UserName,Prefix,server,ADDR)
                time.sleep(2)
            
            elif all (character in choice for character in [Prefix,'settings']):
                    
                    print("Enter the following details:")
                    IP_Address = input("Enter the IP Address:")
                    PORT = int(input("Enter the PORT:"))
                    Prefix = input("Enter the Prefix:")
                    UserName = input("Enter the UserName:")
                    os.putenv('USER_NAME',UserName)
                    os.putenv('Prefix',Prefix)
                    os.putenv('PORT',str(PORT))
                    os.putenv('SERVER_IP',IP_Address)

            elif all (character in choice for character in [Prefix,'exit']):
                
                print("Exiting...")
            
            else:
                
                print("Invalid Input!")
        
        except KeyboardInterrupt:
            print("Exiting...")
            break