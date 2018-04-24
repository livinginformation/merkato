# INSTRUCTIONS
# 
# Put Tuxexchange public/private keys in the API keys section
# Run this program from command line with python 3.

import requests
import urllib.parse
import time
import math
import hashlib
import hmac
import json
import sqlite3
import merkato_config as config
from exchange import Exchange


def main():
    print("Merkato Alpha v0.1.1\n")

    configuration = config.get_config()

    if configuration == "{}":
        print("Failed")

    else:
        print(configuration)
        exchange = Exchange(configuration)

    # Market making range specifications
#    polo_price     = input('What is the price on Poloniex? \n')
#    desired_spread = input('What spread would you like to use? (Recommended .0007-.0015) \n')
#    bid_ladder_min = input('What is the lowest the price could possibly go? (Recommend 0.005) \n') 
#    ask_ladder_max = input('What is the highest price to market make? (Recommend 0.025) \n')
#    total_btc      = input('How much BTC will you use for market making? \n')
#    total_xmr      = input('How much XMR will you use for market making? \n')

#    spread = float(desired_spread)

#    bid_ladder_max = str(float(polo_price) - spread/2)
#    print("Max: " + bid_ladder_max)

#    ask_ladder_min = str(float(polo_price) + spread/2)
#    print("Min: " + ask_ladder_min)

    # Cancel all existing orders
#    cancelrange(bid_ladder_min, ask_ladder_max)

    # Place a bid ladder
#    if float(total_btc) > 0:
#        bid_ladder("XMR", total_btc, bid_ladder_min, bid_ladder_max, '.00004')

    # Place an ask ladder
#    if float(total_xmr) > 0:
#        ask_ladder("XMR", total_xmr, ask_ladder_min, ask_ladder_max, '.00004')

    # Maintain the spread
#    print("Beginning spread maintainence.")
#    maintain_window(spread, "XMR")





if __name__ == '__main__':
    main()
