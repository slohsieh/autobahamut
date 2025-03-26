import utils
import requests

from const import __SIGN_IN_URL__


def sign_in(sess: requests.Session):
    sign_info = sess.post(__SIGN_IN_URL__, data={'action': '2'}).json()
    if sign_info['data']['signin'] == 1:
        return
    token = sess.get('https://www.gamer.com.tw/ajax/get_csrf_token.php').text
    json_info = sess.post(__SIGN_IN_URL__,, data={'action': '1', 'token': token})
    json_info = json_info.json()
    if 'data' in json_info:
        print(f'巴哈姆特自動簽到成功!!\n已簽到第 {str(json_info["data"]["days"])} 天')
    else:
        print('簽到失敗')

if __name__ == '__main__':
    sess = utils.login(utils.login_info())
    sign_in(sess)