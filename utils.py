def updateConfigWithCredentials(config):
	print("API Credentials needed")
	public_key  = input("Public Key: ")
	private_key = input("Private Key: ")
	config['publickey'] = public_key
	config['privatekey'] = private_key

def getExchange():
	print("What exchange is this config file for?")
	print("1. TuxExchange")
	print("2. Poloniex")
	print("3. Bittrex")
	return input("Selection: ")

def getConfigSelection():
	print("Please make a selection:")
	print("1. Create new configuration")
	print("2. Load existing configuration")
	print("3. Exit")
	return input("Selection: ")
