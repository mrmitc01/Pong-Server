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

# Lock threads for synchronization
lock = threading.Lock()

# Variable to track connected players
connectedPlayers = 0

# Function to handle a single client
def handleClient(clientSocket: socket.socket, playerNumber: int) -> None:
    global connectedPlayers, player1PaddleY, player2PaddleY, ballX, ballY, lScore, rScore, sync

    if playerNumber == 1:
        player1PaddleY = 0  # Initialize player 1's paddle position
    else:
        player2PaddleY = 0  # Initialize player 2's paddle position

    # Initialize game state for both players
    player1GameState = {
        "sync": sync,
        "lScore": lScore,
        "rScore": rScore,
        "ballX": ballX,
        "ballY": ballY,
        "paddleY": player1PaddleY,
    }

    player2GameState = {
        "sync": sync,
        "lScore": lScore,
        "rScore": rScore,
        "ballX": ballX,
        "ballY": ballY,
        "paddleY": player2PaddleY,
    }

    if playerNumber == 1:
        clientSocket.send(",".join(map(str, player1GameState.values())).encode())
    else:
        clientSocket.send(",".join(map(str, player2GameState.values())).encode())
    
    connectedPlayers += 1

    # Wait for both players to connect
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

            # Check the length of the received data
            if len(receivedData) == 7:
                if playerNumber == 1:
                    player1PaddleY = int(receivedData[6])
                else:
                    player2PaddleY = int(receivedData[6])

            # Update the game state based on the received data
            if playerNumber == 1:
                player1GameState = {
                    "sync": int(receivedData[0]),
                    "lScore": int(receivedData[1]),
                    "rScore": int(receivedData[2]),
                    "ballX": int(receivedData[3]),
                    "ballY": int(receivedData[4]),
                    "paddleY": int(receivedData[5]),
                }
            else:
                player2GameState = {
                    "sync": int(receivedData[0]),
                    "lScore": int(receivedData[1]),
                    "rScore": int(receivedData[2]),
                    "ballX": int(receivedData[3]),
                    "ballY": int(receivedData[4]),
                    "paddleY": int(receivedData[5]),
                }

            # Relay updated game state to the other client
            with lock:
                if playerNumber == 1:
                    clientSocket.send(",".join(map(str, player2GameState.values())).encode())
                else:
                    clientSocket.send(",".join(map(str, player1GameState.values())).encode())

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
