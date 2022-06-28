from config import get_list_of_possible_statement_headers
from scrape.financial_statements import get_financial_statements
from scrape.urls import get_links
from process import process_all_financial_statements, save_to_csv
import pandas as pd
from pprint import PrettyPrinter

pp = PrettyPrinter()

pd.set_option('display.max_columns', 500)
pd.set_option('display.max_rows', 500)
pd.set_option('display.width', 500)

# Get and process data
url = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0000849399&type=10-k&dateb=&owner=include&count=10&search_text="
urls = get_links(url)
print("Number of URLS: ", len(urls))
urls = urls[:-1]

# Getting html data
list_to_check = get_list_of_possible_statement_headers()
data = []
for link in urls:
    print('Getting data from link: ', link)
    data.append(get_financial_statements(link, list_to_check))

# Processing html data
processed_data = []
for i, x in enumerate(temp):
    print('Processing statement: {}'.format(i + 1))
    processed_data.append(process_all_financial_statements(x))

# check
print(pd.DataFrame(processed_data[0]['income_statement']).transpose())
print(pd.DataFrame(processed_data[0]['balance_sheet']).transpose())
print(pd.DataFrame(processed_data[0]['cash_flow']).transpose())
print(pd.DataFrame(processed_data[-1]['income_statement']).transpose())
print(pd.DataFrame(processed_data[-1]['balance_sheet']).transpose())
print(pd.DataFrame(processed_data[-1]['cash_flow']).transpose())

# Save to csv
save_to_csv(processed_data, 'NortonLifeLock')
