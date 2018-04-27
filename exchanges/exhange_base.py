from abc import ABC, abstractmethod

class ExchangeBase(ABC):
	"""
	Abstract base class for exchange interfaces. 
	A new exchange can be implemented by overriding all abstract methods and members below;
	it may define additional methods for exchange-specific behavior.
	"""
	url = NotImplemented

	@abstractmethod
	def buy(self, amount, ask, ticker):
		pass

	@abstractmethod
	def sell(self, amount, bid, ticker):
		pass

	@abstractmethod
	def get_my_open_orders(self):
		pass

	@abstractmethod
	def cancel_order(self, order_id):
		pass