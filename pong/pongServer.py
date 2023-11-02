# =================================================================================================
# Contributing Authors:	    Sean Evans
# Email Addresses:          siev223@uky.edu
# Date:                     11/2/23
# Purpose:                  To handle data and sync data between two clients. The server is
#                           responsible for maintaining connection between both clients.
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
clients = []  # type: List[socket.socket]
threads = []  # type: List[threading.Thread]

# Game state variables
player1PaddleY = 0  # Initialize paddle positions
player2PaddleY = 0
ballX = 0
ballY = 0
score1 = 0
score2 = 0

lock = threading.Lock()

# Function to handle a single client
def handleClient(clientSocket: socket.socket, playerNumber: int) -> None:
    global player1PaddleY, player2PaddleY, ballX, ballY, score1, score2

    clientSocket.send(f"{playerNumber},{player1PaddleY},{player2PaddleY},{ballX},{ballY},{score1},{score2}".encode())

    while True:
        try:
            # Receive game updates from the client
            data = clientSocket.recv(1024).decode()
            if not data:
                break

            # Split the received data
            receivedData = data.split(",")
            if len(receivedData) == 5:
                playerPaddleY = int(receivedData[4])

                # Update game state variables
                if playerNumber == 1:
                    player1PaddleY = playerPaddleY
                else:
                    player2PaddleY = playerPaddleY

                # Relay game information to the other client
                otherPlayerNumber = 1 if playerNumber == 2 else 2
                with lock:
                    clientSocket.send(f"{otherPlayerNumber},{player1PaddleY},{player2PaddleY},{ballX},{ballY},{score1},{score2}".encode())

        except Exception as e:
            print(f"Error handling client: {e}")
            break

    clientSocket.close()

# Function to listen for client connections
def acceptClients():
    global clients, threads

    while True:
        clientSocket, clientAddr = serverSocket.accept()
        if len(clients) < maxClients:
            playerNumber = len(clients) + 1
            print(f"Client {playerNumber} connected from {clientAddr}")
            clients.append(clientSocket)
            clientThread = threading.Thread(target=handleClient, args=(clientSocket, playerNumber))
            threads.append(clientThread)
            clientThread.start()
        else:
            print("Maximum number of clients reached. Connection refused.")

# Start the server
print(f"Server listening on {serverIp}:{serverPort}")
acceptClients()

# Wait for all client threads to finish
for thread in threads:
    thread.join()

# Close the server socket
serverSocket.close()
