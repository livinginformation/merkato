from merkato import merkato_config as config
from merkato.merkato import Merkato


def create_mutex_table():
    conn = sqlite3.connect('merkato.db')

    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS mutexes
                 (pair text, exchange text, owner text)''')

    conn.commit()
    conn.close()


def main():
    print("Merkato Alpha v0.1.1\n")

    configuration = config.get_config()

    if not configuration:
        raise Exception("Failed to get configuration.")

    print(configuration)
    merkato = Merkato(configuration)

    merkato.exchange.get_all_orders()


if __name__ == '__main__':
    main()
