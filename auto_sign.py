import utils
import requests
import os
import logging

from const import __SIGN_IN_URL__



def sign_in(sess: requests.Session):

    logger = logging.getLogger('SignInLogger')
    script_dir = os.path.dirname(os.path.abspath(__file__))
    log_dir = os.path.join(script_dir, 'log')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    log_file_path = os.path.join(log_dir, 'sign_in_log.txt')
    file_handler = logging.FileHandler(log_file_path, mode='a', encoding='utf-8')
    logger.addHandler(file_handler)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
    logger.addHandler(file_handler)
    logger.setLevel(logging.INFO)

    sign_info = sess.post(__SIGN_IN_URL__, data={'action': '2'}).json()
    if sign_info['data']['signin'] == 1:
        return
    token = sess.get('https://www.gamer.com.tw/ajax/get_csrf_token.php').text
    json_info = sess.post(__SIGN_IN_URL__, data={'action': '1', 'token': token})
    json_info = json_info.json()
    if 'data' in json_info:
        logger.info(f'Signing in successfully. You have signed in for {str(json_info["data"]["days"])} days.')
    else:
        logger.info('Signing in failed.')

if __name__ == '__main__':
    sess = utils.login(utils.login_info())
    sign_in(sess)