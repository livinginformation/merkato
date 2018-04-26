from constants import tuxURL, poloURL

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

def get_ticker_tux(coin="none"):
	params = { "method": "getticker" }
	response = requests.get(tuxURL, params=params)

	if coin == "none":
		return json.loads(response.text)

	response_json = json.loads(response.text)
	print(response_json[coin])
	return response_json[coin]


def get_ticker_polo(coin="none"):
	params = { "command": "returnTicker" }
	response = requests.get(poloURL, params=params)

	if coin == "none":
		return json.loads(response.text)

	response_json = json.loads(response.text)
	print(response_json[coin])
	return response_json[coin]

	pass


def get_ticker(exchange, coin="none"):
	# Coin is of the form BTC_XYZ, where XYZ is the alt ticker
	if exchange == "tux":
		return getticker_tux(coin)

	elif exchange == "poloniex":
		return getticker_polo(coin)

	else:
		print("Exchange currently not supported.")

def get_24h_volume_tux(coin="none"):
	# Coin is of the form BTC_XYZ, where XYZ is the alt ticker

	params = { "method": "get24hvolume" }
	response = requests.get(tuxURL, params=params)

	if coin == "none":
		return json.loads(response.text)

	response_json = json.loads(response.text)
	print(response_json[coin])
	return response_json[coin]


def get_24h_volume_polo(coin="none"):
	# Coin is of the form BTC_XYZ, where XYZ is the alt ticker

	params = { "command": "return24hVolume" }
	response = requests.get(poloURL, params=params)

	if coin == "none":
		return json.loads(response.text)

	response_json = json.loads(response.text)
	print(response_json[coin])
	return response_json[coin]



def get_24h_volume(exchange, coin="none"):
	# Coin is of the form BTC_XYZ, where XYZ is the alt ticker
	if exchange == "tux":
		return get24hvolume_tux(coin)

	elif exchange == "poloniex":
		return get24hvolume_polo(coin)

	else:
		print("Exchange currently not supported.")

def get_orders_tux(coin):
	# Coin here is just the ticker XYZ, not BTC_XYZ
	# Todo: Accept BTC_XYZ by stripping BTC_ if it exists

	params = { "method": "getorders", "coin": coin }
	response = requests.get(tuxURL, params=params)

	response_json = json.loads(response.text)
	if DEBUG: print(response_json)
	return response_json


def get_orders_polo(coin):
	# Coin here is just the ticker XYZ, not BTC_XYZ
	# Todo: Accept BTC_XYZ by stripping BTC_ if it exists
	coin = 'BTC_' + coin
	params = { "command": "returnOrderBook", "currencyPair": coin }
	response = requests.get(poloURL, params=params)

	response_json = json.loads(response.text)
	if DEBUG: print(response_json)
	return response_json



def getorders(exchange, coin):
	# Coin here is just the ticker XYZ, not BTC_XYZ
	# Todo: Accept BTC_XYZ by stripping BTC_ if it exists

	if exchange == "tux":
		return get_orders_tux(coin)

	elif exchange == "poloniex":
		return get_orders_polo(coin)

	else:
		print("Exchange currently not supported.")

    def _getBalances_tux(self, coin='none'):
        print("--> Checking Balances")
        while True:
            try:

                nonce = int(time.time()*1000)
                tuxParams = {"method" : "getmybalances", "nonce":nonce}
                post = urllib.parse.urlencode(tuxParams)
                signature = hmac.new(self.privatekey.encode('utf-8'), post.encode('utf-8'), hashlib.sha512).hexdigest()
                header = {'Key' : self.publickey, 'Sign' : signature}
                tuxbalances = requests.post(tuxURL, data=tuxParams, headers=header).json()

                print("test?")
                print(tuxbalances)
                for crypto in tuxbalances:
                    print(str(crypto) + ": " + str(tuxbalances[crypto]))

                return tuxbalances

            except:
                print("--> WARNING: Something went wrong when I was checking the balances. Let me try again in 30 seconds")
                time.sleep(30)


    def getBalances(self, coin='none'):
        if self.exchange == "tux":
            return self._getBalances_tux(coin)

        else:
            print("Exchange currently unsupported.")

