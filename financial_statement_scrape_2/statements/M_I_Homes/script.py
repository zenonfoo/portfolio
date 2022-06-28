import pandas as pd
from script_calc import Calc

pd.set_option('display.max_columns', 500)
pd.set_option('display.max_rows', 500)
pd.set_option('display.width', 500)

c = Calc()
data = c.load_data('M_I_Homes')
revenue = c.get_line(data, c.income_statement, 'Revenue', 'Sales')
profit = c.get_line(data, c.income_statement, 'Net income', 'Profit')
diluted_eps = c.get_line(data, c.income_statement, 'Diluted', 'Diluted EPS')
land_housing = c.get_line(data, c.income_statement, 'Land and housing', 'Land and Housing')
impairment_of_inventory = c.get_line(data, c.income_statement, 'Impairment of inventory', 'Impairment of Inventory')
inventory = c.get_line(data, c.balance_sheet, 'Inventory', 'Inventory')
assets_less_cash = c.get_and_operate_on_lines(data, c.balance_sheet, ['TOTAL ASSETS', 'cash equivalents'],
                                              'Assets less Cash', False)
equity = c.get_line(data, c.balance_sheet, 'TOTAL SHAREHOLDERS', 'Equity')
owners_earnings = c.get_and_operate_on_lines(data, c.cash_flow, ['Net income',
                                                                 'Depreciation',
                                                                 'Ammortization',
                                                                 'Acquisition',
                                                                 'Purchase',
                                                                 'Investment'],
                                             "Owner's Earnings")
retained_earnings = c.get_line(data, c.balance_sheet, 'Retained earnings', 'Retained Earnings')

results = pd.concat([revenue,
                     land_housing,
                     impairment_of_inventory,
                     profit,
                     diluted_eps,
                     inventory,
                     assets_less_cash,
                     equity]).dropna(axis=1)

# Earnings
earnings = pd.concat([revenue,
                      profit,
                      diluted_eps,
                      owners_earnings,
                      retained_earnings])
# Ratios
ratios = c.operate_on_results_onto_new_df(results, pd.DataFrame(), 'Impairment of Inventory', 'Sales', c.divide,
                                          'Inventory Impairment Margin')
ratios = c.operate_on_results_onto_new_df(results, ratios, 'Land and Housing', 'Sales', lambda x, y: 1 - (x / y),
                                          'Gross Margin')
ratios = c.operate_on_results_onto_new_df(results, ratios, 'Land and Housing', 'Inventory', c.divide,
                                          'Inventory Turnover')

# Returns
returns = c.operate_on_results_onto_new_df(results, pd.DataFrame(), 'Profit', 'Assets less Cash', c.divide,
                                           'ROALC')
returns = c.operate_on_results_onto_new_df(results, returns, 'Profit', 'Equity', c.divide,
                                           'ROE')
print(earnings)
print(ratios)
print(returns)
