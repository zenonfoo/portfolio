import pandas as pd
from yf_api.utils import check

nyse = pd.read_csv('nyse')

counter = 71

for i in range(counter, nyse.shape[0]):
    name = nyse.iloc[i]['name'].lower()
    if 'acquisition' in name or 'investment' in name or 'asset management' in name:
        pass
    else:
        try:
            print(i)
            check(nyse.iloc[i]['ticker'])
        except:
            print('Failed for {}, {}'.format(nyse.iloc[i]['name'], nyse.iloc[i]['ticker']))

        on = input('Continue?')
        if on != '':
            break
