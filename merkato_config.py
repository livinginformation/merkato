# Merkato Configuration

import json
import os.path


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

        print("What exchange is this config file for?")
        print("1. TuxExchange")
        print("2. Poloniex")
        print("3. Bittrex")
        exchange = input("Selection: ")

        if exchange == '1':
            config['exchange'] = 'tux'

            # Eventually break this part out into its own function
            print("API Credentials needed")
            public_key  = input("Public Key: ")
            private_key = input("Private Key: ")
            config['publickey'] = public_key
            config['privatekey'] = private_key

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

        print("Please make a selection:")
        print("1. Create new configuration")
        print("2. Load existing configuration")
        print("3. Exit")

        selection = input("Selection: ")
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
