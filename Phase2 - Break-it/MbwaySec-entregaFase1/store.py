import json,socket,signal,sys,random,base64,secrets,os,hmac,hashlib
from checker import Checker
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import serialization,hashes
from cryptography.hazmat.primitives import padding as pd
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import load_pem_public_key


class StoreServer:
    
    def __init__(self, port, auth_file):
        
        self.port = port
        self.auth_file = auth_file
        
        self.challenge = str(random.randint(0,pow(10,50)))
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        self.public_key = self.private_key.public_key()
        
        self.bank_pubkey = self.mbec_pubkey = self.bank_pubkey = None
        
        self.mbec_store_sym_key = os.urandom(32)
        self.bank_store_sym_key = os.urandom(32)
        self.initial_key = None
        
        self.mbec_store_sec_key = self.bank_store_sec_key = None

    def share_pubkey(self,sock):

        pem = self.public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        hmac_hash = hmac.new(self.initial_key, digestmod=hashlib.sha256)

        # update the hash object with the data
        hmac_hash.update(pem)

        sock.sendall(hmac_hash.digest() + pem) 
        
    def get_mbec_pubkey(self,sock):
        
        data = sock.recv(1024)

        s_hmac_digest = data[:32]
        res_data = data[32:]

        hmac_hash = hmac.new(self.initial_key, digestmod=hashlib.sha256)

        # update the hash object with the data
        hmac_hash.update(res_data)

        # get the HMAC digest
        hmac_digest = hmac_hash.digest()

        self.mbec_pubkey = serialization.load_pem_public_key(res_data) \
            if hmac.compare_digest(s_hmac_digest,hmac_digest) else None
        
    def share_sym(self,sock,data):
        
        js = json.loads(self.decrypt_with_prikey(data))

        if js['op'] == "sharingkeyreq":
            
            sock.sendall(self.encrypt_with_pubkey(self.mbec_pubkey,
                                                  self.mbec_store_sym_key)) #response from bank

        else:
            return
        
    def share_sym2(self,sock):
        
        sharekey_req = {
            "op" : "sharingkeyreq",
        }

        sock.sendall(self.encrypt_with_pubkey(self.bank_pubkey,sharekey_req))

        self.bank_store_sym_key = self.decrypt_with_prikey(sock.recv(1024))
        
        
    def mut_auth_with_bank(self,sock):
        
        self.challenge = str(random.randint(0,pow(10,50)))
        establishreq = {
            'op' : 'establishreq',
            'challenge' : self.challenge
        }

        sock.sendall(self.encrypt_with_pubkey(self.bank_pubkey,
                                              establishreq)) #first send

        res_bank = json.loads(self.decrypt_with_prikey(sock.recv(1024)))

        sys.exit(135) if res_bank["result"] != self.challenge else None

        establishposttrd = {
            "op" : "establishposttrd",
            "result" : res_bank["challenge"]
        }    

        sock.sendall(self.encrypt_with_pubkey(self.bank_pubkey,
                                            establishposttrd)) #second send
        
    def mut_auth_with_mbec(self, client_socket,data):

        self.challenge = str(random.randint(0,pow(10,50)))

        res_dec = self.decrypt_with_prikey(data)
        js = json.loads(res_dec.decode())

        establishpost = {
            'op' : 'establishpost',                                            
            'result' : str(js['challenge']),                 
            'challenge' : self.challenge
        }
        
        client_socket.sendall(self.encrypt_with_pubkey(self.mbec_pubkey,
                                                    establishpost)) 

        snd_req = client_socket.recv(1024) #seconde req from mbec

        res_mbec = json.loads(self.decrypt_with_prikey(snd_req).decode("utf-8"))
        
        return False if res_mbec["result"] != self.challenge else True

    def handle_client_connection(self, recv_sock, send_sock, req):
        
        op = req["op"]
        vcc_file = req["vcc_file"]
        amount = req["balance"]
            
        if op == "shoppingreq":
            
            vcc_req = {
                "op": "vccreq",
                "vcc_file": vcc_file,
                "balance": amount,
                "rand" : str(random.randint(0,pow(10,50))) #introduce randomness in message
            } 
                
            self.send_recv_data(send_sock,"s",
                                vcc_req,
                                self.bank_store_sym_key,
                                self.bank_store_sec_key)
            
            res_bank = self.send_recv_data(send_sock,"r",
                                            send_sock.recv(1024),
                                            self.bank_store_sym_key,
                                            self.bank_store_sec_key)

            response = {
                "op": op + "post",
                "result": res_bank["result"],
                "amount": amount if res_bank["result"] == 1 else None,
                "rand" : str(random.randint(0,pow(10,50)))
            }
            
            if res_bank["result"] == 1 : print({"vcc_file":vcc_file,"vcc_amount_used":float(amount)})

            self.send_recv_data(recv_sock,"s",
                                response,
                                self.mbec_store_sym_key,
                                self.mbec_store_sec_key)
            
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
            
            sys.exit(135) if not hmac.compare_digest(s_hmac_digest,hmac_digest) else None

            decryptor = cipher.decryptor()
            unpadder = pd.PKCS7(128).unpadder()
            
            plaintext = decryptor.update(ciphertext) + decryptor.finalize()
            unpadded = unpadder.update(plaintext) + unpadder.finalize()
            
            return json.loads(unpadded.decode('utf-8'))

        sock.sendall(hmac_digest + res_data)
                
        return

    def share_hmac(self,client_socket):

        self.mbec_store_sec_key = secrets.token_bytes(32)
        
        client_socket.sendall(self.encrypt_with_pubkey(self.mbec_pubkey,
                                                       self.mbec_store_sec_key)) 

    def get_hmac_key(self,sock):

        return self.decrypt_with_prikey(sock.recv(1024))
    
    def decrypt_with_prikey(self,data):
    
        res = self.private_key.decrypt(
        data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        ))
        
        return res
    
    def encrypt_with_pubkey(self,pubkey,data):
    
        f_data = data if isinstance(data,bytes) else (json.dumps(data, ensure_ascii=False)).encode()
        
        req = pubkey.encrypt(
        f_data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        ))
        
        return req
    
    def run_server(self):
        
        # create server socket and bind to port
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('127.0.0.1', self.port))
        server_socket.listen()

        signal.signal(signal.SIGINT, self.cleanup)
        
        #this might have to be inside while loop. To be continued
        #bank_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #bank_socket.connect(('127.0.0.1', 3000))
        
        try: 
            with open(self.auth_file, 'rb') as f:
                bytes = f.read()
            
            self.bank_pubkey = load_pem_public_key(bytes[32:])
            self.initial_key = bytes[:32]

        except:
            sys.exit(135)
        
        try :

            # start listening for client connections
            while True:
                
                client_socket, _ = server_socket.accept()
                
                bank_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                bank_socket.connect(('127.0.0.1', 3000))
                
                self.share_pubkey(bank_socket)
            
                self.mut_auth_with_bank(bank_socket)
                
                self.share_sym2(bank_socket)

                self.bank_store_sec_key = self.get_hmac_key(bank_socket)

                self.get_mbec_pubkey(client_socket)
                
                self.share_pubkey(client_socket)

                self.mut_auth_with_mbec(client_socket,
                                            client_socket.recv(1024))
                
                self.share_sym(client_socket, client_socket.recv(1024))

                self.share_hmac(client_socket)

                data = self.send_recv_data(client_socket,"r",
                                        client_socket.recv(1024),
                                            self.mbec_store_sym_key,
                                            self.mbec_store_sec_key)
                self.handle_client_connection(client_socket,bank_socket,data)
                
        except:
            
            sys.exit(63)
    
    def cleanup(self):
        
        print("Store server exiting...")
        exit(0)

if __name__ == '__main__':

    try :

        check = Checker()
        
        port,auth_file = check.check_args(sys.argv,1)

        store_server = StoreServer(port,auth_file)
        store_server.run_server()

    except :
        sys.exit(135)
    
    sys.exit(0)