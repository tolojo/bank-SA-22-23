import argparse
from socket import *
import time


clients = []

seqNumb = 0
vccSeqNumb = 0
# ordem para criar conta de user = f rc f rb sc
# This function parses the arguments
def parse_args():
    parser = argparse.ArgumentParser(description='mitm')
    parser.add_argument('-p', metavar='mitm-port', type=int, default = 3000, help='The port that mitm will listen on. Defaults to 4000.')
    parser.add_argument('-s', metavar='server-ip-address', type=str, default='127.0.0.1', help='The ip that the store or the bank will listen on')
    parser.add_argument('-q', metavar='server-port', type=int, default = 4000, help='The port that the bank or store are running on')
    return parser.parse_args()

def handle_mitm(client_socket, args):
    db = 0 #data from bank
    data = client_socket.recv(1024)
    print("Received data from client:")
    print(data)
    bank_sock = socket(AF_INET, SOCK_STREAM)
    bank_sock.connect((args.s, args.q))
    while True:
        val = input("\nWhat do you want to do?"
                    "\n(D)rop"
                    "\n(F)orward"
                    "\n(M)odify"
                    "\n(Rc)eceive Client"
                    "\n(Rb)eceive Bank"
                    "\n(Sc)end Client"
                    "\n(Sb)end Bank"
                    "\n")
        if val.lower() == "d":
         print("dropped")

        if val.lower() == "rc":
            data = client_socket.recv(1024)
            print("Received data from client:")
            print(data)
        if val.lower() == "rb":
            data = bank_sock.recv(1024)
            print("Received data from bank:")
            print(data)

        if val == "f":

            bank_sock.send(data)


        if val == "sc":
            client_socket.send(data)

        if val == "sb":

            bank_sock.send(data)


        if val.lower() == "m":
            val = input("\nEnter the new message: ")
            modified_data = val.encode()
            delay = float(input("\nEnter the delay (in seconds) before sending the modified data: "))
            time.sleep(delay)
        
            with socket(AF_INET, SOCK_STREAM) as cli_sock:
                cli_sock.connect((args.s, args.q))
                cli_sock.send(modified_data)
                data = cli_sock.recv(1024)
                print("Received data from bank after modification:")
                print(data)
                client_socket.send(data)
        val = ""





if __name__ == "__main__":
    args = parse_args()
    print("Starting man-in-the-middle with the following configuration:")
    print(f"MITM Port: {args.p}")
    print(f"Server IP: {args.s}")
    print(f"Server Port: {args.q}")
    
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.bind(('127.0.0.1', args.p))
    server_socket.listen()

    print("Man-in-the-middle is listening...")

    while True:
        try:
            client_socket, _ = server_socket.accept()
            print("Accepted connection from client")
            handle_mitm(client_socket, args)
        except Exception as e:
            print("Error occurred:", e)

