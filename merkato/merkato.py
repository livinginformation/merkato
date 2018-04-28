import time
import json

from merkato.exchanges.exchange import Exchange
from merkato.utils import create_price_data
from merkato.constants import BUY, SELL, ID, PRICE

DEBUG = True


class Merkato(object):
    def __init__(self, configuration, ticker, spread, ask_budget, bid_budget):
        self.exchange = Exchange(configuration)
        self.distribution_strategy = 1
        self.ticker = ticker # i.e. 'XMR_BTC'
        self.spread = spread # i.e '15
        self.ask_profile = [(1, 5), (2, 5), (3, 10), (4, 15), (5, 20), (6, 25), (10, 30)] # (% change in price, % balance allocation)
        self.bid_profile = [(-1, 5), (-2, 5), (-3, 10), (-4, 15), (-5, 20), (-6, 25), (-10, 30)]  # (% change in price, % balance allocation)
        self.ask_budget = ask_budget
        self.bid_budget = bid_budget
        self.original_ask = None
        self.original_bid = None

    def rebalance_orders(self):
        pass

    def create_relative_bid_ladder(self,):
        # a ladder that can be user configured (via gui)

        # get market price to make ladder relative from
        orders = self.exchange.get_all_orders(self.ticker)
        if self.original_ask is None:
            lowest_ask = orders['asks'][0][0]
        else:
            lowest_ask = self.original_ask

        for level, allocation in self.bid_profile:
            new_price = lowest_ask * (1 + (float(level) / 100.0))
            new_amount = float(self.bid_budget) * (float(allocation) / 100.0)
            if new_price < lowest_ask and new_amount < self.bid_budget:   # sanity check
                self.exchange.buy(new_amount, new_price, self.ticker)
                time.sleep(.3)
            else:
                # TODO: add more meaningful error text
                raise Exception("ERROR in create_relative_bid_ladder: faulty logic or inputs")

    def create_relative_ask_ladder(self,):
        # a ladder that can be user configured (via gui)

        # get market price to make ladder relative from
        orders = self.exchange.get_all_orders(self.ticker)
        if self.original_bid is None:
            highest_bid = orders['bids'][0][0]
        else:
            highest_bid = self.original_bid

        for level, allocation in self.ask_profile:
            new_price = highest_bid * (1 + (float(level) / 100.0))
            new_amount = float(self.ask_budget) * (float(allocation) / 100.0)
            if new_price > highest_bid and new_amount < self.ask_budget:   # sanity check
                self.exchange.sell(new_amount, new_price, self.ticker)
                time.sleep(.3)
            else:
                # TODO: add more meaningful error text
                raise Exception("ERROR in create_relative_ask_ladder: faulty logic or inputs")



    def create_bid_ladder(self, total_btc, low_price, high_price, increment):
        # TODO: this is currently unused in merkato
        #  low_price, high_price, and increment are strings
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
        orders = self.exchange.get_all_orders(self.ticker)
        lowest_ask = orders['asks'][0][0]

        if float(high_price) >= float(lowest_ask):
            print("Aborting: Bid ladder would make a market order.")
            return

        while bid_price <= float(high_price):
            if DEBUG: print("setting bid at " + "{:.8f}".format(bid_price))
            buy_amount = bid_amount/bid_price
            if DEBUG: print("Buy amount: " + str(buy_amount))
            self.exchange.buy(buy_amount, bid_price, self.ticker)
            bid_price += float(increment)
            time.sleep(.3)


    def create_ask_ladder(self, total_amount, low_price, high_price, increment):
        # TODO: this is currently unused in merkato
        #  low_price, high_price, and increment are all strings
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
        orders = self.exchange.get_all_orders(self.ticker)
        highest_bid = orders['bids'][0][0]

        if ask_price <= float(highest_bid):
            print("Aborting: Ask ladder would make a market order.")
            return

        while ask_price <= float(high_price):
            if DEBUG: print("setting ask at " + "{:.8f}".format(ask_price))
            self.exchange.sell(ask_amount, ask_price, self.ticker)
            ask_price += float(increment)
            time.sleep(.3)

        pass


    def merge_orders(self):
        # TODO still broken post-refactor!
        # Consider changing semantics from existing_order and order to order and new_order.
        # That is, existing_order currently becomes order, and order becomes new_order.
        # Coin is a string

        orders = self.exchange.get_my_open_orders()
        print(orders)

        # Create a dictionary to store our desired orderbook
        orderbook = dict()

        for order in orders:

            price    = orders[order][PRICE]
            coin     = orders[order]["coin"]
            amount   = float(orders[order]["amount"]) # Amount in asset
            total    = float(orders[order]["total"])  # Total in BTC

            if DEBUG: print(orders[order])

            if coin != self.ticker:
                continue

            if price not in orderbook: # always true as orderbook is empty dict

                price_data = create_price_data(orders, order)

                orderbook[price] = price_data
                if DEBUG: print("Found new bid at", price)

            else:

                print("Collision at", price)

                existing_order        = orderbook[price] # this will fail as orderbook is empty dict
                existing_order_id     = existing_order['order_id']
                existing_order_type   = existing_order['type']
                existing_order_total  = float(existing_order['total'])
                existing_order_amount = float(existing_order['amount'])

                # Cancel the colliding orders
                self.exchange.cancel_order(order_id)
                self.exchange.cancel_order(existing_order_id)

                # Update the totals to represent the new totals
                existing_order['total']  = str(existing_order_total + total)
                existing_order['amount'] = str(existing_order_amount + amount)

                # Place a new order on the books with the sum
                if existing_order_type == "buy":
                    print("Placing buy for", existing_order['total'], "bitcoins of", self.ticker, "at a price of", price)
                    new_id = self.exchange.buy(float(existing_order['total'])/float(price), float(price), self.ticker)

                else: # existing_order_type is sell
                    print("Placing sell for", existing_order['amount'], self.ticker, "at a price of", price)
                    new_id = self.exchange.sell(float(existing_order['amount']), float(price), self.ticker)

                if new_id == 0:
                    print("Something went wrong.")
                    return 1

                if DEBUG: print("consolidation successful")
                existing_order['order_id'] = new_id

                if DEBUG: print(existing_order)

        print("Consolidation Successful")
        return 0



    def update_order_book(self):
        # Get current state of trade history before placing orders
        history = self.exchange.get_my_trade_history()
        hist_len = len(history)
        now = str(time.time())
        last_trade_price = self.exchange.interface.get_ticker(coin=self.ticker)["last"] # at least for tux api...

        print("Time: " + now)

        new_history = self.exchange.get_my_trade_history()
        new_hist_len = len(new_history)

        if new_hist_len > hist_len:
            # We have new transactions
            new_txes = new_hist_len - hist_len
            if DEBUG: print("New transactions: " + str(new_txes))
            sold = []
            bought = []
            for tx in new_history[:new_txes]:

                if tx['type'] == SELL:
                    if DEBUG: print(SELL)
                    amount = tx['amount']
                    price = tx[PRICE]
                    sold.append(tx)
                    self.buy(amount, float(price) - self.spread, self.ticker)

                if tx['type'] == BUY:
                    print(BUY)
                    amount = tx['amount']
                    price = tx[PRICE]
                    bought.append(tx)
                    self.sell(amount, float(price) + self.spread, self.ticker)

            hist_len = new_hist_len
            self.merge_orders(self.ticker)

        # context to be used for GUI plotting
        context = {"price": (now, last_trade_price),
                   "filled_orders": {"buy": bought,
                                     "sell": sold},
                   "open_orders": self.exchange.get_my_open_orders(),
                   "balances": self.exchange.interface.get_balances(0,0,0) # TODO: this needs to get abstracted in exchange base class, also args are unused
                   }
        return context


    def modify_settings(self, settings):
        # replace old settings with new settings
        pass


    def cancelrange(self, start, end):
        open_orders = self.exchange.get_my_open_orders()
        for order in open_orders:
            price = open_orders[order][PRICE]
            order_id = open_orders[order][ID]
            if float(price) >= float(start) and float(price) <= float(end):
                self.exchange.cancel_order(order_id)
                if DEBUG: print("price: " + str(price))
                time.sleep(.3)
