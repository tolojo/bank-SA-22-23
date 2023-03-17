import json
import os
import argparse
import sys


def parse_args():
    parser = argparse.ArgumentParser(description='Client')
    parser.add_argument('-i', metavar='bk-ip', type=str, default='127.0.0.1',  help='The IP that the client will search the bank. default is localhost')
    parser.add_argument('-p', metavar='bk-port', type=int, default=3000, help='The port that bank will listen on. Defaults to 3000.')
    parser.add_argument('-s', metavar='auth-file', type=str, default='bank.auth', help='Name of the auth file. Defaults to bank.auth')
    parser.add_argument('-u', metavar='user-file', type=int, help='The port that bank will listen on. Defaults to 3000.')
    parser.add_argument('-a', metavar='account', type=int, help='The account that you want to do operations.')
    parser.add_argument('-n', metavar='balance', type=int, help='The balance of the account that you want to create')
    parser.add_argument('-d', metavar='deposit', type=int, help='The amount you want to deposit on the account')
    parser.add_argument('-c', metavar='vcc', type=int, help='The amount of money that you want to create a virtual card with')
    parser.add_argument('-g', metavar='balance', type=int, help='Get the balance of a certain account')
    return parser.parse_args()

def signal_handler(sig, frame):
    print("SIGTERM received. Exiting cleanly...")
    sys.exit(0)



if __name__ == "__main__":
    args = parse_args()
    print(
        args
    )
