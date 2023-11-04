# =================================================================================================
# Contributing Authors:	    Sean Evans, Cameron Egbert
# Email Addresses:          siev223@uky.edu,  cmeg225@uky.edu
# Date:                     11/4/23
# Purpose:                  Establishes the pong server that will handle player clients. The script
#                           secures connections between clients and handles the transfer of
#                           information between clients while keeping the games synced as best as 
#                           possible.
# =================================================================================================

import socket
import threading

# Define constants
serverIp = "127.0.0.1"
serverPort = 12321
maxClients = 2

# Create a socket and bind it to the server IP and port
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.bind((serverIp, serverPort))
serverSocket.listen(maxClients)

# Lists to hold client connections and their corresponding threads
clients = []
threads = []

# Game state variables
player1PaddleY = 0  # Initialize paddle positions
player2PaddleY = 0
ballX = 0
ballY = 0
lScore = 0
rScore = 0
sync = 0

screenWidth = 640
screenHeight = 480
playerPaddle = ""

# Lock threads for synchronization
lock = threading.Lock()

# Variable to track connected players
connectedPlayers = 0

# Function to handle a single client
# Function to handle a single client
def handleClient(clientSocket: socket.socket, playerNumber: int) -> None:
    global connectedPlayers, player1PaddleY, player2PaddleY, ballX, ballY, lScore, rScore, sync, screenWidth, screenHeight, playerPaddle

    # Initialize player-specific variables
    playerPaddleY = 0
    playerGameState = {
        "sync": sync,
        "lScore": lScore,
        "rScore": rScore,
        "ballX": ballX,
        "ballY": ballY,
        "paddleY": playerPaddleY,
    }

    # Send the player their own game state
    # Set the appropriate paddle position based on the player number
    if playerNumber == 1:
        playerPaddleY = player1PaddleY
        playerGameSettings = {
            "screenWidth": screenWidth,
            "screenHeight": screenHeight,
            "playerPaddle": "left"
        }
    else:
        playerPaddleY = player2PaddleY
        playerGameSettings = {
            "screenWidth": screenWidth,
            "screenHeight": screenHeight,
            "playerPaddle": "right"
        }
    
    clientSocket.send(",".join(map(str, playerGameSettings.values())).encode())
    
    # Wait for both players to connect
    connectedPlayers += 1
    while connectedPlayers < maxClients:
        pass

    while True:
        try:
            # Receive game updates from the client
            data = clientSocket.recv(1024).decode()
            if not data:
                break

            # Split the received data
            receivedData = data.split(",")

            if len(receivedData) == 5:
                # This is the start of the game loop message
                lScore, rScore, ballX, ballY, playerPaddleY = map(int, receivedData)
            elif len(receivedData) == 6:
                # This is the end of the game loop message
                sync, lScore, rScore, ballX, ballY, playerPaddleY = map(int, receivedData)
                
            # Update the game state
            playerGameState = {
                "sync": sync,
                "lScore": lScore,
                "rScore": rScore,
                "ballX": ballX,
                "ballY": ballY,
                "paddleY": playerPaddleY,
            }

            # Relay updated game state to the other client
            with lock:
                # Determine the recipient player's index
                if playerNumber == 1:
                    clients[1].send(",".join(map(str, playerGameState.values())).encode())
                elif playerNumber == 2:
                    clients[0].send(",".join(map(str, playerGameState.values())).encode())

        except Exception as e:
            print(f"Error handling client: {e}")
            break

    clientSocket.close()
    

# Function to listen for client connections
def acceptClients():
    global clients, threads

    while len(clients) < maxClients:
        clientSocket, clientAddr = serverSocket.accept()
        playerNumber = len(clients) + 1
        print(f"Client {playerNumber} connected from {clientAddr}")
        clients.append(clientSocket)
        clientThread = threading.Thread(target=handleClient, args=(clientSocket, playerNumber))
        threads.append(clientThread)
        clientThread.start()

# Start the server
print(f"Server listening on {serverIp}:{serverPort}")
acceptClients()

# Wait for all client threads to finish
for thread in threads:
    thread.join()

# Close the server socket
serverSocket.close()
