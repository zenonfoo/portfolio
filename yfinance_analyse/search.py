from yahooquery import Ticker
from models import FinancialData, UnprocessedFinancialData
from calc_yahooquery import calc
import pandas as pd

pd.set_option('display.width', 400)
pd.set_option('display.max_columns', 20)
pd.set_option('display.max_rows', 1000)


def format_statements(statement: pd.DataFrame):
    twelve_month_data = statement[statement['periodType'] == '12M']
    twelve_month_data.index = twelve_month_data.asOfDate
    return twelve_month_data.transpose()


def check(ticker: str):
    data = Ticker(ticker)
    financial_data = FinancialData(
        format_statements(data.income_statement()),
        format_statements(data.balance_sheet()),
        format_statements(data.cash_flow())
    )
    unprocessed_financial_data = UnprocessedFinancialData([financial_data], data.summary_profile)
    return calc(unprocessed_financial_data)


x = check('7089.KL')
print(x.summary_data)
