import requests
import urllib.parse
import time
import math
import hashlib
import hmac
import json
import sqlite3
from utils import get_ticker, get_24h_volume, getorders

DEBUG = True

class Exchange:
    '''Merkato Market Making Bot Exchange Interface'''
    def __init__(self, configuration):
        self.privatekey = configuration['privatekey']
        self.publickey  = configuration['publickey']
        self.exchange   = configuration['exchange']


    def _getBalances_tux(self, coin='none'):
        print("--> Checking Balances")
        while True:
            try:

                nonce = int(time.time()*1000)
                tuxParams = {"method" : "getmybalances", "nonce":nonce}
                post = urllib.parse.urlencode(tuxParams)
                signature = hmac.new(self.privatekey.encode('utf-8'), post.encode('utf-8'), hashlib.sha512).hexdigest()
                header = {'Key' : self.publickey, 'Sign' : signature}
                tuxbalances = requests.post(tuxURL, data=tuxParams, headers=header).json()

                print("test?")
                print(tuxbalances)
                for crypto in tuxbalances:
                    print(str(crypto) + ": " + str(tuxbalances[crypto]))

                return tuxbalances

            except:
                print("--> WARNING: Something went wrong when I was checking the balances. Let me try again in 30 seconds")
                time.sleep(30)


    def getBalances(self, coin='none'):
        if self.exchange == "tux":
            return self._getBalances_tux(coin)

        else:
            print("Exchange currently unsupported.")


    def _sell_tux(self, amount, ask, ticker):
        ''' Places a sell for a number of an asset at the indicated price (0.00000503 for example)

        Amount and ask are floats, ticker is a string

        Todo: Take arguments of other types, convert to applicable ones.
        '''
        while True:
            try:
                if DEBUG: print("--> Selling...")

                query = { "method": "sell", "market": "BTC", "coin": ticker, "amount": "{:.8f}".format(amount), "price": "{:.8f}".format(ask), "nonce": int(time.time()*1000) }

                post = urllib.parse.urlencode(query)
                signature = hmac.new(self.privatekey.encode('utf-8'), post.encode('utf-8'), hashlib.sha512).hexdigest()
                header = {'Key' : self.publickey, 'Sign' : signature}
                response = requests.post(tuxURL, data = query, headers = header, timeout=15).json()

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
                query = { "method": "buy", "market": "BTC", "coin": ticker, "amount": "{:.8f}".format(amount), "price": "{:.8f}".format(bid), "nonce": int(time.time()*1000) }
                post = urllib.parse.urlencode(query)
                signature = hmac.new(self.privatekey.encode('utf-8'), post.encode('utf-8'), hashlib.sha512).hexdigest()
                header = {'Key' : self.publickey, 'Sign' : signature}
                response = requests.post(tuxURL, data=query, headers=header, timeout=15).json()

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

                query = { "method": "getmyopenorders", "nonce": int(time.time()*1000) }

                post = urllib.parse.urlencode(query)
                signature = hmac.new(self.privatekey.encode('utf-8'), post.encode('utf-8'), hashlib.sha512).hexdigest()
                header = {'Key' : self.publickey, 'Sign' : signature}
                response = requests.post(tuxURL, data=query, headers=header).json()

                return response

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
                    query = { "method": "getmytradehistory", "start": start, "end": end, "nonce": int(time.time()*1000) }
                else:
                    query = { "method": "getmytradehistory", "nonce": int(time.time()*1000) }

                post = urllib.parse.urlencode(query)
                signature = hmac.new(self.privatekey.encode('utf-8'), post.encode('utf-8'), hashlib.sha512).hexdigest()
                header = {'Key' : self.publickey, 'Sign' : signature}
                response = requests.post(tuxURL, data=query, headers=header).json()

                return response
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

            query = { "method": "cancelorder", "market": "BTC", "id": order_id, "nonce": int(time.time()*1000) }
            post = urllib.parse.urlencode(query)
            signature = hmac.new(self.privatekey.encode('utf-8'), post.encode('utf-8'), hashlib.sha512).hexdigest()
            header = {'Key' : self.publickey, 'Sign' : signature}
            response = requests.post(tuxURL, data=query, headers=header, timeout=15).json()

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


    def ask_ladder(self, ticker, total_amount, low_price, high_price, increment):
        # Ticker, low_price, high_price, and increment are all strings
        # total_amount is a float
        #
        # This function will never make a market order.

        order_range = float(high_price) - float(low_price)

        increments = float(order_range)/float(increment)

        ask_amount = float(total_amount)/float(increments)

        if DEBUG: print("order range: " + str(order_range))
        if DEBUG: print("increments: " + str(increments))
        if DEBUG: print("Ask amount: " + str(round(ask_amount)))

        ask_price = float(low_price)

        # Sanity check
        orders = self.getorders(ticker)
        highest_bid = orders['bids'][0][0]

        if ask_price <= float(highest_bid):
            print("Aborting: Ask ladder would make a market order.")
            return

        while ask_price <= float(high_price):
            if DEBUG: print("setting ask at " + "{:.8f}".format(ask_price))
            self.sell(ask_amount, ask_price, ticker)
            ask_price += float(increment)
            time.sleep(.3)


    def bid_ladder(self, ticker, total_btc, low_price, high_price, increment):
        # Ticker, low_price, high_price, and increment are strings
        # total_btc is a float.
        #
        # This function will never make a market order.

        order_range = float(high_price) - float(low_price)

        increments = round(float(order_range)/float(increment))

        bid_amount = float(total_btc)/float(increments)

        if DEBUG: print("order range: " + str(order_range))
        if DEBUG: print("increments: " + str(increments))
        if DEBUG: print("bid_amount: " + str(bid_amount))

        bid_price = float(low_price)

        # Sanity check
        orders = self.getorders(ticker)
        lowest_ask = orders['asks'][0][0]

        if float(high_price) >= float(lowest_ask):
            print("Aborting: Bid ladder would make a market order.")
            return

        while bid_price <= float(high_price):
            if DEBUG: print("setting bid at " + "{:.8f}".format(bid_price))
            buy_amount = bid_amount/bid_price
            if DEBUG: print("Buy amount: " + str(buy_amount))
            self.buy(buy_amount, bid_price, ticker)
            bid_price += float(increment)
            time.sleep(.3)


    def maintain_window(self, spread, ticker):

        # Get current state of trade history before placing orders
        history = self.getmytradehistory()
        hist_len = len(history)

        # Loop every 30 seconds, check tx history, see if orders were hit
        while True:
            print("Time: " + str(time.time()))

            time.sleep(30)
            new_history = self.getmytradehistory()
            new_hist_len = len(new_history)

            if new_hist_len > hist_len:
                # We have new transactions
                new_txes = new_hist_len - hist_len
                if DEBUG: print("New transactions: " + str(new_txes))

                for tx in new_history[:new_txes]:

                    if tx['type'] == 'sell':
                        if DEBUG: print("sell")
                        amount = tx['amount']
                        price = tx['price']
                        self.buy(amount, float(price) - spread, ticker)

                    if tx['type'] == 'buy':
                        print("buy")
                        amount = tx['amount']
                        price = tx['price']
                        self.sell(amount, float(price) + spread, ticker)

                hist_len = new_hist_len
                self.consolidate(ticker)


    def cancelrange(self, start, end):
        orders = self.getmyopenorders()
        for order in orders:
            price = orders[order]["price"]
            order_id = orders[order]["id"]
            if float(price) >= float(start) and float(price) <= float(end):
                self.cancelorder(order_id)
                if DEBUG: print("price: " + str(price))
                time.sleep(.3)


    def consolidate(self, ticker):
        # Consider changing semantics from existing_order and order to order and new_order.
        # That is, existing_order currently becomes order, and order becomes new_order.
        # Coin is a string

        orders = self.getmyopenorders()

        # Create a dictionary to store our desired orderbook
        orderbook = dict()

        for order in orders:

            price    = orders[order]["price"]
            order_id = orders[order]["id"]
            type     = orders[order]["type"]
            coin     = orders[order]["coin"]
            amount   = float(orders[order]["amount"]) # Amount in asset
            total    = float(orders[order]["total"])  # Total in BTC

            if DEBUG: print(orders[order])

            if coin != ticker:
                continue

            if price not in orderbook:

                price_data             = {}

                price_data['total']    = total
                price_data['amount']   = amount
                price_data['order_id'] = order_id
                price_data['type']     = type

                orderbook[price] = price_data
                if DEBUG: print("Found new bid at", price)

            else:

                print("Collision at", price)

                existing_order        = orderbook[price]
                existing_order_id     = existing_order['order_id']
                existing_order_type   = existing_order['type']
                existing_order_total  = float(existing_order['total'])
                existing_order_amount = float(existing_order['amount'])

                # Cancel the colliding orders
                self.cancelorder(order_id)
                self.cancelorder(existing_order_id)

                # Update the totals to represent the new totals
                existing_order['total']  = str(existing_order_total + total)
                existing_order['amount'] = str(existing_order_amount + amount)

                # Place a new order on the books with the sum
                if existing_order_type == "buy":
                    print("Placing buy for", existing_order['total'], "bitcoins of", ticker, "at a price of", price)
                    new_id = self.buy(float(existing_order['total'])/float(price), float(price), ticker)

                else: # existing_order_type is sell
                    print("Placing sell for", existing_order['amount'], ticker, "at a price of", price)
                    new_id = self.sell(float(existing_order['amount']), float(price), ticker)

                if new_id == 0:
                    print("Something went wrong.")
                    return 1

                if DEBUG: print("consolidation successful")
                existing_order['order_id'] = new_id

                if DEBUG: print(existing_order)

        print("Consolidation Successful")
        return 0
