# Merkato Configuration

import json
import os.path
from merkato.utils import write_to_file, update_config_with_credentials, get_exchange, get_config_selection

def load_config():
    # Loads an existing configuration file
    # Returns a dictionary

    while True:
        filename = input("Config file name? ")

        if not os.path.isfile("./"+filename):
            print("File doesn't exist.")
            continue

        with open("./"+filename) as configuration:
            data = json.load(configuration)

        # TODO: Error handling and config validation

        return data


def create_config():
    # Create new config
    config = { "limit_only": True }
    while True:
        filename = input("Config file name? ")

        if os.path.isfile("./"+filename):
            print("Config already exists.")
            continue

        exchange = get_exchange()

        if exchange == 'tux':
            config['exchange'] = 'tux'

            update_config_with_credentials(config)
            write_to_file(filename, config)
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
