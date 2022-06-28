import pandas as pd
from script_calc import Calc

pd.set_option('display.max_columns', 500)
pd.set_option('display.max_rows', 500)
pd.set_option('display.width', 500)

income_statement = 'income_statement'
balance_sheet = 'balance_sheet'
cash_flow = 'cash_flow'


def thousand_wrapper(data: pd.DataFrame):
    temp = data.iloc[:, -1:].applymap(lambda x: x / 1000).combine_first(data)
    return temp[temp.columns[::-1]]


c = Calc(thousand_wrapper)
data = c.load_data('RF Industries')
revenue = c.get_line(data, income_statement, 'Net sales', 'Sales')
profit = c.get_line(data, income_statement, 'profit', 'Profit')
operating_income = c.get_line(data, income_statement, 'Operating', 'Operating Income')
net_income = c.get_line(data, income_statement, 'net', 'Net Income')
owners_earnings = c.get_and_operate_on_lines(data, cash_flow, ['Consolidated net',
                                                                                'Acquisitions',
                                                                                'Capital expenditures',
                                                                                'Purchase of'],
                                                              "Owner's Earnings")
equity = c.get_line(data, balance_sheet, "TOTAL STOCKHOLDERS' EQUITY", 'Equity')
results = pd.concat([revenue,
                     profit,
                     operating_income,
                     net_income,
                     owners_earnings,
                     equity])

print(results)
