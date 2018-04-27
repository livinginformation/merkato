from merkato.exchanges.exchange_base import ExchangeBase

class PoloExchange(ExchangeBase):
	url = "https://poloniex.com/public"

	def get_ticker(coin="none"):
		params = { "command": "returnTicker" }
		response = requests.get(self.url, params=params)

		if coin == "none":
			return json.loads(response.text)

		response_json = json.loads(response.text)
		print(response_json[coin])
		return response_json[coin]


	def get_24h_volume(coin="none"):
		# Coin is of the form BTC_XYZ, where XYZ is the alt ticker

		params = { "command": "return24hVolume" }
		response = requests.get(self.url, params=params)

		if coin == "none":
			return json.loads(response.text)

		response_json = json.loads(response.text)
		print(response_json[coin])
		return response_json[coin]


	def get_orders(coin):
		# Coin here is just the ticker XYZ, not BTC_XYZ
		# Todo: Accept BTC_XYZ by stripping BTC_ if it exists
		coin = 'BTC_' + coin
		params = { "command": "returnOrderBook", "currencyPair": coin }
		response = requests.get(self.url, params=params)

		response_json = json.loads(response.text)
		if DEBUG: print(response_json)
		return response_json
