import time
import json

from merkato.exchanges.tux_exchange.exchange import TuxExchange
from merkato.utils import create_price_data
from merkato.constants import BUY, SELL, ID, PRICE, LAST_ORDER
from merkato.utils.database_utils import update_merkato

DEBUG = True


class Merkato(object):
    def __init__(self, configuration, coin, base, spread, ask_budget, bid_budget):
        self.exchange = TuxExchange(configuration, coin=coin, base=base)
        self.mutex_UUID = configuration['exchange'] + "coin={}_base={}".format(coin,base)
        self.distribution_strategy = 1
        self.spread = spread # i.e '15
        # Create ladders from the bid and ask bidget here
        self.history =  self.exchange.get_my_trade_history() # TODO: Reconstruct from DB

    # Make a second init for recovering a Merkato from the merkatos table here
    
    def rebalance_orders(self, new_history, new_txes):
        # This function places a matching order for every new transaction since last run
        #
        # TODO: Modify so that the parent function only passes in the new transactions, don't
        # do the index check internally.
        
        # new_history is an array of transactions
        # new_txes is the number of new transactions contained in new_history
        sold = []
        bought = []
        index = -1*new_txes # Pop this many elements off the back of the transaction history
        newTransactionHistory = new_history[index:]
        for tx in newTransactionHistory:

            if tx['type'] == SELL:
                if DEBUG: print(SELL)
                amount = tx['amount']
                price = tx[PRICE]
                sold.append(tx)
                buy_price = float(price) - self.spread
                response = self.exchange.buy(amount, buy_price)

            if tx['type'] == BUY:
                print(BUY)
                amount = tx['amount']
                price = tx[PRICE]
                bought.append(tx)
                sell_price = float(price) + self.spread
                self.exchange.sell(amount, sell_price)
                response = self.exchange.buy(amount, buy_price)

            update_merkato(mutex_UUID, LAST_ORDER, response)

            
    def create_bid_ladder_new(self, total_btc, low_price, high_price):
        # TODO: BROKEN. Still fix up the float issues.
        # All parameters should be strings.

        # This gets the total range of the ladder in satoshis
        order_range = float(high_price) - float(low_price)

        # This was supposed to get the total number of orders we would be placing
        increments = round(float(order_range)/float(increment))

        # Divide the total btc by the total orders to get the btc per order
        bid_amount = float(total_btc)/float(increments)

        bid_price = Decimal(low_price)

        # Sanity check. Do a check to make sure that we're limit only.
        # This is also covered in the exchange interface, but having a second
        # check here is warranted.
        orders = self.exchange.get_all_orders()
        lowest_ask = orders['asks'][0][0]

        if float(high_price) >= float(lowest_ask):
            print("Aborting: Bid ladder would make a market order.")
            return

        while bid_price <= float(high_price):
            # 1. Calculate how much to buy
            # 2. Buy that much
            # 3. Increase bid_price by the percentage increment
            # 4. Sleep for .3 seconds (to prevent API throttling)
            # 5. No mutex operation is needed, the mutex operations only need to know
            #    it's last known order to have been hit. This is initialization.
        
        
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
        orders = self.exchange.get_all_orders()
        lowest_ask = orders['asks'][0][0]

        if float(high_price) >= float(lowest_ask):
            print("Aborting: Bid ladder would make a market order.")
            return

        while bid_price <= float(high_price):
            if DEBUG: print("setting bid at " + "{:.8f}".format(bid_price))
            buy_amount = bid_amount/bid_price
            if DEBUG: print("Buy amount: " + str(buy_amount))
            response = self.exchange.buy(buy_amount, bid_price)
            bid_price += float(increment)
            time.sleep(.3)
            update_merkato(self.mutex_UUID, LAST_ORDER, response)


    def create_ask_ladder_new(self, total_amount, low_price, high_price):
        # TODO: BROKEN. Still fix up the float issues.
        # All parameters should be strings.

        # This gets the total range of the ladder in satoshis
        order_range = float(high_price) - float(low_price)

        # This was supposed to get the total number of orders we would be placing
        increments = float(order_range)/float(increment)

        # Divide the total btc by the total orders to get the btc per order
        ask_amount = float(total_amount)/float(increments)

        ask_price = Decimal(low_price)

        # Sanity check. Do a check to make sure that we're limit only.
        # This is also covered in the exchange interface, but having a second
        # check here is warranted.
        highest_bid = self.exchange.get_highest_bid()

        if ask_price <= float(highest_bid):
            print("Aborting: Ask ladder would make a market order.")
            return

        while ask_price <= float(high_price):
            # 1. Calculate how much to sell
            # 2. Sell that much
            # 3. Increase ask_price by the percentage increment
            # 4. Sleep for .3 seconds (to prevent API throttling)
            # 5. No mutex operation is needed, the mutex operations only need to know
            #    it's last known order to have been hit. This is initialization.

        pass
    
    
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

        # Sanity check TODO: remove sanity check to exchange layer
        highest_bid = self.exchange.get_highest_bid()

        if ask_price <= float(highest_bid):
            print("Aborting: Ask ladder would make a market order.")
            return

        while ask_price <= float(high_price):
            if DEBUG: print("setting ask at " + "{:.8f}".format(ask_price))
            response = self.exchange.sell(ask_amount, ask_price)
            ask_price += float(increment)
            time.sleep(.3)
            update_merkato(self.mutex_UUID, LAST_ORDER, response)

        pass


    def merge_orders(self):
        # Takes all bids/asks that are at the same price, and combines them.
        #
        # Consider changing semantics from existing_order and order to order and new_order.
        # That is, existing_order currently becomes order, and order becomes new_order.
        # Coin is a string
        # TODO: Make orders/orderbook variables less semantically similar

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

            if coin != self.exchange.ticker:
                continue

            if price not in orderbook:

                price_data = create_price_data(orders, order)

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
                self.exchange.cancel_order(order_id)
                self.exchange.cancel_order(existing_order_id)

                # Update the totals to represent the new totals
                existing_order['total']  = str(existing_order_total + total)
                existing_order['amount'] = str(existing_order_amount + amount)

                # Place a new order on the books with the sum
                if existing_order_type == "buy":
                    print("Placing buy for", existing_order['total'], "{} of".format(self.base), self.exchange.ticker, "at a price of", price)
                    new_id = self.exchange.buy(float(existing_order['total'])/float(price), float(price), self.ticker)

                else: # existing_order_type is sell
                    print("Placing sell for", existing_order['amount'], self.exchange.ticker, "at a price of", price)
                    new_id = self.exchange.sell(float(existing_order['amount']), float(price), self.exchange.ticker)

                if new_id == 0:
                    print("Something went wrong.")
                    return 1
                else: update_merkato(mutex_UUID, LAST_ORDER, new_id)

                if DEBUG: print("consolidation successful")
                existing_order['order_id'] = new_id

                if DEBUG: print(existing_order)

        print("Consolidation Successful")
        return 0



    def update_order_book(self):
        # Get current state of trade history before placing orders
        hist_len = len(self.history)
        now = str(time.time())
        last_trade_price = self.exchange.get_last_trade_price()

        print("Time: " + now)

        new_history = self.exchange.get_my_trade_history()
        new_hist_len = len(new_history)

        if new_hist_len > hist_len:
            # We have new transactions
            new_txes = new_hist_len - hist_len
            if DEBUG: print("New transactions: " + str(new_txes))
            self.rebalance_orders(new_history, new_txes)
            self.merge_orders()
            
            self.history = new_history

        # context to be used for GUI plotting
        context = {"price": (now, last_trade_price),
                   "filled_orders": {"buy": bought,
                                     "sell": sold},
                   "open_orders": self.exchange.get_my_open_orders(),
                   "balances": self.exchange.get_balances()
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
