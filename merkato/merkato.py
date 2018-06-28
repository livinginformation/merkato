import csv
import datetime
import math
from math import floor
import os
import time

from merkato.constants import BUY, SELL, ID, PRICE, LAST_ORDER, ASK_RESERVE, BID_RESERVE, EXCHANGE, ONE_BITCOIN, \
    ONE_SATOSHI, FIRST_ORDER, MARKET, TYPE
from merkato.utils.database_utils import update_merkato, insert_merkato, merkato_exists, kill_merkato
from merkato.utils import create_price_data, validate_merkato_initialization, get_relevant_exchange, \
    get_allocated_pair_balances, check_reserve_balances, get_last_order, get_new_history, \
    get_first_order, get_time_of_last_order, get_market_results, log_all_methods

import logging
log = logging.getLogger(__name__)

@log_all_methods
class Merkato(object):
    def __init__(self, configuration, coin, base, spread,
                 bid_reserved_balance, ask_reserved_balance,
                 user_interface=None, profit_margin=0, first_order=''):

        validate_merkato_initialization(configuration, coin, base, spread)
        self.initialized = False
        UUID = configuration[EXCHANGE] + "coin={}_base={}".format(coin,base)
        self.mutex_UUID = UUID
        self.distribution_strategy = 1
        self.spread = float(spread)
        self.profit_margin = profit_margin

        # Exchanges have a maximum number of orders every user can place. Due
        # to this, every Merkato has a reserve of coins that are not currently
        # allocated. As the price approaches unallocated regions, the reserves
        # are deployed.
        self.bid_reserved_balance = bid_reserved_balance
        self.ask_reserved_balance = ask_reserved_balance

        # The current sum of all partially filled orders
        self.base_partials_balance = 0
        self.quote_partials_balance = 0

        self.user_interface = user_interface

        exchange_class = get_relevant_exchange(configuration[EXCHANGE])
        self.exchange = exchange_class(configuration, coin=coin, base=base)

        merkato_does_exist = merkato_exists(self.mutex_UUID)

        if not merkato_does_exist:
            log.info("Creating New Merkato")

            self.cancelrange(ONE_SATOSHI, ONE_BITCOIN)

            total_pair_balances = self.exchange.get_balances()

            log.info("total pair balances", total_pair_balances)

            allocated_pair_balances = get_allocated_pair_balances(configuration['exchange'], base, coin)
            funds_available = check_reserve_balances(total_pair_balances, allocated_pair_balances, coin_reserve=ask_reserved_balance, base_reserve=bid_reserved_balance)

            insert_merkato(configuration[EXCHANGE], self.mutex_UUID, base, coin, spread, bid_reserved_balance, ask_reserved_balance, first_order)
            history = self.exchange.get_my_trade_history()

            log.debug('initial history', history)

            if len(history) > 0:
                log.debug('updating history', history[0][ID])
                new_last_order = history[0][ID]
                update_merkato(self.mutex_UUID, LAST_ORDER, new_last_order)
            self.distribute_initial_orders(total_base=bid_reserved_balance, total_alt=ask_reserved_balance)

        else:
            first_order = get_first_order(self.mutex_UUID)
            current_history = self.exchange.get_my_trade_history(first_order)
            last_order = get_last_order(self.mutex_UUID)
            new_history = get_new_history(current_history, last_order)
            self.rebalance_orders(new_history)

        self.initialized = True  # to avoid being updated before orders placed


    def kill(self):
        ''' Cancels all orders and removes references to Merkato in database
        '''
        self.cancelrange(ONE_SATOSHI, ONE_BITCOIN) # Technically not all, but should be good enough
        kill_merkato(self.mutex_UUID)


    def rebalance_orders(self, new_txes):
        # This function places matching orders for all orders that filled fully since last

        factor = self.spread*self.profit_margin/2
        ordered_transactions = new_txes

        log.info('ordered transactions rebalanced: {}'.format(ordered_transactions))

        filled_orders = []
        market_orders = []

        if self.exchange.name == 'tux':
            # Band-aid until tux writes their function
            open_orders = self.exchange.get_my_open_orders()
        
        if self.exchange.name != 'tux':
            self.exchange.process_new_transactions(ordered_transactions)

        for tx in ordered_transactions:

            orderid = tx['orderId']
            tx_id   = tx[ID]
            price   = tx[PRICE]

            filled_amount = float(tx['amount'])
            init_amount   = float(tx['initamount'])

            total_amount = self.get_total_amount(init_amount, orderid)
            amount = float(total_amount)*float((1-factor))

            if self.exchange.name == 'tux':
                partial_fill = orderid in open_orders

            else:
                partial_fill = self.exchange.is_partial_fill(orderid) # todo implement for tux (binance done)

            if partial_fill:
                self.handle_partial_fill(tx[TYPE], filled_amount, tx_id)
                continue

            if orderid in filled_orders:
                self.handle_is_in_filled_orders(tx[TYPE], filled_amount, tx_id)
                continue

            if tx[TYPE] == SELL:
                buy_price = float(price) * ( 1  - self.spread)
                log.info("Found sell {} corresponding buy price: {} amount: {}".format(tx, buy_price, amount))

                market = self.exchange.buy(amount, buy_price)
                # A lock is probably needed somewhere near here in case of unexpected shutdowns

                if market == MARKET:
                    log.info('market buy {}'.format(market))
                    market_orders.append((amount, buy_price, BUY,))

                self.apply_filled_difference(tx, total_amount, SELL)

            if tx[TYPE] == BUY:
                sell_price = float(price) * ( 1  + self.spread)

                log.info("Found buy {} corresponding sell price: {} amount: {}".format(tx, sell_price, amount))

                market = self.exchange.sell(amount, sell_price)
                
                if market == MARKET:
                    log.info('market sell {}'.format(market))
                    market_orders.append((amount, sell_price, SELL,))

                self.apply_filled_difference(tx, total_amount, BUY)

            if market != MARKET: 
                log.info('market != MARKET')
                update_merkato(self.mutex_UUID, LAST_ORDER, tx[ID])

            filled_orders.append(orderid)
            
            first_order = get_first_order(self.mutex_UUID)
            no_first_order = first_order == ''

            if no_first_order:
                update_merkato(self.mutex_UUID, FIRST_ORDER, tx_id)

        for order in market_orders:
            self.handle_market_order(*order)

        self.log_new_transactions(ordered_transactions)
        log.info('ending partials base: {} quote: {}'.format(self.base_partials_balance, self.quote_partials_balance))
        return ordered_transactions


    def apply_filled_difference(self, tx, total_amount, BUY):
        filled_difference = total_amount - float(tx['amount'])
        if filled_difference > 0:
            if tx_type == SELL:
                self.base_partials_balance -= filled_difference * float(tx[PRICE])
                update_merkato(self.mutex_UUID, 'base_partials_balance', self.base_partials_balance)
                log.info('apply_filled_difference base_partials_balance: {}'.format(self.base_partials_balance))
            if tx_type == BUY:
                self.quote_partials_balance -= filled_difference
                update_merkato(self.mutex_UUID, 'quote_partials_balance', self.quote_partials_balance)
                log.info('apply_filled_difference quote_partials_balance: {}'.format(self.quote_partials_balance))


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

            log.info('bid response {}'.format(response))

            self.remove_reserve(current_bid_amount, BID_RESERVE) 
            # TODO Release lock
            
            current_order += 1
            self.avoid_blocking()

        log.info('allocated amount {}'.format(prior_reserve - self.bid_reserved_balance))


    def handle_is_in_filled_orders(self, tx_type, filled_amount, tx_id):
        log.info('{}, orderid in filled_orders filled_amount: {} tx_id: {} '.format(tx_type, filled_amount, tx_id))
        
        if tx_type == BUY:
            self.quote_partials_balance += filled_amount
            update_merkato(self.mutex_UUID, 'quote_partials_balance', self.quote_partials_balance)
        else:
            self.base_partials_balance += filled_amount
            update_merkato(self.mutex_UUID, 'base_partials_balance', self.base_partials_balance)

        update_merkato(self.mutex_UUID, LAST_ORDER, tx_id)


    def distribute_bids(self, price, total_to_distribute, step=1.04):
        # Allocates your market making balance on the bid side, in a way that
        # will never be completely exhausted (run out).
        # total_to_distribute is in the base currency (usually BTC)

        # 2. Call decaying_bid_ladder on that start price, with the given step,
        #    and half the total_to_distribute
        self.decaying_bid_ladder(total_to_distribute/2, step, price)

        # 3. Call decaying_bid_ladder again halving the
        #    start_price, and halving the total_amount
        self.decaying_bid_ladder(total_to_distribute/4, step, price/2)


    def get_total_amount(self, init_amount, orderid):
        if self.exchange.name == "tux":
            return float(init_amount)

        else:
            return self.exchange.get_total_amount(orderid) # todo unimplemented on tux


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
        self.decaying_ask_ladder(total_to_distribute/2, step, price)

        # 3. Call decaying_ask_ladder once more, doubling the
        #    start_price, and halving the total_amount
        self.decaying_ask_ladder(total_to_distribute/4, step, price * 2)


    def distribute_initial_orders(self, total_base, total_alt):
        ''' TODO: Function comment
        '''
        current_price = (float(self.exchange.get_highest_bid()) + float(self.exchange.get_lowest_ask()))/2
        if self.user_interface:
            current_price = self.user_interface.confirm_price(current_price)

        ask_start = current_price + current_price*self.spread/2
        bid_start = current_price - current_price*self.spread/2
        
        self.distribute_bids(bid_start, total_base)
        self.distribute_asks(ask_start, total_alt)


    def handle_partial_fill(self, type, filled_qty, tx_id):
        # This was a buy, so we gained more of the quote asset. 
        # This was a partial fill, so the user's balance is increased by that amount. 
        # However, that amount is 'reserved' (will be placed on the books once the 
        # rest of the order is filled), and therefore is unavailable when creating new
        # Merkatos. Add this amount to a field 'quote_partials_balance'.
        log.info('handle_partial_fill type {} filledqty {} tx_id {}'.format(type, filled_qty, tx_id))
        if type == BUY:
            self.quote_partials_balance += filled_qty # may need a multiply by price
            update_merkato(self.mutex_UUID, 'quote_partials_balance', self.quote_partials_balance)

        elif type == SELL:
            self.base_partials_balance += filled_qty
            update_merkato(self.mutex_UUID, 'base_partials_balance', self.base_partials_balance)

        # 2. update the last order
        update_merkato(self.mutex_UUID, LAST_ORDER, tx_id)


    def handle_market_order(self, amount, price, type):
        log.info('handle market order')
        newest_tx_id = self.exchange.get_my_trade_history()[0][ID]
        if type == BUY:
            self.exchange.market_buy(amount, price)

        elif type == SELL:
            self.exchange.market_sell(amount, price)        

        current_history = self.exchange.get_my_trade_history()
        market_history  = get_new_history(current_history, newest_tx_id)
        market_data     = get_market_results(market_history)

        # The sell gave us some BTC. The buy is executed with that BTC.
        # The market buy will get us X xmr in return. All of that xmr
        # should be placed at the original order's matching price.
        #
        # We need to do something here about the partials if it doesnt fully fill
        amount_executed = float(market_data['amount_executed'])
        price_numerator = float(market_data['price_numerator'])
        last_txid    = market_data['last_txid']
        log.info('market data: {}'.format(market_data))

        market_order_filled = amount == amount_executed
        if market_order_filled:
            self.exchange.sell(amount_executed, price) # Should never market order
        
        else:
            log.info('handle_market_order: partials affected, amount: {} amount_executed: {}'.format(amount, amount_executed))
            if type == BUY:
                self.quote_partials_balance += amount_executed
                update_merkato(self.mutex_UUID, 'quote_partials_balance', self.quote_partials_balance)
                log.info('market buy partials after'.format(self.quote_partials_balance))
            else:
                self.base_partials_balance += amount_executed * price_numerator
                update_merkato(self.mutex_UUID, 'base_partials_balance', self.base_partials_balance)
                log.info('market sell partials after {}'.format(self.base_partials_balance))
        # A market buy occurred, so we need to update the db with the latest tx
        update_merkato(self.mutex_UUID, LAST_ORDER, last_txid)


    def update(self):
        ''' TODO: Function comment
        '''
        log.info("Update entered")
        
        now = str(datetime.datetime.now().isoformat()[:-7].replace("T", " "))
        last_trade_price = self.exchange.get_last_trade_price()

        first_order = get_first_order(self.mutex_UUID)
        last_order  = get_last_order(self.mutex_UUID)
        
        current_history = self.exchange.get_my_trade_history(first_order)
        new_history = get_new_history(current_history, last_order)
        log.debug('first_order', first_order)
        log.debug('last_order', last_order)
        log.debug('new_history', new_history)
        new_transactions = []
        
        if len(new_history) > 0:
            log.info('we have new history')
            log.debug("New transactions: {}".format(new_history))

            new_transactions = self.rebalance_orders(new_history)
            #self.merge_orders()
            # todo: Talk about whether merging 'close enough' orders is reasonable. 
            
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
        ''' TODO: Function comment
            This will be necessary when we remove orders lower on the books so we can place more orders higher.
        '''
        pass


    def remove_reserve(self, amount, type_of_reserve):
        ''' TODO: Function comment
        '''
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
        ''' TODO: Function comment
        '''
        open_orders = self.exchange.get_my_open_orders()
        for order in open_orders:
            price = open_orders[order][PRICE]
            order_id = open_orders[order][ID]
            if float(price) >= float(start) and float(price) <= float(end):
                self.exchange.cancel_order(order_id)

                log.debug("price: {}".format(price))

                time.sleep(.3)


    def avoid_blocking(self):
        ''' TODO: Function comment
        '''
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
