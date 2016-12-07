import time
import sys
import os

import requests


current_dir = os.path.dirname(__file__)
data_folder = os.path.abspath(os.path.join(current_dir, 'data'))


def print_progress(msg):
    sys.stdout.write('\r')
    sys.stdout.write(msg)
    sys.stdout.flush()


def safe_get(url, headers={}):
    while True:
        try:
            r = requests.get(url, headers=headers)
        except requests.exceptions.ConnectionError:
            print('Connection refused')
            time.sleep(3)
        except Exception as exc:
            print('ERR : %s' % exc)
            time.sleep(3)
        else:
            if r.status_code == 200: break
    return r.json()