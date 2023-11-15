Contact Info
============
Group Members & Email Addresses:
    Matt Mitchell, matt.mitchell@uky.edu
    Cameron Egbert, cmeg225@uky.edu
    Sean Evans, siev223@uky.edu

Versioning
==========
Github Link: https://github.com/mrmitc01/Pong-Server

General Info
============
To run Pong-Server with one computer:
1. Navigate to the directory named `pong` in this project via command-line interface and enter `python pongServer.py`.
2. You will be asked if the server and clients will be ran on a single computer. Enter `y`.
3. In a separate command-line window, navigate to the `pong` directory and enter `python pongClient.py`.
4. A pong client window will open prompting you for a Server IP and Server Port. Enter `127.0.0.1` in the Server IP
   field and `12321` in the Server Port field.
5. Click the `Join` button.
6. In a third command-line window, navigate to the `pong` directory and enter `python pongClient.py`.
7. A pong client window will open prompting you for a Server IP and Server Port. Enter `127.0.0.1` in the Server IP
   field and `12321` in the Server Port field.
8. Click the `Join` button.

To run Pong-Server with two computers:
1. Make sure both computers have this project downloaded.
2. Choose a computer that you want to run the server on. On that computer, navigate to the directory named `pong` in this
   project via command-line interface and enter `python pongServer.py`.
3. You will be asked if the server and clients will be ran on a single computer. Enter `n`.
4. You will be prompted for an IP address. Enter that computer's IP address.
5. Follow either the steps below (a) or the steps below (b):
   (a)
       I. On a second computer, navigate to the directory named `pong` in this project via command-line interface and enter
          `python pongClient.py`.
       II. Still on the second computer, in a separate command-line window, navigate to the `pong` directory and enter
          `python pongClient.py`.
   (b)
       I. In a separate command-line window, navigate to the `pong` directory and enter `python pongClient.py`.
       II. On a second computer, navigate to the directory named `pong` in this project via command-line interface and enter
          `python pongClient.py`.
6. Two pong client windows will now be open (one on each computer). On each pong client window, enter the IP address of the
   computer running the server in the Server IP field. Enter `12321` in the Server Port field on each pong client window.
7. On each pong client window, click the `Join` button.

To run Pong-Server with three computers:
1. Make sure all three computers have this project downloaded.
2. Choose a computer that you want to run the server on. On that computer, navigate to the directory named `pong` in this
   project via command-line interface and enter `python pongServer.py`.
3. You will be asked if the server and clients will be ran on a single computer. Enter `n`.
4. You will be prompted for an IP address. Enter that computer's IP address.
5. On a second computer, navigate to the directory named `pong` in this project via command-line interface and enter
   `python pongClient.py`.
6. On a third computer, navigate to the directory named `pong` in this project via command-line interface and enter
   `python pongClient.py`.
7. Two pong client windows will now be open (one on each computer). On each pong client window, enter the IP address of the
   computer running the server in the Server IP field. Enter `12321` in the Server Port field on each pong client window.
8. On each pong client window, click the `Join` button.

Install Instructions
====================
Run the following line to install the required libraries for this project:
`pip3 install -r requirements.txt`

Known Bugs
==========
None
