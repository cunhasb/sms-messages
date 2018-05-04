import os
import json
import inspect
from Crypto.Cipher import AES
import binascii
import pdb
from helpers.aes import aes_encrypt, aes_decrypt

# pdb.set_trace()


def setEnvironVariables():
    os.environ['DATABASE_URL'] = secretsD('dbUri')
    os.environ['SECRET'] = secrets('secret')
    os.environ['SALT'] = secrets('salt')


def secrets(key, file='.secrets.json'):
    dirname = os.getcwd()
    filename = os.path.join(dirname, file)
    config = json.loads(open(filename).read())
    # pdb.set_trace()
    if key in config.keys():
        return aes_decrypt(config[key])
    else:
        return False


def secretsD(key, file='.secrets.json'):
    dirname = os.getcwd()
    filename = os.path.join(dirname, file)
    config = json.loads(open(filename).read())
    # pdb.set_trace()
    if key in config.keys():
        return config[key]
    else:
        return False
