import time
import re
from Server import start
import socket
import json

def is_valid_ip(ip):
    pattern = re.compile(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$")
    if pattern.match(ip):
        return all(0 <= int(num) <= 255 for num in ip.split('.'))
    return False



if __name__ == '__main__':
    
    with open('config.json') as f:
        data = json.load(f)

    Prefix = data['PREFIX']
    PORT = data['PORT']
    IP_Address = data['SERVER_IP']

    print("Welcome to the TERMICHAT!") 

    while True:

        print(f"\nEnter {Prefix}start_server : to start the Server \n {Prefix}start_client : to join server \n{Prefix}exit : to exit the menu\n")
        
        choice=input("Enter your choice:")
        
        try :
            if all (character in choice for character in [Prefix,'start_server']):
                
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

                ADDR=(IP_Address,PORT)
                server=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                server.bind(ADDR)
                start(server,ADDR,IP_Address,PORT)
                break;
            
            elif all (character in choice for character in [Prefix,'start_client']):
                while True:
                    try:
                        ip_address = input("Enter the Server IP:")
                        if is_valid_ip(ip_address):
                            with open('config.json','w') as f:
                                data['SERVER_IP'] = ip_address
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

                import Client
            
            elif all (character in choice for character in [Prefix,'exit']):
                    
                    print("Exiting...")
                    exit()
                
            else:   
                print("Invalid Input!")
        
        except KeyboardInterrupt:
            print("Exiting...")
            exit()

    