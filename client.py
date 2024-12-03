#!/usr/bin/env python3
#
#
# Copyright (c) 2024, Han Nay Aung.
# All rights reserved.
#
import socket
import errno
import time
import sys

HEADER_LENGTH = 10

# to connect with server, socket() -> connect()
ip = "192.168.0.20"
port = 1234
my_username = input("Username: ")
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((ip, port))
client_socket.setblocking(False)

# Prepare username and header and send them
username = my_username.encode('utf-8')
username_header = f"{len(username):<{HEADER_LENGTH}}".encode('utf-8')
client_socket.send(username_header + username)

while True:

    # wait for user to input a message
    message = input('{} > '.format(my_username))
    if message == 'quite':
        quit()

    # if message is not empty  send it
    if message:
        
        # prepare message and header
        message = message.encode('utf-8')
        message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
        client_socket.send(message_header + message)

    try:
        # now we want to loop over received messages
        while True:

            username_header = client_socket.recv(HEADER_LENGTH)

            # If we received no data from server, gracefully closed a connection
            if not len(username_header):
                print('Connection closed by the server')
                sys.exit()

            # convert header to int value
            username_length = int(username_header.decode('utf-8').strip())
            # decode username
            username = client_socket.recv(username_length).decode('utf-8')

            # receive whole message, there's no need to check if it has any length)
            message_header = client_socket.recv(HEADER_LENGTH)
            message_length = int(message_header.strip())
            message = client_socket.recv(message_length)

            if message[:8] == b'\x89PNG\r\n\x1a\n':
                # If the message starts with PNG header, it's an image

                timestamp = time.strftime("%Y%m%d_%H%M%S", time.gmtime())
                filename = f"{my_username}_received_{timestamp}.png"

                with open(filename, "wb") as img_file:
                    img_file.write(message)
                print(f"Image received and saved as '{filename}'")
            else:
                # if it's a text message, decode it as UTF-8
                print(f'{username} > {message.decode("utf-8")}')

    except IOError as e:
        # some os will indicate that using AGAIN, and some using WOULDBLOCK error code
        # we are going to check for both - if one of them - that's expected, means no incoming data, continue as normal
        # if we got different error code - something happened
        if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
            print('Reading error: {}'.format(str(e)))
            sys.exit()

        # we just did not receive anything
        continue

    except Exception as e:
        # any other exception - something happened, exit
        print('Reading error: {}'.format(str(e)))
        sys.exit()
