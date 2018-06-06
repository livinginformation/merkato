from merkato.merkato_config import load_config, get_config, create_config
from merkato.merkato import Merkato
from merkato.parser import parse
from merkato.utils.database_utils import no_merkatos_table_exists, create_merkatos_table, insert_merkato, get_all_merkatos, get_exchange, no_exchanges_table_exists, create_exchanges_table
from merkato.utils import generate_complete_merkato_configs
import sqlite3
import time
import pprint
from merkato.utils.diagnostics import visualize_orderbook

def main():
    print("Merkato Alpha v0.1.1\n")

    if no_merkatos_table_exists():
        create_merkatos_table()
    else:
        print("ERROR: should not find merkatos if new db")

    if no_exchanges_table_exists():
        create_exchanges_table()
    else:
        print("ERROR: should not find exchange table if new db")

    configuration = parse()
    if not configuration:
        configuration = get_config()


    if not configuration:
        raise Exception("Failed to get configuration.")

    base = "BTC"
    coin = "ETH"
    spread = .1
    coin_reserve = 40
    base_reserve = 40

    merkato = Merkato(configuration, coin, base, spread, coin_reserve, base_reserve)
    merkatos = get_all_merkatos()
    complete_merkato_configs = generate_complete_merkato_configs(merkatos)
    print(complete_merkato_configs)
    print(merkatos)
    context = merkato.update()
    visualize_orderbook(context["orderbook"])
    while True:
        context = merkato.update()
        print("\n"*2)
        if context["filled_orders"]:
            print("---- Filled: -----")
            pprint.pprint(context["filled_orders"])
        print("lowest ask:  ", context["orderbook"]["asks"][0])
        print("current price:  ",context["price"][1])
        print("highest bid:  ", context["orderbook"]["bids"][0])
        if context["filled_orders"]:
            visualize_orderbook(context["orderbook"])
        time.sleep(.2)

if __name__ == '__main__':
    main()