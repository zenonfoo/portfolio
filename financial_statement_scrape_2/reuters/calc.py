from typing import List
import pandas as pd
from yahoo.calc import value_when_error_thrown, YearlyQuarterly, divide_selector
import numpy as np

INCOME_STATEMENT = 'income_statement'
BALANCE_SHEET = 'balance_sheet'
CASH_FLOW = 'cash_flow'


def ratio_and_merge(data: List[pd.DataFrame], first: str, second: str):
    results = []
    for x in data:
        result = x.loc[first] / x.loc[second]
        result.name = x.name
        results.append(pd.DataFrame(result).transpose())
    return pd.concat(results)


def ratio_and_merge_2(data: List[pd.DataFrame], first: str, second: str):
    results = []
    for i, b in data:
        result = i.loc[first] / b.loc[second]
        result.name = i.name
        results.append(pd.DataFrame(result).transpose())
    return pd.concat(results)


def get_from_statement(data: dict, statement: str, key_name: str, name: str):
    s = data[statement]
    result = s.loc[key_name]
    result.name = name
    return pd.DataFrame(result).transpose()


def ratio_one_statement(data: dict, statement: str, first: str, second: str, name: str):
    s = data[statement]
    result = s.loc[first] / s.loc[second]
    result.name = name
    return pd.DataFrame(result).transpose()


def ratio_two_statements(data: dict, statement_1: str, statement_2: str, first: str, second: str, name: str):
    s1 = data[statement_1]
    s2 = data[statement_2]
    result = s1.loc[first] / s2.loc[second]
    result.name = name
    return pd.DataFrame(result).transpose()


def calc_roalc(data: dict, func):
    income_statement = data['income_statement']
    balance_sheet = data['balance_sheet']
    margin = func(income_statement.loc['Net Income'], (
            balance_sheet.loc['Total Assets'] - balance_sheet.loc['Cash and Short Term Investments']))
    margin.name = 'ROALC'
    return pd.DataFrame(margin).transpose()


def return_on_non_cash_assets(data: dict, func) -> dict:
    try:
        income_statement = data['income_statement']
        balance_sheet = data['balance_sheet']
        net_income = income_statement.loc['Net Income']
        result = balance_sheet.loc['Total Assets'].copy()
        result -= balance_sheet.loc['Cash and Short Term Investments']
        ronca = func(net_income, result)
        ronca.name = 'Return on Non Cash Assets'
        ronca = pd.DataFrame(ronca).transpose()
    except:
        ronca = value_when_error_thrown(data, 'Return on Non Cash Assets', 'income_statement')

    return ronca


def return_on_tangible_assets(data: dict, func) -> dict:
    try:
        income_statement = data['income_statement']
        balance_sheet = data['balance_sheet']
        net_income = income_statement.loc['Net Income']
        result = balance_sheet.loc['Total Assets'].copy()
        for name in ['Goodwill, Net', 'Intangible, Net']:
            try:
                result -= balance_sheet.loc[name]
            except:
                pass
        ronta = func(net_income, result)
        ronta.name = 'Return on Net Tangible Assets'
        ronta = pd.DataFrame(ronta).transpose()
    except:
        ronta = value_when_error_thrown(data, 'Return on Net Tangible Assets', 'income_statement')

    return ronta


def return_on_tangible_assets_less_cash(data: dict, func) -> dict:
    try:
        income_statement = data['income_statement']
        balance_sheet = data['balance_sheet']
        net_income = income_statement.loc['Net Income']
        result = balance_sheet.loc['Total Assets'].copy()
        for name in ['Goodwill, Net', 'Intangibles, Net', 'Cash and Short Term Investments']:
            try:
                result -= balance_sheet.loc[name]
            except:
                pass
        ronta = func(net_income, result)
        ronta.name = 'Return on Net Tangible Assets less Cash'
        ronta = pd.DataFrame(ronta).transpose()
    except:
        ronta = value_when_error_thrown(data, 'Return on Net Tangible Assets less Cash', 'income_statement')

    return ronta


def calc_owners_earnings(data: dict):
    cash_flow = data['cash_flow']
    results = data['income_statement'].loc['Net Income'].copy()
    for line in ['Depreciation/Depletion', 'Capital Expenditures']:
        results += cash_flow.loc[line]
    results.name = "Owner's Earnings"
    return pd.DataFrame(results).transpose()


def insert_line(data: dict, name: str):
    some_statement = data['income_statement']
    df_data = [''] * some_statement.shape[1]
    return pd.DataFrame(data=[df_data], index=[name], columns=some_statement.columns)


def calc_helper(data: dict, func, result_name: str, numerator: str, denominator: str, first_statement: str,
                second_statement=None) -> dict:
    try:
        if second_statement:
            denominator_val = data[second_statement].loc[denominator]
        else:
            denominator_val = data[first_statement].loc[denominator]
        numerator_val = data[first_statement].loc[numerator]
        result = func(numerator_val, denominator_val)
        result.name = result_name
        result = pd.DataFrame(result).transpose()
    except:
        result = value_when_error_thrown(data, result_name, first_statement)

    return result


def calc(data: dict, divide_type: YearlyQuarterly):
    functions = [lambda x: insert_line(x, 'Earnings'),
                 lambda x: get_from_statement(x, INCOME_STATEMENT, 'Total Revenue', 'Revenue'),
                 lambda x: get_from_statement(x, INCOME_STATEMENT, 'Operating Income', 'Operating Profit'),
                 lambda x: get_from_statement(x, INCOME_STATEMENT, 'Net Income', 'Profit'),
                 calc_owners_earnings,
                 lambda x: calc_helper(x, lambda y, z: y - z, 'Cash Flow Minus Capex', 'Cash from Operating Activities',
                                       'Capital Expenditures', CASH_FLOW),
                 lambda x: get_from_statement(x, BALANCE_SHEET, 'Retained Earnings (Accumulated Deficit)',
                                              'Retained Earnings'),
                 lambda x: get_from_statement(x, CASH_FLOW, 'Total Cash Dividends Paid', 'Dividends'),
                 lambda x: ratio_two_statements(x, CASH_FLOW, INCOME_STATEMENT, 'Total Cash Dividends Paid',
                                                'Net Income',
                                                'Dividends over Earnings'),
                 lambda x: insert_line(x, ''),
                 lambda x: insert_line(x, 'Margins'),
                 lambda x: ratio_one_statement(x, INCOME_STATEMENT, 'Gross Profit', 'Total Revenue', 'Gross Margin'),
                 lambda x: ratio_one_statement(x, INCOME_STATEMENT, 'Operating Income', 'Total Revenue',
                                               'Operating Margin'),
                 lambda x: insert_line(x, ''),
                 lambda x: insert_line(x, 'Balance Sheet Ratios'),
                 lambda x: ratio_one_statement(x, BALANCE_SHEET, 'Cash and Short Term Investments',
                                               'Total Current Liabilities', 'Quick Ratio'),
                 lambda x: ratio_one_statement(x, BALANCE_SHEET, 'Total Current Assets',
                                               'Total Current Liabilities', 'Current Ratio'),
                 lambda x: ratio_one_statement(x, BALANCE_SHEET, 'Total Assets',
                                               'Total Liabilities', 'Assets over Liabilities'),
                 lambda x: calc_helper(x, divide_selector(divide_type, YearlyQuarterly.NUMERATOR_QUARTERLY),
                                       'Inventory Turnover', 'Total Inventory', 'Cost of Revenue, Total', BALANCE_SHEET,
                                       INCOME_STATEMENT),
                 lambda x: calc_helper(x, divide_selector(divide_type, YearlyQuarterly.DENOMINATOR_QUARTERLY),
                                       'Day Sales Outstanding', 'Total Receivables, Net', 'Total Revenue',
                                       BALANCE_SHEET,
                                       INCOME_STATEMENT),
                 lambda x: insert_line(x, ''),
                 lambda x: insert_line(x, 'Capitalization'),
                 lambda x: get_from_statement(x, BALANCE_SHEET, 'Cash and Short Term Investments',
                                              'Cash and Short Term Investments'),
                 lambda x: calc_helper(x, lambda y, z: y - z, 'Cash Minus Liabilities',
                                       'Cash and Short Term Investments',
                                       'Total Liabilities',
                                       BALANCE_SHEET),
                 lambda x: calc_helper(x, lambda y, z: y - z, 'NCAV',
                                       'Total Current Assets',
                                       'Total Liabilities',
                                       BALANCE_SHEET),
                 lambda x: get_from_statement(x, BALANCE_SHEET, 'Total Equity', 'Equity'),
                 lambda x: get_from_statement(x, BALANCE_SHEET, 'Total Assets', 'Total Assets'),
                 lambda x: insert_line(x, ''),
                 lambda x: insert_line(x, 'Capex'),
                 lambda x: get_from_statement(x, BALANCE_SHEET, 'Property/Plant/Equipment, Total - Net', 'PPE Net'),
                 lambda x: get_from_statement(x, CASH_FLOW, 'Capital Expenditures', 'Capital Expenditures'),
                 lambda x: get_from_statement(x, CASH_FLOW, 'Depreciation/Depletion', 'Depreciation'),
                 lambda x: insert_line(x, ''),
                 lambda x: insert_line(x, 'Returns'),
                 lambda x: ratio_two_statements(data, INCOME_STATEMENT, BALANCE_SHEET, 'Net Income', 'Total Equity',
                                                'ROE'),
                 lambda x: calc_roalc(x, divide_selector(divide_type, YearlyQuarterly.NUMERATOR_QUARTERLY)),
                 lambda x: return_on_tangible_assets(x, divide_selector(divide_type, YearlyQuarterly.NUMERATOR_QUARTERLY)),
                 lambda x: insert_line(x, ''),
                 lambda x: insert_line(x, 'Shares'),
                 lambda x: get_from_statement(x, CASH_FLOW, 'Issuance (Retirement) of Stock, Net',
                                              'Share Repurchases'),
                 lambda x: get_from_statement(x, INCOME_STATEMENT, 'Diluted Weighted Average Shares',
                                              'Diluted Shares')]
    results = []
    for func in functions:
        try:
            results.append(func(data))
        except:
            pass
    data['summary_data'] = pd.concat(results)
    return data
