from merkato.merkato_config import load_config, get_config, create_config
from merkato.merkato import Merkato
from merkato.parser import parse
from merkato.utils.database_utils import no_merkatos_table_exists, create_merkatos_table, insert_merkato, get_all_merkatos
from merkato.exchanges.tux_exchange.utils import translate_ticker
import sqlite3

def main():
    print("Merkato Alpha v0.1.1\n")


    configuration = parse()
    if not configuration:
        configuration= get_config()


    if not configuration:
        raise Exception("Failed to get configuration.")

    base = "BTC"
    coin = "ETH"
    spread = ".1"
    pair = translate_ticker(coin, base)
    merkato = Merkato(configuration, coin, base, spread)
    if no_merkatos_table_exists():
        create_merkatos_table()
    insert_merkato(configuration['exchange'])
    get_all_merkatos()
    merkato.exchange.get_all_orders()


if __name__ == '__main__':
    main()