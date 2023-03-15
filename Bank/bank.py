import os, json

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from flask import Flask, request, jsonify, send_file

app = Flask(__name__)
clients = []


class Client:

    def __init__(self, idCartao, saldo, vCard = 0, vCardSaldo = 0):
        self.idCartao = idCartao
        self.saldo = saldo
        self.vCard = vCard
        self.vCardSaldo = vCardSaldo

    def getSaldo(myobject):
        return myobject.saldo


def genServerKeys():
    key = os.urandom(32) #key de 256 bits
    print(key)
    iv = os.urandom(16)  #IV de 128 bits
    print(iv)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    kIv = key + iv
    with open('bank.auth', 'wb') as f:
        f.write(kIv)


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
    return


@app.route('/buyproduct', methods=['POST'])  # Login do user
def buyProd():
    return


if __name__ == "__main__":
    genServerKeys()
    app.run(host="0.0.0.0", port=3000)


