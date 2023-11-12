# =================================================================================================
# Contributing Authors:	    Matt Mitchell, Cameron Egbert
# Email Addresses:          matt.mitchell@uky.edu, cmeg225@uky.edu
# Date:                     11-4-23
# Purpose:                  To communicate with the server to relay and receive information about
#                           the current game state. The client is responsible for sending the
#                           location of the user’s Pong paddle to the server. It will receive from
#                           the server the location of the other player’s paddle, the location of
#                           the ball, and the current score.
# =================================================================================================

import pygame
import tkinter as tk
import sys
import socket

from time import sleep
from assets.code.helperCode import *

# This is the main game loop. For the most part, you will not need to modify this. The sections
# where you should add to the code are marked. Feel free to change any part of this project to
# suit your needs.
def playGame(screenWidth:int, screenHeight:int, playerPaddle:str, client:socket.socket) -> None:
    
    # Pygame inits
    pygame.mixer.pre_init(44100, -16, 2, 2048)
    pygame.init()

    # Constants
    WHITE = (255,255,255)
    clock = pygame.time.Clock()
    scoreFont = pygame.font.Font("./assets/fonts/pong-score.ttf", 32)
    winFont = pygame.font.Font("./assets/fonts/visitor.ttf", 48)
    pointSound = pygame.mixer.Sound("./assets/sounds/point.wav")
    bounceSound = pygame.mixer.Sound("./assets/sounds/bounce.wav")

    # Display objects
    screen = pygame.display.set_mode((screenWidth, screenHeight))
    winMessage = pygame.Rect(0,0,0,0)
    topWall = pygame.Rect(-10,0,screenWidth+20, 10)
    bottomWall = pygame.Rect(-10, screenHeight-10, screenWidth+20, 10)
    centerLine = []
    for i in range(0, screenHeight, 10):
        centerLine.append(pygame.Rect((screenWidth/2)-5,i,5,5))

    # Paddle properties and init
    paddleHeight = 50
    paddleWidth = 10
    paddleStartPosY = (screenHeight/2)-(paddleHeight/2)
    leftPaddle = Paddle(pygame.Rect(10,paddleStartPosY, paddleWidth, paddleHeight))
    rightPaddle = Paddle(pygame.Rect(screenWidth-20, paddleStartPosY, paddleWidth, paddleHeight))

    ball = Ball(pygame.Rect(screenWidth/2, screenHeight/2, 5, 5), -5, 0)
    #ball = Ball(pygame.Rect(50, 50, 5, 5), -5, 0)

    if playerPaddle == "left":
        opponentPaddleObj = rightPaddle
        playerPaddleObj = leftPaddle
    else:
        opponentPaddleObj = leftPaddle
        playerPaddleObj = rightPaddle

    lScore = 0
    rScore = 0

    sync = 0

    while True:
        # Wiping the screen
        screen.fill((0,0,0))

        # Getting keypress events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    playerPaddleObj.moving = "down"

                elif event.key == pygame.K_UP:
                    playerPaddleObj.moving = "up"

            elif event.type == pygame.KEYUP:
                playerPaddleObj.moving = ""
                
        # Update the player paddle and opponent paddle's location on the screen
        for paddle in [playerPaddleObj, opponentPaddleObj]:
            if paddle.moving == "down":
                if paddle.rect.bottomleft[1] < screenHeight-10:
                    paddle.rect.y += paddle.speed
            elif paddle.moving == "up":
                if paddle.rect.topleft[1] > 10:
                    paddle.rect.y -= paddle.speed

        # If the game is over, display the win message
        if lScore > 4 or rScore > 4:
            winText = "Player 1 Wins! " if lScore > 4 else "Player 2 Wins! "
            textSurface = winFont.render(winText, False, WHITE, (0,0,0))
            textRect = textSurface.get_rect()
            textRect.center = ((screenWidth/2), screenHeight/2)
            winMessage = screen.blit(textSurface, textRect)
        else:

            # ==== Ball Logic =====================================================================
            ball.updatePos()

            # If the ball makes it past the edge of the screen, update score, etc.
            if ball.rect.x > screenWidth:
                lScore += 1
                pointSound.play()
                ball.reset(nowGoing="left")
            elif ball.rect.x < 0:
                rScore += 1
                pointSound.play()
                ball.reset(nowGoing="right")
                
            # If the ball hits a paddle
            if ball.rect.colliderect(playerPaddleObj.rect):
                bounceSound.play()
                ball.hitPaddle(playerPaddleObj.rect.center[1])
            elif ball.rect.colliderect(opponentPaddleObj.rect):
                bounceSound.play()
                ball.hitPaddle(opponentPaddleObj.rect.center[1])
                
            # If the ball hits a wall
            if ball.rect.colliderect(topWall) or ball.rect.colliderect(bottomWall):
                bounceSound.play()
                ball.hitWall()
            
            pygame.draw.rect(screen, WHITE, ball)
            # ==== End Ball Logic =================================================================

        # Drawing the dotted line in the center
        for i in centerLine:
            pygame.draw.rect(screen, WHITE, i)
        
        # Drawing the player's new location
        for paddle in [playerPaddleObj, opponentPaddleObj]:
            pygame.draw.rect(screen, WHITE, paddle)

        pygame.draw.rect(screen, WHITE, topWall)
        pygame.draw.rect(screen, WHITE, bottomWall)
        scoreRect = updateScore(lScore, rScore, screen, WHITE, scoreFont)
        pygame.display.update([topWall, bottomWall, ball, leftPaddle, rightPaddle, scoreRect, winMessage])
        pygame.display.flip()
        clock.tick(60)
        
        # This number should be synchronized between you and your opponent. If your number is larger
        # then you are ahead of them in time. If theirs is larger then they are ahead of you, and you need to
        # catch up (use their information).
        sync += 1

        # =========================================================================================
        # Your code here to send an update to the server on your paddle's information,
        # where the ball is, and the current score. Feel free to change when the score is updated
        # to suit your needs/requirements.
        #startInfoToSend = f"{sync},{lScore},{rScore},{ball.rect.x},{ball.rect.y},{playerPaddleObj.rect.y},{opponentPaddleObj.rect.y}"
        startInfoToSend = f"{sync},{lScore},{rScore},{ball.rect.x},{ball.rect.y},{playerPaddleObj.rect.y}"
        client.send(startInfoToSend.encode())
        # =========================================================================================
        
        # =========================================================================================
        # Send your server update here at the end of the game loop to sync your game with your
        # opponent's game
        
        # Get information from server
        respDecode = client.recv(1024).decode()

        '''
        # Wait
        respDecode = ""
        while respDecode == "":
            respDecode = client.recv(1024).decode()
        '''
        # Parse information received from server
        respList = respDecode.split(",")
        sync = int(respList[0])
        lScore = int(respList[1])
        rScore = int(respList[2])
        ball.rect.x = int(respList[3])
        ball.rect.y = int(respList[4])
        opponentPaddleObj.rect.y = int(respList[5])
            
        
        #playerPaddleObj.rect.y = int(respList[5])
        #opponentPaddleObj.rect.y = int(respList[6])

        '''
        # Parse information received from server
        respList = respDecode.split(",")
        opponentSync = int(respList[0])
        opponentLScore = int(respList[1])
        opponentRScore = int(respList[2])
        opponentBallX = int(respList[3])
        opponentBallY = int(respList[4])
        opponentPaddleY = int(respList[5])

        # Set your information to match opponent information if opponent number is larger than yours
        if opponentSync > sync:
            sync = opponentSync
            lScore = opponentLScore
            rScore = opponentRScore
            if lScore <= 4 or rScore <= 4:
                ball.rect.x = opponentBallX
                ball.rect.y = opponentBallY
            
        opponentPaddleObj.rect.y = opponentPaddleY

        # Send your information to server
        endInfoToSend = f"{sync},{lScore},{rScore},{ball.rect.x},{ball.rect.y},{playerPaddleObj.rect.y}"
        client.send(endInfoToSend.encode())
        '''
        # =========================================================================================




# This is where you will connect to the server to get the information required to call the game loop.
# This will mainly be the screen width, height and player paddle (either "left" or "right").
# If you want to hard code the screen's dimensions into the code, that's fine, but you will need to know
# which client is which
def joinServer(ip:str, port:str, errorLabel:tk.Label, app:tk.Tk) -> None:
    # Purpose:      This method is fired when the join button is clicked
    # Arguments:
    # ip            A string holding the IP address of the server
    # port          A string holding the port the server is using
    # errorLabel    A tk label widget, modify it's text to display messages to the user (example below)
    # app           The tk window object, needed to kill the window
    
    # Create a socket and connect to the server
    # You don't have to use SOCK_STREAM, use what you think is best
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Empty the error label and wait 0.5 seconds to provide the user with feedback upon pressing the Join button
    errorLabel.config(text="")
    errorLabel.update()
    sleep(0.5)

    # Get the required information from your server (screen width, height & player paddle, "left or "right)
    try:

        # Connect to server
        client.connect((ip, int(port)))

        # Get information from server
        respDecode = client.recv(1024).decode()

        # Parse information received from server
        respList = respDecode.split(",")
        screenWidth = int(respList[0])
        screenHeight = int(respList[1])
        playerPaddle = respList[2]

        # If you have messages you'd like to show the user use the errorLabel widget like so
        errorLabel.config(text=f"Your input: IP- {ip}, Port- {port}")
        # You may or may not need to call this, depending on how many times you update the label
        errorLabel.update()

        # Close this window and start the game with the information passed to you from the server
        app.withdraw()     # Hides the window (we'll kill it later)
        playGame(screenWidth, screenHeight, playerPaddle, client)  # User will be either left or right paddle
        app.quit()         # Kills the window
    except ConnectionRefusedError:
        # Update error label when there is a connection error
        errorLabel.config(text="Unable to connect to server")
        errorLabel.update()
    except ValueError as invalidInput:
        # Update error label when there is invalid user input
        errorLabel.config(text=invalidInput)
        errorLabel.update()
    



# This displays the opening screen, you don't need to edit this (but may if you like)
def startScreen():
    app = tk.Tk()
    app.title("Server Info")

    image = tk.PhotoImage(file="./assets/images/logo.png")

    titleLabel = tk.Label(image=image)
    titleLabel.grid(column=0, row=0, columnspan=2)

    ipLabel = tk.Label(text="Server IP:")
    ipLabel.grid(column=0, row=1, sticky="W", padx=8)

    ipEntry = tk.Entry(app)
    ipEntry.grid(column=1, row=1)

    portLabel = tk.Label(text="Server Port:")
    portLabel.grid(column=0, row=2, sticky="W", padx=8)

    portEntry = tk.Entry(app)
    portEntry.grid(column=1, row=2)

    errorLabel = tk.Label(text="")
    errorLabel.grid(column=0, row=4, columnspan=2)

    joinButton = tk.Button(text="Join", command=lambda: joinServer(ipEntry.get(), portEntry.get(), errorLabel, app))
    joinButton.grid(column=0, row=3, columnspan=2)

    app.mainloop()

if __name__ == "__main__":
    # Comment out startScreen and uncomment playGame below to play the game without a server to see how it
    # should work
    startScreen()
    
    # The startScreen() function should call playGame with the arguments given to it by the server, this is
    # here for demo purposes only
    #playGame(640, 480,"left",socket.socket(socket.AF_INET, socket.SOCK_STREAM))