import unittest
from mock import patch

from merkato.exchanges.binance_exchange.exchange import BinanceExchange
from binance import enums


class BinanceExchangeTestCase(unittest.TestCase):
    def setUp(self):
        with patch('merkato.exchanges.binance_exchange.exchange.Client'):
            config = {"private_api_key": "abc123", "public_api_key": "456def", "limit_only": False}
            self.exchange = BinanceExchange(config, 'XMR', 'BTC')

    def test_buy(self):
        self.exchange._buy(1.0, 0.01)

        self.exchange.client.create_order.assert_called_once_with(
            symbol='XMRBTC',
            side=enums.SIDE_BUY,
            type=enums.ORDER_TYPE_LIMIT,
            timeInForce=enums.TIME_IN_FORCE_GTC,
            price='0.010000',
            quantity='1.000')

    def test_sell(self):
        self.exchange._sell(1.0, 0.01)

        self.exchange.client.create_order.assert_called_once_with(
            symbol='XMRBTC',
            side=enums.SIDE_SELL,
            type=enums.ORDER_TYPE_LIMIT,
            timeInForce=enums.TIME_IN_FORCE_GTC,
            price='0.010000',
            quantity='1.000')

    def test_get_my_open_orders(self):
        pass

    def test_cancel_order(self):
        pass

    def test_get_balances(self):
        pass

    def test_is_partial_fill(self):
        pass
