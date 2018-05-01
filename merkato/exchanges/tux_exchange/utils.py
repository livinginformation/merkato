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