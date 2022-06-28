from yahoo.scrape_yearly import get_data
from yahoo.calc import calc, YearlyQuarterly
import pandas as pd

pd.set_option('display.width', 400)
pd.set_option('display.max_columns', 20)
pd.set_option('display.max_rows', 1000)

hk_stocks = pd.read_csv('hong_kong_stocks.csv')
pe_less_than_10 = hk_stocks[hk_stocks['P/E Ratio'] < 10]
pe_less_than_10 = pe_less_than_10[pe_less_than_10['P/E Ratio'] > 0]


def dp_2(val):
    try:
        return round(val, 2)
    except:
        return val


def thousand_separator(val):
    try:
        return "{:,}".format(val)
    except:
        return val


def main(ticker: str):
    result = calc(get_data(ticker), YearlyQuarterly.YEARLY)
    print(result['market_cap'])
    print('INCOME STATEMENT')
    print(result['income_statement'].applymap(dp_2).applymap(thousand_separator))
    print()
    print("BALANCE SHEET")
    print(result['balance_sheet'].applymap(dp_2).applymap(thousand_separator))
    print()
    print("CASH FLOW STATEMENT")
    print(result['cash_flow'].applymap(dp_2).applymap(thousand_separator))
    print()
    print("SUMMARY")
    print(result['summary_data'].applymap(dp_2).applymap(thousand_separator))


# for row in pe_less_than_10.T.to_dict().values():
#     try:
#         ticker = str(row['Ticker'])
#         ticker = '0' + ticker if len(ticker) == 3 else ticker
#         result = calc(get_data(ticker + '.HK'), YearlyQuarterly.YEARLY)
#         print(row['Name'], result['market_cap'])
#         print(result['summary_data'].applymap(dp_2).applymap(thousand_separator))
#     except:
#         print('Failed for {}, {}'.format(row['Name'], row['Ticker']))
# 
#     go = input('Continue?')
#     if go != "":
#         break

main('ATVI')
