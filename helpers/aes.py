import os
import json
import inspect
from Crypto.Cipher import AES
import binascii
import pdb


def getSalt(file='.aes.json'):

    dirname = os.getcwd()
    filename = os.path.join(dirname, file)
    config = json.loads(open(filename).read())
    return config['salt']


def aes_encrypt(data):
    cipher = AES.new(getSalt())
    data = data + (" " * (16 - (len(data) % 16)))
    return binascii.hexlify(cipher.encrypt(data)).decode('ascii')


def aes_decrypt(data):
    cipher = AES.new(getSalt())
    return cipher.decrypt(binascii.unhexlify(data)).rstrip().decode('ascii')
