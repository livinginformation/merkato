import json
import os.path

config = {}


def menu():
    while True:

        print("Please make a selection:")
        print("1. Load existing config")
        print("2. Create new config")
        print("3. Exit")

        selection = raw_input("Selection: ")
        if selection =='1':
            # Load existing config
            pass

        elif selection == '2':
            # Create new config

            filename = raw_input("Config file name? ")

            if os.path.isfile("./"+filename):
                print("Config already exists.")
                continue

            print("What exchange is this config file for?")
            print("1. TuxExchange")
            print("2. Poloniex")
            print("3. Bittrex")
            exchange = raw_input("Selection: ")

            if exchange == '1':
                config['exchange'] = 'tux'

                print("API Credentials needed")
                public_key  = raw_input("Public Key: ")
                private_key = raw_input("Private Key: ")
                config['publickey'] = public_key
                config['privatekey'] = private_key

                with open("./"+filename, "w+") as file:
                     json.dump(config, file)
                     print("written, exiting")
                     return

            elif exchange == '2':
                print("Currently Unsupported1")
                continue

            elif exchange == '3':
                print("Currently Unsupported2")
                continue

            else:
               print("Unrecognized Selection")
               continue

        elif selection == '3':
            # Exit
            break

        else:
            print("Unrecognized input.")


menu()
