from merkato.exchanges.test_exchange.utils import create_order, add_resolved_order 

class Orderbook:
    def __init__(self):
        self.bids = []
        self.asks = []
        self.bid_ticker = 'XMR'
        self.ask_ticker = 'BTC'
    
  def addBid(userID, amount, price):
    is_market_order = price > self.asks[0].price
    order = create_order(userID, amount, price)
    self.bids.append(order)
    self.bids = sorted(self.bids, key=lambda bid: bid["price"], reverse=True)
    if is_market_order:
        return self.resolve_market_order()
    
  def addAsk(userID, amount, price):
    is_market_order = price < self.bids[0].price
    # create ask
    order = create_order(userID, amount, price)
    # push ask
    self.asks.append(order)
    # sort asks
    self.asks = sorted(self.asks, key=lambda ask: ask["price"])
    if is_market_order:
        return self.resolve_market_order()
    
  def resolve_market_order():
    resolved_orders = {}
    highest_bid = self.bids[0]
    lowest_ask = self.bids[0]

    while lowest_ask.price > highest_bid
        if highest_bid.amount > lowest_ask.amount
            self.asks.pop(0)
            add_resolved_order(lowest_ask, resolved_orders, self.bid_ticker)
            lowest_ask = self.asks[0]

        if lowest_ask.amount > highest_bid.amount
            self.bids.pop(0)
            add_resolved_order(highest_bid, resolved_orders, self.ask_ticker)
            highest_bid = self.bids[0]
    return resolved_orders
