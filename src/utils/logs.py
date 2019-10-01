from pprint import pprint
import os
import datetime
import json

def make_stats():
    stats = {
        "exec_time": {
            "reconstruction": {
                'make': 0,
                'register': 0,
                'refine': 0,
                'integrate': 0
            }
        },
        "config" : {
        # to be insetred in runtime
        }
    }
    return stats

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
