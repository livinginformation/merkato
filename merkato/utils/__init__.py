import logging
from merkato.exchanges.test_exchange.exchange import TestExchange
from merkato.exchanges.tux_exchange.exchange import TuxExchange
from merkato.exchanges.binance_exchange.exchange import BinanceExchange
from merkato.constants import known_exchanges
from merkato.utils.database_utils import get_exchange as get_exchange_from_db, get_merkatos_by_exchange, get_merkato
import base64
import time
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

salt = 'merkato'

def encrypt(password, source):
    kdf = PBKDF2HMAC(
      algorithm=hashes.SHA256(),
      length=32,
      salt=salt.encode(),
      iterations=10,
      backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(password))
    cipher_suite = Fernet(key)
    cipher_text = cipher_suite.encrypt(source)
    return cipher_text


def decrypt(password, source):
    kdf = PBKDF2HMAC(
      algorithm=hashes.SHA256(),
      length=32,
      salt=salt.encode(),
      iterations=10,
      backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(password))
    cipher_suite = Fernet(key)
    plain_text = cipher_suite.decrypt(source)
    return plain_text


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
    print("4. for BinanceExchange type 'bina'")
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
        'test': TestExchange,
        'bina': BinanceExchange
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
            allocated_pair_balances['base'] += merkato['base_partials_balance']

        if merkato['alt'] == coin:
            allocated_pair_balances['coin'] += merkato['ask_reserved_balance']
            allocated_pair_balances['coin'] += merkato['quote_partials_balance']

    return allocated_pair_balances


def check_reserve_balances(total_balances, allocated_balances, coin_reserve, base_reserve):
    remaining_balances = {
        'base': float(total_balances['base']['amount']['balance']) - allocated_balances['base'],
        'coin': float(total_balances['coin']['amount']['balance']) - allocated_balances['coin']
    }

    if remaining_balances['base'] < base_reserve:
        return False
        # raise ValueError('Cannot create merkato, the suggested base reserve will exceed the amount of the base asset on the exchange.')
    if remaining_balances['coin'] < coin_reserve:
        return False
        #raise ValueError('Cannot create merkato, the suggested coin reserve will exceed the amount of the coin asset on the exchange.')
    return True


def get_last_order( UUID):
    merkato = get_merkato(UUID)
    last_order = merkato[6]
    return last_order


def get_first_order( UUID):
    merkato = get_merkato(UUID)
    first_order = merkato[7]
    return first_order


def get_new_history(current_history, last_order):
    for index, order in enumerate(current_history):
        is_last_order = str(order['id']) == str(last_order)
        if is_last_order:
            new_history = current_history[:index]
            new_history.reverse() # need to reverse due to the newest order at start of the list, we want oldest
            return new_history
    return []

def get_time_of_last_order(ordered_transactions):
    index_of_last_tx = len(ordered_transactions) -1
    last_tx_data = ordered_transactions[index_of_last_tx]['date']
    pattern = '%Y-%m-%d %H:%M:%S'
    epoch = int(time.mktime(time.strptime(last_tx_data, pattern)))
    return epoch

def get_market_results(history): 
    results = {
        'amount_executed': 0, # This is in the quote asset
        'initial_amount': 0, # This is in the base asset
        'price_numerator': 0
    }
    print('get market reseults', history)
    for order in history:
        results['amount_executed'] += float(order['amount'])
        results['initial_amount'] += float(order['initamount'])
        results['price_numerator'] += float(order['amount']) * float(order['price'])
    results['last_txid'] = history[-1]['id']
    results['price_numerator'] /= results['amount_executed']
    return results

def ensure_bytes(password, public_key, private_key):
    if isinstance(password, str):
        password = password.encode('utf-8')
    if isinstance(public_key, str):
        public_key = public_key.encode('utf-8')
    if isinstance(private_key, str):
        private_key = private_key.encode('utf-8')
    return (password, public_key, private_key)


def log_on_call(f):
    def wrapped(self, *args, **kwargs):
        log = logging.getLogger()
        log.debug("Entering {}".format(f.__name__))
        return f(self, *args, **kwargs)
    return wrapped


def log_all_methods(cls):
    for name in cls.__dict__:
        attr = getattr(cls, name)
        if callable(attr):
            setattr(cls, name, log_on_call(attr))
    return cls



