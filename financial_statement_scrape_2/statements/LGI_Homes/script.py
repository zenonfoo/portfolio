import pandas as pd
from script_calc import Calc

pd.set_option('display.max_columns', 500)
pd.set_option('display.max_rows', 500)
pd.set_option('display.width', 500)

c = Calc()
data = c.load_data('LGI_Homes')
revenue = c.get_line(data, c.income_statement, 'Home sales', 'Sales')
cost_of_sales = c.get_line(data, c.income_statement, 'Cost of sales', 'Cost of Sales')
ga = c.get_line(data, c.income_statement, 'General and administrative', 'G&A')
profit = c.get_line(data, c.income_statement, 'Net income', 'Profit')
operating_cash_flow = c.get_line(data, c.cash_flow, 'operating activities', 'Operating Cash Flow')
eps = c.get_line(data, c.income_statement, 'Diluted', 'Diluted EPS')
inventory = c.get_line(data, c.balance_sheet, 'Real estate inventory', 'Inventory')
assets_less_cash = c.get_and_operate_on_lines(data, c.balance_sheet, ['Total assets',
                                                                      'Cash and cash equivalents'],
                                              'Assets less Cash',
                                              False)
equity = c.get_line(data, c.balance_sheet, 'Total equity', 'Equity')
owners_earnings = c.get_and_operate_on_lines(data, c.cash_flow, ['Net income',
                                                                 'Depreciation',
                                                                 'Purchases',
                                                                 'business acquisition',
                                                                 'unconsolidated'],
                                             "Owner's Earnings")
retained_earnings = c.get_line(data, c.balance_sheet, 'Retained earnings', 'Retained Earnings')

results = pd.concat([revenue,
                     cost_of_sales,
                     ga,
                     profit,
                     inventory,
                     assets_less_cash,
                     equity]).dropna(axis=1)

# Earnings
earnings = pd.concat([revenue,
                      profit,
                      owners_earnings,
                      retained_earnings,
                      eps,
                      operating_cash_flow]).dropna(axis=1)
# ratios
ratios = c.operate_on_results_onto_new_df(results, pd.DataFrame(), 'G&A', 'Sales', c.divide, 'G&A Margin')
ratios = c.operate_on_results_onto_new_df(results, ratios, 'Cost of Sales', 'Inventory', c.divide, 'Inventory Turnover')

# Returns
returns = c.operate_on_results_onto_new_df(results, pd.DataFrame(), 'Profit', 'Assets less Cash', c.divide, 'ROALC')
returns = c.operate_on_results_onto_new_df(results, returns, 'Profit', 'Equity', c.divide, 'ROE')

print(earnings)
print(ratios)
print(returns)
