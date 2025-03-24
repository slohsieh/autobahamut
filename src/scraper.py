import requests
import utils
from bs4 import BeautifulSoup
import re
import time
import pandas as pd



def login() -> requests.Session:
    login_info = utils.login_info()
    sess = requests.session()
    sess.headers.update(
        {
            'user-agent': 'Bahadroid (https://www.gamer.com.tw/)',
            'x-bahamut-app-instanceid': 'cc2zQIfDpg4',
            'x-bahamut-app-android': 'tw.com.gamer.android.activecenter',
            'x-bahamut-app-version': '251',
            'content-type': 'application/x-www-form-urlencoded',
            'content-length': '44',
            'accept-encoding': 'gzip',
            'cookie': 'ckAPP_VCODE=7045'
        },
    )

    sess.post('https://api.gamer.com.tw/mobile_app/user/v3/do_login.php', 
              data=login_info)
    sess.headers = {
        'user-agent': 'Bahadroid (https://www.gamer.com.tw/)',
        'x-bahamut-app-instanceid': 'cc2zQIfDpg4',
        'x-bahamut-app-android': 'tw.com.gamer.android.activecenter',
        'x-bahamut-app-version': '251',
        'accept-encoding': 'gzip'
    }
    return sess

def parse_order_data(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    order_blocks = soup.find_all('div', class_='entity-card-block')
    orders = []

    for block in order_blocks:
        order_num = block.find('a', class_='sign-number-content').text.strip()
        order_date = block.find('p', class_='sign-number-content').text.strip()
        product_name = block.find(
            'p', class_='product-name-content').text.strip()

        # check if the result contains unit, like "string*number"
        match = re.search(r'(.+?)\s*\*\s*(\d+)$', product_name)
        if match:
            product_name_clean = match.group(1).strip()
            unit = int(match.group(2))
        else:
            product_name_clean = product_name
            unit = pd.NA

        price = block.find('p', class_='order-price-content').text.strip()

        orders.append({
            'order_id': order_num,
            'order_date': order_date,
            'product_name': product_name_clean,
            'unit': unit,
            'price': price
        })
    return orders

def get_all_pages(base_url, sess):
    base_page_response = sess.get(base_url)
    soup = BeautifulSoup(base_page_response.text, 'html.parser')
    page_links = soup.find('div', id='BH-pagebtn').find_all('a')
    last_page_link = page_links[-1]
    last_page = int(last_page_link.text.strip())

    all_orders = []

    for page in range(1, last_page + 1):
        url = f"{base_url}&page={page}"
        print(f"Crawling page {page}: {url}")

        response = sess.get(url)

        if response.status_code != 200:
            print(f"Page {page} cannot be crawled, skip")
            continue

        page_orders = parse_order_data(response.text)
        all_orders.extend(page_orders)
        time.sleep(1)

    return all_orders