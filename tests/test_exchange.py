import unittest
from mock import Mock, patch, call

from merkato.exchanges.exchange import Exchange

class ExchangeTestCase(unittest.TestCase):
    def setUp(self):
        configuration = {"exchange": "tux", "privatekey": "abc123", "publickey": "def456"}
        self.exchange = Exchange(configuration)
        self.exchange.interface = Mock()

    def test_init__requires_exchange_specified(self):
        configuration = {"foo": "bar"}
        with self.assertRaises(KeyError):
            exchange = Exchange(configuration)

    def test_init__raises_on_unsupported_exchange(self):
        configuration = {"exchange": "fake-exchange"}
        with self.assertRaises(Exception):
            exchange = Exchange(configuration)

    def test_sell(self):
        self.exchange.interface.sell.return_value = True

        response = self.exchange.sell(1, 0.001, 'XMR')

        self.exchange.interface.sell.assert_called_once_with(1, 0.001, 'XMR')
        self.assertTrue(response)

    @patch('merkato.exchanges.exchange.time.sleep')
    def test_sell__retries_n_times_on_failure(self, _):
        self.exchange.interface.sell.return_value = False

        response = self.exchange.sell(1, 0.001, 'XMR')

        self.assertEqual(len(self.exchange.interface.sell.mock_calls), self.exchange.retries)
        self.assertFalse(response)

    def test_sell__doesnt_retry_on_exception(self):
        self.exchange.interface.sell.side_effect = ValueError

        response = self.exchange.sell(1, 0.001, 'XMR')

        self.exchange.interface.sell.assert_called_once_with(1, 0.001, 'XMR')
        self.assertFalse(response)

    def test_buy(self):
        self.exchange.interface.buy.return_value = True

        response = self.exchange.buy(1, 0.001, 'XMR')

        self.exchange.interface.buy.assert_called_once_with(1, 0.001, 'XMR')
        self.assertTrue(response)

    @patch('merkato.exchanges.exchange.time.sleep')
    def test_buy__retries_n_times_on_failure(self, _):
        self.exchange.interface.buy.return_value = False

        response = self.exchange.buy(1, 0.001, 'XMR')

        self.assertEqual(len(self.exchange.interface.buy.mock_calls), self.exchange.retries)
        self.assertFalse(response)

    def test_buy__doesnt_retry_on_exception(self):
        self.exchange.interface.buy.side_effect = ValueError

        response = self.exchange.buy(1, 0.001, 'XMR')

        self.exchange.interface.buy.assert_called_once_with(1, 0.001, 'XMR')
        self.assertFalse(response)

    def test_get_all_orders(self):
        response = self.exchange.get_all_orders('XMR')
        
    def test_get_my_open_orders(self):
        response = self.exchange.get_my_open_orders()

    def test_get_my_trade_history(self):
        response = self.exchange.get_my_trade_history(0, 0)

    def test_cancel_order(self):
        response = self.exchange.cancel_order(12345)
