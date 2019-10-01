import argparse
import json
import os, sys
import pprint




def get_config(config_filename =""):
    parser = argparse.ArgumentParser(description="Object reconstruction system")
    parser.add_argument("--config", default=config_filename, help="path to the config file")
    args = parser.parse_args()
    print("Using config path: [{}]".format(args.config))
    print("Parsed args:", args)

    assert os.path.exists(args.config), \
        "Path %s is not exist!" % args.config

    with open(args.config) as json_file:
        config = json.load(json_file)
        print("Using config: ")
        print()
        pprint.pprint(config)
        return config

