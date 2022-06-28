import os
import yfinance as yf
import pandas as pd
import json

nyse = pd.read_csv('nyse')

to_save_directory = os.getcwd() + '/nyse_data'
for t in list(nyse.ticker.values[2:]):
    x = yf.Ticker(t)
    try:
        info = x.info
        income_statement = x.financials
        balance_sheet = x.balance_sheet
        cash_flow = x.cashflow
        metadata = {'name': info['shortName'],
                    'summary': info['longBusinessSummary'],
                    'industry': info['industry'],
                    'sector': info['sector'],
                    'ticker': t,
                    'financial_currency': info['financialCurrency']}
        # os.makedirs(to_save_directory + '/' + t)
        # income_statement.to_csv(to_save_directory + '/' + t + '/income_statement.csv')
        # balance_sheet.to_csv(to_save_directory + '/' + t + '/balance_sheet.csv')
        # cash_flow.to_csv(to_save_directory + '/' + t + '/cash_flow.csv')
        with open(to_save_directory + '/' + t + '/metadata.json', 'w') as fp:
            json.dump(metadata, fp)
        print('Done for ', x)
    except:
        print('Failed for ', x)
        pass
