import time
import json

from merkato.exchanges.tux_exchange.exchange import TuxExchange
from merkato.constants import BUY, SELL, ID, PRICE, LAST_ORDER, ASK_RESERVE, BID_RESERVE, EXCHANGE, ONE_BITCOIN, ONE_SATOSHI
from merkato.utils.database_utils import update_merkato, insert_merkato, merkato_exists
from merkato.exchanges.tux_exchange.utils import translate_ticker
from merkato.utils import create_price_data, validate_merkato_initialization, get_relevant_exchange, get_allocated_pair_balances, check_reserve_balances, get_last_order, get_new_history
import math
from math import floor
import datetime
DEBUG = False


class Merkato(object):
    def __init__(self, configuration, coin, base, spread, bid_reserved_balance, ask_reserved_balance, user_interface=None):
        self.DEBUG = 100
        validate_merkato_initialization(configuration, coin, base, spread)
        self.initialized = False
        UUID = configuration['exchange'] + "coin={}_base={}".format(coin,base)
        self.mutex_UUID = UUID
        self.distribution_strategy = 1
        self.spread = spread # i.e '.15
        # Create ladders from the bid and ask bidget here
        self.bid_reserved_balance = bid_reserved_balance
        self.ask_reserved_balance = ask_reserved_balance
        self.user_interface = user_interface
        exchange_class = get_relevant_exchange(configuration[EXCHANGE])
        self.exchange = exchange_class(configuration, coin=coin, base=base)
        self.DEBUG = 100
        merkato_does_exist = merkato_exists(UUID)

        if not merkato_does_exist:
            print('new merkato')
            self.cancelrange(ONE_SATOSHI, ONE_BITCOIN)
            total_pair_balances = self.exchange.get_balances()
            print('total_pair_balances', total_pair_balances)
            allocated_pair_balances = get_allocated_pair_balances(configuration['exchange'], base, coin)
            check_reserve_balances(total_pair_balances, allocated_pair_balances, coin_reserve=ask_reserved_balance, base_reserve=bid_reserved_balance)
            insert_merkato(configuration[EXCHANGE], UUID, base, coin, spread, bid_reserved_balance, ask_reserved_balance)
            history = self.exchange.get_my_trade_history()
            update_merkato(self.mutex_UUID, LAST_ORDER, history[0]['orderId'])
            self.distribute_initial_orders(total_base=bid_reserved_balance, total_alt=ask_reserved_balance)

        else:
            #self.history = get_old_history(self.exchange.get_my_trade_history(), self.mutex_UUID)
            current_history = self.exchange.get_my_trade_history()
            last_order = get_last_order(self.mutex_UUID)
            new_history = get_new_history(current_history, last_order)
            self.rebalance_orders(new_history)
        self.initialized = True  # to avoid being updated before orders placed

    def _debug(self, level, header, *args):
        if level <= self.DEBUG:
            print("-" * 10)
            print("{}---> {}:".format(level, header))
            for arg in args:
                print("\t\t" + repr(arg))
            print("-" * 10)

    def rebalance_orders(self, new_txes, profit_margin=0):
        # This function places a matching order for every new transaction since last run
        #
        # profit_margin is a number from 0 to 1 representing the percent of the spread to return
        # to the user's balance before placing the matching order.
        #
        # TODO: Modify so that the parent function only passes in the new transactions, don't
        # do the index check internally.

        # new_history is an array of transactions
        # new_txes is the number of new transactions contained in new_history
        factor = self.spread*profit_margin
        self._debug(2, "merkato.rebalance_orders")
        ordered_transactions = new_txes
        print('ordered transactions rebalanced', ordered_transactions)
        for tx in ordered_transactions:

            if tx['type'] == SELL:
                if DEBUG: print(SELL) #todo: change # to new format
                # print('amount', type(tx['amount']), type(tx[PRICE])) # todo use debug
                
                amount = float(tx['amount']) * float(tx[PRICE])*(1-factor)
                price = tx[PRICE]
                buy_price = float(price) * ( 1  - self.spread)
                self._debug(4, "found sell", tx,"corresponding buy", buy_price)
                self.exchange.buy(amount, buy_price)

            if tx['type'] == BUY:
                amount = tx['amount']*(1-factor)
                price = tx[PRICE]
                sell_price = float(price) * ( 1  + self.spread)
                self._debug(4, "found buy",tx, "corresponding sell", sell_price)
                self.exchange.sell(amount, sell_price)

            update_merkato(self.mutex_UUID, LAST_ORDER, tx['orderId'])
            
        self.log_new_transactions(ordered_transactions)
        
        return ordered_transactions

    def decaying_bid_ladder(self, total_amount, step, start_price):
        # Places an bid ladder from the start_price to 1/2 the start_price.
        # The first order in the ladder is half the amount (in the base currency) of the last
        # order in the ladder. The amount allocated at each step decays as
        # orders are placed.
        # Abandon all hope, ye who enter here. This function uses black magic (math).

        scaling_factor = 0
        total_orders = floor(math.log(2, step)) # 277 for a step of 1.0025
        current_order = 0
        
        # Calculate scaling factor
        while current_order < total_orders:
            scaling_factor += 1/(step**current_order)
            current_order += 1

        current_order = 0
        amount = 0

        prior_reserve = self.bid_reserved_balance
        while current_order < total_orders:
            step_adjusted_factor = step**current_order
            current_bid_amount = float(total_amount/(scaling_factor * step_adjusted_factor))
            current_bid_price = float(start_price/step_adjusted_factor)
            amount += current_bid_amount
            
            # TODO Create lock
            response = self.exchange.buy(current_bid_amount, current_bid_price)
            print('bid response', response)
            self.remove_reserve(current_bid_amount, BID_RESERVE) 
            # TODO Release lock
            
            current_order += 1
            self.avoid_blocking()

        print('allocated amount', prior_reserve - self.bid_reserved_balance)

    def distribute_initial_orders(self, total_base, total_alt):
        # waiting on vizualization for bids before running it as is
        
        current_price = (float(self.exchange.get_highest_bid()) + float(self.exchange.get_lowest_ask()))/2
        if self.user_interface:
            current_price = self.user_interface.confirm_price(current_price)

        ask_start = current_price + current_price*self.spread/2
        bid_start = current_price - current_price*self.spread/2
        
        self.distribute_bids(bid_start, total_base)
        self.distribute_asks(ask_start, total_alt)


    def distribute_bids(self, price, total_to_distribute, step=1.02):
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

    def detect_low_liquidity(self):
        bid = self.exchange.get_highest_bid()
        ask = self.exchange.get_lowest_ask()

        current_price = (bid + ask)/2
        spread_percent = 2(current_price - bid)/current_price

        if spread_percent > .05:
            return True

        acceptable_liquidity = self.check_acceptable_liquidity(current_price)
        
        if not acceptable_liquidity:
            return True

    
    def check_acceptable_liquidity(self, current_price):
        acceptable_bid_price = current_price * .95
        acceptable_ask_price = current_price * 1.05
        accepted_bid_liquidity = 0
        accepted_ask_liquidity = 0
        orders = self.exchange.get_all_orders()
        for order in orders['bids']:
            if order[PRICE] > acceptable_bid_price:
                accepted_bid_liquidity += order['amount']
        for order in orders['asks']:
            if order[PRICE] < acceptable_ask_price:
                accepted_ask_liquidity += order['amount']
        if accepted_bid_liquidity > 200 and accepted_ask_liquidity > 200:
            return True
        else:
            return False


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


    def decaying_ask_ladder(self, total_amount, step, start_price):
        # Places an ask ladder from the start_price to 2x the start_price.
        # The last order in the ladder is half the amount of the first
        # order in the ladder. The amount allocated at each step decays as
        # orders are placed.
        # Abandon all hope, ye who enter here. This function uses black magic (math).

        scaling_factor = 0
        total_orders = floor(math.log(2, step)) # 277 for a step of 1.0025
        current_order = 0

        # Calculate scaling factor
        while current_order < total_orders:
            scaling_factor += 1/(step**current_order)
            current_order += 1

        current_order = 0
        amount = 0

        prior_reserve = self.ask_reserved_balance
        while current_order < total_orders:
            step_adjusted_factor = step**current_order
            current_ask_amount = total_amount/(scaling_factor * step_adjusted_factor)
            current_ask_price = start_price*step_adjusted_factor
            amount += current_ask_amount

            # TODO Create lock
            response = self.exchange.sell(current_ask_amount, current_ask_price)
            print('ask response', response)
            self.remove_reserve(current_ask_amount, ASK_RESERVE) 
            # TODO Release lock

            current_order += 1
            self.avoid_blocking()

        #print(amount)
        print('allocated amount', prior_reserve - self.ask_reserved_balance)


    def distribute_asks(self, price, total_to_distribute, step=1.02):
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
        print("Update entered")
        
        now = str(datetime.datetime.now().isoformat()[:-7].replace("T", " "))
        last_trade_price = self.exchange.get_last_trade_price()

        current_history = self.exchange.get_my_trade_history()
        last_order = get_last_order(self.mutex_UUID)
        new_history = get_new_history(current_history, last_order)

        print('update: new_history', new_history)
        new_transactions = []
        
        if len(new_history) > 0:
            # We have new transactions
            if DEBUG: print("New transactions: " + str(new_history))
            new_transactions = self.rebalance_orders(new_history)
            #self.merge_orders()
            
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

    def avoid_blocking(self):
        if self.user_interface:
            try:
                self.user_interface.app.update_idletasks()
                self.user_interface.app.update()
            except UnicodeDecodeError:
                print("Caught Scroll Error")
            except:
                pass
