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
from merkato.constants import BUY, SELL, PRICE, USER_ID, AMOUNT
from merkato.exchanges.test_exchange.orderbook import Orderbook
from merkato.exchanges.test_exchange.constants import test_asks, test_bids
from merkato.exchanges.tux_exchange.utils import translate_ticker

class TestExchange(ExchangeBase):
    def __init__(self, config, coin, base, user_id=20, accounts = {}, price = 1):
        self.coin = coin
        self.base = base
        self.ticker = translate_ticker(coin=coin, base=base)
        self.orderbook = Orderbook(test_bids, test_asks)
        self.user_id = user_id
        self.user_accounts = accounts
        self.order_history = []
        self.price = price
        self.retries = 3
        self.limit_only = True
        self.DEBUG = 3
        
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
            raise Exception(e)

                
    def _buy(self, amount, bid):
        self.orderbook.addBid(self.user_id, amount, bid)


    def buy(self, amount, bid):
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
            raise Exception(e)
            return False


    def get_order_history(self, user_id):
        return self.order_history


    def generate_fake_data(self, delta_range=[-3,3]):
        positive_or_negative = [-.2, .2]
        self.debug(3,"test exchange.py gen fake data", self.price)
        self.price = abs(self.price * (1 + random.randint(*delta_range) / 100))  # percent walk of price, never < 0
        self.debug(3, "test exchange.py gen fake data: new price", self.price)
        new_orders = self.orderbook.generate_fake_orders(self.price)        
        if new_orders:
            self.order_history.extend(new_orders)


    def get_all_orders(self):
        ''' Returns all open orders for the current pair
        '''
        final_bids = list(map(lambda x: [x[PRICE], x[AMOUNT]], self.orderbook.bids))
        final_asks = list(map(lambda x: [x[PRICE], x[AMOUNT]], self.orderbook.asks))
        return {
            "asks": final_asks,
            "bids": final_bids
        }


    def get_my_open_orders(self):
        ''' Returns all open orders for the authenticated user '''
        # my_filtered_bids = list(filter(lambda order: order[USER_ID] == self.user_id, self.orderbook.bids))
        # my_filtered_asks = list(filter(lambda order: order[USER_ID] == self.user_id, self.orderbook.asks))
        # final_bids = list(map(lambda x: [x[PRICE], x[AMOUNT]], my_filtered_bids))
        # final_asks = list(map(lambda x: [x[PRICE], x[AMOUNT]], my_filtered_asks))
        # all_orders = {
        #     "asks": final_asks,
        #     "bids": final_bids
        # }
        my_filtered_bids = list(filter(lambda order: order[USER_ID] == self.user_id, self.orderbook.bids))
        my_filtered_asks = list(filter(lambda order: order[USER_ID] == self.user_id, self.orderbook.asks))
        combined_orders = []

        combined_orders.extend(my_filtered_asks)
        combined_orders.extend(my_filtered_bids)

        print('combined_orders', combined_orders)
        my_open_orders = {}

        for order in combined_orders:
            order_id = order['id']
            my_open_orders[order_id] = order
        return my_open_orders

    def get_my_trade_history(self):
        try:
            if not self.order_history:
                return []
            filtered_history = list(filter(lambda order: order[USER_ID] == self.user_id, self.order_history))
        except:
            self.debug(3, "get_my_trade_history", self.order_history, self.user_id)
            raise
        return filtered_history 


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
        pair_balances = {"base" : {"amount": 10000000000,
                                   "name" : self.base},
                         "coin": {"amount": 10000000000,
                                  "name": self.coin},
                        }

        return pair_balances


    def get_last_trade_price(self):
        self.generate_fake_data()
        return self.price


    def get_lowest_ask(self):
        asks_exist = len(self.orderbook.asks) > 0
        if not asks_exist:
            return test_asks[0][PRICE]
        return self.orderbook.asks[0][PRICE]


    def get_highest_bid(self):
        bids_exist = len(self.orderbook.bids) > 0
        if not bids_exist:
            return test_bids[0][PRICE]
        return self.orderbook.bids[0][PRICE]
