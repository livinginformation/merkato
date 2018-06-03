from merkato.merkato_config import load_config, get_config, create_config
from merkato.merkato import Merkato
from merkato.parser import parse
from merkato.utils.database_utils import no_merkatos_table_exists, create_merkatos_table, insert_merkato, get_all_merkatos, get_exchange
from merkato.utils import generate_complete_merkato_configs
import sqlite3
import time
import pprint
from merkato.utils.diagnostics import visualize_orderbook

def main():
    print("Merkato Alpha v0.1.1\n")

    if no_merkatos_table_exists():
        create_merkatos_table()

    configuration = parse()
    if not configuration:
        configuration = get_config()


    if not configuration:
        raise Exception("Failed to get configuration.")

    base = "BTC"
    coin = "ETH"
    spread = ".1"
    coin_reserve = 40
    base_reserve = 40
    merkato = Merkato(configuration, coin, base, spread, coin_reserve, base_reserve)
    merkatos = get_all_merkatos()
    complete_merkato_configs = generate_complete_merkato_configs(merkatos)
    print(complete_merkato_configs)
    print(merkatos)
    while True:
        time.sleep(10)
        context = merkato.update()
        pprint.pprint(context)
        visualize_orderbook(context["orderbook"])

if __name__ == '__main__':
    main()