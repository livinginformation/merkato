import hashlib
import hmac
import json
import math
import requests
import time
import urllib.parse
from merkato.exchanges.test_exchange.utils import apply_resolved_orders
from merkato.exchanges.exchange_base import ExchangeBase
from merkato.constants import BUY, SELL
from merkato.exchanges.test_exchange.orderbook import Orderbook

DEBUG = True

class TestExchange(ExchangeBase):
    def __init__(self, config, coin, base, user_id):
        self.coin = coin
        self.base = base
        self.ticker = translate_ticker(coin=coin, base=base)
        self.orderbook = Orderbook()
        self.user_id = user_id
        self.user_accounts = {}

    def debug(self, level, header, *args):
        if level <= self.DEBUG:
            print("-"*10)
            print("{}---> {}:".format(level, header))
            for arg in args:
                print("\t\t" + repr(arg))
            print("-" * 10)

    def _sell(self, amount, ask,):
        newAccounts = self.orderbook.addAsk(self.user_id, amount, ask)
        apply_resolved_orders(self.user_accounts, newAccounts)

    def sell(self, amount, ask):
        attempt = 0
        while attempt < self.retries:
            if self.limit_only:
                # Get current highest bid on the orderbook
                # If ask price is lower than the highest bid, return.
                if self.get_highest_bid() > ask:
                    self.debug(1, "sell","SELL {} {} at {} on {} FAILED - would make a market order.".format(amount, ticker, ask, "tux"))
                    return False # Maybe needs failed or something
            try:
                self._sell(amount, ask)
            except Exception as e:  # TODO - too broad exception handling
                self.debug(0, "sell", "ERROR", e)
                break

                
    def _buy(self, amount, bid):
        newAccounts = self.orderbook.addBid(self.user_id, amount, bid)
        apply_resolved_orders(self.user_accounts, newAccounts)

    def buy(self, amount, bid):
        attempt = 0
        while attempt < self.retries:
            if self.limit_only:
                # Get current lowest ask on the orderbook
                # If bid price is higher than the lowest ask, return.
                if self.get_lowest_ask() < bid:
                    
                    self.debug(1, "buy", "BUY {} {} at {} on {} FAILED - would make a market order.".format(amount, self.ticker, bid, "tux"))
                    return False # Maybe needs failed or something
            try:
                self._buy(amount, bid)
            except Exception as e:  # TODO - too broad exception handling
                self.debug(0, "buy", "ERROR", e)
                return False

    def get_order_history(self, user_id):
        pass

    def get_all_orders(self):
        ''' Returns all open orders for the ticker XYZ (not BTC_XYZ)
            :param coin: string
        '''
        # TODO: Accept BTC_XYZ by stripping BTC_ if it exists

        params = {"method": "getorders", "coin": self.coin}
        response = requests.get(self.url, params=params)

        response_json = json.loads(response.text)
        if DEBUG: print(response_json)
        return response_json


    def get_my_open_orders(self):
        ''' Returns all open orders for the authenticated user '''

        query_parameters = { "method": "getmyopenorders" }

        return self._create_signed_request(query_parameters)


    def cancel_order(self, order_id):
        ''' Cancels the order with the specified order ID
            :param order_id: string
        '''

        if DEBUG: print("--> Cancelling order...")

        if order_id == 0:
            if DEBUG: print("---> Order ID was zero, so bailing on function...")
            return False

        query_parameters = {
            "method": "cancelorder",
            "market": self.base,
            "id": order_id
        }
        return self._create_signed_request(query_parameters)


    def get_ticker(self, coin=None):
        ''' Returns the current ticker data for the given coin. If no coin is given,
            it will return the ticker data for all coins.
            :param coin: string (of the format BTC_XYZ)
        '''

        params = { "method": "getticker" }
        response = requests.get(self.url, params=params)

        if not coin:
            return json.loads(response.text)

        response_json = json.loads(response.text)
        print(response_json[coin])
        return response_json[coin]


    def get_24h_volume(self, coin=None):
        ''' Returns the 24 hour volume for the given coin.
            If no coin is given, returns for all coins.
            :param coin string (of the form BTC_XYZ where XYZ is the alt ticker)
        '''

        params = { "method": "get24hvolume" }
        response = requests.get(self.url, params=params)

        if not coin:
            return json.loads(response.text)

        response_json = json.loads(response.text)
        print(response_json[coin])
        return response_json[coin]


    def get_balances(self):
        # also keys go unused, also coin...
        tuxParams = {"method" : "getmybalances"}

        response = self._create_signed_request(tuxParams)
        print(response)
        for crypto in response:
                print(str(crypto) + ": " + str(response[crypto]))
        pair_balances = {"base" : {"amount": response[self.base],
                                   "name" : self.base},
                         "coin": {"amount": response[self.coin],
                                  "name": self.coin},
                        }
        
        return pair_balances

    def get_last_trade_price(self):
        return self.get_ticker(self.ticker)["last"]

    def get_lowest_ask(self):
        return self.orderbook.asks[0]

    def get_highest_bid(self):
        return self.orderbook.bids[0]
