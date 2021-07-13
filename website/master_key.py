import base64
from os import path, urandom
from pathlib import Path

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from .pw_gen import pwgen_basic
from . import db_path

secret_path = db_path.replace(".db", ".secr")
if not path.exists(secret_path):
    with open(secret_path, "w") as f:
        f.write(pwgen_basic())
with open(secret_path) as f:
    secret_phrase = f.read()

class MasterKey:
    def __init__(self, key):
        self.key = key
        self.salt_path = db_path.replace(".db", ".salt")

    # def exists(self):
    #     return Path(self.key_path).is_file() and Path(self.salt_path).is_file()

    def unlock(self, pw, encrypted_secret):
        # with open(self.key_path, "rb") as f:     # rb = read bytes
        #     self.key = f.read()
        with open(self.salt_path, "rb") as f:     # rb = read bytes
            self.salt = f.read()

        # valid = self.decrypt(secret_pass) == self.__pw_to_key(pw)
        # if valid:
        #     self.fernet = Fernet(self.key)
        # return valid
        if pw:
            self.key = self.__pw_to_key(pw)
        self.fernet = Fernet(self.key)
        try:        # decryption with wrong key will raise invalid token error
            valid = self.decrypt(encrypted_secret) == secret_phrase
            if not valid:
                delattr(self, "key")
                delattr(self, "fernet")
            return valid
        except Exception:
            return False

    def set_pw(self, pw):
        self.salt = urandom(16)
        with open(self.salt_path, "wb") as f:   # wb = write bytes
            f.write(self.salt)

        self.key = self.__pw_to_key(pw)
        # with open(self.key_path, "wb") as f:
        #     f.write(self.key)

        self.fernet = Fernet(self.key)
        return self.encrypt(secret_phrase)

    def encrypt(self, str):
        if self.fernet is None:
            raise Exception('MasterKey is not unlocked')
        return self.fernet.encrypt(str.encode())

    def decrypt(self, bytes):
        if self.fernet is None:
            raise Exception('MasterKey is not unlocked')
        return self.fernet.decrypt(bytes).decode()

    def __pw_to_key(self, pw):
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=101524,
            backend=default_backend()
        )
        return base64.urlsafe_b64encode(kdf.derive(pw.encode()))