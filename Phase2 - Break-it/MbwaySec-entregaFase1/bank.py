import signal,json,hashlib,hmac,random,os,sys,secrets,base64
import socket
from socket import AF_INET, SOCK_DGRAM
from checker import Checker
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import serialization,hashes
from cryptography.hazmat.primitives import padding as pd
from cryptography.hazmat.backends import default_backend

class BankServer:

    def __init__(self, port, auth_file):

        self.port = port
        self.auth_file = auth_file

        self.users = []
        self.challenge = str(random.randint(0,pow(10,50)))

        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        self.public_key = self.private_key.public_key()

        self.symmetric_key = os.urandom(32)
        self.iv = os.urandom(16)
        self.cli_pubkey = self.secret_key = None
        self.initial_key = os.urandom(32)

        self.create_auth_file()
        self.established = 0
             
    def create_auth_file(self):

        try:
            with open(self.auth_file, 'wb') as f:

                f.write(self.initial_key + self.public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo))
                
        except FileExistsError:
                
                sys.exit(125)

    def get_cli_pubkey(self,sock) :

        data = sock.recv(1024)

        s_hmac_digest = data[:32]
        res_data = data[32:]

        hmac_hash = hmac.new(self.initial_key, digestmod=hashlib.sha256)

        # update the hash object with the data
        hmac_hash.update(res_data)

        # get the HMAC digest
        hmac_digest = hmac_hash.digest()

        self.cli_pubkey = serialization.load_pem_public_key(res_data) if hmac.compare_digest(s_hmac_digest,hmac_digest) else None

        if self.cli_pubkey == None : sock.shutdown(socket.SHUT_RDWR)

    def handle_auth(self, client_socket, data):

        self.challenge = str(random.randint(0,pow(10,50)))
        
        fst_req = self.decrypt_with_prikey(data).decode()
        js = json.loads(fst_req)

        establishpost = {
            'op' : 'establishpost',                                            
            'result' : str(js['challenge']),                 
            'challenge' : self.challenge
        }
        
        client_socket.sendall(self.encrypt_with_pubkey(establishpost)) #response from bank

        snd_req = client_socket.recv(1024) #seconde req from mbec

        res_mbec = json.loads(self.decrypt_with_prikey(snd_req).decode("utf-8"))
        
        return False if res_mbec["result"] != self.challenge else True

    def share_cipher_param(self,client_socket,data):
        
        fst_req = self.decrypt_with_prikey(data).decode()
        js = json.loads(fst_req)
        op = js['op']

        if op == "sharingkeyreq":
            
            client_socket.sendall(self.encrypt_with_pubkey(self.symmetric_key)) #response from bank

        else:
            return

    def handle_transaction(self, client_socket, req):
        print("entrei no handle transac")
        # Requests do mbec
        op = req["op"]
        account = req["account"] if op != "vccreq" else None
        user_file = req["user_file"] if op != "vccreq" else None
        balance = req["balance"] if op != "currbalancereq" else None
        sequence = pin = user = vcc_balance = vcc_file_name = None
        
        res_dict = {"createaccountreq" : [1,1,0,0,1], "depositreq" : [1,1,0,0,0], 
                    "createvrtcardreq" : [1,1,1,0,0],"currbalancereq" : [1,1,0,1,0],
                    "vccreq" : [1,1,0,0,0]}
        
        if op != "createaccountreq" and op != "vccreq":
        
            user = self.get_user(account,user_file,1)
            
            if user == None : return self.invalid_req(client_socket,op) 
        
        else :  
            user = self.get_user(account,user_file,0)
        
        # Criar nova conta
        if op == "createaccountreq":
            # Verificar se a conta já existe
            if any(u["account"] == account for u in self.users) \
                    or float(balance) < 15.00 or os.path.exists(user_file): 
                                        
                        return self.invalid_req(client_socket,op) 
            
            self.add_user(account,user_file,balance)

            user = self.get_user(account,user_file,0)
            
            pin = user.get("pin")
            
        # Depositar na conta
        elif op == "depositreq":

            if float(balance) < 0.00 : return self.invalid_req(client_socket,op) 
            user["balance"] += balance
            
        # Criar o cartao virtual
        elif op == "createvrtcardreq":
            
            balance = float(user.get("balance", 0))
            vcc_balance = float(req.get("balance"))

            # Verificar se o utilizador já tem o cartao virtual
            
            if "vcc_file" in user and "purchase_made" in user.get("vcc_file"): 
                
                return self.invalid_req(client_socket,op)
            
            if balance < vcc_balance or vcc_balance < 0.00: return self.invalid_req(client_socket,op) 

            sequence = 1
            if self.users:
                last_user = self.users[-1]
                sequence = int(last_user.get("sequence", 0)) + 1

            # Criar novo cartão virtual
            vcc_file = {"account": account, "user_file": user_file, "balance": balance}
            user["vcc_file"] = vcc_file

            # Atualizar o sequence number do user
            user["sequence"] = str(sequence)
            
        # verificar saldo
        elif op == "currbalancereq":
            balance = user.get("balance", "none")
            
            if balance == "none": return self.invalid_req(client_socket,op)
        
        elif op == "vccreq":

            try :
                with open(req.get("vcc_file"),"r") as f:
                    data = f.read()
                    
            except:
                
                return self.invalid_req(client_socket,op)

            vcc_file_name = req.get("vcc_file")
            vcc_file = json.loads(data)
            vcc_account = vcc_file["account"]
            vcc_user_file = vcc_file["user_file"]
            vcc_balance = float(req.get("balance"))
            
            user = self.get_user(vcc_account,vcc_user_file,1)
            balance = float(user.get("balance", 0))
            
            user = self.get_user(vcc_account,vcc_user_file,1)
            
            if user == None : return self.invalid_req(client_socket,op)

            if vcc_balance > balance or vcc_balance < 0.00: return self.invalid_req(client_socket,op) 
            
            # Deduzir na conta
            if vcc_file and "purchase_made" not in vcc_file:
                user["balance"] = balance - vcc_balance
                vcc_file["purchase_made"] = True

        res = {
            "op" : None,
            "result" : None,
            "sequence" : None,
            "balance" : None,
            "pin" : None,
            "rand" : str(random.randint(0,pow(10,50))) #introduce randomness in message
        }

        fields = {"op" : op + "post","result" : 1,"sequence" : sequence,"balance" : balance ,"pin" : pin}
            
        for r in res_dict:
            
            if op == r:
                
                for f in fields:
                        
                        res[f] = fields[f]
                                                
        self.send_recv_data(client_socket,"s",res,self.symmetric_key,self.secret_key)
        
        vcc_file_name = vcc_file_name if vcc_file_name != None else str(account) + "_" + str(res["sequence"]) + ".card"
        
        ##rollback or smth
        
        dict_skul = {"createaccountreq" : {"account" : account,"initial_balance" : balance}, "depositreq" : {"account" : account,"deposit" : balance}, 
                     "createvrtcardreq" : {"account" : account,"vcc_amount" : vcc_balance, "vcc_file" : vcc_file_name},
                     "currbalancereq" : {"account" : account,"balance" : balance}}

        for s in dict_skul:
        
            if op == s:
                
                print(dict_skul[s])
        
        
    
    def send_recv_data(self,sock,mode,data,k,sec_k):

        s_hmac_digest = res_data = iv = ciphertext = plaintext = None
        
        if isinstance(data,bytes):
            
            s_hmac_digest = data[:32]
            res_data = data[32:]
            
            ciphertext = base64.b64decode(res_data).rstrip()
            iv, ciphertext = ciphertext[:16], ciphertext[16:] 
            
        else:
            
            plaintext = json.dumps(data).rstrip().encode('utf-8')
            iv = os.urandom(16)
            
        cipher = Cipher(
                algorithms.AES(k),
                modes.CBC(iv),
                backend=default_backend()
            )
        
        if mode == "s":

            encryptor = cipher.encryptor()
            padder = pd.PKCS7(128).padder()
            
            padded = padder.update(plaintext) + padder.finalize()
            ciphertext = encryptor.update(padded) + encryptor.finalize()

            res_data = base64.b64encode(iv + ciphertext)

        hmac_hash = hmac.new(sec_k, digestmod=hashlib.sha256)

        # update the hash object with the data
        hmac_hash.update(res_data)

        # get the HMAC digest
        hmac_digest = hmac_hash.digest()
    
        
        if mode == "r" :
            
            sock.shutdown(socket.SHUT_RDWR) if not hmac.compare_digest(s_hmac_digest,hmac_digest) else None

            decryptor = cipher.decryptor()
            unpadder = pd.PKCS7(128).unpadder()
            
            plaintext = decryptor.update(ciphertext) + decryptor.finalize()
            unpadded = unpadder.update(plaintext) + unpadder.finalize()
            
            return json.loads(unpadded.decode('utf-8'))

        sock.sendall(hmac_digest + res_data)
        
        return
    
    def share_hmac_key(self,client_socket):

        self.secret_key = secrets.token_bytes(32)
            
        client_socket.sendall(self.encrypt_with_pubkey(self.secret_key)) #response from bank

    def decrypt_with_prikey(self,data):
    
        res = self.private_key.decrypt(
        data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        ))
        
        return res
    
    def encrypt_with_pubkey(self,data):
        
        f_data = data if isinstance(data,bytes) else (json.dumps(data, ensure_ascii=False)).encode() 
        
        req = self.cli_pubkey.encrypt(
        f_data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        ))
        
        return req
    
    def get_user(self,account,user_file,check_file):
        
        if check_file == 1 :
        
            with open(user_file,"r") as f:
                pin = f.read()
            
        user = None
        for u in self.users:
            
            if u.get("account") == account and check_file == 1 and u.get("pin") == pin :
                return u
            
            if u.get("account") == account:
                return u

        return user 

    def add_user(self,account,user_file,balance):

        pin = str(random.random())
        self.users.append({
            "account": account,
            "user_file": user_file,
            "balance": balance,
            "pin" : pin
        })
                
    def invalid_req(self,sock,op):
        
        res = {
            "op" : op,
            "result" : 0
        }
        
        self.send_recv_data(sock,"s",res,self.symmetric_key,self.secret_key)
        
        return 1
    
    def run(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('127.0.0.1', 4000))
        server_socket.settimeout(10)
        server_socket.listen()
        signal.signal(signal.SIGTERM, self.cleanup)
        
        #try:
        while True:
            try :
                client_socket, _ = server_socket.accept()
                client_socket

                #get cli pubkey 

                self.get_cli_pubkey(client_socket)
                #self.cli_pubkey = serialization.load_pem_public_key(client_socket.recv(1024))

                auth_successful = self.handle_auth(client_socket,client_socket.recv(1024))

                if auth_successful == True:


                    self.established = 1

                    #check this because of loop - try to read forever
                    self.share_cipher_param(client_socket, client_socket.recv(1024))

                    #share_hmac_key
                    self.share_hmac_key(client_socket)
                    
                    req = self.send_recv_data(client_socket,"r",client_socket.recv(1024),
                                            self.symmetric_key,self.secret_key)
                    self.handle_transaction(client_socket, req)
                    
                else :

                    self.established = 0

                    client_socket.shutdown(socket.SHUT_RDWR)
                    client_socket.close()
                    
            except socket.timeout:
                
                print("protocol_error\n")
                
            
    def cleanup(self):
        
        if os.path.exists(self.auth_file):
            os.remove(self.auth_file)
            
        print("Bank server exiting...")
        sys.exit(0)


if __name__ == "__main__":



        check = Checker()

        port,auth_file = check.check_args(sys.argv,0)

        bank_server = BankServer(port, auth_file)
        bank_server.run()
        bank_server.cleanup()
        sys.exit(0)

