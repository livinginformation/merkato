from merkato.merkato_config import load_config, get_config, create_config
from merkato.merkato import Merkato


def create_mutex_table():
    try:
        conn = sqlite3.connect('merkato.db')
        print("connected to db", sqlite3.version)
    except Error as e:
        print(e)
    finally:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS mutexes
                    (pair text, exchange text, owner text)''')
        conn.commit()
        conn.close()

def main():
    print("Merkato Alpha v0.1.1\n")

    configuration = get_config()

    if not configuration:
        raise Exception("Failed to get configuration.")

    ticker = "BTC"
    spread = ".1"
    ask_budget = 1
    bid_budget = 1 
    merkato = Merkato(configuration, ticker, spread, ask_budget, bid_budget)

    merkato.exchange.get_all_orders(ticker)


if __name__ == '__main__':
    main()
