from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import time

STATEMENTS = [('financials', 'income_statement'), ('balance-sheet', 'balance_sheet'), ('cash-flow', 'cash_flow')]


def convert_from_str_to_num(data: str) -> float:
    if data == '' or data == '-':
        return 0
    elif 'k' in data:
        return float(data.replace('k', '')) * 1000
    else:
        return float(''.join(data.split(',')))


def convert_bs4_financial_statement_to_df(data: BeautifulSoup) -> pd.DataFrame:
    header = data.find('div', {'class': 'D(tbhg)'})
    header_row = header.find('div', {'class', 'D(tbr)'})
    header_list = list(map(lambda x: x.get_text(), header_row.find_all('span')))
    body = data.find('div', {'class': 'D(tbrg)'})
    body_rows = body.find_all('div', {'class', 'D(tbr)'})
    body_lists = [list(map(lambda x: x.get_text(), row)) for row in body_rows]
    data_dict = {}
    for row in body_lists:
        temp_holder = {}
        for header, column in zip(header_list[1:], row[1:]):
            temp_holder[header] = convert_from_str_to_num(column)
        data_dict[row[0]] = temp_holder
    try:
        return pd.DataFrame(data_dict).transpose().drop('ttm', axis=1)
    except:
        return pd.DataFrame(data_dict).transpose()


def get_data(driver: webdriver.Chrome, stock: str):
    result = {}

    for s, key in STATEMENTS:
        driver.get('https://uk.finance.yahoo.com/quote/{}/{}?p={}'.format(stock, s, stock))
        time.sleep(1)
        spans = driver.find_elements_by_tag_name('span')
        quarterly = next(filter(lambda x: x.text == 'Quarterly', spans))
        quarterly.click()
        time.sleep(1)
        page_source = BeautifulSoup(driver.page_source, 'html.parser')
        result[key] = convert_bs4_financial_statement_to_df(page_source)

    return result
