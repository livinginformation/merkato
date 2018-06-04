import datetime

from merkato.exchanges.test_exchange.constants import BID, ASK
from merkato.constants import BUY, SELL

class Orderbook:
    def __init__(self, bids=[], asks=[]):
        self.bids = bids
        self.asks = asks
        self.bid_ticker = 'XMR'  # TODO: this needs to com from TestExchange
        self.ask_ticker = 'BTC'  # TODO: this needs to com from TestExchange
        self.current_order_id = 1

    def addBid(self, userID, amount, price):
        #is_market_order = price > self.asks[0].price
        order = self.create_order(userID, amount, price, BUY)
        self.bids.append(order)
        self.bids = sorted(self.bids, key=lambda bid: bid["price"], reverse=True)
        #if is_market_order:
        #    return self.resolve_market_order()
    
    def addAsk(self, userID, amount, price):
        # create ask
        order = self.create_order(userID, amount, price, SELL)
        # push ask
        self.asks.append(order)
        # sort asks
        self.asks = sorted(self.asks, key=lambda ask: ask["price"])

        
    def resolve_market_order(self, type, price):
        resolved_orders = []
        highest_bid = self.bids[0]
        lowest_ask = self.asks[0]

        if type == ASK:
            while float(lowest_ask["price"]) < price:
                self.asks.pop(0)
                self.add_resolved_order(lowest_ask, resolved_orders, SELL)
                lowest_ask = self.asks[0]
        else:
            while float(highest_bid["price"]) > price:
                self.bids.pop(0)
                self.add_resolved_order(highest_bid, resolved_orders, BUY)
                highest_bid = self.bids[0]
        return resolved_orders

    def generate_fake_orders(self, price):
        is_bid_market_order = price < self.bids[0]["price"]
        is_ask_market_order = price > self.asks[0]["price"]

        if(is_ask_market_order):
            return self.resolve_market_order(ASK, price)
        elif(is_bid_market_order):
            return self.resolve_market_order(BID, price)

    def add_resolved_order(self, order, resolved_orders):
        # resolved_amount = float(order["price"]) / float(order["amount"])
        # if order_type == BUY:
        #     amount = order["amount"] 
        # # else: amount = resolved_amount

        # new_order['amount'] = amount

        # new_order['total'] = float(order['price']) * float(amount)
    
        # self.current_order_id += 1
        order['date'] = datetime.datetime.now().isoformat(sep=" ")[:-7], 
        resolved_orders.append(order)
    
    def create_order(self, user_id, amount, price, order_type):
        new_order =  {
            'fee': '0.00000000', 
            'feepercent': '0.000',
            "user_id": user_id,
            "price":price,
            'coin': self.bid_ticker,
            'market_pair': self.ask_ticker + '_' + self.bid_ticker,
            'id': self.current_order_id, 
            'orderid': self.current_order_id, 
            'market': 'BTC',
            'type': order_type
        }   

        new_order['amount'] = amount

        new_order['total'] = float(price) * float(amount)
       
        self.current_order_id += 1

        return new_order
