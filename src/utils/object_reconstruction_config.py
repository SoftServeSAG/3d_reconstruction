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


def add_prefix_to_json_field_value(json_filename, field_name, prefix):
    config = None
    with open(json_filename, 'r') as json_file:
        config = json.load(json_file)
        assert field_name in config, \
            "Config file [{}] does not have a parameter field [{}]".format(json_filename, field_name)
        old_field_value = config[field_name]

        if old_field_value.startswith(prefix):
            print("Field [{}] already has valid prefix [{}]".format(field_name, prefix))
            return

        new_field_value = ''.join([prefix, old_field_value])
        config[field_name] = new_field_value

    with open(json_filename, 'w') as json_file:
        json.dump(config, json_file)
