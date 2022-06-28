import pandas as pd
import sqlite3
from load_yahooquery import load_all_data
from multiprocessing import Pool

from models import UnprocessedFinancialData

pd.set_option('display.width', 400)
pd.set_option('display.max_columns', 20)
pd.set_option('display.max_rows', 1000)

# load data

data = load_all_data()


# convert to table to publish to sqlite
def combine(df_to_add: pd.DataFrame, current_df: pd.DataFrame, statement: str, ticker: str):
    keys = df_to_add.index
    results = []
    for k in keys:
        row = df_to_add.loc[k]
        for i in range(len(row)):
            value = row[i]
            if type(value) != str:
                date = row.index[i]
                results.append([ticker, k, value, statement, date])
    return current_df.append(pd.DataFrame(results, columns=['ticker', 'key', 'value', 'statement', 'date']))


def combine_all_statements(d: UnprocessedFinancialData):
    try:
        result = pd.DataFrame()
        ticker = d.metadata['ticker']
        result = combine(d.financial_data[0].income_statement, result, 'income_statement', ticker)
        result = combine(d.financial_data[0].balance_sheet, result, 'balance_sheet', ticker)
        result = combine(d.financial_data[0].cash_flow, result, 'cash_flow', ticker)
        return result
    except:
        print("Failed")
        return None


p = Pool()
result = p.map(combine_all_statements, data)
final_results = pd.concat(result)

# convert metadata to table to publish to sqlite
metadata_results = []
for d in data:
    try:
        metadata = d.metadata
        metadata_results.append(
            [
                metadata.get('address1'),
                metadata.get('address2'),
                metadata.get('city'),
                metadata.get('state'),
                metadata.get('zip'),
                metadata.get('country'),
                metadata.get('phone'),
                metadata.get('website'),
                metadata.get('industry'),
                metadata.get('sector'),
                metadata.get('longBusinessSummary'),
                metadata.get('fullTimeEmployees'),
                metadata.get('dividendYield'),
                metadata.get('exDividendDate'),
                metadata.get('fiveYearAvgDividendYield'),
                metadata.get('trailingPE'),
                metadata.get('forwardPE'),
                metadata.get('marketCap'),
                metadata.get('currency'),
                metadata.get('ticker'),
                metadata.get('name')
            ]
        )
    except:
        print('Failed')

metadata_df = pd.DataFrame(
    metadata_results,
    columns=[
        'address1',
        'address2',
        'city',
        'state',
        'zip',
        'country',
        'phone',
        'website',
        'industry',
        'sector',
        'longBusinessSummary',
        'fullTimeEmployees',
        'dividendYield',
        'exDividendDate',
        'fiveYearAvgDividendYield',
        'trailingPE',
        'forwardPE',
        'marketCap',
        'currency',
        'ticker',
        'name'
    ]
)

# establish db connection
conn = sqlite3.connect('financial_data_yahooquery.db')
