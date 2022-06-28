import yfinance as yf
import pandas as pd
from functools import reduce


def value_when_error_thrown(data: pd.DataFrame, row_name: str):
    col_length = data.shape[1]
    col_names = data.columns
    df_data = ['-'] * col_length
    return pd.DataFrame([df_data], columns=col_names, index=[row_name])


def add_empty_line(data: pd.DataFrame, name: str, summary_data: pd.DataFrame) -> pd.DataFrame:
    col_length = data.shape[1]
    col_names = data.columns
    df_data = [''] * col_length
    result = pd.DataFrame([df_data], columns=col_names, index=[name])
    if summary_data is not None:
        return pd.concat([summary_data, result])
    else:
        return result


def select_row(data: pd.DataFrame, row_name: str, summary_data: pd.DataFrame) -> pd.DataFrame:
    try:
        row = pd.DataFrame(data.loc[row_name]).transpose()
    except:
        row = value_when_error_thrown(data, row_name)

    return pd.concat([summary_data, row])


def calc_helper(numerator_data: pd.DataFrame, denominator_data: pd.DataFrame, func, result_name: str, numerator: str,
                denominator: str, summary_data: pd.DataFrame) -> pd.DataFrame:
    try:
        if denominator_data is not None:
            denominator_val = denominator_data.loc[denominator]
        else:
            denominator_val = numerator_data.loc[denominator]
        numerator_val = numerator_data.loc[numerator]
        result = func(numerator_val, denominator_val)
        result.name = result_name
        result = pd.DataFrame(result).transpose()
    except:
        result = value_when_error_thrown(numerator_data, result_name)

    return pd.concat([summary_data, result])


def calc(data: yf.Ticker, yearly=True) -> pd.DataFrame:
    if yearly:
        financials = data.financials
        cash_flow = data.cashflow
        balance_sheet = data.balance_sheet
    else:
        financials = data.quarterly_financials
        cash_flow = data.quarterly_cashflow
        balance_sheet = data.quarterly_balance_sheet
    return reduce(lambda x, y: y(x),
                  [None,
                   lambda x: add_empty_line(financials, 'EARNINGS', x),
                   lambda x: select_row(financials, 'Total Revenue', x),
                   lambda x: select_row(financials, 'Operating Income', x),
                   lambda x: select_row(financials, 'Net Income Applicable To Common Shares', x),
                   lambda x: select_row(cash_flow, 'Total Cash From Operating Activities', x),
                   lambda x: calc_helper(cash_flow, None, lambda y, z: y + z, 'Free Cash Flow',
                                         'Total Cash From Operating Activities',
                                         'Capital Expenditures', x),
                   lambda x: select_row(balance_sheet, 'Retained Earnings', x),
                   lambda x: select_row(cash_flow, 'Dividends Paid', x),
                   lambda x: calc_helper(cash_flow, financials, lambda y, z: y / z,
                                         'Dividend Payout Ratio',
                                         'Dividends Paid',
                                         'Net Income Applicable To Common Shares',
                                         x),
                   lambda x: add_empty_line(financials, '', x),
                   lambda x: add_empty_line(financials, 'EARNINGS MARGINS', x),
                   lambda x: calc_helper(financials, None, lambda y, z: y / z, 'Gross Profit Margin',
                                         'Gross Profit',
                                         'Total Revenue',
                                         x),
                   lambda x: calc_helper(financials, None, lambda y, z: y / z, 'Operating Margin',
                                         'Operating Income', 'Total Revenue',
                                         x),
                   lambda x: add_empty_line(financials, '', x),
                   lambda x: add_empty_line(financials, 'BALANCE SHEET RATIOS', x),
                   lambda x: calc_helper(balance_sheet, None, lambda y, z: y / z, 'Current Ratio',
                                         'Total Current Assets',
                                         'Total Current Liabilities', x),
                   lambda x: calc_helper(balance_sheet, None, lambda y, z: y / z, 'Assets over Liabilities',
                                         'Total Assets',
                                         'Total Liab',
                                         x),
                   lambda x: calc_helper(balance_sheet, financials, lambda y, z: y / z,
                                         'Inventory Turnover', 'Inventory', 'Cost Of Revenue', x),
                   lambda x: calc_helper(balance_sheet, financials, lambda y, z: y / z,
                                         'Day Sales Outstanding', 'Net Receivables',
                                         'Total Revenue', x),
                   lambda x: add_empty_line(financials, '', x),
                   lambda x: add_empty_line(financials, 'CAPITALIZATION', x),
                   lambda x: select_row(balance_sheet, "Cash", x),
                   lambda x: calc_helper(balance_sheet, None, lambda y, z: y + z, 'Cash + Short Term Investments',
                                         'Cash',
                                         'Short Term Investments', x),
                   lambda x: calc_helper(balance_sheet, None, lambda y, z: y - z, 'Cash Minus Liabilities', 'Cash',
                                         'Total Liab',
                                         x),
                   lambda x: select_row(balance_sheet, "Total Stockholder Equity", x),
                   lambda x: select_row(balance_sheet, "Total Assets", x),
                   lambda x: add_empty_line(financials, '', x),
                   lambda x: add_empty_line(financials, 'CAPEX', x),
                   lambda x: select_row(cash_flow, 'Capital Expenditures', x),
                   lambda x: select_row(cash_flow, 'Depreciation', x),
                   lambda x: add_empty_line(financials, '', x),
                   lambda x: add_empty_line(financials, 'RETURN RATIOS', x),
                   lambda x: calc_helper(financials, balance_sheet, lambda y, z: y / z, 'ROE',
                                         'Net Income Applicable To Common Shares',
                                         'Total Stockholder Equity',
                                         x),
                   lambda x: add_empty_line(financials, '', x),
                   lambda x: add_empty_line(financials, 'SHARES', x),
                   lambda x: select_row(cash_flow, 'Repurchase Of Stock', x)])
