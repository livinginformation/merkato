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
XMR_AMOUNT_PRECISION = 3
XMR_PRICE_PRECISION = 6

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


    def _sell(self, amount, ask):
        ''' Places a sell for a number of an asset at the indicated price (0.00000503 for example)
            :param amount: string
            :param ask: float
            :param ticker: string
        '''
        amt_str = "{:0.0{}f}".format(amount, XMR_AMOUNT_PRECISION)
        ask_str = "{:0.0{}f}".format(ask, XMR_PRICE_PRECISION)
        order = self.client.create_order(
            symbol=self.ticker,
            side=SIDE_SELL,
            type=ORDER_TYPE_LIMIT,
            timeInForce=TIME_IN_FORCE_GTC,
            quantity=amt_str,
            price=ask_str)

        return order


    def sell(self, amount, ask):
        attempt = 0
        while attempt < self.retries:
            if self.limit_only:
                # Get current highest bid on the orderbook
                # If ask price is lower than the highest bid, return.

                if float(self.get_highest_bid()) > ask:
                    self._debug(1, "sell","SELL {} {} at {} on {} FAILED - would make a market order.".format(amount,self.ticker, ask, "binance"))
                    return False # Maybe needs failed or something

            try:
                success = self._sell(amount, ask)

                if success:
                    self._debug(2, "sell", "SELL {} {} at {} on {}".format(amount, self.ticker, ask, "binance"))
                    return success

                else:
                    self._debug(1, "sell","SELL {} {} at {} on {} FAILED - attempt {} of {}".format(amount, self.ticker, ask, "binance", attempt, self.retries))
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
        amt_str = "{:0.0{}f}".format(amount, XMR_AMOUNT_PRECISION)
        bid_str = "{:0.0{}f}".format(bid, XMR_PRICE_PRECISION)
        print('amt', amt_str)
        print('bid', bid_str)
        info = self.client.get_symbol_info(symbol=self.ticker)
        order = self.client.create_order(
            symbol=self.ticker,
            side=SIDE_BUY,
            type=ORDER_TYPE_LIMIT,
            timeInForce=TIME_IN_FORCE_GTC,
            quantity=amt_str,
            price=bid_str)
        return order


    def buy(self, amount, bid):
        attempt = 0
        bid_amount = amount / bid
        while attempt < self.retries:
            if self.limit_only:
                # Get current lowest ask on the orderbook
                # If bid price is higher than the lowest ask, return.

                if float(self.get_lowest_ask()) < bid:

                    self._debug(1, "buy", "BUY {} {} at {} on {} FAILED - would make a market order.".format(amount, self.ticker, bid, "binance"))
                    return False # Maybe needs failed or something

            try:
                success = self._buy(bid_amount, bid)
                if success:
                    self._debug(2, "buy", "BUY {} {} at {} on {}".format(bid_amount, self.ticker, bid, "binance"))
                    return success

                else:
                    self._debug(1, "buy", "BUY {} {} at {} on {} FAILED - attempt {} of {}".format(amount, self.ticker, bid, "binance", attempt, self.retries))
                    attempt += 1
                    time.sleep(1)

            except Exception as e:  # TODO - too broad exception handling
                raise ValueError(e)

    def market_buy(self, amount, bid):
        attempt = 0
        bid_amount = amount / bid
        while attempt < self.retries:
            try:
                success = self._buy(bid_amount, bid)
                if success:
                    self._debug(2, "buy", "BUY {} {} at {} on {}".format(bid_amount, self.ticker, bid, "binance"))
                    return success

                else:
                    self._debug(1, "buy", "BUY {} {} at {} on {} FAILED - attempt {} of {}".format(amount, self.ticker, bid, "binance", attempt, self.retries))
                    attempt += 1
                    time.sleep(1)

            except Exception as e:  # TODO - too broad exception handling
                raise ValueError(e)

    def market_sell(self, amount, ask):
        attempt = 0
        try:
            success = self._sell(amount, ask)

            if success:
                self._debug(2, "sell", "SELL {} {} at {} on {}".format(amount, self.ticker, ask, "binance"))
                return success

            else:
                self._debug(1, "sell","SELL {} {} at {} on {} FAILED - attempt {} of {}".format(amount, self.ticker, ask, "binance", attempt, self.retries))
                attempt += 1
                time.sleep(1)

        except Exception as e:  # TODO - too broad exception handling
            raise ValueError(e)

    def get_all_orders(self):
        ''' Returns all open orders for the ticker XYZ (not BTC_XYZ)
            :param coin: string
        '''
        # TODO: Accept BTC_XYZ by stripping BTC_ if it exists

        orders = self.client.get_order_book(symbol=self.ticker)

        self._debug(10, "get_all_orders", orders)

        return orders


    def get_my_open_orders(self):
        ''' Returns all open orders for the authenticated user '''
                
        orders = self.client.get_open_orders(symbol=self.ticker)
        # orders is an array of dicts we need to transform it to an dict of dicts to conform to binance
        new_dict = {}
        for order in orders:
            id = order['orderId']
            new_dict[id] = order
            new_dict[id]['id'] = id
        return new_dict


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

        ticker = self.client.get_ticker(symbol=coin)

        # if not coin:
        #     return json.loads(response.text)
        print('tickers', ticker)
        # response_json = json.loads(response.text)
        self._debug(10, "get_ticker", ticker)

        return ticker


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

        trades = self.client.get_my_trades(symbol=self.ticker, fromId=start)
        for trade in trades:
            if trade['isBuyer'] == True:
                trade['type'] = 'buy'
            else:
                trade['type'] = 'sell'
            trade['amount'] = trade['qty']
        return trades


    def get_last_trade_price(self):
        ''' TODO Function Definition
        '''
        return self.get_ticker(self.ticker)["lastPrice"]


    def get_lowest_ask(self):
        ''' TODO Function Definition
        '''
        return self.get_ticker(self.ticker)["askPrice"]


    def get_highest_bid(self):
        ''' TODO Function Definition
        '''
        return self.get_ticker(self.ticker)["bidPrice"]
    
    
    def is_partial_fill(self, order_id): 
        order_info = self.client.get_order(symbol=self.ticker, orderId=order_id)
        amount_placed = float(order_info['origQty'])
        amount_executed = float(order_info['executedQty'])
        return amount_placed > amount_executed and amount_executed > 0

    def get_total_amount(self, order_id):
        order_info = self.client.get_order(symbol=self.ticker, orderId=order_id)
        return float(order_info['origQty'])

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
