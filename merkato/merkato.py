import time
import json

from merkato.exchanges.tux_exchange.exchange import TuxExchange
from merkato.constants import BUY, SELL, ID, PRICE, LAST_ORDER, ASK_RESERVE, BID_RESERVE, EXCHANGE
from merkato.utils.database_utils import update_merkato, insert_merkato, merkato_exists
from merkato.exchanges.tux_exchange.utils import translate_ticker
from merkato.utils import create_price_data, validate_merkato_initialization, get_relevant_exchange, get_allocated_pair_balances, check_reserve_balances
import math
from math import floor
import datetime
DEBUG = False


class Merkato(object):
    def __init__(self, configuration, coin, base, spread, bid_reserved_balance, ask_reserved_balance):
        validate_merkato_initialization(configuration, coin, base, spread)
        UUID = configuration['exchange'] + "coin={}_base={}".format(coin,base)
        
        exchange_class = get_relevant_exchange(configuration[EXCHANGE])
        self.exchange = exchange_class(configuration, coin=coin, base=base)
        total_pair_balances = self.exchange.get_balances()
        allocated_pair_balances = get_allocated_pair_balances(configuration['exchange'], base, coin)
        check_reserve_balances(total_pair_balances, allocated_pair_balances, coin_reserve=ask_reserved_balance, base_reserve=bid_reserved_balance)

        merkato_does_exist = merkato_exists(UUID)
        insert_merkato(configuration[EXCHANGE], UUID, base, coin, spread, bid_reserved_balance, ask_reserved_balance)
        self.mutex_UUID = UUID
        self.distribution_strategy = 1
        self.spread = spread # i.e '.15
        # Create ladders from the bid and ask bidget here
        self.history = self.exchange.get_my_trade_history() # TODO: Reconstruct from DB
        self.bid_reserved_balance = bid_reserved_balance
        self.ask_reserved_balance = ask_reserved_balance
        if not merkato_does_exist:
            print('new merkato')
            self.distribute_initial_orders(total_base=bid_reserved_balance, total_alt=ask_reserved_balance)
        self.DEBUG = 100

    def debug(self, level, header, *args):
        if level <= self.DEBUG:
            print("-" * 10)
            print("{}---> {}:".format(level, header))
            for arg in args:
                print("\t\t" + repr(arg))
            print("-" * 10)

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
        self.debug(2, "merkato.rebalance_orders")
        self.debug(3, "merkato.rebalance_orders:  new txs", newTransactionHistory)
        
        for tx in newTransactionHistory:

            if tx['type'] == SELL:
                if DEBUG: print(SELL)
                amount = tx['amount']
                price = tx[PRICE]
                sold.append(tx)
                buy_price = float(price) * ( 1  - self.spread)
                self.debug(4, "found sell", tx,"corresponding buy", buy_price)
                response = self.exchange.buy(amount, buy_price)

            if tx['type'] == BUY:
                amount = tx['amount']
                price = tx[PRICE]
                bought.append(tx)
                sell_price = float(price) * ( 1  + self.spread)
                self.debug(4, "found buy",tx, "corresponding sell", sell_price)
                response = self.exchange.sell(amount, sell_price)

            update_merkato(self.mutex_UUID, LAST_ORDER, response)
            
        self.log_new_transactions(newTransactionHistory)
        
        return newTransactionHistory

    def decaying_bid_ladder(self, total_amount, step, start_price):
        # Places an bid ladder from the start_price to 1/2 the start_price.
        # The first order in the ladder is half the amount (in the base currency) of the last
        # order in the ladder. The amount allocated at each step decays as
        # orders are placed.
        # Abandon all hope, ye who enter here. This function uses black magic (math).

        scaling_factor = 0
        total_orders = floor(math.log(2, step)) # 277 for a step of 1.0025
        current_order = 1
        
        # Calculate scaling factor
        while current_order < total_orders:
            scaling_factor += 1/(step**current_order)
            current_order += 1

        current_order = 1
        amount = 0

        prior_reserve = self.bid_reserved_balance
        while current_order < total_orders:
            step_adjusted_factor = step**current_order
            current_bid_amount = total_amount/(scaling_factor * step_adjusted_factor)
            current_bid_price = start_price/step_adjusted_factor
            amount += current_bid_amount
            
            # TODO Create lock
            self.exchange.buy(current_bid_amount, current_bid_price)
            self.remove_reserve(current_bid_amount, BID_RESERVE) 
            # TODO Release lock
            
            current_order += 1

        print('allocated amount', prior_reserve - self.bid_reserved_balance)

    def distribute_initial_orders(self, total_base, total_alt):
        # waiting on vizualization for bids before running it as is
        
        current_price = (self.exchange.get_highest_bid() + self.exchange.get_lowest_ask())/2

        ask_start = current_price + current_price*self.spread/2
        bid_start = current_price - current_price*self.spread/2
        
        self.distribute_bids(bid_start, total_base)
        self.distribute_asks(ask_start, total_alt)


    def distribute_bids(self, price, total_to_distribute, step=1.0025):
        # Allocates your market making balance on the bid side, in a way that
        # will never be completely exhausted (run out).
        # total_to_distribute is in the base currency (usually BTC)

        # 2. Call decaying_bid_ladder on that start price, with the given step,
        #    and half the total_to_distribute
        self.decaying_bid_ladder(total_to_distribute/2, step, price)

        # 3. Call decaying_bid_ladder twice more, each time halving the
        #    start_price, and halving the total_amount
        self.decaying_bid_ladder(total_to_distribute/4, step, price/2)
        self.decaying_bid_ladder(total_to_distribute/8, step, price/4)

        # 4. Store the remainder of total_to_distribute, as well as the final
        #    order placed in decaying_bid_ladder
        pass

    def log_new_transactions(self, newTransactionHistory):
        file = open('my_tax_audit_logs.txt', 'a+')
        for transaction in newTransactionHistory:
            file.write(json.dumps(transaction))
        file.close()


    def create_bid_ladder(self, total_btc, low_price, high_price, increment):
        # This function has been deprecated in favor of decaying_bid_ladder and
        # distribute_bids. Having the ability to place a ladder within Merkato
        # (independent of market making) may eventually be useful, but will require
        # some reworking of this function (due to amount/price scaling).
        #
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


    def decaying_ask_ladder(self, total_amount, step, start_price):
        # Places an ask ladder from the start_price to 2x the start_price.
        # The last order in the ladder is half the amount of the first
        # order in the ladder. The amount allocated at each step decays as
        # orders are placed.
        # Abandon all hope, ye who enter here. This function uses black magic (math).

        scaling_factor = 0
        total_orders = floor(math.log(2, step)) # 277 for a step of 1.0025
        current_order = 1

        # Calculate scaling factor
        while current_order < total_orders:
            scaling_factor += 1/(step**current_order)
            current_order += 1

        current_order = 1
        amount = 0

        prior_reserve = self.ask_reserved_balance
        while current_order < total_orders:
            step_adjusted_factor = step**current_order
            current_ask_amount = total_amount/(scaling_factor * step_adjusted_factor)
            current_ask_price = start_price*step_adjusted_factor
            amount += current_ask_amount

            # TODO Create lock
            self.exchange.sell(current_ask_amount, current_ask_price)
            self.remove_reserve(current_ask_amount, ASK_RESERVE) 
            # TODO Release lock

            current_order += 1

        #print(amount)
        print('allocated amount', prior_reserve - self.ask_reserved_balance)


    def distribute_asks(self, price, total_to_distribute, step=1.0025):
        # Allocates your market making balance on the ask side, in a way that
        # will never be completely exhausted (run out).

        # 2. Call decaying_ask_ladder on that start price, with the given step,
        #    and half the total_to_distribute
        self.decaying_ask_ladder(total_to_distribute/2, step, price)

        # 3. Call decaying_ask_ladder twice more, each time doubling the
        #    start_price, and halving the total_amount
        self.decaying_ask_ladder(total_to_distribute/4, step, price * 2)
        self.decaying_ask_ladder(total_to_distribute/8, step, price * 4)

        # 4. Store the remainder of total_to_distribute, as well as the final
        #    order placed in decaying_ask_ladder
        pass


    def create_ask_ladder(self, total_amount, low_price, high_price, increment):
        # This function has been deprecated in favor of decaying_ask_ladder and
        # distribute_asks. Having the ability to place a ladder within Merkato
        # (independent of market making) may eventually be useful, but will require
        # some reworking of this function (due to amount/price scaling).
        #
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
        #print(orders)

        # Create a dictionary to store our desired orderbook
        orderbook = dict()

        for order in orders:
            print( 'order', order)

            price    = orders[order][PRICE]
            coin     = orders[order]["coin"]
            amount   = float(orders[order]["amount"]) # Amount in asset
            total    = float(orders[order]["total"])  # Total in BTC
            order_id = orders[order]['id']

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
                existing_order_id     = existing_order['id']
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
                    print("Placing buy for", existing_order['total'], "{} of".format(self.exchange.base), self.exchange.ticker, "at a price of", price)
                    new_id = self.exchange.buy(float(existing_order['total'])/float(price), float(price), self.exchange.ticker)

                else: # existing_order_type is sell
                    print("Placing sell for", existing_order['amount'], self.exchange.ticker, "at a price of", price)
                    new_id = self.exchange.sell(float(existing_order['amount']), float(price), self.exchange.ticker)

                if new_id == 0:
                    print("Something went wrong.")
                    return 1
                else: update_merkato(self.mutex_UUID, LAST_ORDER, new_id)

                if DEBUG: print("consolidation successful")
                existing_order['id'] = new_id

                if DEBUG: print(existing_order)

        print("Consolidation Successful")
        return 0



    def update(self):
        # Get current state of trade history before placing orders
        #print(self.history)
        hist_len = len(self.history)
        now = str(datetime.datetime.now().isoformat()[:-7].replace("T", " "))
        last_trade_price = self.exchange.get_last_trade_price()

        #print("Time: " + now)

        new_history = self.exchange.get_my_trade_history()
        new_hist_len = len(new_history)
        new_transactions = []
        
        if new_hist_len > hist_len:
            # We have new transactions
            new_txes = new_hist_len - hist_len
            if DEBUG: print("New transactions: " + str(new_txes))
            new_transactions = self.rebalance_orders(new_history, new_txes)
            #self.merge_orders()
            
            self.history = new_history

        # context to be used for GUI plotting
        context = {"price": (now, last_trade_price),
                   "filled_orders": new_transactions,
                   "open_orders": self.exchange.get_my_open_orders(),
                   "balances": self.exchange.get_balances(),
                   "orderbook": self.exchange.get_all_orders()
                   }
        return context


    def modify_settings(self, settings):
        # replace old settings with new settings
        pass

    def add_reserve(self):
        pass
    
    def remove_reserve(self, amount, type_of_reserve):
        current_reserve_amount = self.ask_reserved_balance if type_of_reserve == ASK_RESERVE else self.bid_reserved_balance
        invalid_reserve_reduction = amount > current_reserve_amount
        if invalid_reserve_reduction:
            return False
        
        if type_of_reserve == ASK_RESERVE:
            new_amount = self.ask_reserved_balance - amount
            self.ask_reserved_balance = new_amount            
        else:
            new_amount = self.bid_reserved_balance - amount
            self.bid_reserved_balance = new_amount
        update_merkato(self.mutex_UUID, type_of_reserve, new_amount)
        return True
        
    def cancelrange(self, start, end):
        open_orders = self.exchange.get_my_open_orders()
        for order in open_orders:
            price = open_orders[order][PRICE]
            order_id = open_orders[order][ID]
            if float(price) >= float(start) and float(price) <= float(end):
                self.exchange.cancel_order(order_id)
                if DEBUG: print("price: " + str(price))
                time.sleep(.3)

