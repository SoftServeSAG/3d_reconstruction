# TODO make "launcher" for the whole end-to-end system

import json
import argparse
import time, datetime
import sys
import os
from pprint import pprint

sys.path.append(".")
sys.path.append("../")

from utils.file import check_folder_structure, get_project_root_dir
from utils.object_reconstruction_config import get_config

def make_stats():
    stats = {
        "exec_time": {
            "reconstruction": {
                'make': 0,
                'register': 0,
                'refine': 0,
                'integrate': 0
            }
        }
    }
    return stats


def specify_config_pathes(subconfig_filename, main_cfg, updated_config_filename):
    if 'home' not in subconfig_filename:  # case if abs path used
        subconfig_filename = os.path.join(main_cfg['project_root'],
                                          subconfig_filename)

    subconfig = get_config(subconfig_filename)
    subconfig['path_dataset'] = os.path.join( main_cfg['project_root'],
                                                       main_cfg['path_dataset']
                                                       )

    subconfig['path_intrinsic'] = os.path.join( main_cfg['project_root'],
                                                         main_cfg['path_intrinsic']
                                                         )

    with open(updated_config_filename, 'w') as json_file:
        json.dump(subconfig, json_file, indent=4, sort_keys=True)


def log_stats(stats, config):
    pprint(stats)
    logs_dir = os.path.join(
        config['project_root'],
        os.path.join( config['path_dataset'], "logs")
    )
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    timestamp = datetime.datetime.now().strftime("%d-%m-%Y_%I-%M-%S_%p")
    log_filename = "{}_stats_{}.json".format(config['project_name'], timestamp)
    log_path = os.path.join(logs_dir, log_filename)
    print("Storing log to file [{}]".format(log_path) )
    with open(log_path, 'w') as json_file:
        json.dump(stats, json_file, indent=4, sort_keys=True)

PROJECT_NAME = "object_3d_reconstruction"
DEFAULT_CONFIFG_FILENAME = 'cfg/reconstruction/default/main.json'

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Object reconstruction pipeline launcher")
    parser.add_argument("--config", help="path to the config file")
    args = parser.parse_args()
    config_filename = DEFAULT_CONFIFG_FILENAME
    if args.config is not None:
        config_filename = args.config

    project_root = get_project_root_dir(os.getcwd(), PROJECT_NAME)

    condig_file_fullpath = config_filename
    if PROJECT_NAME not in config_filename and 'home' not in config_filename:
        condig_file_fullpath = os.path.join(project_root, config_filename)

    config = get_config(condig_file_fullpath)
    config['project_root'] = project_root

    stats = make_stats()

    if config['reconstruction']:
        reconstruction_args = config['reconstruction_args']

        reconstruction_runner_filename = reconstruction_args['runfile']
        if 'home' not in reconstruction_runner_filename:  # case if abs path used
            reconstruction_runner_filename = os.path.join(project_root, reconstruction_runner_filename)

        runfile_dir, runfile_name = os.path.split(reconstruction_runner_filename)
        sys.path.append(runfile_dir)
        os.chdir(runfile_dir)

        specified_config_filename = os.path.join(
            config['project_root'],
            os.path.join(os.path.dirname(reconstruction_args['config']),
                         'reconstruction.json')
            )

        specify_config_pathes( subconfig_filename=reconstruction_args['config'],
                               main_cfg=config,
                               updated_config_filename=specified_config_filename)

        for stage_name in ['make', 'register', 'refine', 'integrate']:
            if reconstruction_args[stage_name]:
                reconstruction_steps_flags = ' --{} '.format(stage_name)
                if (reconstruction_args['debug_mode']):
                    reconstruction_steps_flags += " --debug_mode "
                exec_line = " ".join(["python",
                                      runfile_name,
                                      specified_config_filename,
                                      reconstruction_steps_flags
                                      ])
                stage_start_time = time.time()
                os.system(exec_line)
                stats['exec_time']['reconstruction'][stage_name] = time.time() - stage_start_time

    log_stats(stats, config)





