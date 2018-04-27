from merkato.exchanges.tux_exchange import TuxExchange

DEBUG = True

class Exchange(object):
    '''Merkato Market Making Bot Exchange Interface
        This class acts as an entry point for all exchange interfaces.
        handling delegation to the proper exchange interface (tux, polo, etc), retry logic, etc.
    '''
    def __init__(self, configuration):
        self.privatekey = configuration['privatekey']
        self.publickey  = configuration['publickey']
        self.exchange   = configuration['exchange']
        self.DEBUG = 100 # TODO: move to configuration object

        self.interface = None
        if self.exchange == "tux":
            self.interface = TuxExchange()
        else:
            raise Exception("ERROR: unsupported exchange: {}".format(self.exchange))

        self.retries = 5

    def debug(self, level, header, *args):
        if level <= self.DEBUG:
            print("-"*10)
            print("{}---> {}:".format(level, header))
            for arg in args:
                print("\t\t" + repr(arg))
            print("-" * 10)

    def sell(self, amount, ask, ticker):
        attempt = 0
        while attempt < self.retries:
            try:
                success = self.interface.sell(amount, ask, ticker)
                if success:
                    self.debug("SELL {} {} at {} on {}".format(amount, ticker, ask, self.exchange))
                    return success
                else:
                    self.debug("SELL {} {} at {} on {} FAILED - attempt {} of {}".format(amount, ticker, ask, self.exchange, attempt, self.retries))
                    attempt += 1
                    time.sleep(5)
            except Exception as e:  # TODO - too broad exception handling
                self.debug("ERROR", e)
                break


    def buy(self, amount, bid, ticker):
        attempt = 0
        while attempt < self.retries:
            try:
                success = self.interface.buy(amount, bid, ticker)
                if success:
                    self.debug("BUY {} {} at {} on {}".format(amount, ticker, bid, self.exchange))
                    return success
                else:
                    self.debug("BUY {} {} at {} on {} FAILED - attempt {} of {}".format(amount, ticker, bid, self.exchange, attempt, self.retries))
                    attempt += 1
                    time.sleep(5)
            except Exception as e:  # TODO - too broad exception handling
                self.debug("ERROR", e)
                break


    def get_all_open_orders(self, ticker):
        return self.interface.get_all_open_orders(ticker)
        

    def get_my_open_orders(self):
        return self.interface.get_my_open_orders()


    def get_my_trade_history(self, start=0, end=0):
        return self.interface.get_my_trade_history(start, end)


    def cancel_order(self, order_id):
        return self.interface.cancel_order(order_id)


