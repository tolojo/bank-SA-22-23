# bank-SA-22-23

Para correr o programa é necessário ter o python 3 instalado, preferencialmente a versão 3.11

## Bank
No diretório do projeto:

```bash
cd Bank
python3 Bank.py
```
E copiar o ficheiro de autenticação (auth.bank por omissão) para o diretório ../Client e ../Shop

## Client (MBeC)
No diretório do projeto:
```bash
cd Client
```
E verificar se o ficheiro de autenticação do banco existe e se encontra presente no diretório atual

Exemplos:
```bash
python3 Client.py -s bank.auth -u 55555.user -a 55555 -n 1000.00
python3 Client.py -s bank.auth -u 55555.user -a 55555 -c 63.10  
python3 Client.py -a 55555_0.card -m 45.10 
```

## Store (shop.py)
No diretório do projeto:
```bash
cd Shop
python3 shop.py
```

Nota: Verificar se o ficheiro de autenticação do banco existe e se encontra presente no diretório atual
