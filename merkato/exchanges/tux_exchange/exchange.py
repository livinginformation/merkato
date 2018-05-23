import hashlib
import hmac
import json
import math
import requests
import time
import urllib.parse
from merkato.exchanges.tux_exchange.utils import getQueryParameters, translate_ticker
from merkato.exchanges.exchange_base import ExchangeBase
from merkato.constants import BUY, SELL


class TuxExchange(ExchangeBase):
    url = "https://tuxexchange.com/api"

    def __init__(self, config, coin, base):
        self.privatekey = config['privatekey']
        self.publickey  = config['publickey']
        self.limit_only = config['limit_only']
        self.retries = 5
        self.coin = coin
        self.base = base
        self.ticker = translate_ticker(coin=coin, base=base)
        self.name = 'tux'

    def debug(self, level, header, *args):
        if level <= self.DEBUG:
            print("-"*10)
            print("{}---> {}:".format(level, header))

            for arg in args:
                print("\t\t" + repr(arg))

            print("-" * 10)


    def _sell(self, amount, ask,):
        ''' Places a sell for a number of an asset at the indicated price (0.00000503 for example)
            :param amount: string
            :param ask: float
            :param ticker: string
        '''
        query_parameters = getQueryParameters(SELL, self.ticker, amount, ask)
        response = self._create_signed_request(query_parameters)

        return response['success']


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
                success = self._sell(amount, ask)

                if success:
                    self.debug(2, "sell", "SELL {} {} at {} on {}".format(amount, self.ticker, ask, "tux"))
                    return success

                else:
                    self.debug(1, "sell","SELL {} {} at {} on {} FAILED - attempt {} of {}".format(amount, ticker, ask, "tux", attempt, self.retries))
                    attempt += 1
                    time.sleep(5)

            except Exception as e:  # TODO - too broad exception handling
                self.debug(0, "sell", "ERROR", e)
                break


    def _buy(self, amount, bid):
        ''' Places a buy for a number of an asset at the indicated price (0.00000503 for example)
            :param amount: string
            :param bid: float
            :param ticker: string
        '''
        query_parameters = getQueryParameters(BUY, self.ticker, amount, bid)
        response = self._create_signed_request(query_parameters)

        return response['success']


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
                success = self._buy(amount, bid)

                if success:
                    self.debug(2, "buy", "BUY {} {} at {} on {}".format(amount, self.ticker, bid, "tux"))
                    return success

                else:
                    self.debug(1, "buy", "BUY {} {} at {} on {} FAILED - attempt {} of {}".format(amount, self.ticker, bid, "tux", attempt, self.retries))
                    attempt += 1
                    time.sleep(5)

            except Exception as e:  # TODO - too broad exception handling
                self.debug(0, "buy", "ERROR", e)
                return False


    def get_all_orders(self):
        ''' Returns all open orders for the ticker XYZ (not BTC_XYZ)
            :param coin: string
        '''
        # TODO: Accept BTC_XYZ by stripping BTC_ if it exists

        params = {"method": "getorders", "coin": self.coin}
        response = requests.get(self.url, params=params)

        response_json = json.loads(response.text)
        self.debug(10, "get_all_orders", response.text)

        return response_json


    def get_my_open_orders(self):
        ''' Returns all open orders for the authenticated user '''

        query_parameters = { "method": "getmyopenorders" }

        return self._create_signed_request(query_parameters)


    def cancel_order(self, order_id):
        ''' Cancels the order with the specified order ID
            :param order_id: string
        '''

        self.debug(10, "cancel_order","---> cancelling order")


        if order_id == 0:
            self.debug(3, "cancel_order","---> Order ID was zero, bailing")

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
        self.debug(10, "get_ticker", response_json[coin])

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
        self.debug(10, "get_24h_volume", response_json[coin])

        return response_json[coin]


    def get_balances(self):
        ''' TODO Function Definition
        '''

        # also keys go unused, also coin...
        tuxParams = {"method" : "getmybalances"}

        response = self._create_signed_request(tuxParams)
        self.debug(10, "get_balances", response)

        pair_balances = {"base" : {"amount": response[self.base],
                                   "name" : self.base},
                         "coin": {"amount": response[self.coin],
                                  "name": self.coin},
                        }

        return pair_balances


    def get_my_trade_history(self, start=0, end=0):
        ''' TODO Function Definition
        '''
        self.debug(10, "get_my_trade_history","---> Getting trade history...")

        query_parameters = { "method": "getmytradehistory" }

        if start != 0 and end != 0:
            query_parameters["start"] = start
            query_parameters["end"] = end

        return self._create_signed_request(query_parameters)


    def get_last_trade_price(self):
        ''' TODO Function Definition
        '''
        return self.get_ticker(self.ticker)["last"]


    def get_lowest_ask(self):
        ''' TODO Function Definition
        '''
        return self.get_ticker(self.ticker)["lowestAsk"]


    def get_highest_bid(self):
        ''' TODO Function Definition
        '''
        return self.get_ticker(self.ticker)["highestBid"]


    def _create_signed_request(self, query_parameters, nonce=None, timeout=15):
        ''' Signs provided query parameters with API keys
            :param query_parameters: dictionary
            :param nonce: int
            :param timeout: int
        '''

        # return response needing signature, nonce created if not supplied
        if not nonce:
            nonce = int(time.time() * 1000)

        query_parameters.update({"nonce": nonce})
        post = urllib.parse.urlencode(query_parameters)

        signature = hmac.new(self.privatekey.encode('utf-8'), post.encode('utf-8'), hashlib.sha512).hexdigest()
        head = {'Key': self.publickey, 'Sign': signature}

        response = requests.post(self.url, data=query_parameters, headers=head, timeout=timeout).json()
        return response
