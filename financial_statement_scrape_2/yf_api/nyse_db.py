import pandas as pd
import os
import json
from multiprocessing import Pool
from yf_api.calc import calc


class YfTicker:

    def __init__(self, financials, balance_sheet, cash_flow):
        self.financials = financials
        self.balance_sheet = balance_sheet
        self.cashflow = cash_flow


pd.set_option('display.width', 400)
pd.set_option('display.max_columns', 20)
pd.set_option('display.max_rows', 1000)

directory_with_data = os.getcwd() + '/nyse_data'
stocks = os.listdir(directory_with_data)


def get_data(stock):
    current_dir = directory_with_data + '/' + stock
    with open(current_dir + '/metadata.json', 'r') as fp:
        temp = json.load(fp)
    income_statement = pd.read_csv(current_dir + '/income_statement.csv', index_col=0)
    balance_sheet = pd.read_csv(current_dir + '/balance_sheet.csv', index_col=0)
    cash_flow = pd.read_csv(current_dir + '/cash_flow.csv', index_col=0)
    yfTicker = YfTicker(income_statement, balance_sheet, cash_flow)
    temp['yfTicker'] = yfTicker
    temp['summary_data'] = calc(yfTicker)
    return temp


p = Pool()
data = p.map(get_data, stocks)
us_companies = [x for x in data if x.get('financial_currency') == 'USD']