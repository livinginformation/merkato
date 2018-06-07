# Merkato Configuration

import json
import os.path
from merkato.utils.database_utils import get_exchange,insert_exchange, no_exchanges_table_exists, create_exchanges_table, get_exchange as get_exchange_from_db
from merkato.exchanges.tux_exchange.utils import validate_credentials
from merkato.constants import EXCHANGE
from merkato.utils import update_config_with_credentials, get_exchange, get_config_selection

def load_config():
    # Loads an existing configuration file
    # Returns a dictionary
    exchange_name = input("what is the exchange name? ")
    return get_exchange_from_db(exchange_name)
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

        if exchange == 'tux':
            config[EXCHANGE] = 'tux'

            update_config_with_credentials(config)
            credentials_are_valid = validate_credentials(config, url)
            print('credentials_are_valid', credentials_are_valid)
            while not credentials_are_valid:
                config = update_config_with_credentials(config)
                credentials_are_valid = validate_credentials(config, url)
            insert_config_into_exchanges(config)
            return config
        
        elif exchange == 'test':
            config[EXCHANGE] = 'test'
            update_config_with_credentials(config)
            insert_config_into_exchanges(config)
            return config

        elif exchange == 'polo':
            print("Currently Unsupported")
            continue

        elif exchange == 'bit':
            print("Currently Unsupported")
            continue

        else:
            print("Unrecognized Selection")
            continue


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
            return config

        elif selection == '3':
            # Exit
            return {}

        else:
            print("Unrecognized input.")
