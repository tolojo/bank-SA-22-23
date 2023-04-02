import json
import os
import argparse
import sys

import requests
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from flask import Flask, request
app = Flask(__name__)


def parse_args():
    parser = argparse.ArgumentParser(description='Store')
    parser.add_argument('-p', metavar='store-port', type=int, default=3000, help='The port that the store will listen on. Defaults to 3000.')
    parser.add_argument('-s', metavar='auth-file', type=str, default='bank.auth', help='Name of the auth file. Defaults to bank.auth')
    return parser.parse_args()

@app.route('/buy', methods=['POST'])
def buy_product(ip, port):
    data = request.data

    with open("bank.auth", 'rb') as f:
        key = f.read()
    cipher = Cipher(algorithms.AES(key[:32]), modes.CBC(key[32:]))
    decryptor = cipher.decryptor()
    decrypted_data = decryptor.update(data).decode("utf8")
    request_dict = json.loads(decrypted_data)

    response = requests.post(url=f"http://{ip}:{port}/account/buyproduct", data=request_dict)

    response_dict = response.json()
    response_json = json.dumps(response_dict).encode('utf-8')
    encryptor = cipher.encryptor()
    encrypted_response = encryptor.update(response_json) + encryptor.finalize()

    return encrypted_response

if __name__ == "__main__":
    args = parse_args()

    app.run(host="0.0.0.0", port=args.p)

