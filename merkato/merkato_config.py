# Merkato Configuration

import json
import os.path
from utils import update_config_with_credentials, get_exchange, get_config_selection

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
    config = {}
    while True:
        filename = input("Config file name? ")

        if os.path.isfile("./"+filename):
            print("Config already exists.")
            continue

        exchange = get_exchange()

        if exchange == '1':
            config['exchange'] = 'tux'

            # Eventually break this part out into its own function
            update_config_with_credentials(config)

            with open("./"+filename, "w+") as file:
                 json.dump(config, file)
                 print("written")
                 return config

        elif exchange == '2':
            print("Currently Unsupported")
            continue

        elif exchange == '3':
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
