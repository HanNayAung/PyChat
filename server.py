#!/usr/bin/env python3
#
#
# Copyright (c) 2024, Han Nay Aung.
# All rights reserved.
#
import socket
import select

HEADER_LENGTH = 10

ip = "0.0.0.0"    # using 0.0.0.0 means to listen on all available interfaces
port = 1234       # you can change any big numbers you like. Num. 80 is an html page, so you cannot use.

# create a socket [socket() -> bind() -> listen() -> accept()]
# socket.AF_INET =  address family, IPv4, some other possible are AF_INET6, AF_BLUETOOTH, AF_UNIX
# socket.SOCK_STREAM = TCP, conection-based, socket.SOCK_DGRAM - UDP, connectionless, datagrams, socket.SOCK_RAW - raw IP packets
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((ip, port))
server_socket.listen()

# list of sockets to monitor
sockets = [server_socket]

# list of clients, store client name.
clients = {}

print('Listening for connections on {}:{}...'.format(ip, port))


def receive_message(client_socket):
    try:
        message_header = client_socket.recv(HEADER_LENGTH)
        # if no data was received ,close
        if not len(message_header):
            return False
        # remove space in string
        message_length = int(message_header.decode('utf-8').strip())  
        return {'header': message_header, 'data': client_socket.recv(message_length)}
    except:
        return False


def weather():
    try:
        message_data = "We will search for u".encode('utf-8')
        message_length = b'20        '
        return {'header': message_length, 'data': (message_data)}
    except:
        print("error")
        return False


def server_name():
    try:
        name_data = "server".encode('utf-8')
        name_length = b'6         '
        return {'header': name_length, 'data': (name_data)}
    except:
        print("error")
        return False


def send_picture(filename):
    # send a picture file to a client
    try:
        # Read the image file as binary data
        with open(filename, "rb") as file:
            image_data = file.read()

        # encode the length of the image data in the header
        image_length = f"{len(image_data):<{HEADER_LENGTH}}".encode('utf-8')

        return {'header': image_length, 'data': image_data}
    except Exception as e:
        print(f"Error reading image file: {e}")
        return False


while True:
    # wait until any socket is ready for processing
    readable, writable, exceptional = select.select(sockets, [], [])
    for sock in readable:
        # if a new connection, accept it
        if sock == server_socket:

            # accept new connection
            client_socket, client_address = server_socket.accept()

            # recceive client name
            user = receive_message(client_socket)
            if user is False:
                continue

            # add client_socket to  sockets
            sockets.append(client_socket)

            # save username and username header
            clients[client_socket] = user
            print('Accepted new connection from {}:{}, username-> {}'.format(*client_address, user['data'].decode('utf-8')))

        # if already existing socket is sending a message
        else:
            # handle data received from clients
            message = receive_message(sock)

            # example {'header': b'2         ', 'data': b'hi'}
            # print(message)
            
            # If the client return no data. will be assumbed as disconnects, clean up.
            if message is False:
                print('Closed connection from: {}'.format(clients[sock]['data'].decode('utf-8')))
                # remove from list for sockets
                sockets.remove(sock)
                # remove from list of clients
                del clients[sock]
                continue

            # get user name  by notified socket, so we will know who sent the message.
            user_name = clients[sock]
            print('Received message from {}: {}'.format(user_name["data"].decode("utf-8"), message["data"].decode("utf-8")))

            if message['data'] != b'quit':
                if message['data'] == b'weather':
                    for client_socket in clients:
                        if client_socket == sock:
                            reply = weather()
                            name = server_name()
                            client_socket.send(name['header'] + name['data'] + reply['header'] + reply['data'])
                            print("{} {} {} {} ".format(name['header'], name['data'], reply['header'], reply['data']))

                elif message['data'] == b'get_picture':
                    for client_socket in clients:
                        if client_socket == sock:
                            picture = send_picture("code.png")
                            name = server_name()
                            client_socket.send(name['header'] + name['data'] + picture['header'] + picture['data'])
                            # print(name['header'] + name['data'] + picture['header'] + picture['data'])
                            print("Sent picture to client.")

            # broadcast message over connected clients
            for client_socket in clients:
                # the message will be sent to all clients except the server
                if client_socket != sock:
                    # message header sent by sender, and saved username header send by user when he connected
                    client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])
                    print("log {} {} {} {} ".format(user['header'],user['data'],message['header'],message['data']))
                    
