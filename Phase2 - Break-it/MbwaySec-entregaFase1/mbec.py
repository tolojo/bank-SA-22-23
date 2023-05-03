import sys,json,socket,hashlib,random,base64,os,hashlib,hmac
from checker import Checker
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import serialization,hashes
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.hazmat.primitives import padding as pd

private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048
)

public_key = private_key.public_key()

challenge = str(random.randint(0,pow(10,50)))

bank_key = encrypt_key = cipher = encryptor = decryptor = padder = intial_key = None

def handle_ops(mode,cli_sock,account,vcc_file,user_file,amount,encrypt_key,secret_key):
    
    req = {
        "op" : None,
        "account" : None,
        "user_file" : None,
        "balance" : None,
        "vcc_file" : None,
        "rand" : str(random.randint(0,pow(10,50))) #introduce randomness in message
    }
    
    values = [account,user_file,amount,vcc_file]
    op_dict = {"-n" : ["createaccountreq",1,1,1,0], "-d" : ["depositreq",1,1,1,0], "-c" : ["createvrtcardreq",1,1,1,0],
          "-g" : ["currbalancereq",1,1,0,0], "-m" : ["shoppingreq",0,0,1,1]}
    
    for op in op_dict:
        
        if mode == op:
            
            i = 0
            
            for p,field in zip(op_dict[op],req):
                
                if isinstance(p, str):
                    req[field] = p
                else :
                    if p == 1:
                        req[field] = values[i]
                    i += 1       
    
    send_recv_data(cli_sock,"s",req,encrypt_key,secret_key)
    
    res = send_recv_data(cli_sock,"r",cli_sock.recv(1024),encrypt_key,secret_key)
    
    sys.exit(130) if res["result"] == 0 else None
    
    data = None
    file = None
    vcc_skul = {
        "account": account ,
        "user_file" : user_file
    }
    json_data = json.dumps(vcc_skul)
    
    if mode == "-n" :
        
        data,file = res["pin"],user_file 
    
    if mode == "-c":
        
        data,file = json_data,str(account) + "_" + str(res["sequence"]) + ".card"
        
    if data != None and file != None:
        
        with open(file,"w") as f:
            
            f.write(data)
    
    dict_skul = {"-n" : {"account" : account,"initial_balance" : amount}, "-d" : {"account" : account,"deposit" : amount}, "-c" : {"account" : account,"vcc_amount" : amount,
                                                                                                                                "vcc_file" : vcc_file},
        "-g" :{"account" : account,"balance" : None if mode != "-g" else res["balance"]}, "-m" : {"vcc_file" : vcc_file,"vcc_amount_user" : amount}}

    for op in dict_skul:
    
        if mode == op:
            
            print(dict_skul[op])
 
def share_pubkey(sock,k):

    pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    hmac_hash = hmac.new(k, digestmod=hashlib.sha256)

    # update the hash object with the data
    hmac_hash.update(pem)

    sock.sendall(hmac_hash.digest() + pem)

def get_store_pubkey(sock,k):

    data = sock.recv(1024)

    s_hmac_digest = data[:32]
    res_data = data[32:]

    hmac_hash = hmac.new(k, digestmod=hashlib.sha256)

    # update the hash object with the data
    hmac_hash.update(res_data)

    # get the HMAC digest
    hmac_digest = hmac_hash.digest()

    return serialization.load_pem_public_key(res_data) \
        if hmac.compare_digest(s_hmac_digest,hmac_digest) else None    


def encrypt_with_pubkey(pubkey,data):
    
    f_data = data if isinstance(data,bytes) else (json.dumps(data, ensure_ascii=False)).encode()
    
    req = pubkey.encrypt(
    f_data,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    ))
    
    return req

def decrypt_with_prikey(priv_key,data):
    
    res = priv_key.decrypt(
    data,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    ))
    
    return res
    
def mutual_auth(sock,pubkey):

    establishreq = {
        'op' : 'establishreq',
        'challenge' : challenge
    }
    
    sock.sendall(encrypt_with_pubkey(pubkey,establishreq)) #first send

    res = sock.recv(1024)
    
    res_dec = decrypt_with_prikey(private_key,res)

    res_bank = json.loads(res_dec.decode("utf-8"))

    sys.exit(130) if res_bank["result"] != challenge else None

    establishposttrd = {
        "op" : "establishposttrd",
        "result" : res_bank["challenge"]
    }

    sock.sendall(encrypt_with_pubkey(pubkey,establishposttrd)) #second send

def get_sym_key(sock,pubkey):

    sharekey_req = {
        "op" : "sharingkeyreq"
    }

    sock.sendall(encrypt_with_pubkey(pubkey,sharekey_req))

    data = sock.recv(1024)

    return decrypt_with_prikey(private_key,data)

def send_recv_data(sock,mode,data,k,sec_k):

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
        
        sys.exit(130) if not hmac.compare_digest(s_hmac_digest,hmac_digest) else None

        decryptor = cipher.decryptor()
        unpadder = pd.PKCS7(128).unpadder()
        
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        unpadded = unpadder.update(plaintext) + unpadder.finalize()
        
        return json.loads(unpadded.decode('utf-8'))

    sock.sendall(hmac_digest + res_data)
        
    return

    #add errors and some other things

def main():
        
    check = Checker()

    try :

        account,auth_file,dest_ip,dest_port,user_file,vvc_file,modes_dict = check.check_mbec_args(sys.argv)

        store = check.is_store_op()

    except :
        
        sys.exit(130)
    
    try: 
        with open(auth_file, 'rb') as f:
            bytes = f.read()
        
        bank_key = load_pem_public_key(bytes[32:])
        initial_key = bytes[:32]

    except:
        sys.exit(130)
    
    try :

        #create a socket object and connect
        cli_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cli_sock.connect((dest_ip, dest_port))

        share_pubkey(cli_sock,initial_key)

        dest_pubkey = bank_key if store == 0 else get_store_pubkey(cli_sock,initial_key)
        
        mutual_auth(cli_sock,dest_pubkey)

        encrypt_key = get_sym_key(cli_sock,dest_pubkey)

        secret_key = decrypt_with_prikey(private_key,cli_sock.recv(1024))
        
    except:
        sys.exit(63)
    
    #Mbec modes handler
    for m in modes_dict:

        if modes_dict[m][0] == 1:

            amount = modes_dict[m][1]
            
            handle_ops(m,cli_sock,account,vvc_file,user_file,amount,encrypt_key,secret_key)

if __name__ == "__main__":

    try :  
        main()

    except :
        sys.exit(130)

    sys.exit(0)