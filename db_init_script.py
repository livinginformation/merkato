from merkato.merkato_config import load_config, get_config, create_config
from merkato.merkato import Merkato
from merkato.parser import parse
from merkato.utils.database_utils import no_merkatos_table_exists, create_merkatos_table, insert_merkato, get_all_merkatos, get_exchange, no_exchanges_table_exists, create_exchanges_table, drop_merkatos_table, drop_exchanges_table
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
        should_drop_merkatos = input('Do you want to drop merkatos? y/n: ')
        if should_drop_merkatos == 'y':
            drop_merkatos_table()
            create_merkatos_table()

    if no_exchanges_table_exists():
        create_exchanges_table()
    else:
        should_drop_exchanges = input('Do you want to drop exchanges? y/n: ')
        if should_drop_exchanges == 'y':
            drop_exchanges_table()
            create_exchanges_table()

    configuration = parse()

    if not configuration:
        configuration = get_config()

    if not configuration:
        raise Exception("Failed to get configuration.")

    base = "BTC"
    coin = "XMR"
    spread = .02
    coin_reserve = 17
    base_reserve = .4

    print("Would you like to start the merkato?")
    print("1. If so, type 'Y'")
    print("2. If not, 'N'")
    should_start = input("Selection: ")
    print('should_start', should_start)
    if should_start != 'Y' and should_start != 'y':
        return False

    merkato = Merkato(configuration, coin, base, spread, base_reserve, coin_reserve)
    context = merkato.update()
    print('context', context)
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
        time.sleep(1)

if __name__ == '__main__':
    main()
