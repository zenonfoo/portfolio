import pandas as pd
import pprint as pp
import yfinance as yf
from yf_api.calc import calc

balance_sheet_order = [
    'Cash',
    'Short Term Investments',
    'Net Receivables',
    'Inventory',
    'Other Current Assets',
    'Total Current Assets',
    'Long Term Investments',
    'Good Will',
    'Intangible Assets',
    'Other Assets',
    'Total Assets',
    'Accounts Payable',
    'Other Current Liab',
    'Total Current Liabilities',
    'Property Plant Equipment',
    'Deferred Long Term Asset Charges',
    'Short Long Term Debt',
    'Long Term Debt',
    'Deferred Long Term Liab',
    'Other Liab',
    'Total Liab',
    'Net Tangible Assets',
    'Retained Earnings',
    'Treasury Stock',
    'Total Stockholder Equity',
    'Other Stockholder Equity',
    'Common Stock',
    'Minority Interest',
    'Capital Surplus'
]

cash_flow_order = [
    'Net Income',
    'Change To Netincome',
    'Depreciation',
    'Change To Inventory',
    'Change To Account Receivables',
    'Change To Liabilities',
    'Effect Of Exchange Rate',
    'Total Cash From Operating Activities',
    'Change To Operating Activities',
    'Capital Expenditures',
    'Investments',
    'Other Cashflows From Investing Activities',
    'Total Cashflows From Investing Activities',
    'Issuance Of Stock',
    'Repurchase Of Stock',
    'Dividends Paid',
    'Other Cashflows From Financing Activities',
    'Net Borrowings',
    'Total Cash From Financing Activities',
    'Change In Cash'
]

prettyPrinter = pp.PrettyPrinter()


def format_num(val):
    try:
        temp = round(val, 2)
        return "{:,}".format(temp)
    except:
        return val


def organise_data(order, data: pd.DataFrame, type: str):
    value_in_df_not_in_order = list(set(data.index.tolist()) - set(order))
    if len(value_in_df_not_in_order) == 0:
        result = None
        for i, o in enumerate(order):
            try:
                if i == 0:
                    result = pd.DataFrame(data.loc[o]).transpose()
                else:
                    result = pd.concat([result, pd.DataFrame(data.loc[o]).transpose()])
            except:
                pass
    else:
        raise Exception('Values not in order for {}: {}'.format(type, value_in_df_not_in_order))

    return result


def check(ticker: str, yearly=True):
    data = yf.Ticker(ticker)
    info = data.info
    print("Name: {}, Ticker: {}, Market Cap: {}".format(info['shortName'], ticker, format_num(info['marketCap'])))
    try:
        prettyPrinter.pprint(info['longBusinessSummary'])
    except:
        print('No longBusinessSummary')
    if yearly:
        calc_data = calc(data)
        balance_sheet = data.balance_sheet
        cash_flow = data.cashflow
    else:
        calc_data = calc(data, False)
        balance_sheet = data.quarterly_balance_sheet
        cash_flow = data.quarterly_cashflow
    print('SUMMARY DATA')
    print(calc_data.applymap(format_num))
    print()
    print('BALANCE SHEET')
    print(organise_data(balance_sheet_order, balance_sheet, 'balance sheet').applymap(format_num))
    print()
    print('CASH FLOW')
    print(organise_data(cash_flow_order, cash_flow, 'cash flow').applymap(format_num))
    print()
