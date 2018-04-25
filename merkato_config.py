# Merkato Configuration

import json
import os.path
from utils import updateConfigWithCredentials, getExchange, getConfigSelection

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

        exchange = getExchange()

        if exchange == '1':
            config['exchange'] = 'tux'

            # Eventually break this part out into its own function
            updateConfigWithCredentials(config)

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

        selection = getConfigSelection()
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
