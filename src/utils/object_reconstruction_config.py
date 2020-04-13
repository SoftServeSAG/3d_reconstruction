import argparse
import json
import os, sys
import pprint


def get_config(config_filename):
    print("Using config path: [{}]".format(config_filename))

    assert os.path.exists(config_filename), \
        "Path [%s] does not exist!" % config_filename

    with open(config_filename) as json_file:
        config = json.load(json_file)
        print("Using config: ")
        print()
        pprint.pprint(config)
        return config


def specify_config_pathes(subconfig, main_cfg, updated_config_filename=''):

    subconfig['path_dataset'] = os.path.join( main_cfg['project_root'],
                                                       main_cfg['path_dataset']
                                                       )

    subconfig['path_intrinsic'] = os.path.join( main_cfg['project_root'],
                                                         main_cfg['path_intrinsic']
                                                         )
    if len(updated_config_filename) != 0:
        with open(updated_config_filename, 'w') as json_file:
            json.dump(subconfig, json_file, indent=4, sort_keys=True)
    return subconfig
