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

# Alternative game state variables
ballX1 = 0
ballX2 = 0
ballY1 = 0
ballY2 = 0
lScore1 = 0
lScore2 = 0
rScore1 = 0
rScore2 = 0
sync1 = 0
sync2 = 0

screenWidth = 640
screenHeight = 480

# Lock threads for synchronization
lock = threading.Lock()

# Variable to track connected players
connectedPlayers = 0


# Function to handle a single client
def handleClient(clientSocket: socket.socket, playerNumber: int) -> None:
    global connectedPlayers, player1PaddleY, player2PaddleY, ballX, ballY, lScore, rScore, sync
    global ballX1, ballX2, ballY1, ballY2, lScore1, lScore2, rScore1, rScore2, sync1, sync2

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

    playerGameSettings = {
        "screenWidth": screenWidth,
        "screenHeight": screenHeight,
        "playerPaddle": ""
    }
    if playerNumber == 1:
        playerGameSettings["playerPaddle"] = "left"
    elif playerNumber == 2:
        playerGameSettings["playerPaddle"] = "right"
    
    clientSocket.send(",".join(map(str, playerGameSettings.values())).encode())
    
    # Wait for both players to connect
    connectedPlayers += 1
    while connectedPlayers < maxClients:
        pass

    while True:
        try:
            # Get client1 data
            # Get client2 data
            # Compare sync numbers
            # Send game state of client with higher sync number to both clients
            
            data = clientSocket.recv(1024).decode()

            # Split the received data
            receivedData = data.split(",")

            sync, lScore, rScore, ballX, ballY, playerPaddleY = map(int, receivedData)
            
            if playerNumber == 1:
                sync1 = sync
                lScore1 = lScore
                rScore1 = rScore
                ballX1 = ballX
                ballY1 = ballY
            elif playerNumber == 2:
                sync2 = sync
                lScore2 = lScore
                rScore2 = rScore
                ballX2 = ballX
                ballY2 = ballY

            if sync1 >= sync2:
                playerGameState["sync"] = sync1
                playerGameState["lScore"] = lScore1
                playerGameState["rScore"] = rScore1
                playerGameState["ballX"] = ballX1
                playerGameState["ballY"] = ballY1
            elif sync2 > sync1:
                playerGameState["sync"] = sync2
                playerGameState["lScore"] = lScore2
                playerGameState["rScore"] = rScore2
                playerGameState["ballX"] = ballX2
                playerGameState["ballY"] = ballY2
            
            playerGameState["paddleY"] = playerPaddleY

            with lock:
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
