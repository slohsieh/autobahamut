
import os
from os.path import dirname, join
import json
from collections import namedtuple
from typing import Dict
import requests
from datetime import datetime, date as _date

script_dir = dirname(__file__)

headers_pre_login =  {
            'user-agent': 'Bahadroid (https://www.gamer.com.tw/)',
            'x-bahamut-app-instanceid': 'cc2zQIfDpg4',
            'x-bahamut-app-android': 'tw.com.gamer.android.activecenter',
            'x-bahamut-app-version': '251',
            'content-type': 'application/x-www-form-urlencoded',
            'content-length': '44',
            'accept-encoding': 'gzip',
            'cookie': 'ckAPP_VCODE=7045'
        }

headers_post_login = {
        'user-agent': 'Bahadroid (https://www.gamer.com.tw/)',
        'x-bahamut-app-instanceid': 'cc2zQIfDpg4',
        'x-bahamut-app-android': 'tw.com.gamer.android.activecenter',
        'x-bahamut-app-version': '251',
        'accept-encoding': 'gzip'
    }

def login(login_info: Dict) -> requests.Session:
    sess = requests.session()
    sess.headers.update(headers_pre_login)
    sess.post('https://api.gamer.com.tw/mobile_app/user/v3/do_login.php', 
              data=login_info)
    sess.headers = headers_post_login
    return sess

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
    return data