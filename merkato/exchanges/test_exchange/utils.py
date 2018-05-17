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

def apply_resolved_orders(current_accounts, resolved_orders):
    for user_id, user in resolved_orders.items():
        user_id = user.user_id
        user_is_not_in_accounts = user_id not in current_accounts
        if user_is_not_in_accounts:
            current_accounts[user_id] = {}
        for ticker, amount in user:
            user_does_not_have_ticker = ticker not in  current_accounts[user_id]
            if user_does_not_have_ticker:
                user[ticker] = resolved_orders[user_id][ticker]
            else:
                user[ticker] += resolved_orders[user_id][ticker]




