import pandas as pd
from script_calc import Calc

pd.set_option('display.max_columns', 500)
pd.set_option('display.max_rows', 500)
pd.set_option('display.width', 500)

c = Calc()
data = c.load_data('D_R_Horton')
revenue = c.get_line(data, c.income_statement, 'Sales', 'Sales')
cost_of_sale = c.get_line(data, c.income_statement, 'Cost of sales', 'Cost of Sales')
inventory = c.get_line(data, c.balance_sheet, 'Total inventory', 'Inventory')
profit = c.get_line(data, c.income_statement, 'Net income', 'Profit')
operating_cash_flow = c.get_line(data, c.cash_flow, 'operating activities', 'Operating Cash Flow')
equity = c.get_line(data, c.balance_sheet, 'Total equity', 'Equity')
eps = c.get_and_operate_on_lines(data, c.income_statement, ['Diluted',
                                                            'Net income per common share assuming dilution'],
                                 'Diluted EPS')
assets_less_cash = c.get_and_operate_on_lines(data, c.balance_sheet, ['Total assets',
                                                                      'Cash and cash equivalents'],
                                              'Assets less Cash',
                                              False)
retained_earnings = c.get_line(data, c.balance_sheet, 'Retained earnings', 'Retained Earnings')
owners_earnings = c.get_and_operate_on_lines(data, c.cash_flow, ['Net income',
                                                                 'Depreciation',
                                                                 'Ammortization',
                                                                 'Expenditures',
                                                                 'business',
                                                                 'Purchases'],
                                             "Owner's Earnings")
share_repurchases = c.get_and_operate_on_lines(data, c.cash_flow, ['Purchase of treasury stock',
                                                                   'Repurchases of common stock'],
                                               'Share Repurchases')
dividends = c.get_line(data, c.cash_flow, 'Cash dividends paid', 'Dividends')
results = pd.concat([revenue,
                     cost_of_sale,
                     profit,
                     inventory,
                     equity,
                     assets_less_cash]).dropna(axis=1)

# Earnings
earnings = pd.concat([revenue,
                      profit,
                      owners_earnings,
                      retained_earnings,
                      eps,
                      operating_cash_flow]).dropna(axis=1)

# Ratios
ratios = c.operate_on_results_onto_new_df(results, pd.DataFrame(), 'Cost of Sales', 'Inventory', c.divide,
                                          'Inventory Turnover')

# Returns
returns = c.operate_on_results_onto_new_df(results, pd.DataFrame(), 'Profit', 'Equity', c.divide, 'ROE')
returns = c.operate_on_results_onto_new_df(results, returns, 'Profit', 'Assets less Cash', c.divide, 'ROALC')
returns = pd.concat([returns,share_repurchases,dividends])

print(earnings)
print(ratios)
print(returns)
