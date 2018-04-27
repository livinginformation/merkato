from merkato.exchanges.exchange_base import ExchangeBase

class TuxExchange(ExchangeBase):
    url = "https://tuxexchange.com/api"

    def sell(self, amount, ask, ticker):
        ''' Places a sell for a number of an asset at the indicated price (0.00000503 for example)
            :param amount: string
            :param ask: float 
            :param ticker: string
        '''
        query_parameters = {
            "method": "sell", 
            "market": "BTC", 
            "coin": ticker, 
            "amount": "{:.8f}".format(amount), 
            "price": "{:.8f}".format(ask)
        }
        response = self._create_signed_request(query_parameters)

        return response['success']


    def buy(self, amount, bid, ticker):
        ''' Places a buy for a number of an asset at the indicated price (0.00000503 for example)
            :param amount: string
            :param bid: float 
            :param ticker: string
        '''
        query_parameters = { 
            "method": "buy", 
            "market": "BTC", 
            "coin": ticker, 
            "amount": "{:.8f}".format(amount), 
            "price": "{:.8f}".format(bid)
        }
        response = self._create_signed_request(query_parameters)

        return response['success']


    def get_my_open_orders(self):
        query_parameters = {
            "method": "getmyopenorders"
        }

        return self._create_signed_request(query_parameters)


    def cancel_order(self, order_id):
        # This function has a stack overflow risk, fix it. Don't use tail recursion.
        if DEBUG: print("--> Cancelling order...")

        if order_id == 0:
            if DEBUG: print("---> Order ID was zero, so bailing on function...")
            return

        query_parameters = { 
            "method": "cancelorder", 
            "market": "BTC", 
            "id": order_id
        }
        response = self._create_signed_request(query_parameters)

        if response['success'] != 0:
            if DEBUG: print("--> Cancel successful")
            return True

        print("--> Cancel error, retrying   ")
        return self.cancel_order(order_id)


    def get_ticker(self, coin="none"):
        params = { "method": "getticker" }
        response = requests.get(tuxURL, params=params)

        if coin == "none":
            return json.loads(response.text)

        response_json = json.loads(response.text)
        print(response_json[coin])
        return response_json[coin]


    def get_24h_volume(coin="none"):
        # Coin is of the form BTC_XYZ, where XYZ is the alt ticker

        params = { "method": "get24hvolume" }
        response = requests.get(tuxURL, params=params)

        if coin == "none":
            return json.loads(response.text)

        response_json = json.loads(response.text)
        print(response_json[coin])
        return response_json[coin]


    def get_orders(self, coin):
        # Coin here is just the ticker XYZ, not BTC_XYZ
        # Todo: Accept BTC_XYZ by stripping BTC_ if it exists

        params = { "method": "getorders", "coin": coin }
        response = requests.get(tuxURL, params=params)

        response_json = json.loads(response.text)
        if DEBUG: print(response_json)
        return response_json


    def get_balances(self, privatekey, publickey, coin='none'):
        tuxParams = {"method" : "getmybalances"}
        
        response = self._create_signed_request(tuxParams)
        print(response)
        for crypto in response:
                print(str(crypto) + ": " + str(response[crypto]))

        return response


    def get_my_trade_history(self, start=0, end=0):
        if DEBUG: print("--> Getting trade history...")

        if start != 0 and end != 0:
            query_parameters = { 
                "method": "getmytradehistory", 
                "start": start, 
                "end": end, 
            }
        else:
            query_parameters = { 
                "method": "getmytradehistory"
            }
        
        return self._create_signed_request(query_parameters)


    def _create_signed_request(self, query_parameters, nonce=None, timeout=15):
        # return response needing signature, nonce created if not supplied
        if not nonce:
            nonce = int(time.time() * 1000)

        query_parameters.update({"nonce": nonce})
        post = urllib.parse.urlencode(query_parameters)

        signature = hmac.new(self.privatekey.encode('utf-8'), post.encode('utf-8'), hashlib.sha512).hexdigest()
        head = {'Key': self.publickey, 'Sign': signature}

        response = requests.post(self.url, data=query_parameters, headers=head, timeout=timeout).json()
        return response
