# Merkato Configuration

import json
import os.path
from merkato.utils.database_utils import get_exchange,insert_exchange, no_exchanges_table_exists, create_exchanges_table, get_exchange as get_exchange_from_db
from merkato.exchanges.tux_exchange.utils import validate_credentials
from merkato.exchanges.binance_exchange.utils import validate_keys
from merkato.constants import EXCHANGE
from merkato.utils import update_config_with_credentials, get_exchange, get_config_selection, encrypt, decrypt, ensure_bytes
import getpass

def load_config():
    # Loads an existing configuration file
    # Returns a dictionary
    exchange_name = input("what is the exchange name? ")
    exchange = get_exchange_from_db(exchange_name)
    decrypt_keys(exchange)
    return exchange
    # TODO: Error handling and config validation


def insert_config_into_exchanges(config):
    limit_only = config["limit_only"]
    public_key = config["public_api_key"]
    private_key = config["private_api_key"]
    exchange = config["exchange"]

    if no_exchanges_table_exists():
        create_exchanges_table()

    insert_exchange(exchange, public_key, private_key, limit_only)


def create_config():
    # Create new config
    config = { "limit_only": True }
    url = "https://tuxexchange.com/api"

    while True:
        exchange = get_exchange()
        config[EXCHANGE] = exchange

        if exchange == 'tux':
            update_config_with_credentials(config)
            credentials_are_valid = validate_credentials(config)
            print('credentials_are_valid', credentials_are_valid)

            while not credentials_are_valid:
                update_config_with_credentials(config)
                credentials_are_valid = validate_credentials(config)

            encrypt_keys(config)
            insert_config_into_exchanges(config)
            decrypt_keys(config)
            return config
        
        elif exchange == 'test':
            config[EXCHANGE] = 'test'
            update_config_with_credentials(config)
            encrypt_keys(config)
            insert_config_into_exchanges(config)
            return config

        elif exchange == 'polo':
            print("Currently Unsupported")
            continue

        elif exchange == 'bit':
            print("Currently Unsupported")
            continue
        
        elif exchange == 'bina':
            update_config_with_credentials(config)
            credentials_are_valid = validate_keys(config, url)
            print('credentials_are_valid', credentials_are_valid)

            while not credentials_are_valid:
                update_config_with_credentials(config)
                credentials_are_valid = validate_keys(config, url)

            encrypt_keys(config)
            insert_config_into_exchanges(config)
            decrypt_keys(config)
            return config

        else:
            print("Unrecognized Selection")
            continue


def encrypt_keys(config, password=None):
    ''' Encrypts the API keys before storing the config in the database
    '''
    public_key  = config["public_api_key"]
    private_key = config["private_api_key"]

    if password is None:
        password = getpass.getpass("\n\ndatabase password:") # Prompt user for password / get password from Nasa. This should be a popup?

    password, public_key, private_key = ensure_bytes(password, public_key, private_key)

    # encrypt(password, data)
    # Inputs are of type:
    # - password: bytes
    # - data:     bytes

    public_key_encrypted  = encrypt(password, public_key)
    private_key_encrypted = encrypt(password, private_key)
    config["public_api_key"]  = public_key_encrypted
    config["private_api_key"] = private_key_encrypted
    return config


def decrypt_keys(config, password=None):
    ''' Decrypts the API keys before storing the config in the database
    '''
    public_key  = config["public_api_key"]
    private_key = config["private_api_key"]

    if password is None:
        password = getpass.getpass("\n\ndatabase password:") # Prompt user for password / get password from Nasa. This should be a popup?

    password, public_key, private_key = ensure_bytes(password, public_key, private_key)

    # decrypt(password, data)
    # Inputs are of type:
    # - password: bytes
    # - data:     bytes

    public_key_decrypted  = decrypt(password, public_key)
    private_key_decrypted = decrypt(password, private_key)
    config["public_api_key"]  = public_key_decrypted.decode('utf-8')
    config["private_api_key"] = private_key_decrypted.decode('utf-8')

    return config

def decrypt_merkato(merkato, password=None):
    ''' Decrypts the API keys inside a merkato dict before storing the config in the database
    '''
    decrypt_keys(merkato["configuration"], password)
    return merkato


def get_config():
    while True:

        selection = get_config_selection()
        if selection =='1':
            # Create new config
            config = create_config()
            return config

        elif selection == '2':
            # Load existing config
            config = load_config()
            # decrypt_passwords(config)
            return config

        elif selection == '3':
            # Exit
            return {}

        else:
            print("Unrecognized input.")
