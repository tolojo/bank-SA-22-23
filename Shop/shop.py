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

def parse_args():
    parser = argparse.ArgumentParser(description='Store')
    parser.add_argument('-p', metavar='store-port', type=int, default=5000, help='The port that the store will listen on. Defaults to 3000.')
    parser.add_argument('-s', metavar='auth-file', type=str, default='bank.auth', help='Name of the auth file. Defaults to bank.auth')
    return parser.parse_args()

@app.route('/buy', methods=['POST'])
def buy_product():
    data = request.data

    with open("bank.auth", 'rb') as f:
        key = f.read()

    h = hmac.new(key[:32], data, hashlib.sha3_256).hexdigest()

    if(h == request.headers.get("Authorization")):

        data=data.decode("latin1")
        cipher = Cipher(algorithms.AES(key[:32]), modes.CBC(key[32:]))
        decryptor = cipher.decryptor()

        amount = data.split("|")[1].encode("latin1")
        decrypted_amount = decryptor.update(amount).decode("utf8")

        print(decrypted_amount) #Apenas faz sentido para a loja saber o que está a ser transacionado
        print("data: "+data)
        requestBank = requests.post(url=f"http://127.0.0.1:3000/buyproduct", headers=request.headers, data=data)

        if(requestBank.status_code==200):
            print("Bank approval")
            return "success", 200
        return "failed transaction", 401

if __name__ == "__main__":
    args = parse_args()

    app.run(host="0.0.0.0", port=args.p)

