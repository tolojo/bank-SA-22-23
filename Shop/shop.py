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
        print("hashes match")
        cipher = Cipher(algorithms.AES(key[:32]), modes.CBC(key[32:]))
        decryptor = cipher.decryptor()
        amount = data.split("|")[1].encode("latin1")
        decrypted_data = decryptor.update(amount).decode("utf8")
        print(decrypted_data) #Apenas faz sentido para a loja saber o que está a ser transacionado

        requestBank = requests.post(url=f"http://127.0.0.1:3000/account/buyproduct", data=)
        """
        response_dict = response.json()
        response_json = json.dumps(response_dict).encode('utf-8')
        encryptor = cipher.encryptor()
        encrypted_response = encryptor.update(response_json) + encryptor.finalize()
        return encrypted_response
        """
        return


if __name__ == "__main__":
    args = parse_args()

    app.run(host="0.0.0.0", port=args.p)

