import hashlib
import json
import os
import argparse
import sys
import hmac
import re
import signal

import flask
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.asymmetric import rsa
from flask import Flask, request, jsonify

app = Flask(__name__)
clients = []

filename_regex = re.compile(r'^[_\-\.0-9a-z]{1,127}$')
account_name_regex = re.compile(r'^[_\-\.0-9a-z]{1,122}$')


class Client:
    # This class represents a client
    # conta: The account number
    # pin: The pin of the account
    # saldo: The balance of the account
    # vCard: The virtual card number
    # vCardSaldo: The balance of the virtual card
    def __init__(self, conta, pin, saldo, vCard=0, vCard_pin=0, vCardSaldo=0):
        self.conta = conta
        self.pin = pin
        self.saldo = saldo
        self.vCard = vCard
        self.vCard_pin = vCard_pin
        self.vCardSaldo = vCardSaldo

    def get_vcard_pin(self):
        return self.vCard_pin

    # This function returns the amount of money on the account
    def getSaldo(self):
        return self.saldo

    # This function deposits money on the account
    def deposit(self, amount):
        self.saldo += float(amount)

    # This function creates a virtual card
    # amount: The amount of money that you want to create a virtual card with
    # return: The virtual card number
    def create_vcard(self, amount, vCard_pin):
        amount = float(amount)
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
    def buy_product(self, amount):
        if self.vCardSaldo >= amount:
            self.vCardSaldo -= amount
            self.saldo += self.vCardSaldo
            self.vCardSaldo = 0
            self.vCard = 0
            self.vCard_pin = 0

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

    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    public_key = private_key.public_key()

    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    with open("bank_ptk.pem", 'wb') as f:
        f.write(pem)

    pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    with open("bank_pbk.pem", 'wb') as f:
        f.write(pem)


# This function parses the arguments
def parse_args():
    parser = argparse.ArgumentParser(description='Bank')
    parser.add_argument('-p', metavar='bk-port', type=int, default=3000, help='The port that bank will listen on. Defaults to 3000.')
    parser.add_argument('-s', metavar='auth-file', type=str, default='bank.auth', help='Name of the auth file. Defaults to bank.auth')
    return parser.parse_args()

# This function validates the input arguments
def validate_args(args):
    if not re.match(r'^[1-9]\d*$', args.p):
        return False, 135
    if not (1024 <= args.p <= 65535):
        return False, 135

    if not re.match(filename_regex, args.s):
        return False, 130

    return True, None

# This function handles the SIGTERM signal
def signal_handler(sig, frame):
    sys.exit(0)

# Routes
# User Login
@app.route('/account/<conta>', methods=['GET'])
def getUser(conta):
    if not re.match(account_name_regex, conta):
         sys.exit(125)
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
    if not re.match(account_name_regex, conta):
        sys.exit(125)
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
    data = request.get_data()

    with open("bank.auth", 'rb') as f:
        key = f.read()

    h = hmac.new(key[:32], data, hashlib.sha3_256).hexdigest()

    if (h == request.headers.get("Authorization")):
        user = request.headers.get("User")
        for clientAux in clients:
            if clientAux.conta == user:
                iv = clientAux.pin
        data = data.decode("latin1")
        cipher = Cipher(algorithms.AES(key[:32]), modes.CBC(key[32:]))
        decryptor = cipher.decryptor()

        conta = data.split("|")[0].encode("latin1")
        amount = data.split("|")[1].encode("latin1")
        decrypted_amount = decryptor.update(amount).decode("utf8")

        if not re.match(r'^\d+\.\d{2}$', decrypted_amount):
            sys.exit(125)

        cipher = Cipher(algorithms.AES(key[:32]), modes.CBC(iv))
        decryptor = cipher.decryptor()
        decrypted_conta = decryptor.update(conta).decode("utf8")
        for clientAux in clients:
            if clientAux.conta == decrypted_conta.strip(" "):
                clientAux.deposit(decrypted_amount)
                return "Deposit successful", 200
        return "Not found", 404

# Create virtual card
@app.route('/account/createCard/<conta_id>', methods=['POST'])
def regCard(conta_id):
    if not re.match(account_name_regex, conta_id):
        sys.exit(125)
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
    
    if not re.match(r'^\d+\.\d{2}$', amount):
         sys.exit(125)

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
    print(amount)
    headers = request.headers
    user = headers.get("User")

    for clientAux in clients:
        if clientAux.conta == user:
            iv = clientAux.get_vcard_pin()
            cipher = Cipher(algorithms.AES(key[:32]), modes.CBC(iv))
            adecryptor = cipher.decryptor()
            account = adecryptor.update(account).decode("utf8")
            account = account.split("_")[0].split(": ")[1]+".user"
            print(account)
            if account == user:
                if clientAux.buy_product(amount):
                    return "Purchase successful", 200
            else:
                return "Insufficient balance in virtual card", 400
    return "Not found", 404

@app.route('/serverPK', methods=['GET'])
def get_server_pbk():
    with open("bank.auth", 'rb') as f:
        key = f.read()

    with open("bank_pbk.pem", 'rb') as f:
        pk = f.read()

    cipher = Cipher(algorithms.AES(key[:32]), modes.CBC(key[32:]))
    encryptor = cipher.encryptor()
    pk = encryptor.update(pk)
    h = hmac.new(key[:32], pk, hashlib.sha3_256).hexdigest()
    resp = flask.Response()
    resp.data = pk
    resp.headers["Authorization"] = h
    return resp

if __name__ == "__main__":
    args = parse_args()
    valid, error_code = validate_args(args)
    if not valid:
        sys.exit(error_code)

    if len(' '.join(sys.argv[1:])).replace(' ', '') > 4096:
        sys.exit(130)

    signal.signal(signal.SIGTERM, signal_handler)
    genServerKeys(args.s)
    app.run(host="0.0.0.0", port=args.p)

