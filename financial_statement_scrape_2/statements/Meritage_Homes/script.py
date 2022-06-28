import pandas as pd
from script_calc import Calc

pd.set_option('display.max_columns', 500)
pd.set_option('display.max_rows', 500)
pd.set_option('display.width', 500)

c = Calc()
data = c.load_data('Meritage_Homes')
revenue = c.get_line(data, c.income_statement, 'Total closing revenue', 'Sales')
cost_of_closing = c.get_line(data, c.income_statement, 'Total cost of closings', 'Cost of closing')
inventory = c.get_line(data, c.balance_sheet, 'Real estate', 'Inventory')
profit = c.get_line(data, c.income_statement, 'Net', 'Profit')
retained_earnings = c.get_line(data, c.balance_sheet, 'Retained earnings', 'Retained Earnings')
assets_less_cash = c.get_and_operate_on_lines(data, c.balance_sheet, ['Total assets',
                                                                      'Cash and cash equivalents'],
                                              'Assets less Cash',
                                              False)
owners_earnings = c.get_and_operate_on_lines(data, c.cash_flow, ['Net earnings',
                                                                 'Depreciation',
                                                                 'Investments',
                                                                 'Distributions',
                                                                 'Purchases'],
                                             "Owner's Earnings")
equity = c.get_line(data, c.balance_sheet, 'Total stockholders’ equity', 'Equity')
results = pd.concat([revenue,
                     profit,
                     inventory,
                     cost_of_closing,
                     equity,
                     assets_less_cash])

# Earnings
earnings = pd.concat([revenue,
                      profit,
                      retained_earnings,
                      owners_earnings])

# Ratios
ratios = c.operate_on_results_onto_new_df(results, pd.DataFrame(), 'Cost of closing', 'Inventory', c.divide,
                                          'Inventory Turnover')

# Returns
returns = c.operate_on_results_onto_new_df(results, pd.DataFrame(), 'Profit', 'Equity', c.divide, 'ROE')
returns = c.operate_on_results_onto_new_df(results, returns, 'Profit', 'Assets less Cash', c.divide, 'ROALC')

print(earnings)
print(ratios)
print(returns)
