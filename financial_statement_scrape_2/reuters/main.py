from reuters.scrape import get_data
from reuters.calc import calc
from typing import List
import pandas as pd
from yahoo.scrape_yearly import get_market_cap, get_description
from yahoo.calc import YearlyQuarterly
from pprint import PrettyPrinter

pp = PrettyPrinter()

KEY = ['income_statement', 'balance_sheet', 'cash_flow']

hk_stocks = pd.read_csv('hk_stocks_with_industry.csv')
pe_less_than_10 = hk_stocks[hk_stocks['P/E Ratio'] < 10]
pe_less_than_10 = pe_less_than_10[pe_less_than_10['P/E Ratio'] > 0]


def format(val):
    try:
        temp = round(val, 2)
        return "{:,}".format(temp)
    except:
        return val


def get_pe_ratio_less_than(data: pd.DataFrame, pe_ratio: int):
    temp = data[data['P/E Ratio'] < pe_ratio]
    return temp[temp['P/E Ratio'] > 0]


def generate_urls(url: str, yearly_or_quarterly: YearlyQuarterly):
    if yearly_or_quarterly == YearlyQuarterly.YEARLY:
        val = 'annual'
    else:
        val = 'quarterly'
    return [url + '/financials/income_statement-' + val,
            url + '/financials/balance-sheet-' + val,
            url + '/financials/cash-flow-' + val]


def check_one(ric: str, divide_type: YearlyQuarterly):
    urls = generate_urls('https://www.reuters.com/companies/' + ric, divide_type)
    statements = {k: v for k, v in zip(KEY, [get_data(url) for url in urls])}
    statements['market_cap'] = get_market_cap(ric)
    statements['description'] = get_description(ric)
    statements['ric'] = ric
    return calc(statements, divide_type)


def average_summary_data(data: List[dict]):
    results = []
    for d in data:
        summary_data = d['summary_data']
        results_per_ric = []
        for row in range(summary_data.shape[0]):
            temp = summary_data.iloc[row, :].copy()
            try:
                result = temp.mean()
            except:
                result = ''
            results_per_ric.append(pd.DataFrame([result], index=[temp.name], columns=[d['ric']]))
        results.append(pd.concat(results_per_ric))
    return pd.concat(results, axis=1).applymap(format)


def check_row(data: List[dict], row_name: str):
    rows = []
    for d in data:
        summary_data = d['summary_data']
        row = summary_data.loc[row_name]
        row.name = d['ric']
        rows.append(row)
    results = pd.concat(rows, axis=1)
    results.name = row_name
    return results.transpose().applymap(format)


result = check_one('RRD', YearlyQuarterly.YEARLY)
result['summary_data'].applymap(format)
# auto = ['GM', 'F', 'FCHA.MI', '7201.T', '7267.T', '7203.T']
# results = []
# for i in auto:
#     try:
#         results.append(check_one(i, YearlyQuarterly.YEARLY))
#     except:
#         print(i)
#
# average_summary_data(results)

# for row in construction.T.to_dict().values():
#     try:
#         ticker = str(row['Ticker'])
#         ticker = '0' + ticker if len(ticker) == 3 else ticker
#         result = check_one(ticker + '.HK', YearlyQuarterly.YEARLY)
#         print(row['Name'], result['market_cap'], row['Ticker'])
#         pp.pprint(result['description'])
#         print(result['summary_data'].applymap(format))
#     except:
#         print('Failed for {}'.format(row['Name']))
#
#     go = input('Continue?')
#     if go != "":
#         break
