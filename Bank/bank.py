import json
import os
import argparse
import sys

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from flask import Flask, request, jsonify

app = Flask(__name__)
clients = []


class Client:
    # This class represents a client
    # conta: The account number
    # pin: The pin of the account
    # saldo: The balance of the account
    # vCard: The virtual card number
    # vCardSaldo: The balance of the virtual card
    def __init__(self, conta, pin, saldo, vCard=0,vCard_pin = 0, vCardSaldo=0):
        self.conta = conta
        self.pin = pin
        self.saldo = saldo
        self.vCard = vCard
        self.vCard_pin = vCard_pin
        self.vCardSaldo = vCardSaldo

    # This function returns the amount of money on the account
    def getSaldo(self):
        return self.saldo

    # This function deposits money on the account
    def deposit(self, amount):
        self.saldo += amount

    # This function creates a virtual card
    # amount: The amount of money that you want to create a virtual card with
    # return: The virtual card number
    def create_vcard(self, amount, vCard_pin):
        amount=float(amount)
        if self.saldo >= amount:
            self.saldo -= amount
            self.vCardSaldo += amount
            self.vCard = os.urandom(16)
            self.vCard_pin = vCard_pin
            return self.vCard
        else:
            return None

    # This function buys a product
    # amount: The amount of money that you want to spend
    # return: True if the purchase was successful, False otherwise
    def buy_product(self, amount): # Podemos introduzir uma vulnerabilidade aqui
        if self.vCardSaldo >= amount:
            self.vCardSaldo -= amount
            return True
        else:
            return False

# This function generates the server keys
def genServerKeys(filePath): # Generate the server keys
    key = os.urandom(32)  # key de 256 bits
    print(key)
    iv = os.urandom(16)  # IV de 128 bits
    print(iv)
    kIv = key + iv
    with open(filePath, 'wb') as f:
        f.write(kIv)

# This function parses the arguments
def parse_args():
    parser = argparse.ArgumentParser(description='Bank')
    parser.add_argument('-p', metavar='bk-port', type=int, default=3000, help='The port that bank will listen on. Defaults to 3000.')
    parser.add_argument('-s', metavar='auth-file', type=str, default='bank.auth', help='Name of the auth file. Defaults to bank.auth')
    return parser.parse_args()

# This function handles the SIGTERM signal
def signal_handler(sig, frame):
    print("SIGTERM received. Exiting cleanly...")
    sys.exit(0)

# Routes
# User Login
@app.route('/account/<conta>', methods=['GET'])
def getUser(conta):
    for clientAux in clients:
        if clientAux.conta == conta:
            return jsonify({"saldo": clientAux.saldo}), 200
    return "Not found", 404

# User Register
@app.route('/account', methods=['POST'])
def regUser():
    data = request.data
    with open("bank.auth", 'rb') as f:
        key = f.read()
    cipher = Cipher(algorithms.AES(key[:32]), modes.CBC(key[32:]))
    decryptor = cipher.decryptor()
    data = decryptor.update(data).decode("utf8")
    conta = data.split(", ")[0].split(": ")[1]
    pin = data.split(", ")[1].split(": ")[1].encode("latin1")
    saldo = float(data.split(", ")[2].split(": ")[1])
    user = {
        "conta": conta,
        "pin": pin,
        "saldo": saldo
    }
    print(user)
    clients.append(Client(conta, pin, saldo))
    return "Cliente criado com sucesso", 200

# Deposit
@app.route('/account/deposit', methods=['POST'])
def deposit():
    data = request.get_json()
    conta = data.get("conta")
    amount = data.get("amount")

    for clientAux in clients:
        if clientAux.conta == conta:
            clientAux.deposit(amount)
            return "Deposit successful", 200
    return "Not found", 404

# Create virtual card
@app.route('/account/createCard/<conta_id>', methods=['POST'])
def regCard(conta_id):
    data = request.get_data()
    iv = 0
    with open("bank.auth", 'rb') as f:
        key = f.read()
    for clientAux in clients:
        if clientAux.conta == conta_id+".user":
            iv = clientAux.pin
    cipher = Cipher(algorithms.AES(key[:32]), modes.CBC(iv))
    decryptor = cipher.decryptor()
    data = decryptor.update(data).decode("utf8")

    print(data)
    data = eval(data)
    conta = data.get("account")
    amount = data.get("vcc")
    vcc_pin = data.get("vcc_pin").encode("latin1")
    print(data)
    for clientAux in clients:
        if clientAux.conta == conta:
            vCard = clientAux.create_vcard(amount, vcc_pin)
            if vCard:
                return jsonify({"vCard": vCard.hex()}), 200
            else:
                return "Insufficient balance", 400
    return "Not found", 404


# Buy product
@app.route('/buyproduct', methods=['POST'])
def buy_product():
    with open("bank.auth", 'rb') as f:
        key = f.read()
    cipher = Cipher(algorithms.AES(key[:32]), modes.CBC(key[32:]))
    bdecryptor = cipher.decryptor()

    data = request.get_data()
    data = data.decode("latin1")
    account = data.split("|")[0].encode("latin1")
    amount = data.split("|")[1].encode("latin1")
    amount = float(bdecryptor.update(amount).decode("utf8"))
    headers = request.headers

    user = headers.get("User")
    print(user)
    for clientAux in clients:
        if clientAux.conta == user:
            if clientAux.buy_product(amount):
                return "Purchase successful", 200
            else:
                return "Insufficient balance in virtual card", 400
    return "Not found", 404


if __name__ == "__main__":
    args = parse_args()
    genServerKeys(args.s)
    app.run(host="0.0.0.0", port=args.p)

