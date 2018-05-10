import sqlite3

def create_mutex_table():
		try:
				conn = sqlite3.connect('merkato.db')
		except Exception as e:
				print(str(e))
		finally:
				c = conn.cursor()
				c.execute('''CREATE TABLE IF NOT EXISTS mutexes
										(exchange text, exchange_pair text, pair text, spread text, profit_limit integer, last_order text)''')
				c.execute('''CREATE UNIQUE INDEX id_exchange_pair ON mutexes (exchange_pair)''')
				conn.commit()
				conn.close()

def no_mutex_table_exists():
		try:
				conn = sqlite3.connect('merkato.db')
		except Exception as e:
				print(str(e))
		finally:
				c = conn.cursor()
				c.execute('''SELECT count(*) FROM sqlite_master WHERE type="table" AND name="mutexes"''')
				number_of_mutex_tables = c.fetchall()[0][0]
				conn.commit()
				conn.close()
				return number_of_mutex_tables == 0


def insert_mutex(exchange, exchange_pair='tuxBTC_ETH', pair='BTC_ETH', spread='.1', profit_limit=10, last_order=''):
		try:
				conn = sqlite3.connect('merkato.db')
		except Exception as e:
				print(str(e))
		finally:
				c = conn.cursor()
				c.execute("""INSERT INTO mutexes 
										(exchange, exchange_pair, pair, spread, profit_limit, last_order) VALUES (?,?,?,?,?,?)""", 
										(exchange, exchange_pair, pair, spread, profit_limit, last_order))
				conn.commit()
				conn.close()

def update_mutex(exchange_pair, key, value):
		try:
				conn = sqlite3.connect('merkato.db')
		except Exception as e:
				print(str(e))
		finally:
				c = conn.cursor()
				query = "UPDATE mutexes SET {} = ? WHERE exchange_pair = ?".format(key)
				c.execute(query, (value, exchange_pair) )
				conn.commit()
				conn.close()

def get_all_mutexes():
		try:
				conn = sqlite3.connect('merkato.db')
		except Exception as e:
				print(str(e))
		finally:
				c = conn.cursor()
				c.execute("SELECT * FROM mutexes")
				all_mutexes = c.fetchall()
				conn.commit()
				conn.close()
				return all_mutexes