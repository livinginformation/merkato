import urllib.parse
import hmac
import requests
import time
import hashlib
import base64
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto import Random

def getQueryParameters(type, ticker, amount, price):
    formatted_amount = "{:.8f}".format(float(amount))
    formatted_price = "{:.8f}".format(float(price))
    print('ticker', ticker)
    return {
        "method": type,
        "market": "BTC",
        "coin": ticker,
        "amount": formatted_amount,
        "price": formatted_price,
    }

def validate_credentials(config, url):
    query_parameters = { "method": "getmyopenorders" }
    nonce = int(time.time() * 1000)
    timeout=15

    query_parameters.update({"nonce": nonce})
    post = urllib.parse.urlencode(query_parameters)


    signature = hmac.new(config['private_api_key'].encode('utf-8'), post.encode('utf-8'), hashlib.sha512).hexdigest()
    head = {'Key': config['public_api_key'], 'Sign': signature}

    request = requests.post(url, data=query_parameters, headers=head, timeout=timeout).json()
    return 'error' not in request

def translate_ticker(coin, base):
    if base == "BTC":
        if coin == "ZEC":
            return "BTC_ZEC"
        if coin == "PPC":
            return "BTC_PPC"
        if coin == "EMC":
            return "BTC_EMC"
        if coin == "ICN":
            return "BTC_ICN"
        if coin == "POT":
            return "BTC_POT"
        if coin == "NMC":
            return "BTC_NMC"
        if coin == "DOGE":
            return "BTC_DOGE"
        if coin == "BCY":
            return "BTC_BCY"
        if coin == "LTC":
            return "BTC_LTC"
        if coin == "DASH":
            return "BTC_DASH"
        if coin == "ETH":
            return "BTC_ETH"
        if coin == "BLK":
            return "BTC_BLK"
        if coin == "DTB":
            return "BTC_DTB"
        if coin == "DCR":
            return "BTC_DCR"
        if coin == "GNT":
            return "BTC_GNT"
        if coin == "PEPECASH":
            return "BTC_PEPECASH"
        if coin == "SYS":
            return "BTC_SYS"
        if coin == "XCP":
            return "BTC_XCP"
        if coin == "XMR":
            return "BTC_XMR"

    raise NotImplementedError("Unknown pair: coin={}, base={}".format(coin, base))
    
def encrypt(key, source, encode=True):
    key = SHA256.new(key).digest()  # use SHA-256 over our key to get a proper-sized AES key
    IV = Random.new().read(AES.block_size)  # generate IV
    encryptor = AES.new(key, AES.MODE_CBC, IV)
    padding = AES.block_size - len(source) % AES.block_size  # calculate needed padding
    source += bytes([padding]) * padding  # Python 2.x: source += chr(padding) * padding
    data = IV + encryptor.encrypt(source)  # store the IV at the beginning and encrypt
    return base64.b64encode(data).decode("latin-1") if encode else data

def decrypt(key, source, decode=True):
    if decode:
        source = base64.b64decode(source.encode("latin-1"))
    key = SHA256.new(key).digest()  # use SHA-256 over our key to get a proper-sized AES key
    IV = source[:AES.block_size]  # extract the IV from the beginning
    decryptor = AES.new(key, AES.MODE_CBC, IV)
    data = decryptor.decrypt(source[AES.block_size:])  # decrypt
    padding = data[-1]  # pick the padding value from the end; Python 2.x: ord(data[-1])
    if data[-padding:] != bytes([padding]) * padding:  # Python 2.x: chr(padding) * padding
        raise ValueError("Invalid padding...")
    return data[:-padding]  # remove the padding
