import base64
import string
from os import path, urandom, remove
from sys import platform
from shutil import copy2
from random import choice, randint, sample

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

if platform.startswith("linux"):
    key_path = path.expanduser("~/.keys/pwmngr.key")
    db_path = path.expanduser("~/.database/pwmngr.db")
elif platform.startswith("win32"):
    key_path = path.abspath(" /../../.keys/pwmngr.key")
    db_path = path.abspath(" /../../.database/pwmngr.db")
key_path = key_path.replace("pwmngr.key", "temp_pwmngr.key")        # temp path for testing
db_path = db_path.replace("pwmngr.db", "temp_pwmngr.db")  # temporary path for testing
salt_path = key_path.replace("pwmngr.key", "pwmngr.salt")

def salt_gen():
    salt_new = urandom(16)
    with open(salt_path, "wb") as f:
        f.write(salt_new)

def key_write(key):
    with open(key_path, "wb") as f:     # wb = write bytes
        f.write(key)
    f.close()

def key_read():
    with open(key_path, "rb") as f:     # rb = read bytes
        key = f.read()
    f.close()
    return key

def key_random():
    key = Fernet.generate_key()
    return key

def key_pw(pw_for_keygen):
    password = pw_for_keygen.encode()
    with open(salt_path, "rb") as f:
        salt = f.read()
    f.close
    # salt = b'u\xbc\x17c\x8b\xff_\xc1\xc2go"\xa7\xa3}t'
    kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=101524,
            backend=default_backend()
        )
    key = base64.urlsafe_b64encode(kdf.derive(password))
    return key

def file_encrypt(file_in, file_out, key, opt):
    with open(file_in, "rb") as f:   # Open the file to encrypt
        data = f.read()
    fernet = Fernet(key)
    if opt == "en":
        output = fernet.encrypt(data)
    elif opt == "de":
        output = fernet.decrypt(data)
    with open(file_out, "wb") as f: # Write the encrypted file
        f.write(output)

def str_encrypt(str_in, key, opt):
    fernet = Fernet(key)
    if opt == "en":
        str_out = fernet.encrypt(str_in.encode())
    elif opt == "de":
        str_out = fernet.decrypt(str_in).decode()
    return str_out

def master_pw(pw_in, opt):
    if opt == "login":
        key = key_pw(pw_in)
        if key == key_read():
            print("Master Password correct!")
            return True
        else:
            print("Incorrect password!")
            return False
    elif opt == "new":
        key = key_pw(pw_in)
        key_write(key)
    elif opt == "change":
        key = key_pw(pw_in)
        copy2(key_path, key_path+".old")
        key_write(key)
    elif opt == "del_old":
        remove(key_path+".old")

def pwgen(in_put):
    in_put = str(in_put).replace(" ","")
    if in_put != "" and not allpunct(in_put): return in_put
    pw_length = randint(10,14)
    p_up = "".join(choice(string.ascii_uppercase) for x in range(randint(1,3)))
    p_nums = "".join(choice(string.digits) for x in range(randint(2,3)))
    if in_put=="":
        # p_punc = "".join(choice(string.punctuation) for x in range(randint(1,3)))
        p_punc = "".join(choice("!@#$%^&*-_+=<>,.?") for x in range(randint(1,3)))
    else:
        p_punc = "".join(choice(in_put) for x in range(randint(1,2)))
    p_low = "".join(choice(string.ascii_lowercase) for x in range(pw_length-len(p_up)-len(p_nums)-len(p_punc)))
    password = "".join(sample(p_up+p_low+p_nums+p_punc, pw_length))
    return password

def allpunct(in_put):
    for i in in_put:
        if i not in string.punctuation:
            return False
    return True