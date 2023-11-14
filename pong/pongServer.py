# =================================================================================================
# Contributing Authors:	    Sean Evans, Cameron Egbert, Matt Mitchell
# Email Addresses:          siev223@uky.edu, cmeg225@uky.edu, 
# Date:                     11/13/23
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

# Game state variables that save information from client1 and client2 respectively
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


def handleClient(clientSocket: socket.socket, playerNumber: int) -> None:
    # Authors:      Sean Evans, Matt Mitchell
    # Purpose:      This method is called on a separate thread for each client that connects. It will
    #               send the game settings to the client, receive the game state sent from the client, 
    #               and compare the sync values of the two clients. It will send the game state
    #               belonging to the client with the higher sync value to both clients.
    # Pre:          This method expects the client to already be connected to the server, with each
    #               client stored in a list of clients before being called. It also expects the player 
    #               count, screen width and height, and client1 and client2 game state variables to
    #               already contain values (or at least be initialized). Lastly, it expects to be ran
    #               on its own thread and that the threads have been locked.
    # Post:         This method sets the variables for client1 and client2 as well as the player
    #               count as global and updates them. It also sends game settings to the client once,
    #               and after this has been done for each client, it repeatedly sends the game state
    #               data to the client.

    # Set player count and client1 and client2 game state variables to be global so they can be modified
    # every time the method is called
    global connectedPlayers, ballX1, ballX2, ballY1, ballY2, lScore1, lScore2, rScore1, rScore2, sync1, sync2

    # Initialize game state data that will be sent to both clients
    sync = 0
    lScore = 0
    rScore = 0
    ballX = 0
    ballY = 0
    playerPaddleY = 0
    playerGameState = {
        "sync": sync,
        "lScore": lScore,
        "rScore": rScore,
        "ballX": ballX,
        "ballY": ballY,
        "paddleY": playerPaddleY,
    }

    # Set game settings that will be sent to the client
    playerGameSettings = {
        "screenWidth": screenWidth,
        "screenHeight": screenHeight,
        "playerPaddle": ""
    }
    if playerNumber == 1:
        playerGameSettings["playerPaddle"] = "left"
    elif playerNumber == 2:
        playerGameSettings["playerPaddle"] = "right"

    # Send the game settings to the client
    clientSocket.send(",".join(map(str, playerGameSettings.values())).encode())

    # Wait for both players to connect
    connectedPlayers += 1
    while connectedPlayers < maxClients:
        pass

    while True:
        try:
            # Receive the data from the client
            data = clientSocket.recv(1024).decode()

            # Split the received data
            receivedData = data.split(",")

            # Store the received data in the game state variables
            sync, lScore, rScore, ballX, ballY, playerPaddleY = map(int, receivedData)

            with lock:
                # Update the game state variables for each player
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

                # Determine which player's game state to send to the clients based on sync values
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

                # Send updated game state to both clients
                if playerNumber == 1:
                    clients[1].send(",".join(map(str, playerGameState.values())).encode())
                elif playerNumber == 2:
                    clients[0].send(",".join(map(str, playerGameState.values())).encode())

        except Exception as e:
            print(f"Error handling client: {e}")
            break
    
    # Close the client socket
    clientSocket.close()


def acceptClients():
    # Authors:      Sean Evans
    # Purpose:      This method listens for client connections. When each client connects, it adds the
    #               client to the clients list and starts a new thread that handles the client and
    #               adds that thread to the threads list.
    # Pre:          This method expects the clients list, threads list, and maximum clients variable
    #               to already be initialized before being called. It also expects a server socket to
    #               already be created with a server IP and port bound to it.
    # Post:         This method sets the clients list and threads list as global variables and updates
    #               them. It also creates a new socket for each client until the maximum number of
    #               clients has been reached.
    
    # Set clients list and threads list to be global so their values can be modified and then used
    # outside of the method
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
