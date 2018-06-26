import json
import requests
import time
from merkato.exchanges.exchange_base import ExchangeBase
from binance.client import Client
from binance.enums import *

import logging
log = logging.getLogger(__name__)

XMR_AMOUNT_PRECISION = 3
XMR_PRICE_PRECISION = 6


class BinanceExchange(ExchangeBase):
    url = "https://api.binance.com"

    def __init__(self, config, coin, base, password='password'):
        self.client = Client(config['public_api_key'], config['private_api_key'])
        self.limit_only = config['limit_only']
        self.retries = 5
        self.coin = coin
        self.base = base
        self.ticker = coin + base
        self.name = 'bina'

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
                    log.info("SELL {} {} at {} on {} FAILED - would make a market order.".format(amount,self.ticker, ask, "binance"))
                    return False # Maybe needs failed or something

            try:
                success = self._sell(amount, ask)

                if success:
                    log.info("SELL {} {} at {} on {}".format(amount, self.ticker, ask, "binance"))
                    return success

                else:
                    log.info("SELL {} {} at {} on {} FAILED - attempt {} of {}".format(amount, self.ticker, ask, "binance", attempt, self.retries))
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
        info = self.client.get_symbol_info(symbol=self.ticker)
        log.info("TEST ONE TWO")
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

                    log.info("BUY {} {} at {} on {} FAILED - would make a market order.".format(amount, self.ticker, bid, "binance"))
                    return False # Maybe needs failed or something

            try:
                success = self._buy(bid_amount, bid)
                if success:
                    log.info("BUY {} {} at {} on {}".format(bid_amount, self.ticker, bid, "binance"))
                    return success

                else:
                    log.info("BUY {} {} at {} on {} FAILED - attempt {} of {}".format(amount, self.ticker, bid, "binance", attempt, self.retries))
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
                    log.info("BUY {} {} at {} on {}".format(bid_amount, self.ticker, bid, "binance"))
                    return success

                else:
                    log.info("BUY {} {} at {} on {} FAILED - attempt {} of {}".format(amount, self.ticker, bid, "binance", attempt, self.retries))
                    attempt += 1
                    time.sleep(1)

            except Exception as e:  # TODO - too broad exception handling
                raise ValueError(e)

    def market_sell(self, amount, ask):
        attempt = 0
        try:
            success = self._sell(amount, ask)

            if success:
                log.info("SELL {} {} at {} on {}".format(amount, self.ticker, ask, "binance"))
                return success

            else:
                log.info("SELL {} {} at {} on {} FAILED - attempt {} of {}".format(amount, self.ticker, ask, "binance", attempt, self.retries))
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

        log.info("get_all_orders", orders)
        return orders


    def get_my_open_orders(self, context_formatted=False):
        ''' Returns all open orders for the authenticated user '''
                
        orders = self.client.get_open_orders(symbol=self.ticker, recvWindow=10000000)
        # orders is an array of dicts we need to transform it to an dict of dicts to conform to binance
        new_dict = {}
        for order in orders:
            id = order['orderId']
            new_dict[id] = order
            new_dict[id]['id'] = id
            if context_formatted:
                if order['side'] == 'BUY':
                    new_dict[id]['type'] = 'buy'
                else:
                    new_dict[id]['type'] = 'sell'
        return new_dict


    def cancel_order(self, order_id):
        ''' Cancels the order with the specified order ID
            :param order_id: string
        '''

        log.info("Cancelling order.")

        if order_id == 0:
            log.warning("Cancel order id 0. Bailing")
            return False

        return self.client.cancel_order(
            symbol=self.ticker,
            orderId=order_id)


    def get_ticker(self, coin=None):
        ''' Returns the current ticker data for the given coin. If no coin is given,
            it will return the ticker data for all coins.
            :param coin: string (of the format BTC_XYZ)
        '''

        ticker = self.client.get_ticker(symbol=coin)

        # if not coin:
        #     return json.loads(response.text)
        # response_json = json.loads(response.text)
        log.info(ticker)

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
        log.info(response_json[coin])

        return response_json[coin]


    def get_balances(self):
        ''' TODO Function Definition
        '''

        # also keys go unused, also coin...
        base_balance = self.client.get_asset_balance(asset=self.base, recvWindow=10000000)
        coin_balance = self.client.get_asset_balance(asset=self.coin, recvWindow=10000000)
        base = float(base_balance['free']) + float(base_balance['locked'])
        coin = float(coin_balance['free']) + float(coin_balance['locked'])

        log.info("Base balance: {}".format(base_balance))
        log.info("Coin balance: {}".format(coin_balance))

        pair_balances = {"base" : {"amount": {'balance': base},
                                   "name" : self.base},
                         "coin": {"amount": {'balance': coin},
                                  "name": self.coin},
                        }

        return pair_balances


    def get_my_trade_history(self, start=0, end=0):
        ''' TODO Function Definition
        '''
        log.info("Getting trade history...")
        # start_is_provided = start != 0 and start != ''
        # print('start', start)
        # if start_is_provided:
        #     trades = self.client.get_my_trades(symbol=self.ticker, fromId=int(start), recvWindow=10000000)
        # else:
        trades = self.client.get_my_trades(symbol=self.ticker, recvWindow=10000000)

        for trade in trades:
            if trade['isBuyer'] == True:
                trade['type'] = 'buy'
            else:
                trade['type'] = 'sell'
            trade['amount'] = trade['qty']
            if 'time' in trade:
                date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(trade['time'])))
                trade['date'] = date
        trades.reverse()
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
        print('order info', order_info)
        print('amount executed', amount_executed)
        print('amount placed', amount_placed)
        return amount_placed > amount_executed and amount_executed > 0

    def get_total_amount(self, order_id):
        order_info = self.client.get_order(symbol=self.ticker, orderId=order_id)
        print('get toal amount', order_info)
        return float(order_info['origQty'])
