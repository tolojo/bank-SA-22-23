import json
import os
import argparse
import sys

import requests
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.ciphers.algorithms import AES
global seqNumber
seqNumber = 0


def parse_args():
    parser = argparse.ArgumentParser(description='Client')
    parser.add_argument('-i', metavar='bk-ip', type=str, default='127.0.0.1',  help='The IP that the client will search the bank. default is localhost')
    parser.add_argument('-p', metavar='bk-port', type=int, default=3000, help='The port that bank will listen on. Defaults to 3000.')
    parser.add_argument('-s', metavar='auth-file', type=str, default='bank.auth', help='Name of the auth file. Defaults to bank.auth')
    parser.add_argument('-u', metavar='user-file', type=str, default = None, help='The customer user file. The default value is the account name prepended to .user')
    parser.add_argument('-a', metavar='account', type=int, help='The account that you want to do operations.')
    parser.add_argument('-n', metavar='balance', type=float, help='The balance of the account that you want to create')
    parser.add_argument('-d', metavar='deposit', type=int, help='The amount you want to deposit on the account')
    parser.add_argument('-c', metavar='vcc', type=float, help='The amount of money that you want to create a virtual card with')
    parser.add_argument('-g', metavar='balance', type=int, help='Get the balance of a certain account')
    return parser.parse_args()

def signal_handler(sig, frame):
    print("SIGTERM received. Exiting cleanly...")
    sys.exit(0)


def get_account_balance(ip, port, account):
    response = requests.get(url=f"http://{ip}:{port}/account/{account}")
    if response.status_code == 200:
        print(response.text)
    else:
        print("Error getting account balance")


def deposit(ip, port, account, deposit_amount):
    payload = {'account': account, 'deposit': deposit_amount}
    response = requests.post(url=f"http://{ip}:{port}/account/deposit", json=payload)
    if response.status_code == 200:
        print(response.text)
    else:
        print("Error depositing money")


def create_vcc(ip, port, account, vcc_amount):
    global seqNumber
    vcc_pin = os.urandom(16)  # IV de 128 bits
    user = str(account)+".user"
    payload = '{"account": "'+user+'","vcc_pin":"'+vcc_pin.decode('latin1')+'", "vcc": "'+str(vcc_amount)+'"}                  '
    with open("bank.auth", 'rb') as f:
        key = f.read()
    with open(str(account)+".user", 'rb') as f:
        iv = f.read()
    cipher = Cipher(algorithms.AES(key[:32]), modes.CBC(iv))
    encryptor = cipher.encryptor()
    data = encryptor.update(payload.encode('utf8'))
    response = requests.post(url=f"http://{ip}:{port}/account/createCard/"+str(account), data=data)
    if response.status_code == 200:
        with open(str(account)+"_"+str(seqNumber)+".card", 'wb') as f:
            f.write(vcc_pin)
        print(payload)
        seqNumber+=1

    else:
        print("Error creating virtual card")



if __name__ == "__main__":
    args = parse_args()
    print(args)
    if args.u is None and args.a is not None: # If the user file is not specified, use the account name prepended to .user
        args.u = f"{args.a}.user"

    if args.u is not None and args.a is not None and args.n is not None:

        pin = os.urandom(16)  # Pin de 128 bits, para ser usado como IV para encriptação de comunicação cliente banco para criar um vcc
        with open(args.u, 'wb') as f:
            f.write(pin)
        data="conta: "+str(args.u)+", pin: "+pin.decode("latin1")+", saldo: "+str(args.n)+ "                                     "
        print(data)
        key=""
        with open("bank.auth", 'rb') as f:
            key = f.read()
        cipher = Cipher(algorithms.AES(key[:32]), modes.CBC(key[32:]))
        encryptor = cipher.encryptor()
        ct = encryptor.update(data.encode("utf8"))
        response = requests.post(url=f"http://{args.i}:{args.p}/account", data=ct)

    if args.g is not None:
        get_account_balance(args.i, args.p, args.g)

    if args.d is not None and args.a is not None:
        deposit(args.i, args.p, args.a, args.d)

    if args.c is not None and args.a is not None:
        create_vcc(args.i, args.p, args.a, args.c)

