import hashlib
import hmac
import json
import math
import requests
import time
import urllib.parse
from merkato.exchanges.exchange_base import ExchangeBase
from merkato.constants import BUY, SELL
from binance.client import Client
from binance.enums import *
precision = 5


class BinanceExchange(ExchangeBase):
    url = "https://api.binance.com"

    def __init__(self, config, coin, base, password='password'):
        self.client = Client(config['public_api_key'], config['private_api_key'])
        self.limit_only = config['limit_only']
        print('TuxExchange config', config)
        self.retries = 5
        self.coin = coin
        self.base = base
        self.ticker = coin + base
        self.name = 'bina'
        self.debug = 100
        
    def _debug(self, level, header, *args):
        if level <= self.debug:
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
        amt_str = "{:0.0{}f}".format(amount, precision)
        order = self.client.create_order(
            symbol=self.ticker,
            side=SIDE_SELL,
            type=ORDER_TYPE_LIMIT,
            timeInForce=TIME_IN_FORCE_GTC,
            quantity=amt_str,
            price=ask)

        return order['success']


    def sell(self, amount, ask):
        attempt = 0
        while attempt < self.retries:
            if self.limit_only:
                # Get current highest bid on the orderbook
                # If ask price is lower than the highest bid, return.

                if float(self.get_highest_bid()) > ask:
                    self._debug(1, "sell","SELL {} {} at {} on {} FAILED - would make a market order.".format(amount,self.ticker, ask, "tux"))
                    return False # Maybe needs failed or something

            try:
                success = self._sell(amount, ask)

                if success:
                    self._debug(2, "sell", "SELL {} {} at {} on {}".format(amount, self.ticker, ask, "tux"))
                    return success

                else:
                    self._debug(1, "sell","SELL {} {} at {} on {} FAILED - attempt {} of {}".format(amount, self.ticker, ask, "tux", attempt, self.retries))
                    attempt += 1
                    time.sleep(1)

            except Exception as e:  # TODO - too broad exception handling
                raise ValueError(e)


    def _buy(self, amount, bid):
        ''' Places a buy for a number of an asset at the indicated price (0.00000503 for example)
            :param amount: string
            :param bid: float
            :param ticker: string
        '''
        amt_str = "{:0.0{}f}".format(amount, precision)
        order = self.client.create_order(
            symbol=self.ticker,
            side=SIDE_BUY,
            type=ORDER_TYPE_LIMIT,
            timeInForce=TIME_IN_FORCE_GTC,
            quantity=amt_str,
            price=bid)
        return order


    def buy(self, amount, bid):
        attempt = 0
        bid_amount = amount / bid
        while attempt < self.retries:
            if self.limit_only:
                # Get current lowest ask on the orderbook
                # If bid price is higher than the lowest ask, return.

                if float(self.get_lowest_ask()) < bid:

                    self._debug(1, "buy", "BUY {} {} at {} on {} FAILED - would make a market order.".format(amount, self.ticker, bid, "tux"))
                    return False # Maybe needs failed or something

            try:
                success = self._buy(bid_amount, bid)
                if success:
                    self._debug(2, "buy", "BUY {} {} at {} on {}".format(bid_amount, self.ticker, bid, "tux"))
                    return success

                else:
                    self._debug(1, "buy", "BUY {} {} at {} on {} FAILED - attempt {} of {}".format(amount, self.ticker, bid, "tux", attempt, self.retries))
                    attempt += 1
                    time.sleep(1)

            except Exception as e:  # TODO - too broad exception handling
                raise ValueError(e)


    def get_all_orders(self):
        ''' Returns all open orders for the ticker XYZ (not BTC_XYZ)
            :param coin: string
        '''
        # TODO: Accept BTC_XYZ by stripping BTC_ if it exists

        orders = client.get_order_book(symbol=self.ticker)
        print('get_all_orders', get_all_orders)

        self._debug(10, "get_all_orders", orders)

        return orders


    def get_my_open_orders(self):
        ''' Returns all open orders for the authenticated user '''
                
        orders = self.client.get_open_orders(symbol=self.ticker)
        print('open orders', orders)
        # filtered_orders = {order_id : order for order_id, order in orders.items() if self.ticker in order["market_pair"]}
        # Return orders in standardized format (list of buys/sells)
        # Tux returns {id: {order}, id: {order}, ...}, we want
        # [{order}, {order}, ...]
        return orders


    def cancel_order(self, order_id):
        ''' Cancels the order with the specified order ID
            :param order_id: string
        '''

        self._debug(10, "cancel_order","---> cancelling order")


        if order_id == 0:
            self._debug(3, "cancel_order","---> Order ID was zero, bailing")

            return False

        return self.client.cancel_order(
            symbol=self.ticker    ,
            orderId=order_id)


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
        self._debug(10, "get_ticker", response_json[coin])

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
        self._debug(10, "get_24h_volume", response_json[coin])

        return response_json[coin]


    def get_balances(self):
        ''' TODO Function Definition
        '''

        # also keys go unused, also coin...
        base_balance = self.client.get_asset_balance(asset=self.base)
        coin_balance = self.client.get_asset_balance(asset=self.coin)
        base = float(base_balance['free']) + float(base_balance['locked'])
        coin = float(coin_balance['free']) + float(coin_balance['locked'])

        self._debug(10, "get_balances", base_balance)
        self._debug(10, "get_balances", coin_balance)

        pair_balances = {"base" : {"amount": {'balance': base},
                                   "name" : self.base},
                         "coin": {"amount": {'balance': coin},
                                  "name": self.coin},
                        }

        return pair_balances


    def get_my_trade_history(self, start=0, end=0):
        ''' TODO Function Definition
        '''
        self._debug(10, "get_my_trade_history","---> Getting trade history...")

        trades = self.client.get_my_trades(symbol=self.ticker)

        return trades


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
