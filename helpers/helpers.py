import os
import json
import inspect
from Crypto.Cipher import AES
import binascii
import pdb
from helpers.aes import aes_encrypt, aes_decrypt

# pdb.set_trace()


def secrets(keys, file='.secrets.json'):
    dirname = os.getcwd()
    filename = os.path.join(dirname, file)
    config = json.loads(open(filename).read())
    if keys in config.keys():
        return aes_decrypt(config[keys])
    else:
        return False


def secretsD(keys, file='.secrets.json'):
    dirname = os.getcwd()
    filename = os.path.join(dirname, file)
    config = json.loads(open(filename).read())
    if keys in config.keys():
        return config[keys]
    else:
        return False
