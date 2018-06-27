import argparse
from merkato.constants import known_exchanges, implemented_exchanges
import json
import os.path


def skip(args):
    return None

def new(args):
    print("...Generating New Config File...")
    config = {}

    if args.exchange not in implemented_exchanges:
        raise NotImplementedError("Exchange is not yet available for use: {}".format(args.exchange))
    else:
        config.update({"exchange": args.exchange})

    config.update({"privatekey": args.privatekey[0],
                   "publickey": args.publickey[0]})

    if os.path.isfile(args.outfile[0]):
        raise FileExistsError("Proposed filename exists: {}".format(args.outfile[0]))
    else:
        with open(args.outfile[0], "w+") as f:
            json.dump(config, f)
            print("written to {}".format(args.outfile[o]))
            return config

def load(args):
    return json.load(args.infile[0])

def parse():
    parser = argparse.ArgumentParser()
    parser.set_defaults(func=skip)
    subparsers = parser.add_subparsers(help='sub-command help')

    parser_load = subparsers.add_parser('load', help='load config file for existing merkato')
    parser_load.add_argument('infile', nargs=1, type=argparse.FileType("r"), help='existing config JSON file')
    parser_load.set_defaults(func=load)

    parser_new = subparsers.add_parser('new', help='create new merkato/config')
    parser_new.add_argument('-x', '--exchange', choices=[k for k, v in known_exchanges.items()], required=True)
    parser_new.add_argument('-o', '--outfile', nargs=1, required=True, help="new config file name")
    parser_new.add_argument('-p', '--publickey', nargs=1, required=True, help="exchange API public key")
    parser_new.add_argument('-s', '--privatekey', nargs=1, required=True, help="exchange API private key")
    parser_new.set_defaults(func=new)

    args = parser.parse_args()
    config  = args.func(args)
    return config

if __name__ == "__main__":
    from pprint import pprint
    print("------------\nTesting parser:\n")
    config = parse()
    # print(type(config))
    # pprint(config)
    print("\n----------- End of test--------")