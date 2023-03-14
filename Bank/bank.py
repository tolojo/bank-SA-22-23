from cryptography.fernet import Fernet
from flask import Flask, request, jsonify, send_file

app = Flask(__name__)


def genServerKeys():
    key = Fernet.generate_key()
    with open('server_public_key.pem', 'wb') as f:
        f.write(key)

@app.route('/account', methods=['GET'])  # Login do user
def userReg():

@app.route('/account', methods=['POST'])  # Login do user
def userReg():

@app.route('/createCard', methods=['POST'])  # Login do user
def userReg():


@app.route('/buyproduct', methods=['POST'])  # Login do user
def userReg():


if __name__ == "__main__":
    genServerKeys()
    app.run(host="0.0.0.0", port=3000)


