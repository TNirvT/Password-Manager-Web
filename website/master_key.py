import base64
from os import path, urandom

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from .pw_gen import phrase_gen
from . import salt_path, secret_phrase

class MasterKey:
    def __init__(self, key):
        self.key = key
        self.salt_path = salt_path

    def unlock(self, pw, encrypted_secret):
        with open(self.salt_path, "rb") as f:     # rb = read bytes
            self.salt = f.read()

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