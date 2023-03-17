import json
import os
import argparse
import sys

from flask import Flask, request

app = Flask(__name__)
clients = []


class Client:
    def __init__(self, idCartao, saldo, vCard=0, vCardSaldo=0):
        self.idCartao = idCartao
        self.saldo = saldo
        self.vCard = vCard
        self.vCardSaldo = vCardSaldo

    def getSaldo(self):
        return self.saldo


def genServerKeys(filePath):
    key = os.urandom(32) #key de 256 bits
    print(key)
    iv = os.urandom(16)  #IV de 128 bits
    print(iv)
    kIv = key + iv
    with open(filePath, 'wb') as f:
        f.write(kIv)


def parse_args():
    parser = argparse.ArgumentParser(description='Bank')
    parser.add_argument('-p', metavar='bk-port', type=int, default=3000, help='The port that bank will listen on. Defaults to 3000.')
    parser.add_argument('-s', metavar='auth-file', type=str, default='bank.auth', help='Name of the auth file. Defaults to bank.auth')
    return parser.parse_args()

def signal_handler(sig, frame):
    print("SIGTERM received. Exiting cleanly...")
    sys.exit(0)



@app.route('/account/<idcartao>', methods=['GET'])  # Login do user
def getUser(idcartao):
    for clientAux in clients:
        if clientAux.idCartao == idcartao:
            return "saldo:"+clientAux.saldo, 200
    return "Not found", 404


@app.route('/account', methods=['POST'])  # Login do user
def regUser():
    data = json.dumps(request.get_json())
    data = json.loads(data)
    print(data)
    client = Client(idCartao=data['idcartao'], saldo=data['saldo'])
    print(client.idCartao)
    clients.append(client)
    print(clients)
    return "Cliente criado com sucesso", 200


@app.route('/createCard', methods=['POST'])  # Login do user
def regCard():
    data = json.dumps(request.get_json())
    data = json.loads(data)
    print(data)
    return


@app.route('/buyproduct', methods=['POST'])  # Login do user
def buyProd():
    return


if __name__ == "__main__":
    args = parse_args()
    genServerKeys(args.s)
    app.run(host="0.0.0.0", port=args.p)


