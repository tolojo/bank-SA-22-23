import hashlib
import json
import os
import argparse
import signal
import sys
import hmac
from multiprocessing import Process

import requests
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.ciphers.algorithms import AES
global seqNumber
seqNumber = 0

"""
python3 Client.py -s bank.auth -u 55555.user -a 55555 -n 1000.00
python3 Client.py -s bank.auth -u 55555.user -a 55555 -c 63.10  
python3 Client.py -a 55555_0.card -m 45.10 

"""
def handler(signum, frame):
   print("Forever is over!")
   raise Exception("end of time")

# Argument Parsing #
def check_balance(value):
    if value <= 0:
        raise argparse.ArgumentTypeError("Balance must be a positive number.")
    return value

def check_account(value):
    if not os.path.isfile(value + '.user'):
        raise argparse.ArgumentTypeError(f"Account '{value}' does not exist.")
    return value

def parse_args():
    parser = argparse.ArgumentParser(description='Client')
    parser.add_argument('-i', metavar='bk-ip', type=str, default='127.0.0.1',  help='The IP that the client will search the bank. default is localhost')
    parser.add_argument('-p', metavar='bk-port', type=check_port, default=3000, help='The port that bank will listen on. Defaults to 3000.')
    parser.add_argument('-s', metavar='auth-file', type=check_auth_file, default='bank.auth', help='Name of the auth file. Defaults to bank.auth')
    parser.add_argument('-u', metavar='user-file', type=str, default=None, help='The customer user file. The default value is the account name prepended to .user')
    parser.add_argument('-a', metavar='account', type=check_account, help='The account that you want to do operations.')
    parser.add_argument('-n', metavar='balance', type=check_balance, help='The balance of the account that you want to create')
    parser.add_argument('-d', metavar='deposit', type=check_balance, help='The amount you want to deposit on the account')
    parser.add_argument('-c', metavar='vcc', type=check_balance, help='The amount of money that you want to create a virtual card with')
    parser.add_argument('-g', metavar='balance', type=int, help='Get the balance of a certain account')
    parser.add_argument('-m', metavar='purchase', type=check_balance, help='Withdraw the amount of money specified from the virtual credit card and the bank account')
    return parser.parse_args()


def signal_handler(sig, frame):
    print("SIGTERM received. Exiting cleanly...")
    sys.exit(0)


def get_account_balance(ip, port, account):
    response = requests.get(url=f"http://{ip}:{port}/account/{account}.user")
    if response.status_code == 200:
        print(response.text)
    else:
        print("Error getting account balance")


def deposit(ip, port, account, deposit_amount):
    user = (account+".user                                            ").encode("utf8")
    deposit_amount = (str(deposit_amount) + "                                       ").encode("utf8")

    with open("bank.auth", 'rb') as f:
        key = f.read()
    with open(account+".user", 'rb') as f:
        iv = f.read()

    cipher = Cipher(algorithms.AES(key[:32]), modes.CBC(iv))
    encryptor = cipher.encryptor()
    user = encryptor.update(user)

    cipher = Cipher(algorithms.AES(key[:32]), modes.CBC(key[32:]))
    encryptor = cipher.encryptor()

    amount = encryptor.update(deposit_amount)

    payload = (user.decode("latin1") + "|" + amount.decode("latin1")).encode("latin1")
    h =  hmac.new(key[:32],payload,hashlib.sha3_256).hexdigest()

    headers = {
        "Authorization": f"{h}",
        "User": f"{account}.user"
    }
    response = requests.post(url=f"http://{ip}:{port}/account/deposit", headers=headers, data=payload, timeout=10)
    if response.status_code == 200:
        print(response.text)
    else:
        print("Error depositing money")

def buy_product(account, amount_used):
    user = "account: "+account
    amount_used = (str(amount_used)+"                       ").encode("utf8")

    with open("bank.auth", 'rb') as f:
        key = f.read()
    with open(account, 'rb') as f:
        iv = f.read()

    cipher = Cipher(algorithms.AES(key[:32]), modes.CBC(iv))
    encryptor = cipher.encryptor()
    user = encryptor.update(user.encode("utf8"))

    cipher = Cipher(algorithms.AES(key[:32]), modes.CBC(key[32:]))
    encryptor = cipher.encryptor()

    amount = encryptor.update(amount_used)
    payload = (user.decode("latin1")+"|"+amount.decode("latin1")).encode("latin1")
    # Encrypt account with vcc iv and amount with .auth iv
    h =  hmac.new(key[:32],payload,hashlib.sha3_256).hexdigest()
    account=account+"                                            "
    user = account.split("_")[0]
    headers = {
        "Authorization": f"{h}",
        "User": f"{user}.user"
    }

    response = requests.post(url=f"http://127.0.0.1:5000/buy",headers=headers, data=payload,timeout=10)

    if response.status_code == 200:
        os.remove(account.strip(" "))
        print(response.text)
    else:
        print("Invalid transaction")

def create_vcc(ip, port, account, vcc_amount):
    global seqNumber
    vcc_pin = os.urandom(16)  # IV de 128 bits
    user = account+".user"
    payload = '{"account": "'+user+'","vcc_pin":"'+vcc_pin.decode('latin1')+'", "vcc": "'+str(vcc_amount)+'"}                  '
    with open("bank.auth", 'rb') as f:
        key = f.read()
    with open(account+".user", 'rb') as f:
        iv = f.read()
    cipher = Cipher(algorithms.AES(key[:32]), modes.CBC(iv))
    encryptor = cipher.encryptor()
    data = encryptor.update(payload.encode('utf8'))
    response = requests.post(url=f"http://{ip}:{port}/account/createCard/"+account, data=data, timeout=10)
    if response.status_code == 200:
        with open(account+"_"+str(seqNumber)+".card", 'wb') as f:
            f.write(vcc_pin)
        print(payload)
        seqNumber+=1

    else:
        print("Error creating virtual card")



if __name__ == "__main__":
    args = parse_args()

    if args.u is None and args.a is not None: # If the user file is not specified, use the account name prepended to .user
        args.u = f"{args.a}.user"

    if args.u is not None and args.a is not None and args.n is not None:

        pin = os.urandom(16)  # Pin de 128 bits, para ser usado como IV para encriptação de comunicação cliente banco para criar um vcc
        data="conta: "+str(args.u)+", pin: "+pin.decode("latin1")+", saldo: "+str(args.n)+ "                                     "
        print(data)
        key=""
        with open("bank.auth", 'rb') as f:
            key = f.read()
        cipher = Cipher(algorithms.AES(key[:32]), modes.CBC(key[32:]))
        encryptor = cipher.encryptor()
        ct = encryptor.update(data.encode("utf8"))
        response = requests.post(url=f"http://{args.i}:{args.p}/account", data=ct, timeout=10)
        if response.status_code == 200:
            with open(args.u, 'wb') as f:
                f.write(pin)

    if args.g is not None:
        get_account_balance(args.i, args.p, args.g)

    if args.d is not None and args.a is not None:
        deposit(args.i, args.p, args.a, args.d)

    if args.c is not None and args.a is not None:
        create_vcc(args.i, args.p, args.a, args.c)

    if args.m is not None and args.a is not None:
        buy_product(args.a, args.m)

