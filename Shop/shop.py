import hashlib
import hmac
import json
import os
import argparse
import sys

import requests
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from flask import Flask, request

app = Flask(__name__)
HMACs = {}
sys.stderr = open("/dev/null", "w")

def valid_port(port):
    return 1 <= port <= 65535


def check_auth_file(value):
    if not os.path.isfile(value):
        raise argparse.ArgumentTypeError(f"File '{value}' does not exist.")
    return value


def check_port(value):
    value = int(value)
    if not valid_port(value):
        raise argparse.ArgumentTypeError("Invalid port number.")
    return value


def parse_args():
    parser = argparse.ArgumentParser(description='Store')
    parser.add_argument('-p', metavar='store-port', type=check_port, default=5000,
                        help='The port that the store will listen on. Defaults to 3000.')
    parser.add_argument('-s', metavar='auth-file', type=check_auth_file, default='bank.auth',
                        help='Name of the auth file. Defaults to bank.auth')
    return parser.parse_args()


@app.route('/buy', methods=['POST'])
def buy_product():
    data = request.data

    with open(request.args.s, 'rb') as f:
        key = f.read()

    h = hmac.new(key[:32], data, hashlib.sha3_256).hexdigest()

    if (h == request.headers.get("Authorization")):
        # falta fazer verificação do hmac no buy product do bank
        data = data.decode("latin1")
        cipher = Cipher(algorithms.AES(key[:32]), modes.CBC(key[32:]))
        decryptor = cipher.decryptor()

        amount = data.split("|")[1].encode("latin1")
        decrypted_amount = decryptor.update(amount).decode("utf8")

        try:
            amount_in_cents = int(decrypted_amount)
        except ValueError:
            print("Invalid amount")
            sys.exit(135)

        print(decrypted_amount)  # Apenas faz sentido para a loja saber o que está a ser transacionado
        print("data: " + data)

        try:
            requestBank = requests.post(url=f"http://127.0.0.1:3000/buyproduct", headers=request.headers, data=data,
                                         timeout=10)
            requestBank.raise_for_status()
        except requests.exceptions.Timeout:
            sys.exit(63)
        except requests.exceptions.RequestException:
            sys.exit(63)

        if (requestBank.status_code == 200):
            print("Bank approval")
            return "success", 200
        else:
            print("Failed transaction")
            sys.exit(135)
            return "failed transaction", 401
    else:
        print("Invalid authorization")
        sys.exit(130)
        return "Unauthorized", 401


if __name__ == "__main__":
    args = parse_args()

    app.run(host="0.0.0.0", port=args.p)
