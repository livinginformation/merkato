import unittest
from mock import mock, patch, call
from freezegun import freeze_time

from merkato.exchanges.tux_exchange.exchange import TuxExchange

class TuxExchangeTestCase(unittest.TestCase):
	def setUp(self):
		config = {"privatekey": "abc123", "publickey": "456def", "limit_only": False}
		self.exchange = TuxExchange(config)

	@freeze_time('2001-01-01T12:00:00.0000')
	@patch('merkato.exchanges.tux_exchange.requests.post')
	def test_create_signed_request(self, post_mock):
		query_params = {"foo": "bar"}

		self.exchange._create_signed_request(query_params)

		post_mock.assert_called_once_with(
			'https://tuxexchange.com/api', 
			data={
				'foo': 'bar', 
				'nonce': 978350400000
			}, 
			headers={
				'Key': '456def', 
				'Sign': 'fbc8f9574ddab11d841f25f33d02854fe4932c91695611a9262f444220c4eb09ea9544af45a17d398fa623fa983ba47d38cdfe0a65483444f241ef5b9b34c621'
			}, 
			timeout=15
		)

	@patch('merkato.exchanges.tux_exchange.TuxExchange._create_signed_request')
	def test_buy(self, signed_request_mock):
		response = self.exchange.buy(1, 0.001, 'XMR')

		signed_request_mock.assert_called_once_with({
			'method': 'buy', 
			'market': 'BTC', 
			'coin': 'XMR', 
			'amount': '1.00000000', 
			'price': '0.00100000'
		})
		#     @patch('merkato.exchanges.exchange.time.sleep')
	def test_buy__retries_n_times_on_failure(self, _):
		self.exchange.buy.return_value = False

		response = self.exchange.buy(1, 0.001, 'XMR')

		self.assertEqual(len(self.exchange.buy.mock_calls), self.exchange.retries)
		self.assertFalse(response)

	def test_buy__doesnt_retry_on_exception(self):
		self.exchange.buy.side_effect = ValueError

		response = self.exchange.buy(1, 0.001, 'XMR')

		self.exchange.buy.assert_called_once_with(1, 0.001, 'XMR')
		self.assertFalse(response)

    	def test_sell__doesnt_retry_on_exception(self):
		self.exchange.sell.side_effect = ValueError

		response = self.exchange.sell(1, 0.001, 'XMR')

		self.exchange.sell.assert_called_once_with(1, 0.001, 'XMR')
		self.assertFalse(response)
	
    	def test_sell(self):
		self.exchange.sell.return_value = True

		response = self.exchange.sell(1, 0.001, 'XMR')

		self.exchange.sell.assert_called_once_with(1, 0.001, 'XMR')
		self.assertTrue(response)

	@patch('merkato.exchanges.exchange.time.sleep')
	def test_sell__retries_n_times_on_failure(self, _):
		self.exchange.sell.return_value = False

		response = self.exchange.sell(1, 0.001, 'XMR')

		self.assertEqual(len(self.exchange.sell.mock_calls), self.exchange.retries)
		self.assertFalse(response)

if __name__ == "__main__":
	unittest.main()
