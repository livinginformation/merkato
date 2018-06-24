import math
import time
from math import floor

import csv
import datetime
import logging
import os

from merkato.constants import BUY, SELL, ID, PRICE, LAST_ORDER, ASK_RESERVE, BID_RESERVE, EXCHANGE, ONE_BITCOIN, \
    ONE_SATOSHI, FIRST_ORDER, MARKET
from merkato.utils import create_price_data, validate_merkato_initialization, get_relevant_exchange, \
    get_allocated_pair_balances, check_reserve_balances, get_last_order, get_new_history, \
    get_first_order, get_market_results, log_all_methods
from merkato.utils.database_utils import update_merkato, insert_merkato, merkato_exists, kill_merkato

log = logging.getLogger(__name__)


@log_all_methods
class Merkato(object):
    def __init__(self, configuration, coin, base, spread,
                 bid_reserved_balance, ask_reserved_balance,
                 user_interface=None, profit_margin=0, first_order=''):

        validate_merkato_initialization(configuration, coin, base, spread)
        self.initialized = False
        UUID = configuration[EXCHANGE] + "coin={}_base={}".format(coin, base)
        self.mutex_UUID = UUID
        self.distribution_strategy = 1
        self.spread = float(spread)
        self.profit_margin = profit_margin
        # Create ladders from the bid and ask bidget here
        self.bid_reserved_balance = bid_reserved_balance
        self.ask_reserved_balance = ask_reserved_balance
        self.user_interface = user_interface
        exchange_class = get_relevant_exchange(configuration[EXCHANGE])
        self.exchange = exchange_class(configuration, coin=coin, base=base)
        merkato_does_exist = merkato_exists(UUID)

        if not merkato_does_exist:
            log.info("Creating New Merkato")
            self.cancelrange(ONE_SATOSHI, ONE_BITCOIN)
            total_pair_balances = self.exchange.get_balances()
            log.info("total pair balances", total_pair_balances)
            allocated_pair_balances = get_allocated_pair_balances(configuration['exchange'], base, coin)
            check_reserve_balances(total_pair_balances, allocated_pair_balances, coin_reserve=ask_reserved_balance,
                                   base_reserve=bid_reserved_balance)
            insert_merkato(configuration[EXCHANGE], UUID, base, coin, spread, bid_reserved_balance,
                           ask_reserved_balance, first_order)
            history = self.exchange.get_my_trade_history()
            if len(history) > 0:
                new_last_order = history[0]['orderId']
                update_merkato(self.mutex_UUID, LAST_ORDER, new_last_order)
            self.distribute_initial_orders(total_base=bid_reserved_balance, total_alt=ask_reserved_balance)

        else:
            # self.history = get_old_history(self.exchange.get_my_trade_history(), self.mutex_UUID)
            first_order = get_first_order(self.mutex_UUID)
            current_history = self.exchange.get_my_trade_history(first_order)
            last_order = get_last_order(self.mutex_UUID)
            new_history = get_new_history(current_history, last_order)
            self.rebalance_orders(new_history)
        self.initialized = True  # to avoid being updated before orders placed

    def kill(self):
        ''' TODO: Function comment
        '''
        # Cancel all orders
        self.cancelrange(ONE_SATOSHI, ONE_BITCOIN)  # Technically not all, but should be good enough

        # Remove references to merkato in db
        kill_merkato(self.mutex_UUID)

    def rebalance_orders(self, new_txes):
        # This function places a matching order for every new transaction since last run
        #
        # profit_margin is a number from 0 to 1 representing the percent of the spread to return
        # to the user's balance before placing the matching order.
        #
        # TODO: Modify so that the parent function only passes in the new transactions, don't
        # do the index check internally.

        # new_history is an array of transactions
        # new_txes is the number of new transactions contained in new_history
        factor = self.spread * self.profit_margin / 2
        ordered_transactions = new_txes
        log.info('ordered transactions rebalanced: {}'.format(ordered_transactions))
        for tx in ordered_transactions:
            log.info('length of ordered_transactions length length: {}'.format(len(ordered_transactions)))
            if tx['type'] == SELL:
                log.info('amount: {}'.format(type(tx['amount']), type(tx[PRICE])))

                amount = float(tx['amount']) * float(tx[PRICE]) * (1 - factor)
                price = float(tx[PRICE])
                buy_price = price * (1 - self.spread)
                log.info("found sell {}; corresponding buy {}".format(tx, buy_price))
                market = self.exchange.buy(amount, buy_price)
                if market == MARKET:
                    log.info('market sell', market)
                    last_order_time = str(int(time.time()))
                    self.exchange.market_buy(amount, buy_price)
                    market_history = self.exchange.get_my_trade_history(start=last_order_time)
                    market_data = get_market_results(market_history)

                    # We have a sell executed. We want to place a matching buy order.
                    # If the whole order is executed, no edge case.
                    # If the order has a remainder, the remainder will be on the books at
                    # the appropriate price. So no problem. 
                    # If the remainder is too small to have a matching order, it could 
                    # disappear, but this is such a minor edge case we can ignore it.
                    # 
                    # The sell gave us some BTC. The buy is executed with that BTC.
                    # The market buy will get us X xmr in return. All of that xmr
                    # should be placed at the original order's matching price.
                    amount_executed = float(market_data['amount_executed'])
                    last_orderid = market_data['last_orderid']
                    log.info('market data: {}'.format(market_data))

                    self.exchange.sell(amount_executed, price)  # Should never market order

                    # A market buy occurred, so we need to update the db with the latest tx
                    update_merkato(self.mutex_UUID, LAST_ORDER, last_orderid)

            if tx['type'] == BUY:
                amount = float(tx['amount']) * float((1 - factor))
                price = tx[PRICE]
                sell_price = float(price) * (1 + self.spread)
                log.info("found buy", tx, "corresponding sell", sell_price)
                market = self.exchange.sell(amount, sell_price)
                if market == MARKET:
                    log.info('market buy {}'.format(market))
                    last_order_time = str(int(time.time()))
                    self.exchange.market_sell(amount, sell_price)
                    market_history = self.exchange.get_my_trade_history(start=last_order_time)
                    market_data = get_market_results(market_history)

                    # We have a buy executed. We want to place a matching sell order.
                    # If the whole order is executed, no edge case.
                    # If the order has a remainder, the remainder will be on the books at
                    # the appropriate price. So no problem. 
                    # If the remainder is too small to have a matching order, it could 
                    # disappear, but this is such a minor edge case we can ignore it.
                    # 
                    # The buy gave us some alt. The sell is executed with that alt.
                    # The market sell will get us X btc in return. All of that btc
                    # should be placed at the original order's matching price.
                    amount_executed = float(market_data['total_gotten'])
                    last_orderid = market_data['last_orderid']
                    log.info('market data {}'.format(market_data))
                    self.exchange.buy(amount_executed, float(price))  # Should never market order

                    # A market buy occurred, so we need to update the db with the latest tx
                    update_merkato(self.mutex_UUID, LAST_ORDER, last_orderid)

            if market != MARKET:
                log.info('market != MARKET market != MARKET')
                update_merkato(self.mutex_UUID, LAST_ORDER, tx['orderId'])

            first_order = get_first_order(self.mutex_UUID)
            no_first_order = first_order == ''
            if no_first_order:
                update_merkato(self.mutex_UUID, FIRST_ORDER, tx['orderId'])

        self.log_new_transactions(ordered_transactions)

        return ordered_transactions

    def decaying_bid_ladder(self, total_amount, step, start_price):
        # Places an bid ladder from the start_price to 1/2 the start_price.
        # The first order in the ladder is half the amount (in the base currency) of the last
        # order in the ladder. The amount allocated at each step decays as
        # orders are placed.
        # Abandon all hope, ye who enter here. This function uses black magic (math).

        scaling_factor = 0
        total_orders = floor(math.log(2, step))  # 277 for a step of 1.0025
        current_order = 0

        # Calculate scaling factor
        while current_order < total_orders:
            scaling_factor += 1 / (step ** current_order)
            current_order += 1

        current_order = 0
        amount = 0

        prior_reserve = self.bid_reserved_balance
        while current_order < total_orders:
            step_adjusted_factor = step ** current_order
            current_bid_amount = float(total_amount / (scaling_factor * step_adjusted_factor))
            current_bid_price = float(start_price / step_adjusted_factor)
            amount += current_bid_amount

            # TODO Create lock
            response = self.exchange.buy(current_bid_amount, current_bid_price)
            log.info('bid response {}'.format(response))
            self.remove_reserve(current_bid_amount, BID_RESERVE)
            # TODO Release lock

            current_order += 1
            self.avoid_blocking()

        log.info('allocated amount', prior_reserve - self.bid_reserved_balance)

    def distribute_bids(self, price, total_to_distribute, step=1.04):
        # Allocates your market making balance on the bid side, in a way that
        # will never be completely exhausted (run out).
        # total_to_distribute is in the base currency (usually BTC)

        # 2. Call decaying_bid_ladder on that start price, with the given step,
        #    and half the total_to_distribute
        self.decaying_bid_ladder(total_to_distribute / 2, step, price)

        # 3. Call decaying_bid_ladder twice more, each time halving the
        #    start_price, and halving the total_amount
        self.decaying_bid_ladder(total_to_distribute / 4, step, price / 2)
        self.decaying_bid_ladder(total_to_distribute / 8, step, price / 4)

        # 4. Store the remainder of total_to_distribute, as well as the final
        #    order placed in decaying_bid_ladder
        pass

    def decaying_ask_ladder(self, total_amount, step, start_price):
        # Places an ask ladder from the start_price to 2x the start_price.
        # The last order in the ladder is half the amount of the first
        # order in the ladder. The amount allocated at each step decays as
        # orders are placed.
        # Abandon all hope, ye who enter here. This function uses black magic (math).

        scaling_factor = 0
        total_orders = floor(math.log(2, step))  # 277 for a step of 1.0025
        current_order = 0

        # Calculate scaling factor
        while current_order < total_orders:
            scaling_factor += 1 / (step ** current_order)
            current_order += 1

        current_order = 0
        amount = 0

        prior_reserve = self.ask_reserved_balance
        while current_order < total_orders:
            step_adjusted_factor = step ** current_order
            current_ask_amount = total_amount / (scaling_factor * step_adjusted_factor)
            current_ask_price = start_price * step_adjusted_factor
            amount += current_ask_amount

            # TODO Create lock
            response = self.exchange.sell(current_ask_amount, current_ask_price)
            log.info('ask response {}'.format(response))
            self.remove_reserve(current_ask_amount, ASK_RESERVE)
            # TODO Release lock

            current_order += 1
            self.avoid_blocking()

        log.info('allocated amount: {}'.format(prior_reserve - self.ask_reserved_balance))

    def distribute_asks(self, price, total_to_distribute, step=1.04):
        # Allocates your market making balance on the ask side, in a way that
        # will never be completely exhausted (run out).

        # 2. Call decaying_ask_ladder on that start price, with the given step,
        #    and half the total_to_distribute
        self.decaying_ask_ladder(total_to_distribute / 2, step, price)

        # 3. Call decaying_ask_ladder twice more, each time doubling the
        #    start_price, and halving the total_amount
        self.decaying_ask_ladder(total_to_distribute / 4, step, price * 2)
        self.decaying_ask_ladder(total_to_distribute / 8, step, price * 4)

        # 4. Store the remainder of total_to_distribute, as well as the final
        #    order placed in decaying_ask_ladder
        pass

    def distribute_initial_orders(self, total_base, total_alt):
        # waiting on vizualization for bids before running it as is

        current_price = (float(self.exchange.get_highest_bid()) + float(self.exchange.get_lowest_ask())) / 2
        if self.user_interface:
            current_price = self.user_interface.confirm_price(current_price)

        ask_start = current_price + current_price * self.spread / 2
        bid_start = current_price - current_price * self.spread / 2

        self.distribute_bids(bid_start, total_base)
        self.distribute_asks(ask_start, total_alt)

    def merge_orders(self):
        # Takes all bids/asks that are at the same price, and combines them.
        #
        # Consider changing semantics from existing_order and order to order and new_order.
        # That is, existing_order currently becomes order, and order becomes new_order.
        # Coin is a string
        # TODO: Make orders/orderbook variables less semantically similar

        orders = self.exchange.get_my_open_orders()

        # Create a dictionary to store our desired orderbook
        orderbook = dict()

        for order in orders:
            log.info('order {}'.format(order))

            price = orders[order][PRICE]
            coin = orders[order]["coin"]
            amount = float(orders[order]["amount"])  # Amount in asset
            total = float(orders[order]["total"])  # Total in BTC
            order_id = orders[order]['id']

            log.debug(orders[order])

            if coin != self.exchange.ticker:
                continue

            if price not in orderbook:

                price_data = create_price_data(orders, order)

                orderbook[price] = price_data
                log.debug("Found new bid at {}".format(price))

            else:

                log.info("Collision at {}".format(price))

                existing_order = orderbook[price]
                existing_order_id = existing_order['id']
                existing_order_type = existing_order['type']
                existing_order_total = float(existing_order['total'])
                existing_order_amount = float(existing_order['amount'])

                # Cancel the colliding orders
                self.exchange.cancel_order(order_id)
                self.exchange.cancel_order(existing_order_id)

                # Update the totals to represent the new totals
                existing_order['total'] = str(existing_order_total + total)
                existing_order['amount'] = str(existing_order_amount + amount)

                # Place a new order on the books with the sum
                if existing_order_type == "buy":
                    log.info("Placing buy for {} - {} of {} at a price of {}".format(
                        existing_order['total'], self.exchange.base, self.exchange.ticker, price
                    ))
                    new_id = self.exchange.buy(float(existing_order['total']) / float(price), float(price),
                                               self.exchange.ticker)

                else:  # existing_order_type is sell
                    log.info("Placing sell for {} - {} of {} at a price of {}".format(
                        existing_order['total'], self.exchange.base, self.exchange.ticker, price
                    ))
                    new_id = self.exchange.sell(float(existing_order['amount']), float(price), self.exchange.ticker)

                if new_id == 0:
                    log.warning("Something went wrong.")
                    return 1
                else:
                    update_merkato(self.mutex_UUID, LAST_ORDER, new_id)

                log.debug("consolidation successful")
                existing_order['id'] = new_id

                log.debug(existing_order)

        log.info("Consolidation Successful")
        return 0

    def update(self):
        # Get current state of trade history before placing orders
        log.info("Update entered")

        now = str(datetime.datetime.now().isoformat()[:-7].replace("T", " "))
        last_trade_price = self.exchange.get_last_trade_price()

        first_order = get_first_order(self.mutex_UUID)
        current_history = self.exchange.get_my_trade_history(first_order)
        last_order = get_last_order(self.mutex_UUID)
        new_history = get_new_history(current_history, last_order)

        new_transactions = []

        if len(new_history) > 0:
            # We have new transactions
            log.info('we have new history')
            log.debug("New transactions: {}".format(new_history))
            new_transactions = self.rebalance_orders(new_history)
            # self.merge_orders()

        # context to be used for GUI plotting
        context = {"price": (now, last_trade_price),
                   "filled_orders": new_transactions,
                   "open_orders": self.exchange.get_my_open_orders(context_formatted=True),
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
                log.debug("price: {}".format(price))
                time.sleep(.3)

    def avoid_blocking(self):
        if self.user_interface:
            try:
                self.user_interface.app.update_idletasks()
                self.user_interface.app.update()
            except UnicodeDecodeError:
                log.info("Caught Scroll Error")
            except:
                pass

    def log_new_transactions(self, newTransactionHistory, path="my_merkato_tax_audit_logs.csv"):
        """
        [
            {'id': '430236', 'date': '2018-05-30 17:03:41', 'type': 'buy', 'price': '0.00000290',
             'amount': '78275.86206896', 'total': '0.22700000', 'fee': '0.00000000', 'feepercent': '0.000',
             'orderId': '86963799', 'market': 'BTC', 'coin': 'PEPECASH', 'market_pair': 'BTC_PEPECASH'},

            {'id': '423240', 'date': '2018-04-22 06:19:19', 'type': 'sell', 'price': '0.00000500',
             'amount': '6711.95200000', 'total': '0.03355976', 'fee': '0.00000000', 'feepercent': '0.000',
             'orderId': '90404882', 'market': 'BTC', 'coin': 'PEPECASH', 'market_pair': 'BTC_PEPECASH'},
            ...
        ]
        """
        scrubbed_history = []
        for dirty_tx in newTransactionHistory:
            scrubbed_tx = dirty_tx.copy()
            for k, v in scrubbed_tx.copy().items():
                if k in ["price", "amount", "total", "fee", "feepercent"]:
                    scrubbed_tx[k] = float(v)
                elif k in ["id", "orderId"]:
                    scrubbed_tx[k] = int(v)
            scrubbed_history.append(scrubbed_tx)

        headers_needed = not os.path.exists(path)

        with open(path, 'a+') as csvfile:
            fieldnames = ['coin', 'market', 'market_pair', 'date', 'type',
                          "id", "orderId", "price", "amount", "total", "fee"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')
            if headers_needed:
                writer.writeheader()
            for tx in scrubbed_history:
                writer.writerow(tx)

    def log_new_cointrackr_transactions(self, newTransactionHistory, path="my_merkato_tax_audit_logs.csv"):
        scrubbed_history = []
        for dirty_tx in newTransactionHistory:
            scrubbed_tx = []
            scrubbed_tx.append(dirty_tx['date'])
            if dirty_tx['type'] == 'buy':
                scrubbed_tx.append(dirty_tx['amount'])
                scrubbed_tx.append(dirty_tx['coin'])
                scrubbed_tx.append(dirty_tx['total'])
                scrubbed_tx.append(dirty_tx['market'])
            else:
                scrubbed_tx.append(dirty_tx['total'])
                scrubbed_tx.append(dirty_tx['market'])
                scrubbed_tx.append(dirty_tx['amount'])
                scrubbed_tx.append(dirty_tx['coin'])
            scrubbed_history.append(scrubbed_tx)

        headers_needed = not os.path.exists(path)

        with open(path, 'a+') as csvfile:
            fieldnames = ['Date', 'Recieved Quantity', "Currency", "Sent Quantity", "Currency"]
            writer = csv.writer(csvfile, extrasaction='ignore')
            if headers_needed:
                writer.writerow(fieldnames)
            for tx in scrubbed_history:
                writer.writerow(tx)
