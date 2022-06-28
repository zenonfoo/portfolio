import urllib.request
from bs4 import BeautifulSoup
from typing import List
from functools import reduce
from pprint import PrettyPrinter
from datetime import date
import pandas as pd

pp = PrettyPrinter()

pd.set_option('display.max_columns', 500)
pd.set_option('display.max_rows', 500)
pd.set_option('display.width', 500)


def get_page(url: str) -> BeautifulSoup:
    with urllib.request.urlopen(url) as response:
        html = response.read()
    return BeautifulSoup(html, 'html.parser')


def construct_table(data: BeautifulSoup) -> List[List[str]]:
    data_store = []

    try:
        for row in data.find_all('tr'):
            data_store.append([cols.text for cols in row.find_all('th')])
            data_store.append([cols.text for cols in row.find_all('td')])
    except:
        data_store.append(None)

    return data_store


def convert_str_to_num(data: str):
    result = data.replace(',', '')
    if '(' in data:
        return float(result.replace('(', '-').replace(')', ''))
    elif result == '--':
        return 0
    else:
        return float(result)


def clean_up_list_list_table(data: List[List[str]]):
    temp = data[2:]
    result = []
    for i, x in enumerate(temp):
        if i % 2 == 0:
            result.append(x)
        else:
            key = result.pop(-1)
            no_space_x = filter(lambda y: y != '', x)
            number_x = [convert_str_to_num(z) for z in no_space_x]
            result.append(key + number_x)
    return result


def get_column_list(data: List[List]):
    num_of_dates = len(data[0])
    return list(range(0,-num_of_dates,-1))


def convert_to_dict(data: List[List]):
    dates = get_column_list(data)
    results = {}
    for row in data:
        key = row[0]
        cols = row[1:]
        results[key] = {d: v for d, v in zip(dates, cols)}
    return results


def convert_to_df(data: dict, url: str):
    ticker = url.split('/')[4]
    df = pd.DataFrame(data).transpose()
    df.name = ticker
    return df


def get_data(url: str):
    return reduce(lambda x, y: y(x),
                  [url,
                   get_page,
                   construct_table,
                   clean_up_list_list_table,
                   convert_to_dict,
                   lambda x: convert_to_df(x, url)])
