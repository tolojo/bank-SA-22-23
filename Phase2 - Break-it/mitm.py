import argparse
from socket import socket


class Flask:
    pass


app = Flask(__name__)
clients = []

seqNumb = 0
vccSeqNumb = 0

# This function parses the arguments
def parse_args():
    parser = argparse.ArgumentParser(description='mitm')
    parser.add_argument('-p', metavar='mitm-port', type=int, default=4000, help='The port that mitm will listen on. Defaults to 4000.')
    parser.add_argument('-s', metavar='server-ip-address', type=str, default='bank.auth', help='The ip that the store or the bank will listen on')
    parser.add_argument('-q', metavar='server-port', type=int, help='The port that the bank or store are running on')
    return parser.parse_args()




if __name__ == "__main__":
    args = parse_args()
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('127.0.0.1', args.p))
    server_socket.listen()
    client_socket, _ = server_socket.accept() #MBEC socket
    cli_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Bank socket
    cli_sock.connect((args.s, args.q))
    # try:
    while True:
        try:
            client_socket, _ = server_socket.accept()  # MBEC socket
            data = client_socket.recv(1024)
            print("i have data")
            print(data)
            val = input("\n What do you want to do?"
                  "\n (D)rop"
                  "\n (F)orward"
                  "\n (M)odify")
            if val == "D":
                continue
            if val == "F":
                continue
            if val == "M":
                continue
        except:
            print("boooo")


    app.run(host="0.0.0.0", port=args.p)
