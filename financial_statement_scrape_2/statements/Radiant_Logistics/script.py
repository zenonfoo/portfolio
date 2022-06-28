import pandas as pd
from script_calc import Calc

pd.set_option('display.max_columns', 500)
pd.set_option('display.max_rows', 500)
pd.set_option('display.width', 500)


def thousand_wrapper(data: pd.DataFrame):
    temp = data.iloc[:, -2:].applymap(lambda x: x / 1000).combine_first(data)
    return temp[temp.columns[::-1]]


c = Calc(thousand_wrapper)
data = c.load_data('Radiant_Logistics')
revenue = c.get_line(data, c.income_statement, 'Revenues', 'Sales')
profits = c.get_line(data, c.income_statement, 'attributable to Radiant Logistics, Inc.', 'Profit')
retained_earnings = c.get_line(data, c.balance_sheet, 'Retained earnings', 'Retained Earnings')
equity = c.get_line(data, c.balance_sheet, 'Total stockholders’ equity', 'Equity')
assets_less_cash = c.get_and_operate_on_lines(data,
                                              c.balance_sheet,
                                              ['Total assets',
                                               'Cash and cash equivalents'],
                                              'Assets less Cash',
                                              False)
results = pd.concat([revenue,
                     profits,
                     retained_earnings,
                     equity,
                     assets_less_cash]).dropna(axis=1)

returns = c.operate_on_results_onto_new_df(results, pd.DataFrame(), 'Profit', 'Equity', c.divide, 'ROE')
returns = c.operate_on_results_onto_new_df(results, returns, 'Profit', 'Assets less Cash', c.divide, 'ROALC')
print(returns)
