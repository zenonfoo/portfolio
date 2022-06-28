import pandas as pd
from script_calc import Calc

pd.set_option('display.max_columns', 500)
pd.set_option('display.max_rows', 500)
pd.set_option('display.width', 500)


c = Calc()
data = c.load_data('NortonLifeLock')
revenue = c.get_line(data, c.income_statement, 'Net revenues', 'Sales')