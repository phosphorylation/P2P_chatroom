import cryptography

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import serialization

###############RSA is special, we encrypt with public key and decrypt with private key


def asy_key_gen():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    return private_key


def asy_encrypt(message, public_key):    # encrypt a message using other's public key
    encrypted = public_key.encrypt(
        message,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return encrypted


def asy_decrypt(message, private_key):   # decrypt using your own private key
    decrypted = private_key.decrypt(
        message,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return decrypted


def key_to_bytes(public_key):
    pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo)
    return pem


def bytes_to_key(my_bytes):
    public_key = serialization.load_pem_public_key(
        my_bytes,
        backend=default_backend())
    return public_key


def signing(message, private_key):   # sign a message using your own private key
    signature = private_key.sign(
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH),
        hashes.SHA256()
        )
    return signature


def verify(signature, public_key, message):  # verify using the other's public key
    try:
        public_key.verify(
            signature,
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256()
        )
    except cryptography.exceptions.InvalidSignature:
        print ("signature doesn't match!")
        return False
    return True


def sym_key_gen():
    key = Fernet.generate_key()
    return key


def sym_encrypt(message, key):
    f = Fernet(key)
    token = f.encrypt(message)
    return token


def sym_decrypt(message,key):
    f = Fernet(key)
    decrypted = f.decrypt(message)
    return decrypted

if __name__ == '__main__':
    p = asy_key_gen()
    bytes = key_to_bytes(p.public_key())
    public = p.public_key()
    message = "sadfsadfsd".encode()
    sym = sym_key_gen()
    string = sym_encrypt(message,sym)
    public = string_to_key(string)
    print(public)