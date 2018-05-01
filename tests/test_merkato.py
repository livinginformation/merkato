import unittest
from mock import Mock, patch, call

from merkato.merkato import Merkato

class MerkatoTestCase(unittest.TestCase):
	def setUp(self):
		config = {"exchange": "tux", "privatekey": "abc123", "publickey": "def456", "limit_only": False}
		self.merkato = Merkato(config, ticker='XMR', spread='15', ask_budget=10, bid_budget=10)

	def test_create_bid_ladder(self):
		pass

	def test_create_ask_ladder(self):
		pass

	def test_merge_orders(self):
		pass

	def test_update_order_book(self):
		pass

	def test_cancelrange(self):
		pass
