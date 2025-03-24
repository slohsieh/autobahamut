
import os
from os.path import dirname, join
import json
from collections import namedtuple

script_dir = dirname(__file__)

def read_config():
    config_path = os.path.join(script_dir, 'config.json')
    with open(config_path, 'r', encoding='utf-8') as file:
        config_data = json.load(file)

    return config_data

def login_info():
    config_data = read_config()
    data = {
        'uid': config_data['account']['username'],
        'passwd': config_data['account']['password'],
        'vcode': '7045'
    }