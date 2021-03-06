# From 2014 and back amounts are in thousands
import pandas as pd
from script_calc import Calc
from statements.util import Data

pd.set_option('display.max_columns', 500)
pd.set_option('display.max_rows', 500)
pd.set_option('display.width', 500)


def thousand_wrapper(data: pd.DataFrame):
    temp = data.iloc[:, -3:].applymap(lambda x: x / 1000).combine_first(data)
    return temp[temp.columns[::-1]]


c = Calc(thousand_wrapper)
data = c.load_data('Gilead_Sciences')
revenue = c.get_line(data, c.income_statement, 'Total revenues', 'Sales')
profit = c.get_line(data, c.income_statement, 'Net income attributable', 'Profit')
retained_earnings = c.get_line(data, c.balance_sheet, 'Retained earnings', 'Retained Earnings')
rd = c.get_line(data, c.income_statement, 'Research', 'R&D')
marketing = c.get_line(data, c.income_statement, 'Selling', 'SG&A')
equity = c.get_line(data, c.balance_sheet, 'Total stockholdersâ€™ equity', 'Equity')
assets_less_cash = c.get_and_operate_on_lines(data,
                                              c.balance_sheet,
                                              ['Total assets', 'Cash and cash equivalents'],
                                              'Assets less Cash',
                                              False)
share_repurchases = c.get_line(data, c.cash_flow, 'Repurchases of common stock', 'Share Repurchases')
results = pd.concat([revenue,
                     profit,
                     rd,
                     marketing,
                     equity,
                     assets_less_cash,
                     share_repurchases]).dropna(axis=1)

# Earnings
earnings = pd.concat([revenue,
                      profit,
                      retained_earnings])
# Margins
margins = c.operate_on_results_onto_new_df(results, pd.DataFrame(), 'Profit', 'Sales', c.divide, 'Profit Margins')
margins = c.operate_on_results_onto_new_df(results, margins, 'R&D', 'Sales', c.divide, 'R&D Margin')
margins = c.operate_on_results_onto_new_df(results, margins, 'SG&A', 'Sales', c.divide, 'SG&A Margin')

# Returns
returns = c.operate_on_results_onto_new_df(results, pd.DataFrame(), 'Profit', 'Equity', c.divide, 'ROE')
returns = c.operate_on_results_onto_new_df(results, returns, 'Profit', 'Assets less Cash', c.divide,
                                           'Return on Assets less Cash')

# Ratios
ratios = c.operate_on_results_onto_new_df(results, pd.DataFrame(), 'Share Repurchases', 'Profit', c.divide,
                                          'Share Repurchases Over Profit')

gilead = Data('Gilead Sciences', earnings, ratios, margins, returns)

print()
print("Gilead_Sciences")
print()
print(earnings)
print()
print(margins)
print()
print(returns)
print()
print(ratios)
