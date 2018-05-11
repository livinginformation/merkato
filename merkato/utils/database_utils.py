import sqlite3

def create_merkatos_table():
    try:
        conn = sqlite3.connect('merkato.db')
    except Exception as e:
        print(str(e))
    finally:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS merkatos
                    (exchange text, exchange_pair text, pair text, spread text, profit_limit integer, last_order text)''')
        c.execute('''CREATE UNIQUE INDEX id_exchange_pair ON merkatos (exchange_pair)''')
        conn.commit()
        conn.close()

def no_merkatos_table_exists():
    try:
        conn = sqlite3.connect('merkato.db')
    except Exception as e:
        print(str(e))
    finally:
        c = conn.cursor()
        c.execute('''SELECT count(*) FROM sqlite_master WHERE type="table" AND name="merkatos"''')
        number_of_mutex_tables = c.fetchall()[0][0]
        conn.commit()
        conn.close()
        return number_of_mutex_tables == 0


def insert_merkato(exchange, exchange_pair='tuxBTC_ETH', pair='BTC_ETH', spread='.1', profit_limit=10, last_order=''):
    try:
        conn = sqlite3.connect('merkato.db')
    except Exception as e:
        print(str(e))
    finally:
        c = conn.cursor()
        c.execute("""INSERT INTO merkatos 
                    (exchange, exchange_pair, pair, spread, profit_limit, last_order) VALUES (?,?,?,?,?,?)""", 
                    (exchange, exchange_pair, pair, spread, profit_limit, last_order))
        conn.commit()
        conn.close()

def update_merkato(exchange_pair, key, value):
    try:
        conn = sqlite3.connect('merkato.db')
    except Exception as e:
        print(str(e))
    finally:
        c = conn.cursor()
        query = "UPDATE merkatos SET {} = ? WHERE exchange_pair = ?".format(key)
        c.execute(query, (value, exchange_pair) )
        conn.commit()
        conn.close()

def get_all_merkatos():
    try:
        conn = sqlite3.connect('merkato.db')
    except Exception as e:
        print(str(e))
    finally:
        c = conn.cursor()
        c.execute("SELECT * FROM merkatos")
        all_merkatos = c.fetchall()
        conn.commit()
        conn.close()
        return all_merkatos

def create_exchanges_table():
    try:
        conn = sqlite3.connect('merkato.db')
    except Exception as e:
        print(str(e))
    finally:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS exchanges
                    (exchange text, public_api_key text, private_api_key text, limit_only text	)''')
        c.execute('''CREATE UNIQUE INDEX id_exchange ON exchanges (exchange)''')
        conn.commit()
        conn.close()

def insert_exchange(exchange, public_api_key='', private_api_key='', limit_only=True):
    try:
        conn = sqlite3.connect('merkato.db')
    except Exception as e:
        print(str(e))
    finally:
        c = conn.cursor()
        c.execute("""INSERT INTO exchanges 
                    (exchange, public_api_key, private_api_key, limit_only) VALUES (?,?,?,?)""", 
                    (exchange, public_api_key, private_api_key, limit_only))
        conn.commit()
        conn.close()

def update_exchange(exchange, key, value):
    try:
        conn = sqlite3.connect('merkato.db')
    except Exception as e:
        print(str(e))
    finally:
        c = conn.cursor()
        query = "UPDATE exchanges SET {} = ? WHERE exchange = ?".format(key)
        c.execute(query, (value, exchange) )
        conn.commit()
        conn.close()

def get_all_exchanges():
    try:
        conn = sqlite3.connect('merkato.db')
    except Exception as e:
        print(str(e))
    finally:
        c = conn.cursor()
        c.execute("SELECT * FROM exchanges")
        all_exchanges = c.fetchall()
        conn.commit()
        conn.close()
        return all_exchanges

def get_all_exchanges():
    try:
        conn = sqlite3.connect('merkato.db')
    except Exception as e:
        print(str(e))
    finally:
        c = conn.cursor()
        c.execute("SELECT * FROM exchanges")
        all_exchanges = c.fetchall()
        conn.commit()
        conn.close()
        return all_exchanges

def get_exchange(exchange):
    try:
        conn = sqlite3.connect('merkato.db')
    except Exception as e:
        print(str(e))
    finally:
        c = conn.cursor()
        c.execute('''SELECT * FROM exchanges WHERE exchange = ?"''', (exchange))
        exchange = c.fetchall()[0][0]
        conn.commit()
        conn.close()
        return exchange

def no_exchanges_table_exists():
    try:
        conn = sqlite3.connect('merkato.db')
    except Exception as e:
        print(str(e))
    finally:
        c = conn.cursor()
        c.execute('''SELECT count(*) FROM sqlite_master WHERE type="table" AND name="exchanges"''')
        number_of_exchange_tables = c.fetchall()[0][0]
        conn.commit()
        conn.close()
        return number_of_exchange_tables == 0
