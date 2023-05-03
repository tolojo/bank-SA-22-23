# MbwaySec

## Installing Python

1. Access the official Python website at https://www.python.org/downloads/ and download the LTS version.
2. To check if Python was installed correctly, open a terminal or command prompt and run the following command:
    ```
    python --version
    ```
    This will display the version number of Python that was installed on your machine.

## Installing Cryptography module

Access the official module website at https://cryptography.io/en/latest/ or run the following command:

```
pip install cryptography
```

### Disclaimer

If you don't have pip installed in your machine, one can follow the tutorial at https://www.geeksforgeeks.org/how-to-install-pip-on-windows/
    
## Download the Project

1. Download the Zip
2. Extract the zip and you will see a Folder called MbwaySec
3. Open the Visual Studio, then click on File, Select Open Folder and click on the folder that you have extract
4. Open 3 terminal on Visual Studio, one for the client, bank and the store:
## Bank
    
    python3 bank.py
    
## Store
    
    python3 store.py
    
## Client(Mbec)
Examples:
```
python3 mbec.py -s bank.auth -u 55555.user -a 55555 -n 1000.00
python3 mbec.py -s bank.auth -u 55555.user -a 55555 -c 63.10
python3 mbec.py -v 55555_1.card -m 45.10

```

## Environment and limitations

To run this program, you must be on Windows and have all the previous tools installed on your machine. Failing to do so, you might be in the position where this program doesn't work. 

### Sockets

Because this system relies on python sockets, and because the implementation does not free the binding after the program exit, we advise you to ensure that the port you intend to use on any party of this system is free and ready to bind.

Following this topic, sockets might have a erratic behaviour when dealing with several sequential and no-interval-given messages. Because of the way sockets are being used in this system and the way they are natively implemented, messages can sometimes be joined and this can cause problems in system behaviour. So, if you pretend to have some automate system to test it or to use it, please have this in mind

### Messages

If you expected a message and it didn't appear, this might happened for two reasons - first, you used the program without following the guidelines or two - something happened inside the system, maybe because of the sockets problem, maybe for some other reason. Whenever the transaction goes well the message will be printed, giving you that confirmation

### Files and files

Bank.auth must not exist if you want to use a new bank public key. Since the bank fail if there's already a bank.auth and you try to create a new one, it's up to you to delete the file after every program exit. Failing to do so leads to not being able to use the bank properly

Regarding user files, it's again up to you if you to keep that files for next iterations or create new ones.
