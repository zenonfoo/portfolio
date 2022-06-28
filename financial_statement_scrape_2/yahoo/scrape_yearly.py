from bs4 import BeautifulSoup
import pandas as pd
import time
import urllib.request as request

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


def get_page(url: str) -> BeautifulSoup:
    with request.urlopen(url) as response:
        html = response.read()
    return BeautifulSoup(html, 'html.parser')


def get_financial_statement_from_link(link: str) -> pd.DataFrame:
    data = get_page(link)
    return convert_bs4_financial_statement_to_df(data)


def get_market_cap(symbol: str) -> str:
    link = 'https://uk.finance.yahoo.com/quote/' + symbol
    page = get_page(link)
    spans = page.find_all('span')
    for i, span in enumerate(spans):
        if span.text == 'Market cap':
            return spans[i + 1].text


def get_description(symbol: str) -> str:
    link = 'https://uk.finance.yahoo.com/quote/' + symbol + '/profile'
    page = get_page(link)
    tags = page.find_all(['span', 'p'])
    for i, tag in enumerate(tags):
        if tag.text == 'Description':
            return tags[i + 1].text


def get_data(symbol: str):
    income_statement = get_financial_statement_from_link(
        'https://uk.finance.yahoo.com/quote/' + symbol + '/financials?p=' + symbol)
    time.sleep(1)
    balance_sheet = get_financial_statement_from_link(
        'https://uk.finance.yahoo.com/quote/' + symbol + '/balance-sheet?p=' + symbol)
    time.sleep(1)
    cash_flow = get_financial_statement_from_link(
        'https://uk.finance.yahoo.com/quote/' + symbol + '/cash-flow?p=' + symbol)
    time.sleep(1)
    market_cap = get_market_cap(symbol)
    time.sleep(1)
    description = get_description(symbol)
    data = {'income_statement': income_statement,
            'balance_sheet': balance_sheet,
            'cash_flow': cash_flow,
            'market_cap': market_cap,
            'description': description}
    return data
