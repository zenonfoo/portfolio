from multiprocessing import Pool
import pandas as pd
from functools import reduce
from models import FinancialData, UnprocessedFinancialData, ProcessedFinancialData
from typing import List


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


def calc_capex_ratio(data: pd.DataFrame) -> pd.DataFrame:
    result_name = 'Capex Plus Deprec Over Income'
    try:
        capex = data.loc['Capital Expenditure']
        deprec = data.loc['Depreciation And Amortization']
        income = data.loc['Net Income Common Stockholders']
        result = (capex + deprec) / income
        result.name = result_name
        result = pd.DataFrame(result).transpose()
    except:
        result = value_when_error_thrown(data, result_name)

    return pd.concat([data, result])


def space_out_index_helper(name: str) -> str:
    new_str = name[0]
    prev_str = name[0]

    for current_str in name[1:]:
        if prev_str.islower() and current_str.isupper():
            new_str = new_str + ' ' + current_str
        else:
            new_str += current_str
        prev_str = current_str

    return new_str


def space_out_index(data: pd.DataFrame) -> pd.DataFrame:
    statement = data.copy()
    new_index = [space_out_index_helper(i) for i in statement.index]
    statement.index = new_index

    return statement


def combine_dates(data: List[FinancialData]) -> FinancialData:
    if len(data) == 1:
        return FinancialData(space_out_index(data[0].income_statement), space_out_index(data[0].balance_sheet),
                             space_out_index(data[0].cash_flow))
    else:
        descending_data_by_year = sorted(data, key=lambda x: x.income_statement.columns.sort_values()[-1], reverse=True)
        income_statement = descending_data_by_year[0].income_statement
        balance_sheet = descending_data_by_year[0].balance_sheet
        cash_flow = descending_data_by_year[0].cash_flow

        for d in descending_data_by_year[1:]:
            income_statement = income_statement.combine_first(d.income_statement)
            balance_sheet = balance_sheet.combine_first(d.balance_sheet)
            cash_flow = cash_flow.combine_first(d.cash_flow)

        return FinancialData(space_out_index(income_statement), space_out_index(balance_sheet),
                             space_out_index(cash_flow))


def calc(data: UnprocessedFinancialData) -> ProcessedFinancialData:
    combined_dates = combine_dates(data.financial_data)
    income_statement = combined_dates.income_statement
    balance_sheet = combined_dates.balance_sheet
    cash_flow = combined_dates.cash_flow
    summary_data: pd.DataFrame = reduce(lambda x, y: y(x),
                                        [None,
                                         lambda x: add_empty_line(income_statement, 'EARNINGS', x),
                                         lambda x: select_row(income_statement, 'Total Revenue', x),
                                         lambda x: select_row(income_statement, 'Operating Income', x),
                                         lambda x: select_row(income_statement, 'Net Income Common Stockholders', x),
                                         lambda x: select_row(cash_flow, 'Operating Cash Flow', x),
                                         lambda x: select_row( cash_flow, 'Free Cash Flow', x),
                                         lambda x: select_row(balance_sheet, 'Retained Earnings', x),
                                         lambda x: select_row(cash_flow, 'Cash Dividends Paid', x),
                                         lambda x: calc_helper(cash_flow, income_statement, lambda y, z: y / z,
                                                               'Dividend Payout Ratio',
                                                               'Cash Dividends Paid',
                                                               'Net Income Common Stockholders',
                                                               x),
                                         lambda x: add_empty_line(income_statement, '', x),
                                         lambda x: add_empty_line(income_statement, 'EARNINGS MARGINS', x),
                                         lambda x: calc_helper(income_statement, None, lambda y, z: y / z,
                                                               'Gross Profit Margin',
                                                               'Operating Revenue',
                                                               'Total Revenue',
                                                               x),
                                         lambda x: calc_helper(income_statement, None, lambda y, z: y / z,
                                                               'Operating Margin',
                                                               'Operating Income', 'Total Revenue',
                                                               x),
                                         lambda x: add_empty_line(income_statement, '', x),
                                         lambda x: add_empty_line(income_statement, 'BALANCE SHEET RATIOS', x),
                                         lambda x: calc_helper(balance_sheet, None, lambda y, z: y / z, 'Current Ratio',
                                                               'Current Assets',
                                                               'Current Liabilities', x),
                                         lambda x: calc_helper(balance_sheet, None, lambda y, z: y / z,
                                                               'Assets over Liabilities',
                                                               'Total Assets',
                                                               'Total Liabilities Net Minority Interest',
                                                               x),
                                         lambda x: calc_helper(balance_sheet, income_statement, lambda y, z: y / z,
                                                               'Inventory Turnover', 'Inventory', 'Cost Of Revenue', x),
                                         lambda x: calc_helper(balance_sheet, income_statement, lambda y, z: y / z,
                                                               'Day Sales Outstanding', 'Receivables',
                                                               'Total Revenue', x),
                                         lambda x: add_empty_line(income_statement, '', x),
                                         lambda x: add_empty_line(income_statement, 'CAPITALIZATION', x),
                                         lambda x: select_row(balance_sheet, "Cash And Cash Equivalents", x),
                                         lambda x: select_row(balance_sheet,
                                                              "Cash Cash Equivalents And Short Term Investments", x),
                                         lambda x: calc_helper(balance_sheet, None, lambda y, z: y - z,
                                                               'Cash Minus Liabilities',
                                                               'Cash And Cash Equivalents',
                                                               'Total Liabilities Net Minority Interest',
                                                               x),
                                         lambda x: select_row(balance_sheet, "Stockholders Equity", x),
                                         lambda x: select_row(balance_sheet, "Total Assets", x),
                                         lambda x: add_empty_line(income_statement, '', x),
                                         lambda x: add_empty_line(income_statement, 'CAPEX', x),
                                         lambda x: select_row(cash_flow, 'Capital Expenditure', x),
                                         lambda x: select_row(cash_flow, 'Depreciation And Amortization', x),
                                         lambda x: calc_capex_ratio(x),
                                         lambda x: add_empty_line(income_statement, '', x),
                                         lambda x: add_empty_line(income_statement, 'RETURN RATIOS', x),
                                         lambda x: calc_helper(income_statement, balance_sheet, lambda y, z: y / z,
                                                               'ROE',
                                                               'Net Income Common Stockholders',
                                                               'Stockholders Equity',
                                                               x),
                                         lambda x: add_empty_line(income_statement, '', x),
                                         lambda x: add_empty_line(income_statement, 'SHARES', x),
                                         lambda x: select_row(cash_flow, 'Repurchase Of Capital Stock', x)])
    return ProcessedFinancialData(combined_dates, summary_data.dropna(axis=1), data.metadata)


def calc_many(data: List[UnprocessedFinancialData]):
    p = Pool()
    return p.map(calc, data)
