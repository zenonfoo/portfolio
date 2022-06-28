import os
from multiprocessing import Pool
import json
import pandas as pd
from models import FinancialData, UnprocessedFinancialData

data_directory = os.getcwd() + '/financial_data_yahooquery'


def get_stocks_to_name_dict() -> dict:
    stocks_dir = os.getcwd() + '/stocks'
    exchanges = os.listdir(stocks_dir)
    results = {}
    for exchange in exchanges:
        result = list(pd.read_csv(stocks_dir + '/' + exchange, index_col=0).to_dict().values())[0]
        results = {**results, **result}
    return results


def add_ticker_and_name_to_metadata(metadata: dict, ticker: str, ticker_to_name: dict):
    ticker_and_name_dict = {'ticker': ticker, 'name': ticker_to_name.get(ticker)}
    try:
        return {**metadata, **ticker_and_name_dict}
    except:
        return ticker_and_name_dict


def convert_to_float(num: str):
    try:
        return float(num)
    except:
        return num


ticker_to_name_dict = get_stocks_to_name_dict()


def load_individual_yearly_data(ticker: str):
    directory_for_ticker = data_directory + '/' + ticker
    try:
        with open(directory_for_ticker + '/metadata.json', 'r') as fp:
            metadata = json.load(fp)

        yearly_directory = directory_for_ticker + '/yearly'
        all_years_for_ticker = [x for x in os.listdir(yearly_directory) if '-' in x]
        financial_data = []

        for year in all_years_for_ticker:
            income_statement = pd.read_csv(yearly_directory + '/' + year + '/income_statement.csv', index_col=0).applymap(
                convert_to_float)
            balance_sheet = pd.read_csv(yearly_directory + '/' + year + '//balance_sheet.csv', index_col=0).applymap(
                convert_to_float)
            cash_flow = pd.read_csv(yearly_directory + '/' + year + '/cash_flow.csv', index_col=0).applymap(
                convert_to_float)
            financial_data.append(FinancialData(income_statement, balance_sheet, cash_flow))

        metadata = add_ticker_and_name_to_metadata(metadata, ticker, ticker_to_name_dict)
        return UnprocessedFinancialData(financial_data, metadata)
    except:
        return None


def load_all_data():
    tickers_with_data = os.listdir(data_directory)
    p = Pool()
    return p.map(load_individual_yearly_data, tickers_with_data)
