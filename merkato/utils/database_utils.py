import sqlite3

from pprint import pprint

def create_merkatos_table():
    ''' TODO: Function Comment
    '''
    try:
        conn = sqlite3.connect('merkato.db')

    except Exception as e:
        print(str(e))
        
    finally:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS merkatos
                    (exchange text, exchange_pair text, base text, alt text, spread float, profit_limit integer, last_order text, first_order text, ask_reserved_balance float, bid_reserved_balance float, profit_margin integer, base_partials_balance integer, quote_partials_balance integer)''')
        c.execute('''CREATE UNIQUE INDEX id_exchange_pair ON merkatos (exchange_pair)''')
        conn.commit()
        conn.close()


def no_merkatos_table_exists():
    ''' TODO: Function Comment
    '''
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


def insert_merkato(exchange, exchange_pair='tuxBTC_ETH', base='BTC', alt='XMR', spread='.1', bid_reserved_balance=0, ask_reserved_balance=0, first_order='', profit_limit=10, last_order='', profit_margin=0):
    ''' TODO: Function Comment
    '''
    try:
        conn = sqlite3.connect('merkato.db')

    except Exception as e:
        print(str(e))

    finally:
        c = conn.cursor()
        c.execute("""REPLACE INTO merkatos 
                    (exchange, exchange_pair, base, alt, spread, profit_limit, last_order, first_order, ask_reserved_balance, bid_reserved_balance, profit_margin, base_partials_balance, quote_partials_balance) VALUES (?,?,?,?,?,?,?,?,?,?,?)""", 
                    (exchange, exchange_pair, base, alt, spread, profit_limit, last_order, first_order, ask_reserved_balance, bid_reserved_balance, profit_margin, 0, 0))
        conn.commit()
        conn.close()


def update_merkato(exchange_pair, key, value):
    ''' TODO: Function Comment
    '''
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


def kill_merkato(UUID):
    ''' TODO: Function Comment
    '''
    try:
        conn = sqlite3.connect('merkato.db')

    except Exception as e:
        print(str(e))

    finally:
        c = conn.cursor()
        c.execute('''DELETE FROM merkatos WHERE exchange_pair = ?''', (UUID,))
        conn.commit()
        conn.close()


def get_all_merkatos():
    ''' TODO: Function Comment
    '''
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
    ''' TODO: Function Comment
    '''
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
    ''' TODO: Function Comment
    '''
    try:
        conn = sqlite3.connect('merkato.db')

    except Exception as e:
        print(str(e))

    finally:
        c = conn.cursor()
        c.execute("""REPLACE INTO exchanges 
                    (exchange, public_api_key, private_api_key, limit_only) VALUES (?,?,?,?)""", 
                    (exchange, public_api_key, private_api_key, limit_only))
        conn.commit()
        conn.close()


def update_exchange(exchange, key, value):
    ''' TODO: Function Comment
    '''
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
    ''' TODO: Function Comment
    '''
    try:
        conn = sqlite3.connect('merkato.db')
        conn.row_factory = sqlite3.Row

    except Exception as e:
        print(str(e))

    finally:
        c = conn.cursor()
        c.execute("SELECT * FROM exchanges")
        all_exchanges = c.fetchall()
        conn.commit()
        conn.close()
        exchange_index = {config["exchange"]:dict(config) for config in all_exchanges}
        exchange_menu = [name for name,config in exchange_index.items()]
        pprint(exchange_index)

        return exchange_menu, exchange_index


def get_exchange(exchange):
    ''' TODO: Function Comment
    '''
    try:
        conn = sqlite3.connect('merkato.db')
        conn.row_factory = dict_factory

    except Exception as e:
        print(str(e))

    finally:
        c = conn.cursor()
        c.execute('''SELECT * FROM exchanges WHERE exchange = ?''', (exchange,))
        exchange = c.fetchall()[0]
        conn.commit()
        conn.close()

        return exchange


def exchange_exists(exchange):
    ''' TODO: Function Comment
    '''
    try:
        conn = sqlite3.connect('merkato.db')

    except Exception as e:
        print(str(e))

    finally:
        c = conn.cursor()
        c.execute('''SELECT * FROM exchanges WHERE exchange = ?''', (exchange,))
        result = len(c.fetchall())

        conn.commit()
        conn.close()

        return result > 0


def merkato_exists(UUID):
    ''' TODO: Function Comment
    '''
    try:
        conn = sqlite3.connect('merkato.db')

    except Exception as e:
        print(str(e))

    finally:
        c = conn.cursor()
        c.execute('''SELECT * FROM merkatos WHERE exchange_pair = ?''', (UUID,))
        result = len(c.fetchall())
        conn.commit()
        conn.close()

        return result > 0


def no_exchanges_table_exists():
    ''' TODO: Function Comment
    '''
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


def get_merkato(exchange_name_pair):
    ''' TODO: Function Comment
    '''
    try:
        conn = sqlite3.connect('merkato.db')

    except Exception as e:
        print(str(e))

    finally:
        c = conn.cursor()
        c.execute('''SELECT * FROM merkatos WHERE exchange_pair = ?''', (exchange_name_pair,))
        exchange = c.fetchall()[0]
        conn.commit()
        conn.close()

        return exchange


def get_merkatos_by_exchange(exchange):
    ''' TODO: Function Comment
    '''
    try:
        conn = sqlite3.connect('merkato.db')
        conn.row_factory = dict_factory

    except Exception as e:
        print(str(e))

    finally:
        c = conn.cursor()
        c.execute('''SELECT * FROM merkatos WHERE exchange = ?''', (exchange,))
        exchanges = c.fetchall()
        conn.commit()
        conn.close()

        return exchanges


def remove_base_partial(UUID, amount)
pass


def remove_quote_partial(UUID, amount)
pass


# I realize this could be done with negative values. For readability's sake,
# i'm implementing it so you never need to pass in a negative number.
def add_base_partial(UUID, amount)
pass


def add_quote_partial(UUID, amount)
pass


def dict_factory(cursor, row):
    ''' TODO: Function Comment
    '''
    d = {}

    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]

    return d
