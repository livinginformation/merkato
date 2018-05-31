import json
from merkato.exchanges.test_exchange.exchange import TestExchange
from merkato.exchanges.tux_exchange.exchange import TuxExchange
from merkato.constants import known_exchanges
from merkato.utils.database_utils import get_exchange as get_exchange_from_db

def update_config_with_credentials(config):
	print("API Credentials needed")
	public_key  = input("Public Key: ")
	private_key = input("Private Key: ")
	config['publickey'] = public_key
	config['privatekey'] = private_key


def get_exchange():
	print("What exchange is this config file for?")
	print("1. for TuxExchange type 'tux'")
	print("2. for Poloniex type 'polo'")
	print("3. for Bittrex type 'bit'")
	print("3. for TestExchange type 'test'")
	selection = input("Selection: ")
	if selection not in known_exchanges:
		print('selected exchange not supported, try again')
		return get_exchange()
	return selection


def get_config_selection():
	print("Please make a selection:")
	print("1 -> Create new configuration")
	print("2 -> Load existing configuration")
	print("3 -> Exit")
	return input("Selection: ")

def create_price_data(orders, order):
	price_data             = {}
	price_data['total']    = float(orders[order]["total"])
	price_data['amount']   = float(orders[order]["amount"])
	price_data['order_id'] = orders[order]["id"]
	price_data['type']     = orders[order]["type"]
	return price_data

def validate_merkato_initialization(configuration, coin, base, spread):
	if all (keys in configuration for keys in ("publickey","exchange", "privatekey", "limit_only")):
		return
	raise ValueError('config does not contain needed values.')


def get_relevant_exchange(exchange_name):
	exchange_classes = {
		'tux': TuxExchange,
		'test': TestExchange
	}
	return exchange_classes[exchange_name]

def generate_complete_merkato_configs(merkato_tuples):
	merkato_complete_configs = []
	for tuple in merkato_tuples:
		complete_config = {}
		config = {"limit_only": True}
		exchange = get_exchange_from_db(tuple[0])
		
		config['exchange'] = tuple[0]
		config['publickey'] = exchange[1]
		config['privatekey'] = exchange[2]

		complete_config['configuration'] = config
		complete_config['base'] = tuple[2]
		complete_config['coin'] = tuple[3]
		complete_config['spread'] = tuple[4]
		merkato_complete_configs.append(complete_config)

	return merkato_complete_configs