import pandas as pd
from script_calc import Calc

pd.set_option('display.max_columns', 500)
pd.set_option('display.max_rows', 500)
pd.set_option('display.width', 500)

income_statement = 'income_statement'
balance_sheet = 'balance_sheet'
cash_flow = 'cash_flow'

c = Calc()

data = c.load_data('Amgen')
revenue = c.get_line(data, income_statement, 'Total revenues', 'Sales')
profit = c.get_line(data, income_statement, 'Net income', 'Profit')
equity = c.get_line(data, balance_sheet, 'Total stockholders’ equity', 'Equity')
assets_less_cash = c.get_and_operate_on_lines(data,
                                              balance_sheet,
                                              ['Total assets',
                                               'Cash and cash equivalents'],
                                              'Assets less Cash',
                                              False)
results = pd.concat([revenue,
                     profit,
                     equity,
                     assets_less_cash]).dropna(axis=1)

# Earnings
earnings = pd.concat([revenue,
                      profit])

# Returns
returns = c.operate_on_results_onto_new_df(results, pd.DataFrame(), 'Profit', 'Equity', c.divide, 'ROE')
returns = c.operate_on_results_onto_new_df(results,
                                           returns,
                                           'Profit',
                                           'Assets less Cash',
                                           c.divide,
                                           'ROALC')
