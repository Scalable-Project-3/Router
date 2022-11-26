from cryptography.fernet import Fernet
import rsa


def sign(message, private_key):
    return rsa.sign(message.encode('utf8'), private_key, 'SHA-1')


def verify(message, signature, pub_key):
    try:
        return rsa.verify(message.encode('utf8'), signature, pub_key, ) == 'SHA-1'
    except:
        return False


def encrypt_with_rsa(msg, pub_key):
    return rsa.encrypt(msg.encode('utf8'), pub_key)


def decrypt_with_rsa(encrypted_msg, d_key):
    try:
        return rsa.decrypt(encrypted_msg, d_key).decode('utf8')
    except:
        return False


def encrypt_with_aes(msg, aes_key):
    f = Fernet(aes_key)
    return f.encrypt(msg)


def decrypt_with_aes(encrypted_msg, symmetric_key):
    f = Fernet(symmetric_key)
    return f.decrypt(encrypted_msg)


def generate_aes_key():
    return Fernet.generate_key()


def load_private_key():
    with open('security/keys/privateKey.pem', 'rb') as p:
        privateKey = rsa.PrivateKey.load_pkcs1(p.read())
    return privateKey


def load_pub_key():
    with open('security/keys/publicKey.pem', 'rb') as p:
        publicKey = rsa.PublicKey.load_pkcs1(p.read())
    return publicKey


def generate_rsa_key_pair():
    (publicKey, privateKey) = rsa.newkeys(1024)
    with open('security/keys/publicKey.pem', 'wb') as p:
        p.write(publicKey.save_pkcs1('PEM'))
    with open('security/keys/privateKey.pem', 'wb') as p:
        p.write(privateKey.save_pkcs1('PEM'))
