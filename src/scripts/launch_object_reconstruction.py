# TODO make "launcher" for the whole end-to-end system

import json
import argparse
import time, datetime
import sys
import os
from pprint import pprint

sys.path.append(".")
sys.path.append("../")

# sys.path.append("utils")
from utils.file import check_folder_structure, get_project_root_dir
from utils.object_reconstruction_config import get_config

import subprocess


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

# def run_stage_with(stage_filename, args):

def add_datapath_to_cfg(reconstruction_config_filename, main_cfg):
    if 'home' not in reconstruction_config_filename:  # case if abs path used
        reconstruction_config_filename = os.path.join( main_cfg['project_root'],
                                                       reconstruction_config_filename)

    reconstruction_cfg = get_config(reconstruction_config_filename)
    reconstruction_cfg['path_dataset'] = os.path.join( main_cfg['project_root'],
                                                       main_cfg['path_dataset']
                                                       )

    reconstruction_cfg['path_intrinsic'] = os.path.join( main_cfg['project_root'],
                                                         main_cfg['path_intrinsic']
                                                         )

    abspath_reconstruction_config_filename = os.path.join(os.path.split(reconstruction_config_filename)[0],
                                                          'reconstruction.json'
                                                          )

    with open(abspath_reconstruction_config_filename, 'w') as json_file:
        json.dump(reconstruction_cfg, json_file, indent=4, sort_keys=True)

    return abspath_reconstruction_config_filename

def log_stats(stats, config):
    pprint(stats)
    logs_dir = os.path.join(
        config['project_root'],
        os.path.join( config['path_dataset'], "logs")
    )
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    log_filename = "blah_log.json"
    log_path = os.path.join(logs_dir, log_filename)
    print("Storing log to file [{}]".format(log_path) )
    with open(log_path, 'w') as json_file:
        json.dump(stats, json_file, indent=4, sort_keys=True)

PROJECT_NAME = "object_3d_reconstruction"
DEFAULT_CONFIFG_FILENAME = 'cfg/reconstruction/default/main.json'

if __name__ == "__main__":

    print(sys.path)

    #  TODO add config name argument
    print("Hello from main launcher")
    project_root = get_project_root_dir(os.getcwd(), PROJECT_NAME)

    condig_file_fullpath = DEFAULT_CONFIFG_FILENAME
    if PROJECT_NAME not in DEFAULT_CONFIFG_FILENAME and 'home' not in DEFAULT_CONFIFG_FILENAME:
        condig_file_fullpath = os.path.join(project_root, DEFAULT_CONFIFG_FILENAME)

    config = get_config(condig_file_fullpath)
    config['project_root'] = project_root

    stats = make_stats()
    log_stats(stats, config)

    if config['reconstruction']:
        reconstruction_args = config['reconstruction_args']

        reconstruction_runner_filename = reconstruction_args['runfile']
        if 'home' not in reconstruction_runner_filename:  # case if abs path used
            reconstruction_runner_filename = os.path.join(project_root, reconstruction_runner_filename)

        # reconstruction_config_with_relative_pathes = reconstruction_args['config']
        # if 'home' not in reconstruction_config_with_relative_pathes:  # case if abs path used
        #     reconstruction_config_with_relative_pathes = os.path.join(project_root, reconstruction_config_with_relative_pathes)


        runfile_dir, runfile_name = os.path.split(reconstruction_runner_filename)
        sys.path.append(runfile_dir)
        os.chdir(runfile_dir)

        abspath_reconstruction_config_filename = \
            add_datapath_to_cfg(reconstruction_args['config'], config)


        for stage_name in ['make', 'register', 'refine', 'integrate']:
            if reconstruction_args[stage_name]:
                reconstruction_steps_flags = ' --{} '.format(stage_name)
                if (reconstruction_args['debug_mode']):
                    reconstruction_steps_flags += " --debug_mode "
                exec_line = " ".join(["python",
                                      runfile_name,
                                      abspath_reconstruction_config_filename,
                                      reconstruction_steps_flags
                                      ])
                stage_start_time = time.time()
                os.system(exec_line)
                stats['exec_time']['reconstruction'][stage_name] = time.time() - stage_start_time

    log_stats(stats, config)





