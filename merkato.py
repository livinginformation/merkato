import time
import json
from exchange import Exchange


class Merkato:
    def __init__(self, exchange):
        self.exchange = exchange
        self.distribution_strategy = 1
        self.spread = '15' # Take as parameter eventually


    def rebalance_orders(self):
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


    def merge_orders(self):
        # Consider changing semantics from existing_order and order to order and new_order.
        # That is, existing_order currently becomes order, and order becomes new_order.
        # Coin is a string

        orders = self.exchange.getmyopenorders()

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
                self.exchange.cancelorder(order_id)
                self.exchange.cancelorder(existing_order_id)

                # Update the totals to represent the new totals
                existing_order['total']  = str(existing_order_total + total)
                existing_order['amount'] = str(existing_order_amount + amount)

                # Place a new order on the books with the sum
                if existing_order_type == "buy":
                    print("Placing buy for", existing_order['total'], "bitcoins of", ticker, "at a price of", price)
                    new_id = self.exchange.buy(float(existing_order['total'])/float(price), float(price), ticker)

                else: # existing_order_type is sell
                    print("Placing sell for", existing_order['amount'], ticker, "at a price of", price)
                    new_id = self.exchange.sell(float(existing_order['amount']), float(price), ticker)

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
        history = self.exchange.getmytradehistory()
        hist_len = len(history)

        # Loop every 30 seconds, check tx history, see if orders were hit
        while True:
            print("Time: " + str(time.time()))

            time.sleep(30)
            new_history = self.exchange.getmytradehistory()
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
                self.merge_orders(ticker)


    def modify_settings(self, settings):
        # replace old settings with new settings
        pass

    def cancelrange(self, start, end):
        open_orders = self.exchange.getmyopenorders()
        for order in open_orders:
            price = open_orders[order]["price"]
            order_id = open_orders[order]["id"]
            if float(price) >= float(start) and float(price) <= float(end):
                self.exchange.cancelorder(order_id)
                if DEBUG: print("price: " + str(price))
                time.sleep(.3)
