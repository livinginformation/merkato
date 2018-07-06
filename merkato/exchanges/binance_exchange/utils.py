from binance.client import Client

import logging
log = logging.getLogger(__name__)


def validate_keys(config):
    print('config', config)
    public_key = config["public_api_key"]
    private_key = config["private_api_key"]
    client = Client(public_key, private_key, )

    try:
        response = client.get_open_orders(symbol='ETHBTC', recvWindow=10000000)
    except Exception as e:
        log.error(e)
        return False

    return True