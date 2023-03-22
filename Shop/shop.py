import json
import os
import argparse
import sys

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from flask import Flask, request
app = Flask(__name__)


def parse_args():
    parser = argparse.ArgumentParser(description='Bank')
    parser.add_argument('-p', metavar='store-port', type=int, default=3000, help='The port that the store will listen on. Defaults to 3000.')
    parser.add_argument('-s', metavar='auth-file', type=str, default='bank.auth', help='Name of the auth file. Defaults to bank.auth')
    return parser.parse_args()


@app.route('/buy', methods=['POST'])  # Login do user
def buyProduct():
    data = request.data




    return "Not found", 404


if __name__ == "__main__":
    args = parse_args()

    app.run(host="0.0.0.0", port=args.p)

