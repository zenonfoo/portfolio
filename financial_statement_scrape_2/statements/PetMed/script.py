import pandas as pd
from script_calc import Calc

pd.set_option('display.max_columns', 500)
pd.set_option('display.max_rows', 500)
pd.set_option('display.width', 500)

c = Calc()
data = c.load_data('PetMed')
revenue = c.get_line(data, 'income_statement', 'Sales', 'Sales')
cost_of_sales = c.get_line(data, 'income_statement', 'Cost of sales', 'Cost of sales')
profit = c.get_line(data, 'income_statement', 'Net income', 'Net income')
assets_less_cash_and_securities = c.get_and_operate_on_lines(data, 'balance_sheet',
                                                                       ['Total assets',
                                                                        'Short term investments',
                                                                        'Cash and cash equivalents'],
                                                                       'Assets less Cash and Securities',
                                                                       False)
equity = c.get_line(data, 'balance_sheet', 'Total shareholders', 'Equity')
owners_earnings = c.get_and_operate_on_lines(data, 'cash_flow', ['Net income',
                                                                           'Depreciation',
                                                                           'Purchases of property and equipment'],
                                                       "Owner's Earnings")
cash = c.get_line(data, 'balance_sheet', 'Cash and cash equivalents', 'Cash')
inventory = c.get_line(data, 'balance_sheet', 'nventories', 'Inventories')
retained_earnings = c.get_line(data, 'balance_sheet', 'Retained earnings', 'Retained earnings')
operating_cash_flow = c.get_line(data, 'cash_flow', 'operating activities', 'Operating Cash Flow')
dividends = c.get_line(data, 'cash_flow', 'Dividends', 'Dividends')
advertising = c.get_line(data, 'income_statement', 'Advertising', 'Advertising')
results = pd.concat(
    [revenue, cost_of_sales, advertising, profit, operating_cash_flow, assets_less_cash_and_securities, equity,
     owners_earnings, cash, inventory, retained_earnings, dividends]).dropna(axis=1)

# Gross Margin
gross_margin = results.loc['Cost of sales'] / results.loc['Sales']
gross_margin.name = 'Gross Margin'
margins = pd.DataFrame(gross_margin).transpose()

# Advertising Margin
margins = c.operate_on_results_onto_new_df(results, margins, 'Advertising', 'Sales', c.divide, 'Advertising Margin')

# return of assets less cash and securities
roalcas = results.loc['Net income'] / results.loc['Assets less Cash and Securities']
roalcas.name = 'Return on Assets less Cash and Securities'
returns = pd.DataFrame(roalcas).transpose()

# ROE
roe = results.loc['Net income'] / results.loc['Equity']
roe.name = 'ROE'
returns = pd.concat([returns, pd.DataFrame(roe).transpose()])

# Inventory turnover
inventory_turnover = results.loc['Cost of sales'] / results.loc['Inventories']
inventory_turnover.name = 'Inventory Turnover'
results = pd.concat([results, pd.DataFrame(inventory_turnover).transpose()])

print(results)
print(returns)
print(margins)