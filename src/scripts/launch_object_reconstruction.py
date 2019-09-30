# TODO make "launcher" for the whole end-to-end system

import json
import argparse
import time, datetime
import sys
import os

sys.path.append(".")
sys.path.append("../..")

# sys.path.append("../utils")
from utils.file import check_folder_structure, get_project_root_dir
from utils.object_reconstruction_config import get_config



DEFAULT_CONFIFG_FILENAME = 'cfg/reconstruction/default/main.json'

if __name__ == "__main__":
    #  TODO add config argument
    print("Hello from main launcher")
    project_root = get_project_root_dir(os.getcwd())
    assert len(project_root) != 0 , \
        "Unable to identify expected name of project root, expected [{}] in path".format("object_3d_reconstruction")
    print("Project root set to [{}]".format(project_root))

    condig_file_fullpath = os.path.join(project_root, DEFAULT_CONFIFG_FILENAME)
    config = get_config(condig_file_fullpath)

    if config['reconstruction']:
        reconstruction_cfg = config['reconstruction_cfg']

        reconstruction_runner_filename = reconstruction_cfg['runfile']
        if 'home' not in reconstruction_runner_filename:  # case if abs path used
            reconstruction_runner_filename = os.path.join(project_root, reconstruction_runner_filename)

        stages_flags = ""
        for stage_name in ['make', 'register', 'refine', 'integrate']:
            if reconstruction_cfg['stage_name']:
                stages_flags += '--{} '.format(stage_name)



