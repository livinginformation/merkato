import hashlib
import hmac
import json
import math
import requests
import time
import random
import urllib.parse
from merkato.exchanges.test_exchange.utils import apply_resolved_orders
from merkato.exchanges.exchange_base import ExchangeBase
from merkato.constants import BUY, SELL
from merkato.exchanges.test_exchange.orderbook import Orderbook
from merkato.exchanges.text_exchange.constants import test_asks, test_bids
DEBUG = True


class TestExchange(ExchangeBase):
    def __init__(self, config, coin, base, user_id, accounts = {}, price = 1):
        self.coin = coin
        self.base = base
        self.ticker = translate_ticker(coin=coin, base=base)
        self.orderbook = Orderbook(test_bids, test_asks)
        self.user_id = user_id
        self.user_accounts = accounts
        self.order_history = []
        self.price = price


    def debug(self, level, header, *args):
        if level <= self.DEBUG:
            print("-"*10)
            print("{}---> {}:".format(level, header))
            for arg in args:
                print("\t\t" + repr(arg))
            print("-" * 10)


    def _sell(self, amount, ask,):
        self.orderbook.addAsk(self.user_id, amount, ask)


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
        self.orderbook.addBid(self.user_id, amount, bid)


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
        return self.order_history


    def generate_fake_data(self, delta_range=[-3,3]):
        positive_or_negative = [-.2, .2]
        self.price = abs(self.price * (1 + random.randint(*delta_range) / 100))  # percent walk of price, never < 0
        new_orders = self.orderbook.generate_fake_orders(self.price)        
        if new_orders:
            apply_resolved_orders(self.user_accounts, new_orders)
            self.order_history.append(new_orders)


    def get_all_orders(self):
        ''' Returns all open orders for the current pair
        '''
        return self.orderbook # We need to decide on the format this returns.


    def get_my_open_orders(self):
        ''' Returns all open orders for the authenticated user '''
        my_bids = filter(lambda order: order["user_id"] == self.user_id, self.orderbook.bids)
        my_asks = filter(lambda order: order["user_id"] == self.user_id, self.orderbook.aks)
        return {
            "asks": my_asks,
            "bids": my_bids
        }

    def get_my_trade_history(self):
        return filter(lambda order: order["user_id"] == self.user_id, self.order_history)


    def cancel_order(self, order_id):
        ''' Cancels the order with the specified order ID
            :param order_id: string
        '''
        # Broken, TODO
        return ""


    def get_ticker(self):
        ''' Returns the current ticker data for the target coin.
        '''
        # Broken, TODO
        return ""


    def get_24h_volume(self):
        ''' Returns the 24 hour volume for the target coin.
        '''
        # Broken, TODO
        return ""


    def get_balances(self):
        # broken, TODO        
        return ""


    def get_last_trade_price(self):
        return self.get_ticker()


    def get_lowest_ask(self):
        return self.orderbook.asks[0]


    def get_highest_bid(self):
        return self.orderbook.bids[0]
