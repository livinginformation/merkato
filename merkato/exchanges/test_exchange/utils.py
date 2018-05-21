def create_order(user_id, amount, price):
    return {
        "user_id": user_id,
        "amount": amount,
        "price":price
    }

def add_resolved_order(order, resolved_orders, add_ticker, sell_ticker):
    user_id = order.user_id
    resolved_order_amount_to_add = order.price / order.amount

    user_is_not_in_orders = user_id not in resolved_orders
    user_does_not_have_resolved_add_ticker = add_ticker not in  resolved_orders[user_id]
    user_does_not_have_resolved_sell_ticker = sell_ticker not in resolved_orders[user_id]

    if user_is_not_in_orders:
        resolved_orders[user_id] = {} 

    if user_does_not_have_resolved_add_ticker:
        resolved_orders[user_id][add_ticker] = resolved_order_amount_to_add
    else:
        resolved_orders[user_id][add_ticker] += resolved_order_amount_to_add
    
    if user_does_not_have_resolved_sell_ticker:
        resolved_orders[user_id][sell_ticker] = -order.amount
    else:
        resolved_orders[user_id][sell_ticker] -= order.amount
    

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
