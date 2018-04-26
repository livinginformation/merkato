import time
import json
from exchange import Exchange


class Merkato:
    def __init__(self, exchange):
        self.exchange = exchange
        self.distribution_strategy = 1
        self.spread = '15' # Take as parameter eventually


    def rebalance_orders():
        pass


    def create_bid_ladder(self, ticker, total_btc, low_price, high_price, increment):
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
        orders = get_orders(self.exchange.exchange, ticker)
        lowest_ask = orders['asks'][0][0]

        if float(high_price) >= float(lowest_ask):
            print("Aborting: Bid ladder would make a market order.")
            return

        while bid_price <= float(high_price):
            if DEBUG: print("setting bid at " + "{:.8f}".format(bid_price))
            buy_amount = bid_amount/bid_price
            if DEBUG: print("Buy amount: " + str(buy_amount))
            self.exchange.buy(buy_amount, bid_price, ticker)
            bid_price += float(increment)
            time.sleep(.3)


    def create_ask_ladder(self, ticker, total_amount, low_price, high_price, increment):
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
        orders = get_orders(self.exchange.exchange, ticker)
        highest_bid = orders['bids'][0][0]

        if ask_price <= float(highest_bid):
            print("Aborting: Ask ladder would make a market order.")
            return

        while ask_price <= float(high_price):
            if DEBUG: print("setting ask at " + "{:.8f}".format(ask_price))
            self.exchange.sell(ask_amount, ask_price, ticker)
            ask_price += float(increment)
            time.sleep(.3)

        pass


    def merge_orders():
        pass


    def update_order_book():
        pass
