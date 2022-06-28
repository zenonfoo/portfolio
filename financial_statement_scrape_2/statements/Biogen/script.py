# From 2014 and back amounts are in thousands
import pandas as pd
from script_calc import Calc
from statements.util import Data

pd.set_option('display.max_columns', 500)
pd.set_option('display.max_rows', 500)
pd.set_option('display.width', 500)

income_statement = 'income_statement'
balance_sheet = 'balance_sheet'
cash_flow = 'cash_flow'


def thousand_wrapper(data: pd.DataFrame):
    temp = data.iloc[:, -4:].applymap(lambda x: x / 1000).combine_first(data)
    return temp[temp.columns[::-1]]


c = Calc(thousand_wrapper)

data = c.load_data('Biogen')
revenue = c.get_line(data, 'income_statement', 'otal revenues', 'Sales')
profits = c.get_line(data, 'income_statement', 'Net income attributable to Biogen', 'Profit')
rd = c.get_line(data, c.income_statement, 'Research', 'R&D')
sga = c.get_line(data, c.income_statement, 'Selling', 'SG&A')
assets_less_cash = c.get_and_operate_on_lines(data,
                                              'balance_sheet',
                                              ['Total assets', 'Cash and cash equivalents'],
                                              'Assets less Cash',
                                              False)
operating_cash_flow = c.get_line(data, c.cash_flow, 'Net cash flows provided by operating activities',
                                 'Operating Cash Flow')
owners_earnings_with_marketable_securities_and_stock_repurchase = c.get_and_operate_on_lines(data,
                                                                                             'cash_flow',
                                                                                             ['Net income',
                                                                                              'Depreciation',
                                                                                              'Acquisition',
                                                                                              'Purchases',
                                                                                              'Contingent consideration',
                                                                                              'Investment'],
                                                                                             "Owner's Earnings with marketable securities and stock repurchase")
marketable_securities_and_stock_purchase = c.get_and_operate_on_lines(data,
                                                                      'cash_flow',
                                                                      ['Purchases of marketable securities',
                                                                       'Purchases of treasury stock'],
                                                                      'Purchases of marketable securities and treasury stock')
retained_earnings = c.get_line(data, 'balance_sheet', 'Retained earnings', 'Retained earnings')
equity = c.get_line(data, 'balance_sheet', 'Total equity', 'Equity')
share_repurchases = c.get_line(data, 'cash_flow', 'treasury stock', 'Share repurchases')
results = pd.concat([revenue,
                     rd,
                     sga,
                     profits,
                     retained_earnings,
                     owners_earnings_with_marketable_securities_and_stock_repurchase,
                     marketable_securities_and_stock_purchase,
                     assets_less_cash,
                     equity,
                     share_repurchases,
                     operating_cash_flow]).dropna(axis=1)
results = c.operate_on_results(results,
                               "Owner's Earnings with marketable securities and stock repurchase",
                               'Purchases of marketable securities and treasury stock',
                               lambda x, y: x - y,
                               "Owner's Earnings")

# Earnings
earnings = pd.concat([revenue,
                      profits,
                      retained_earnings,
                      pd.DataFrame(results.loc["Owner's Earnings"]).transpose()])
# Margins
margin = c.operate_on_results_onto_new_df(results, pd.DataFrame(), 'R&D', 'Sales', c.divide, 'R&D Margin')
margin = c.operate_on_results_onto_new_df(results, margin, 'SG&A', 'Sales', c.divide, 'SG&A Margin')
margin = c.operate_on_results_onto_new_df(results, margin, 'Profit', 'Sales', c.divide, 'Profit Margin')

# Returns
returns = c.operate_on_results_onto_new_df(results, pd.DataFrame(), 'Profit', 'Assets less Cash', c.divide,
                                           'Return on Assets less Cash')
returns = c.operate_on_results_onto_new_df(results, returns, 'Profit', 'Equity', c.divide, 'ROE')

# Ratios
ratios = c.operate_on_results_onto_new_df(results, pd.DataFrame(), 'Share repurchases', 'Profit', c.divide,
                                          'Share Repurchases Over Profit')

results = results.drop(["Owner's Earnings with marketable securities and stock repurchase",
                        'Purchases of marketable securities and treasury stock'])

biogen = Data('Biogen', earnings, ratios, margin, returns)

print()
print("Biogen")
print()
print(earnings)
print()
print(returns)
print()
print(margin)
print()
print(ratios)
