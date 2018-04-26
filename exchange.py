import requests
import urllib.parse
import time
import math
import hashlib
import hmac
import json
import sqlite3
from utils.utils import get_ticker, get_24h_volume, get_orders, get_balances
from constants import *

DEBUG = True

class Exchange:
    '''Merkato Market Making Bot Exchange Interface'''
    def __init__(self, configuration):
        self.privatekey = configuration['privatekey']
        self.publickey  = configuration['publickey']
        self.exchange   = configuration['exchange']


    def debug(self, level, header, *args):
        if level <= self.DEBUG:
            print("-"*10)
            print("{}---> {}:".format(level, header))
            for arg in args:
                print("\t\t" + repr(arg))
            print("-" * 10)


    def _create_signed_request(self, query_parameters, nonce=None, timeout=15):
        # return response needing signature, nonce created if not supplied
        if not nonce:
            nonce = int(time.time() * 1000)

        query_parameters.update({"nonce": nonce})
        post = urllib.parse.urlencode(query_parameters)

        signature = hmac.new(self.privatekey.encode('utf-8'), post.encode('utf-8'), hashlib.sha512).hexdigest()
        head = {'Key': self.publickey, 'Sign': signature}

        response = requests.post(self.api, data=query_parameters, headers=head, timeout=timeout).json()
        return response


    def _sell_tux(self, amount, ask, ticker):
        ''' Places a sell for a number of an asset at the indicated price (0.00000503 for example)

        Amount and ask are floats, ticker is a string

        Todo: Take arguments of other types, convert to applicable ones.
        '''
        while True:
            try:
                if DEBUG: print("--> Selling...")

                query_parameters = { "method": "sell", "market": "BTC", "coin": ticker, "amount": "{:.8f}".format(amount), "price": "{:.8f}".format(ask), "nonce": int(time.time()*1000) }
                response = self._create_signed_request(query_parameters)


                if response['success'] != 0:
                    if DEBUG: print("--> SELL INFO: Tuxexchange ask placed.")
                    return response['success']

                print("--> SELL ERROR: Tuxexchange ask failed. Retrying.")
                time.sleep(5)
            except:
                print("ERROR")


    def sell(self, amount, ask, ticker):
        ''' Places a sell for a number of an asset at the indicated price (0.00000503 for example)

        Amount and ask are floats, ticker is a string

        Todo: Take arguments of other types, convert to applicable ones.
        '''
        if self.exchange == "tux":
            return self._sell_tux(amount, ask, ticker)

        else:
            print("Exchange currently not supported.")


    def _buy_tux(self, amount, bid, ticker):
        # Places a buy for a number of an asset, at the
        # indicated price (0.00000503 for example)
        #
        # Amount and bid are floats, ticker is a string
        #
        # Todo: Take arguments of other types, convert to applicable ones.
        while True:
            try:
                if DEBUG: print("--> Buying...")
                query_parameters = { "method": "buy", "market": "BTC", "coin": ticker, "amount": "{:.8f}".format(amount), "price": "{:.8f}".format(bid), "nonce": int(time.time()*1000) }
                response = self._create_signed_request(query_parameters)

                if response['success'] != 0:
                    if DEBUG: print("--> BUY INFO: Tuxexchange bid placed.")
                    return response['success'] # ID of the new order

                print("--> BUY ERROR: Tuxexchange bid failed. Retrying.")
                time.sleep(5) # Wait to prevent flooding
            except:
                print("ERROR")


    def buy(self, amount, bid, ticker):
        if self.exchange == "tux":
            return self._buy_tux(amount, bid, ticker)

        else:
            print("Exchange currently not supported.")


    def _getmyopenorders_tux(self):
        while True:

            try:
                if DEBUG: print("--> Getting open orders...")

                query_parameters = { "method": "getmyopenorders", "nonce": int(time.time()*1000) }

                return self._create_signed_request(query_parameters)

            except:
                print("ERROR")


    def getmyopenorders(self):
        if self.exchange == "tux":
            return self._getmyopenorders_tux()

        else:
            print("Exchange currently not supported")


    def _getmytradehistory_tux(self, start=0, end=0):
        while True:
            try:
                if DEBUG: print("--> Getting trade history...")

                if start != 0 and end != 0:
                    query_parameters = { "method": "getmytradehistory", "start": start, "end": end, "nonce": int(time.time()*1000) }
                else:
                    query_parameters = { "method": "getmytradehistory", "nonce": int(time.time()*1000) }
                
                return self._create_signed_request(query_parameters)
            except:
                print("ERROR")


    def getmytradehistory(self, start=0, end=0):
        if self.exchange == "tux":
            return self._getmytradehistory_tux(start, end)

        else:
            print("Exchange currently not supported.")


    def _cancelorder_tux(self, order_id):
        # This function has a stack overflow risk, fix it. Don't use tail recursion.
        try:
            if DEBUG: print("--> Cancelling order...")

            if order_id == 0:
                if DEBUG: print("---> Order ID was zero, so bailing on function...")
                return

            query_parameters = { "method": "cancelorder", "market": "BTC", "id": order_id, "nonce": int(time.time()*1000) }
            response = self._create_signed_request(query_parameters)

            if response['success'] != 0:
                if DEBUG: print("--> Cancel successful")
                return True

            print("--> Cancel error, retrying   ")
            return self.cancelorder(order_id)
        except:
            print("ERROR")


    def cancelorder(self, order_id):
        if self.exchange == "tux":
            return self._cancelorder_tux(order_id)

        else:
            print("Exchange currently not supported.")

