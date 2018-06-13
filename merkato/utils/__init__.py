import json
from merkato.exchanges.test_exchange.exchange import TestExchange
from merkato.exchanges.tux_exchange.exchange import TuxExchange
from merkato.constants import known_exchanges
from merkato.utils.database_utils import get_exchange as get_exchange_from_db, get_merkatos_by_exchange, get_merkato
import base64
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto import Random


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


def update_config_with_credentials(config):
    print("API Credentials needed")
    public_key  = input("Public Key: ")
    private_key = input("Private Key: ")
    config['public_api_key'] = public_key
    config['private_api_key'] = private_key


def get_exchange():
    print("What exchange is this config file for?")
    print("1. for TuxExchange type 'tux'")
    print("2. for Poloniex type 'polo'")
    print("3. for Bittrex type 'bit'")
    print("3. for TestExchange type 'test'")
    selection = input("Selection: ")
    if selection not in known_exchanges:
        print('selected exchange not supported, try again')
        return get_exchange()
    return selection


def get_config_selection():
    print("Please make a selection:")
    print("1 -> Create new configuration")
    print("2 -> Load existing configuration")
    print("3 -> Exit")
    return input("Selection: ")

def create_price_data(orders, order):
    price_data             = {}
    price_data['total']    = float(orders[order]["total"])
    price_data['amount']   = float(orders[order]["amount"])
    price_data['id'] = orders[order]["id"]
    price_data['type']     = orders[order]["type"]
    return price_data

def validate_merkato_initialization(configuration, coin, base, spread):
    if len(configuration) == 4:
        return
    raise ValueError('config does not contain needed values.', configuration)


def get_relevant_exchange(exchange_name):
    exchange_classes = {
        'tux': TuxExchange,
        'test': TestExchange
    }
    return exchange_classes[exchange_name]


def generate_complete_merkato_configs(merkato_tuples):
    merkato_complete_configs = []
    for tuple in merkato_tuples:
        complete_config = {}
        config = {"limit_only": True}
        exchange = get_exchange_from_db(tuple[0])
        
        config['exchange'] = tuple[0]
        config['public_api_key'] = exchange['public_api_key']
        config['private_api_key'] = exchange['private_api_key']

        complete_config['configuration'] = config
        complete_config['base'] = tuple[2]
        complete_config['coin'] = tuple[3]
        complete_config['spread'] = tuple[4]
        complete_config['ask_reserved_balance'] = tuple[7]
        complete_config['bid_reserved_balance'] = tuple[8]
        merkato_complete_configs.append(complete_config)

    return merkato_complete_configs


def get_allocated_pair_balances(exchange, base, coin):
    allocated_pair_balances = {
        'base': 0,
        'coin': 0
    }

    merkatos = get_merkatos_by_exchange(exchange)
    for merkato in merkatos:
        if merkato['base'] == base:
            allocated_pair_balances['base'] += merkato['bid_reserved_balance']

        if merkato['alt'] == coin:
            allocated_pair_balances['coin'] += merkato['ask_reserved_balance']
    return allocated_pair_balances


def check_reserve_balances(total_balances, allocated_balances, coin_reserve, base_reserve):
    remaining_balances = {
        'base': float(total_balances['base']['amount']['balance']) - allocated_balances['base'],
        'coin': float(total_balances['coin']['amount']['balance']) - allocated_balances['coin']
    }
    print('remaning', remaining_balances, 'base_reserve', base_reserve)
    if remaining_balances['base'] < base_reserve:
        raise ValueError('Cannot create merkato, the suggested base reserve will exceed the amount of the base asset on the exchange.')
    if remaining_balances['coin'] < coin_reserve:
        raise ValueError('Cannot create merkato, the suggested coin reserve will exceed the amount of the coin asset on the exchange.')


def get_last_order( UUID):
    merkato = get_merkato(UUID)
    last_order = merkato[6]
    print('last order', last_order)
    return last_order


def get_first_order( UUID):
    merkato = get_merkato(UUID)
    first_order = merkato[7]
    print('first order', first_order)
    return first_order


def get_new_history(current_history, last_order):
    for index, order in enumerate(current_history):
        print('orderId', order['orderId'], 'last_order', last_order)
        is_last_order = order['orderId'] == last_order
        if is_last_order:
            return current_history[:index]
    return []