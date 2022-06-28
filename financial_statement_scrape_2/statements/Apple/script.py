import pandas as pd
from script_calc import Calc

pd.set_option('display.max_columns', 500)
pd.set_option('display.max_rows', 500)
pd.set_option('display.width', 500)

c = Calc()

data = c.load_data('Apple')
revenue = c.get_line(data, 'income_statement', 'et sales', 'Net Sales')
income = c.get_line(data, 'income_statement', 'Net income', 'Net income')
ppe = c.get_line(data, 'balance_sheet', 'plant and equipment', 'PPE')
ppe_and_acquisitions = c.get_and_operate_on_lines(data, 'cash_flow', ['acquisition'], 'PPE + Acquisitions')
assets_less_cash_and_securities = c.get_and_operate_on_lines(data,
                                                             'balance_sheet',
                                                             ['otal assets', 'cash equivalents',
                                                              'securities'],
                                                             'Assets less Cash and Securities',
                                                             False)

results = pd.concat([income, assets_less_cash_and_securities]).dropna(axis=1)
