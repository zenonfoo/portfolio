import pandas as pd
from functools import reduce
from multiprocessing import Pool
from typing import List
import numpy as np
from enum import Enum


class YearlyQuarterly(Enum):
    YEARLY = 1
    QUARTERLY = 2
    NUMERATOR_QUARTERLY = 3
    DENOMINATOR_QUARTERLY = 4


def add(x, y):
    try:
        return x + y
    except:
        return x


def divide_selector(selector: YearlyQuarterly, num_or_denom=None):
    if selector == YearlyQuarterly.YEARLY:
        return lambda x, y: x.replace(0, np.nan) / y.replace(0, np.nan)
    elif selector == YearlyQuarterly.QUARTERLY:
        if num_or_denom == YearlyQuarterly.NUMERATOR_QUARTERLY:
            return lambda x, y: (x.replace(0, np.nan) * 4) / y.replace(0, np.nan)
        elif num_or_denom == YearlyQuarterly.DENOMINATOR_QUARTERLY:
            return lambda x, y: x.replace(0, np.nan) / (y.replace(0, np.nan) * 4)
        else:
            return lambda x, y: x.replace(0, np.nan) / y.replace(0, np.nan)
    else:
        raise Exception('Selector = {}'.format(selector))


def value_when_error_thrown(data: dict, row_name: str, statement: str):
    col_length = data[statement].shape[1]
    col_names = data[statement].columns
    df_data = ['-'] * col_length
    return pd.DataFrame([df_data], columns=col_names, index=[row_name])


def select_row(data: dict, row_name: str, statement: str) -> dict:
    try:
        row = pd.DataFrame(data[statement].loc[row_name]).transpose()
    except:
        row = value_when_error_thrown(data, row_name, statement)

    k = list(data.keys())
    if 'summary_data' in k:
        data['summary_data'] = pd.concat([data['summary_data'], row])
    else:
        data['summary_data'] = row
    return data


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

    k = list(data.keys())
    if 'summary_data' in k:
        data['summary_data'] = pd.concat([data['summary_data'], result])
    else:
        data['summary_data'] = result
    return data


# Includes Amortization
def depreciation_over_ppe(data: dict) -> dict:
    try:
        balance_sheet = data['balance_sheet']
        depreciation = data['cash_flow'].loc['Depreciation & amortisation']
        result = balance_sheet.loc['Property Plant And Equipment, Net'].copy()
        for name in ['Goodwill', 'Other Intangibles']:
            try:
                result += balance_sheet.loc[name]
            except:
                pass
        dppe = depreciation.replace(0, np.nan) / result.replace(0, np.nan)
        dppe.name = 'Depreciation over PPE'
        dppe = pd.DataFrame(dppe).transpose()
    except:
        dppe = value_when_error_thrown(data, 'Depreciation over PPE', 'income_statement')
    data['summary_data'] = pd.concat([data['summary_data'], dppe])
    return data


def return_on_non_cash_assets(data: dict, func) -> dict:
    try:
        income_statement = data['income_statement']
        balance_sheet = data['balance_sheet']
        net_income = income_statement.loc['Net income available to common shareholders']
        result = balance_sheet.loc['Total assets'].copy()
        result -= balance_sheet.loc['Total cash']
        ronca = func(net_income, result)
        ronca.name = 'Return on Non Cash Assets'
        ronca = pd.DataFrame(ronca).transpose()
    except:
        ronca = value_when_error_thrown(data, 'Return on Non Cash Assets', 'income_statement')

    data['summary_data'] = pd.concat([data['summary_data'], ronca])
    return data


def return_on_tangible_assets(data: dict, func) -> dict:
    try:
        income_statement = data['income_statement']
        balance_sheet = data['balance_sheet']
        net_income = income_statement.loc['Net income available to common shareholders']
        result = balance_sheet.loc['Total assets'].copy()
        for name in ['Goodwill', 'Intangible assets']:
            try:
                result -= balance_sheet.loc[name]
            except:
                pass
        ronta = func(net_income, result)
        ronta.name = 'Return on Net Tangible Assets'
        ronta = pd.DataFrame(ronta).transpose()
    except:
        ronta = value_when_error_thrown(data, 'Return on Tangible Assets', 'income_statement')

    data['summary_data'] = pd.concat([data['summary_data'], ronta])
    return data


def return_on_tangible_assets_less_cash(data: dict, func) -> dict:
    try:
        income_statement = data['income_statement']
        balance_sheet = data['balance_sheet']
        net_income = income_statement.loc['Net income available to common shareholders']
        result = balance_sheet.loc['Total assets'].copy()
        for name in ['Goodwill', 'Intangible assets', 'Total cash']:
            try:
                result -= balance_sheet.loc[name]
            except:
                pass
        ronta = func(net_income, result)
        ronta.name = 'Return on Net Tangible Assets less Cash'
        ronta = pd.DataFrame(ronta).transpose()
    except:
        ronta = value_when_error_thrown(data, 'Return on Net Tangible Assets less Cash', 'income_statement')

    data['summary_data'] = pd.concat([data['summary_data'], ronta])
    return data


def owners_earnings(data: dict) -> dict:
    cash_flow = data['cash_flow']
    income_statement = data['income_statement']
    result = income_statement.loc['Net income available to common shareholders'].copy()
    for name in ['Depreciation & amortisation',
                 'Capital Expenditures',
                 'Acquisitions, net']:
        try:
            result += cash_flow.loc[name]
        except:
            pass
    result.name = "Owner's Earnings"
    result = pd.DataFrame(result).transpose()
    data['summary_data'] = pd.concat([data['summary_data'], result])
    return data


def add_empty_line(data: dict, name: str) -> dict:
    col_length = data['income_statement'].shape[1]
    col_names = data['income_statement'].columns
    df_data = [''] * col_length
    result = pd.DataFrame([df_data], columns=col_names, index=[name])
    k = list(data.keys())
    if 'summary_data' in k:
        data['summary_data'] = pd.concat([data['summary_data'], result])
    else:
        data['summary_data'] = result
    return data


def calc(data: dict, divide_type: YearlyQuarterly) -> dict:
    return reduce(lambda x, y: y(x),
                  [data,
                   lambda x: add_empty_line(x, 'EARNINGS'),
                   lambda x: select_row(x, 'Total revenue', 'income_statement'),
                   lambda x: select_row(x, 'Operating income or loss', 'income_statement'),
                   lambda x: select_row(x, 'Net income available to common shareholders', 'income_statement'),
                   owners_earnings,
                   lambda x: calc_helper(x, lambda y, z: y + z, 'Cash Flow Minus Capex', 'Operating cash flow',
                                         'Capital expenditure', 'cash_flow'),
                   lambda x: select_row(x, 'Retained earnings', 'balance_sheet'),
                   lambda x: select_row(x, 'Dividends paid', 'cash_flow'),
                   lambda x: calc_helper(x, divide_selector(divide_type), 'Dividends over Earnings',
                                         'Dividends paid', 'Net income available to common shareholders', 'cash_flow',
                                         'income_statement'),
                   lambda x: add_empty_line(x, ''),
                   lambda x: add_empty_line(x, 'EARNINGS MARGINS'),
                   lambda x: calc_helper(x, divide_selector(divide_type), 'Gross profit margin', 'Gross profit',
                                         'Total revenue',
                                         'income_statement'),
                   lambda x: calc_helper(x, divide_selector(divide_type), 'Operating Margin',
                                         'Operating income or loss', 'Total revenue',
                                         'income_statement'),
                   lambda x: add_empty_line(x, ''),
                   lambda x: add_empty_line(x, 'BALANCE SHEET RATIOS'),
                   lambda x: calc_helper(x, divide_selector(divide_type), 'Quick Ratio', 'Total cash',
                                         'Total current liabilities', 'balance_sheet'),
                   lambda x: calc_helper(x, divide_selector(divide_type), 'Current Ratio', 'Total current assets',
                                         'Total current liabilities', 'balance_sheet'),
                   lambda x: calc_helper(x, divide_selector(divide_type), 'Assets over Liabilities', 'Total assets',
                                         'Total liabilities',
                                         'balance_sheet'),
                   lambda x: calc_helper(x, divide_selector(divide_type, YearlyQuarterly.DENOMINATOR_QUARTERLY),
                                         'Inventory Turnover', 'Inventory', 'Cost of revenue',
                                         'balance_sheet', 'income_statement'),
                   lambda x: calc_helper(x, divide_selector(divide_type, YearlyQuarterly.DENOMINATOR_QUARTERLY),
                                         'Day Sales Outstanding', 'Net receivables',
                                         'Total revenue', 'balance_sheet', 'income_statement'),
                   lambda x: add_empty_line(x, ''),
                   lambda x: add_empty_line(x, 'CAPITALIZATION'),
                   lambda x: select_row(x, 'Total cash', 'balance_sheet'),
                   lambda x: calc_helper(x, lambda y, z: y - z, 'NCAV', 'Total current assets', 'Total liabilities',
                                         'balance_sheet'),
                   lambda x: calc_helper(x, lambda y, z: y - z, 'Cash Minus Liabilities', 'Total cash',
                                         'Total liabilities',
                                         'balance_sheet'),
                   lambda x: select_row(x, "Total stockholders' equity", 'balance_sheet'),
                   lambda x: select_row(x, "Total assets", 'balance_sheet'),
                   lambda x: add_empty_line(x, ''),
                   lambda x: add_empty_line(x, 'CAPEX'),
                   lambda x: select_row(x, 'Net property, plant and equipment', 'balance_sheet'),
                   lambda x: select_row(x, 'Capital expenditure', 'cash_flow'),
                   lambda x: select_row(x, 'Depreciation & amortisation', 'cash_flow'),
                   lambda x: add_empty_line(x, ''),
                   lambda x: add_empty_line(x, 'RETURN RATIOS'),
                   lambda x: return_on_non_cash_assets(x, divide_selector(divide_type,
                                                                          YearlyQuarterly.NUMERATOR_QUARTERLY)),
                   lambda x: return_on_tangible_assets(x, divide_selector(divide_type,
                                                                          YearlyQuarterly.NUMERATOR_QUARTERLY)),
                   lambda x: calc_helper(x, divide_selector(divide_type, YearlyQuarterly.NUMERATOR_QUARTERLY), 'ROE',
                                         'Net income available to common shareholders',
                                         "Total stockholders' equity",
                                         'income_statement',
                                         'balance_sheet'),
                   lambda x: add_empty_line(x, ''),
                   lambda x: add_empty_line(x, 'SHARES'),
                   lambda x: select_row(x, 'Common stock repurchased', 'cash_flow'),
                   lambda x: select_row(x, 'Diluted average shares', 'income_statement')])


def calc_many(data: List[dict], divide_type: YearlyQuarterly) -> List[dict]:
    p = Pool()
    return p.map(lambda x: calc(x, divide_type), data)
