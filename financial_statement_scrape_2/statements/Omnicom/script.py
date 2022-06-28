import pandas as pd
from script_calc import Calc

pd.set_option('display.max_columns', 500)
pd.set_option('display.max_rows', 500)
pd.set_option('display.width', 500)

c = Calc()
data = c.load_data('Omnicom')
revenue = c.get_line(data, 'income_statement', 'Revenue', 'Sales')
operating_profit = c.get_and_operate_on_lines(data, 'income_statement', ['Operating Profit',
                                                                         'Operating Income'], 'Operating Profit')
net_income = c.get_line(data, c.income_statement, 'Net Income Attributed', 'Net Income')
retained_earnings = c.get_line(data, c.balance_sheet, 'Retained earnings', 'Retained Earnings')
results = pd.concat([revenue,
                     operating_profit,
                     net_income])

# Earnings
earnings = pd.concat([revenue,
                      operating_profit,
                      net_income,
                      retained_earnings])

# Margins
margins = c.operate_on_results_onto_new_df(results, pd.DataFrame(), 'Operating Profit', 'Sales', c.divide,
                                           'Operating Margin')
margins = c.operate_on_results_onto_new_df(results, margins, 'Net Income', 'Sales', c.divide, 'Profit Margin')

print(earnings)
print(margins)
