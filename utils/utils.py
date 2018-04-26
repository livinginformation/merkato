from tux import get_ticker_tux, get_24h_volume_tux, get_orders_tux, get_balances_tux
from pol import get_ticker_polo, get_24h_volume_polo, get_orders_polo

def update_config_with_credentials(config):
	print("API Credentials needed")
	public_key  = input("Public Key: ")
	private_key = input("Private Key: ")
	config['publickey'] = public_key
	config['privatekey'] = private_key

def get_exchange():
	print("What exchange is this config file for?")
	print("1. TuxExchange")
	print("2. Poloniex")
	print("3. Bittrex")
	return input("Selection: ")

def get_config_selection():
	print("Please make a selection:")
	print("1. Create new configuration")
	print("2. Load existing configuration")
	print("3. Exit")
	return input("Selection: ")

def get_ticker(exchange, coin="none"):
	# Coin is of the form BTC_XYZ, where XYZ is the alt ticker
	if exchange == "tux":
		return get_ticker_tux(coin)

	elif exchange == "poloniex":
		return getticker_polo(coin)

	else:
		print("Exchange currently not supported.")


def get_24h_volume(exchange, coin="none"):
	# Coin is of the form BTC_XYZ, where XYZ is the alt ticker
	if exchange == "tux":
		return get24hvolume_tux(coin)

	elif exchange == "poloniex":
		return get24hvolume_polo(coin)

	else:
		print("Exchange currently not supported.")


def get_orders(exchange, coin):
	# Coin here is just the ticker XYZ, not BTC_XYZ
	# Todo: Accept BTC_XYZ by stripping BTC_ if it exists

	if exchange == "tux":
		return get_orders_tux(coin)

	elif exchange == "poloniex":
		return get_orders_polo(coin)

	else:
		print("Exchange currently not supported.")


def get_balances(exchange, private_key, public_key, coin='none'):
		if exchange == "tux":
				return getBalances_tux(private_key, public_key, coin)

		else:
				print("Exchange currently unsupported.")

