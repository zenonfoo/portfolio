import pandas as pd
from typing import List
import numpy as np
from yf_api.utils import format_num, organise_data, balance_sheet_order, cash_flow_order
import pprint as pp
import yfinance as yf

prettyPrinter = pp.PrettyPrinter()


def list_all_industries(data: List[dict]):
    industries = [x['industry'] for x in data]
    return pd.Series(industries).value_counts()


def get_industry(data: List[dict], industry: str):
    return [x for x in data if x['industry'] == industry]


def organise_summary_data(data: List[dict]):
    results = pd.DataFrame()
    for d in data:
        intended_data = pd.DataFrame(d['summary_data'].iloc[:, 0].drop('')).transpose()
        intended_data.index = [d['name']]
        results = pd.concat([results, intended_data])
    return results.replace('-', 0)


def organise_for_industry(data: List[dict], industry: str):
    data_for_industry = get_industry(data, industry)
    return organise_summary_data(data_for_industry)


def filter_roe_greater_than_20(data: List[dict]):
    results = []
    for d in data:
        try:
            if d['summary_data'].loc['ROE'].mean() > 0.2:
                results.append(d)
        except:
            pass
    return results


def print_top_10_based_on_key_value(data: List[dict], key: str):
    organised_data = organise_summary_data(data)
    return organised_data.sort_values(key, ascending=False).replace('', np.nan).dropna(
        how='all',
        axis=1).head(
        10).transpose().applymap(format_num)


def read(data: List[dict], counter=0):
    start_counter = counter
    for d in data[counter:]:
        info = yf.Ticker(d['ticker']).info
        print("Name: {}, Ticker: {}, Market Cap: {}, Counter: {}".format(info['shortName'], d['ticker'],
                                                                         format_num(info['marketCap']), start_counter))
        prettyPrinter.pprint(info['longBusinessSummary'])
        print('SUMMARY DATA')
        print(d['summary_data'].applymap(format_num))
        print()
        print('BALANCE SHEET')
        print(organise_data(balance_sheet_order, d['yfTicker'].balance_sheet, 'balance sheet').applymap(format_num))
        print()
        print('CASH FLOW')
        print(organise_data(cash_flow_order, d['yfTicker'].cashflow, 'cash flow').applymap(format_num))
        print()
        start_counter += 1
        on = input('Continue?')
        if on != '':
            break

# software_application = organise_for_industry(data, 'Software—Application')
# software_application.sort_values('Total Revenue', ascending=False).replace('', np.nan).dropna(how='all', axis=1).head(
#     10).transpose().applymap(format_num)
#
# all_data = organise_summary_data(us_companies)
