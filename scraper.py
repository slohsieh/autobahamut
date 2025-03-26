import requests
from bs4 import BeautifulSoup
import re
import time
from datetime import datetime
import pandas as pd
from typing import Dict

def parse_order_data(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    order_blocks = soup.find_all('div', class_='entity-card-block')
    orders = []

    for block in order_blocks:
        order_num = block.find('a', class_='sign-number-content').text.strip()
        order_date = block.find('p', class_='sign-number-content').text.strip()
        platform = block.find('span', class_=lambda x: x and x.startswith('img-color-')).text.strip()
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
            'platform': platform,
            'product_name': product_name_clean,
            'unit': unit,
            'price': price
        })
    return orders

def get_last_page_number(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    page_links = soup.find('div', id='BH-pagebtn').find_all('a')
    last_page_link = page_links[-1]
    last_page = int(last_page_link.text.strip())
    return last_page

def get_all_orders(base_url, sess):
    base_page_response = sess.get(base_url)
    last_page = get_last_page_number(base_page_response.text)

    all_orders = []

    for page in range(1, last_page + 1):
        url = f"{base_url}&page={page}"
        print(f"Crawling order page {page}: {url}")

        response = sess.get(url)

        if response.status_code != 200:
            print(f"Page {page} cannot be crawled, skip")
            continue

        page_orders = parse_order_data(response.text)
        all_orders.extend(page_orders)
        time.sleep(1)

    return all_orders

def read_orders_df(sess: requests.Session):
    base_url = 'https://buy.gamer.com.tw/atmHistory.php?filter=5'
    all_orders = get_all_orders(base_url, sess)
    df = pd.DataFrame(all_orders)
    df['price'] = pd.to_numeric(df['price'])
    df['order_date'] = pd.to_datetime(df['order_date'])
    df = df.sort_values('order_date', ascending=False)
    return df

def parse_product_info(html_content) -> Dict:
    soup = BeautifulSoup(html_content, 'html.parser')

    detail_container = soup.find('div', class_='detail-container-area')
    if not detail_container:
        return {}
    
    product_name = detail_container.find('div', class_='detail-name-block').find('p').text.strip()
    try:
        publish_date_str = detail_container.find('div', class_='publish-date').find('p', class_='publish-date-content').text.strip()
    except AttributeError:
        publish_date_str = ''
    try:
        publish_date = datetime.strptime(publish_date_str, '%Y-%m-%d')
    except ValueError:
        publish_date = None
    try:
        platform = detail_container.find('span', class_=lambda x: x and x.startswith('img-color-')).text.strip()
    except:
        platform = None
    price_str = detail_container.find('div', class_='price-info-detail').find('p', class_='info-main-price').text.strip()
    price_str_clean = re.findall(r'\d+', price_str)
    price = int(price_str_clean[0])
    
    product_info = {
        'product_name': product_name,
        'publish_date': publish_date,
        'platform': platform,
        'price': price
    }
    
    return product_info

def parse_sn(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    sn_list = []
    product_cards = soup.find_all('div', class_='products-card')
    sn_pattern = re.compile(r'atmItem\.php\?sn=(\d+)')
    
    for card in product_cards:

        link = card.find('a', href=True)
        if link:
            href = link['href']
            match = sn_pattern.search(href)
            if match:
                sn_value = match.group(1)
                sn_list.append(sn_value)
    
    return sn_list


def read_console_sn(sess, console_code: int):
    base_url = f'https://buy.gamer.com.tw/indexList.php?gc1={console_code}'
    base_page_response = sess.get(base_url)
    n_pages = get_last_page_number(base_page_response.text)

    sns = []
    for page in range(1, n_pages + 1):
        url = f'https://buy.gamer.com.tw/indexList.php?page={page}&gc1={console_code}&sort=1'
        print(f"Crawling product page {page}: {url}")

        response = sess.get(url)

        if response.status_code != 200:
            print(f"Page {page} cannot be crawled, skip")
            continue

        page_sns = parse_sn(response.text)
        sns.extend(page_sns)
        time.sleep(0.5)
    return sns

def read_console_products(sess, console_code: int) -> Dict:
    sns = read_console_sn(sess, console_code)

    products = []
    for sn in sns:
        url = f'https://buy.gamer.com.tw/atmItem.php?sn={sn}'
        response = sess.get(url)
        product_info = parse_product_info(response.text)
        product_info = product_info | {'sn': sn}
        products.append(product_info)
        time.sleep(0.5)
    return products

def read_console_products_df(console_code: int):
    session = requests.Session()
    session.cookies.set("ckBUY_item18UP", "18UP")
    session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124"})
    products = read_console_products(session, console_code)
    df = pd.DataFrame(products)
    return df