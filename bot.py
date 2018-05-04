from merkato.merkato_config import load_config, get_config, create_config
from merkato.merkato import Merkato
from merkato.parser import parse
import sqlite3

def create_mutex_table():
    try:
        conn = sqlite3.connect('merkato.db')
    except Exception as e:
        print(str(e))
    finally:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS mutexes
                    (exchange text, pair text, spread text, profit_limit integer, last_order text)''')
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


def insert_or_update_mutex(exchange, pair='BTC/XMR', spread='.1', profit_limit=10, last_order=''):
    try:
        conn = sqlite3.connect('merkato.db')
    except Exception as e:
        print(str(e))
    finally:
        c = conn.cursor()
        c.execute("""INSERT INTO mutexes 
                    (exchange, pair, spread, profit_limit, last_order) VALUES (?,?,?,?,?)""", 
                    (exchange, pair, spread, profit_limit, last_order))
        conn.commit()
        conn.close()

def main():
    print("Merkato Alpha v0.1.1\n")


    configuration = parse()
    if not configuration:
        configuration= get_config()


    if not configuration:
        raise Exception("Failed to get configuration.")

    ticker = "BTC"
    spread = ".1"
    ask_budget = 1
    bid_budget = 1 
    merkato = Merkato(configuration, ticker, spread, ask_budget, bid_budget)
    if no_mutex_table_exists():
        create_mutex_table()
    insert_or_update_mutex(configuration['exchange'])
    merkato.exchange.get_all_orders(ticker)


if __name__ == '__main__':
    main()
