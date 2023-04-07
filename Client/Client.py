import hashlib
import json
import os
import argparse
import sys
import hmac
import re
import signal
from multiprocessing import Process
from flask import request
import requests
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.ciphers.algorithms import AES

seqNumber = 0
vccSecNumb = 0
filename_regex = re.compile(r'^[_\-\.0-9a-z]{1,127}$')
decimal_regex = re.compile(r'^(0|[1-9][0-9]*)$')
float_regex = re.compile(r'^\d{1,10}\.\d{2}$')

"""
python3 Client.py -s bank.auth -u 55555.user -a 55555 -n 1000.00
python3 Client.py -s bank.auth -u 55555.user -a 55555 -c 63.10  
python3 Client.py -a 55555_0.card -m 45.10 
"""
seqNumber = 0
def parse_args():
    parser = argparse.ArgumentParser(description='Client')
    parser.add_argument('-i', metavar='bk-ip', type=str, default='127.0.0.1',  help='The IP that the client will search the bank. default is localhost')
    parser.add_argument('-p', metavar='bk-port', type=int, default=3000, help='The port that bank will listen on. Defaults to 3000.')
    parser.add_argument('-s', metavar='auth-file', type=str, default='bank.auth', help='Name of the auth file. Defaults to bank.auth')
    parser.add_argument('-u', metavar='user-file', type=str, default = None, help='The customer user file. The default value is the account name prepended to .user')
    parser.add_argument('-a', metavar='account', type=str, help='The account that you want to do operations.')
    parser.add_argument('-n', metavar='balance', type=str, help='The balance of the account that you want to create')
    parser.add_argument('-d', metavar='deposit', type=str, help='The amount you want to deposit on the account')
    parser.add_argument('-c', metavar='vcc', type=str, help='The amount of money that you want to create a virtual card with')
    parser.add_argument('-g', metavar='balance', type=int, help='Get the balance of a certain account')
    parser.add_argument('-m', metavar='purchase', type=str, help='Withdraw the amount of money specified from the virtual credit card and the bank account')
    return parser.parse_args()

def validate_args(args):
    if not re.match(r'^[1-9]\d*$', str(args.p)):
        return False, 135
    if not (1024 <= args.p <= 65535):
        return False, 135

    if not re.match(filename_regex, args.s):
        return False, 130

    ip_pattern = re.compile(r'^((25[0-5]|2[0-4]\d|1\d{2}|[1-9]\d|\d)\.){3}(25[0-5]|2[0-4]\d|1\d{2}|[1-9]\d|\d)$')
    if not re.match(ip_pattern, args.i):
        return False, 130

    return True, None

def signal_handler(sig, frame):
    sys.exit(0)


def get_account_balance(ip, port, account):
    try:
        response = requests.get(url=f"http://{ip}:{port}/account/{account}.user", timeout=10)
        response.raise_for_status()

        with open("bank.auth", 'rb') as f:
            key = f.read()
        with open(str(account) + ".user", 'rb') as f:
            iv = f.read()

        h = hmac.new(key[:32], response.text.encode("latin1"), hashlib.sha3_256).hexdigest()

        if (h == response.headers.get("Authorization")):

            cipher = Cipher(algorithms.AES(key[:32]), modes.CBC(iv))
            decryptor = cipher.decryptor()

            saldo = decryptor.update(response.text.encode("latin1")).decode("utf8")

    except requests.exceptions.Timeout:
        sys.exit(63)
    except requests.exceptions.RequestException:
        sys.exit(63)
    if response.status_code == 200:
        print(saldo)
        sys.stdout.flush()
    else:
        sys.exit(135)


def deposit(ip, port, account, deposit_amount):
    global seqNumber
    if not re.match(r'^\d+\.\d{2}$', str(deposit_amount)):
        sys.exit(125) # invalid input amount format
    if not re.match(r'^[_\-\.0-9a-z]{1,127}$', account):
        sys.exit(125) # invalid account name format

    user = (account+".user                                                     ").encode("utf8")
    deposit_amount = ("amount: "+str(deposit_amount) + "                                                  ").encode("utf8")

    # rest of the function code

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
    cipher = Cipher(algorithms.AES(key[:32]), modes.CBC(key[32:]))
    encryptor = cipher.encryptor()
    seq_number = encryptor.update(("number: " + str(seqNumber) + "                                                                           ").encode("utf8"))

    payload = (seq_number.decode("latin1")+"|"+user.decode("latin1") + "|" + amount.decode("latin1")).encode("latin1")
    h = hmac.new(key[:32], payload, hashlib.sha3_256).hexdigest()

    headers = {
        "Authorization": f"{h}",
        "User": f"{account}.user"
    }
    
    try:
        response = requests.post(url=f"http://{ip}:{port}/account/deposit", headers=headers, data=payload, timeout=10)
        response.raise_for_status()
    except requests.exceptions.Timeout:
        sys.exit(63)
    except requests.exceptions.RequestException:
        sys.exit(63)
    if response.status_code == 200:
        print(response.text)
        sys.stdout.flush()
    else:
        sys.exit(135)

def buy_product(account, amount_used):
    #ver, não está a funcionar
    global seqNumber
    user = "account: "+account
    amount_used = ("amount: "+str(amount_used)+"                                    ").encode("utf8")

    with open("bank.auth", 'rb') as f:
        key = f.read()
    with open(account, 'rb') as f:
        iv = f.read()

    cipher = Cipher(algorithms.AES(key[:32]), modes.CBC(iv))
    encryptor = cipher.encryptor()
    user = encryptor.update(user.encode("utf8"))


    cipher = Cipher(algorithms.AES(key[:32]), modes.CBC(key[32:]))
    encryptor = cipher.encryptor()
    seq_number = encryptor.update(("number: "+str(seqNumber)+"                                                                   ").encode("utf8"))
    print(seq_number.decode("latin1"))
    cipher = Cipher(algorithms.AES(key[:32]), modes.CBC(key[32:]))
    encryptor = cipher.encryptor()
    amount = encryptor.update(amount_used)

    payload = (seq_number.decode("latin1") +"|"+user.decode("latin1")+"|"+amount.decode("latin1")).encode("latin1")
    # Encrypt account with vcc iv and amount with .auth iv
    h =  hmac.new(key[:32],payload,hashlib.sha3_256).hexdigest()
    account=account+"                                            "
    user = account.split("_")[0]
    headers = {
        "Authorization": f"{h}",
        "User": f"{user}.user"
    }

    try:
        response = requests.post(url=f"http://127.0.0.1:5000/buy",headers=headers, data=payload, timeout=10)
        response.raise_for_status()
    except requests.exceptions.Timeout:
        sys.exit(63)
    except requests.exceptions.RequestException:
        sys.exit(63)
    if response.status_code == 200:
        os.remove(account.strip(" "))
        print(response.text)
    else:
        sys.exit(135)

def create_vcc(ip, port, account, vcc_amount):
    if not re.match(r'^[_\-\.0-9a-z]{1,122}$', account):
        sys.exit(125)  # invalid account name format
    if not re.match(r'^\d+\.\d{2}$', str(vcc_amount)):
        sys.exit(125)  # invalid input amount format

    user = account+".user"
    payload = '{"account": "'+user+'","vcc": "'+str(vcc_amount)+'"}                  '
    with open("bank.auth", 'rb') as f:
        key = f.read()
    with open(account+".user", 'rb') as f:
        iv = f.read()

    cipher = Cipher(algorithms.AES(key[:32]), modes.CBC(iv))
    encryptor = cipher.encryptor()
    data = encryptor.update(payload.encode('utf8'))
    
    try:
        response = requests.post(url=f"http://{ip}:{port}/account/createCard/"+account, data=data, timeout=10)
        response.raise_for_status()
    except requests.exceptions.Timeout:
        sys.exit(63)
    except requests.exceptions.RequestException:
        sys.exit(63)
    if response.status_code == 200:

        decryptor = cipher.decryptor()
        vcc_pin = decryptor.update(response.text.encode("latin1"))
        """
        vcc_seq_number = response.headers.get("VCC_SEQ_NUMB")
        vcc_seq_number = decryptor.update(vcc_seq_number.encode("latin1")).decode("utf8").strip(" ").strip("seq:")
        """
        vcc_seq_number = response.headers.get("VCC_SEQ_NUMB")
        with open(account+"_"+str(vcc_seq_number)+".card", 'wb') as f:
            f.write(vcc_pin)
        global vccSecNumb
        vccSecNumb = vcc_seq_number
        print(payload)


    else:
        sys.exit(135) # invalid account name or vcc amount

if __name__ == "__main__":

    args = parse_args()

    if ' '.join(sys.argv[1:]).replace(' ', '').__len__() > 4096:
        sys.exit(130)
    valid, error_code = validate_args(args)
    if not valid:
        sys.exit(error_code)

    if args.u is None and args.a is not None: # If the user file is not specified, use the account name prepended to .user
        if not re.match(r'^[_.\-a-zA-Z0-9]{1,122}$', args.a):
            sys.exit(130)

        args.u = f"{args.a}.user"

    if args.u is not None and args.a is not None and args.n is not None:

        if not re.match(r'^[_.\-a-zA-Z0-9]{1,122}$', args.a):
            sys.exit(130)

        if not re.match(float_regex, args.n):
            sys.exit(130)

        if not re.match(filename_regex, args.u):
            sys.exit(130)
        data = "conta: "+str(args.u)+", saldo: "+str(args.n) + "                                     "
        key = ""
        with open("bank.auth", 'rb') as f:
            key = f.read()
        cipher = Cipher(algorithms.AES(key[:32]), modes.CBC(key[32:]))
        encryptor = cipher.encryptor()
        ct = encryptor.update(data.encode("utf8"))
        decryptor = cipher.decryptor()

        try:
            response = requests.post(url=f"http://{args.i}:{args.p}/account", data=ct, timeout=10)
            print(response.status_code)

            if response.status_code == 400:
                sys.exit(130)

            pin = decryptor.update(response.text.encode("latin1"))
            response.raise_for_status()

        except requests.exceptions.Timeout:
            sys.exit(63)

        except requests.exceptions.RequestException:
            sys.exit(63)

        if response.status_code == 200:
            with open(args.u, 'wb') as f:
                f.write(pin)


    if args.g is not None:
        if not re.match(decimal_regex, str(args.g)):
            sys.exit(130)

        get_account_balance(args.i, args.p, args.g)

    if args.d is not None and args.a is not None:
        response = requests.get(url=f"http://{args.i}:{args.p}/seqnumb", timeout=10)
        with open("bank.auth", 'rb') as f:
            key = f.read()
        cipher = Cipher(algorithms.AES(key[:32]), modes.CBC(key[32:]))
        decryptor = cipher.decryptor()

        seqNumber = int(decryptor.update(response.text.encode("latin1")).decode("utf8"))
        if not re.match(float_regex, args.d):
            sys.exit(130)

        deposit(args.i, args.p, args.a, args.d)

    if args.c is not None and args.a is not None:
        response = requests.get(url=f"http://{args.i}:{args.p}/seqnumb", timeout=10)
        with open("bank.auth", 'rb') as f:
            key = f.read()
        cipher = Cipher(algorithms.AES(key[:32]), modes.CBC(key[32:]))
        decryptor = cipher.decryptor()

        seqNumber = int(decryptor.update(response.text.encode("latin1")).decode("utf8"))
        if not re.match(r'^[_.\-a-zA-Z0-9]{1,122}$', args.a):
            sys.exit(130)

        if not re.match(float_regex, args.c):
            sys.exit(130)

        create_vcc(args.i, args.p, args.a, args.c)

    if args.m is not None and args.a is not None:
        response = requests.get(url=f"http://{args.i}:{args.p}/seqnumb", timeout=10)
        with open("bank.auth", 'rb') as f:
            key = f.read()
        cipher = Cipher(algorithms.AES(key[:32]), modes.CBC(key[32:]))
        decryptor = cipher.decryptor()

        seqNumber = int(decryptor.update(response.text.encode("latin1")).decode("utf8"))
        if not re.match(float_regex, args.m):
            sys.exit(130)

        if not re.match(r'^[_.\-a-zA-Z0-9]{1,122}$', args.a):
            sys.exit(130)

        buy_product(args.a, args.m)
