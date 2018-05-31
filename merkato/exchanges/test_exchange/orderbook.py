from merkato.exchanges.test_exchange.utils import create_order, add_resolved_order 
from merkato.exchanges.test_exchange.constants import BID, ASK

class Orderbook:
    def __init__(self, bids=[], asks=[]):
        self.bids = bids
        self.asks = asks
        self.bid_ticker = 'XMR'
        self.ask_ticker = 'BTC'
    
    def addBid(self, userID, amount, price):
        is_market_order = price > self.asks[0].price
        order = create_order(userID, amount, price)
        self.bids.append(order)
        self.bids = sorted(self.bids, key=lambda bid: bid["price"], reverse=True)
        if is_market_order:
            return self.resolve_market_order()
    
    def addAsk(self, userID, amount, price):
        # create ask
        order = create_order(userID, amount, price)
        # push ask
        self.asks.append(order)
        # sort asks
        self.asks = sorted(self.asks, key=lambda ask: ask["price"])

        
    def resolve_market_order(self, type, price):
        resolved_orders = {}
        highest_bid = self.bids[0]
        lowest_ask = self.asks[0]

        if type == ASK:
            while lowest_ask < price:
                self.asks.pop(0)
                add_resolved_order(lowest_ask, resolved_orders, self.bid_ticker, self.ask_ticker)
                lowest_ask = self.asks[0]
        else:
            while highest_bid > price:
                self.bids.pop(0)
                add_resolved_order(highest_bid, resolved_orders, self.ask_ticker, self.bid_ticker)
                highest_bid = self.bids[0]
        return resolved_orders

    def generate_fake_orders(self, price):
        is_bid_market_order = price < self.bids[0].price
        is_ask_market_order = price > self.asks[0].price

        if(is_ask_market_order):
            return self.resolve_market_order(ASK, price)
        elif(is_bid_market_order):
            return self.resolve_market_order(BID, price)