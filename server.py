# Written by Zach Keeler, Raymond Bicknell, and Heidi Lamb at CSU for CS370 in Fall 2022

from socket import socket, gethostbyname, AF_INET, SOCK_DGRAM

# settings for the server
PORT_NUMBER = 5000
SIZE = 1024
hostName = gethostbyname( '0.0.0.0' )
mySocket = socket( AF_INET, SOCK_DGRAM )
mySocket.bind( (hostName, PORT_NUMBER) )

# receives and prints messages from the window sensors computer
if __name__ == "__main__":
    while True:
        (data,addr) = mySocket.recvfrom(SIZE)
        print(data.decode('utf-8'))