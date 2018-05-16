def getQueryParameters(type, ticker, amount, price):
    formatted_amount = "{:.8f}".format(amount)
    formatted_price = "{:.8f}".format(price)
    return {
        "method": type,
        "market": "BTC",
        "coin": ticker,
        "amount": formatted_amount,
        "price": formatted_price
    }


def translate_ticker(coin, base):
    if base == "BTC":
        if coin == "ZEC":
            return "BTC_ZEC"
        if coin == "PPC":
            return "BTC_PPC"
        if coin == "EMC":
            return "BTC_EMC"
        if coin == "ICN":
            return "BTC_ICN"
        if coin == "POT":
            return "BTC_POT"
        if coin == "NMC":
            return "BTC_NMC"
        if coin == "DOGE":
            return "BTC_DOGE"
        if coin == "BCY":
            return "BTC_BCY"
        if coin == "LTC":
            return "BTC_LTC"
        if coin == "DASH":
            return "BTC_DASH"
        if coin == "ETH":
            return "BTC_ETH"
        if coin == "BLK":
            return "BTC_BLK"
        if coin == "DTB":
            return "BTC_DTB"
        if coin == "DCR":
            return "BTC_DCR"
        if coin == "GNT":
            return "BTC_GNT"
        if coin == "PEPECASH":
            return "BTC_PEPECASH"
        if coin == "SYS":
            return "BTC_SYS"
        if coin == "XCP":
            return "BTC_XCP"
        if coin == "XMR":
            return "BTC_XMR"

    raise NotImplementedError("Unknown pair: coin={}, base={}".format(coin, base))

def create_order(user_id, amount, price):
    return {
        "user_id": user_id,
        "amount": amount,
        "price":price
    }

def add_resolved_order(order, resolved_orders, ticker):
    user_id = order.user_id
    resolved_order_amount = order.price / order.amount

    user_is_not_in_orders = user_id not in resolved_orders
    user_does_not_have_resolved_ticker = ticker not in  resolved_orders[user_id]

    if user_is_not_in_orders:
        user = create_user(user_id, resolved_order_amount)
        resolved_orders[user_id] = user 
    else if user_does_not_have_resolved_ticker:
        resolved_orders[user_id][ticker] = resolved_order_amount
    else:
        resolved_orders[user_id][ticker] += resolved_order_amount

def create_user(user_id, resolved_order_amount):
    return {
        "user_id": user_id,
        "resolved_order_amount": resolved_order_amount
    }