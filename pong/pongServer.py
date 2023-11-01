# =================================================================================================
# Contributing Authors:	    Sean Evans
# Email Addresses:          siev223@uky.edu
# Date:                     11/1/23
# Purpose:                  Establishes the pong server that will handle player clients
# Misc:                     <Not Required.  Anything else you might want to include>
# =================================================================================================

import socket
import threading

# Define constants
SERVER_IP = "127.0.0.1"
SERVER_PORT = 12321
MAX_CLIENTS = 2

# Create a socket and bind it to the server IP and port
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((SERVER_IP, SERVER_PORT))
server_socket.listen(MAX_CLIENTS)

# Lists to hold client connections and their corresponding threads
clients = []  # type: List[socket.socket]
threads = []  # type: List[threading.Thread]

# Game state variables
player1_paddle_y = 0  # Initialize paddle positions
player2_paddle_y = 0
ball_x = 0
ball_y = 0
score1 = 0
score2 = 0

# Lock for thread synchronization
lock = threading.Lock()

# Start the server
print(f"Server listening on {SERVER_IP}:{SERVER_PORT}")

# Wait for all client threads to finish
for thread in threads:
    thread.join()

# Close the server socket
server_socket.close()


# Use this file to write your server logic
# You will need to support at least two clients
# You will need to keep track of where on the screen (x,y coordinates) each paddle is, the score 
# for each player and where the ball is, and relay that to each client
# I suggest you use the sync variable in pongClient.py to determine how out of sync your two
# clients are and take actions to resync the games