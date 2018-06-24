import logging
from binance.client import Client

log = logging.getLogger(__name__)


def validate_keys(config, url):
    print('config', config)
    public_key = config["public_api_key"]
    private_key = config["private_api_key"]
    client = Client(public_key, private_key)

    try:
        response = client.get_open_orders(symbol='ETHBTC')
    except Exception as e:
        log.error(e)
        return False

    return True
