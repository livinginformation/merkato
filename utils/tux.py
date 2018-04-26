from ..constants import tuxURL
import json
import urllib.parse
import hmac
import hashlib

def get_ticker_tux(coin="none"):
	params = { "method": "getticker" }
	response = requests.get(tuxURL, params=params)

	if coin == "none":
		return json.loads(response.text)

	response_json = json.loads(response.text)
	print(response_json[coin])
	return response_json[coin]

def get_24h_volume_tux(coin="none"):
	# Coin is of the form BTC_XYZ, where XYZ is the alt ticker

	params = { "method": "get24hvolume" }
	response = requests.get(tuxURL, params=params)

	if coin == "none":
		return json.loads(response.text)

	response_json = json.loads(response.text)
	print(response_json[coin])
	return response_json[coin]

def get_orders_tux(coin):
	# Coin here is just the ticker XYZ, not BTC_XYZ
	# Todo: Accept BTC_XYZ by stripping BTC_ if it exists

	params = { "method": "getorders", "coin": coin }
	response = requests.get(tuxURL, params=params)

	response_json = json.loads(response.text)
	if DEBUG: print(response_json)
	return response_json

def get_balances_tux(privatekey, publickey, coin='none'):
		print("--> Checking Balances")
		while True:
				try:

						nonce = int(time.time()*1000)
						tuxParams = {"method" : "getmybalances", "nonce":nonce}
						post = urllib.parse.urlencode(tuxParams)
						signature = hmac.new(privatekey.encode('utf-8'), post.encode('utf-8'), hashlib.sha512).hexdigest()
						header = {'Key' : publickey, 'Sign' : signature}
						tuxbalances = requests.post(tuxURL, data=tuxParams, headers=header).json()

						print("test?")
						print(tuxbalances)
						for crypto in tuxbalances:
								print(str(crypto) + ": " + str(tuxbalances[crypto]))

						return tuxbalances

				except:
						print("--> WARNING: Something went wrong when I was checking the balances. Let me try again in 30 seconds")
						time.sleep(30)