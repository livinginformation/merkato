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


def create_price_data(orders, order):
	price_data             = {}
	price_data['total']    = float(orders[order]["total"])
	price_data['amount']   = float(orders[order]["amount"])
	price_data['order_id'] = orders[order]["id"]
	price_data['type']     = orders[order]["type"]
	return price_data