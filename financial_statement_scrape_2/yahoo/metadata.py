import time
from yahoo.scrape_yearly import get_page
import pandas as pd

KEY = ['income_statement', 'balance_sheet', 'cash_flow']

hk_stocks = pd.read_csv('hong_kong_stocks.csv')
results = []
for row in hk_stocks.T.to_dict().values():
    result = {}
    try:
        ticker = str(row['Ticker'])
        ticker = '0' + ticker if len(ticker) == 3 else ticker
        ticker += '.HK'
        page = get_page('https://uk.finance.yahoo.com/quote/{}/profile?p={}'.format(ticker, ticker))
        spans = page.find_all('span')
        for i,span in enumerate(spans):
            if 'Sector' in span.get_text():
                result['sector'] = spans[i+1].get_text()

            if 'Industry' in span.get_text():
                result['industry'] = spans[i+1].get_text()
                break
        result['ticker'] = row['Ticker']
        print(result)
        results.append(result)
        time.sleep(3)
    except:
        print('Failed for {}, {}'.format(row['Name'], row['Ticker']))
